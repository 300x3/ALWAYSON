#!/usr/bin/env bash
# ALWAYS ON - privileged post-deploy steps for the ao-admin plane (WORK 000020
# follow-through). Run ONCE with operator authorization:
#   pkexec bash /ALWAYSON/quadlet/operations/pkexec-post-deploy.sh
#
# Everything unprivileged (image pulls, Quadlet units, rootless startup) is
# done WITHOUT this script. This script performs ONLY steps that require
# root: system-store container recovery and read-only reporting-role creation.
#
# Idempotent: safe to re-run. Logs to /ALWAYSON/logs/operations/pkexec-post-deploy.log.
set -u
LOG=/ALWAYSON/logs/operations/pkexec-post-deploy.log
exec > >(tee -a "$LOG") 2>&1
printf '===== %s : pkexec-post-deploy =====\n' "$(date --iso-8601=seconds)"

step() { printf '\n--- %s ---\n' "$1"; }

step '1. System-store container inventory (non-destructive)'
sudo -n true 2>/dev/null || true
SYSTEM_CONTAINERS=$(podman --store-storage 2>/dev/null ps -a --format '{{.Names}} {{.Status}}' || true)
# Fall back: if this script was launched via pkexec, podman here IS root.
system_podman() { if [ "$(id -u)" -eq 0 ]; then podman "$@"; else echo 'NOT ROOT'; fi; }
system_podman ps -a --format '{{.Names}}\t{{.Image}}\t{{.Status}}'

step '2. Restart WebODM/NodeODM system-store stack (mapping operator workflow)'
for c in ao-webodm-db ao-webodm-broker ao-webodm-worker ao-nodeodm ao-webodm-web; do
  CID=$(system_podman ps -a --format '{{.Names}}' | grep -x "$c" || true)
  if [ -n "$CID" ]; then
    state=$(system_podman ps --format '{{.Names}}' | grep -x "$c" || true)
    if [ -z "$state" ]; then system_podman start "$c" && echo "started $c" || echo "FAILED to start $c";
    else echo "$c already running"; fi
  else
    echo "$c not present in system store (skipped)"
  fi
done

step '3. PostgreSQL 18 read-only reporting role for Metabase (Section 15.1/6.A.2)'
# Creates role metaread (login, read-only) and grants SELECT on the salesdb
# public schema IF the sales database exists in the host cluster.
# idempotent: skipped if role already exists.
if sudo -n -u postgres psql -Atqc "SELECT 1 FROM pg_roles WHERE rolname='metaread'" 2>/dev/null | grep -q 1; then
  echo 'role metaread already exists (skipped)'
else
  MPASS=$(openssl rand -base64 18 | tr -d '/+=')
  sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL || echo 'ROLE CREATION FAILED (review log)'
CREATE ROLE metaread LOGIN PASSWORD '$MPASS';
SQL
  # store the password host-only for the operator to wire into Metabase
  umask 077; printf 'metaread password: %s\n' "$MPASS" > /ALWAYSON/secrets/metaread.credential 2>/dev/null || {
    mkdir -p /ALWAYSON/secrets; printf 'metaread password: %s\n' "$MPASS" > /ALWAYSON/secrets/metaread.credential; }
  chmod 600 /ALWAYSON/secrets/metaread.credential 2>/dev/null || true
  echo 'metaread password written to /ALWAYSON/secrets/metaread.credential (0600)'
fi
for DB in salesdb salesdb_production $(sudo -u postgres psql -Atqc "SELECT datname FROM pg_database WHERE datistemplate=false" 2>/dev/null | grep -i sales); do
  if sudo -u postgres psql -Atqc "SELECT 1 FROM pg_database WHERE datname='$DB'" 2>/dev/null | grep -q 1; then
    sudo -u postgres psql -d "$DB" -v ON_ERROR_STOP=1 <<SQL || echo "grant failed on $DB"
GRANT CONNECT ON DATABASE "$DB" TO metaread;
GRANT USAGE ON SCHEMA public TO metaread;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO metaread;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO metaread;
SQL
    echo "read-only grants applied on $DB"
  fi
done

step '4. Listener and firewall verification (no changes unless a violation exists)'
ss -tlnp | grep -v '127.0.0.1\|::1\|127.0.0.53\|127.0.0.54' || echo 'no non-loopback TCP listeners'
ufw status verbose | head -15 || true

step '5. Summary'
echo 'Privileged steps complete. Rootless ao-admin plane status:'
systemctl --user is-active ao-prometheus.service ao-node-exporter.service ao-grafana.service ao-metabase.service 2>/dev/null || true
printf '===== done =====\n'
