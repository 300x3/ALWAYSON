#!/usr/bin/env bash
# ALWAYS ON - Materialize sales database env from KDE Wallet.
# Usage: fetch-sales-db-env.sh <output-env-file>
set -Eeuo pipefail
OUTPUT="${1:?usage: fetch-sales-db-env.sh <output-env-file>}"
WALLET_HELPER=/ALWAYSON/scripts/ops/wallet-read-secret.py
umask 077
password="$("$WALLET_HELPER" kdewallet ALWAYSON sales-db-password)"
[[ -n "$password" ]] || { echo "ERROR: KDE Wallet entry unavailable: ALWAYSON/sales-db-password" >&2; exit 3; }
{
  printf 'POSTGRES_PASSWORD=%s\n' "$password"
  printf 'POSTGRES_USER=sales_migration_role\n'
} >"$OUTPUT.tmp"
mv "$OUTPUT.tmp" "$OUTPUT"
chmod 0600 "$OUTPUT"
echo "OK: wallet-backed sales database env materialized"
