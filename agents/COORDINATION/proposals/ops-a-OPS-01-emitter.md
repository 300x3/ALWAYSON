---
item: OPS-01
action: update
evidence: |
  # The Metabase persistence half of OPS-01 is ALREADY SATISFIED, and the reason
  # is counter-intuitive enough to record: the app-data volume is empty.

  $ podman inspect ao-metabase --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'
  /home/scottw/.local/share/containers/storage/volumes/ao-metabase-postgres-data/_data -> /metabase-postgres-data
  /var/run/postgresql -> /var/run/postgresql

  $ podman inspect ao-metabase --format '{{range .Config.Env}}{{println .}}{{end}}' | sed -E 's/(PASS|SECRET|KEY|TOKEN)=.*/\1=<redacted>/I'
  MB_DB_HOST=10.42.0.1
  MB_DB_USER=metabase_app
  MB_DB_DBNAME=metabase
  MB_DB_TYPE=postgres
  MB_DB_SSL=false

  $ podman volume inspect ao-metabase-postgres-data --format '{{.Mountpoint}}{{"\n"}}CreatedAt: {{.CreatedAt}}'
  /home/scottw/.local/share/containers/storage/volumes/ao-metabase-postgres-data/_data
  CreatedAt: 2026-09-24 20:40:06 -0700

  $ du -sh /home/scottw/.local/share/containers/storage/volumes/ao-metabase-postgres-data/_data
  4.0K    .../ao-metabase-postgres-data/_data
  $ ls -la /home/scottw/.local/share/containers/storage/volumes/ao-metabase-postgres-data/_data
  total 8
  drwxr-xr-x 2 scottw scottw 4096 Sep 24 20:40 .
  drwx------ 3 scottw scottw 4096 Sep 24 20:40 ..

  $ curl -s localhost:3002/api/health
  {"status":"ok"}

  # It moved off embedded H2 on 2026-09-25:
  $ tail -n 2 /ALWAYSON/logs/operations/metabase-h2-migrate-final.log.1
  2026-09-25 03:45:40,747 INFO liquibase.changelog :: Columns json_unfolding(boolean) added to metabase_field
  2026-09-25 03:45:40,751 INFO liquibase.changelog :: ChangeSet migrations/001_update_migrations.yaml::v47.00-002::calherries ran successfully
  # after an earlier attempt failed:
  # ERROR Set up h2 source database and run migrations...: Unable to connect to Metabase h2 DB.

  # The read-only half is BLOCKED on privileges. All three routes refused:
  $ runuser -u postgres -- psql -tAc "SELECT datname FROM pg_database"
  runuser: may not be used by non-root users
  $ sudo -n -u postgres psql -tAc 'select 1'
  sudo: interactive authentication is required
  $ psql -h /var/run/postgresql -tAc "select current_user"
  psql: error: ... FATAL:  role "scottw" does not exist
section: 17-backup-restore-monitoring-and-completion-criteria
---
Adds **§17.2.0**, recording that the persistence half of OPS-01 is already met
and — more usefully — that `ao-metabase-postgres-data` is a **vestigial, never-written
volume**. It is 4 KB, empty, and has been since it was created on 2026-09-24.

That is correct, not a fault. `MB_DB_HOST=10.42.0.1` points Metabase at the host
PostgreSQL cluster via the `metabase_app` role created by
`scripts/ops/provision-reporting-postgres.sh`, so saved questions, dashboards
and subscriptions live in the `metabase` database on the host. The deployment
migrated off embedded H2 on 2026-09-25 (liquibase `v47.00-002` is the last H2
migration in `metabase-h2-migrate-final.log.1`).

The reason this is worth writing down: **the mount is declared in both the
repository Quadlet and the deployed copy, and an agent auditing persistence by
volume size would correctly conclude that Metabase is losing all its state.** It
is not. Flagged for removal as separate cleanup — deliberately **not** done here,
because removing a declared volume mount is a container-definition change outside
the backup/monitoring remit.

**OPS-01 stays OPEN, blocked, on the read-only half.** Creating the per-source
read-only roles means running `config/platform/postgresql/metaread-grants.sql` as
the PostgreSQL superuser with a bound password, and all three escalation routes
are refused to this session (evidence above). Running the verification query also
requires a `metaread` password from KDE Wallet and a Metabase session — inside the
"secrets and credentials" stop condition. Neither step is guessed at or marked
done. The remaining work for whoever picks this up: create `metaread`, restart
`ao-metabase`, confirm state survives, then run one ad-hoc `SELECT` and confirm
zero source writes.

What I got worth recording: I opened this item expecting the empty volume to be
the bug, because "container app-data volume is empty" is a familiar failure shape
and I had a plausible story ready for it — H2 never migrated. The migration logs
show the opposite migration direction (H2 **out**, PostgreSQL **in**, on
2026-09-25) and the env vars settle it. Checking the direction of a migration
before theorising about it cost one command; assuming it would have cost a
false finding filed as fact.