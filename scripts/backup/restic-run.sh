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
  #
  # `--latest 1` returns one snapshot PER PATH GROUP, not one snapshot overall.
  # This backup passes 11 paths in a single restic invocation, so the array
  # holds one element per path, each from a different timestamp, and `head -1`
  # picks the FIRST element rather than the newest. Measured on a scratch repo
  # 2026-10-03: 2 path groups produced a 2-element array whose head was the
  # OLDER snapshot. That made the backup journal record a stale ID forever:
  # /ALWAYSON/logs/backup.log showed 548d9910 on three consecutive runs while
  # journalctl showed the real IDs e79edfbf and fbc25f93.
  #
  # Fix: sort by the snapshot time field and take the maximum explicitly
  # instead of trusting array order, and filter to this run's --tag.
  snapshot="$(bash -c "set -a && source '$envfile' && restic snapshots --tag alwayson --json 2>/dev/null" \
    | python3 -c 'import json,sys
try:
    snaps = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if snaps:
    print(max(snaps, key=lambda s: s.get("time",""))["short_id"])' || true)"
  ao_backup_run "${snapshot:-unavailable}" OK "restic backup completed"
  ao_audit "restic backup completed"
fi
echo "OK: restic run finished"
