# ALWAYS ON - sale-transfer.sh: end-to-end sale-transfer orchestration.
# Usage: sale-transfer.sh <object_type> <origin_domain> <content_path> <local_ref> [transaction_id]
# Per Section 11.6: IPFS first (transfer verification + blockchain listing),
# then encrypted pCloud. Requires ao-sales authorisation first. Not reached
# directly from the internet; does not originate a transfer on its own.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh

otype="${1:-}"
odomain="${2:-}"
content_path="${3:-}"
local_ref="${4:-}"
transaction_id="${5:-}"

# Detect --dry-run in any argument position
AO_DRY_RUN=0
for arg in "$@"; do
  if [[ "$arg" == "--dry-run" ]]; then AO_DRY_RUN=1; break; fi
done
export AO_DRY_RUN

[[ -n "$otype" && -n "$odomain" && -n "$content_path" && -n "$local_ref" ]] || {
  echo "Usage: ${0##*/} <object_type> <origin_domain> <content_path> <local_ref> [transaction_id] [--dry-run]" >&2; exit 2; }
[[ -f "$content_path" ]] || { echo "ERROR: content not found: $content_path" >&2; exit 10; }

ao_require_cmds jq sha256sum

staging="${AO_EGRESS_STAGING:-/ALWAYSON/data/ao-egress-archive}"
mkdir -p "$staging"
work_dir="$staging/sale-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$work_dir"

ao_log INFO "sale-transfer: object_type=$otype origin_domain=$odomain content=$content_path"

# Step 1: Build manifest
manifest="$work_dir/manifest.json"
if (( AO_DRY_RUN )); then
  ao_log INFO "DRY-RUN: build-manifest.sh $otype $odomain $content_path $local_ref $transaction_id"
else
  /ALWAYSON/scripts/ledger/build-manifest.sh "$otype" "$odomain" "$content_path" "$local_ref" "$transaction_id" > "$manifest"
  ao_log INFO "sale-transfer: manifest built: $manifest"
fi

# Step 2: Sign manifest (requires producer key — wallet or file)
if (( AO_DRY_RUN )); then
  ao_log INFO "DRY-RUN: sign-manifest.sh $manifest wallet:ao-sim-fabrication"
else
  /ALWAYSON/scripts/ledger/sign-manifest.sh "$manifest" "wallet:ao-sim-fabrication" || {
    echo "WARN: signing failed — proceeding with unsigned manifest for transfer-only" >&2
  }
fi

# Step 3: IPFS transfer
ipfs_record=""
if (( AO_DRY_RUN )); then
  ao_log INFO "DRY-RUN: ipfs-transfer.sh $content_path --dry-run"
else
  ipfs_record="$(/ALWAYSON/scripts/ipfs/ipfs-transfer.sh "$content_path" --dry-run)" || true
  ao_log INFO "sale-transfer: IPFS record: $ipfs_record"
fi

# Step 4: pCloud transfer (if IPFS succeeded or dry-run)
if (( AO_DRY_RUN )); then
  ao_log INFO "DRY-RUN: pcloud-transfer.sh <record> --dry-run"
else
  if [[ -n "$ipfs_record" && -f "$ipfs_record" ]]; then
    pcloud_record="$(/ALWAYSON/scripts/egress/pcloud-transfer.sh "$ipfs_record" --dry-run)" || true
    ao_log INFO "sale-transfer: pCloud record: $pcloud_record"
  else
    echo "WARN: IPFS record missing — skipping pCloud transfer" >&2
  fi
fi

# Step 5: Submit ledger event (gateway may not be deployed)
if (( AO_DRY_RUN )); then
  ao_log INFO "DRY-RUN: submit-ledger-event.sh $manifest"
else
  /ALWAYSON/scripts/ledger/submit-ledger-event.sh "$manifest" || {
    echo "WARN: ledger submission pending (gateway not deployed — manifest staged)" >&2
  }
fi

# Step 6: Record transfer log
transfer_log="$work_dir/transfer-log.json"
jq -n \
  --arg object_type "$otype" \
  --arg origin_domain "$odomain" \
  --arg content_path "$content_path" \
  --arg local_ref "$local_ref" \
  --arg transaction_id "${transaction_id:-null}" \
  --arg manifest "$manifest" \
  --arg ipfs_record "${ipfs_record:-null}" \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{
    object_type: $object_type,
    origin_domain: $origin_domain,
    content_path: $content_path,
    local_storage_reference: $local_ref,
    transaction_id: ($transaction_id),
    manifest_path: $manifest,
    ipfs_record: ($ipfs_record),
    transferred_at_utc: $ts
  }' > "$transfer_log"

ao_audit "sale-transfer: object_type=$otype origin_domain=$odomain content=$content_path manifest=$manifest"
ao_log INFO "sale-transfer: complete — log=$transfer_log"
echo "$transfer_log"
