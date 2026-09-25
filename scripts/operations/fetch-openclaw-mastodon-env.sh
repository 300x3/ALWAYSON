#!/usr/bin/env bash
# ALWAYS ON - Materialize OpenClaw/Mastodon bridge env from KDE Wallet.
# Usage: fetch-openclaw-mastodon-env.sh <output-env-file>
set -Eeuo pipefail
OUTPUT="${1:?usage: fetch-openclaw-mastodon-env.sh <output-env-file>}"
WALLET_HELPER=/ALWAYSON/scripts/ops/wallet-read-secret.py
umask 077
bot_password="$("$WALLET_HELPER" kdewallet ao-mastodon openclaw-bot-password)"
access_token="$("$WALLET_HELPER" kdewallet ao-mastodon openclaw-bot-access-token)"
client_id="$("$WALLET_HELPER" kdewallet ao-mastodon openclaw-bot-client-id)"
client_secret="$("$WALLET_HELPER" kdewallet ao-mastodon openclaw-bot-client-secret)"
[[ -n "$bot_password" && -n "$access_token" && -n "$client_id" && -n "$client_secret" ]] || {
  echo "ERROR: one or more KDE Wallet entries unavailable in ao-mastodon" >&2
  exit 3
}
{
  printf 'MASTODON_SERVER=https://300x3.com\n'
  printf 'MASTODON_BOT_HANDLE=bot\n'
  printf 'MASTODON_BOT_EMAIL=300x3@posteo.net\n'
  printf 'MASTODON_BOT_PASSWORD=%s\n' "$bot_password"
  printf 'MASTODON_ACCESS_TOKEN=%s\n' "$access_token"
  printf 'MASTODON_CLIENT_ID=%s\n' "$client_id"
  printf 'MASTODON_CLIENT_SECRET=%s\n' "$client_secret"
} >"$OUTPUT.tmp"
mv "$OUTPUT.tmp" "$OUTPUT"
chmod 0600 "$OUTPUT"
echo "OK: wallet-backed OpenClaw/Mastodon env materialized"
