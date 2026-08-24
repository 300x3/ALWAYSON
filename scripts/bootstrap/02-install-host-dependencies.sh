# ALWAYS ON - idempotent host dependency install (Section 2.4)
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_dry_run_init "${1:-}"
pkgs=(podman uidmap slirp4netns fuse-overlayfs containernetworking-plugins nftables ufw git curl jq ca-certificates gnupg openssl restic smartmontools lm-sensors acl python3 python3-venv python3-pip)
missing=()
for p in "${pkgs[@]}"; do dpkg -s "$p" >/dev/null 2>&1 || missing+=("$p"); done
if (( ${#missing[@]} == 0 )); then echo "OK: all host dependencies present"; exit 0; fi
echo "Missing: ${missing[*]} - installing requires elevated privileges:"
printf 'sudo apt install -y %s\n' "${missing[*]}"
exit 5
