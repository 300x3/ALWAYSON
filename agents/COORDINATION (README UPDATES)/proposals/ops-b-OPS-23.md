---
item: OPS-23
action: close
evidence: |
  $ AO_ROOT=$PWD python3 scripts/build-update/provenance-log.py --offline \
        --out /tmp/ops23v/s.md --html /tmp/ops23v/s.html --plan /tmp/ops23v/p.json
  $ grep -o '<summary>[^<]*</summary>' /tmp/ops23v/s.md
  <summary>Rolled-up launchers — expand to list every application entry (153 entries across 34 groups)</summary>
  <summary>Ubuntu archive packages — expand to list all 3857 packages with their installed versions</summary>
  <summary>ROS 2 lyrical (whole train) — expand to list all 351 packages with their installed versions</summary>
  <summary>KDE Plasma Desktop — expand to list all 191 components</summary>

  $ grep -c "details class='drill'" /tmp/ops23v/s.html
  38

  $ python3 -m pytest scripts/build-update/test_generators.py -q -k 'Rollup or rollup or drill'
  7 passed, 55 deselected in 0.11s
section: 12-host-installation-and-configuration
---
Every collapsed row now carries its `members` and renders them as a `<details>`
drill-down in Markdown, HTML and the PDF, with each member's own installed
version (`libc6 (2.42-1)`) rather than a bare name. §12.5.6 documents it.

The original failure was **silent**, which is why it survived: members were
computed and carried on the row as `members`, but the HTML renderer never
emitted them, so the drill-down existed in Markdown only and HTML/PDF quietly
lost it. Nothing errored; the document just stopped answering a question.
`TestRollupsCanBeDrilledInto` (7 tests) asserts the HTML path and that the
drill-down survives the print stylesheet, since a PDF that hides it reintroduces
the same dead end. Member names are HTML-escaped — they come from `.desktop`
files on disk.

**Two fixes that the first fix created.** Attaching members made the Markdown
~3× larger, but the roll-up renderer joined them into one table cell, so the
Ubuntu archive came out as a single **40,000-character line** — technically
"reachable", practically as useless as the original count. Package roll-ups now
render one member per row in their own collapsible block. And the two apt
roll-ups were still bare counts after the first pass; both now attach theirs.
The ROS train matters most: it is FROZEN, making "which 351 packages are
affected" the question an operator will actually ask. `rollup_details_md()` was
extracted from `render()` so this is unit-testable — `render()` spends hundreds
of apt round trips, which no test should pay to assert a formatting rule.

**What I got wrong, and the reason this took a second pass.** I verified this
item against the **tracked artifacts** rather than against a fresh render, and
they showed only 2 summaries and **0** drill-downs — which reads exactly like
"the fix does not work". The tracked `docs/software-status.md` and
`tmp/software-status.html` are dated 2026-10-03 20:53 while the generator landed
2026-10-04 10:30. The code was correct and the artifacts simply predated it. I
re-ran the generator into a scratch directory and every number in the section
reproduced exactly (4 summaries, 38 drill-downs).

**Left open, and it is a real gap:** the committed documents have **not** been
regenerated, so the shipped PDF still collapses the apt and ROS roll-ups to bare
counts. One `./scripts/build-update/refresh-install-log.sh` fixes it, but that
rewrites tracked documents and belongs to whoever owns the render cadence, not
to a validator change.