---
item: OPS-20
action: close
evidence: |
  $ AO_ROOT=$PWD python3 scripts/build-update/apply-plan.py --no-snapshot
  plan        : /tmp/ao-sessions/wt-ops-b/data/build-update/update-plan.json
  sha256      : b753e5dab017df1be539b4b86e26713cc1293d9cde1c034ebb376f78aac9453f
  generated   : 2026-10-04T16:55:20+00:00   schema: 2
  items       : 224  -> 0 eligible, 224 excluded
  would run   : 0 argv steps across 0 item(s)
  would touch: NOTHING - no item is eligible
  EXECUTED    : nothing. This tool is a validator only.
  validation  : OK

  $ AO_ROOT=$PWD python3 scripts/build-update/apply-plan.py --no-snapshot \
        --expect-hash 0000000000000000000000000000000000000000000000000000000000000000
  MISMATCH_EXIT=4
  HASH MISMATCH
    approved : 0000000000000000000000000000000000000000000000000000000000000000
    on disk  : b753e5dab017df1be539b4b86e26713cc1293d9cde1c034ebb376f78aac9453f
section: 12-host-installation-and-configuration
---
`scripts/build-update/apply-plan.py` validates a plan without executing
anything, and prints what an updater *would* touch: eligible items, argv step
count, items that need a human, and the target set. Exit codes are `0`
well-formed, `2` usage, `3` validation failure, `4` hash mismatch. §12.5.4
documents it.

The `--expect-hash` flag is the part that makes it usable for approval. The
plan regenerates on every refresh and the `generated` timestamp alone changes
its bytes when no item changed, so **the file an operator approved is not the
file a tool would run**. `--expect-hash` refuses anything but the approved
bytes, and `TestVerbAllowlistAgreesAcrossFiles` asserts the verb allowlist is
identical in the validator and the generator.

**The trap, recorded because it cost real time and would mislead the next
agent.** The validator defaults `AO_ROOT` to `/ALWAYSON`, so running it from a
worktree silently validates **the live main-repo plan, not your worktree's**,
and prints a plausible result. A first run of mine reported 199 items and
schema 1 while the worktree plan held 224 items and schema 2. Always pass
`AO_ROOT=$PWD` and check the `plan :` line against the file you meant.

The same class of bug existed literally in `refresh-install-log.sh`, whose
summary-report heredoc opened a hardcoded
`/ALWAYSON/data/build-update/update-plan.json` while the surrounding script
honoured `AO_ROOT`; it now takes the path as `sys.argv[1]`.

**Still-open, and deliberately not done here:** the *live* `/ALWAYSON` plan is
still schema 1 (193 of 199 items carry no `manual` key), so the validator exits
**3** against it with 33 problems. Regenerating it is one
`./scripts/build-update/refresh-install-log.sh`, but that rewrites tracked
documents and is an operator action, not a silent side effect of a validation
change.