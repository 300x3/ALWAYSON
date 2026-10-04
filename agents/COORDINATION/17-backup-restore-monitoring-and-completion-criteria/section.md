# 17. Backup, Restore, Monitoring, and Completion Criteria

## 17.1 Backup and Restore Policy

**Target policy: 3-2-1** — three copies, two media types, and one off-host or
off-site copy.

What is actually backed up, and what is outstanding, is status and lives in §19.1 and
§19.1 (OPS). This section is the policy only.

| Copy | Where | Requirement |
|---|---|---|
| Primary | Live system | — |
| Backup | Encrypted restic repository outside the data path | A successful snapshot, verified by hash |
| Off-site | pCloud, as the restic destination | A second repository, disjoint from the host |

Two consequences to be aware of. First, the restic repository is on the same
machine as the data it protects, so it does not survive loss of this host. Second,
`ao-egress-archive` is not a substitute: per §11.6 it is a sale-transfer store
with no restore duty.

Both statements were re-measured on 2026-10-03 and the first is now only
half-true, so it is corrected here rather than left to drift:

| Path | Device id | Physical media | Status |
|---|---|---|---|
| `/ALWAYSON` (the data) | 66306 | root disk | live |
| `/var/backups/alwayson-restic` (local repo) | 66306 | root disk | **same device as the data** |
| `/media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS` | 2049 | separate media | off-host repository, exists and verifies |

The 3-2-1 target is therefore **partially met**: copy two is still on the root
disk, but a genuinely host-disjoint copy now exists on separate media inside the
running pCloud sync root, which replicates without a separate rclone remote. It
is deliberately **not scheduled** — no timer, no cron, no reference from
`restic-run.sh` — so it holds a single snapshot rather than a series. Until it is
scheduled it mitigates total disk loss but does not satisfy "one off-site copy"
in the sense the policy intends. Enabling it is an operator decision.

| Frequency | Required activity |
|---|---|
| Continuous or 15-minute where enabled | Database WAL/archive strategy for critical recovery objectives |
| Hourly incremental | Configuration, manifests, sales records, field telemetry, current project data |
| Daily | PostgreSQL dumps for `salesdb`, `mastodon`, `webodm`, and `cordadb` when active; Corda backup; mapping manifests; simulation exports; storefront releases |
| Weekly | Repository integrity check. Off-host copy validation applies only once a pCloud repository exists |
| Monthly | Isolated restore test |
| Quarterly | Full disaster-recovery exercise |

Restore testing must:

1. Restore to an isolated test path or test host.
2. Validate database integrity.
3. Recalculate artifact hashes.
4. Compare hashes with stored manifests.
5. Verify associated Corda receipt/manifests where available.
6. Record operator, source backup ID, result, and exceptions.
7. Alert on failure.

### 17.1.1 Named executors

Every row of the frequency table above has a named executor. §16.1 lists
`scripts/backup/` and `scripts/restore/` as directories; these are the files in
them and the units that run them.

| Duty | Executor script | Unit | Timer | Cadence |
|---|---|---|---|---|
| PostgreSQL dumps, all domains | `scripts/backup/dump-all-postgres.sh` | `ao-db-dump.service` | `ao-db-dump.timer` | 03:00 daily |
| Restic backup of approved paths | `scripts/backup/restic-run.sh` | `ao-restic-backup.service` | `ao-restic-backup.timer` | 03:30 daily |
| Repository integrity check | `scripts/backup/verify-backup.sh` | `ao-restic-verify.service` | `ao-restic-verify.timer` | Sun 04:30 |
| Seven-step restore test | `scripts/restore/restore-restic-drill.sh` | none yet — see below | none yet | manual; **OPS-24 stays open until a timer exists** |

**The seven-step contract has an executor: OPS-04 closed 2026-10-04.** The
requirement is not owned by the `check-*.sh` validators — those verify the
installed state, and none of them opens a repository or restores anything. It is
owned by `scripts/restore/restore-restic-drill.sh`, one script, one function per
step, each printing a `STEP n:` banner. The mapping is not a claim about intent,
it is the script's own control flow:

