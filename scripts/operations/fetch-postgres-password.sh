#!/usr/bin/env bash
# ALWAYS ON - Fetch one PostgreSQL credential from KDE Wallet.
# Usage: fetch-postgres-password.sh <wallet-folder> <wallet-entry>
set -Eeuo pipefail
FOLDER="${1:?usage: fetch-postgres-password.sh <wallet-folder> <wallet-entry>}"
ENTRY="${2:?usage: fetch-postgres-password.sh <wallet-folder> <wallet-entry>}"
exec /ALWAYSON/scripts/ops/wallet-read-secret.py kdewallet "$FOLDER" "$ENTRY"
