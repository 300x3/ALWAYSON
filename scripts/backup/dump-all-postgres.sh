#!/usr/bin/env bash
# ALWAYS ON - backup/dump-all-postgres.sh: dump all consolidated databases
# directly from Host PostgreSQL 18.6 using dedicated application roles.
# Tolerant: one failed dump does not abort the others. Intended for the
# ao-db-dump user timer (daily 03:00) and manual runs.
set -u
H=/ALWAYSON/scripts/backup/backup-host-postgres.sh
# Container-scoped databases are NOT on the host cluster and need a podman-exec dump.
C=/ALWAYSON/scripts/backup/backup-container-postgres.sh
LOG=/ALWAYSON/logs/backup/db-dump.log
mkdir -p "$(dirname "$LOG")"
fail=0
{
  echo "===== $(date --iso-8601=seconds) db dump start ====="
  # mastodon and webodm live in their own containers; the host dump cannot see them.
  bash "$C" mastodon mastodon-db mastodon mastodon || { echo "FAIL: mastodon"; fail=1; }
  bash "$H" sales salesdb sales_migration_role || { echo "FAIL: salesdb"; fail=1; }
  bash "$C" mapping ao-webodm-db webodm_dev postgres || { echo "FAIL: webodm"; fail=1; }
  bash "$H" metabase metabase metabase_app || { echo "FAIL: metabase"; fail=1; }
  bash "$H" grafana grafana grafana_app || { echo "FAIL: grafana"; fail=1; }
  echo "===== $(date --iso-8601=seconds) db dump end (fail=$fail) ====="
} >> "$LOG" 2>&1
tail -15 "$LOG"
exit $fail
