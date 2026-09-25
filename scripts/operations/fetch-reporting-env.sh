#!/usr/bin/env bash
# ALWAYS ON - Materialize reporting PostgreSQL env from KDE Wallet.
# Usage: fetch-reporting-env.sh <metabase|grafana> <output-env-file>
# Static connection settings remain in repository-adjacent config; only the
# database password is taken from KDE Wallet.
set -Eeuo pipefail
ROLE="${1:?usage: fetch-reporting-env.sh <metabase|grafana> <output-env-file>}"
OUTPUT="${2:?usage: fetch-reporting-env.sh <metabase|grafana> <output-env-file>}"
WALLET_HELPER=/ALWAYSON/scripts/ops/wallet-read-secret.py
umask 077

case "$ROLE" in
  metabase)
    folder=ao-admin
    entry=metabase-db-password
    password="$("$WALLET_HELPER" kdewallet "$folder" "$entry")"
    [[ -n "$password" ]] || { echo "ERROR: KDE Wallet entry unavailable: $folder/$entry" >&2; exit 3; }
    {
      printf 'MB_DB_TYPE=postgres\n'
      printf 'MB_DB_HOST=10.42.0.1\n'
      printf 'MB_DB_PORT=5432\n'
      printf 'MB_DB_DBNAME=metabase\n'
      printf 'MB_DB_USER=metabase_app\n'
      printf 'MB_DB_SSL=false\n'
      printf 'MB_DB_PASS=%s\n' "$password"
    } >"$OUTPUT.tmp"
    ;;
  grafana)
    folder=ao-admin
    entry=grafana-db-password
    password="$("$WALLET_HELPER" kdewallet "$folder" "$entry")"
    [[ -n "$password" ]] || { echo "ERROR: KDE Wallet entry unavailable: $folder/$entry" >&2; exit 3; }
    {
      printf 'GF_DATABASE_TYPE=postgres\n'
      printf 'GF_DATABASE_HOST=10.42.0.1\n'
      printf 'GF_DATABASE_PORT=5432\n'
      printf 'GF_DATABASE_NAME=grafana\n'
      printf 'GF_DATABASE_USER=grafana_app\n'
      printf 'GF_DATABASE_SSL_MODE=disable\n'
      printf 'GF_PATHS_DATA=/var/lib/grafana-postgres\n'
      printf 'GF_DATABASE_PASSWORD=%s\n' "$password"
    } >"$OUTPUT.tmp"
    ;;
  *)
    echo "ERROR: unknown reporting role: $ROLE" >&2
    exit 2
    ;;
esac
mv "$OUTPUT.tmp" "$OUTPUT"
chmod 0600 "$OUTPUT"
echo "OK: wallet-backed reporting env materialized for $ROLE"
