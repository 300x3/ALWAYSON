---
item: OPS-07
action: update
evidence: |
  # one canonical root: no sibling, no LOGOS-JOURNALS draft directory anywhere
  $ cd /ALWAYSON && find . -maxdepth 2 -iname '*LOGOS*'
  (no output)
  $ cd /ALWAYSON && ls logs/ | head
  README.txt  audit.log  backup  backup.log  gpu-runtime  gpu-runtime-check.log
  installation  installation-journal.log  lmstudio-readme-preset.sha256  mastodon-local-proxy.log
  # logs/installation is a SUBDIRECTORY of logs/, not a sibling root

  # the half that is NOT done: logs/ is absent from the restic path set
  $ grep -o "restic backup.*" scripts/backup/restic-run.sh | tr ' ' '\n' | grep ALWAYSON
  /ALWAYSON/config /ALWAYSON/artifacts /ALWAYSON/backups/postgres
  /ALWAYSON/data/ardupilot /ALWAYSON/data/corda-install /ALWAYSON/data/sim-fabrication
  /ALWAYSON/data/sales /ALWAYSON/data/mapping /ALWAYSON/data/field
  /ALWAYSON/data/payment /ALWAYSON/data/ledger
  # 11 paths, none of them logs/
section: 17-backup-restore-monitoring-and-completion-criteria
---
**Half met, half open — recorded as such rather than closed.** Re-measured
2026-10-03: `/ALWAYSON/logs/` is the single journal root. There is no second
root, `logs/installation/` is a subdirectory of it and not a sibling, and the
`LOGS-JOURNALS/` draft name appears nowhere on disk. The canonical-root half of
this item is therefore satisfied.

**The outstanding half is that `logs/` is still absent from the restic path
set.** Measured directly: the nightly job passes 11 paths and none is
`logs/`. The consequence is stated plainly in §17.5 — a restore to a new host
comes back with **no operational history at all**, which undercuts §16.3's
entire purpose.

I did not add it. It is a one-line change to an approved path list, but it
enlarges what the nightly job copies, and the journals are the fastest-growing
thing in `logs/`. That is an operator decision, and it is why this item is
`update`, not `close`.

Also new in §17.5: the retention policy that OPS-25/OPS-26 previously left
unowned, staged and parse-verified (see the OPS-26 proposal).

Files changed: `agents/COORDINATION/…/17-…/section.md` (§17.5).