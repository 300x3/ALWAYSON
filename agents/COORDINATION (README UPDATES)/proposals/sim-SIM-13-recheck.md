---
item: SIM-13
action: close
evidence: |
  Re-verified 2026-10-11 in worktree /tmp/ao-sessions/wt-sim.
  $ grep -n '<model name="safety_zones">' GAZEBO/worlds/factory.world
  695:    <model name="safety_zones">
  $ python3 scripts/simulation/verify_safety_zones.py
  REHEARSAL ONLY - actuates nothing. 4 zones, 2 unresolved dependencies.
    [ok]      zone-arms-cell           min=[4.9813, 0.8617, -0.4685] max=[7.8213, 4.5341, 2.7701]
    [ok]      zone-arms-reach          min=[5.2313, 1.1117, -0.2185] max=[7.5713, 4.2841, 2.5201]
    [ok]      zone-conveyor-cell       min=[4.9491, 1.5235, -0.2373] max=[7.1969, 3.1511, 2.2947]
    [ok]      zone-fabrication-floor   min=[-1.0, -1.0, -1.0] max=[8.874, 5.8311, 3.0574]
    [GAP]     printer-01           datum.origin is null (source: declared-by-operator)
    [GAP]     cnc-01               datum.origin is null (source: declared-by-operator)
  No interlock is enforced in the simulation; they report only.  (exit 0)
  $ curl -s -m 5 http://127.0.0.1:8765/api/safety-zones | python3 -c "import json,sys; d=json.load(sys.stdin); print([z['id'] for z in d['zones'] if z['resolved']])"
  ['zone-arms-cell', 'zone-arms-reach', 'zone-conveyor-cell', 'zone-fabrication-floor']
  §19.1 text ("factory.world contains no safety-zone or interlock entity") is
  false as of this measurement. Does not supersede sim-SIM-13.md; same verdict,
  fresh evidence.
section: 10-simulation-architecture
---
The safety-zone and interlock model exists, resolves, and is served live: four
zones with computed boxes, three report-only interlocks, two honestly reported
[GAP] datums. The rehearsal-only boundary is stated in the same words the tool
prints. Recorded in the §10.10-adjacent recheck table.

What I got wrong: nothing on this item this pass.
