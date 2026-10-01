#!/usr/bin/env bash
# ALWAYS ON - check-network-isolation.sh: all domain networks must exist and be internal-only.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_require_cmds podman
registry="$AO_ROOT/config/platform/network-cidrs.yaml"
# Workload networks that MUST be Internal=true. Every one of these is an
# isolation domain, so a non-internal network here is a failure.
# ao-sales is NOT in this list: it is deliberately non-internal so Sidekiq can
# deliver ActivityPub, and is asserted as Internal=false in the egress list.
expected=(ao-payment ao-field ao-mapping ao-sim-vehicle ao-sim-fabrication ao-ledger-ingest ao-ledger-core ao-data ao-admin ao-fabrication)
# Egress networks are deliberately NOT internal: they exist to reach a provider
# or the public internet, which is the whole point of a separate egress network.
# They are still registered here so the registry is the single authority for
# every workload CIDR (README §5.1), but they are recorded and checked against
# Internal=false rather than being reported as a violation.
#   ao-reporting-egress  10.89.10.0/24  ao-grafana, ao-metabase
#
# ao-egress-community is RETIRED and removed from this host. It is no longer
# listed here or in the registry, because the live podman network is gone.
# ao-sales is now Internal=false and carries ActivityPub delivery itself.
# See README 15.4 / 18.5 / 18.6.
egress=(ao-reporting-egress ao-sales)
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
for net in "${egress[@]}"; do
  info="$(podman network inspect "$net" --format '{{.Name}} internal={{.Internal}} subnets={{range .Subnets}}{{.Subnet}} {{end}}' 2>/dev/null)" \
    || { echo "ERROR: missing network: $net" >&2; fails=$((fails+1)); continue; }
  echo "$info" | tee -a "$registry.tmp"
  grep -q 'internal=false' <<<"$info" || { echo "ERROR: $net egress network is internal=$info (expected false)" >&2; fails=$((fails+1)); }
done
mv "$registry.tmp" "$registry"
ao_audit "refreshed network CIDR registry"
(( fails == 0 )) && echo "OK: all domain networks present; isolation domains internal-only; ao-sales + ao-reporting-egress non-internal by decision" || exit 42
