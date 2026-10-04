---
item: OPS-10
action: close
evidence: |
  $ find . -name '*restic*' -not -path './.git/*'   # (also ao-db-dump units checked the same way)
  ./systemd/backup/ao-restic-verify.timer
  ./systemd/backup/ao-restic-verify.service
  ./systemd/backup/ao-restic-prefetch.timer
  ./systemd/backup/ao-restic-prefetch.service
  ./systemd/backup/ao-restic-backup.timer
  ./systemd/backup/ao-restic-backup.service
  ./scripts/backup/restic-run.sh
  ./scripts/backup/verify-backup.sh
  ./scripts/restore/restore-restic-drill.sh

  $ grep -n 'ExecStart\|timer' scripts/ops/install-backup-schedule.sh
  15:ExecStart=/ALWAYSON/scripts/backup/restic-run.sh
  21:Description=ALWAYS ON nightly restic backup timer (03:30)
  39:Description=ALWAYS ON weekly restic integrity check timer (Sun 04:30)

  # the restore drill refuses every unsafe invocation (see OPS-24 evidence):
  $ bash scripts/restore/restore-restic-drill.sh --repo /nonexistent --scratch /ALWAYSON/data/evil ; echo rc=$?
  rc=1
  $ bash scripts/restore/restore-restic-drill.sh --repo /nonexistent ; echo rc=$?
  ERROR: --scratch is required (never defaults to a live path)
  rc=2
section: 17-backup-restore-monitoring-and-completion-criteria
---
New §17.1.1 "Named executors" gives every row of the §17.1 frequency table a
named script path, a systemd unit, a timer and a cadence. The defect was that
§16.1 listed `scripts/backup/` and `scripts/restore/` as empty directories
while ST-18 claimed active timers; both directories are now populated and the
six unit files exist under `systemd/backup/`.

The seven-step restore test now has a named executor —
`scripts/restore/restore-restic-drill.sh` — which is new in this session.
§17.1.1 states honestly that it has **no cadence**: nothing schedules it, so
§17.1's "Monthly" requirement is still unmet and that half of the item is
carried by OPS-24 rather than claimed here.

**Correction worth recording:** I first searched `quadlet/operations/` for the
restic units and got nothing, and my instinct was to record that they did not
exist. They do — under `systemd/backup/`. I had assumed a directory layout
instead of enumerating one, which is the single most expensive mistake available
in a repo this size. The units are also **not deployed**
(`ls ~/.config/containers/systemd/ | grep -i restic` → none deployed), because
they are root-level units installed by `install-backup-schedule.sh`, not
Quadlets.

Files changed: `agents/COORDINATION/…/17-…/section.md` (§17.1.1),
`scripts/restore/restore-restic-drill.sh` (new).