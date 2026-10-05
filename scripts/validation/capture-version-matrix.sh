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

tmp="$(mktemp)"
sed \
  -e "s|^  systemd: .*|  systemd: \"${systemd_version}\"|" \
  -e "s|^  podman: .*|  podman: \"$(podman --version | awk '{print $3}')\"|" \
  -e "s|^  quadlet_capability: .*|  quadlet_capability: \"Quadlet systemd generator functional in podman ${podman_host_version} (user scope)\"|" \
  -e "s|^  netplan: .*|  netplan: \"$(netplan --version 2>/dev/null || echo 'not present')\"|" \
  -e "s|^  nvidia_driver: .*|  nvidia_driver: \"$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null || echo unknown)\"|" \
  "$MATRIX" > "$tmp"

mv "$tmp" "$MATRIX"
ao_audit "captured host facts into version-matrix.yaml"
echo "OK: version matrix updated:"
grep -E 'systemd|podman|nvidia_driver' "$MATRIX"