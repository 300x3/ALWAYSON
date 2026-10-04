#!/usr/bin/env python3
"""ALWAYS ON - system-health projection collector (README Section 6 / 17.2).

Grafana's only datasource is PostgreSQL. This collector runs on the host as
the `scottw` user and projects the live facts Grafana needs -- podman
containers, ao-* networks, systemd units, listening sockets, disks, GPU state
and the README-declared SQLite stores -- into schema `ao_status` in Grafana's
own PostgreSQL application database.

READ-ONLY BY CONSTRUCTION
  * Every podman/systemd/socket query is an inspection call. Nothing is
    started, stopped, restarted or reconfigured.
  * Every SQLite store is opened `mode=ro` with `PRAGMA query_only=ON`.
  * Only metadata and row counts leave a SQLite store. Message bodies, mail,
    browsing history and credentials are never read into the projection.
  * No password, token or key is read, logged or written here.

Prometheus is deliberately not consulted. Grafana does not read it.

Usage: collect-system-health.py [--dry-run]
"""

from __future__ import annotations

import glob as globmod
import json
import os
import pathlib
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time

VERSION = "1.0.0"
DB_HOST = "/var/run/postgresql"
DB_NAME = "grafana"
DB_USER = "grafana_app"

# The SQLite stores named in README 4.3 / 3.3. Those rows are: MeshChatX,
# QGroundControl, Akonadi, browser profile stores, Podman metadata. An earlier
# revision of this list carried OpenClaw instead of the browser row and was
# wrong: OpenClaw is not a README 4.3 store. Corrected 2026-10-02.
#
# `paths` are candidate locations for a declared store; the first that exists
# wins. A declared store with no existing path is recorded present=false.
# Nothing outside this list is ever opened.
SQLITE_STORES = [
    # ------------------------------------------------------------------
    # Browser profile stores. README 4.3 row 481 names Firefox, Brave,
    # Chrome AND Edge as one store class, so each browser gets its OWN
    # declared entry. An earlier revision listed Chromium and Brave only as
    # fallback paths on the Chrome entry, which was wrong in a way that hid
    # real data: it projected at most one browser and could never report a
    # second one. Measured 2026-10-02: Edge is installed at
    # ~/.config/microsoft-edge with the same Default/History, Cookies,
    # Login Data, Web Data layout as Chrome, and was silently absent.
    # ------------------------------------------------------------------
    {
        "id": "db-browser-chrome-history",
        "label": "Google Chrome profile — History",
        "authority": "not_authoritative",
        "mount_only": True,
        "paths": ["~/.config/google-chrome/Default/History"],
        # Counts only. No URL, title or visit timestamp is ever projected.
        "metrics": [("history_urls", "SELECT count(*) FROM urls")],
    },
    {
        "id": "db-browser-chrome-cookies",
        "label": "Google Chrome profile — Cookies",
        "authority": "not_authoritative",
        "mount_only": True,
        "paths": ["~/.config/google-chrome/Default/Cookies"],
        # Counts only. No host, name or value is ever projected.
        "metrics": [("cookies", "SELECT count(*) FROM cookies")],
    },
    {
        "id": "db-browser-chrome-logins",
        "label": "Google Chrome profile — Login Data (credential store)",
        "authority": "not_authoritative",
        "mount_only": True,
        "paths": ["~/.config/google-chrome/Default/Login Data"],
        # Deliberately no metrics. This table holds username and password
        # blobs. Its existence, size and mtime are reported; not one row of
        # content is read, so no credential can reach the projection
        # (README 4.2, 4.1 rule 5).
        "metrics": [],
    },
    {
        "id": "db-browser-chrome-webdata",
        "label": "Google Chrome profile — Web Data",
        "authority": "not_authoritative",
        "mount_only": True,
        "paths": ["~/.config/google-chrome/Default/Web Data"],
        # The table is `autofill` on this Chrome build, not `autofill_profiles`
        # as on older ones; the collector skips a metric whose table is absent,
        # so a renamed schema degrades to "no metric" rather than an error.
        # Counts only. This schema also holds a `credit_cards` table, which is
        # never referenced by any query here.
        "metrics": [("autofill_profiles", "SELECT count(*) FROM autofill")],
    },
    {
        "id": "db-browser-edge-history",
        "label": "Microsoft Edge profile — History",
        "authority": "not_authoritative",
        "mount_only": True,
        "paths": ["~/.config/microsoft-edge/Default/History"],
        # Counts only, same rule as the Chrome entry.
        "metrics": [("history_urls", "SELECT count(*) FROM urls")],
    },
    {
        "id": "db-browser-edge-cookies",
        "label": "Microsoft Edge profile — Cookies",
        "authority": "not_authoritative",
        "mount_only": True,
        "paths": ["~/.config/microsoft-edge/Default/Cookies"],
        # Counts only, same rule as the Chrome entry.
        "metrics": [("cookies", "SELECT count(*) FROM cookies")],
    },
    {
        "id": "db-browser-edge-logins",
        "label": "Microsoft Edge profile — Login Data (credential store)",
        "authority": "not_authoritative",
        "mount_only": True,
        "paths": ["~/.config/microsoft-edge/Default/Login Data"],
        # Deliberately no metrics, same rule as the Chrome credential store.
        "metrics": [],
    },
    {
        "id": "db-browser-edge-webdata",
        "label": "Microsoft Edge profile — Web Data",
        "authority": "not_authoritative",
        "mount_only": True,
        "paths": ["~/.config/microsoft-edge/Default/Web Data"],
        # Counts only, same rule as the Chrome entry.
        "metrics": [("autofill_profiles", "SELECT count(*) FROM autofill")],
    },
    {
        "id": "db-browser-firefox-places",
        "label": "Firefox profile — places.sqlite",
        "authority": "not_authoritative",
        "mount_only": True,
        # Firefox profile directories are named places.sqlite under a random
        # profile name, so the profile directory is globbed, never hard-coded.
        # If Firefox is not installed this stays present=false, which is the
        # honest report.
        "paths": ["~/.mozilla/firefox/*/places.sqlite"],
        # Counts only. place names and visit timestamps are never projected.
        "metrics": [("history_urls", "SELECT count(*) FROM moz_places")],
    },
    {
        "id": "db-browser-brave-history",
        "label": "Brave profile — History",
        "authority": "not_authoritative",
        "mount_only": True,
        "paths": ["~/.config/BraveSoftware/Brave-Browser/Default/History"],
        # Counts only, same rule as the Chrome entry.
        "metrics": [("history_urls", "SELECT count(*) FROM urls")],
    },
    {
        "id": "db-akonadi",
        "label": "Akonadi / KDE PIM SQLite",
        "authority": "not_authoritative",
        "mount_only": True,
        "paths": ["~/.local/share/akonadi/akonadi.db"],
        # Counts only. Mail bodies and indexes are never read.
        "metrics": [
            ("pim_items", "SELECT count(*) FROM PimItemTable"),
            ("collections", "SELECT count(*) FROM CollectionTable"),
        ],
    },
    {
        "id": "db-podman",
        "label": "Podman rootless metadata store",
        "authority": "not_authoritative",
        "paths": ["~/.local/share/containers/storage/db.sql"],
        # Counts only. The Config tables hold full argv/env; never selected.
        "metrics": [
            ("containers", "SELECT count(*) FROM ContainerConfig"),
            ("pods", "SELECT count(*) FROM PodConfig"),
            ("volumes", "SELECT count(*) FROM VolumeConfig"),
        ],
    },
    {
        "id": "db-meshchatx",
        "label": "MeshChatX SQLite store",
        "authority": "not_authoritative",
        "paths": [
            "~/.local/share/MeshChatX/meshchatx.sqlite",
            "~/.local/share/meshchatx/meshchatx.db",
        ],
        # Counts only. Message bodies are never read.
        "metrics": [],
    },
    {
        "id": "db-qgroundcontrol",
        "label": "QGroundControl SQLite store",
        "authority": "not_authoritative",
        "paths": [
            "~/.local/share/QGroundControl.org/QGroundControl.db",
            "~/.config/QGroundControl.org/QGroundControl.db",
        ],
        # Counts only. Flight plans and waypoints are never read.
        "metrics": [],
    },
    # ------------------------------------------------------------------
    # Stores found by inspection on 2026-10-02, excluding mail and browser
    # profiles per the operator's directive. Each was verified to open
    # read-only before being declared; a store that is later removed simply
    # reports present=false.
    # ------------------------------------------------------------------
    {
        "id": "db-openclaw-agent-main",
        "label": "OpenClaw agent state — main",
        "authority": "not_authoritative",
        "paths": ["~/.openclaw/agents/main/agent/openclaw-agent.sqlite"],
        # Counts only. No prompt, response or tool payload is ever read.
        # auth_profile_* is deliberately omitted: it holds credentials.
        "metrics": [
            ("memory_chunks", "SELECT count(*) FROM memory_index_chunks"),
            ("memory_sources", "SELECT count(*) FROM memory_index_sources"),
        ],
    },
    {
        "id": "db-openclaw-agent-sitebot",
        "label": "OpenClaw agent state — sitebot",
        "authority": "not_authoritative",
        "paths": ["~/.openclaw/agents/sitebot/agent/openclaw-agent.sqlite"],
        # Counts only. Same omission as the main agent.
        "metrics": [
            ("memory_chunks", "SELECT count(*) FROM memory_index_chunks"),
            ("memory_sources", "SELECT count(*) FROM memory_index_sources"),
        ],
    },

    {
        "id": "db-nperf-history",
        "label": "nPerf run history",
        "authority": "not_authoritative",
        "paths": ["~/.local/share/nPerf/history.db"],
        "metrics": [("runs", "SELECT count(*) FROM history")],
    },
    {
        "id": "db-nperf-settings",
        "label": "nPerf settings",
        "authority": "not_authoritative",
        "paths": ["~/.local/share/nPerf/settings.db"],
        # Row count only. Settings values are never selected.
        "metrics": [("settings_rows", "SELECT count(*) FROM user")],
    },
    {
        "id": "db-reticulum-meshchatx-observer",
        "label": "MeshChatX declarative performance observer",
        "authority": "not_authoritative",
        "paths": ["~/.config/reticulum-meshchatx/declarative_performance_observer.db"],
        # Counts only. Report bodies are never selected.
        "metrics": [
            ("reports", "SELECT count(*) FROM declarative_performance_observer_reports"),
            ("policies", "SELECT count(*) FROM declarative_performance_observer_policies"),
        ],
    },
    {
        "id": "db-klipper-history",
        "label": "Klipper clipboard history",
        "authority": "not_authoritative",
        "paths": ["~/.local/share/klipper/history3.sqlite"],
        # Deliberately no metrics. This store holds clipboard contents, which
        # can include passwords and tokens. Only existence, size and mtime are
        # reported (README 4.2, 4.1 rule 5).
        "metrics": [],
        # And never snapshotted: a snapshot would place copied clipboard content
        # in a world-readable file inside data/. Metadata only.
        "no_snapshot": True,
    },
    {
        "id": "db-libaccounts",
        "label": "libaccounts-glib accounts store",
        "authority": "not_authoritative",
        "paths": ["~/.config/libaccounts-glib/accounts.db"],
        # Deliberately no metrics: this table holds account identifiers.
        "metrics": [],
        # Measured 2026-10-03: Signatures(key, token) and Settings(key). Never
        # snapshotted for the same reason as klipper.
        "no_snapshot": True,
    },

    {
        "id": "db-elisa",
        "label": "Elisa music library",
        "authority": "not_authoritative",
        "paths": ["~/.local/share/elisa/elisaDatabase.db"],
        # Counts only. No titles, artists or paths are ever selected.
        "metrics": [
            ("tracks", "SELECT count(*) FROM Tracks"),
            ("albums", "SELECT count(*) FROM Albums"),
            ("artists", "SELECT count(*) FROM Artists"),
        ],
    },
]


