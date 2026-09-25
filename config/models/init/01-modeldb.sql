-- ALWAYS ON model registry database bootstrap (Section 8.6.3)
--
-- The 3D/CAD model registry is its own PostgreSQL database. Section 8.6.3 says
-- only "implemented in PostgreSQL"; Section 3.3 does not name a model database.
-- Operator decision 2026-09-25: give the registry its own database so model
-- provenance can be reported without granting reporting identities access to
-- sales operational tables or Corda internal persistence tables.
--
-- Apply as the postgres superuser on the host cluster:
--   sudo -u postgres psql -f /ALWAYSON/config/models/init/01-modeldb.sql
--
-- Idempotent: safe to re-run.

-- Roles. Section 6.A.2 requires separated identities; the reporting identity
-- (metaread) is granted read-only access at the bottom of this file.
DO $do$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='model_migration_role') THEN
    CREATE ROLE model_migration_role LOGIN;
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='model_api_role') THEN
    CREATE ROLE model_api_role LOGIN;
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='model_backup_role') THEN
    CREATE ROLE model_backup_role LOGIN;
  END IF;
END $do$;

SELECT 'CREATE DATABASE modeldb OWNER model_migration_role'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='modeldb')\gexec

\connect modeldb

-- 8.6.3 model_objects - stable logical identity, survives every revision.
CREATE TABLE IF NOT EXISTS model_objects (
  model_object_id          text PRIMARY KEY,
  object_type              text NOT NULL,   -- cad_assembly|mesh|texture|drawing|package
  canonical_name           text NOT NULL,
  source_system            text,            -- cad_release|webodm_export|sim_result
  -- Section 8.6.6: only explicitly approved objects may back a public proof.
  is_public_proof_eligible boolean NOT NULL DEFAULT false,
  created_at_utc           timestamptz NOT NULL DEFAULT now(),
  created_by               text NOT NULL,
  current_revision_id      text
);

-- 8.6.3 model_revisions - one row per immutable artifact revision.
CREATE TABLE IF NOT EXISTS model_revisions (
  model_revision_id         text PRIMARY KEY,
  model_object_id           text NOT NULL REFERENCES model_objects(model_object_id) ON DELETE CASCADE,
  revision_number           integer NOT NULL CHECK (revision_number > 0),
  content_hash_sha256       char(64) NOT NULL,
  source_artifact_reference text,
  archive_reference         text,
  license_reference         text,
  schema_version            text NOT NULL DEFAULT '1.0',
  -- 8.6.5: superseded revisions are preserved and marked, never reused.
  status                    text NOT NULL DEFAULT 'current'
                              CHECK (status IN ('current','superseded')),
  created_at_utc            timestamptz NOT NULL DEFAULT now(),
  created_by                text NOT NULL,
  UNIQUE (model_object_id, revision_number)
);

-- model_objects.current_revision_id -> model_revisions (added after both exist).
DO $do$ BEGIN
  IF NOT EXISTS (
    SELECT FROM pg_constraint WHERE conname='model_objects_current_revision_fk'
  ) THEN
    ALTER TABLE model_objects
      ADD CONSTRAINT model_objects_current_revision_fk
      FOREIGN KEY (current_revision_id) REFERENCES model_revisions(model_revision_id)
      DEFERRABLE INITIALLY DEFERRED;
  END IF;
END $do$;

-- 8.6.5: a model object may have many revisions but only one current revision.
CREATE UNIQUE INDEX IF NOT EXISTS model_revisions_one_current
  ON model_revisions (model_object_id) WHERE status = 'current';

