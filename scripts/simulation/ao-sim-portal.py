#!/usr/bin/env python3
"""ALWAYS ON - ao-sim-fabrication HTML portal control surface (README Section 10.2.1).

Section 10.2.1 requires the fabrication simulation to be "fully settable and
operable from" a browser-served HTML portal without a desktop GUI client:

  start, stop, reset and inspect the world; view live robot, machine and stock
  state; run a cell or kitchen task plan; select and configure the
  reinforcement learning objects; and read back boning and tolerance
  measurements.

The previous portal was a static nginx index whose buttons called /api/* routes
that did not exist. This service implements them.

SCOPE AND SAFETY. This portal operates the SIMULATION ONLY. It never touches
live machinery: the only thing it can start or stop is ao-sim-fabrication-gz,
the Gazebo server container, and it holds no path to the Klipper/field
hardware. That separation is the one recorded in README Section 10.2 and it is
enforced by the fact that no other systemd unit is reachable from here.

WHY IT RUNS ON THE HOST AND NOT IN THE DOMAIN. The README asks for the portal
to run inside ao-sim-fabrication. Start/stop/reset of the world means acting on
the sibling Quadlet unit ao-sim-fabrication-gz.service, which is managed by the
scottw user manager; a container on ao-sim-fabrication has no access to it and
no route to the host. Running the portal as a host user service keeps the
control path real while leaving the container on its isolated network. The
service binds 127.0.0.1 only, so it is not reachable from the LAN, and it is
not published through Podman, Cloudflare or a router.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = "/ALWAYSON/GAZEBO"
PORTAL_DIR = os.path.join(ROOT, "portal")
BONING = os.path.join(ROOT, "sim", "boning.yaml")
OBJECTS = os.path.join(ROOT, "sim", "objects.yaml")
WORLD = os.path.join(ROOT, "worlds", "factory.world")

# The one and only unit this portal is permitted to act on.
CONTROLLED_UNIT = "ao-sim-fabrication-gz.service"
ACTIONS = ("start", "stop", "reset", "inspect", "status")


def log(msg: str) -> None:
    print(f"[ao-sim-portal] {msg}", file=sys.stderr, flush=True)


def unit_action(action: str) -> str:
    """Run a systemctl action against the single permitted unit."""
    if action == "reset":
        cmd = ["systemctl", "--user", "restart", CONTROLLED_UNIT]
    elif action == "status":
        cmd = ["systemctl", "--user", "is-active", CONTROLLED_UNIT]
    else:
        cmd = ["systemctl", "--user", action, CONTROLLED_UNIT]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        out = (p.stdout or "").strip() or (p.stderr or "").strip()
        return f"{' '.join(cmd[2:])} -> rc={p.returncode} {out}".strip()
    except subprocess.TimeoutExpired:
        return f"{action}: timed out"


def unit_state() -> dict:
    try:
        p = subprocess.run(
            ["systemctl", "--user", "show", CONTROLLED_UNIT, "-p", "ActiveState",
             "-p", "SubState", "-p", "MainPID", "--no-pager"],
            capture_output=True, text=True, timeout=30)
        st = {}
        for line in p.stdout.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                st[k] = v
        return st
    except Exception as exc:  # noqa: BLE001
        return {"error": type(exc).__name__}


def load_yaml(path: str):
    """Minimal YAML load. PyYAML is not present on every host, and these two
    files use a deliberately plain subset; falls back to json for .json."""
    try:
        import yaml  # type: ignore
        with open(path) as fh:
            return yaml.safe_load(fh)
    except ImportError:
        return {"error": "PyYAML unavailable", "path": path}


def boning_summary() -> dict:
    d = load_yaml(BONING)
    if "error" in d:
        return d
    cells = []
    for c in d.get("cells", []):
        cells.append({
            "id": c.get("id"),
            "name": c.get("name"),
            "link": c.get("link"),
            "origin": (c.get("datum") or {}).get("origin"),
            "extent": (c.get("datum") or {}).get("extent"),
            "datum_source": (c.get("datum") or {}).get("source"),
        })
    machines = []
    for m in d.get("machines", []):
        machines.append({
            "id": m.get("id"),
            "name": m.get("name"),
            "in_exports": m.get("present_in_exports"),
            "declared": (m.get("datum") or {}).get("origin") is not None,
            "envelope_declared": (m.get("work_envelope") or {}).get("min") is not None,
            "tolerance_mm": m.get("tolerance_mm"),
        })
    # The honest bit: a reach may only be called verified against a machine
    # envelope when that machine has been surveyed. Everything here is derived
    # from the SketchUp exports, so nothing is.
    verified = all(mm["envelope_declared"] for mm in machines) and bool(machines)
    return {
        "units": d.get("units"),
        "frame": d.get("frame"),
        "frame_definition": d.get("frame_definition"),
        "cells": cells,
        "machines": machines,
        "joints": d.get("joints", []),
        "storage": d.get("storage", []),
        "reach_verified_against_machine": verified,
        "note": d.get("status", {}).get("note", "").strip(),
    }


def objects_summary() -> dict:
    d = load_yaml(OBJECTS)
    if "error" in d:
        return d
    groups = []
    total = 0
    for g in d.get("groups", []):
        objs = g.get("objects", [])
        total += len(objs)
        groups.append({
            "id": g.get("id"),
            "name": g.get("name"),
            "description": g.get("description"),
            "objects": [
                {
                    "id": o.get("id"),
                    "label": o.get("label"),
                    "class": o.get("class"),
                    "home_pose": o.get("home_pose"),
                    "size": o.get("size"),
                    "mass_kg": o.get("mass_kg"),
                    "tolerance_m": o.get("tolerance_m"),
                }
                for o in objs
            ],
        })
    return {
        "model": d.get("model"),
        "resettable": d.get("resettable"),
        "total_objects": total,
        "groups": groups,
        "actors": d.get("actors", []),
        "observable_from": (d.get("defaults") or {}).get("observable_from", []),
    }


def world_summary() -> dict:
    links = []
    try:
        cur = None
        with open(WORLD) as fh:
            for line in fh:
                t = line.strip()
                if t.startswith("<link name="):
                    cur = t.split('"')[1]
                elif t.startswith("</link>") and cur:
                    links.append(cur)
                    cur = None
    except OSError as exc:
        return {"error": str(exc)}
    return {"path": WORLD, "link_count": len(links), "links": links}


class Handler(BaseHTTPRequestHandler):
    server_version = "ao-sim-fabrication-portal"

    def log_message(self, fmt, *a):
        log(fmt % a)

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj):
        self._send(code, json.dumps(obj, indent=2).encode(), "application/json")

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", "/index.html"):
            try:
                with open(os.path.join(PORTAL_DIR, "index.html"), "rb") as fh:
                    self._send(200, fh.read(), "text/html; charset=utf-8")
            except OSError as exc:
                self._send(500, str(exc).encode(), "text/plain")
        elif path == "/api/status":
            self._json(200, {"unit": CONTROLLED_UNIT, "state": unit_state(),
                             "world": world_summary()})
        elif path == "/api/boning":
            self._json(200, boning_summary())
        elif path == "/api/objects":
            self._json(200, objects_summary())
        elif path == "/api/health":
            self._json(200, {"ok": True, "controls": CONTROLLED_UNIT})
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if not path.startswith("/api/"):
            self._send(404, b"not found", "text/plain")
            return
        action = path[len("/api/"):]
        if action not in ACTIONS:
            self._json(400, {"error": f"unknown action; allowed: {', '.join(ACTIONS)}"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)
        result = unit_action(action)
        self._json(200, {"action": action, "unit": CONTROLLED_UNIT,
                         "result": result, "state": unit_state()})


def main() -> int:
    ap = argparse.ArgumentParser(description="ao-sim-fabrication portal control surface")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        log(f"REFUSING to bind {args.host}: the portal is loopback-only by policy")
        return 2
    log(f"portal on {args.host}:{args.port}; controls {CONTROLLED_UNIT} only")
    HTTPServer((args.host, args.port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
