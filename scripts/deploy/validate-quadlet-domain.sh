# ALWAYS ON - validate-quadlet-domain.sh: confirm systemd can load deployed units.
set -Eeuo pipefail
IFS=$'\n\t'
domain="${1:-}"
[[ -n "$domain" ]] || { echo "Usage: ${0##*/} <domain>" >&2; exit 2; }
DEST="$HOME/.config/containers/systemd/$domain"
[[ -d "$DEST" ]] || { echo "ERROR: $DEST not deployed" >&2; exit 10; }
fails=0; found=0
for f in "$DEST"/*.container "$DEST"/*.network "$DEST"/*.volume; do
  [[ -e "$f" ]] || continue
  found=$((found+1))
  systemctl --user cat "${f##*/}" >/dev/null 2>&1 || { echo "ERROR: cannot load $f" >&2; fails=$((fails+1)); }
done
(( found > 0 )) || { echo "ERROR: no units found in $DEST" >&2; exit 11; }
(( fails == 0 )) && echo "OK: $domain units loadable by systemd" || exit 41
