GAZEBO - WORLD SETUP
====================

Location: /ALWAYSON/GAZEBO
This readme: README-GAZEBO-WORLD_MOVING.txt
Updated: 2026-10-01
Authoritative doc: /ALWAYSON/README.md (§10.2, §10.2.1, §19.4 items 30-31).
This file is the folder index; the README governs on any conflict.

FILES IN THIS FOLDER (root level, 5 items)
------------------------------------------

  File name                                                    Size (bytes)
  -----------------------------------------------------------  -----------
  09-SIMULATIONARMS.dae                                        2,428,555
  09-SIMULATIONCONVEYOR.dae                                      999,636
  09-SIMULATIONVEHICLES-ARMS.dae                               4,375,974
  \n09-SIMULATIONMASSING-ADUDOORS_FABRICATIONAREA.dae          2,209,716
  README-GAZEBO-WORLD_MOVING.txt  (this file)                  see below

ADDED STRUCTURE (2026-09-30 / 2026-10-01)
-----------------------------------------

  worlds/factory.world ................ canonical self-contained entry point
                                          (sun + ground + factory inlined)
  worlds-run/factory.world .............. container run copy (collisions
                                          visual-only; mesh URIs rewritten to
                                          file:///world/...)
  worlds-run/models/meshes/*.dae ........ dereferenced mesh copies for the
                                          container (originals untouched)
  models/factory_assets/model.sdf ....... reusable 4-link model artifact
  models/factory_assets/model.config .... model metadata (SDF 1.11)
  models/factory_assets/meshes/*.dae .... symlinks to the four root exports
  containers/gz-sim/Containerfile ....... gz-sim10-server image definition
  containers/foxglove-bridge/Containerfile  foxglove_bridge image (UNBUILT —
                                          ros-lyrical-* needs resolute suite;
                                          see journal 2026-10-01)
  portal/index.html ..................... HTML portal served at
                                          http://127.0.0.1:8765/

NOTES
-----

- The four .dae files are Collada mesh assets, all <unit inch 0.0254> Z_UP
  with in-place placement matrices: pose 0 0 0, scale 0.0254, shared frame.
- The MASSING-ADUDOORS_FABRICATIONAREA file's name literally begins with a
  newline byte (0x0A) before "09-SIMULATION...". Shown above with an escaped
  leading \n. Reached in-container via the massing_fab.dae symlink/copy.
  Flagged for operator review; do not rename without explicit approval
  (README.md hard rules 1-2).
- Git state 2026-10-01: GAZEBO/ is UNTRACKED (?? GAZEBO/). The main README
  records the portal at its §loopback row and §20 evidence row; nothing from
  this folder has been pushed to GitHub (HEAD == origin/main, 01f653c).

WORLD ASSEMBLY
--------------

All four .dae exports are combined in the self-contained entry point
worlds/factory.world (reusable artifact: models/factory_assets/model.sdf).

Placement: every link sits at pose 0 0 0 in the shared aligned frame.
Deliberate deviation, recorded in the world file: the vehicles overlay
duplicates arms/vehicles content, so it is lifted to pose 0 0 2.5 m to stay
inspectable; set it to 0 0 0 for exact in-place overlay.

RUNNING STACK (2026-10-01, verified live)
-----------------------------------------

  ao-gz-sim ..... Gazebo Sim 10.5.0 headless server in Podman
                  (localhost/gz-sim10-server, bridge net, GZ_IP=127.0.0.1,
                  GZ_PARTITION=alwayson_fabrication_sim). Log shows only
                  non-fatal CustomMeshShape normal-count warnings (SketchUp
                  edge/shelving submeshes ignored for COLLISION; visuals
                  intact). Visual-only collisions in the container run copy.
  gazebo-portal . nginx:alpine on bridge net, 127.0.0.1:8765->80 (loopback
                  only), /ALWAYSON/GAZEBO mounted ro. Serves portal/index.html
                  + world.sdf + model.sdf + readme.txt, all verified 200.
  Link .......... http://127.0.0.1:8765/

Foxglove: NOT RUNNING. No foxglove_bridge binary on host; container build
fails (ubuntu:24.04 resolves noble, ros-lyrical-* needs resolute suite +
libpython3.14). One host `sudo apt-get install -y ros-lyrical-foxglove-bridge`
unblocks the host-run path. Desktop app: https://foxglove.dev/download,
then open ws://localhost:8766 after starting the bridge.

Launch (host, after apt install):  gazebo /ALWAYSON/GAZEBO/worlds/factory.world
Valid:   gz sdf --check -> Valid; --print shows ground_plane + factory/4 links.

Rules applying to this world (from /ALWAYSON/README.md):
  - §10.2 (line 2002): models/worlds live under the domain unit's directories
    as committed *.sdf + supporting files, NOT fetched at runtime. Current
    gap: canonical worlds/factory.world uses file:// mesh URIs (no
    GZ_SIM_RESOURCE_PATH yet, cf. §10.1 line 1842); the container run copy in
    worlds-run/ rewrites them to file:///world/.... Reconcile when this world
    is adopted into ao-sim-fabrication.
  - §10.2 (line 1990-1994): vehicle and fabrication domains require SEPARATE
    ardupilot_gazebo build/install, Fuel model dirs, plugin paths, Gazebo
    partitions. We set GZ_PARTITION=alwayson_fabrication_sim only; the rest is
    missing (no Fuel dirs, no plugin paths, no per-domain builds).
  - §10.2.1: still missing per this list — datum per cell (we ship one
    unrotated vehicle view instead), algorithm per cell, RL bookkeeping per
    cell, matching GUIs (Foxglove blocked, §19.4 items 30-31), and portal
    start/stop/reset/operation (line 2037; ours is an index page, not inside
    ao-sim-fabrication). "3D world setup ... still open" (WORK 000801/ST-08).
  - §10.2 (line 2009): large meshes via Git LFS or separate artifact repo;
    models not committed until data is staged. GAZEBO/ untracked is compliant.
  - §16 (line 3452): sim-gz-server.log must exist while the server runs.
    Currently only in container logs: podman logs ao-gz-sim.
  - §4.3: simulation must never command live machinery (ao-fabrication owns
    real production data in a_fab).
  - Env: ROS_DOMAIN_ID=22, GZ_PARTITION=alwayson_fabrication_sim.
  - §17: sim result archives are per-domain (ao-sim-vehicle /
    ao-sim-fabrication own their artifacts, lines 2065-2066); our loose
    ao-gz-sim / gazebo-portal containers belong to neither domain yet.

