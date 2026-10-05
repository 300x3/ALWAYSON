#!/usr/bin/env bash
# ALWAYS ON - privileged installer for recurring backup schedule (Section 17.1).
# Installs root-level systemd timers for nightly restic backup (03:30) and
# weekly repository integrity verification (Sun 04:30). Complements the
# scottw-level ao-db-dump.timer (nightly PostgreSQL dumps 03:00).
# Run via: pkexec bash /ALWAYSON/scripts/ops/install-backup-schedule.sh
set -Eeuo pipefail
[ "$(id -u)" -eq 0 ] || { echo "ERROR: must run as root (pkexec)" >&2; exit 1; }

install -m 0644 /dev/stdin /etc/systemd/system/ao-restic-backup.service <<'UNIT'
[Unit]
Description=ALWAYS ON nightly restic backup of approved paths
[Service]
Type=oneshot
ExecStart=/ALWAYSON/scripts/backup/restic-run.sh
TimeoutStartSec=7200
# Operator approved 2026-10-04 (OPS-13). Linger is already yes and is a
# BINARY per-service setting, so the 20s is a separate systemd stop timeout.
# restic is not a daemon: it holds no state between runs, so a stop that
# interrupts a snapshot only loses the in-flight snapshot, which the next
# nightly run recreates. Without it, systemd's default 90s stop timeout makes
# a wedged restic hold the unit in 'stopping' long after the timer fires.
TimeoutStopSec=20
UNIT

install -m 0644 /dev/stdin /etc/systemd/system/ao-restic-backup.timer <<'UNIT'
[Unit]
Description=ALWAYS ON nightly restic backup timer (03:30)
[Timer]
OnCalendar=*-*-* 03:30:00
Persistent=true
RandomizedDelaySec=600
[Install]
WantedBy=timers.target
UNIT

install -m 0644 /dev/stdin /etc/systemd/system/ao-restic-verify.service <<'UNIT'
[Unit]
Description=ALWAYS ON weekly restic repository integrity check
[Service]
Type=oneshot
ExecStart=/ALWAYSON/scripts/backup/verify-backup.sh
TimeoutStartSec=7200
UNIT

install -m 0644 /dev/stdin /etc/systemd/system/ao-restic-verify.timer <<'UNIT'
[Unit]
Description=ALWAYS ON weekly restic integrity check timer (Sun 04:30)
[Timer]
OnCalendar=Sun *-*-* 04:30:00
Persistent=true
RandomizedDelaySec=600
[Install]
WantedBy=timers.target
UNIT

systemctl daemon-reload
systemctl enable --now ao-restic-backup.timer ao-restic-verify.timer
systemctl list-timers --no-pager | grep alwayson || true

# Retention, per the operator's 40 GB budget (2026-10-04, OPS-24/OPS-31).
# Installed as its own timer rather than appended to the backup unit so that a
# prune failure cannot fail the backup, and a backup failure cannot skip the
# prune: they are independent recovery concerns. The prune runs at 05:10, well
# after the 03:30 backup, so it trims what that night's snapshot just added.
# Retained: last 24 hourly, 7 daily, 4 weekly, 6 monthly, grouped per host+path.
install -m 0644 /dev/stdin /etc/systemd/system/ao-restic-retention.service <<'UNIT'
[Unit]
Description=ALWAYS ON restic retention and prune (40 GB budget)
# Runs after the backup so it trims what tonight's snapshot added.
After=ao-restic-backup.service
[Service]
Type=oneshot
Environment=RESTIC_ENV_FILE=/run/user/1000/ao-restic.env
ExecStartPre=/ALWAYSON/scripts/operations/fetch-restic-env.sh /run/user/1000/ao-restic.env
ExecStart=/ALWAYSON/scripts/backup/restic-retention.sh --env-file /run/user/1000/ao-restic.env --max-gb 40
TimeoutStartSec=7200
TimeoutStopSec=20
UNIT

install -m 0644 /dev/stdin /etc/systemd/system/ao-restic-retention.timer <<'UNIT'
[Unit]
Description=ALWAYS ON nightly restic retention timer (05:10)
[Timer]
OnCalendar=*-*-* 05:10:00
Persistent=true
RandomizedDelaySec=600
[Install]
WantedBy=timers.target
UNIT

systemctl daemon-reload
systemctl enable --now ao-restic-retention.timer
systemctl list-timers --no-pager | grep alwayson || true

echo '--- running one restic backup now to verify end-to-end ---'
systemctl start ao-restic-backup.service && echo 'RESTIC BACKUP RUN OK' || echo 'RESTIC BACKUP RUN FAILED (check journalctl -u ao-restic-backup)'
systemctl list-timers --no-pager | grep alwayson
echo 'OK: backup schedule installed'
