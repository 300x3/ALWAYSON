#!/usr/bin/env bash
# ALWAYS ON - validate a three-form transaction bundle before Corda handoff.
set -Eeuo pipefail
IFS=$'\n\t'
dir="${1:?usage: validate-transaction-bundle.sh <bundle-dir>}"
[[ -d "$dir" ]] || { echo "ERROR: bundle directory missing: $dir" >&2; exit 2; }
status="$dir/BUNDLE-STATUS.txt"
[[ -f "$status" ]] || { echo 'ERROR: BUNDLE-STATUS.txt missing' >&2; exit 3; }
id="$(sed -n 's/^transaction_id=//p' "$status" | tail -1)"
[[ "$id" =~ ^TXN-[0-9]{8}T[0-9]{6}Z-[A-F0-9]{12}$ ]] || { echo "ERROR: invalid transaction ID: $id" >&2; exit 4; }
for f in 01-purchase-request 02-payment-confirmation 03-receipt; do
  [[ -f "$dir/$f.html" ]] || { echo "ERROR: missing $f.html" >&2; exit 5; }
  grep -q "transaction_id.*$id\|$id" "$dir/$f.html" || { echo "ERROR: $f does not carry issued ID $id" >&2; exit 6; }
done
for f in "$dir"/provider-evidence/*; do
  [[ -f "$f" ]] || continue
  case "${f,,}" in *paypal*|*Zelle*|*coinbase*) ;; *) echo "ERROR: unrecognized provider evidence: $f" >&2; exit 7;; esac
done
printf 'OK: transaction bundle structure valid: %s\n' "$id"
printf 'NOTE: content/evidence validation still requires operator review and the receipt validator.\n'
