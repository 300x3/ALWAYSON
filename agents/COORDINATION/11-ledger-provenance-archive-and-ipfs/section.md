# 11. Ledger, Provenance, Archive, and IPFS

## 11.1 Ledger Authority Policy

Corda is the authoritative ledger for approved business provenance, receipt, entitlement,
fulfillment-approval and release-approval records. It is **not** the authoritative store for
domain-operational source data — that stays in the related PostgreSQL database (§3.3.b).

**Corda runs on Corda 5 against `cordadb`**, a separate logical database on the host
PostgreSQL 18 cluster with its own roles and backup scope. H2 is not an acceptable backing
store for this node. Roles, host-loopback binding, backup scope, restore procedure, and
separation from the sales and mapping databases are specified in §17.1 and §3.3.1.

| Area | Authoritative operational data | Network |
|---|---|---|
| Sales | Sales PostgreSQL order, fulfillment, and customer-service records | `ao-sales` |
| Payment | Verified provider event record and normalized payment state | `ao-payment` (ingress via `ao-ingress-payment`) |
| Field | Raw packet store, telemetry spool, and mission records | `ao-field` |
| Mapping | Validated imagery, WebODM project data, processing outputs, and deliverables | `ao-mapping` |
| Vehicle simulation | Scenario definitions, run data, and result artifacts | `ao-sim-vehicle` |
| Fabrication simulation | Facility/task models, safety scenarios, and result artifacts | `ao-sim-fabrication` |
| Archive | Encrypted archive objects and retention records | `ao-egress-archive` |
| Ledger | Corda state, PKI, and the complete ledger of debits and credits | `ao-ledger-core` |

Network names are the real Podman names used throughout this document, in the Quadlet
definitions, and in `config/platform/network-cidrs.yaml`. Where an area is served by a
controlled adapter rather than a workload network, the adapter is named in the same cell.

One row is an adapter and has **no network of its own**: `ao-egress-archive` is absent
from both `config/platform/network-cidrs.yaml` and `podman network ls`. Every other
network named in the table above is present in both. This is measured, not inferred:

```text
$ grep -c '^ao-' config/platform/network-cidrs.yaml
14
$ grep -n 'ao-egress-archive' config/platform/network-cidrs.yaml
(no match)

$ podman network ls --format '{{.Name}}' | grep -c '^ao-'
14
$ podman network ls --format '{{.Name}}' | grep -c 'ao-egress-archive'
0
```

The registry and the live host agree on fourteen `ao-*` networks, eleven
`Internal=true` and three `Internal=false` — so the archive row is a genuine
exception, not a counting artefact. `config/platform/topology-model.yaml` already
records it correctly as `adapter: true`, `status: planned`. See §11.6.1.

Corda records signed references, hashes, approved transitions, and entitlement and
provenance data sufficient to verify a claim without duplicating sensitive or high-volume
data.

## 11.2 Ledger Flow

```text
Domain event or artifact
      │
      ▼
SHA-256 content hash
      │
      ▼
Signed manifest
      │
      ▼
Ledger-ingestion gateway
      ├── Mutual TLS
      ├── Authorization
      ├── Schema validation
      ├── Signature verification
      ├── Idempotency
      └── Audit logging
              │
              ▼
Corda transaction
              │
              ▼
Receipt, entitlement, provenance, or approval state
```

### 11.2.1 Cross-System Correlation and Provenance Model

The primary business correlation tuple is:

```text
serial_number + receipt_number + event_timestamp_utc
```

These fields link records across PostgreSQL domains and approved ledger records:

- `serial_number` identifies the physical product, vehicle, component, or asset.
- `receipt_number` identifies the approved commercial transaction or receipt.
- `event_timestamp_utc` identifies when the source event occurred, using ISO-8601 UTC.

The tuple should be accompanied by a source event identifier and schema version:

```text
correlation_id
serial_number
receipt_number
event_timestamp_utc
event_type
source_domain
source_record_id
schema_version
content_hash_sha256
```

Example:

```json
{
  "correlation_id": "ORDER-2026-000123-LOT-A",
  "serial_number": "SN-300X3-000042",
  "receipt_number": "RCPT-2026-000123",
  "event_timestamp_utc": "2026-09-25T12:34:56.000Z",
  "event_type": "entitlement_issued",
  "source_domain": "sales",
  "source_record_id": "order-line-000123-01",
  "schema_version": "1.0",
  "content_hash_sha256": "SHA256_DIGEST"
}
```

The same correlation fields should be carried into approved records from sales,
mapping, field, fulfillment, simulation, and release workflows where the event
is relevant. A database view or reporting projection should join the records by
the correlation tuple rather than by free-text names or presentation labels.

### Ledger responsibility: integrity and provenance, not general encryption

Corda/blockchain records should contain the minimum data needed to verify that
an approved event, artifact, receipt, entitlement, or state transition occurred:

```text
serial_number
receipt_number
event_timestamp_utc
event_type
state or status
content_hash_sha256
opaque source reference
signature/authorization metadata
```

The ledger should not contain:

```text
card numbers, CVV, payment secrets, private keys,
full customer PII, raw telemetry, imagery, point clouds,
or large operational payloads
```

Encryption is performed before sensitive data leaves its authoritative store,
for example before pCloud archival replication or private IPFS distribution.
Corda then records the encrypted-object reference and content hash. This gives
integrity and provenance for the encrypted object without putting the plaintext
payload on the ledger.

### Sales and marketing reporting flow

```text
Sales PostgreSQL salesdb
  order, product, serial, receipt, payment, fulfillment, entitlement
        │
        ├── correlation tuple:
        │     serial_number + receipt_number + event_timestamp_utc
        │
        ├── Metabase  (REPORTING — reads salesdb)
        │       └── sales/marketing reports and PDF exports
        │
        ├── Grafana  (dashboards and metrics — reads approved PostgreSQL)
        │       └── sales/fulfillment/provenance dashboards
        │
        └── signed minimized manifest
                └── Corda receipt/entitlement/provenance state
```

Marketing and sales reporting should use approved PostgreSQL views or
projections. The reporting layer may join:

```text
product/SKU
serial number
receipt number
order and order-line state
entitlement state
Corda receipt/provenance status
event timestamp
```

It must not infer that a product is fulfilled, entitled, paid, or blockchain-verified
solely from a marketing label. Those states must come from the authoritative
PostgreSQL event and the approved ledger projection.

### Implementation preconditions

Before enabling this flow:

1. Initialize and verify the `salesdb` schema.
2. Define canonical `serial_number`, `receipt_number`, and UTC timestamp fields.
3. Confirm the Metabase reporting identity can read `salesdb` and produce the
   standard PDF reports and receipts, and confirm the Grafana datasource can
   read it for dashboards. Neither tool writes into `salesdb`.
4. Define the signed manifest schema and correlation-ID uniqueness rule.
5. Implement ledger-ingest authorization, signature verification, idempotency,
   replay protection, and audit logging.
