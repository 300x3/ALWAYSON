#!/usr/bin/env python3
"""ALWAYS ON - generate the rl_objects model into the Gazebo world.

WHY THIS EXISTS. README Section 10.2.1 lists the reinforcement learning
objects as a baseline deliverable that must be individually addressable,
observable and resettable. GAZEBO/sim/objects.yaml declares them and names a
non-static model `rl_objects` as their home, but no such model existed in
factory.world. The portal's /api/objects therefore described objects Gazebo
had never instantiated.

This script closes that gap and keeps it closed. It renders objects.yaml into
an SDF `<model name="rl_objects">` block and splices it into the world. The
world is GENERATED in that one region: running it twice is a no-op, and
running it after editing objects.yaml is how you make the catalogue and the
simulation agree. Everything outside the marked region is untouched.

WHY A GENERATOR RATHER THAN HAND EDITING. The defect was a silent
disagreement between two files. Hand editing cannot stop that recurring;
generating one from the other makes divergence impossible to author without
deleting the marker block deliberately.

Each object gets a free-floating link with collision and explicit inertia, so
the arms can interact with it and the engine does not have to infer inertia.
The `id` is carried in a comment and as the link name, because gz-transport
addresses links by name and the portal addresses objects by that same id.

Usage:
  build-rl-objects.py --check     fail if the world is stale
  build-rl-objects.py --write     regenerate the block
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

import yaml

# Paths are resolved from this file, NOT hardcoded to /ALWAYSON.
#
# These were absolute literals until 2026-10-04 and that was a live hazard: a
# git worktree per session means `python3 build-rl-objects.py --write` run from
# a worktree silently rewrote the LIVE /ALWAYSON world instead of the checkout
# the operator was standing in. It also made `--check` meaningless in a
# worktree -- it reported on a different file than the one being edited, so it
# failed (or passed) for reasons unrelated to the work in front of you.
#
# Resolving from __file__ makes each checkout self-contained, which is what a
# per-session worktree requires. See proposals/sim-SIM-09.md.
ROOT = pathlib.Path(__file__).resolve().parents[2]
OBJECTS = str(ROOT / "GAZEBO" / "sim" / "objects.yaml")
WORLD = str(ROOT / "GAZEBO" / "worlds" / "factory.world")

BEGIN = "    <!-- BEGIN GENERATED: rl_objects (scripts/simulation/build-rl-objects.py) -->"
END = "    <!-- END GENERATED: rl_objects -->"

# The generated region that must follow ours. The world carries four generated
# regions in a fixed order -- rl_objects, safety_zones, conveyor_loops,
# elevation cameras -- and rl_objects being the first of them is what makes a
# reorder detectable at all. Verified by measurement, not assumed: the block
# sits at line 543 with safety_zones at 695.
SUCCESSOR = "safety_zones"

# Per-class visual colours, distinct from the static world (walls dark tan,
# belts blue, arms orange) so a trainable object is never mistaken for scenery.
COLOURS = {
    "marked_part": (0.85, 0.15, 0.15, 1.0),   # red
    "stock_item":  (0.20, 0.45, 0.80, 1.0),   # blue
    "task_target": (0.10, 0.70, 0.35, 1.0),   # green
}
DEFAULT_COLOUR = (0.80, 0.80, 0.10, 1.0)

# Shared specular response for every generated object. Added 2026-10-04: the
# specular/shininess pair had been added to factory.world BY HAND inside the
# generated block, which is precisely the divergence the generator exists to
# prevent. `--check` had therefore been failing continuously (exit 1) and no
# one could tell a real catalogue drift from this cosmetic hand edit, so the
# guard was effectively disarmed. Declaring the values here makes the world
# reproducible from the catalogue again, and --check regains its meaning.
#
# Carried over from main (a05f018); this branch's copy predated the fix, which
# is why --check failed at HEAD here. See proposals/sim-SIM-09.md.
SPECULAR = (0.30, 0.30, 0.30, 1.0)
SHININESS = 24


def esc(name: str) -> str:
    """SDF link names cannot contain some characters; keep ids stable."""
    return re.sub(r"[^A-Za-z0-9_]", "_", name)


def colour_of(obj: dict):
    return COLOURS.get(obj.get("class"), DEFAULT_COLOUR)


def render_inertial(mass: float, size) -> list:
    """Solid-box inertia from the object's own mass and size.

    Explicit so the physics engine never has to infer it from collision
    geometry, which is what produces the "missing <inertial>" warning for
    small dynamic bodies in gz-sim 10.
    """
    lx, ly, lz = size
    ix = mass * (ly * ly + lz * lz) / 12.0
    iy = mass * (lx * lx + lz * lz) / 12.0
    iz = mass * (lx * lx + ly * ly) / 12.0
    return ["        <inertial>",
            f"          <mass>{mass}</mass>",
            f"          <inertia><ixx>{ix:.6f}</ixx><iyy>{iy:.6f}</iyy>"
            f"<izz>{iz:.6f}</izz>"
            "<ixy>0</ixy><ixz>0</ixz><iyz>0</iyz></inertia>",
            "        </inertial>"]


def render_object(obj: dict) -> list:
    # The link pose MUST carry home_pose. The rl_objects model sits at the world
    # origin, so a link left at 0 0 0 stacks every object on the origin instead
    # of at its catalogued home. That is invisible in the log and only shows up
    # as "the objects are not where the catalogue says they are".
    home = obj.get("home_pose", [0, 0, 0, 0, 0, 0])
    flat: list = []
    for v in (home if isinstance(home, (list, tuple)) else [home]):
        # objects.yaml writes the trailing roll/pitch/yaw as one flow string:
        #   home_pose: [6.20, 2.10, 0.80, 0 0 0]
        if isinstance(v, str):
            flat.extend(v.strip().strip("[]").split())
        else:
            flat.append(v)
    home = [float(v) for v in flat]
    while len(home) < 6:
        home.append(0.0)
    pose = " ".join(f"{v:g}" for v in home)
    size = [float(v) for v in obj.get("size", [0.1, 0.1, 0.1])]
    mass = float(obj.get("mass_kg", 1.0))
    r, g, b, a = colour_of(obj)
    box = f"<box><size>{size[0]} {size[1]} {size[2]}</size></box>"
    o = [f'      <link name="{esc(obj["id"])}">',
         f"        <pose>{pose}</pose>",
         f"        <!-- id={obj['id']} class={obj.get('class')} "
         f"home_pose={pose} -->",
         '        <visual name="visual">',
         f"          <geometry>{box}</geometry>",
         f"          <material><ambient>{r:.3f} {g:.3f} {b:.3f} {a:.3f}</ambient>"
         f"<diffuse>{r:.3f} {g:.3f} {b:.3f} {a:.3f}</diffuse>"
         f"<specular>{SPECULAR[0]:.2f} {SPECULAR[1]:.2f} {SPECULAR[2]:.2f} "
         f"{SPECULAR[3]:g}</specular><shininess>{SHININESS}</shininess></material>",
         "        </visual>",
         '        <collision name="collision">',
         f"          <geometry>{box}</geometry>",
         "        </collision>"]
    o.extend(render_inertial(mass, size))
    o.append("      </link>")
    return o
def render(cat: dict) -> str:
    model = esc(cat.get("model", "rl_objects"))
    groups = cat["groups"]
    total = sum(len(g["objects"]) for g in groups)
    out = [BEGIN,
           f"    <!-- Source of truth: GAZEBO/sim/objects.yaml "
           f"(schema {cat.get('schema_version')}).",
           f"         {total} objects in {len(groups)} groups, plus "
           f"{len(cat.get('actors', []))} actors.",
           "         Non-static so placement varies without touching "
           "factory_assets. -->",
           f'    <model name="{model}">',
           "      <static>false</static>",
           "      <pose>0 0 0 0 0 0</pose>"]
    for group in groups:
        out.append(f"      <!-- group: {group['id']} - {group.get('name', '')} -->")
        for obj in group["objects"]:
            out.extend(render_object(obj))
    out.append("    </model>")
    out.append(END)
    return "\n".join(out)


# The generated block is replaced IN PLACE. It was previously stripped and
# re-appended immediately before </world>, which is not position-idempotent: any
# real catalogue edit moved rl_objects to the end of the file and dragged
# safety_zones and camera_elev_massing up after it. The world stayed valid and
# lost no link, so nothing broke -- but a routine refresh produced a large
# reorder diff that the next reader cannot tell from a real geometry change.
# Fixing the block in place keeps a legitimate edit down to the block itself.
# See proposals/sim-SIM-15.md.
BLOCK_RE = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.S)


def strip_existing(s: str) -> str:
    """Remove a previously generated block so regeneration is idempotent.

    Normalises only the seam the removal creates -- and, separately, the gap
    before </world>, which is the second seam when a drifted block sat at the end
    of the file. Both are anchored; a blanket \\n{3,} collapse is not, and
    applying one globally corrupted the XML.
    """
    out = BLOCK_RE.sub("", s)
    out = re.sub(r"\n{3,}(?=\s*</world>)", "\n\n", out)
    return out


def successor_after(world: str, frm: int):
    """Name of the next generated region after offset `frm`, or None."""
    nxt = re.search(r"<!--\s*BEGIN GENERATED:\s*([A-Za-z_]+)", world[frm:])
    return nxt.group(1) if nxt else None


def rejoin(prefix: str, block: str, suffix: str) -> str:
    """Splice `block` between two halves with the world's own spacing.

    The committed world separates each generated region from its neighbours by
    exactly two newlines (one blank line) on the leading side and two on the
    trailing side -- measured, not assumed:

        '    </model>\\n\\n\\n    <!-- BEGIN GENERATED: rl_objects'   leading
        '    <!-- END GENERATED: rl_objects -->\\n\\n    <!-- BEGIN GENERATED: safety_zones'

    BLOCK_RE already consumes one trailing newline, so the seam is normalised
    here rather than by rewriting whole regions.
    """
    return prefix.rstrip("\n") + "\n\n\n" + block.rstrip("\n") + "\n\n" + \
        suffix.lstrip("\n")


def splice(world: str, block: str) -> tuple:
    """Return (new_world, how) placing `block` at its canonical position.

    Canonical position is immediately before the SUCCESSOR region's BEGIN
    marker. If our block is already there it is replaced where it lies, which
    is what makes a routine refresh produce a diff confined to the block
    instead of reordering the world (SIM-15). If it has drifted, it is lifted
    out and re-inserted at the canonical position, so --write repairs a world
    that an earlier run reordered.
    """
    anchor_re = r"^[ \t]*<!--\s*BEGIN GENERATED:\s*" + SUCCESSOR + r"\b"

    def before_successor(text: str):
        a = re.search(anchor_re, text, flags=re.M)
        return a.start() if a else None

    m = BLOCK_RE.search(world)
    if m and successor_after(world, m.end()) == SUCCESSOR:
        # Already canonical: replace where it lies.
        return rejoin(world[:m.start()], block, world[m.end():]), "replaced in place"

    if m:
        # The block has drifted. Lift it out, then re-insert before the
        # successor region.
        #
        # Getting the blank lines right took two attempts. The first rstripped
        # the entire prefix rather than the junction, so the normalisation
        # landed at the end of the document instead of at the seam. The second
        # used a blanket \n{3,} collapse, which ate blank lines elsewhere and
        # corrupted the XML (gz sdf: Unable to read file). Both were caught by
        # diffing the healed world against the committed one and by parsing it.
        # BEFORE/AFTER are measured from the committed world, not chosen.
        at = before_successor(strip_existing(world))
        if at is None:
            raise SystemExit(
                f"cannot place rl_objects: no '{SUCCESSOR}' region in {WORLD} to "
                "anchor to, and the existing block is misplaced. Refusing to guess.")
        rest = strip_existing(world)
        return rejoin(rest[:at], block, rest[at:]), \
            f"relocated before {SUCCESSOR}"

    at = before_successor(world)
    if at is not None:
        return rejoin(world[:at], block, world[at:]), f"inserted before {SUCCESSOR}"
    # First run against a world with no generated regions at all. The block must
    # stay INSIDE <world>; appending past </sdf> is junk after the document
    # element and fails to parse.
    tail = re.sub(r"\s*</world>\s*</sdf>\s*$", "\n", world, flags=re.S)
    return tail.rstrip("\n") + "\n\n" + block + "\n\n</world>\n</sdf>\n", \
        "inserted before </world>"


def load() -> tuple:
    with open(OBJECTS) as fh:
        cat = yaml.safe_load(fh)
    with open(WORLD) as fh:
        return cat, fh.read()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="fail if the world is stale")
    ap.add_argument("--write", action="store_true", help="regenerate the block")
    args = ap.parse_args()

    cat, world = load()
    block = render(cat)

    if args.write:
        # Content may already match while position is wrong -- an older --write
        # could relocate the block. So decide on the splice result, not on
        # `block in world`, or a reordered world could never be repaired.
        new, how = splice(world, block)
        if new == world:
            print("rl_objects block already current; nothing written")
            return 0
        with open(WORLD, "w") as fh:
            fh.write(new)
        total = sum(len(g["objects"]) for g in cat["groups"])
        print(f"wrote {len(cat['groups'])} groups / {total} objects ({how}) into {WORLD}")
        return 0

    if block not in world:
        print("STALE: run scripts/simulation/build-rl-objects.py --write", file=sys.stderr)
        return 1
    # Content matches, but content alone proved nothing about position. The
    # world holds several generated regions and they have a canonical order;
    # rl_objects is followed by safety_zones. Assert that successor directly.
    # An earlier attempt used "a rewrite would be a no-op", which is worthless:
    # replacing in place is a fixed point of relocation, so a world whose block
    # had been moved to the end still reported OK. Measured, then discarded.
    m = BLOCK_RE.search(world)
    found = successor_after(world, m.end())
    if found != SUCCESSOR:
        print(f"MISPLACED: rl_objects block is followed by "
              f"{found or 'nothing'}, expected {SUCCESSOR}. "
              "A reorder, not a content change. Repair with --write",
              file=sys.stderr)
        return 1
    print(f"OK: rl_objects block matches objects.yaml and precedes {SUCCESSOR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())