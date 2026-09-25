#!/usr/bin/env bash
# ALWAYS ON - verify-backup.sh: weekly repository integrity check (Section 4.4).
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
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
bash -c "set -a && source '$envfile' && restic check --read-data-subset=5%"
ao_audit "restic integrity check completed"
echo "OK: repository integrity verified"