6. Complete the Corda key/certificate ceremony.
7. Test the complete correlation path with synthetic data before connecting
   real sales, payment, customer, or product records.

### 11.2.2 Mandatory Corda Entry Evidence

A sale is eligible for Corda submission only when all three evidence classes are present for
the same business correlation record:

1. **Sale-request email**
   - Customer-originated sale/KIT REQUEST email or approved equivalent.
   - Captures requester, requested items/SKUs, comments, and request timestamp.
   - Does not by itself prove a contract or payment.

2. **Payment-validation email**
   - Provider-specific validation for PayPal, Zelle, or Coinbase.
   - Identifies the provider, provider reference, amount, currency, validation
     status, and validation timestamp.
   - Does not by itself prove that funds settled into the approved account.

3. **Funds-transfer verification**
   - Operator/provider reconciliation evidence that the funds actually
     transferred and settled.
   - Records settlement/available state, transfer reference, amount, currency,
     and verification timestamp.
   - Must not be treated as verified merely because a payment was initiated.

The three records must resolve to the same:

```text
correlation_id
receipt_number
serial_number(s)
event_timestamp_utc
```

Evidence record:

```text
evidence_id
evidence_type = sale_request | payment_validation | funds_transfer_verification
provider = website | paypal | zelle | coinbase | bank | manual_reconciliation
source_reference
received_at_utc
validated_by
content_hash_sha256
```

An evidence record counts only once it carries all of the following. Anything short of all of
them does not count, and no partial record is stored as though it did:

```text
sale_request.present                = true
payment_validation.present          = true
funds_transfer_verification.present = true
```


Corda records references, hashes, states, and operator authorization for these
three gates; it must not store raw payment credentials or unrestricted email
content. PostgreSQL stores the detailed evidence metadata and reporting
projection. Metabase is for reporting and Grafana is for dashboards and metrics;
both show the resulting confirmed state and neither performs or waives the
verification.

Before the three gates can be satisfied, the operator key/certificate ceremony
must be complete and the correlation path must be proven with synthetic data.

### 11.2.3 Corda-Managed Sale and Receipt Process

The detailed process, state machine, correlation model, and activation gate are
maintained in the canonical runbook:

```text
/ALWAYSON/docs/runbooks/corda-sale-receipt-process.md
```

The short rule is:

```text
KIT REQUEST/inquiry
  → verified payment
  → PostgreSQL provisional projection
  → signed sale-contract manifest
  → ledger-ingest gateway
  → Corda transaction/state
  → PostgreSQL final projection
  → receipt and reporting views
```

A receipt is not final until Corda has returned a confirmed transaction/state
reference and the PostgreSQL projection records that reference. The intake,
form, schema, and validator artifacts are:

```text
/ALWAYSON/data/sales/kit-request-intake/
/ALWAYSON/forms/three-column-corda-sale-receipt-form.html
/ALWAYSON/forms/three-column-corda-sale-receipt-form.pdf
/ALWAYSON/forms/corda-sale-receipt.html
/ALWAYSON/config/sales/sale-receipt.schema.json
/ALWAYSON/config/sales/sale-receipt.example.json
/ALWAYSON/scripts/validation/validate-sale-receipt.sh
```

The form is an internal operator form. It does not write to PostgreSQL, contact
Corda, process payments, or create a public proof. Submission must go through
the authorized ledger-ingest workflow after operator review.

### 11.2.4 Ledger-Ingest Probe Status

The ingest-path probe `scripts/validation/check-ledger-ingest.sh` is **resolved and
deterministic**, not missing or blocked. It runs unprivileged and requires no
pending operator command:

```text
$ bash /ALWAYSON/scripts/validation/check-ledger-ingest.sh
PENDING: ledger-ingest gateway not deployed yet (Section 2.8 step 3 awaits Corda version approval)
$ echo $?
3
```

Exit `3` is a defined **PENDING** state, distinct from a failure (`44`) and from
healthy (`0`). The script exits `3` before any network call because no container
named `ledger-ingest` exists — confirmed independently:

```text
$ podman ps -a --format '{{.Names}}' | grep -c 'ledger-ingest'
0
```

There is therefore no unresolved socket-bridge fault to diagnose. The probe is
blocked only by the gateway not being deployed, which is downstream of the
Corda 5 node build and the operator key ceremony. No privileged command is
pending for this item.

Signing and submission are likewise staged, not broken:
`scripts/ledger/sign-manifest.sh` signs and `scripts/ledger/submit-ledger-event.sh`
stages unsigned-or-unsubmitted manifests to
`artifacts/pending-ledger-submissions/<YYYYMMDD>/` and exits `3`, so nothing is
lost while the gateway is absent. Ingest security properties (§11.2.1) are
therefore **specified and enforced client-side**, but remain **unproven end to
end** until the gateway exists.

### 11.2.5 Ingest Security Requirements (specified, not yet enforced by a gateway)

The ingest gateway must enforce all of the following. Each maps to a control in
§11.2.1 and §4.4; none is satisfied by the current staging behaviour.

| # | Requirement | Enforced by | Current state |
|---|---|---|---|
| 1 | Mutual TLS; one client certificate per exporter domain | Gateway | Not implemented — no gateway |
| 2 | Path authorization against `config/ledger/authorization-policy.yaml` | Gateway | Policy file exists, no enforcer |
| 3 | JSON Schema validation against `config/ledger/manifest-schema.json` | Gateway | Schema exists; `additionalProperties: false` |
| 4 | Detached signature verification against the exporter's registered key | Gateway | **Signer-side only.** `sign-manifest.sh` signs; nothing verifies |
| 5 | `producer_key_id` must match the mTLS certificate identity | Gateway | Not implemented |
| 6 | Idempotency on `correlation_id` (§11.2.1) | Gateway | Required by policy, unenforced |
| 7 | Replay defence — reject a re-presented digest/timestamp | Gateway | Not implemented |
| 8 | Audit log of accept **and** reject, with reason code | Gateway | Not implemented |

Two design points an implementer should not get wrong:

- **Minimization is enforced at the schema, not by convention.** The manifest
  schema is `additionalProperties: false` and requires no field outside
  `config/ledger/manifest-schema.json`. A payload carrying raw customer PII,
  card data, or telemetry is therefore *rejected*, not merely discouraged.
- **A `sales_receipt` manifest requires `transaction_id`**, enforced by the
  schema's conditional (`if object_type == sales_receipt then required
  [transaction_id]`) and again by `build-manifest.sh`, which rejects a
  `sales_receipt` without an issued `transaction_id` (exit `12`).

Until rows 1–8 exist in a running gateway, **LEDGER-03 stays open**. What is
demonstrable today is only the client half: build → sign → stage. Signing proves
a manifest is well-formed and signed; it proves nothing about acceptance,
authorization, or replay defence, because there is no acceptor to test.

#### What the client half actually does — exercised, not assumed

Run against synthetic content only; no real sales, payment, customer, or product
record was used, and the staged test artifact was deleted afterwards.

```text
$ bash scripts/ledger/build-manifest.sh sales_receipt sales <file> testref
ERROR: sales_receipt requires issued transaction_id          # exit 12

