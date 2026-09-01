#!/usr/bin/env bash
# ALWAYS ON - restic-run.sh: encrypted restic backup of approved paths (3-2-1, Section 4.4).
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_dry_run_init "${1:-}"
envfile="$AO_ROOT/secrets/operations/restic.env"
[[ -f "$envfile" ]] || { echo "PENDING: $envfile not provisioned (Section 3.4 secrets approval)" >&2; exit 3; }
ao_run bash -c "set -a && source '$envfile' && restic backup '$AO_ROOT/config' '$AO_ROOT/artifacts' '$AO_ROOT/backups/postgres' '/media/scottw/500GBPHOTOGRAM/manifests' --tag alwayson"
(( AO_DRY_RUN )) || ao_audit "restic backup completed"
echo "OK: restic run finished"
