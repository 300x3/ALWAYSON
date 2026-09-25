#!/usr/bin/env bash
# Validate the structural fields of a Corda-managed sale receipt record.
# This does not submit data, contact Corda, or validate signatures.
set -Eeuo pipefail
IFS=$'\n\t'
input="${1:?usage: validate-sale-receipt.sh <receipt.json>}"
[[ -f "$input" ]] || { echo "ERROR: file not found: $input" >&2; exit 2; }
command -v jq >/dev/null || { echo 'ERROR: jq is required' >&2; exit 3; }
required=(transaction_id correlation_id receipt_number event_timestamp_utc order_id customer_reference sku serial_number payment_reference corda_event_type schema_version corda_state sale_request_evidence payment_validation_evidence funds_transfer_evidence)
for key in "${required[@]}"; do jq -e --arg k "$key" 'has($k) and (.[$k] != null) and (.[$k] != "")' "$input" >/dev/null || { echo "ERROR: missing $key" >&2; exit 10; }; done
jq -e '.schema_version == "1.0" and (.transaction_id | test("^TXN-[0-9]{8}T[0-9]{6}Z-[A-F0-9]{12}$")) and (.corda_state | IN("PENDING_SUBMISSION","SUBMITTED","CONFIRMED","REJECTED","FAILED")) and (.corda_event_type | IN("SALE_CONTRACT_CREATED","ENTITLEMENT_ISSUED","ENTITLEMENT_REVOKED","FULFILLMENT_APPROVED","DELIVERY_CONFIRMED","RETURN_APPROVED","REFUND_RECORDED")) and (.sale_request_evidence.status == "validated") and (.payment_validation_evidence.status == "validated") and (.funds_transfer_evidence.status == "validated")' "$input" >/dev/null || { echo 'ERROR: invalid enum/schema value, transaction ID, or unvalidated evidence gate' >&2; exit 11; }
jq -e '(.event_timestamp_utc | fromdateiso8601)' "$input" >/dev/null 2>&1 || { echo 'ERROR: event_timestamp_utc must be ISO-8601 UTC' >&2; exit 12; }
if jq -e 'has("card_number") or has("cvv") or has("payment_password") or has("private_key")' "$input" >/dev/null; then echo 'ERROR: prohibited sensitive field present' >&2; exit 13; fi
printf 'OK: structural receipt validation passed: %s\n' "$input"
