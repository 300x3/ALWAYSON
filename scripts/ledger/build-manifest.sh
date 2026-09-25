# ALWAYS ON - build-manifest.sh: build a signed-ready manifest per Section 1.9 format.
# Usage: build-manifest.sh <object_type> <origin_domain> <content_path> <local_storage_reference> [transaction_id]
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_require_cmds sha256sum jq uuidgen
[[ $# -eq 4 || $# -eq 5 ]] || { echo "Usage: ${0##*/} <object_type> <origin_domain> <content_path> <local_ref> [transaction_id]" >&2; exit 2; }
otype="$1"; odomain="$2"; cpath="$3"; ref="$4"; transaction_id="${5:-}"
if [[ "$otype" == sales_receipt && ! "$transaction_id" =~ ^TXN-[0-9]{8}T[0-9]{6}Z-[A-F0-9]{12}$ ]]; then
  echo "ERROR: sales_receipt requires issued transaction_id" >&2; exit 12
fi
[[ -f "$cpath" ]] || { echo "ERROR: content not found: $cpath" >&2; exit 10; }
case "$otype" in sales_receipt|telemetry_batch|map_product|vehicle_simulation|fabrication_simulation) ;; *) echo "ERROR: bad object_type" >&2; exit 11;; esac
hash="$(sha256sum "$cpath" | awk '{print $1}')"
size="$(stat -c %s "$cpath")"
jq -n \
  --arg id "$(uuidgen)" --arg t "$otype" --arg d "$odomain" \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg h "$hash" --arg s "$size" --arg r "$ref" --arg tx "$transaction_id" \
  '{object_id:$id, object_type:$t, origin_domain:$d, created_at_utc:$ts,
    schema_version:"1.0", content_hash_sha256:$h, content_size_bytes:($s|tonumber),
    local_storage_reference:$r, ipfs_cid:"", pcloud_archive_reference:"",
    transaction_id:(if $tx=="" then null else $tx end),
    authorization_policy_id:"", producer_key_id:"", signature:""}'
