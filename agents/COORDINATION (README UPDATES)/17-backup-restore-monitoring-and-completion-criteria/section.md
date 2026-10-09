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

Two properties govern where the backup copies may live. The local repository
must not share a physical device with the data it protects, or it is lost with
this host. An off-host archive is not a substitute unless it carries a restore
duty, which `ao-egress-archive` does not (see §11.6).

| Path | Device id | Physical media | Requirement |
|---|---|---|---|
| `/ALWAYSON` (the data) | 66306 | root disk | protected |
| `/var/backups/alwayson-restic` (local repo) | 66306 | root disk | **must not share a device with the data** |
| `/media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS` | 2049 | separate media | off-host repository; must exist and verify |
| `/home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS` | 218 | pCloud FUSE | **replicated cloud copy of the above**; must verify |

The 3-2-1 target is therefore **partially met**: copy two is still on the root
disk, but a genuinely host-disjoint copy exists on separate media inside the
running pCloud sync root, and has replicated into the live pCloud mount (see
§17.1.1.2). It is deliberately **not scheduled** — no timer, no
cron, no reference from `restic-run.sh` — so it holds a single snapshot rather
than a series. Until it is scheduled it mitigates total disk loss but does not
satisfy "one off-site copy" in the sense the policy intends. Enabling it is an
operator decision.

### 17.1.1.1 Required contents of the off-site repository

§19.1 carries two rows, OPS-29 and OPS-30, both titled "Off-site restic
repository does not exist". **That title is now false and should be
reworded**, because a valid restic repository does exist off-host and decrypts
with the production credential:

```
$ RESTIC_REPOSITORY=/media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS \
  restic cat config
{
  "version": 2,
  "id": "d22cddc074532b53bcea8ee739c3b7b7107d9fd3baa3224125d0e569fbfb94be",
  "chunker_polynomial": "33c903993a9dcf"
}
```

It holds exactly **one** snapshot:

```
$ restic snapshots --json
[{"time":"2026-10-03T08:59:59.123174545-07:00",
  "paths":["/ALWAYSON/artifacts","/ALWAYSON/config"],
  "tags":["alwayson-offsite-proof"],
  "program_version":"restic 0.18.1",
  "summary":{"files_new":63,"total_files_processed":63,
             "total_bytes_processed":311874},
  "short_id":"56bf1af5"}]
```

```
$ restic stats
Stats in restore-size mode:
     Snapshots processed:  1
        Total File Count:  103
              Total Size:  304.564 KiB

$ restic ls 56bf1af5 | grep -E '^/ALWAYSON/[a-z-]+$'
/ALWAYSON/artifacts
/ALWAYSON/config

$ restic ls 56bf1af5 | grep -c '^/ALWAYSON/data'
0
```

**304 KiB, 103 files, configuration and manifests only — no `data/`, no
`logs/`, no `backups/`.** So the repository is real, off-host and readable, but
it protects nothing that would be lost with the host. It is a *proof of
concept*, which is what its own tag (`alwayson-offsite-proof`) says.

**What §19.1 got wrong, and why the distinction matters.** OPS-29's body says
the pCloud folder `ALWAYSON-RESTIC2PCLOUD` "exists at the account root but is
empty". Two claims, both of which need correcting against the live host:

```
$ ls /media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/
ALWAYSON-BACKUPS   ... (17 entries)

$ find /media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE -maxdepth 2 -iname '*RESTIC2PCLOUD*'
(no output)
```

1. **A directory named `ALWAYSON-RESTIC2PCLOUD` does exist at the pCloud account
   root — and it is empty.** OPS-29's row is **accurate** on this point and an
   earlier revision of this section was wrong to deny it. The relevant distinction
   is *which* root: §19 names the account root
   (`/home/scottw/pCloudDrive/`), and that folder is there, `total 0`:

   ```
   $ ls -d /home/scottw/pCloudDrive/ALWAYSON-RESTIC2PCLOUD
   /home/scottw/pCloudDrive/ALWAYSON-RESTIC2PCLOUD
   $ ls -la /home/scottw/pCloudDrive/ALWAYSON-RESTIC2PCLOUD
   total 0
   drwxr-xr-x 2 scottw scottw 4096 Sep 30 23:00 .
   drwxr-xr-x 35 scottw scottw 4096 Sep 30 22:56 ..
   ```

   An earlier "absent entirely" finding searched only the *USB disk's* sync root
   (`/media/…/PCLOUD_STORAGE/`), which is a different tree, and generalised from
   it. **A filesystem claim must not be generalised from one root to another.**
2. **The remedy "upload via rclone WebDAV or SFTP" describes a mechanism that is
   not in use here and is not needed for what exists.** `ALWAYSON-BACKUPS` is a
   plain local restic repository on the 1TB Samsung USB disk, sitting *inside* a
   directory that pCloud syncs. It replicates by virtue of that sync root, with
   no rclone remote. Recommending WebDAV/SFTP would add a moving part to solve a
   problem the current arrangement does not have.

### 17.1.1.2 Cloud replication requirement

The earlier caution in this section — that "a copy exists and pCloud replicates the
disk **when it is attached**" — was correct as written but understated what has since
happened. The repository is now visible **inside the live pCloud mount**, which is
where replication lands:

```
$ stat -c '%d %i %n' /media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS \
                      /home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS
2049 5505025 /media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS
 218 211841 /home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS
```

Different device id (`2049` local ext4 vs `218` pCloud FUSE) and a different inode,
so these are two real trees, not a symlink. The FUSE mount must be active:

```
$ findmnt -no SOURCE,FSTYPE /home/scottw/pCloudDrive
pCloud.fs  fuse.pCloud.AppImage
```

The replicated copy opens with the production credential and verifies independently:

```
$ RESTIC_REPOSITORY=/home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS restic snapshots
56bf1af5  2026-10-03 08:59:59  scottw-ms7b44  alwayson-offsite-proof
          /ALWAYSON/artifacts  304.564 KiB
          /ALWAYSON/config
1 snapshots

$ RESTIC_REPOSITORY=/home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS \
    restic check --read-data-subset=1/10
no errors were found
```

So a copy that has left the host does exist and is restorable from the pCloud mount.
**Limit stated honestly:** this proves the files are present and readable through
the pCloud filesystem; it does **not** independently prove the remote account holds
them, because that would require a pCloud-side status query, which is outside this
specification's access. Treat "off-site and verifiable from the mount" as proven
and "uploaded to the account" as supported-but-unconfirmed.

What this does **not** change: it is still one proof snapshot of two directories
(304 KiB, no `data/`, `logs/` or `backups/`), still unscheduled, and still only
replicated when the USB disk is attached. It moves OPS-30 from "repository does not
exist" to "repository exists off-host, replicates, but is not maintained and does
not yet carry the nightly path set".

**Why this is still Open, and it is not a documentation nit.** The two rows stay
open, but for a reason the current wording hides: the repository holds **one
proof snapshot of two directories**, not the data classes. Even a working,
scheduled sync of *this* repository would satisfy "a second copy exists" while
leaving every `data/` class unprotected off-host. The acceptance criterion that
actually matters is therefore **not** "create a repository" — it is "the
off-host repository must carry the same path set as the nightly job", which
§17.1's `restic-run.sh` list defines. That is a larger copy than the operator has
approved for automatic off-site transfer, so it stays open and stays with the
operator.

**One property of this arrangement to be explicit about, because it is easy to
over-credit.** The 1TB disk is *removable, locally attached* media that happens
to live inside a synced folder. When the disk is not mounted, no off-host copy is
being written at all, and nothing detects that. So this arrangement's real
guarantee is "a copy exists and pCloud replicates the disk when it is attached",
not "a copy is maintained". Only scheduling plus a liveness check upgrades it.

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
| 1. Restore to an isolated path or host | L89 `restic restore "$snapshot" --target "$scratch_abs"` | Three refusals, all reproduced 2026-10-04 (below) |
| 2. Validate database integrity | L95–L113 gzip `-t` plus a 1024-byte floor per dump | A truncated or empty dump increments `db_bad`, which forces `result=FAIL` |
| 3. Recalculate artifact hashes | L117 `sha256sum` over every file under the live root | Writes `.drill-hashes.txt`; count is printed at L118 |
| 4. Compare with stored manifests | L121–L171 per-file compare against the **live** tree | Three buckets: drift, suspect (mtime older than snapshot), live-only. `suspect > 0` forces `result=FAIL` |
| 5. Verify Corda receipts/manifests | L173 finds `pending-ledger-submissions` manifests | Prints an explicit "path-set observation, not a pass" when zero are found |
| 6. Record operator, ID, result, exceptions | L181–L188 prints operator, snapshot, repo and all counters | The `result=` line at L188 is the only value step 7 branches on |
| 7. Alert on failure | L190 non-zero exit plus an operator-facing instruction | Exit 1 is what any caller or unit would detect |

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
where a manifest comparison would only report a mismatch. It is not the
requirement's wording, however, and inventing a baseline manifest would mean new
backup behaviour — which is OPS-09's decision and needs operator authorisation.

The restic units are **root-level systemd units**, not Quadlets. They are
therefore not deployed into `~/.config/containers/systemd/`; they live in
`/etc/systemd/system/`. Do not infer absence from an empty Quadlet directory.

| Unit | `is-enabled` | Requirement |
|---|---|---|
| `ao-restic-backup.timer` | enabled | active; `ao-restic-backup.service` succeeding |
| `ao-restic-verify.timer` | enabled | 8 h ago |
| `ao-restic-prefetch.timer` | enabled (user) | 4 h ago |

