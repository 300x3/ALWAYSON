# ALWAYS ON - idempotent Podman network creation (Section 2.7)
set -Eeuo pipefail
IFS=$'\n\t'
command -v podman >/dev/null || { echo "ERROR: podman missing" >&2; exit 10; }
for net in ao-sales ao-payment ao-field ao-mapping ao-sim-vehicle ao-sim-fabrication ao-ledger-ingest ao-ledger-core ao-data ao-admin; do
  podman network exists "$net" || podman network create "$net"
done
podman network ls
