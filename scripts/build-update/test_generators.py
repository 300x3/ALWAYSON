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
    """Assertion 1: every generated pull step carries a FULL digest."""

    def test_truncated_digest_produces_no_step(self):
        """A 12-char digest must yield NO command, not a broken one."""
        self.assertEqual(pl.update_steps(container_row(SHA256_TRUNC),
                                         unit_path=UNIT), [],
                         "a truncated digest must not become a pull command")

    def test_full_digest_produces_valid_pull(self):
        steps = pl.update_steps(container_row(SHA256_FULL), unit_path=UNIT)
        pulls = [s for s in steps if s.startswith("podman pull ")]
        self.assertEqual(len(pulls), 1, f"expected one pull step, got {steps}")
        self.assertIn(SHA256_FULL, pulls[0])

    def test_empty_digest_produces_no_step(self):
        self.assertEqual(pl.update_steps(container_row(""), unit_path=UNIT), [])

    def test_prose_error_string_produces_no_step(self):
        """Assertion 2: a prose error string is not a digest."""
        for prose in ("upstream digest unreachable (registry refused)",
                      "no version tag", "unknown", "-"):
            self.assertEqual(pl.update_steps(container_row(prose),
                                             unit_path=UNIT), [],
                             f"prose {prose!r} must not become a command")

    def test_every_pull_step_across_shapes_has_full_hex(self):
        """Belt and braces: sweep row shapes, check the emitted command text."""
        rows = [container_row(SHA256_FULL),
                container_row("sha512:" + "b" * 128),
                container_row(SHA256_TRUNC),
                container_row(""),
                dict(container_row(SHA256_FULL), rel_digest=None)]
        seen = 0
        for row in rows:
            for step in pl.update_steps(row, unit_path=UNIT):
                if step.startswith("podman pull "):
                    seen += 1
                    digest = step.split("@", 1)[1]
                    self.assertRegex(
                        digest, r"^(sha256:[0-9a-f]{64}|sha512:[0-9a-f]{128})$",
                        f"malformed digest in: {step}")
        self.assertGreaterEqual(seen, 1, "no pull step was exercised at all")

    def test_no_pull_step_embeds_a_not_a_value_marker(self):
        for tgt in (SHA256_TRUNC, "", "unreachable", "not recorded",
                    "no version tag", "-", "unknown"):
            for step in pl.update_steps(container_row(tgt), unit_path=UNIT):
                if "@" in step:
                    frag = step.split("@", 1)[1]
                    self.assertFalse(has_not_a_value(frag),
                                     f"not-a-value marker in: {step}")


class TestAptStepsUsePackageNames(unittest.TestCase):
    """Assertion 3: apt steps name a PACKAGE, never a display name."""

    def test_desktop_app_uses_owning_package(self):
        row = {"item": "Account Wizard", "via": "desktop app (apt)",
               "repo": "apt: accountsservice"}
        self.assertEqual(pl.update_steps(row),
                         ["apt install --only-upgrade accountsservice"])

    def test_display_name_never_reaches_the_command(self):
        row = {"item": "Account Wizard", "via": "desktop app (apt)",
               "repo": "apt: accountsservice"}
        for step in pl.update_steps(row):
            self.assertNotIn("Wizard", step)
            for tok in step.split()[3:]:
                self.assertRegex(
                    tok, r"^[a-z0-9][a-z0-9+.\-]*(:[a-z0-9]+)?$",
                    f"non-package token {tok!r} in {step!r}")

    def test_desktop_app_with_no_package_yields_no_step(self):
        self.assertEqual(
            pl.update_steps({"item": "Some App", "via": "desktop app (apt)",
                             "repo": ""}), [])

    def test_third_party_apt_step_names_a_package(self):
        steps = pl.update_steps({"item": "microsoft-edge-stable",
                                 "via": "apt/third-party",
                                 "repo": "apt: packages.microsoft.com"})
        self.assertEqual(len(steps), 1)
        self.assertRegex(steps[0].split()[3], r"^[a-z0-9][a-z0-9+.\-]*(:[a-z0-9]+)?$")

    def test_non_package_vias_have_no_mechanical_step(self):
        for via in ("local build", "ROS 2", "vendor/.deb",
                    "desktop app (not dpkg-owned)"):
            self.assertEqual(
                pl.update_steps({"item": "x", "via": via, "repo": ""}), [],
                f"{via} should have no mechanical step")


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


def load_module(name, path):
    """Import a module from an explicit path, independent of sys.path/CWD."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

if __name__ == "__main__":
    unittest.main(verbosity=2)