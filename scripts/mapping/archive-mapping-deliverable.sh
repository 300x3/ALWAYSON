# ALWAYS ON - mapping/archive-mapping-deliverable.sh
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
echo "PENDING: archive-mapping-deliverable.sh requires its domain deployment first (Section 2.8 safe sequence)"
exit 3
