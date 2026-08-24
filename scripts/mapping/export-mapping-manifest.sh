# ALWAYS ON - mapping/export-mapping-manifest.sh
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
echo "PENDING: export-mapping-manifest.sh requires its domain deployment first (Section 2.8 safe sequence)"
exit 3
