# ALWAYS ON - pcloud-transfer.sh: encrypt and upload content to pCloud.
# Usage: pcloud-transfer.sh <transfer-record.json> [--dry-run]
# Per Section 11.6: Encrypt before pCloud archival replication unless an
# explicitly approved equivalent encryption control applies. pCloud is a
# transfer copy — NOT a backup.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh

record_path="${1:-}"
[[ -n "$record_path" && -f "$record_path" ]] || { echo "Usage: ${0##*/} <transfer-record.json> [--dry-run]" >&2; exit 2; }

# Detect --dry-run in any argument position
AO_DRY_RUN=0
for arg in "$@"; do
  if [[ "$arg" == "--dry-run" ]]; then AO_DRY_RUN=1; break; fi
done
export AO_DRY_RUN

ao_require_cmds jq openssl sha256sum rclone

# Read transfer record
cid="$(jq -r '.ipfs_cid // empty' "$record_path")"
hash="$(jq -r '.content_hash_sha256 // empty' "$record_path")"
content_path="$(jq -r '.content_path // empty' "$record_path")"
[[ -n "$cid" && -n "$hash" && -n "$content_path" ]] || { echo "ERROR: transfer record missing required fields" >&2; exit 3; }
[[ -f "$content_path" ]] || { echo "ERROR: content file missing: $content_path" >&2; exit 4; }

# Read pCloud remote name from KDE Wallet
wallet_entry="$(python3 /ALWAYSON/scripts/ops/wallet-read-secret.py kdewallet ao-archive pcloud-remote-name 2>/dev/null || echo "")"
rclone_remote="${wallet_entry:-pcloud:}"

# Encrypt content before upload (Section 11.6)
enc_file="${content_path}.enc.$(date -u +%Y%m%dT%H%M%SZ)"
encryption_passphrase="$(python3 /ALWAYSON/scripts/ops/wallet-read-secret.py kdewallet ao-archive pcloud-encryption-passphrase 2>/dev/null || echo "")"
if [[ -z "$encryption_passphrase" ]]; then
  echo "ERROR: pcloud-encryption-passphrase not in KDE Wallet (ao-archive)" >&2
  exit 5
fi

if (( AO_DRY_RUN )); then
  ao_log INFO "DRY-RUN: encrypt $content_path -> $enc_file"
  ao_log INFO "DRY-RUN: rclone copy $enc_file $rclone_remote/ALWAYSON-TRANSFER/"
  pcloud_ref="pcloud:DRYRUN-$(date -u +%Y%m%dT%H%M%SZ)"
else
  openssl enc -aes-256-cbc -salt -pbkdf2 -in "$content_path" -out "$enc_file" -pass "pass:$encryption_passphrase"
  ao_log INFO "pcloud-transfer: encrypted $content_path -> $enc_file"

  rclone copy "$enc_file" "${rclone_remote}/ALWAYSON-TRANSFER/" 2>&1 | tail -3
  remote_path="${rclone_remote}/ALWAYSON-TRANSFER/$(basename "$enc_file")"
  pcloud_ref="$remote_path"
  ao_log INFO "pcloud-transfer: uploaded to $remote_path"

  # Clean up local encrypted file (transfer copy only — retention is restic)
  shred -u "$enc_file" 2>/dev/null || rm -f "$enc_file"
fi

# Update transfer record with pCloud reference
tmp_file="${record_path}.tmp"
jq --arg ref "$pcloud_ref" \
   --arg uploaded "$(date -u +%Y%m%dT%H%M%SZ)" \
   '.pcloud_archive_reference = $ref | .pcloud_uploaded_at_utc = $uploaded' \
   "$record_path" > "$tmp_file" && mv "$tmp_file" "$record_file"

ao_log INFO "pcloud-transfer: ref=$pcloud_ref record=$record_file"
echo "$record_file"
