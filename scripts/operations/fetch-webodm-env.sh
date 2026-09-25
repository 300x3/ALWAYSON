#!/usr/bin/env bash
# ALWAYS ON - Materialize WebODM database env from KDE Wallet.
# Usage: fetch-webodm-env.sh <output-env-file>
set -Eeuo pipefail
OUTPUT="${1:?usage: fetch-webodm-env.sh <output-env-file>}"
WALLET_HELPER=/ALWAYSON/scripts/ops/wallet-read-secret.py
umask 077
password="$("$WALLET_HELPER" kdewallet ao-mapping webodm-postgres-password)"
[[ -n "$password" ]] || { echo "ERROR: KDE Wallet entry unavailable: ao-mapping/webodm-postgres-password" >&2; exit 3; }
printf 'POSTGRES_PASSWORD=%s\n' "$password" >"$OUTPUT.tmp"
mv "$OUTPUT.tmp" "$OUTPUT"
chmod 0600 "$OUTPUT"
echo "OK: wallet-backed WebODM env materialized"