$ bash scripts/ledger/build-manifest.sh telemetry_batch field <file> testref
exit 0; object_type=telemetry_batch, origin_domain=field, content_size_bytes=23, signature=""

$ bash scripts/ledger/submit-ledger-event.sh <unsigned-manifest>
ERROR: manifest is unsigned (run sign-manifest.sh first)      # exit 20

$ bash scripts/ledger/submit-ledger-event.sh <signed-manifest>
PENDING: gateway not deployed; manifest staged for later submission   # exit 3

$ bash scripts/ledger/verify-ledger-receipt.sh RCPT-FAKE-0001 <manifest>
FAIL: receipt mismatch                                        # exit 50
```

So the **unsigned-rejection** and **schema conditional** behaviours are real and
now verified by execution rather than by reading the source.

#### A real weakness: staging does not validate the signature

`submit-ledger-event.sh` checks only that `.signature` is a **non-empty string**
(`jq -r '.signature // empty'`, then `[[ -n "$sig" ]]`). A deliberately bogus
value is accepted and staged:

```text
$ jq '.signature="ed25519:SYNTHETIC_NOT_A_REAL_SIGNATURE"' m.json > m3.json
$ bash scripts/ledger/submit-ledger-event.sh m3.json
PENDING: gateway not deployed; manifest staged for later submission   # exit 3
```

This is **not currently a security hole**, because the manifest goes to a local
staging directory and is never transmitted — there is no gateway to accept it.
It becomes one the moment row 4 (server-side signature verification) is skipped.
Therefore:

- The gateway **must** verify the detached signature cryptographically against
  the exporter's registered key and **must not** trust `producer_key_id` or the
  embedded `signature` field as supplied (row 5).
- Anything replayed out of `artifacts/pending-ledger-submissions/` after the
  gateway comes up is untrusted input and must traverse the full row 1–8 set.
- If a future staging replay tool re-signs locally instead of submitting, it
  creates records that look operator-approved and are not.

The empty `producer_key_id` and `authorization_policy_id` fields that
`build-manifest.sh` emits are currently unpopulated placeholders. They must be
filled by the gateway from the authenticated mTLS identity, never from the
submitted body.

## 11.3 Corda Stores and Private Data

Corda may retain approved private transaction data as an encrypted private
payload or encrypted attachment. Corda does not make plaintext private data
safe merely by being on a ledger: confidentiality depends on encryption,
authorized recipients, key management, access policy, and audit controls.

### Corda contract state

Corda state should contain the small, shared, verifiable business facts:

```text
transaction_id
correlation_id
receipt_number
order_id
serial_number(s)
sku
model_object_id / model_revision_id
payment provider
payment-validation reference/hash
funds-transfer reference/hash
payment/settlement state
entitlement/fulfillment/delivery state
Corda transaction ID
timestamps
signatures/authorization metadata
```

### Encrypted private payload

Approved private data may be encrypted before submission and stored as a
private attachment or confidential private-state object:

```text
customer identity and contact details
purchase-request email/content
payment-validation email/content
funds-transfer verification content
full receipt and contract
fulfillment, delivery, return, and support records
private 3D model files and attachments
```

The private payload envelope must include:

```text
transaction_id
data_classification = PRIVATE
schema_version
encryption algorithm
encryption key identifier
authorized recipients
payload SHA-256
retention policy identifier
created_at_utc
```

The encryption key must be held by the approved KMS/wallet/key-management
process and must never be stored in Corda, PostgreSQL, Git, HTML, logs, or the
transaction bundle.

Corda tracks the transaction ID, state, hashes, references, and authorized
signatures. PostgreSQL retains the operational/reporting projection keyed by
the same transaction ID. Metabase reports the confirmed state and Grafana shows
it on a dashboard; neither creates or waives payment verification.

### 11.3.1 Accounting Model for the Authoritative Ledger

Corda is the authoritative record of **approved postings**. PostgreSQL remains
authoritative for **source operational data** (§11.1). The two are not in
conflict: a posting is an approved assertion that a business event occurred, and
it exists only after the event is verified and reconciled. The accounting report
required by §4.4 is **computed in reporting**, from approved PostgreSQL rows
joined to approved Corda postings by the correlation tuple — never from a balance
stored as a mutable field on the ledger.

#### Accounts

The account set is deliberately small and closed. Anything that is not one of
these is rejected at ingest.

| Code | Type | Meaning |
|---|---|---|
| `CASH_EU` / `CASH_US` | Asset | Funds received and settled into the approved account |
| `CASH_PENDING` | Asset | Payment validated but **not** yet funds-transfer verified (§11.2.2 gate 3) |
| `RECEIVABLE_CUSTOMER` | Asset | Entitlement issued, payment not yet verified |
| `REVENUE_SALE` | Revenue | Value of a confirmed sale |
| `REVENUE_DIGITAL_TRANSFER` | Revenue | Value of a post-sale archive/IPFS transfer |
| `REFUNDS_PAYABLE` | Liability | Refunds approved and owed |
| `TAX_PAYABLE_<jurisdiction>` | Liability | Tax accrued and owed, per approved jurisdiction |
| `EXPENSE_ARCHIVE` | Expense | pCloud/IPFS replication cost attributed to a delivery |

#### Debit/credit entry semantics

Every posting is a **balanced double-entry** of two or more legs against one
`transaction_id`. Each leg carries `account_code`, `side` (`DEBIT` | `CREDIT`),
`amount`, `currency`, and `correlation_id`. The invariant, enforced at ingest and
re-checked in reporting:

```text
SUM(debits) = SUM(credits)   per transaction_id, per currency
```

A posting that does not balance, or that mixes currencies within one leg set, is
**rejected**. There is no unbalanced posting and no "plug" or suspense account
that exists to absorb a difference.

- Amounts are stored in **minor units as integers** (cents). No floats.
- Amounts and balances are immutable once a posting is confirmed. A correction is
  a **new reversing transaction** referencing the original `transaction_id`;
  history is never edited and never deleted (§11.6, rule: no data deletion).
- Corda records **no running balance**. A balance is a query result over the
  posting set, so a balance can never disagree with its postings.

#### Currency handling

A posting is **single-currency**. Multi-currency is handled by separate postings
plus an explicit `FX_REVALUATION` event carrying `from_currency`,
`to_currency`, `rate_source`, and `rate_as_of_utc`. The rate is a recorded input,
never computed silently. There is no implicit conversion at read time.

#### Posting rule (what may be posted, and when)

```text
NO EVENT, NO POSTING
```

| Event | May post to | Gate |
|---|---|---|
| Payment provider event received | — | None. This is **not** a posting. It only advances `CASH_PENDING`. |
| Payment validated | — | Still not a posting; §11.2.2 gate 2 alone is insufficient |
| Funds transfer verified | `CASH_EU`/`CASH_US` DR / `RECEIVABLE_CUSTOMER` CR | **All three** §11.2.2 gates |
| Entitlement issued | `RECEIVABLE_CUSTOMER` DR / `REVENUE_SALE` CR | Sale confirmed on the ledger |
| Post-sale transfer authorised | `CASH_EU`/`CASH_US` DR / `REVENUE_DIGITAL_TRANSFER` CR | `ao-sales` authorisation (§11.6) |
| Refund approved | `CASH_EU`/`CASH_US` DR / `REFUNDS_PAYABLE` CR | Explicit operator approval |
| Archive replication cost | `EXPENSE_ARCHIVE` DR / `CASH_EU`/`CASH_US` CR | Verified provider cost |

Every row above names exactly two legs and they are the DR/CR pair required by the
balance invariant, so each row is a balanced posting on its own. `CASH_PENDING` is
named only in the "not a posting" rows and is deliberately **absent** from this table;
`TAX_PAYABLE_<jurisdiction>` has no posting rule here — see §11.12, finding 3.

**Corda is not a payment processor and does not create funds.** It cannot move
money, initiate a refund, set a price, or decide tax. It records that an approved
event happened and was authorised by whom. A posting is evidence, never a
payment instruction (§7.2).

#### Reconciliation between Corda and `salesdb`

Both sides are compared **per correlation tuple** and reported as a difference,
never auto-corrected:

```text
for each (receipt_number, serial_number, event_timestamp_utc):
  ledger_posting_set   := approved Corda postings
  salesdb_record_set   := verified + operator-reconciled salesdb rows
  reconcile            := matched | ledger_only | salesdb_only | amount_mismatch | currency_mismatch
