---
item: OPS-37
action: new
section: 17-backup-restore-monitoring-and-completion-criteria
evidence: |
  # NEW ITEM. Next free id after OPS-36 (19.1 tops out at OPS-34; OPS-35 and
  # OPS-36 are my own unmerged proposals). Never renumbered.

  # FINDING: the weekly restic integrity check has never succeeded. One run ever.

  $ journalctl -u ao-restic-verify.service --no-pager | grep -c Starting
  1

  $ journalctl -u ao-restic-verify.service --no-pager -o short-iso
  2026-10-04T04:32:01-07:00 verify-backup.sh[3251293]: ERROR: root restic execution requires RESTIC_ENV_FILE from the operator wallet session
  2026-10-04T04:32:01-07:00 systemd[1]: ao-restic-verify.service: Main process exited, code=exited, status=3/NOTIMPLEMENTED
  2026-10-04T04:32:01-07:00 systemd[1]: ao-restic-verify.service: Failed with result 'exit-code'.

  # cause: the two units installed by the SAME script disagree about the env file.
  $ grep -n 'Environment\|ExecStart' /etc/systemd/system/ao-restic-backup.service
  8:Environment=RESTIC_ENV_FILE=/run/user/1000/ao-restic.env
  9:ExecStart=/ALWAYSON/scripts/backup/restic-run.sh

  $ grep -n 'Environment\|ExecStart' /etc/systemd/system/ao-restic-verify.service
  5:ExecStart=/ALWAYSON/scripts/backup/verify-backup.sh

  # both scripts fall back to a path that does not exist on this host:
  $ ls -l /run/alwayson/restic.env
  ls: cannot access '/run/alwayson/restic.env': No such file or directory

  # so the "no env file" branch fires, and as root that branch is a refusal (exit 3),
  # not a wallet fetch. verify-backup.sh:10-13.

  # the backup timer is unaffected - three consecutive parent-chained snapshots:
  $ journalctl -u ao-restic-backup.service --since 2026-10-03 | grep -E 'snapshot .* saved|using parent'
  2026-10-03T08:12:24  snapshot fbc25f93 saved
  2026-10-04T03:35:38  using parent snapshot fbc25f93 / snapshot 0548f116 saved
  2026-10-05T03:32:47  using parent snapshot 0548f116 / snapshot c249b5db saved

  PREPARED FIX (one line, NOT applied - install-backup-schedule.sh is not a file
  this session owns, editing needs root, and re-running it rewrites
  /etc/systemd/system/):
    add to the ao-restic-verify.service heredoc in
    scripts/ops/install-backup-schedule.sh:
        Environment=RESTIC_ENV_FILE=/run/user/1000/ao-restic.env
        ExecStartPre=/ALWAYSON/scripts/operations/fetch-restic-env.sh /run/user/1000/ao-restic.env
  The retention unit at lines 74-76 already does exactly this, so there is an
  in-repo precedent to copy rather than invent.

  NEEDS EXPLICIT OPERATOR APPROVAL: yes - root write to /etc/systemd/system.
---
