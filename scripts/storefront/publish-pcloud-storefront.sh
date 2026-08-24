# ALWAYS ON - storefront/publish-pcloud-storefront.sh
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
echo "PENDING: publish-pcloud-storefront.sh requires pCloud Public Folder credential provisioning (Section 3.4) - paused for operator approval"
exit 3