| §17.1 requirement | Implemented at | How it is proved to be able to fail |
|---|---|---|
| 1. Restore to an isolated path or host | L77 `restic restore --target "$scratch_abs"` | Three refusals, all reproduced 2026-10-04 (below) |
| 2. Validate database integrity | L84 gzip `-t` plus a 1024-byte floor per dump | A truncated or empty dump increments `db_bad`, which forces `result=FAIL` |
| 3. Recalculate artifact hashes | L104 `sha256sum` over every restored file | Writes `.drill-hashes.txt`; count is printed and asserted against the find |
| 4. Compare with stored manifests | L110 per-file compare against the **live** tree | Three buckets: drift, suspect (mtime older than snapshot), live-only. `suspect > 0` forces `result=FAIL` |
| 5. Verify Corda receipts/manifests | L162 finds `pending-ledger-submissions` manifests | Prints an explicit "path-set observation, not a pass" when zero are found |
| 6. Record operator, ID, result, exceptions | L170 prints operator, snapshot, repo and all counters | The `result=` line is the only value step 7 branches on |
| 7. Alert on failure | L179 non-zero exit plus an operator-facing instruction | Exit 1 is what any caller or unit would detect |

**One honest deviation, recorded rather than smoothed over.** §17.1 step 4 says
"compare hashes with stored manifests". There is no stored per-file manifest of
the backed-up set — measured: `find artifacts -maxdepth 2 -name '*.sha256*'`
returns only three upstream Corda download checksums
(`artifacts/corda-5.2.2/*.sha256sum`), which are vendor checksums for jars and
packages, not a manifest of what restic backed up. The drill therefore compares
the restored tree against the **live** tree, which answers a different question:
*did anything change since the snapshot*, rather than *does the snapshot match a
recorded baseline*. That is arguably the more useful question for a restore drill
and it is stricter about corruption, because the suspect-bucket test can fail
where a manifest comparison would only report a mismatch. But it is not the
requirement's wording, and inventing a baseline manifest would mean new backup
behaviour, which is OPS-09's decision and not this session's.

`install-backup-schedule.sh` installs the two root-level restic units. The
`ao-db-dump` timer is armed only during a graphical session because host-database
passwords come from KDE Wallet, so a pre-login firing could only fail;
`Persistent=true` catches a missed slot at the next login.

**The restore test has an executor but no cadence.** The drill script exists and
has been run by hand (§17.4), but nothing schedules it, so §17.1's "Monthly"
requirement is unmet. Adding a timer is a small change that is deliberately not
made here: see OPS-24 in §19.1.

### 17.1.2 Recovery point and recovery time objectives

Stated per data class, because a single number would be a fiction. RPO is the
data loss a failure may cause; RTO is how long the class may be unavailable.
Both are bounded by the executors above, so they change if the schedule does.

| Data class (§4.2) | Backup mechanism | **RPO** | **RTO** | Bounding executor |
|---|---|---|---|---|
| Secret — KDE Wallet entries | **None — not backed up** | **Total loss** | Re-provision by operator | n/a — see the warning below |
| Sensitive — ledger, Corda, customer data | restic path set + nightly dumps | 24 h | 4 h | `restic-run.sh`, `dump-all-postgres.sh` |
| Internal operational — databases | Nightly `pg_dump` (`salesdb`, `mastodon`, `webodm`, `metabase`, `grafana`) | 24 h | 2 h | `ao-db-dump.timer` |
| Internal operational — config, manifests, artifacts | restic, daily | 24 h | 1 h | `ao-restic-backup.timer` |
| Public — storefront, product data | restic, daily | 24 h | 1 h | `ao-restic-backup.timer` |

