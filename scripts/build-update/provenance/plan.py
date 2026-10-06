"""Machine-readable update plans.

A plan item is either `eligible` with exact ordered argv steps, or `excluded`
with the rule that excludes it. There is no third state and no implicit default,
so an updater cannot act on an item whose status was never decided.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from .common import AO_ROOT, is_complete_digest, now_utc
from .policy import NEEDS_APPROVAL, _argv_is_safe, pin_policy
from .render import match_of



def update_steps(r, unit_path=None):
    """Exact steps to apply this update, as `{"steps": [...], "manual": [...]}`.

    The split is the whole point of the function, and it was what was missing.
    Steps used to be a flat list of STRINGS mixing two different things:

      "podman pull repo@sha256:<64>"      <- a machine could run this
      "edit Image= in quadlet/mapping/x"  <- no machine could ever run this

    An item was marked `eligible` on the strength of the first while carrying
    the second, so "eligible" did not mean "automatable" and no executor could
    tell which was which. `steps` is now a list of argv arrays drawn from the
    verb allowlist; `manual` is prose a human reads. An executor consumes
    `steps` and must refuse to act when it is empty, whatever `decision` says.

    Deliberately emits NO command rather than a broken one. The Quadlet deploy
    step is the part that is easy to forget and silently leaves the old image
    running: editing the repo unit does nothing, because
    ~/.config/containers/systemd/ holds copies, not symlinks.
    """
    via = str(r.get("via", ""))
    item = str(r.get("item", ""))
    tgt = str(r.get("rel_digest") or r.get("rel_hash", ""))
    steps, manual = [], []
    if via.startswith("container"):
        # Never build a pull command from something that is not a real, COMPLETE
        # digest. Two separate defects lived here:
        #   - a prose error string ("upstream digest unreachable (registry
        #     refused)") used as a digest, producing a plausible-looking but
        #     meaningless command;
        #   - a TRUNCATED digest. Checking only the "sha256:" prefix was not
        #     enough: `sha256:` + 12 hex characters passes that test and
        #     `podman pull repo@sha256:<12>` fails HTTP 400. The length is
        #     part of what makes the reference valid, so it is checked.
        # Emitting no command at all is strictly better than emitting a broken
        # one: a human reads the row, a script gates on `steps` being non-empty.
        if not is_complete_digest(tgt):
            return {"steps": [], "manual": []}
        repo = str(r.get("repo", "")).split(" ")[0]
        steps.append(["podman", "pull", f"{repo}@{tgt}"])
        if unit_path:
            # Rewriting Image= in a Quadlet unit is a text edit with no safe
            # mechanical form: the digest may appear in several keys and the
            # line must stay parseable. It stays prose on purpose.
            manual.append(f"set Image= in {unit_path} to {tgt}")
            steps.append(["./scripts/deploy/deploy-quadlet-domain.sh",
                          unit_path.split("/")[1]])
        else:
            manual.append(f"locate the Quadlet unit for {item} and set "
                          f"Image= to {tgt}, then deploy the domain")
        steps.append(["systemctl", "--user", "daemon-reload"])
        steps.append(["systemctl", "--user", "restart", item])
    elif via.startswith("snap"):
        steps.append(["snap", "refresh", item])
    elif via.startswith("flatpak"):
        steps.append(["flatpak", "update", item])
    elif via.startswith("apt/third-party"):
        steps.append(["apt", "install", "--only-upgrade", item])
    elif via.startswith("desktop app (apt)"):
        # The Item column is the application NAME an operator recognises
        # ("Account Wizard"), not a package name. Feeding that to apt produced
        # `apt install --only-upgrade Account` - a real command that would fail,
        # or worse, match some unrelated package. Use the owning package.
        pkg = str(r.get("repo", "")).replace("apt:", "").strip()
        if pkg:
            steps.append(["apt", "install", "--only-upgrade", pkg])
    else:
        # not dpkg-owned, vendor, local build, ROS: no mechanical step exists.
        pass
    # A step that fails the safety check is downgraded to prose rather than
    # dropped, so the operator still sees the intent but no executor can run it.
    safe = [a for a in steps if _argv_is_safe(a)]
    for a in steps:
        if a not in safe:
            manual.append("manual: " + " ".join(str(x) for x in a)
                          + "   [rejected by the argv safety check]")
    return {"steps": safe, "manual": manual}



def write_update_plan(rows, out_path):
    """Emit a machine-readable plan an automated updater can gate on.

    Every item is either `eligible` with exact ordered steps, or `excluded`
    with the rule that excludes it. There is no third state and no implicit
    default, so an updater cannot act on an item whose status was never decided.

    Schema note (OPS-19): `eligible` means **a machine can carry this out**,
    not merely "no recorded rule forbids it". Each item carries two separate
    lists:

      "steps":  [ ["podman","pull","repo@sha256:<64>"], ... ]   argv arrays
      "manual": [ "set Image= in quadlet/x.container to sha256:...", ... ] prose

    `steps` is what an executor may run, and only without a shell. `manual` is
    never executable. An executor must refuse to act when `steps` is empty,
    whatever `decision` says.
    """
    plan = {
        "generated": now_utc(),
        "host": os.uname().nodename,
        "schema": 2,
        "policy": ("This plan is ADVISORY. `eligible` means the item can be "
                   "applied mechanically from `steps` alone; `excluded` means "
                   "either a recorded project rule forbids it without explicit "
                   "operator approval, or no machine-executable step exists and "
                   "a human is required (see `manual`). `steps` entries are "
                   "argv arrays: run them WITHOUT a shell. Nothing here is "
                   "executed by this tool."),
        "items": [],
    }
    for r in sorted(rows, key=lambda x: str(x.get("item", ""))):
        verdict = match_of(r)
        # Only items needing a decision. An up-to-date item is not "excluded",
        # it simply has nothing to do, and listing 200 of them buries the list.
        if verdict in ("yes", "summary", "local"):
            continue
        item = str(r.get("item", ""))
        pol, why = pin_policy(item)
        unit = None
        if str(r.get("via", "")).startswith("container"):
            for f in sorted((AO_ROOT / "quadlet").glob("*/*.container")):
                if f.stem == item:
                    unit = str(f.relative_to(AO_ROOT))
                    break
        approval = NEEDS_APPROVAL.get(item)
        pol_key = pol
        deliberate = pol != "mechanism-default"
        sm = update_steps(r, unit)
        steps, manual = sm["steps"], sm["manual"]
        if approval:
            decision, reason = "excluded", approval
        elif pol_key == "deliberate-float":
            # Floating is itself the recorded decision. Never auto-update it,
            # whatever the upstream digest happens to say today.
            decision, reason = ("excluded",
                                f"deliberate decision on record: {why}")
        elif pol_key == "deliberate-hold" and verdict == "**NO**":
            decision, reason = ("excluded",
                                f"deliberate decision on record: {why}")
        elif not steps:
            # "eligible" is reserved for items a machine can ACTUALLY carry out.
            # An item whose only instructions are prose is not automatable, and
            # marking it eligible is what made this plan untrustworthy: a
            # consumer gating on `decision == "eligible"` had no way to tell
            # `podman pull <digest>` from `edit Image= in <file>`. Those items
            # are now excluded with a reason that says a human is required, and
            # the prose is preserved under `manual`.
            decision, reason = ("excluded",
                                "no machine-executable step exists for this "
                                "source; the remainder is prose under `manual` "
                                "and needs a human")
        elif verdict != "**NO**":
            # "?" means no upstream comparison was performed. That is not
            # evidence of being behind, so it must never authorise an update.
            decision, reason = ("excluded",
                                "no evidence of being behind; verdict is "
                                "'unknown', not 'behind'")
        else:
            decision, reason = "eligible", (why if deliberate
                                            else "no exclusion recorded")
        plan["items"].append({
            "item": item,
            "via": r.get("via", "-"),
            "verdict": verdict,
            "current": r.get("pinned", "-"),
            "target": r.get("released", "-"),
            "installed_identity": r.get("pin_hash", "-"),
            "target_identity": r.get("rel_hash", "-"),
            "target_digest_full": r.get("rel_digest") or r.get("rel_hash", "-"),
            "pin_policy": pol,
            "pin_reason": why,
            "decision": decision,
            "reason": reason,
            "unit": unit,
            # `steps` are argv arrays drawn from the verb allowlist in
            # provenance-log.py; an executor MUST refuse to run them through a
            # shell. `manual` is prose and is never executable.
            "steps": steps if decision == "eligible" else [],
            "manual": manual,
        })
    n_el = sum(1 for i in plan["items"] if i["decision"] == "eligible")
    n_ex = len(plan["items"]) - n_el
    plan["summary"] = {
        "behind": sum(1 for i in plan["items"] if i["verdict"] == "**NO**"),
        "eligible": n_el, "excluded": n_ex,
    }
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    t = p.with_suffix(p.suffix + ".tmp")
    t.write_text(json.dumps(plan, indent=2, sort_keys=False), encoding="utf-8")
    t.replace(p)
    return plan
