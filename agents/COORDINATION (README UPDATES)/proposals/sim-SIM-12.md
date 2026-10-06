---
item: SIM-12
action: keep-open
evidence: |
  Confirmed absent, 2026-10-03. No facility scheduler exists anywhere in the repo.

  $ grep -rni 'scheduler' GAZEBO/ scripts/simulation/ quadlet/ | grep -v Binary
  quadlet/sales/ao-mastodon-sidekiq.container:  # ... Sidekiq scheduler comment (unrelated)

  That single hit is a comment in an unrelated sales container. There is no
  scheduler in the simulation tree, no scheduler unit in quadlet/sim-fabrication/,
  and no schedule data file alongside boning.yaml, objects.yaml, safety_zones.yaml
  or conveyor_loops.yaml.

  # For contrast, the simulation files that DO exist and are consumed:
  $ ls GAZEBO/sim/
  boning.yaml  conveyor_loops.yaml  objects.yaml  safety_zones.yaml
section: 10-simulation-architecture
---
SIM-12 stands, and I am confirming rather than closing it because confirming is
what the evidence supports.

A case-insensitive search for `scheduler` across `GAZEBO/`, `scripts/simulation/`
and `quadlet/` returns exactly one hit: a comment in
`quadlet/sales/ao-mastodon-sidekiq.container`, which is the sales domain and has
nothing to do with facility scheduling. There is no scheduler script in
`scripts/simulation/`, no scheduler unit in `quadlet/sim-fabrication/`, and no
schedule data file next to the four simulation data files that do exist.

That absence is at least documented rather than silent, which is more than most
gaps of this size manage. But the acceptance criteria ask for a scheduler that can
drive the simulation, and there is nothing to drive. This is a build item, not a
defect, and it is not blocked on anything external -- unlike SIM-07 it needs no
operator approval and no network. It simply has not been started.

§10.3 in my section file records the search and the negative result so the next
session does not re-run it from scratch.

**Note for the compiler.** SIM-12, SIM-13 and SIM-14 are contiguous in the
simulation domain and now have very different states: one is a build item, two are
delivered but were recorded as absent. If §19 groups these under a single
"absent" narrative it will be misleading, which is why all three carry measured
evidence in their proposals rather than a status change alone.