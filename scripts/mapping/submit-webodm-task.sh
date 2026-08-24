# ALWAYS ON - mapping/submit-webodm-task.sh
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
echo "PENDING: submit-webodm-task.sh requires its domain deployment first (Section 2.8 safe sequence)"
exit 3
