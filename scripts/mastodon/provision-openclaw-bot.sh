#!/usr/bin/env bash
# provision-openclaw-bot.sh - create the OpenClaw Mastodon bot credential.
# Stores the bot password in KDE Wallet (ao-mastodon) and writes a gitignored
# env file the OpenClaw Mastodon posting skill reads.
set -Eeuo pipefail
cd /ALWAYSON
KW=scripts/ops/kwallet-provision.sh
ENV=secrets/mastodon/openclaw-mastodon.env
BOTPASS=$(openssl rand -hex 16)

"$KW" put kdewallet ao-mastodon openclaw-bot-password "$BOTPASS" >/dev/null
echo "stored openclaw-bot-password in KDE Wallet ao-mastodon"

umask 077
cat > "$ENV" <<EOF
# ALWAYS ON OpenClaw -> Mastodon bot credential (generated; gitignored;
# mirrored in KDE Wallet ao-mastodon).
MASTODON_SERVER=http://localhost:3000
MASTODON_BOT_HANDLE=300x3bot
MASTODON_BOT_EMAIL=300x3@posteo.net
MASTODON_BOT_PASSWORD=$BOTPASS
# MASTODON_ACCESS_TOKEN=   # fill after stack is up (tootctl or OAuth)
EOF
chmod 0600 "$ENV"
echo "wrote $ENV"
sed 's/\(=.*\)/=<redacted>/' "$ENV"

echo "--- verify wallet read ---"
"$KW" get kdewallet ao-mastodon openclaw-bot-password 2>/dev/null | tr -d '\n' | head -c 40
echo
