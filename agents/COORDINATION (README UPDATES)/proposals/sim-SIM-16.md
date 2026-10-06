---
item: SIM-16
action: open
evidence: |
  **REV 2, 2026-10-05 second pass. Supersedes REV 1 of this same file (which remains accurate
  and is not retracted, except the camera claim corrected below).** SIM-16 is re-confirmed STILL
  OPEN and still requires an operator restart. What changed: the restart is now PROVEN SAFE
  rather than argued safe, the blast radius is measured and is much smaller than REV 1 implied,
  and one REV 1 claim is corrected.

  # 0. SIM-16 RE-CONFIRMED, unchanged. Re-measured, not quoted.
  $ podman inspect ao-sim-fabrication-gz --format '{{.State.StartedAt}} restarts={{.RestartCount}}'
  2026-10-03 18:19:21.186619129 -0700 PDT restarts=0
  $ podman exec ao-sim-fabrication-gz ps -o etimes= -p 1
  137327                                   # +1005 s since the REV 1 reading
  $ stat -c '%y %s' /ALWAYSON/GAZEBO/worlds/factory.world
  2026-10-04 15:45:38.213485858 -0700 62883
  # `podman ps` shows "Up 38 hours", which reads like a fresh start and hides this.

  # 1. THE RESTART IS PROVEN SAFE. Committed world loaded in a THROWAWAY container
  #    from the SAME pinned digest, SEPARATE GZ_PARTITION, bounded iterations, --rm.
  $ podman run --rm --name ao-sim-worldcheck \
      -e GZ_PARTITION=ao_sim_worldcheck_$$ -e GZ_SIM_RESOURCE_PATH=/ALWAYSON/GAZEBO/models \
      -e HOME=/tmp -v /ALWAYSON/GAZEBO:/ALWAYSON/GAZEBO:ro \
      --entrypoint /usr/libexec/gz/sim10/gz-sim-server \
      localhost/gz-sim10-server@sha256:55f8dbcf8decb0b97c6be7cf2fde8859b0fd05735c7a759df09a12e091933581 \
      /ALWAYSON/GAZEBO/worlds/factory.world -r -s -v 4 --iterations 400
  exit=0
  $ grep -c '\[err\]' /tmp/worldcheck.log
  0
  # 400 iterations, clean exit, zero errors. The committed world LOADS on the pinned image.
  # Only pre-existing warnings: '<gui><camera> can't be converted yet' and Ogre2Camera
  # SetVisibilityMask reserved-bit notices from the eight cameras.

  # 2. BLAST RADIUS, measured by hashing the entity inventory rather than reading it.
  $ for c in c24f673 78b4e60; do git show $c:GAZEBO/worlds/factory.world \
      | grep -oE '<(model|link) name="[^"]*"' | sort | sha256sum; done
  a95679bcc654bb2a7a5ff97817bfab19bca3918ce56165154343a83f1f066a57   # c24f673 (loaded)
  a95679bcc654bb2a7a5ff97817bfab19bca3918ce56165154343a83f1f066a57   # 78b4e60 (committed)
  # IDENTICAL. 167 changed lines total, confined to: the massing mesh URI, the massing
  # material block, and the POSITION of the camera_elev_arms block.
  # => boned datums, RL objects, safety zones, link poses and all EIGHT cameras are already
  #    CORRECT on the live server. Only the massing mesh and its material are stale.

  # 3. CORRECTION TO REV 1: camera_elev_arms is NOT missing from the loaded world.
  $ git show c24f673:GAZEBO/worlds/factory.world | grep -c '<model name="camera_elev_arms"'
  1
  $ git show HEAD:GAZEBO/worlds/factory.world | grep -c '<model name="camera_elev_arms"'
  1
  # pose identical in both: <pose>6.401 4.056 1.151 0 0.0000 -1.5708</pose>
  # The diff hunk '542,621d541' is a BLOCK RELOCATION, which diff renders as delete+insert.
  # SIM-09's fix IS rendered on the live server. I nearly filed a false regression on it.

  # 4. PORTAL BLIND SPOT, confirmed by reading the code, fix belongs to the portal's owner.
  #    world_summary() parses WORLD off disk; unit_state() os.stat's it and reports
  #    modified_epoch. Neither knows a load event happened, so /api/status calls the file
  #    authoritative across exactly the divergence it exists to reveal.
  #    Minimal fix: flag stale_since_restart when world.mtime > server.started. Both values
  #    are already reachable (os.stat + read-only podman inspect), so the view-only guarantee
  #    is preserved. This is CHEAPER than the dynamic_pose/info probe REV 1 proposed.

  STILL THE OPERATOR'S CALL, STILL NOT MINE: `systemctl --user restart
  ao-sim-fabrication-gz` is a live service restart. I proved it safe; I did not run it.
  No Quadlet edit is needed — the world is a bind mount, so the restart picks up the
  committed file as-is. That single command closes SIM-16.

  WHAT I GOT WRONG: I read a unified-diff hunk header as a semantic deletion and nearly
  filed a false regression against my own SIM-09 closure. I reached for diff output, which
  is optimised for humans skimming changes, when the question was "does entity X exist with
  value Y in both versions" — a counted grep answers that directly. Same class as the
  REV 1 error: accepting a representation's shape as evidence about the thing. Third pass
  running. Check the value, not the hunk.

  # --- REV 1 evidence, retained below, still accurate ---
  NEW FAULT, filed 2026-10-05 by the SIM session. Not in §19 yet — this takes the
  next free number in the SIM group. The running simulation server is executing a
  world file that is two commits behind the repository.

  # 1. The server has not restarted since before the world file was last edited.
  $ podman inspect ao-sim-fabrication-gz --format '{{.State.StartedAt}} {{.RestartCount}}'
  2026-10-03 18:19:21.186619129 -0700 PDT 0
  $ podman exec ao-sim-fabrication-gz ps -o etimes= -p 1
  136322
  $ stat -c '%y' /ALWAYSON/GAZEBO/worlds/factory.world
  2026-10-04 15:45:38.213485858 -0700
  $ date -u
  Mon Oct  5 15:11:23 UTC 2026

  # 2. The server logged ONE load and has never reloaded.
  $ grep 'Loading SDF world file' /ALWAYSON/logs/sim-gz-server.log.1 | tail -1
  2026-10-03T18:19:21.216791935-07:00 [info] [ServerPrivate.cc:697] Loading SDF
  world file[/ALWAYSON/GAZEBO/worlds/factory.world].
  $ # same grep filtered to timestamps later than 18:19:22 -> EMPTY
  $ grep -c 'Loading SDF world file' /ALWAYSON/logs/sim-gz-server.log
  0

  # 3. The file is read once, at startup: it is a bind mount, not a watch.
  $ podman inspect ao-sim-fabrication-gz --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'
  /ALWAYSON/GAZEBO -> /ALWAYSON/GAZEBO
  $ podman exec ao-sim-fabrication-gz cat /proc/1/cmdline | tr '\0' ' '
  /usr/libexec/gz/sim10/gz-sim-server /ALWAYSON/GAZEBO/worlds/factory.world -r -s -v 4

  # 4. WHAT IS LOADED vs WHAT IS COMMITTED. At 18:19:21 the working tree held
  #    c24f673 (committed 17:59:41); ec34c71 landed 18:21:13, i.e. 112 s AFTER
  #    the load. Compared as XML:
  #      mesh       loaded: massing_fab.dae    committed: massing_flat.dae
  #      <emissive> loaded: 0.72 0.72 0.74 1   committed: (none)
  #      diffuse    loaded: 0 0 0 1            committed: 0.58 0.58 0.60 1
  #      models/links/poses: 61 vs 61, IDENTICAL
  #
  #    The identical inventory is why this went unnoticed: every structural check
  #    against the file (link counts, boned poses, RL objects) also passes against
  #    the running server. Only the RENDERING differs.

  # 5. The live server is reachable and does publish entity state, from the
  #    foxglove container (it shares the L2 segment with the server):
  $ podman exec ao-sim-fabrication-foxglove gz topic -e -t \
      /world/factory/dynamic_pose/info -n 1
  pose { name: "rl_objects" id: 44 position { x: 4.38e-12 y: -0.0737 z: -0.578 } ... }
  pose { name: "storage_low_l0_motorbox" id: 121 ... }

  CONSEQUENCE: every visual claim about the running simulation since 2026-10-03
  18:19:21 describes the OLD massing mesh and the OLD emissive material. The
  flat-shading work in dc72f5c / c24f673 / ec34c71 is committed but has never been
  rendered on the live server.

  ALSO: scripts/simulation/ao-sim-portal.py cannot detect this divergence.
  world_summary() (lines 209-223) and objects_summary() parse the FILE on disk and
  never ask the server what it loaded, so /api/status reports link_count 37 from
  the file while the server holds a different document.

  NOT DONE, NEEDS OPERATOR: restarting ao-sim-fabrication-gz is a live service
  restart, so I did not do it. Nothing was modified. Proposed fix after restart:
  have the portal read /world/factory/dynamic_pose/info and report loaded-vs-committed.

  WHAT I GOT WRONG: I had been reading the world FILE and calling it "the
  simulation". Repository state and simulation state are different objects with a
  load boundary between them, and I never looked for that boundary. Both obvious
  direct probes failed first — /world/factory/scene/info returns 0 bytes to a plain
  subscriber, and gz service -s /world/factory/generate_world_sdf timed out at 20 s
  — so I fell back to the log, where the answer was one grep away in the ROTATED
  log file. logs/sim-gz-server.log is empty; logs/sim-gz-server.log.1 holds the history.

section: 10-simulation-architecture
---
The SIM session added §10.9 to its own section file, documenting the fault in full with the
comparison table, the trap list for the next session, and the retraction of the visual half of its
own SIM-06 closure.

SIM-06 is deliberately **left closed**, not reopened. Its acceptance criteria are about the GUI
client building and running — unit starts, 18 plugins load, `gz-rendering-ogre2` initialises,
6762 distinct colours in the capture, zero render errors. All of that remains true and none of it
depends on which world the server holds. What is retracted is narrower: the capture cannot be cited
as evidence that the *committed* world renders correctly. The operator should re-shoot the visual
after a restart, and that restart needs their approval.