#!/usr/bin/env bash
# ALWAYS ON - Materialize Cloudflare Tunnel runtime config from KDE Wallet.
# Usage: fetch-cloudflared-env.sh <output-config-file> <output-credentials-file>
# Only the tunnel ID and credentials JSON come from KDE Wallet. Routing policy
# remains repository-controlled.
set -Eeuo pipefail
CONFIG_OUTPUT="${1:?usage: fetch-cloudflared-env.sh <output-config-file> <output-credentials-file>}"
CREDENTIALS_OUTPUT="${2:?usage: fetch-cloudflared-env.sh <output-config-file> <output-credentials-file>}"
WALLET_HELPER=/ALWAYSON/scripts/ops/wallet-read-secret.py
umask 077
tunnel_id="$("$WALLET_HELPER" kdewallet ao-mastodon cloudflare-tunnel-id)"
[[ -n "$tunnel_id" ]] || { echo "ERROR: KDE Wallet entry unavailable: ao-mastodon/cloudflare-tunnel-id" >&2; exit 3; }
"$WALLET_HELPER" kdewallet ao-mastodon cloudflare-tunnel-credentials-json >"$CREDENTIALS_OUTPUT.tmp"
[[ -s "$CREDENTIALS_OUTPUT.tmp" ]] || { echo "ERROR: KDE Wallet entry unavailable: ao-mastodon/cloudflare-tunnel-credentials-json" >&2; exit 3; }
mv "$CREDENTIALS_OUTPUT.tmp" "$CREDENTIALS_OUTPUT"
chmod 0400 "$CREDENTIALS_OUTPUT"
{
  printf '# Generated from KDE Wallet ao-mastodon at service startup.\n'
  printf 'tunnel: %s\n' "$tunnel_id"
  printf 'credentials-file: %s\n' "$CREDENTIALS_OUTPUT"
  printf 'ingress:\n'
  printf '  - hostname: mastodon.300x3.com\n'
  printf '    service: http://127.0.0.1:3000\n'
  printf '  - service: http_status:404\n'
} >"$CONFIG_OUTPUT.tmp"
mv "$CONFIG_OUTPUT.tmp" "$CONFIG_OUTPUT"
chmod 0600 "$CONFIG_OUTPUT"
echo "OK: wallet-backed Cloudflare Tunnel config materialized"
