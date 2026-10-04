#!/usr/bin/env python3
"""ALWAYS ON ao-build-update: plan DRY-RUN VALIDATOR. Executes nothing.

Answers one question: *if an operator approved this plan, what would it touch?*
It loads `update-plan.json`, hashes it, snapshots it, validates every step
against the verb allowlist, groups items by blast radius, and prints the
result. It never pulls, installs, edits, restarts or prompts.

THIS TOOL CANNOT APPLY ANYTHING, AND MUST NEVER BE EXTENDED TO.
----------------------------------------------------------------------
There is no code path here that pulls an image, installs a package, edits a
Quadlet, deploys a unit, or restarts a service. The only thing it writes is its
own audit record under `data/build-update/runs/`. Applying an update remains a
separate, deliberate human action through promote-image-digest.sh or an
operator-run command.

Why approval must pin to the plan HASH
--------------------------------------
`update-plan.json` is regenerated on every refresh, so the file an operator
approved yesterday is not the file a tool would run today -- the `generated`
timestamp alone changes the bytes even when no item changed. An approval
recorded against a *filename* is therefore meaningless. This tool prints the
SHA-256 and `--expect-hash` refuses to validate anything else, so an approval
can name exactly the bytes that were reviewed.

Usage:
  apply-plan.py [--plan FILE] [--json] [--expect-hash SHA256]
                [--runs-dir DIR] [--no-snapshot]

Exit: 0 well-formed, 2 usage error, 3 validation failure, 4 hash mismatch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

AO_ROOT = Path(os.environ.get("AO_ROOT", "/ALWAYSON"))
DEFAULT_PLAN = AO_ROOT / "data/build-update/update-plan.json"
DEFAULT_RUNS = AO_ROOT / "data/build-update/runs"

# Mirrors PLAN_VERBS in provenance-log.py. Duplicated deliberately rather than
# imported, so this tool still runs when provenance-log.py is broken; the test
# suite asserts the two lists agree so they cannot drift apart.
ALLOWED_VERBS = ("podman", "snap", "flatpak", "apt", "apt-get", "systemctl")
ALLOWED_SCRIPTS = ("./scripts/deploy/deploy-quadlet-domain.sh",)

SHELL_METACHARS = ";|&$`<>()\n\\\"'*?[]{}"


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_step(step, where) -> list:
    """Return a list of problems with one argv array. Empty means valid.

    A step is only valid as an argv ARRAY. A bare string is rejected outright
    rather than split, because splitting is a guess about intent, and the whole
    point of the argv schema is that no shell interpretation ever happens.
    """
    bad = []
    if isinstance(step, str):
        return [f"{where}: step is a bare string, not an argv array. A plan "
                f"step must never be executed through a shell."]
    if not isinstance(step, (list, tuple)) or not step:
        return [f"{where}: step is empty or not an array: {step!r}"]
    verb = str(step[0])
    if verb not in ALLOWED_VERBS and verb not in ALLOWED_SCRIPTS:
        bad.append(f"{where}: verb {verb!r} is not allowlisted "
                   f"({', '.join(ALLOWED_VERBS + ALLOWED_SCRIPTS)})")
    for a in step[1:]:
        s = str(a)
        if not s.strip():
            bad.append(f"{where}: empty argument")
        if any(c in s for c in SHELL_METACHARS):
            bad.append(f"{where}: argument {s!r} carries a shell metacharacter")
    # A pull must name a COMPLETE digest. An abbreviated display digest is not
    # a slow step, it is an HTTP 400 -- the first defect pinned in OPS-22.
    if verb == "podman" and len(step) > 2 and step[1] == "pull":
        ref = str(step[2])
        if "@sha256:" not in ref:
            bad.append(f"{where}: pull reference {ref!r} is not digest-pinned")
        elif len(ref.split("@sha256:", 1)[1]) != 64:
            bad.append(f"{where}: pull digest is not 64 hex characters; a "
                       f"registry will reject this with HTTP 400")
    return bad
def validate_plan(plan) -> list:
    """Structural checks on the whole plan. Empty list means well-formed."""
    bad = []
    if not isinstance(plan, dict):
        return ["plan is not a JSON object"]
    for k in ("generated", "host", "items"):
        if k not in plan:
            bad.append(f"plan has no {k!r} key")
    if not isinstance(plan.get("items"), list):
        return bad + ["`items` is not a list"]
    n_no_manual = 0
    for idx, it in enumerate(plan["items"]):
        if not isinstance(it, dict):
            bad.append(f"items[{idx}]: item is not an object")
            continue
        w = f"items[{idx}] {it.get('item', '?')}"
        if it.get("decision") not in ("eligible", "excluded"):
            bad.append(f"{w}: decision {it.get('decision')!r} is neither "
                       f"'eligible' nor 'excluded' -- an undecided item must "
                       f"never be actionable")
        # `manual` is only required where the separation actually matters: an
        # item a machine is allowed to act on. Emitting it for the 193
        # `excluded` rows buried the 26 findings that mattered under 199
        # identical lines, so the plan schema is reported once instead.
        eligible_item = it.get("decision") == "eligible"
        if eligible_item and "manual" not in it:
            bad.append(f"{w}: no `manual` key; an eligible item must separate "
                       f"prose from executable steps")
        elif not eligible_item and "manual" not in it:
            n_no_manual += 1
        steps = it.get("steps")
        if steps is None:
            bad.append(f"{w}: no `steps` key")
            continue
        if not isinstance(steps, list):
            bad.append(f"{w}: `steps` is not a list")
            continue
        if it.get("decision") == "eligible" and not steps:
            # The exact defect OPS-19 existed to remove: an item no machine can
            # act on, marked as though it could.
            bad.append(f"{w}: marked eligible but carries no executable step")
        for j, s in enumerate(steps):
            bad += validate_step(s, f"{w} steps[{j}]")
    if n_no_manual:
        bad.append(f"plan: {n_no_manual} of {len(plan['items'])} items carry no "
                   f"`manual` key. This is a schema-1 plan (prose and executable "
                   f"steps are not separated). Every eligible step in it is a bare "
                   f"string, so nothing in it is safe to hand to an executor -- "
                   f"this is OPS-19, not a per-item defect.")
    return bad


def _digest_of_pull_step(item):
    """The sha256 digest this item's own steps would actually pull, or "".

    Read from `steps` rather than from a summary column, because the summary
    column and the executable step can disagree, and when they do the step is
    what runs. Returning "" (never a guess) means a disagreement degrades to
    "not known to be coupled", which is the safe direction: the alternative
    would couple two units that share nothing.

    The full `sha256:<hex>` reference is returned, not the bare hex, so the
    caller can keep its single prefix check and there is exactly one place that
    decides what a digest looks like.
    """
    for s in (item.get("steps") or []):
        if (isinstance(s, (list, tuple)) and len(s) > 2
                and str(s[0]) == "podman" and s[1] == "pull"
                and "@sha256:" in str(s[2])):
            return "sha256:" + str(s[2]).split("@sha256:", 1)[1]
    return ""


def blast_radius(items) -> dict:
    """Group eligible items by what they share, so coupled risk is visible.

    Two units pinned to the same digest move together: if that digest is wrong,
    restarting one is a partial rollback of a change already applied to the
    other. Two units in the same Quadlet domain are restarted by one deploy
    script invocation, so a domain is one blast radius.

    The digest is read out of the item's own `podman pull` step, not out of the
    `target_digest_full` display column. The display column is what a human
    reads and it is formatted for reading; the pull step is what a machine
    would execute. Coupling is a statement about execution, so it must be
    derived from execution. `target_digest_full` is kept only as a fallback for
    a plan whose steps have been stripped by an older schema.
    """
    by_digest, by_domain = {}, {}
    for it in items:
        if not isinstance(it, dict) or it.get("decision") != "eligible":
            continue
        d = _digest_of_pull_step(it) or str(it.get("target_digest_full") or "")
        if d.startswith("sha256:"):
            by_digest.setdefault(d, []).append(it["item"])
        unit = str(it.get("unit") or "")
        if unit.startswith("quadlet/"):
            by_domain.setdefault(unit.split("/")[1], []).append(it["item"])
    return {
        "by_digest": {k: sorted(v) for k, v in by_digest.items() if len(v) > 1},
        "by_domain": {k: sorted(v) for k, v in by_domain.items() if len(v) > 1},
        "coupled_digests": len([v for v in by_digest.values() if len(v) > 1]),
        "multi_unit_domains": len([v for v in by_domain.values() if len(v) > 1]),
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Validate an update plan and report its blast radius. "
                    "Executes nothing, ever.")
    ap.add_argument("--plan", default=str(DEFAULT_PLAN))
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--expect-hash",
                    help="refuse unless the plan hashes to this SHA-256; this is "
                         "how an approval is pinned to reviewed bytes")
    ap.add_argument("--runs-dir", default=str(DEFAULT_RUNS))
    ap.add_argument("--no-snapshot", action="store_true",
                    help="do not copy the plan into the run directory")
    args = ap.parse_args()

    plan_path = Path(args.plan)
    if not plan_path.is_file():
        print(f"ERROR: no plan at {plan_path}", file=sys.stderr)
        print("       run scripts/build-update/refresh-install-log.sh first",
              file=sys.stderr)
        return 2
    try:
        raw = plan_path.read_bytes()
    except OSError as e:
        print(f"ERROR: cannot read {plan_path}: {e}", file=sys.stderr)
        return 2

    # Hash the BYTES ON DISK, never a re-serialised object. Re-serialising
    # normalises whitespace and key order, so a hash computed that way would
    # not match the bytes an operator actually reviewed.
    digest = hashlib.sha256(raw).hexdigest()

    if args.expect_hash and args.expect_hash.lower() != digest:
        print("HASH MISMATCH", file=sys.stderr)
        print(f"  approved : {args.expect_hash.lower()}", file=sys.stderr)
        print(f"  on disk  : {digest}", file=sys.stderr)
        print("  The live plan regenerates on every refresh, so the file you "
              "approved is not the file on disk. Re-read and re-approve.",
              file=sys.stderr)
        return 4

    try:
        plan = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: plan is not valid JSON: {e}", file=sys.stderr)
        return 3

    problems = validate_plan(plan)
    items = plan.get("items", [])
    eligible = [i for i in items if isinstance(i, dict)
                and i.get("decision") == "eligible"]
    radius = blast_radius(items)

    snap = None
    if not args.no_snapshot:
        rd = Path(args.runs_dir) / now_utc().replace(":", "")
        try:
            rd.mkdir(parents=True, exist_ok=True)
            snap = rd / "update-plan.json"
            snap.write_bytes(raw)
            (rd / "plan.sha256").write_text(
                f"{digest}  {plan_path.name}\n", encoding="utf-8")
        except OSError as e:
            problems.append(f"could not snapshot the plan: {e}")

    report = {
        "validated_at": now_utc(),
        "plan": str(plan_path),
        "plan_sha256": digest,
        "expected_sha256": args.expect_hash,
        "hash_matches": (args.expect_hash.lower() == digest
                         if args.expect_hash else None),
        "schema": plan.get("schema"),
        "generated": plan.get("generated"),
        "host": plan.get("host"),
        "items": len(items),
        "eligible": len(eligible),
        "excluded": len(items) - len(eligible),
        "would_execute": sum(len(i.get("steps") or []) for i in eligible),
        "manual_only": len([i for i in items if isinstance(i, dict)
                            and i.get("manual") and not i.get("steps")]),
        "blast_radius": radius,
        "snapshot": str(snap) if snap else None,
        "problems": problems,
        "valid": not problems,
        "executed": False,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"plan        : {plan_path}")
        print(f"sha256      : {digest}")
        if args.expect_hash:
            print(f"approved    : {args.expect_hash.lower()}  MATCH")
        print(f"generated   : {plan.get('generated')}   schema: {plan.get('schema')}")
        print(f"items       : {len(items)}  -> {len(eligible)} eligible, "
              f"{len(items) - len(eligible)} excluded")
        print(f"would run   : {report['would_execute']} argv steps across "
              f"{len(eligible)} item(s)")
        print(f"manual only : {report['manual_only']} item(s) need a human")
        for d, its in sorted(radius["by_domain"].items()):
            print(f"  coupled domain {d}: {', '.join(its)}")
        for dg, its in sorted(radius["by_digest"].items()):
            print(f"  coupled digest {dg[:19]}...: {', '.join(its)}")
        if not eligible:
            print("would touch: NOTHING - no item is eligible")
        else:
            print("would touch:")
            for it in eligible:
                for s in (it.get("steps") or []):
                    print(f"  {' '.join(str(x) for x in s)}")
                for m in (it.get("manual") or []):
                    print(f"  [manual] {m}")
        if snap:
            print(f"snapshot    : {snap}")
        print("EXECUTED    : nothing. This tool is a validator only.")
        if problems:
            print("")
            print(f"VALIDATION FAILED ({len(problems)} problem(s)):")
            for p in problems:
                print(f"  - {p}")
        else:
            print("validation  : OK")

    return 0 if not problems else 3


if __name__ == "__main__":
    raise SystemExit(main())