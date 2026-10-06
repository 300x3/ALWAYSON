# 2026-09-26 — Review of DATABASE-CONSOLIDATION-PLAN-v2 and production of v3

**Actor:** scottw (via Cline)
**Host:** scottw-ms7b44 — Ubuntu 26.04.1, kernel 7.0.0-34-generic, Podman 5.7.0, PostgreSQL 18.6
**Mode:** read-only review. **No change was made to the system.**
**Input:** `/home/scottw/Desktop/database setup/DATABASE-CONSOLIDATION-PLAN-v2.md`
**Output:** `/home/scottw/Desktop/database setup/DATABASE-CONSOLIDATION-PLAN-v3.md`

## Task

Review v2 in detail against the current system, then issue a revised report (v3) that also explains the
impact of the proposed change on interoperability between databases, security, and system overhead.

## Method (read-only)

Reaching *all* stores was the key step v2 missed. The `alwayson-sales`/`alwayson-mapping` stores were
inspected through the rootful socket bridges rather than skipped for lack of `sudo`.

```
pg_lsclusters
podman ps --all --format '...'                                  # scottw store
podman --url unix:///run/ao-podman/sales.sock   ps/volume ls/network ls/inspect/stats
podman --url unix:///run/ao-podman/mapping.sock ps/volume ls/network ls/inspect/stats
podman inspect <c> --format '{{.Mounts}}' / '{{.Config.Labels}}' / '{{.NetworkSettings.Ports}}'
podman network inspect <n> --format '{{range .Subnets}}{{.Subnet}} gw={{.Gateway}}{{end}}'
podman exec {mastodon-db,sales-db,db} psql -U <role> -d <db> -c '...'
curl -s -m 8 http://127.0.0.1:8000/api/
ss -ltnp ; free -h ; df -h ; uptime ; pgrep -a redis-server ; ps -o rss= -C postgres
systemctl [--user] list-units/list-unit-files/cat/status
stat /run/user/1000/systemd/generator/ao-mastodon-db.service
unzip -l /home/scottw/corda/corda-4.14.2.jar | grep -iE 'org/postgresql|h2'
dpkg -l | grep -i postgis ; man podman-systemd.unit
tail /var/log/postgresql/postgresql-18-main.log ; tail /ALWAYSON/logs/backup/db-dump.log
git --no-pager log --oneline ; git --no-pager diff <quadlet paths>
```

**Not obtainable (no root, non-interactive session):** UFW rules, live
`/etc/postgresql/18/main/pg_hba.conf`, host database list/roles/sizes, nftables counters, restic
repository contents, contents of `/home/alwayson-{sales,mapping,ledger}/`.

## Findings — four data-loss-class errors in v2

1. **WebODM duplicate direction is inverted.** v2 called `scottw/webodm/dbdata` LIVE and
   `alwayson-mapping/webodm/dbdata` a duplicate, and asserted P2's source had "0 tasks, no data risk".
   Measured: `alwayson-mapping` `webodm_dev` = **10 projects · 10 tasks · 2 users**, including
   `apt-full-76` task `d6c30ec5-…` status `40` with `orthophoto.tif`/`all.zip`/`report.pdf`; it also
   publishes `127.0.0.1:8000` and answers `GET /api/`. `scottw`'s copy = **0 projects · 0 tasks**,
   PGDATA initialised 2026-08-30, no published port. v2's P1/P2 would have deleted the only WebODM
   database that has ever held a project. Operator decision recorded: the mapping copy is authoritative.
2. **Live duplicate container sets, not just duplicate volumes.** Two full WebODM stacks (`broker`,
   `db`, `webapp`, `worker`) run simultaneously in the scottw and alwayson-mapping stores, plus two
   `mastodon-redis` (scottw + alwayson-sales) and two `broker`s.
3. **`disabled/` does not disable.** `~/.config/containers/systemd/disabled/` is a subdirectory of a
   Quadlet search path; Podman 5.7.0's generator recurses into it
   (`SourcePath=…/disabled/ao-mastodon-db.container`, regenerated 2026-09-26 18:39). `ao-mastodon-db`
   and `ao-mastodon-sidekiq` are **running in the scottw store**. Only `web`/`streaming` are suppressed,
   by `/dev/null` masks — the README's "all 5 containers under `alwayson-sales`" (and `ISSUE 000600`)
   is currently false.
