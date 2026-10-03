#!/usr/bin/env python3
"""ALWAYS ON - resolve safety zones against the boned datums.

Computes each zone's world-space AABB from its boned cell datum plus the named
clearance, and states plainly which zones are resolved and which are not.

The point of this script is the honesty rule, not the arithmetic. A zone that
depends on an undeclared machine datum must never be reported as covering that
machine - the same rule boning.yaml already applies to machine envelopes, where
a null origin means a simulated reach cannot be called verified. `--strict`
exits non-zero on any unresolved zone so this can gate a task plan.

Usage:
  verify_safety_zones.py            print the resolved table
  verify_safety_zones.py --json     machine-readable
  verify_safety_zones.py --strict   non-zero exit if anything is unresolved
"""
from __future__ import annotations

import argparse
import json
import sys

import yaml

WORLD = "/ALWAYSON/GAZEBO/worlds/factory.world"
BEGIN = ("    <!-- BEGIN GENERATED: safety_zones "
         "(scripts/simulation/verify_safety_zones.py) -->")
END = "    <!-- END GENERATED: safety_zones -->"

# Zone volumes are visual only: no collision, no actuation.
# ALPHA 0.14 was invisible in practice - the volumes were present and correct
# in the SDF but could not be seen in the render, which defeats the purpose of
# a rehearsal marker. 0.35 reads clearly without hiding the geometry inside.
TINT = {"restricted": (0.95, 0.25, 0.20), "robot_reach": (0.95, 0.70, 0.15)}
ALPHA = 0.35
# Zone volumes are not drawn by default: the fabrication-floor zone encloses the
# whole building, so drawing it tints every camera and hides the simulation.
# Pass --visual to render them when inspecting the zone model itself.
SHOW_VISUALS = False

BONING = "/ALWAYSON/GAZEBO/sim/boning.yaml"
ZONES = "/ALWAYSON/GAZEBO/sim/safety_zones.yaml"


def resolve(zones_doc: dict, boning: dict) -> list:
    cells = {c["id"]: c for c in boning.get("cells", [])}
    clearances = zones_doc.get("clearances_m", {})
    out = []
    for z in zones_doc.get("zones", []):
        cell = cells.get(z.get("derived_from"))
        rec = {"id": z.get("id"), "kind": z.get("kind"),
               "derived_from": z.get("derived_from"),
               "clearance": z.get("clearance")}
        if cell is None:
            rec["resolved"] = False
            rec["reason"] = f"derived_from {z.get('derived_from')!r} is not a boned cell"
            out.append(rec)
            continue
        datum = cell.get("datum") or {}
        origin, extent = datum.get("origin"), datum.get("extent")
        if origin is None or extent is None:
            rec["resolved"] = False
            rec["reason"] = f"boned datum for {cell['id']} is undeclared"
            out.append(rec)
            continue
        c = clearances.get(z.get("clearance"))
        if c is None:
            rec["resolved"] = False
            rec["reason"] = f"clearance {z.get('clearance')!r} is not defined"
            out.append(rec)
            continue
        lo = [origin[i] - c for i in range(3)]
        hi = [origin[i] + extent[i] + c for i in range(3)]
        rec.update({"resolved": True, "min": [round(v, 4) for v in lo],
                    "max": [round(v, 4) for v in hi],
                    "clearance_m": c,
                    "centre": [round((lo[i] + hi[i]) / 2, 4) for i in range(3)]})
        out.append(rec)
    return out


def unresolved_machines(zones_doc: dict) -> list:
    return [u for u in zones_doc.get("unresolved_dependencies", [])]


