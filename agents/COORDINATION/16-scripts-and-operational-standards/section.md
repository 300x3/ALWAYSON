# 16. Scripts and Operational Standards

## 16.1 Scripts Layout

```text
/ALWAYSON/scripts/
├── bootstrap/
│   ├── 00-inventory.sh
│   ├── 01-verify-photogrammetry-mount.sh
│   ├── 02-install-host-dependencies.sh
│   ├── 03-create-operational-layout.sh
│   ├── 04-create-podman-networks.sh
│   ├── ao-bootstrap-privileged.sh
│   └── install-heltec-udev.sh
├── deploy/
│   ├── deploy-quadlet-domain.sh
│   ├── validate-quadlet-domain.sh
│   ├── enable-domain-services.sh
│   ├── rollback-domain.sh
│   ├── ao-podman-bridge.sh
│   └── bootstrap-sales-db.sh
├── validation/
│   ├── check-photogrammetry-mount.sh
│   ├── check-open-ports.sh
│   ├── check-network-isolation.sh
│   ├── check-secrets-exposure.sh
│   ├── check-gpu-runtime.sh
│   ├── check-ledger-ingest.sh
│   ├── check-deployment-conformance.sh
│   ├── check-local-services.js
│   ├── check-logs-journals.sh
│   ├── validate-sale-receipt.sh
│   └── capture-version-matrix.sh
├── mapping/         # imagery intake, deliverable archive, manifest export
├── radio/           # heltec detect, radio-profile validate, LoRa link test
├── simulation/
├── storefront/
├── ledger/
├── backup/          # restic backup + verify; executors named in 16.1.2
├── restore/         # restore tests; executors named in 16.1.2
├── maintenance/
├── mastodon/        # deploy, federation runnerbook helpers, instance actor repair
├── operations/      # wallet bridge, service start helpers, local proxy, collectors
├── ops/             # wallet read/write helpers, kwallet provisioning
├── openclaw/        # chat relay for the ao-sales chat path
├── payment/         # ao-ingress-payment adapter, host relay, reconciliation CLI
├── sales/           # sales-domain helpers
├── lib/             # shared shell library (common.sh)
└── sync-lmstudio-readme-preset.sh
```

`mastodon/` holds `repair-instance-actor.rb` and the deploy scripts, `operations/` holds the
KWallet bridge and `start-sales-stack.sh`, `ops/` holds `wallet-read-secret.py` and
`wallet-write-secret.py`, and `lib/common.sh` is sourced by every script in
`scripts/validation/`.

`ops/` and `operations/` are distinct and both current: `ops/` is Python
D-Bus wallet tooling, `operations/` is the bash service layer.

The tree above was a **partial** listing and understated three directories.
Measured with `ls -1` on 2026-10-04, the entry counts are: `bootstrap` 7,
`deploy` 6, `validation` 11, `backup` 9, `restore` 5, `operations` 21,
`simulation` 15, `ops` 8, `mastodon` 10. `bootstrap` and `deploy` are now
listed in full above; `validation` was already complete. `backup/` and
`restore/` are named in §16.1.2 rather than expanded here, because that is
where the mapping to their systemd units matters. The remaining
count-bearing directories are intentionally summarised as one line each —
they are not part of any acceptance criterion and expanding them would make
this tree go stale on every new script.

`scripts/build-update/` is a further directory holding the software-status
generators (`provenance-log.py`, `inventory-full.py`, `refresh-install-log.sh`,
`apt_history.py`, `test_generators.py`); it predates this section and is
described in §12.5.
### 16.1.2 Backup, restore and receipt executors (measured 2026-10-04)

Measured with `ls -1` against the tree, not read off this document. This mapping
was missing: §16.1 named `backup/` and `restore/` as bare directories while §17.1
claimed active timers, so no reader could tell which file a timer actually ran.

`scripts/backup/` holds nine scripts. Which unit runs each:

| Script | Invoked by |
|---|---|
| `restic-run.sh` | `ao-restic-backup.service` — `ExecStart=/ALWAYSON/scripts/backup/restic-run.sh` |
| `verify-backup.sh` | `ao-restic-verify.service` — `ExecStart=/ALWAYSON/scripts/backup/verify-backup.sh` |
| `fetch-restic-env.sh` (in `operations/`, not `backup/`) | `ao-restic-prefetch.service` — `ExecStart=/ALWAYSON/scripts/operations/fetch-restic-env.sh /run/user/1000/ao-restic.env`. It resolves the wallet-backed restic credentials before the other two run; note it lives outside `backup/`, so `ls scripts/backup/` alone does not reveal that the backup path depends on it. |
| `dump-all-postgres.sh` | operator-invoked; dumps every PostgreSQL database in one pass |
| `backup-postgres.sh`, `backup-host-postgres.sh`, `backup-container-postgres.sh` | per-source PostgreSQL dump helpers |
| `backup-corda.sh`, `backup-photogrammetry.sh` | domain backups |
| `pcloud-restic-setup.sh` | one-time pCloud restic repository setup |

