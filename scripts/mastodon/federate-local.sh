#!/usr/bin/env bash
# ALWAYS ON - configure controlled Mastodon federation and follow a remote account.
# Run as: pkexec /ALWAYSON/scripts/mastodon/federate-local.sh [acct]
set -Eeuo pipefail
# pkexec starts in /root; rootless service-account tools require an accessible cwd.
cd /tmp


REMOTE_ACCT="${1:-300x3@mastodon.social}"
SALES_USER=ao-sales
SALES_UID=$(id -u "$SALES_USER")
SALES_HOME=/home/ao-sales
SALES_RUNTIME=/run/user/${SALES_UID}
DBUS="unix:path=${SALES_RUNTIME}/bus"
SOURCE_ROOT=/ALWAYSON
DEPLOYED_ROOT=/home/scottw/.config/containers/systemd

as_sales() {
  runuser -u "$SALES_USER" -- env \
    HOME="$SALES_HOME" XDG_RUNTIME_DIR="$SALES_RUNTIME" \
    DBUS_SESSION_BUS_ADDRESS="$DBUS" "$@"
}

systemctl_sales() {
  as_sales systemctl --user "$@"
}

[[ $EUID -eq 0 ]] || { echo 'Run with pkexec.' >&2; exit 1; }
[[ "$REMOTE_ACCT" =~ ^[A-Za-z0-9_]+@[A-Za-z0-9.-]+$ ]] || {
  echo "Invalid account: $REMOTE_ACCT" >&2; exit 2;
}

# The deployed Quadlet source is the runtime source of truth on this host.
# ao-egress-community was retired 2026-09-30: ao-sales itself is now
# Internal=false and carries the outbound route, so there is no second
# network to install, create, or attach here any more.
install -m 0644 "$SOURCE_ROOT/quadlet/networks/ao-sales.network" \
  "$DEPLOYED_ROOT/ao-sales.network"

systemctl_sales daemon-reload
systemctl_sales restart ao-sales-network.service
systemctl_sales restart ao-mastodon-web.service ao-mastodon-sidekiq.service
sleep 8

# The generator is host-account scoped; re-attach the containers to ao-sales so
# the service account keeps the outbound route after any network recreation.
as_sales podman network connect ao-sales mastodon-web    >/dev/null 2>&1 || true
as_sales podman network connect ao-sales mastodon-sidekiq >/dev/null 2>&1 || true

# The host has IPv4 Internet but no IPv6 route. Force Ruby HTTP to prefer IPv4.
as_sales podman exec -u 0 mastodon-web sh -lc '
  grep -q "^precedence ::ffff:0:0/96 100$" /etc/gai.conf ||
    printf "\\nprecedence ::ffff:0:0/96 100\\n" >> /etc/gai.conf
'

as_sales podman exec mastodon-web sh -lc \
  "curl -4 -fsS -o /dev/null --max-time 15 'https://mastodon.social/.well-known/webfinger?resource=acct:${REMOTE_ACCT}'"

# Resolve the remote ActivityPub actor and make the local admin account follow it.
as_sales podman exec mastodon-web bin/rails runner '
  remote = ARGV.fetch(0)
  source = Account.find(117170400040581488)
  target = ResolveAccountService.new.call(remote, suppress_errors: false)
  abort "Unable to resolve #{remote}" if target.nil?
  FollowService.new.call(source, target, bypass_limit: true)
  puts({ source: source.acct, target: target.acct,
         following: source.following?(target),
         requested: source.requested?(target) }.inspect)
' "$REMOTE_ACCT"

curl -fsS -o /dev/null --max-time 10 http://localhost:3000/home
echo "Federation follow configured: ${REMOTE_ACCT}"
