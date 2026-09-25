#!/usr/bin/env bash
# ALWAYS ON - provision the sales reporting path (Section 11.2 precondition 3).
set -Eeuo pipefail
umask 077
PW_FILE=/ALWAYSON/secrets/reporting/sales-reporting.env
PW=""
[ -f "$PW_FILE" ] && PW="$(sed -n 's/^SALES_REPORTING_PASSWORD=//p' "$PW_FILE" | tail -n1)"
if [ -z "$PW" ]; then
  PW="$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)"
  echo 'generated a new sales_reporting_role password'
else
  echo 'reusing the existing sales_reporting_role password'
fi
podman exec sales-db psql -U sales_migration_role -d salesdb -v ON_ERROR_STOP=1 \
  -c "ALTER ROLE sales_reporting_role PASSWORD '$PW';" >/dev/null
printf 'SALES_REPORTING_USER=sales_reporting_role\nSALES_REPORTING_PASSWORD=%s\n' "$PW" > "$PW_FILE"
chmod 0600 "$PW_FILE"
echo 'OK: password set on role and stored 0600'
if /ALWAYSON/scripts/ops/kwallet-provision.sh put kdewallet ao-admin sales-reporting-password "$PW" >/dev/null 2>&1; then
  echo 'OK: mirrored to KDE Wallet (ao-admin/sales-reporting-password)'
else
  echo 'WARN: KDE Wallet mirror failed (locked?)'
fi
install -m 0600 /tmp/reporting-hub.sql /tmp/reporting-hub.sql
pkexec /usr/bin/sudo -u postgres /usr/bin/psql -q -v ON_ERROR_STOP=1 --set=pw="$PW" -f /tmp/reporting-hub.sql 2>&1 | grep -vE '^$' | tail -20
echo 'DONE'
