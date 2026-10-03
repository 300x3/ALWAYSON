-- ALWAYS ON - Grafana system-health projection (README Section 6, 17.2, 3.3).
--
-- Grafana reads PostgreSQL and nothing else. Prometheus is not a Grafana
-- datasource and nothing in Grafana connects to it. Because the live health
-- facts (podman, systemd, sockets, disks, GPU) are not held in any database,
-- a read-only host collector projects them here, into Grafana's own
-- PostgreSQL application database, which README 3.3 already records as
-- Grafana's dedicated application state.
--
-- WHY A SCHEMA AND NOT A NEW DATABASE
-- Creating a new database or a new role requires the postgres superuser.
-- grafana_app is not a superuser and cannot CREATEDB (verified 2026-10-02:
--   SELECT rolsuper, rolcreatedb FROM pg_roles WHERE rolname='grafana_app'
--   -> f | f
--   SELECT has_database_privilege('grafana_app','grafana','CREATE') -> t
-- ), so the projection lives in schema ao_status inside the existing
-- database that Grafana already owns and already authenticates with. This
-- adds no new credential, no new listener and no new network. It is recorded
-- as an open deviation: the writer shares grafana_app rather than holding a
-- dedicated least-privilege writer role.
--
-- Idempotent. Run as any role holding CREATE on the grafana database:
--   psql -v ON_ERROR_STOP=1 -h /var/run/postgresql -U grafana_app \
--        -d grafana -f ao-status.sql
--
-- SECRET RULE: no password, token or key may appear here.

CREATE SCHEMA IF NOT EXISTS ao_status;

-- Single row, rewritten every cycle. Surfaced on the dashboard so a stalled
-- collector is visible as stale data rather than silently reading as healthy.
CREATE TABLE IF NOT EXISTS ao_status.fact_generated (
    id                  int PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    generated_utc       timestamptz NOT NULL DEFAULT now(),
    collector_host      text,
    collector_version   text,
    CONSTRAINT fact_generated_singleton CHECK (id = 1)
);

CREATE TABLE IF NOT EXISTS ao_status.container (
    name            text PRIMARY KEY,
    quadlet         text,
    state           text,          -- running / exited / configured / absent
    health          text,          -- healthy / unhealthy / none
    restart_count   int  NOT NULL DEFAULT 0,
    image           text,
    started_utc     timestamptz,
    collected_utc   timestamptz NOT NULL DEFAULT now()
);

-- One row per container/network attachment.
CREATE TABLE IF NOT EXISTS ao_status.container_network (
    container   text NOT NULL,
    network     text NOT NULL,
    ip_address  text,
    PRIMARY KEY (container, network)
);

