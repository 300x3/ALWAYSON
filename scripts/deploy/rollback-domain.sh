# ALWAYS ON - rollback-domain.sh: stop/disable and remove a domain's units.
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
  ao_run systemctl --user disable --now "${f##*/}" || true
done
ao_run rm -r --interactive=never "$DEST"
ao_run systemctl --user daemon-reload
(( AO_DRY_RUN )) || ao_audit "rolled back domain $domain"
echo "OK: domain '$domain' rolled back"
