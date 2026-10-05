---
item: SIM-15
action: close
evidence: |
  SUPERSEDES the 2026-10-04 `action: create` proposal previously in this file. The
  defect is now fixed in scripts/simulation/build-rl-objects.py. All measurements
  on scratch copies (/tmp/t4, /tmp/t5), never the live tree.

  THE FIX. The generated block is replaced at its canonical position instead of
  being stripped and re-appended before </world>. Canonical position is defined
  structurally, not by line number: immediately before the safety_zones region.
  The world carries four generated regions in a fixed order -- rl_objects,
  safety_zones, conveyor_loops, elevation cameras -- which is what makes a
  reorder detectable at all:

      $ grep -n 'BEGIN GENERATED' GAZEBO/worlds/factory.world
        543:    <!-- BEGIN GENERATED: rl_objects -->
        691:    <!-- BEGIN GENERATED: safety_zones -->
        721:    <!-- BEGIN GENERATED: conveyor_loops -->
        1356:   <!-- BEGIN GENERATED: elevation cameras -->

  A REAL CATALOGUE EDIT no longer reorders the world. part-a1/a3 home_pose
  6.20 -> 6.90 in GAZEBO/sim/objects.yaml:

      $ python3 scripts/simulation/build-rl-objects.py --check    -> STALE, exit 1
      $ python3 scripts/simulation/build-rl-objects.py --write
        wrote 3 groups / 9 objects (replaced in place)
      $ diff <committed> GAZEBO/worlds/factory.world | grep '^[0-9]'
        552,553c552,553
        582,583c582,583
      # only the two intended pose line pairs; all four generated regions
      # unmoved at 543/691/721/1356. Previously the same edit gave
      # rl_objects 547 -> 1289, safety_zones 695 -> 548, and
      # camera_elev_massing 1410 -> 1263.
      $ gz sdf -k GAZEBO/worlds/factory.world   -> Valid.
      $ grep -c '<link name=' ...               -> 37  (unchanged)

  --check NOW DETECTS A REORDER, which it never did. Content equality cannot see
  position, and position was the entire defect. Proven by making it fail on a
  world reordered exactly the way the old --write did (block moved to just
  before </world>):

      $ grep -n 'BEGIN GENERATED: rl_objects' GAZEBO/worlds/factory.world
        1285:    <!-- BEGIN GENERATED: rl_objects -->
      $ python3 scripts/simulation/build-rl-objects.py --check
        MISPLACED: rl_objects block is followed by nothing, expected
        safety_zones. A reorder, not a content change. Repair with --write
                                                            (exit 1)

  REPAIR IS EXACT. Healing that reordered world reproduces the committed file
  byte for byte -- the property that makes the fix trustworthy:

      $ python3 scripts/simulation/build-rl-objects.py --write
        wrote 3 groups / 9 objects (relocated before safety_zones)
      $ sha256sum GAZEBO/worlds/factory.world
        5667873ca41968bea3e41b68dbc03321a22e8553059271ec65b522a0657e7b26
      $ cmp GAZEBO/worlds/factory.world <committed world>
        BYTE-IDENTICAL TO COMMITTED
      $ python3 scripts/simulation/build-rl-objects.py --check  -> OK, exit 0
      $ gz sdf -k GAZEBO/worlds/factory.world                   -> Valid.
      $ grep -c '<link name=' ...                               -> 37

  IDEMPOTENCY and no collateral damage to the sibling generators:

      $ python3 scripts/simulation/build-rl-objects.py --write
        rl_objects block already current; nothing written
      $ sha256sum before / after a second --write  -> identical (876c8788...)
      $ python3 scripts/simulation/build-boning-cameras.py --check -> OK, exit 0
      $ python3 scripts/simulation/verify_safety_zones.py         -> exit 0

  THE LIVE TREE WAS NEVER A TARGET:

      $ sha256sum /ALWAYSON/GAZEBO/worlds/factory.world
        5667873ca41968bea3e41b68dbc03321a22e8553059271ec65b522a0657e7b26
      $ git -C /ALWAYSON status --short -- GAZEBO/worlds/factory.world \
                                   scripts/simulation/build-rl-objects.py
        (empty)
section: 10-simulation-architecture
---

`build-rl-objects.py --write` is now position-idempotent. It replaces the generated
block where the generator puts it — immediately before the `safety_zones` region — so a
legitimate catalogue edit produces a diff of the intended pose lines and nothing else,
instead of relocating `rl_objects` and dragging `safety_zones` and `camera_elev_massing`
after it.

The second half of the fix matters more than the first. `--check` previously compared
block *content* only, so a reordered world passed cleanly while its diff misrepresented
the change. `--check` now asserts the block is followed by its expected successor region
and reports `MISPLACED` (exit 1) when it is not, and `--write` relocates a drifted block
back to the canonical position. Healing a reordered world reproduces the committed world
byte for byte, verified with `cmp` and the sha256 above.

**What I got wrong.** Three attempts, and the first two were wrong in ways a happy-path
test would never have caught.

1. My first guard asserted that a rewrite would be a no-op. That is worthless:
   replacing in place is a *fixed point* of relocation, so a world whose block had been
   moved to the end still reported `OK`. I found this only because I ran the guard
   against a deliberately broken world. A check whose entire job is to catch a broken
   world cannot be validated by passing on a good one.
2. My first relocate implementation computed the successor's offset on the unmodified
   string and applied it to the already-shortened one, splitting an XML comment into
   `<` and `!--` and producing a world Gazebo refused to read
   (`Error Code 1: Unable to read file`).
3. The second attempt used a blanket `\n{3,}` collapse to tidy the seam, which ate
   blank lines across the whole document.

All three were caught by byte-comparing against the committed world and by parsing the
result — not by reading the code. One root cause underneath: I wrote the seam handling
from intuition instead of measuring the committed file's actual spacing, and I validated
the happy path instead of the failure it exists to catch. The separators in `rejoin()`
are now measured from the committed world and documented with the bytes they came from.

Note for other sessions: the `--write`-from-a-worktree hazard recorded in §10.5 is fixed
in this branch (paths resolve from `__file__`), but copies in other worktrees still
hardcode `/ALWAYSON`. Nobody should run `build-rl-objects.py --write` from one of those
until its session fixes it, because those copies also predate the `SPECULAR`/`SHININESS`
fix and would strip every `<specular>` from the live world.

