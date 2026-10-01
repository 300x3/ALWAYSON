#!/usr/bin/env bash
# ALWAYS ON - idempotently create the reporting application databases and
# least-privilege owners. Run as root; credentials are read from KDE Wallet,
# which is the sole secret authority (README 4.1 rule 7 / 14.1.1).
set -Eeuo pipefail
SECRETS=/ALWAYSON/secrets/reporting
HBA=/etc/postgresql/18/main/pg_hba.conf
WALLET_HELPER=/ALWAYSON/scripts/ops/wallet-read-secret.py
umask 077
# The reporting containers share only PostgreSQL's Unix socket directory.
# Add role-specific SCRAM rules rather than enabling passwordless local access.
# Host rules are scoped to loopback. They previously covered 10.42.0.0/16,
# which authorised the socat bridge that published this cluster on the eno1
# physical NIC; that bridge was removed 2026-09-25, so the LAN range was
# dropped and only loopback remains.
for rule in \
  'local metabase metabase_app scram-sha-256' \
  'local grafana grafana_app scram-sha-256' \
  'host metabase metabase_app 127.0.0.1/32 scram-sha-256' \
  'host grafana grafana_app 127.0.0.1/32 scram-sha-256' \
  'host metabase metabase_app ::1/128 scram-sha-256' \
  'host grafana grafana_app ::1/128 scram-sha-256'; do
  if ! grep -Fqx "$rule" "$HBA"; then
    printf '%s\n' "$rule" >>"$HBA"
  fi
done
wallet_pass() {
  "$WALLET_HELPER" kdewallet ao-admin "$1" 2>/dev/null
}
META_PASS="$(wallet_pass metabase-db-password)"
GRAF_PASS="$(wallet_pass grafana-db-password)"
[[ -n "$META_PASS" && -n "$GRAF_PASS" ]] || { echo 'missing reporting database credentials in KDE Wallet ao-admin' >&2; exit 2; }
# Superseded plaintext copies from before the wallet migration; never read.
rm -f "$SECRETS/metabase.env" "$SECRETS/grafana-postgres.env"
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
