# ALWAYS ON - mapping/intake-imagery.sh
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
echo "PENDING: intake-imagery.sh requires its domain deployment first (Section 2.8 safe sequence)"
exit 3