**KDE Wallet is not backed up and that is a deliberate policy, not an
oversight.** Restoring a wallet would mean restoring credential material into a
new host, which §4.1 rule 7 and §4.3 forbid. The consequence must be stated
plainly: **loss of this host is loss of every stored credential**, and recovery
depends on the operator re-provisioning them from an out-of-band record. The
RPO for the secret class is therefore total loss, and no amount of backup work
changes that without an operator decision to the contrary.

No WAL or continuous archiving is configured, so no class achieves an RPO better
than 24 hours. The §17.1 row proposing "continuous or 15-minute" WAL for critical
recovery objectives is **aspirational and not implemented**; it is the reason
every RPO above is 24 h rather than minutes.

### 17.1.3 Restore ordering

Filesystem and database restores are not independent. `pg_dump` output is
captured into `backups/postgres/<role>/` and is then itself backed up by restic,
so a correct restore is:

1. Restore the **repository** to an isolated path. Never over the live tree.
2. Restore **filesystem paths** (`config`, `artifacts`, `backups/`).
3. Restore **databases** from the restored `backups/postgres/*.sql.gz`, using
   `psql`/`pg_restore` against a target cluster.
4. **Recreate roles before loading**, because `pg_dump --no-owner
   --no-privileges` (as `backup-host-postgres.sh` uses) emits no `CREATE ROLE`,
   so the dump assumes the roles already exist.
5. **Re-provision credentials** from KDE Wallet. A dump restores data, not
   access, and the wallet is not in any backup (§17.1.2).
6. **Re-verify hashes** against the live tree and the restored dumps.

Step 4 is the one that is easy to miss and is called out because
`backup-host-postgres.sh` deliberately strips ownership: a restore that skips it
fails at the first object grant, not at the first table.

#### 17.1.4 The backup journal recorded a stale snapshot ID

Found while proving the drill, and it is the most consequential defect this
session fixed. **The journal disagreed with reality about which snapshot was
created**, which undermines the evidence every restore decision rests on.

`/ALWAYSON/logs/backup.log` showed the same ID on three consecutive runs:

```
2026-10-03T03:24:50+00:00 actor=root script=restic-run.sh snapshot=548d9910 result=OK restic backup completed
2026-10-03T10:40:03+00:00 actor=root script=restic-run.sh snapshot=548d9910 result=OK restic backup completed
2026-10-03T15:12:25+00:00 actor=root script=restic-run.sh snapshot=548d9910 result=OK restic backup completed
```

`journalctl -u ao-restic-backup.service` for the same runs showed restic's own
output naming two completely different snapshots:

```
Oct 03 03:40:03 restic-run.sh[2146371]: snapshot e79edfbf saved
Oct 03 08:12:24 restic-run.sh[2900245]: snapshot fbc25f93 saved
```

The cause is the way the ID was extracted. `restic snapshots --latest 1 --json`
does **not** return one snapshot — it returns **one snapshot per path group**.
`restic-run.sh` passes 11 paths in a single `restic backup` invocation, and where
snapshots with *different* path sets exist in the same repository, that array has
one element per group, each from a different timestamp. `grep … | head -1` then
takes **array position 0**, not the newest snapshot.

Measured on a scratch repository, 2026-10-03:

```
elements: 2
 idx 0 b26bb566 20:21:10 paths=[full, proof] tags=[alwayson]
 idx 1 63b251ca 20:21:13 paths=[proof]        tags=[alwayson-offsite-proof]
what the OLD code recorded (head -1):  b26bb566   <- the OLDER snapshot
what the NEW code records:             b26bb566   <- correct for tag "alwayson"
TRUTH: newest snapshot in repo:        63b251ca
```

The fix in `scripts/backup/restic-run.sh` selects by **maximum `time` field**
rather than array position, and filters to the run's own `--tag alwayson` so a
manually-seeded proof snapshot cannot be mistaken for the nightly run. Verified
in the same experiment: the old pipeline reports `b26bb566` where the repository
truth is `63b251ca`.

The deeper lesson, and the reason it is written down rather than just patched:
**a journal that is generated by re-querying the repository is not a record of
what happened.** restic prints `snapshot <id> saved` on stdout; that string is the
authoritative answer and should be what is journalled. Re-deriving the ID after
the fact is what allowed a stale value to survive three runs unnoticed.