`systemd/backup/` is the only systemd tree in the repository and holds exactly six
unit files — `ao-restic-backup`, `ao-restic-verify` and `ao-restic-prefetch`, each
as a `.service` + `.timer` pair. Backup and restore are also the only subsystem
still using plain units rather than Quadlet.

```
$ find systemd -type f | sort
systemd/backup/ao-restic-backup.service
systemd/backup/ao-restic-backup.timer
systemd/backup/ao-restic-prefetch.service
systemd/backup/ao-restic-prefetch.timer
systemd/backup/ao-restic-verify.service
systemd/backup/ao-restic-verify.timer
```

`scripts/restore/` holds five scripts, and this is the honest state of the
seven-step restore test of §17.1:

| Script | §17.1 steps | State |
|---|---|---|
| `verify-hashes-and-receipts.sh` | 3–5 | **Implemented.** Recomputes `sha256sum` over each manifest's `local_storage_reference`, compares against `content_hash_sha256`, then checks receipt linkage. Exits 51 on mismatch, 2 on bad usage. |
| `restore-sales-db-test.sh` | sales DB | PENDING — `exit 3` |
| `restore-corda-test.sh` | Corda | PENDING — `exit 3` |
| `restore-mapping-artifact-test.sh` | mapping | PENDING — `exit 3` |
| `restore-simulation-artifact-test.sh` | simulation | PENDING — `exit 3` |

The seven-step test therefore has a named executor and **one real implementation,
not five**. The four PENDING scripts exit immediately with
`PENDING: <path> requires completed backups plus isolated test-path approval`; they
are honest stubs rather than broken scripts, and `bash -n` passes on all five.
Closing them needs operator approval of an isolated test path and a completed
backup, so they remain stubs until that approval exists.

There is **no restore timer**. `scripts/validation/check-logs-journals.sh` asserts
freshness of `restore-test.log` at 3650 days — a placeholder that can never fail,
not a cadence. The restore test is manual until a timer and interval are approved.

`sales/` and `validate-sale-receipt.sh` both exist. `sales/` holds seven scripts
(`add-pdf-form-fields.py`, `autofill-handoff-form.py`, `intake-kit-request-pdf.sh`,
`intake-request-record.py`, `intake-to-pdf.sh`, `issue-transaction-bundle.sh`,
`validate-transaction-bundle.sh`) and `validate-sale-receipt.sh` lives in
`validation/`. Both were previously reported missing against an earlier snapshot
of this section; that report is stale and is retracted here.


### 16.1.1 Quadlet deploy path

**Quadlet units deploy flat.** `~/.config/containers/systemd/` holds copies, not symlinks,
and Quadlet does not read a per-domain subdirectory. A unit placed in
`~/.config/containers/systemd/<domain>/` is silently ignored, so a deploy can appear to
succeed while changing nothing.

`deploy-quadlet-domain.sh`, `rollback-domain.sh`, `validate-quadlet-domain.sh`, and
`enable-domain-services.sh` all target the flat directory. `rollback-domain.sh` removes only
the named files of the requested domain; it must never `rm -r` the directory, because with
a flat layout that would delete every other domain's units.

Confirm what a deployed unit actually resolved to:

```bash
systemctl --user show ao-grafana.service -p SourcePath
```

Editing `quadlet/<domain>/*.container` in the repository changes nothing on the host until it
is deployed; the live unit is a copy.

## 16.2 Script Standard

