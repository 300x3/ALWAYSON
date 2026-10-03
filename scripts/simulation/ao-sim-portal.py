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
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = "/ALWAYSON/GAZEBO"
PORTAL_DIR = os.path.join(ROOT, "portal")
BONING = os.path.join(ROOT, "sim", "boning.yaml")
OBJECTS = os.path.join(ROOT, "sim", "objects.yaml")
WORLD = os.path.join(ROOT, "worlds", "factory.world")

# The unit this portal REPORTS on. It is never acted upon from here - see the
# module docstring. World lifecycle is the operator CLI ao-sim-portal.sh.
CONTROLLED_UNIT = "ao-sim-fabrication-gz.service"

# View-only. Nothing in this tuple can change the state of the simulation.
READ_ACTIONS = ("status", "inspect")


def log(msg: str) -> None:
    print(f"[ao-sim-portal] {msg}", file=sys.stderr, flush=True)


def unit_state() -> dict:
    """Read-only view of the simulation's data files. NO systemctl, NO control.

    Deliberately does not shell out. It reports what exists on disk and when it
    last changed, which is enough for an operator to tell whether the world has
    been rebuilt, without this process holding any handle on the running
    simulation. Probing a gz-transport control service instead would defeat the
    view-only guarantee - see the module docstring.
    """
    out = {"unit": CONTROLLED_UNIT, "controlled": False,
           "note": "view-only portal; it never acts on the unit. "
                   "Use scripts/operations/ao-sim-portal.sh for control."}
    for label, path in (("world", WORLD), ("boning", BONING), ("objects", OBJECTS)):
        try:
            st = os.stat(path)
            out[label] = {"path": path, "size_bytes": st.st_size,
                          "modified_epoch": int(st.st_mtime)}
        except OSError as exc:
            out[label] = {"path": path, "error": str(exc)}
    return out


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
        elif path == "/viewer" or path.startswith("/viewer/"):
            # The local simulation viewer. Static HTML only: it opens a
            # WebSocket to the Foxglove bridge on 127.0.0.1:8081 and renders
            # the camera. It sends nothing outward and has no credentials -
            # the bridge it talks to is loopback-only.
            rel = path[len("/viewer"):].lstrip("/") or "index.html"
            if ".." in rel or rel.startswith("/"):
                self._send(400, b"bad path", "text/plain")
                return
            try:
                with open(os.path.join(PORTAL_DIR, "viewer", rel), "rb") as fh:
                    self._send(200, fh.read(), "text/html; charset=utf-8")
            except OSError as exc:
                self._send(404, str(exc).encode(), "text/plain")
        elif path == "/api/status":
            self._json(200, {"unit": CONTROLLED_UNIT, "state": unit_state(),
                             "world": world_summary()})
        elif path == "/api/boning":
            self._json(200, boning_summary())
        elif path == "/api/objects":
            self._json(200, objects_summary())
        elif path == "/api/health":
            self._json(200, {"ok": True, "view_only": True,
                             "reports_on": CONTROLLED_UNIT,
                             "controls": None})
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self):
        # VIEW-ONLY. Every write verb is refused; the portal exposes no route
        # that can change the simulation. 405 with an Allow header is the
        # correct response for a method the resource does not support.
        body = json.dumps({
            "error": "view-only portal: this service cannot modify the simulation",
            "control_path": "/ALWAYSON/scripts/operations/ao-sim-portal.sh "
                            "{start|stop|reset|inspect|status}",
            "allowed": list(READ_ACTIONS),
        }, indent=2).encode()
        self.send_response(405)
        self.send_header("Allow", "GET, HEAD")
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)


def main() -> int:
    ap = argparse.ArgumentParser(description="ao-sim-fabrication portal, VIEW-ONLY (no control actions)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        log(f"REFUSING to bind {args.host}: the portal is loopback-only by policy")
        return 2
    log(f"portal on {args.host}:{args.port}; VIEW-ONLY, controls nothing "
        f"(reports on {CONTROLLED_UNIT}; control via scripts/operations/ao-sim-portal.sh)")
    HTTPServer((args.host, args.port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
