# ALWAYS ON - validate-quadlet-domain.sh: confirm systemd can load deployed units.
set -Eeuo pipefail
IFS=$'\n\t'
# AO_ROOT is provided by common.sh. Without this the script aborted on an
# unbound variable before validating anything.
. /ALWAYSON/scripts/lib/common.sh
domain="${1:-}"
[[ -n "$domain" ]] || { echo "Usage: ${0##*/} <domain>" >&2; exit 2; }
DEST="$HOME/.config/containers/systemd"
SRC="$AO_ROOT/quadlet/$domain"
[[ -d "$SRC" ]] || { echo "ERROR: $SRC not found" >&2; exit 10; }
fails=0; found=0
# Units are deployed FLAT (see deploy-quadlet-domain.sh), so validate the files
# this domain owns by name from the repo, not by globbing a subdirectory.
#
# Two checks, because `systemctl --user cat` is not a valid test for every
# file type: a .network or .volume is only instantiated once something uses it,
# so `cat` fails on a perfectly good deployed file. What actually matters is
# (a) the unit is deployed and (b) it has not drifted from the repo source.
for f in "$SRC"/*.container "$SRC"/*.network "$SRC"/*.volume; do
  [[ -e "$f" ]] || continue
  found=$((found+1))
  base="${f##*/}"
  if [[ ! -e "$DEST/$base" ]]; then
    echo "ERROR: not deployed: $base" >&2; fails=$((fails+1)); continue
  fi
  if ! cmp -s "$f" "$DEST/$base"; then
    echo "ERROR: DRIFT: $base differs from $f" >&2; fails=$((fails+1)); continue
  fi
  if [[ "$base" == *.container ]]; then
    unit="${base%.container}.service"
    systemctl --user show "$unit" -p SourcePath --value >/dev/null 2>&1 \
      || { echo "ERROR: systemd cannot resolve $unit" >&2; fails=$((fails+1)); }
  fi
done
(( found > 0 )) || { echo "ERROR: no units found in $SRC" >&2; exit 11; }
(( fails == 0 )) && echo "OK: $domain - $found unit(s) deployed, no drift" || exit 41
