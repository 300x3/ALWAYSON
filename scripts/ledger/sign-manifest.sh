# ALWAYS ON - sign-manifest.sh: detached Ed25519 signature over the manifest digest.
# Usage: sign-manifest.sh <manifest.json> <producer_private_key.pem>
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_require_cmds openssl jq sha256sum
[[ $# -eq 2 ]] || { echo "Usage: ${0##*/} <manifest.json> <key.pem>" >&2; exit 2; }
m="$1"; k="$2"
[[ -f "$m" && -f "$k" ]] || { echo "ERROR: manifest or key missing (keys live ONLY in $AO_ROOT/secrets/<domain>/)" >&2; exit 10; }
digest="$(sha256sum "$m" | awk '{print $1}')"
sigfile="${m%.json}.sig"
printf '%s' "$digest" > /tmp/.ao-digest-$$
openssl pkeyutl -sign -inkey "$k" -rawin -in /tmp/.ao-digest-$$ -out "$sigfile"
shred -u /tmp/.ao-digest-$$
sig_b64="$(base64 -w0 "$sigfile")"
jq --arg kid "$(basename "$k" .pem)" --arg sig "ed25519:$sig_b64" \
   '.producer_key_id=$kid | .signature=$sig' "$m" > "$m.tmp" && mv "$m.tmp" "$m"
echo "OK: detached signature at $sigfile and embedded in manifest (digest $digest)"
