#!/usr/bin/env bash
# ALWAYS ON podman socket bridge v2.1 — replaces /usr/local/sbin/ao-podman-bridge.sh
# History:
#   v1: one-shot at boot; lost the race against lingered users' podman.socket,
#       bridged nothing, slept forever (2026-08-26 reboot incident).
#   v2: added retry loop BUT health-checked with pgrep -f '"..."' whose literal
#       quote chars never matched the socat cmdline -> needless churn/spawn leak.
#   v2.1: PID-file health checks. Healthy = recorded PID alive AND socket file
#         present. Stale/legacy instances are cleaned via anchored pkill.
#   v2.2: v2.1 checked only that the socat was alive, never that the SOURCE
#         podman.socket actually answered. After 2026-09-24 the
#         alwayson-sales and alwayson-ledger podman.socket units sat in
#         trigger-limit-hit, so their socats stayed "healthy" while bridging
#         to a dead backend -> sales.sock/ledger.sock EOF on every request.
#         That silently broke the nightly mastodon DB backup. v2.2 adds an
#         end-to-end _ping against the source socket, and resets+starts a
#         failed source podman.socket so the bridge self-heals after reboot.
set -u
BRIDGE_DIR=/run/ao-podman
RETRY_SECS=15

mkdir -p "$BRIDGE_DIR"
chmod 0755 "$BRIDGE_DIR"

bridge() {
  local name="$1" from="$2" machine="${3:-}"
  local to="$BRIDGE_DIR/$name.sock" pidfile="$BRIDGE_DIR/$name.pid" pid=""
  [ -r "$pidfile" ] && pid=$(cat "$pidfile")

  # Healthy only if the socat is alive, its socket exists, AND the source
  # podman backend actually answers. v2.1 stopped at the first two checks.
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null && [ -S "$to" ] && [ -S "$from" ] \
     && curl -s --max-time 3 --unix-socket "$from" http://d/v1.0.0/libpod/_ping 2>/dev/null | grep -q OK; then
    return
  fi

  # Source socket exists but is not answering (typically systemd
  # trigger-limit-hit on podman.socket). Clear the failed state and retry so
  # the bridge recovers on its own instead of needing a manual restart.
  if [ -S "$from" ] && [ -n "${machine:-}" ]; then
    systemctl --user --machine="${machine}@" reset-failed podman.socket podman.service >/dev/null 2>&1
    systemctl --user --machine="${machine}@" start podman.socket >/dev/null 2>&1
    echo "$(date --iso-8601=seconds) $name: reset source podman.socket (${machine})"
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

# Service account that owns each source socket, used to reset a failed
# podman.socket via `systemctl --user --machine=<user>@`.
declare -A OWNERS=(
  [mapping]=alwayson-mapping
  [sales]=alwayson-sales
  [ledger]=alwayson-ledger
)

echo "$(date --iso-8601=seconds) ao-podman-bridge v2.2 starting"
while true; do
  for name in mapping sales ledger; do
    bridge "$name" "${SOURCES[$name]}" "${OWNERS[$name]}"
  done
  sleep "$RETRY_SECS"
done

