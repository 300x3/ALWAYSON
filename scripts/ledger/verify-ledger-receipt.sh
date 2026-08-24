# ALWAYS ON - verify-ledger-receipt.sh: verify receipt ID against local manifest record.
set -Eeuo pipefail
IFS=$'\n\t'
receipt="${1:-}"; manifest="${2:-}"
[[ -n "$receipt" && -f "${manifest:-}" ]] || { echo "Usage: ${0##*/} <receipt_id> <manifest.json>" >&2; exit 2; }
jq -e --arg r "$receipt" '.ledger_receipt_id == $r' "$manifest" >/dev/null \
  && echo "OK: receipt matches manifest record" || { echo "FAIL: receipt mismatch" >&2; exit 50; }
