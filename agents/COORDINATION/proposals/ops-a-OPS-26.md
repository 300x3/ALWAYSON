---
item: OPS-26
action: update
evidence: |
  # the drop-in directory itself does not exist, so nothing could be installed
  $ ls -la /etc/systemd/journald.conf.d/
  ls: cannot access '/etc/systemd/journald.conf.d/': No such file or directory
  $ grep -n '^#\?SystemMaxUse\|^#\?SystemKeepFree\|^#\?MaxRetentionSec' /etc/systemd/journald.conf
  27:#SystemMaxUse=
  28:#SystemKeepFree=
  35:#MaxRetentionSec=0
  $ journalctl --disk-usage
  Archived and active journals take up 3.9G in the file system.
  $ df -h / | tail -1
  /dev/nvme0n1p2  458G  307G  128G  71% /

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

**Status corrected 2026-10-04: the log blocks are installed and rotating; only
the journald half remains aspirational.** The table above previously marked all
six rows "Staged, not installed". The logrotate half was installed in the interim
(`/etc/logrotate.d/alwayson`, root-owned, 5237 B, byte-identical to source by
`cmp`) and has genuinely rotated — 13 files match `logs/*.log.[0-9]`, 67 match
`logs/operations/*.log.[0-9]`. The journald half is still absent, and the
evidence is now stronger than "not found":

    $ ls -la /etc/systemd/journald.conf.d/
    ls: cannot access '/etc/systemd/journald.conf.d/': No such file or directory

The drop-in *directory* does not exist, so nothing could have been installed
into it. `journalctl --disk-usage` re-measured at **3.9G**, and every effective
cap is still commented out (`SystemMaxUse`, `SystemKeepFree`, `MaxRetentionSec`
all `#`-prefixed). So `SystemMaxUse=4G` and `MaxRetentionSec=90day` remain
proposals, and this half of OPS-26 needs one privileged command.

Everything below about the *design* of the budgets stands unchanged — the 400-day
subdirectory budget, the reasoning against `maxsize`, and the staging decision
are unaffected by which half is installed. Only the "is it live" column changed.

**Measurement error worth preserving from the first pass of this item:** I ran
`du -sh logs/...` from the session worktree and got `No such file or directory`
for all four directories, and nearly recorded the sizes as absent. The live tree
at `/ALWAYSON` is the authority and returns real values. This is the same
worktree-vs-live confusion that produced the wrong "not deployed" claim in
OPS-10 and the wrong "not installed" claim here — three items in one session,
all from measuring the wrong tree or the wrong directory.

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