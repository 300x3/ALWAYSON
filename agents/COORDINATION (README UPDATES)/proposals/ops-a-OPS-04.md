---
item: OPS-04
action: close
evidence: |
  # the requirement has an executor, and it is not a check-*.sh validator:
  $ grep -l 'restic' scripts/validation/*.sh
  NONE
  $ ls scripts/restore/
  restore-corda-test.sh  restore-mapping-artifact-test.sh  restore-restic-drill.sh
  restore-sales-db-test.sh  restore-simulation-artifact-test.sh  verify-hashes-and-receipts.sh

  # step banners are the script's own control flow, one per requirement:
  $ grep -n 'STEP ' scripts/restore/restore-restic-drill.sh
  88:STEP 1  95:STEP 2  115:STEP 3  121:STEP 4  173:STEP 5  181:STEP 6  190:STEP 7

  # the three safety refusals reproduce, each exiting 2 (re-measured 2026-10-04):
  $ bash scripts/restore/restore-restic-drill.sh --repo /nonexistent ; echo EXIT=$?
  ERROR: --scratch is required (never defaults to a live path)
  EXIT=2
  $ bash scripts/restore/restore-restic-drill.sh --repo /nonexistent --scratch /ALWAYSON/data/evil-probe
  REFUSED: scratch path /ALWAYSON/data/evil-probe is inside the live /ALWAYSON tree.
  EXIT=2
  $ bash scripts/restore/restore-restic-drill.sh --repo /nonexistent --scratch <non-empty dir>
  REFUSED: scratch directory /tmp/ao-nonempty-probe-644426 already exists and is not empty.
  EXIT=2
  # and no live path was created by the refusal:
  $ ls -d /ALWAYSON/data/evil-probe
  ls: cannot access '/ALWAYSON/data/evil-probe': No such file or directory

  # step 4 can fail: `suspect > 0` forces result=FAIL, which is what step 7 branches on
  $ sed -n '182,195p' scripts/restore/restore-restic-drill.sh
  result=PASS
  [ "$db_bad" -gt 0 ] && result=FAIL
  [ "$changed_before_snapshot" -gt 0 ] && result=FAIL
  ... exit 1

  # the deviation is real: there is no stored per-file manifest of the backed-up set
  $ find artifacts -maxdepth 2 -name '*.sha256*'
  artifacts/corda-5.2.2/notary-plugin-non-validating-server-5.2.2.0-package.cpb.sha256sum
  artifacts/corda-5.2.2/corda-combined-worker-5.2.2.0.jar.sha256sum
  artifacts/corda-5.2.2/corda-cli-installer-5.2.2.0.zip.sha256sum
  # vendor checksums for jars/packages, not a manifest of the restic path set
section: 17-backup-restore-monitoring-and-completion-criteria
---
**Closed, and this proposal is late.** §17.1.1 has said "OPS-04 closed
2026-10-04" since commit `667e3f5`, but no proposal file was ever written — the
session was interrupted after editing the section and before writing the
proposal. The claim was in the section with nothing behind it, which is exactly
the state this single-writer arrangement exists to prevent. I re-derived the
evidence from the live host rather than trusting the section's own text.

The item asked the section either to state that the `check-*.sh` scripts implement
the seven-step restore test, or to acknowledge the requirement has no executor.
The answer is neither: it has an executor, and it is
`scripts/restore/restore-restic-drill.sh`. `grep -l 'restic' scripts/validation/*.sh`
returns nothing, so the validators are confirmed not to be the owners.

**What I checked in the section and got right**, because the section cites line
numbers and those rot: all seven `STEP` banners are still at the cited lines
(88, 95, 115, 121, 173, 181, 190), and the three refusals reproduce with exit 2
rather than the exit 1 recorded in the older OPS-10 proposal. That older figure
was wrong — exit 2 is the documented usage/refused code.

**The one deviation is recorded, not smoothed over.** §17.1 step 4 says "compare
hashes with stored manifests". There is no stored per-file manifest of the
backed-up set; the only `.sha256` files under `artifacts` are three upstream
Corda vendor checksums for jars and packages. The drill therefore compares the
restored tree against the **live** tree, which answers "did anything change since
the snapshot" rather than "does the snapshot match a recorded baseline". §17.1.1
says so explicitly. Creating a baseline manifest would be new backup behaviour
and is OPS-09's decision, not this item's.

This closes the *ownership* question only. The drill still has no cadence —
nothing schedules it, so §17.1's "Monthly" requirement is unmet, and that half
stays with OPS-24.

Files changed: `agents/COORDINATION (README UPDATES)/…/17-…/section.md` (§17.1.1 verified, no
substantive edit needed beyond the line-number recheck).