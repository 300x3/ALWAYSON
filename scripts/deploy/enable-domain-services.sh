# ALWAYS ON - enable-domain-services.sh
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_dry_run_init "${2:-}"
domain="${1:-}"
[[ -n "$domain" ]] || { echo "Usage: ${0##*/} <domain> [--dry-run]" >&2; exit 2; }
DEST="$HOME/.config/containers/systemd/$domain"
[[ -d "$DEST" ]] || { echo "ERROR: domain not deployed: $domain" >&2; exit 10; }
for f in "$DEST"/*.container; do
  [[ -e "$f" ]] || continue
  ao_run systemctl --user enable --now "${f##*/}"
done
(( AO_DRY_RUN )) || ao_audit "enabled services for domain $domain"
echo "OK: domain '$domain' enabled"
