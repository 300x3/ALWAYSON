#!/usr/bin/env python3
# ALWAYS ON - scripts/operations/generate-topology.py
"""Generate the ALWAYS ON system topology diagram and companion artifacts.

Authority: the v6 architecture document (Sections ES.1-ES.2, 2.2, 3.1, 3.3, 3.3.1, 5.1,
5.2, 6.A, 9, 10, 18, 20.0), supplied by the operator as
"/ALWAYSON/TOPOLOGY/ALWAYS ON \u2014 Architecture, Operations, and Status - v6.md".
Where v6 and the older /ALWAYSON/README.md disagree, v6 governs (v6 ES.1).
Declarative overlay: /ALWAYSON/config/platform/topology-model.yaml
Declared runtime facts: /ALWAYSON/quadlet/**  +  /ALWAYSON/config/platform/*.yaml
Observed runtime facts: podman / systemd --user / ss / /proc / /dev/serial/by-id

Outputs (default /ALWAYSON/TOPOLOGY/):
  alwayson-system-topology.dot   Graphviz source
  alwayson-system-topology.svg   vector diagram (rendered by `dot`)
  alwayson-system-topology.png   raster diagram (144 dpi)
  alwayson-system-topology.html  self-contained diagram + inventory tables
  topology-inventory.json        machine-readable inventory (declared + live + drift)
  TOPOLOGY.md                    generated tables for README citation

Optional (--skip-grafana disables):
  config/platform/monitoring/grafana/provisioning/dashboards/alwayson-topology.yml
  config/platform/monitoring/grafana/provisioning/dashboards/json/alwayson-topology.json

Safety:
  * Read-only host inspection.  No service, network, port, mount, or database is
    modified.  Grafana files are written only under the ALWAYSON config tree;
    restarting ao-grafana.service is an explicit separate step.
  * Never reads /ALWAYSON/secrets/** or any *.env file.  No secret value, token,
    or credential is placed in any output artifact.
  * --dry-run prints the plan and writes nothing.

Usage:
  python3 generate-topology.py [--out-dir DIR] [--no-live] [--dry-run]
                               [--skip-grafana] [--print-json] [--quiet]
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment prerequisite
    sys.stderr.write("generate-topology: PyYAML is required\n")
    sys.exit(2)

PROJECT_ROOT = Path("/ALWAYSON")
QUADLET_DIR = PROJECT_ROOT / "quadlet"
PLATFORM_DIR = PROJECT_ROOT / "config" / "platform"
MODEL_PATH = PLATFORM_DIR / "topology-model.yaml"
CIDR_PATH = PLATFORM_DIR / "network-cidrs.yaml"
ALLOWLIST_PATH = PLATFORM_DIR / "listener-allowlist.yaml"
OUT_DIR_DEFAULT = PROJECT_ROOT / "TOPOLOGY"
GRAFANA_PROVISIONING = PROJECT_ROOT / "config" / "platform" / "monitoring" / "grafana" / "provisioning"
LOG_PATH = PROJECT_ROOT / "logs" / "operations" / "topology-generation.log"
DEPLOYED_QUADLET_DIR = Path.home() / ".config" / "containers" / "systemd"

STATUS_FILL = {
    "implemented": "#1b5e20",
    "partial": "#f9a825",
    "in_progress": "#ef6c00",
    "planned": "#455a64",
    "blocked": "#b71c1c",
    "declared": "#37474f",
    "unknown": "#616161",
}
STATUS_RANK = {
    "implemented": 0,
    "partial": 1,
    "in_progress": 2,
    "planned": 3,
    "declared": 4,
    "unknown": 5,
    "blocked": 6,
}
# Ports/LAN listeners that belong to the base OS, not to an ALWAYS ON service.
HOST_NOISE_PORTS = {
    (53, "udp"),
    (53, "tcp"),
    (67, "udp"),
    (323, "udp"),
    (631, "tcp"),
    (5353, "udp"),
    (5345, "tcp"),
}
LISTEN_RE = re.compile(
    r"^(?P<proto>tcp|udp)\s+(?:LISTEN|UNCONN)\s+\d+\s+\d+\s+(?P<local>\S+)\s+\S+\s*(?P<proc>users:\(\(.*\)\))?"
)
PROC_NAME_RE = re.compile(r'\("(?P<name>[^"]+)",pid=(?P<pid>\d+)')


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(message: str, quiet: bool = False) -> None:
    if not quiet:
        sys.stderr.write("generate-topology: %s\n" % message)


def journal(message: str, dry_run: bool) -> None:
    """Append an operational journal entry (README 4.1 rule 11)."""
    if dry_run:
        return
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write("%s %s\n" % (utc_now(), message))
    except OSError as exc:  # pragma: no cover - journal is best effort
        sys.stderr.write("generate-topology: journal write failed: %s\n" % exc)


def run(cmd: list[str]) -> tuple[int, str]:
    """Run a read-only inspection command."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, "ERROR: %s" % exc
    return result.returncode, result.stdout


def parse_ini_blocks(path: Path) -> dict[str, dict[str, list[str]]]:
    """Parse a Quadlet/systemd INI file keeping duplicate keys (Network=, Volume=...)."""
    sections: dict[str, dict[str, list[str]]] = {}
    current: str | None = None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return sections
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            sections.setdefault(current, {})
            continue
        if "=" in line and current is not None:
            key, value = line.split("=", 1)
            sections[current].setdefault(key.strip(), []).append(value.strip())
    return sections


def first(section: dict[str, list[str]], key: str, default: str = "") -> str:
    values = section.get(key)
    return values[0] if values else default


def all_values(section: dict[str, list[str]], key: str) -> list[str]:
    return list(section.get(key, []))


def short_image(image: str) -> tuple[str, str]:
    """Return (name, version) for an image reference, digest-pinned or tagged."""
    base = image.split("@", 1)[0]
    digest = ""
    if "@sha256:" in image:
        digest = image.rsplit("@sha256:", 1)[1][:10]
    tail = base.rsplit("/", 1)[-1]
    tag = tail.rsplit(":", 1)[1] if ":" in tail else ""
    plain = tail.rsplit(":", 1)[0] if ":" in tail else tail
    if digest:
        tag = "sha256:%s" % digest
    return plain, tag


def expand_home(value: str) -> str:
    return value.replace("%h", str(Path.home()))


