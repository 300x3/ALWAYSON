# ALWAYS ON - verify photogrammetry mount (wrapper; logic in validation script)
set -Eeuo pipefail
IFS=$'\n\t'
exec /ALWAYSON/scripts/validation/check-photogrammetry-mount.sh
