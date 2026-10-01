# ALWAYS ON - enable-domain-services.sh
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_dry_run_init "${2:-}"
domain="${1:-}"
[[ -n "$domain" ]] || { echo "Usage: ${0##*/} <domain> [--dry-run]" >&2; exit 2; }
SRC="$AO_ROOT/quadlet/$domain"
# Units are deployed FLAT into the systemd user dir (see
# deploy-quadlet-domain.sh); globbing a "<domain>" subdirectory enabled nothing.
DEST="$HOME/.config/containers/systemd"
[[ -d "$SRC" ]] || { echo "ERROR: domain not deployed: $domain" >&2; exit 10; }
enabled=0
for f in "$SRC"/*.container; do
  [[ -e "$f" ]] || continue
  base="${f##*/}"
  [[ -e "$DEST/$base" ]] || continue
  ao_run systemctl --user enable --now "$base"
  enabled=$((enabled + 1))
done
(( AO_DRY_RUN )) || ao_audit "enabled services for domain $domain"
echo "OK: domain '$domain' enabled ($enabled unit(s))"
