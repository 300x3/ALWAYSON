#!/usr/bin/env bash
# ALWAYS ON podman socket bridge v2.1 — replaces /usr/local/sbin/ao-podman-bridge.sh
# History:
#   v1: one-shot at boot; lost the race against lingered users' podman.socket,
#       bridged nothing, slept forever (2026-08-26 reboot incident).
#   v2: added retry loop BUT health-checked with pgrep -f '"..."' whose literal
#       quote chars never matched the socat cmdline -> needless churn/spawn leak.
#   v2.1: PID-file health checks. Healthy = recorded PID alive AND socket file
#         present. Stale/legacy instances are cleaned via anchored pkill.
set -u
BRIDGE_DIR=/run/ao-podman
RETRY_SECS=15

mkdir -p "$BRIDGE_DIR"
chmod 0755 "$BRIDGE_DIR"

bridge() {
  local name="$1" from="$2"
  local to="$BRIDGE_DIR/$name.sock" pidfile="$BRIDGE_DIR/$name.pid" pid=""
  [ -r "$pidfile" ] && pid=$(cat "$pidfile")

  # Healthy if our recorded socat is alive and its listening socket exists.
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null && [ -S "$to" ]; then
    return
  fi

  # Tear down stale instance(s): recorded PID plus any legacy anchor-matched socat.
  [ -n "$pid" ] && kill "$pid" 2>/dev/null
  pkill -f "^socat .*ao-podman/${name}\\.sock" 2>/dev/null
  rm -f "$pidfile" "$to"

  if [ ! -S "$from" ]; then
    echo "$(date --iso-8601=seconds) $name: waiting-for-src ($from)"
    return
  fi

  nohup socat UNIX-LISTEN:"$to",fork,reuseaddr,mode=0660,user=scottw,group=scottw \
        UNIX-CONNECT:"$from" >/dev/null 2>&1 &
  echo $! > "$pidfile"
  echo "$(date --iso-8601=seconds) $name: bridge_up pid=$!"
}

declare -A SOURCES=(
  [mapping]=/run/user/997/podman/podman.sock
  [sales]="/run/user/993/podman/podman.sock"
  [ledger]=/run/user/994/podman/podman.sock
)

echo "$(date --iso-8601=seconds) ao-podman-bridge v2.1 starting"
while true; do
  for name in mapping sales ledger; do
    bridge "$name" "${SOURCES[$name]}"
  done
  sleep "$RETRY_SECS"
done

