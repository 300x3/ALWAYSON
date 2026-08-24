# ALWAYS ON - rotate-logs.sh: compress logs older than 14 days into dated archives.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_dry_run_init "${1:-}"
find "$AO_ROOT/logs" -type f -name '*.log' -mtime +14 ! -name 'audit.log' -print0 |
  while IFS= read -r -d '' f; do ao_run gzip -9 "$f"; done
(( AO_DRY_RUN )) || ao_audit "rotated logs older than 14 days"
echo "OK: log rotation complete"
