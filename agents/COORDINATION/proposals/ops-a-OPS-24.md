---
item: OPS-24
action: update
evidence: |
  # the drill ran against the off-host repository; table in 17.4:
  #   snapshot 56bf1af5, 63 files, 304.564 KiB
  #   hash-identical to live: 59 of 63
  #   changed since snapshot: 4 (all config/, all mtime AFTER the snapshot)
  #   changed with mtime BEFORE the snapshot (corruption signature): 0
  #   database dumps in this snapshot: 0
  #   result: PASS
  $ export RESTIC_REPOSITORY=/media/scottw/…/ALWAYSON-BACKUPS
  $ restic check --read-data-subset=1/10
  no errors were found

  # still no cadence — nothing schedules the drill:
  $ systemctl --user list-timers --all | grep -i restic
  ao-restic-prefetch.timer   (only the prefetch timer exists)

  # data/ is still absent from the nightly path set:
  $ grep -o "restic backup.*" scripts/backup/restic-run.sh | tr ' ' '\n' | grep ALWAYSON
  /ALWAYSON/config /ALWAYSON/artifacts /ALWAYSON/backups/postgres
  /ALWAYSON/data/ardupilot /ALWAYSON/data/corda-install /ALWAYSON/data/sim-fabrication
  /ALWAYSON/data/sales /ALWAYSON/data/mapping /ALWAYSON/data/field
  /ALWAYSON/data/payment /ALWAYSON/data/ledger
section: 17-backup-restore-monitoring-and-completion-criteria
---
**Progress, still OPEN.** New §17.4 records a restore drill actually executed
by `scripts/restore/restore-restic-drill.sh` (new this session) against the
off-host repository, with the per-measure table.

Why it does not close, and the two limits are recorded rather than buried:

1. **The drill had no database dumps to validate** — step 2 of the seven-step
   test had nothing to work on, because the off-host repository holds a single
   proof snapshot covering only `config` and `artifacts`, while the `pg_dump`
   output lives in the local repository. Reporting "0 dumps, 0 problems" as a
   pass would overstate the result, so it is reported as a scoped pass.
2. **It still has no cadence** — §17.1 requires a monthly restore test and
   nothing schedules it. Installing a timer would restart nothing and touch no
   data, but it creates a recurring privileged job on backup material, so it is
   left as an operator decision rather than done unasked.

**The most important thing I got wrong, and it is worth the whole session.**
The drill's comparison step first resolved the live file as
`$live_root/$rel` and fell back to `/ALWAYSON/…` only when that path was
absent — but `$live_root` **is** the restored tree, so it compared every
restored file with itself and reported `identical: 63, changed: 0`. A perfect
score from a test that cannot fail. Corrected, the same snapshot reports
`identical: 59, changed: 4`, which matches an independent manual `sha256sum`
comparison done outside the script. A false pass is worse than a failure
because it gets filed as evidence. The lesson is now a comment in the script:
**a comparison step must be able to fail**, and the cheapest proof is to run it
once against data already known to have changed.

Safety is by construction rather than by care: the script requires an explicit
`--scratch`, refuses any path inside `/ALWAYSON` after resolving it with
`readlink -m`, and refuses a scratch directory that is not empty. All three
refusals are shown in the OPS-08 evidence above.

Files changed: `scripts/restore/restore-restic-drill.sh` (new),
`agents/COORDINATION/…/17-…/section.md` (§17.4).