#!/usr/bin/env bash
# ALWAYS ON - Materialize reporting PostgreSQL env from KDE Wallet.
# Usage: fetch-reporting-env.sh <metabase|grafana> <output-env-file>
# Static connection settings remain in repository-adjacent config; only the
# database password is taken from KDE Wallet.
#
# DB_HOST is the host PostgreSQL UNIX socket directory, not a TCP address.
# The ao-grafana/ao-metabase quadlets bind-mount /var/run/postgresql
# read-only, so reporting reaches PostgreSQL with no network listener at all.
# The previous 10.42.0.1 TCP bridge published the host cluster on the eno1
# physical NIC and required a `host ... 10.42.0.0/16` pg_hba.conf rule; both
# were removed 2026-09-25.
set -Eeuo pipefail
IFS=$'\n\t'
DB_HOST=/var/run/postgresql
ROLE="${1:?usage: fetch-reporting-env.sh <metabase|grafana> <output-env-file>}"
OUTPUT="${2:?usage: fetch-reporting-env.sh <metabase|grafana> <output-env-file>}"
WALLET_HELPER=/ALWAYSON/scripts/ops/wallet-read-secret.py
umask 077

# 2026-10-01: this script had NO wait for the wallet to be unlocked. It read
# KWallet immediately, so at login it raced kwalletd and returned 3
# ("KDE Wallet entry unavailable"), which failed the ExecStartPre and left
# ao-metabase down -- the same class of fault as the ao-grafana outage fixed in
# fetch-kwallet-secret.sh the same day. Both scripts must tolerate the gap
# between kwalletd APPEARING on the session bus and the wallet being OPEN.
#
# isOpen(handle) is the real readiness question. KWallet also declares an
# isOpen(wallet, app) overload; dbus-python binds the proxy to the last declared
# signature, so the app-name form raises TypeError. Use the one-argument form.
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

# Wait up to ~60s for the wallet to actually be open.
for _i in $(seq 1 30); do
    kwallet_ready && break
    sleep 2
done
if ! kwallet_ready; then
    echo "ERROR: KDE Wallet not unlocked on the session bus after 60s" >&2
    exit 3
fi

case "$ROLE" in
  metabase)
    folder=ao-admin
    entry=metabase-db-password
    password="$("$WALLET_HELPER" kdewallet "$folder" "$entry")"
    [[ -n "$password" ]] || { echo "ERROR: KDE Wallet entry unavailable: $folder/$entry" >&2; exit 3; }
    {
      printf 'MB_DB_TYPE=postgres\n'
      # Metabase's pgjdbc driver cannot use the host UNIX socket here:
      #   - MB_DB_HOST=/var/run/postgresql -> "JDBC URL contains too many /"
      #   - MB_DB_CONNECTION_URI ?host=   -> Metabase strips the query, pgjdbc
      #     then reports "protocol = socket host = null"
      #   - PGHOST + MB_DB_HOST=localhost  -> the URL host wins, TCP to
      #     localhost:5432 is refused inside the container netns
      # So Metabase keeps a TCP path. It is NOT reachable from the LAN: the
      # `host ... 10.42.0.0/16` pg_hba.conf rules that authorised this were
      # removed 2026-09-25, so no role can authenticate over the bridge even
      # though the listener exists. Grafana uses the socket path instead.
      printf 'MB_DB_HOST=10.42.0.1\n'
      printf 'MB_DB_PORT=5432\n'
      printf 'MB_DB_DBNAME=metabase\n'
      printf 'MB_DB_USER=metabase_app\n'
      printf 'MB_DB_SSL=false\n'
      printf 'MB_DB_PASS=%s\n' "$password"
    } >"$OUTPUT.tmp"
    ;;
  grafana)
    folder=ao-admin
    entry=grafana-db-password
    password="$("$WALLET_HELPER" kdewallet "$folder" "$entry")"
    [[ -n "$password" ]] || { echo "ERROR: KDE Wallet entry unavailable: $folder/$entry" >&2; exit 3; }
    {
      printf 'GF_DATABASE_TYPE=postgres\n'
      printf 'GF_DATABASE_HOST=%s\n' "$DB_HOST"
      printf 'GF_DATABASE_PORT=5432\n'
      printf 'GF_DATABASE_NAME=grafana\n'
      printf 'GF_DATABASE_USER=grafana_app\n'
      printf 'GF_DATABASE_SSL_MODE=disable\n'
      printf 'GF_PATHS_DATA=/var/lib/grafana-postgres\n'
      printf 'GF_DATABASE_PASSWORD=%s\n' "$password"
    } >"$OUTPUT.tmp"
    ;;
  *)
    echo "ERROR: unknown reporting role: $ROLE" >&2
    exit 2
    ;;
esac
mv "$OUTPUT.tmp" "$OUTPUT"
chmod 0600 "$OUTPUT"
echo "OK: wallet-backed reporting env materialized for $ROLE"