**The journal has not been corrected.** The three wrong lines above are historical
evidence of a real defect and rewriting them would destroy the only trace of it.
The fix applies to future runs; the first run after deployment is the evidence
that it works.

## 17.2 Monitoring

Monitoring runs in `ao-admin`, which has no VPN, no explicit allowlist and no public
exposure. Its only permitted output is the Grafana dashboard and the Metabase reports.

The split of purpose between Prometheus, Grafana and Metabase is specified in §3.3.
Prometheus is the security instrument and is independent of the other two in both
directions; Grafana presents dashboards and metrics; Metabase produces reports.

Monitor at minimum:

| Component | Required metrics |
|---|---|
| Host | CPU, RAM, storage health, disk usage, temperature, GPU state, kernel errors |
| Podman/systemd | Unit state, restart loops, health, image digest |
| Mapping | Queue depth, failures, duration, disk space, CPU/GPU use |
| Field | Packet rate, RSSI, SNR, retries, replay rejections, spool depth, gateway uptime |
| Sales | Payment-verification failures, receipt failures, orders, API latency |
| AI/community | Model latency, request count, GPU use, approval queue, OAuth failures |
| Vehicle simulation | Scenario success, SITL/ROS/Gazebo health, result export |
| Fabrication simulation | Task state, collision/safety events, result export |
| Ledger | Corda health, ingest failures, certificate expiry, backup age |
| Backup | Last success, repository health, restore-test result, queue age |

Alerts must cover disk pressure, backup failure, failed restore tests, container
restart loops, unexpected listeners, failed payment verification, radio
disconnection, WebODM backlog, GPU contention, expired certificates, and denied
cross-domain traffic.

### 17.2.1 Alerting component and routing

The alerting component is **Prometheus rule evaluation**, not Alertmanager.
Measured 2026-10-03: there is no Alertmanager container, no Alertmanager image,
and no Alertmanager receiver configured anywhere in the repository. This is
consistent with §3.3, which makes Prometheus the *security instrument* whose
output is the Grafana dashboard only — an independent Prometheus that pages a
human would contradict that isolation.

The consequence is stated rather than hidden: **rules evaluate and become
visible in Prometheus/Grafana, but nothing is delivered to an operator who is not
looking.** For a host whose only intended output is a dashboard this is
consistent; for the three backup conditions below it is a real gap, because a
backup that silently stops is exactly what nobody notices. Closing it needs
Alertmanager plus a delivery target, which is a new component, a new network
path and possibly a new credential — all requiring operator approval, so it is
recorded in §19.1 as OPS-11 rather than built here.

Rules live in `config/platform/monitoring/alwayson-alerts.yml`, loaded from
`prometheus.yml` through `rule_files`. It is a separate file because Prometheus
rejects a top-level `groups:` key in `prometheus.yml` itself (measured:
`promtool check config` → `field groups not found in type config.plain`), so the
rules cannot be inlined. Both files are read-only bind mounts on
`ao-prometheus.container`.

### 17.2.2 Thresholds

Ten rules, in four groups, evaluated every 60 s. Each threshold below is one
that was checked against a live query on this host before being written; the
series counts in the rule file comments are the measurements behind them.