```

Rules:

1. A `salesdb` row with **no** approved Corda posting is `salesdb_only`. It is a
   missing posting and is an **exception that blocks the receipt being called
   final** (§11.2.3).
2. A Corda posting with **no** `salesdb` row is `ledger_only` and is a provenance
   defect. It is investigated; it is not deleted.
3. Amount or currency disagreement is `amount_mismatch` / `currency_mismatch` and
   is resolved by a reversing transaction plus a corrected posting (§11.2.2 gate
   evidence is re-checked), never by editing either side.
4. Reconciliation is a **read-only report**. Metabase surfaces it; Grafana
   dashboards it. Neither writes to `salesdb` or to Corda.

#### What the §4.4 accounting report is

`Standard accounting/ledger report PDF → ao-admin reporting output` (§4.4) is a
**computed projection**, built from approved `salesdb` rows joined to approved
Corda postings by the correlation tuple. It reports postings, not stored
balances. It cannot create, waive, or infer a payment state: §11.2.2 gate
evidence and the Corda posting must both be present, or the line does not appear.

## 11.4 Corda Does Not Store

Corda may store approved encrypted private transaction data as described in §11.3. It must
never store plaintext secrets or unencrypted credentials.

Never store:

```text
card numbers
CVV
bank credentials
payment-provider secret keys
passwords
OAuth tokens
private keys
TLS private keys
KMS master keys
data-encryption keys
recovery phrases
```

## 11.5 Manifest Format

```json
{
  "object_id": "UUID",
  "object_type": "sales_receipt | telemetry_batch | map_product | vehicle_simulation | fabrication_simulation",
  "origin_domain": "sales | field | mapping | sim_vehicle | sim_fabrication",
  "created_at_utc": "ISO-8601 UTC timestamp",
  "schema_version": "1.0",
  "content_hash_sha256": "HEX_DIGEST",
  "content_size_bytes": 0,
  "local_storage_reference": "opaque internal reference",
  "ipfs_cid": "optional encrypted CID",
  "pcloud_archive_reference": "optional opaque encrypted reference",
  "authorization_policy_id": "policy ID",
  "producer_key_id": "service key ID",
  "signature": "detached signature"
}
```

## 11.6 pCloud and IPFS Rules

**What "archived" means here.** A package held by `ao-egress-archive` is **"archived for
data transfer and sale"**. It is **not a backup**. It exists so a sold map, imagery set, or
telemetry/IoT package can be *transferred* to the authorised recipient, and verified in
transfer, with a blockchain sales listing where applicable. There is **no restore duty, no
recovery duty, and no retention duty** attached to it.

**The backup is restic.** Host-wide encrypted backup and restore validation are governed by
§17.1. If `ao-egress-archive` is lost, nothing is "recovered" from it — the backup
set is what protects the data, and the backup set lives under restic, not IPFS and not
pCloud archival staging.

**Authorisation.** `ao-egress-archive` requires **`ao-sales` authorisation** first. It is
never reached directly from the internet and it does not originate a transfer on its own.

```text
Local source data
      │
      ├── Content hash
      ├── Signed manifest
      ├── Corda receipt or approval state
      ├── Encrypted pCloud archive
      └── Private or encrypted IPFS distribution
```

- Local source data remains authoritative.
- Encrypt before pCloud archival replication unless an explicitly approved
  equivalent encryption control applies.
- Do not place private data, PII, payment data, private keys, raw telemetry,
  sensitive imagery, or proprietary technical designs on public IPFS.
- For post-sale transfer of sensitive artifacts, use a private IPFS swarm,
  controlled pinning, or encryption before any public IPFS distribution.
- Record content hash and CID separately.
- Post-sale, store only CIDs and encrypted package references in Corda. IPFS is a
  post-sale marking/transfer mechanism only (ES.1); it is not archive, accounting,
  or ledger storage, and Corda has no IPFS dependency.
- **IPFS is for file-transfer verification and, potentially, sales listing on a
  blockchain.** It is not a backup, not a disaster-recovery copy, and not a retention
  store.
- **pCloud replication here is a transfer copy, not the backup set.** The backup set is
  restic (§17.1).
- Archive replication occurs only through `ao-egress-archive`.

### 11.6.1 pCloud Archive Credential Status

`ao-egress-archive` **does not exist as a Quadlet, a container, or a network.**
This is the concrete reason LEDGER-04 cannot progress, and it is a fact measured
this session, not an inference:

```text
$ find quadlet -ipath '*archive*'          # no output
$ podman ps -a --format '{{.Names}}' | grep -c -E 'archive|egress'
0
```

Only the policy file exists (`config/pcloud/replication-policy.yaml`), which
constrains scope but provisions nothing. **Credentials cannot be provisioned into
a service that has no unit.** Building that adapter is separate work; until it
exists, "credentials into `ao-archive`" is not executable as written.

Note the naming mismatch for whoever builds it: §11.1 and §4.4 call this
component **`ao-egress-archive`**; the LEDGER-04 acceptance criteria call it
**`ao-archive`**. Use **`ao-egress-archive`** — it is the name used in the
architecture, the network table (§11.1), and the approved-path table (§4.4).

When it is built, credential handling is **presence-only**: prove an entry
exists by name and non-zero length, never print, copy, or export the value.
No replication test has been run and none was run this session — it requires
credentials and is a stop condition.

## 11.7 Corda 5 Node Build Status and Blockers

**The node is not built. No Corda 5 node exists, and none can be built by an
agent session.** The artifacts are present and verified, but the remaining steps
are operator-only key ceremonies (§11.2, README §4.1 rule 14).

### What is verified in place

```text
$ sha256sum -c corda-combined-worker-5.2.2.0.jar.sha256sum   # in data/corda-install/
corda-combined-worker-5.2.2.0.jar: OK
```

Corda 5.2.2 worker JAR, CLI installer, and notary plugin are staged in
`data/corda-install/` with checksum sidecars. The Corda 4.14.2 / H2 installation
was retired on 2026-09-29 under operator approval — see
`logs/operations/2026-09-28-corda4-retirement.md`.

### Correction to the bootstrap runbook — service account name

`docs/runbooks/ledger-bootstrap.md` says the service account is
`alwayson-ledger`. **That is wrong**, and an agent that trusts it will build the
node under the wrong identity or wrongly conclude the account is missing. The
account exists as **`ao-ledger`**:

```text
$ getent passwd ao-ledger
ao-ledger:x:994:974:ALWAYS ON ledger core service:/home/alwayson-ledger:/usr/sbin/nologin

