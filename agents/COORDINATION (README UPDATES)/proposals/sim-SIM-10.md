---
item: SIM-10
action: keep-open
evidence: |
  Measured 2026-10-04. §19's diagnosis reproduces exactly: the massing mesh has
  34 parts and every one is a cube signature, so size cannot distinguish a door.

  $ python3 scripts/simulation/split-collada-parts.py --list \
      GAZEBO/models/factory_assets/meshes/massing_fab.dae
  GAZEBO/models/factory_assets/meshes/massing_fab.dae: 34 parts
    size(150, 150, 150) x2
    size(161, 161, 161) x2
    size(152, 152, 152) x2
    size(190, 190, 190) x2
    size(81, 81, 81)   x2
    size(149, 149, 149) x1
    ... 22 further distinct sizes, all of the form size(n, n, n) ...
    size(56, 56, 61) x1     <- the only non-cube in the whole file

  33 of 34 parts are perfectly cubic (size(n,n,n)). The splitter separates by
  size, and a door is not distinguished from a wall by being a different cube.

  CORRECTION TO §19's OWN PREMISE. §19 names the file `massing_fab.dae` and
  describes its parts as "anonymous group_0-group_25". The filename is right.
  The node count is not:

  $ python3 -c "...re.findall(r'\bname=\"([^\"]*)\"', open(f).read())..."
  massing_fab.dae    group_N count: 13  ['group_0'...'group_12']
  massing_flat.dae   group_N count: 13  ['group_0'...'group_12']
  semantic-ish names (door|wall|floor): [] for both

  So the massing file carries 13 anonymous group nodes, not 26. The directory
  name is group_0-group_25, which is where the figure came from.

  This does not weaken the conclusion -- the operative fact is that NO part
  carries a semantic name and 33 of 34 are cubes, both verified directly -- but
  §19's stated part count is wrong and the compiler should correct it rather
  than propagate it. I am not editing §19; this proposal carries the correction.

  NOTE ON WHICH FILE IS LIVE. The world renders `massing_flat.dae`, not
  `massing_fab.dae` (factory.world line 183). Both were checked: identical 13
  group nodes, no semantic names in either.

  The fix is a re-export from SketchUp with named groups (door, wall, floor).
  That is a modelling action on the operator's side, on a file this session has
  no authority to regenerate. The splitter will then separate it with no code
  change -- the existing tool already keys on names.

  I did NOT guess a door colour or split the mesh heuristically. Doors keep the
  wall material, which is the honest state.
section: 10-simulation-architecture
---

SIM-10 stays open, blocked on a SketchUp re-export that only the operator can perform.
§19's diagnosis is confirmed precisely rather than approximately.

The massing mesh has **34 parts and 33 of them are exact cubes** — `size(n, n, n)` for
n = 81, 149, 150, 151, 152, 153, 154, 157, 158, 159, 161, 162, 163, 165, 167, 170, 173,
190, 191, 215, 269/271, 274 and others. The single exception is `size(56, 56, 61)`. The
splitter separates parts by size precisely because the parts are anonymous — **13**
`group_0`–`group_12` nodes and no `door`/`wall`/`floor` name anywhere in either massing
file — and a door standing in a wall is not smaller than the wall in a way that
survives rounding to an integer cube.

**A correction to §19, which I copied before checking.** §19 describes the parts of
`massing_fab.dae` as "anonymous `group_0`–`group_25`". There are 13 of them, not 26 —
I had taken the range from §19 rather than counting, and counted only when the number
would not reconcile with the other figures in my own evidence. The mistake is mine as
much as §19's: the range looks like a measurement, so quoting it felt safe. The
conclusion is unchanged and independently verified — no semantic names, 33 of 34 cubes
— but the compiler should correct the count rather than propagate it.

The remedy is already understood by the tooling and needs no code change: re-export
`massing_fab.dae` from SketchUp with semantic group names — door, wall, floor — and
`split-collada-parts.py` will separate them by name instead of by size. That is a modelling
action on the operator's file. I did not re-export it, did not modify the mesh, and did not
hand-assign a door material.

I want to be explicit about what I did **not** do. It would have been easy to make one of
those 33 cubes render a different colour and call the item done. That would be a guess
dressed as a fix: I cannot tell which cube is the door, I would be choosing on no evidence,
and a wrong guess is harder to detect later than an obviously-unresolved wall. Doors
keeping the wall material is the accurate state of the world, and §10 records it as such.

**What I got wrong.** I ran the splitter with no arguments first and got an argparse usage
error, and I recorded its `echo "exit=$?"` as `0` because the pipeline through `head` masked
the real exit status. The fault is measuring `$?` after a pipe instead of inside it — it
would have let me write "exit 0" as evidence of success for a command that never ran. I
re-ran it properly with `--list` and a real file argument; every result in this proposal
comes from that second run.
