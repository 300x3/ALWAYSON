#!/bin/bash
# ALWAYS ON - remove the duplicate Mastodon stack owned by the ao-sales service user.
#
# WHY: two Mastodon stacks were running. The live, serving one is owned by scottw
# (mastodon-web/streaming/db/redis/sidekiq, published on 127.0.0.1:3000 and reachable
# at http://127.0.0.1:3300/ via mastodon-local-proxy). A second, duplicate set
# (ao-mastodon-db, ao-mastodon-redis, ao-mastodon-sidekiq) was running as
# ao-sales (uid 993) with its own separate Postgres storage. It serves nothing,
# duplicates the database, and its units pull in wallet-backed ExecStartPre.
#
# SAFETY: refuses to run unless the scottw stack is confirmed healthy FIRST.
# Only ever touches the ao-sales user's units/containers. Never touches
# scottw's Mastodon, and never touches 993's other units (sales-db, grafana, ...).
#
# Run as root:  sudo bash /ALWAYSON/scripts/operations/remove-993-mastodon-duplicates.sh
# Re-run safely: it is idempotent.

set -uo pipefail

SALES_USER="ao-sales"
UNITS=(ao-mastodon-db.service ao-mastodon-redis.service ao-mastodon-sidekiq.service)
UNIT_FILES=(
  "$SALES_USER/.config/containers/systemd/sales/ao-mastodon-db.container"
  "$SALES_USER/.config/containers/systemd/sales/ao-mastodon-redis.container"
  "$SALES_USER/.config/containers/systemd/sales/ao-mastodon-sidekiq.container"
  "$SALES_USER/.config/containers/systemd/disabled/ao-mastodon-db.container"
  "$SALES_USER/.config/containers/systemd/disabled/ao-mastodon-redis.container"
  "$SALES_USER/.config/containers/systemd/disabled/ao-mastodon-sidekiq.container"
)
CONTAINERS=(mastodon-db mastodon-redis mastodon-sidekiq)

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }

if [[ $EUID -ne 0 ]]; then
  log "ABORT: must run as root (sudo)."
  exit 1
fi

# --- Gate: the stack we are keeping must be healthy before we touch anything ---
log "Pre-flight: verifying the scottw Mastodon stack is serving."
code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 http://127.0.0.1:3300/ 2>/dev/null || true)"
if [[ "$code" != "200" ]]; then
  log "ABORT: http://127.0.0.1:3300/ returned '$code' (expected 200). Not touching anything."
  exit 1
fi
for c in mastodon-web mastodon-db mastodon-redis; do
  if ! podman ps --format '{{.Names}}' 2>/dev/null | grep -qx "$c"; then
    log "ABORT: container '$c' is not running under scottw. Not touching anything."
    exit 1
  fi
done
log "Pre-flight OK: 127.0.0.1:3300 -> 200 and scottw containers present."

# --- Stop and disable the duplicate units ---
for u in "${UNITS[@]}"; do
  log "Stopping $u"
  runuser -u "$SALES_USER" -- \
    env XDG_RUNTIME_DIR="/run/user/$(id -u "$SALES_USER")" \
        DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u "$SALES_USER")/bus" \
    systemctl --user stop "$u" 2>/dev/null || log "  (not running or not present)"
done
for u in "${UNITS[@]}"; do
  log "Disabling $u"
  runuser -u "$SALES_USER" -- \
    env XDG_RUNTIME_DIR="/run/user/$(id -u "$SALES_USER")" \
        DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u "$SALES_USER")/bus" \
    systemctl --user disable "$u" 2>/dev/null || log "  (no enablement symlink)"
done

# --- Remove the duplicate containers (993's own podman storage only) ---
for c in "${CONTAINERS[@]}"; do
  log "Removing container $c (as $SALES_USER)"
  runuser -u "$SALES_USER" -- podman rm -f "$c" 2>/dev/null || log "  (absent)"
done

# --- Remove the unit files so the generator cannot recreate them ---
for f in "${UNIT_FILES[@]}"; do
  if [[ -e "/home/$f" ]]; then
    log "Removing unit file /home/$f"
    rm -f "/home/$f"
  fi
done

# --- Reload that user's generator ---
uid="$(id -u "$SALES_USER")"
runuser -u "$SALES_USER" -- \
  env XDG_RUNTIME_DIR="/run/user/$uid" DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$uid/bus" \
  systemctl --user daemon-reload 2>/dev/null || true

log "Remaining containers owned by $SALES_USER (should not list the three above):"
runuser -u "$SALES_USER" -- podman ps -a --format '{{.Names}} {{.Status}}' 2>/dev/null | grep -iE 'mastodon' || log "  (no mastodon containers)"
log "Post-check: scottw stack still serving -> $(curl -s -o /dev/null -w '%{http_code}' --max-time 10 http://127.0.0.1:3300/)"
log "DONE. The duplicate Postgres volume for $SALES_USER (if any) was intentionally left in place;"
log "remove it separately with: sudo podman --root ... volume ls   # only after confirming it is unused."
