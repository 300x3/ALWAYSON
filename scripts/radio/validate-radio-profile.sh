# ALWAYS ON - radio/validate-radio-profile.sh
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
echo "PENDING: validate-radio-profile.sh requires its domain deployment first (Section 2.8 safe sequence)"
exit 3
