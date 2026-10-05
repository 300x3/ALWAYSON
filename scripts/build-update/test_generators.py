#!/usr/bin/env python3
"""Regression assertions for the ao-build-update inventory generators.

Why these exist
---------------
Three defects shipped in generated plans because nothing asserted them:

  1. A `podman pull` step carrying a 12-character truncated digest. That is not
     a valid manifest reference -- every such step returned HTTP 400, so the
     "update this" instruction was dead on arrival.
  2. A step built from the application DISPLAY name, producing
     `apt install --only-upgrade Account` for "Account Wizard" -- a real command
     that would fail, or worse, match some unrelated package.
  3. A prose error string ("upstream digest unreachable (registry refused)")
     used as a digest, producing a plausible-looking but meaningless command.

All three are fixed; these assertions exist so they cannot come back. The
digest-length and not-a-value checks are the two named in the work item.

Run:  python3 scripts/build-update/test_generators.py
Exit: 0 all pass, 1 any failure. Read-only: no network, no writes.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))


def _load(name):
    """Import a generator module by path (their filenames are not identifiers:
    provenance-log.py contains a hyphen)."""
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pl = _load("provenance-log")
ah = _load("apt_history")

SHA256_FULL = "sha256:" + "a" * 64
SHA256_TRUNC = "sha256:" + "a" * 12
UNIT = "/ALWAYSON/quadlet/mapping/ao-webodm-web.container"


def has_not_a_value(token: str) -> bool:
    """True when a command fragment carries a marker instead of a value."""
    t = token.strip().lower()
    if not t or t == "-":
        return True
    return any(m in t for m in ("unreachable", "refused", "not found",
                                "not recorded", "unknown", "error"))


def container_row(rel_digest):
    return {"item": "ao-webodm-web", "via": "container/mapping",
            "repo": "webodm/webodm_webapp", "rel_digest": rel_digest,
            "rel_hash": (rel_digest[:19] if isinstance(rel_digest, str)
                         and rel_digest.startswith("sha") else "")}


class TestContainerPullSteps(unittest.TestCase):
    """Assertion 1: every generated pull step carries a FULL digest.

    OPS-19 changed the return type from a list of shell STRINGS to
    `{"steps": [argv, ...], "manual": [prose, ...]}`. These assertions are
    unchanged in meaning -- only in how they read the result -- because the
    point of them was and remains "never emit a broken command".
    """

    def test_truncated_digest_produces_no_step(self):
        """A 12-char digest must yield NO command, not a broken one."""
        self.assertEqual(pl.update_steps(container_row(SHA256_TRUNC),
                                         unit_path=UNIT)["steps"], [],
                         "a truncated digest must not become a pull command")

    def test_full_digest_produces_valid_pull(self):
        steps = pl.update_steps(container_row(SHA256_FULL),
                                unit_path=UNIT)["steps"]
        pulls = [s for s in steps if s[0] == "podman" and s[1] == "pull"]
        self.assertEqual(len(pulls), 1, f"expected one pull step, got {steps}")
        self.assertIn(SHA256_FULL, pulls[0][2])

    def test_empty_digest_produces_no_step(self):
        self.assertEqual(
            pl.update_steps(container_row(""), unit_path=UNIT)["steps"], [])

    def test_prose_error_string_produces_no_step(self):
        """Assertion 2: a prose error string is not a digest."""
        for prose in ("upstream digest unreachable (registry refused)",
                      "no version tag", "unknown", "-"):
            self.assertEqual(pl.update_steps(container_row(prose),
                                             unit_path=UNIT)["steps"], [],
                             f"prose {prose!r} must not become a command")

    def test_every_pull_step_across_shapes_has_full_hex(self):
        """Belt and braces: sweep row shapes, check the emitted digest."""
        rows = [container_row(SHA256_FULL),
                container_row("sha512:" + "b" * 128),
                container_row(SHA256_TRUNC),
                container_row(""),
                dict(container_row(SHA256_FULL), rel_digest=None)]
        seen = 0
        for row in rows:
            for step in pl.update_steps(row, unit_path=UNIT)["steps"]:
                if step[0] == "podman" and step[1] == "pull":
                    seen += 1
                    digest = step[2].split("@", 1)[1]
                    self.assertRegex(
                        digest, r"^(sha256:[0-9a-f]{64}|sha512:[0-9a-f]{128})$",
                        f"malformed digest in: {step}")
        self.assertGreaterEqual(seen, 1, "no pull step was exercised at all")

    def test_no_pull_step_embeds_a_not_a_value_marker(self):
        for tgt in (SHA256_TRUNC, "", "unreachable", "not recorded",
                    "no version tag", "-", "unknown"):
            for step in pl.update_steps(container_row(tgt),
                                        unit_path=UNIT)["steps"]:
                if "@" in step[-1]:
                    frag = step[-1].split("@", 1)[1]
                    self.assertFalse(has_not_a_value(frag),
                                     f"not-a-value marker in: {step}")


class TestAptStepsUsePackageNames(unittest.TestCase):
    """Assertion 3: apt steps name a PACKAGE, never a display name."""

    def test_desktop_app_uses_owning_package(self):
        row = {"item": "Account Wizard", "via": "desktop app (apt)",
               "repo": "apt: accountsservice"}
        self.assertEqual(pl.update_steps(row)["steps"],
                         [["apt", "install", "--only-upgrade",
                           "accountsservice"]])

    def test_display_name_never_reaches_the_command(self):
        row = {"item": "Account Wizard", "via": "desktop app (apt)",
               "repo": "apt: accountsservice"}
        for step in pl.update_steps(row)["steps"]:
            joined = " ".join(step)
            self.assertNotIn("Wizard", joined)
            for tok in step[3:]:
                self.assertRegex(
                    tok, r"^[a-z0-9][a-z0-9+.\-]*(:[a-z0-9]+)?$",
                    f"non-package token {tok!r} in {joined!r}")

    def test_desktop_app_with_no_package_yields_no_step(self):
        self.assertEqual(
            pl.update_steps({"item": "Some App", "via": "desktop app (apt)",
                             "repo": ""})["steps"], [])

    def test_third_party_apt_step_names_a_package(self):
        steps = pl.update_steps({"item": "microsoft-edge-stable",
                                 "via": "apt/third-party",
                                 "repo": "apt: packages.microsoft.com"})["steps"]
        self.assertEqual(len(steps), 1)
        self.assertRegex(steps[0][3], r"^[a-z0-9][a-z0-9+.\-]*(:[a-z0-9]+)?$")

    def test_non_package_vias_have_no_mechanical_step(self):
        for via in ("local build", "ROS 2", "vendor/.deb",
                    "desktop app (not dpkg-owned)"):
            self.assertEqual(
                pl.update_steps({"item": "x", "via": via, "repo": ""})["steps"],
                [], f"{via} should have no mechanical step")


class TestStepsAreArgvNotShellStrings(unittest.TestCase):
    """OPS-19: the split between what a machine can do and what a human must.

    `update_steps` used to return a flat list of strings mixing
    `podman pull repo@sha256:<64>` -- runnable -- with
    `edit Image= in quadlet/x` -- runnable by nothing, ever. An item was marked
    `eligible` on the strength of the first while carrying the second, so
    "eligible" did not mean "automatable" and nothing could tell them apart.
    """

    def test_no_step_is_ever_a_bare_string(self):
        """Every step is an argv ARRAY, so no executor needs a shell."""
        for row in (container_row(SHA256_FULL),
                    {"item": "foo", "via": "snap", "repo": ""},
                    {"item": "foo", "via": "flatpak", "repo": ""},
                    {"item": "foo", "via": "apt/third-party", "repo": ""},
                    {"item": "Some App", "via": "desktop app (apt)",
                     "repo": "apt: accountsservice"}):
            for s in pl.update_steps(row, unit_path=UNIT)["steps"]:
                self.assertIsInstance(s, list, f"step must be argv, got {s!r}")
                self.assertTrue(all(isinstance(a, str) for a in s),
                                f"argv must hold strings, got {s!r}")

    def test_the_quadlet_edit_is_prose_and_never_a_step(self):
        """The one step that cannot be mechanised must not pretend to be."""
        out = pl.update_steps(container_row(SHA256_FULL), unit_path=UNIT)
        joined = " ".join(" ".join(s) for s in out["steps"])
        self.assertNotIn("edit Image=", joined,
                         "a prose instruction leaked into executable steps")
        self.assertTrue(any("Image=" in m for m in out["manual"]),
                        "the Image= edit must still be recorded as manual prose")

    def test_prose_only_sources_report_no_executable_step(self):
        """A source with no mechanical path yields empty `steps`, not a fake."""
        out = pl.update_steps({"item": "x", "via": "local build", "repo": ""})
        self.assertEqual(out["steps"], [])
        self.assertIsInstance(out["manual"], list)

    def test_every_emitted_step_passes_the_safety_check(self):
        """Nothing leaves the generator that an executor could not run safely."""
        rows = [container_row(SHA256_FULL),
                container_row(SHA256_TRUNC),
                {"item": "foo", "via": "snap", "repo": ""},
                {"item": "foo", "via": "flatpak", "repo": ""},
                {"item": "evil; rm -rf /", "via": "snap", "repo": ""}]
        for row in rows:
            for s in pl.update_steps(row, unit_path=UNIT)["steps"]:
                self.assertTrue(pl._argv_is_safe(s),
                                f"unsafe step emitted: {s!r}")

    def test_a_shell_metacharacter_is_downgraded_to_prose(self):
        """Hostile item names must not become runnable argv."""
        row = {"item": "pkg; rm -rf /", "via": "apt/third-party", "repo": ""}
        out = pl.update_steps(row)
        self.assertEqual(out["steps"], [],
                         "a metacharacter-bearing name must not be executable")
        self.assertTrue(out["manual"], "the intent must still be recorded")

    def test_the_deploy_script_is_the_only_script_path_allowed(self):
        self.assertTrue(pl._argv_is_safe(
            ["./scripts/deploy/deploy-quadlet-domain.sh", "mapping"]))
class TestRollupsCanBeDrilledInto(unittest.TestCase):
    """OPS-23: a roll-up row must not be a dead end.

    A row reading "plasma-workspace (28 launchers)" is only useful if the
    reader can see WHICH 28. The members were computed and carried on the row
    as `members`, but the HTML table renderer never emitted them -- so the
    drill-down existed in markdown only, and the HTML/PDF render silently lost
    it. Silent loss is the failure mode that matters: nothing errored, the
    document just quietly stopped being able to answer a question.
    """

    ROW = {"item": "plasma-workspace (28 launchers)", "via": "desktop app (apt)",
           "publisher": "KDE", "repo": "apt:kde", "pinned": "5.27", "released": "5.27",
           "pin_hash": "x", "rel_hash": "x", "date": "-", "download": "-",
           "is_pinned": True, "nocompare": True,
           "members": ["Dolphin", "Konsole", "Kate"]}

    def test_html_row_drills_into_its_members(self):
        h = pl.rows_to_html([self.ROW], "3 items", "t")
        self.assertIn("3 entries", h, "the drill-down is missing from the row")
        for m in self.ROW["members"]:
            self.assertIn(m, h, f"member {m!r} is not reachable in the HTML")

    def test_a_row_with_no_members_gets_no_drilldown(self):
        r = dict(self.ROW)
        r.pop("members")
        h = pl.rows_to_html([r], "1 item", "t")
        self.assertNotIn("entries</summary>", h,
                         "a non-roll-up row must not claim to have members")

    def test_member_names_are_html_escaped(self):
        """Members come from .desktop files on disk; a name is not trusted."""
        r = dict(self.ROW, members=["<img src=x onerror=alert(1)>"])
        h = pl.rows_to_html([r], "1 item", "t")
        self.assertNotIn("<img src=x", h, "member name was not escaped")
        self.assertIn("&lt;img src=x", h)

    def test_the_drilldown_survives_the_print_stylesheet(self):
        """A PDF that hides the drill-down reintroduces the dead end."""
        self.assertIn("@media print", pl.CSS)
        self.assertIn("details.drill", pl.CSS)

    def test_the_apt_rollups_carry_their_members(self):
        """The two apt roll-ups were the remaining dead ends.

        The KDE and launcher roll-ups were drillable; "Ubuntu archive
        packages" and "ROS 2 lyrical (whole train)" were still a bare count.
        Both lists are already in `inv`, so this asserts the rows carry them.
        """
        inv = {"apt_packages": [
            {"package": "libc6", "version": "2.42-1", "release": "Ubuntu 26.04"},
            {"package": "ros-jazzy-rclcpp", "version": "1.0.0",
             "release": "Third-party", "origin": "packages.ros.org",
             "suite": "resolute"},
        ], "os": {"pretty": "Ubuntu 26.04.1 LTS", "codename": "resolute"}}

        for row in pl.ubuntu_summary(inv) + pl.ros_summary(inv):
            self.assertTrue(row.get("members"),
                            f"{row['item']} is a roll-up with no members: "
                            f"a reader cannot drill into it")
            for m in row["members"]:
                self.assertIn(" (", m,
                              f"member {m!r} carries no version; OPS-23 asks "
                              f"for members with their own versions")

    def test_a_package_rollup_renders_one_row_per_member(self):
        """Thousands of members must not be joined into one table cell.

        The first fix produced a single 40,000-character line for the Ubuntu
        archive. That technically satisfied "the members are reachable" and
        practically failed the reader just as badly as the bare count did.
        """
        r = dict(self.ROW, item="Ubuntu archive packages",
                 package_rollup=True,
                 members=["libc6 (2.42-1)", "zlib1g (1:1.3.dfsg-1)"])
        md = pl.rollup_details_md([r])
        self.assertIn("| `libc6` | `2.42-1` |", md)
        self.assertIn("| `zlib1g` | `1:1.3.dfsg-1` |", md)
        self.assertIn("expand to list all 2 packages", md)
        # the package must not be glued to the version by the roll-up renderer
        self.assertNotIn("libc6 (2.42-1)", md)

    def test_a_launcher_rollup_is_not_a_package_rollup(self):
        """The launcher grouping keeps its joined cell; only packages split."""
        md = pl.rollup_details_md([dict(self.ROW)])
        self.assertIn("expand to list every application entry", md)


class TestVerbAllowlistAgreesAcrossFiles(unittest.TestCase):
    """apply-plan.py duplicates the verb list so it runs standalone.

    A duplicated constant is a drift risk: if provenance-log.py gains a verb
    the validator has never heard of, every step using it fails validation and
    the operator cannot tell whether the plan or the validator is wrong.
    """

    def test_allowlists_are_identical(self):
        ap = load_module("ap_verbs", Path(__file__).resolve().parent
                         / "apply-plan.py")
        self.assertEqual(tuple(pl.PLAN_VERBS), tuple(ap.ALLOWED_VERBS),
                         "the generator and the validator disagree about "
                         "which verbs a plan step may use")

    def test_the_deploy_script_allowlist_is_identical(self):
        ap = load_module("ap_scripts", Path(__file__).resolve().parent
                         / "apply-plan.py")
        self.assertEqual(("./scripts/deploy/deploy-quadlet-domain.sh",),
                         ap.ALLOWED_SCRIPTS)


class TestApplyPlanValidator(unittest.TestCase):
    """OPS-20: the dry-run validator must reject what it cannot trust."""

    def setUp(self):
        self.ap = load_module("ap_validator", Path(__file__).resolve().parent
                              / "apply-plan.py")

    def _plan(self, items):
        return {"generated": "2026-10-04T00:00:00Z", "host": "h", "schema": 2,
                "items": items}

    def test_a_bare_string_step_is_rejected(self):
        """Splitting a string would be a guess; the validator refuses."""
        bad = self.ap.validate_step("podman pull repo@sha256:" + "a" * 64, "x")
        self.assertTrue(any("bare string" in b for b in bad), bad)

    def test_a_non_allowlisted_verb_is_rejected(self):
        bad = self.ap.validate_step(["curl", "-s", "http://x"], "x")
        self.assertTrue(any("not allowlisted" in b for b in bad), bad)

    def test_a_shell_metacharacter_argument_is_rejected(self):
        bad = self.ap.validate_step(["apt", "install", "foo; rm -rf /"], "x")
        self.assertTrue(any("metacharacter" in b for b in bad), bad)

    def test_a_truncated_pull_digest_is_rejected(self):
        bad = self.ap.validate_step(
            ["podman", "pull", "repo@sha256:" + "a" * 12], "x")
        self.assertTrue(any("64 hex" in b for b in bad), bad)

    def test_a_floating_pull_reference_is_rejected(self):
        bad = self.ap.validate_step(["podman", "pull", "repo:latest"], "x")
        self.assertTrue(any("not digest-pinned" in b for b in bad), bad)

    def test_a_valid_step_produces_no_problems(self):
        self.assertEqual(
            self.ap.validate_step(
                ["podman", "pull", "repo@sha256:" + "a" * 64], "x"), [])

    def test_eligible_with_no_step_is_the_defect_OPS19_removed(self):
        plan = self._plan([{"item": "x", "decision": "eligible",
                            "steps": [], "manual": ["do it by hand"]}])
        bad = self.ap.validate_plan(plan)
        self.assertTrue(any("no executable step" in b for b in bad), bad)

    def test_an_undecided_item_is_never_actionable(self):
        plan = self._plan([{"item": "x", "decision": "maybe", "steps": [],
                            "manual": []}])
        self.assertTrue(self.ap.validate_plan(plan))

    def test_a_well_formed_plan_validates_clean(self):
        plan = self._plan([
            {"item": "x", "decision": "eligible", "unit": "quadlet/mapping/a",
             "target_digest_full": "sha256:" + "a" * 64,
             "steps": [["podman", "pull", "r@sha256:" + "a" * 64],
                       ["systemctl", "--user", "daemon-reload"]],
             "manual": ["set Image= by hand"]},
            {"item": "y", "decision": "excluded", "unit": "",
             "target_digest_full": "-", "steps": [], "manual": ["float"]}])
        self.assertEqual(self.ap.validate_plan(plan), [])

    def test_two_units_sharing_a_digest_are_reported_as_coupled(self):
        """A shared digest means one rollback cannot be partial."""
        d = "sha256:" + "a" * 64
        plan = self._plan([
            {"item": "x", "decision": "eligible", "unit": "quadlet/mapping/a",
             "target_digest_full": d, "steps": [], "manual": []},
            {"item": "y", "decision": "eligible", "unit": "quadlet/mapping/b",
             "target_digest_full": d, "steps": [], "manual": []}])
        r = self.ap.blast_radius(plan["items"])
        self.assertEqual(r["coupled_digests"], 1)
        self.assertEqual(r["by_domain"]["mapping"], ["x", "y"])

    def test_excluded_items_never_enter_the_blast_radius(self):
        d = "sha256:" + "a" * 64
        plan = self._plan([
            {"item": "x", "decision": "eligible", "unit": "quadlet/mapping/a",
             "target_digest_full": d, "steps": [], "manual": []},
            {"item": "y", "decision": "excluded", "unit": "quadlet/mapping/b",
             "target_digest_full": d, "steps": [], "manual": []}])
        r = self.ap.blast_radius(plan["items"])
        self.assertEqual(r["coupled_digests"], 0,
                         "an excluded item is not being touched, so it is "
                         "not part of the blast radius")

    def test_coupling_is_read_from_the_pull_step_not_the_display_column(self):
        """The step is what runs, so the step is what couples.

        The two digests disagree on purpose. Coupling them because a
        human-readable summary column matched would report a risk that the
        commands do not have.
        """
        plan = self._plan([
            {"item": "x", "decision": "eligible", "unit": "quadlet/mapping/a",
             "target_digest_full": "sha256:" + "b" * 64,
             "steps": [["podman", "pull", "r@sha256:" + "a" * 64]],
             "manual": []},
            {"item": "y", "decision": "eligible", "unit": "quadlet/lidar/b",
             "target_digest_full": "sha256:" + "b" * 64,
             "steps": [["podman", "pull", "r@sha256:" + "a" * 64]],
             "manual": []}])
        r = self.ap.blast_radius(plan["items"])
        self.assertEqual(r["coupled_digests"], 1,
                         "both items pull the same digest, so they are coupled")
        self.assertEqual(r["by_digest"]["sha256:" + "a" * 64], ["x", "y"])

    def test_an_item_with_no_pull_step_does_not_fabricate_coupling(self):
        """A snap refresh has no digest; it must not inherit one from a column."""
        plan = self._plan([
            {"item": "x", "decision": "eligible", "unit": "",
             "target_digest_full": "sha256:" + "a" * 64,
             "steps": [["snap", "refresh", "x"]], "manual": []},
            {"item": "y", "decision": "eligible", "unit": "",
             "target_digest_full": "-", "steps": [["snap", "refresh", "y"]],
             "manual": []}])
        r = self.ap.blast_radius(plan["items"])
        self.assertEqual(r["coupled_digests"], 0,
                         "no pull step means no digest is being applied, so "
                         "there is nothing to couple")


class TestAptHistoryParsing(unittest.TestCase):
    """The install-date column must come from apt's history, not mtimes."""

    SAMPLE = (
        "Start-Date: 2026-04-23  00:44:38\n"
        "Commandline: apt-get -y install accountsservice\n"
        "Requested-By: scottw (1000)\n"
        "Install: accountsservice:amd64 (4.0.2-2build1)\n"
        "End-Date: 2026-04-23  00:44:40\n"
        "\n"
        "Start-Date: 2026-08-04  11:34:23\n"
        "Commandline: apt-get -y full-upgrade\n"
        "Upgrade: accountsservice:amd64 (4.0.2-2build1, 4.0.2-2build2)\n"
        "End-Date: 2026-08-04  11:34:54\n"
        "\n"
        "Start-Date: 2026-10-01  06:29:21\n"
        "Commandline: /usr/bin/unattended-upgrade\n"
        "Upgrade: openvpn:amd64 (2.7.0-1ubuntu1.2, 2.7.0-1ubuntu1.3)\n"
        "End-Date: 2026-10-01  06:29:23\n"
        "\n"
        "Start-Date: 2026-10-03  10:00:00\n"
        "Commandline: apt-get install -y rclone\n"
        "Install: rclone:amd64 (1.60.1+dfsg-4ubuntu3.2)\n"
        "End-Date: 2026-10-03  10:00:05\n"
        "\n"
        # Installed, then purged. dbeaver-ce is the real case on this host:
        # installed 2026-08-29, purged 2026-10-01, no longer in dpkg's database.
        "Start-Date: 2026-08-29  09:12:00\n"
        "Commandline: apt install -y /tmp/dbeaver-ce.deb\n"
        "Install: dbeaver-ce:amd64 (26.1.5)\n"
        "End-Date: 2026-08-29  09:12:30\n"
        "\n"
        "Start-Date: 2026-10-01  09:00:00\n"
        "Commandline: /usr/bin/apt-get purge -y --no-install-recommends dbeaver-ce\n"
        "Purge: dbeaver-ce:amd64 (26.1.5)\n"
        "End-Date: 2026-10-01  09:00:10\n"
        "\n"
        # Two packages on one Upgrade line, each with a two-version list. A
        # naive comma split cuts inside the parentheses and loses both names.
        "Start-Date: 2026-10-02  06:00:00\n"
        "Commandline: /usr/bin/unattended-upgrade\n"
        "Upgrade: libfoo:amd64 (1.0-1, 1.0-2), libbar:amd64 (2.0-1, 2.0-2)\n"
        "End-Date: 2026-10-02  06:00:05\n"
    )

    def _index(self):
        """Parse the SAMPLE fixture from a temp dir via the injectable arg.

        No module reload and no patching of the real /var/log/apt: the parser
        takes log_dir precisely so this test never touches system state.
        """
        tmp = Path(tempfile.mkdtemp())
        (tmp / "history.log").write_text(self.SAMPLE)
        self.addCleanup(shutil.rmtree, tmp, True)
        return ah.parse_history(log_dir=tmp)

    def test_install_date_wins_over_later_upgrade(self):
        idx = self._index()
        self.assertEqual(idx["accountsservice:amd64"]["date"], "2026-04-23")
        self.assertEqual(idx["accountsservice:amd64"]["action"], "Install")

    def test_later_upgrade_is_recorded_separately(self):
        rec = self._index()["accountsservice:amd64"]
        self.assertEqual(rec["upgraded"], "2026-08-04")

    def test_unattended_run_is_flagged(self):
        rec = self._index()["openvpn:amd64"]
        self.assertTrue(rec["unattended"],
                        "unattended-upgrade must be distinguishable")

    def test_manual_install_is_not_flagged_unattended(self):
        self.assertFalse(self._index()["accountsservice:amd64"]["unattended"])

    def test_requested_by_is_captured(self):
        self.assertEqual(self._index()["accountsservice:amd64"]["requested_by"],
                         "scottw (1000)")

    def test_archless_lookup_finds_qualified_record(self):
        mod = ah
        date, rec = mod.install_date("rclone", self._index())
        self.assertEqual(date, "2026-10-03")
    def test_apt_history_loads_regardless_of_working_directory(self):
        """The production invocation cd's to AO_ROOT before running.

        A bare `import apt_history` resolves against sys.path, which holds the
        CWD, not the script's own directory -- so it raised ImportError on
        every real run and silently reverted to the dpkg mtime this module
        exists to replace. Loading by __file__ is what fixes it, and this
        asserts the fix holds from a directory that does not contain the
        module.
        """
        import subprocess
        # provenance-log.py is the SIBLING of this test file, not this file.
        prov = Path(__file__).resolve().parent / "provenance-log.py"
        self.assertTrue(prov.is_file(), f"missing generator: {prov}")
        code = (
            "import importlib.util,sys;"
            f"spec=importlib.util.spec_from_file_location('pl',{str(prov)!r});"
            "pl=importlib.util.module_from_spec(spec);spec.loader.exec_module(pl);"
            "m=pl._load_apt_history();"
            "print('LOADED' if m is not None else 'MISSING')"
        )
        # /tmp contains no apt_history.py, so a passing run proves the load is
        # path-relative rather than CWD-relative.
        out = subprocess.run([sys.executable, "-c", code], cwd="/tmp",
                             capture_output=True, text=True, timeout=60)
        self.assertEqual(out.stdout.strip(), "LOADED",
                         f"apt_history did not load from a foreign CWD "
                         f"(rc={out.returncode}): {out.stderr[-400:]}")

    def test_unknown_package_yields_no_date_rather_than_a_guess(self):
        date, rec = ah.install_date("definitely-not-installed-xyzzy",
                                    self._index())
        self.assertIsNone(date)
        self.assertIsNone(rec)

    def test_empty_name_is_handled(self):
        self.assertEqual(ah.install_date("", {}), (None, None))

    def test_apt_date_labels_its_source(self):
        """Whatever it returns must name which of the two sources it used."""
        val = pl.apt_date("accountsservice")
        self.assertTrue(val.startswith("2026-04-23") or "dpkg mtime" in val,
                        f"unlabelled date returned: {val!r}")

    def test_apt_date_never_returns_a_bare_unlabelled_date(self):
        for pkg in ("accountsservice", "rclone", "bash", "nonexistent-xyzzy"):
            val = pl.apt_date(pkg)
            self.assertTrue(val == "-" or "(" in val,
                            f"date for {pkg} carries no source label: {val!r}")

    def test_purged_package_reports_no_install_date(self):
        """A removed package must not be given an install date.

        Regression: the record kept the original Install date after a later
        Purge overwrote only some fields, so the report showed a 2026-08-29
        install for dbeaver-ce -- a package `dpkg -l` no longer lists at all.
        """
        date, rec = ah.install_date("dbeaver-ce", self._index())
        self.assertIsNone(date, "a purged package must not report an install date")
        self.assertTrue(rec["removed"])
        self.assertEqual(rec["action"], "Purge")

    def test_purge_wins_over_the_earlier_install(self):
        rec = self._index()["dbeaver-ce:amd64"]
        self.assertEqual(rec["date"], "2026-10-01", "the removal is the latest truth")

    def test_multi_package_line_yields_every_package(self):
        """A comma inside the version list must not hide the real packages.

        `Upgrade: libfoo:amd64 (1.0-1, 1.0-2), libbar:amd64 (...)` splits on
        the naive comma into fragments like " 1.0-2)" that match no package,
        silently dropping both names from the index.
        """
        idx = self._index()
        for name in ("libfoo:amd64", "libbar:amd64"):
            self.assertIn(name, idx, f"{name} lost to naive comma splitting")
        self.assertEqual(idx["libfoo:amd64"]["versions"], ["1.0-1", "1.0-2"])
        self.assertEqual(idx["libbar:amd64"]["versions"], ["2.0-1", "2.0-2"])


