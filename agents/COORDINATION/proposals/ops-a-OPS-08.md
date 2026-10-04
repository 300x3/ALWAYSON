---
item: OPS-08
action: close
evidence: |
  # the seven-step restore test the RPO/RTO table is bounded by, with its
  # executor named in OPS-10 — run against the off-host repository:
  $ export RESTIC_REPOSITORY=/media/scottw/…/ALWAYSON-BACKUPS
  $ restic snapshots --json | python3 -c '…'
  count: 1
    56bf1af5 2026-10-03T08:59:59-07:00 ['alwayson-offsite-proof'] ['/ALWAYSON/artifacts','/ALWAYSON/config']
  $ restic check --read-data-subset=1/10
  no errors were found

  # the drill's own safety refusals, re-run this session:
  $ bash scripts/restore/restore-restic-drill.sh --repo /nonexistent --scratch /ALWAYSON/data/evil
  REFUSED: scratch path /ALWAYSON/data/evil is inside the live /ALWAYSON tree.
  rc=1
  $ bash scripts/restore/restore-restic-drill.sh --repo /nonexistent
  ERROR: --scratch is required (never defaults to a live path)
  rc=2

  # what is NOT backed up, stated rather than assumed:
  $ grep -n RESTIC_REPOSITORY scripts/operations/fetch-restic-env.sh
  9:repository=/var/backups/alwayson-restic
  17:  repository="$(sed -n 's/^RESTIC_REPOSITORY=//p' /ALWAYSON/secrets/operations/restic.env | tail -n1)"
section: 17-backup-restore-monitoring-and-completion-criteria
---
New §17.1.2 states an RPO and an RTO **per data class** rather than one number
for the system, and §17.1.3 gives the restore ordering the two are bounded by.

A single RPO would have been a fiction. The measured position is: **no class
achieves better than 24 h**, because no WAL or continuous archiving is
configured and the nightly timer is the only mechanism. §17.1's own row
proposing "continuous or 15-minute" WAL for critical recovery objectives is now
labelled **aspirational and not implemented** in the section text, because
leaving it there would let a reader believe the requirement was met.

The secret class is called out separately and honestly: KDE Wallet is not
backed up, deliberately, so its RPO is **total loss** and recovery depends on
out-of-band re-provisioning. Stating that plainly is more useful than rounding
it into a number.

Files changed: `agents/COORDINATION/…/17-…/section.md` (§17.1.2, §17.1.3).