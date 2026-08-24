# ALWAYS ON - mapping/validate-imagery.sh
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
echo "PENDING: validate-imagery.sh requires its domain deployment first (Section 2.8 safe sequence)"
exit 3
