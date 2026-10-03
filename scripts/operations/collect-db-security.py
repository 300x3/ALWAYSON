#!/usr/bin/env python3
"""ALWAYS ON - collect database security facts for Prometheus (README 3.3, 17.2).

Prometheus is the isolated security layer and does security work OUTWARD: this
collector is that work applied to the databases. It is deliberately one
direction only. Nothing writes into Prometheus, and this collector exposes no
query surface of its own -- it writes the Prometheus textfile collector format
and returns. Prometheus reads the files; nothing else does.

Design constraints, each one measured rather than assumed:

* The collector runs on the HOST, not in a container. Every container on
  ao-admin is on Internal=true and cannot reach the databases at all -- verified
  with a TCP probe from ao-prometheus and ao-node-exporter, both NOT-reachable
  to the host PostgreSQL. A containerised collector could not do this job.
* PostgreSQL is read through the psql CLIENT, not a Python driver. Neither
  psycopg2 nor psycopg3 is installed on this host and installing one needs root.
* SQLite is opened mode=ro with PRAGMA query_only, matching the existing
  collect-system-health.py behaviour. Belt and braces: the URI mode and the
  pragma both refuse writes.
* Every statement is a read. No INSERT, UPDATE, DELETE, DDL or VACUUM appears
  anywhere in this file, and none is constructed from input.
* No secret is printed, logged, or placed on a command line. The PostgreSQL
  password comes from a 0600 wallet-backed environment file and is handed to
  psql via PGPASSWORD in the child environment only.
"""
from __future__ import annotations

import os
import pathlib
import sqlite3
import subprocess
import sys
import time

OUT_DIR = pathlib.Path(os.environ.get("AO_PROM_TEXTFILE_DIR", "/ALWAYSON/data/prometheus-textfile"))
# Measured 2026-10-02 against pg_hba.conf: the application roles are granted
# scram-sha-256 on host 127.0.0.1 and on the local socket, but the socket path
# for a NON-superuser role is `peer`, which can only ever match the OS user of
# the same name. Connecting as grafana_app over /var/run/postgresql therefore
# fails with "Peer authentication failed" no matter how correct the password is.
# TCP to 127.0.0.1 is the path that scram-sha-256 actually accepts, so that is
# what this collector uses.
PGHOST = os.environ.get("AO_PROM_PGHOST", "127.0.0.1")

# Which PostgreSQL databases to inspect, and the socket port each answers on.
# Ports are the published loopback rootless ports measured with `ss -ltnp`; the
# host cluster itself is on 5432. A database that is down is reported as down,
# never skipped silently.
PG_TARGETS = (
    # label, port, database, role
    #
    # Every database declared in README 3.3.1 is listed, including the ones this
    # process cannot currently reach. A database that cannot be read reports
    # reachable=0 rather than being omitted, so the gap is visible in Prometheus
    # instead of being invisible by absence. Measured 2026-10-03:
    #
    #   grafana          reachable -- grafana_app has CONNECT (read 21 backends)
    #   host-cluster     not reachable -- no CONNECT on the `postgres` database
    #   sales            not reachable -- grafana_app has no CONNECT on salesdb
    #   fabrication      not reachable -- grafana_app has no CONNECT on a_fab
    #   cordadb          not reachable -- no CONNECT, and it is on the host
    #                     cluster, not on a published port
    #   mastodon         UNREACHABLE BY CONSTRUCTION -- mastodon-db publishes no
    #                     host port (`podman ps` shows bare 5432/tcp), so there is
    #                     no loopback path to it. Publishing one is a port
    #                     exposure and needs operator approval (README 4.1).
    #   webodm           same: ao-webodm-db publishes no host port
    #
    # Granting a read identity on the five reachable-by-network databases needs a
    # superuser change on each cluster, which is an operator action; the metrics
    # turn to 1 by themselves once the grant exists. No port is opened here.
    ("grafana", 5432, "grafana", "grafana_app"),
    ("host-cluster", 5432, "postgres", "grafana_app"),
    ("sales", 15432, "salesdb", "grafana_app"),
    ("fabrication", 15433, "a_fab", "grafana_app"),
    ("cordadb", 5432, "cordadb", "grafana_app"),
    ("mastodon", 5432, "mastodon", "grafana_app"),
    ("webodm", 25463, "webodm", "grafana_app"),
)

