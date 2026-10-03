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
  # README 16.3 requires the backup journal to record failure as well as
  # success. With set -e a restic failure would otherwise abort at the
  # ao_run line with nothing written, so the failure is journalled on the
  # way out. The exit code is tested first: this trap also runs on SUCCESS,
  # and recording "FAILED" with exit code 0 would be a false failure entry
  # in the backup journal.
  trap 'rc=$?; if (( rc != 0 )); then ao_backup_run none FAILED "restic backup aborted with exit code $rc"; fi; rm -f "$cleanup_envfile"' EXIT
fi
# data/ was NOT covered here. That is where the bulk of the persistent state
# lives: data/ardupilot is 2.1G across ~30k files and data/corda-install is
# 282M. A restore from this set would bring back configuration but no
# operational data. The photogrammetry drive is excluded deliberately - it is
# the physical media, not a backup target.
ao_run bash -c "set -a && source '$envfile' && restic backup '$AO_ROOT/config' '$AO_ROOT/artifacts' '$AO_ROOT/backups/postgres' '$AO_ROOT/data/ardupilot' '$AO_ROOT/data/corda-install' '$AO_ROOT/data/sim-fabrication' '$AO_ROOT/data/sales' '$AO_ROOT/data/mapping' '$AO_ROOT/data/field' '$AO_ROOT/data/payment' '$AO_ROOT/data/ledger' --tag alwayson"
if (( AO_DRY_RUN )); then
  # A dry run backs nothing up, so it is not a backup run and must not be
  # recorded as one in the README 16.3 backup journal.
  ao_backup_run none DRY-RUN "restic backup not executed (--dry-run); no snapshot created"
else
  # Snapshot ID comes from restic itself, not from a guess. Recorded only on
  # success; a failure below is journalled by the trap and exits non-zero.
  snapshot="$(bash -c "set -a && source '$envfile' && restic snapshots --latest 1 --json 2>/dev/null" \
    | grep -oE '"short_id"[[:space:]]*:[[:space:]]*"[0-9a-f]+"' | head -1 \
    | grep -oE '[0-9a-f]{8,}' || true)"
  ao_backup_run "${snapshot:-unavailable}" OK "restic backup completed"
  ao_audit "restic backup completed"
fi
echo "OK: restic run finished"
