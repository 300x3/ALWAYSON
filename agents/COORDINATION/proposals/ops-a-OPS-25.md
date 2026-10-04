---
item: OPS-25
action: update
evidence: |
  $ ls /etc/logrotate.d/ | grep -i alwayson || echo 'NOT installed'
  NOT installed
  $ ls /etc/systemd/journald.conf.d/ | grep -i alwayson || echo 'NOT installed'
  NOT installed
  $ sudo -n true
  sudo: interactive authentication is required

  # the staged policy parses and describes all five blocks:
  $ logrotate -d config/host/logrotate-alwayson.conf 2>&1 | grep -c 'rotating pattern'
  5
  $ bash scripts/ops/install-log-retention.sh --dry-run
  DRY RUN -- no files will be written.
  would install: …/logrotate-alwayson.conf -> /etc/logrotate.d/alwayson
  would install: …/journald-alwayson.conf -> /etc/systemd/journald.conf.d/60-alwayson-retention.conf
  rotating pattern: /ALWAYSON/logs/*.log … (14 rotations) …
  rotating pattern: /ALWAYSON/logs/operations/*.log … (400 rotations) …
  rotating pattern: /ALWAYSON/logs/backup/*.log … (400 rotations) …
  rotating pattern: /ALWAYSON/logs/installation/*.log … (400 rotations) …
  rotating pattern: /ALWAYSON/logs/gpu-runtime/*.log … (400 rotations) …
  rc=0
section: 17-backup-restore-monitoring-and-completion-criteria
---
**Stays OPEN — installing it needs root, which is an operator action.** The
acceptance test in §19.1 is "install it, then confirm one rotation actually
occurs"; neither half is done, so this is not closed. What moved is that the
privileged step is now a single reviewed script instead of an ad-hoc copy, and
the dry run is verifiable without escalating.

`scripts/ops/install-log-retention.sh` installs the policy to
`/etc/logrotate.d/alwayson` and the journald drop-in to
`/etc/systemd/journald.conf.d/60-alwayson-retention.conf`, and deliberately
**does not restart systemd-journald** unless `--restart-journald` is passed —
restarting the journal daemon is a visible host action. It validates the policy
with `logrotate --debug` *before* writing it, so a malformed file never lands
in `/etc/logrotate.d/`.

**Two defects I found in my own staged artifacts and fixed, both of which
would have been filed as "done":**

1. The logrotate file's own header read `Installed 2026-10-03` while
   `/etc/logrotate.d/alwayson` does not exist. A future agent reading that
   header would have skipped this item entirely. It now reads `STAGED …
   NOT INSTALLED`.
2. The same file's comment said the subdirectories "are NOT rotated", while
   the four blocks immediately below it rotate them on a 400-day budget. The
   comment predated the OPS-26 work and was left contradicting its own file.

I also narrowed the root guard so `--dry-run` works unprivileged. As written it
exited `must run as root` before printing anything, which means the operator
could not inspect the policy without escalating first — backwards. Measured
before and after:

    $ bash scripts/ops/install-log-retention.sh --dry-run   # before
    ERROR: must run as root (pkexec)
    rc=1
    $ bash scripts/ops/install-log-retention.sh --dry-run   # after
    DRY RUN -- no files will be written.
    … 5 rotating patterns …
    rc=0

**Note for the next agent, it cost me a wrong turn:** this session runs in a
git worktree at `/tmp/ao-sessions/wt-ops-a`, so `/ALWAYSON/config/host/` does
**not** contain the staged files — `ls /ALWAYSON/config/host/journald-alwayson.conf`
→ *No such file or directory*, and the live
`logrotate-alwayson.conf` there is the older 1225-byte version. The installer
reads from `/ALWAYSON`, so from a worktree its preflight correctly refuses with
`staged source missing`. That is the guard working, not a bug.

**Operator action required:** run
`pkexec bash /ALWAYSON/scripts/ops/install-log-retention.sh`, then confirm one
rotation occurs (`logrotate -v /etc/logrotate.d/alwayson` or wait for
`logrotate.timer`).

Files changed: `scripts/ops/install-log-retention.sh` (new),
`config/host/logrotate-alwayson.conf` (header + subdirectory comment),
`agents/COORDINATION/…/17-…/section.md` (§17.5).