SQLITE_TARGETS = (
    # Operator instruction 2026-10-03: collect the application SQLite stores,
    # and explicitly NOT the mail or browser ones.
    #
    # EXCLUDED BY INSTRUCTION -- do not add these, even though README 3.3.1
    # lists them as declared stores:
    #   * Akonadi / KDE PIM  -- contacts, calendars and MAIL INDEXES
    #   * Firefox, Brave, Chrome, Edge profile stores
    # Both hold personal or browsing material a security metric has no business
    # surfacing, and neither is application state worth alerting on.
    ("meshchatx", tuple(
        sorted(str(p) for p in pathlib.Path(
            os.path.expanduser("~/.reticulum-meshchatx/identities")
        ).glob("*/database.db"))
    ) or ("~/.reticulum-meshchatx/identities/*/database.db",)),
    ("meshchatx-plugins", (
        "~/.reticulum-meshchatx/plugins/plugin_state.db",
    )),
    ("qgroundcontrol", (
        "~/.cache/QGroundControl/QGroundControl/QGCMapCache/qgcMapCache.db",
    )),
)

# Podman's rootless metadata store is BoltDB (storage/db.sql), not SQLite, so it
# is not a target of this collector. Recorded because README 3.3.1 lists it and
# a later reader should not go looking for it.
_NOT_SQLITE = (
    "podman rootless metadata: ~/.local/share/containers/storage/db.sql (BoltDB)",
)

# Podman's rootless metadata store is BoltDB (storage/db.sql), not SQLite, so it
# is not a target of this collector. Recorded here because README 3.3.1 lists it
# under SQLite-adjacent stores and a later reader should not go looking for it.
_NOT_SQLITE = (
    "podman rootless metadata: ~/.local/share/containers/storage/db.sql (BoltDB)",
)


_DECLARED: set[str] = set()


def _now() -> int:
    return int(time.time())


def _write_metric(name: str, value, mtype: str = "gauge", help_text: str = "") -> str:
    """Emit one metric in node_exporter textfile format.

    Labels belong on the SAMPLE line only. node_exporter rejects a "# TYPE" line
    that carries labels -- measured live: "text format parsing error in line 4:
    invalid metric name in comment". The earlier version split the name and put
    `{db="..."}` on the TYPE line, which made every scrape fail.

    HELP is emitted once per bare metric name and omitted entirely otherwise,
    because a repeated HELP for a name that already has one is itself a parse
    error in some versions. TYPE is emitted once per bare name and skipped when
    that name has already been declared in this run.
    """
    bare = name.split("{", 1)[0]
    if bare in _DECLARED:
        return "%s %s\n" % (name, value)
    _DECLARED.add(bare)
    head = ""
    if help_text:
        head += "# HELP %s %s\n" % (bare, help_text)
    head += "# TYPE %s %s\n" % (bare, mtype)
    return head + "%s %s\n" % (name, value)


def psql_scalar(port: int, database: str, sql: str, user: str) -> tuple[str, str]:
    """Run one read-only scalar query. Returns (value, error).

    The password is passed through the child environment, never argv, so it
    cannot appear in `ps` output or in any log of the command line.
    """
    env = dict(os.environ)
    # The systemd EnvironmentFile provides GF_DATABASE_PASSWORD (the wallet
    # variable name used by ao-status-collect.service too). AO_PROM_PG_PASSWORD
    # is honoured first for ad-hoc/manual runs.
    env["PGPASSWORD"] = os.environ.get("AO_PROM_PG_PASSWORD") or os.environ.get("GF_DATABASE_PASSWORD", "")
    env.setdefault("PGCONNECT_TIMEOUT", "5")
    cmd = [
        "psql", "--no-password", "-tAq",
        "-h", PGHOST, "-p", str(port), "-d", database, "-U", user,
        "-v", "ON_ERROR_STOP=1", "-c", sql,
    ]
    try:
        proc = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=15,
        )
    except subprocess.TimeoutExpired:
        return "0", "timeout"
    except FileNotFoundError:
        return "0", "psql_missing"
    if proc.returncode != 0:
        # stderr can echo the failing SQL, never the password: PGPASSWORD is
        # not part of the connection string. Trim it to a single stable token
        # so the metric does not leak server text or version banners.
        return "0", "connect_failed"
    out = proc.stdout.strip()
    return (out if out else "0"), ""


