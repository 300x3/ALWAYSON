# ALWAYS ON - storefront/rollback-storefront-release.sh
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
echo "PENDING: rollback-storefront-release.sh requires pCloud Public Folder credential provisioning (Section 3.4) - paused for operator approval"
exit 3
