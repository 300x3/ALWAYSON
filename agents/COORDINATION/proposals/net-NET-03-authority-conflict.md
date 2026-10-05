---
item: NET-03
action: update
evidence: |
  NET-03 is substantively SATISFIED. All four acceptance clauses are met and verified.
  One residual defect remains, and it is a self-contradiction between two files that
  disagree about who owns the registry.

  === CLAUSE 1: ONE AUTHORITATIVE INVENTORY, GENERATED FROM network-cidrs.yaml ===
    $ grep -c '^ao-' config/platform/network-cidrs.yaml
    14
    $ sed -n '15,17p' scripts/validation/check-network-isolation.sh
    #   check-network-isolation.sh               assert the registry against the host
    #   check-network-isolation.sh --emit-table  print the 5.1.1 inventory rows,
    #                                           derived from the registry
  The 5.1.1 inventory rows are DERIVED from the registry by --emit-table, not
  hand-maintained. The authority chain NET-03 asked for exists.

  === CLAUSE 2: THE SCRIPT MUST NOT REGENERATE THE REGISTRY FROM A HARDCODED LIST ===
  This is the clause NET-03 called out specifically, and it is met. The script reads
  the registry and asserts the host against it; it has no write path at all:

    $ grep -n 'registry' scripts/validation/check-network-isolation.sh | grep -c '>'
    0                    # no redirect writes to the registry anywhere in the file
    $ sed -n '6p' scripts/validation/check-network-isolation.sh
    # deliberately read-only: it never creates, edits, or regenerates the registry.

  Proven by execution, not by reading - mtime and digest unchanged across a full run:
    $ stat -c '%y' config/platform/network-cidrs.yaml
    2026-10-03 18:48:25.520104294 -0700
    $ AO_REGISTRY=$PWD/config/platform/network-cidrs.yaml \
        bash scripts/validation/check-network-isolation.sh
    OK: all domain networks present; isolation domains internal-only; 3 egress networks non-internal by decision; registry matches host (14 = 11 + 3)
    $ stat -c '%y' config/platform/network-cidrs.yaml
    2026-10-03 18:48:25.520104294 -0700
    $ md5sum config/platform/network-cidrs.yaml
    dd52ee77ae0f81df896382fade1dc06c

  The registry has not been written since 2026-10-03, which is what "the named
  source of truth is authoritative" means in practice.

  === CLAUSE 3: ao-html-window (10.89.14) AND ao-build-update (10.89.13) ACCOUNTED FOR ===
    $ grep '^ao-html-window\|^ao-build-update' config/platform/network-cidrs.yaml
    ao-html-window internal=true subnets=10.89.14.0/24
    ao-build-update internal=false subnets=10.89.13.0/24
  Both are registered, both are asserted by the script, and §2.2 line 37 names both
  explicitly ("Eleven are Internal=true ... plus ao-html-window. Three are
  deliberately Internal=false: ao-sales, ao-reporting-egress, ao-build-update").

  === CLAUSE 4: ONE ASSERTED COUNT, NOT THREE ===
  The old "twelve / twelve / thirteen" divergence is resolved. §19 NET-03 records it
  as stale in §19 only, and the other two now agree:

    $ grep -c '^ao-' config/platform/network-cidrs.yaml
    14
    §2.2 (02-platform-baseline:37):  "**Fourteen** ao-* networks"
    §13.3:                           "the 14 ao-* .network definitions"
    §5.1.1 emitted table:            derived from the same registry
    check output:                    "registry matches host (14 = 11 + 3)"

  Four places now read fourteen, all traceable to one file, and 14 = 11 + 3 is
  asserted arithmetically rather than asserted twice.

  === RESIDUAL DEFECT: THE REGISTRY NAMES THE WRONG OWNER FOR ITSELF ===
    $ head -1 config/platform/network-cidrs.yaml
    # Podman network CIDR registry - maintained by check-network-isolation.sh
    $ sed -n '6p' scripts/validation/check-network-isolation.sh
    # deliberately read-only: it never creates, edits, or regenerates the registry.

  The registry's own header says the script maintains it. The script's own header
  says it never writes it. Both cannot be true, and the execution evidence above
  settles which: the script never writes. The registry header is stale, and it is
  the more dangerous of the two, because it invites the next maintainer to "just run
  the script" expecting the registry to update - and it will silently not.

  PROPOSED, NOT APPLIED. config/platform/network-cidrs.yaml is not a file I own.
  This is a one-line comment fix with no functional change.
section: 05-network-domains-and-controlled-external-access
---
**NET-03 is substantively satisfied. All four acceptance clauses are met, verified by
execution rather than by reading, and I recommend the compiler close it with the one
residual defect noted below rather than leave it open for a cosmetic comment.**

The clause that mattered most was the one warning that `check-network-isolation.sh`
must not regenerate the CIDR file from a hardcoded list, because if it did the
named source of truth would not be authoritative. It does not, and I proved that by
running it rather than by reading it: the registry's mtime and md5 are byte-identical
before and after a full validation run, and it has not been written since 2026-10-03.
The script asserts the host against the registry and derives the §5.1.1 inventory
rows from it via `--emit-table`. The authority chain NET-03 asked for exists and
holds.

`ao-html-window` (10.89.14) and `ao-build-update` (10.89.13) are both registered and
both named in §2.2. The old "twelve / twelve / thirteen" divergence is gone: §2.2
says **Fourteen**, §13.3 says **14**, the emitted table derives from the registry, and
the check now asserts the arithmetic directly — `registry matches host (14 = 11 + 3)`.
Four places agree and all four trace to one file.

**The residual defect is a self-contradiction about ownership, and it is worth
keeping open for one edit.** The registry's first line says it is
`maintained by check-network-isolation.sh`; the script's own header says it is
`deliberately read-only: it never creates, edits, or regenerates the registry`. Both
cannot be true, and the execution evidence settles it — the script never writes. The
registry's header is the stale one, and it is the more dangerous of the pair, because
it invites the next maintainer to run the script expecting the registry to update,
and it will silently not. I have **not** fixed it: `network-cidrs.yaml` is not a file
I own. It is a one-line comment change with no functional effect.

**What I got wrong.** I spent the first part of this item re-deriving that the
registry has fourteen entries and that §2.2 agrees — a conclusion §19 had already
recorded, and which `check-network-isolation.sh` re-asserts on every run. The clause
I should have gone to first was the hardcoded-regeneration warning, because it was
the only clause where a *negative* result (the script does not write) was possible,
and a negative result is exactly what re-reading prose cannot establish. I also
inherited NET-02's framing that the Grafana dashboard was a NET-03 deliverable; it is
not, it is generated by `generate-topology.py` from `topology-model.yaml`, which is
why it belongs to NET-02. Two of NET-03's apparent sub-deliverables were never this
item's.