-- 8.6.5: a revision ID cannot point to different content hashes. The hash and
-- the owning object are immutable once the revision row is written.
CREATE OR REPLACE FUNCTION model_revisions_immutable()
RETURNS trigger LANGUAGE plpgsql AS $fn$
BEGIN
  IF NEW.content_hash_sha256 IS DISTINCT FROM OLD.content_hash_sha256 THEN
    RAISE EXCEPTION 'model_revisions.content_hash_sha256 is immutable (revision %)',
      OLD.model_revision_id;
  END IF;
  IF NEW.model_object_id IS DISTINCT FROM OLD.model_object_id THEN
    RAISE EXCEPTION 'model_revisions.model_object_id is immutable (revision %)',
      OLD.model_revision_id;
  END IF;
  RETURN NEW;
END $fn$;

DROP TRIGGER IF EXISTS model_revisions_immutable ON model_revisions;
CREATE TRIGGER model_revisions_immutable
  BEFORE UPDATE ON model_revisions
  FOR EACH ROW EXECUTE FUNCTION model_revisions_immutable();


-- 8.6.3 model_object_links - the cross-reference table. Relates a model object
-- to a product, serial, receipt, order, mapping project, simulation result or
-- release without embedding the operational record in the 3D file.
CREATE TABLE IF NOT EXISTS model_object_links (
  id                  bigserial PRIMARY KEY,
  model_object_id     text NOT NULL REFERENCES model_objects(model_object_id) ON DELETE CASCADE,
  link_type           text NOT NULL
                        CHECK (link_type IN ('serial','receipt','order','product',
                                             'mapping_project','simulation_result','release')),
  serial_number       text,
  correlation_id      text,
  receipt_number      text,
  event_timestamp_utc timestamptz NOT NULL,
  valid_from_utc      timestamptz NOT NULL DEFAULT now(),
  valid_to_utc        timestamptz,
  source_system       text,
  CHECK (valid_to_utc IS NULL OR valid_to_utc >= valid_from_utc)
);

CREATE INDEX IF NOT EXISTS model_object_links_object_idx
  ON model_object_links (model_object_id);
CREATE INDEX IF NOT EXISTS model_object_links_correlation_idx
  ON model_object_links (correlation_id);
CREATE INDEX IF NOT EXISTS model_object_links_serial_idx
  ON model_object_links (serial_number);

-- 8.6.3 model_ledger_references - Corda provenance reference for a revision.
-- Holds references, states and hashes only; never Corda private keys or
-- unrestricted Corda state (Sections 8.6.7, 11.3).
CREATE TABLE IF NOT EXISTS model_ledger_references (
  id                     bigserial PRIMARY KEY,
  model_revision_id      text NOT NULL REFERENCES model_revisions(model_revision_id) ON DELETE CASCADE,
  corda_event_type       text NOT NULL CHECK (corda_event_type IN (
                           'SALE_CONTRACT_CREATED','ENTITLEMENT_ISSUED','ENTITLEMENT_REVOKED',
                           'FULFILLMENT_APPROVED','DELIVERY_CONFIRMED','RETURN_APPROVED',
                           'REFUND_RECORDED')),
  corda_transaction_id   text UNIQUE,
  corda_state            text NOT NULL DEFAULT 'PENDING_SUBMISSION' CHECK (corda_state IN (
                           'PENDING_SUBMISSION','SUBMITTED','CONFIRMED','REJECTED','FAILED')),
  corda_confirmed_at_utc timestamptz,
  manifest_reference     text,
  created_at_utc         timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS model_ledger_references_revision_idx
  ON model_ledger_references (model_revision_id);

-- Role grants. Same separation as Section 15.1: runtime writes, migrations own,
-- backups and reporting read only.
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO model_api_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO model_api_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO model_backup_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO model_api_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO model_backup_role;

DO $do$ BEGIN
  IF EXISTS (SELECT FROM pg_roles WHERE rolname='metaread') THEN
    EXECUTE 'GRANT CONNECT ON DATABASE modeldb TO metaread';
    EXECUTE 'GRANT USAGE ON SCHEMA public TO metaread';
    EXECUTE 'GRANT SELECT ON ALL TABLES IN SCHEMA public TO metaread';
  END IF;
END $do$;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO metaread;
