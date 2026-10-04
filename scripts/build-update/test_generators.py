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


if __name__ == "__main__":
    unittest.main(verbosity=2)