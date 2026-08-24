# ALWAYS ON - create/verify operational layout (Sections 2.6, 3.1)
set -Eeuo pipefail
IFS=$'\n\t'
required_dirs=(
  /ALWAYSON/docs/adr /ALWAYSON/docs/architecture /ALWAYSON/docs/runbooks /ALWAYSON/docs/compliance
  /ALWAYSON/storefront/source /ALWAYSON/storefront/build /ALWAYSON/storefront/releases /ALWAYSON/storefront/manifests /ALWAYSON/storefront/pcloud-public-folder
  /ALWAYSON/quadlet/networks /ALWAYSON/config/platform /ALWAYSON/secrets /ALWAYSON/data/sales /ALWAYSON/artifacts
)
fails=0
for d in "${required_dirs[@]}"; do
  [[ -d "$d" ]] || { echo "MISSING: $d"; fails=$((fails+1)); }
done
(( fails == 0 )) && echo "OK: operational layout complete" || exit 12