$ getent passwd alwayson-ledger ; echo $?
2
```

`alwayson-ledger` is the **home directory**; `ao-ledger` is the **username**.
Two further claims in that same runbook block are also false — "linger enabled"
and "systemd user unit installed" — and the consequence is that its step 5 cannot
succeed even after the name is corrected. See **§11.10**.
`/home/alwayson-ledger` is not readable by the operator's own `scottw` account,
so a direct `ls` returns `Permission denied`. That refusal is correct behaviour,
not a missing account — do not "fix" it by loosening the mode or by running the
node as `scottw`. Note also that the retirement log (`…corda4-retirement.md`)
already used `alwayson-ledger` for uid 994, so this same error is present there.

### The blocking conditions, in order

1. **Ledger keys (LEDGER-01).** The TLS certificate chain and keystores for the
   Corda 5 cluster require the operator to hold the passphrases in KWallet under
   `ao-ledger`. An agent must not generate, export, or activate production ledger
   keys. **Stop condition.**
2. **The `cordadb` owner role password (LEDGER-02, LEDGER-07).** The `corda`
   role has no working password, so `preinstall check-postgres` cannot pass.
   Resetting a role password is a credential change. **Stop condition.**
3. **The encrypted worker config.** Produced by `corda-cli.sh config encrypt`
   from operator-held secrets and installed `0600`. It cannot be generated
   without the operator's key material.
4. **Linger is not enabled for `ao-ledger`, and no `ao-ledger-core.service`
   unit file exists.** Not credential work, but the runbook's start command
   cannot succeed without them. Measured and detailed in §11.10.

Until step 1 completes, the node cannot be created, the ledger is **not
production-ready**, and no receipt, entitlement, or provenance record can be
final (§11.2.3).

### What could not be verified unprivileged

Database state could **not** be measured this session. Both PostgreSQL paths are
closed to the agent account, and neither failure means the database is absent:

```text
$ psql -tAc 'select 1'
psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed:
FATAL:  role "scottw" does not exist

$ sudo -n -u postgres psql -tAc "SELECT count(*) FROM pg_tables WHERE schemaname='public';"
sudo: interactive authentication is required
```

The "0 tables in `cordadb`" claim in §19 for LEDGER-07 is therefore **carried
forward from §19 and NOT re-verified here**. It should not be repeated as
established fact until the operator runs:

```bash
sudo -u postgres psql -tAc "SELECT count(*) FROM pg_tables WHERE schemaname='public' AND tablename NOT LIKE 'pg_%';"
sudo -u postgres psql -tAc "\du corda"   # inspect role state; do not print the password
```

### The node build is native, not containerised — and that is deliberate

Corda 5 ships no official container image. Ledger core therefore runs as a native
systemd user unit for `ao-ledger`, bound to loopback PostgreSQL. This is a
**documented deviation** from the Podman-and-Quadlet-only rule (README §4.1 rule
5) and is the single place it applies. It is recorded here so it is not later
mistaken for an oversight. It widens **no** listener and uses **no**
`--privileged`; the node is not reachable from any workload network. The two
`ao-ledger-core` and `ao-ledger-ingest` Quadlet networks are nevertheless
defined in `quadlet/networks/` and remain `Internal=true`, ready for the
gateway.

---
## 11.8 Second-Pass Verification, 2026-10-04 (LEDGER session)

Every factual claim in §11.7 was **re-measured** this session rather than carried
forward. All of it reproduced: the worker JAR checksum is `OK`, `ao-ledger` is
uid 994, `alwayson-ledger` is not a username, and no Corda node unit exists.

**Measuring "does the ledger unit exist?" — use `LoadState`, not `is-active`.**

```text
$ systemctl --user is-active ao-ledger-core.service
inactive                                  # exit 4  -- MISLEADING

$ systemctl --user show ao-ledger-core.service \
    -p LoadState -p ActiveState -p FragmentPath
LoadState=not-found
ActiveState=inactive
FragmentPath=
```

`is-active` prints the word `inactive` and exits 4 **both** when a unit does not
exist and when it exists but is stopped. Only `LoadState=not-found` with an empty
`FragmentPath` proves the unit was never installed. Here the truth is the latter:
**the ledger core was never built — it is not merely stopped.** Do not attempt to
start or enable it. (I hit this trap myself on the first check of this session.)

**Standing correction to §19 (LEDGER-07).** §19 states `cordadb` "holds 0 tables".
That figure remains **carried forward and unverified**. Neither the 2026-10-03
session nor this one could measure it — `psql` fails authentication for `scottw`
and `sudo -u postgres` requires interactive auth. An authentication failure is
**not** evidence that a database is empty, so §19's figure must not be restated
as established fact. To confirm:

```bash
sudo -u postgres psql -tAc \
  "SELECT count(*) FROM pg_tables WHERE schemaname='public' AND tablename NOT LIKE 'pg_%';"
