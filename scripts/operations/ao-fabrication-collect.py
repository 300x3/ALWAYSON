#!/usr/bin/env python3
"""ALWAYS ON - per-machine fabrication production collector.

Pulls per-machine production data from each individual MainsailOS / Moonraker /
Klipper machine on the EQUIPMENT LAN (10.42.0.0/24) and pushes records into
a_fab, the ao-fabrication database.

Why this runs on the HOST and not inside the domain (README v7 3.3.0.1):
`ao-fabrication` is Internal=true, so a container on it has no default route
and cannot reach the equipment LAN. The host bridge at 10.89.12.1 IS reachable
from inside the domain, so the host performs the LAN hop and hands the data to
a_fab over loopback. Same shape as ao-postgres-reporting-bridge.

PULL ONLY. This never writes to a machine. Moonraker is queried with GET and
this file contains no POST/PUT/DELETE helper, so there is no code path that
issues a print command or any other control action. Commanding live machinery is
a separate authorisation decision and is deliberately not implemented.

Usage:
    ao-fabrication-collect.py [--once|--dry-run] [--machine ID] [--init-db]
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

# Machines are configured explicitly, never discovered. An unauthenticated
# Moonraker on a DHCP LAN must be opted in by name, not auto-enrolled by a scan.
MACHINES_FILE = os.environ.get(
    "AO_FAB_MACHINES", os.path.expanduser("~/.config/alwayson/fabrication-machines.json"))

# a_fab is published on loopback only (ao-fabrication-db.container).
DB_HOST = os.environ.get("AO_FAB_DB_HOST", "127.0.0.1")
DB_PORT = int(os.environ.get("AO_FAB_DB_PORT", "15433"))
DB_NAME = os.environ.get("AO_FAB_DB_NAME", "a_fab")
DB_USER = os.environ.get("AO_FAB_DB_USER", "fabrication_role")
# Read from the env file fetch-kwallet-secret.sh wrote. Never a literal here.
DB_PASSWORD_ENV = "POSTGRES_PASSWORD"

INTERVAL = int(os.environ.get("AO_FAB_INTERVAL", "300"))
HTTP_TIMEOUT = float(os.environ.get("AO_FAB_HTTP_TIMEOUT", "8"))

# The Moonraker fields that are genuine per-machine production data.
QUERY = "print_stats&display_status&extruder&heater_bed&webhooks"


def log(msg):
    sys.stderr.write("ao-fabrication-collect: %s\n" % msg)
    sys.stderr.flush()


def load_machines(path=MACHINES_FILE):
    """Explicit opt-in machine list -> [(id, base_url, apikey), ...]."""
    if not os.path.exists(path):
        log("no machine list at %s -- nothing to collect" % path)
        return []
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    out = []
    for m in doc.get("machines", []):
        if not m.get("enabled", True):
            continue
        mid, host = m.get("id"), m.get("host")
        if not mid or not host:
            log("skipping malformed entry: %r" % m)
            continue
        base = host if host.startswith("http") else "http://" + host
        apikey = m.get("apikey") or os.environ.get("AO_FAB_APIKEY_%s" % mid)
        out.append((mid, base.rstrip("/"), apikey))
    return out


def get_json(url, apikey=None):
    """GET only."""
    req = urllib.request.Request(url, method="GET")
    if apikey:
        req.add_header("X-Api-Key", apikey)
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def collect_one(machine_id, base, apikey):
    """Pull one machine's production data and shape it for a_fab."""
    data = get_json("%s/printer/objects/query?%s" % (base, QUERY), apikey)
    status = (data.get("result") or {}).get("status") or {}
    ps = status.get("print_stats") or {}
    ext = status.get("extruder") or {}
    bed = status.get("heater_bed") or {}
    ds = status.get("display_status") or {}

    # An unreachable or erroring machine must not be recorded as a zero-output
    # run; that would silently corrupt the optimisation data.
    if not ps:
        raise RuntimeError("no print_stats in response -- refusing to record a "
                           "blank production record")

    def num(d, key, default=None):
        v = d.get(key)
        return v if isinstance(v, (int, float)) and not isinstance(v, bool) else default

    info = ps.get("info") or {}
    rec = {
        "machine_id": machine_id,
        "observed_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "klippy_state": ps.get("state"),
        "print_duration_s": num(ps, "print_duration", 0.0),
        "total_duration_s": num(ps, "total_duration", 0.0),
        "filament_used_mm": num(ps, "filament_used", 0.0),
        "filename": ps.get("filename") or None,
        "current_layer": info.get("current_layer"),
        "total_layer": info.get("total_layer"),
        "nozzle_c": num(ext, "temperature"),
        "bed_c": num(bed, "temperature"),
        "progress_pct": num(ds, "progress"),
    }
    rec["payload_sha256"] = hashlib.sha256(
        json.dumps(rec, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return rec


SCHEMA = """
CREATE TABLE IF NOT EXISTS machine_production (
    id               BIGSERIAL PRIMARY KEY,
    machine_id       TEXT        NOT NULL,
    observed_at_utc  TIMESTAMPTZ NOT NULL,
    klippy_state     TEXT,
    print_duration_s DOUBLE PRECISION,
    total_duration_s DOUBLE PRECISION,
    filament_used_mm DOUBLE PRECISION,
    filename         TEXT,
    current_layer    INTEGER,
    total_layer      INTEGER,
    nozzle_c         DOUBLE PRECISION,
    bed_c            DOUBLE PRECISION,
    progress_pct     DOUBLE PRECISION,
    payload_sha256   CHAR(64)    NOT NULL,
    ingested_at_utc  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS machine_production_uniq
    ON machine_production (machine_id, observed_at_utc);
CREATE INDEX IF NOT EXISTS machine_production_machine
    ON machine_production (machine_id, observed_at_utc DESC);
COMMENT ON TABLE machine_production IS
    'Per-machine production data pulled from each individual machine. Not a '
    'ledger, not a sales record, not a backup target (README v7 3.3.0).';
"""

COLS = ["machine_id", "observed_at_utc", "klippy_state", "print_duration_s",
        "total_duration_s", "filament_used_mm", "filename", "current_layer",
        "total_layer", "nozzle_c", "bed_c", "progress_pct", "payload_sha256"]


def _psql(sql, timeout=60):
    pw = os.environ.get(DB_PASSWORD_ENV)
    if not pw:
        log("no %s in environment; refusing (run under the Quadlet unit so "
            "fetch-kwallet-secret.sh has populated it)" % DB_PASSWORD_ENV)
        return None
    try:
        return subprocess.run(
            ["psql", "-h", DB_HOST, "-p", str(DB_PORT), "-U", DB_USER,
             "-d", DB_NAME, "-v", "ON_ERROR_STOP=1", "-q", "-c", sql],
            env={**os.environ, "PGPASSWORD": pw},
            capture_output=True, text=True, timeout=timeout)
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        log("psql unavailable: %s" % e)
        return None


def init_schema(dry_run=False):
    if dry_run:
        log("DRY-RUN would create machine_production in %s" % DB_NAME)
        return True
    r = _psql(SCHEMA)
    if r is None or r.returncode != 0:
        if r is not None:
            log("schema init failed: %s" % (r.stderr or "").strip()[:300])
        return False
    log("a_fab schema ready")
    return True


def write_record(rec, dry_run=False):
    """Insert idempotently; the unique index makes a re-run a no-op."""
    if dry_run:
        log("DRY-RUN %s -> %s" % (rec["machine_id"],
                                  json.dumps(rec, sort_keys=True)))
        return True
    vals = []
    for c in COLS:
        v = rec.get(c)
        if v is None:
            vals.append("NULL")
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            vals.append(str(v))
        else:
            vals.append("'" + str(v).replace("'", "''") + "'")
    sql = ("INSERT INTO machine_production (%s) VALUES (%s) "
           "ON CONFLICT (machine_id, observed_at_utc) DO NOTHING;"
           % (", ".join(COLS), ", ".join(vals)))
    r = _psql(sql, timeout=30)
    if r is None:
        return False
    if r.returncode != 0:
        log("insert failed for %s: %s"
            % (rec["machine_id"], (r.stderr or "").strip()[:300]))
        return False
    return True


def run_once(machines, dry_run=False, verbose=False):
    ok = fail = 0
    for machine_id, base, apikey in machines:
        try:
            rec = collect_one(machine_id, base, apikey)
            if verbose:
                log("%s: state=%s layer=%s/%s filament=%.1fmm"
                    % (machine_id, rec["klippy_state"], rec["current_layer"],
                       rec["total_layer"], rec["filament_used_mm"] or 0.0))
            if write_record(rec, dry_run):
                ok += 1
            else:
                fail += 1
        except (urllib.error.URLError, OSError, ValueError, RuntimeError) as e:
            # One machine being down must never stop the others.
            log("collect failed for %s: %s" % (machine_id, e))
            fail += 1
    log("pass complete: %d ok, %d failed" % (ok, fail))
    return fail


def main():
    ap = argparse.ArgumentParser(description="per-machine fabrication collector")
    ap.add_argument("--once", action="store_true", help="poll once and exit")
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would be written; touch nothing")
    ap.add_argument("--machine", help="collect only this machine id")
    ap.add_argument("--init-db", action="store_true",
                    help="create the a_fab schema and exit")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if args.init_db:
        return 0 if init_schema(args.dry_run) else 1

    machines = load_machines()
    if args.machine:
        machines = [m for m in machines if m[0] == args.machine]
        if not machines:
            log("machine %r is not in %s" % (args.machine, MACHINES_FILE))
            return 1
    if not machines:
        return 0
    if args.once or args.dry_run:
        return 0 if run_once(machines, args.dry_run, args.verbose) == 0 else 1
    while True:
        run_once(machines, args.dry_run, args.verbose)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    sys.exit(main())
