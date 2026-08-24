# ALWAYS ON - cleanup-approved-temp-data.sh: delete ONLY within explicitly approved dirs.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_dry_run_init "${1:-}"
approved=(
  "/media/scottw/500GBPHOTOGRAM/tmp/processing"
  "/ALWAYSON/tmp"
)
for d in "${approved[@]}"; do
  [[ -d "$d" ]] || continue
  find "$d" -mindepth 1 -maxdepth 1 -mtime +7 -print0 | while IFS= read -r -d '' p; do
    case "$p" in "$d"/*) ;; *) echo "REFUSING outside approved dir: $p" >&2; continue;; esac
    ao_run rm -rf --one-file-system "$p"
  done
done
(( AO_DRY_RUN )) || ao_audit "cleaned approved temp directories (>7 days)"
echo "OK: cleanup complete"
