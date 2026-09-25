#!/usr/bin/env bash
# ALWAYS ON - provision the metaread reporting identity (Section 6.A.2).
set -Eeuo pipefail
umask 077
PW_FILE=/ALWAYSON/secrets/reporting/metaread.env
PW=""
[ -f "$PW_FILE" ] && PW="$(sed -n 's/^METAREAD_PASSWORD=//p' "$PW_FILE" | tail -n1)"
if [ -z "$PW" ]; then
  PW="$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)"
  echo 'generated a new metaread password'
else
  echo 'reusing the existing metaread password'
fi
chmod 0644 /tmp/metaread-grants.sql
pkexec /usr/bin/sudo -u postgres /usr/bin/psql -q -v ON_ERROR_STOP=1 --set=pw="$PW" -f /tmp/metaread-grants.sql 2>&1 | tail -15
printf 'METAREAD_USER=metaread\nMETAREAD_PASSWORD=%s\n' "$PW" > "$PW_FILE"
chmod 0600 "$PW_FILE"
echo 'OK: metaread password set and stored 0600'
if /ALWAYSON/scripts/ops/kwallet-provision.sh put kdewallet ao-admin metaread-password "$PW" >/dev/null 2>&1; then
  echo 'OK: mirrored to KDE Wallet (ao-admin/metaread-password)'
else
  echo 'WARN: KDE Wallet mirror failed'
fi
echo DONE
