# ALWAYS ON - check-ledger-ingest.sh: probe gateway health once deployed.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
if ! podman ps --format '{{.Names}}' 2>/dev/null | grep -q 'ledger-ingest'; then
  echo "PENDING: ledger-ingest gateway not deployed yet (Section 2.8 step 3 awaits Corda version approval)"
  exit 3
fi
code="$(curl -s -o /dev/null -w '%{http_code}' https://ledger-ingest.ao-ledger-ingest:8443/healthz --max-time 5 2>/dev/null || true)"
[[ "$code" == "200" ]] && { echo "OK: ledger ingest healthy"; exit 0; }
echo "FAIL: ledger ingest health returned '${code:-none}'" >&2
exit 44
