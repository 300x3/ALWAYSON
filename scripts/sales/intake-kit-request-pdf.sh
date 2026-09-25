#!/usr/bin/env bash
# ALWAYS ON - non-destructive intake of KIT REQUEST PDFs.
# Creates hash, extracted text, manifest, and review record. Does not log a sale.
set -Eeuo pipefail
IFS=$'\n\t'
ROOT=/ALWAYSON/data/sales/kit-request-intake
INBOX=$ROOT/inbox
EXTRACTED=$ROOT/extracted
MANIFESTS=$ROOT/manifests
REVIEW=$ROOT/review
mkdir -p "$INBOX" "$EXTRACTED" "$MANIFESTS" "$REVIEW" "$ROOT/archive" "$ROOT/quarantine"
source_pdf="${1:?usage: intake-kit-request-pdf.sh <inbox-pdf>}"
[[ -f "$source_pdf" ]] || { echo "ERROR: PDF not found: $source_pdf" >&2; exit 2; }
[[ "$source_pdf" == *.pdf || "$source_pdf" == *.PDF ]] || { echo 'ERROR: input must be .pdf' >&2; exit 2; }
command -v pdfinfo >/dev/null || { echo 'ERROR: pdfinfo is required' >&2; exit 3; }
command -v pdftotext >/dev/null || { echo 'ERROR: pdftotext is required' >&2; exit 3; }
command -v sha256sum >/dev/null || { echo 'ERROR: sha256sum is required' >&2; exit 3; }
base="$(basename "$source_pdf")"; id="$(date -u +%Y%m%dT%H%M%SZ)-${RANDOM}"
meta="$MANIFESTS/$id.json"; text="$EXTRACTED/$id.txt"; review="$REVIEW/$id.md"
info="$(pdfinfo "$source_pdf" 2>/dev/null || true)"
pdftotext -layout "$source_pdf" "$text"
if grep -Eiq 'card number|cvv|bank account|routing number|password|private key|BEGIN (RSA|OPENSSH|PRIVATE)' "$text"; then dest="$ROOT/quarantine/$id-$(basename "$source_pdf")"; reason='sensitive-payment-or-secret-pattern-detected'; else dest="$ROOT/archive/$id-$(basename "$source_pdf")"; reason='request-intake-only'; fi
install -m 0440 "$source_pdf" "$dest"
hash="$(sha256sum "$dest" | awk '{print $1}')"
jq -n --arg id "$id" --arg source "$source_pdf" --arg sha256 "$hash" --arg text "$text" --arg archive "$dest" --arg reason "$reason" --arg info "$info" '{intake_id:$id,source_path:$source,sha256:$sha256,extracted_text_path:$text,stored_path:$archive,classification:"kit_request_inquiry",sale_logged:false,corda_state:"NOT_SUBMITTED",reason:$reason,pdfinfo:$info,ingested_at_utc:(now|todate)}' >"$meta"
cat >"$review" <<EOF
# KIT REQUEST Intake Review

- Intake ID: \`$id\`
- Source PDF: \`$source_pdf\`
- Stored copy: \`$dest\`
- SHA-256: \`$hash\`
- Extracted text: \`$text\`
- Classification: **kit_request_inquiry**
- Sale logged: **No**
- Corda state: **NOT_SUBMITTED**
- Review reason: $reason

## Required human review

- [ ] PDF is legible and matches the KIT REQUEST format
- [ ] Requester identity is validated
- [ ] Selected kit(s) are identified
- [ ] Request is not a duplicate
- [ ] Classify as inquiry, quote, pending payment, or verified sale
- [ ] If payment is verified, create the PostgreSQL sale projection
- [ ] Submit a signed sale-contract manifest through ledger-ingest
- [ ] Record Corda confirmation before issuing a final receipt
EOF
chmod 0640 "$meta" "$text" "$review"; printf 'OK: intake=%s\nmanifest=%s\ntext=%s\nreview=%s\nstored=%s\nsale_logged=false\ncorda_state=NOT_SUBMITTED\n' "$id" "$meta" "$text" "$review" "$dest"
