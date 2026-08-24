# ALWAYS ON - restore-simulation-artifact-test.sh: isolated restore test (Section 4.4 requirements 1-7).
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
echo "PENDING: $0 requires completed backups plus isolated test-path approval"
exit 3
