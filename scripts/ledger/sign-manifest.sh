#!/usr/bin/env bash
# ALWAYS ON - sign-manifest.sh: Ed25519 signature over canonical manifest payload.
# Usage:
#   sign-manifest.sh <manifest.json> <producer_private_key.pem>
#   sign-manifest.sh <manifest.json> wallet:ao-sim-vehicle
#   sign-manifest.sh <manifest.json> wallet:ao-sim-fabrication
#   sign-manifest.sh <manifest.json> wallet:ao-sales
#   sign-manifest.sh <manifest.json> wallet:ao-payment
#   sign-manifest.sh <manifest.json> wallet:ao-field
#   sign-manifest.sh <manifest.json> wallet:ao-mapping
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_require_cmds openssl jq sha256sum
[[ $# -eq 2 ]] || { echo "Usage: ${0##*/} <manifest.json> <key.pem|wallet:ao-sim-vehicle|wallet:ao-sim-fabrication|wallet:ao-sales|wallet:ao-payment|wallet:ao-field|wallet:ao-mapping>" >&2; exit 2; }
m="$1"; k="$2"
wallet_key=""
case "$k" in
  wallet:ao-sim-vehicle) wallet_key=ao-sim-vehicle ;;
  wallet:ao-sim-fabrication) wallet_key=ao-sim-fabrication ;;
  wallet:ao-sales) wallet_key=ao-sales ;;
  wallet:ao-payment) wallet_key=ao-payment ;;
  wallet:ao-field) wallet_key=ao-field ;;
  wallet:ao-mapping) wallet_key=ao-mapping ;;
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
if [[ -n "$wallet_key" && ! -f "$k" ]]; then
  echo "ERROR: wallet key not implemented: $k (supported: wallet:ao-sim-vehicle, wallet:ao-sim-fabrication, wallet:ao-sales, wallet:ao-payment, wallet:ao-field, wallet:ao-mapping)" >&2; exit 10
fi
[[ -f "$m" && -f "$k" ]] || { echo "ERROR: manifest or key file missing" >&2; exit 10; }

# Canonicalise the signable payload: every field except producer_key_id and signature,
# with keys sorted and compact JSON. This is what gets signed — post-signature field
# edits change the canonical hash and invalidate the signature.
signable="$(jq -S 'del(.producer_key_id, .signature)' "$m")"
signed_payload_sha256="$(printf '%s' "$signable" | sha256sum | awk '{print $1}')"
printf '%s' "$signed_payload_sha256" > /tmp/.ao-digest-$$
openssl pkeyutl -sign -inkey "$k" -rawin -in /tmp/.ao-digest-$$ -out "${m%.json}.sig"
shred -u /tmp/.ao-digest-$$
sig_b64="$(base64 -w0 "${m%.json}.sig")"
key_id="$k"
if [[ -n "$wallet_key" ]]; then key_id="$wallet_key"; else key_id="$(basename "$k" .pem)"; fi
jq --arg kid "$key_id" --arg sig "ed25519:$sig_b64" --arg sp "$signed_payload_sha256" \
   '.producer_key_id=$kid | .signature=$sig | .signed_payload_sha256=$sp' "$m" > "$m.tmp" && mv "$m.tmp" "$m"
echo "OK: detached signature at ${m%.json}.sig and embedded in manifest (signed_payload_sha256 $signed_payload_sha256)"
