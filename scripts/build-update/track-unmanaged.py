#!/usr/bin/env python3
"""ALWAYS ON ao-build-update: freshness tracking for unmanaged software.

The operator's decision, 2026-10-02: "YOUR JOB IS TO TRACK THESE AS WELL."
AppImages, /opt trees and ~/.local/bin executables have no package manager
watching them, so a stale copy stays invisible until it fails. This compares
what is on disk against config/build-update/unmanaged-software.yaml and, where an
upstream can be queried, checks whether something newer exists.

READ-ONLY. It queries version endpoints and reads files. It installs nothing,
downloads nothing, and changes nothing.

Four outcomes per item:
  CURRENT     installed version matches what upstream offers
  BEHIND      upstream offers a newer version
  UNCHECKABLE no way to compare automatically - a known gap, not a pass
  UNREGISTERED found on disk but absent from the registry: it has no recorded
              provenance at all, which is itself a finding

Usage:
  track-unmanaged.py [--markdown] [--out FILE] [--offline]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

AO_ROOT = Path(os.environ.get("AO_ROOT", "/ALWAYSON"))
REGISTRY = AO_ROOT / "config/build-update/unmanaged-software.yaml"
TIMEOUT = 20


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def get_json(url):
    """Fetch JSON, or None on any failure. One bad endpoint must not abort the
    whole run; the item is reported as NOT CHECKED instead."""
    req = urllib.request.Request(url, headers={"User-Agent": "alwayson-ao-build-update"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read().decode())
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        return None


def normalise(v):
    """Extract a comparable version number from a tag or a version string.

    Release tags are not uniform: GitHub CLI publishes "v2.102.0", bun
    publishes "bun-v1.4.2", cline publishes "cli-v3.0.68". Comparing those
    literally against a bare installed version marks every one of them BEHIND
    when it is not, so the numeric core is extracted first.
    """
    if not v:
        return ""
    m = re.search(r"(\d+(?:\.\d+)*)", str(v))
    return m.group(1) if m else ""


def run(cmd, timeout=30):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return p.returncode, p.stdout, p.stderr
    except (subprocess.TimeoutExpired, OSError) as e:
        return 127, "", str(e)


# ---------------------------------------------------------------------------
# upstream checks
# ---------------------------------------------------------------------------
def check_pypi(pkg):
    d = get_json(f"https://pypi.org/pypi/{pkg}/json")
    return d["info"]["version"] if d else None


def check_github(repo):
    d = get_json(f"https://api.github.com/repos/{repo}/releases/latest")
    return d.get("tag_name") if d else None


def check_apt(pkg):
    rc, out, _ = run(["apt-cache", "policy", pkg])
    if rc != 0:
        return None
    for line in out.splitlines():
        if line.strip().startswith("Candidate:"):
            return line.split(":", 1)[1].strip()
    return None


def load_registry():
    """Parse unmanaged-software.yaml. Uses PyYAML when present, else a minimal
    reader; this file is hand-maintained and small, but PyYAML is available on
    this host and keeps the parser honest."""
    if not REGISTRY.exists():
        sys.exit(f"ERROR: registry not found: {REGISTRY}")
    text = REGISTRY.read_text()
    try:
        import yaml
        return yaml.safe_load(text)
    except ImportError:
        sys.exit("ERROR: PyYAML is required to read the registry")


def discover():
    """What is actually on disk right now."""
    found = {"appimages": [], "executables": []}
    for root in (Path.home() / "Applications", Path.home() / "Documents" / "APP IMAGES",
                 Path.home() / ".local/bin", Path("/opt")):
        if not root.exists():
            continue
        try:
            for f in sorted(root.rglob("*.AppImage")):
                found["appimages"].append(str(f))
        except (OSError, PermissionError):
            pass
    lb = Path.home() / ".local/bin"
    if lb.exists():
        for f in sorted(lb.iterdir()):
            if (f.is_file() or f.is_symlink()) and not f.name.startswith("__"):
                found["executables"].append(f.name)
    return found


# ---------------------------------------------------------------------------
# evaluation
# ---------------------------------------------------------------------------
def evaluate(reg, offline):
    results = []

    # ---- AppImages ----------------------------------------------------
    registered = {a["name"]: a for a in reg.get("appimages", [])}
    seen = set()
    for path in discover()["appimages"]:
        name = os.path.basename(path)
        seen.add(name)
        entry = registered.get(name)
        if not entry:
            results.append({"item": name, "kind": "AppImage", "status": "UNREGISTERED",
                            "installed": "?", "upstream": "-", "download": "-",
                            "note": "On disk but absent from the registry: no recorded "
                                    "provenance, so nothing knows where it came from."})
            continue
        # An AppImage can carry no version in its filename and still be fully
        # checkable, because the upstream release knows the version. Check it the
        # same way everything else is checked rather than giving up on the name.
        installed = entry.get("version_in_name")
        kind = entry.get("check_kind")
        if not entry.get("checkable"):
            status, upstream = "UNCHECKABLE", "-"
        elif offline:
            status, upstream = "NOT CHECKED", "-"
        elif kind == "github":
            upstream = check_github(entry.get("github_repo", ""))
            if upstream is None:
                status = "NOT CHECKED"
            elif installed and normalise(upstream) == normalise(installed):
                status = "CURRENT"
            elif installed:
                status = "BEHIND"
            else:
                # No local version to compare: report upstream, do not guess.
                status = "UNVERSIONED-LOCAL"
        else:
            status, upstream = "UNCHECKABLE", "-"
        results.append({
            "item": name, "kind": "AppImage", "status": status,
            "installed": installed or "not in filename",
            "upstream": upstream or "-",
            "download": entry.get("linux_amd64_direct") or entry.get("download_url") or "-",
            "note": entry.get("note", "").strip(),
        })
    for name, entry in registered.items():
        if name not in seen:
            results.append({"item": name, "kind": "AppImage", "status": "MISSING",
                            "installed": "-", "upstream": "-", "download": "-",
                            "note": "In the registry but not on disk. It was deleted; "
                                    "remove it from the registry or restore it."})

    # ---- executables --------------------------------------------------
    om = reg.get("operator_managed", {}) or {}
    op_managed = set(om.get("items", []) if isinstance(om, dict) else om)
    for e in reg.get("executables", []):
        if e["name"] in op_managed:
            continue
        kind = e.get("check_kind")
        installed = e.get("version", "unknown")
        upstream = None
        if offline or not e.get("checkable"):
            status = "UNCHECKABLE" if not e.get("checkable") else "NOT CHECKED"
        elif kind == "pypi":
            upstream = check_pypi(e.get("pypi_package", e["name"].split()[0]))
            status = "NOT CHECKED" if upstream is None else (
                "CURRENT" if normalise(upstream) == normalise(installed) else "BEHIND")
        elif kind == "github":
            upstream = check_github(e.get("github_repo", ""))
            status = "NOT CHECKED" if upstream is None else (
                "CURRENT" if normalise(upstream) == normalise(installed) else "BEHIND")
        elif kind == "apt":
            upstream = check_apt(e.get("apt_package", ""))
            status = "NOT CHECKED" if upstream is None else (
                "CURRENT" if normalise(upstream) == normalise(installed) else "BEHIND")
        else:
            status = "UNCHECKABLE"
        results.append({"item": e["name"], "kind": "executable", "status": status,
                        "installed": installed, "upstream": upstream or "-",
                        "download": e.get("download_url") or "-",
                        "note": e.get("note", "").strip()})

    return results


ORDER = ["BEHIND", "UNVERSIONED-LOCAL", "UNREGISTERED", "MISSING", "NOT CHECKED",
         "UNCHECKABLE", "CURRENT"]

MEANING = {
    "CURRENT": "Installed version matches upstream.",
    "BEHIND": "Upstream offers something newer.",
    "UNCHECKABLE": "No way to check automatically. A known gap, not a pass.",
    "NOT CHECKED": "Check skipped, or upstream could not be reached this run.",
    "UNREGISTERED": "On disk with no recorded provenance.",
    "MISSING": "Registered but no longer on disk.",
    "UNVERSIONED-LOCAL": "Upstream version known; the local file carries no version to compare.",
}


def render(results, offline):
    L = []
    w = L.append
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    w("# ALWAYS ON — Unmanaged Software Tracking")
    w("")
    w(f"> Generated `{now_utc()}` by `scripts/build-update/track-unmanaged.py`.")
    w(">")
    w("> ```bash")
    w("> /ALWAYSON/scripts/build-update/track-unmanaged.py --markdown \\")
    w(">   --out /ALWAYSON/docs/unmanaged.md")
    w("> ```")
    w("")
    w("**Read-only.** It queries version endpoints and reads files. It installs")
    w("nothing, downloads nothing, and changes nothing.")
    w("")
    w("This exists because the operator decided these files are ours to track")
    w("(2026-10-02). They have no package manager, so a stale copy stays invisible")
    w("until it fails. Provenance is recorded in")
    w("`config/build-update/unmanaged-software.yaml`.")
    w("")

    w("## Summary")
    w("")
    w("| Status | Count | Meaning |")
    w("|---|---|---|")
    for s in ORDER:
        if counts.get(s):
            w(f"| {s} | {counts[s]} | {MEANING[s]} |")
    w("")
    behind = counts.get("BEHIND", 0)
    unreg = counts.get("UNREGISTERED", 0)
    w(f"**{behind} item(s) behind, {unreg} with no recorded provenance.** "
      f"{counts.get('UNCHECKABLE', 0)} cannot be checked automatically at all — "
      f"those are known gaps, not passes.")
    w("")

    w("## Detail")
    w("")
    w("| Item | Kind | Installed | Upstream | Status | Download | Note |")
    w("|---|---|---|---|---|---|---|")
    for r in sorted(results, key=lambda x: (ORDER.index(x["status"]), x["item"])):
        note = (r["note"] or "").replace("\n", " ")[:170]
        dl = r.get("download") or "-"
        dl_cell = (f"[link]({dl})" if dl.startswith("http") else dl)
        w(f"| `{r['item']}` | {r['kind']} | `{r['installed']}` | `{r['upstream']}` | "
          f"{r['status']} | {dl_cell} | {note} |")
    w("")

    w("## What this deliberately does not do")
    w("")
    w("- **It does not update anything.** BEHIND is a finding for a human, not a task.")
    w("- **It does not chase UNCHECKABLE items with downloads.** The AppImages with "
      "no version in the filename would need a vendor page parsed; that is a "
      "deliberate gap, recorded so its absence is visible.")
    w("- **It does not track Obsidian or Crossover.** The operator keeps track of "
      "those personally.")
    w("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(
        description="Freshness tracking for unmanaged software (read-only).")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--offline", action="store_true",
                    help="do not query upstream; report installed versions only")
    args = ap.parse_args()

    reg = load_registry()
    results = evaluate(reg, args.offline)
    text = render(results, args.offline)

    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        t = p.with_suffix(p.suffix + ".tmp")
        t.write_text(text, encoding="utf-8")
        t.replace(p)
        print(f"wrote {p}")
    else:
        print(text)

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("  " + ", ".join(f"{k} {counts[k]}" for k in ORDER if counts.get(k)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
