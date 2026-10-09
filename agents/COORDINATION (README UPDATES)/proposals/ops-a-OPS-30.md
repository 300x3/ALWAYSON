---
item: OPS-30
action: update
evidence: |
  # The repository exists, opens with the production credential, and verifies:
  $ set -a; . /run/user/1000/ao-restic.env; set +a
  $ export RESTIC_REPOSITORY=/media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS
  $ restic cat config
  { "version": 2,
    "id": "d22cddc074532b53bcea8ee739c3b7b7107d9fd3baa3224125d0e569fbfb94be",
    "chunker_polynomial": "33c903993a9dcf" }
  $ restic snapshots
  56bf1af5  2026-10-03 08:59:59  scottw-ms7b44  alwayson-offsite-proof
            /ALWAYSON/artifacts  304.564 KiB
            /ALWAYSON/config
  1 snapshots
  $ restic check --read-data-subset=1/10
  no errors were found

  # NEW THIS RUN: it has replicated into the live pCloud mount, distinct inode
  # and distinct device — two real trees, not a symlink:
  $ stat -c '%d %i %n' /media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS \
                        /home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS
  2049 5505025 /media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS
   218 211841 /home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS
  $ findmnt -no SOURCE,FSTYPE /home/scottw/pCloudDrive
  pCloud.fs  fuse.pCloud.AppImage

  # and the REPLICATED copy verifies independently from the pCloud side:
  $ export RESTIC_REPOSITORY=/home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS
  $ restic snapshots
  56bf1af5  2026-10-03 08:59:59  scottw-ms7b44  alwayson-offsite-proof
  1 snapshots
  $ restic check --read-data-subset=1/10
  no errors were found

  # ...but it is still NOT maintained:
  $ grep -c 'ALWAYSON-BACKUPS\|offsite' /ALWAYSON/scripts/backup/restic-run.sh
  0
  $ systemctl --user list-timers --all --no-pager | grep -i restic
  Sun 2026-10-04 20:30:54 PDT ... ao-restic-prefetch.timer

  # the password was read only as a length; no secret value is recorded:
  pwlen=44
section: 17-backup-restore-monitoring-and-completion-criteria
---
**New proposal for OPS-30 — the one item of my thirteen that had no proposal of
its own.** (Everything below is re-measured today, 2026-10-04; nothing is carried
over from the earlier run unverified.)

**The row's title is now false in a good way.** "Off-site restic repository does
not exist" — it does exist, it decrypts with the production credential, it
verifies clean, and **this run establishes something the earlier proposals did
not: it has replicated to pCloud.**

```
$ stat -c '%d %i %n' /media/…/PCLOUD_STORAGE/ALWAYSON-BACKUPS \
                      /home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS
2049 5505025 /media/…/PCLOUD_STORAGE/ALWAYSON-BACKUPS
 218 211841 /home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS
```

Different device id (2049 local ext4 vs 218 pCloud FUSE) **and** different inode,
so these are two real trees. The FUSE mount is live (`pCloud.fs`), and the
replicated repository opens and checks clean from the pCloud side:

```
$ RESTIC_REPOSITORY=/home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS \
    restic check --read-data-subset=1/10
no errors were found
```

That is the meaningful upgrade: a copy that has actually left the machine, which
is what "off-site" is supposed to mean. My earlier proposals described the USB-disk
copy only and were careful to call it local-but-disjoint; that understated it.

**Honest limit on that claim.** This proves the files are present and restorable
through the pCloud mount. It does **not** independently prove the remote account
holds them — that needs a pCloud-side status query I did not run, and I am not
going to assert account state I did not measure. Read it as "off-site and
verifiable from the mount: proven", "uploaded to the account: supported, unconfirmed".

**Why it stays Open anyway.** The repository is real but it is not yet a backup:

- it holds **one** snapshot, `56bf1af5`, tagged `alwayson-offsite-proof`;
- that snapshot is **304 KiB / 103 files, `config` and `artifacts` only** — no
  `data/`, no `logs/`, no `backups/`;
- `grep -c 'ALWAYSON-BACKUPS\|offsite' restic-run.sh` → **0**, and the only
  restic timer is `ao-restic-prefetch.timer`. Nothing refreshes it.

So it is a verified proof of mechanism, not a maintained copy of anything that
would be lost with the host. **The acceptance criterion that actually matters is
not "create a repository" — it is "the off-host repository carries the same path
set as the nightly job".** That is a larger copy than the operator has approved
for automatic off-site transfer.

**One property worth stating because it is easy to over-credit:** the 1TB disk is
*removable, locally attached* media that happens to sit inside a synced folder.
When it is not attached, nothing is written and nothing detects that. The real
guarantee is "a copy exists and replicates when the disk is attached", not "a copy
is maintained". Only scheduling plus a liveness check upgrades it.

**Blocked on an operator decision, deliberately not taken.** Scheduling a recurring
privileged job that writes backup media into the live pCloud sync root touches
backup data and creates a recurring privileged action. I stopped rather than doing
it unasked. Enabling it, and approving the off-site path set, are both operator
calls.

Files changed: `agents/COORDINATION (README UPDATES)/…/17-…/section.md` (new §17.1.1.2; §17.1
device table now carries the pCloud row).

*Related, and a retraction to carry forward: see my revised `ops-a-OPS-29.md`.
I had wrongly reported `ALWAYSON-RESTIC2PCLOUD` as absent. It exists and is
empty, exactly as OPS-29 states. Do not merge that row away on my earlier say-so.*