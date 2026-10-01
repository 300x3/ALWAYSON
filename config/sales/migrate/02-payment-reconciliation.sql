-- ALWAYS ON - reconciliation evidence columns for payment_references.
--
-- The bootstrap table carries only order_id, provider, provider_ref and
-- state, which is enough to record that a provider event arrived but not
-- enough to satisfy the Section 7.2 control for manual paths: Zelle has no
-- webhook, so a reconciled payment must carry the settlement reference, the
-- operator who approved it, and an authorization reference (the same control
-- set as a wire transfer).
--
-- These columns are additive and nullable, so existing rows are unaffected and
-- no other table changes. Section 18.4 requires Zelle reconciliation to be
-- manual and operator-approved; recording that approval needs somewhere to put
-- it, which is what this provides.
--
-- Idempotent.

BEGIN;

ALTER TABLE payment_references
  ADD COLUMN IF NOT EXISTS amount_cents      bigint,
  ADD COLUMN IF NOT EXISTS currency          char(3),
  ADD COLUMN IF NOT EXISTS settlement_ref    text,
  ADD COLUMN IF NOT EXISTS approved_by       text,
  ADD COLUMN IF NOT EXISTS authorization_ref text,
  ADD COLUMN IF NOT EXISTS note              text,
  ADD COLUMN IF NOT EXISTS updated_at        timestamptz NOT NULL DEFAULT now();

-- Only these states are permitted, matching the state comment in the
-- bootstrap file (pending|verified|failed|refunded).
DO $do$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_constraint
                 WHERE conname='payment_references_state_check') THEN
    ALTER TABLE payment_references ADD CONSTRAINT payment_references_state_check
      CHECK (state IN ('pending','verified','failed','refunded'));
  END IF;
END $do$;

-- A payment may only be 'verified' if a manual path recorded an approver.
-- Automated providers (paypal, coinbase) set approved_by from the verified
-- webhook, so the rule is enforced only for the manual providers.
DO $do$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_constraint
                 WHERE conname='payment_references_manual_approval_check') THEN
    ALTER TABLE payment_references
      ADD CONSTRAINT payment_references_manual_approval_check CHECK (
        state <> 'verified'
        OR provider NOT IN ('Zelle','bank','manual_reconciliation')
        OR approved_by IS NOT NULL
      );
  END IF;
END $do$;

-- Provider spelling must match sale_evidence.provider and
-- config/sales/sale-receipt.schema.json, including 'Zelle'.
DO $do$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_constraint
                 WHERE conname='payment_references_provider_check') THEN
    ALTER TABLE payment_references ADD CONSTRAINT payment_references_provider_check
      CHECK (provider IN ('paypal','Zelle','coinbase','bank','manual_reconciliation'));
  END IF;
END $do$;

COMMIT;
