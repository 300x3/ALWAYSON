# N. Grafana read PostgreSQL only; the ALWAYSON_STATIC panels were empty and the Prometheus datasource was a defect

**From:** Cline (C.BOT) · **Date:** 2026-10-02 (local) / 2026-10-03T15:05Z
**Scope:** Grafana only. Prometheus NOT in scope and NOT touched.
**State:** NOT committed (no commit requested). Nothing OPEN that blocks other sessions.

**Journal:** `/ALWAYSON/logs/operations/grafana-system-health-dashboard-2026-10-02.log`

---

**Supersedes:** revision 2 (2026-10-03 08:40 PDT) — extends SQLite coverage to
all 14 README-declared stores including browser profiles; records two faults
found and fixed during that extension. Revision 1 covered only 5 stores.

## Read this first

The SQLite store list in `collect-system-health.py` is **14 declared stores,
not 5**. Revision 1 of this document was incomplete on that point. If you are
reading an earlier copy or a stale note claiming "5 SQLite stores", it is wrong.

Two faults caught during the extension, both worth not repeating:

1. **A locked SQLite store silently voided its own metrics.** With Chrome
   running, `sqlite3.connect(timeout=5)` raised, the handler set `read_error`
   and threw away metrics already collected for that store. The dashboard then
   showed a *present* store with no counts, which reads as "healthy, nothing to
   report" rather than as a fault. Fixed: `timeout=15`, a retry, and per-metric
   fault isolation so one locked table cannot blank a store's other counts.
   **If you add a store, keep the per-metric isolation.**
2. **The Grafana admin user is `ao-admin`, not `admin`.** Any script you write
   against `/api/ds/query` will 401 with `admin`. This cost me a false
   "credentials are broken" conclusion.

1. **Grafana's ONLY datasource is now PostgreSQL.** Measured:
   `select uid,name,type,is_default from data_source` → exactly one row,
   `ao-status | postgres | true`. `provisioning/datasources/prometheus.yml` is
   **deleted** and `Requires=ao-prometheus.service` is removed from
   `quadlet/operations/ao-grafana.container`. If you find a doc claiming
   otherwise, it is wrong — I corrected the six lines I found (§3.3 L335,
   §5.3 L903, §11 tree, §17.2, §19.1 ST-19 L4250, §20).
2. **The previous dashboard was 10/10 dead and it was not obvious.** All stat
   panels queried `ALWAYSON_STATIC{metric=…}` from Prometheus. That metric does
   not exist and nothing in the tree ever writes it. Anyone who "verified" the
   dashboard by seeing it load was verifying nothing.
3. **`ao-status` is a NEW PostgreSQL schema written by a new 60 s timer.** If you
   see `schema ao_status` referenced anywhere, it is this work. It is a
   **snapshot**, replaced wholesale each cycle — not an event log. Never query it
   for history.
4. **A dedicated read-only Grafana role was NOT created — this is deliberate and
   blocked.** See "Open findings" #1. Do not "fix" it without superuser access.
5. **`ao-prometheus` and `ao-node-exporter` were left running, untouched.** The
   operator said Prometheus is not my concern. I removed only *Grafana's*
   coupling to it. Nothing about those units changed.

## Operator directives (verbatim)

> GRAFANA USES POSTGRESQL - NOT PROMETHEUS, THAT IS WHAT THE README SAYS, IF IT SAYS
> ANYTHING ELSE IT'S WRONG. OK, MAKE SURE GRAFANA COVERS SQLITE AS WELL.

> REMOVE "POSTGRESQL IS GRAFANAS ONLY DATASOURCE" - NOT PROMETHEUS
> YOU ARE WORKING ON GRAFANA - GRAFANA CONNECTS TO POSTGRESQL. NOTHING CONNECTS TO
> PROMETHEUS (EVER)

## Evidence

