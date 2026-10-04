---
item: OPS-24
action: update
evidence: |
  # NEW THIS SESSION: the nightly repository cannot be drilled at all without
  # root. The PASS in 17.4 was against the OFF-HOST repo, because that one is
  # readable. The repo that actually holds data/ + ledger/ + payment/ +
  # backups/postgres/ is the one that is unreadable.
  $ ls -ld /var/backups/alwayson-restic
  drwx------ 7 root root 4096 Aug 25 14:11 /var/backups/alwayson-restic

  # the SECRET half works fine -- wallet materialises the env:
  $ ./scripts/operations/fetch-restic-env.sh "$E"
  OK: wallet-backed restic env materialized

  # but the failure is a directory permission, not a decryption failure:
  $ restic snapshots --tag alwayson
  Fatal: unable to open config file: stat /var/backups/alwayson-restic/config: permission denied
  Is there a repository at the following location?
  /var/backups/alwayson-restic

  # the drill script reports it correctly as its environment class, not as an
  # empty result:
  $ ./scripts/restore/restore-restic-drill.sh --repo "$RESTIC_REPOSITORY" --scratch /var/tmp/ao-drill-$$
  ERROR: could not resolve a snapshot; pass --snapshot explicitly
  rc=3

  # the scripted safety refusals still hold, and notably the live-tree refusal
  # fires BEFORE the credential check:
  $ ./scripts/restore/restore-restic-drill.sh --repo /var/backups/alwayson-restic --scratch /ALWAYSON/data/evil
  REFUSED: scratch path /ALWAYSON/data/evil is inside the live /ALWAYSON tree.
  rc=2
section: 17-backup-restore-monitoring-and-completion-criteria
---
**Still OPEN, and the reason is now much sharper.** New §17.4.1 pins the
blocker to a specific permission. The drill recorded as PASS in §17.4 was run
against the off-host repository because that one is readable; the nightly
repository is mode `0700 root root`, so it cannot be read with valid credentials.
That inverts the intuitive reading of the evidence — the passing drill exercises
the repository that protects the least (config + artifacts), and the repository
that protects the most is the one never drilled.

Closing it needs a privilege change on backup data (`pkexec`, a read-only group,
or service-account read access), which is an explicit stop condition. Nothing was
changed, no scratch directory remains, and nothing under `/ALWAYSON` was written.

## What I got wrong this session

I initially read `stat` mtimes on the rotated files and concluded the rotations
predated the logrotate policy install — reasoning that a `.log.1` older than
`/etc/logrotate.d/alwayson` could not have come from it. **That inference was
wrong**, for the reason §17.5 already documents: under `nocopytruncate` the
rotation *renames*, so the rotated file retains the mtime of its last write. mtime
measures the content's age, not the rotation's time, and cannot date a rotation
at all. I repeated an error the section had already recorded against a previous
revision of itself. The rule I keep relearning: to date a rotation, read the
journal (`pkexec`/`logrotate.service` lines), never the filesystem.

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