sudo -u postgres psql -tAc "SELECT rolname, rolcanlogin FROM pg_roles WHERE rolname='corda';"
```

The second command deliberately selects no password column.
---

## 11.9 Producer-Key Coverage Gap in the Ingest Path (2026-10-04)

This section records a defect **not** previously documented, found by running the
ingest scripts rather than reading them. It concerns LEDGER-03
("ingest accepts only approved signed data") and is a prerequisite for the
gateway build. `scripts/` is not my file, so this is a **report, not a fix**.

### Finding 1 — only 2 of the 6 authoritative domains can sign

§11.1 makes six domains authoritative operational data that feeds the ledger:
Sales, Payment, Field, Mapping, Vehicle simulation, Fabrication simulation.
`sign-manifest.sh` can obtain a key from KDE Wallet for exactly **two** of them:

```text
$ grep -oP 'wallet:ao-[a-z-]+' /ALWAYSON/scripts/ledger/sign-manifest.sh | sort -u
wallet:ao-sim-fabrication
wallet:ao-sim-vehicle
```

The mapping is a literal `case` with two arms. **Sales, Payment, Field and
Mapping have no wallet-backed signing path at all.** A manifest from those domains
can only be signed with a private-key *file path*, which is exactly the path the
script labels "for migration/testing". Since Sales is the domain that actually
produces the `sales_receipt` object type, the strongest provenance guarantee in
§11.2.2 is currently unavailable for the record type that matters most.

### Finding 2 — an unsupported wallet key fails with a misleading error

```text
$ bash /ALWAYSON/scripts/ledger/sign-manifest.sh manifest.json wallet:ao-sales
ERROR: manifest or key missing (keys live in KDE Wallet ao-sim-*; file path accepted for migration/testing)
EXIT=10
```

The `case` falls through, `wallet_key` stays empty, and the literal string
`wallet:ao-sales` is then tested as a **file path**. The operator is told a file is
missing when the real problem is that this wallet key is unimplemented. Exit `10`
is indistinguishable between the two causes.

### Finding 3 — `origin_domain` is never validated

`build-manifest.sh` validates `object_type` against a closed `case` list but
passes `origin_domain` straight through to `jq`:

```text
$ bash /ALWAYSON/scripts/ledger/build-manifest.sh map_product TOTALLY_MADE_UP_DOMAIN p.txt ref://x | jq -r .origin_domain
"TOTALLY_MADE_UP_DOMAIN"
EXIT=0
```

An invented domain is accepted and stamped into the manifest. Since
`origin_domain` drives the §11.1 authority decision, an unvalidated value means a
manifest can claim authority it does not have. It must be validated against the
closed §11.1 set at build time **and** re-derived from the authenticated mTLS
identity at the gateway, never trusted from the body.

### Finding 4 — the staged queue already contains unverified-key material

One manifest is staged from 2026-08-24:

```text
$ jq -r '{producer_key_id, authorization_policy_id, sig_len:(.signature|length)}' \
    /ALWAYSON/artifacts/pending-ledger-submissions/20260824/manifest.json
{ "producer_key_id": "test", "authorization_policy_id": "", "sig_len": 96 }
```

`producer_key_id` is `"test"` and `authorization_policy_id` is empty — neither
identifies a registered producer. Confirmed again this session that staging
performs **no** cryptographic check: a manifest with a fabricated signature and an
invented `producer_key_id` was accepted and staged, exit `3`.

**I created that test manifest and have removed it.** The 20260824 manifest is
pre-existing project data and was left untouched. Nothing was signed, transmitted,
deleted from the project, or written to any external system.

### What this means for LEDGER-03

§11.2 requires signature verification against the exporter's **registered** key. As
written, the producer-key model cannot satisfy that for four of six domains, and
`producer_key_id` is self-asserted rather than registered. The gateway must not be
built on the assumption that a non-empty `signature` implies an authorised
producer. Recommended, for the operator — each needs approval since keys and
credentials are a stop condition:

1. Provision wallet entries for `ao-sales`, `ao-field`, `ao-mapping` (and
   `ao-payment` if it submits directly) and extend the `case` in
   `sign-manifest.sh`. **Credential work — operator only.**
2. Make an unrecognised `wallet:` argument fail with its own distinct exit code,
   not by masquerading as a missing file.
3. Validate `origin_domain` against the §11.1 closed set in `build-manifest.sh`.
4. Treat everything in `pending-ledger-submissions/` as **untrusted replay input**;
   the 20260824 entry with `producer_key_id: "test"` must not be auto-submitted
   when the gateway comes up.

---

## 11.10 Third-Pass Verification, 2026-10-04 (LEDGER session)

§11.7, §11.8 and §11.9 were re-measured from scratch rather than trusted. Every
inherited claim **reproduced** — see the ledger in
`agents/COORDINATION/proposals/ledger-LEDGER-0*.md` for the raw command output.
This pass adds one thing the previous two missed: **§11.7 understates the
blockers.** It lists three. There are at least five, and the two added here are
not credential work.

### The bootstrap runbook's "State after scaffold" is wrong in two places

`docs/runbooks/ledger-bootstrap.md` opens with a block asserting completed state.
Two of its four assertions are false, and both were carried forward unchallenged
by the first two passes, which checked only the account **name**:

```text
# Runbook line 4:  "- Service account `alwayson-ledger` (linger enabled)"
$ loginctl show-user ao-ledger -p Linger
Failed to get user: User ID 994 is not logged in or lingering

$ loginctl list-users
 UID USER   LINGER STATE
1000 scottw yes    active
1 users listed.

# Runbook line 9:  "- systemd user unit installed: `ao-ledger-core.service` (**not started**)"
$ systemctl --user show ao-ledger-core.service -p LoadState -p FragmentPath
LoadState=not-found
FragmentPath=

$ systemctl --user list-unit-files | grep -iE 'ledger|corda'   # no output, rc=1
$ systemctl list-unit-files          | grep -iE 'ledger|corda' # no output, rc=1
$ find /etc/systemd /usr/lib/systemd ~/.config/systemd \
       -iname '*ledger*' -o -iname '*corda*'                     # no output
```

**Finding A — linger is not enabled.** The runbook says it is. `ao-ledger` does
not appear in `loginctl list-users` at all, and there is no runtime directory for
it:

```text
$ ls -d /run/user/994
ls: cannot access '/run/user/994': No such file or directory
```

**Finding B — no unit file exists anywhere.** The runbook's parenthetical
"(**not started**)" implies an installed-but-stopped unit. That is the same
`is-active` misreading §11.8 warns about, committed to a document: a reader is
told to run `systemctl --user enable --now`, which cannot work because there is
nothing to enable. Only two `ao-ledger` files exist in `quadlet/`, and both are
`.network` files — no `.service` and no `.container`:

```text
$ find quadlet -iname '*ledger*'
quadlet/networks/ao-ledger-core.network
quadlet/networks/ao-ledger-ingest.network
```

### Why this matters more than a naming typo

§11.7 records the wrong-account finding as "an agent could build the node under
the wrong identity". Measured, it is worse: **the runbook's step 5 cannot
succeed even after the name is corrected.**

```bash
# Runbook lines 33-35, as written:
sudo -u alwayson-ledger env HOME=/home/alwayson-ledger \
  XDG_RUNTIME_DIR=/run/user/$(id -u alwayson-ledger) \
  systemctl --user enable --now ao-ledger-core.service