| Alert | Expression (abbreviated) | Threshold | For | Severity |
|---|---|---|---|---|
| `AoFilesystemLowSpace` | `node_filesystem_avail_bytes / node_filesystem_size_bytes` | `< 0.15` | 30 m | warning |
| `AoFilesystemCriticallyFull` | same ratio | `< 0.05` | 10 m | critical |
| `AoFilesystemReadOnly` | `node_filesystem_readonly` | `== 1` | 5 m | critical |
| `AoBackupStale` | `time() - ao_restic_backup_last_success` | `> 900 s` (15 m) | 15 m | critical |
| `AoRestoreTestStale` | `time() - ao_restore_test_last_run` | `> 86400 s` (24 h) | 1 h | warning |
| `AoRepositoryVerifyStale` | `time() - ao_repository_verify_last_success` | `> 604800 s` (7 d) | 1 h | warning |
| `AoMemoryLow` | `MemAvailable / MemTotal` | `< 0.10` | 15 m | warning |
| `AoLoadHigh` | `node_load1 / count(node_cpu_seconds_total{mode="idle"})` | `> 1.5` | 30 m | warning |
| `AoExporterDown` | `up == 0` | any target | 5 m | critical |
| `AoDbSecurityCollectorStale` | textfile collector mtime | `> 900 s` | 30 m | warning |

The filesystem rules deliberately do **not** exempt the photogrammetry drive.
It is the WebODM target volume, so filling it stops mapping; excluding it because
it is large would be exactly the wrong trade.

`AoBackupStale`, `AoRestoreTestStale` and `AoRepositoryVerifyStale` read three
metric names that **nothing currently exports**. They are the correct
thresholds and the correct expressions, and they will stay silent until a
textfile collector writes them — the same mechanism
`collect-db-security.py` already uses for the `alwayson_db_*` facts. The
collector is not written here because writing the backup-status writer means
deciding the retention and failure semantics of that file, and OPS-11 is
already open for the routing half. **A rule that can never fire is not
alerting**, so these three are documented as unwired rather than counted as
coverage.

### 17.2.3 Coverage that is deliberately absent

The eleven required alert conditions do not all have a metric on this host, and
this is measured, not assumed:

- `node_systemd_unit_state` returns **0 series** — there is no systemd exporter,
  so container restart loops, unit health and image digests have no source.
- Only two jobs are scraped (`prometheus`, `node-host`), so per-domain
  conditions — payment verification, radio loss, WebODM backlog, GPU
  contention, certificate expiry, cross-domain denials, unexpected listeners —
  have no exporter at all.

An alert on an absent metric either fires forever or never, which is worse than
an acknowledged gap. Those seven conditions are therefore recorded as
**uncovered with a named missing exporter**, not silently omitted. Closing them
requires new exporters, which is new component work for the owning domain
sessions, not a §17 edit.

## 17.3 Completion Evidence

No installation or deployment agent may claim completion until it produces:

1. Host inventory report.
2. Photogrammetry-drive report with mount source, UUID, filesystem, free space,
   ownership, and permission validation.
3. Installed package and version matrix.
4. Rootless and/or system Podman/Quadlet verification.
5. GPU driver and container-runtime validation.
6. Podman network list and domain-isolation results.
7. IPv4 and IPv6 firewall/listening-port report.
8. WebODM CPU-only smoke-test result using the dedicated drive.
9. Vehicle-simulation smoke-test result.
10. Fabrication-simulation smoke-test result.
11. Heltec stable serial-device detection and LoRa-link test result.
12. Ledger-ingestion test and Corda receipt result.
13. Sales receipt-manifest test without payment secrets.
14. Backup execution result.
15. At least one isolated restore-test result.
16. A current list of unresolved blockers, deviations, risks, and actions
    requiring human approval.

### 17.4 Restic path set and measured restore-drill evidence

**Path-set coverage.** The nightly repository covers `config`, `artifacts`,
`backups/postgres`, and the `data/` classes `ardupilot`, `corda-install`,
`sim-fabrication`, `sales`, `mapping`, `field`, `payment`, `ledger`. Two
exclusions are deliberate and each has a reason:

- `data/build-update/cache` is regenerable build output, so backing it up would
  spend repository space on something that can be rebuilt.
- The photogrammetry drive is excluded because it is large and holds source
  imagery, not system state. **This is the weakest exclusion in the set**: that
  drive holds the mapping source data, and §17.1's copy table treats
  "current project data" as hourly-backup material. It is recorded rather than
  quietly accepted.

