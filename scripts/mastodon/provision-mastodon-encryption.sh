#!/usr/bin/env bash
# provision-mastodon-encryption.sh - generate Mastodon v4.3+ ActiveRecord
# encryption keys, store them in KDE Wallet (ao-mastodon) and append them to
# the gitignored mastodon.env. Idempotent.
set -Eeuo pipefail
cd /ALWAYSON
KW=scripts/ops/kwallet-provision.sh
ENV=secrets/mastodon/mastodon.env

have() { grep -q "^$1=" "$ENV" 2>/dev/null && [ -n "$(sed -n "s/^$1=//p" "$ENV" | tail -1)" ]; }

gen_if_missing() { # <varname> <wallet-entry>
  local var="$1" entry="$2" val
  if have "$var"; then echo "$var: already present"; return 0; fi
  val=$(openssl rand -hex 32)
  printf '%s=%s\n' "$var" "$val" >> "$ENV"
  "$KW" put kdewallet ao-mastodon "$entry" "$val" >/dev/null
  echo "$var: generated + stored in KDE Wallet (ao-mastodon/$entry)"
}

gen_if_missing ACTIVE_RECORD_ENCRYPTION_DETERMINISTIC_KEY mastodon-ar-deterministic-key
gen_if_missing ACTIVE_RECORD_ENCRYPTION_PRIMARY_KEY        mastodon-ar-primary-key
gen_if_missing ACTIVE_RECORD_ENCRYPTION_KEY_DERIVATION_SALT mastodon-ar-derivation-salt
chmod 0600 "$ENV"
echo "--- wallet verification ---"
"$KW" get kdewallet ao-mastodon mastodon-ar-primary-key 2>/dev/null | tr -d '\n' | head -c 30; echo "..."