```

`id -u alwayson-ledger` exits 1 and prints nothing, so the substitution collapses:

```text
$ id -u alwayson-ledger
id: 'alwayson-ledger': no such user        # stdout empty
$ echo "XDG_RUNTIME_DIR=/run/user/$(id -u alwayson-ledger 2>/dev/null)"
XDG_RUNTIME_DIR=/run/user/                 # trailing slash, no uid
```

Fixing only the name is still not enough, because `XDG_RUNTIME_DIR=/run/user/994`
does not exist either (§Finding A). Without linger there is no `systemd --user`
instance for `ao-ledger` at all, so `systemctl --user` under `sudo -u ao-ledger`
has no bus to talk to.

**So LEDGER-07 has a fourth blocker that is not a key ceremony:** enable
linger for `ao-ledger`, and write the `ao-ledger-core.service` unit file. Neither
is credential work, but enabling linger for a service account **creates a
persistent background session that survives logout**, which is an access-control
change to a service identity — I am not making it, and it needs operator sign-off.
It is also **outside my ownership**: `docs/runbooks/` is not my file.

The `quadlet/networks/ao-ledger-{core,ingest}.network` files *are* real and
`Internal=true`, matching `config/platform/network-cidrs.yaml:8-9`. §11.7 is
correct on that point, and the networks are definitions with no container
attached — consistent with "the node was never built".

### What I got wrong in this pass

I intended to re-verify the inherited claims and found nothing new, because I
began by checking the account **name** — the one thing two prior sessions had
already found. Re-reading the runbook line by line instead of grepping it for
the known-wrong token surfaced two assertions nobody had checked, including one
that is self-refuting: the runbook tells you to enable a unit it also says is
"not started", while `list-unit-files` shows no such unit. **A document that
states completed state must be verified field by field; grepping it for the
token you already know is wrong tells you nothing new.**
---

## 11.11 Fourth-Pass Verification, 2026-10-04 (LEDGER session)

Three prior passes re-verified the *same* inherited claims and found the same
blockers. This pass deliberately changed method: instead of re-running the
recorded checks, I **executed the ledger scripts against a throwaway key in
`/tmp`** and read what the tooling actually does, rather than what it says it
does. That surfaced **four new defects**, none of which is credential work and
none of which any prior pass found.

The inherited claims all still reproduce — see
`agents/COORDINATION/proposals/ledger-LEDGER-0*.md`. What was missing is that
**"the ingest path has no signature verification" (§11.8/§11.9) undersells the
problem.** The signature that exists is not verifiable by its intended recipient,
the staging queue can silently destroy records, and the manifest carries none of
the correlation identity §11.2.1 declares mandatory.

### Finding A — the signature does not cover the signed file (NEW, most serious)

`sign-manifest.sh:33` hashes the manifest, and `:36` signs the **digest**, then
`:41-42` **rewrites the same file** to embed `producer_key_id` and `signature`.
So the artifact that is signed and the artifact that is delivered are different
bytes:

```text
$ B=$(sha256sum m.json | awk '{print $1}')   # before signing
0c7ac6ba098c736c601112a352eb9a5e2b3dddb9c4d034316b7bc7364e7c9600
$ bash scripts/ledger/sign-manifest.sh m.json /tmp/.../k.pem   # ephemeral throwaway key
OK: detached signature at m.sig and embedded in manifest (digest 0c7ac6ba...)
$ A=$(sha256sum m.json | awk '{print $1}')   # after signing
d240030093a1acfd82e3b2908a4911b0beb271dbc9b8815c06326e2d1a76b76b
DIFFERENT -- signature does not cover the delivered file
```

The signature is valid, but only over the *pre-signature* digest:

```text
$ openssl pkeyutl -verify -pubin -inkey <(openssl pkey -in k.pem -pubout) \
    -rawin -in d.txt -sigfile sig.bin
Signature Verified Successfully
EXIT=0
```

**And the recipient cannot reproduce that digest.** Stripping the two injected
fields does not round-trip, because `jq` re-serialises and the original came
from `jq -n` with different key order/indentation:

```text
$ jq 'del(.producer_key_id,.signature)' m.json > re.json
$ sha256sum re.json
6efd1830b0957a7a9eb1ffcbb787cfc91900a84faf65f231694b578a2165e2b9
DOES NOT ROUND-TRIP -- recipient cannot reproduce the signed digest
```

The digest is printed to stdout and stored **nowhere in the manifest**. So a
gateway given only `manifest.json` has no way to verify it. Concretely, a field
tampered after signing is undetectable from the file alone:

```text
$ jq '.local_storage_reference="refA_TAMPERED"' m.json > t.json
signature UNCHANGED after content tamper
```

**Recommendation, for the operator.** Canonicalise: hash a fixed byte sequence
of the *fields to be signed*, sign that, and store the signed digest **inside**
the manifest as e.g. `signed_payload_sha256`. Verification then re-canonicalises
and compares. This is `scripts/` — **not my file, report only, no fix applied.**

### Finding B — the staging queue is keyed on filename and silently loses records

§11.2 requires **idempotency and replay defence**. `submit-ledger-event.sh:10-11`
stages by `$(date -u +%Y%m%d)/<basename of input>`, so the de-duplication key is
whatever the caller happened to name the file. Two *different* signed manifests
with the same filename collide:

```text
# 1st: telemetry_batch / field  -> staged
after 1st: telemetry_batch/field
# 2nd: map_product / mapping, same filename, submitted
after 2nd, DIFFERENT manifest, SAME filename: map_product/mapping
>>> first manifest is GONE. Silent data loss in the staging queue.
```

Also: `install` is used with no mode, so staged manifests land **`0755`** —
world-readable — rather than the `0600` a ledger artifact should carry:

```text
$ stat -c '%a %U %n' .../20260824/manifest.json
755 scottw /ALWAYSON/artifacts/pending-ledger-submissions/20260824/manifest.json
```

This also refines §11.9 Finding 4: the pre-existing `20260824` manifest is
world-readable, which matters more once a replay tool exists. Recommend keying
on `object_id` and `install -m 0600`.

### Finding C — no idempotency key exists even in principle

Two submissions of the *same* `object_id` both succeed and both stage (the file
is overwritten in place, so the count stays at 1 — but nothing rejects the
duplicate, and nothing records that it was seen). There is no replay ledger, no
`correlation_id` uniqueness constraint, and no audit record of a submission
attempt. §11.2 row 5–6 ("Idempotency", "Audit logging") is **entirely
unimplemented**; the staged file is the only trace.

### Finding D — the manifest carries none of the mandatory correlation tuple

§11.2.1 names `serial_number + receipt_number + event_timestamp_utc` as *the*
primary correlation tuple, and §11.3 lists `correlation_id`, `serial_number`,
`receipt_number` in required Corda state. But `build-manifest.sh` emits:

```text
$ jq -r 'keys_unsorted|join(" ")' m.json
object_id object_type origin_domain created_at_utc schema_version
content_hash_sha256 content_size_bytes local_storage_reference ipfs_cid
pcloud_archive_reference transaction_id authorization_policy_id
producer_key_id signature

