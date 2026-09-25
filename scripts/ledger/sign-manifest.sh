#!/usr/bin/env bash
# ALWAYS ON - sign-manifest.sh: detached Ed25519 signature over the manifest digest.
# Usage:
#   sign-manifest.sh <manifest.json> <producer_private_key.pem>
#   sign-manifest.sh <manifest.json> wallet:ao-sim-vehicle
#   sign-manifest.sh <manifest.json> wallet:ao-sim-fabrication
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_require_cmds openssl jq sha256sum
[[ $# -eq 2 ]] || { echo "Usage: ${0##*/} <manifest.json> <key.pem|wallet:ao-sim-vehicle|wallet:ao-sim-fabrication>" >&2; exit 2; }
m="$1"; k="$2"
wallet_key=""
case "$k" in
  wallet:ao-sim-vehicle) wallet_key=ao-sim-vehicle ;;
  wallet:ao-sim-fabrication) wallet_key=ao-sim-fabrication ;;
esac
key_tmp=""
cleanup() {
  if [[ -n "$key_tmp" ]]; then
    shred -u "$key_tmp" 2>/dev/null || rm -f "$key_tmp"
  fi
}
trap cleanup EXIT
if [[ -n "$wallet_key" ]]; then
  key_tmp="$(mktemp)"
  chmod 0600 "$key_tmp"
  /ALWAYSON/scripts/ops/wallet-read-secret.py kdewallet "$wallet_key" producer-private-key >"$key_tmp"
  [[ -s "$key_tmp" ]] || { echo "ERROR: KDE Wallet entry unavailable: $wallet_key/producer-private-key" >&2; exit 3; }
  k="$key_tmp"
fi
[[ -f "$m" && -f "$k" ]] || { echo "ERROR: manifest or key missing (keys live in KDE Wallet ao-sim-*; file path accepted for migration/testing)" >&2; exit 10; }
digest="$(sha256sum "$m" | awk '{print $1}')"
sigfile="${m%.json}.sig"
printf '%s' "$digest" > /tmp/.ao-digest-$$
openssl pkeyutl -sign -inkey "$k" -rawin -in /tmp/.ao-digest-$$ -out "$sigfile"
shred -u /tmp/.ao-digest-$$
sig_b64="$(base64 -w0 "$sigfile")"
key_id="$k"
if [[ -n "$wallet_key" ]]; then key_id="$wallet_key"; else key_id="$(basename "$k" .pem)"; fi
jq --arg kid "$key_id" --arg sig "ed25519:$sig_b64" \
   '.producer_key_id=$kid | .signature=$sig' "$m" > "$m.tmp" && mv "$m.tmp" "$m"
echo "OK: detached signature at $sigfile and embedded in manifest (digest $digest)"
