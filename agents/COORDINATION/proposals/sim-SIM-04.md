---
item: SIM-04
action: keep-open
evidence: |
  Measured 2026-10-04. The vehicle 3D world does not exist. There is one world in the
  repository and it is the fabrication one.

  $ ls GAZEBO/worlds/
  factory.world
  ^ a single file. No vehicle.world, no rover.world, no airframe world.

  $ ls GAZEBO/
  09-SIMULATIONVEHICLES-ARMS.dae
  09-SIMULATIONARMS.dae
  09-SIMULATIONCONVEYOR.dae
  09-SIMULATIONMASSING-ADUDOORS_FABRICATIONAREA.dae
  COMPATIBILITY.md  README-GAZEBO-WORLD_MOVING.txt
  containers  handoff.md  models  portal  sim  worlds  worlds-run

  A vehicle/arms mesh exists, but nothing consumes it as a world: the only world is
  fabrication, and the vehicle Quadlet is SITL only with no viewer.

  $ ls quadlet/sim-vehicle/
  ao-ardupilot-sitl.container

  $ ls scripts/simulation/ | grep -i vehicle
  export-vehicle-manifest.sh
  run-vehicle-scenario.sh
  ^ scripts exist for the vehicle, which is why the item reads as outstanding work
    rather than as never-started. The scripting is there; the world is not.

  Every limb of the acceptance criteria is therefore unmet for the vehicle:
    - world setup scripted and repeatable      -> no world to script
    - boning frame and tolerances exported    -> no vehicle boning data
    - RL objects addressable and resettable   -> no vehicle objects.yaml
    - fully settable from the HTML portal     -> portal serves factory.world only
section: 10-simulation-architecture
---

SIM-04 stays open, and unlike most of my group it is not partially done — **the vehicle 3D
world does not exist**. `GAZEBO/worlds/` contains exactly one file, `factory.world`, which is
the fabrication world. There is no vehicle world, so all four acceptance limbs are unmet
rather than partly met: there is nothing to script, no vehicle boning data to export, no
vehicle RL objects, and the portal serves the fabrication world only.

Worth recording because it is the opposite of what the item's wording suggests: the
*scaffolding* for the vehicle side is well advanced. `GAZEBO/` holds
`09-SIMULATIONVEHICLES-ARMS.dae`, and `scripts/simulation/` contains both
`run-vehicle-scenario.sh` and `export-vehicle-manifest.sh`. So this is a missing
assembly rather than a project that never started, and that is a real distinction for whoever
picks it up.

I did not build a vehicle world. That is new Gazebo content, it needs the real vehicle
geometry and a boned frame agreed against the actual airframe, and fabricating a plausible
world file here would produce exactly the kind of invented geometry this session is supposed
to be eliminating.

**What I got wrong.** I opened SIM-04 planning to check whether the *boning* was right,
carrying SIM-09's framing across from the fabrication side. On the vehicle side there is no
boning to check — no world, no `boning.yaml`, no datum. I was auditing the correctness of
something that had not been built, which is the §10.3 lesson again: establish that the
artifact exists before measuring it.
