#!/usr/bin/env bash
# ALWAYS ON - launcher for the Gazebo Sim 10 GUI client (README 10.1.2/10.2.1).
#
# Runs INSIDE the ao-sim-fabrication-gui-gz container, which shares the server's
# network namespace. It attaches to the world the server is already running;
# it never starts a second one.
#
# Its only real job is to find the Xauthority cookie. The host runs Plasma on
# Wayland with XWayland, and Xwayland creates a per-session file named
# /run/user/<uid>/xauth_XXXXXX whose suffix changes every login. Hardcoding that
# name in the unit would break the GUI at the next login, so it is resolved
# here against the mounted /run/user/1000 instead.
set -Eeuo pipefail

rundir="${XDG_RUNTIME_DIR:-/run/user/1000}"
auth=""
for f in "$rundir"/xauth_*; do
  [ -f "$f" ] || continue
  # Newest wins: the current session's file has the most recent mtime.
  if [ -z "$auth" ] || [ "$f" -nt "$auth" ]; then auth="$f"; fi
done

if [ -n "$auth" ]; then
  export XAUTHORITY="$auth"
  echo "[ao-sim-gui] using XAUTHORITY=$auth"
else
  echo "[ao-sim-gui] WARNING: no xauth_* file under $rundir; the X11 connection will fail" >&2
fi

# GZ_PARTITION must match ao-sim-fabrication-gz or the client discovers no
# world and silently shows an empty scene.
export GZ_PARTITION="${GZ_PARTITION:-alwayson_fabrication_sim}"
# GZ_IP must match the server for the same reason: both containers share one
# network namespace, and gz-transport will not complete discovery if the
# client advertises a different address than the server.
export GZ_IP="${GZ_IP:-127.0.0.1}"
echo "[ao-sim-gui] attaching to partition $GZ_PARTITION (ip $GZ_IP)"

# Allow a core dump so the "construction from null" abort is diagnosable from
# the stack instead of by guesswork. The host core_pattern pipes to
# systemd-coredump; the traceback is then readable with coredumpctl.
ulimit -c unlimited 2>/dev/null || true

exec /usr/libexec/gz/sim10/gz-sim-gui-client -v "${GZ_VERBOSITY:-3}"
