#!/usr/bin/env bash
# ALWAYS ON - idempotently create the reporting application databases and
# least-privilege owners. Run as root; credentials are read from 0600 files.
set -Eeuo pipefail
SECRETS=/ALWAYSON/secrets/reporting
HBA=/etc/postgresql/18/main/pg_hba.conf
umask 077
# The reporting containers share only PostgreSQL's Unix socket directory.
# Add role-specific SCRAM rules rather than enabling passwordless local access.
for rule in \
  'local metabase metabase_app scram-sha-256' \
  'local grafana grafana_app scram-sha-256' \
  'host metabase metabase_app 10.42.0.0/16 scram-sha-256' \
  'host grafana grafana_app 10.42.0.0/16 scram-sha-256'; do
  if ! grep -Fqx "$rule" "$HBA"; then
    printf '%s\n' "$rule" >>"$HBA"
  fi
done
get_env() {
  local file=$1 key=$2
  sed -n "s/^${key}=//p" "$file" | tail -n1
}
META_PASS="$(get_env "$SECRETS/metabase.env" MB_DB_PASS)"
GRAF_PASS="$(get_env "$SECRETS/grafana-postgres.env" GF_DATABASE_PASSWORD)"
[[ -n "$META_PASS" && -n "$GRAF_PASS" ]] || { echo 'missing reporting database credentials' >&2; exit 2; }
runuser -u postgres -- psql -v ON_ERROR_STOP=1 --set=meta_pass="$META_PASS" --set=graf_pass="$GRAF_PASS" <<'SQL'
SELECT format('CREATE ROLE metabase_app LOGIN PASSWORD %L', :'meta_pass')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname='metabase_app') \gexec
SELECT format('CREATE ROLE grafana_app LOGIN PASSWORD %L', :'graf_pass')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname='grafana_app') \gexec
SELECT 'CREATE DATABASE metabase OWNER metabase_app'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='metabase') \gexec
SELECT 'CREATE DATABASE grafana OWNER grafana_app'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='grafana') \gexec
REVOKE ALL ON DATABASE metabase FROM PUBLIC;
REVOKE ALL ON DATABASE grafana FROM PUBLIC;
GRANT CONNECT,TEMPORARY ON DATABASE metabase TO metabase_app;
GRANT CONNECT,TEMPORARY ON DATABASE grafana TO grafana_app;
SQL
for spec in 'metabase metabase_app' 'grafana grafana_app'; do
  read -r db role <<<"$spec"
  runuser -u postgres -- psql -v ON_ERROR_STOP=1 -d "$db" <<SQL
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE,CREATE ON SCHEMA public TO $role;
ALTER SCHEMA public OWNER TO $role;
SQL
done
runuser -u postgres -- psql -v ON_ERROR_STOP=1 -c 'SELECT pg_reload_conf();'
