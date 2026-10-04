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
| Funds transfer verified | `CASH_*` DR / `RECEIVABLE` or `REVENUE` CR | **All three** §11.2.2 gates |
| Entitlement issued | `RECEIVABLE_CUSTOMER` DR / `REVENUE_SALE` CR | Sale confirmed on the ledger |
| Post-sale transfer authorised | `REVENUE_DIGITAL_TRANSFER` CR | `ao-sales` authorisation (§11.6) |
| Refund approved | `REFUNDS_PAYABLE` CR / `CASH_*` DR | Explicit operator approval |
| Archive replication cost | `EXPENSE_ARCHIVE` DR / `CASH_*` CR | Verified provider cost |

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