Every script begins with:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'
```

Every script must:

- Use absolute paths.
- Validate prerequisites.
- Log in UTC.
- Avoid secrets.
- Support `--dry-run` for external or destructive activity.
- Use locks where concurrent invocation could corrupt data.
- Return meaningful exit codes.
- Avoid `eval`.
- Avoid unexamined `|| true`.
- Validate canonical paths before move or delete activity.
- Verify the photogrammetry mount before mapping activity.
- Refuse to delete outside explicitly approved and validated paths.
- Write an audit entry for operational changes.

## 16.3 Logs-Journals

All logs and journals are kept in one place:

```text
/ALWAYSON/logs/
```

`LOGS-JOURNALS/` is **not** the location; it was a name in an earlier draft and
never matched the implementation. Every writer uses `/ALWAYSON/logs/`:
`common.sh` sets `AO_LOG_DIR`, the deployed Gazebo quadlet sets
`--log-opt path=…/logs/sim-gz-server.log`, `ao-build-update` bind-mounts
`logs/operations`, and the §12.1 install step writes
`logs/installation/agent-install.log`. The earlier `LOGS-JOURNALS/` name was never implemented; §16.3 is the single statement.

Rotation: `/etc/logrotate.d/` policy staged at
`config/host/logrotate-alwayson.conf` (daily, 14 kept, no compression — see
§19.1 OPS-25). Subdirectories are not rotated; their retention is OPS-26.

Logs are classified per §4.2 and are never a place to record secrets.

`scripts/validation/check-logs-journals.sh` asserts every entry below exists
and is within its staleness budget: exit 0 pass, 1 missing, 2 stale.

| Log / journal | How often it updates | Purpose |
|---|---|---|
| `installation-journal.log` | Appended during every install or change session | The installation journal required by §4.1 rule 11. Writer: `ao_install`. |
| `operations-journal.log` | Appended on every operational change | Deploys, enable/disable, restarts, and validation-script outcomes. Writer: `ao_operation`. |
| `audit.log` | Appended on every audited operation | Immutable audit trail of operational changes and authorization decisions. Writer: `ao_audit`; `ao_audit_secret` redacts credentials. |
| `backup.log` | After every backup run | Repository, snapshot ID, and success/failure. Writer: `ao_backup_run`, called by `scripts/backup/restic-run.sh`. Dry runs are recorded as `DRY-RUN` and are not counted as backup runs. |
| `restore-test.log` | After every restore test | Source backup ID, operator, result, exceptions. Writer: `ao_restore_test`. No entries yet, and none can exist yet: four of the five scripts under `scripts/restore/` exit 3 as PENDING and `verify-hashes-and-receipts.sh` is a manual command that does not write the journal (see §16.1.2). The freshness threshold of 3650 days is a placeholder, not a cadence. |
| `gpu-runtime-check.log` | On each GPU runtime validation | Driver/CDI state and whether GPU access was granted to the workload. Writer: `scripts/validation/check-gpu-runtime.sh`. |
| `script-runs.log` | On every script invocation | Which script ran, its arguments, exit code, and dry-run status. Writer: `ao_log`. |
| `mastodon-local-proxy.log` | While the local proxy runs | Local Mastodon proxy activity and errors. |
| `meshchatx.log` | Continuously while MeshChatX runs | Pointer to the MeshChatX application log, which the application writes into its own storage dir. Not a second writer. See this document. |
| `sim-gz-server.log` | While the Gazebo server runs | Headless Gazebo simulation output. Written by the deployed quadlet. |
| `sim-foxglove-bridge.log` | While the bridge runs | Foxglove bridge output and connection state. |
| `sim-clock-bridge.log` | While the clock bridge runs | Simulation clock bridge output. |
| `web-console.log` | On console operations | Web console operations and their outcomes. |
| `lmstudio-readme-preset.sha256` | On preset change | Checksum of the LM Studio README preset, for drift detection. |
| `gpu-runtime/` | On each validation | Directory of GPU runtime validation captures, one timestamped file per run. |
| `backup/` | After every backup run | Directory of backup run records and repository metadata. |
| `operations/` | On each operational change | Directory of per-operation journals, one file per operation. Mounted into `ao-build-update`; do not relocate. |
| `installation/` | During install sessions | The install-step output log `agent-install.log` referenced by §12.1. Retained as-is. |

Logs are classified per §4.2 and are never a place to record secrets.

## 16.4 Document Coordination

`README.md` is **compiled, not hand-edited**. The source of truth is `agents/COORDINATION/`, which
holds one folder per section. Each session edits only its own file, so two sessions can
never collide on the same 4,000-line document.

| Path | Role |
|---|---|
| `agents/COORDINATION/MANIFEST.md` | The fixed section order the compiler concatenates in |
| `agents/COORDINATION/<nn>-<slug>/section.md` | One README section, beginning with its own `# N. Title` heading |
| `agents/COORDINATION/tools/split.py` | `README.md` → the section folders |
| `agents/COORDINATION/tools/compile.py` | The section folders → `README.md`; `--check` verifies without writing |

**Rules.**

1. **Edit one file.** A session owns one section folder and changes nothing else.
2. **Never edit `README.md` directly.** Edit the section file, then recompile.
3. **Keep the heading.** Each `section.md` opens with its section heading. Renaming a section
   means renaming its folder *and* its row in `MANIFEST.md`.
4. **Never renumber `19.x` item IDs.** Items are keyed by group prefix (`PLAT`, `NET`,
   `SEC`, `LEDGER`, `PAY`, `COMM`, `FIELD`, `SIM`, `OPS`) precisely so a new item cannot
   collide and adding one never renumbers another. Take the next free number in its group.
5. **New work goes in §19.1 only.** It is the single status log; never start a parallel list.
6. **Sections 1–16 stay specification** — no status, history, revision or decision dates.
   Anything current belongs in §17 or §19.
7. **Commit only your own section file.** `git add -A` sweeps in other sessions' work.

**The two roles.**

| Role | Does |
|---|---|
| Section session | Edits exactly one `section.md`; commits only that file |
| Compiler session | Runs `compile.py`, requires `--check` to report `identical`, then pushes |

**If `--check` reports `DIFFERS`**, someone edited `README.md` directly. Do not overwrite
it — that discards their work. Re-run `split.py` to fold their edit into the section file,
confirm the round trip, and continue. This has happened; it is recoverable, and the recovery
is one command.

The split/compile round trip is byte-exact, so the README can always be trusted to equal the
sum of its parts.

This folder is distinct from `COORDINATION BETWEEN AI/`, which holds session handoff
narrative. That folder is prose; `COORDINATION/` is build input.

---
