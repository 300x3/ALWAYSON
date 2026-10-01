#!/usr/bin/env bash
# ALWAYS ON - start the sales stack as the operator account (called via sudo NOPASSWD).
# No secrets here. Bridge materializes env files first; this only starts units.
# Approved 2026-09-29: scottw is sole operator with sudo; narrow start-only helper.
# 2026-09-30: Mastodon no longer runs under the retired alwayson-sales/ao-sales service
# account. Per README 15.4.1 / 20.0 the 5 Mastodon containers run in the scottw user
# manager, so they are started here as scottw too. Starting them as ao-sales would
# create a second, duplicate Mastodon store - exactly the duplication this cleanup
# removed. Sidekiq is included because it performs ActivityPub federation delivery.
set -Eeuo pipefail
systemctl --user start ao-mastodon-db.service ao-mastodon-redis.service
systemctl --user start ao-mastodon-web.service ao-mastodon-sidekiq.service \
  ao-mastodon-streaming.service ao-sales-db.service
echo "SALES STACK START REQUESTED"