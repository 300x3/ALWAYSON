# ALWAYS ON — Corda-Managed Sale and Receipt Process

## Authority

Corda is the managing authority for the final sale/contract and its ledger state:

```text
Payment verified
  → PostgreSQL provisional order/customer/payment projection
  → signed sale-contract manifest
  → ledger-ingest gateway
  → Corda contract transaction
  → Corda receipt/entitlement state
  → PostgreSQL final projection and reporting views
```

## Mandatory Corda entry evidence

A sale is not eligible for Corda submission until all three evidence records are
validated against the same `correlation_id`, `receipt_number`, serial
identity, and UTC event time:

1. Sale-request email or approved equivalent.
2. Provider payment-validation email for PayPal, Zelle, Coinbase/stablecoin,
   or another approved provider.
3. Funds-transfer verification showing that the funds actually transferred and
   settled into the approved account.

The required evidence statuses are:

```text
sale_request.status = validated
payment_validation.status = validated
funds_transfer_verification.status = validated
```

Payment initiation alone is not payment validation, and payment validation alone
is not proof of settlement. Store hashes and references in PostgreSQL; store
only the approved references, hashes, states, and authorization in Corda. Never
store raw payment credentials in the evidence records, PostgreSQL, or Corda.

## Three-form transaction bundle

Each purchase transaction uses one system-issued ID and one folder:

```text
/ALWAYSON/data/sales/transactions/<transaction-id>/
├── 01-purchase-request.html
├── 02-payment-confirmation.html
├── 03-receipt.html
├── BUNDLE-STATUS.txt
└── provider-evidence/
```

Issue and validate the bundle with:

```bash
/ALWAYSON/scripts/sales/issue-transaction-bundle.sh
/ALWAYSON/scripts/sales/validate-transaction-bundle.sh \
  /ALWAYSON/data/sales/transactions/<transaction-id>
```

The same ID must appear in all three forms and in the bundle status. The ID is also
required in the Corda sale-receipt event and in the PostgreSQL contract
projection. Form 2 must distinguish provider payment validation from
funds-transfer settlement. Form 3 is provisional until all three evidence
references are validated and Corda confirms the contract state.

Corda stores the transaction ID, event/state, hashes, and approved references so
payment and ledger state can be tracked against the same ID. Detailed private
data remains in the encrypted PostgreSQL projection; do not copy full customer
records, raw emails, payment credentials, or unrestricted evidence into Corda.


## Three-column operational receipt form

The operator form is:

```text
/ALWAYSON/forms/three-column-corda-sale-receipt-form.html
/ALWAYSON/forms/three-column-corda-sale-receipt-form.pdf
```

It is an operator form, not a demo. Each column captures the sale identity,
the three mandatory evidence gates, Corda/proof fields, handshake acceptance,
and the CC BY-NC-SA 4.0 notice. It does not send email, write to PostgreSQL,
process payment, or submit to Corda; submission remains an authorized operator
workflow.

## Transaction authority and projection

Corda owns the final contract identity, receipt association, entitlement state,
and approved state transitions. PostgreSQL owns detailed operational records,
customer/order queries, payment operations, fulfillment records, support data,
and reporting projections.
customer/order queries, payment operations, fulfillment records, support data,
and reporting projections.

A receipt is not final until Corda has returned a confirmed transaction/state
reference and the PostgreSQL projection records that reference.

## Correlation identity

Every sale line and ledger event carries:

```text
correlation_id
serial_number
receipt_number
event_timestamp_utc
```

`correlation_id` is the stable business correlation key. A receipt may contain
multiple serial numbers. One serial number may have multiple lifecycle events.
The unique event key is:

```text
correlation_id + event_type + event_version
```

## Process states

```text
DRAFT
PAYMENT_PENDING
PAYMENT_VERIFIED
CONTRACT_PENDING_CORDA
CONTRACT_CONFIRMED
ENTITLEMENT_ISSUED
READY_TO_FULFILL
FULFILLMENT_PENDING
FULFILLMENT_CONFIRMED
DELIVERY_CONFIRMED
RETURN_REQUESTED
REFUND_RECORDED
ENTITLEMENT_REVOKED
REJECTED
```

Only authorized state transitions may be submitted to Corda. A failed or
rejected transition remains visible in PostgreSQL and is never silently
replaced.

## PostgreSQL projection

The sales database stores the operational projection and the Corda result:

```text
salesdb.orders
salesdb.order_lines
salesdb.payment_references
salesdb.receipts
salesdb.entitlements
salesdb.fulfillment_events
salesdb.returns
salesdb.audit_events
```

The final receipt projection must include:

```text
receipt_number
correlation_id
corda_transaction_id
corda_state
corda_confirmed_at_utc
corda_event_hash
```

Corda must not receive full customer PII, payment credentials, private keys,
raw telemetry, imagery, or large operational objects.

## Corda event types

The initial sale contract should support:

```text
SALE_CONTRACT_CREATED
PAYMENT_VERIFIED
ENTITLEMENT_ISSUED
ENTITLEMENT_REVOKED
FULFILLMENT_APPROVED
DELIVERY_CONFIRMED
RETURN_APPROVED
REFUND_RECORDED
```

Each event is signed and idempotent. The ledger-ingest gateway must reject
replays, unauthorized state changes, malformed correlation tuples, and events
whose source PostgreSQL record does not exist.

## Reporting

```text
Corda confirmed state
        │
        ▼
PostgreSQL final projection/read-only views
        ├── Metabase: sales, receipt, entitlement, marketing reports
        └── Grafana: sales/ledger/fulfillment dashboards
```

Metabase and Grafana must report the Corda-confirmed state, not infer it from a
marketing label, receipt PDF, or unresolved PostgreSQL event.

## Activation gate

The workflow is staged until the following are complete:

1. `salesdb` schema and roles are initialized.
2. Corda database/node and key ceremony are complete.
3. Ledger-ingest mTLS identity and authorization policy are provisioned.
4. The sale-contract manifest schema and signature verification are deployed.
5. Synthetic end-to-end contract/receipt tests pass.
6. Backup and reconciliation include PostgreSQL projections and Corda records.

Do not mark a real sale final or publish a public provenance proof before the
Corda confirmation reference is present in the PostgreSQL projection.