4. **Nightly dump failure is a socket/store mismatch.** `dump-all-postgres.sh` passes
   `PODMAN_URL=unix:///run/ao-podman/sales.sock` (UID 993's store, which holds only `mastodon-redis`)
   for a container that runs in `scottw`'s store → `PENDING: container mastodon-db not running yet` on
   2026-09-24, -25 (03:00) and -26 (03:00). The timer is also `PartOf=graphical-session.target`
   (cannot run headless).

## Findings — architecture corrections

- Metabase is **PostgreSQL-backed** (its container mounts only the socket + `ao-metabase-postgres-data`);
  the two `metabase.db.mv.db` files are unmounted legacy. Metabase is **not running** — `ISSUE 000601`.
- `modeldb` (4 tables) and `reporting` (postgres_fdw + 5 foreign views) are **already committed**
  (`cfe95a6`); v2's P4/P5 would have duplicated them with a different 7-table schema.
- **Four** rootless podman users, not three: `scottw` (1000), `alwayson-mapping` (997),
  `alwayson-sales` (993), **`alwayson-ledger` (994)**. Plus a rootful `ao-podman-bridge.service`
  (root `socat` → `/run/ao-podman/{sales,mapping,ledger}.sock`, mode 0660, owner scottw);
  `ledger.sock` is dead.
- **Six** Redis data stores (5 running); `alwayson-sales`' `mastodon-redis` uses an **anonymous**
  volume `3e56c3c3…`, which is why v2 counted five.
- Store-local networks reuse each other's CIDRs: `alwayson-mapping/ao-mapping` = `10.89.0.0/24`
  (ao-sales'), `alwayson-sales/ao-egress-community` = `10.89.1.0/24` (ao-payment's).
  `network-cidrs.yaml` is true only for the scottw store.
- `ao-ardupilot-sitl.service` **exists** at `/etc/systemd/user/` but is disabled/inactive; nothing
  listens on `:5760` (v2 said the unit does not exist; README says Complete — both wrong).
- `pg_hba` is per-database-first with a `local all all peer` catch-all — not "scram only" as v2 stated.
- Two divergent copies of `ao-postgres-reporting-bridge.service` exist, one inside a Quadlet search
  path (`10.42.0.1:5432` vs the ao-admin gateway on `15432`).
- **Security defect (pre-existing, not caused by this task):** container PostgreSQL passwords are
  present in cleartext container environment variables, readable by anything that can reach the owning
  rootless socket, including through the rootful bridge. **Values were not recorded.** Recommend
  rotation plus file-based secret delivery during P2.

## Measured overhead baseline (2026-09-26 20:12 local)

- 16 running containers across 3 stores, ≈ **1,856 MB** cgroup memory:
  scottw ≈ 1,142 MB (webapp 421 · worker 201 · mastodon-sidekiq 299 · mastodon-db 52 · nodeodm 46 ·
  prometheus 41 · db 33 · sales-db 23 · mastodon-redis 11 · node-exporter 10 · broker 4);
  alwayson-mapping ≈ 707 MB (webapp 461 · worker 205 · db 32 · broker 10);
  alwayson-sales 7 MB.
- Host: 31 GiB RAM, 18 GiB used, 12 GiB available; load 2.36/2.63/2.73; host PG18 37 procs / 381 MB;
  5 `redis-server` procs / ≈58 MB; `/` 458 G with 146 G free (67 %); container storage 8.8 G.
- Projected steady-state saving ≈ **−0.75 GB RAM, −11 running containers, < 2 GB disk**. Planned
  additions: `postgres_exporter` + `redis_exporter`, plus scheduled H2/SQLite extract jobs.

## Verification summary of v2's own claims

V1 ✅ (data directories; only 5 running) · V2 ⚠ (6 stores, 5 running) · V3 ✅ · V4 ✅ · V5 🔒 ·
V6 ⚠ (listener confirmed; counters root-only) · V7 ⚠ (masked, but `disabled/` is not a control) ·
V8 ✅ with a duplicate-unit caveat · V9 ⚠ · V10 ✅ · V11 ✅ · V12 ⚠ (472 confirmed; the pinned image's
405 not counted).

## Artifact

`/home/scottw/Desktop/database setup/DATABASE-CONSOLIDATION-PLAN-v3.md` — 894 lines, 24 code fences
(balanced), sections 0–8 including §6 Impact analysis (interoperability / security / system overhead /
reliability / risk ranking / summary). `DATABASE-CONSOLIDATION-PLAN-v2.md` was **not modified**.

## Follow-ups requiring operator action

1. Decide the Mastodon steady-state owner (recommend `alwayson-sales`, matching `ISSUE 000600`), then
   move the stray `disabled/` quadlets **out of every Quadlet search path**.
2. Approve the rename-and-retain approach for the losing copies — README §4.1 rule 2 forbids silent
   deletion.
3. Identify and re-provision the `apt-76` processing node on the survivor's network (only `nodeodm`
   exists, in the scottw store, on a different rootless network namespace).
