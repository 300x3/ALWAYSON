#!/bin/bash
# ALWAYS ON - Fetch secrets from KDE Wallet (KWallet) for systemd Quadlet units
# Usage: fetch-kwallet-secret.sh <output-env-file> <entry1> [entry2] ...
set -euo pipefail

# 2026-10-01: umask 077 was MISSING here while the sibling fetch-reporting-env.sh
# had it. Consequence, measured not assumed: the shell creates "$OUTPUT_FILE.tmp"
# with mode 0664 under the default umask, so the secret sits world-readable in
# that temp file for the whole duration of the write block. Only the FINAL file
# got chmod 600 (line 141), so the guard in check-secrets-exposure.sh passed
# while the exposure window was real. Observed live: a leftover 0-byte
# reporting-grafana-admin.env.tmp at mode 0664. Fix the creation mode, not just
# the end state.
umask 077

# Never leave a stale temp file behind. Observed 2026-10-01: a 0-byte
# reporting-grafana-admin.env.tmp survived a failed ExecStartPre and sat in the
# secrets directory indefinitely. A future reader (or script) could mistake it
# for a real materialized secret.
if [ $# -lt 2 ]; then
    echo "Usage: $0 <output-env-file> <entry1> [entry2] ..."
    exit 1
fi

OUTPUT_FILE="$1"
shift

# The trap is installed only after OUTPUT_FILE is assigned: `set -u` would make
# the cleanup function abort on the usage-error path above.
cleanup_tmp() { rm -f "$OUTPUT_FILE.tmp"; }
trap cleanup_tmp EXIT

# Wait for the desktop session + kwalletd to be available (max ~60s),
# so we never D-Bus-activate kwalletd headless at login (which crashes
# kwalletd6 with "could not connect to display" -> SIGABRT).
# 2026-10-01 FIX (this predicate was the real root cause of the ao-grafana /
# ao-metabase login outage). It previously tested only whether kwalletd was
# *present on the session bus*:
#
#     busctl --user list | grep -q 'org.kde.kwalletd6'
#
# kwalletd6 is D-Bus-activated the instant anything touches it and appears on
# the bus LONG BEFORE the wallet is unlocked. So the predicate returned true
# immediately, the 60-second wait never actually waited, and both units read
# the wallet while it was still locked -> hasEntry false -> ExecStartPre failed
# -> systemd's 5 fast restarts were exhausted in ~5 seconds and the unit stayed
# down. Measured: units first attempted at 15:08:20, wallet usable by 15:08:40.
#
# The correct question is not "is the daemon up" but "is the wallet OPEN".
# isOpen(handle) is the D-Bus method that answers it. Note the single-argument
# form: KWallet also declares an isOpen(wallet, app) overload, and dbus-python
# resolves the proxy to the LAST declared signature, so passing an app name
# raises TypeError. See README 14.1.1 for the verified call.
kwallet_ready() {
    python3 - <<'PY' >/dev/null 2>&1
import dbus
bus = dbus.SessionBus()
kw = bus.get_object('org.kde.kwalletd6', '/modules/kwalletd6')
iface = dbus.Interface(kw, 'org.kde.KWallet')
h = iface.open('kdewallet', 0, 'ao-secret-reader')
if not isinstance(h, int) or h < 0:
    raise SystemExit(1)
try:
    if not bool(iface.isOpen(h)):
        raise SystemExit(1)
finally:
    iface.close(h, False, 'ao-secret-reader')
PY
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
          payment-db-password|payment-paypal-webhook-id|payment-paypal-webhook-secret|payment-coinbase-webhook-secret)
              echo "ao-payment" ;;
        fabrication-db-password) echo "ao-fabrication" ;;
        grafana-admin-password|metabase-admin-password|metaread-password|sales-reporting-password|restic-repository-password)
            echo "ao-admin" ;;
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
            payment-credentials)
                # Writes the COMPLETE env file in one pass, deliberately.
                # Every invocation rewrites the whole output file, so one
                # ExecStartPre per key would each erase the previous one's
                # output and leave the adapter with no PAYMENT_DSN at all.
                # Assembled from wallet material only; nothing is echoed.
                dbp=$(fetch_secret "payment-db-password")
                ppi=$(fetch_secret "payment-paypal-webhook-id")
                pps=$(fetch_secret "payment-paypal-webhook-secret")
                cbs=$(fetch_secret "payment-coinbase-webhook-secret")
                printf 'PAYMENT_DSN=postgresql://sales_migration_role:%s@127.0.0.1:15432/salesdb\n' "$dbp"
                printf 'PAYPAL_WEBHOOK_ID=%s\n' "$ppi"
                printf 'PAYPAL_WEBHOOK_SECRET=%s\n' "$pps"
                printf 'COINBASE_WEBHOOK_SECRET=%s\n' "$cbs"
                ;;
            grafana-admin-password)
                # Grafana's web admin credential. Held in ao-admin only; the
                # non-secret settings live in config/platform/monitoring/
                # grafana-admin.env so this file carries the password alone.
                val=$(fetch_secret "grafana-admin-password")
                printf 'GF_SECURITY_ADMIN_PASSWORD=%s\n' "$val"
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