def load_yaml(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    except (OSError, yaml.YAMLError) as exc:
        sys.stderr.write("generate-topology: cannot read %s: %s\n" % (path, exc))
        return {}
    return data if isinstance(data, dict) else {}


def read_network_cidrs() -> dict[str, str]:
    """Parse the free-text CIDR registry into network -> subnet."""
    cidrs: dict[str, str] = {}
    try:
        for line in CIDR_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.match(r"^(?P<name>[\w.-]+)\s+.*subnets=(?P<subnets>\S+)", line)
            if match:
                cidrs[match.group("name")] = match.group("subnets").split(",")[0]
    except OSError:
        pass
    return cidrs


def read_listener_allowlist() -> set[int]:
    allowed: set[int] = set()
    try:
        for line in ALLOWLIST_PATH.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^\s*-\s*(\d+)\s*$", line)
            if match:
                allowed.add(int(match.group(1)))
    except OSError:
        pass
    return allowed


# ---------------------------------------------------------------------------
# Declared runtime (Quadlet definitions in /ALWAYSON/quadlet)
# ---------------------------------------------------------------------------

def declared_containers() -> dict[str, dict]:
    containers: dict[str, dict] = {}
    network_ref = network_name_for_references()
    for path in sorted(QUADLET_DIR.glob("*/*.container")):
        sections = parse_ini_blocks(path)
        unit = path.stem
        container = sections.get("Container", {})
        unit_section = sections.get("Unit", {})
        service = sections.get("Service", {})
        install = sections.get("Install", {})
        image = first(container, "Image")
        name, version = short_image(image) if image else ("", "")
        containers[unit] = {
            "unit": unit,
            "file": str(path),
            "category": path.parent.name,
            "container_name": first(container, "ContainerName", unit),
            "description": first(unit_section, "Description", unit),
            "image": image,
            "image_name": name,
            "image_version": version,
            "networks": [network_ref.get(n.replace(".network", ""), n.replace(".network", ""))
                         for n in all_values(container, "Network")],
            "publish": [p for p in all_values(container, "PublishPort")],
            "volumes": [expand_home(v) for v in all_values(container, "Volume")],
            "environment": [e for e in all_values(container, "Environment")
                            if not e.lower().startswith("password")],
            "env_files": len(all_values(container, "EnvironmentFile")),
            "no_new_privileges": first(container, "NoNewPrivileges", "false"),
            "health_cmd": first(container, "HealthCmd"),
            "memory_max": first(service, "MemoryMax"),
            "cpu_quota": first(service, "CPUQuota"),
            "wanted_by": all_values(install, "WantedBy"),
            "declared": True,
            "live": False,
            "status": "declared",
            "state": "",
            "status_text": "",
            "ip_by_network": {},
            "published": [],
        }
    return containers


def declared_networks() -> dict[str, dict]:
    networks: dict[str, dict] = {}
    for path in sorted(QUADLET_DIR.glob("**/*.network")):
        sections = parse_ini_blocks(path)
        net = sections.get("Network", {})
        name = first(net, "NetworkName", path.stem)
        networks[name] = {
            "name": name,
            "file": str(path),
            "internal": first(net, "Internal", "true").lower() == "true",
            "declared": True,
            "live": False,
            "subnet": "",
            "gateway": "",
        }
    return networks


def network_name_for_references() -> dict[str, str]:
    """Map a Quadlet ``Network=`` reference to the runtime network name.

    A ``[Container] Network=`` value names a ``*.network`` unit file, not the
    network itself; the runtime name is that file's ``NetworkName=`` (e.g.
    ``ao-sales-network.network`` declares ``NetworkName=ao-sales``).  Without
    this mapping, container-to-network edges reference a network that does not
    exist at runtime.
    """
    mapping: dict[str, str] = {}
    for path in QUADLET_DIR.glob("**/*.network"):
        sections = parse_ini_blocks(path)
        mapping[path.stem] = first(sections.get("Network", {}), "NetworkName", path.stem)
        mapping[path.name] = mapping[path.stem]
    return mapping


def declared_units() -> list[dict]:
    units: list[dict] = []
    for path in sorted(QUADLET_DIR.glob("*/*.service")):
        sections = parse_ini_blocks(path)
        unit_section = sections.get("Unit", {})
        units.append({
            "unit": path.stem,
            "file": str(path),
            "description": first(unit_section, "Description", path.stem),
            "category": path.parent.name,
        })
    return units


# ---------------------------------------------------------------------------
# Observed runtime (read-only host inspection)
# ---------------------------------------------------------------------------

def live_containers() -> dict[str, dict]:
    containers: dict[str, dict] = {}
    code, out = run(["podman", "ps", "-a", "--format", "json"])
    if code != 0:
        return containers
    try:
        rows = json.loads(out)
    except json.JSONDecodeError:
        return containers
    for row in rows:
        names = row.get("Names") or []
        name = names[0] if isinstance(names, list) and names else str(names)
        if not name:
            continue
        published: list[dict] = []
        for port in row.get("Ports") or []:
            if isinstance(port, dict):
                published.append({
                    "host_ip": str(port.get("host_ip", "")),
                    "host_port": str(port.get("host_port", "")),
                    "container_port": str(port.get("container_port", "")),
                    "protocol": str(port.get("protocol", "tcp")),
                })
        containers[name] = {
            "name": name,
            "image": row.get("Image", ""),
            "state": row.get("State", ""),
            "status_text": row.get("Status", ""),
            "networks": row.get("Networks") or [],
            "published": published,
            "ip_by_network": {},
        }
    return containers


def fill_container_ips(containers: dict[str, dict]) -> None:
    """Fill IP-by-network for each observed container (one inspect call each)."""
    for name, record in containers.items():
        code, out = run(["podman", "inspect", "--format", "json", name])
        if code != 0:
            continue
        try:
            payload = json.loads(out)
        except json.JSONDecodeError:
            continue
        entry = payload[0] if isinstance(payload, list) and payload else payload
        if not isinstance(entry, dict):
            continue
        nets = (entry.get("NetworkSettings") or {}).get("Networks") or {}
        for net_name, net in nets.items():
            if isinstance(net, dict):
                record["ip_by_network"][net_name] = net.get("IPAddress", "")
        record["image_name"] = entry.get("ImageName", record["image"])
        record["health"] = "configured" if ((entry.get("Config") or {}).get("Healthcheck")) else ""


def live_networks() -> dict[str, dict]:
    networks: dict[str, dict] = {}
    code, out = run(["podman", "network", "ls", "--format", "json"])
    if code != 0:
        return networks
    try:
        rows = json.loads(out)
    except json.JSONDecodeError:
        return networks
    for row in rows:
        name = row.get("name", "")
        if not name:
            continue
        record = {
            "name": name,
            "driver": row.get("driver", ""),
            "id": (row.get("id") or "")[:12],
            "subnet": "",
            "gateway": "",
            "internal": None,
            "declared": False,
            "live": True,
        }
        code_i, out_i = run(["podman", "network", "inspect", name, "--format", "json"])
        if code_i == 0:
            try:
                payload = json.loads(out_i)
            except json.JSONDecodeError:
                payload = []
            entry = payload[0] if isinstance(payload, list) and payload else payload
            if isinstance(entry, dict):
                subnets = entry.get("subnets") or []
                if subnets and isinstance(subnets[0], dict):
                    record["subnet"] = subnets[0].get("subnet", "")
                    record["gateway"] = subnets[0].get("gateway", "")
                record["internal"] = entry.get("internal")
                record["dns_enabled"] = entry.get("dns_enabled")
        networks[name] = record
    return networks


def live_listeners() -> list[dict]:
    listeners: list[dict] = []
    code, out = run(["ss", "-lntup"])
    if code != 0:
        code, out = run(["ss", "-lntu"])
    if code != 0:
        return listeners
    for line in out.splitlines()[1:]:
        match = LISTEN_RE.match(line.strip())
        if not match:
            continue
        local = match.group("local")
        proto = match.group("proto")
        if ":" not in local:
            continue
        addr, _, port = local.rpartition(":")
        if "%" in addr:
            addr = addr.split("%", 1)[0]
        try:
            port_int = int(port)
        except ValueError:
            continue
        proc_name = ""
        pid = ""
        proc_match = PROC_NAME_RE.search(match.group("proc") or "")
        if proc_match:
            proc_name = proc_match.group("name")
            pid = proc_match.group("pid")
        if addr in ("127.0.0.1", "::1"):
            scope = "loopback"
        elif addr in ("0.0.0.0", "*", "::"):
            scope = "wildcard"
        else:
            scope = "interface"
        listeners.append({
            "proto": proto,
            "address": addr,
            "port": port_int,
            "scope": scope,
            "process": proc_name,
            "pid": pid,
            "host_noise": (port_int, proto) in HOST_NOISE_PORTS,
        })
    return sorted(listeners, key=lambda item: (item["port"], item["proto"]))


def live_units() -> dict[str, str]:
    units: dict[str, str] = {}
    code, out = run(["systemctl", "--user", "list-units", "--type=service", "--all",
                     "--plain", "--no-legend", "--no-pager"])
    if code != 0:
        return units
    for line in out.splitlines():
        parts = line.split(None, 4)
        if len(parts) >= 3 and parts[0].endswith(".service"):
            units[parts[0]] = parts[2]
    return units


def serial_devices() -> list[str]:
    directory = Path("/dev/serial/by-id")
    try:
        return sorted(item.name for item in directory.iterdir())
    except OSError:
        return []


def host_interfaces() -> list[dict]:
    interfaces: list[dict] = []
    code, out = run(["ip", "-brief", "address"])
    if code != 0:
        return interfaces
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 3:
            interfaces.append({"name": parts[0], "state": parts[1], "addresses": parts[2:]})
    return interfaces


# ---------------------------------------------------------------------------
# Inventory: merge declared + observed + documented claims
# ---------------------------------------------------------------------------

def build_inventory(model: dict, use_live: bool) -> dict:
    cidrs = read_network_cidrs()
    allowlist = read_listener_allowlist()
    declared_c = declared_containers()
    declared_n = declared_networks()
    declared_u = declared_units()

    containers_live: dict[str, dict] = live_containers() if use_live else {}
    if use_live:
        fill_container_ips(containers_live)
    networks_live = live_networks() if use_live else {}
    listeners = live_listeners() if use_live else []
    units = live_units() if use_live else {}
    serials = serial_devices() if use_live else []
    interfaces = host_interfaces() if use_live else []

    containers: list[dict] = []
    for unit, record in declared_c.items():
        name = record["container_name"]
        observed = containers_live.get(name)
        record["unit_state"] = units.get("%s.service" % unit, "")
        if observed:
            record["live"] = True
            record["state"] = observed["state"]
            record["status_text"] = observed["status_text"]
            record["ip_by_network"] = observed["ip_by_network"]
            record["published"] = observed["published"]
            record["networks_live"] = observed["networks"]
            record["health"] = observed.get("health", "")
            record["status"] = "implemented" if observed["state"] == "running" else "declared"
        else:
            record["status"] = "declared"
        containers.append(record)

    declared_names = {record["container_name"] for record in declared_c.values()}
    for name, observed in containers_live.items():
        if name in declared_names:
            continue
        containers.append(undeclared_record(name, observed, units))

    model_networks = model.get("networks") or {}
    networks: list[dict] = []
    for name in sorted(set(declared_n) | set(networks_live) | set(model_networks)):
        networks.append(network_record(name, declared_n, networks_live, model_networks,
                                       cidrs, containers))

    drift = evaluate_drift(model, networks, containers, listeners, allowlist, networks_live)
    inventory = {
        "generated_at_utc": utc_now(),
        "authority": model.get("authority", "/ALWAYSON/README.md"),
        "model_revision": model.get("revision", ""),
        "declared_source": str(QUADLET_DIR),
        "observed": use_live,
        "host": dict(model.get("host") or {}, live_interfaces=interfaces),
        "databases": model.get("databases") or [],
        "authority_short": model.get("authority_short", ""),
        "supersedes": model.get("supersedes", ""),
        "host_services": model.get("host_services") or [],
        "desktop_software": model.get("desktop_software") or [],
        "field": model.get("field") or {},
        "edge": model.get("edge") or {},
        "planned_components": model.get("planned_components") or [],
        "networks": networks,
        "containers": sorted(containers, key=lambda item: (item["category"], item["container_name"])),
        "declared_units": declared_u,
        "listeners": listeners,
        "serial_devices": serials,
        "listener_allowlist": sorted(allowlist),
        "drift": drift,
        "counts": counts_for(networks, containers, listeners, declared_n, declared_c, model),
    }
    inventory["counts"]["drift_items"] = sum(1 for item in drift if item["status"] == "drift")
    return inventory


def undeclared_record(name: str, observed: dict, units: dict[str, str]) -> dict:
    image_name, image_version = short_image(observed["image"])
    return {
        "unit": "",
        "file": "",
        "category": "undeclared",
        "container_name": name,
        "description": "Running container with no matching /ALWAYSON/quadlet definition",
        "image": observed["image"],
        "image_name": image_name,
        "image_version": image_version,
        "networks": observed["networks"],
        "publish": [],
        "volumes": [],
        "environment": [],
        "env_files": 0,
        "no_new_privileges": "unknown",
        "health_cmd": "",
        "memory_max": "",
        "cpu_quota": "",
        "wanted_by": [],
        "declared": False,
        "live": True,
        "status": "implemented" if observed["state"] == "running" else "unknown",
        "state": observed["state"],
        "status_text": observed["status_text"],
        "ip_by_network": observed["ip_by_network"],
        "published": observed["published"],
        "networks_live": observed["networks"],
        "unit_state": units.get("container-%s.service" % name, ""),
    }


def network_record(name: str, declared_n: dict, networks_live: dict, model_networks: dict,
                   cidrs: dict, containers: list[dict]) -> dict:
    declared = declared_n.get(name, {})
    observed = networks_live.get(name, {})
    spec = model_networks.get(name) or {}
    members = [record["container_name"] for record in containers
               if name in (record.get("networks") or [])
               or name in (record.get("networks_live") or [])]
    if observed:
        status = spec.get("status") or ("implemented" if members else "declared")
    else:
        status = spec.get("status") or "planned"
    internal = (observed.get("internal") if observed.get("internal") is not None
                else declared.get("internal"))
    # Podman always pre-creates a default network named "podman"; it carries no
    # Quadlet definition and is not an ALWAYS ON workload domain, so it is
    # recorded but excluded from the workload count and the diagram.
    podman_default = (name == "podman" and not declared and not spec)
    return {
        "name": name,
        "subnet": observed.get("subnet") or cidrs.get(name, ""),
        "gateway": observed.get("gateway", ""),
        "internal": internal,
        "declared": name in declared_n,
        "live": name in networks_live,
        "purpose": spec.get("purpose", ""),
        "status": status,
        "note": spec.get("note", ""),
        "adapter": bool(spec.get("adapter", False)),
        "includes": spec.get("includes", []),
        "members": members,
        "cidr_registry": cidrs.get(name, ""),
        "podman_default": podman_default,
    }


def counts_for(networks, containers, listeners, declared_n, declared_c, model) -> dict:
    return {
        "networks_declared": len(declared_n),
        "networks_total": sum(1 for item in networks if not item["podman_default"]),
        "networks_live": sum(1 for item in networks if item["live"] and not item["podman_default"]),
        "containers_declared": len(declared_c),
        "containers_live": sum(1 for item in containers if item["live"]),
        "containers_running": sum(1 for item in containers if item["state"] == "running"),
        "listeners": len(listeners),
        "loopback_listeners": sum(1 for item in listeners if item["scope"] == "loopback"),
        "non_loopback_listeners": sum(1 for item in listeners
                                      if item["scope"] != "loopback" and not item["host_noise"]),
        "host_services": len(model.get("host_services") or []),
        "desktop_software": len(model.get("desktop_software") or []),
        "databases": len(model.get("databases") or []),
        "databases_authoritative": sum(1 for item in (model.get("databases") or [])
                                       if str(item.get("authority", "")).startswith("authoritative")),
        "databases_relational": sum(1 for item in (model.get("databases") or [])
                                    if item.get("kind") in ("postgresql", "postgis")),
        "drift_items": 0,
    }


# ---------------------------------------------------------------------------
# Drift: documented claim vs observed state
# ---------------------------------------------------------------------------

def drift_item(item_id: str, claim: str, expected: str, observed: str,
               severity: str, matched: bool) -> dict:
    return {
        "id": item_id,
        "claim": claim,
        "expected": expected,
        "observed": observed,
        "severity": severity,
        "status": "match" if matched else "drift",
    }


def evaluate_drift(model: dict, networks: list[dict], containers: list[dict],
                   listeners: list[dict], allowlist: set[int],
                   networks_live: dict) -> list[dict]:
    if not listeners and not networks_live:
        return [drift_item("live-probe-unavailable",
                           "Declared-only run (--no-live)",
                           "live probes executed",
                           "no live inspection performed", "info", True)]

    workload = [item for item in networks if not item["adapter"] and not item["podman_default"]]
    live_workload = [item for item in workload if item["live"]]
    network_count = len(live_workload)
    results = [drift_item(
        "net-count",
        "v6 2.2/3.2: 'Ten ao-* networks present'",
        "10 live workload networks",
        "%d live workload networks (%s)" % (
            network_count, ", ".join(item["name"] for item in live_workload) or "none"),
        "attention" if network_count != 10 else "info",
        network_count == 10,
    )]

    names = {item["container_name"] for item in containers if item["live"]}
    mastodon_db = "mastodon-db" in names
    results.append(drift_item(
        "mastodon-db-placement",
        "v6 3.3: mastodon state consolidated onto Host PostgreSQL 18.6",
        "no mastodon-db container; mastodon uses host PG 18 database 'mastodon'",
        "mastodon-db container running on ao-sales - container-scoped PostgreSQL"
        if mastodon_db else "no mastodon-db container observed; host PG placement holds",
        "attention" if mastodon_db else "info",
        not mastodon_db,
    ))

    webodm_db = "db" in names or "webodm-db" in names
    results.append(drift_item(
        "webodm-db-placement",
        "v6 3.3: WebODM backing data consolidated onto Host PG 18 (webodm/PostGIS 3.6.2)",
        "no WebODM database container; webapp/worker use host PG 18",
        "running WebODM database container observed" if webodm_db
        else "no WebODM database container running; quadlet still declares ao-webodm-db (container-scoped DB)",
        "attention" if webodm_db else "info",
        not webodm_db,
    ))

    corda = [name for name in names if "corda" in name.lower()]
    results.append(drift_item(
        "corda-persistence",
        "v6 ES.1/3.3/18.2: Corda 5.2.2 persists in PostgreSQL 'cordadb'; the Corda 4.14.2 H2 scaffold was retired 2026-09-28",
        "no running Corda containers; cordadb is the documented persistence target",
        "no running Corda containers (matches the blocked state; Corda 4 H2 scaffold retired 2026-09-28)"
        if not corda else "Corda containers running: %s" % ", ".join(corda),
        "info" if not corda else "mismatch",
        not corda,
    ))

    external = [item["name"] for item in networks
                if item["live"] and item["internal"] is False and not item["adapter"]
                and not item["podman_default"]]
    results.append(drift_item(
        "workload-internal",
        "v6 5.1: all workload-domain networks are Internal=true",
        "every workload network reports Internal=true",
        "workload networks with Internal=false: %s" % ", ".join(external) if external
        else "all live workload networks are Internal=true",
        "mismatch" if external else "info",
        not external,
    ))

    exposed = [item for item in listeners if item["scope"] != "loopback" and not item["host_noise"]
               and item["port"] not in allowlist]
    exposed_text = ", ".join("%s:%d/%s (%s)" % (item["address"] or "0.0.0.0", item["port"],
                                                item["proto"], item["process"] or "unknown")
                             for item in exposed) or "none"
    results.append(drift_item(
        "non-loopback-listeners",
        "README 4.1 rule 6 + listener-allowlist.yaml (listeners: []) - no public ports without approval",
        "no unapproved non-loopback listener",
        exposed_text,
        "attention" if exposed else "info",
        not exposed,
    ))
    return results


# ---------------------------------------------------------------------------
# Rendering: Graphviz DOT
# ---------------------------------------------------------------------------
STATUS_TINT = {
    "implemented": "#e8f5e9",
    "partial": "#fff8e1",
    "in_progress": "#fff3e0",
    "planned": "#eceff1",
    "blocked": "#ffebee",
    "declared": "#eceff1",
    "unknown": "#f5f5f5",
}


def dot_escape(text: str) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def dot_wrap(text: str, width: int = 46) -> list[str]:
    """Wrap a label line so nodes stay a readable width.

    Long role/description strings otherwise make single nodes hundreds of
    characters wide, which forces the whole layout to sprawl.
    """
    import textwrap
    words = str(text).split()
    if not words:
        return [""]
    return textwrap.wrap(" ".join(words), width=width) or [""]


def dot_wrapped(text: str, font: str = "", color: str = "", size: int = 9,
                width: int = 46) -> str:
    """Return one or more <font>-wrapped DOT lines for a text value."""
    if not text:
        return ""
    out: list[str] = []
    for line in dot_wrap(text, width):
        if font or color or size != 9:
            attrs = []
            if font:
                attrs.append("point-size='%d'" % size)
            if color:
                attrs.append("color='%s'" % color)
            if font:
                attrs.insert(0, font)
            out.append("<font %s>%s</font>" % (" ".join(attrs), dot_escape(line)))
        else:
            out.append(dot_escape(line))
    return "<br/>".join(out)


def dot_id(text: str) -> str:
    return "n_" + re.sub(r"[^0-9A-Za-z_]", "_", str(text))


def status_attrs(status: str, live: bool = True, declared: bool = True) -> str:
    fill = STATUS_TINT.get(status, "#f5f5f5")
    border = STATUS_FILL.get(status, "#616161")
    style = "rounded,filled"
    if not live:
        style = "rounded,filled,dashed"
    if not declared:
        style = "rounded,filled,bold"
        border = "#00695c"
    return 'style="%s", fillcolor="%s", color="%s"' % (style, fill, border)


def emitted_ids(inv: dict) -> set[str]:
    """Every node id that render_dot emits (used to guard edge creation)."""
    ids = {"host", "operator", "legend", "internet", "adapter-placeholders", "drift", "provenance"}
    edge_spec = inv.get("edge") or {}
    ids.add((edge_spec.get("internet") or {}).get("id", "internet"))
    ids |= {path["id"] for path in edge_spec.get("paths") or []}
    field = inv.get("field") or {}
    ids |= {item["id"] for item in field.get("drone_side") or []}
    ids |= {item["id"] for item in field.get("radios") or []}
    ids |= {item["id"] for item in inv.get("host_services") or []}
    ids |= {item["id"] for item in inv.get("desktop_software") or []}
    ids |= {item["container_name"] for item in inv.get("containers") or []}
    ids |= {item["id"] for item in inv.get("planned_components") or []}
    ids |= {"%s_placeholder" % net["name"] for net in inv.get("networks") or []
            if not net["members"]}
    return ids


def container_node_decl(record: dict, network: str) -> str:
    """Full DOT node statement for a container: software, image, IP, ports, state."""
    name = record["container_name"]
    label = ["<b>%s</b>" % dot_escape(name)]
    image = record.get("image_name") or ""
    version = record.get("image_version") or ""
    if image:
        label.append(dot_escape(("%s %s" % (image, version)).strip()))
    if record.get("description") and not record.get("declared"):
        label.append("<font point-size='9' color='#004d40'>%s</font>"
                     % dot_escape("no Quadlet definition"))
    attachments = []
    for net_name, ip in sorted((record.get("ip_by_network") or {}).items()):
        attachments.append("%s · %s" % (net_name, ip or "no IP"))
    if not attachments:
        for net_name in record.get("networks") or []:
            attachments.append("%s · not attached" % net_name)
    for item in attachments:
        label.append("<font color='#37474f'>%s</font>" % dot_escape(item))
    published = record.get("published") or []
    if published:
        for port in published:
            label.append("<font color='#1565c0'>%s</font>"
                         % dot_escape("%s:%s -> %s/%s" % (port.get("host_ip") or "0.0.0.0",
                                                          port.get("host_port"),
                                                          port.get("container_port"),
                                                          port.get("protocol"))))
    else:
        for port in record.get("publish") or []:
            label.append("<font color='#1565c0'>publish %s</font>" % dot_escape(port))
    if not published and not record.get("publish"):
        label.append("<font point-size='9' color='#607d8b'>internal only (no published port)</font>")
    if record.get("state") and record["state"] != "running":
        label.append("<i>state: %s</i>" % dot_escape(record["state"]))
    elif record.get("status_text"):
        label.append("<i>%s</i>" % dot_escape(record["status_text"]))
    else:
        label.append("<i>declared — not running</i>")
    if record.get("unit_state"):
        label.append("<font point-size='8' color='#6a1b9a'>unit %s</font>"
                     % dot_escape(record["unit_state"]))
    attrs = status_attrs(record.get("status", "unknown"), record.get("live", False),
                         record.get("declared", True))
    return "%s [%s, label=<%s>]" % (dot_id(name), attrs, "<br/>".join(label))


VIEWS: dict[str, dict] = {
    "overview": {
        "slug": "overview",
        "title": "ALWAYS ON — TOPOLOGY OVERVIEW",
        "subtitle": "networks · data stores · external paths · status",
        "sections": ("edge", "netsum", "datastore", "planned", "legend"), "notes": True,
        "rankdir": "LR", "ranksep": 0.8,
    },
    "networks": {
        "slug": "workload-networks",
        "title": "ALWAYS ON — WORKLOAD NETWORKS & CONTAINERS",
        "subtitle": "Podman networks · CIDRs · container IPs · published ports · status",
        "sections": ("host", "networks", "legend"), "notes": True,
        "rankdir": "LR", "ranksep": 0.8,
    },
    "hostsw": {
        "slug": "host-software",
        "title": "ALWAYS ON — HOST SOFTWARE & OPERATOR ACCESS",
        "subtitle": "systemd services · desktop software · loopback-only operator access",
        "sections": ("host", "hostsw", "operator", "legend"), "notes": False,
        "rankdir": "LR", "ranksep": 0.8,
    },
    "field": {
        "slug": "field-and-edge",
        "title": "ALWAYS ON — FIELD, RADIO & CONTROLLED EXTERNAL PATHS",
        "subtitle": "drone link · radios · controlled ingress/egress · external services",
        "sections": ("host", "edge", "field", "legend"), "notes": False,
        "rankdir": "LR", "ranksep": 0.8,
    },
}


def render_dot(inv: dict, view: str = "system") -> str:
    spec = VIEWS.get(view) or {
        "slug": "system", "title": "ALWAYS ON — SYSTEM TOPOLOGY",
        "subtitle": "Podman networks · CIDRs · container IPs · published ports",
        "sections": ("host", "edge", "field", "hostsw", "datastore", "operator",
                     "networks", "orphan", "planned", "legend"), "notes": True,
        "rankdir": "LR", "ranksep": 1.1,
    }
    want = set(spec["sections"])
    lines: list[str] = []
    _sink = lines.append
    # Section gate.  Rather than reindenting every block under an `if`, the
    # output sink is switched to a no-op, so including or dropping a section
    # costs one line and leaves the existing block structure untouched.
    gate = [True]

    def add(*parts: str) -> None:
        if gate[0]:
            _sink(*parts)
    counts = inv["counts"]
    stamp = inv["generated_at_utc"]
    observed = "live inspection" if inv["observed"] else "declared definitions only (--no-live)"
    add("digraph alwayson {")
    add('  graph [rankdir=%s, compound=true, newrank=true, concentrate=true, fontname="DejaVu Sans", fontsize=11,'
        ' bgcolor="#ffffff", nodesep=0.45, ranksep=%s, splines=spline, pad=0.3,'
        ' labelloc=t, fontsize=24,'
        ' label=<<b>%s</b><br/>'
        '<font point-size="11">%s'
        ' · generated %s (%s)</font><br/>'
        '<font point-size="10">%d networks · %d containers (%d running) · %d listeners (%d loopback)'
        ' · %d drift items — authority: v6 §3.3.1/§5.1/§5.2/§6.A/§20.0</font>>];'
        % (spec.get("rankdir", "LR"), spec.get("ranksep", 1.1),
           dot_escape(spec["title"]), dot_escape(spec["subtitle"]), stamp, observed,
           counts["networks_total"], counts["containers_declared"],
           counts["containers_running"], counts["listeners"], counts["loopback_listeners"],
           counts["drift_items"]))
    add('  node [shape=box, style="rounded,filled", fontname="DejaVu Sans", fontsize=10,'
        ' margin="0.14,0.09", penwidth=1.4];')
    add('  edge [fontname="DejaVu Sans", fontsize=9, color="#607d8b", penwidth=1.1, arrowsize=0.7];')

    gate[0] = "host" in want
    host = inv["host"]
    host_label = ["<b>%s</b>" % dot_escape(host.get("label", "HOST"))]
    host_label.append(dot_escape(host.get("software", "")))
    host_label.append("kernel %s · %s" % (dot_escape(host.get("kernel", "")),
                                          dot_escape(host.get("cpu", ""))))
    host_label.append(dot_escape(host.get("gpu", "")))
    host_label.append("<i>%s</i>" % dot_escape(host.get("container_runtime", "")))
    interfaces = host.get("live_interfaces") or []
    if interfaces:
        for entry in interfaces:
            if entry["name"] == "lo":
                continue
            addrs = " ".join(entry["addresses"][:2])
            host_label.append("%s: %s" % (dot_escape(entry["name"]), dot_escape(addrs)))
    add('  %s [shape=box3d, fillcolor="#e3f2fd", color="#0d47a1", fontsize=12,'
        ' label=<%s>];' % (dot_id("host"), "<br/>".join(host_label)))
    add("")

    gate[0] = "edge" in want
    # ---- controlled external paths -------------------------------------
    edge_spec = inv.get("edge") or {}
    add('  subgraph cluster_edge {')
    add('    label=<<b>CONTROLLED EXTERNAL PATHS</b> <font point-size="9">(README §5.2)</font>>;'
        ' style="rounded,filled"; fillcolor="#f3f7fb"; color="#1565c0"; fontsize=12;')
    internet = edge_spec.get("internet") or {"id": "internet", "label": "PUBLIC INTERNET"}
    add('    %s [shape=ellipse, fillcolor="#cfd8dc", color="#37474f", fontsize=12, label="%s"];'
        % (dot_id(internet.get("id", "internet")), dot_escape(internet.get("label", "INTERNET"))))
    for path in edge_spec.get("paths") or []:
        label = ["<b>%s</b>" % dot_escape(path.get("label", ""))]
        if path.get("software"):
            label.append(dot_escape(path["software"]))
        for listen in path.get("listens") or []:
            label.append("listen %s" % dot_escape(listen))
        for publish in path.get("publishes") or []:
            label.append(dot_escape(publish))
        if path.get("direction"):
            label.append("<i>direction: %s</i>" % dot_escape(path["direction"]))
        if not path.get("status", "").endswith("implemented"):
            label.append("status: %s" % dot_escape(path.get("status", "")))
        add('    %s [%s, label=<%s>];' % (dot_id(path["id"]), status_attrs(path.get("status", "")),
                                          "<br/>".join(label)))
    add('    %s [shape=box, style="rounded,dashed", fillcolor="#eceff1", color="#455a64",'
        ' label="ao-ingress-payment\\nao-egress-archive\\nao-build-update\\n(adapters, not deployed)"];'
        % dot_id("adapter-placeholders"))
    add("  }")
    add("")

    gate[0] = "field" in want
    # ---- field / radio sub-system --------------------------------------
    field = inv.get("field") or {}
    add('  subgraph cluster_field {')
    add('    label=<<b>FIELD, RADIO &amp; DRONE LINK</b> <font point-size="9">(README §9)</font>>;'
        ' style="rounded,filled"; fillcolor="#fffde7"; color="#f9a825"; fontsize=12;')
    for node in field.get("drone_side") or []:
        label = ["<b>%s</b>" % dot_escape(node.get("label", "")), dot_escape(node.get("software", ""))]
        if node.get("hardware"):
            label.append(dot_escape(node["hardware"]))
        add('    %s [%s, label=<%s>];' % (dot_id(node["id"]), status_attrs(node.get("status", "")),
                                          "<br/>".join(label)))
    for radio in field.get("radios") or []:
        label = ["<b>%s</b>" % dot_escape(radio.get("label", "")), dot_escape(radio.get("software", "")),
                 "<font color='#6d4c41'>%s</font>" % dot_escape(radio.get("rf", "")),
                 dot_escape(radio.get("hardware", ""))]
        add('    %s [%s, label=<%s>];' % (dot_id(radio["id"]), status_attrs(radio.get("status", "")),
                                          "<br/>".join(label)))
    add("  }")
    add("")

    gate[0] = "hostsw" in want
    # ---- host software (services + desktop) ----------------------------
    add('  subgraph cluster_hostsw {')
    add('    label=<<b>HOST SOFTWARE (non-container)</b> <font point-size="9">(v6 §3.3, §9.2, §20.0)</font>>;'
        ' style="rounded,filled"; fillcolor="#f1f8e9"; color="#33691e"; fontsize=12;')
    for service in inv.get("host_services") or []:
        label = ["<b>%s</b>" % dot_escape(service.get("label", "")),
                 dot_escape(service.get("software", ""))]
        for listen in service.get("listens") or []:
            label.append("<font color='#1565c0'>listen %s</font>" % dot_escape(listen))
        for relay in service.get("relays") or []:
            label.append("<font color='#1565c0'>relay %s</font>" % dot_escape(relay))
        if service.get("data"):
            label.append(dot_wrapped(service["data"], size=8, width=52))
        if service.get("note"):
            label.append(dot_wrapped(service["note"], color="#6d4c41", size=8, width=52))
        add('    %s [%s, label=<%s>];' % (dot_id(service["id"]), status_attrs(service.get("status", "")),
                                          "<br/>".join(label)))
    for app in inv.get("desktop_software") or []:
        label = ["<b>%s</b>" % dot_escape(app.get("label", "")), dot_escape(app.get("software", ""))]
        for listen in app.get("listens") or []:
            label.append("<font color='#1565c0'>listen %s</font>" % dot_escape(listen))
        for target in app.get("connects") or []:
            label.append("connects %s" % dot_escape(target))
        for env in app.get("env") or []:
            label.append("<i>%s</i>" % dot_escape(env))
        add('    %s [%s, label=<%s>];' % (dot_id(app["id"]), status_attrs(app.get("status", "")),
                                          "<br/>".join(label)))
    add("  }")
    add("")

    gate[0] = "datastore" in want
    # ---- data stores (summary pointer; full registry is a separate diagram) --
    databases = inv.get("databases") or []
    if databases:
        relational = [item for item in databases if item.get("kind") in ("postgresql", "postgis")]
        others = [item for item in databases if item.get("kind") not in ("postgresql", "postgis")]
        add('  %s [shape=box3d, fillcolor="#e8eaf6", color="#283593", fontsize=11,'
            ' label=<<b>DATA STORES</b><br/>'
            '<font point-size="9">%d databases &amp; data stores (v6 §3.3.1)</font><br/>'
            '<font point-size="9" color="#283593">%d relational (PostgreSQL 18 / PostGIS)</font><br/>'
            '<font point-size="9" color="#455a64">%d non-relational (Redis, Prometheus TSDB, SQLite, '
            'filesystem, H2 legacy)</font><br/>'
            '<font point-size="8">full registry: alwayson-databases.svg</font>>];'
            % (dot_id("datastore-summary"), len(databases), len(relational), len(others)))
        add("")

    gate[0] = "operator" in want
    # ---- operator access ------------------------------------------------
    loops = [item for item in inv["listeners"] if item["scope"] == "loopback" and not item["host_noise"]]
    operator_label = ["<b>OPERATOR ACCESS (loopback only)</b>",
                      "Konqueror / QGroundControl / DBeaver / Podman Desktop",
                      "no public port; listener-allowlist is empty"]
    for item in loops:
        operator_label.append("%s:%d/%s %s" % (item["address"], item["port"], item["proto"],
                                               dot_escape(item["process"] or "")))
    # Keep the operator node short: it is a legend, not an inventory (the full
    # listener table lives in the HTML/Markdown companions).  Without a cap the
    # stacked list forces an enormous empty column in the layout.
    operator_label = operator_label[:3] + operator_label[3:9]
    if len(loops) > 9:
        operator_label.append("+%d more loopback listeners — see listener table" % (len(loops) - 9))
    add('  %s [shape=box, fillcolor="#f3e5f5", color="#6a1b9a", fontsize=10,'
        ' label=<%s>];' % (dot_id("operator"), "<br/>".join(operator_label)))
    add("")

    gate[0] = "netsum" in want
    # Compact per-network summary for the overview sheet: one box per network
    # carrying its CIDR/internal flag and a member count, instead of the full
    # container nodes.  The per-container detail lives in the "networks" view.
    if "netsum" in want:
        live_nets = [n for n in inv["networks"] if not n["podman_default"]]
        for network in sorted(live_nets, key=lambda item: (item["adapter"], item["name"])):
            nm = network["name"]
            internal = {True: "Internal=true", False: "Internal=false",
                        None: "Internal=?"}[network["internal"]]
            state = "live" if network["live"] else "not created"
            body = [
                "<b>%s</b>" % dot_escape(nm),
                "<font point-size='9'>%s</font>" % dot_escape(network["subnet"] or "CIDR not registered"),
                "<font point-size='9'>%s &middot; %s</font>" % (internal, state),
                "<font point-size='9'>%s</font>" % dot_escape(network["status"]),
                "<font point-size='9'>%d container(s)</font>" % len(network["members"]),
            ]
            lines.append(
                '  %s [shape=box, fillcolor="%s", color="%s", label=<%s>];'
                % (dot_id(nm),
                   "#f9fbe7" if network["adapter"] else "#ffffff",
                   "#00695c" if network["adapter"] else "#1565c0",
                   "<br/>".join(body)))
        gate[0] = True

    gate[0] = "networks" in want
    # ---- podman networks ------------------------------------------------
    network_names = {item["name"] for item in inv["networks"]}
    adapter_names = {item["name"] for item in inv["networks"] if item["adapter"]}
    primary: dict[str, str] = {}
    for record in inv["containers"]:
        candidates = [name for name in (record.get("networks") or []) if name in network_names]
        if not candidates:
            continue
        workload = [name for name in candidates if name not in adapter_names]
        primary[record["container_name"]] = (workload or candidates)[0]

    node_defined: set[str] = set()
    representative: dict[str, str] = {}
    for network in sorted(inv["networks"], key=lambda item: (item["adapter"], item["name"])):
        if network["podman_default"]:
            continue
        members = [record for record in inv["containers"]
                   if record["container_name"] in network["members"]]
        cluster = "cluster_net_%s" % dot_id(network["name"])
        border = "#00695c" if network["adapter"] else "#1565c0"
        fill = "#f9fbe7" if network["adapter"] else "#ffffff"
        state = "live" if network["live"] else "not created"
        internal = {True: "Internal=true", False: "Internal=false", None: "Internal=?"}[network["internal"]]
        label = ["<b>%s</b> — %s" % (dot_escape(network["name"]),
                                     dot_escape(network["subnet"] or "CIDR not registered"))]
        label.append("%s · gw %s · %s" % (internal,
                                          dot_escape(network["gateway"] or "?"), state))
        if network["purpose"]:
            label.append(dot_wrapped(network["purpose"], size=9, width=54))
        if network["members"]:
            label.append("<font point-size='9' color='#37474f'>%s</font>"
                         % dot_escape(" · ".join(network["members"])))
        add("  subgraph %s {" % cluster)
        add("    label=<%s>; style=\"rounded,filled\"; fillcolor=\"%s\"; color=\"%s\";"
            " fontsize=12;" % ("<br/>".join(label), fill, border))
        if not members:
            add('    %s [shape=box, style="rounded,dashed", fillcolor="#fafafa", color="#9e9e9e",'
                ' label="%s\\n(status: %s)"];'
                % (dot_id(network["name"] + "_placeholder"),
                   "%s — no runtime yet" % dot_escape(network["purpose"] or network["name"]),
                   dot_escape(network["status"])))
        for record in members:
            name = record["container_name"]
            if primary.get(name) != network["name"] or name in node_defined:
                continue
            node_defined.add(name)
            representative.setdefault(network["name"], name)
            add("    %s;" % container_node_decl(record, network["name"]))
        add("  }")
        add("")

    orphans = [record for record in inv["containers"]
               if record["container_name"] not in node_defined]
    if orphans:
        add("  subgraph cluster_orphan {")
        add("    label=< <b>CONTAINERS WITHOUT A DECLARED NETWORK</b> >; style=\"rounded,filled\";"
            " fillcolor=\"#efebe9\"; color=\"#4e342e\"; fontsize=12;")
        for record in orphans:
            add("    %s;" % container_node_decl(record, ""))
        add("  }")
        add("")

    if inv.get("planned_components"):
        add("  subgraph cluster_planned {")
        add("    label=< <b>PLANNED &amp; BLOCKED DOMAINS</b>"
            " <font point-size='9'>(README §4.4, §11, §18)</font> >; style=\"rounded,filled\";"
            " fillcolor=\"#fafafa\"; color=\"#616161\"; fontsize=12;")
        for item in inv["planned_components"]:
            label = ["<b>%s</b>" % dot_escape(item.get("label", "")),
                     dot_escape(item.get("software", "")), dot_escape(item.get("note", ""))]
            add('    %s [%s, label=<%s>];' % (dot_id(item["id"]), status_attrs(item.get("status", "")),
                                              "<br/>".join(part for part in label if part)))
        add("  }")
        add("")

    legend_lines = ["<b>STATUS LEGEND</b>"]
    for status in ("implemented", "partial", "in_progress", "planned", "blocked", "declared"):
        legend_lines.append("<font color='%s'>■</font> %s" % (STATUS_FILL[status], status))
    legend_lines.append("<i>dashed border</i> = declared but not running / not created")
    legend_lines.append("<b>bold teal border</b> = running without a Quadlet definition")
    legend_lines.append("<i>blue text</i> = listener or relay endpoint (host:port)")
    add('  %s [shape=box, fillcolor="#ffffff", color="#424242", fontsize=10,'
        ' label=<%s>];' % (dot_id("legend"), "<br/>".join(legend_lines)))
    add("")

    gate[0] = "edges" in want
    # ---- edges -----------------------------------------------------------
    defined = emitted_ids(inv)

    def edge(src: str, dst: str, label: str = "", style: str = "solid",
             color: str = "#607d8b") -> None:
        if src not in defined or dst not in defined or src == dst:
            return
        attrs = ['color="%s"' % color, 'style="%s"' % style]
        if label:
            attrs.append('label="%s"' % label)
        add("  %s -> %s [%s];" % (dot_id(src), dot_id(dst), ", ".join(attrs)))

    for network in inv["networks"]:
        rep = representative.get(network["name"])
        if rep and network["live"]:
            edge("host", rep, "bridge %s" % (network["gateway"] or network["subnet"] or ""),
                 style="dashed", color="#90a4ae")
    edge("host", "host-postgresql", "systemd", style="dashed", color="#a5d6a7")
    # Databases owned by the host cluster get an explicit ownership edge so the
    # logical-database boundary is visible, not just implied by the cluster.
    db_ids = {dot_id(entry["id"]) for entry in inv.get("databases") or []}
    for entry in inv.get("databases") or []:
        parent = entry.get("parent")
        if not parent or entry.get("placement") != "host":
            continue
        if dot_id(parent) in db_ids:
            edge(parent, entry["id"], "logical database", style="dashed", color="#9fa8da")
    edge("host", "host-redis", "systemd", style="dashed", color="#a5d6a7")
    edge("host", "host-ardupilot-sitl", "systemd", style="dashed", color="#a5d6a7")
    edge("desktop-openclaw", "desktop-lmstudio", "OpenAI API 127.0.0.1:1234")
    edge("desktop-tokodon", "desktop-meshchatx", "local UI :18000")
    edge("desktop-tokodon", "host", "loopback UIs :3000/:3001/:3002/:8000")
    edge("desktop-meshchatx", "desktop-reticulum", "embedded RNS")
    edge("desktop-reticulum", "radio-people", "LoRa 915 MHz / 125 kHz")
    edge("desktop-reticulum", "radio-drone", "LoRa 917 MHz / 250 kHz")
    edge("desktop-reticulum", "edge-reticulum-tcp", "RNS peers / 0.0.0.0:4242")
    edge("desktop-qgc", "radio-drone", "MAVLink radio tunnel")
    edge("desktop-qgc", "host-ardupilot-sitl", "tcp 127.0.0.1:5760")
    edge("internet", "edge-cloudflare-tunnel", "TLS")
    edge("edge-cloudflare-tunnel", "mastodon-web", "300x3.com -> 127.0.0.1:3000")
    edge("edge-cloudflare-tunnel", "desktop-openclaw", "chat.300x3.com -> 127.0.0.1:18790")
    edge("internet", "edge-pcloud-storefront", "static HTML")
    edge("internet", "edge-ao-build-update", "images / packages")
    edge("edge-ao-ingress-payment", "internet", "webhooks (planned)",
         style="dashed", color="#b71c1c")
    edge("edge-ao-egress-archive", "internet", "encrypted archive (planned)",
         style="dashed", color="#b71c1c")
    edge("ao-grafana", "host-postgresql", "socket /var/run/postgresql")
    edge("ao-metabase", "host-postgresql", "10.42.0.1:5432 relay")
    edge("ao-grafana", "ao-prometheus", "query :9090")
    edge("ao-prometheus", "ao-node-exporter", "scrape :9100")
    edge("host-postgresql", "host-redis", "reporting hub + source DBs",
         style="dashed", color="#7e57c2")
    if "webapp" in defined:
        edge("webapp", "host-postgresql", "webodm DB (host PG 18 + PostGIS)")
        edge("worker", "broker", "Celery broker :6379")
        edge("nodeodm", "webapp", "NodeODM :3000")
    if "mastodon-db" in defined:
        edge("mastodon-db", "mastodon-web", "mastodon DB (container PG)")
        edge("mastodon-redis", "mastodon-web", "Redis :6379")
        edge("mastodon-redis", "mastodon-sidekiq", "Redis :6379")
        edge("mastodon-web", "mastodon-streaming", ":4000 streaming")
    if "sales-db" in defined:
        edge("sales-db", "host-postgresql", "salesdb reporting views (fdw)",
             style="dashed", color="#7e57c2")
    edge("internet", "adapter-placeholders", "controlled adapters only",
         style="dashed", color="#b71c1c")
    edge("sales-api", "corda-ingest", "signed manifest (planned)",
         style="dashed", color="#b71c1c")
    edge("corda-ingest", "corda-core", "mTLS (planned)", style="dashed", color="#b71c1c")
    edge("corda-ingest", "host-postgresql", "cordadb projection (staged)",
         style="dashed", color="#b71c1c")
    edge("operator", "host", "SSH / local session", style="dotted", color="#6a1b9a")
    edge("legend", "operator", "status reference", style="invis")

    gate[0] = "notes" in want
    # ---- generated notes -------------------------------------------------
    drift_lines = ["<b>DOCUMENTED CLAIM vs OBSERVED STATE</b>"]
    for item in inv["drift"]:
        mark = "<font color='#2e7d32'>match</font>" if item["status"] == "match" \
            else "<font color='#c62828'>drift</font>"
        drift_lines.append("%s — %s" % (mark, dot_escape(item["claim"])))
        drift_lines.append("<font point-size='9' color='#37474f'>obs: %s</font>"
                           % dot_escape(item["observed"]))
    add('  %s [shape=note, fillcolor="#fff8e1", color="#f9a825", fontsize=10,'
        ' label=<%s>];' % (dot_id("drift"), "<br/>".join(drift_lines)))
    add('  %s [shape=plaintext, fontsize=8, fontcolor="#616161",'
        ' label="generated by /ALWAYSON/scripts/operations/generate-topology.py\\n'
        'sources: /ALWAYSON/README.md, /ALWAYSON/quadlet/, /ALWAYSON/config/platform/\\n'
        'no secret material is included in this diagram"];' % dot_id("provenance"))
    gate[0] = True
    add("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Rendering: Graphviz DOT - database registry (v6 3.3 / 3.3.1)
# ---------------------------------------------------------------------------

AUTHORITY_STYLE = {
    "authoritative_relational": ("#c8e6c9", "#1b5e20", "AUTHORITATIVE RELATIONAL"),
    "authoritative_ledger": ("#fff9c4", "#f57f17", "AUTHORITATIVE LEDGER"),
    "current_migration_state": ("#ffe0b2", "#e65100", "CURRENT MIGRATION STATE"),
    "target": ("#e1bee7", "#6a1b9a", "TARGET"),
    "blocked": ("#ffcdd2", "#b71c1c", "BLOCKED"),
    "not_authoritative": ("#eceff1", "#546e7a", "NOT AUTHORITATIVE"),
    "not_an_application_db": ("#ffcdd2", "#b71c1c", "NOT AN APPROVED APPLICATION DB"),
}

# Character budget for wrapped prose inside a database node.  Wider than the
# system diagram's default so the registry reads as prose instead of a column.
DB_WRAP = 62

KIND_TITLE = {
    "postgresql": "PostgreSQL 18 (system-wide relational platform)",
    "postgis": "PostgreSQL / PostGIS 3.6.2",
    "redis": "Redis 8 (cache and coordination - not a system of record)",
    "tsdb": "Prometheus TSDB (metrics, health, alerting)",
    "sqlite": "SQLite (embedded desktop state)",
    "filesystem": "Filesystem / local application state",
    "h2": "H2 (retained migration backups only)",
}


def database_node(entry: dict) -> str:
    fill, border, authority_label = AUTHORITY_STYLE.get(
        str(entry.get("authority", "")), ("#f5f5f5", "#616161", "UNKNOWN"))
    label = ["<b>%s</b>" % dot_escape(entry.get("label", ""))]
    if entry.get("software"):
        label.append(dot_wrapped(entry["software"], color="#0d47a1", width=DB_WRAP))
    label.append("<font point-size='9' color='%s'><b>%s</b></font>" % (border, authority_label))
    for listen in entry.get("listens") or []:
        label.append("<font point-size='9' color='#1565c0'>listen %s</font>" % dot_escape(listen))
    if entry.get("path"):
        label.append("<font point-size='9' color='#455a64'>path %s</font>"
                     % dot_wrapped(entry["path"], width=DB_WRAP))
    if entry.get("programs"):
        label.append(dot_wrapped("used by %s" % ", ".join(entry["programs"]),
                                 color="#37474f", size=8, width=DB_WRAP))
    if entry.get("role"):
        label.append(dot_wrapped(entry["role"], size=8, width=DB_WRAP))
    if entry.get("note"):
        label.append(dot_wrapped("!! %s" % entry["note"], color="#b71c1c", size=8, width=DB_WRAP))
    label.append("<font point-size='8' color='#6a1b9a'>status: %s</font>"
                 % dot_escape(str(entry.get("status", ""))))
    attrs = ('shape=box, style="rounded,filled", fillcolor="%s", color="%s", penwidth=1.5'
             % (fill, border))
    if entry.get("status") == "blocked":
        attrs += ', style="rounded,filled,dashed"'
    return "%s [%s, label=<%s>];" % (dot_id(entry["id"]), attrs, "<br/>".join(label))


def render_dot_databases(inv: dict) -> str:
    databases = inv.get("databases") or []
    lines: list[str] = []
    add = lines.append
    add("digraph alwayson_databases {")
    # rankdir=TB: the stores are grouped into families whose membership is the
    # meaningful structure, so families read top-to-bottom and the canvas stays
    # near page proportions.  LR stretched the same content to ~4:1.
    add('  graph [rankdir=TB, compound=true, newrank=true, fontname="DejaVu Sans", fontsize=11,'
        ' bgcolor="#ffffff", nodesep=0.45, ranksep=0.75, splines=spline, pad=0.4, labelloc=t,'
        ' fontsize=22, label=<<b>ALWAYS ON &mdash; DATABASES &amp; DATA STORES</b><br/>'
        '<font point-size="11">v6 3.3 / 3.3.1 Program-to-Database Map &mdash; authority, placement,'
        ' status, and the programs that use each store</font><br/>'
        '<font point-size="10">generated %s &mdash; PostgreSQL 18 is the system-wide relational'
        ' platform; Redis is not a system of record; SQLite and H2 are not approved application'
        ' databases for Grafana or Metabase</font>>];' % inv["generated_at_utc"])
    add('  node [shape=box, fontname="DejaVu Sans", fontsize=10, margin="0.16,0.10"];')
    add('  edge [fontname="DejaVu Sans", fontsize=9, color="#607d8b", arrowsize=0.7];')

    legend = ["<<TABLE BORDER=\"0\" CELLBORDER=\"0\" CELLSPACING=\"3\">",
              "<TR><TD COLSPAN=\"2\"><B>LEGEND &mdash; authority and status</B></TD></TR>"]
    for key, (fill, border, title) in AUTHORITY_STYLE.items():
        if not any(str(item.get("authority", "")) == key for item in databases):
            continue
        legend.append('<TR><TD><FONT COLOR="%s">&#9632;</FONT></TD>'
                      '<TD><FONT POINT-SIZE="9">%s</FONT></TD></TR>' % (border, dot_escape(title)))
    legend.append("</TABLE>>")
    add('  %s [shape=note, fillcolor="#ffffff", color="#455a64", label=%s];'
        % (dot_id("legend"), "".join(legend)))

    groups: dict[str, list[dict]] = {}
    for entry in databases:
        groups.setdefault(str(entry.get("kind", "other")), []).append(entry)

    kind_order = sorted(groups, key=lambda item: (item not in ("postgresql", "postgis"), item))
    for kind in kind_order:
        entries = groups[kind]
        add("  subgraph cluster_db_%s {" % dot_id(kind))
        add('    label=<<b>%s</b> <font point-size="9">(%d)</font>>; style="rounded,filled";'
            ' fillcolor="#fafbfd"; color="#7986cb"; fontsize=12;'
            % (dot_escape(KIND_TITLE.get(kind, kind)), len(entries)))
        for entry in entries:
            add("    " + database_node(entry))
        # Invisible sibling chain: without it dot stacks every store in a family
        # into one vertical column, which wastes the whole horizontal canvas.
        for first, second in zip(entries, entries[1:]):
            add("    %s -> %s [style=invis];"
                % (dot_id(first["id"]), dot_id(second["id"])))
        add("  }")

    add("")
    # No invisible chain between family heads: with rankdir=TB it pushed the
    # families into a single tall column and left the right half of the canvas
    # empty.  rankdir/sort already emit the families in kind_order.
    ids = {entry["id"] for entry in databases}
    for entry in databases:
        parent = entry.get("parent")
        if parent and parent in ids:
            add('  %s -> %s [label="logical database", color="#9fa8da", style=dashed, '
                'fontcolor="#3949ab"];' % (dot_id(parent), dot_id(entry["id"])))
    add("}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Rendering: Markdown tables and self-contained HTML
# ---------------------------------------------------------------------------

def md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        out.append("| " + " | ".join(str(cell).replace("|", "\\|") for cell in row) + " |")
    return out


def render_markdown(inv: dict) -> str:
    counts = inv["counts"]
    lines = ["# ALWAYS ON — generated system topology inventory",
             "",
             "Generated: `%s`  " % inv["generated_at_utc"],
             "Authority: `%s` (README §3.1, §3.3, §5.1, §5.2, §6.A, §9, §20.0)  " % inv["authority"],
             "Generator: `/ALWAYSON/scripts/operations/generate-topology.py`  ",
             "Observed mode: `%s`" % ("live inspection" if inv["observed"] else "declared only"),
             "",
             "Networks: **%d** (%d live) · containers: **%d** declared, %d running · "
             "listeners: **%d** (%d loopback) · drift items: **%d**"
             % (counts["networks_total"], counts["networks_live"], counts["containers_declared"],
                counts["containers_running"], counts["listeners"], counts["loopback_listeners"],
                counts["drift_items"]),
             "",
             "## 1. Podman networks",
             ""]
    rows = []
    for net in inv["networks"]:
        rows.append([net["name"], net["subnet"] or "—", net["gateway"] or "—",
                     {True: "true", False: "false", None: "?"}[net["internal"]],
                     "**podman default** (not an ALWAYS ON domain)" if net["podman_default"]
                     else ("adapter" if net["adapter"] else "workload"),
                     "live" if net["live"] else "not created",
                     net["status"], ", ".join(net["members"]) or "—"])
    lines += md_table(["Network", "Subnet", "Gateway", "Internal", "Kind", "Runtime",
                       "Status", "Members"], rows)
    lines += ["", "## 2. Containers, networks, IPs and published ports", ""]
    rows = []
    for record in inv["containers"]:
        attachments = ", ".join("%s=%s" % (name, ip or "—")
                                for name, ip in sorted((record.get("ip_by_network") or {}).items()))
        ports = ", ".join("%s:%s->%s/%s" % (port.get("host_ip") or "0.0.0.0",
                                            port.get("host_port"), port.get("container_port"),
                                            port.get("protocol"))
                          for port in record.get("published") or [])
        if not ports:
            ports = ", ".join("publish %s" % item for item in record.get("publish") or []) or "internal only"
        rows.append([record["container_name"],
                     "%s %s" % (record.get("image_name", ""), record.get("image_version", "")),
                     attachments or "—", ports, record.get("state") or "not running",
                     record["status"], record.get("unit_state") or "—",
                     "yes" if record.get("declared") else "**no**"])
    lines += md_table(["Container", "Local software / image", "Networks + IP", "Published ports",
                       "State", "Status", "systemd unit", "Quadlet"], rows)
    lines += ["", "## 3. Databases and data stores (v6 §3.3 / §3.3.1)", ""]
    rows = []
    for entry in inv.get("databases") or []:
        rows.append([entry.get("label", ""), entry.get("kind", ""),
                     entry.get("software", ""), entry.get("placement", ""),
                     str(entry.get("authority", "")).replace("_", " "),
                     ", ".join(entry.get("programs") or []) or "—",
                     ", ".join(entry.get("listens") or []) or entry.get("path", "") or "—",
                     entry.get("status", ""), entry.get("role", "")])
    lines += md_table(["Database / store", "Kind", "Software", "Placement", "Authority",
                       "Used by", "Listens / path", "Status", "Role"], rows)
    lines += ["", "## 4. Host software (non-container)", ""]
    rows = []
    for service in inv["host_services"]:
        rows.append([service["label"], service.get("software", ""),
                     ", ".join(service.get("listens") or []) or "—",
                     ", ".join(service.get("relays") or []) or "—", service.get("status", "")])
    for app in inv["desktop_software"]:
        rows.append([app["label"], app.get("software", ""),
                     ", ".join(app.get("listens") or []) or "—",
                     ", ".join(app.get("connects") or []) or "—", app.get("status", "")])
    lines += md_table(["Component", "Software", "Listens", "Connects/relays", "Status"], rows)
    lines += ["", "## 5. Field, radio and drone link", ""]
    field = inv.get("field") or {}
    rows = []
    for node in field.get("drone_side") or []:
        rows.append([node["label"], node.get("software", ""), node.get("hardware", "—"),
                     node.get("status", ""), node.get("note", "")])
    for radio in field.get("radios") or []:
        rows.append([radio["label"], radio.get("software", ""), radio.get("hardware", "—"),
                     radio.get("status", ""), radio.get("rf", "")])
    lines += md_table(["Component", "Software", "Hardware / path", "Status", "RF / note"], rows)
    lines += ["", "## 6. Observed listeners", ""]
    rows = [[item["proto"], item["address"], item["port"], item["scope"],
             item["process"] or "—", item["pid"] or "—",
             "yes" if item["host_noise"] else "no"] for item in inv["listeners"]]
    lines += md_table(["Proto", "Address", "Port", "Scope", "Process (unprivileged view)", "PID",
                       "Base-OS noise"], rows)
    lines += ["", "## 7. Documented claim vs observed state (drift)", ""]
    rows = [[item["status"], item["severity"], item["claim"], item["expected"], item["observed"]]
            for item in inv["drift"]]
    lines += md_table(["Result", "Severity", "Documented claim", "Expected", "Observed"], rows)
    lines += ["", "---", "",
              "Generated file — do not hand-edit. Re-run "
              "`python3 /ALWAYSON/scripts/operations/generate-topology.py` after any change.",
              ""]
    return "\n".join(lines)


HTML_HEAD = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>ALWAYS ON — system topology</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
 body{font-family:"DejaVu Sans",system-ui,sans-serif;background:#111418;color:#e6e6e6;margin:0;padding:1.4em 1.8em}
 h1{font-size:1.5em;margin:.2em 0 .1em} h2{font-size:1.1em;margin:1.6em 0 .4em;color:#9fd3ff}
 .meta{color:#9aa7b4;font-size:.86em;margin-bottom:1em}
 .stat{display:inline-block;background:#1b2026;border:1px solid #2c343d;border-radius:8px;padding:.5em .8em;margin:.15em .3em .15em 0}
 .stat b{color:#7fd18a;font-size:1.15em}
 table{border-collapse:collapse;width:100%;margin:.3em 0;font-size:.83em}
 th,td{border:1px solid #2c343d;padding:4px 7px;text-align:left;vertical-align:top}
 th{background:#1b2026;color:#9fd3ff}
 tr:nth-child(even) td{background:#161b20}
 code{color:#ffcf7a} .ok{color:#7fd18a} .warn{color:#ffb74d} .bad{color:#ef7b7b}
 .diagram{background:#fff;border-radius:8px;padding:.4em;overflow:auto}
 .note{color:#9aa7b4;font-size:.85em}
</style></head><body>
"""


def html_table(headers: list[str], rows: list[list[str]], css: str = "") -> str:
    out = ['<table class="%s"><thead><tr>' % css]
    out += "".join("<th>%s</th>" % html.escape(str(cell)) for cell in headers)
    out += "</tr></thead><tbody>"
    for row in rows:
        out.append("<tr>" + "".join("<td>%s</td>" % cell for cell in row) + "</tr>")
    return "".join(out) + "</tbody></table>"


def render_html_header(inv: dict, png_name: str, md_name: str) -> list[str]:
    counts = inv["counts"]
    parts = [HTML_HEAD, "<h1>ALWAYS ON — system topology</h1>"]
    parts.append('<p class="meta">Generated <code>%s</code> · authority '
                 '<code>%s</code> (v6 §3.1/§3.3/§3.3.1/§5.1/§5.2/§6.A/§9/§10/§18) · '
                 'observed mode: <b>%s</b> · generator '
                 '<code>/ALWAYSON/scripts/operations/generate-topology.py</code></p>'
                 % (html.escape(inv["generated_at_utc"]), html.escape(inv["authority"]),
                    "live inspection" if inv["observed"] else "declared definitions only"))
    for label, value in (("networks", counts["networks_total"]),
                         ("networks live", counts["networks_live"]),
                         ("containers declared", counts["containers_declared"]),
                         ("containers running", counts["containers_running"]),
                         ("listeners", counts["listeners"]),
                         ("loopback listeners", counts["loopback_listeners"]),
                         ("non-loopback listeners", counts["non_loopback_listeners"]),
                         ("drift items", counts["drift_items"])):
        parts.append('<div class="stat">%s <b>%s</b></div>' % (html.escape(label), value))
    parts.append('<p class="note">Static self-contained view: the diagram is embedded SVG '
                 '(also on disk as <code>alwayson-system-topology.svg</code> and '
                 '<code>%s</code>); the tables below are the inventory the diagram is built from. '
                 'Live Grafana view: <code>http://127.0.0.1:3001/d/alwayson-topology/'
                 'alwayson-system-topology</code> (operator login required). '
                 'Markdown tables: <code>%s</code>.</p>'
                 % (html.escape(png_name), html.escape(md_name)))
    return parts


def render_html(inv: dict, svg: str, png_name: str, md_name: str) -> str:
    parts = render_html_header(inv, png_name, md_name)
    parts.append('<h2>Topology diagram</h2><div class="diagram">%s</div>' % svg)

    parts.append("<h2>1. Podman networks (CIDR · gateway · Internal · members)</h2>")
    rows = []
    for net in inv["networks"]:
        rows.append([
            "<b>%s</b>" % html.escape(net["name"]),
            html.escape(net["subnet"] or "—"), html.escape(net["gateway"] or "—"),
            {True: "true", False: '<span class="warn">false</span>', None: "?"}[net["internal"]],
            '<span class="note">podman default (not an ALWAYS ON domain)</span>'
            if net["podman_default"] else ("adapter" if net["adapter"] else "workload"),
            "live" if net["live"] else '<span class="note">not created</span>',
            html.escape(net["status"]),
            html.escape(", ".join(net["members"]) or "—"),
            html.escape(net["purpose"] or ""),
        ])
    parts.append(html_table(["Network", "Subnet", "Gateway", "Internal", "Kind", "Runtime",
                             "Status", "Members", "Purpose (v6 §5.1)"], rows))

    parts.append("<h2>2. Containers — local software, network IPs, published ports</h2>")
    rows = []
    for record in inv["containers"]:
        attachments = ", ".join("%s·%s" % (html.escape(name), html.escape(ip or "—"))
                                for name, ip in sorted((record.get("ip_by_network") or {}).items()))
        ports = ", ".join(html.escape("%s:%s→%s/%s" % (port.get("host_ip") or "0.0.0.0",
                                                       port.get("host_port"),
                                                       port.get("container_port"),
                                                       port.get("protocol")))
                          for port in record.get("published") or [])
        if not ports:
            ports = ", ".join(html.escape(item) for item in record.get("publish") or []) \
                or '<span class="note">internal only</span>'
        state = record.get("state") or "not running"
        state_html = state if state == "running" \
            else '<span class="warn">%s</span>' % html.escape(state)
        rows.append([html.escape(record["container_name"]),
                     html.escape("%s %s" % (record.get("image_name", ""),
                                            record.get("image_version", ""))),
                     attachments or "—", ports, state_html, html.escape(record["status"]),
                     html.escape(record.get("unit_state") or "—"),
                     "yes" if record.get("declared") else '<span class="bad">no</span>'])
    parts.append(html_table(["Container", "Local software / image", "Networks·IP",
                             "Published ports", "State", "Status", "systemd unit", "Quadlet"], rows))

    parts.append("<h2>3. Databases and data stores — v6 §3.3 / §3.3.1 Program-to-Database Map</h2>")
    parts.append('<p class="note">PostgreSQL 18 is the system-wide relational platform: one host '
                 'cluster, separate logical databases, separate application roles. Redis is a cache '
                 'and coordination layer, <b>not</b> a system of record. Prometheus TSDB is the '
                 'separate metrics store. SQLite and H2 are <b>not</b> approved application databases '
                 'for Grafana or Metabase.</p>')
    rows = []
    for entry in inv.get("databases") or []:
        authority = str(entry.get("authority", "")).replace("_", " ")
        if authority.startswith("authoritative"):
            authority_html = '<b class="ok">%s</b>' % html.escape(authority)
        elif authority in ("not_an_application_db",):
            authority_html = '<span class="bad">%s</span>' % html.escape(authority)
        else:
            authority_html = '<span class="note">%s</span>' % html.escape(authority)
        note = entry.get("note") or ""
        rows.append([
            "<b>%s</b>" % html.escape(entry.get("label", "")),
            html.escape(entry.get("kind", "")),
            html.escape(entry.get("software", "")),
            html.escape(entry.get("placement", "")),
            authority_html,
            html.escape(", ".join(entry.get("programs") or []) or "—"),
            html.escape(", ".join(entry.get("listens") or []) or entry.get("path", "") or "—"),
            html.escape(str(entry.get("status", ""))),
            html.escape(entry.get("role", "")) + (('<br/><span class="bad">%s</span>'
                                                  % html.escape(note)) if note else ""),
        ])
    parts.append(html_table(["Database / store", "Kind", "Software", "Placement", "Authority",
                             "Used by", "Listens / path", "Status", "Role"], rows))

    parts.append("<h2>4. Host software (non-container) — host PG, Redis, SITL, restic, KDE Wallet</h2>")
    rows = []
    for service in inv["host_services"]:
        rows.append([html.escape(service["label"]), html.escape(service.get("software", "")),
                     html.escape(", ".join(service.get("listens") or []) or "—"),
                     html.escape(", ".join(service.get("relays") or []) or "—"),
                     html.escape(service.get("data", "")), html.escape(service.get("status", ""))])
    for app in inv["desktop_software"]:
        rows.append([html.escape(app["label"]), html.escape(app.get("software", "")),
                     html.escape(", ".join(app.get("listens") or []) or "—"),
                     html.escape(", ".join(app.get("connects") or []) or "—"),
                     html.escape(", ".join(app.get("env") or []) or "—"),
                     html.escape(app.get("status", ""))])
    parts.append(html_table(["Component", "Software", "Listens", "Connects / relays",
                             "Env / data", "Status"], rows))
    return "".join(parts) + render_html_tail(inv, md_name)


def render_html_tail(inv: dict, md_name: str) -> str:
    """Sections 4-8 plus footer of the self-contained HTML report."""
    parts = []
    counts = inv["counts"]

    parts.append("<h2>5. Field, radio and drone link</h2>")
    field = inv.get("field") or {}
    rows = []
    for node in field.get("drone_side") or []:
        rows.append([html.escape(node["label"]), html.escape(node.get("software", "")),
                     html.escape(node.get("hardware", "—")), html.escape(node.get("status", "")),
                     html.escape(node.get("note", ""))])
    for radio in field.get("radios") or []:
        rows.append([html.escape(radio["label"]), html.escape(radio.get("software", "")),
                     html.escape(radio.get("hardware", "—")), html.escape(radio.get("status", "")),
                     html.escape(radio.get("rf", ""))])
    parts.append(html_table(["Component", "Software", "Hardware / path", "Status", "RF / note"], rows))
    if inv["serial_devices"]:
        parts.append('<p class="note">Serial devices observed: <code>%s</code></p>'
                     % html.escape(", ".join(inv["serial_devices"])))

    parts.append("<h2>6. Controlled edge paths and planned components</h2>")
    rows = []
    edge = inv.get("edge") or {}
    internet = edge.get("internet") or {}
    if internet:
        rows.append(["<b>%s</b>" % html.escape(internet.get("label", "internet")),
                     html.escape(str(internet.get("status", ""))), "&mdash;", "&mdash;",
                     "origin ports stay loopback; no inbound port-forward"])
    for path in edge.get("paths") or []:
        rows.append([html.escape(path["label"]), html.escape(path.get("software", "")),
                     html.escape(", ".join(path.get("listens") or []) or "—"),
                     html.escape(", ".join(path.get("publishes") or []) or "—"),
                     html.escape(path.get("status", "") + (" — " + path["note"] if path.get("note") else ""))])
    for node in inv.get("planned_components") or []:
        rows.append([html.escape(node["label"]), html.escape(node.get("software", "")),
                     "&mdash;", "&mdash;",
                     html.escape(node.get("status", "") + (" — " + node["note"] if node.get("note") else ""))])
    parts.append(html_table(["Component", "Local software", "Listens", "Publishes",
                             "Status / note"], rows))

    parts.append("<h2>7. Observed listeners (unprivileged process view)</h2>")
    rows = []
    for item in inv["listeners"]:
        scope = item["scope"]
        scope_html = scope if scope == "loopback" else '<span class="warn">%s</span>' % html.escape(scope)
        rows.append([html.escape(item["proto"]), html.escape(item["address"]),
                     str(item["port"]), scope_html, html.escape(item["process"] or "—"),
                     html.escape(item["pid"] or "—"),
                     "yes" if item["host_noise"] else "no"])
    parts.append(html_table(["Proto", "Local address", "Port", "Scope", "Process", "PID",
                             "Base-OS noise"], rows))
    parts.append('<p class="note">Operator listener policy: loopback only unless a port appears in '
                 '<code>/ALWAYSON/config/platform/listener-allowlist.yaml</code> (currently: '
                 '<code>%s</code>).</p>'
                 % html.escape(", ".join(str(p) for p in inv["listener_allowlist"]) or "empty — none approved"))

    parts.append("<h2>8. Documented claim vs observed state (drift)</h2>")
    rows = []
    for item in inv["drift"]:
        badge = ('<span class="ok">match</span>' if item["status"] == "match"
                 else '<span class="warn">drift</span>')
        rows.append([badge, html.escape(item["severity"]), html.escape(item["claim"]),
                     html.escape(item["expected"]), html.escape(item["observed"])])
    parts.append(html_table(["Result", "Severity", "Documented claim (README)", "Expected",
                             "Observed"], rows))
    parts.append('<p class="note">Drift items are informational: the README remains authoritative and '
                 'any persistent divergence must be recorded in its "Approved Deviations and Open '
                 'Decisions" section. %d drift item(s) at this run.</p>' % counts["drift_items"])

    parts.append("<h2>9. Live Grafana view</h2><ul>"
                 "<li>Grafana (loopback, operator login required): "
                 "<code>http://127.0.0.1:3001/d/alwayson-topology/alwayson-system-topology</code></li>"
                 "<li>Prometheus: <code>http://127.0.0.1:9090</code> · "
                 "Metabase: <code>http://127.0.0.1:3002</code></li>"
                 "<li>Dashboard is provisioned from "
                 "<code>config/platform/monitoring/grafana/provisioning/dashboards/</code>; a copy is "
                 "kept here as <code>grafana-dashboard.json</code>.</li></ul>")

    parts.append('<hr><p class="note">Generated file — do not hand-edit. Re-run '
                 '<code>python3 /ALWAYSON/scripts/operations/generate-topology.py</code> after any '
                 'change. Markdown twin: <code>%s</code>.</p></body></html>' % html.escape(md_name))
    return "".join(parts)


def render_live_links(inv: dict, svg_name: str, png_name: str, html_name: str,
                      md_name: str, companions: list[str] | None = None) -> str:
    """Index of artifacts and live loopback links for this run."""
    counts = inv["counts"]
    lines = [
        "# ALWAYS ON — topology artifacts and live links",
        "",
        "Generated `%s` from `/ALWAYSON/README.md` declarations plus %s."
        % (inv["generated_at_utc"], "live inspection" if inv["observed"] else "declared definitions only"),
        "Regenerate with `python3 /ALWAYSON/scripts/operations/generate-topology.py`.",
        "",
        "## Diagram and documents (this folder)",
        "",
        "| File | What it is |",
        "|---|---|",
        "| `%s` | Vector diagram — open in a browser or Inkscape |" % svg_name,
        "| `%s` | Raster diagram, 144 dpi |" % png_name,
        "| `%s` | Self-contained diagram + full inventory tables |" % html_name,
        "| `%s` | Graphviz source |" % Path(svg_name).with_suffix(".dot").name,
        "| `topology-inventory.json` | Machine-readable inventory (declared + live + drift) |",
        "| `%s` | Markdown inventory tables |" % md_name,
        "| `grafana-dashboard.json` | Grafana dashboard definition (provisioned copy) |",
        "| `grafana-provider.yml` | Grafana file-provider definition (provisioned copy) |",
    ]
    for name in companions or []:
        stem = Path(name).stem
        lines.append("| `%s` | Companion sheet — see its `.svg` / `.png` / `.dot` |" % name)
    lines += [
        "",
        "## Live loopback links",
        "",
        "| Service | URL |",
        "|---|---|",
        "| Grafana — ALWAYS ON system topology dashboard | "
        "http://127.0.0.1:3001/d/alwayson-topology/alwayson-system-topology |",
        "| Grafana root | http://127.0.0.1:3001 |",
        "| Prometheus | http://127.0.0.1:9090 |",
        "| Metabase | http://127.0.0.1:3002 |",
        "",
        "All operator listeners are loopback-only by policy (v6 §4.1 rule 6 and "
        "`config/platform/listener-allowlist.yaml`); Grafana requires an operator login. No public "
        "port is opened by these links.",
        "",
        "## This run",
        "",
        "- Networks: %d (%d live)" % (counts["networks_total"], counts["networks_live"]),
        "- Containers: %d declared, %d running" % (counts["containers_declared"],
                                                   counts["containers_running"]),
        "- Listeners observed: %d (%d loopback, %d non-loopback)"
        % (counts["listeners"], counts["loopback_listeners"], counts["non_loopback_listeners"]),
        "- Drift items: %d" % counts["drift_items"],
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Grafana provisioning (README 20.0 — loopback-only operator surface)
# ---------------------------------------------------------------------------

def _grafana_state(status: str, live: bool = True) -> str:
    if status == "blocked":
        return "error"
    if not live:
        return "neutral"
    return "ok"


def _node(node_id: str, title: str, subtitle: str, state: str, main: str, detail: str) -> dict:
    return {"id": node_id, "title": title, "subTitle": subtitle, "mainStat": main,
            "secondaryStat": "", "arc__": "", "detail__": detail, "status": state}


def grafana_graph(inv: dict) -> tuple[list[dict], list[dict]]:
    """Node-graph nodes and edges built from the same inventory as the diagram."""
    nodes: list[dict] = []
    edges: list[dict] = []
    seen: set[str] = set()

    def add(node: dict) -> str:
        nodes.append(node)
        seen.add(node["id"])
        return node["id"]

    def link(src: str, dst: str, main: str = "", second: str = "", detail: str = "") -> None:
        if src in seen and dst in seen:
            edges.append({"id": "%s=>%s" % (src, dst), "source": src, "target": dst,
                          "mainStat": main, "secondaryStat": second, "detail__": detail})

    host = inv["host"]
    iface_text = " · ".join("%s %s" % (item.get("name", ""), ",".join(item.get("addresses") or []))
                            for item in host.get("live_interfaces") or []) or "no interface data"
    host_id = add(_node("host", host.get("label", "ALWAYS ON HOST"),
                        host.get("software", ""), _grafana_state(host.get("status", "")),
                        str(inv["counts"]["containers_running"]), iface_text))

    pg_listens: list[str] = []
    for service in inv["host_services"]:
        if service.get("id") == "host-postgresql":
            pg_listens = service.get("listens") or []
    pg_id = add(_node("host-postgresql", "PostgreSQL 18.6 (host cluster)",
                      "postgresql-18 18.6 / PostGIS 3.6.2", "ok",
                      ", ".join(pg_listens) or "127.0.0.1:5432",
                      "Consolidated relational platform; REVOKE CONNECT FROM PUBLIC enforced"))
    link(host_id, pg_id, "tcp/5432", "loopback", "host PostgreSQL serves every containerised database role")
    for service in inv["host_services"]:
        if service.get("id") == "host-redis":
            rid = add(_node("host-redis", "Redis 8.0.5 (host service)", service.get("software", ""),
                            _grafana_state(service.get("status", "")),
                            ", ".join(service.get("listens") or []) or "127.0.0.1:6379",
                            "cache / coordination layer, not a system of record"))
            link(host_id, rid, "tcp/6379", "loopback")
            break

    network_ids: dict[str, str] = {}
    for net in inv["networks"]:
        if net["podman_default"]:
            continue
        state = _grafana_state(net["status"], net["live"])
        if net["live"] and net["internal"] is False and not net["adapter"]:
            state = "warning"
        network_ids[net["name"]] = add(_node(
            "net-%s" % net["name"], net["name"], "adapter" if net["adapter"] else "workload",
            state, net["subnet"] or net["cidr_registry"] or "no subnet",
            "%s · gw %s · Internal=%s · members: %s"
            % (net["status"], net["gateway"] or "—", net["internal"], ", ".join(net["members"]) or "none")))
        link(host_id, network_ids[net["name"]],
             "Internal=true" if net["internal"] else "Internal=false", net["status"], net["purpose"])

    for record in inv["containers"]:
        running = record.get("state") == "running"
        state = "ok" if running else _grafana_state(record["status"], running)
        attachments = ", ".join("%s=%s" % (name, ip or "—")
                                for name, ip in sorted((record.get("ip_by_network") or {}).items()))
        ports = ", ".join("%s:%s->%s/%s" % (port.get("host_ip") or "0.0.0.0", port.get("host_port"),
                                           port.get("container_port"), port.get("protocol"))
                          for port in record.get("published") or [])
        node_id = add(_node("ctr-%s" % record["container_name"], record["container_name"],
                            "%s %s" % (record.get("image_name", ""), record.get("image_version", "")),
                            state, attachments or "no IP assigned",
                            "%s · ports: %s · unit: %s · status: %s"
                            % (record.get("state") or "not running", ports or "internal only",
                               record.get("unit_state") or "—", record["status"])))
        for net_name in sorted(set(record.get("networks") or []) | set(record.get("networks_live") or [])):
            if net_name not in network_ids:
                continue
            link(network_ids[net_name], node_id,
                 (record.get("ip_by_network") or {}).get(net_name, ""), net_name)
        for port in record.get("published") or []:
            if str(port.get("container_port")) == "5432":
                link(node_id, pg_id, "tcp/5432", "host bridge")

    for entry in inv.get("databases") or []:
        authority = str(entry.get("authority", ""))
        if authority.startswith("authoritative"):
            db_state = "ok"
        elif entry.get("status") in ("blocked", "not_active"):
            db_state = "error"
        elif entry.get("status") in ("target", "current_migration_state", "planned"):
            db_state = "warning"
        else:
            db_state = "neutral"
        main = ", ".join(entry.get("listens") or []) or entry.get("path") or entry.get("kind", "")
        detail = "%s · used by: %s" % (authority.replace("_", " "),
                                       ", ".join(entry.get("programs") or []) or "—")
        if entry.get("role"):
            detail += " · %s" % entry["role"]
        db_id = add(_node("dbnode-%s" % entry["id"], entry.get("label", entry["id"]),
                          entry.get("software", ""), db_state, main, detail))
        link(host_id, db_id, entry.get("kind", ""), entry.get("status", ""))
        parent = entry.get("parent")
        if parent and "dbnode-%s" % parent in seen:
            link("dbnode-%s" % parent, db_id, "logical database", entry.get("status", ""))

    edge = inv.get("edge") or {}
    internet = edge.get("internet") or {}
    internet_id = add(_node("internet", internet.get("label", "PUBLIC INTERNET"),
                            "no inbound port-forward", "warning", "outbound only",
                            "cloudflared tunnel publishes loopback origins; origin ports stay loopback"))
    link(host_id, internet_id, "outbound", "controlled")
    for path in edge.get("paths") or []:
        if path.get("id") == "edge-cloudflare-tunnel":
            link(internet_id, host_id, "ingress", "tunnel", "; ".join(path.get("publishes") or []))
    for node in inv.get("planned_components") or []:
        pid = add(_node("plan-%s" % node["id"], node["label"], node.get("software", ""),
                        _grafana_state(node.get("status", ""), False), node.get("status", "planned"),
                        node.get("note", "")))
        link(host_id, pid, "planned", node.get("status", ""))
    return nodes, edges


def grafana_dashboard(inv: dict, model: dict) -> dict:
    """Grafana dashboard JSON embedding the same topology as a node graph."""
    nodes, edges = grafana_graph(inv)
    uid = model.get("grafana_dashboard_uid", "alwayson-topology")
    slug = model.get("grafana_dashboard_slug", "alwayson-system-topology")
    counts = inv["counts"]
    ds = {"type": "prometheus", "uid": "${DS_PROMETHEUS}"}
    panels: list[dict] = []
    tiles = [
        ("networks total", counts["networks_total"]),
        ("networks live", counts["networks_live"]),
        ("containers declared", counts["containers_declared"]),
        ("containers running", counts["containers_running"]),
        ("listeners", counts["listeners"]),
        ("loopback listeners", counts["loopback_listeners"]),
        ("non-loopback listeners", counts["non_loopback_listeners"]),
        ("databases &amp; stores", counts["databases"]),
        ("authoritative stores", counts["databases_authoritative"]),
        ("drift items", counts["drift_items"]),
    ]
    for index, (title, value) in enumerate(tiles):
        panels.append({
            "id": index + 1,
            "type": "stat",
            "title": title,
            "gridPos": {"h": 4, "w": 24 // len(tiles), "x": (index % len(tiles)) * (24 // len(tiles)),
                        "y": 0},
            "datasource": ds,
            "targets": [{"refId": "A", "datasource": ds, "instant": True,
                         "expr": "ALWAYSON_STATIC{metric=\"%s\"}" % title.replace(" ", "_")}],
            "options": {"reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
                        "colorMode": "background", "graphMode": "none"},
            "fieldConfig": {"defaults": {"color": {"mode": "thresholds"},
                                         "thresholds": {"mode": "absolute", "steps": [
                                             {"color": "green", "value": None}]}}},
        })
    panels.append({
        "id": 100,
        "type": "nodeGraph",
        "title": "ALWAYS ON — networks · containers · host software",
        "description": "Generated by /ALWAYSON/scripts/operations/generate-topology.py from "
                       "README-authoritative declarations plus live inspection. "
                       "Node mainStat = CIDR or container IP; edge labels = published port / IP.",
        "gridPos": {"h": 22, "w": 24, "x": 0, "y": 4},
        "datasource": {"type": "datasource", "uid": "grafana"},
        "nodes": nodes,
        "edges": edges,
        "options": {"nodeSize": {"width": 340, "height": 110},
                    "zoomMode": "cooperative",
                    "dragging": True,
                    "legend": {"showLabel": True, "showType": True, "showStats": True,
                               "showPorts": True}},
    })
    panels.append({
        "id": 101,
        "type": "text",
        "title": "Where the artifacts live",
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 26},
        "datasource": ds,
        "options": {"mode": "markdown", "content": (
            "**Topology artifacts:** `/ALWAYSON/TOPOLOGY/` — SVG, PNG, self-contained HTML, "
            "Graphviz DOT, `topology-inventory.json`, `TOPOLOGY.md`, `LIVE-LINKS.md`.\n\n"
            "**Prometheus:** http://127.0.0.1:9090 · **Metabase:** http://127.0.0.1:3002 · "
            "**Grafana:** http://127.0.0.1:3001 (loopback only, operator login).\n\n"
            "Regenerate after any Quadlet, network, or port change: "
            "`python3 /ALWAYSON/scripts/operations/generate-topology.py`")},
    })
    return {
        "__inputs": [{"name": "DS_PROMETHEUS", "label": "Prometheus",
                      "description": "Prometheus datasource for the ALWAYS ON topology dashboard",
                      "type": "datasource", "pluginId": "prometheus", "pluginName": "Prometheus"}],
        "__requires": [
            {"type": "grafana", "id": "grafana", "name": "Grafana", "version": "10.0.0"},
            {"type": "datasource", "id": "prometheus", "name": "Prometheus", "version": "1.0.0"},
            {"type": "panel", "id": "nodeGraph", "name": "Node graph", "version": ""},
        ],
        "annotations": {"list": [{"builtIn": 1, "datasource": {"type": "grafana", "uid": "-- Grafana --"},
                                  "enable": True, "hide": True, "iconColor": "rgba(0, 211, 255, 1)",
                                  "name": "Annotations & Alerts", "type": "dashboard"}]},
        "description": "ALWAYS ON system topology: networks, ports, IP addresses, local software "
                       "names, field radio and drone links.",
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 1,
        "links": [],
        "panels": panels,
        "preload": False,
        "refresh": "60s",
        "schemaVersion": 39,
        "tags": ["alwayson", "topology", "networks"],
        "templating": {"list": []},
        "time": {"from": "now-6h", "to": "now"},
        "timepicker": {},
        "timezone": "browser",
        "title": "ALWAYS ON — system topology",
        "uid": uid,
        "url": "/d/%s/%s" % (uid, slug),
        "version": 1,
        "weekStart": "",
    }


def grafana_provision_files(inv: dict, model: dict) -> tuple[Path, str, Path, str]:
    """Return (provider_path, provider_yaml, dashboard_path, dashboard_json)."""
    dashboard_json = json.dumps(grafana_dashboard(inv, model), indent=2) + "\n"
    provider = {
        "apiVersion": 1,
        "providers": [{
            "name": "alwayson",
            "orgId": 1,
            "folder": "ALWAYS ON",
            "type": "file",
            "disableDeletion": True,
            "allowUiUpdates": True,
            "updateIntervalSeconds": 30,
            "options": {"path": "/etc/grafana/provisioning/dashboards",
                        "foldersFromFilesStructure": False},
        }],
    }
    dash_dir = GRAFANA_PROVISIONING / "dashboards"
    return (dash_dir / "alwayson-topology.provider.yml",
            yaml.safe_dump(provider, sort_keys=False),
            dash_dir / "json" / "alwayson-topology.json", dashboard_json)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def render_html_databases(inv: dict, svg: str, png_name: str, md_name: str) -> str:
    """Self-contained HTML for the dedicated database registry page."""
    counts = inv["counts"]
    parts = [HTML_HEAD.replace("system topology", "databases &amp; data stores"),
             "<h1>ALWAYS ON — databases &amp; data stores</h1>"]
    parts.append('<p class="meta">Generated <code>%s</code> · authority <code>%s</code> '
                 '(v6 §3.3, §3.3.1) · observed mode: <b>%s</b> · generator '
                 '<code>/ALWAYSON/scripts/operations/generate-topology.py</code></p>'
                 % (html.escape(inv["generated_at_utc"]), html.escape(inv["authority"]),
                    "live inspection" if inv["observed"] else "declared definitions only"))
    for label, value in (("databases &amp; stores", counts["databases"]),
                         ("relational (PostgreSQL/PostGIS)", counts["databases_relational"]),
                         ("authoritative stores", counts["databases_authoritative"])):
        parts.append('<div class="stat">%s <b>%s</b></div>' % (label, value))
    parts.append('<h2>Database registry diagram</h2><div class="diagram">%s</div>' % svg)
    parts.append('<p class="note">Companion system diagram: '
                 '<code>alwayson-system-topology.html</code>. Markdown tables: '
                 '<code>%s</code>.</p>' % html.escape(md_name))
    return "".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the ALWAYS ON system topology diagram and companion artifacts.")
    parser.add_argument("--out-dir", default=str(OUT_DIR_DEFAULT),
                        help="output directory (default: %s)" % OUT_DIR_DEFAULT)
    parser.add_argument("--no-live", action="store_true",
                        help="use declared definitions only; skip podman/systemd/ss inspection")
    parser.add_argument("--dry-run", action="store_true", help="print the plan and write nothing")
    parser.add_argument("--skip-grafana", action="store_true",
                        help="do not write Grafana provisioning files")
    parser.add_argument("--print-json", action="store_true",
                        help="print the machine-readable inventory to stdout")
    parser.add_argument("--quiet", action="store_true", help="suppress progress messages")
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir).expanduser().resolve()
    journal("generate-topology start out_dir=%s live=%s skip_grafana=%s dry_run=%s"
            % (out_dir, not args.no_live, args.skip_grafana, args.dry_run), args.dry_run)
    log("output directory: %s" % out_dir, args.quiet)
    log("observed mode: %s" % ("live inspection" if not args.no_live else "declared only"),
        args.quiet)

    if args.dry_run:
        log("dry run — no files written", args.quiet)
        journal("generate-topology dry-run complete", True)
        return 0

    if not MODEL_PATH.exists():
        sys.stderr.write("generate-topology: missing model %s\n" % MODEL_PATH)
        journal("generate-topology FAILED missing model %s" % MODEL_PATH, False)
        return 2
    model = load_yaml(MODEL_PATH)

    inventory = build_inventory(model, use_live=not args.no_live)
    counts = inventory["counts"]
    log("networks %d (%d live) · containers %d declared / %d running · listeners %d · drift %d"
        % (counts["networks_total"], counts["networks_live"], counts["containers_declared"],
           counts["containers_running"], counts["listeners"], counts["drift_items"]), args.quiet)

    json_name, md_name = "topology-inventory.json", "TOPOLOGY.md"
    links_name = "LIVE-LINKS.md"

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / json_name).write_text(json.dumps(inventory, indent=2, default=str) + "\n",
                                     encoding="utf-8")
    (out_dir / md_name).write_text(render_markdown(inventory), encoding="utf-8")

    # ---- diagram sheets -------------------------------------------------
    # "alwayson-system-topology" is kept as the overview's filename so existing
    # links (TOPOLOGY.md, LIVE-LINKS.md, docs) keep resolving to a real sheet.
    view_files = {
        "overview": ("alwayson-system-topology.dot", "alwayson-system-topology.svg",
                     "alwayson-system-topology.png", "alwayson-system-topology.html"),
        "networks": ("alwayson-workload-networks.dot", "alwayson-workload-networks.svg",
                     "alwayson-workload-networks.png", "alwayson-workload-networks.html"),
        "hostsw": ("alwayson-host-software.dot", "alwayson-host-software.svg",
                   "alwayson-host-software.png", "alwayson-host-software.html"),
        "field": ("alwayson-field-and-edge.dot", "alwayson-field-and-edge.svg",
                  "alwayson-field-and-edge.png", "alwayson-field-and-edge.html"),
    }
    have_dot = bool(shutil.which("dot"))
    emitted: dict[str, tuple[str, str, str, str]] = {}
    for view, (d_name, s_name, p_name, h_name) in view_files.items():
        (out_dir / d_name).write_text(render_dot(inventory, view), encoding="utf-8")
        svg_text = ""
        if have_dot:
            code, _ = run(["dot", "-Tsvg", "-o", str(out_dir / s_name), str(out_dir / d_name)])
            if code == 0:
                svg_text = (out_dir / s_name).read_text(encoding="utf-8")
                log("rendered %s" % s_name, args.quiet)
            else:
                log("graphviz svg rendering failed for %s (exit %d)" % (d_name, code), args.quiet)
            code, _ = run(["dot", "-Tpng", "-Gdpi=96", "-Gsize=\"60,40!\"",
                           "-o", str(out_dir / p_name), str(out_dir / d_name)])
            if code == 0:
                log("rendered %s" % p_name, args.quiet)
            else:
                log("graphviz png rendering failed for %s (exit %d)" % (d_name, code), args.quiet)
        if svg_text:
            (out_dir / h_name).write_text(render_html(inventory, svg_text, p_name, md_name),
                                         encoding="utf-8")
            log("wrote %s (self-contained, embedded SVG)" % h_name, args.quiet)
        emitted[view] = (d_name, s_name, p_name, h_name)
    if not have_dot:
        log("graphviz 'dot' not installed — SVG/PNG not rendered", args.quiet)

    # LIVE-LINKS points at the overview sheet plus the companions.
    od, os_, op, oh = emitted["overview"]
    companion = [emitted[v][3] for v in ("networks", "hostsw", "field")]
    (out_dir / links_name).write_text(
        render_live_links(inventory, os_, op, oh, md_name, companion), encoding="utf-8")

    # ---- database registry diagram (v6 3.3 / 3.3.1) --------------------
    db_dot, db_svg = "alwayson-databases.dot", "alwayson-databases.svg"
    db_png, db_html = "alwayson-databases.png", "alwayson-databases.html"
    if inventory.get("databases"):
        (out_dir / db_dot).write_text(render_dot_databases(inventory), encoding="utf-8")
        db_svg_text = ""
        if shutil.which("dot"):
            code, _ = run(["dot", "-Tsvg", "-o", str(out_dir / db_svg), str(out_dir / db_dot)])
            if code == 0:
                db_svg_text = (out_dir / db_svg).read_text(encoding="utf-8")
            code, _ = run(["dot", "-Tpng", "-Gdpi=96", "-Gsize=\"60,40!\"",
                           "-o", str(out_dir / db_png), str(out_dir / db_dot)])
            if code != 0:
                log("database diagram png rendering failed (exit %d)" % code, args.quiet)
        if db_svg_text:
            (out_dir / db_html).write_text(
                render_html_databases(inventory, db_svg_text, db_png, md_name), encoding="utf-8")
            log("wrote %s / %s / %s" % (db_svg, db_png, db_html), args.quiet)

    grafana_paths: list[str] = []
    if not args.skip_grafana:
        provider_path, provider_yaml, dash_path, dash_json = grafana_provision_files(inventory, model)
        try:
            dash_path.parent.mkdir(parents=True, exist_ok=True)
            dash_path.write_text(dash_json, encoding="utf-8")
            provider_path.write_text(provider_yaml, encoding="utf-8")
            grafana_paths = [str(provider_path), str(dash_path)]
            (out_dir / "grafana-dashboard.json").write_text(dash_json, encoding="utf-8")
            (out_dir / "grafana-provider.yml").write_text(provider_yaml, encoding="utf-8")
            log("wrote Grafana provisioning: %s" % ", ".join(grafana_paths), args.quiet)
            log("note: Grafana polls provisioning every 30s; this script does not restart services",
                args.quiet)
        except OSError as exc:
            sys.stderr.write("generate-topology: grafana provisioning write failed: %s\n" % exc)
            journal("generate-topology grafana write FAILED: %s" % exc, False)

    for name in sorted(os.listdir(out_dir)):
        log("artifact: %s" % (out_dir / name), args.quiet)

    if args.print_json:
        sys.stdout.write(json.dumps(inventory, indent=2, default=str) + "\n")

    journal("generate-topology OK out_dir=%s networks=%d/%d containers=%d/%d listeners=%d "
            "drift=%d views=%d grafana=%s"
            % (out_dir, counts["networks_live"], counts["networks_total"],
               counts["containers_running"], counts["containers_declared"], counts["listeners"],
               counts["drift_items"], len(emitted), bool(grafana_paths)), False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
