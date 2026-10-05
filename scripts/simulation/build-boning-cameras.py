#!/usr/bin/env python3
"""ALWAYS ON - derive the elevation camera poses from the boning data.

WHY THIS EXISTS. SIM-09 asked for two things: put the as-built cell centroid in
the boning data, and recompute the camera poses from it. The first was a data
change. This script is the second, and it is what stops the two drifting apart
again.

The defect was a silent disagreement. The three `camera_elev_*` poses in
factory.world were hand-written literals; their comment asserted they were
aimed at "a BONED cell centre from GAZEBO/sim/boning.yaml", but no code read
boning.yaml to produce them. So when commit 365bd42 corrected the cell-arms
datum, the cameras had to be re-aimed by hand in the same commit. Miss that
edit and the world still loads, still renders, and simply frames the wrong
thing -- the exact failure SIM-09 was raised to prevent.

So the region of factory.world holding the three elevation cameras is
GENERATED from boning.yaml. Running this twice is a no-op; running it after
editing a datum or a standoff is how the world and the boning data agree.

It also refuses to proceed if a `centroid:` in boning.yaml disagrees with
origin+extent/2. That check is the point: a hand-edited centroid that is merely
plausible would otherwise be laundered into the world as if it were measured.

The generated poses reproduce the previously committed ones exactly (SIM-09
records the three standoffs as correct), so adopting this changes no rendered
view -- it only removes the manual step that could have got it wrong.

Usage:
  build-boning-cameras.py --check     fail if the world is stale
  build-boning-cameras.py --write     regenerate the block
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

import yaml

# Paths are resolved from this file, NOT hardcoded to /ALWAYSON. The simulation
# scripts run from several checkouts at once (one git worktree per session), and
# a hardcoded absolute path means running --write here silently rewrites the
# live /ALWAYSON world instead of the checkout you are standing in.
ROOT = pathlib.Path(__file__).resolve().parents[2]
BONING = ROOT / "GAZEBO" / "sim" / "boning.yaml"
WORLD = ROOT / "GAZEBO" / "worlds" / "factory.world"

BEGIN = ("    <!-- BEGIN GENERATED: elevation cameras "
         "(scripts/simulation/build-boning-cameras.py) -->")
END = "    <!-- END GENERATED: elevation cameras -->"

# Metre tolerance between a stated centroid and origin+extent/2. Both are
# 6dp renderings of the same AABB, so they should agree to well under this; a
# real disagreement is orders of magnitude larger.
CENTROID_TOL = 1e-3


def centroid_of(cell: dict) -> list:
    """The stated centroid, after checking it against origin+extent/2."""
    datum = cell.get("datum") or {}
    stated = datum.get("centroid")
    if stated is None:
        raise SystemExit(
            f"cell {cell['id']!r} has no datum.centroid; SIM-09 requires the "
            f"as-built centroid to be stated in {BONING.name}")
    origin, extent = datum.get("origin"), datum.get("extent")
    if origin is None or extent is None:
        raise SystemExit(f"cell {cell['id']!r} datum lacks origin/extent")
    computed = [origin[i] + extent[i] / 2.0 for i in range(3)]
    for axis, name in enumerate("xyz"):
        if abs(stated[axis] - computed[axis]) > CENTROID_TOL:
            raise SystemExit(
                f"cell {cell['id']!r} datum.centroid[{name}]={stated[axis]} "
                f"disagrees with origin+extent/2={computed[axis]:.6f} "
                f"(tolerance {CENTROID_TOL}); refusing to generate")
    return [float(v) for v in stated]
def render(boning: dict) -> str:
    cells = {c["id"]: c for c in boning["cells"]}
    cams = boning.get("elevation_cameras") or []
    if not cams:
        raise SystemExit(f"{BONING.name} declares no elevation_cameras")

    out = [BEGIN,
           "    <!-- Source of truth: GAZEBO/sim/boning.yaml, block "
           "elevation_cameras.",
           "         Each pose is the cell's stated centroid plus its "
           "centroid_offset,",
           "         so re-aiming a view is a boning.yaml edit plus a write, "
           "never a",
           "         hand edit of this file. Generated; do not edit by hand. -->"]
    for cam in cams:
        cell = cells.get(cam["cell"])
        if cell is None:
            raise SystemExit(
                f"elevation camera {cam['id']!r} references unknown cell "
                f"{cam['cell']!r}")
        c = centroid_of(cell)
        off = cam["centroid_offset"]
        pose = [c[i] + float(off[i]) for i in range(3)]
        p = " ".join(f"{v:.3f}" for v in pose)
        name = cam["id"].replace("-", "_")
        out += [
            f"    <!-- Camera \"{cam['id']}\": elevation over "
            f"{cell.get('name', cam['cell'])}.",
            f"         Aimed at the boned centroid {c} of cell {cam['cell']},",
            f"         offset {off} and yawed {cam['yaw']} rad to face the "
            f"cell. -->",
            f'    <model name="camera_{name}">',
            "      <static>true</static>",
            f"      <pose>{p} 0 0.0000 {cam['yaw']}</pose>",
            f'      <link name="camera_{name}">',
            "        <pose>0 0 0 0 0 0</pose>",
            f'        <sensor name="camera_{name}" type="camera">',
            "          <pose>0 0 0 0 0 0</pose>",
            "          <always_on>1</always_on>",
            "          <update_rate>10</update_rate>",
            "          <visualize>0</visualize>",
            f"          <topic>{cam['topic']}</topic>",
            f'          <camera name="camera_{name}">',
            "            <horizontal_fov>0.6</horizontal_fov>",
            "            <image><width>640</width><height>480</height></image>",
            "            <clip><near>0.05</near><far>100</far></clip>",
            "          </camera>",
            "        </sensor>",
            "      </link>",
            "    </model>",
            ""]
    out.append(END)
    block = "\n".join(out)
    # An XML comment may not contain "--", and the generated block is mostly
    # comments. Writing one silently produces a world that no longer parses,
    # which is exactly the kind of quiet breakage a generator should not cause,
    # so it is checked here rather than discovered by the next --check run.
    for line in block.splitlines():
        if "--" in line.replace("<!--", "").replace("-->", ""):
            raise SystemExit(
                "refusing to generate: an XML comment may not contain '--': "
                f"{line.strip()!r}")
    return block


def strip_existing(world: str) -> str:
    """Remove a previously generated block so regeneration is idempotent."""
    return re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", "",
                  world, flags=re.S)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="fail if the world is stale")
    ap.add_argument("--write", action="store_true", help="regenerate the block")
    args = ap.parse_args()

    boning = yaml.safe_load(BONING.read_text())
    block = render(boning)
    world = WORLD.read_text()

    if args.write:
        if block in world:
            print("elevation cameras already current; nothing written")
            return 0
        if BEGIN not in world:
            print(f"note: adopting; no prior generated block in {WORLD}",
                  file=sys.stderr)
        new = strip_existing(world)
        # The block belongs INSIDE <world>, before its closing tag. Appending
        # after </sdf> would be junk after the document element.
        new = re.sub(r"\s*</world>\s*</sdf>\s*$", "\n", new, flags=re.S)
        new = new.rstrip("\n") + "\n\n" + block + "\n\n</world>\n</sdf>\n"
        WORLD.write_text(new)
        print(f"wrote {len(boning['elevation_cameras'])} elevation cameras "
              f"into {WORLD}")
        return 0

    if block in world:
        print("OK: elevation cameras match boning.yaml")
        return 0
    print("STALE: run scripts/simulation/build-boning-cameras.py --write",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())