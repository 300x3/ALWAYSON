# Payment Provider Evaluation (README §18.4, WORK 000030)

Date: 2026-08-28 · Status: Evaluation draft for operator decision (§18.4 OPEN)

Constraints from the architecture (README §3, §5, §7):
- Static pCloud Public Folder storefront only; no server-side checkout code on the host.
- Payment domain (`ao-payment`) receives provider webhooks through `ao-ingress-payment`
  with mandatory provider-signature verification, rate limits, and audit logging.
- Webhook receiver must be reachable from the Internet — the only permitted inbound
  adapter. If the host cannot safely expose a listener, a provider-hosted relay
  (e.g., serverless function) that forwards signed events is the fallback.
- No payment secrets, keys, or card data on the ALWAYSON host or in its repos (§4, §14).
- Refund/dispute records and signed receipt manifests feed `ao-ledger-ingest`.

## Evaluation matrix

| §18.4 criterion | Stripe Checkout | Paddle Merchant | PayPal Commerce | BigCommerce |
|---|---|---|---|---|
| Static-site compatible checkout | Yes (hosted/payment links) | Yes (overlay/hosted) | Yes (hosted buttons) | Partial (own hosted store) |
| Webhook signature verification | Yes, documented scheme | Yes, signed events | Yes (webhook validation API) | Platform-dependent |
| Card + PayPal support | Card native; PayPal add-on | Card + PayPal built-in | PayPal + cards via powered checkout | Via integrated gateways |
| Refund/dispute workflow | Full API + dashboard | Full API (MoR) | Full API/dashboard | Via gateway |
| Exportable accounting records | CSV + API | CSV + API | CSV/API | CSV |
| Fee model | ~2.9% + 30¢; monthly $0 | ~5% + 50¢ (MoR, tax-inclusive) | ~3.49% + fixed (PP fees vary) | Platform fee ($29–299/mo) + gateway fees |
| Merchant-of-record / sales tax handling | No (you are MoR) | **Yes** | No | No |
| Inventory/catalog integration | Native catalog + optional | Product catalog | Buttons; limited catalog | Full store platform |
| Recurring cost | $0 base | $0 base | $0 base | $29+/month recurring |
| Privacy/data-processing terms | DPA available | DPA available; strongest data minimization (MoR) | Standard | Requires review; store data on their platform |
| Data flow into ALWAYSON | Signed webhook events only | Signed webhook events only | Signed webhook events only | Platform-dependent; broader coupling |

## Key trade-offs

1. **Paddle** is the only merchant-of-record option — it assumes sales-tax/VAT
   liability, which matters for a solo operator selling internationally.
   Trade-off: highest per-transaction fee and least catalog flexibility.
2. **Stripe Checkout** best matches the static-storefront + signed-webhook
   architecture: payment links require zero host-side server code, and webhook
   signature verification maps 1:1 onto the `ao-payment` normalizer design.
   Operator must still own tax compliance.
3. **PayPal** alone is simple but weak as the sole provider (limited webhooks,
   fee structure); better as a secondary method behind Stripe or Paddle.
4. **BigCommerce** conflicts with the static pCloud storefront model (it wants to
   host the storefront) and adds recurring cost — README §18.4 explicitly flags
   this for documentation. Not recommended without a storefront rethink.

## Recommendation (draft, for operator approval)

Primary: **Stripe Checkout via payment links** with signed webhooks into
`ao-ingress-payment` → `ao-payment` verifier. Optional secondary PayPal via
Stripe's PayPal method (single integration, single webhook stream).

## Next actions on operator decision

1. Select provider; record decision + rationale in README §18.4 (move to Approved Deviations if deviating).
2. Provision API keys via approved secret delivery (KDE Wallet runbook, §14.1) — no secrets in repo.
3. Implement `ao-payment` webhook verifier behind `ao-ingress-payment` with:
   signature verification, rate limiting, event normalization, audit log, idempotency.
4. Generate a signed receipt-manifest test event (no live charge, no secrets) and
   validate the `ao-ledger-ingest` path with a scaffold (pre-key-ceremony) receipt ID.
