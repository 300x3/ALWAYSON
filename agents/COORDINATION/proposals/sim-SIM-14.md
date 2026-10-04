---
item: SIM-14
action: close
evidence: |
  §19.1 recorded this item as absent ("That model does not exist"). The model
  exists in the world as live links. Measured 2026-10-03.

  $ curl -s http://127.0.0.1:8765/api/objects | head -c 260
  {"model": "rl_objects", "resettable": true, "total_objects": 9, "groups": [
   {"id": "marked-parts", "name": "Marked parts (inspection tasks)", "objects": [
    {"id": "part-a1", "label": "Marked part A1", "class": "marked_part",
     "home_pose": [6.2, 2.1, 0.8, "0 0 0"], "size": [0.12,0.12,0.06],
     "mass_kg": 1.2, "tolerance_m": null}, ...

  $ curl -s http://127.0.0.1:8765/api/status   # world link list, RL entries
  rl links: ['part_a1','part_a2','part_a3','stock_s1','stock_s2','stock_s3',
             'target_bin_a','target_bin_b','target_shelf']
  link_count 37

  $ grep -n 'BEGIN GENERATED: rl_objects' GAZEBO/worlds/factory.world
  623:    <!-- BEGIN GENERATED: rl_objects (scripts/simulation/build-rl-objects.py) -->

  $ grep -n '<model name="rl_objects">' -A1 GAZEBO/worlds/factory.world
      <model name="rl_objects">
        <static>false</static>

  Nine catalogue objects are instantiated as a non-static `rl_objects` model in
  the committed world: nine links, three groups, two actors, resettable to
  `home_pose`. They are world entities, not a YAML-only catalogue, which is the
  distinction the item asks about.
section: 10-simulation-architecture
---
§19.1 records SIM-14 as absent ("That model does not exist"). It exists. The nine
catalogue entries in `GAZEBO/sim/objects.yaml` are generated into the committed
`factory.world` as a non-static `rl_objects` model with nine links, and the running
server reports those links through the portal. The separation the item is really
concerned with -- RL entities held apart from the static `factory_assets` so a
training run can vary count and placement without rebuilding the world -- is
implemented by making the model non-static.

§10.3 in my section file now records the measurement instead of the §19 assertion.

**Closing this does not mean the generator is sound, and I found a real defect
while verifying it.** `build-rl-objects.py --check` exits 1 against the committed
world. Two separate causes, both reproduced on a copy under `/tmp/gen-test`:

1. The committed block carries `<specular>` and `<shininess>` on all nine
   materials, added by commit `fa3f8f6` ("material shininess"), which the
   generator was never taught to emit. Nine material lines differ.
2. `--write` strips the existing block and re-appends before `</world>`, so the
   model moves from line 623 to the end of the file -- after `safety_zones` and
   `conveyor_loops`. Regeneration is not idempotent in position even once cause 1
   is settled.

Neither is a §19 item, so I have left both open rather than renumbering into a
group I do not own. Cause 2 is the more dangerous of the two: a routine refresh
silently reorders three generated models in the world that the live server has
open. That belongs in a new SIM item.

**What I got wrong.** I ran `--write` against `/ALWAYSON` before I had copied the
tree to a scratch directory. That modified the shared live tree, which is exactly
the interference I am supposed to avoid; I caught it in the diff (149 insertions,
147 deletions, the rl_objects block relocated) and restored with
`git checkout -- GAZEBO/worlds/factory.world`, after which
`git status --short -- GAZEBO/ scripts/ quadlet/` printed nothing and the file
sha256 returned to `bce32f2a7ff035b4022db82d9a90267ca829261d08038d3e26e5ff3fe5f51053`.
I caused the fault, so I reverted only my own edit -- but the sequence was wrong,
and the diff is what caught it rather than my checking first.