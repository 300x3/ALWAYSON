---
item: SIM-13
action: close
evidence: |
  §19.1 recorded this item as absent ("nothing in the repo implements one"). It is
  present, running, and served by the portal. Measured 2026-10-03.

  $ python3 /ALWAYSON/scripts/simulation/verify_safety_zones.py
  REHEARSAL ONLY - actuates nothing. 4 zones, 2 unresolved dependencies.
    [ok]      zone-arms-cell           min=[4.9813, 0.8617, -0.4685] max=[7.8213, 4.5341, 2.7701]
    [ok]      zone-arms-reach          min=[5.2313, 1.1117, -0.2185] max=[7.5713, 4.2841, 2.5201]
    [ok]      zone-conveyor-cell       min=[4.9491, 1.5235, -0.2373] max=[7.1969, 3.1511, 2.2947]
    [ok]      zone-fabrication-floor   min=[-1.0, -1.0, -1.0] max=[8.874, 5.8311, 3.0574]
    [GAP]     printer-01           datum.origin is null (source: declared-by-operator)
    [GAP]     cnc-01               datum.origin is null (source: declared-by-operator)
  No interlock is enforced in the simulation; they report only.
  (exit 0)

  $ curl -s http://127.0.0.1:8765/api/safety-zones | head -c 200
  {"rehearsal_only": true, "actuates_nothing": true, "zones": [
   {"id": "zone-arms-cell", "kind": "restricted", "derived_from": "cell-arms",
    "clearance": "operator_aisle", "resolved": true,
    "min": [4.9813,0.8617,-0.4685], "max": [7.8213,4.5341,2.7701],
    "clearance_m": 1.0, "centre": [6.4013,2.6979,1.1508]}, ...

  $ grep -c 'enforced_in_simulation: false' GAZEBO/sim/safety_zones.yaml
  4
  # re-counted 2026-10-04: that 4 is 3 interlocks plus 1 prose mention in a
  # comment on line 85. Three interlocks, all false:
  $ grep -n 'enforced_in_simulation' GAZEBO/sim/safety_zones.yaml
  85:# permit. `enforced_in_simulation: false` is the important field: this model
  94:    enforced_in_simulation: false
  100:    enforced_in_simulation: false
  106:    enforced_in_simulation: false

  $ curl -s -m 5 .../api/status | python3 -c '... ["world"]["links"] ...'
  zone links: 4 ['zone-arms-cell', 'zone-arms-reach', 'zone-conveyor-cell',
                 'zone-fabrication-floor']

  Four zones resolve with computed bounding boxes, three interlocks are declared,
  and the four zones are live links in the served world. Two machines
  (printer-01, cnc-01) remain without a datum and are reported as [GAP] rather
  than silently omitted. Every interlock is `enforced_in_simulation: false` and
  the model actuates nothing -- that is the declared boundary, not a shortfall.
section: 10-simulation-architecture
---
§19.1 was wrong on this item and the correction matters more than the closure. It
records SIM-13 as absent with the sentence "nothing in the repo implements one";
`GAZEBO/sim/safety_zones.yaml`, `scripts/simulation/verify_safety_zones.py` and
the portal's `/api/safety-zones` endpoint have all existed and been serving since
before this session began.

I have added §10.3 to my section file. It states what was measured rather than
what is claimed: four zones resolved with computed boxes, three interlocks
declared and all of them reporting-only, and the two unresolved machine datums
named in the open rather than buried. The "rehearsal only, actuates nothing"
boundary is recorded in the README in the same words the tool prints, because a
reader scanning §10 could otherwise mistake a zone model for an enforced one.

Two points I deliberately did **not** close. The `printer-01` and `cnc-01` gaps
are real and remain open — they need operator-supplied datums, which is not mine
to invent. And no interlock is enforced anywhere, so closing this item must not be
read as "the simulation has working safety interlocks"; it means the model exists,
resolves, and is honest about not enforcing.

**What I got wrong.** I spent this session assuming §19 was a reliable index and
only checked it against the running system at the end. Checking first would have
found that two of my fourteen items were already delivered, and that the manifest
drift had grown well past the size §19 recorded.