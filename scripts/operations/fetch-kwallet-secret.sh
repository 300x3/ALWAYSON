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
# Wait for the desktop session + kwalletd to be available (max ~60s),
# so we never D-Bus-activate kwalletd headless at login (which crashes
# kwalletd6 with "could not connect to display" -> SIGABRT).
kwallet_ready() {
    busctl --user list 2>/dev/null | grep -qE '(^|[[:space:]])org\.kde\.kwalletd6?5?([[:space:]]|$)'
}
for _i in $(seq 1 30); do
    if kwallet_ready; then
        break
    fi
    sleep 2
done
if ! kwallet_ready; then
    echo "ERROR: org.kde.kwalletd5/d6 not available on the session bus after 60s" >&2
    exit 1
fi

# Wallet folder per key. The legacy 'ALWAYSON' folder was retired 2026-09-30;
# every secret now lives in the ao-<domain> folder that owns it, matching the
# ao- naming standard used for networks, units and containers.
wallet_folder_for() {
    case "$1" in
        mastodon-db-password|mastodon-secret-key-base|mastodon-otp-secret|mastodon-db-app-password)
            echo "ao-mastodon" ;;
        sales-db-password)   echo "ao-sales" ;;
        webodm-postgres-password) echo "ao-mapping" ;;
    payment-db-password)            folder=ao-payment   ; pass_key=payment-db-password          ;;
    payment-paypal-webhook-id)      folder=ao-payment   ; pass_key=payment-paypal-webhook-id    ;;
    payment-paypal-webhook-secret)  folder=ao-payment   ; pass_key=payment-paypal-webhook-secret;;
    payment-coinbase-webhook-secret) folder=ao-payment ; pass_key=payment-coinbase-webhook-secret;;
        fabrication-db-password) echo "ao-fabrication" ;;
        *) echo "" ;;
    esac
}

fetch_secret() {
    local entry="$1"
    local folder; folder="$(wallet_folder_for "$entry")"
    [ -n "$folder" ] || { echo "no wallet folder mapped for $entry" >&2; return 2; }
    python3 -c "
import dbus, sys
folder = '$folder'
entry = '$entry'
bus = dbus.SessionBus()
kw = bus.get_object('org.kde.kwalletd6', '/modules/kwalletd6')
kwiface = dbus.Interface(kw, 'org.kde.KWallet')
handle = kwiface.open('kdewallet', 0, 'ao-secret-reader')
if handle < 0: sys.exit(1)
try:
    if not bool(kwiface.hasEntry(handle, folder, entry, 'ao-secret-reader')):
        sys.stderr.write('wallet entry unavailable: %s/%s\n' % (folder, entry)); sys.exit(3)
    val = kwiface.readPassword(handle, folder, entry, 'ao-secret-reader')
finally:
    kwiface.close(handle, False, 'ao-secret-reader')
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
            fabrication-db-password)
                val=$(fetch_secret "fabrication-db-password")
                printf 'POSTGRES_PASSWORD=%s\n' "$val"
                # The role is fabrication_role and the database is a_fab; a_fab is
                # the database name, not the role. Writing POSTGRES_USER=a_fab
                # makes the image try to bootstrap a role that does not exist.
                printf 'POSTGRES_USER=fabrication_role\n'
                printf 'POSTGRES_DB=a_fab\n'
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
