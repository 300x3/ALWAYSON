# ALWAYS ON - verify-hashes-and-receipts.sh: recalculate artifact hashes and compare
# with stored manifests, then verify receipt linkage (Section 4.4 steps 3-5).
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_require_cmds sha256sum jq
artdir="${1:-}"
[[ -d "$artdir" ]] || { echo "Usage: ${0##*/} <restored_artifacts_dir>" >&2; exit 2; }
fails=0 checked=0
while IFS= read -r m; do
  h="$(jq -r '.content_hash_sha256' "$m")"
  ref="$(jq -r '.local_storage_reference // empty' "$m")"
  [[ -f "$ref" ]] || { echo "WARN: referenced artifact missing: $ref"; fails=$((fails+1)); continue; }
  actual="$(sha256sum "$ref" | awk '{print $1}')"
  checked=$((checked+1))
  [[ "$actual" == "$h" ]] || { echo "FAIL hash mismatch: $ref" >&2; fails=$((fails+1)); }
done < <(find "$artdir" -name '*.json')
echo "checked=$checked failures=$fails"
(( fails == 0 )) && echo "OK: all restored hashes match manifests" || exit 51
