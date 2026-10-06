---
item: OPS-08
action: close
evidence: |
  # §17.1.3 gained the two steps its acceptance criteria name ("preflight and
  # snapshot selection") and which it did not previously have. Verified by
  # reading back the section, not by intent:
  $ grep -c 'Preflight' agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md
  1
  $ grep -c 'Select the snapshot explicitly' agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md
  1

  # the (label -> database, user) table the restore runbook now transcribes.
  # My first draft DERIVED the database name from the dump filename; that is
  # wrong, because 'sales' is the directory and 'salesdb' is the database.
  $ sed -n '11,17p' /ALWAYSON/scripts/backup/backup-host-postgres.sh
  metabase:metabase:metabase_app)      folder=ao-admin;    pass_key=metabase-db-password ;;
  grafana:grafana:grafana_app)         folder=ao-admin;    pass_key=grafana-db-password ;;
  sales:salesdb:sales_migration_role)  folder=ao-sales;    pass_key=sales-db-password ;;
  mastodon:mastodon:mastodon)          folder=ao-mastodon; pass_key=mastodon-db-password ;;
  webodm:webodm:webodm_app)            folder=ao-mapping;  pass_key=webodm-postgres-password ;;
  *) echo "refusing unexpected host PostgreSQL backup target" >&2; exit 2 ;;
  $ ls /ALWAYSON/backups/postgres/
  grafana  mapping  mastodon  metabase  sales  webodm

  # format claim verified, so 'pg_restore' is not carried in the runbook:
  $ sed -n '22p' /ALWAYSON/scripts/backup/backup-host-postgres.sh
  if pg_dump --host=127.0.0.1 --port=5432 --username="$user" --dbname="$db" \
      --no-owner --no-privileges | gzip -9 >"$out.tmp"; then
  # -> plain SQL, no -Fc, so psql reads the stream.

  # pg_isready proves liveness, NOT access. My first preflight draft treated it
  # as sufficient; on this host an unauthenticated superuser connection fails:
  $ pg_isready -h 127.0.0.1
  127.0.0.1:5432 - accepting connections
  $ psql -h 127.0.0.1 -U postgres -tAc 'select rolname from pg_roles'
  Password for user postgres:
  psql: error: connection to server at "127.0.0.1", port 5432 failed:
          fe_sendauth: no password supplied

  # the RESTIC_REPOSITORY ordering trap, reproduced:
  $ export RESTIC_REPOSITORY=/media/scottw/…/ALWAYSON-BACKUPS
  $ set -a; . /tmp/ao-e.sh; set +a     # fetch-restic-env.sh also sets it
  $ restic stats
  Stat(<config/>) failed: stat /var/backups/alwayson-restic/config: permission denied
  $ export RESTIC_REPOSITORY=/media/scottw/…/ALWAYSON-BACKUPS   # AFTER sourcing
  $ restic snapshots
  ID        Time                 Host           Tags                    Paths
  56bf1af5  2026-10-03 08:59:59  scottw-ms7b44  alwayson-offsite-proof  /ALWAYSON/artifacts
                                                                         /ALWAYSON/config
  1 snapshots

  # RPO is measured; RTO is a target. The two OnCalendar values were read:
  $ systemctl cat ao-restic-backup.timer | grep OnCalendar
  OnCalendar=*-*-* 03:30:00
  $ systemctl cat ao-restic-verify.timer | grep OnCalendar
  OnCalendar=Sun *-*-* 04:30:00
  # both Persistent=true -> worst case is 48h after a FAILED run, not 24h.

  # no restore test is scheduled at all, which is what keeps every RTO untested:
  $ systemctl list-timers --all --no-pager | grep -iE 'restore'
  $ systemctl --user list-timers --all --no-pager | grep -iE 'restore'
        (no output in either scope)
section: 17-backup-restore-monitoring-and-completion-criteria
---
Second OPS-08 proposal. §17.1.3 was rewritten from a six-line prose list into an
executable runbook, because the acceptance criteria name **preflight** and
**snapshot selection** and the previous text had neither. It now carries a
numbered step 0 through step 7, each with runnable commands.

**Two errors I introduced and then caught in the same edit cycle — both are the
kind of thing that survives into a runbook and gets used during an incident.**
First draft derived the database name from the dump filename
(`sed 's/^[0-9T]*Z-//'`). That is wrong: the sales database is `salesdb` under
the directory `sales`, so the runbook would have pointed `psql` at a database
that does not exist. The fix reads the (label, database, user) mapping from the
guard table at the top of `backup-host-postgres.sh`, which is the single source
of truth, and treats an unrecognised label as a **stop** rather than a default —
mirroring the backup script's own `*)` guard. Second, the preflight treated
`pg_isready` succeeding as proof the cluster was usable; it is not, and an
unauthenticated `psql` fails `fe_sendauth`. Reachability and access are now
separate checks.

I also removed `pg_restore` from the runbook. The dumps are plain SQL (no `-Fc`),
so `psql` reads the stream; carrying `pg_restore` would have been a plausible-
sounding wrong instruction.

**The RPO/RTO table is now labelled honestly, which is a correction rather than
an addition.** The prior text stated RTOs of 1 h / 2 h / 4 h in the same voice as
the RPOs. Only the RPOs are measured. Two measured facts bound them: both timers
are `Persistent=true`, so after a *failed* run the worst case is **48 h**, not
24 h; and **no restore timer exists in either systemd scope**, so every RTO in
that table is an untested intention. A class with a 1 h RTO and a measured
filesystem restore of seconds has not thereby been shown to recover in 1 h —
redeploy, credential re-provisioning and verification are all untimed.

**`logs/` is still absent from the restic path set**, so a restore to a new host
comes back with no operational history. That is a one-line change to an
approved path list and enlarges what the nightly job copies, so it stays an
operator decision (unrelated to this proposal, recorded for the next session).

Files changed: `agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md` (§17.1.2 RPO/RTO
labelling, §17.1.3 rewrite).