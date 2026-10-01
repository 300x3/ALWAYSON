#!/usr/bin/env bash
# ALWAYS ON - provision the sales reporting path (Section 11.2 precondition 3).
# Reads the password from KDE Wallet (ao-admin/sales-reporting-password), which
# is the source of truth, and mirrors it back. No plaintext copy is retained.
set -Eeuo pipefail
umask 077
PW_FILE=/ALWAYSON/secrets/reporting/sales-reporting.env
WALLET_HELPER=/ALWAYSON/scripts/ops/wallet-read-secret.py

# 2026-10-01 hardening, same rationale as provision-metaread.sh: a missing
# wallet entry used to trigger silent generation, which would rotate the
# password on a live role. A locked wallet and a genuinely absent entry are
# indistinguishable at this point, so generation must be opt-in.
GENERATE_NEW=0
for arg in "$@"; do
  case "$arg" in
    --generate-new) GENERATE_NEW=1 ;;
    *) echo "Usage: ${0##*/} [--generate-new]" >&2; exit 2 ;;
  esac
done

PW="$("$WALLET_HELPER" kdewallet ao-admin sales-reporting-password 2>/dev/null || true)"
if [ -n "$PW" ]; then
  echo 'reusing the existing sales_reporting_role password from KDE Wallet'
elif [ "$GENERATE_NEW" -eq 1 ]; then
  PW="$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)"
  echo 'generated a new sales_reporting_role password (--generate-new)'
else
  echo "ERROR: no ao-admin/sales-reporting-password in KDE Wallet." >&2
  echo "  Refusing to generate implicitly -- that would silently rotate the" >&2
  echo "  password on a live role. Re-run with --generate-new if this really" >&2
  echo "  is a first-time bootstrap." >&2
  exit 3
fi
podman exec sales-db psql -U sales_migration_role -d salesdb -v ON_ERROR_STOP=1 \
  -c "ALTER ROLE sales_reporting_role PASSWORD '$PW';" >/dev/null
rm -f "$PW_FILE"
echo 'OK: password set on role; no plaintext copy retained'
if /ALWAYSON/scripts/ops/kwallet-provision.sh put kdewallet ao-admin sales-reporting-password "$PW" >/dev/null 2>&1; then
  echo 'OK: mirrored to KDE Wallet (ao-admin/sales-reporting-password)'
else
  echo 'WARN: KDE Wallet mirror failed (locked?)'
fi
install -m 0600 /tmp/reporting-hub.sql /tmp/reporting-hub.sql
pkexec /usr/bin/sudo -u postgres /usr/bin/psql -q -v ON_ERROR_STOP=1 --set=pw="$PW" -f /tmp/reporting-hub.sql 2>&1 | grep -vE '^$' | tail -20
echo 'DONE'