Four `data/` subdirectories are **not** in the path set and are not yet
classified: `cache` (4 KB), `monitoring` (269 MB),
`prometheus-textfile` (8 KB), `sim-vehicle` (8 KB). `data/monitoring` at 269 MB
is the one that matters — it is generated metric history, so losing it is
acceptable, but its size means the exclusion should be a decision on record
rather than an omission. OPS-09 in §19.1 tracks this.

**Restore drill, executed 2026-10-03.** Run with
`scripts/restore/restore-restic-drill.sh`, which implements the seven steps
above and refuses by construction to write anywhere near the live tree: it
requires an explicit `--scratch`, refuses any scratch path inside `/ALWAYSON`
after resolving it with `readlink -m`, and refuses a scratch directory that
already contains files. All three refusals were exercised:

```
$ bash scripts/restore/restore-restic-drill.sh --repo /nonexistent --scratch /ALWAYSON/data/evil
REFUSED: scratch path /ALWAYSON/data/evil is inside the live /ALWAYSON tree.
Use a path outside /ALWAYSON, e.g. /var/tmp/ao-restore-drill.
$ bash scripts/restore/restore-restic-drill.sh --repo /nonexistent --scratch /tmp/refuse-test-1613112
REFUSED: scratch directory /tmp/refuse-test-1613112 already exists and is not empty.
$ bash scripts/restore/restore-restic-drill.sh --repo /nonexistent
ERROR: --scratch is required (never defaults to a live path)
```

Drill run against the off-host repository, restoring only into `/var/tmp`:

| Measure | Value |
|---|---|
| Snapshot under test | `56bf1af5`, taken 2026-10-03 08:59:59 −0700 |
| Source paths | `/ALWAYSON/config`, `/ALWAYSON/artifacts` |
| Files restored | 63 files, 103 files/dirs, 304.564 KiB |
| Hash-identical to live | **59 of 63** |
| Changed since snapshot | 4 (all `config/`, all with live mtime **after** the snapshot) |
| Changed with mtime *before* the snapshot (corruption signature) | **0** |
| Database dumps in this snapshot | **0** — see the warning below |
| Corda submission manifests found | 1 |
| Repository integrity | `restic check --read-data-subset=1/10` → `no errors were found` |
| Result | **PASS** |

The 4 differing files were each checked individually and every one has a live
mtime later than the snapshot, so the differences are normal drift over the ten
hours between backup and drill, not corruption. That distinction is the reason
the drill separates "changed" from "changed but older than the snapshot" — a
naive hash comparison reports these four as failures and teaches the operator to
ignore the drill.

**Two limits of this drill, both real.** First, `data/` was **not** in this
snapshot's path set, so the drill exercised config and artifacts only — it is
not evidence that a data restore works. Second, it found **0 database dumps**,
because the off-host repository was seeded with a proof snapshot covering only
`config` and `artifacts`; the `pg_dump` output under `backups/postgres/` lives in
the local repository. So step 2 of the seven-step test had nothing to validate,
and reporting "0 dumps, 0 problems" as a pass would overstate the result. Both
are tracked in OPS-24.

The repository was not modified: after the drill the off-host repository still
reports exactly 1 snapshot, and the scratch directory was removed.

**The drill script had a bug of its own, caught on its first run.** Step 4 first
resolved the live file as `$live_root/$rel` and only fell back to `/ALWAYSON/…`
when that path was absent — but `$live_root` *is* the restored tree, so it
compared every restored file with **itself** and reported `identical: 63,
changed: 0`. That is a false pass, and a false pass is worse than a failure
because it would have been filed as evidence. The same run, with the path
resolution corrected, reports `identical: 59, changed: 4` — matching an
independent manual `sha256sum` comparison of the same snapshot done outside the
script. The lesson recorded in the script's own comments: **a comparison step
must be able to fail**, and the cheapest proof that it can is to run it once
against data already known to have changed.

### 17.5 Log retention and the journal root

