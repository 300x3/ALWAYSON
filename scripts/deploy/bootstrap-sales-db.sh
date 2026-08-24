#!/usr/bin/env bash
# ALWAYS ON - apply Section 3.8 sales schema to a running sales-db container.
set -Eeuo pipefail
IFS=$'\n\t'
LOG=/ALWAYSON/logs/installation/agent-install.log
exec >>"$LOG" 2>&1
cd /
MU=alwayson-sales
export HOME=/home/$MU XDG_RUNTIME_DIR=/run/user/$(id -u $MU)
P() { runuser -u $MU -- env HOME=$HOME XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR podman "$@"; }
[[ -f /home/$MU/init/01-database.sql ]] || { echo "ERROR: schema sql missing" >&2; exit 10; }
P cp /home/$MU/init/01-database.sql sales-db:/tmp/
P exec sales-db psql -v ON_ERROR_STOP=1 -U sales_migration_role -d salesdb -f /tmp/01-database.sql
# sync API role password with provisioned secret
APIPASS=$(grep SALES_API_DB_PASSWORD /home/$MU/secrets/sales-db.env | cut -d= -f2)
P exec sales-db psql -U sales_migration_role -d salesdb -c "ALTER ROLE sales_api_role PASSWORD '$APIPASS'"
echo "SALES_SCHEMA_APPLIED"
