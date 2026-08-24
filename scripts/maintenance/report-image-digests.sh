# ALWAYS ON - report-image-digests.sh: record pinned digests for operational images.
set -Eeuo pipefail
IFS=$'\n\t'
podman images --digests --format 'table {{.Repository}}\t{{.Digest}}\t{{.Tag}}' 2>/dev/null || true
