# 17. Backup, Restore, Monitoring, and Completion Criteria

This section states what backup, restore, retention and monitoring **must** do. It
carries no measured state. Outstanding work, current coverage and evidence live in
`README-ACTION_ITEMS/status-and-references.md` (§19.1, `OPS` group); this section is
the requirement those rows are measured against.

## 17.1 Backup and Restore Policy

### 17.1.1 The 3-2-1 target

Maintain **3-2-1**: three copies, on two media types, with one copy off-host or
off-site.

| Copy | Location | Requirement |
|---|---|---|
| Primary | Live system | — |
| Backup | Encrypted restic repository outside the data path | Produce a successful snapshot, verified by hash |
| Off-site | pCloud, as a restic destination | Maintain a second repository, disjoint from the host |

### 17.1.2 Placement rules

1. **Keep the local repository off the data's physical device.** A repository that
   shares the data's device is lost with that device and does not count as a copy.
2. **Do not count an off-host archive as the off-site copy unless it carries a
   restore duty.** `ao-egress-archive` carries none (see §11.6) and must not be
   counted toward 3-2-1.
3. **Record the device id of every backup path**, and re-verify separation after any
   storage, mount or repository change.

| Path | Role | Requirement |
|---|---|---|
| `/ALWAYSON` | the data | protected |
| `/var/backups/alwayson-restic` | local repository | **must not share a device with the data** |
| `/media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS` | off-host repository | must exist, decrypt with the production credential, and verify |
| `/home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS` | replicated cloud copy | must verify |

### 17.1.3 Off-site repository requirements

The off-site repository must satisfy all of the following.

1. **Exist as a valid restic repository** and decrypt with the production
   credential (`restic cat config` succeeds).
2. **Hold a snapshot series, not a single snapshot.** A one-snapshot repository
   proves a copy once; it does not prove a copy is maintained. Schedule it, or
   record an explicit approved deviation.
3. **Cover every path class the nightly repository covers** (see §17.4). A
   repository holding only a subset is not a restore source.
4. **Verify** — `restic check` must pass against it.

### 17.1.4 Named executors

Every backup and restore action must name its executor. An action with no named
executor is unscheduled, and an unscheduled backup satisfies no objective in this
section. Verify the timer, not the script.

| §17.1 requirement | Executor |
|---|---|
| Nightly snapshot | `scripts/backup/restic-run.sh` on `ao-restic-backup.timer` |
| Host PostgreSQL dumps | `scripts/backup/backup-host-postgres.sh` |
| All-database dump series | `scripts/backup/dump-all-postgres.sh` on the nightly timer |
| Off-host repository snapshot | **none scheduled — see §19.1 `OPS-30`** |
| Restore drill | `scripts/restore/restore-restic-drill.sh` |
| Repository integrity | `scripts/backup/verify-backup.sh` on `ao-restic-verify.timer` |

### 17.1.5 Recovery objectives

| Class | RPO requirement | RTO target |
|---|---|---|
| Project data under `/ALWAYSON` | 24 h | 4 h |
| Application databases | 24 h | 2 h |

1. **Treat the RPO column as a requirement and the RTO column as a target.** Only
   the RPO column is checkable against the schedule; the RTO column requires a
   timed drill.
2. **Do not claim an RPO the configuration cannot deliver.** Without WAL or
   continuous archiving, no class achieves an RPO better than the dump interval.
   State the achievable figure.
3. **Never widen a repository's permissions to make a drill pass.** A drill that
   needs broader access is a blocked drill; record the blocker instead
   (README §4.1 rule 3).

### 17.1.6 Restore ordering

Execute restores in this order. Steps 4, 5 and 6 are order-dependent: **step 4
cannot connect without step 5, and step 5 cannot authenticate without step 6.**

1. **Pin the snapshot by intent.** Select it explicitly and record the id; never let
   a tool choose. After an incident the newest snapshot is the one most likely to
   contain the fault being recovered from.

   ```bash
   set -a; . <envfile>; set +a          # source the env file FIRST
   export RESTIC_REPOSITORY=/var/backups/alwayson-restic   # then override
   restic snapshots --tag alwayson
   SNAP=<short_id>
   ```

   **Set `RESTIC_REPOSITORY` after sourcing the env file.** The env file also
   carries that variable and overrides an earlier export, which surfaces as a
   permission-denied `stat` on the repository config and reads like a credential or
   corruption failure.

2. **Restore into an isolated path, never over the live tree.** The drill script
   enforces this by construction and must keep doing so:
   - require an explicit `--scratch` and never default it to a live path;
   - refuse any scratch path resolving inside `/ALWAYSON` after `readlink -m`, so a
     symlink cannot evade the check;
   - refuse a scratch directory that already contains files.

