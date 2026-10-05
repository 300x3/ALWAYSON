---
item: LEDGER-04
action: update
evidence: |
  $ find quadlet -ipath '*archive*'
  (no output)

  $ podman ps -a --format '{{.Names}}' | grep -c -E 'archive|egress'
  0

  $ ls config/pcloud/
  replication-policy.yaml
section: 11-ledger-provenance-archive-and-ipfs
---
**Re-verified a third time, 2026-10-04.** All three checks reproduce: no
Quadlet matches `*archive*`, zero containers match `archive|egress`, and
`config/pcloud/` contains only `replication-policy.yaml`. Still blocked earlier
than §19's wording suggests — there is no `ao-egress-archive` service to hold
credentials. No credential read, printed, or exported; no replication test run.

**Stays open, and is blocked earlier than §19 suggests.** §19 frames this as
"credentials provisioned into `ao-archive`". The acceptance criteria cannot be
met as written, because **`ao-egress-archive` does not exist** — no Quadlet, no
container, no network. Only the policy file
(`config/pcloud/replication-policy.yaml`) exists, and it constrains scope without
provisioning anything.

**Credentials cannot be provisioned into a service that has no unit.** Building
that adapter is separate work outside my ownership (`quadlet/` is not my file),
so I have stopped here rather than building it.

## Naming discrepancy for the operator

§11.1 and §4.4 name the component **`ao-egress-archive`**; the LEDGER-04
acceptance criteria name it **`ao-archive`**. I have recorded
**`ao-egress-archive`** as correct, since that is the name used in the
architecture, the network table, and the approved-path table.

## Secret handling

**No credential was read, printed, copied, or exported, and no replication test
was run.** Presence-only handling applies when this is unblocked: prove an entry
exists by name and non-zero length, never its value. A non-destructive
encrypted replication test is a stop condition requiring operator approval.