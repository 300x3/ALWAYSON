-- ALWAYS ON reporting hub (Section 6.A.2, Section 11.2 precondition 3).
--
-- The ao-admin reporting tools keep exactly one connection to the host cluster.
-- Cross-boundary data is pulled IN to this hub as foreign tables, so the
-- reporting containers never join ao-sales/ao-mapping/ao-field and the source
-- databases never publish anything beyond a loopback-only port.
--
-- Run as the postgres superuser with the reporting password bound:
--   psql -v ON_ERROR_STOP=1 --set=pw="$PW" -f reporting-hub.sql
--
-- Idempotent: the server and schema are dropped and rebuilt each run.

SELECT 'CREATE DATABASE reporting OWNER metaread'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='reporting')\gexec

\connect reporting

CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- salesdb lives in the ao-sales container network. It is reachable only on the
-- host loopback via its loopback-only published port (see ao-sales-db.container).
DROP SERVER IF EXISTS salesdb_srv CASCADE;
CREATE SERVER salesdb_srv FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host '127.0.0.1', port '15432', dbname 'salesdb', sslmode 'disable');

-- The hub authenticates to the source as the read-only reporting role, which
-- can only see the approved views. Nothing else on salesdb is reachable.
-- The postgres mapping exists only so IMPORT FOREIGN SCHEMA (run as superuser)
-- can introspect the remote; it grants no privilege on the host side.
CREATE USER MAPPING FOR metaread SERVER salesdb_srv
  OPTIONS (user 'sales_reporting_role', password :'pw');
CREATE USER MAPPING FOR postgres SERVER salesdb_srv
  OPTIONS (user 'sales_reporting_role', password :'pw');

DROP SCHEMA IF EXISTS reporting_sales CASCADE;
CREATE SCHEMA reporting_sales;

IMPORT FOREIGN SCHEMA public
  LIMIT TO (v_corda_entry_readiness,
            v_reporting_orders,
            v_reporting_entitlements,
            v_reporting_receipts,
            v_reporting_sale_provenance)
  FROM SERVER salesdb_srv INTO reporting_sales;

REVOKE ALL ON SCHEMA reporting_sales FROM PUBLIC;
GRANT USAGE ON SCHEMA reporting_sales TO metaread;
GRANT SELECT ON ALL TABLES IN SCHEMA reporting_sales TO metaread;

REVOKE ALL ON DATABASE reporting FROM PUBLIC;
GRANT CONNECT ON DATABASE reporting TO metaread;

\det reporting_sales.*
