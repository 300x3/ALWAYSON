#!/usr/bin/env bash
# mastodon-post.sh - post a status to the local ALWAYS ON Mastodon "300X3".
# Reads credentials from /ALWAYSON/secrets/mastodon/openclaw-mastodon.env
# (gitignored; mirrored in KDE Wallet ao-mastodon).
# Usage: mastodon-post.sh "status text" [--visibility public|private|unlisted]
set -Eeuo pipefail

ENV=/ALWAYSON/secrets/mastodon/openclaw-mastodon.env
[ -f "$ENV" ] || { echo "ERROR: $ENV missing (run provision-openclaw-bot.sh)" >&2; exit 3; }
set -a; . "$ENV"; set +a

SERVER="${MASTODON_SERVER:-http://127.0.0.1:3000}"
TOKEN="${MASTODON_ACCESS_TOKEN:-}"
[ -n "$TOKEN" ] || { echo "ERROR: MASTODON_ACCESS_TOKEN not set (obtain once stack is up; see docs/runbooks/mastodon.md)" >&2; exit 3; }

TEXT="${1:-}"
[ -n "$TEXT" ] || { echo "Usage: mastodon-post.sh <status> [--visibility ...]" >&2; exit 2; }
VIS="public"
[ "${2:-}" = "--visibility" ] && [ -n "${3:-}" ] && VIS="$3"

# draft-by-default safety unless explicitly approved (Section 3.8)
[ "$VIS" = "public" ] && { echo "Refusing public by default; use --visibility private|unlisted unless operator approved." >&2; exit 2; }

curl -sS -H "Authorization: Bearer $TOKEN" \
  --data-urlencode "status=$TEXT" \
  --data-urlencode "visibility=$VIS" \
  "$SERVER/api/v1/statuses"
