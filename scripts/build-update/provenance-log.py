#!/usr/bin/env python3
"""ALWAYS ON ao-build-update: complete software provenance log.

One document recording, for every piece of software on this host, WHERE IT COMES
FROM: publisher, repository, installed version, upstream version, and the exact
download link. The other reports answer "is it stale?"; this one answers "what
is it and where do I get it?" - which is the question you have to ask before you
can update anything.

READ-ONLY. Queries version endpoints and reads local state. Installs nothing,
downloads nothing, changes nothing.

Covers all five delivery mechanisms, because they each need a different kind of
"where does this come from":

    container   registry, repository, digest, and the pull reference
    snap        publisher and the snapcraft store page
    flatpak     origin remote and the flathub page
    apt         archive host, suite, component, and the package page
    direct      vendor site, version, and the download link (no feed)

Usage:
  provenance-log.py [--markdown] [--out FILE] [--html FILE] [--offline]

LAYOUT (OPS-18). This used to be a single ~2,300-line module holding
collection, policy, plan generation and rendering together; repeated edits to
that file produced malformed edits that only surfaced at compile time. The
logic now lives in the `provenance` package, split by concern:

    provenance/common.py     constants, subprocess, timestamps, normalisation
    provenance/collector.py  evidence gathering (the only mutable caches)
    provenance/policy.py     what an updater may do, and the recorded reason
    provenance/plan.py       machine-readable update plans
    provenance/render.py     rows to Markdown and HTML

This file remains the executable entrypoint AND re-exports every public name,
so `test_generators.py` and any existing caller keep working unchanged. Nothing
here holds logic - it is the argument parsing and the flag wiring.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# Re-export the whole public surface. Callers and tests have always reached
# these as `provenance_log.<name>`; keeping that working is the reason this
# shim exists at all rather than deleting the filename.
from provenance import *          # noqa: F401,F403
from provenance import collector, common, plan, policy, render   # noqa: F401
from provenance.collector import (COLLECTED, INVENTORY, cache_ttl,  # noqa: F401
                                  set_cache_ttl)
from provenance.policy import (EXCLUSIONS, NEEDS_APPROVAL,  # noqa: F401
                               PIN_POLICY, PLAN_VERBS, _argv_is_safe,
                               pin_policy, update_risk)
from provenance.render import (CSS, HEADERS, rollup_details_md,  # noqa: F401
                               rows_to_html, to_html)
from provenance.plan import update_steps, write_update_plan    # noqa: F401


def set_offline(flag: bool) -> None:
    """Set the collector's offline flag.

    `--offline` is a hard guarantee that no network call is made, so it lives
    with the code that makes the calls rather than in the entrypoint. It is
    rebound as an ATTRIBUTE here; the accessor is what every caller uses.
    """
    collector.OFFLINE = bool(flag)


def main():
    ap = argparse.ArgumentParser(
        description="Complete software provenance log (read-only).")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--html", help="also render to HTML at this path")
    ap.add_argument("--offline", action="store_true",
                    help="use cached upstream data only; never touch the network")
    ap.add_argument("--plan", help="write a machine-readable update plan JSON")
    ap.add_argument("--refresh", action="store_true",
                    help="ignore the cache TTL and re-check every upstream "
                         "value now (this is how the Released hash column is "
                         "brought up to date quickly)")
    args = ap.parse_args()

    set_offline(args.offline)
    if args.refresh and not args.offline:
        # TTL 0 makes every cached entry read as expired, so each lookup is
        # re-fetched. Failed fetches are still never written as values.
        set_cache_ttl(0)

    if not INVENTORY.exists():
        sys.exit("ERROR: run inventory-full.py first.")
    inv = json.loads(INVENTORY.read_text())
    text = render.render(inv, inv["os"]["codename"], args.offline)
    _rows = COLLECTED["rows"]
    _km = COLLECTED["kde_members"]
    behind, current, unknown, local, _summary = COLLECTED["counts"]

    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        t = p.with_suffix(p.suffix + ".tmp")
        t.write_text(text, encoding="utf-8")
        t.replace(p)
        print(f"wrote {p}")
    else:
        print(text)

    if args.plan:
        _plan = write_update_plan(_rows, args.plan)
        print(f"wrote {args.plan}: {_plan['summary']}")

    if args.html:
        rows = (collector.ubuntu_summary(inv) + collector.ros_summary(inv)
                + collector.gazebo_summary(inv) + _rows)
        title = f"ALWAYS ON - Software Status - {inv['os']['pretty']}"
        counts = (f"{len(rows)} items. {behind} behind - {current} up to date - "
                  f"{unknown} no version published - {local} local build.")
        h = Path(args.html)
        h.parent.mkdir(parents=True, exist_ok=True)
        h.write_text(rows_to_html(rows, counts, title, _km), encoding="utf-8")
        print(f"wrote {h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
