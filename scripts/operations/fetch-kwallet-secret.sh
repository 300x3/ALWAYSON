#!/bin/bash
# ALWAYS ON - Fetch secrets from KDE Wallet (KWallet) for systemd Quadlet units
# Usage: fetch-kwallet-secret.sh <output-env-file> <entry1> [entry2] ...
set -euo pipefail

if [ $# -lt 2 ]; then
    echo "Usage: $0 <output-env-file> <entry1> [entry2] ..."
    exit 1
fi

OUTPUT_FILE="$1"
shift

fetch_secret() {
    local entry="$1"
    python3 -c "
import dbus, sys
bus = dbus.SessionBus()
kw = bus.get_object('org.kde.kwalletd5', '/modules/kwalletd5')
kwiface = dbus.Interface(kw, 'org.kde.KWallet')
handle = kwiface.open('kdewallet', 0, 'ALWAYSON')
if handle < 0: sys.exit(1)
val = kwiface.readPassword(handle, 'ALWAYSON', '$entry', 'ALWAYSON')
kwiface.close(handle, False, 'ALWAYSON')
print(val, end='')
"
}

{
    for entry in "$@"; do
        case "$entry" in
            webodm-postgres-password)
                val=$(fetch_secret "webodm-postgres-password")
                printf 'POSTGRES_PASSWORD=%s\n' "$val"
                ;;
            sales-db-password)
                val=$(fetch_secret "sales-db-password")
                printf 'POSTGRES_PASSWORD=%s\n' "$val"
                ;;
            mastodon-db-password)
                val=$(fetch_secret "mastodon-db-password")
                printf 'POSTGRES_PASSWORD=%s\n' "$val"
                printf 'POSTGRES_USER=mastodon\n'
                printf 'POSTGRES_DB=mastodon\n'
                ;;
            mastodon-secret-key-base)
                val=$(fetch_secret "mastodon-secret-key-base")
                printf 'SECRET_KEY_BASE=%s\n' "$val"
                ;;
            mastodon-otp-secret)
                val=$(fetch_secret "mastodon-otp-secret")
                printf 'OTP_SECRET=%s\n' "$val"
                ;;
            mastodon-db-app-password)
                val=$(fetch_secret "mastodon-db-password")
                printf 'DB_PASS=%s\n' "$val"
                printf 'POSTGRES_PASSWORD=%s\n' "$val"
                ;;
            *)
                echo "Unknown secret entry: $entry" >&2
                exit 1
                ;;
        esac
    done
} > "$OUTPUT_FILE.tmp"

mv "$OUTPUT_FILE.tmp" "$OUTPUT_FILE"
chmod 600 "$OUTPUT_FILE"
echo "Secrets written to $OUTPUT_FILE"
