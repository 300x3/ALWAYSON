# ALWAYS ON - backup-postgres.sh: dump a domain PostgreSQL via podman exec.
# Usage: backup-postgres.sh <container> <db> <role-label> [--dry-run]
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_dry_run_init "${4:-}"
c="${1:?container}"; db="${2:?database}"; role="${3:?role label}"
out="$AO_ROOT/backups/postgres/${role}/$(date -u +%Y%m%dT%H%M%SZ)-${db}.sql.gz"
mkdir -p "$(dirname "$out")"
if ! podman ps --format '{{.Names}}' 2>/dev/null | grep -qx "$c"; then
  echo "PENDING: container $c not running yet" >&2; exit 3
fi
ao_run podman exec "$c" pg_dump -U "$db" "$db" | gzip -9 > "$out.tmp" && mv "$out.tmp" "$out"
(( AO_DRY_RUN )) || ao_audit "postgres backup role=$role db=$db file=$(basename "$out")"
echo "OK: $out"
