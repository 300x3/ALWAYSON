---
item: SIM-09
action: close
evidence: |
  Re-verified 2026-10-11 in worktree /tmp/ao-sessions/wt-sim.
  $ grep -n 'centroid' GAZEBO/sim/boning.yaml | head -3
  55:      centroid: [6.401314, 2.697865, 1.150797]
  $ python3 -c "o=[5.981314,1.861669,0.531531];e=[0.840000,1.672391,1.238532];print([round(o[i]+e[i]/2,6) for i in range(3)])"
  [6.401314, 2.697865, 1.150797]
  $ grep -n -A2 '<model name="camera_elev_arms">' GAZEBO/worlds/factory.world
  1364:    <model name="camera_elev_arms">
  1366-      <pose>6.401 4.056 1.151 0 0.0000 -1.5708</pose>
  $ python3 scripts/simulation/build-boning-cameras.py --check
  OK: elevation cameras match boning.yaml  (exit 0)
  The centroid is stated in the boning data (not hand-computed), equals
  origin+extent/2 exactly, and the elevation pose is derived from it by the
  generator. Does not supersede sim-SIM-09.md; same verdict, fresh evidence.
section: 10-simulation-architecture
---
§10.2.1 asked for the as-built arm centroid to be added to the boning data and
the pose recomputed from it. Re-measured 2026-10-11: `cell-arms` carries
`centroid [6.401314, 2.697865, 1.150797]`, the arithmetic reproduces it
exactly, and `build-boning-cameras.py --check` exits 0 with the
`camera_elev_arms` pose derived from that datum. Recorded in the new
§10.10-adjacent recheck table.

What I got wrong: nothing on this item this pass — but see the SIM-14 note in
the section about nearly claiming a unit restart counts as an object reset.