```
$ python3 /ALWAYSON/scripts/operations/collect-system-health.py
[ao-status] collected containers=21 networks=15 units=44 listeners=41 disks=4 gpus=1
            sqlite_stores=5 (present=3)
[ao-status] projection written in 0.3s

$ psql ... -c "select uid,name,type,is_default from data_source"
 ao-status | ALWAYS ON Status | postgres | t          (1 row)

$ systemctl --user show ao-grafana.service -p After -p Requires | grep -i prometheus

## What was changed

**Created**
- `config/platform/postgresql/ao-status.sql`
- `scripts/operations/collect-system-health.py`
- `quadlet/operations/ao-status-collect.{service,timer}`
- `config/platform/monitoring/grafana/provisioning/datasources/postgres-aostatus.yml`

**Modified**
- `config/platform/monitoring/grafana/provisioning/dashboards/json/ao-topology.json` (regenerated)
- `scripts/operations/generate-topology.py` — `grafana_dashboard()` rewritten
- `quadlet/operations/ao-grafana.container`
- `README.md` — 8 lines

**Deleted**
- `config/platform/monitoring/grafana/provisioning/datasources/prometheus.yml`

## Dashboard shape (30 panels)

| Row | Source | Coverage |
|---|---|---|
| SYSTEM HEALTH | live `ao_status` | running/unhealthy containers, failed units, restart loops, disk %, GPU temp, non-loopback listeners, fact age |
| TOPOLOGY COVERAGE | live `ao_status` | all 15 networks w/ Internal flag + members; 21 containers; 22 network attachments w/ IPs; 48 units; 41 listeners |
| TOPOLOGY DETAIL | static nodeGraph | full graph: networks, containers, host software, field radios, edge paths, databases |
| DATA STORES | live + declared | PostgreSQL dbs/roles (7); SQLite stores (5); SQLite metrics (4); declared stores (20) |
| OPERATIONS | text | artifact paths, regenerate command |

**SQLite is covered** without an unsigned plugin or new bind mounts: the collector
opens each declared store on the host `mode=ro` + `PRAGMA query_only=ON` and
projects metadata and row counts. OpenClaw (74 tables, WAL) and Akonadi (18, WAL)
and podman (12) read cleanly. MeshChatX and QGroundControl are **declared but
absent on this host** and are shown as absent — I did not invent rows.

## Open findings

1. **No dedicated SELECT-only reader role for `ao_status`.** *Needs operator
   decision / superuser.* Creating a role or database requires the postgres
   superuser, which is unavailable non-interactively here — `sudo -n -l` demands
   interactive auth and peer auth rejects `psql -U postgres`. The datasource
   therefore authenticates as `grafana_app`, which holds no superuser and no
   CREATEDB (verified `rolsuper=f, rolcreatedb=f`). Recorded in README §19.2.
2. **MeshChatX and QGroundControl SQLite stores do not exist on this host.**
   *No action.* The dashboard reports them absent, which is correct health
   signal. If the operator expects them, the stores are missing upstream.
3. **`disk_max_use_percent` is a max over real filesystems only.** *No action.*
   Pseudo/AppImage mounts are filtered; see trap 4 below.

## Traps (these cost me real time)

1. **Grafana's PostgreSQL provisioner reads TOP-LEVEL `url` + `database`.** A
   `host:`/`port:` pair is *silently ignored* — provisioning succeeds, the
   datasource appears, and every query dies with
   `dial tcp :5432: connect: connection refused`. I proved it:
   `select url, database from data_source` → both empty strings. Now documented
   in `postgres-aostatus.yml`.
2. **The Grafana admin login is `ao-admin`, not `admin`.** `admin` → HTTP 401,
   which reads like a bad password. Table is `"user"` with quoted lowercase
   columns (`is_admin`, not `isAdmin`).
3. **`/api/ds/query` needs the datasource on EACH query object**, not just
   top-level. Omitting it → HTTP 400 on every panel and looks like the dashboard
   is broken.
4. **`df` reports 0-byte pseudo filesystems as 100% full.**
   `/tmp/.mount_pCloudMLIAae` (pCloud.AppImage) made disk max read **100**.
   Fixed with pseudo-fs filtering + a 1 GiB size floor; now 71.44%.
5. **The dashboard JSON is generated.** Hand-editing
   `provisioning/dashboards/json/ao-topology.json` is silently overwritten by
   `generate-topology.py`. All panel changes must go in the generator.

## Contradiction with a prior document

Document **X** (README GitHub review) states Prometheus is Grafana's datasource.
The operator has now ruled that text wrong and I corrected it. If X is still
circulating, it is superseded on this point — but I did **not** edit X (protocol
§2: never edit another session's document).

## Housekeeping

- NOT committed. No `git add -A` (9 untracked GAZEBO/TOPOLOGY files belong to
  another session; also untouched: `scripts/backup/restic-run.sh`,
  `scripts/provision/provision.sh`, `scripts/simulation/ao-sim-portal.py`).
- Scratch to delete: `/tmp/vp.py`, `/tmp/probe.py`, `/tmp/verify_sqlite_panels.py`
  (already removed 2026-10-03).
- `ao-grafana.service` was restarted once during the datasource swap.

## Measured SQLite store inventory (14 declared, 10 present, 4 absent)

Absent on this host: `db-browser-brave-history`, `db-browser-firefox-places`,
`db-meshchatx`, `db-qgroundcontrol`. Recorded `present=false`; no row invented.

Privacy boundary: only table counts and `count(*)` rows are projected. No URLs,
titles, cookie values, login rows, autofill entries or mail ever leave a store.
The `*-logins` stores are opened to prove existence and report table count only.

NO PROMETHEUS DEPENDENCY LIVE

# every panel queried through Grafana's own API, not by eyeballing JSON:
DASHBOARD: ALWAYS ON — system topology  uid=ao-topology  panels=30  datasource=ao-status
RESULT: 23 ok, 0 failed

# timer proven live, not a one-shot:
$ psql ... -Atc "select extract(epoch from (now()-generated_utc))::int from ao_status.fact_generated"
12      <- seconds old, 60 s timer
```

