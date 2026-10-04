---
item: OPS-26
action: update
evidence: |
  # journald today: 4G in use, shipped caps all commented out
  $ journalctl --disk-usage
  Archived and active journals take up 4G in the file system.
  $ grep -n '^#*SystemMaxUse\|^#*MaxRetentionSec' /etc/systemd/journald.conf
  27:#SystemMaxUse=
  35:#MaxRetentionSec=0
  $ df -h /
  /dev/nvme0n1p2  458G  308G  127G  71% /

  # the staged drop-in, effective settings only:
  $ grep -vE '^\s*#|^\s*$' config/host/journald-alwayson.conf
  [Journal]
  SystemMaxUse=4G
  SystemKeepFree=8G
  SystemMaxFileSize=256M
  MaxRetentionSec=90day
  RuntimeMaxUse=200M
  RuntimeKeepFree=100M

  # subdirectory sizes, measured against the LIVE tree (/ALWAYSON), not the worktree:
  $ cd /ALWAYSON && du -sh logs/operations logs/gpu-runtime logs/backup logs/installation
  580K  logs/operations
  12K   logs/gpu-runtime
  28K   logs/backup
  288K  logs/installation
section: 17-backup-restore-monitoring-and-completion-criteria
---
**Retention is now stated per class; installation still needs root.** §17.5
carries a table giving each log class its rotation policy, its budget and
whether it is active. Measured and stated:

| Class | Budget |
|---|---|
| `logs/*.log` top level | 14 rotations, daily |
| `logs/{operations,installation,backup,gpu-runtime}/` | 400 rotations, daily |
| journald | `SystemMaxUse=4G`, `MaxRetentionSec=90day`, `SystemKeepFree=8G` |

Two decisions worth defending, because both look wrong at a glance:

- **The subdirectories get 400 days, not 14.** They hold per-operation audit
  records that §16.3 exists to preserve; rotating them on the same schedule as
  top-level files would destroy the evidence. 400 days covers four quarterly
  DR exercises plus margin. It is *age*-based (`rotate 400` with `daily`) and
  not `maxsize`, because `maxsize` evicts the **newest** file when a threshold
  is exceeded — precisely backwards for an audit trail.
- **The budgets are generous headroom, not a disk-pressure response.** Measured
  sizes are `backup` 28K, `gpu-runtime` 12K, `installation` 288K, `operations`
  580K on a 458G filesystem with 127G free. If a future measurement shows
  `operations/` growing large, the budget can be narrowed per directory;
  nothing today justifies it.

`MaxRetentionSec=90day` is the setting that actually changes behaviour.
`SystemMaxUse=4G` alone is roughly what is already in use (4G measured), so it
evicts nothing on a normal day. What is being removed today is the
**unbounded** forensic window: the shipped `journald.conf` has every cap
commented out, so the effective ceiling is a size-based default with no age
limit at all. Backup and restore evidence is **not** lost to the 90-day cap —
it lives in `/ALWAYSON/logs/` and `/ALWAYSON/backups/` on the 400-day budget,
not in journald.

**Measurement error I made and corrected:** I first ran `du -sh logs/...` from
the session worktree and got `No such file or directory` for all four, then
almost recorded the sizes from the worktree as absent. The live tree at
`/ALWAYSON` is the authority and returns the values above. Re-measuring also
showed `operations/` had grown 572K → 580K as concurrent sessions logged,
which is itself evidence these directories are append-only and live — so the
§17.5 text was updated rather than left quoting the stale figure.

The drop-in is staged as `journald-alwayson.conf` for installation at
`/etc/systemd/journald.conf.d/60-alwayson-retention.conf`, deliberately **not**
as an edit of the shipped `journald.conf`, which a package upgrade overwrites.

**Consequence while this stays uninstalled**, recorded in §17.5:
`sim-gz-server.log` has no size cap — the top-level policy rotates by age, not
by size — so a chatty Gazebo session grows that file without bound, and the
subdirectories grow without bound too. Neither is a capacity risk today; both
are unbounded in principle.

Files changed: `config/host/journald-alwayson.conf` (new),
`config/host/logrotate-alwayson.conf` (four subdirectory blocks),
`agents/COORDINATION/…/17-…/section.md` (§17.5).