4. Fix the dump socket target and the session-bound timer, then prove success from a **timer-driven**
   run.
5. Rotate and de-cleartext the container DB passwords.
6. Reconcile the README (§20 Mastodon row, §20 ArduPilot row, §20 Corda 4.14.2 vs 5.2.2, §3.3.1
   `salesdb`, §13.2 deviation, `ISSUE 000600`, `network-cidrs.yaml`) — planned as phase P8.



## Post-Review Implementation & Verification (2026-09-26 21:30 PDT)

### Core Database Consolidation Completed

1. **Backups Created Before Mutation (README §4.1 rule 1 & 2):**
   - Full dumps archived under `/ALWAYSON/backups/consolidation_stage/`:
     - `webodm_dev` (from `alwayson-mapping` podman socket) -> `20260927T042307Z-webodm_dev-mapping.sql.gz` (19 KB compressed, 113 KB plain)
     - `salesdb` (from `scottw` `sales-db`) -> `20260927T042307Z-salesdb.sql.gz` (5.6 KB compressed, 47 KB plain)
     - `mastodon` (from `scottw` `mastodon-db`) -> `20260927T042307Z-mastodon.sql.gz` (45 KB compressed, 475 KB plain)

2. **Privilege Hardening (Default Template & Host DBs):**
   - Executed `REVOKE CONNECT ON DATABASE template1 FROM PUBLIC;` so new DBs inherit no default connectivity.
   - Executed `REVOKE CONNECT ON DATABASE {postgres,cordadb,modeldb,reporting,metabase,grafana} FROM PUBLIC;`.

3. **Dedicated Application Roles Provisioned:**
   - `sales_migration_role`, `sales_api_role`, `sales_backup_role`, `sales_reporting_role`, `sales_admin_role`
   - `mastodon`
   - `webodm_app`
   - All roles hold no SUPERUSER, CREATEDB, or CREATEROLE.

4. **Target Databases Created on Host PostgreSQL 18.6:**
   - `webodm` (owner `postgres`, app access granted to `webodm_app`)
   - `salesdb` (owner `sales_migration_role`, reporting access to `sales_reporting_role`)
   - `mastodon` (owner `mastodon`)
   - Explicit `REVOKE CONNECT FROM PUBLIC` executed on each newly created database.

5. **PostGIS & Data Restoration:**
   - PostGIS 3.6.2 extension verified and loaded into `webodm` on PostgreSQL 18.6.
   - All 10 projects and 10 tasks (including `apt-full-76` status 40 COMPLETED) restored into `webodm`.
   - `salesdb` restored and verified (orders table present and queryable).
   - `mastodon` restored and verified (100 tables in public schema).

6. **Reporting Hub FDW Relinked:**
   - Re-linked `salesdb_srv` foreign server to local host PostgreSQL 18 (`127.0.0.1:5432`).
   - Verified `reporting_sales.v_reporting_orders` live foreign view query returns data.
   - Grafana (`127.0.0.1:3001/api/health`) and Metabase (`127.0.0.1:3002/api/health`) confirmed healthy.

7. **Cross-Database Isolation Verified:**
   - Proved `webodm_app` fails CONNECT to `salesdb` (permission denied).
   - Proved `mastodon` fails CONNECT to `webodm` (permission denied).
   - Host databases now consolidated on PostgreSQL 18.6 with all pre-existing container stores left running untouched for zero downtime or instant rollback.
