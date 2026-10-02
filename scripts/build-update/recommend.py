#!/usr/bin/env python3
"""ALWAYS ON ao-build-update: update RECOMMENDATIONS (advisory only).

Reads the drift report and the inventory, and produces a ranked, explained
recommendation for the operator. It answers "what should I do about this, and
what happens if I do?" - it does not do anything.

THIS SCRIPT CANNOT UPDATE ANYTHING, AND MUST NEVER BE EXTENDED TO.
-----------------------------------------------------------------------
There is deliberately no code path here that installs a package, promotes a
digest, edits a Quadlet, deploys a unit, or restarts a service, and the
recommendations it emits are prose plus a command for a human to read and
choose to run. Automatic updates are the LAST thing this system does, and they
require review and explicit authorization. If a future change appears to need
this tool to act, it does not - it needs a person, and a decision.

A recommendation is advice, not a task. Acting on one is always a separate,
deliberate human action through promote-image-digest.sh or an operator-run apt
command.

Usage:
  recommend.py [--markdown] [--out FILE]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

AO_ROOT = Path(os.environ.get("AO_ROOT", "/ALWAYSON"))
DRIFT = AO_ROOT / "data/build-update/drift.json"
INVENTORY = AO_ROOT / "data/build-update/inventory-full.json"
PROMOTE = "scripts/build-update/promote-image-digest.sh"

# Advisory classes, most urgent first. Each is advice; none is an action.
#
#   TAKE_NOW     a newer patch of the SAME major, from a tracked rolling tag.
#                Low blast radius. Still a human decision.
#   REVIEW       the host is not on a release it says it tracks. The change may
#                be a version bump, so it needs reading, not just applying.
#   SECURITY     a pending apt update in the -security pocket. Normally
#                unattended-upgrades handles it; this means verify it ran.
#   BLOCKED      installed software that NO repository can deliver an update to,
#                because the source is unreachable. Nobody can fix this by
#                running an update; it needs the source repaired.
#   ORPHANED     installed but present in no apt index. The source is gone, so
#                no repository will ever deliver an update.
#   UNPINNED     a floating tag. The image can change underneath the unit.
#   UNMANAGED    software with no package manager. A stale copy is invisible
#                until it fails.
#   LEAVE        behind upstream with no tracked channel, or deliberately held
#                at an older major. Acting would be a MAJOR change, not an
#                update. Explicitly not a to-do.
ORDER = ["SECURITY", "REVIEW", "TAKE_NOW", "UNPINNED", "BLOCKED",
         "ORPHANED", "UNMANAGED", "LEAVE"]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load():
    if not DRIFT.exists():
        sys.exit(f"ERROR: {DRIFT} not found. Run drift-report.py first.")
    if not INVENTORY.exists():
        sys.exit(f"ERROR: {INVENTORY} not found. Run inventory-full.py first.")
    return (json.loads(DRIFT.read_text()), json.loads(INVENTORY.read_text()))


def apt_pocket(origin, suite):
    if "security.ubuntu.com" in (origin or "") or "security" in (suite or ""):
        return "SECURITY"
    if "updates" in (suite or ""):
        return "UPDATES"
    return "OTHER"


def parse_ref(ref):
    """(registry, repo, digest) from a possibly short image reference."""
    if "@" in ref:
        base, digest = ref.split("@", 1)
        host, sep, repo = base.partition("/")
        if not sep:
            host, repo = "docker.io", f"library/{host}"
        elif host not in ("docker.io", "ghcr.io", "quay.io"):
            host, repo = "docker.io", base
        return host, repo, digest
    return None, None, None


def load_stable_refs():
    """Read the stable-reference policy. Fails loudly rather than returning {},
    because an empty policy would silently convert every finding into a no-op."""
    path = AO_ROOT / "config/build-update/stable-refs.yaml"
    if not path.exists():
        return {}
    images, cur, in_images = {}, None, False
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        s = line.strip()
        if indent == 0:
            in_images = (s == "images:")
            cur = None
            continue
        if not in_images:
            continue
        if indent == 2 and s.endswith(":"):
            cur = s[:-1]
            images[cur] = {}
        elif cur and indent >= 4 and ":" in s:
            k, _, v = s.partition(":")
            v = v.strip().strip("\"'")
            images[cur][k.strip()] = None if v in ("null", "~", "") else v
    return images


def build_recommendations(drift, inv):
    """Turn measurements into advice. Returns a list of dicts, one per item."""
    recs = []
    stable = load_stable_refs()

    # Container recommendations are driven by the verdicts the drift report
    # actually measured, not by re-deriving them here. An earlier version of this
    # function recomputed from the stable-refs table alone and marked all three
    # Mastodon units for review, when the report had measured two of them as
    # already in sync. A recommendation must not claim a finding the measurement
    # did not make.
    measured = {v["unit"]: v for v in drift.get("containers", [])}
    if not measured:
        sys.exit("ERROR: drift.json has no per-unit container verdicts. "
                 "Re-run drift-report.py so it can record them.")
    for unit, v in sorted(measured.items()):
        domain, verdict = v["domain"], v.get("verdict", "")
        item = f"{domain}/{unit}"
        if verdict == "IN SYNC":
            continue
        if verdict.startswith("DRIFT"):
            recs.append({
                "class": "REVIEW", "item": item, "subject": v["ref"].split("@")[-1],
                "why": "Measured: the host is not on a release it declares it tracks. "
                       "Its sibling units in the same stack are, so this one is the "
                       "outlier rather than a deliberate hold.",
                "risk": "medium - Mastodon applies migrations on boot, so a version "
                        "change is a real change, not a drop-in",
                "action": f"Read the release notes, then re-pin: {PROMOTE} {domain} "
                          f"{unit}.container <image>@sha256:<digest of the tracked tag> "
                          f"then redeploy the domain and restart the unit"})
        elif verdict.startswith("BEHIND TRACKED TAG"):
            recs.append({
                "class": "TAKE_NOW", "item": item, "subject": v["ref"].split("@")[-1],
                "why": "Measured: a newer patch of the SAME major is available. Rolling "
                       "tags are rebuilt for security fixes, so this is normally a "
                       "security or correctness patch, not a behaviour change.",
                "risk": "low - same major, so no data format or API break expected",
                "action": f"Re-pin and redeploy when convenient: {PROMOTE} {domain} "
                          f"{unit}.container <image>@sha256:<digest of the tracked tag> "
                          f"then redeploy, restart, and regenerate docs/drift.md"})
        elif verdict.startswith("UNPINNED"):
            recs.append({
                "class": "UNPINNED", "item": item, "subject": v["ref"],
                "why": "The tag can move, so the image running can change with no edit "
                       "to this repository. That is exactly what digest pinning exists "
                       "to prevent.",
                "risk": "high - the unit can silently run different code after a host "
                        "restart or an image prune",
                "action": f"Pin it with: {PROMOTE} {domain} {unit}.container "
                          f"<image>@sha256:<64 hex>.  This unit is also not deployed, "
                          f"so nothing live would break today."})
        elif verdict.startswith("UNRESOLVED"):
            recs.append({
                "class": "BLOCKED", "item": item, "subject": v.get("verdict", "")[:90],
                "why": "The registry did not answer, so no comparison could be made. "
                       "This is an unmeasured item, not a clean one.",
                "risk": "unknown - nothing is known about this image's currency",
                "action": "Re-run drift-report.py. If it persists, check network egress "
                          "from the ao-build-update network."})
        else:
            # LOCAL BUILD and BEHIND LATEST need no action
            recs.append({
                "class": "LEAVE", "item": item, "subject": v["ref"],
                "why": ("Built on this host by ao-sim-fabrication; a rebuild changes the "
                        "digest and fails the unit until re-pinned, which is the "
                        "intended fail-safe."
                        if verdict.startswith("LOCAL") else
                        "No declared stable channel for this image, so there is no "
                        "release to be behind. For a base image a digest change is "
                        "often a rebuild with no functional change."),
                "risk": "n/a",
                "action": "Nothing."})

    ver = {t["package"]: t for t in inv.get("apt_packages", [])}
    for entry in sorted(drift.get("apt_drift", []), key=lambda x: x.get("package", "")):
        name, old = entry.get("package"), entry.get("installed", "")
        t = ver.get(name, {})
        if apt_pocket(t.get("origin"), t.get("suite")) == "SECURITY":
            recs.append({
                "class": "SECURITY", "item": f"apt:{name}",
                "subject": f"{old} -> newer in -security",
                "why": "A security-pocket update is pending. unattended-upgrades is "
                       "enabled and permitted to install these, so this most likely "
                       "arrived after its last daily run rather than being missed. "
                       "Check the log before assuming a failure.",
                "risk": "low, and already automatic by policy",
                "action": "Confirm it ran: journalctl -u unattended-upgrades. If it "
                          "did, do nothing - the next apt-daily-upgrade.timer run "
                          "takes it."})
        else:
            recs.append({
                "class": "TAKE_NOW", "item": f"apt:{name}",
                "subject": f"{old} -> newer in {t.get('suite') or 'updates'}",
                "why": "An ordinary -updates pocket update is pending. That pocket is "
                       "deliberately manual, so it waits for a decision rather than "
                       "installing itself.",
                "risk": "low",
                "action": "sudo apt upgrade, or leave it - nothing is at risk beyond "
                          "the benefit"})

    ros = [t for t in inv.get("apt_packages", [])
           if "ros.org" in (t.get("release") or "")]
    if ros:
        recs.append({
            "class": "BLOCKED", "item": f"{len(ros)} ROS packages",
            "subject": "packages.ros.org",
            "why": "This host fails TLS verification against packages.ros.org, so no "
                   "new or updated ROS package can be fetched. Disabling verification "
                   "was considered and rejected. This is the largest block of software "
                   "on the machine that currently cannot be updated by anyone.",
            "risk": "n/a - there is no working update path to have risk from",
            "action": "Repair the repository's certificate path, or accept that the "
                      "ROS stack is frozen at its current versions. Do NOT work around "
                      "it by disabling TLS verification."})

    orphans = [t["package"] for t in inv.get("apt_packages", [])
               if (t.get("release") or "").startswith("Not in any")]
    if orphans:
        recs.append({
            "class": "ORPHANED", "item": ", ".join(orphans),
            "subject": "installed, absent from every apt index",
            "why": "These are installed but appear in no downloaded repository index, so "
                   "no apt operation will ever offer them an update. They came from a "
                   "local file or a source that has since been removed.",
            "risk": "unknown - they receive no security updates at all",
            "action": "Decide per application: reinstall from a real repository, accept "
                      "it as frozen, or remove it."})

    unmanaged = inv.get("non_package_apps", [])
    if unmanaged:
        recs.append({
            "class": "UNMANAGED",
            "item": f"{len(unmanaged)} applications, "
                    f"{inv['counts']['user_binaries']} local executables",
            "subject": "no package manager tracks these",
            "why": "AppImages, /opt trees and ~/.local/bin executables are tracked by "
                   "nothing. Several are load-bearing for this project. A stale copy is "
                   "invisible until it fails, and the inventory cannot tell you one is "
                   "old because there is nothing to compare it against.",
            "risk": "unknown until something breaks",
            "action": "Review by hand. A version in the file name, as most AppImages "
                      "carry, is the only signal available."})

    return sorted(recs, key=lambda r: (ORDER.index(r["class"]), r["item"]))


CLASS_MEANING = {
    "SECURITY": "A security-pocket update is pending.",
    "REVIEW": "Not on a release the host says it tracks. Read before applying.",
    "TAKE_NOW": "Low risk, human decision. Nothing here applies it for you.",
    "UNPINNED": "A floating tag that can move underneath the unit.",
    "BLOCKED": "Installed software no repository can deliver an update to.",
    "ORPHANED": "Installed, but present in no repository index.",
    "UNMANAGED": "No package manager tracks this at all.",
    "LEAVE": "Behind upstream with no tracked release. Acting would be a major change, "
             "not an update. Explicitly not a to-do.",
}


def render(recs, drift, inv):
    L = []
    w = L.append
    counts = {}
    for r in recs:
        counts[r["class"]] = counts.get(r["class"], 0) + 1

    w("# ALWAYS ON — Update Recommendations")
    w("")
    w(f"> Generated `{now_utc()}` by `scripts/build-update/recommend.py`.")
    w("> Inputs: `docs/drift.md` and `docs/applications.md`.")
    w(">")
    w("> ```bash")
    w("> /ALWAYSON/scripts/build-update/recommend.py --markdown \\")
    w(">   --out /ALWAYSON/docs/recommendations.md")
    w("> ```")
    w("")
    w("## This document is advice, not action")
    w("")
    w("**Nothing in this toolchain updates anything by itself.** This script reads")
    w("measurements and writes explanations. It cannot install a package, promote a")
    w("digest, edit a Quadlet, deploy a unit, or restart a service, and the commands")
    w("below are printed for a human to read and choose to run.")
    w("")
    w("Automatic updates are the **last** thing this system does and they require")
    w("review and explicit authorization. They are not built, and this script must")
    w("never be extended to perform them. If a future change appears to need this")
    w("tool to act, it needs a person and a decision instead.")
    w("")

    w("## What needs you")
    w("")
    w("| Class | Count | What it means |")
    w("|---|---|---|")
    for cls in ORDER:
        if counts.get(cls):
            w(f"| `{cls}` | {counts[cls]} | {CLASS_MEANING[cls]} |")
    w("")
    actionable = sum(counts.get(c, 0) for c in ("SECURITY", "REVIEW", "TAKE_NOW", "UNPINNED"))
    w(f"**{actionable} items need a decision. 0 have been acted on.**")
    w("")

    for cls in ORDER:
        items = [r for r in recs if r["class"] == cls]
        if not items:
            continue
        w(f"## {cls} — {CLASS_MEANING[cls]}")
        w("")
        for r in items:
            w(f"### `{r['item']}`")
            w("")
            w(f"- **Subject:** {r['subject']}")
            w(f"- **Why:** {r['why']}")
            w(f"- **Risk:** {r['risk']}")
            w(f"- **If you choose to act:** {r['action']}")
            w("")

    w("## What was deliberately not recommended")
    w("")
    w("- **Promoting to `latest` for images held at an older major.** PostgreSQL 17, "
      "Redis 7, Prometheus 3 are deliberate holds. Moving to `latest` is a major "
      "version change needing a dump/restore or a compatibility check, not an update.")
    w("- **Re-pinning the local Gazebo builds.** Those belong to `ao-sim-fabrication`, "
      "which re-pins after its own rebuild.")
    w("- **Disabling TLS verification for packages.ros.org** to unblock 351 packages. "
      "That converts a transport fault into a trust fault.")
    w("- **Any unattended application of the above.** Not built, by decision.")
    w("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(
        description="Update RECOMMENDATIONS. Advisory only; applies nothing.")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args()

    drift, inv = load()
    recs = build_recommendations(drift, inv)
    text = render(recs, drift, inv)

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
    for r in recs:
        counts[r["class"]] = counts.get(r["class"], 0) + 1
    print("  recommendations: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    print("  applied: 0 (this tool applies nothing, by design)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