class TestAptHistoryIsActuallyUsed(unittest.TestCase):
    """Regression tests for two defects that both made the report lie quietly.

    Neither raised an error. Both produced a document that looked correct and
    carried the wrong dates, which is the failure mode this file exists to
    catch -- so they are pinned here.
    """

    def test_apt_history_module_loads_from_a_foreign_cwd(self):
        """The import must not depend on CWD.

        refresh-install-log.sh does `cd "$AO_ROOT"` before invoking
        provenance-log.py, so a bare `import apt_history` found nothing on
        sys.path, the ImportError was swallowed, and every date silently fell
        back to the dpkg mtime. Reproduced before the fix by loading the module
        by path from /tmp: apt_date('rclone') returned '(dpkg mtime)'.
        """
        here = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as td:
            old = os.getcwd()
            os.chdir(td)          # a directory with no provenance-log siblings
            try:
                mod = load_module("pl_cwd_probe", here / "provenance-log.py")
                self.assertIsNotNone(mod._load_apt_history(),
                                     "apt_history must load regardless of CWD")
            finally:
                os.chdir(old)

    def test_a_purged_package_never_shows_an_install_date(self):
        """dpkg no longer lists it, so the Installed cell must not claim a date."""
        mod = load_module("pl_purged", Path(__file__).resolve().parent
                          / "provenance-log.py")
        self.assertNotRegex(mod.apt_date("nginx"), r"^\d{4}-\d{2}-\d{2} ")

    def test_every_returned_date_carries_its_provenance_label(self):
        """A bare date is the ambiguity OPS-21 existed to remove."""
        mod = load_module("pl_labels", Path(__file__).resolve().parent
                          / "provenance-log.py")
        for pkg in ("rclone", "bash", "gstreamer1.0-plugins-bad",
                    "accountsservice", "nonexistent-xyzzy"):
            val = mod.apt_date(pkg)
            self.assertTrue(val == "-" or "(" in val,
                            f"date for {pkg} carries no source label: {val!r}")

    def test_automatic_flag_is_not_reported_as_a_version(self):
        """dpkg writes "1.2.3, automatic"; 'automatic' is a flag, not a version."""
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "history.log").write_text(
            "Start-Date: 2026-08-04  10:00:00\n"
            "Commandline: apt-get install -y thing\n"
            "Install: thing:amd64 (1.2.3-1, automatic)\n"
            "End-Date: 2026-08-04  10:00:05\n\n")
        rec = ah.parse_history(log_dir=tmp)["thing:amd64"]
        self.assertEqual(rec["versions"], ["1.2.3-1"])
        self.assertNotIn("automatic", rec["versions"])


