# ALWAYS ON - submit-ledger-event.sh: submit signed manifest to ledger-ingest gateway.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
m="${1:-}"
[[ -f "$m" ]] || { echo "Usage: ${0##*/} <signed-manifest.json>" >&2; exit 2; }
sig="$(jq -r '.signature // empty' "$m")"
[[ -n "$sig" ]] || { echo "ERROR: manifest is unsigned (run sign-manifest.sh first)" >&2; exit 20; }
if ! podman ps --format '{{.Names}}' 2>/dev/null | grep -q 'ledger-ingest'; then
  mkdir -p "$AO_ROOT/artifacts/pending-ledger-submissions/$(date -u +%Y%m%d)"
  install "$m" "$AO_ROOT/artifacts/pending-ledger-submissions/$(date -u +%Y%m%d)/"
  echo "PENDING: gateway not deployed; manifest staged for later submission"
  exit 3
fi
echo "ERROR: mTLS client certificate provisioning required first (Section 3.4) - paused for operator approval" >&2
exit 21
