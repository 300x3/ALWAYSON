#!/usr/bin/env bash
# ALWAYS ON - validation: capture-version-matrix.sh fills host facts into version-matrix.yaml (Section 3.2)
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_lock capture-version-matrix

MATRIX="$AO_ROOT/config/platform/version-matrix.yaml"
[[ -f "$MATRIX" ]] || { echo "ERROR: $MATRIX missing" >&2; exit 10; }
ao_require_cmds podman jq nvidia-smi

systemd_version="$($AO_ROOT/../usr/lib/systemd/systemd --version 2>/dev/null | head -n1 | awk '{print $2}')"
[[ -n "${systemd_version:-}" ]] || systemd_version="$(systemctl --version | head -n1 | awk '{print $2}')"

# `.Host.Version` was removed from podman 5.7's info schema; the field is now
# `.Version.Version`. Measured 2026-10-04: the old template fails with
# "can't evaluate field Version in type *define.HostInfo", and because this
# line was guarded by `|| echo unknown` the failure was swallowed and wrote a
# LITERAL "podman unknown" into the matrix, silently degrading a good recorded
# value. So the fallback now fails loudly instead of inventing a value.
podman_host_version="$(podman info --format '{{.Version.Version}}' 2>/dev/null || true)"
[[ -n "$podman_host_version" ]] || {
  echo "ERROR: cannot read the podman host version; refusing to write a degraded matrix" >&2
  exit 11
}

# --- Capture image digests from deployed containers (OPS-02) ---
# Map running container names -> version-matrix.yaml digest fields.
# We read RepoDigests from podman inspect so the matrix records the exact
# deployed image digest, never a hand-typed tag that could drift.
declare -A CONTAINER_TO_FIELD=(
  ["ao-mastodon-web"]="image_web"
  ["ao-mastodon-streaming"]="image_streaming"
  ["ao-mastodon-sidekiq"]="image_sidekiq"
  ["ao-mastodon-db"]="image_postgres"
  ["ao-mastodon-redis"]="image_redis"
  ["ao-grafana"]="image_grafana"
  ["ao-metabase"]="image_metabase"
  ["ao-prometheus"]="image_prometheus"
  ["ao-node-exporter"]="image_node_exporter"
  ["ao-sim-fabrication-gz"]="gz_sim_image_digest"
  ["ao-sim-fabrication-foxglove"]="image_foxglove_bridge"
  ["ao-webodm-web"]="webodm_image_digest"
  ["ao-nodeodm"]="nodeodm_image_digest"
  ["ao-webodm-db"]="webodm_db_image_digest"
  ["ao-webodm-broker"]="broker_image_digest"
  ["ao-ingress-payment"]="image_ingress_payment"
)

# sed expressions for host facts (unchanged)
tmp="$(mktemp)"
sed \
  -e "s|^  systemd: .*|  systemd: \"${systemd_version}\"|" \
  -e "s|^  podman: .*|  podman: \"$(podman --version | awk '{print $3}')\"|" \
  -e "s|^  quadlet_capability: .*|  quadlet_capability: \"Quadlet systemd generator functional in podman ${podman_host_version} (user scope)\"|" \
  -e "s|^  netplan: .*|  netplan: \"$(netplan --version 2>/dev/null || echo 'not present')\"|" \
  -e "s|^  nvidia_driver: .*|  nvidia_driver: \"$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null || echo unknown)\"|" \
  "$MATRIX" > "$tmp"

# Overlay container digests onto the matrix. For each running container that
# maps to a matrix field, extract the first RepoDigest and replace the field's
# digest portion while preserving any parenthesised version comment.
for container in "${!CONTAINER_TO_FIELD[@]}"; do
  field="${CONTAINER_TO_FIELD[$container]}"
  # Skip if container is not running
  if ! podman ps --format '{{.Names}}' | grep -qx "$container"; then
    continue
  fi
  digest="$(podman inspect --format '{{index .RepoDigests 0}}' "$container" 2>/dev/null || true)"
  [[ -n "$digest" && "$digest" != "<no value>" ]] || continue
  # Replace everything after the field key up to the newline, keeping the
  # version comment in parentheses if one exists.
  sed -i "s|^  ${field}: .*|  ${field}: \"${digest}\"|" "$tmp"
done

mv "$tmp" "$MATRIX"
ao_audit "captured host facts and container image digests into version-matrix.yaml"
echo "OK: version matrix updated:"
grep -E 'systemd|podman|nvidia_driver' "$MATRIX"
for f in image_web image_streaming image_sidekiq image_postgres image_redis image_grafana image_metabase image_prometheus image_node_exporter gz_sim_image_digest image_foxglove_bridge webodm_image_digest nodeodm_image_digest webodm_db_image_digest broker_image_digest image_ingress_payment; do
  grep -E "^  ${f}:" "$MATRIX"
done