# ALWAYS ON - check-network-isolation.sh: all domain networks must exist and be internal-only.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_require_cmds podman
registry="$AO_ROOT/config/platform/network-cidrs.yaml"
expected=(ao-sales ao-payment ao-field ao-mapping ao-sim-vehicle ao-sim-fabrication ao-ledger-ingest ao-ledger-core ao-data ao-admin)
fails=0
{
  echo "# Podman network CIDR registry - maintained by check-network-isolation.sh"
  echo "# Internal=true is mandatory per Section 1.3 isolation domains."
} > "$registry.tmp"
for net in "${expected[@]}"; do
  info="$(podman network inspect "$net" --format '{{.Name}} internal={{.Internal}} subnets={{range .Subnets}}{{.Subnet}} {{end}}' 2>/dev/null)" \
    || { echo "ERROR: missing network: $net" >&2; fails=$((fails+1)); continue; }
  echo "$info" | tee -a "$registry.tmp"
  grep -q 'internal=true' <<<"$info" || { echo "ERROR: $net is NOT internal" >&2; fails=$((fails+1)); }
done
mv "$registry.tmp" "$registry"
ao_audit "refreshed network CIDR registry"
(( fails == 0 )) && echo "OK: all domain networks present and internal-only" || exit 42
