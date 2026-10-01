#!/usr/bin/env bash
# ALWAYS ON - dump a host PostgreSQL database using an application role.
# Usage: backup-host-postgres.sh <role-label> <database> <user>
# Passwords are sourced from KDE Wallet; no plaintext reporting credential is
# read from /ALWAYSON/secrets during backup.
set -Eeuo pipefail
role_label="${1:?role label}"; db="${2:?database}"; user="${3:?user}"
WALLET_HELPER=/ALWAYSON/scripts/ops/wallet-read-secret.py
case "$role_label:$db:$user" in
  metabase:metabase:metabase_app) folder=ao-admin; pass_key=metabase-db-password ;;
  grafana:grafana:grafana_app) folder=ao-admin; pass_key=grafana-db-password ;;
  sales:salesdb:sales_migration_role) folder=ALWAYSON; pass_key=sales-db-password ;;
  mastodon:mastodon:mastodon) folder=ALWAYSON; pass_key=mastodon-db-password ;;
  webodm:webodm:webodm_app) folder=ALWAYSON; pass_key=webodm-postgres-password ;;
  *) echo "refusing unexpected host PostgreSQL backup target" >&2; exit 2 ;;
esac
PGPASSWORD="$("$WALLET_HELPER" kdewallet "$folder" "$pass_key")"
export PGPASSWORD
[[ -n "$PGPASSWORD" ]] || { echo "missing password from KDE Wallet $folder/$pass_key" >&2; exit 2; }
out="/ALWAYSON/backups/postgres/${role_label}/$(date -u +%Y%m%dT%H%M%SZ)-${db}.sql.gz"
mkdir -p "$(dirname "$out")"; chmod 0750 "$(dirname "$out")"
if pg_dump --host=127.0.0.1 --port=5432 --username="$user" --dbname="$db" --no-owner --no-privileges | gzip -9 >"$out.tmp"; then
  # Assert non-trivial size (> 1KB) to catch empty dumps
  size=$(stat -c%s "$out.tmp" 2>/dev/null || echo 0)
  if [ "$size" -lt 1024 ]; then
    echo "FAILED: pg_dump output suspiciously small (${size} bytes) for $db" >&2
    rm -f "$out.tmp"; exit 1
  fi
  mv "$out.tmp" "$out"; chmod 0640 "$out"; echo "OK: $out ($size bytes)"
else
  rm -f "$out.tmp"; echo "FAILED: host pg_dump database=$db" >&2; exit 1
fi
