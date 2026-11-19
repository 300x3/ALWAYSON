# ALWAYS ON - ipfs-transfer.sh: add file to IPFS, record CID and hash.
# Usage: ipfs-transfer.sh <content_path> [--dry-run]
# Per Section 11.6: IPFS is for file-transfer verification and blockchain
# listing only — NOT a backup. Encrypt before any public IPFS distribution
# for sensitive artifacts.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh

content_path="${1:-}"
[[ -n "$content_path" && -f "$content_path" ]] || { echo "Usage: ${0##*/} <content_path> [--dry-run]" >&2; exit 2; }

# Detect --dry-run in any argument position
AO_DRY_RUN=0
for arg in "$@"; do
  if [[ "$arg" == "--dry-run" ]]; then AO_DRY_RUN=1; break; fi
done
export AO_DRY_RUN

ao_require_cmds ipfs jq sha256sum

hash="$(sha256sum "$content_path" | awk '{print $1}')"
size="$(stat -c %s "$content_path")"

ao_log INFO "ipfs-transfer: content=$content_path hash=$hash size=$size"

cid=""
if (( AO_DRY_RUN )); then
  ao_log INFO "DRY-RUN: ipfs add $content_path"
  cid="QmDRYRUNPLACEHOLDER"
else
  result="$(ipfs add --quiet "$content_path")"
  cid="$(echo "$result" | tail -1 | awk '{print $1}')"
  [[ -n "$cid" ]] || { echo "ERROR: ipfs add returned no CID" >&2; exit 30; }
fi

# Record CID and hash to staging for downstream pCloud/ledger steps
staging="${AO_EGRESS_STAGING:-/ALWAYSON/data/ao-egress-archive}"
mkdir -p "$staging"
record_file="$staging/transfer-$(date -u +%Y%m%dT%H%M%SZ).json"
jq -n \
  --arg path "$content_path" \
  --arg hash "$hash" \
  --arg size "$size" \
  --arg cid "$cid" \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{
    content_path: $path,
    content_hash_sha256: $hash,
    content_size_bytes: ($size|tonumber),
    ipfs_cid: $cid,
    ipfs_added_at_utc: $ts
  }' > "$record_file"

ao_log INFO "ipfs-transfer: cid=$cid record=$record_file"
echo "$record_file"
