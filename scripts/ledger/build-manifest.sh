# ALWAYS ON - build-manifest.sh: build a signed-ready manifest per Section 1.9 format.
# Usage: build-manifest.sh <object_type> <origin_domain> <content_path> <local_storage_reference> [transaction_id] [correlation_id] [serial_number] [receipt_number] [event_timestamp_utc] [event_type]
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_require_cmds sha256sum jq uuidgen
[[ $# -ge 4 && $# -le 10 ]] || { echo "Usage: ${0##*/} <object_type> <origin_domain> <content_path> <local_ref> [transaction_id] [correlation_id] [serial_number] [receipt_number] [event_timestamp_utc] [event_type]" >&2; exit 2; }
otype="$1"; odomain="$2"; cpath="$3"; ref="$4"
transaction_id="${5:-}"; correlation_id="${6:-}"; serial_number="${7:-}"
receipt_number="${8:-}"; event_timestamp_utc="${9:-}"; event_type="${10:-}"
if [[ "$otype" == sales_receipt && ! "$transaction_id" =~ ^TXN-[0-9]{8}T[0-9]{6}Z-[A-F0-9]{12}$ ]]; then
  echo "ERROR: sales_receipt requires issued transaction_id" >&2; exit 12
fi
[[ -f "$cpath" ]] || { echo "ERROR: content not found: $cpath" >&2; exit 10; }
case "$otype" in sales_receipt|telemetry_batch|map_product|vehicle_simulation|fabrication_simulation|ledger_posting) ;; *) echo "ERROR: bad object_type" >&2; exit 11;; esac
case "$odomain" in sales|payment|field|mapping|sim_vehicle|sim_fabrication|archive|ledger) ;; *) echo "ERROR: origin_domain not in closed §11.1 set: $odomain" >&2; exit 13;; esac
hash="$(sha256sum "$cpath" | awk '{print $1}')"
size="$(stat -c %s "$cpath")"
idempotency_key="$(uuidgen)"
jq -n \
  --arg id "$(uuidgen)" --arg t "$otype" --arg d "$odomain" \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg h "$hash" --arg s "$size" --arg r "$ref" --arg tx "$transaction_id" \
  --arg cid "$correlation_id" --arg sn "$serial_number" --arg rn "$receipt_number" \
  --arg ets "$event_timestamp_utc" --arg et "$event_type" --arg ik "$idempotency_key" \
  '{object_id:$id, object_type:$t, origin_domain:$d, created_at_utc:$ts,
    schema_version:"1.0", content_hash_sha256:$h, content_size_bytes:($s|tonumber),
    local_storage_reference:$r, ipfs_cid:"", pcloud_archive_reference:"",
    transaction_id:(if $tx=="" then null else $tx end),
    correlation_id:(if $cid=="" then null else $cid end),
    serial_number:(if $sn=="" then null else $sn end),
    receipt_number:(if $rn=="" then null else $rn end),
    event_timestamp_utc:(if $ets=="" then null else $ets end),
    event_type:(if $et=="" then null else $et end),
    idempotency_key:$ik,
    authorization_policy_id:"", producer_key_id:"", signature:"", signed_payload_sha256:""}'
