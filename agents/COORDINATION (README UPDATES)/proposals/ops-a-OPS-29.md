---
item: OPS-29
action: update
supersedes: |
  The evidence line `find . -maxdepth 1 -iname '*RESTIC*'` → `./ALWAYSON-BACKUPS`
  recorded in my earlier version of this proposal was FALSE and is retracted.
  ALWAYSON-BACKUPS contains no substring "RESTIC", so that find cannot have
  returned it. The claim "the folder OPS-29 names, ALWAYSON-RESTIC2PCLOUD, is
  ABSENT" is also retracted — see the correction below.
evidence: |
  # RETRACTION, re-measured 2026-10-04. My earlier claim that
  # ALWAYSON-RESTIC2PCLOUD is ABSENT was WRONG. It exists at the pCloud ACCOUNT
  # ROOT, and it is empty — exactly as OPS-29's row says.
  $ ls -d /home/scottw/pCloudDrive/ALWAYSON-RESTIC2PCLOUD
  /home/scottw/pCloudDrive/ALWAYSON-RESTIC2PCLOUD
  $ ls -la /home/scottw/pCloudDrive/ALWAYSON-RESTIC2PCLOUD
  total 0
  drwxr-xr-x 2 scottw scottw 4096 Sep 30 23:00 .
  drwxr-xr-x 35 scottw scottw 4096 Sep 30 22:56 ..

  # the error was searching only the USB disk's sync root, a DIFFERENT tree:
  $ find /media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE -maxdepth 1 -iname '*RESTIC*'
  (no output)

  # which also means my earlier evidence line was impossible on its face:
  #   ALWAYSON-BACKUPS contains no substring "RESTIC", yet I recorded it as
  #   the output of `find -iname '*RESTIC*'`. I did not check the output
  #   against the pattern.

  # the repository that does exist, and it verifies:
  $ set -a; . /run/user/1000/ao-restic.env; set +a
  $ export RESTIC_REPOSITORY=/media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS
  $ restic snapshots
  56bf1af5  2026-10-03 08:59:59  scottw-ms7b44  alwayson-offsite-proof
            /ALWAYSON/artifacts  304.564 KiB
            /ALWAYSON/config
  1 snapshots
  $ restic check --read-data-subset=1/10
  no errors were found

  # ...and it has replicated into the live pCloud mount, as a separate inode:
  $ stat -c '%d %i %n' /media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS \
                        /home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS
  2049 5505025 /media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS
   218 211841 /home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS
  $ RESTIC_REPOSITORY=/home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS restic check --read-data-subset=1/10
  no errors were found

  # and it is deliberately NOT scheduled:
  $ systemctl --user list-timers --all --no-pager | grep -i restic
  ao-restic-prefetch.timer          # the only restic timer; no offsite timer
  $ grep -c 'ALWAYSON-BACKUPS\|offsite' /ALWAYSON/scripts/backup/restic-run.sh
  0
section: 17-backup-restore-monitoring-and-completion-criteria
---
**This item and OPS-30 are duplicates, and OPS-30 is the one with the evidence.
Both are titled "Off-site restic repository does not exist".**

**I have to retract my own earlier finding on this item.** My previous OPS-29
proposal said the folder `ALWAYSON-RESTIC2PCLOUD` was "ABSENT entirely" and
recommended merging the row away as describing a path that "does not exist".
**That was wrong.** Measured again today:

```
$ ls -d /home/scottw/pCloudDrive/ALWAYSON-RESTIC2PCLOUD
/home/scottw/pCloudDrive/ALWAYSON-RESTIC2PCLOUD
$ ls -la /home/scottw/pCloudDrive/ALWAYSON-RESTIC2PCLOUD
total 0
```

The folder exists at the pCloud **account root** and is empty — which is exactly
what OPS-29's row states, word for word ("exists at the account root but is empty
and nothing has been uploaded"). **OPS-29 was right and I contradicted a correct
row.** The compiler should not treat that part of it as false.

**How I got it wrong, twice, and the class of bug.** I searched
`/media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/` — the sync root on the USB disk —
and generalised a negative result to "anywhere". There are two distinct trees
here (device 2049 local ext4, device 218 pCloud FUSE) and I had conflated them.
Worse, my evidence line was `find … -iname '*RESTIC*'` returning `./ALWAYSON-BACKUPS`,
which is self-evidently impossible: that name contains no "RESTIC". I recorded an
output without ever comparing it to the pattern I matched on. That is the real
failure — not the wrong path, but transcribing a plausible-looking result instead
of reading it. A find output that does not match its own glob is a self-check I
should have run, and it would have caught the error immediately.

**What still stands from my earlier proposal.** The remedy is superseded: OPS-29
prescribes rclone WebDAV or SFTP, but the operator chose a path inside the running
pCloud sync root, which replicates with no rclone remote and no WebDAV credential
(`scripts/backup/pcloud-restic-setup.sh` is retained only as an unused fallback).
So the *remedy* is obsolete even though the *observation* is correct.

**Recommended to the compiler:** merge OPS-29 into OPS-30 as a duplicate, since
tracking both implies two independent workstreams. When merging, **keep OPS-29's
"folder exists and is empty" wording and discard my retraction of it.**

**What genuinely remains open (also what OPS-31 waits on):** the off-site
repository holds exactly **one** snapshot, tagged `alwayson-offsite-proof`,
covering only `config` and `artifacts` — 304 KiB, no `data/`, `logs/` or
`backups/`. `grep` of `restic-run.sh` for the off-site path returns 0 and there is
no off-site timer, so it is not a maintained copy. Until it is scheduled and
carries the nightly path set, it is a working proof, not a backup.

**Enabling it is an operator decision** and was not done: it means a recurring
privileged job writing to backup media inside the pCloud sync root.

Files changed: `agents/COORDINATION (README UPDATES)/…/17-…/section.md` (§17 intro device table;
§17.1.1.1 corrected; new §17.1.1.2).