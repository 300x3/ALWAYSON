---
item: NET-01
action: update
supersedes: |
  net-NET-01-followup.md, first revision (2026-10-04, earlier this session).
  Same item, same action; the earlier revision recorded only the section-05
  self-contradiction fix and is replaced here because this revision adds the
  worktree-write finding. No other proposal is modified.
evidence: |
  THIRD PASS on NET-01. The item's status does not move: it is still blocked
  on the operator, and the block is unchanged. This records one governance
  defect that is adjacent to NET-01 but is not a NET-01 blocker.

  1. The adapter is still not enabled, and the unit state is as recorded:
    $ systemctl --user is-enabled ao-build-update
    generated
    $ systemctl --user is-active ao-build-update
    inactive
    $ podman network inspect ao-build-update --format '{{.Internal}}'
    false

  2. The allowlist is still enforced in code. Re-run this session, all three:
    $ python3 scripts/build-update/ao-build-update.py localhost/foo:latest
      localhost/foo:latest: DENIED: localhost is on the adapter deny list
    EXIT=4
    $ python3 scripts/build-update/ao-build-update.py docker.io/library/nginx:latest
      docker.io/library/nginx:latest: UNPINNED: docker.io is allowed but the
      reference carries no sha256 digest
    EXIT=4
    $ python3 scripts/build-update/ao-build-update.py \
        'docker.io/library/nginx@sha256:0000...0000'
      docker.io/library/nginx@sha256:0000...0000: ALLOWED-PINNED
    EXIT=0

  3. MY OWN ERROR, AND THE MOST IMPORTANT THING IN THIS PROPOSAL.
    Running those three checks from my worktree wrote FOUR files into the LIVE
    /ALWAYSON tree, because the script resolves its output paths against
    AO_ROOT and its default is /ALWAYSON, not the current directory:

    $ ls -la /ALWAYSON/data/build-update/staging/acquisition-20261004T2247*.json
    acquisition-20261004T224710+0000.json     (DENIED case)
    acquisition-20261004T224711+0000.json     (UNPINNED case)
    acquisition-20261004T224711+0000-2.json   (ALLOWED-PINNED case)
    $ tail -3 /ALWAYSON/logs/operations/build-update-audit.log
    ... three new JSON audit lines at 2026-10-04T22:47:10/11+00:00

    Four files, not three: the ALLOWED-PINNED case wrote two, because two runs
    landed in the same second and the second took the -2 suffix.

    Scripts can write to the live tree from an isolated worktree. The two
    earlier NET-01 proposals quote these same three commands as evidence
    without mentioning any side effect, so this has probably happened on every
    pass, not only mine.

    I did NOT delete the files. They are audit records, §4.1 rule 3 forbids
    deleting without operator approval, and an audit log with holes punched in
    it is a worse artefact than one carrying harmless plan-mode entries.

    The fix is not mine to make either: the script is not mine, the default is
    arguably correct for production, and choosing worktree-vs-live behaviour
    is an operator decision about what a validation run may touch. Raised as
    NET-06, because it is a scripts question rather than a NET-01 one.
section: 05-network-domains-and-controlled-external-access
---
**NET-01 stays open on the same two operator decisions as before. Nothing I did
this session moved it, and I did not try to.**

Unchanged and re-verified: `ao-build-update` is `generated`/`inactive` on a
plain `Internal=false` bridge, so the allowlist is enforced in the script and
unenforced at the network segment. Closing that gap needs firewall or proxy
policy, which is §4.1 rule 6 and rule 12 territory. Separate adapter
credentials are a secret acquisition, an explicit stop condition.
`ao-ingress-payment` and `ao-egress-archive` remain unimplemented.

The substantive finding this pass is **not** in my two section files at all:
running the adapter's own dry-run checks from an isolated worktree **wrote four
files into the live `/ALWAYSON` tree**, because
`scripts/build-update/ao-build-update.py` resolves its staging and audit paths
against `AO_ROOT`, which defaults to `/ALWAYSON` rather than to the working
directory. My checks were read-only in intent and were not read-only in effect.

This reaches beyond my session. Both earlier NET-01 proposals quote those same
three commands as evidence and neither mentions a side effect, which suggests
every NET pass has been writing to the live tree while describing the command as
a check. Recorded as NET-06 rather than fixed here.

I have not deleted the four files. They are legitimate plan-mode audit records,
§4.1 rule 3 requires approval to delete anything, and an audit log with holes
in it is a worse artefact than one with extra entries.

The section-05 correction from the earlier revision of this document — the
*Containment* paragraph now reading "enforced in code, unenforced at the
segment" instead of contradicting the verified evidence above it — stands, and
is still in place in the section file.

Unchanged and re-verified: `ao-build-update` is `generated`/`inactive` on a
plain `Internal=false` bridge, so the allowlist is enforced in the script and
unenforced at the network segment. Closing that gap needs firewall or proxy
policy, which is §4.1 rule 6 and rule 12 territory. Separate adapter credentials
are a secret acquisition, an explicit stop condition. `ao-ingress-payment` and
`ao-egress-archive` remain unimplemented.

The substantive new finding this pass is **not** in my two section files: running
the adapter's own dry-run checks from an isolated worktree **wrote four files
into the live `/ALWAYSON` tree**, because `scripts/build-update/ao-build-update.py`
resolves its staging and audit paths against `AO_ROOT`, which defaults to
`/ALWAYSON` rather than to the working directory. My checks were read-only in
intent and were not read-only in effect.

This matters beyond my session. Both earlier NET-01 proposals quote those same
three commands as evidence and neither mentions a side effect, which suggests
this has been happening on every NET pass and writing to the live tree each
time. I have recorded the exact files and timestamps in a new item, NET-06,
rather than fixing it here: the script is not mine, the default is arguably
correct for production, and choosing the worktree-vs-live behaviour is an
operator decision about what a validation run is allowed to touch.

I have not deleted the four files. They are legitimate plan-mode audit records,
and §4.1 rule 3 requires approval to delete anything — and an audit log with
holes punched in it is a worse artefact than one with extra entries.