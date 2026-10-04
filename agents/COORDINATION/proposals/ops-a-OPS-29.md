---
item: OPS-29
action: update
evidence: |
  # OPS-29's stated remedy folder does not exist on the pCloud root:
  $ cd /media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE && find . -maxdepth 1 -iname '*RESTIC*'
  ./ALWAYSON-BACKUPS
  # the folder OPS-29 names, ALWAYSON-RESTIC2PCLOUD, is ABSENT — not "present but empty"

  # the repository that does exist, and it verifies:
  $ export RESTIC_REPOSITORY=/media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS
  $ restic snapshots --json
  count: 1
    56bf1af5 2026-10-03T08:59:59-07:00 ['alwayson-offsite-proof'] ['/ALWAYSON/artifacts','/ALWAYSON/config']
  $ restic check --read-data-subset=1/10
  no errors were found

  # and it is deliberately NOT scheduled:
  $ systemctl --user list-timers --all | grep -i restic
  ao-restic-prefetch.timer          # the only restic timer; no offsite timer
  $ grep -c 'ALWAYSON-BACKUPS\|offsite' scripts/backup/restic-run.sh
  0
section: 17-backup-restore-monitoring-and-completion-criteria
---
**This item contradicts OPS-30 in §19, and OPS-30 is the accurate one.** Both
are titled "Off-site restic repository does not exist". Measured this session:

- **OPS-30** says the operator chose
  `/media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS`, that it is
  initialised and verifies, and that it is deliberately not scheduled.
- **OPS-29** says the pCloud folder `ALWAYSON-RESTIC2PCLOUD` exists at the
  account root but is empty, and prescribes rclone WebDAV or SFTP.

OPS-29's folder is **absent entirely** — `find . -maxdepth 1 -iname '*RESTIC*'`
returns only `./ALWAYSON-BACKUPS`. OPS-29 describes a location that no longer
exists as described, and its prescribed remedy (a second rclone remote and a
WebDAV credential) was explicitly superseded by the operator's choice of a path
inside the running pCloud sync root, which replicates with no rclone remote at
all.

**Recommended to the compiler:** OPS-29 should be merged into OPS-30 as a
duplicate rather than tracked separately, since tracking both implies two
independent off-site workstreams and one of them describes a path that does not
exist. I am not editing §19 to do this.

**What genuinely remains open, and it is what OPS-31 also waits on:** the
off-site repository holds exactly **one** snapshot, tagged
`alwayson-offsite-proof`, covering only `config` and `artifacts`. It is not
referenced by `restic-run.sh` (grep count 0) and has no timer. Until it is
scheduled it mitigates total disk loss but is not a maintained off-site copy,
and — per the device-id measurement in the OPS-31 proposal — the local
repository is still on the same disk as the data it protects.

**Enabling it is an operator decision** and was not done: it means a recurring
privileged job writing to backup media inside the pCloud sync root.

Files changed: `agents/COORDINATION/…/17-…/section.md` (§17 intro, device-id
table and 3-2-1 status).