def collect_postgres(label: str, port: int, database: str, user: str) -> list[str]:
    # Exactly one series per (metric, label) pair. Emitting the labelled form
    # twice -- once optimistically and once after a failure -- produced a
    # duplicate-series file that Prometheus rejects at parse time.
    out: list[str] = []
    # Active and idle backends are the security-relevant pair: a count far
    # above the expected worker set is the signal worth alerting on.
    for metric, sql in (
        ("alwayson_db_postgres_backends", "SELECT count(*) FROM pg_stat_activity;"),
        ("alwayson_db_postgres_active", "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"),
        ("alwayson_db_postgres_write_conflicts",
         "SELECT coalesce(sum(conflicts),0) FROM pg_stat_database;"),
        ("alwayson_db_postgres_deadlocks",
         "SELECT coalesce(sum(deadlocks),0) FROM pg_stat_database;"),
        ("alwayson_db_postgres_connections_max",
         "SELECT setting::bigint FROM pg_settings WHERE name = 'max_connections';"),
    ):
        value, err = psql_scalar(port, database, sql, user)
        if err:
            out.append(_write_metric('alwayson_db_postgres_reachable{db="%s"}' % label, 0))
            out.append(_write_metric('alwayson_db_postgres_scrape_error{db="%s"}' % label, 1))
            return out
        if metric == "alwayson_db_postgres_backends":
            # First successful read for this database: it is reachable.
            out.append(_write_metric('alwayson_db_postgres_reachable{db="%s"}' % label, 1))
        out.append(_write_metric(metric + '{db="%s"}' % label, value))
    out.append(_write_metric('alwayson_db_postgres_scrape_error{db="%s"}' % label, 0))
    return out


def collect_sqlite(label: str, candidates: tuple[str, ...]) -> list[str]:
    out = []
    resolved = next(
        (os.path.expanduser(p) for p in candidates if os.path.exists(os.path.expanduser(p))),
        None,
    )
    if resolved is None:
        out.append(_write_metric('alwayson_db_sqlite_reachable{db="%s"}' % label, 0))
        out.append(_write_metric('alwayson_db_sqlite_scrape_error{db="%s"}' % label, 1))
        return out

    out.append(_write_metric('alwayson_db_sqlite_reachable{db="%s"}' % label, 1))
    try:
        size = os.stat(resolved).st_size
    except OSError:
        out.append(_write_metric('alwayson_db_sqlite_scrape_error{db="%s"}' % label, 1))
        return out
    out.append(_write_metric('alwayson_db_sqlite_size_bytes{db="%s"}' % label, size))

    try:
        # mode=ro refuses writes at the VFS layer; query_only makes the intent
        # explicit to any later reader of this code, as in collect-system-health.
        conn = sqlite3.connect("file:%s?mode=ro" % resolved, uri=True, timeout=5)
    except sqlite3.Error:
        out.append(_write_metric('alwayson_db_sqlite_scrape_error{db="%s"}' % label, 1))
        return out

    try:
        conn.execute("PRAGMA query_only=ON")
        tables = conn.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table';").fetchone()[0]
        out.append(_write_metric('alwayson_db_sqlite_tables{db="%s"}' % label, tables))
        try:
            fk = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        except sqlite3.Error:
            fk = "unknown"
        # An integrity check is a read of the file, not a write. It is the one
        # genuinely useful security fact about a local store: a corrupted or
        # tampered file shows up here.
        try:
            integrity = conn.execute("PRAGMA quick_check;").fetchone()[0]
        except sqlite3.Error:
            integrity = "unknown"
        out.append(_write_metric(
            'alwayson_db_sqlite_integrity_ok{db="%s",result="%s"}' % (label, integrity), 1))
        out.append(_write_metric('alwayson_db_sqlite_scrape_error{db="%s"}' % label, 0))
    finally:
        conn.close()
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [_write_metric("alwayson_db_security_scrape_timestamp_seconds", _now())]

    for label, port, database, user in PG_TARGETS:
        try:
            lines.extend(collect_postgres(label, port, database, user))
        except Exception as exc:  # never let one database abort the others
            lines.append(_write_metric('alwayson_db_postgres_reachable{db="%s"}' % label, 0))
            lines.append(_write_metric('alwayson_db_postgres_scrape_error{db="%s"}' % label, 1))
            sys.stderr.write("postgres %s failed: %s\n" % (label, type(exc).__name__))

    for label, candidates in SQLITE_TARGETS:
        try:
            lines.extend(collect_sqlite(label, candidates))
        except Exception as exc:
            lines.append(_write_metric('alwayson_db_sqlite_reachable{db="%s"}' % label, 0))
            sys.stderr.write("sqlite %s failed: %s\n" % (label, type(exc).__name__))

    target = OUT_DIR / "ao-db-security.prom"
    tmp = OUT_DIR / "ao-db-security.prom.tmp"
    tmp.write_text("\n".join(lines), encoding="utf-8")
    os.chmod(tmp, 0o644)
    tmp.replace(target)
    sys.stderr.write("wrote %s (%d lines)\n" % (target, len(lines)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