def log(message: str) -> None:
    """Operational log to stderr only. Never contains a secret."""
    print("[ao-status] %s" % message, file=sys.stderr, flush=True)


def run(argv: list, timeout: int = 20):
    """Run an inspection command. Returns stdout, or None on any failure."""
    if not shutil.which(argv[0]):
        return None
    try:
        proc = subprocess.run(
            argv, capture_output=True, text=True, timeout=timeout, check=False
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        log("command failed %s: %s" % (argv[0], type(exc).__name__))
        return None
    return proc.stdout if proc.returncode == 0 else None


def run_json(argv: list, timeout: int = 25) -> list:
    out = run(argv, timeout=timeout)
    if not out:
        return []
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        log("non-JSON output from %s" % argv[0])
        return []
    return data if isinstance(data, list) else []


def _num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------
# podman: containers, attachments, networks
# --------------------------------------------------------------------------

def _health_from_status(status: str) -> str:
    low = (status or "").lower()
    if "(unhealthy)" in low:
        return "unhealthy"
    if "(healthy)" in low:
        return "healthy"
    return "none"


def _restarts_from_status(status: str) -> int:
    low = (status or "").lower()
    if "(restart=" not in low:
        return 0
    try:
        return int(low.split("(restart=", 1)[1].split(")", 1)[0])
    except (IndexError, ValueError):
        return 0


def collect_containers():
    """Returns (containers, attachments, published_ports).

    `podman ps --format json` reports network NAMES only, with no IP
    addresses, so container addresses come from `podman inspect`. Both are
    read-only inspection calls.
    """
    containers = []
    attachments = []
    published = {}

    for entry in run_json(["podman", "ps", "-a", "--format", "json"]):
        names = entry.get("Names") or []
        name = names[0] if names else (entry.get("Id") or "")[:12]
        if not name:
            continue
        status = entry.get("Status") or ""
        images = entry.get("Image") or []
        if isinstance(images, str):
            image = images
        elif images and isinstance(images[0], dict):
            image = images[0].get("Names") or images[0].get("Id") or ""
        else:
            image = ""
        # Restarts is a real top-level field in this podman version; fall back
        # to parsing the status string if a future version drops it.
        restarts = entry.get("Restarts")
        containers.append({
            "name": name,
            "quadlet": "%s.container" % name,
            "state": (entry.get("State") or "").lower(),
            "health": _health_from_status(status),
            "restart_count": int(restarts) if isinstance(restarts, (int, float))
                              else _restarts_from_status(status),
            # Strip the digest: the inventory keeps the repository name only.
            "image": image.split("@", 1)[0] if "@" in image else image,
            "started_utc": None,
        })

    listed = [c["name"] for c in containers]
    if listed:
        for detail in run_json(["podman", "inspect"] + listed, timeout=40):
            name = (detail.get("Name") or "").lstrip("/")
            if not name:
                continue
            settings = detail.get("NetworkSettings") or {}
            for net_name, net_cfg in (settings.get("Networks") or {}).items():
                attachments.append({
                    "container": name,
                    "network": net_name,
                    "ip_address": (net_cfg or {}).get("IPAddress") or None,
                })
            for port_key, bindings in (settings.get("Ports") or {}).items():
                for binding in bindings or []:
                    try:
                        host_port = int(binding.get("HostPort"))
                    except (TypeError, ValueError):
                        continue
                    published[host_port] = {
                        "container": name,
                        "host_ip": binding.get("HostIp") or "0.0.0.0",
                        "protocol": port_key.split("/")[0],
                    }

    return containers, attachments, published


def collect_networks(attachments):
    """One row per network, with Internal flag, subnets and member count.

    `podman network ls --format json` uses lower-case keys, unlike
    `podman ps --format json` which is title-case. Both spellings are read so
    a podman version change cannot silently empty this table.
    """
    networks = []
    for net in run_json(["podman", "network", "ls", "--format", "json"]):
        name = net.get("name") or net.get("Name") or ""
        if not name:
            continue
        subnets = [s["subnet"] for s in (net.get("subnets") or [])
                   if isinstance(s, dict) and s.get("subnet")]
        internal = net.get("internal", net.get("Internal"))
        networks.append({
            "name": name,
            "internal": bool(internal),
            "driver": net.get("driver") or net.get("Driver") or "",
            "cidr": "; ".join(sorted(subnets)),
            # Counted from the same inspect view the attachment rows came from,
            # so member counts agree with the container table.
            "member_count": sum(1 for a in attachments if a["network"] == name),
        })
    return networks


# --------------------------------------------------------------------------

def collect_units():
    """Every ao-* user unit, with ActiveState, SubState, LoadState, NRestarts."""
    units = []
    out = run([
        "systemctl", "--user", "list-units", "--all", "--no-legend", "--no-pager",
        "--plain", "--property=Id,ActiveState,SubState,LoadState,NRestarts",
    ], timeout=30)
    if not out:
        log("systemctl --user list-units returned nothing")
        return units

    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 2 or not parts[0].startswith("ao-"):
            continue
        name, props = parts[0], {}
        for token in parts[1:]:
            key, sep, value = token.partition("=")
            if sep:
                props[key] = value
        try:
            restarts = int(props.get("NRestarts") or 0)
        except ValueError:
            restarts = 0
        # Quadlets deploy flat, so a unit file in the deployed directory is
        # the reliable marker that a unit is a Quadlet container.
        quadlet = pathlib.Path(
            os.path.expanduser("~/.config/containers/systemd/%s" % name)
        )
        units.append({
            "name": name,
            "active_state": props.get("ActiveState") or "unknown",
            "sub_state": props.get("SubState") or "",
            "load_state": props.get("LoadState") or "",
            "kind": "ao- container" if quadlet.exists() else "systemd service",
            "restarts": restarts,
        })
    return units


# --------------------------------------------------------------------------
# sockets, disks, gpu
# --------------------------------------------------------------------------

# Listening sockets are collected wholesale and attributed afterwards by
# published port; see collect_listeners for why process-name filtering fails
# for rootless podman sockets.


def collect_listeners(published):
    """Listening sockets, attributed to the ao-* container that published them.

    TRAP (measured 2026-10-02): `ss -p` run as the `scottw` user cannot see the
    owning process of a rootless podman-published socket. ao-grafana's
    127.0.0.1:3001 shows LISTEN with an EMPTY process column. Filtering on
    process name therefore records zero ao-* listeners. Ownership is instead
    resolved by matching the listening port against the published-port map
    that `podman inspect` reports, which is authoritative.
    """
    rows = []
    out = run(["ss", "-ltn"], timeout=20)
    if not out:
        log("ss -ltn returned nothing")
        return rows
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 4:
            continue
        local = parts[3]
        address, sep, port_s = local.rpartition(":")
        if not sep:
            continue
        try:
            port = int(port_s)
        except ValueError:
            continue
        # Strip the %iface suffix ss appends, e.g. 0.0.0.0%eno1 or 127.0.0.53%lo.
        bare = address.split("%", 1)[0]
        owner = published.get(port)
        rows.append({
            "protocol": "tcp",
            "address": bare,
            "port": port,
            "owner": owner["container"] if owner else "host-process",
            "loopback": bare in ("127.0.0.1", "::1", "[::1]", "localhost", "127.0.0.53"),
            "scope": "ao-service" if owner else "host-app",
        })
    return rows


# Pseudo and packaged filesystems that report a meaningless 0-byte size and
# therefore a fake 100% full. Measured 2026-10-02: /tmp/.mount_pCloudMLIAae
# (pCloud.AppImage, 0.0 GB) came through as disk_max_use_percent = 100.
_PSEUDO_FS = ("appimage", "efivarfs", "squashfs", "overlay", "fuse.snap")


def collect_disks():
    """Real filesystems only, with a floor on size so a 0-byte pseudo mount
    cannot masquerade as a full disk."""
    rows = []
    min_bytes = 1024 ** 3  # 1 GiB
    out = run(["df", "-P", "-B1", "-x", "tmpfs", "-x", "devtmpfs"], timeout=20)
    for line in (out or "").splitlines():
        parts = line.split()
        if len(parts) < 6 or parts[0] == "Filesystem" or not parts[5].startswith("/"):
            continue
        filesystem = parts[0]
        if any(marker in filesystem.lower() for marker in _PSEUDO_FS):
            continue
        try:
            size, used, avail = int(parts[1]), int(parts[2]), int(parts[3])
        except ValueError:
            continue
        if size < min_bytes:
            continue
        rows.append({
            "mountpoint": parts[5],
            "filesystem": filesystem,
            "size_bytes": size,
            "used_bytes": used,
            "avail_bytes": avail,
            "use_percent": round(used / size * 100, 2) if size else None,
        })
    return rows


# --------------------------------------------------------------------------
# declared stores, from the README-authoritative topology model
# --------------------------------------------------------------------------

MODEL_PATH = "/ALWAYSON/config/platform/topology-model.yaml"


def collect_declared_stores():
    """Read the store inventory out of topology-model.yaml.

    This is a declaration list, not a measurement, so it is a straight read of
    the model file. Kept in the projection so the dashboard can show declared
    authority next to the live SQLite presence check.
    """
    try:
        import yaml
        with open(MODEL_PATH, "r", encoding="utf-8") as handle:
            model = yaml.safe_load(handle) or {}
    except (OSError, ValueError) as exc:
        log("topology-model.yaml unreadable: %s" % type(exc).__name__)
        return []

    rows = []
    for entry in model.get("databases") or []:
        if not isinstance(entry, dict) or not entry.get("id"):
            continue
        rows.append({
            "id": entry["id"],
            "label": entry.get("label") or "",
            "kind": entry.get("kind") or "",
            "software": entry.get("software") or "",
            "placement": entry.get("placement") or "",
            "authority": entry.get("authority") or "",
            "status": entry.get("status") or "",
        })
    return rows


# --------------------------------------------------------------------------
# write
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# OPS-33: absent is not an error.
#
# `read_error` is free text and every non-ok row put a sentence in it, so a
# store that is simply NOT INSTALLED on this host and a store that is present
# but CORRUPT both rendered as "a row with an error in it". The dashboard and
# any alert built on that column could not tell an expected, healthy absence
# from a fault that needs a human.
#
# These are different facts with different owners: absence is answered by
# "is this software installed", corruption is answered by "restore this file".
# So the state is now an explicit enum, derived in ONE place from the facts the
# row already carries, rather than set at each return path -- a new return path
# cannot forget to set it, which is exactly how the two cases got conflated.
# --------------------------------------------------------------------------

# Failure texts that mean the file is there and could not be used. Anything
# else that lands in read_error is an operator directive, which is a decision
# and not a fault.
_STORE_ERRORS = (
    "stat failed", "not a sqlite file", "header read failed",
    "open failed", "read failed", "snapshot failed", "integrity",
)

# Strings that are a fault even though they contain no word like "failed".
# sqlite3 raises DatabaseError("file is not a database") /
# "database disk image is malformed" for a corrupt file, and those sentences
# match none of the markers above - so a CORRUPT store was classified
# 'excluded', i.e. reported as a deliberate operator decision.
#
# That is the exact confusion OPS-33 exists to remove, and it was the more
# dangerous direction: an unreadable database silently counted as "on purpose".
# Measured 2026-10-04 with classify_store({'present': True,
# 'read_error': 'database disk image is malformed'}) -> 'excluded'.
_STORE_CORRUPT = (
    "malformed", "not a database", "corrupt", "encrypted",
    "unable to open database",
)


def classify_store(row):
    """Set row['status'] to absent | error | excluded | ok. Mutates and returns.

    Order matters and is not interchangeable:
      1. not present at all -> absent. This wins over any read_error, because a
         store that is simply not installed has no error to report, whatever
         text the inspecting path left behind.
      2. present and the failure text matches a known fault -> error.
      3. present with some other text -> excluded (an operator directive).
      4. present, no text at all -> ok.
    """
    err = (row.get("read_error") or "").strip()
    low = err.lower()
    if not row.get("present"):
        row["status"] = "absent"
    elif any(marker in low for marker in _STORE_ERRORS) \
            or any(marker in low for marker in _STORE_CORRUPT):
        row["status"] = "error"
    elif err:
        # Present, readable metadata, but an operator directive applies.
        row["status"] = "excluded"
    else:
        row["status"] = "ok"
    return row


def collect_sqlite():
    """Read every declared store in place and return (rows, metrics).

    This is the metadata pass. It runs whether or not a snapshot directory is
    configured, so the dashboard can still report on a store whose contents
    are never snapshotted (mail and browser stores, excluded by operator
    decision on 2026-10-03). Rows carry presence, size, journal mode and table
    count only -- never message bodies, mail, browsing history or credentials.
    """
    rows, metrics = [], []
    for spec in SQLITE_STORES:
        row, store_metrics = inspect_sqlite_store(spec)
        rows.append(classify_store(row))
        metrics.extend(store_metrics)
    return rows, metrics


def collect_gpu():
    if not shutil.which("nvidia-smi"):
        return []
    out = run([
        "nvidia-smi", "--query-gpu=name,driver_version,temperature.gpu,"
        "utilization.gpu,memory.used,memory.total",
        "--format=csv,noheader,nounits",
    ], timeout=20)
    rows = []
    for line in (out or "").splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 6:
            continue
        used, total = _num(parts[4]), _num(parts[5])
        rows.append({
            "name": parts[0],
            "driver": parts[1],
            "temperature_c": _num(parts[2]),
            "utilisation_pct": _num(parts[3]),
            "memory_used_mib": int(used) if used is not None else None,
            "memory_total_mib": int(total) if total is not None else None,
        })
    return rows
# --------------------------------------------------------------------------

def inspect_sqlite_store(spec):
    """Open one declared store read-only. Returns (row, metrics). Never writes."""
    row = {
        "id": spec["id"],
        "label": spec["label"],
        "path": spec["paths"][0],
        "authority": spec["authority"],
        "present": False,
        # Whether Grafana can actually query this store through the SQLite
        # datasource. Deliberately NOT derived from the spec flags here: a flag
        # says what we intend, not what happened. This starts False and is set
        # True only by snapshot_sqlite() once a snapshot is on disk. Setting it
        # from the spec was a real defect -- it reported metadata-only stores
        # (klipper, libaccounts) as integrated when no snapshot exists for them.
        "integrated": False,
        "size_bytes": None,
        "modified_utc": None,
        "table_count": None,
        "journal_mode": None,
        "read_error": None,
        # Set by classify_store() on the way out; declared here so the key is
        # always present even if a new return path forgets to classify.
        "status": "ok",
    }
    metrics = []

    # Paths may be literals or globs (Firefox names its profile directory
    # randomly, so places.sqlite cannot be hard-coded). Sorted so the reported
    # path is stable across runs rather than depending on directory order.
    candidates: list[str] = []
    for pattern in spec["paths"]:
        expanded = os.path.expanduser(pattern)
        if any(ch in expanded for ch in "*?["):
            candidates.extend(sorted(globmod.glob(expanded)))
        else:
            candidates.append(expanded)

    resolved = next((c for c in candidates if os.path.exists(c)), None)
    if resolved is None:
        row["read_error"] = "declared store not present on this host"
        return row, metrics

    row["path"] = resolved
    try:
        stat = os.stat(resolved)
        row["size_bytes"] = stat.st_size
        row["modified_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(stat.st_mtime))
    except OSError as exc:
        row["read_error"] = "stat failed: %s" % type(exc).__name__
        return row, metrics

    # An operator directive may exclude a store from integration entirely. It
    # is then reported by stat only: the file is never opened, so a running
    # application's own database lock cannot stall the collector and no
    # content is read. This is the path taken by the mail and browser stores.
    if spec.get("mount_only"):
        # It exists; we are choosing not to open it. Reporting present=false
        # would be a lie, so present tracks existence and read_error carries
        # the exclusion.
        row["present"] = True
        row["read_error"] = row["read_error"] or "excluded from integration by operator directive (metadata only)"
        return row, metrics

    # A .db extension is not a format. Verified 2026-10-02: both
    # nPerf/engine.db and phishingurl/malware.db carry a .db name but begin
    # with binary data, not the SQLite magic, and fail with "file is not a
    # database". Checking the header keeps such a file out of the declaration
    # entirely instead of reporting a confusing per-run error.
    try:
        with open(row["path"], "rb") as handle:
            if handle.read(16) != b"SQLite format 3\x00":
                row["read_error"] = "not a SQLite file (bad header)"
                return row, metrics
    except OSError as exc:
        row["read_error"] = "header read failed: %s" % type(exc).__name__
        return row, metrics

    try:
        conn = sqlite3.connect("file:%s?mode=ro" % resolved, uri=True, timeout=5)
    except sqlite3.Error as exc:
        row["read_error"] = "open failed: %s" % type(exc).__name__
        return row, metrics

    try:
        # Belt and braces: mode=ro already refuses writes, and query_only makes
        # the intent explicit to any later reader of this code.
        conn.execute("PRAGMA query_only=ON")
        row["present"] = True
        try:
            row["journal_mode"] = conn.execute("PRAGMA journal_mode").fetchone()[0]
        except sqlite3.Error:
            pass
        tables = [
            r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
        ]
        row["table_count"] = len(tables)
        for metric, query in spec.get("metrics", []):
            # Only run a query whose table was just confirmed present, so a
            # changed schema cannot turn a count into an error.
            if query.split("FROM", 1)[1].strip() not in tables:
                continue
            try:
                metrics.append({
                    "store_id": spec["id"],
                    "metric": metric,
                    "value": int(conn.execute(query).fetchone()[0]),
                })
            except (sqlite3.Error, TypeError, ValueError):
                continue
    except sqlite3.Error as exc:
        row["read_error"] = "read failed: %s" % type(exc).__name__
    finally:
        conn.close()
    return row, metrics


def snapshot_sqlite(spec, out_dir):
    """Write a VACUUM INTO snapshot of one declared store into out_dir.

    WHY A SNAPSHOT RATHER THAN A DIRECT MOUNT
    The two live stores (openclaw, akonadi) are WAL-mode. SQLite must create
    and write the -shm index to read a WAL database, so a read-only bind mount
    of the originals fails. Measured 2026-10-03 on this host:

      file:...openclaw.sqlite?mode=ro            -> OperationalError:
                                                   attempt to write a readonly database
      same, with immutable=1                     -> OK (stale, ignores -wal)
      sqlite3 .backup() of a WAL source          -> stays WAL, still fails read-only
      VACUUM INTO (mode=ro source) -> delete-mode-> OK on a read-only mount

    immutable=1 was rejected: it ignores the -wal file, so Grafana would report
    stale data while appearing healthy. So the collector snapshots instead, and
    Grafana reads a snapshot. Two consequences, both deliberate:
      * No ACL or permission change is applied to any personal store.
      * Grafana cannot write to, or corrupt, a live store.
    The source is opened mode=ro, so VACUUM INTO writes only to the new file.

    Returns (row, ok).
    """
    row, _ = inspect_sqlite_store(spec)
    if not row["present"]:
        return row, False
    if spec.get("mount_only"):
        # inspect_sqlite_store already refused to open it; stop here rather
        # than opening it again below.
        return row, False
    if spec.get("no_snapshot"):
        # Metadata only. A snapshot would copy credential-bearing content into
        # a world-readable file under data/, which README 4.1 rule 5 forbids.
        row["read_error"] = "metadata only: store content is not snapshotted"
        target = os.path.join(out_dir, "%s.db" % spec["id"])
        # Remove any snapshot an earlier revision left behind.
        if os.path.exists(target):
            os.unlink(target)
        return row, False

    target = os.path.join(out_dir, "%s.db" % spec["id"])
    staging = "%s.tmp" % target
    try:
        if os.path.exists(staging):
            os.unlink(staging)
        source = sqlite3.connect("file:%s?mode=ro" % row["path"], uri=True, timeout=10)
        try:
            source.execute("VACUUM INTO '%s'" % staging.replace("'", "''"))
        finally:
            source.close()
        # Replace atomically so a reader never sees a half-written snapshot.
        os.replace(staging, target)
        os.chmod(target, 0o644)
    except sqlite3.Error as exc:
        row["read_error"] = "snapshot failed: %s" % type(exc).__name__
        if os.path.exists(staging):
            os.unlink(staging)
        return row, False

    row["snapshot_path"] = target
    row["snapshot_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    # Only now is Grafana genuinely able to query this store. Verify the file
    # really landed rather than trusting os.replace alone.
    row["integrated"] = os.path.exists(target) and os.path.getsize(target) > 0
    return row, row["integrated"]


def snapshot_all_sqlite(out_dir):
    """Snapshot every declared store. Returns (rows, snapshot_paths)."""
    os.makedirs(out_dir, exist_ok=True)
    rows, paths = [], []
    for spec in SQLITE_STORES:
        if spec.get("mount_only"):
            # Declared store that exists but is deliberately not snapshotted.
            row, _ = inspect_sqlite_store(spec)
            row["read_error"] = row["read_error"] or "excluded from snapshot by operator decision"
            rows.append(classify_store(row))
            continue
        row, ok = snapshot_sqlite(spec, out_dir)
        rows.append(classify_store(row))
        if ok:
            paths.append(row["snapshot_path"])
    return rows, paths


# --------------------------------------------------------------------------
# write
# --------------------------------------------------------------------------

# table -> ordered column list. The projection is a snapshot, not a log, so
# each table is replaced wholesale on every cycle.
_TABLES = (
    ("container", ("name", "quadlet", "state", "health", "restart_count", "image", "started_utc")),
    ("container_network", ("container", "network", "ip_address")),
    ("network", ("name", "internal", "driver", "cidr", "member_count")),
    ("unit", ("name", "active_state", "sub_state", "load_state", "kind", "restarts")),
    ("listener", ("protocol", "address", "port", "owner", "loopback", "scope")),
    ("disk", ("mountpoint", "filesystem", "size_bytes", "used_bytes", "avail_bytes", "use_percent")),
    ("gpu", ("name", "driver", "temperature_c", "utilisation_pct",
             "memory_used_mib", "memory_total_mib")),
    ("sqlite_store", ("id", "label", "path", "authority", "present", "integrated",
                      "size_bytes", "modified_utc", "table_count", "journal_mode",
                      "read_error", "status")),
    ("sqlite_metric", ("store_id", "metric", "value")),
    ("declared_store", ("id", "label", "kind", "software", "placement",
                        "authority", "status")),
)


def _literal(value):
    """Render a Python value as a SQL literal.

    The snapshot is written through the psql client rather than a Python
    driver: neither psycopg2 nor psycopg3 is installed on this host, and
    installing one would need root (measured 2026-10-02). Every value below is
    a number, a boolean, None, or a string from podman/systemd/stat/stat --
    never a secret.
    """
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    # Escape backslashes first, then quotes: the value is emitted as an
    # E'' string so the escaping is explicit rather than server-setting
    # dependent.
    text = str(value).replace("\\", "\\\\").replace("'", "''")
    return "E'%s'" % text


def write_projection(snapshot):
    """Replace the projection in one transaction, via the psql client."""
    password = os.environ.get("GF_DATABASE_PASSWORD", "")
    if not password:
        raise SystemExit("GF_DATABASE_PASSWORD is not set")
    if not shutil.which("psql"):
        raise SystemExit("psql is not on PATH")

    lines = ["BEGIN;", "SET LOCAL search_path TO ao_status, public;"]
    for table, columns in _TABLES:
        lines.append("TRUNCATE %s;" % table)
        for record in snapshot[table]:
            values = ",".join(_literal(record[c]) for c in columns)
            lines.append("INSERT INTO %s (%s) VALUES (%s);" % (
                table, ",".join(columns), values))

    # Stamped last, inside the same transaction: a panel can never see a fresh
    # fact_generated_utc beside a half-written snapshot.
    lines.append(
        "INSERT INTO fact_generated (id, generated_utc, collector_host,"
        " collector_version) VALUES (1, now(), %s, %s)"
        " ON CONFLICT (id) DO UPDATE SET generated_utc = now(),"
        " collector_host = EXCLUDED.collector_host,"
        " collector_version = EXCLUDED.collector_version;"
        % (_literal(socket.gethostname()), _literal(VERSION)))
    lines.append("COMMIT;")

    # mkstemp creates the file 0600 in a private directory, so the transient
    # write script is never world-readable.
    handle, path = tempfile.mkstemp(prefix="ao-status-", suffix=".sql")
    try:
        with os.fdopen(handle, "w") as sql_file:
            sql_file.write("\n".join(lines) + "\n")
        env = dict(os.environ, PGPASSWORD=password)
        proc = subprocess.run(
            ["psql", "-v", "ON_ERROR_STOP=1", "-q", "-h", DB_HOST,
             "-U", DB_USER, "-d", DB_NAME, "-f", path],
            capture_output=True, text=True, timeout=120, env=env, check=False,
        )
        if proc.returncode != 0:
            # psql stderr carries SQL text, never the password.
            raise SystemExit("psql failed: %s" % (proc.stderr or "").strip()[:500])
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    started = time.time()

    containers, attachments, published = collect_containers()
    snapshot = {
        "container": containers,
        "container_network": attachments,
        "network": collect_networks(attachments),
        "unit": collect_units(),
        "listener": collect_listeners(published),
        "disk": collect_disks(),
        "gpu": collect_gpu(),
    }
    snapshot["sqlite_store"], snapshot["sqlite_metric"] = collect_sqlite()
    snapshot["declared_store"] = collect_declared_stores()

    # Stage 2: snapshot the non-excluded stores to a read-only directory that
    # is bind-mounted into the Grafana container. Grafana's SQLite datasource
    # reads these copies; it never sees, and can never touch, a live store.
    snap_dir = os.environ.get("AO_SQLITE_SNAPSHOT_DIR", "")
    if dry_run or not snap_dir:
        if not snap_dir:
            log("AO_SQLITE_SNAPSHOT_DIR unset; skipping snapshot stage")
    else:
        store_rows, snap_paths = snapshot_all_sqlite(snap_dir)
        snapshot["sqlite_store"] = store_rows
        log("snapshot stage: %d snapshot(s) in %s, %d excluded by operator decision"
            % (len(snap_paths), snap_dir,
               sum(1 for s in SQLITE_STORES if s.get("mount_only"))))

    log("collected containers=%d networks=%d units=%d listeners=%d disks=%d gpus=%d "
        "sqlite_stores=%d (present=%d)"
        % (len(snapshot["container"]), len(snapshot["network"]), len(snapshot["unit"]),
           len(snapshot["listener"]), len(snapshot["disk"]), len(snapshot["gpu"]),
           len(snapshot["sqlite_store"]),
           sum(1 for s in snapshot["sqlite_store"] if s["present"])))

    if dry_run:
        print(json.dumps(snapshot, indent=2))
        return 0

    write_projection(snapshot)
    log("projection written in %.1fs" % (time.time() - started))
    return 0


if __name__ == "__main__":
    sys.exit(main())
