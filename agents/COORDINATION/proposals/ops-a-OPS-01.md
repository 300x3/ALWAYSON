---
item: OPS-01
action: update
evidence: |
  # HALF 1 — the Metabase application database exists and is in use.
  # (names only, no credential values)
  $ podman logs ao-metabase | grep -i 'application database'
  2026-10-01 22:22:54 INFO db.setup :: Successfully verified PostgreSQL 18.6
      (Ubuntu 18.6-0ubuntu0.26.04.1) application database connection.
  2026-10-01 22:22:56 INFO db.setup :: Database Migrations Current ...
  $ podman exec ao-metabase sh -c 'env | sed "s/=.*/=<redacted>/"' | grep MB_DB
  MB_DB_DBNAME  MB_DB_HOST  MB_DB_PASS  MB_DB_PORT
  MB_DB_SSL  MB_DB_TYPE  MB_DB_USER          # all values redacted
  $ podman inspect ao-metabase --format '{{range .Mounts}}…'
  /metabase-postgres-data <- …/volumes/ao-metabase-postgres-data/_data
  # a named volume, so state survives restart

  # HALF 2 — the per-source read-only reporting role does NOT exist.
  $ podman exec ao-sales-db psql -U sales_migration_role -d salesdb -tAc \
      "select rolname from pg_roles where rolname in ('metaread','sales_reporting_role')"
  sales_reporting_role            # metaread is absent
  $ podman exec ao-sales-db psql -U sales_migration_role -d salesdb -tAc \
      "select nspname from pg_namespace where nspname='reporting_sales'"
  (no output)                     # the schema is absent too

  # the read-only SQL exists in-tree but its wrapper points at a stale path:
  $ grep -n GRANT config/platform/postgresql/reporting-hub.sql | head -3
  47:GRANT USAGE ON SCHEMA reporting_sales TO metaread;
  48:GRANT SELECT ON ALL TABLES IN SCHEMA reporting_sales TO metaread;
  $ ls /tmp/reporting-hub.sql
  No such file or directory       # but the script reads it from there
  $ find . -name reporting-hub.sql -not -path './.git/*'
  ./config/platform/postgresql/reporting-hub.sql
section: 17-backup-restore-monitoring-and-completion-criteria
---
**Half done, and I stopped at the half that needs credentials.** No §17 edit;
this records measured state so the compiler can correct the OPS-01 row.

**Half 1 — the application database exists and is in use.** Measured, not
assumed: `ao-metabase` logs `Successfully verified PostgreSQL 18.6 … application
database connection` and `Database Migrations Current`, and its app data is on
the named volume `ao-metabase-postgres-data`, so state survives restart.
`MB_DB_DBNAME/HOST/USER/PASS/…` are set in the container. **No secret value was
printed** — names only, values redacted.

I nearly filed the opposite conclusion. `podman logs ao-metabase` is full of
`h2 Database 1 'Sample Database'` lines, which reads like Metabase running on
an embedded H2 file with no PostgreSQL at all — and H2 would fail the
persistence requirement outright. It is not: the h2 lines are Metabase's
bundled *sample dataset* being synced as a source, not its application store.
The application store is the PostgreSQL 18.6 line above. Lesson: a log grep
that matches the wrong subsystem produces a confident false alarm.

**Half 2 — the per-source read-only reporting role does not exist, and creating
it is a stop condition I did not cross.** Measured: `metaread` is absent and
the `reporting_sales` schema it would read from is absent too.
`scripts/ops/provision-sales-reporting.sh` is supposed to provision this and is
**broken in two ways, both found by reading it rather than running it**:

1. `install -m 0600 /tmp/reporting-hub.sql /tmp/reporting-hub.sql` — identical
   source and destination, so it is a no-op that appears to "install" the file.
2. The SQL it feeds to `psql` lives at
   `config/platform/postgresql/reporting-hub.sql` in the repo, not at
   `/tmp/reporting-hub.sql`. Measured: `/tmp/reporting-hub.sql` → *No such file
   or directory*. So the script's final `psql -f` would fail even if the file
   were staged there by hand.

The wrapper also provisions `sales_reporting_role`, which is a **different**
role from the read-only `metaread` that OPS-01 asks for, and it never grants
`SELECT`. Read-only reporting is therefore not delivered on this path.

**Why I stopped rather than fixed it.** Provisioning the role means reading a
credential from KDE Wallet, creating a login role, and granting it access to
reporting data — credentials and database privileges, both explicit stop
conditions in my brief. The two script defects are safe to fix in themselves
(stale path, no-op `install`), but fixing them without the operator's approval
would leave a script that *looks* runnable for a privilege change nobody
approved, which is worse than leaving it visibly broken.

**Operator decision required:** approve provisioning the `metaread` read-only
role (one per source, `CONNECT` + `USAGE` + `SELECT` only, no write, DDL or
owner) and confirm whether `sales_reporting_role` should be replaced by it or
kept as a separate write-capable role. The SQL already exists in-tree and
grants exactly the right privileges.

**Also belongs to another group, reported not touched:** the sales domain owns
`provision-sales-reporting.sh` and the `sales_reporting_role` grant. Fixing its
broken paths is arguably a PAY/SALES item, not an OPS one. I did not renumber
or edit anything outside §17.

Files changed: none for this item (measurement only).