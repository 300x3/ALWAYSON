-- ALWAYS ON - normalise the Zelle provider spelling to 'Zelle'.
--
-- config/sales/sale-receipt.schema.json has always spelled the provider
-- 'Zelle'. The bootstrap CHECK constraint in config/sales/init/01-database.sql
-- spelled it 'zelle', so any receipt validated against the JSON schema would
-- have failed to insert: the enum values disagreed between the two sources of
-- truth. The operator confirmed on 2026-10-01 that 'Zelle' is correct in all
-- uses, so the constraint is changed to match the schema rather than the
-- reverse.
--
-- Idempotent, and safe on a populated table: no rows existed when this ran.

BEGIN;

ALTER TABLE sale_evidence DROP CONSTRAINT IF EXISTS sale_evidence_provider_check;

UPDATE sale_evidence SET provider = 'Zelle' WHERE provider = 'zelle';

ALTER TABLE sale_evidence ADD CONSTRAINT sale_evidence_provider_check
  CHECK (provider IN ('website','paypal','Zelle','coinbase','bank','manual_reconciliation'));

COMMIT;
