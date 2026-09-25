#!/usr/bin/env bash
# ALWAYS ON - restic-run.sh: encrypted restic backup of approved paths (3-2-1, Section 4.4).
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_dry_run_init "${1:-}"
envfile="${RESTIC_ENV_FILE:-/run/alwayson/restic.env}"
cleanup_envfile=""
if [[ ! -f "$envfile" ]]; then
  if [[ "$(id -u)" -eq 0 ]]; then
    echo "ERROR: root restic execution requires RESTIC_ENV_FILE from the operator wallet session" >&2
    exit 3
  fi
  envfile="$(mktemp)"
  cleanup_envfile="$envfile"
  /ALWAYSON/scripts/operations/fetch-restic-env.sh "$envfile"
  trap 'rm -f "$cleanup_envfile"' EXIT
fi
ao_run bash -c "set -a && source '$envfile' && restic backup '$AO_ROOT/config' '$AO_ROOT/artifacts' '$AO_ROOT/backups/postgres' '/media/scottw/500GBPHOTOGRAM/manifests' --tag alwayson"
(( AO_DRY_RUN )) || ao_audit "restic backup completed"
echo "OK: restic run finished"
