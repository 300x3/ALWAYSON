-- ALWAYS ON read-only reporting identity grants (Section 6.A.2).
--
-- metaread is the single least-privilege reporting identity. It owns no
-- database and holds SELECT only. Nothing here grants write, DDL, ownership,
-- superuser, migration, backup, payment-provider or Corda-key access.
--
-- Run as the postgres superuser with the password bound:
--   psql -v ON_ERROR_STOP=1 --set=pw="$PW" -f metaread-grants.sql
--
-- Idempotent.

ALTER ROLE metaread PASSWORD :'pw';

\connect cordadb
GRANT CONNECT ON DATABASE cordadb TO metaread;
GRANT USAGE ON SCHEMA public TO metaread;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO metaread;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO metaread;

\connect modeldb
GRANT CONNECT ON DATABASE modeldb TO metaread;
GRANT USAGE ON SCHEMA public TO metaread;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO metaread;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO metaread;

\connect reporting
GRANT CONNECT ON DATABASE reporting TO metaread;
GRANT USAGE ON SCHEMA reporting_sales TO metaread;
GRANT SELECT ON ALL TABLES IN SCHEMA reporting_sales TO metaread;
ALTER DEFAULT PRIVILEGES IN SCHEMA reporting_sales GRANT SELECT ON TABLES TO metaread;

\connect postgres
\echo '--- metaread effective access ---'
SELECT datname,
       has_database_privilege('metaread', datname, 'CONNECT') AS can_connect
FROM pg_database
WHERE datname IN ('cordadb','modeldb','reporting','grafana','metabase','postgres')
ORDER BY datname;
