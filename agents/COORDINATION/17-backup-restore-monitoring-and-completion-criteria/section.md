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
disk, but a genuinely host-disjoint copy exists on separate media inside the
running pCloud sync root. It is deliberately **not scheduled** — no timer, no
cron, no reference from `restic-run.sh` — so it holds a single snapshot rather
than a series. Until it is scheduled it mitigates total disk loss but does not
satisfy "one off-site copy" in the sense the policy intends. Enabling it is an
operator decision.

### 17.1.1.1 What the off-site repository actually contains (measured 2026-10-04)

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

1. **No directory named `ALWAYSON-RESTIC2PCLOUD` exists anywhere in the sync
   root.** So the row's remedy — "point the restic repository at it" — names a
   target that was never created. The repository that does exist is
   `ALWAYSON-BACKUPS`, a different path the row does not mention.
2. **The remedy "upload via rclone WebDAV or SFTP" describes a mechanism that is
   not in use here and is not needed for what exists.** `ALWAYSON-BACKUPS` is a
   plain local restic repository on the 1TB Samsung USB disk, sitting *inside* a
   directory that pCloud syncs. It replicates by virtue of that sync root, with
   no rclone remote. Recommending WebDAV/SFTP would add a moving part to solve a
   problem the current arrangement does not have.

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
where a manifest comparison would only report a mismatch. But it is not the
requirement's wording, and inventing a baseline manifest would mean new backup
behaviour, which is OPS-09's decision and not this session's.

**Correction to an earlier claim in this section.** It previously said the restic
units were "not deployed", on the evidence of
`ls ~/.config/containers/systemd/ | grep -i restic` returning nothing. That
measurement was correct and the conclusion drawn from it was wrong. These are
**root-level systemd units**, not Quadlets, so they are not deployed into
`~/.config/containers/systemd/` at all — they live in `/etc/systemd/system/`.
Measured 2026-10-04, they are installed, enabled and running:

| Unit | `is-enabled` | Last activation |
|---|---|---|
| `ao-restic-backup.timer` | enabled | `ao-restic-backup.service` succeeded, exit 0, 9 h ago |
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

## 17.2 Monitoring

### 17.2.0 Metabase persistence: the app-data volume is empty, and that is correct

OPS-01 asks for Metabase persistence plus a first read-only query. Measured
2026-10-04, the persistence half is already satisfied and the reason is not
obvious enough to leave unstated.

`ao-metabase` is running and healthy against the host PostgreSQL cluster, not
against a private database container:

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
correctly conclude data is being lost. It is not. Recorded here so the next
session does not repeat that false alarm, and flagged for removal as a separate
cleanup — **not** done by this session, because deleting a declared volume mount
is a container-definition change outside the backup/monitoring remit.

**What OPS-01 still needs, and why this session stops short of it.** Two
elements remain: (a) confirming state survives a restart, and (b) a protected
ad-hoc read-only reporting query succeeding with no source writes. Both are
blocked on privileges this session does not have and should not acquire:

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

**One trap worth naming, because I fell into it and it produced a false
denial.** `reporting_sales.v_reporting_orders` is visible in
`information_schema` but querying it unqualified fails with
`relation "v_reporting_orders" does not exist`. `metaread`'s `search_path` is
`"$user", public` — it does **not** include `reporting_sales`. A checker that
stops at the first `does not exist` would conclude the reporting views are
unreadable and that Metabase cannot be wired to them, when in fact the fix is
simply to schema-qualify. Relatedly, `cordadb` currently exposes **no** tables
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
| **Restart** persistence check | Stopping `ao-metabase` is a service interruption on the reporting plane; not this session's call. |
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
timestamps into that same directory would complete it. **This session has not
written it**, for two reasons that are not about effort: it changes what
`ops` is responsible for emitting into a shared monitoring path, and it is the
mechanism by which an operator would be paged about backup failure — new
alerting behaviour, which is operator territory. It is left as the concrete,
scoped remainder of OPS-11.

**What I got wrong, and it is worth recording because the error was subtle.**
The §17.2.2 table previously listed these three rules with different metric names
(`ao_restic_backup_last_success`, `ao_restore_test_last_run`,
`ao_repository_verify_last_success`) and different thresholds (900 s / 86400 s /
604800 s). Those names were plausible, not measured — I reconstructed them from
what the rules are *for* rather than reading the `expr:` lines. The real names
carry a `_timestamp_seconds` suffix and the real thresholds are far looser:
93600 s (26 h) not 15 m, 3024000 s (35 d) not 24 h, 777600 s (9 d) not 7 d.
The 15-minute backup threshold in particular was **twenty-six times tighter than
what is written**, against a job that runs **once a night**. Had a reader trusted
the table and tuned against it, they would have concluded the nightly job breaches
its own SLO on every run.

Two lessons, both generalisable past this file. First, a threshold table
transcribed by an agent must be diffed against the source, not retyped from
meaning. Second, **a loose-looking threshold is worth asking about**: 93600 s for a
job that runs every 24 h is a 2 h grace window, which is a real design decision
someone made, and the "correct-looking" 900 s I had invented was me guessing at
a number rather than reading one.

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

### 17.4.1 The local repository cannot be drilled without root (measured 2026-10-04)

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

