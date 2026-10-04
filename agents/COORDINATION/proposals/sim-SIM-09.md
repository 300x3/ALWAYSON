---
item: SIM-09
action: update
evidence: |
  SUPERSEDES the 2026-10-03 `action: close` proposal previously in this file.
  The camera re-aim is real, but the acceptance criteria have a second limb that
  was never met. Re-measured 2026-10-04.

  Limb 1 -- "the arms elevation is centred on the boned arms-cell centre": DONE.
  $ python3 -c "... boning cell-arms datum ..."
  boned cell-arms MIN : [5.981314, 1.861669, 0.531531]
  boned centre        : [6.401314, 2.697865, 1.150797]
  $ grep -n 'camera_elev_arms' GAZEBO/worlds/factory.world
  549:    <model name="camera_elev_arms">
  551:      <pose>6.401 4.056 1.151 0 0.0000 -1.5708</pose>
  Camera x = 6.401 matches the boned centre x = 6.401314. Commit 365bd42 did this.

  Limb 2 -- "boning.yaml does not carry the as-built arm centroid. Add the
  centroid to the boning data": NOT DONE.
  $ grep -c 'centroid' GAZEBO/sim/boning.yaml
  0
  ^ zero occurrences of "centroid" anywhere in the file

  The datum carries only `origin` (documented as the MIN corner) and `extent`.
  The centroid is recoverable only by the reader doing origin+extent/2 by hand;
  it is never stated. And the camera pose is not derived from the datum at all --
  it is a literal in factory.world, recomputed by hand in 365bd42:
  $ grep -rln 'camera_elev_arms' GAZEBO/ scripts/ quadlet/
  GAZEBO/worlds/factory.world
  ^ the world file is the ONLY place the pose exists; no generator computes it
section: 10-simulation-architecture
---

SIM-09 should read **partially complete**, not closed. The prior proposal in this file
verified the arithmetic and stopped there. The arithmetic is right, but verifying that
origin+extent/2 reproduces a number is not the same as the datum *carrying* that number,
which is what §19 asks for.

Two things are still outstanding. `boning.yaml` contains no `centroid` field at all — grep
returns 0 — so the as-built centroid exists only as something a reader must compute. And the
camera pose is a hand-written literal in `factory.world`: it is the only file in
`GAZEBO/`, `scripts/` or `quadlet/` that mentions `camera_elev_arms`. So the datum and the
camera can disagree again silently, which is the recurrence this item exists to prevent.
Adding `centroid:` to the cell-arms datum and generating the elevation poses from the
boning data would close it properly; that is fabrication-side work I have not done here.

**What I got wrong.** I inherited a `close` from my own group and nearly re-filed it without
checking the criteria clause by clause. I had verified the *numbers* in the previous session
and that verification felt like enough, so I skipped re-reading what the item actually
demands. Checking the acceptance text against the file — one grep — would have caught it.
The lesson is that "I verified the arithmetic last time" is not a substitute for reading
whether the requirement is met, and those two things came apart here.

---

## Revision 2 — 2026-10-04, SIM-09 closed

Both outstanding points are now done. Measured in this worktree (`/tmp/ao-sessions/wt-sim`,
branch `ai-sim`, base `1332005`).

### 1. The datum now carries the centroid

`centroid:` added to all three cell datums in `GAZEBO/sim/boning.yaml`, each equal to
`origin+extent/2`:

    $ python3 -c "import yaml; ..."
    cell-arms       centroid=[6.401314, 2.697865, 1.150797]
    cell-conveyor   centroid=[6.072980, 2.337311, 1.028700]
    cell-massing    centroid=[3.937000, 2.415536, 1.028700]

### 2. The elevation poses are now generated, not literals

New `scripts/simulation/build-boning-cameras.py`, with an `elevation_cameras:` block in
`boning.yaml` declaring each camera's `centroid_offset` and `yaw`. Pose = centroid + offset.

