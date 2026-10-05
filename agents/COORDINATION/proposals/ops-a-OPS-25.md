---
item: OPS-25
action: update
evidence: |
  # *** SUPERSEDES the "NOT installed" lines in the earlier evidence block. ***
  # The logrotate half IS installed, byte-identical to source, and has rotated.
  $ ls -la /etc/logrotate.d/alwayson
  -rw-r--r-- 1 root root 5237 Oct  4 09:07 /etc/logrotate.d/alwayson
  $ cmp /etc/logrotate.d/alwayson /ALWAYSON/config/host/logrotate-alwayson.conf
  (identical - no output)
  $ logrotate -d /etc/logrotate.d/alwayson 2>&1 | grep -c 'rotating pattern'
  5
  # rotations are real, not merely configured:
  $ ls -1 /ALWAYSON/logs/*.log.[0-9] | wc -l
  13
  $ ls -1 /ALWAYSON/logs/operations/*.log.[0-9] | wc -l
  67
  $ find /ALWAYSON/logs -name '*.log' ! -user scottw | wc -l
  0

  # the journald half of the SAME installer is still absent, and the drop-in
  # directory does not exist on this host at all:
  $ ls -la /etc/systemd/journald.conf.d/
  ls: cannot access '/etc/systemd/journald.conf.d/': No such file or directory
  $ grep -n '^#\?SystemMaxUse\|^#\?SystemKeepFree\|^#\?MaxRetentionSec' /etc/systemd/journald.conf
  27:#SystemMaxUse=
  28:#SystemKeepFree=
  35:#MaxRetentionSec=0
  $ journalctl --disk-usage
  Archived and active journals take up 3.9G in the file system.
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
**Revision 2026-10-05: the "has genuinely rotated" claim above was resting on the
wrong evidence, and is now resting on the right one.**

Both earlier revisions of OPS-25 inferred rotation from rotated *files* being
present. Those files were created by the install-time **`logrotate -f`** forced
run, which §17.5.2 now shows is a different event from the one OPS-25's
acceptance criterion asks for ("confirm one rotation actually occurs"). A forced
run proves the policy parses and the permissions work; it does not prove the
unprivileged daily timer path works on a `su scottw scottw` policy.

The unattended run has now happened, and is attested by inode change-time rather
than content-time:

```
$ stat -c '%n  mtime=%y  ctime=%z' /ALWAYSON/logs/audit.log.1 /ALWAYSON/logs/backup.log.1
/ALWAYSON/logs/audit.log.1  mtime=2026-10-04 18:43:10   ctime=2026-10-05 00:22:50
/ALWAYSON/logs/backup.log.1 mtime=2026-10-04 10:35:39   ctime=2026-10-05 00:22:50
```

A rename updates ctime but not mtime, so `ctime=2026-10-05 00:22:50` is the
rotation instant. The live file was recreated empty at the same instant
(`operations-journal.log` mtime=ctime=00:22:50, size=0), which is the `create`
directive firing. One pass renamed all five blocks across two different rotate
budgets (14 and 400), which only a full timer-driven run produces:

```
$ find /ALWAYSON/logs -maxdepth 2 -newerct '2026-10-05 00:20' ! -newerct '2026-10-05 00:30' -printf '%p\n' | sort
/ALWAYSON/logs/audit.log.1
/ALWAYSON/logs/audit.log.2
/ALWAYSON/logs/backup
/ALWAYSON/logs/backup/db-dump.log.1
/ALWAYSON/logs/backup/db-dump.log.2
/ALWAYSON/logs/backup.log.1
/ALWAYSON/logs/backup.log.2
/ALWAYSON/logs/operations-journal.log.1
/ALWAYSON/logs/operations-journal.log.2
/ALWAYSON/logs/operations-journal.log
```

No `*.log.N` file has a ctime between the install (2026-10-04 09:07) and the
timer (2026-10-05 00:22), so no human ran a rotation in that window and the
timer is the only candidate cause. Full write-up in §17.5.2.

**The logrotate half of OPS-25 is now met on the correct evidence and I am
recommending the compiler mark that half CLOSED.** The journald half of the same
installer remains untouched and is unchanged from the revision above:
`/etc/systemd/journald.conf.d/` still does not exist.

**New finding, filed separately as OPS-36 (superseding my own earlier
OPS-36 proposal):** the policy's own comment justifying `nocopytruncate` is
false, and now that rotation runs unattended the consequence is real rather than
latent. Two Podman `conmon` processes hold descriptors on the *rotated* inode:

```
$ lsof /ALWAYSON/logs/sim-gz-server.log.1
COMMAND     PID   USER FD   TYPE DEVICE SIZE/OFF     NODE NAME
conmon   1195162 scottw 6w   REG  259,2  1437117 18222278 /ALWAYSON/logs/sim-gz-server.log.1

$ stat -c '%n ino=%i links=%h size=%s' /ALWAYSON/logs/sim-gz-server.log*
/ALWAYSON/logs/sim-gz-server.log    ino=18223611 links=1 size=0
/ALWAYSON/logs/sim-gz-server.log.1  ino=18222278 links=1 size=1437117
```

Nothing has been lost yet and I want that stated precisely rather than
overclaimed — the detached inode is still linked and **not currently growing**
(two samples 20 s apart both 1437117 bytes; Gazebo has written nothing since
2026-10-04 09:25). The fault is that *when* Gazebo next writes it writes to an
inode the policy no longer tracks, and after `rotate 14` shifts that inode is
unlinked while still being written. Fixing it means `copytruncate` or moving
those containers off this path — a container-logging change, not a comment edit.

**Still OPEN as a whole, but the logrotate half is now done, and this supersedes
the earlier "neither half is done" statement.** That was true when written;
someone installed the policy in the interim. The file is root-owned, 5237 B,
**byte-identical** to the in-tree source (`cmp` → no output), dated Oct 4 09:07.

It is not merely installed, it has **actually rotated**: 13 rotated files at
`logs/*.log.[0-9]` and 67 in `logs/operations/`. That is exactly the acceptance
test §19.1 sets — "install it, then confirm one rotation actually occurs" — so
that half is met. The ownership precondition also holds:
`find /ALWAYSON/logs -name '*.log' ! -user scottw` → 0.

**The item stays open because the same installer also handles the journald
drop-in, and that half is still not installed.** The evidence is stronger than
"file not found": the drop-in *directory* does not exist on this host, so
nothing could have been written into it. §17.5's table now shows the split
explicitly — five log blocks "Installed and rotating", journald "NOT installed".
Presenting all six as one uniform staged state is precisely what made the first
claim wrong, and it is the reason the table was rewritten rather than patched.

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