class TestImageDigestChecker(unittest.TestCase):
    """OPS-02: the digest check must be able to say OK, not only DRIFT.

    A checker observed only in its failing state proves nothing -- "7 rows
    drifted" is exactly what a broken comparison also prints. Each case below
    drives the real script against a synthetic tree and asserts the exit code,
    so the OK path is exercised as carefully as the failing one.
    """

    SCRIPT = "scripts/validation/check-image-digests.sh"
    ROOT = Path(__file__).resolve().parents[2]

    def run_check(self, units, matrix_yaml, *args):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "units").mkdir()
        for name, body in units.items():
            (tmp / "units" / f"{name}.container").write_text(body)
        (tmp / "m.yaml").write_text(matrix_yaml)
        env = {**os.environ,
               "AO_ROOT": str(self.ROOT),
               "QUADLET_DEPLOY_DIR": str(tmp / "units"),
               "VERSION_MATRIX": str(tmp / "m.yaml")}
        return subprocess.run(["bash", str(self.ROOT / self.SCRIPT), *args],
                              capture_output=True, text=True, env=env, cwd=self.ROOT)

    D1 = "sha256:" + "1" * 64
    D2 = "sha256:" + "2" * 64

    def test_a_matrix_matching_the_deployed_units_reports_ok(self):
        r = self.run_check({"a": f"Image=example.com/a@{self.D1}\n"},
                           f'host:\n  images:\n    a: "example.com/a@{self.D1}"\n',
                           "--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("RESULT: OK", r.stdout)

    def test_a_stale_matrix_row_is_reported_and_fails_the_check(self):
        r = self.run_check({"a": f"Image=example.com/a@{self.D1}\n"},
                           f'host:\n  images:\n    a: "example.com/a@{self.D2}"\n',
                           "--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("DRIFT", r.stdout)
        self.assertIn("host.images.a", r.stdout)

    def test_a_tag_only_image_is_a_rule_9_violation(self):
        """An Image= with no digest passes review for months."""
        r = self.run_check({"a": f"Image=example.com/a@{self.D1}\n",
                            "b": "Image=example.com/b:latest\n"},
                           f'host:\n  images:\n    a: "example.com/a@{self.D1}"\n',
                           "--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("UNPINNED", r.stdout)

    def test_a_truncated_digest_counts_as_unpinned(self):
        """The OPS-22 lesson: a `sha256:` prefix is not a pinned reference.

        `sha256:` plus 12 hex characters looks pinned and is not.
        """
        short = "sha256:" + "a" * 12
        r = self.run_check({"a": f"Image=example.com/a@{short}\n"},
                           'host:\n  images: {}\n', "--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("UNPINNED", r.stdout)

    def test_drift_is_reported_but_the_default_run_still_exits_zero(self):
        """Reporting is the default; --check is the gate.

        A validation script that always exits non-zero stops being run, so the
        distinction has to be in the exit code and not only in the text.
        """
        r = self.run_check({"a": f"Image=example.com/a@{self.D1}\n"},
                           f'host:\n  images:\n    a: "example.com/a@{self.D2}"\n')
        self.assertEqual(r.returncode, 0)
        self.assertIn("RESULT: DRIFT", r.stdout)


class TestProvenancePackageBoundaries(unittest.TestCase):
    """OPS-18: the split into the `provenance` package must hold.

    The refactor moved ~2,300 lines across five modules. A split can compile,
    import, and pass every behavioural test while still being wrong in ways no
    behavioural test sees -- a silently swallowed import, a stale re-export, a
    function that now looks for its sibling one directory too low. Each of
    those produced a document that LOOKED correct and carried the wrong data,
    which is the failure mode this file exists to catch, so the boundaries are
    pinned here rather than trusted.
    """

    HERE = Path(__file__).resolve().parent
    PROV = HERE / "provenance"

    def test_all_five_modules_exist_and_are_not_empty(self):
        for mod in ("common", "policy", "plan", "render", "collector"):
            p = self.PROV / f"{mod}.py"
            self.assertTrue(p.is_file(), f"missing module: {p}")
            self.assertGreater(len(p.read_text().splitlines()), 20,
                               f"{mod}.py is too small to be the real module")

    def test_entrypoint_holds_no_collector_logic(self):
        """The file that was one large module must stay an entrypoint.

        Not a line count -- a specific check. If collection logic creeps back
        into provenance-log.py the split is undone in substance while every
        other test here still passes.
        """
        src = (self.HERE / "provenance-log.py").read_text()
        # COLLECTED[...] is allowed: main() reads the collector's summary to
        # print the counts line. What must NOT come back is the machinery that
        # fills it -- a definition, or a network call, in the entrypoint.
        # json.loads IS allowed: main() reads the inventory file. What must
        # not come back is the machinery that gathers or renders anything.
        for leaked in ("def apt_date", "def containers", "def _load_apt_history",
                       "urllib.request", "subprocess.", "def rows_to_html",
                       "def render("):
            self.assertNotIn(leaked, src,
                             f"collection logic leaked back into the entrypoint: {leaked}")
        # It must still be an orchestrator, not a shim that does nothing.
        self.assertIn("def main()", src, "entrypoint lost main()")

    def test_dependency_direction_is_acyclic(self):
        """common <- collector <- render, and policy depends on nothing local.

        A cycle would import only by accident of statement order. Asserted from
        the import statements themselves, so the graph is checked as written
        rather than as intended.
        """
        import re as _re
        allowed = {
            "common":    set(),
            "policy":    set(),
            "collector": {"common"},
            "render":    {"collector", "common", "policy"},
            "plan":      {"common", "policy", "render"},
        }
        for mod, legal in allowed.items():
            src = (self.PROV / f"{mod}.py").read_text()
            for dep in _re.findall(r"^from \.(\w+) import", src, _re.M):
                self.assertIn(dep, legal,
                              f"{mod}.py imports .{dep}, which is not one of {sorted(legal)}")

    def test_policy_module_is_auditable_without_the_import_graph(self):
        """The allowlist is the safety property; it must be readable alone."""
        src = (self.PROV / "policy.py").read_text()
        for guard in ("EXCLUSIONS", "NEEDS_APPROVAL", "PIN_POLICY", "PLAN_VERBS"):
            self.assertIn(guard, src, f"policy.py lost {guard}")
        self.assertNotIn("from .common", src,
                         "policy.py must not depend on the rest of the tree")

    def test_apt_history_sibling_is_found_after_the_split(self):
        """The refactor moved the loader one directory away from its data.

        `Path(__file__).parent / "apt_history.py"` pointed INSIDE the package
        once the function moved, raised FileNotFoundError, and the except
        clause swallowed it into None -- silently reverting every install date
        to the dpkg mtime. No behavioural test caught it; this asserts the
        lookup resolves, and specifically that the module is not None.
        """
        mod = load_module("pl_pkg_apt", self.HERE / "provenance-log.py")
        self.assertIsNotNone(
            mod._load_apt_history(),
            "apt_history.py did not resolve from the package; install dates "
            "would silently fall back to the dpkg mtime")

    def test_underscore_names_survive_the_reexport(self):
        """`from module import *` skips underscore names.

        Two existing regressions reach `_load_apt_history` and `_argv_is_safe`
        through the entrypoint, so the re-export must be built from an explicit
        namespace walk rather than a star import. Pinned because the failure is
        a silent AttributeError at the call site, not an import error.
        """
        mod = load_module("pl_pkg_star", self.HERE / "provenance-log.py")
        for name in ("_load_apt_history", "_argv_is_safe", "_best_tag",
                     "_cache_path", "_digest_of"):
            self.assertTrue(hasattr(mod, name),
                            f"{name} missing from the entrypoint: a star import "
                            f"drops underscore-prefixed names")

    def test_cache_ttl_is_read_through_one_accessor(self):
        """`--refresh` rebinds the TTL at runtime and the banner reads it.

        A plain imported global binds a copy at import time, so a forced refresh
        would print the default 6h TTL. Asserted through the accessor, which is
        the fix: one owner, read on every call.
        """
        mod = load_module("pl_pkg_ttl", self.HERE / "provenance-log.py")
        import provenance.collector as coll
        before = coll.cache_ttl()
        try:
            mod.set_cache_ttl(0)
            self.assertEqual(coll.cache_ttl(), 0)
        finally:
            coll.set_cache_ttl(before)
        self.assertEqual(coll.cache_ttl(), before, "TTL was not restored")

    def test_set_offline_reaches_the_module_that_makes_the_calls(self):
        """--offline is a hard no-network guarantee; the owner must see it."""
        mod = load_module("pl_pkg_off", self.HERE / "provenance-log.py")
        import provenance.collector as coll
        before = coll.OFFLINE
        try:
            mod.set_offline(True)
            self.assertTrue(coll.OFFLINE, "set_offline did not reach the collector")
        finally:
            coll.OFFLINE = before


class TestRenderProducesBothOutputs(unittest.TestCase):
    """OPS-18 acceptance: the render path must still be exercised end to end.

    Every other test in this file probes one function in isolation. The split
    moved the Markdown and HTML writers into render.py with a new import edge to
    collector.py, and a missing name on that edge only fails when a row is
    actually formatted -- which no unit test of the collectors does. This
    builds a minimal row set and renders both outputs, so the edge is covered by
    a real call rather than by an import check.
    """

    def setUp(self):
        self.mod = load_module("pl_render_out", Path(__file__).resolve().parent
                               / "provenance-log.py")

    @staticmethod
    def _rows():
        """Rows in the shape the collectors actually emit.

        Keyed to the literals in collector.py (item/via/publisher/repo/
        pinned/released/pin_hash/rel_hash/download). Guessing these produced a
        KeyError on 'released' the first time round, which is the point: the
        renderer indexes rows directly, so a fixture must match the real
        schema rather than a plausible-looking one.
        """
        return [
            {"item": "rclone", "via": "apt", "publisher": "Ubuntu",
             "repo": "jammy/main", "pinned": "1.60.1-1ubuntu1",
             "released": "1.60.1-1ubuntu1.1", "tag": None,
             "pin_hash": "1.60.1-1ubuntu1", "rel_hash": "1.60.1-1ubuntu1.1",
             "download": "https://example.invalid/rclone", "is_pinned": True,
             "local": False, "date": "2026-10-03 (apt history, Install)"},
            {"item": "ao-nodeodm", "via": "container/build-update",
             "publisher": "Docker Hub", "repo": "docker.io/opendronemap/nodeodm",
             "pinned": "no version tag", "released": "2.6.0",
             "tag": "latest",
             "pin_hash": "floating tag, no digest pinned", "rel_hash": "sha256:abc123",
             "download": "https://example.invalid/nodeodm", "is_pinned": False,
             "local": False, "date": "-"},
        ]

    def test_rows_to_html_emits_a_table_containing_every_row(self):
        html = self.mod.rows_to_html(self._rows(), "2 items.",
                                     "ALWAYS ON - Software Status", [])
        self.assertIn("<table", html)
        for token in ("rclone", "ao-nodeodm", "1.60.1-1ubuntu1",
                      "sha256:abc123"):
            self.assertIn(token, html, f"{token} missing from the rendered HTML")

    def test_html_escapes_instead_of_emitting_raw_markup(self):
        """A package or repo name carrying markup must not reach the page raw."""
        rows = self._rows()
        rows[0]["item"] = "<script>alert(1)</script>"
        rows[0]["repo"] = "<b>bold</b>"
        html = self.mod.rows_to_html(rows, "2 items.", "t", [])
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<b>bold</b>", html)

    def test_rollup_details_render_for_a_populated_group(self):
        """The drill-down (OPS-23) must survive the move into render.py.

        `rollup_details_md(rows, kde_members)` -- the second argument is the KDE
        component list as (name, owning_package) PAIRS. Passing roll-up names
        there raised "too many values to unpack", so the pairs are pinned here
        rather than left to the next reader to infer.
        """
        rows = self._rows()
        rows[0]["members"] = ["plasma-workspace", "systemsettings"]
        md = self.mod.rollup_details_md(
            rows, [("plasma-desktop", "plasma-desktop"), ("kwin", "")])
        self.assertIsInstance(md, str)
        for token in ("plasma-workspace", "systemsettings", "plasma-desktop"):
            self.assertIn(token, md,
                          f"{token} missing from the roll-up details: the "
                          f"drill-down (OPS-23) must survive the move into render.py")

    def test_rollup_details_tolerate_an_empty_member_list(self):
        """A group with no launchers must not emit an empty details block."""
        rows = self._rows()
        rows[0]["members"] = []
        md = self.mod.rollup_details_md(rows, None)
        self.assertNotIn("Rolled-up launchers", md)


def load_module(name, path):
    """Import a module from an explicit path, independent of sys.path/CWD."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

if __name__ == "__main__":
    unittest.main(verbosity=2)