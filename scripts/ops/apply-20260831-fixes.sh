#!/usr/bin/env bash
# ALWAYS ON - combined privileged fixes, 2026-08-31 (operator-authorized via pkexec):
#  1. Run quadlet/operations/pkexec-post-deploy.sh (WebODM system-store recovery +
#     Metabase metaread role)
#  2. Fix ownership of /ALWAYSON/backups/postgres (root-owned from Aug 25 system-store
#     era) so the scottw-level db-dump timer can write
#  3. Fix /etc/systemd/user/ao-ardupilot-sitl.service: remove --console (stdio mode,
#     exits under systemd) and unsupported --out flags; SITL serves MAVLink on TCP 5760
#  4. Install recurring backup schedule (restic nightly 03:30 + weekly verify Sun 04:30)
# Idempotent. Log: /ALWAYSON/logs/operations/apply-20260831-fixes.log
set -u
LOG=/ALWAYSON/logs/operations/apply-20260831-fixes.log
exec > >(tee -a "$LOG") 2>&1
printf '===== %s : apply-20260831-fixes =====\n' "$(date --iso-8601=seconds)"

step '1. pkexec-post-deploy (WebODM + metaread role)'
bash /ALWAYSON/quadlet/operations/pkexec-post-deploy.sh || echo 'NOTE: pkexec-post-deploy reported errors (review its log)'

step '2. Fix /ALWAYSON/backups/postgres ownership for scottw db-dump timer'
chown -R scottw:scottw /ALWAYSON/backups/postgres
chmod -R u=rwX,g=rX,o-rwx /ALWAYSON/backups/postgres
ls -ld /ALWAYSON/backups/postgres

step '3. Fix ao-ardupilot-sitl.service flags'
U=/etc/systemd/user/ao-ardupilot-sitl.service
if [ -f "$U" ]; then
  cp -n "$U" "${U}.orig-20260831" || true
  sed -i 's/ --console//g; s/ --out=udp:127\.0\.0\.1:14550//g; s/ --out=udp:127\.0\.0\.1:14551//g' "$U"
  grep -n 'ExecStart' "$U"
  echo 'NOTE: run `systemctl --user daemon-reload` as scottw to pick up the fix'
else
  echo "unit not found: $U"
fi

step '4. Install recurring backup schedule (restic nightly + weekly verify)'
bash /ALWAYSON/scripts/ops/install-backup-schedule.sh

printf '===== %s : apply-20260831-fixes done =====\n' "$(date --iso-8601=seconds)"