CREATE TABLE IF NOT EXISTS ao_status.network (
    name          text PRIMARY KEY,
    internal      boolean,
    driver        text,
    cidr          text,
    member_count  int NOT NULL DEFAULT 0,
    collected_utc timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ao_status.unit (
    name          text PRIMARY KEY,
    active_state  text,
    sub_state     text,
    load_state    text,
    kind          text,           -- ao- container / systemd service / other
    restarts      int NOT NULL DEFAULT 0,
    collected_utc timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ao_status.listener (
    protocol   text,
    address    text,
    port       int,
    owner      text,
    loopback   boolean NOT NULL DEFAULT true,
    scope      text,              -- ao-service / host-app / system
    collected_utc timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ao_status.disk (
    mountpoint  text PRIMARY KEY,
    filesystem  text,
    size_bytes  bigint,
    used_bytes  bigint,
    avail_bytes bigint,
    use_percent numeric(5,2),
    collected_utc timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ao_status.gpu (
    name             text PRIMARY KEY,
    driver           text,
    temperature_c    numeric(5,2),
    utilisation_pct  numeric(5,2),
    memory_used_mib  bigint,
    memory_total_mib bigint,
    collected_utc    timestamptz NOT NULL DEFAULT now()
);

-- The SQLite stores named in the README store inventory. A store that is
-- declared but not present on this host is recorded as present=false; no row
-- is invented for a store that was never declared.
CREATE TABLE IF NOT EXISTS ao_status.sqlite_store (
    id             text PRIMARY KEY,
    label          text,
    path           text,
    authority      text,
    present        boolean NOT NULL DEFAULT false,
    -- integrated=false means the store is declared and its existence is
    -- recorded, but it is never opened, snapshotted or queried. The mail
    -- (Akonadi) and browser stores are excluded by operator directive: no
    -- content is read and no snapshot is produced. The dashboard shows the
    -- distinction so an excluded store never reads as an integrated one.
    integrated     boolean NOT NULL DEFAULT false,
    size_bytes     bigint,
    modified_utc   timestamptz,
    table_count    int,
    journal_mode   text,
    read_error     text,
    collected_utc  timestamptz NOT NULL DEFAULT now()
);

-- Migration for databases created before `integrated` existed. CREATE TABLE IF
-- NOT EXISTS is a no-op on an existing table, so the column has to be added
-- separately. Idempotent.
ALTER TABLE ao_status.sqlite_store
    ADD COLUMN IF NOT EXISTS integrated boolean NOT NULL DEFAULT false;

-- Counts only. Never message bodies, mail, browsing history or credentials.
CREATE TABLE IF NOT EXISTS ao_status.sqlite_metric (
    store_id  text NOT NULL,
    metric    text NOT NULL,
    value     bigint,
    collected_utc timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (store_id, metric)
);

-- The stores declared in config/platform/topology-model.yaml. Static facts from
-- the README-authoritative model, projected so the dashboard can show declared
-- authority alongside the live SQLite presence check in the same row group.
CREATE TABLE IF NOT EXISTS ao_status.declared_store (
    id         text PRIMARY KEY,
    label      text,
    kind       text,          -- postgresql / sqlite / redis / h2 / ...
    software   text,
    placement  text,          -- host / container / external
    authority  text,          -- README data classification
    status     text
);

-- Grafana reads every panel from this view.
CREATE OR REPLACE VIEW ao_status.v_system_health AS
SELECT
    (SELECT count(*) FROM ao_status.container)                          AS containers_observed,
    (SELECT count(*) FROM ao_status.container WHERE state = 'running')  AS containers_running,
    (SELECT count(*) FROM ao_status.container WHERE health = 'unhealthy') AS containers_unhealthy,
    (SELECT count(*) FROM ao_status.network)                           AS networks_observed,
    (SELECT count(*) FROM ao_status.network WHERE internal)            AS networks_internal,
    (SELECT count(*) FROM ao_status.network WHERE NOT internal)        AS networks_non_internal,
    (SELECT count(*) FROM ao_status.unit WHERE active_state = 'failed')    AS units_failed,
    (SELECT count(*) FROM ao_status.unit WHERE active_state = 'activating') AS units_activating,
    (SELECT count(*) FROM ao_status.container WHERE restart_count > 3)    AS containers_restarting,
    (SELECT count(*) FROM ao_status.listener)                          AS listeners,
    (SELECT count(*) FROM ao_status.listener WHERE NOT loopback)       AS listeners_non_loopback,
    (SELECT count(*) FROM ao_status.disk)                              AS disks,
    (SELECT coalesce(max(use_percent), 0) FROM ao_status.disk)        AS disk_max_use_percent,
    (SELECT count(*) FROM ao_status.sqlite_store)                      AS sqlite_stores_declared,
    (SELECT count(*) FROM ao_status.sqlite_store WHERE present)        AS sqlite_stores_present,
    (SELECT count(*) FROM ao_status.sqlite_store WHERE NOT present)    AS sqlite_stores_absent,
    (SELECT count(*) FROM ao_status.gpu)                               AS gpus,
    (SELECT max(temperature_c) FROM ao_status.gpu)                     AS gpu_max_temperature_c,
    f.generated_utc                                                    AS fact_generated_utc,
    EXTRACT(EPOCH FROM (now() - f.generated_utc))::int                 AS fact_age_seconds
FROM ao_status.fact_generated f
WHERE f.id = 1;

\echo '--- ao_status projection ready ---'
SELECT count(*) AS tables FROM information_schema.tables WHERE table_schema = 'ao_status';
SELECT count(*) AS views   FROM information_schema.views  WHERE table_schema = 'ao_status';