3. **Restore filesystem paths** from the pinned snapshot:

   ```bash
   restic restore "$SNAP" --target "$scratch_abs" \
       --include /ALWAYSON/config --include /ALWAYSON/artifacts \
       --include /ALWAYSON/backups/postgres
   ```

4. **Restore databases in dependency order** — host cluster roles first, then each
   application database. Test each dump's integrity before loading it, and refuse an
   unrecognised label rather than guessing.

   ```bash
   for f in "$scratch_abs"/ALWAYSON/backups/postgres/*/*.sql.gz; do
       gzip -t "$f" || { echo "STOP: corrupt dump $f"; break; }
       label="$(basename "$(dirname "$f")")"     # the directory is authoritative
       case "$label" in
         metabase)  db=metabase;  user=metabase_app         ;;
         grafana)   db=grafana;   user=grafana_app          ;;
         sales)     db=salesdb;   user=sales_migration_role ;;
         mastodon)  db=mastodon;  user=mastodon             ;;
         webodm)    db=webodm;    user=webodm_app           ;;
         *) echo "STOP: unknown dump label '$label'"; break  ;;
       esac
       gunzip -c "$f" | PGPASSWORD="$pw" psql -h 127.0.0.1 -U "$user" -d "$db"
   done
   ```

   **Read the `(label, database, user)` mapping; never derive the database name from
   the filename.** The mapping is the guard table at the top of
   `scripts/backup/backup-host-postgres.sh`, which is the single source of truth. An
   unexpected label is a **stop**, matching that script's own `*)` guard — a restore
   without the guard loads into whatever it is pointed at.

   These are plain SQL dumps (`pg_dump` with no `-Fc`), so `psql` reads the stream.
   `pg_restore` applies only to custom and directory formats.

5. **Recreate missing roles before loading.** `pg_dump --no-owner --no-privileges`
   emits no `CREATE ROLE`, so ownership handling rests entirely on this step.

   ```bash
   psql -h 127.0.0.1 -U postgres -tAc \
     "select rolname from pg_roles where rolname in
       ('metabase_app','grafana_app','sales_migration_role','mastodon','webodm_app')"
   # any name not returned must be CREATE ROLE'd, with its own wallet password,
   # BEFORE step 4 loads anything
   ```

   **A restore that skips this step loads data successfully into a database no
   application can read**, which presents as a working restore and a broken
   application.

6. **Re-provision credentials from KDE Wallet.** Passwords are not in the backup:
   the dump script reads them at dump time and stores none, and the wallet is not in
   any backup. Re-provision the same `(folder, pass_key)` pairs so the restored roles
   can authenticate. A dump restores data, not access.

7. **Re-verify hashes** against the live tree and the restored dumps, using
   `scripts/restore/verify-hashes-and-receipts.sh` or the drill's own step.

### 17.1.7 The backup journal

1. **Record every snapshot attempt** to `/ALWAYSON/logs/backup.log` with actor,
   script, snapshot id and result. A snapshot with no journal entry is not evidence
   of a backup.
2. **Treat a journal id that does not resolve as a defect, not a stale record.**
   When the journal names a snapshot the repository does not hold, correct the
   journal path or the id; do not leave both standing.
3. **Require the journal to prove an incremental chain.** Successive entries must
   reference a parent snapshot; identical ids across nights mean the repository is
   copying one state, not accumulating.

## 17.2 Monitoring

### 17.2.1 Component responsibilities

| Component | Responsibility | Isolation requirement |
|---|---|---|
| Prometheus | the security instrument | independent of Grafana and Metabase in both directions |
| Grafana | dashboards and metric presentation | application state in its own database |
| Metabase | operator reports | read-only against every source |

Monitoring runs in `ao-admin`, which must have no VPN, no explicit allowlist and no
public exposure. Its only permitted outputs are the Grafana dashboard and the
Metabase reports.

### 17.2.2 Required metrics

Monitor at minimum:

| Component | Required metrics |
|---|---|
| Host | CPU, RAM, storage health, disk usage, temperature, GPU state, kernel errors |
| Podman/systemd | Unit state, restart loops, health, image digest |

### 17.2.3 Alerting rules

1. **Ship every alert rule as a deployed file, not merely a staged one.** A rule
   present in the repository and absent from the deployed unit provides no coverage.
   Edit the repository copy and reinstall; never edit the live unit.
