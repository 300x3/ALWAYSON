---
item: OPS-25
action: close
evidence: |
  $ ls -la /etc/logrotate.d/alwayson
  -rw-r--r-- 1 root root 4588 Oct  4 00:16 /etc/logrotate.d/alwayson

  $ cmp /etc/logrotate.d/alwayson /ALWAYSON/config/host/logrotate-alwayson.conf
  (identical)

  $ find /ALWAYSON/logs -name '*.log' ! -user scottw | wc -l
  0

  $ logrotate -d /etc/logrotate.d/alwayson | grep -c 'rotating pattern'
  5

  # an ordinary run first found nothing due - it said "already been rotated",
  # so exit 0 there was NOT evidence of a rotation:
  $ logrotate -v /etc/logrotate.d/alwayson
    Last rotated at 2026-10-04 00:00
    log does not need rotating (log has already been rotated)
  REAL_RUN_EXIT=0

  # forced, and it really rotated:
  $ logrotate -f -v /etc/logrotate.d/alwayson
    renaming /ALWAYSON/logs/installation/agent-install.log.15 to ....16 (rotatecount 400, ...)
    ... (renames .2 -> .3 through .15 -> .16)
  $ ls -1 /ALWAYSON/logs/*.log.[0-9] | wc -l
  13

  $ stat -c '%i %n' /ALWAYSON/logs/audit.log /ALWAYSON/logs/audit.log.1
  18223513 /ALWAYSON/logs/audit.log        <- new inode
  18219280 /ALWAYSON/logs/audit.log.1      <- rotated inode, different

  $ stat -c '%U:%G %a %n' /ALWAYSON/logs/audit.log
  scottw:scottw 664

  # the nocopytruncate hazard, checked rather than assumed:
  $ bash -c 'source scripts/lib/common.sh; ao_backup_run rotation-probe OK "..."'
  $ tail -1 /ALWAYSON/logs/backup.log
  2026-10-04T07:20:57+00:00 actor=scottw script=bash snapshot=rotation-probe result=OK ...
  $ stat -c %s /ALWAYSON/logs/backup.log.1
  1247          <- unchanged: writes went to the NEW file, none lost

  $ systemctl is-active logrotate.timer
  active
section: 17-backup-restore-monitoring-and-completion-criteria
---
Installed and confirmed by an observed rotation, not by an exit code.

Two things had to be fixed before the install would have worked. Two logs in
`operations/` — `pkexec-post-deploy.log` and `apply-20260831-fixes.log` — were
owned by root, so the `su scottw scottw` block could not rotate them. The first
attempt at fixing this gave them their own policy block, which was wrong: the
existing `operations/*.log` wildcard already matched them, so logrotate rejected
the whole file with `duplicate log entry for
/ALWAYSON/logs/operations/apply-20260831-fixes.log` and exit 1. That would have
made the daily timer fail. They are chowned to `scottw:scottw` instead; they are
the only two non-scottw logs under `/ALWAYSON/logs` and nothing needs them
root-owned. `find /ALWAYSON/logs -name '*.log' ! -user scottw` now returns 0.

The confirmation worth recording: an ordinary `logrotate -v` run returned
**exit 0 while rotating nothing** — it reported "log does not need rotating
(log has already been rotated)". Treating that exit code as proof would have
closed this item on a no-op. The forced run is the evidence: 13 rotated files
created, `agent-install.log` renumbered .2 through .16 against its 400-rotation
budget, and `audit.log` moved from inode 18219280 to 18223513 with the new file
created `scottw:scottw 0664`.

The policy uses `nocopytruncate`, which is only safe if writers reopen the file
per write. `ao_backup_run` and `ao_restore_test` in `scripts/lib/common.sh`
append with `>>` on every call and hold no descriptor, so a rename cannot
orphan a writer. Proved rather than assumed: after rotation, calling
`ao_backup_run` wrote into the new `backup.log` while `backup.log.1` stayed at
1247 bytes, so nothing was written into the rotated inode and lost.
