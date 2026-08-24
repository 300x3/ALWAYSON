# ALWAYS ON - simulation/export-fabrication-manifest.sh
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
echo "PENDING: export-fabrication-manifest.sh requires its domain deployment first (Section 2.8 safe sequence)"
exit 3
