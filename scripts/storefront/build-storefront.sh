# ALWAYS ON - build-storefront.sh: assemble static site from source into build/.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
src="$AO_ROOT/storefront/source"
build="$AO_ROOT/storefront/build"
[[ -d "$src" && -n "$(ls "$src" 2>/dev/null)" ]] || { echo "PENDING: no storefront source yet (Section 1.4 structure)" >&2; exit 3; }
rm -rf "$build"/* 2>/dev/null || true
cp -a "$src"/. "$build"/
# Safety: refuse to ship anything secret-shaped into the public tree.
if grep -rEin 'BEGIN [A-Z ]*PRIVATE KEY|api[_-]?key[[:space:]]*[:=]|oauth|connection string|10\.89\.' "$build" --include='*.html' --include='*.js' >/dev/null 2>&1; then
  echo "ERROR: forbidden content pattern found in build output - aborting (Section 1.4)" >&2
  exit 30
fi
ao_audit "storefront built"
echo "OK: built $build"
