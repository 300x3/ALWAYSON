#!/usr/bin/env bash
# ALWAYS ON - kwallet-provision.sh
# Manage secrets in the operator KDE Wallet (kwalletd6) per Section 14.1.1 /
# docs/runbooks/secrets.md. Run THIS FROM THE INTERACTIVE PLASMA SESSION
# (the wallet must be unlocked; normally auto-unlocks with your login).
#
# Usage:
#   kwallet-provision.sh create-folders
#   kwallet-provision.sh put <wallet> <folder> <key> <value>
#   kwallet-provision.sh get <wallet> <folder> <key>
#   kwallet-provision.sh list <wallet>            # show folders
#
# Uses gdbus against org.kde.kwalletd6 (correct for this host).
set -u
BUS=org.kde.kwalletd6
OBJ=/modules/kwalletd6
APP=alwayson-ops

G() { gdbus call --session --dest "$BUS" --object-path "$OBJ" --method "$@"; }

open_wallet_handle() {
  local wallet="$1" out handle
  out="$(G org.kde.KWallet.open "$wallet" 0 "$APP")" || return 1
  # gdbus returns e.g. '(0,)' with the handle as first int32 of a tuple.
  handle="$(printf '%s' "$out" | tr -d '()' | cut -d, -f1 | tr -dc '0-9-')"
  if [ -z "$handle" ] || [ "$handle" -lt 0 ]; then
    echo "ERROR: could not open wallet '$wallet' (locked?) => $out" >&2
    return 1
  fi
  printf '%s' "$handle"
}

create_folder() {
  local handle="$1" folder="$2"
  G org.kde.KWallet.createFolder "$handle" "$folder" "$APP" 2>&1
}

put() {
  # put <wallet> <folder> <key> <value>
  local wallet="$1" folder="$2" key="$3" value="$4" h has
  h="$(open_wallet_handle "$wallet")" || return 1
  has="$(G org.kde.KWallet.hasFolder "$wallet" "$folder" 2>/dev/null || echo '(false,)' )"
  has="$(printf '%s' "$has" | tr -dc 'truefalse')"
  if [ "$has" != "true" ]; then
    G org.kde.KWallet.createFolder "$h" "$folder" "$APP" >/dev/null 2>&1
  fi
  # writePassword(handle i, folder s, key s, value s, appid s)
  G org.kde.KWallet.writePassword "$h" "$folder" "$key" "$value" "$APP" 2>&1
}

get() {
  local wallet="$1" folder="$2" key="$3" h
  h="$(open_wallet_handle "$wallet")" || return 1
  G org.kde.KWallet.hasEntry "$h" "$folder" "$key" "$APP" 2>&1 | tr -d '\n'
  printf '  '
  G org.kde.KWallet.readPassword "$h" "$folder" "$key" "$APP" 2>&1
}

create_folders() {
  local handle
  handle="$(open_wallet_handle "${1:-kdewallet}")" || return 1
  for f in ao-mastodon ao-sales ao-payment ao-field ao-mapping ao-ledger ao-archive ao-admin ao-sim-vehicle ao-sim-fabrication; do
    echo "  createFolder $f: $(create_folder "$handle" "$f")"
  done
}

case "${1:-}" in
  create-folders) create_folders "${2:-kdewallet}" ;;
  put) put "${2:-kdewallet}" "$3" "$4" "$5" ;;
  get) get "${2:-kdewallet}" "$3" "$4" ;;
  *) echo "usage (see top)"; exit 2 ;;
esac