#!/usr/bin/env bash
# ALWAYS ON - backup-postgres.sh: dump a domain PostgreSQL via podman exec.
# Usage: backup-postgres.sh <container> <db> <role-label> [--dry-run] [<user>]
#   <user> optional; defaults to <db> (previous behaviour).
#   Set PODMAN_URL (e.g. unix:///run/ao-podman/sales.sock) to target a
#   remote/bridged rootless store instead of the invoking user's store.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_dry_run_init "${4:-}"
c="${1:?container}"; db="${2:?database}"; role="${3:?role label}"
puser="${5:-$db}"
out="$AO_ROOT/backups/postgres/${role}/$(date -u +%Y%m%dT%H%M%SZ)-${db}.sql.gz"
mkdir -p "$(dirname "$out")"
podman_cmd() {
  if [ -n "${PODMAN_URL:-}" ]; then podman --url "$PODMAN_URL" "$@"; else podman "$@"; fi
}
if ! podman_cmd ps --format '{{.Names}}' 2>/dev/null | grep -qx "$c"; then
  echo "PENDING: container $c not running yet" >&2; exit 3
fi
if ao_run podman_cmd exec "$c" pg_dump -U "$puser" "$db" | gzip -9 > "$out.tmp"; then
  mv "$out.tmp" "$out"
  chmod 0640 "$out"
  (( AO_DRY_RUN )) || ao_audit "postgres backup role=$role db=$db file=$(basename "$out")"
  echo "OK: $out"
else
  rm -f "$out.tmp"
  echo "FAILED: pg_dump container=$c db=$db" >&2
  exit 1
fi
