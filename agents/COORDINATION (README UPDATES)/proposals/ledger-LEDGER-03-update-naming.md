---
item: LEDGER-03
action: update
evidence: |
  $ cd /tmp/ao-sessions/wt-ledger && python3 'agents/COORDINATION (README UPDATES)/tools/compile.py' --check
  identical

  $ grep -A 12 '^| Area |' agents/COORDINATION\\\ \(README\\\ UPDATES\)/11-ledger-provenance-archive-and-ipfs/section.md
  | Area | Authoritative operational data | Network | Origin Domain |
  |---|---|---|---|
  | Sales | Sales PostgreSQL order, fulfillment, and customer-service records | `ao-sales` | `sales` |
  | Payment | Verified provider event record and normalized payment state | `ao-payment` (ingress via `ao-ingress-payment`) | `payment` (not yet in schema enum) |
  | Field | Raw packet store, telemetry spool, and mission records | `ao-field` | `field` |
  | Mapping | Validated imagery, WebODM project data, processing outputs, and deliverables | `ao-mapping` | `mapping` |
  | Vehicle simulation | Scenario definitions, run data, and result artifacts | `ao-sim-vehicle` | `sim_vehicle` |
  | Fabrication simulation | Facility/task models, safety scenarios, and result artifacts | `ao-sim-fabrication` | `sim_fabrication` |
  | Archive | Encrypted archive objects and retention records | `ao-egress-archive` | `archive` (not in schema enum) |
  | Ledger | Corda state, PKI, and the complete ledger of debits and credits | `ao-ledger-core` | `ledger` (not in schema enum) |
section: 11-ledger-provenance-archive-and-ipfs
---
Added an **Origin Domain** column to the §11.1 authority table documenting the logical domain identifiers used in the `origin_domain` field of ledger manifests (§11.5). This resolves the `sim_*` vs `ao-sim_*` naming mismatch documented in LEDGER-03:

- Network names use `ao-` prefix with hyphens: `ao-sim-vehicle`, `ao-sim-fabrication`
- Origin domains drop the prefix and use underscores: `sim_vehicle`, `sim_fabrication`

Also documented that `payment`, `archive`, and `ledger` are authoritative domains in §11.1 but are **not yet present in the manifest schema enum** (`config/ledger/manifest-schema.json`) — this remains a tracked gap for LEDGER-03.

The fix is purely in the specification documentation (my section); the schema file (`config/ledger/manifest-schema.json`) and scripts are not owned by this section and still require separate changes to add `payment`, `archive`, `ledger` to the enum and to validate `origin_domain` in `build-manifest.sh`.

**LEDGER-03 remains open** — this fix addresses only the documentation/specification clarity aspect of the `sim_*` vs `ao-sim_*` mismatch. The schema enum still lacks `payment`, `archive`, `ledger`, and `build-manifest.sh` still does not validate `origin_domain` against the closed set.