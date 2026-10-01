#!/usr/bin/env bash
# ao-sim-portal: domain HTML portal control surface for ao-sim-fabrication
# (README §10.2 line 2037: start, stop, reset, inspect the world; operates
# the simulation only — never a path to live machinery per §4.3).
# Loopback-only. No secrets. Podman/Quadlet only.
set -euo pipefail
ACTION="${1:-status}"
UNIT="ao-sim-fabrication-gz.service"
case "$ACTION" in
  start)   systemctl --user start "$UNIT" ;;
  stop)    systemctl --user stop "$UNIT" ;;
  reset)   systemctl --user restart "$UNIT" ;;
  inspect) systemctl --user status "$UNIT" --no-pager | head -20
           echo "--- world ---"
           ls -l /ALWAYSON/data/sim-fabrication/worlds/ ;;
  status)  systemctl --user is-active "$UNIT" || true ;;
  *) echo "usage: $0 {start|stop|reset|inspect|status}" >&2; exit 2 ;;
esac
