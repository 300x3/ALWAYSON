# Corda 4.14.2 Retirement and H2 Database Removal

- **Date (UTC):** 2026-09-29T04:35Z
- **Operator:** scottw (approval given in session: "delete corda 4 and its h2
  databases and we will work with corda 5")
- **Agent:** Cline
- **Outcome:** SUCCESS — Corda 4.14.2 removed, documentation corrected,
  Corda 5.2.2 on PostgreSQL `cordadb` confirmed as the sole ledger.
- **README reference:** §18.2.1

## 1. Discovery

Full-filesystem search (`find / -xdev` for `*.mv.db`, `*.h2.db`, `*.trace.db`)
found exactly one set of real H2 databases, all under
`/home/scottw/corda/network/`:

| Path | Size | Modified |
|---|---|---|
| `Notary/persistence.mv.db` | 212992 | Aug 5 22:06 |
| `PartyA/persistence.mv.db` | 204800 | Sep 26 19:08 |
| `PartyB/persistence.mv.db` | 204800 | Aug 5 22:06 |

plus three `persistence.trace.db` files.

A fourth hit, `~/.local/share/containers/storage/overlay/.../plugins/sample-database.db.mv.db`,
is sample content inside a Podman image layer. **Deliberately left untouched** —
removing it would corrupt the overlay layer and recover no user data.

## 2. Version determination (root cause of the confusion)

`unzip -p ~/corda/network/Notary/corda.jar META-INF/MANIFEST.MF`:

```
Corda-Release-Version: 4.14.2
Corda-Platform-Version: 160
Corda-Vendor: Corda Community Edition
Corda-Docs-Link: https://docs.corda.net/docs/corda-os/4.14.2
```

The H2 files were produced by **Corda 4.14.2**, not Corda 5. A separate and
unrelated Corda 5.2.2 deployment exists for the `alwayson-ledger` service
account (uid 994) at `/home/alwayson-ledger/.config` (not readable as
`scottw`).


## 3. Pre-deletion verification (read-only)

H2 2.2.224 was extracted from the Corda capsule JAR to `/tmp/h2tool`
(sha256 `b9d8f19358ada82a4f6eb5b174c6cfe320a375b5a9cb5a4fe456d623e6e55497`).
Databases were copied to `/tmp/corda4-inspect/` and queried with
`ACCESS_MODE_DATA=r;IFEXISTS=TRUE` so the originals were never opened
read-write. Original checksums were recorded before and after and were
byte-identical:

```
b83ee684ef171ac31392ce96e3f84c1b5f1fcc415f132be0d0a52dfed1c5713c  Notary/persistence.mv.db
1f1102541f27805a79fa119f4df2b42125ae4c4b57efea9688debc9f60ed0f4f  PartyA/persistence.mv.db
a55d2612ef2a700e21d56f844d506011adc382a466509fb0d0274a8a69b2320e  PartyB/persistence.mv.db
```

Row counts, identical across all three nodes:

| Table | Notary | PartyA | PartyB |
|---|---|---|---|
| VAULT_STATES | 0 | 0 | 0 |
| VAULT_LINEAR_STATES | 0 | 0 | 0 |
| VAULT_FUNGIBLE_STATES | 0 | 0 | 0 |
| VAULT_TRANSACTION_NOTES | 0 | 0 | 0 |
| STATE_PARTY | 0 | 0 | 0 |
| NODE_TRANSACTIONS | 0 | 0 | 0 |
| NODE_ATTACHMENTS | 0 | 0 | 0 |
| NODE_MESSAGE_IDS | 0 | 0 | 0 |
| NODE_NOTARY_COMMITTED_TXS | 0 | n/a | n/a |
| NODE_NOTARY_COMMITTED_STATES | 0 | n/a | n/a |
| NODE_INFOS | 3 | 3 | 3 |
| NODE_AES_ENCRYPTION_KEYS | — | 10 | — |

**Conclusion: zero ledger state, no financial records present.** Only
network-membership discovery rows and internal schema keys were populated.
`NODE_NOTARY_COMMITTED_*` exist only on the Notary node; the query was
split accordingly.

## 4. Backup (created before deletion)

`/ALWAYSON/backups/corda4-retirement-20260929T043531Z` — 772 KB, mode `go-rwx`.

- 6 H2 files (`persistence.mv.db` + `persistence.trace.db` × 3 nodes)
- Non-secret config: `node.conf`, `network-parameters` per node
- `nodeInfo-filenames.txt` and `certificates-PRESENT-NOT-COPIED.txt` per node
- 3 legacy log files
- `SHA256SUMS.txt` — 21 files, all `OK` under `sha256sum -c`

**Restore test performed:** a copy of the backed-up `PartyA` database was
reopened read-only with H2 and queried successfully, confirming the archive
is genuinely restorable rather than merely present.

**Secret handling:** certificate keystores (`nodekeystore.jks`,
`sslkeystore.jks`, `truststore.jks`) were **not** copied into the backup, per
AGENTS.md rule 5. Their former existence is recorded by filename only.

## 5. Deletion

Pre-checks: no Corda process running; no systemd unit, quadlet, or script
referenced `/home/scottw/corda`.

## 6. Documentation corrections

| File | Change |
|---|---|
| `README.md` §3.3 diagram | H2 engine panel → "CORDA 5.2.2 DLT (PG) CORE", cordadb, retirement note |
| `README.md` §3.3 prose | H2 persistence claim → `cordadb` |
| `README.md` §3.3.1 table | Removed the "H2 Database / Corda DLT Nodes" row |
| `README.md` §18.2 | **New §18.2.1** — decision, correction of the prior false record, verification data, evidence path, scope |
| `config/platform/topology-model.yaml:128` | Removed "DEFECT: ... scaffolded on H2 by mistake"; states retirement |
| `config/platform/topology-model.yaml:487` | Software string → "Corda 5.2.2 node + cordadb (PostgreSQL 18) persistence" |
| `config/platform/topology-model.yaml:520` | Drift claim corrected |
| `config/platform/version-matrix.yaml` | `postgres_version` filled in; `retired:` key added |
| `.../grafana/.../alwayson-topology.json:1213` | Subtitle corrected |
| `scripts/operations/generate-topology.py:731-733` | Drift-check text corrected |
| `TOPOLOGY/ALWAYS ON — ... v6.md` | Two stale claims corrected (persistence row + ASCII diagram) |

`TOPOLOGY/` SVG/PNG/HTML/JSON artifacts regenerated via
`python3 scripts/operations/generate-topology.py` from the corrected YAML
(21 artifacts, no errors). All YAML and JSON re-validated as parseable
afterwards. A repository-wide search for the stale claims
(`scaffolded on H2`, `H2 by mistake`, `H2 = BUG`, `persistence.mv.db`) now
returns only the backup manifest and the deliberate historical record in
README §18.2.1.

## 7. Untouched / not authorised

- Corda 5.2.2 under `alwayson-ledger` — not modified.
- `cordadb` — remains at 0 tables, unmodified. PostgreSQL access requires
  `pkexec` and was not attempted.
- §18.3 key/certificate ceremony — **not** performed. Production ledger key
  generation is operator-only per README §18.3. This remains the blocker to
  a running Corda 5.
- No service was started; no `GRANT`/`ALTER ROLE` issued.
- Unrelated pre-existing working-tree modifications were left alone.

## 8. Open items for the operator

1. **§18.3 key/certificate ceremony** — the actual blocker. `cordadb` stays
   empty until the operator runs it.
2. **Java version** — host runs OpenJDK 25.0.4.1; the Corda 5.2 scaffold
   notes Java 17 LTS. The JDK actually used by the `alwayson-ledger` install
   could not be verified (directory not readable as `scottw`). Confirm
   before runtime work.
3. **`scripts/backup/backup-corda.sh`** is still a `PENDING` stub that exits
   3. It should be implemented now that `cordadb` is the sole ledger.
4. `scripts/restore/restore-corda-test.sh` likewise remains a stub.

## 9. Errors encountered

- One `editor` call was issued with a non-existent tool name (`edit`) and was
  rejected. Re-issued correctly with `editor`.
- The first backup manifest included `SHA256SUMS.txt` in its own checksum
  list, causing a self-referential FAILED line. Regenerated excluding the
  manifest itself; 21/21 then verified OK.
- The v6.md ASCII diagram contains box-drawing characters that defeated exact
  string matching in the editor; replaced via a line-scoped Python edit that
  preserved column alignment.
- Corda documentation at `docs.r3.com` returned HTTP 403 and the Corda
  GitHub mirrors returned 404, so Corda 5 database requirements could not be
  confirmed from vendor documentation during this task. The version and
  database findings above rest on local evidence (JAR manifest, install log,
  PostgreSQL catalog) rather than vendor docs.


```
rm -rf /home/scottw/corda
```

Removed ~853 MB: the H2 databases, 3 × 112 MB `corda.jar` (4.14.2),
`nodeInfo-*` identity files, `certificates/`, `artemis/` broker state, logs.
Temp working directories (`/tmp/corda4-inspect`, `/tmp/corda4-verify`,
`/tmp/h2tool`) were removed afterwards.

Installation log (`/ALWAYSON/logs/installation/agent-install.log:641-661`)
confirms the Corda 5.2.2 scaffold provisioned PostgreSQL from its first run:

```
===== LEDGER SCAFFOLD 2026-08-23T21:22:10-07:00 =====
== provisioning cordadb on host PostgreSQL (operator-approved reuse)
verify corda-combined-worker-5.2.2.0.jar: expected=34607be9... actual=34607be9...
verify corda-cli-installer-5.2.2.0.zip:  expected=131fa2f0... actual=131fa2f0...
```

**Timeline:** Corda 4 H2 files created Aug 5; Corda 5.2.2 scaffold Aug 23.
The two were never one deployment. The prior documentation claim that
"Corda 5.2.2 was scaffolded on H2 by mistake and must be migrated onto
cordadb" was factually incorrect — no migration was required or possible,
since Corda 5 cannot read Corda 4 H2 files.