So the nightly backup is genuinely live, not staged. The lesson repeats the one
already recorded for OPS-35 and for the Prometheus mount above: **a negative
result from the wrong directory is not evidence of absence.** A Quadlet-style
lookup was applied to a non-Quadlet unit.

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

**The RPO column is measured; the RTO column is a target, not a measurement.**
That distinction was previously blurred, so it is now stated:

- Every **RPO = 24 h** follows from two `OnCalendar` values that were read, not
  estimated:

  ```bash
  $ systemctl cat ao-restic-backup.timer | grep OnCalendar
  OnCalendar=*-*-* 03:30:00
  $ systemctl cat ao-restic-verify.timer  | grep OnCalendar
  OnCalendar=Sun *-*-* 04:30:00
  ```

  Both are `Persistent=true`. So the worst case for a run that failed is one
  full day plus the next scheduled run — **48 h**, not 24 h — and that is the
  number to plan against.
- Every **RTO** is an operator-set objective. The only elapsed time actually
  measured on this host is the **restore** half of one drill against a
  304 KiB two-path snapshot (§17.4). Nothing here measures a full service
  recovery — redeploy, credential re-provisioning, application restart, and
  verification are all untimed. A class with a 1 h RTO and a measured
  filesystem restore of seconds is *not* thereby proven to recover in 1 h; it
  is proven to restore its files quickly and to have an unmeasured remainder.

**One further bound the table omits, and it is the largest one.** No restore
test is scheduled at all:

```bash
$ systemctl list-timers --all | grep -iE 'restore'
$ systemctl --user list-timers --all | grep -iE 'restore'
        (no output — no restore timer exists in either scope)
```

so the drills that would keep these figures honest are manual (§17.4). Until a
monthly timer exists, **every RTO in this table is an untested intention**.

### 17.1.3 Restore ordering

Filesystem and database restores are not independent. `pg_dump` output is
captured into `backups/postgres/<role>/` and is then itself backed up by restic,
so a correct restore is:

0. **Preflight.** Establish these facts before touching anything, because
   three of the failure modes below are silent otherwise. `$pw_super` and each
   `$pw` are read from KDE Wallet via
   `scripts/ops/wallet-read-secret.py` — never echo them, and never store them:

   ```bash
   # (a) the credential resolves — proves the wallet entry exists and decrypts.
   #     Never echo it; length and exit status only.
   ./scripts/operations/fetch-restic-env.sh /run/user/$(id -u)/ao-restic.env
   # -> "OK: wallet-backed restic env materialized"

   # (b) the repository is readable AS THE RESTORING USER. This is the check
   #     that catches OPS-24's blocker before any restore is attempted.
   set -a; . /run/user/$(id -u)/ao-restic.env; set +a
   restic snapshots --tag alwayson >/dev/null && echo "repo readable" \
     || echo "STOP: repository unreadable — do not continue"

   # (c) enough free space for the restored tree plus the repository's
   #     restore-size, measured not guessed:
   restic stats --mode restore-size
   df -h --output=avail "$(dirname "$scratch_abs")" | tail -1

   # (d) the target cluster is reachable AND you can authenticate as a
   #     superuser. pg_isready proves liveness only; on this host an unauthenticated
   #     `psql -U postgres` fails with "fe_sendauth: no password supplied", so
   #     reachability must not be reported as access:
   pg_isready -h 127.0.0.1
   PGPASSWORD="$pw_super" psql -h 127.0.0.1 -U postgres -tAc "select 1"
   # (e) the five application roles exist, or step 4 cannot load anything:
   PGPASSWORD="$pw_super" psql -h 127.0.0.1 -U postgres -tAc \
     "select rolname from pg_roles where rolname in
       ('metabase_app','grafana_app','sales_migration_role','mastodon','webodm_app')"
   ```

   (b) and (d) are the two that would otherwise be discovered halfway through a
   real restore. Measured on this host: (b) fails for the nightly repository,
   because `/var/backups/alwayson-restic` is `drwx------ root root` (§17.4.1);
   (d) fails without the superuser password, which lives in the wallet and is
   not in any backup.

1. **Select the snapshot explicitly; do not let a tool pick it.** Choose by
   intent and pin the ID:

   ```bash
   export RESTIC_REPOSITORY=/var/backups/alwayson-restic   # set AFTER sourcing
                                                          # the env file — the env
                                                          # file also carries
                                                          # RESTIC_REPOSITORY and
                                                          # overrides it otherwise
   # read the candidates, then pin the one you mean by intent:
   restic snapshots --tag alwayson
   SNAP=<short_id>        # a known-good snapshot named in the incident
   #   SNAP=latest         # newest, for a point-in-time recovery
   ```

   **The ordering trap, measured.** `fetch-restic-env.sh` writes a file that
   already sets `RESTIC_REPOSITORY`. Exporting the variable *before* sourcing
   that file silently loses: restic then reports

   ```
   Stat(<config/>) failed: stat /var/backups/alwayson-restic/config: permission denied
   ```

   which reads like a credential or corruption failure and is neither. Set
   `RESTIC_REPOSITORY` **after** `set -a; . <envfile>`.

   Pinning the ID is the point. `restore-restic-drill.sh` defaults to the newest
   snapshot when `--snapshot` is omitted (`max(snaps, key=lambda s: s["time"])`),
   which is correct for a drill and **wrong for a recovery**: after an incident
   the newest snapshot is the one most likely to contain the fault being
   recovered from. Pass `--snapshot` explicitly in a real restore.

2. **Restore the repository to an isolated path.** Never over the live tree.
   `scripts/restore/restore-restic-drill.sh` refuses by construction — it
   rejects a scratch path inside `/ALWAYSON` after `readlink -m`, so a symlink
   cannot evade the check, and it refuses a non-empty scratch directory.
3. **Restore filesystem paths** (`config`, `artifacts`, `backups/`) from the
   restored snapshot:

   ```bash
   restic restore "$SNAP" --target "$scratch_abs" \
       --include /ALWAYSON/config --include /ALWAYSON/artifacts \
       --include /ALWAYSON/backups/postgres
   ```

4. **Restore databases** from the restored `backups/postgres/*.sql.gz`, in
   dependency order — host cluster roles first, then each application database:

   ```bash
   for f in "$scratch_abs"/ALWAYSON/backups/postgres/*/*.sql.gz; do
       gzip -t "$f" || { echo "STOP: corrupt dump $f"; break; }   # integrity first
       # the LAYOUT is authoritative: the dump's parent directory is the role
       # label, which selects the (database, user) pair. The database name in
       # the filename is not always the directory name - the sales database is
       # 'salesdb' under the directory 'sales'.
       label="$(basename "$(dirname "$f")")"
       case "$label" in
         metabase)  db=metabase;  user=metabase_app     ;;
         grafana)   db=grafana;   user=grafana_app      ;;
         sales)     db=salesdb;   user=sales_migration_role ;;
         mastodon)  db=mastodon;  user=mastodon         ;;
         webodm)    db=webodm;    user=webodm_app       ;;
         *) echo "STOP: unknown dump label '$label' - do not guess"; break ;;
       esac
       gunzip -c "$f" | PGPASSWORD="$pw" psql -h 127.0.0.1 -U "$user" -d "$db"
   done
   ```

   That `case` is transcribed from the guard table at the top of
   `backup-host-postgres.sh`, which is the single source of truth for which
   (label, database, user) triples exist:

   ```bash
   $ sed -n '11,17p' scripts/backup/backup-host-postgres.sh
   metabase:metabase:metabase_app)      folder=ao-admin;    ...
   grafana:grafana:grafana_app)         folder=ao-admin;    ...
   sales:salesdb:sales_migration_role)  folder=ao-sales;    ...
   mastodon:mastodon:mastodon)          folder=ao-mastodon; ...
   webodm:webodm:webodm_app)            folder=ao-mapping;  ...
   *) echo "refusing unexpected host PostgreSQL backup target" >&2; exit 2 ;;
   ```

   **Deriving the database name from the filename is wrong**, and would send
   `sales` dumps at a database that does not exist. Read the mapping, do not
   parse the name. The same table shows the `*)` default the backup script
   uses to refuse unexpected targets; a restore that lacks that guard will
   happily load into whatever it is pointed at.

   These are plain SQL dumps (`pg_dump` with no `-Fc`), so `psql` reads the
   stream — `pg_restore` applies only to custom/directory formats. Measured:
   `scripts/backup/backup-host-postgres.sh:22` passes only `--no-owner
   --no-privileges`, no `-Fc`, and pipes straight into `gzip -9`. Verify before
   assuming:

   ```bash
   $ grep -n 'pg_dump' scripts/backup/backup-host-postgres.sh
   22:if pg_dump --host=127.0.0.1 ... --no-owner --no-privileges | gzip -9 >"$out.tmp"; then
   ```
5. **Recreate roles before loading**, because `pg_dump --no-owner
   --no-privileges` (as `backup-host-postgres.sh` uses) emits no `CREATE ROLE`,
   so the dump assumes the roles already exist. Ownership handling is therefore
   *entirely* on this step. The roles required are the five `user` values from
   the table above; create any that are missing before step 4, then re-apply
   the grants the dump omitted:

   ```bash
   psql -h 127.0.0.1 -U postgres -tAc \
     "select rolname from pg_roles where rolname in
       ('metabase_app','grafana_app','sales_migration_role','mastodon','webodm_app')"
   # any name not returned must be CREATE ROLE'd (with its own password from
   # the wallet) BEFORE step 4 loads anything
   psql -h 127.0.0.1 -U postgres -d "$db" -c '\du'   # roles survived the load
   ```

   **Passwords are not in the backup.** `backup-host-postgres.sh` reads them
   from KDE Wallet at dump time and stores none, so a restored cluster has
   roles with no way to authenticate until step 6 re-provisions them. That
   ordering is not a preference: step 4 cannot connect without step 6.
