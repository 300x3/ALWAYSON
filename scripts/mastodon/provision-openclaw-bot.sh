#!/usr/bin/env bash
# provision-openclaw-bot.sh - create the OpenClaw Mastodon bot credential.
# The bot password is generated and stored ONLY in KDE Wallet (ao-mastodon);
# no plaintext env file is written any more. Consumers materialize the
# credential on demand with scripts/operations/fetch-openclaw-mastodon-env.sh
# (README 4.1 rule 7 / 14.1.1).
set -Eeuo pipefail
cd /ALWAYSON
KW=scripts/ops/kwallet-provision.sh
BOTPASS=$(openssl rand -hex 16)

"$KW" put kdewallet ao-mastodon openclaw-bot-password "$BOTPASS" >/dev/null
echo "stored openclaw-bot-password in KDE Wallet ao-mastodon"

echo "no plaintext env file written; consumers run fetch-openclaw-mastodon-env.sh"

echo "--- verify wallet read (length only, value not shown) ---"
"$KW" get kdewallet ao-mastodon openclaw-bot-password 2>/dev/null | tr -d '\n' | wc -c
