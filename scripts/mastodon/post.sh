#!/usr/bin/env bash
# mastodon-post.sh - post a status to the ALWAYS ON Mastodon "300X3".
# Origin: https://300x3.com (Cloudflare Tunnel edge; WORK 000060).
# Env override MASTODON_SERVER is honored; loopback default kept for
# pre-cutover diagnostics only.
# Credentials are NOT read from disk. They are materialized on demand from KDE
# Wallet (ao-mastodon) into a 0600 temp file, used, and removed. This script
# used to read /ALWAYSON/secrets/mastodon/openclaw-mastodon.env, a second
# plaintext copy of the bot token; KDE Wallet is the sole authority now
# (README 4.1 rule 7 / 14.1.1).
# Usage: mastodon-post.sh "status text" [--visibility public|private|unlisted]
set -Eeuo pipefail

umask 077
ENV="$(mktemp -t ao-openclaw-env.XXXXXX)"
trap 'shred -u "$ENV" 2>/dev/null || rm -f "$ENV"' EXIT
/ALWAYSON/scripts/operations/fetch-openclaw-mastodon-env.sh "$ENV" >/dev/null
[ -f "$ENV" ] || { echo "ERROR: could not materialize bot credentials from KDE Wallet ao-mastodon" >&2; exit 3; }
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