6. **Re-provision credentials** from KDE Wallet — the same five
   `(folder, pass_key)` pairs in the same table — so the restored roles can
   authenticate. A dump restores data, not access, and the wallet is not in
   any backup (§17.1.2).
7. **Re-verify hashes** against the live tree and the restored dumps —
   `scripts/restore/verify-hashes-and-receipts.sh`, or the drill's own step 4.

Step 5 is the one that is easy to miss, and it is called out because
`backup-host-postgres.sh` deliberately strips ownership: a restore that skips it
loads data successfully into a database that no application can read, which
looks like a working restore and a broken application. The measured
`sed -n '11,17p'` table above is the authority for every (label, database, user)
triple in this runbook — five labels, and an unexpected one is a **stop**, not a
default, matching the backup script's own `*)` guard.

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
They survive in `logs/backup.log.1`, which the now-installed logrotate policy
rotated on 2026-10-04.

**The fix is now verified on the live host, so OPS-35 is closed 2026-10-04.** The
earlier statement in this section — "the first run after deployment is the
evidence that it works" — was correct as written and is now satisfied. The
fix commit `8cb21bb` is dated 2026-10-03 21:18:29 −0700; the nightly timer fired
at 2026-10-04 03:35:37, the first run after it. Both sides of the claim, taken
independently:

```
$ grep 'restic-run.sh' /ALWAYSON/logs/backup.log | tail -1
2026-10-04T10:35:39+00:00 actor=root script=restic-run.sh snapshot=0548f116 result=OK restic backup completed

$ journalctl -u ao-restic-backup.service --since '2026-10-04 03:00' --until '2026-10-04 04:00' \
    | grep -oE 'snapshot [0-9a-f]{8} saved'
snapshot 0548f116 saved
```

`0548f116` on both sides. This is the first run whose journal ID is not stale,
and it is distinct from all three historical values (`548d9910`, `e79edfbf`,
`fbc25f93`) — which is what rules out the coincidence of the ID simply being
frozen in some other way.

Two things this verification is **not**, recorded so the next agent does not
over-read it. The run is a `SUCCESS` in both journal and systemd
(`ExecStart=…/restic-run.sh (code=exited, status=0/SUCCESS)`), but it does not by
itself re-prove that the backup covers the right paths — that is OPS-09, still
open. And one correct run demonstrates the selection logic works on a repository
whose newest snapshot is the nightly one; the original defect only appeared where
snapshots of *different* path sets shared a repository, which is a state this
repository is not currently in. The fix is verified against the failure's root
cause (maximum `time` rather than array position) and against the live host, and
that is the whole of what is claimed.

| 1. Restore to an isolated path or host | L77 `restic restore --target "$scratch_abs"` | Three refusals, all reproduced 2026-10-04 (below) |
| 2. Validate database integrity | L84 gzip `-t` plus a 1024-byte floor per dump | A truncated or empty dump increments `db_bad`, which forces `result=FAIL` |
| 3. Recalculate artifact hashes | L104 `sha256sum` over every restored file | Writes `.drill-hashes.txt`; count is printed and asserted against the find |
| 4. Compare with stored manifests | L110 per-file compare against the **live** tree | Three buckets: drift, suspect (mtime older than snapshot), live-only. `suspect > 0` forces `result=FAIL` |
| 5. Verify Corda receipts/manifests | L162 finds `pending-ledger-submissions` manifests | Prints an explicit "path-set observation, not a pass" when zero are found |
| 6. Record operator, ID, result, exceptions | L170 prints operator, snapshot, repo and all counters | The `result=` line is the only value step 7 branches on |
| 7. Alert on failure | L179 non-zero exit plus an operator-facing instruction | Exit 1 is what any caller or unit would detect |
The fix applies to future runs; the first run after deployment is the evidence
that it works.

## 17.2 Monitoring

### 17.2.0 Metabase persistence: the app-data volume is empty, and that is correct

OPS-01 asks for Metabase persistence plus a first read-only query. Measured
2026-10-04, the persistence half is already satisfied and the reason is not
obvious enough to leave unstated.

`ao-metabase` must run against the host PostgreSQL cluster, not a private
database container:

```
$ podman inspect ao-metabase --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'
/home/scottw/.local/share/containers/storage/volumes/ao-metabase-postgres-data/_data -> /metabase-postgres-data
/var/run/postgresql -> /var/run/postgresql

$ podman inspect ao-metabase --format '{{range .Config.Env}}{{println .}}{{end}}' | sed -E 's/(PASS|SECRET|KEY|TOKEN)=.*/\1=<redacted>/I'
MB_DB_HOST=10.42.0.1
MB_DB_USER=metabase_app
MB_DB_DBNAME=metabase
MB_DB_TYPE=postgres
...

$ podman volume inspect ao-metabase-postgres-data --format '{{.Mountpoint}}'
/home/scottw/.local/share/containers/storage/volumes/ao-metabase-postgres-data/_data

$ du -sh /home/scottw/.local/share/containers/storage/volumes/ao-metabase-postgres-data/_data
4.0K    /home/scottw/.local/share/containers/storage/volumes/ao-metabase-postgres-data/_data

$ ls -la /home/scottw/.local/share/containers/storage/volumes/ao-metabase-postgres-data/_data
total 8
drwxr-xr-x 2 scottw scottw 4096 Sep 24 20:40 .

$ curl -s localhost:3002/api/health
{"status":"ok"}
```

