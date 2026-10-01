# ALWAYS ON - rollback-domain.sh: stop/disable and remove a domain's units.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_dry_run_init "${2:-}"
domain="${1:-}"
[[ -n "$domain" ]] || { echo "Usage: ${0##*/} <domain> [--dry-run]" >&2; exit 2; }
SRC="$AO_ROOT/quadlet/$domain"
# Units live FLAT in the systemd user dir (see deploy-quadlet-domain.sh). Roll
# back must therefore remove ONLY this domain's unit files, named from the
# repo source of truth - never `rm -r` the directory, which holds every other
# domain plus the networks and volumes they share.
DEST="$HOME/.config/containers/systemd"
[[ -d "$SRC" ]] || { echo "ERROR: domain not deployed: $domain" >&2; exit 10; }
removed=0
for f in "$SRC"/*; do
  [[ -e "$f" ]] || continue
  base="${f##*/}"
  ao_run systemctl --user disable --now "$base" || true
  if [[ -e "$DEST/$base" ]]; then
    ao_run rm -f "$DEST/$base"
    removed=$((removed + 1))
  fi
done
ao_run systemctl --user daemon-reload
(( AO_DRY_RUN )) || ao_audit "rolled back domain $domain"
echo "OK: domain '$domain' rolled back ($removed unit file(s) removed)"
