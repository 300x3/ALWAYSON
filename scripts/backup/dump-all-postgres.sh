#!/usr/bin/env bash
# ALWAYS ON - backup/dump-all-postgres.sh: dump all running domain PostgreSQL
# containers (mastodon-db, sales-db, webodm db) to /ALWAYSON/backups/postgres/.
# Tolerant: one failed dump does not abort the others. Intended for the
# alwayson-db-dump user timer (daily 03:00) and manual runs.
set -u
B=/ALWAYSON/scripts/backup/backup-postgres.sh
LOG=/ALWAYSON/logs/backup/db-dump.log
mkdir -p "$(dirname "$LOG")"
fail=0
{
  echo "===== $(date --iso-8601=seconds) db dump start ====="
  PODMAN_URL=unix:///run/ao-podman/sales.sock bash "$B" mastodon-db mastodon mastodon || { echo "FAIL: mastodon-db"; fail=1; }
  bash "$B" sales-db salesdb sales "" sales_migration_role || { echo "FAIL: sales-db"; fail=1; }
  bash "$B" db webodm webodm "" postgres || { echo "FAIL: webodm-db"; fail=1; }
  echo "===== $(date --iso-8601=seconds) db dump end (fail=$fail) ====="
} >> "$LOG" 2>&1
tail -12 "$LOG"
exit $fail