correlation_id           false
serial_number            false
receipt_number           false
event_timestamp_utc      false
event_type               false
```

None of the §11.2.1 fields are present, and `transaction_id` is `null` unless
the object type is `sales_receipt`. **§11.5's manifest format is missing them
too** — so this is a specification gap, not just a script gap. A ledger built on
today's manifest cannot be joined by the correlation tuple that §11.2.1 defines
as the join key for reporting and reconciliation. Recommend adding the five
fields to both §11.5 and `build-manifest.sh`, with the domain-appropriate ones
required (not nullable).

### What this means for LEDGER-03

LEDGER-03 asks that ingest "accept only approved signed data, with
authorization, idempotency, replay defence, and audit". Measured against the
current tooling, **all five are absent**: authorization is a non-empty-string
test (§11.8), signature verification is absent *and* the signature is
unverifiable by the recipient (Finding A), idempotency is absent (Findings B,
C), replay defence is absent, and audit is a directory listing. LEDGER-03
cannot be closed by writing gateway code on top of this manifest format —
**Findings A and D must be fixed in the format first.**

### Housekeeping

The ephemeral Ed25519 key and all test manifests were created under `mktemp -d`
and have been removed. Three manifests I staged today
(`m.json`, `manifest.json`, `collide.json`) were deleted;
`artifacts/pending-ledger-submissions/` again contains **only** the pre-existing
`20260824` directory. Nothing was signed with, or read from, any project or
ledger key; no file outside my own section was modified; nothing was transmitted.

### What I got wrong in this pass

My first instinct was to re-run the recorded checks a fourth time, because that
is what the previous three passes did and they all reproduced. That produces
completeness, not information. The three findings that mattered came only from
*running* the scripts with an input no prior pass had tried — a throwaway key, a
filename collision, and a `keys_unsorted` dump. **Verifying that a recorded
claim still holds is worth doing once; doing it again is how three passes in a
row all concluded "nothing new".**

---

## 11.12 Fifth-Pass Verification, 2026-10-05 (LEDGER session)

Four passes had re-measured the host. This pass audited the **documents I own for
internal consistency**, which no prior pass did, and validated candidates against the
real schema rather than reading it. All three findings are new and are proved by
execution.

### Method note — validate, don't read

`jsonschema` 4.26.0 is available on this host, so a candidate manifest can be tested
against `config/ledger/manifest-schema.json` for real:

```text
$ python3 -c 'import importlib.metadata as m; print(m.version("jsonschema"))'
4.26.0
```

Reading the schema says it has `additionalProperties: false`; validating says which
payloads are *rejected*. The second is evidence.

### Finding A — §11.3.1's posting model has no carrier in the wire format

§11.3.1 defines a posting leg as carrying `account_code`, `side`, `amount`, `currency`,
and `correlation_id`, and §11.5 defines the manifest as the thing submitted to the
gateway. **The manifest format cannot express a posting at all.** Validated:

```text
--- 11.3.1 posting leg (DR CASH_EU 10000 EUR): REJECTED
     Additional properties are not allowed ('account_code', 'amount',
     'correlation_id', 'currency', 'side' were unexpected)
```

None of those five fields appears anywhere in the schema:

```text
$ for k in account_code side amount currency correlation_id; do
      printf '%-16s %s\n' "$k" "$(grep -c "\"$k\"" config/ledger/manifest-schema.json)"; done
account_code     0
side             0
amount           0
currency         0
correlation_id   0
```

This is **worse than §11.11 Finding D**, which found that the correlation tuple is
missing from the manifest. Finding D meant reporting could not join by the tuple. This
means the accounting model §11.3.1 defines has **no object that could ever carry it** —
so §11.3.1 is currently a specification with no implementation surface. §11.5 needs a
posting-leg array, or a distinct posting object type; neither exists. This is a
specification change to §11.5 and to `config/ledger/`, and §11.5 is mine but
`config/ledger/manifest-schema.json` is **not** — so the schema half is reported, not
done.

### Finding B — corrections are unexpressible, so §11.3.1's immutability rule has no mechanism

§11.3.1 requires that a correction be "a **new reversing transaction** referencing the
original `transaction_id`", and that history is never edited or deleted. There is no way
to represent a reversing transaction:

```text
--- 11.3.1 reversing transaction (object_type=reversal): REJECTED
     'reversal' is not one of ['sales_receipt', 'telemetry_batch', 'map_product',
      'vehicle_simulation', 'fabrication_simulation']

--- 11.3.1 correction referencing original: REJECTED
     Additional properties are not allowed ('transaction_ref' was unexpected)
```

So the rule is stated but has no object type and no reference field to implement it
with. An implementer following the schema literally cannot correct a posting at all —
they would have to edit or delete, which the same paragraph forbids. This is the
sharpest form of the §11.2.5 minimization tension: `additionalProperties: false` is
correct for PII minimization, but it also forbids every legitimate bookkeeping field.

### Finding C — `TAX_PAYABLE_<jurisdiction>` is defined but unreachable

The account table declares `TAX_PAYABLE_<jurisdiction>`, but **no row in the posting
rule may post to it**. In the posting-rule table (§11.3.1) the code appears exactly
once, and it is the account-table row that defines it — not a posting row. Measured
before this section was added, so that no self-reference inflates the count:

```text
$ grep -n 'TAX_PAYABLE' agents/COORDINATION/11-ledger-provenance-archive-and-ipfs/section.md
528:| `TAX_PAYABLE_<jurisdiction>` | Liability | Tax accrued and owed, per approved jurisdiction |
```

§11.3.1 also states "Corda … cannot … decide tax". Both can be true — Corda records
accrued tax, it does not compute it — but as written the account is unreachable, so no
tax accrual can ever be posted and no tax liability can appear in the §4.4 report. I
have **not** invented a tax posting rule: tax rates, jurisdictions and accrual timing
are pricing and financial-policy decisions belonging to §7.2 and the PAY group, and
setting them is a money-movement-adjacent decision. **Reported, not decided.**

### What I corrected in this pass

Finding A also exposed two defects **inside §11.3.1 itself**, which are mine to fix and
are fixed: the posting table used `CASH_*`, `RECEIVABLE` and `REVENUE`, none of which
are account codes in the table directly above it (`RECEIVABLE` and `REVENUE` do not
exist; the codes are `RECEIVABLE_CUSTOMER`, `REVENUE_SALE`, `REVENUE_DIGITAL_TRANSFER`).
The "Funds transfer verified" row also offered "RECEIVABLE **or** REVENUE", which is
ambiguous where the balance invariant requires one answer. The DR/CR columns of two
rows were also presented credit-first. All five rows now name real codes in DR-then-CR
order, each a balanced pair, and the shorthand defects are recorded here rather than
silently repaired.

### What I got wrong in this pass

My first instinct was, again, to re-run the recorded host checks — that is what four
prior passes did and all four reproduced. I stopped, because §11.11 had already written
down the lesson and I was about to repeat the mistake it describes. The three findings
came from asking a question nobody had asked: **not "is the host in the documented
state?" but "does the specification I own agree with the artefacts it governs?"** The
host was fine in all four passes. The documents were not, and no amount of
`sha256sum -c` would have found it.

Equally, I nearly reported Finding C as a defect and stopped one step short of asking
*whose* decision a missing tax rule is. It is not mine. An agent that "helpfully"
invents a tax accrual rule here would be making a pricing decision it has no authority
to make (README §4.1 rule 14).