def render_world_block(resolved: list) -> str:
    """SDF for the zone volumes. Visual only - deliberately no <collision>.

    A zone with collision geometry would stop an arm or an object entering it,
    which would be an interlock. This is a rehearsal marker, not a barrier, so
    it must not be able to change how anything moves.
    """
    lines = [BEGIN,
             "    <!-- Rehearsal-only zone volumes, DERIVED from boning.yaml cell"
             " datums plus",
             "         the named clearance. Visual only: no collision, no"
             " actuation, no interlock.",
             "         Generated - edit GAZEBO/sim/safety_zones.yaml, not here. -->",
             '    <model name="safety_zones">',
             "      <static>true</static>",
             "      <pose>0 0 0 0 0 0</pose>"]
    for z in resolved:
        if not z["resolved"]:
            continue
        mn, mx, c = z["min"], z["max"], z["centre"]
        size = [round(mx[i] - mn[i], 4) for i in range(3)]
        r, g, b = TINT.get(z["kind"], (0.9, 0.9, 0.2))
        lines += [
            f"      <!-- {z['id']} ({z['kind']}) derived from {z['derived_from']}"
            f" +{z['clearance']} m clearance -->",
            f'      <link name="{z["id"]}">',
            f"        <pose>{c[0]:.4f} {c[1]:.4f} {c[2]:.4f} 0 0 0</pose>"]
        if not SHOW_VISUALS:
            # Geometry stays in the SDF so the zones remain machine-readable and
            # verifiable, but nothing is drawn. zone-fabrication-floor encloses
            # the entire building, so rendering it washes every camera in flat
            # colour and destroys the view the operator is meant to watch.
            lines.append(
                "        <!-- volume not rendered: pass the visual flag"
                " to draw zones -->")
        else:
            lines += [
                '        <visual name="visual">',
                f"          <geometry><box><size>{size[0]} {size[1]}"
                f" {size[2]}</size></box></geometry>",
                f"          <material><ambient>{r} {g} {b} {ALPHA}</ambient>"
                f"<diffuse>{r} {g} {b} {ALPHA}</diffuse></material>",
                "        </visual>"]
        lines.append("      </link>")
    lines += ["    </model>", END]
    return "\n".join(lines)


def write_world_block(resolved: list) -> int:
    """Splice the zone block in before </world>. Idempotent."""
    import re
    block = render_world_block(resolved)
    with open(WORLD) as fh:
        world = fh.read()
    if block in world:
        print("safety_zones block already current; nothing written")
        return 0
    # Appending to the end of the file lands it after </sdf>, which is junk
    # after the document element. It must go before </world>.
    world = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", "", world, flags=re.S)
    world = re.sub(r"\s*</world>\s*</sdf>\s*$", "\n", world, flags=re.S)
    with open(WORLD, "w") as fh:
        fh.write(world.rstrip("\n") + "\n\n" + block + "\n\n</world>\n</sdf>\n")
    print(f"wrote {sum(1 for z in resolved if z['resolved'])} zone volumes into {WORLD}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if any zone is unresolved")
    ap.add_argument("--write-world", action="store_true",
                    help="regenerate the zone volumes in factory.world")
    ap.add_argument("--visual", action="store_true",
                    help="draw the zone volumes (off by default: the "
                         "fabrication-floor zone encloses the whole building "
                         "and tints every camera)")
    args = ap.parse_args()

    global SHOW_VISUALS
    SHOW_VISUALS = args.visual

    with open(BONING) as fh:
        boning = yaml.safe_load(fh)
    with open(ZONES) as fh:
        zones_doc = yaml.safe_load(fh)

    resolved = resolve(zones_doc, boning)
    bad = [r for r in resolved if not r["resolved"]]
    gaps = unresolved_machines(zones_doc)

    if args.write_world:
        return write_world_block(resolved)

    if args.json:
        print(json.dumps({
            "rehearsal_only": zones_doc.get("rehearsal_only"),
            "actuates_nothing": zones_doc.get("actuates_nothing"),
            "zones": resolved,
            "unresolved_dependencies": gaps,
            "interlocks": [
                {"id": i["id"], "name": i["name"],
                 "enforced_in_simulation": i["enforced_in_simulation"]}
                for i in zones_doc.get("interlocks", [])],
        }, indent=2))
    else:
        print(f"REHEARSAL ONLY - actuates nothing. "
              f"{len(resolved)} zones, {len(gaps)} unresolved dependencies.")
        for r in resolved:
            if r["resolved"]:
                print(f"  [ok]      {r['id']:24s} min={r['min']} max={r['max']}")
            else:
                print(f"  [UNRESOLVED] {r['id']:20s} {r['reason']}")
        for g in gaps:
            print(f"  [GAP]     {g['machine']:20s} {g['because']}")
        print("No interlock is enforced in the simulation; they report only.")

    return 1 if (args.strict and (bad or gaps)) else 0


if __name__ == "__main__":
    sys.exit(main())