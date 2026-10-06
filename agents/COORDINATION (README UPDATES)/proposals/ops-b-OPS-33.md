---
item: OPS-33
action: close
evidence: |
  # 16-case classifier check, all cases now pass
  ok  present=False declared store not present on this host  -> absent
  ok  present=False stat failed: FileNotFoundError           -> absent
  ok  present=True  None                                     -> ok
  ok  present=True  excluded from snapshot by operator decision -> excluded
  ok  present=True  not a SQLite file (bad header)           -> error
  ok  present=True  database disk image is malformed         -> error   # was 'excluded'
  ok  present=True  file is not a database                   -> error   # was 'excluded'
  ok  present=True  database is encrypted                     -> error
  ALL PASS

  # SQL backfill against a throwaway PostgreSQL 18.6, NOT the live Grafana db
  $ initdb -D /tmp/ao-pgtest -U postgres --auth=trust
  PostgreSQL 18.6 (Ubuntu 18.6-0ubuntu0.26.04.1)
  # seeded 6 rows with `status` column dropped, then re-ran the migration
  $ psql -v ON_ERROR_STOP=1 -f config/platform/postgresql/ao-status.sql ; echo rc=$?
  rc=0
  $ SELECT id, status FROM ao_status.sqlite_store ORDER BY id;
       id      |  status
  -------------+----------
   s-absent    | absent
   s-badheader | error
   s-corrupt   | error
   s-excluded  | excluded
   s-notadb    | error
   s-ok        | ok
  (6 rows)

  # idempotent: second run leaves statuses unchanged
  # constraint holds
  $ INSERT INTO ao_status.sqlite_store (id,present,status) VALUES ('bad',true,'banana');
  ERROR: new row ... violates check constraint "sqlite_store_status_check"
section: 16-scripts-and-operational-standards
---
`ao_status.sqlite_store.status` is `CHECK (status IN ('absent','error','excluded','ok'))`,
the view exposes `sqlite_stores_absent`, `sqlite_stores_error` and
`sqlite_stores_excluded` as separate counters, and the collector sets `error` for
anything it could not stat, open or parse. §16.1.3 documents the four states and,
more usefully, records that the classification is **keyword-based over
`read_error` free text** — a known fragility that the next reader should not trust
blindly.

**What I got wrong.** The fault list matched only `failed` / `not a sqlite file` /
`header read failed` / `open failed` / `read failed` / `snapshot failed` /
`integrity`. `sqlite3` reports corruption as `DatabaseError('file is not a
database')` or `'database disk image is malformed'` — sentences containing **none**
of those markers. Measured before the fix:

```
classify_store({'present': True, 'read_error': 'database disk image is malformed'}) -> 'excluded'
classify_store({'present': True, 'read_error': 'file is not a database'})            -> 'excluded'
```

So a **corrupt database was recorded as a deliberate operator decision** — a
fault reported as intent, which means nobody would ever be paged for it. That is
the more dangerous direction of the two: the conflation OPS-33 exists to remove
was still present for the one failure mode that matters most.

The same gap existed *independently* in the SQL backfill in
`config/platform/postgresql/ao-status.sql` — which is the worse half, because
that is the statement that would have poisoned rows already written into a live
database. Both now carry the corruption markers (`malformed`, `not a database`,
`corrupt`, `encrypted`, `unable to open database`), and the SQL is written to
mirror the Python `_STORE_ERRORS`/`_STORE_CORRUPT` so the two cannot silently
disagree. If they ever do, the collector overwrites the value on its next cycle.

I found this by **enumerating the `read_error` strings the collector can actually
emit** (`grep -n read_error`) and testing each against the classifier, rather
than by testing the cases I expected to matter. Reading the classifier alone would
not have surfaced it, because the function is correct in isolation — it is the
*vocabulary* on the other side that was incomplete.

Verification was done against a throwaway PostgreSQL 18.6 on port 55432 with its
own `PGDATA` under `/tmp`, deliberately **not** the live Grafana database, and
the instance was stopped and deleted afterwards (`pg_ctl stop` rc=0, `rm -rf`).
Seeding required `DROP VIEW ao_status.v_system_health` first — the view depends
on the `status` column, so `DROP COLUMN` is refused without it. That is worth
noting for whoever next touches this migration.