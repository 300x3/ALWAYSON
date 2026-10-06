---
item: NET-06
action: create
evidence: |
  NEW ITEM RAISED BY THIS SESSION. Found by me, caused by me, and it belongs to
  the scripts group rather than to NET, so I have not touched the script.

  scripts/build-update/ao-build-update.py resolves its output paths against
  AO_ROOT, which DEFAULTS TO THE LIVE TREE rather than to the working
  directory:

    $ sed -n '34p;138,139p' scripts/build-update/ao-build-update.py
    AO_ROOT = Path(os.environ.get("AO_ROOT", "/ALWAYSON"))
    staging = os.environ.get("AO_BUILD_UPDATE_STAGING") or str(_resolve(staging, AO_ROOT))
    audit = os.environ.get("AO_BUILD_UPDATE_AUDIT_LOG") or str(_resolve(audit, AO_ROOT))

  So running the adapter's dry-run checks from an isolated worktree writes into
  the live /ALWAYSON tree. Demonstrated, not inferred:

    $ ls -la /ALWAYSON/data/build-update/staging/acquisition-20261004T2247*.json
    acquisition-20261004T224710+0000.json     485 bytes
    acquisition-20261004T224711+0000.json     523 bytes
    acquisition-20261004T224711+0000-2.json   551 bytes
    $ tail -3 /ALWAYSON/logs/operations/build-update-audit.log
    ... three JSON audit lines at 2026-10-04T22:47:10/11+00:00

  Note the third file: the ALLOWED-PINNED case wrote TWO files because two runs
  landed in the same second and the second took a -2 suffix. Four files from
  three commands.

  WHY THIS MATTERS AND WHY IT IS NOT MINE. In production the default is
  correct and changing it could break the Quadlet's audit trail. The defect is
  that the default is unconditional, so it also applies when the script is run
  by hand from a worktree or a checkout, which is exactly what eleven
  concurrent agent sessions do when they verify things. Net effect: validation
  runs silently mutate live state while being described in proposals as checks.

  I did NOT delete the four files. §4.1 rule 3 forbids deleting without
  operator approval, they are genuine plan-mode audit records, and an audit log
  with holes in it is worse than one with extra harmless entries.

  Candidate fixes, none applied, all needing operator sign-off because each
  changes audit behaviour:
    (a) Have sessions export AO_ROOT=$PWD when running dry checks. Zero code
        change, but relies on every session remembering, and the ones that
        forget are invisible.
    (b) Make --plan write nothing outside an explicitly given path, failing
        closed if none is set. Strongest, changes existing behaviour.
    (c) Print the resolved staging and audit paths at startup so a session sees
        it is writing outside its worktree before it does.
  I would take (c) immediately and (b) eventually. I am not choosing, because
  it alters an audit trail.
section: 05-network-domains-and-controlled-external-access
---
**New item: validation scripts resolve output paths against `/ALWAYSON` by
default, so running them from an isolated worktree writes into the live tree.**

Found while re-verifying NET-01's allowlist enforcement. The three dry-run
commands every NET-01 proposal quotes as evidence each wrote an acquisition
record and an audit line into the live `/ALWAYSON` tree, because
`ao-build-update.py` defaults `AO_ROOT` to `/ALWAYSON` instead of deriving it
from the working directory.

Four files from three commands — the third case wrote two, since two runs
collided in the same second and the second took a `-2` suffix.

This is a scripts defect, not a network one, so it is reported rather than
fixed. I have not edited the script, not changed any default, and not deleted
the four files it produced: they are real audit records, rule 3 requires
approval to delete anything, and an audit log with holes punched in it is a
worse artefact than one with extra plan-mode entries.

The cheapest honest fix is to have the script print its resolved staging and
audit paths at startup, so a session sees it is writing outside its worktree
before it does. The strongest is to make `--plan` refuse to write anywhere
unless a path is given explicitly. Both change audit behaviour, so both need
the operator.