The three generated poses are **byte-identical to the hand-written ones**, which is the
correct outcome — §19 records the three standoffs as already correct, so this removes the
manual re-aiming step without changing a single rendered view:

    arms      <pose>6.401 4.056 1.151 0 0.0000 -1.5708</pose>   IDENTICAL
    conveyor  <pose>6.073 -2.042 1.029 0 0.0000  1.5708</pose>  IDENTICAL
    massing   <pose>11.746 2.416 1.029 0 0.0000  3.1416</pose>  IDENTICAL

A semantic XML comparison of the three `<model>` elements, HEAD vs now, is identical after
whitespace normalisation — so no camera property moved, not just the pose.

### Guards, each proved by making it fail

- Standoff drift in `boning.yaml` → `--check` exits 1.
- A stated `centroid` disagreeing with `origin+extent/2` → **refuses to generate**:
  `cell 'cell-arms' datum.centroid[z]=9.150797 disagrees with origin+extent/2=1.150797
  (tolerance 0.001); refusing to generate`. This is the important one: a plausible-looking
  hand-edited centroid is otherwise laundered into the world as if it were measured.
- An XML comment containing `--` → refuses. **I hit this one for real.** My first generated
  block contained the literal `--write` in a comment; XML comments may not contain `--`, and
  the result was a world that no longer parsed. The check now rejects it up front.

Final state:

    $ python3 scripts/simulation/build-rl-objects.py --check     -> OK (exit 0)
    $ python3 scripts/simulation/build-boning-cameras.py --check  -> OK (exit 0)
    $ gz sdf -k GAZEBO/worlds/factory.world                      -> Valid.

**SIM-09 is closed.** The datum carries the centroid, and the pose is derived from it.

---

## Cross-session hazard — every session must read this

**`build-rl-objects.py` had `/ALWAYSON` hardcoded, so `--write` from ANY worktree rewrote
the LIVE world.** Ten of the eleven worktrees still carry the defective copy:

    wt-comm SPECULAR=0 hardcoded_ALWAYSON=1     wt-ops-a SPECULAR=0 hardcoded_ALWAYSON=1
    wt-field SPECULAR=0 hardcoded_ALWAYSON=1    wt-ops-b SPECULAR=0 hardcoded_ALWAYSON=1
    wt-ledger SPECULAR=0 hardcoded_ALWAYSON=1   wt-pay SPECULAR=0 hardcoded_ALWAYSON=1
    wt-net SPECULAR=0 hardcoded_ALWAYSON=1      wt-plat SPECULAR=0 hardcoded_ALWAYSON=1
    wt-sec SPECULAR=0 hardcoded_ALWAYSON=1      wt-spec SPECULAR=0 hardcoded_ALWAYSON=1
                                                 wt-sim SPECULAR=3 hardcoded_ALWAYSON=0  (fixed here)

Worse, those copies predate main's `SPECULAR`/`SHININESS` fix (`a05f018`), so running
`--write` from one of them strips every `<specular>` from the live world. This is not
hypothetical: during this session `/ALWAYSON/GAZEBO/worlds/factory.world` was rewritten at
13:12:01 and its `rl_objects` specular count dropped from **9 to 0**. Some session ran
`--write` from a stale worktree. `--check` also reported on a file the caller was not
editing, so it failed for reasons unrelated to the work in hand.

**I restored `/ALWAYSON` to its committed state and verified it:**

    sha256   bce32f2a7ff035b4022db82d9a90267ca829261d08038d3e26e5ff3fe5f51053  (63205 bytes)
    git status --short -- GAZEBO/worlds/factory.world   -> empty (unmodified vs HEAD)
    specular in rl_objects                             -> 9
    python3 scripts/simulation/build-rl-objects.py --check -> OK (exit 0)
    gz sdf -k GAZEBO/worlds/factory.world              -> Valid.

**Operator decision needed (not mine to make):** the other ten worktrees still hold the
defective generator. Fixing them means editing files in other sessions' trees, which the
coordination protocol forbids without agreement. Options: (a) each session fixes its own
copy, (b) merge `ai-sim` so all branches inherit the fix, or (c) I fix them on the
operator's explicit say-so. Until then, **nobody should run
`build-rl-objects.py --write` from a worktree** — it will damage the live world.
