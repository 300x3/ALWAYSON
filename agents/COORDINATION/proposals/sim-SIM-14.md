---
item: SIM-14
action: update
evidence: |
  SUPERSEDES the 2026-10-03 `action: close` proposal previously in this same file.
  The model exists, so §19.1's "That model does not exist" is wrong and must be
  corrected. But "close" was the wrong verdict for a second reason I did not
  check on 2026-10-03: §19 asks for objects "addressable and resettable", and
  reset is NOT delivered. Re-measured 2026-10-04.

  LIMB 1 -- the `rl_objects` model exists as live world entities. TRUE.
  $ grep -n 'name="rl_objects"' GAZEBO/worlds/factory.world
  547:    <model name="rl_objects">

  $ curl -s -m 5 http://127.0.0.1:8765/api/status | python3 -c '...'
  world keys: ['path', 'link_count', 'links']
  link_count: 37
  rl links: 9 ['part_a1', 'part_a2', 'part_a3', 'stock_s1', 'stock_s2',
               'stock_s3', 'target_bin_a', 'target_bin_b', 'target_shelf']

  ^ nine catalogue objects instantiated as non-static links. §19.1's assertion
  that the model does not exist is contradicted; it is retracted here.

  LIMB 2 -- "resettable". FALSE.
  $ curl -s -o /dev/null -w '%{http_code}\n' -m 5 http://127.0.0.1:8765/api/reset
  404
  $ curl -s -m 5 http://127.0.0.1:8765/api/objects | python3 -c '...'
  model rl_objects
  total 9
  claimed True available False
  note objects.yaml declares resettable: true and documents a reset action
       returning each object to home_pose, but this portal implements no reset
       endpoint and performs no reset. Treat resettable_claimed as an unverified
       catalogue assertion, not an available operation.

  There is no reset endpoint, so placement cannot be returned to `home_pose` at
  run time without rewriting the world. "Resettable" is undelivered.
section: 10-simulation-architecture
---

§19.1 records SIM-14 as absent ("That model does not exist"). **That assertion is wrong and
should be corrected in §19**: the nine catalogue entries in `GAZEBO/sim/objects.yaml` are
generated into the committed `factory.world` as a non-static `rl_objects` model with nine
links, and the running server reports those links through the portal. The separation the item
is really concerned with — RL entities held apart from the static `factory_assets` so a
training run can vary count and placement without rebuilding the world — is implemented by
making the model non-static.

**SIM-14 must stay Open, for a limb I did not check on 2026-10-03.** §19 asks for objects
"individually addressable, observable and **resettable**". Addressable is delivered. Resettable
is not: `/api/reset` returns 404, the portal implements no reset, and placement cannot be
returned to `home_pose` at run time without rewriting the world. My own portal correction in
§10.4 replaced the bare `"resettable": true` with `resettable_claimed` beside an explicit
`reset_available: false` — and that correction is precisely what made the undelivered half
visible. Filing `close` while my own section file said the opposite was an inconsistency I
should have caught by reading the two documents together.

**On the generator defects I flagged in 2026-10-03.** Cause 1 (hand-added `<specular>`
disarming `--check`) is **fixed and verified**: the generator now emits `SPECULAR`/`SHININESS`,
and `--check` exits 0. Cause 2 (non-idempotent *position* on write) is **still present** and is
now filed as **SIM-15** rather than left in prose. Re-measured 2026-10-04 on a scratch copy:

    $ python3 scripts/simulation/build-rl-objects.py --check     -> OK, exit 0 (no-op path safe)
    $ python3 scripts/simulation/build-rl-objects.py --write     -> "already current; nothing written"
    # force a real catalogue change (part-a1 home_pose 6.20 -> 6.90) and rewrite:
    $ python3 scripts/simulation/build-rl-objects.py --check     -> STALE, exit 1
    $ python3 scripts/simulation/build-rl-objects.py --write     -> wrote 3 groups / 9 objects
    # rl_objects model position:  547 -> 1289
    # safety_zones model position: 695 -> 548
    # camera_elev_massing:       1410 -> 1263
    $ gz sdf -k ...                                               -> Valid.
    $ grep -c '<link name=' -> 37 (unchanged, no content lost)

So a legitimate catalogue edit silently reorders three generated models — `rl_objects` is
re-appended after `safety_zones` and the conveyor loops — in the world the live server has open.
The world stays parseable and no link is lost, so this is a diff-noise and review hazard rather
than a rendering fault, but it is exactly the kind of silent reordering that makes a world
unreviewable later.

**What I got wrong.** I filed `close` on 2026-10-03 for SIM-14 having verified only the half I
found interesting — that the model exists — and not the half §19 actually names, resettability,
which my own section file already contradicted. The 2026-10-03 evidence block is also now stale
in form: `/api/status` returns `world.links` and `world.link_count` as **nested** keys, so a
top-level `d.get("links")` returns `[]` and a top-level `d.get("link_count")` returns `None`. I
re-ran my original one-liner unchanged, got 0 RL links, and briefly took that as evidence that
the model had disappeared. It had not; my query was wrong. Re-reading the response shape gave
the real 9 links and `link_count` 37. That is the second time this session that re-running an
old command unchanged, without checking whether its assumptions still held, produced a
confidently wrong answer. A measurement whose *inputs* may have drifted needs re-derivation, not
just re-execution.

I also ran `--write` against the live `/ALWAYSON` tree before copying to a scratch directory,
modifying the shared tree. I caught it in the diff and reverted only my own edit
(`git checkout -- GAZEBO/worlds/factory.world`), after which the sha256 returned to
`bce32f2a7ff035b4022db82d9a90267ca829261d08038d3e26e5ff3fe5f51053`. Caught is not the same as
avoided; the correct order was copy first. Both of today's relocation measurements were done on
`/tmp/gen-test-sim`, never on the live tree.