2. **Re-read names and thresholds from the deployed rules before changing them.** Do
   not reconstruct a metric name or a threshold from what a rule appears to be for;
   the deployed `expr:` line is the only authority.
3. **Load rules with a glob that matches the file actually installed.** A
   `rule_files` glob matching nothing is not a Prometheus startup failure, so it
   survives unnoticed. Verify the glob resolves.
4. **Never count an unwired rule as coverage.** A rule whose metric nothing exports
   can never fire, and a rule that can never fire is not alerting. Document it as
   unwired and record the missing collector as outstanding work.
5. **Never raise an alert on an absent metric.** An alert on a metric with no
   exporter either fires forever or never fires, which is worse than an acknowledged
   gap. Record the gap with the named missing exporter.

| Rule | Expression basis | Threshold | For | Severity |
|---|---|---|---|---|
| `AoBackupStale` | `ao_backup_last_success_timestamp_seconds` | `> 93600` | 1 h | warning |
| `AoRestoreTestStale` | `ao_restore_test_last_run_timestamp_seconds` | `> 3024000` | 1 h | warning |
| `AoRepositoryVerifyStale` | `ao_backup_last_verify_timestamp_seconds` | `> 777600` | 1 h | warning |
| `AoMemoryLow` | `MemAvailable / MemTotal` | `< 0.10` | 15 m | warning |
| `AoLoadHigh` | `node_load1 / count(node_cpu_seconds_total{mode="idle"})` | `> 1.5` | 30 m | warning |
| `AoExporterDown` | `up == 0` | any target | 5 m | critical |
| `AoDbSecurityCollectorStale` | textfile collector mtime | `> 900 s` | 30 m | warning |

**Do not exempt the photogrammetry drive from filesystem rules.** It is the WebODM
target volume, so filling it stops mapping. Excluding it because it is large is the
wrong trade.

### 17.2.4 Reporting access

1. **Grant reporting read access and deny write access on the same relations.** A
   read-only reporting identity must read a real source successfully *and* be
   refused a write against a relation that demonstrably exists.
2. **Qualify the schema before concluding a view is unreadable.** A reporting
   identity's `search_path` may exclude the schema holding the view, so an
   unqualified query fails with `relation does not exist` while the view is
   perfectly readable.
3. **Never treat `relation does not exist` as evidence about privileges.** Run the
   write test against a relation that exists; a missing relation proves nothing.
4. **Do not infer an unreachable fact from an unread store.** Before reporting a
   divergence between a live artefact and a stored value, establish that something
   reads the stored value. One grep for the entry name, run before the comparison.
5. **Require a negative control for any probe that contradicts a prior measurement.**
   A probe returning the same answer for every input is broken; confirm it returns
   the opposite answer for a known-absent input before believing the positive
   results.

## 17.3 Completion Evidence

No installation or deployment agent may claim completion until it produces all of
the following.

1. Host inventory report.
2. Photogrammetry-drive report with mount source, UUID, filesystem, free space,
   ownership and permission validation.
3. Installed package and version matrix.
4. Rootless and/or system Podman/Quadlet verification.
5. GPU driver and container-runtime validation.
6. Podman network list and domain-isolation results.
7. IPv4 and IPv6 firewall and listening-port report.
8. WebODM CPU-only smoke-test result using the dedicated drive.
9. Vehicle-simulation smoke-test result.
10. Fabrication-simulation smoke-test result.
11. Heltec stable serial-device detection and LoRa-link test result.
12. Ledger-ingestion test and Corda receipt result.
13. Sales receipt-manifest test without payment secrets.
14. Backup execution result.
15. At least one isolated restore-test result.
16. A current list of unresolved blockers, deviations, risks and actions requiring
    human approval.

## 17.4 Restic path set

### 17.4.1 Required coverage

The nightly repository must cover, at minimum:

- `config`
- `artifacts`
- `backups/postgres`
- the `data/` classes `ardupilot`, `corda-install`, `sim-fabrication`, `sales`,
  `mapping`, `field`, `payment`, `ledger`

### 17.4.2 Exclusions

1. **Justify every exclusion in writing.** An exclusion with no recorded reason is an
   omission, not a decision.
2. **Never exclude a path because it is large when the excluded data cannot be
   regenerated.** Size is not a reason to lose irreplaceable data.
3. **Enumerate the path set mechanically, not from memory.** Derive it from the
   backup script and the directory listing, and record both the covered and the
   excluded count:

   ```bash
   ls /ALWAYSON/data/ | wc -l
   grep -oE '/ALWAYSON/data/[a-z-]+' scripts/backup/restic-run.sh | sort -u
   ```

   A count asserted from memory goes stale when a directory is added.

