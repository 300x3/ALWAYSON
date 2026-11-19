# ALWAYS ON - submit-ledger-event.sh: submit signed manifest to ledger-ingest gateway.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
m="${1:-}"
[[ -f "$m" ]] || { echo "Usage: ${0##*/} <signed-manifest.json>" >&2; exit 2; }
sig="$(jq -r '.signature // empty' "$m")"
[[ -n "$sig" ]] || { echo "ERROR: manifest is unsigned (run sign-manifest.sh first)" >&2; exit 20; }
if ! podman ps --format '{{.Names}}' 2>/dev/null | grep -q 'ledger-ingest'; then
  staging_dir="$AO_ROOT/artifacts/pending-ledger-submissions/$(date -u +%Y%m%d)"
  mkdir -p "$staging_dir"
  manifest_hash="$(sha256sum "$m" | awk '{print $1}')"
  staging_name="manifest-${manifest_hash}.json"
  if [[ -f "$staging_dir/$staging_name" ]]; then
    echo "PENDING: manifest with identical content already staged; not duplicating"
    exit 3
  fi
  install -m 0600 "$m" "$staging_dir/$staging_name"
  echo "PENDING: gateway not deployed; manifest staged for later submission"
  exit 3
fi
echo "ERROR: mTLS client certificate provisioning required first (Section 3.4) - paused for operator approval" >&2
exit 21
