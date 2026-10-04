---
item: SIM-15
action: create
evidence: |
  New item in my own group (SIM), next free number after SIM-14. Nothing existing
  covers this: SIM-14 covers the objects model, SIM-09 the elevation cameras, and
  the `--check` guard itself was fixed in SIM-09's session. What is left is that a
  *correct* regeneration is not position-idempotent. Measured 2026-10-04 on a
  scratch copy at /tmp/gen-test-sim, never on the live tree.

  The no-op path is safe:
  $ python3 scripts/simulation/build-rl-objects.py --check
  OK: rl_objects block matches objects.yaml           (exit 0)
  $ python3 scripts/simulation/build-rl-objects.py --write
  rl_objects block already current; nothing written   (exit 0, sha256 unchanged)

  But make a legitimate catalogue change (part-a1 home_pose 6.20 -> 6.90) and
  rewrite:
  $ python3 scripts/simulation/build-rl-objects.py --check
  STALE: run scripts/simulation/build-rl-objects.py --write   (exit 1)
  $ python3 scripts/simulation/build-rl-objects.py --write
  wrote 3 groups / 9 objects into .../factory.world

  Model positions after that write:
      rl_objects          547 -> 1289
      safety_zones        695 ->  548
      camera_elev_massing 1410 -> 1263

  $ gz sdf -k ...                       -> Valid.
  $ grep -c '<link name=' ...           -> 37 (unchanged; no content lost)

  So `--write` strips the existing BEGIN/END block and re-appends it before
  `</world>`, which moves `rl_objects` after `safety_zones` and the conveyor
  loops. The world stays valid and no link is lost, so nothing breaks today --
  but a routine refresh silently produces a large reordering diff in the world
  the live server has open, and the next person to read that diff cannot tell a
  reorder from a real geometry change. Fix by replacing the block in place rather
  than deleting and re-appending.
section: 10-simulation-architecture
---

`build-rl-objects.py --write` is not idempotent in position. It strips the generated
`rl_objects` block and re-appends it before `</world>`, so any genuine catalogue change moves
that model from line 547 to the end of the file, dragging `safety_zones` and `camera_elev_massing`
up with it. The world remains parseable (`gz sdf -k` → Valid) and no link is lost (37 before and
after), so this is a review-integrity hazard rather than a runtime fault — which is precisely
why it went unnoticed for as long as it did. It should replace the block in place.

This is the "cause 2" I described in prose inside the 2026-10-03 SIM-14 proposal rather than
filing, on the grounds that it was not a §19 item. That reasoning was wrong: the protocol's
constraint is that I must not renumber into another session's group, and this defect is in my
group's own scripts and world file. Leaving a known defect in a prose footnote, in a file the
compiler does not merge, is the same as not filing it. The next free number in SIM is 15.

**What I got wrong.** I twice deferred to "not a §19 item, so I will leave it in prose" when the
bar for filing in my own group is not whether §19 lists it but whether I am the session that can
fix it. Both times the deferral cost a full session of the defect remaining undocumented in any
place a reader would look first.
