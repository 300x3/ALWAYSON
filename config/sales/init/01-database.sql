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

-- Section 3.8 role grants: API runtime vs migrations vs backups
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO sales_api_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO sales_backup_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO sales_api_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO sales_backup_role;
