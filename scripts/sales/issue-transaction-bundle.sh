#!/usr/bin/env bash
# ALWAYS ON - issue one transaction bundle ID and create its three-form folder.
set -Eeuo pipefail
IFS=$'\n\t'
ROOT=/ALWAYSON/data/sales/transactions
mkdir -p "$ROOT"
id="TXN-$(date -u +%Y%m%dT%H%M%SZ)-$(openssl rand -hex 6 | tr '[:lower:]' '[:upper:]')"
dir="$ROOT/$id"
mkdir -m 0750 "$dir" "$dir/provider-evidence"
for form in 01-purchase-request 02-payment-confirmation 03-receipt; do
  sed "s/transaction_id\" name=\"transaction_id\"/transaction_id\" name=\"transaction_id\" value=\"$id\"/" \
    "/ALWAYSON/forms/transactions/$form.html" >"$dir/$form.html"
  chmod 0640 "$dir/$form.html"
done
    { echo "transaction_id=$id"; echo "purchase_request=pending"; echo "payment_confirmation=pending"; echo "receipt=pending"; echo "provider_evidence=pending"; echo "corda_state=NOT_SUBMITTED"; echo "sale_logged=false"; echo "created_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } >"$dir/BUNDLE-STATUS.txt"
chmod 0640 "$dir/BUNDLE-STATUS.txt"
printf '%s\n' "$dir"
