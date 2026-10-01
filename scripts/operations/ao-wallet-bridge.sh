#!/usr/bin/env bash
# ALWAYS ON - wallet bridge: materialize KWallet secrets to service env files.
# Runs as scottw (graphical session, wallet unlocked by PAM at login).
# KDE Wallet stays the center: values live in the wallet, files are 0600
# delivery copies refreshed at login. Never log secret values.
# Usage: ao-wallet-bridge.sh
set -Eeuo pipefail
OP=/ALWAYSON/scripts/operations
umask 077
fail=0
materialize() { # $1 = fetcher, rest = args
  if ! "$OP/$1" "${@:2}"; then
    echo "BRIDGE FAIL: $1 ${*:2}" >&2
    fail=1
  fi
}
install -d -m 0700 /home/scottw/.local/share/ao-secrets
STAGE=/home/scottw/.local/share/ao-secrets
# Mastodon full bundle (ao-mastodon folder) for the sales-domain stack.
materialize fetch-mastodon-env.sh $STAGE/mastodon.env
# Sales DB (ALWAYSON folder) for ao-sales-db.
materialize fetch-sales-db-env.sh $STAGE/sales-db.env
# Narrow read-only ACL for the consumer UID (approved 2026-09-29, option A):
# traverse + read on the two env files only. Wallet stays the source of truth.
setfacl -m u:ao-sales:--x /home/scottw /home/scottw/.local /home/scottw/.local/share /home/scottw/.local/share/ao-secrets
setfacl -m u:ao-sales:r-- $STAGE/mastodon.env $STAGE/sales-db.env
if [[ $fail -ne 0 ]]; then
  echo "BRIDGE: one or more secrets unavailable (wallet locked?)" >&2
  exit 3
fi
echo "BRIDGE OK: sales secrets materialized"