### 17.4.3 Confidentiality

State the confidentiality consequence of the path set explicitly. `data/ledger` and
`data/payment` carry provenance and transactional records and belong in the path set;
because restic stores them as ciphertext in a repository on the same disk as the
source, confidentiality rests on the repository password alone. **A restored copy
carries exactly the sensitivity of the live copy — restore grants no privilege
drop.**

### 17.4.4 Restore-drill contract

`scripts/restore/restore-restic-drill.sh` must implement the §17.1.6 ordering and
enforce the three scratch refusals in §17.1.6 step 2.

1. **Run the drill against the off-host repository**, restoring only into a path
   outside `/ALWAYSON`.
2. **Require the drill's comparison step to be able to fail.** A comparison that
   cannot return a difference is a false pass, and a false pass is worse than a
   failure because it would be filed as evidence. Prove it can fail by running it
   once against data known to have changed.
3. **Resolve the live file independently of the restored tree.** Comparing a restored
   file against another restored file reports every file identical.
4. **Remove the scratch directory and leave the repository unmodified.** After a
   drill the repository must report the same snapshot count as before it.
5. **Never create a probe artefact from pre-existing project data.** Create probe
   fixtures for the test and remove them afterwards.
6. **Do not count a passing manual check as a scheduled control.** Integrity checking
   exists to catch bit rot and truncation, which develop *after* a drill; only a
   scheduled run closes that gap.

## 17.5 Log retention and the journal root

§16.3 fixes `/ALWAYSON/logs/` as the single journal root.

1. **Keep one canonical journal root.** A second root anywhere on the host is a
   defect; a subdirectory of the canonical root is not a second root.
2. **Include `logs/` in the restic path set.** A restore that returns without the
   operational history cannot be diagnosed.
3. **Install the logrotate policy from the repository copy**, never by editing the
   deployed file, and keep the deployed file byte-identical to the repository copy.
4. **State a retention budget for every log class**, and record any class whose
   budget is unmet.
5. **Retain the per-operation subdirectories far longer than the top-level logs.**
   They hold audit evidence §16.3 exists to keep; truncating or compressing them
   destroys it. Apply a single flat age budget to them rather than the
   rotation-count budget used for top-level files.
6. **Omit compression from the policy.** It is the only step that reads whole files,
   and the daily pass is cheap without it.
7. **Confirm rotation works unattended.** A rotation demonstrated only by a forced or
   hand-invoked run proves nothing about the scheduled path. Verify from the journal
   that a rotation occurred with no privileged invocation in the window.
8. **Attribute a rotated file only to a rotator proven to have produced it.** A file
   count cannot establish which rotator created a given file; a rotated file whose
   mtime predates the policy was produced by an earlier mechanism.
9. **Validate staleness against a held write handle, not against mtime.** Confirm per
   log that a live process holds a write handle on the path being checked, using
   `fuser` or `lsof`. An mtime-only check reports a recreated live file as fresh while
   its writer stays attached to the rotated inode, and that writer's output is
   discarded at the next rotation.
10. **Keep any safety justification in a policy comment true for every writer it
    claims to cover.** A comment verified against one library and worded as "every
    writer" is a false claim in a file an operator will believe. Verify against all
    writers, including container runtimes that open a log path once at start and
    never reopen it.
11. **Require journald caps to be installed, not merely configured.** A drop-in
    directory that does not exist means nothing was installed, and the shipped
    defaults apply. Verify the directory and the effective values.

### 17.5.1 Container logging

For every container that writes to a rotated path, the policy must guarantee the
writer follows the rotation. Either:

- enable `copytruncate` for those files, accepting that it briefly duplicates content
  and briefly races writers; or
- add a `postrotate` that signals the container to reopen its log; or
- move the container to `journald` or `k8s-file` under a path the policy does not
  rotate.

**Choose deliberately and record the choice.** Both active options touch a running
service and require operator approval (README §4.1 rule 6).

## 17.6 Backup integrity

1. **Schedule repository integrity checking.** `restic check` is the only control
   that detects a silently corrupted or truncated repository. The 3-2-1 claim in
   §17.1 and every restore-drill result in §17.4 rest on it.
2. **Run it at least weekly.** A one-off manual check is evidence about that moment
   only.
3. **Supply the credential file the verify unit requires.** A verify script whose
   default env path does not exist must fail closed and be reported, not left to exit
   non-zero unnoticed every week.
4. **Verify the deployed unit, not the staged one.** When the deployed unit lags the
   repository copy, the repository is correct and the running system is not.
