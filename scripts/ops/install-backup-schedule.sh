#!/usr/bin/env bash
# ALWAYS ON - privileged installer for recurring backup schedule (Section 17.1).
# Installs root-level systemd timers for nightly restic backup (03:30) and
# weekly repository integrity verification (Sun 04:30). Complements the
# scottw-level alwayson-db-dump.timer (nightly PostgreSQL dumps 03:00).
# Run via: pkexec bash /ALWAYSON/scripts/ops/install-backup-schedule.sh
set -Eeuo pipefail
[ "$(id -u)" -eq 0 ] || { echo "ERROR: must run as root (pkexec)" >&2; exit 1; }

install -m 0644 /dev/stdin /etc/systemd/system/alwayson-restic-backup.service <<'UNIT'
[Unit]
Description=ALWAYS ON nightly restic backup of approved paths
[Service]
Type=oneshot
ExecStart=/ALWAYSON/scripts/backup/restic-run.sh
TimeoutStartSec=7200
UNIT

install -m 0644 /dev/stdin /etc/systemd/system/alwayson-restic-backup.timer <<'UNIT'
[Unit]
Description=ALWAYS ON nightly restic backup timer (03:30)
[Timer]
OnCalendar=*-*-* 03:30:00
Persistent=true
RandomizedDelaySec=600
[Install]
WantedBy=timers.target
UNIT

install -m 0644 /dev/stdin /etc/systemd/system/alwayson-restic-verify.service <<'UNIT'
[Unit]
Description=ALWAYS ON weekly restic repository integrity check
[Service]
Type=oneshot
ExecStart=/ALWAYSON/scripts/backup/verify-backup.sh
TimeoutStartSec=7200
UNIT

install -m 0644 /dev/stdin /etc/systemd/system/alwayson-restic-verify.timer <<'UNIT'
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
systemctl enable --now alwayson-restic-backup.timer alwayson-restic-verify.timer
systemctl list-timers --no-pager | grep alwayson || true

echo '--- running one restic backup now to verify end-to-end ---'
systemctl start alwayson-restic-backup.service && echo 'RESTIC BACKUP RUN OK' || echo 'RESTIC BACKUP RUN FAILED (check journalctl -u alwayson-restic-backup)'
systemctl list-timers --no-pager | grep alwayson
echo 'OK: backup schedule installed'