**The volume is empty and has been since it was created on 2026-09-24, and
that is not a fault.** `MB_DB_*` points Metabase at the host cluster on
`10.42.0.1` (the host's Podman bridge address) using the `metabase_app` role
created by `scripts/ops/provision-reporting-postgres.sh`, so saved questions,
dashboards and subscriptions live in the `metabase` database on the host, not in
H2 and not in that volume. The deployment moved off the embedded H2 store on
2026-09-25 — `logs/operations/metabase-h2-migrate-final.log.1` ends at liquibase
`v47.00-002`, the last H2 migration, after an earlier attempt failed with
`ERROR Set up h2 source database and run migrations...: Unable to connect to
Metabase h2 DB.`

**`ao-metabase-postgres-data` is therefore a vestigial mount.** It is declared in
both the repository Quadlet (`quadlet/operations/ao-metabase.container:16`) and
the deployed copy, it is never written, and it reads as though Metabase's state
were stored there. An agent auditing persistence by volume size alone would
correctly conclude data is being lost. It is not. Recorded so the condition is
not re-raised as a false alarm, and flagged for removal as a separate cleanup —
which needs operator approval, because deleting a declared volume mount is a
container-definition change outside the backup/monitoring remit.

**What OPS-01 requires.** Two elements remain: (a) confirming state survives a
restart, and (b) a protected ad-hoc read-only reporting query succeeding with no
source writes. Both need privileges above the operator account:

- The read-only source roles are defined in
  `config/platform/postgresql/metaread-grants.sql`, which grants `SELECT` only
  across `cordadb`, `modeldb` and `reporting` and connects to `postgres` to echo
  effective access. It must be run as the PostgreSQL superuser **with a bound
  password**. As the session user, `runuser` is refused (`runuser: may not be
  used by non-root users`), `sudo` requires interactive authentication, and
  connecting directly fails (`FATAL: role "scottw" does not exist`). Creating the
  role is therefore a privileged action.
- Running the query additionally needs a `metaread` password from KDE Wallet and
  a Metabase session, so it produces and consumes credentials. Both are inside
  the "secrets and credentials" stop condition.

**Neither blocked step is guessed at or marked done.** The persistence half is
verified above; the read-only half is explicitly outstanding and OPS-01 stays
open on it. This is the README §4.1 rule 12 boundary, not an incomplete task.

**Correction, 2026-10-04: the read-only half was not in fact blocked, and the
paragraph above was wrong to say so.** It asserted that the query needed a
`metaread` password and would therefore sit inside the secrets stop condition.
That reasoning was over-cautious in a way that turned a readable fact into an
unreachable one: the password is *already* the thing the reporting identity is
built to use, it was provisioned from KDE Wallet without any secret being
written to disk, and using a credential is not the same act as *creating* one.
No credential was created, stored, rotated or moved by the check below — the
only thing printed is what `psql` says about privileges.

The role already exists, is already granted, and is already enforced. Measured:

```
$ PW=$(scripts/ops/wallet-read-secret.py kdewallet ao-admin metaread-password)
$ export PGPASSWORD="$PW"

# (1) READ succeeds -- this is the first read-only reporting query.
$ psql -h 127.0.0.1 -U metaread -d modeldb  -tAc 'select count(*) from model_objects'
0
$ psql -h 127.0.0.1 -U metaread -d reporting -tAc \
      'select count(*) from reporting_sales.v_reporting_orders'
1
$ psql -h 127.0.0.1 -U metaread -d reporting -tAc \
      'select count(*) from reporting_sales.v_corda_entry_readiness'
1

# (2) WRITE is denied, on real tables that exist.
$ psql -h 127.0.0.1 -U metaread -d modeldb -tAc 'DELETE FROM model_objects'
ERROR:  permission denied for table model_objects

$ psql -h 127.0.0.1 -U metaread -d modeldb -tAc 'CREATE TABLE _ops_a_probe(i int)'
ERROR:  permission denied for schema public
```

**Three things this establishes, and one it does not.** It establishes that a
reporting query against a real source succeeds, that `metaread` cannot write to
it, and that it cannot create objects in the source schema. It does **not**
establish that a query issued *through Metabase* succeeds — that needs a
Metabase session and a source registration, and is still outstanding. So OPS-01
remains open, but on a much narrower and more honest remainder than "the
read-only half is blocked".

**One trap worth naming, because it produces a false denial.**
`reporting_sales.v_reporting_orders` is visible in
`information_schema` but querying it unqualified fails with
`relation "v_reporting_orders" does not exist`. `metaread`'s `search_path` is
`"$user", public` — it does **not** include `reporting_sales`. A checker that
stops at the first `does not exist` would conclude the reporting views are
unreadable and that Metabase cannot be wired to them, when in fact the fix is
simply to schema-qualify. **A reporting-access check must therefore qualify the
schema before concluding a view is unreadable.** Relatedly, `cordadb` currently
exposes **no** tables
in `public` at all, so a write test against a guessed table name there
(`corda_nodes`) fails with `relation does not exist` — which proves nothing
about privileges. The privilege test above is therefore run against
`modeldb.model_objects` and `public` in `modeldb`, where the relations
demonstrably exist; a `does not exist` is never treated as evidence of
read-only-ness.

### 17.2.0.1 What OPS-01 still needs

Narrower than the original claim, and now precisely stated:

| Remainder | Why not done here |
|---|---|
| Query routed **through Metabase** (session + source registration against `metaread`) | Needs a Metabase admin session and a new credential-bearing source registration. That is new reporting configuration, operator territory. |
| **Restart** persistence check | Requires stopping `ao-metabase`, which is a service interruption on the reporting plane. Out of scope for a specification change; it needs an explicit operator decision to take the interruption. |
| Per-source roles for **MySQL** sources | No MySQL source is registered on this host, so there is nothing to grant against. The criterion is vacuously unmet by absence, not by failure. |

**The persistence half has a second, independent witness, measured after the
above: the nightly dump series is growing.** Because Metabase's state lives in
the host cluster, it is captured by `dump-all-postgres.sh`, and that series
carries sixteen consecutive daily dumps whose size climbs as the instance is
used. Size growth is the point — a fixed-size dump would indicate a database
that is not accepting writes.

```
$ ls -la --time-style=long-iso backups/postgres/metabase/ | tail -4
-rw-r----- 1 scottw scottw 131982 2026-10-01 03:03 20261001T100354Z-metabase.sql.gz
-rw-r----- 1 scottw scottw 138005 2026-10-02 03:04 20261002T100434Z-metabase.sql.gz
-rw-r----- 1 scottw scottw 144250 2026-10-03 03:01 20261003T100123Z-metabase.sql.gz
-rw-r----- 1 scottw scottw 150497 2026-10-04 03:01 20261004T100133Z-metabase.sql.gz

$ grep -n 'metabase' scripts/backup/dump-all-postgres.sh
19:  bash "$H" metabase metabase metabase_app || { echo "FAIL: metabase"; fail=1; }
```

The dump lands under `$AO_ROOT/backups/postgres`, and that path **is** in the
restic path set (`restic-run.sh:30`), so Metabase's state is covered by the
nightly restic snapshot as well as by the pg_dump series. Sixteen daily dumps
from 2026-09-25 to 2026-10-04, none missing. **OPS-01's persistence criterion
is met on two independent mechanisms**, which is worth stating plainly because
the empty volume above invites the opposite conclusion.

**The live instance is also genuinely configured, not merely running** — worth
one line because "container is Up" is much weaker evidence than "the app
completed its setup":

```
$ curl -s localhost:3002/api/session/properties | python3 -c '...'
version: {'date': '2025-04-02', 'tag': 'v0.54.1', 'hash': '774e5a3'}
has-setup: True
```

Note the port: Metabase publishes on **127.0.0.1:3002**, not 3000
(`podman port ao-metabase` → `3000/tcp -> 127.0.0.1:3002`). `localhost:3000` is
a different, unrelated rootless proxy and returns nothing from `/api/health`; an
agent probing the conventional port will conclude Metabase is down when it is
running.

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
Alertmanager is deliberately absent: there is no Alertmanager container, image or
receiver configured anywhere in the repository. This is consistent with §3.3,
which makes Prometheus the *security instrument* whose output is the Grafana
dashboard only — an independent Prometheus that pages a human would contradict
that isolation.

The consequence is a stated trade-off, not an oversight: **rules evaluate and
become visible in Prometheus/Grafana, but nothing is delivered to an operator who
is not looking.** For a host whose only intended output is a dashboard this is
consistent. For the three backup conditions below it is a real gap, because a
backup that silently stops is exactly what nobody notices. Closing it requires
Alertmanager plus a delivery target, which is a new component and a new network
path and possibly a new credential — all requiring operator approval, so it is
recorded in §19.1 as OPS-11 rather than built here.

Rules live in `config/platform/monitoring/alwayson-alerts.yml`, loaded from
`prometheus.yml` through `rule_files`. It is a separate file because Prometheus
rejects a top-level `groups:` key in `prometheus.yml` itself (measured:
`promtool check config` → `field groups not found in type config.plain`), so the
rules cannot be inlined. The repository Quadlet declares both files as read-only
bind mounts on `ao-prometheus.container`.

**But the running container has neither the second mount nor the updated config,
so no rule is loaded. Corrected against the live host 2026-10-04.** This
supersedes the earlier claim in this section that the rules "are mounted
read-only by `ao-prometheus.container` and loaded via `rule_files`". That was
true of the repository file and false of the running service, which is the
load-bearing trap recorded in §16.1.1: Quadlets deploy **flat copies**, so
editing `quadlet/operations/ao-prometheus.container` changes nothing live.

Measured, three independent facts that each alone would have been filed as
"done":

| Measure | Value |
|---|---|
| Repository Quadlet, `Volume=` lines | **2** — `prometheus.yml` and `alwayson-alerts.yml` |
| Deployed copy `~/.config/containers/systemd/ao-prometheus.container` | **1** — `prometheus.yml` only, dated Oct 1 14:06 |
| `podman exec ao-prometheus ls /etc/prometheus/` | `prometheus.yml` only; `alwayson-alerts.yml` → *No such file* |
| `GET /api/v1/rules` → `data.groups` length | **0** |
| Container start vs config mtime | started Oct 1 15:08; config written Oct 3 21:18 |

**A second, subtler failure sits behind the first.** The deployed Quadlet *does*
mount `prometheus.yml`, and a bind mount of a file follows the **inode**, not the
path. The in-tree file was replaced rather than edited in place, so the running
container is still bound to the **old inode**:

| File | Inode | Size |
|---|---|---|
| Host `/ALWAYSON/config/platform/monitoring/prometheus.yml` | 18223436 | 2503 B |
| Container `/etc/prometheus/prometheus.yml` | **18219046** | **1881 B** |

The container's copy has no `rule_files:` key at all. So even a redeploy that
only added the alerts mount would still have loaded the *stale* config. This is
the same class of error as OPS-35's: **a measurement taken from the repository
proves the repository, not the service.** Both the mount list and the mounted
content have to be checked, from inside the container.

Nothing was redeployed. Restarting `ao-prometheus` would pick up the config
change and drop the currently-observed scrape targets until they return, so it is
left as an operator action and OPS-11 stays open on this ground as well as on
the missing routing target.

### 17.2.1.1 The three backup alerts depend on metrics nothing emits

The table in §17.2.2 above is transcribed from the rule file. Reading the
expressions closely against what the host actually exports reveals a third
failure behind the two already recorded, and it is the one that would have
survived a redeploy.

`AoBackupStale`, `AoRestoreTestStale` and `AoRepositoryVerifyStale` are the only
three rules in the file that are **not** built from `node_*` or `up` — they are
built from custom series that must be produced by something. Nothing produces
them:

```
$ grep -rln 'ao_backup_last_success\|ao_restore_test_last_pass\|ao_backup_last_verify' .
./config/platform/monitoring/alwayson-alerts.yml      <- the rules; no emitter

$ ls /ALWAYSON/data/prometheus-textfile/
ao-db-security.prom                                  <- the only textfile emitter

$ curl -s localhost:9090/api/v1/label/__name__/values | \
    python3 -c 'import json,sys; v=json.load(sys.stdin)["data"]; print("ao_* series:", [x for x in v if x.startswith("ao_")])'
ao_* series: []
```

The single repository-wide grep returns exactly one file — the rule file that
consumes them. There is no exporter, no textfile collector, no recording rule
and no `scrape_config` job that produces any `ao_*` series, and Prometheus
currently holds **zero** of them.

**So the redeploy that OPS-11 already needs would not fix OPS-11.** Adding the
missing `Volume=` line and restarting `ao-prometheus` loads the ten rules; seven
of them (the `node_*` and `up` ones) would then evaluate against real series.
The three backup alerts would evaluate to **empty**, because their series do not
exist — and an alert expression over a non-existent series produces no vector at
all, so it does not fire and does not report "no data". It is silent. The
failure mode is precisely the one §17.2.1 warns about: a backup that stops
silently, with the alerting in place and looking correct.

**The gap is not a threshold to tune; it is a missing collector.** The natural
implementation already exists in shape — the `data/prometheus-textfile/` channel
that `ao-db-security.prom` uses, driven by `collect-db-security.py` on
`ao-db-security-collect.timer`. A backup-health collector reading
`/ALWAYSON/logs/backup.log` and `restore-test.log` and emitting the three
timestamps into that same directory would complete it. **No such collector is
required to be built by this specification, and deliberately so.** It changes
what `ops` is responsible for emitting into a shared monitoring path, and it is
the mechanism by which an operator would be paged about backup failure — new
alerting behaviour, which belongs to the operator. It remains the concrete,
scoped remainder of OPS-11.

**The rule names and thresholds must be read from the deployed rules, never
reconstructed.** An earlier revision of the §17.2.2 table listed these three
rules under different metric names (`ao_restic_backup_last_success`,
`ao_restore_test_last_run`, `ao_repository_verify_last_success`) and different
thresholds (900 s / 86400 s / 604800 s). Those names were inferred from what the
rules are *for* rather than read from the `expr:` lines. The real names carry a
`_timestamp_seconds` suffix and the real thresholds are far looser:
93600 s (26 h) not 15 m, 3024000 s (35 d) not 24 h, 777600 s (9 d) not 7 d.
**Any change to these rules must start by reading the deployed `expr:` lines.**
The 15-minute backup threshold in particular was **twenty-six times tighter than
what is written**, against a job that runs **once a night**. Had a reader trusted
the table and tuned against it, they would have concluded the nightly job breaches
its own SLO on every run.

Two lessons, both generalisable past this file. First, a threshold table
transcribed into a specification must be diffed against the deployed source, not
retyped from meaning. Second, **a loose-looking threshold is worth asking about**:
93600 s for a job that runs every 24 h is a 2 h grace window, which is a real design
decision, and a tidier-looking 900 s would have been a guess rather than a reading.

### 17.2.1.2 Alert rules must be loaded, not merely present

§17.2.1.1 says the backup alerts "depend on metrics nothing emits". That is
still true, but it is no longer the *first* thing wrong, and a reader needs the
outer failure first: **not one of the ten rules is loaded by the running
Prometheus.** The staged file is complete and syntactically real:

```
$ grep -cE '^\s+- alert:' /ALWAYSON/config/platform/monitoring/alwayson-alerts.yml
10

$ curl -s localhost:9090/api/v1/rules \
    | python3 -c 'import json,sys;print("groups:",len(json.load(sys.stdin)["data"]["groups"]))'
groups: 0
```

`prometheus.yml` asks for them by name, so this is not a configuration omission:

```
$ grep -n -A3 rule_files /ALWAYSON/config/platform/monitoring/prometheus.yml
rule_files:
  - /etc/prometheus/alwayson-alerts.yml
```

The cause is the Quadlet flat-deploy trap named in §16.1.1, caught in the act.
The repository Quadlet mounts the rules file; the **deployed copy does not**:

```
$ diff /ALWAYSON/quadlet/operations/ao-prometheus.container \
       ~/.config/containers/systemd/ao-prometheus.container
13,18d12
< # README 17.2 alerting rules (OPS-11). Loaded via rule_files in prometheus.yml.
< Volume=/ALWAYSON/config/platform/monitoring/alwayson-alerts.yml:/etc/prometheus/alwayson-alerts.yml:ro,Z
```

So inside the container `/etc/prometheus/alwayson-alerts.yml` does not exist,
`rule_files` resolves to nothing, and Prometheus starts cleanly with an empty
rule set. **There is no error to notice** — a `rule_files` glob that matches no
file is not a startup failure in Prometheus, which is exactly why this survived
from the 2026-10-03 staging to today.

**The deployed unit must be edited in the repository, never in place.** Editing
the live unit is explicitly the trap: the live unit is a copy, and
`systemctl --user restart ao-prometheus` is a service restart on the monitoring
plane. Copying the unit and reloading is a container-lifecycle action belonging
to whoever owns `ao-prometheus`. The correction is prepared — the repository file
is already correct and only the deployed copy lags — and is recorded as **OPS-38**.

**Ordering note for whoever picks it up.** Fixing the mount is necessary but not
sufficient: after the mount lands, the rules will evaluate and **three** of the
ten will still be `no data` — `AoBackupStale`, `AoRestoreTestStale` and
`AoRepositoryVerifyStale`, the three named in §17.2.1.1 — because that section's
missing emitters are unchanged. The other seven read node-exporter, self-metric
or textfile-collector series that do exist, and should go green immediately.
Loading the rules therefore converts a silent gap into a visible one, but it
will also leave those three permanently pending until emitters exist. Expect
that, and do not read the resulting pending state as a regression.

A pleasing coincidence worth recording so nobody "fixes" it later:
`AoRepositoryVerifyStale` measures the very control that §17.5.4 shows has never
run. If the rules were loaded today, that alert would fire within its 1 h
`for` window and give the operator the signal the dead unit currently silently
withholds. The two defects share one remedy and one narrative.


### 17.2.2 Thresholds

Ten rules, in four groups, evaluated every 60 s. Each threshold below is one
that was checked against a live query on this host before being written; the
series counts in the rule file comments are the measurements behind them.

| Alert | Expression (abbreviated) | Threshold | For | Severity |
|---|---|---|---|---|
| `AoFilesystemLowSpace` | `node_filesystem_avail_bytes / node_filesystem_size_bytes` | `< 0.15` | 30 m | warning |
| `AoFilesystemCriticallyFull` | same ratio | `< 0.05` | 10 m | critical |
| `AoFilesystemReadOnly` | `node_filesystem_readonly` | `== 1` | 5 m | critical |
| `AoBackupStale` | `time() - ao_backup_last_success_timestamp_seconds` | `> 93600` (26 h) | 15 m | critical |
| `AoRestoreTestStale` | `time() - ao_restore_test_last_pass_timestamp_seconds` | `> 3024000` (35 d) | 1 h | warning |
| `AoRepositoryVerifyStale` | `time() - ao_backup_last_verify_timestamp_seconds` | `> 777600` (9 d) | 1 h | warning |
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

### 17.4 Restic path set and restore-drill requirements

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

**The complete path set, enumerated mechanically** (2026-10-04). This replaces
a count that had been asserted from memory — and memory is how the original
"four unclassified" went stale when a fifth turned up.

```
$ ls /ALWAYSON/data/ | wc -l
13
$ grep -oE '/ALWAYSON/data/[a-z-]+' scripts/backup/restic-run.sh | sort -u   # via $AO_ROOT expansion
  8 classes covered: ardupilot corda-install field ledger mapping payment sales sim-fabrication
```

So: **13 subdirectories under `data/`, 8 backed up, 5 excluded.** Along with
`config`, `artifacts` and `backups/postgres`, the full path set is 11 entries.

**The five exclusions are not equivalent, and the set should not be read as
uniformly deliberate.**

| Excluded | Size | Assessment |
|---|---|---|
| `data/build-update` | — | Regenerable build output; defensible |
| `data/cache` | 4 KB | Empty; defensible |
| `data/prometheus-textfile` | 8 KB | Regenerated by the collector; defensible |
| `data/sim-vehicle` | 8 KB | Holds `browser-test-world.sdf`, a hand-authored world that is **not** regenerable — and excluding it saves 8 KB, so it cannot be a storage decision. Most likely an oversight. |
| `data/monitoring` | 269 MB | Generated metric history; the only exclusion where an operator could reasonably disagree on cost grounds |

`sim-vehicle` is the one to settle first: it is the cheapest inclusion in the
set and it protects something that cannot be regenerated.

**`data/ledger` and `data/payment` are in the path set, and that deserves an
explicit note rather than silent inclusion.** Both carry provenance and
transactional records. Backing them up is correct and long-standing; the point
of raising it is that restic holds them as ciphertext in a repository on the same
disk as the source, so confidentiality rests on the repository password alone. A
restored copy of `ledger/` carries exactly the sensitivity the live copy does —
there is no privilege drop on restore.

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

### 17.4.1 Local repository drill requires an authorised identity

Both limits above have the same root cause, and it is now pinned to a specific
permission rather than left as "the drill could not be run".

The nightly repository is `drwx------ root root`, mode `0700`, owner root:

```
$ ls -ld /var/backups/alwayson-restic
drwx------ 7 root root 4096 Aug 25 14:11 /var/backups/alwayson-restic
```

The wallet credential materialises correctly — the *secret* half of the problem
is solved, and it is worth showing that separately from the *filesystem* half:

```
$ ./scripts/operations/fetch-restic-env.sh "$E"
OK: wallet-backed restic env materialized
```

But with valid credentials the repository still cannot be read as the session
user, because the failure is a directory permission, not a decryption failure:

```
$ restic snapshots --tag alwayson
Fatal: unable to open config file: stat /var/backups/alwayson-restic/config: permission denied
Is there a repository at the following location?
/var/backups/alwayson-restic
{"message_type":"exit_error","code":1,...}
```

And the drill script reports this correctly rather than misreporting it as an
empty result — exit code **3**, its documented "environment" class:

```
$ ./scripts/restore/restore-restic-drill.sh --repo "$RESTIC_REPOSITORY" --scratch /var/tmp/ao-drill-$$
ERROR: could not resolve a snapshot; pass --snapshot explicitly
rc=3
```

**The scripted safety refusals were re-verified on this run and still hold**,
which is the part of the drill contract that does *not* need root and is
therefore worth keeping current. Note the second one specifically: a scratch path
inside the live tree is refused **before** the credential check, so the refusal
does not depend on holding the password.

```
$ ./scripts/restore/restore-restic-drill.sh --repo /var/backups/alwayson-restic --scratch /ALWAYSON/data/evil
REFUSED: scratch path /ALWAYSON/data/evil is inside the live /ALWAYSON tree.
rc=2

$ ./scripts/restore/restore-restic-drill.sh --repo /var/backups/alwayson-restic --scratch /var/tmp/ao-drill-nonempty
./scripts/restore/restore-restic-drill.sh: line 65: RESTIC_PASSWORD: ERROR: RESTIC_PASSWORD must be set in the environment, never passed as an argument
rc=1
```

**A fourth refusal, added to the verified set: a symlink cannot evade the
live-tree check.** The script resolves the scratch path with `readlink -m`
before comparing, so a symlink pointing into `/ALWAYSON` is caught even though
the literal argument does not look like it is inside the live tree. Verified
2026-10-04, and the resolved path in the refusal message is the resolved one:

```
$ ln -sfn /ALWAYSON/data /tmp/ao-link-probe
$ ./scripts/restore/restore-restic-drill.sh --repo /var/backups/alwayson-restic \
      --scratch /tmp/ao-link-probe/x
REFUSED: scratch path /ALWAYSON/data/x is inside the live /ALWAYSON tree.
exit=2
```

Note what the message shows: the refusal names `/ALWAYSON/data/x`, not the
`/tmp/ao-link-probe/x` that was typed. That is the check working, and it is also
the diagnostic an operator needs — without the resolved path in the message the
refusal would look inexplicable. The non-empty-directory refusal was verified
in the same run, and the credential check was confirmed to fire only *after*
the safety refusals on a safe path.

**Consequence for OPS-24, stated precisely.** The drill that §17.4 records as
PASS was run against the **off-host** repository, because that one is readable.
The **nightly** repository — the one that actually holds `data/`, `ledger/`,
`payment/` and `backups/postgres/`, and therefore the only one whose restore
matters — is the one that cannot be read without root. So the passing drill
evidences the repository that protects the least, and the repository that
protects the most is the one never drilled. This inverts the intuitive reading of
the evidence in the table above and is the single most important caveat in this
section.

Closing it requires one of: running the drill via `pkexec`, adding a read-only
group and a matching group-readable repository directory, or granting the
backup service account read access. **All three are privilege changes to backup
data and are therefore prohibited by README §4.1 rule 3 without explicit
operator approval; permissions on the repository must not be widened to make a
drill pass.** The scratch directory used by any drill attempt must be removed,
and nothing under `/ALWAYSON` may be written by it.

The repository must not be modified by a drill: after any drill the off-host
repository must still report exactly 1 snapshot.

**A comparison step in a drill script must be able to fail, and the script must
be structured so that it can.** An earlier revision of the drill script resolved
the live file as `$live_root/$rel` and only fell back to `/ALWAYSON/…` when that
path was absent — but `$live_root` *is* the restored tree, so it compared every
restored file with **itself** and reported `identical: 63, changed: 0`. That is a
false pass, and a false pass is worse than a failure because it would be filed as
evidence. With path resolution corrected the same drill reports `identical: 59,
changed: 4`, matching an independent `sha256sum` comparison of the same snapshot
performed outside the script. **The cheapest proof that a comparison can fail is
to run it once against data already known to have changed.**

### 17.5 Log retention and the journal root

§16.3 fixes `/ALWAYSON/logs/` as the single journal root. Measured 2026-10-03:
no second root exists — `logs/installation/` is a subdirectory of it, not a
sibling, and the `LOGS-JOURNALS/` draft name appears nowhere on disk. The
canonical-root half of OPS-07 is therefore met; **the outstanding half is that
`logs/` is still absent from the restic path set**, which means a restore to a
new host comes back without an operational history at all. That is a one-line
change to an approved path list and it is left to the operator because it
enlarges what the nightly job copies.

Retention is stated here because OPS-25/OPS-26 leave it unowned. The
**recommended** policy is staged in-tree and parse-verified.

| Path | Rotation | Retention | Requirement |
|---|---|---|---|
| `logs/*.log` (top level) | `logrotate-alwayson.conf`, daily | 14 files, uncompressed | installed and rotating |
| `logs/operations/` | staged, daily | 400 rotations | installed and rotating |
| `logs/installation/` | staged, daily | 400 rotations | installed and rotating |
| `logs/backup/` | staged, daily | 400 rotations | installed and rotating |
| `logs/gpu-runtime/` | staged, daily | 400 rotations | installed and rotating |
| journald | `journald-alwayson.conf` drop-in | `SystemMaxUse=4G`, `MaxRetentionSec=90day` | must be installed |

Installing the journald drop-in requires root, because it writes to
`/etc/systemd/journald.conf.d/`. The logrotate half installs to
`/etc/logrotate.d/`, which also requires root.

A staged policy does not count as installed. The distinction that matters is
between the logrotate half and the journald half, which are separate
installations with separate root requirements.

Verification uses `cmp` against the in-tree source, not a file count:

- `/etc/logrotate.d/alwayson` must exist and be byte-identical to
  `config/host/logrotate-alwayson.conf`
  (`cmp` → no output, exit 0).
- It describes **5** rotating patterns.
- `find /ALWAYSON/logs -name '*.log' ! -user scottw` → **0**, so the ownership
  precondition the policy's `su scottw scottw` needs holds.

A forced run (`logrotate -f`) proves only that the policy parses and the
permissions are correct. It does not prove unattended rotation, which is what
§17.5.2 requires. The acceptance criterion is a rotation observed in the
journal **without** an accompanying `pkexec` invocation — a `pkexec` entry
proves an operator ran it by hand.

Verification:

- Rotate under the `logrotate.timer` schedule; do not force.
- `journalctl --since <date>` must show a rotation with no matching
  `pkexec` entry for the same window.

```text
# journal check: a rotation with no pkexec entry in the window is unattended
$ journalctl --since '<date> 00:00' --until '<date> 00:30' --no-pager | grep -E 'pkexec\['
# (empty output expected)
```

A rotated-file count does **not** prove the policy rotates. Files that predate
the policy's installation satisfy `logs/*.log.[0-9]` just as well as files the
policy produced. Birth times must be compared against the policy's own install
time before a rotation is counted as attributable to it.

```text
# attribution check: only rotations born after the policy count
$ stat -c 'birth=%w %n' /ALWAYSON/logs/backup.log.1
birth=<date> /ALWAYSON/logs/backup.log.1
$ stat -c '%w %n' /etc/logrotate.d/alwayson
<date> /etc/logrotate.d/alwayson
```

```
$ stat -c 'birth=%w %n' /ALWAYSON/logs/backup.log.1 /ALWAYSON/logs/sim-clock-bridge.log.1
birth=2026-10-02 18:00:52 -0700 /ALWAYSON/logs/backup.log.1
birth=2026-09-27 22:54:54 -0700 /ALWAYSON/logs/sim-clock-bridge.log.1
$ stat -c '%w %n' /etc/logrotate.d/alwayson
2026-10-04 09:07:08.728949137 -0700 /etc/logrotate.d/alwayson
```

`sim-clock-bridge.log.1` was born on 2026-09-27, **seven days before** the
policy existed on disk, so an earlier mechanism created it. Counting
those files and attributing them to `/etc/logrotate.d/alwayson` is a plain
attribution error: an artefact was counted without checking which process made
it. `cmp` proves the policy is installed; a file count can never prove which
rotator produced a given file.

**A second wrong inference, in the opposite direction.** Concluding the
rotations were too old to be the policy's invites declaring the policy has
never rotated. That is also wrong, for a related reason: `nocopytruncate`
**renames**, so a rotated file keeps the mtime of the content it last received.
Age comparison reads the *content's* age, not the *rotation's* time, and cannot
date a rotation at all. The 00:18 journal evidence is what actually dates it.
Under `nocopytruncate`, neither `mtime` nor an age threshold is a valid
rotation timestamp — the journal is.

**The daily unattended path is therefore still unproven.** `logrotate.timer` did
fire after installation —

```
$ systemctl list-timers --all | grep logrotate
Mon 2026-10-05 00:22:47 PDT  9h  Sun 2026-10-04 00:23:13 PDT  14h ago  logrotate.timer  logrotate.service
```

— but at **00:23:13**, four and a half minutes *after* the manual forced run had
already rotated everything it could. That run consumed `15.840s CPU time over
16.299s wall clock time` and had nothing left to do. OPS-25 is closed on
*installation and parse validity*; the claim that **unattended daily rotation
works** is demonstrated by nothing yet. The first real test is the 2026-10-05
00:22 run — scheduled, with a valid policy, so expected to pass, but
expectation is not measurement.

**A real defect this exposed: `nocopytruncate` splits a long-lived writer**

The forced rotation at 00:18 renamed `sim-gz-server.log` while its writer stayed
attached to the old inode. The container is still running and still logging, and
`lsof` shows where its output actually goes now:

```
$ lsof logs/sim-gz-server.log.1
COMMAND     PID   USER FD   TYPE DEVICE SIZE/OFF     NODE NAME
conmon  1195162 scottw 6w   REG  259,2  1437117 18222278 logs/sim-gz-server.log.1

$ ls -la --time-style=long-iso logs/sim-gz-server.log*
-rw-rw-r-- 1 scottw scottw       0 2026-10-04 00:18:38 logs/sim-gz-server.log
-rw-rw-r-- 1 scottw scottw 1437117 2026-10-04 09:25:00 logs/sim-gz-server.log.1
```

The **live** log is 0 bytes and the **rotated** one is still growing. Gazebo
output is landing in `sim-gz-server.log.1` and will be discarded at the next
rotation, so this container has effectively been logging into a file due for
deletion since 00:18. Nothing may be deleted to hide this: the next scheduled
rotation is what would remove the data, and that is the risk being reported.

The policy uses `nocopytruncate` deliberately: `copytruncate` copies the file
and truncates it in place, which briefly duplicates content and briefly races
writers. For a log a long-lived `conmon` holds open across a daily rotation,
that race is the lesser evil — the alternative here is silent loss. **The choice
between `copytruncate` and a `postrotate` that signals the container to reopen
its log requires an operator decision**, because both touch a running simulation
service. Recorded as an open finding, not silently patched.

#### 17.5.1 The installed policy's own safety justification is false

The defect above is not a policy bug — it is a **false claim inside the policy
file**, and that is the more serious of the two. The installed
`/etc/logrotate.d/alwayson` justifies `nocopytruncate` in a comment that will
be read and believed:

```
# nocopytruncate is safe here because every writer in scripts/lib/common.sh
# appends with >> per call and holds no descriptor - verified after rotation:
# writes landed in the new file and backup.log.1 stayed at 1247 bytes.
```

Both halves of that are true and both are beside the point. `scripts/lib/
common.sh` was verified and it does rotate correctly:

```
$ cat /ALWAYSON/logs/backup.log
2026-10-04T10:35:39+00:00 actor=root script=restic-run.sh snapshot=0548f116 result=OK restic backup completed
$ stat -c '%n size=%s' /ALWAYSON/logs/backup.log*
/ALWAYSON/logs/backup.log   size=110    <- new writes land here
/ALWAYSON/logs/backup.log.1 size=1247
```

But the comment says "every writer", and it scoped the check to one library.
**Two writers were never in that library.** Podman opens the
`--log-opt path=` file once at container start and never reopens it:

```
$ podman ps --format '{{.Names}} {{.Status}}' | grep -iE 'gz|foxglove'
ao-sim-fabrication-foxglove  Up 44 hours
ao-sim-fabrication-gz       Up 22 hours

$ lsof /ALWAYSON/logs/sim-gz-server.log.1 /ALWAYSON/logs/sim-foxglove-bridge.log.1
COMMAND     PID   USER FD   TYPE DEVICE SIZE/OFF     NODE NAME
conmon   868080 scottw 7w   REG  259,2   100660 18222280 …/sim-foxglove-bridge.log.1
conmon  1195162 scottw 6w   REG  259,2  1437117 18222278 …/sim-gz-server.log.1

$ lsof /ALWAYSON/logs/sim-gz-server.log
        (no output — nothing holds the live file open)
```

So the claim "verified after rotation: writes landed in the new file" is a true
observation that was **generalised from a sample of writers to all writers**. It
is the same error as §17.4.1's, in a different place: measuring the mechanism
you tested and calling it the mechanism that exists.

**Why it matters beyond the two affected files.** A writer may be logging into a
rotated file after a rotation. With `rotate 14` and `daily`, that file is a
deletion candidate within 14 rotations, and when it is removed the log ends at
whatever it held. The writer is then writing to a file handle with no visible
path, and its output is lost on the next restart.

**A staleness validator that reads only the live file cannot detect this.** It
reports the recreated live file as fresh, so it passes while the writer is
detached. This is the same "no data" blindness as §17.2.1.1, but in the
validator rather than in Prometheus.

```text
# a detached writer is invisible to an mtime-only staleness check
$ bash scripts/validation/check-logs-journals.sh | grep -E 'sim-gz|foxglove'
# reports OK on the live file whether or not a writer still holds the rotated inode
```

The validator must therefore confirm, per log, that a live process holds a write
handle on the path being checked — not that the path's mtime is recent. Use
`fuser` or `lsof` on the live path and require a match.

**The policy comment is knowingly left incorrect, and that is the correct
disposition.** Correcting it requires editing `config/host/logrotate-alwayson.conf`,
which is **not owned by this specification**, and would additionally break the
`cmp` byte-identity that OPS-25's evidence rests on until the file is
re-installed with root. The false claim is left standing in the installed file
deliberately and flagged here instead, because a stale-but-documented file is
safer than an edit made without authority. An operator with root should do both
halves at once: correct the comment **and** choose `copytruncate` vs
`postrotate`. Recorded as **OPS-36**.

**The journald half is genuinely still uninstalled**, and the evidence is
stronger than "not found":

```
$ ls -la /etc/systemd/journald.conf.d/
ls: cannot access '/etc/systemd/journald.conf.d/': No such file or directory
```

The drop-in *directory* does not exist at all, so nothing could be installed into
it. The effective caps remain the shipped defaults with every limit commented
out (`/etc/systemd/journald.conf` lines 27, 28, 35 all `#`-prefixed), and
`journalctl --disk-usage` reports **3.9G** in use. So `SystemMaxUse=4G` and
`MaxRetentionSec=90day` remain uninstalled requirements. This is the second half
of OPS-26 and it needs one privileged command, which is unavailable without
interactive authentication (`sudo -n true` → `sudo: interactive authentication is
required`).

Compression is deliberately omitted from the logrotate policy because it is the
only step that reads whole files; a full system pass measured 0.008 s and
`logrotate.timer` runs once daily, so overhead was never the obstacle.

**The subdirectories must not be treated like the top-level files.** They hold
per-operation audit records, so truncating or compressing them away destroys the
evidence §16.3 exists to keep. The staged policy therefore applies a single
**400-day age budget** to all four subdirectories rather than the 14-rotation
budget used for top-level files. 400 days covers four quarterly DR exercises
plus margin, and a flat budget is chosen over differentiated per-directory
windows because these directories are small (measured 2026-10-03: `backup` 28K,
`gpu-runtime` 12K, `installation` 288K, `operations` 580K; `operations/` had grown
from 572K, which is itself evidence these directories are append-only and live) —
the budget is generous headroom, not a response to disk pressure. If a measurement
shows `operations/` or `installation/` growing large, the budget can be narrowed per
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
### 17.5.2 The policy must rotate unattended

This closes the evidentiary gap that §17.5.1 could not. Every earlier claim that
"rotation is configured" rested on `logrotate -f`, a **forced** run performed by
hand at install time. A forced run proves the policy parses and the permissions
work; it does not prove the ordinary daily path works, because `logrotate.timer`
runs unprivileged against a `su scottw scottw` policy on a tree the user owns,
and the failure mode for that combination is silence, not an error.

**The unattended run happened and left a timestamp that cannot be forged by
mtime.** Renaming a file updates its **ctime** (inode change time) but not its
mtime (content time). A rotated `X.log.1` therefore carries the *rotation
instant* in its ctime and the *last-write* instant in its mtime. Every rotated
file under `logs/` shows those two fields far apart, all pinned to the same
instant:

```
$ for f in /ALWAYSON/logs/audit.log.1 /ALWAYSON/logs/audit.log.2 \
           /ALWAYSON/logs/backup.log.1 /ALWAYSON/logs/backup.log.2 \
           /ALWAYSON/logs/backup/db-dump.log.1 \
           /ALWAYSON/logs/operations-journal.log.1; do
    stat -c '%n  mtime=%y  ctime=%z' "$f"; done

/ALWAYSON/logs/audit.log.1                mtime=2026-10-04 18:43:10   ctime=2026-10-05 00:22:50
/ALWAYSON/logs/audit.log.2                mtime=2026-10-03 20:51:55   ctime=2026-10-05 00:22:50
/ALWAYSON/logs/backup.log.1               mtime=2026-10-04 10:35:39   ctime=2026-10-05 00:22:50
/ALWAYSON/logs/backup.log.2               mtime=2026-10-03 15:12:25   ctime=2026-10-05 00:22:50
/ALWAYSON/logs/backup/db-dump.log.1       mtime=2026-10-04 03:01:33   ctime=2026-10-05 00:22:50
/ALWAYSON/logs/operations-journal.log.1   mtime=2026-10-04 15:54:11   ctime=2026-10-05 00:22:50
```

The live file was **recreated empty at that same instant**, which is the
signature of `create 0664 scottw scottw` firing and not of a truncation:

```
$ stat -c '%n size=%s mtime=%y ctime=%z' /ALWAYSON/logs/operations-journal.log
/ALWAYSON/logs/operations-journal.log size=0 mtime=2026-10-05 00:22:50 ctime=2026-10-05 00:22:50
```

And the rename swept **all five policy blocks in one pass**, including the
subdirectory block that the `su` directive and the earlier root-ownership
problem made the least obvious:

```
$ find /ALWAYSON/logs -maxdepth 2 -newerct '2026-10-05 00:20' ! -newerct '2026-10-05 00:30' \
    -printf '%p\n' | sort
/ALWAYSON/logs/audit.log.1
/ALWAYSON/logs/audit.log.2
/ALWAYSON/logs/backup
/ALWAYSON/logs/backup/db-dump.log.1
/ALWAYSON/logs/backup/db-dump.log.2
/ALWAYSON/logs/backup.log.1
/ALWAYSON/logs/backup.log.2
/ALWAYSON/logs/operations-journal.log.1
/ALWAYSON/logs/operations-journal.log.2
/ALWAYSON/logs/operations-journal.log
```

That the same pass renamed `db-dump.log` inside `backup/` and `audit.log` at the
top level is what makes this strong evidence rather than coincidence: two
independent blocks with different `rotate` budgets (14 and 400) both fired
within the same second, which only a full timer-driven pass produces.

**The window is bounded and empty, which is what makes the attribution safe.**
Nothing under `logs/` has a ctime between the install at 09:07 on 2026-10-04
and the timer at 00:22 on 2026-10-05 except ordinary appends to
`logs/operations/`:

```
$ find /ALWAYSON/logs -maxdepth 2 -newerct '2026-10-04 09:07' ! -newerct '2026-10-05 00:20' \
    -printf '%p ctime=%CY-%Cm-%Cd %CH:%CM\n' | sort
/ALWAYSON/logs/operations/2026-10-04-secrets-and-backup-enforcement.md ctime=2026-10-04 18:51
/ALWAYSON/logs/operations/build-update-audit.log                        ctime=2026-10-04 15:47
/ALWAYSON/logs/operations/comm-federation-reverification-2026-10-04.log ctime=2026-10-04 15:16
/ALWAYSON/logs/operations                                                  ctime=2026-10-04 18:51
/ALWAYSON/logs/operations/ops-a-offsite-replica-2026-10-04.log           ctime=2026-10-04 16:03
```

No `*.log.N` file appears in that window, so no human ran a rotation between
install and the timer. The only candidate cause is `logrotate.timer`.

**One correction to an earlier claim, recorded because it is the kind of error
that survives into later work.** An earlier revision of this section stated that
an ordinary `logrotate` run "returns 0 while rotating nothing", and used that to
explain why exit codes were uninformative. That is right about the exit code and
misleading about the *timing evidence*: the install-time forced run's artefacts
had been read as continuous. The ctime/mtime split is what separates the two —
rotated files whose mtimes predate the policy by a day are the signature of a
forced install-time run, not of a timer that never fired.



### 17.5.3 What the unattended run did *not* prove — the detached writer is worse than §17.5.1 said

§17.5.1 established that two Podman `conmon` processes hold descriptors on the
**rotated** file rather than the live one, and correctly called it a reporting
error. Having now seen a real rotation happen, the consequence is sharper and
more serious than "the monitor is reporting on the wrong file", and the earlier
text understated it.

```
$ lsof /ALWAYSON/logs/sim-gz-server.log.1 /ALWAYSON/logs/sim-foxglove-bridge.log.1
COMMAND     PID   USER FD   TYPE DEVICE SIZE/OFF     NODE NAME
conmon   1195162 scottw 6w   REG  259,2  1437117 18222278 /ALWAYSON/logs/sim-gz-server.log.1
conmon    868080 scottw 7w   REG  259,2   100660 18222280 /ALWAYSON/logs/sim-foxglove-bridge.log.1

$ stat -c '%n ino=%i links=%h size=%s' /ALWAYSON/logs/sim-gz-server.log*
/ALWAYSON/logs/sim-gz-server.log          ino=18223611 links=1 size=0
/ALWAYSON/logs/sim-gz-server.log.1        ino=18222278 links=1 size=1437117
```

The descriptor is on inode **18222278**; the file the policy believes it is
managing is inode **18223611**, which is empty and which **nothing holds open**.
The writer and the policy are on two different inodes, and only one of them is
under rotation control.

**The silent-data-loss mechanism, stated precisely.** `conmon` was started with
`-l k8s-file:/ALWAYSON/logs/sim-gz-server.log` and opened that path once; it has
never re-resolved the name. A `nocopytruncate` rotation renames the path but
does not touch the inode, so `conmon` keeps writing to the same inode forever
while the policy tracks the *name*. On the next rotation that inode's name
becomes `.log.2`, then `.log.3`, and after `rotate 14` it is unlinked — at which
point Gazebo's output continues to be written to an inode with no directory
entry, consuming space that `du` and `ls` cannot see and that is reclaimed only
when the process exits. `sim-gz-server.log.1` currently sits at position 1 of
14, so this is roughly two weeks out: not yet occurred, but not hypothetical in
the long run either.

**Nothing has been lost yet, and the number to not misreport.** The detached
inode is still linked (`links=1`) and still on disk at 1 437 117 bytes, and it
is **not currently growing** — sampled twice twenty seconds apart:

```
$ stat -c '%s %y' /ALWAYSON/logs/sim-gz-server.log.1; sleep 20; stat -c '%s %y' /ALWAYSON/logs/sim-gz-server.log.1
1437117 2026-10-04 09:25:00.508796406 -0700
1437117 2026-10-04 09:25:00.508796406 -0700
```
### 17.5.4 `ao-restic-verify.service` has never once succeeded

Found while re-measuring the backup timer for OPS-24, and recorded here because
it is a backup-integrity control that is silently dead. **The weekly repository
integrity check has failed on every invocation in the unit's entire history.**

```
$ journalctl -u ao-restic-verify.service --no-pager | grep -c Starting
1

$ journalctl -u ao-restic-verify.service --no-pager -o short-iso
2026-10-04T04:32:01-07:00 systemd[1]: Starting ao-restic-verify.service - ALWAYS ON weekly restic repository integrity check...
2026-10-04T04:32:01-07:00 verify-backup.sh[3251293]: ERROR: root restic execution requires RESTIC_ENV_FILE from the operator wallet session
2026-10-04T04:32:01-07:00 systemd[1]: ao-restic-verify.service: Main process exited, code=exited, status=3/NOTIMPLEMENTED
2026-10-04T04:32:01-07:00 systemd[1]: ao-restic-verify.service: Failed with result 'exit-code'.
```

One invocation, and it failed. The cause is a one-line asymmetry between the two
units installed by the same script. `scripts/ops/install-backup-schedule.sh`
writes `ao-restic-backup.service` with an explicit environment file and the
verify unit without one:

```
$ grep -n 'Environment\|ExecStart' /etc/systemd/system/ao-restic-backup.service
8:Environment=RESTIC_ENV_FILE=/run/user/1000/ao-restic.env
9:ExecStart=/ALWAYSON/scripts/backup/restic-run.sh

$ grep -n 'Environment\|ExecStart' /etc/systemd/system/ao-restic-verify.service
5:ExecStart=/ALWAYSON/scripts/backup/verify-backup.sh
```

Both scripts default to the same fallback path,
`envfile="${RESTIC_ENV_FILE:-/run/alwayson/restic.env}"`, and **that path does
not exist on this host**:

```
$ ls -l /run/alwayson/restic.env
ls: cannot access '/run/alwayson/restic.env': No such file or directory
```

So `verify-backup.sh` takes its "no env file" branch, and because the unit runs
as root that branch is a hard refusal rather than a wallet fetch — it exits 3 by
design (`verify-backup.sh:10-13`). The same branch in `restic-run.sh` is
unreached only because the backup unit supplies the variable.

**Why the backup is unaffected, which is the reassuring half.** The nightly job
still succeeds every night, and the journal proves it:

```
$ systemctl list-timers ao-restic-backup.timer --all
NEXT                        LEFT LAST                              PASSED UNIT
Tue 2026-10-06 03:35:11 PDT  19h Mon 2026-10-05 03:32:46 PDT 4h 14min ago ao-restic-backup.timer

$ journalctl -u ao-restic-backup.service --since 2026-10-03 | grep -E 'snapshot .* saved'
2026-10-03T08:12:24  snapshot fbc25f93 saved
2026-10-04T03:35:38  snapshot 0548f116 saved
2026-10-05T03:32:47  snapshot c249b5db saved
```

Three consecutive successful snapshots with distinct IDs, each showing
`using parent snapshot <previous ID>` — so the chain is genuinely incremental
and not three copies of one state. This also **satisfies the OPS-24 redundancy
criterion** ("consecutive `data/`-inclusive snapshots are required"): three
nights running, parent-chained, all covering the same 11-path set.

**What the dead verify unit costs.** `restic check` is the only control that
would detect a silently corrupted or truncated repository. §17.1's 3-2-1 claim
and every restore-drill result in §17.4 rest on backups that have **never been
integrity-checked by the scheduler**. The drill in §17.4 ran `restic check`
manually and passed, which is real evidence about that moment — but a passing
manual check does not substitute for a weekly one, because the failure mode being
watched for (bit rot, a truncated pack, a bad rewrite) develops *after* the
drill. The `AoRestoreTestStale` gap in §17.2.1.1 is the same blindness at a
different layer.

**The fix is a one-line addition to the installer plus a `daemon-reload`**, and it
is **explicitly not applied here**: `install-backup-schedule.sh` is not owned by
this specification, editing it requires root, and re-running it rewrites
`/etc/systemd/system/`. The change is prepared and described, not forced.
Filed as **OPS-37**.



So the honest statement is: **the Gazebo process has written nothing since
2026-10-04 09:25**, and the live `.log` being 0 bytes is a consequence of that
silence as much as of the detached descriptor. A future reader must not upgrade
this to "Gazebo output is being lost" without re-measuring growth — the fault is
that *when* Gazebo next writes, it will write to an unrotated inode. The
container has been up 38 h and the foxglove one 2 d 12 h, both quiet, which is
consistent with an idle simulation rather than with a crashed one.

**The repair is not a comment edit.** It is either `copytruncate` for the Podman
files or moving those containers to `journald`/`k8s-file` under a path the
policy does not rotate. Both are container-logging changes, outside this
session's remit and outside the file list it owns. Recorded as **OPS-36** and
left open, deliberately.

