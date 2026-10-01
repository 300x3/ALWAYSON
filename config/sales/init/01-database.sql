-- ALWAYS ON sales database bootstrap (Section 3.8)
-- Runs once on first container init as postgres superuser.

-- Idempotent role creation (sales_migration_role may already exist via POSTGRES_USER)
DO $do$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='sales_api_role') THEN
    CREATE ROLE sales_api_role LOGIN;
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='sales_migration_role') THEN
    CREATE ROLE sales_migration_role LOGIN;
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='sales_backup_role') THEN
    CREATE ROLE sales_backup_role LOGIN;
  END IF;
  -- Section 15.1 names five roles. The read-only reporting role and the
  -- administrative role were missing from the original bootstrap; added
  -- 2026-09-25. sales_reporting_role is the identity Metabase/Grafana use,
  -- and it reaches only the approved reporting views (Section 6.A.2).
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='sales_reporting_role') THEN
    CREATE ROLE sales_reporting_role LOGIN;
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='sales_admin_role') THEN
    CREATE ROLE sales_admin_role LOGIN;
  END IF;
END $do$;

SELECT 'CREATE DATABASE salesdb OWNER sales_migration_role'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='salesdb')\gexec

\connect salesdb

CREATE TABLE customers (
  id          bigserial PRIMARY KEY,
  email       text NOT NULL UNIQUE,
  name        text NOT NULL,
  status      text NOT NULL DEFAULT 'active',
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE customer_contacts (
  id           bigserial PRIMARY KEY,
  customer_id  bigint NOT NULL REFERENCES customers(id),
  kind         text NOT NULL,           -- e.g. billing|shipping|support
  value        text NOT NULL,
  created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE products (
  sku         text PRIMARY KEY,
  name        text NOT NULL,
  description text,
  active      boolean NOT NULL DEFAULT true
);

CREATE TABLE product_versions (
  id                   bigserial PRIMARY KEY,
  sku                  text NOT NULL REFERENCES products(sku),
  version              text NOT NULL,
  artifact_hash_sha256 char(64),
  released_at          timestamptz,
  UNIQUE (sku, version)
);

CREATE TABLE orders (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id bigint NOT NULL REFERENCES customers(id),
  status      text NOT NULL DEFAULT 'pending',  -- pending|paid|fulfilled|closed|refunded
  currency    char(3) NOT NULL DEFAULT 'USD',
  total_cents bigint NOT NULL DEFAULT 0,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE order_lines (
  id            bigserial PRIMARY KEY,
  order_id      uuid NOT NULL REFERENCES orders(id),
  sku           text NOT NULL REFERENCES products(sku),
  quantity      integer NOT NULL CHECK (quantity > 0),
  unit_price_cents bigint NOT NULL
);

CREATE TABLE payment_provider_events (
  id                bigserial PRIMARY KEY,
  provider          text NOT NULL,
  event_type        text NOT NULL,
  payload_hash_sha256 char(64) NOT NULL,
  raw_ref           text NOT NULL,          -- opaque internal reference (never raw secret payload)
  received_at       timestamptz NOT NULL DEFAULT now(),
  processed         boolean NOT NULL DEFAULT false
);

CREATE TABLE payment_references (
  id           bigserial PRIMARY KEY,
  order_id     uuid NOT NULL REFERENCES orders(id),
  provider     text NOT NULL,
  provider_ref text NOT NULL UNIQUE,
  state        text NOT NULL               -- pending|verified|failed|refunded
);

CREATE TABLE receipts (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id          uuid NOT NULL REFERENCES orders(id),
  receipt_hash_sha256 char(64) NOT NULL,
  ledger_receipt_id text,                  -- filled when Corda receipt returns
  issued_at         timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE fulfillment_events (
  id        bigserial PRIMARY KEY,
  order_id  uuid NOT NULL REFERENCES orders(id),
  event     text NOT NULL,
  occurred_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE entitlements (
  id              bigserial PRIMARY KEY,
  customer_id     bigint NOT NULL REFERENCES customers(id),
  sku             text NOT NULL REFERENCES products(sku),
  source_order_id uuid REFERENCES orders(id),
  state           text NOT NULL DEFAULT 'granted',
  granted_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE returns (
  id         bigserial PRIMARY KEY,
  order_id   uuid NOT NULL REFERENCES orders(id),
  reason     text NOT NULL,
  state      text NOT NULL DEFAULT 'open',
  opened_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE support_cases (
  id          bigserial PRIMARY KEY,
  customer_id bigint REFERENCES customers(id),
  channel     text NOT NULL,               -- mastodon|email|web
  subject     text NOT NULL,
  state       text NOT NULL DEFAULT 'open',
  opened_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE audit_events (
  id     bigserial PRIMARY KEY,
  actor  text NOT NULL,
  action text NOT NULL,
  detail jsonb NOT NULL DEFAULT '{}',
  at     timestamptz NOT NULL DEFAULT now()
);

-- Corda-managed final contract/receipt projection.
-- Apply after the base sales schema; PostgreSQL stores operational data and
-- the confirmed Corda reference, not a duplicate of Corda state.
CREATE TABLE IF NOT EXISTS sale_contracts (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id              uuid NOT NULL REFERENCES orders(id),
  transaction_id         text NOT NULL UNIQUE,
  correlation_id        text NOT NULL UNIQUE,
  receipt_number        text NOT NULL UNIQUE,
  event_timestamp_utc   timestamptz NOT NULL,
  customer_reference    text NOT NULL,
  authorized_by         text NOT NULL,
  authorization_reference text,
  corda_event_type      text NOT NULL CHECK (corda_event_type IN (
    'SALE_CONTRACT_CREATED', 'ENTITLEMENT_ISSUED', 'ENTITLEMENT_REVOKED',
    'FULFILLMENT_APPROVED', 'DELIVERY_CONFIRMED', 'RETURN_APPROVED',
    'REFUND_RECORDED'
  )),
  corda_transaction_id  text UNIQUE,
  corda_state           text NOT NULL DEFAULT 'PENDING_SUBMISSION' CHECK (corda_state IN (
    'PENDING_SUBMISSION', 'SUBMITTED', 'CONFIRMED', 'REJECTED', 'FAILED'
  )),
  corda_confirmed_at_utc timestamptz,
  corda_event_hash      char(64),
  manifest_reference    text,
  created_at            timestamptz NOT NULL DEFAULT now(),
  updated_at            timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sale_contract_lines (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_id        uuid NOT NULL REFERENCES sale_contracts(id) ON DELETE CASCADE,
  sku                text NOT NULL REFERENCES products(sku),
  serial_number      text NOT NULL,
  quantity           integer NOT NULL CHECK (quantity > 0),
  unit_price_cents   bigint NOT NULL CHECK (unit_price_cents >= 0),
  currency           char(3) NOT NULL DEFAULT 'USD',
  UNIQUE (contract_id, serial_number)
);

-- Section 11.2.1 cross-system correlation model. The primary business tuple is
-- serial_number + receipt_number + event_timestamp_utc. The fuller record below
-- adds source-event identity so records can be joined across domains by the
-- correlation tuple rather than by free-text names or presentation labels.
CREATE TABLE IF NOT EXISTS correlation_records (
  id                  bigserial PRIMARY KEY,
  correlation_id      text NOT NULL,
  serial_number       text NOT NULL,
  receipt_number      text NOT NULL,
  event_timestamp_utc timestamptz NOT NULL,
  event_type          text NOT NULL,
  source_domain       text NOT NULL CHECK (source_domain IN (
                        'sales','payment','fulfillment','ledger','mapping','field',
                        'simulation','release','support')),
  source_record_id    text NOT NULL,
  schema_version      text NOT NULL DEFAULT '1.0',
  content_hash_sha256 char(64) NOT NULL,
  created_at          timestamptz NOT NULL DEFAULT now(),
  -- Idempotency for Section 11.2 precondition 5: re-ingesting the same source
  -- event must not create a duplicate correlation record.
  UNIQUE (source_domain, source_record_id, event_timestamp_utc)
);

CREATE INDEX IF NOT EXISTS correlation_records_correlation_idx
  ON correlation_records (correlation_id);
CREATE INDEX IF NOT EXISTS correlation_records_tuple_idx
  ON correlation_records (serial_number, receipt_number, event_timestamp_utc);

-- Section 11.2.2 mandatory Corda entry evidence. A sale is not eligible for
-- Corda submission unless sale_request, payment_validation and
-- funds_transfer_verification are all validated for the same correlation_id.
-- This table holds evidence metadata and hashes; it never holds raw payment
-- credentials or unrestricted email content (Section 11.3).
CREATE TABLE IF NOT EXISTS sale_evidence (
  evidence_id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  correlation_id      text NOT NULL,
  evidence_type       text NOT NULL CHECK (evidence_type IN (
                        'sale_request','payment_validation','funds_transfer_verification')),
  provider            text NOT NULL CHECK (provider IN (
                        'website','paypal','Zelle','coinbase','bank','manual_reconciliation')),
  source_reference    text NOT NULL,
  received_at_utc     timestamptz NOT NULL DEFAULT now(),
  validated_by        text,
  content_hash_sha256 char(64) NOT NULL,
  status              text NOT NULL DEFAULT 'received' CHECK (status IN (
                        'received','validated','rejected','superseded')),
  -- Correlation fields carried alongside the evidence so the three evidence
  -- classes can be resolved to one business correlation record.
  serial_number       text,
  receipt_number      text,
  created_at          timestamptz NOT NULL DEFAULT now(),
  UNIQUE (correlation_id, evidence_type, content_hash_sha256)
);

CREATE INDEX IF NOT EXISTS sale_evidence_correlation_idx
  ON sale_evidence (correlation_id);
CREATE INDEX IF NOT EXISTS sale_evidence_status_idx
  ON sale_evidence (status);

-- Section 3.8 role grants: API runtime vs migrations vs backups
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO sales_api_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO sales_backup_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO sales_api_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO sales_backup_role;

-- ---------------------------------------------------------------------------
-- Section 11.2 preconditions 2 and 3: canonical correlation fields and
-- approved read-only reporting views for Metabase and Grafana.
--
-- Reporting joins by the correlation tuple (serial_number + receipt_number +
-- event_timestamp_utc), never by free-text names or presentation labels, and
-- must not infer paid/fulfilled/entitled/verified state from a marketing label.
-- ---------------------------------------------------------------------------

-- Section 11.2.2 gate: Corda entry requires all three evidence classes
-- validated for the same correlation_id.
CREATE OR REPLACE VIEW v_corda_entry_readiness AS
SELECT correlation_id,
       count(DISTINCT evidence_type) FILTER (WHERE status = 'validated')
         AS validated_evidence_classes,
       (count(DISTINCT evidence_type) FILTER (WHERE status = 'validated') = 3)
         AS corda_entry_eligible,
       max(received_at_utc) AS latest_evidence_utc
FROM sale_evidence
GROUP BY correlation_id;

-- Order state without customer PII. Reporting reads state, amounts and counts.
CREATE OR REPLACE VIEW v_reporting_orders AS
SELECT o.id            AS order_id,
       o.status,
       o.currency,
       o.total_cents,
       count(ol.id)    AS line_count,
       coalesce(sum(ol.quantity), 0) AS unit_count,
       o.created_at
FROM orders o
LEFT JOIN order_lines ol ON ol.order_id = o.id
GROUP BY o.id, o.status, o.currency, o.total_cents, o.created_at;

-- Entitlement state joined to the order that granted it.
CREATE OR REPLACE VIEW v_reporting_entitlements AS
SELECT e.id, e.sku, p.name AS product_name, e.state,
       e.source_order_id, e.granted_at
FROM entitlements e
LEFT JOIN products p ON p.sku = e.sku;

-- Receipt state and the Corda reference once the ledger projection returns.
CREATE OR REPLACE VIEW v_reporting_receipts AS
SELECT r.id AS receipt_id, r.order_id, r.receipt_hash_sha256,
       r.ledger_receipt_id, r.issued_at,
       sc.correlation_id, sc.receipt_number, sc.corda_state
FROM receipts r
LEFT JOIN sale_contracts sc ON sc.order_id = r.order_id;

-- The approved cross-reference: product/serial/receipt/entitlement state plus
-- the confirmed Corda reference and event timestamp (Section 11.2).
CREATE OR REPLACE VIEW v_reporting_sale_provenance AS
SELECT sc.receipt_number,
       sc.correlation_id,
       scl.serial_number,
       scl.sku,
       p.name AS product_name,
       scl.quantity,
       scl.unit_price_cents,
       scl.currency,
       sc.corda_event_type,
       sc.corda_state,
       sc.corda_transaction_id,
       sc.corda_confirmed_at_utc,
       sc.event_timestamp_utc,
       r.receipt_hash_sha256,
       r.issued_at
FROM sale_contracts sc
JOIN sale_contract_lines scl ON scl.contract_id = sc.id
LEFT JOIN products p ON p.sku = scl.sku
LEFT JOIN receipts r ON r.order_id = sc.order_id;

-- Section 6.A.2: the reporting identity reads only the approved views. It gets
-- no SELECT on base tables, so raw customer/contact rows stay out of reach.
GRANT CONNECT ON DATABASE salesdb TO sales_reporting_role;
GRANT USAGE ON SCHEMA public TO sales_reporting_role;
GRANT SELECT ON v_corda_entry_readiness,
                v_reporting_orders,
                v_reporting_entitlements,
                v_reporting_receipts,
                v_reporting_sale_provenance
  TO sales_reporting_role;
