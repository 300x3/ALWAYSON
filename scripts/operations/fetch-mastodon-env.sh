#!/usr/bin/env bash
# ALWAYS ON - Materialize full Mastodon env from KDE Wallet.
# Usage: fetch-mastodon-env.sh <output-env-file>
# Static Mastodon topology remains repository-controlled; secrets come from KDE
# Wallet ao-mastodon.
set -Eeuo pipefail
OUTPUT="${1:?usage: fetch-mastodon-env.sh <output-env-file>}"
WALLET_HELPER=/ALWAYSON/scripts/ops/wallet-read-secret.py
umask 077
secret_key_base="$("$WALLET_HELPER" kdewallet ao-mastodon mastodon-secret-key-base)"
otp_secret="$("$WALLET_HELPER" kdewallet ao-mastodon mastodon-otp-secret)"
db_password="$("$WALLET_HELPER" kdewallet ao-mastodon mastodon-db-password)"
ar_deterministic="$("$WALLET_HELPER" kdewallet ao-mastodon mastodon-ar-deterministic-key)"
ar_primary="$("$WALLET_HELPER" kdewallet ao-mastodon mastodon-ar-primary-key)"
ar_salt="$("$WALLET_HELPER" kdewallet ao-mastodon mastodon-ar-derivation-salt)"
[[ -n "$secret_key_base" && -n "$otp_secret" && -n "$db_password" && -n "$ar_deterministic" && -n "$ar_primary" && -n "$ar_salt" ]] || {
  echo "ERROR: one or more KDE Wallet entries unavailable in ao-mastodon" >&2
  exit 3
}
{
  printf 'LOCAL_DOMAIN=300x3.com\n'
  printf 'SINGLE_USER_MODE=false\n'
  printf 'DEFAULT_LOCALE=en\n'
  printf 'SECRET_KEY_BASE=%s\n' "$secret_key_base"
  printf 'OTP_SECRET=%s\n' "$otp_secret"
  printf 'DB_HOST=mastodon-db\n'
  printf 'DB_USER=mastodon\n'
  printf 'DB_NAME=mastodon\n'
  printf 'DB_PASS=%s\n' "$db_password"
  printf 'POSTGRES_DB=mastodon\n'
  printf 'POSTGRES_USER=mastodon\n'
  printf 'POSTGRES_PASSWORD=%s\n' "$db_password"
  printf 'REDIS_HOST=mastodon-redis\n'
  printf 'REDIS_PORT=6379\n'
  printf 'WEB_CONCURRENCY=2\n'
  printf 'MAX_THREADS=5\n'
  printf 'STREAMING_CLUSTER_NUM=1\n'
  printf 'ES_ENABLED=false\n'
  printf 'ACTIVE_RECORD_ENCRYPTION_DETERMINISTIC_KEY=%s\n' "$ar_deterministic"
  printf 'ACTIVE_RECORD_ENCRYPTION_PRIMARY_KEY=%s\n' "$ar_primary"
  printf 'ACTIVE_RECORD_ENCRYPTION_KEY_DERIVATION_SALT=%s\n' "$ar_salt"
  printf 'RAILS_FORCE_SSL=true\n'
  printf 'LOCAL_HTTPS=true\n'
} >"$OUTPUT.tmp"
mv "$OUTPUT.tmp" "$OUTPUT"
chmod 0600 "$OUTPUT"
echo "OK: wallet-backed Mastodon env materialized"