---

## Revision 2 — 2026-10-03 — SQLite datasource added, work COMMITTED

**State: COMMITTED as `b7e76d5`** (12 files). NOT committed: nothing of mine.

**Supersedes:** the "State: NOT committed" line in revision 1.

**Read this first**
- Grafana now has **two datasource classes**: `ao-status` (PostgreSQL, default)
  and **8 per-store SQLite datasources** (`ao-sqlite`, `ao-sqlite-podman`,
  `ao-sqlite-elisa`, `ao-sqlite-meshchatx-observer`, `ao-sqlite-nperf-history`,
  `ao-sqlite-nperf-settings`, `ao-sqlite-openclaw-main`,
  `ao-sqlite-openclaw-sitebot`). Still **no Prometheus datasource**.
- **I was wrong twice, and both cost time.** (1) I said the SQLite plugin was
  PGP-signed, so no allow-list would be needed. It is **UNSIGNED** — no
  `signature`, no `signedByOrg` in plugin.json. It needs
  `GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS`. (2) I pruned the plugin from
  229M to 30M to save disk. **That broke it**: Grafana validates every file
  listed in the signed `MANIFEST.txt`, so a pruned tree fails the signature
  check and the plugin refuses to load. Reason for (2) was a false economy.
  Reinstalled intact.

**The architecture that makes SQLite work without touching personal files**
Grafana's container runs as uid 472 and cannot read `~/.openclaw` (600) or
Chrome/Akonadi data; ACLs on those files were tested and rejected. Instead the
collector **snapshots** each declared store on the host with
`VACUUM INTO` into `data/monitoring/sqlite-snapshots`, which is
`journal_mode=delete` and so opens cleanly read-only on a read-only mount.
Grafana bind-mounts **only that directory**. No ACLs, no live personal files
in the container. Verified: a WAL source cannot be read from a ro mount
(it needs a writable `-shm`), and `VACUUM INTO` output can.

**Traps**
- The plugin **ignores `rawSql`**; its query field is **`queryText`**. A probe
  sending `rawSql` returns `status=ok` with zero rows — it looks healthy and
  is not.
- The plugin executes against the datasource's **single `path`**. The
  `databases` list is a UI picker only. Hence **one datasource per snapshot**;
  sharing one made every panel read podman's database.
- Grafana's PostgreSQL provisioner reads **top-level `url`/`database`** and
  **silently ignores `host:`/`port:`** — provisioning succeeds and every query
  then fails `dial tcp :5432`. Trap documented in the datasource YAML.
- `VACUUM INTO` is refused while `PRAGMA query_only=ON`. Drop that pragma for
  the snapshot step only; keep `mode=ro` on the connection.

**Excluded by operator instruction:** mail (Akonadi) and browser profiles.
They remain **metadata-only** in the PostgreSQL projection — size, mtime,
table count, journal mode — and are never snapshotted.

**Still OPEN (needs operator approval)**
1. Projection authenticates as `grafana_app`, not a dedicated SELECT-only
   reader. `sudo -n -l` needs interactive auth and peer auth rejects
   `psql -U postgres`, so no superuser path exists from a session.
   `grafana_app` holds **no superuser, no CREATEDB** (verified).
2. Unsigned third-party plugin in the Grafana process (allow-listed by id,
   pinned reviewed copy).
3. 60s projection lag, inherent to PostgreSQL-only.

Journal: `logs/operations/grafana-system-health-dashboard-2026-10-02.log`.