§16.3 fixes `/ALWAYSON/logs/` as the single journal root. Re-measured
2026-10-03: no second root exists — `logs/installation/` is a subdirectory of it,
not a sibling, and the `LOGS-JOURNALS/` draft name appears nowhere on disk. The
canonical-root half of OPS-07 is therefore met; **the outstanding half is that
`logs/` is still absent from the restic path set**, which means a restore to a
new host comes back without an operational history at all. That is a one-line
change to an approved path list and it is left to the operator because it
enlarges what the nightly job copies.

Retention is stated here because OPS-25/OPS-26 leave it unowned. The
**recommended** policy is staged in-tree and parse-verified; none of it is
installed, because `/etc/logrotate.d/` and `/etc/systemd/journald.conf.d/` both
need root and this session has no sudo (measured: `sudo -n true` →
`sudo: a password is required`).

| Path | Rotation | Retention | Status |
|---|---|---|---|
| `logs/*.log` (top level) | `logrotate-alwayson.conf`, daily | 14 files, uncompressed | **Staged, not installed** |
| `logs/operations/` | staged, daily | 400 rotations | **Staged, not installed** |
| `logs/installation/` | staged, daily | 400 rotations | **Staged, not installed** |
| `logs/backup/` | staged, daily | 400 rotations | **Staged, not installed** |
| `logs/gpu-runtime/` | staged, daily | 400 rotations | **Staged, not installed** |
| journald | `journald-alwayson.conf` drop-in | `SystemMaxUse=4G`, `MaxRetentionSec=90day` | **Staged, not installed** |

Compression is deliberately omitted from the logrotate policy because it is the
only step that reads whole files; a full system pass measured 0.008 s and
`logrotate.timer` runs once daily, so overhead was never the obstacle.

**The subdirectories must not be treated like the top-level files.** They hold
per-operation audit records, so truncating or compressing them away destroys the
evidence §16.3 exists to keep. The staged policy therefore applies a single
**400-day age budget** to all four subdirectories rather than the 14-rotation
budget used for top-level files. 400 days covers four quarterly DR exercises
plus margin, and a flat budget is chosen over differentiated per-directory
windows because these directories are small (measured 2026-10-03, re-measured
after a stall in the same day: `backup` 28K, `gpu-runtime` 12K, `installation`
288K, `operations` 580K — it grew from 572K as sessions logged, which is itself
evidence these directories are append-only and live) — the budget is
generous headroom, not a response to disk pressure. If a future measurement shows
`operations/` or `installation/` growing large, the budget can be narrowed per
directory; nothing today justifies it.

Age-based retention is also why the policy uses `rotate 400` with `daily` rather
than `maxsize`: `maxsize` evicts the newest file when a size is exceeded, which
is the opposite of what an audit trail needs.

For journald, the shipped `/etc/systemd/journald.conf` has **every size cap
commented out** (measured: lines 27–29 and 35 are all `#`-prefixed), so the
effective ceiling is `SystemMaxUse=10%` of the filesystem with no age cap at
all. On a 458G root filesystem that is an implicit ~45G and an unbounded
forensic window. The staged drop-in sets an explicit `SystemMaxUse=4G` —
roughly equal to the 4G actually in use, so nothing is evicted on a normal day —
plus the change that actually matters, `MaxRetentionSec=90day`. Backup and
restore evidence is **not** lost to the age cap: it lives in `/ALWAYSON/logs/`
and `/ALWAYSON/backups/` on the 400-day budget above, not in journald.
`SystemKeepFree=8G` is a floor rather than a target, and is the setting that
actually protects the host filesystem under pressure.

The drop-in is staged as `config/host/journald-alwayson.conf` for installation
at `/etc/systemd/journald.conf.d/60-alwayson-retention.conf` — **not** as an
edit of the shipped `journald.conf`, which a package upgrade would overwrite.

**Consequence while this stays uninstalled.** `sim-gz-server.log` has no size cap
at all — the top-level policy rotates by age, not by size — so a chatty Gazebo
session grows that file without bound. The subdirectories grow without bound too,
though slowly. Neither is a capacity risk today; both are unbounded in principle.

---
