#!/usr/bin/env bash
# ALWAYS ON - email intake to printed PDF forms.
#
#   intake-to-pdf.sh <request.txt> <out-dir> [--sha256 HASH]
#
# Reads a website Kit Request (the text produced by intake-kit-request-pdf.sh,
# or a forwarded email body) and produces two single-page PDFs:
#
#   00-kit-request-intake-record.pdf   what was received, and how it read
#   01-kit-request-work-order.pdf      the work order for operator review
#
# Both come from the same parsed record, so they cannot disagree. Nothing is
# sent anywhere, no payment is taken, no order is created and no Corda state
# changes: every output carries sale_logged=false, corda_state=NOT_SUBMITTED.
set -Eeuo pipefail
IFS=$'\n\t'

ROOT=/ALWAYSON
source_txt="${1:?usage: intake-to-pdf.sh <request.txt> <out-dir> [--sha256 HASH]}"
out_dir="${2:?usage: intake-to-pdf.sh <request.txt> <out-dir>}"
shift 2

[[ -f "$source_txt" ]] || { echo "ERROR: no such file: $source_txt" >&2; exit 2; }
mkdir -p "$out_dir"

record="$out_dir/request-record.json"
python3 "$ROOT/scripts/sales/intake-request-record.py" \
  "$source_txt" "$record" \
  --items "$ROOT/config/sales/catalogue.csv" "$@"
record_status=$?

for form in 00-kit-request-intake-record 01-kit-request-work-order; do
  python3 "$ROOT/scripts/sales/autofill-handoff-form.py" \
    "$ROOT/forms/handoffs/$form.html" "$record" \
    "$out_dir/$form.html" "$out_dir/$form.pdf" \
    --css "$ROOT/assets/sales-print.css" 2>/dev/null \
    || { echo "ERROR: render failed for $form" >&2; exit 3; }
done

# Overlay the clickable AcroForm fields where a spec exists for the form.
spec_dir="$ROOT/config/sales/examples"
for form in 00-kit-request-intake-record 01-kit-request-work-order; do
  spec="$spec_dir/$form.fields.json"
  [[ -f "$spec" ]] || continue
  python3 "$ROOT/scripts/sales/add-pdf-form-fields.py" \
    "$out_dir/$form.pdf" "$out_dir/$form-fillable.pdf" --fields "$spec" \
    || { echo "ERROR: form-field overlay failed for $form" >&2; exit 5; }
done

# One page each, or the sheet is wrong and must not be filed.
for pdf in "$out_dir"/*.pdf; do
  pages=$(pdfinfo "$pdf" | awk '/^Pages:/{print $2}')
  if [[ "$pages" != "1" ]]; then
    echo "ERROR: $(basename "$pdf") is $pages pages, expected 1" >&2
    exit 4
  fi
  echo "OK: 1 page - $pdf"
done

echo "record: $record"
exit $record_status