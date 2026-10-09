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

  # CORRECTION: an earlier version of this proposal said the units were "not
  # deployed", on `ls ~/.config/containers/systemd/ | grep -i restic` -> none.
  # That lookup was right and the conclusion wrong: these are ROOT systemd units,
  # not Quadlets, so they are never in the containers/systemd directory.
  $ systemctl is-enabled ao-restic-backup.timer ao-restic-verify.timer
  enabled
  enabled
  $ ls -la /etc/systemd/system/ao-restic-*.{timer,service}
  -rw-r--r-- 1 root root  453 Oct  2 20:21 ao-restic-backup.service
  -rw-r--r-- 1 root root  171 Oct  2 20:21 ao-restic-backup.timer
  ... 6 files total
  $ systemctl status ao-restic-backup.service --no-pager | head -8
     Active: inactive (dead) since Sun 2026-10-04 03:35:39 PDT; 9h ago
     Process: 3078186 ExecStart=/ALWAYSON/scripts/backup/restic-run.sh
                       (code=exited, status=0/SUCCESS)
  # and the nightly run really did work:
  $ journalctl -u ao-restic-backup.service --since '2026-10-04 03:00' \
      --until '2026-10-04 04:00' | grep -E 'Files:'
  Files:          46 new,    13 changed, 30190 unmodified
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

**Correction, and it strengthens the item rather than closing it.** An earlier
version of this proposal said the units were "not deployed" because
`ls ~/.config/containers/systemd/ | grep -i restic` returned nothing. The
measurement was right and the conclusion wrong: these are root-level systemd
units, not Quadlets, so they are never in the containers/systemd directory. They
are installed in `/etc/systemd/system/`, both timers `is-enabled` → `enabled`,
and `ao-restic-backup.service` exited `status=0/SUCCESS` 9 h ago having
processed `46 new, 13 changed, 30190 unmodified` files. So the nightly backup is
genuinely live, which §17.1.1 now states.

This is the third time this session drew an absence claim from a negative
lookup and it is worth naming the pattern rather than each instance: a negative
result from the wrong directory is not evidence of absence. The restic units were
looked up in a Quadlet directory; the Prometheus alerts mount was looked up in
the repository rather than the deployed copy; the journald drop-in was looked up
in a directory that does not exist on this host at all.

I also removed the three refusal commands from the evidence block and replaced
them. They belonged to OPS-24's drill, not to "named executors", and the exit
code recorded there was wrong: the refusals exit **2**, not 1. Re-measured
individually, all three, with no live path created by any of them — see
`ops-a-OPS-04.md`.

The cadence half of the item is unchanged and still honest: `restore-restic-drill.sh`
has **no timer**, so §17.1's "Monthly" restore-test requirement is unmet and
OPS-24 carries it.

Files changed: `agents/COORDINATION (README UPDATES)/…/17-…/section.md` (§17.1.1),
`scripts/restore/restore-restic-drill.sh` (new).