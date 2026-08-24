# ALWAYS ON - report-container-status.sh
set -Eeuo pipefail
IFS=$'\n\t'
podman ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}' 2>/dev/null || echo "no containers yet"
systemctl --user --failed --no-legend 2>/dev/null || true
