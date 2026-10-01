#!/usr/bin/env bash
# ALWAYS ON - start sales stack as ao-sales (called via sudo NOPASSWD).
# No secrets here. Bridge materializes env files first; this only starts units.
# Approved 2026-09-29: scottw is sole operator with sudo; narrow start-only helper.
set -Eeuo pipefail
UID993_RUNTIME=/run/user/993
export XDG_RUNTIME_DIR=$UID993_RUNTIME
export DBUS_SESSION_BUS_ADDRESS=unix:path=$UID993_RUNTIME/bus
runuser -u ao-sales -- systemctl --user start ao-mastodon-db.service ao-mastodon-redis.service
runuser -u ao-sales -- systemctl --user start ao-mastodon-web.service ao-mastodon-sidekiq.service ao-mastodon-streaming.service ao-sales-db.service
echo "SALES STACK START REQUESTED"