#!/usr/bin/env python3
"""Generate conveyor loops, drive motorboxes and carried loads into factory.world.

Reads GAZEBO/sim/conveyor_loops.yaml and emits SDF into factory.world between
generated markers. The block is regenerated wholesale each run, so the script is
idempotent and the YAML is the single source of truth.

Edit the YAML, not the world.
"""
from __future__ import annotations

import argparse
import math
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, "GAZEBO", "sim", "conveyor_loops.yaml")
WORLD = os.path.join(ROOT, "GAZEBO", "worlds", "factory.world")

BEGIN = "    <!-- BEGIN GENERATED: conveyor_loops -->"
END = "    <!-- END GENERATED: conveyor_loops -->"


def esc(v: float) -> str:
    return f"{v:.4f}".rstrip("0").rstrip(".")


def mat(d: dict, indent: str) -> list[str]:
    return [
        f"{indent}<material>",
        f"{indent}  <ambient>{d['ambient']}</ambient>",
        f"{indent}  <diffuse>{d['diffuse']}</diffuse>",
        f"{indent}  <specular>{d['specular']}</specular>",
        f"{indent}  <shininess>{d['shininess']}</shininess>",
        f"{indent}</material>",
    ]


def box_visual(name, size, pose, material, indent="        ") -> list[str]:
    return [
        f'{indent}<visual name="{name}">',
        f"{indent}  <geometry><box><size>{esc(size[0])} {esc(size[1])} "
        f"{esc(size[2])}</size></box></geometry>",
        f"{indent}  <pose>{esc(pose[0])} {esc(pose[1])} {esc(pose[2])} 0 0 0</pose>",
    ] + mat(material, indent + "  ") + [
        f"{indent}</visual>",
    ]


def build_loop(tag, ox, oy, deck, cfg, load, belts, out):
    """One rectangular belt circuit plus its motorbox and its carried load.

    `belts` collects the static belt geometry, which must live inside a model:
    a <visual> dropped straight into <world> is not valid SDF and Gazebo merely
    copies it, so the belt would never be placed. `out` collects the dynamic
    motorbox and load models.

    `tag` must be globally unique across every area, pair and loop: Gazebo
    rejects a world containing two models with the same name.
    """
    L = cfg["loop_run_length_m"]
    W = cfg["loop_width_m"]
    mb = cfg["motorbox"]
    msize = mb["size_m"]
    lsize = load["size_m"]

    # Belt deck: two long runs at y = oy and oy+W, two short returns at the ends.
    belt = {"ambient": "0.04 0.08 0.18 1", "diffuse": "0.14 0.29 0.68 1",
            "specular": "0.30 0.32 0.36 1", "shininess": "32"}
    for i, y in enumerate((oy + msize[1] / 2, oy + W - msize[1] / 2)):
        belts += box_visual(f"{tag}_belt{i}", (L, msize[1], 0.014),
                            (ox + L / 2, y, deck), belt)
    for i, x in enumerate((ox + msize[0] / 2, ox + L - msize[0] / 2)):
        belts += box_visual(f"{tag}_ret{i}", (msize[0], W - 2 * msize[1], 0.014),
                            (x, oy + W / 2, deck), belt)

    # Motorbox at the head of the circuit. Its own model so it can later take a
    # revolute joint and a motor; the load sits downstream of it.
    mx = ox + msize[0] / 2
    my = oy + W / 2
    steel = {"ambient": "0.17 0.18 0.19 1", "diffuse": "0.62 0.64 0.67 1",
             "specular": "0.85 0.86 0.90 1", "shininess": "72"}
    out += [
        f'    <model name="{tag}_motorbox">',
        "      <pose>{} {} {} 0 0 0</pose>".format(esc(mx), esc(my), esc(deck - msize[2] / 2 - 0.007)),
        '      <link name="gearbox">',
        f"        <inertial>",
        f"          <mass>{mb['mass_kg']}</mass>",
        f"          <inertia><ixx>0.09</ixx><iyy>0.09</iyy><izz>0.11</izz>"
        f"<ixy>0</ixy><ixz>0</ixz><iyz>0</iyz></inertia>",
        f"        </inertial>",
    ] + box_visual("housing", msize, (0, 0, 0), steel) + [
        '        <collision name="collision">',
        f"          <geometry><box><size>{esc(msize[0])} {esc(msize[1])} "
        f"{esc(msize[2])}</size></box></geometry>",
        "        </collision>",
        "      </link>",
        "    </model>",
    ]
    # NO LOAD IS GENERATED. The operator is modelling the bins and crates
    # themselves and has said these are sized and placed wrongly, so the
    # generator deliberately emits only the belt circuit and its motorbox.
    # The YAML still records what each area carries, as documentation.
    return belts, out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="splice into factory.world")
    ap.add_argument("--dry-run", action="store_true", help="report only")
    args = ap.parse_args()

    with open(SPEC) as fh:
        doc = yaml.safe_load(fh)
    cfg = doc["defaults"]
    out: list[str] = []
    counts = {}
    seen: set[str] = set()
    for aid, area in doc["areas"].items():
        ax, ay, _ = area["origin"]
        n = 0
        belts: list[str] = []
        for pair in area["pairs"]:
            px, py = pair["at"]
            # Each pair sits at its own deck height: the storage has a low and a
            # high pair, the cold store a freezer, fridge and pantry pair.
            deck = pair["deck_m"]
            label = pair["label"]
            for loop_id in pair["loops"]:
                # The two loops of a pair sit side by side across the belt
                # width, otherwise both land on the same spot and overlap.
                oy = ay + py + loop_id * (cfg["loop_width_m"] + cfg["pair_gap_m"])
                # Tag must be unique across area+pair+loop: loop_id alone repeats
                # once per pair, and Gazebo rejects duplicate model names.
                tag = f"{aid}_{label}_l{loop_id}"
                assert tag not in seen, f"duplicate loop tag {tag}"
                seen.add(tag)
                belts, out = build_loop(tag, ax + px, oy, deck, cfg,
                                        area["load"], belts, out)
                n += 1
        counts[aid] = n
        # Belt geometry is static and belongs in a model of its own. It must sit
        # inside a <link>: this SDF parser rejects both a <visual> directly under
        # <world> ("child of element[world], not defined in SDF") and one
        # directly under <model> ("child of element[model], not defined in
        # SDF"), logging a warning and copying the element instead of placing
        # the geometry.
        out = ([f'    <model name="{aid}_conveyor">',
                "      <static>true</static>",
                "      <pose>0 0 0 0 0 0</pose>",
                '      <link name="belt_frame">']
               + belts
               + ["      </link>", "    </model>"] + out)

    for aid, n in counts.items():
        print(f"[{aid}] {n} loops, {n} motorboxes (no loads generated)")
    print(f"total loops {sum(counts.values())}, "
          f"motorboxes {sum(counts.values())}")

    if args.dry_run or not args.write:
        return 0

    with open(WORLD) as fh:
        s = fh.read()
    block = "\n".join([BEGIN] + out + [END, ""])
    if BEGIN in s and END in s:
        pre, rest = s.split(BEGIN, 1)
        _, post = rest.split(END, 1)
        s = pre + block + post
    else:
        s = s.replace("</world>", block + "</world>")
    with open(WORLD, "w") as fh:
        fh.write(s)
    print(f"wrote {len(out)} SDF lines into {WORLD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