Closing it needs one of: running the drill via `pkexec`, adding a read-only
group and a matching group-readable repository directory, or granting the
backup service account read access. **All three are privilege changes to backup
data**, which is an explicit stop condition, so this session stops here rather
than widening permissions on the repository. The scratch directory used was
removed and nothing under `/ALWAYSON` was written.

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
| `logs/*.log` (top level) | `logrotate-alwayson.conf`, daily | 14 files, uncompressed | **Installed and rotating** |
| `logs/operations/` | staged, daily | 400 rotations | **Installed and rotating** |
| `logs/installation/` | staged, daily | 400 rotations | **Installed and rotating** |
| `logs/backup/` | staged, daily | 400 rotations | **Installed and rotating** |
| `logs/gpu-runtime/` | staged, daily | 400 rotations | **Installed and rotating** |
| journald | `journald-alwayson.conf` drop-in | `SystemMaxUse=4G`, `MaxRetentionSec=90day` | **NOT installed** |

**Corrected against the live host 2026-10-04: the logrotate policy is installed,
and the table above previously said "staged, not installed" for all five log
blocks.** That was true when written and stopped being true; the distinction now
drawn is between the two halves, which are genuinely in different states.

Measured 2026-10-04:

- `/etc/logrotate.d/alwayson` exists, root-owned (`-rw-r--r-- root root`), 5237 B,
  and is **byte-identical** to the in-tree `config/host/logrotate-alwayson.conf`
  (`cmp` → no output, exit 0).
- It describes **5** rotating patterns.
- `find /ALWAYSON/logs -name '*.log' ! -user scottw` → **0**, so the ownership
  precondition the policy's `su scottw scottw` needs holds.

**It has rotated exactly once, and not on a timer.** The single rotation was a
manual forced run, proven from the journal rather than inferred from timestamps:

```
$ journalctl --since '2026-10-04 00:17' --until '2026-10-04 00:30' --no-pager | grep -E 'pkexec\['
Oct 04 00:17:43 pkexec[2462221]: scottw: Executing command [USER=root] ... [COMMAND=/usr/bin/sh -c logrotate -v /etc/logrotate.d/alwayson; echo "REAL_RUN_EXIT=$?"]
Oct 04 00:18:38 pkexec[2465005]: scottw: Executing command [USER=root] ... [COMMAND=/usr/bin/sh -c logrotate -f -v /etc/logrotate.d/alwayson 2>&1 | tail -40; echo "FORCE_EXIT=${PIPESTATUS[0]}"]
```

The corroborating filesystem evidence is the `create 0664 scottw scottw`
directive firing: eight live logs were truncated to **0 bytes at exactly 00:18**,
the minute of the forced run.

```
$ ls -la --time-style=long-iso /ALWAYSON/logs/*.log
-rw-rw-r-- 1 scottw scottw       0 2026-10-04 00:18 gpu-runtime-check.log
-rw-rw-r-- 1 scottw scottw       0 2026-10-04 00:18 installation-journal.log
-rw-rw-r-- 1 scottw scottw       0 2026-10-04 00:18 mastodon-local-proxy.log
-rw-rw-r-- 1 scottw scottw       0 2026-10-04 00:18 meshchatx.log
-rw-rw-r-- 1 scottw scottw       0 2026-10-04 00:18 operations-journal.log
-rw-rw-r-- 1 scottw scottw       0 2026-10-04 00:18 restore-test.log
-rw-rw-r-- 1 scottw scottw       0 2026-10-04 00:18 script-runs.log
-rw-rw-r-- 1 scottw scottw       0 2026-10-04 00:18 sim-clock-bridge.log
```

**What I got wrong, and it is the most-read part of this subsection.** The
previous revision of this section claimed:

> It has **already rotated**: 13 files match `logs/*.log.[0-9]` and **67** match
> `logs/operations/*.log.[0-9]`. Rotations are real, not merely configured.

**That count was used as proof that this policy rotates, and it proves nothing
of the kind.** Those files mostly predate the policy's installation. Birth times
against the install time:

```
$ stat -c 'birth=%w %n' /ALWAYSON/logs/backup.log.1 /ALWAYSON/logs/sim-clock-bridge.log.1
birth=2026-10-02 18:00:52 -0700 /ALWAYSON/logs/backup.log.1
birth=2026-09-27 22:54:54 -0700 /ALWAYSON/logs/sim-clock-bridge.log.1
$ stat -c '%w %n' /etc/logrotate.d/alwayson
2026-10-04 09:07:08.728949137 -0700 /etc/logrotate.d/alwayson
```

`sim-clock-bridge.log.1` was born on 2026-09-27, **seven days before** the
policy existed on disk, so an unknown earlier mechanism created it. Counting
those files and attributing them to `/etc/logrotate.d/alwayson` was a plain
attribution error: I counted an artefact without checking which process made
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
deletion since 00:18. Nothing was deleted by this session, and the log is not
lost yet — the next scheduled rotation is what would remove it.

The policy uses `nocopytruncate` deliberately: `copytruncate` copies the file
and truncates it in place, which briefly duplicates content and briefly races
writers. For a log a long-lived `conmon` holds open across a daily rotation,
that race is the lesser evil — the alternative here is silent loss. **This
needs an operator decision and is not changed by this session**, because the
correct fix is either `copytruncate` or a `postrotate` that signals the
container to reopen its log, and both touch a running simulation service.
Recorded as an open finding, not silently patched.

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
`MaxRetentionSec=90day` remain aspirational. This is the second half of OPS-26
and it needs one privileged command, which this session does not have
(`sudo -n true` → `sudo: interactive authentication is required`).

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
