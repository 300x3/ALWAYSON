#!/usr/bin/env bash
# ALWAYS ON podman socket bridge v2 — replaces /usr/local/sbin/ao-podman-bridge.sh
# Fixes boot race (2026-08-26 review Finding 1): the original one-shot script ran
# before lingered users' podman.socket existed, bridged nothing, then slept forever.
# v2 continuously reconciles: waits for source sockets, (re)starts socat when the
# destination socket is absent/stale, and retries every RETRY_SECS.
set -u
BRIDGE_DIR=/run/ao-podman
RETRY_SECS=15

mkdir -p "$BRIDGE_DIR"
chmod 0755 "$BRIDGE_DIR"

bridge() {
  local name="$1" from="$2" to="$BRIDGE_DIR/${name}.sock"
  if [ ! -S "$from" ]; then
    if [ -S "$to" ] || pgrep -f "UNIX-LISTEN:\"$to\"" >/dev/null 2>&1; then
      pkill -f "UNIX-LISTEN:\"$to\"" 2>/dev/null && rm -f "$to"
      echo "$(date --iso-8601=seconds) $name: torn_down_src_missing"
    fi
    return
  fi
  if [ -S "$to" ] && pgrep -f "UNIX-LISTEN:\"$to\"" >/dev/null 2>&1; then
    return  # healthy, nothing to do
  fi
  pkill -f "UNIX-LISTEN:\"$to\"" 2>/dev/null || true
  rm -f "$to"
  nohup socat UNIX-LISTEN:"$to",fork,reuseaddr,mode=0660,user=scottw,group=scottw \
        UNIX-CONNECT:"$from" >/dev/null 2>&1 &
  echo "$(date --iso-8601=seconds) $name: bridge_up"
}

declare -A SOURCES=(
  [mapping]=/run/user/997/podman/podman.sock
  [sales]="/run/user/993/podman/podman.sock"
  [ledger]=/run/user/994/podman/podman.sock
)

echo "$(date --iso-8601=seconds) ao-podman-bridge v2 starting"
while true; do
  for name in mapping sales ledger; do
    bridge "$name" "${SOURCES[$name]}"
  done
  sleep "$RETRY_SECS"
done
