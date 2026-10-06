---
item: OPS-31
action: update
evidence: |
  # device ids re-measured — local repo and the data share one device:
  $ for p in /ALWAYSON /var/backups/alwayson-restic \
      /media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS; do
      printf '%s -> %s\n' "$p" "$(stat -c %d "$p")"; done
  /ALWAYSON -> 66306
  /var/backups/alwayson-restic -> 66306
  /media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS -> 2049

  # the off-site repository exists, verifies, and holds ONE snapshot:
  $ restic check --read-data-subset=1/10
  no errors were found
  $ restic snapshots --json
  count: 1   (56bf1af5, paths: /ALWAYSON/config, /ALWAYSON/artifacts)

  # ...but it is not maintained, so it is not yet a second copy:
  $ grep -c 'ALWAYSON-BACKUPS\|offsite' scripts/backup/restic-run.sh
  0
section: 17-backup-restore-monitoring-and-completion-criteria
---
**Mitigated but still OPEN — this item is unclosable on evidence alone, and
that is the finding.** Measured by device id:

| Path | Device | Media |
|---|---|---|
| `/ALWAYSON` (the data) | 66306 | root disk |
| `/var/backups/alwayson-restic` (local repo) | **66306** | **same disk as the data** |
| `…/PCLOUD_STORAGE/ALWAYSON-BACKUPS` (off-site) | 2049 | separate media |

The local repository cannot survive loss of the root disk. The off-site
repository is on genuinely different physical media and verifies clean, so
**3-2-1 is now partially met** — copy two is still on the root disk, but a
host-disjoint copy exists. §17 previously claimed flatly "Nothing outside this
host currently holds a copy"; that is no longer true and has been corrected in
the section rather than left to drift.

**Why it stays open anyway.** A single unmaintained snapshot is not a copy. The
off-site repository holds exactly one snapshot, tagged
`alwayson-offsite-proof`, covering only `config` and `artifacts`; it is not
referenced by `restic-run.sh` and has no timer. Until it is scheduled and
holds a series, it mitigates total disk loss but does not satisfy "one
off-site copy" in the sense the policy intends.

`ao-egress-archive` is not a substitute and §17 says so explicitly: §11.6 makes
it a sale-transfer store with no restore duty.

**Blocked on an operator decision, deliberately not taken:** scheduling a
recurring privileged job that writes backup media into the live pCloud sync
root. That touches backup data and creates a recurring privileged action, so
I stopped rather than doing it unasked.

Files changed: `agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md` (§17 intro device-id
table and 3-2-1 status).