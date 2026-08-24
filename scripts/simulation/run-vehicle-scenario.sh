# ALWAYS ON - simulation/run-vehicle-scenario.sh
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
echo "PENDING: run-vehicle-scenario.sh requires its domain deployment first (Section 2.8 safe sequence)"
exit 3
