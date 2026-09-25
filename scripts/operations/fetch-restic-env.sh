#!/usr/bin/env bash
# ALWAYS ON - Materialize restic environment from KDE Wallet.
# Usage: fetch-restic-env.sh <output-env-file>
# The repository path is host configuration; only the repository password
# comes from KDE Wallet.
set -Eeuo pipefail
OUTPUT="${1:?usage: fetch-restic-env.sh <output-env-file>}"
WALLET_HELPER=/ALWAYSON/scripts/ops/wallet-read-secret.py
umask 077
repository=/var/backups/alwayson-restic
if [[ -r /ALWAYSON/secrets/operations/restic.env ]]; then
  repository="$(sed -n 's/^RESTIC_REPOSITORY=//p' /ALWAYSON/secrets/operations/restic.env | tail -n1)"
fi
[[ -n "$repository" ]] || repository=/var/backups/alwayson-restic
password="$("$WALLET_HELPER" kdewallet ao-admin restic-repository-password)"
[[ -n "$password" ]] || { echo "ERROR: KDE Wallet entry unavailable: ao-admin/restic-repository-password" >&2; exit 3; }
{
  printf 'RESTIC_REPOSITORY=%s\n' "$repository"
  printf 'RESTIC_PASSWORD=%s\n' "$password"
} >"$OUTPUT.tmp"
mv "$OUTPUT.tmp" "$OUTPUT"
chmod 0600 "$OUTPUT"
echo "OK: wallet-backed restic env materialized"
