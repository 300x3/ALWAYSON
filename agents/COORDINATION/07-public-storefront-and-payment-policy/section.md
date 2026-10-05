# 7. Public Storefront and Payment Policy

## 7.1 Storefront Boundary

The public storefront is static HTML hosted in the pCloud Public Folder. It carries no
secrets, no local ports and no internal hosts. What it may and must never contain is listed in
§7.1.1.

## 7.1.1 Frontend Website Details

Source is the [HTML-300X3](https://github.com/300x3/HTML-300X3) repository. It publishes as
a **single self-contained `index.html`** — one page, no build-time subpages. The sections
below are regions of that page; each catalog entry is a `data-item` JSON payload rendered
into a modal.

```text
www.300x3.com
└── index.html                       the entire site, ~85 KB, self-contained
    ├── MAIN PAGE                    hero, project introduction, status highlights
    │   └── navigation to every section below
    ├── EQUIPMENT                    Camping (Walk&Car) Essentials · Adapter · Boiler
    │   │                             Pneumatic Speargun Ulu · Structural Battery
    │   │                             Appliances · Computer
    ├── BUILDINGS                    Furniture · ADU (80sf and up) · Mall · Tower
    │                                 Concrete Island
    ├── VEHICLES                     Drone (air/land/sea) · Boat (micro modular
    │                                 aircraft carrier) · Personal Vehicle
    │                                 Electric Car Wheel · Balloon
    ├── DIGITAL                      Images (Reality Capture) · Topography (3D points)
    │                                 Route Around Your County (turn-by-turn)
    │                                 Where's My ______? (telemetry)
    ├── DISCUSSION                   Forum (Mastodon) · RNS MeshChatX (+LoRa)
    ├── DOCUMENTATION                 Introductory Video · Project Plan (Working PDF)
    │                                 Server Coding · 3D Models · Heads Up Display App
    │                                 Simulations · AI Systems · Hardware · Software
    │                                 Fabrication · Raw Material
    ├── DONATE                       PayPal button; Zelle; Coinbase / stablecoin;
    │                                 other — customisation at 300X3@POSTEO.NET
    ├── KIT REQUEST                  written request form, composed to the operator
    └── CHAT                         OpenClaw assistant panel, exposes no infrastructure
```

The publish folder holds exactly two files:

```text
PCLOUD-PUBLIC/***CURRENT***/site/
├── index.html                       the site
└── alwayson-single-topology.html    the topology viewer (ES.2)
```

Catalog entries are modal payloads inside `index.html`, not directories. Every Equipment,
Buildings and Vehicles entry carries the sales action below. `§7.1.2` lists the additional
live views specified for the product modals that are not in this build.

### Order of follow-up, support, and chat links

The order below is deliberate and is the order presented on the page:

1. Follow-up — order status and follow-up links.
2. Support — support request and help links.
3. Chat — AI-assisted support entry point (OpenClaw), which exposes no private
   infrastructure.

Mastodon/community links follow these three.


### Sales-link integration plan

Each catalog modal under Equipment / Buildings / Vehicles gets a sales action
that stays inside the static-site boundary (no secrets, no local ports, no
internal hosts — see Section 7.1 prohibitions):

1. Modal shows product images, parts list / detailed drawings link, pCloud
   folder link, and IPFS digital-asset mark where applicable.
2. A purchase button routes to provider-hosted checkout (PayPal hosted button
   today; Zelle instructions and Coinbase/USDC flow per §7.2 as
   if built) or to a `mailto:300X3@POSTEO.NET` order-request template
   carrying product name, options, and quantity.
3. Checkout completion returns a provider-signed event (or manual
   reconciliation record for Zelle/wire) into the Section 7.3 sales and
   receipt sequence; Corda records the receipt/entitlement state per
   Section 11.
4. No payment-card data, webhook secrets, OAuth tokens, or ledger keys ever
   appear in the static HTML, pCloud folder, or Git history.



The public site may include:

- Product catalog and documentation.
- Hosted payment checkout links.
- Provider-controlled payment buttons.
- Order follow-up links.
- Support links.
- Chat: AI-assisted support entry points that do not expose private infrastructure.
- Mastodon/community links.
- Shipping, return, warranty, privacy, and legal content.

The public site must never include:

- Payment-provider secret keys.
- Corda keys, RPC credentials, or node addresses.
- Mastodon OAuth tokens.
- pCloud archive credentials.
- IPFS private keys or swarm keys.
- Local hostnames, LAN addresses, Podman ports, or private API routes.
- Database connection strings.
- Drone radio configuration, control endpoints, or flight-control access.
- Internal service certificates, identifiers, or diagnostic output.

### 7.1.2 Live HTML Views for Product Modals

These are the **live HTML views on the product modals** of the storefront. This table is the
requirement list for each one, not a status report.

Every view below must satisfy the same boundary as the rest of §7.1: the public
site carries only public content and interactive iframe content from other
servers, and never a local hostname, LAN address, Podman port, or private API
route (§7.1 prohibitions; ES.1 "Static HTML & interactive iframe content from
other servers"). The Instructables view is the straightforward case — it is an
outbound link and a static image. The remaining eight are not, and that is the
substance of the constraint column.

| # | View | Placement | What it shows | Requirement and constraint |
|---|---|---|---|---|
| 1 | **Instructables — fabrication directions** | Bottom-right of **each** product modal | The robot picture, linked to the operator's Instructables member page. **Not** the "Autodesk Instructables" wordmark | No image asset may be fetched or substituted: the operator supplied an Instructables logo SVG and specified *not* to use it |
| 2 | **MeshChatX — network visualizer** | Modal window area | The Reticulum network stack visualizer, live, plus a direct-messaging entry point | MeshChatX is `https://127.0.0.1:18000/`, loopback-only and **not a public ingress** (§9.2.1), so it cannot be iframed. It must be a static export, an approved published view, or an existing external public visualizer |
| 3 | **IPFS/pCloud — route orthotiff** | Maps / digital | WebODM-processed orthotiff along the 300X3 route, the full way around the county, as a **free download including route times and telemetry data** | A public download must carry no internal host, port, or path; check against §4.2 before publication |
| 4 | **Trimble — San Vicente Reservoir point clouds** | Maps / digital | Point-cloud viewing of the reservoir, from a processed WebODM topography | Requires a completed WebODM task for the reservoir (§8) |
| 5 | **LocusMap** | Maps / digital | Downloadable route around San Diego County in the LocusMap format | Format and licensing of the published tile set must be confirmed before any public link |
| 6 | **Mapbox** | Maps / digital | Mapping tiles, San Vicente Reservoir | Requires a Mapbox account and an access token held **outside** the repository. A public browser token is publishable by design; a secret-classified token is not (§4.2, §7.1) |
| 7 | **Mastodon — live forum** | Discussion | A live forum view inside the modal | `mastodon.social` refuses to be framed, and that refusal is enforced by the remote. The local instance UI is `https://127.0.0.1:3300/`, loopback-only, so it is not a substitute without a new approved public entry |
| 8 | **Gazebo/Foxglove — simulation** | Modal, three views | Kitchen; storage/CNC; vehicle | Both origins are loopback-only (sim console `127.0.0.1:8099/sim`, Gazebo portal `127.0.0.1:8765/` and its `/viewer` 3D view, §5.1.2), as is the bridge on `127.0.0.1:8081`. A live embed is a new public entry requiring explicit operator approval under §4.1 rule 6, and depends on §19.1 |
| 9 | **Trimble SketchUp — grid of 3D views** | Modal grid | The SketchUp model views | SketchUp is a desktop/paid service; what may be linked or embedded publicly must be confirmed before use |

**No public port is opened by this section.** Rows 2, 7 and 8 each require explicit operator
authorisation before any live view is published, and none of them may be satisfied by
publishing a loopback address. Which rows are built is status and is recorded in §19.1 and
§19.1.

### 7.1.3 Build state of the nine views, 2026-10-03

**None of the nine views is built.** The storefront in the pCloud Public Folder
carries `index.html` and `alwayson-single-topology.html` only, and no asset,
export, route or embed for rows 1–9 exists in this repository or in the pCloud
site tree. The table above is a requirement list; it is not a status report, and
it must not be read as one.

Row 1 is the only row with no unresolved technical blocker — it is an outbound
link plus one operator-supplied image, and the constraint is a *negative* one
(do not substitute the Instructables wordmark). Rows 2, 7 and 8 are blocked by the
loopback-only rule and each needs an explicit operator authorisation for a new
public entry before it can be built at all. Rows 3, 4 and 5 are blocked on data
that must be produced and licensed first (§8 WebODM tasks, LocusMap tile terms).
Rows 6 and 9 are blocked on an external account or licence confirmation.

This is recorded as **OPEN**. Building rows 2, 7 or 8 would require opening a
public ingress, which is a §4.1 rule 6 stop condition and is reserved to the
operator; this session built none of them. This extends, and does not contradict,
the 2026-10-01 note in PAY-05: the three preconditions recorded there still hold,
and the remaining six rows are blocked for the per-row reasons above.

## 7.2 Payment and Settlement Policy

ALWAYS ON does not process, transmit, or store payment-card numbers, CVV
values, or payment-provider secret material in the storefront, sales database,
Corda, Git repository, logs, pCloud Public Folder, or IPFS.

There are three forms of payment processing:

| # | Form | Providers | Intended use | Required control |
|---|---|---|---|---|
| 1 | **Card / PayPal** | Hosted card checkout and hosted PayPal checkout | Standard online transactions | Provider-hosted checkout, signature-verified webhook, no local card handling |
| 2 | **Wire transfer / Zelle** | Wire transfer and Zelle | Approved high-value and direct-to-bank transactions | Manual reconciliation, operator approval, auditable reference record |
| 3 | **Coinbase / stablecoin (USDC)** | Coinbase or similar | Crypto/stablecoin settlement | Documented provider terms, accounting treatment, refund process, and explicit operator approval |

**In scope, decided, and closed as a policy question: PayPal, Zelle and Coinbase/USDC.**
This is the single normative statement of provider scope for the project. It was
settled when §7.2 was written and it is not open. Earlier wording elsewhere that
treats provider selection as undecided — ES.2's "deployable once the provider
decision is recorded (§7.2)" and ST-27's "open on payment-provider selection" —
refers to the *implementation* being gated, not to the choice being unmade, and
is corrected by this statement. Choosing the providers never authorised accepting
a payment: §4.1 rule 14 still requires explicit operator approval before payment
acceptance is enabled, and ST-12 remains the gate for that.

The default payment model is provider-hosted checkout; the provider is
responsible for card capture and authorization. The local payment verifier
accepts only provider-signed webhook events and stores normalized business state.

`ao-ingress-payment` exposes three webhook paths. Zelle publishes no webhook and
returns 501 on any inbound POST, so Zelle is verified by operator reconciliation
against the provider record. Coinbase is verified against the on-chain settlement
record. Bodies are capped at 256 KiB, only a SHA-256 hash and an opaque reference
are stored, and a raw payload is never persisted.

**Measured state of the automated verifier, 2026-10-03.** The verifier in
`scripts/payment/ao-payment-adapter.py` is *not* conformant with either provider
and must not be treated as a working control. Two defects, both proven by running
the adapter, are recorded as **OPEN**:

1. **The signature scheme is one PayPal does not produce.** The adapter computes
   `HMAC-SHA256(secret, transmission_id | transmission_time | raw_body)`. PayPal
   documents a different construction entirely: the message string is
   `transmissionId | timeStamp | webhookId | crc32` — the CRC-32 of the raw body,
   not the body — and it is verified with the RSA public key from the
   `paypal-cert-url` certificate, not a shared HMAC secret. Tested directly: a
   signature built on PayPal's documented message string is **rejected** by
   `verify_paypal`, and only the adapter's own non-standard construction is
   accepted. Consequence: as written the adapter would reject every genuine PayPal
   delivery. This fails closed, so it is not a money-loss risk, but it means no
   PayPal payment can be accepted and §7.2's "signature-verified webhook" control
   does not exist yet.
2. **Coinbase is verified with the PayPal verifier.** `AUTOMATED = ("paypal",
   "coinbase")` and both branches call `verify_paypal`. Proven over HTTP: a
   PayPal-style signed POST to `/webhook/coinbase` returns **200 accepted**, while
   a Coinbase event carrying its own `x-cc-webhook-signature` header returns
   **401**. `COINBASE_WEBHOOK_SECRET` is provisioned into `payment.env` by the
   wallet bridge but is **never read by any code**. The Coinbase path therefore
   admits PayPal-shaped events and rejects all real Coinbase events.

A third defect sits in the normalized event model rather than the verifier: for a
real PayPal `PAYMENT.CAPTURE.COMPLETED` payload the money is at
`resource.amount.value`, which `normalize()` does not read, so `amount_cents`
comes back `None` and the amount is silently lost. For Coinbase the
money-bearing reference is `charge.id`, which `normalize()` also does not read;
it falls through to the top-level **event** id, so the adapter records the event
that arrived rather than the charge being reconciled. A 2026-10-04 correction to
an earlier statement in this session: that reference is **not** empty, because a
real Coinbase payload does carry a top-level `id`, so the adapter does not reject
it with 400. The reference it records is simply the wrong one, which breaks
reconciliation without looking like a failure.

These are payment-verification defects. Correcting them changes how money-bearing
events are accepted, so the fix is prepared and reported for operator approval
rather than applied by this session.

### 7.2.1 Prepared verifier correction, proven offline 2026-10-04

The correction has been **written and proven, and deliberately not applied.** The
live adapter is unchanged — `scripts/payment/ao-payment-adapter.py` still hashes to
`sha256:71a74988b0731695f61a7d56d9580a3c8364a3371906fa333c1784638d399f58`, its
sha256 as measured before this work began, and the running service still answers
`{"ok": true, "enabled": true}` on `127.0.0.1:8899`.

PayPal's construction was re-read from the vendor rather than from the previous
session's notes. Per developer.paypal.com, "Integrate webhooks" → *Self
verification method*, the signed message is
`transmissionId | timeStamp | webhookId | crc32`, where `crc32` is the CRC-32 of
the **original raw body** in decimal, and the signature is checked with the
**RSA public key** from the certificate at `paypal-cert-url`. `webhookId`
arrives in **no header and no body** — it is listener configuration, which is why
the adapter could not have been correct as written.

The candidate was built in `/tmp` from a copy of the live file and proven two
ways. A unit harness generated a throwaway 2048-bit RSA keypair in-process, stubbed
the certificate fetch so the host allowlist and certificate-to-key extraction
still execute, and ran **18 of 18 checks**: the candidate accepts a
PayPal-documented signature and rejects a tampered body, a wrong `webhookId`, a
stale timestamp, an HMAC forgery in the adapter's *current* scheme, and two
non-PayPal certificate URLs. `verify_coinbase()` accepts a genuine Coinbase HMAC
and rejects a PayPal-shaped event.

The acceptance criterion — "A test payment event produces a verified normalized
record" — was then proven **end to end over HTTP** against the candidate on a
spare loopback port in `--dry-run`, so no row could be written:

| Step | Request | Result |
|---|---|---|
| 1 | Genuine PayPal event, PayPal-documented signature | `200 {"accepted": true}` |
| 2 | Same event, one byte of body tampered | `401 signature verification failed` |
| 3 | Genuine Coinbase event, HMAC over the raw body | `200 {"accepted": true}` |
| 4 | PayPal-shaped event to the Coinbase path | `401` — the 200-from-defect-2 no longer happens |
| 5 | Zelle POST | `501` — still manual-reconciliation only |

and the adapter's own log shows the normalized records it produced, carrying the
amount and currency that the live code drops:

```text
DRY-RUN (no DSN): event provider=paypal type=PAYMENT.CAPTURE.COMPLETED
  ref=paypal:3b97c70f1e963687d2da6dbd62f7d7bd amount_cents=50000 currency=USD verified=True
DRY-RUN (no DSN): event provider=coinbase type=charge:confirmed
  ref=coinbase:9871540c485e614b22a7e30fda45d736 amount_cents=1234 currency=USD verified=True
```

**This is prepared, not applied.** Approving it changes which money-bearing
events are trusted to create business state — README §4.1 rule 14 and the first
stop condition of this session's brief. Deployment also needs
`PAYPAL_WEBHOOK_ID` and `COINBASE_WEBHOOK_SECRET` as real configuration, and
`COINBASE_WEBHOOK_SECRET` is currently provisioned but read by nothing. The
operator decision requested is narrower than "fix the verifier": it is whether to
accept PayPal and Coinbase webhooks at all, because the honest consequence of
today's code is that neither provider can complete a payment.

**Independent re-verification, 2026-10-04.** The `/tmp` harness and candidate
referenced above were session-local and no longer exist on disk, so the candidate's
**18/18** result could not be re-run and is **not** re-claimed here. The three
defects it was built to fix *were* re-derived independently against the live file, and
all three reproduce:

- `verify_paypal()` returns `False` for a signature built on PayPal's documented
  message string (`transmissionId|timeStamp|webhookId|crc32`, with `crc32` the
  CRC-32 of the raw body in decimal) and returns `True` only for the adapter's own
  HMAC construction.
- `verify_coinbase` is **not defined** in the file, `AUTOMATED` still contains
  `coinbase`, and line 209 gates **both** webhook paths through the single
  `verify_paypal()`. `COINBASE_WEBHOOK_SECRET` is referenced **zero** times.
- `normalize()` returns `amount_cents: null` for both providers on realistic
  payloads.

One detail the earlier account did not record, found by re-running: **Coinbase's
`amount_cents` is also lost**, not only its `provider_ref`. A real `charge:confirmed`
carries the money at `charge.amount.amount`, which `normalize()` does not read, so it
returns `null` for the amount *and* records the top-level event `id` in place of
`charge.id`. Coinbase events therefore lose both the money and the reconciled
reference. Reproduced with a throwaway in-memory payload only; no secret, no live
request and no row was written.

**How each form is verified.**

| Form | Verification |
|---|---|
| Card / PayPal | The provider's signature on the webhook. **Not implemented conformantly — see the measured state above.** |
| Wire transfer / Zelle | The operator reconciles settlement against the provider record, because those channels publish no webhook |
| Coinbase / stablecoin | On-chain settlement against the wallet record. The webhook path is non-conformant — see the measured state above |

In every case the verification result, provider reference, amount, currency and UTC
verification timestamp are recorded before the transaction is documented in the ledger, so
that the three evidence gates in §11.2.2 resolve to the same correlation record.

Corda is not a payment processor. It never accepts cards and does not replace the payment
provider, banking, tax, consumer-protection, accounting or refund processing. It records
approved receipt, fulfillment, entitlement and provenance state **after** a payment event is
verified or manually reconciled, correlated to the PostgreSQL operational record per
transaction and per serial number (§3.3.b), and it must be queryable by the authorised
reporting services.

## 7.3 Sales and Receipt Sequence

### 7.3.1 Verified implementation state, 2026-10-03

Measured against the running system, not asserted.

**`salesdb` is live and initialized.** The database holds the 14 core tables named
in §15.1 plus `correlation_records`, `sale_contracts`, `sale_contract_lines` and
`sale_evidence` (18 base tables), and all five §15.1 roles exist with login. The
reporting boundary holds: `sales_reporting_role` holds `SELECT` on exactly the
five `v_reporting_*` / `v_corda_entry_readiness` views and on **zero** base
tables, which is the least-privilege property §6 requires. `sales_migration_role`
holds the full 161 grants needed to administer the schema. The relational half of
the sales pipeline is therefore real and correctly separated.

**The receipt-manifest chain works offline, end to end.** A structurally valid
receipt passes `scripts/validation/validate-sale-receipt.sh`; the same receipt with
a `card_number` field added is rejected with exit 13, so the sensitive-field gate
is live and not decorative. `scripts/ledger/build-manifest.sh sales_receipt` then
produces a manifest whose only fields are the content SHA-256, the content size,
an opaque local storage reference, the transaction ID and empty IPFS/pCloud slots —
verified to contain **no** customer, SKU, serial or card token, and its
`content_hash_sha256` equals `sha256(receipt)` exactly. `sign-manifest.sh` attaches
a detached Ed25519 signature over the manifest digest.

**A trap in that chain, measured.** The signature is computed over the digest of
the manifest *before* the signature is embedded into it, so the signature verifies
against the pre-signing digest and **fails against the final file**
(`Signature Verification Failure`, exit 1). That is self-consistent — signing a file
and then mutating it necessarily changes its hash — but there is no in-tree
verifier that knows to blank `signature` and `producer_key_id` before hashing, and
`grep` finds no `verify-manifest` script anywhere. A verifier written naively
against the final file will reject every validly signed manifest. **Whoever builds
the ingest-side verifier must hash the manifest with those two fields removed.**

Submission to `ao-ledger-ingest` is a separate gate and is **not** claimed here:
the gateway is not deployed and `submit-ledger-event.sh` exits 3 at staging, so
nothing left the host during this session.

**The Sales API does not exist.** §7.3 names a "Sales API and sales PostgreSQL"
as the component that turns a verified event into order, receipt, fulfillment and
entitlement state. There is no such service: no Quadlet unit, script or
configuration anywhere in the tree implements one. The only `ao-sales`
containers are `ao-sales-db` and the five Mastodon containers of §15.3, and
`ao-sales` is the network, not an application. **The step between a verified
payment event and an order/receipt/entitlement record is therefore missing**, and
nothing in the current build can create business state from a payment. This is
recorded as **OPEN**.

**The customer-facing PDF email path is half built, and the sending half does not
exist.** PDF generation is proven: `scripts/sales/intake-to-pdf.sh` runs end to
end and emits the intake record, the work order, and a 10-field fillable
AcroForm overlay, each verified at one page. There is **no mail path of any
kind** — `msmtp`, `sendmail`, `mailx`, `mutt`, `swaks` and `s-nail` are all absent
from the host, no SMTP configuration exists, and no script sends anything. The
existing path is deliberately one-way: its own header states "Nothing is sent
anywhere, no payment is taken, no order is created". So the three customer
messages §7.3 owes — purchase-request confirmation, receipt, and work-order
status with expected delivery — can be **generated** as PDFs but **cannot be
delivered**. Installing an MTA or configuring an SMTP relay is a credentials and
egress decision reserved to the operator, so this is **OPEN** pending approval.

**`ao-ingress-payment` is running but not reachable from the internet.** Both
`http://127.0.0.1:8899/health` and `http://127.0.0.1:8900/health` return
`{"ok": true, "enabled": true}`, and `ss -ltn` confirms all three listeners —
`127.0.0.1:8899`, `127.0.0.1:8900`, `127.0.0.1:15432` — are bound to loopback
only, so nothing is LAN- or internet-reachable. No Cloudflare Tunnel route
targets port 8900, so the approval gate on enabling the public route has not been
opened. Note that `"enabled": true` means the adapter holds a database DSN, which
contradicts ST-12's statement that it "runs with no DSN"; the credential finding
below explains why.

**Credential finding — `payment.env` was hand-written, not wallet-produced.** The
four `ao-payment` KDE Wallet entries do not exist (`hasEntry` returns `false` for
`payment-db-password`, `payment-paypal-webhook-id`, `payment-paypal-webhook-secret`
and `payment-coinbase-webhook-secret`; for comparison `ao-sales`/`sales-db-password`
returns `true`). Despite that, a `payment.env` exists, mode 0600, containing one
key, `PAYMENT_DSN`, whose password is **byte-identical to the `sales-db` wallet
password** (both 48 characters, identical SHA-256 prefix). So the file was created
by hand on 2026-09-30, it duplicates an existing secret rather than holding a
distinct payment credential, and it grants `ao-ingress-payment` the
`sales_migration_role` — the full 161-grant schema-admin role. That is a wider
privilege than a payment ingress adapter needs, and it is a §14.1 deviation
introduced outside the wallet bridge. The wallet bridge would overwrite this file
in a single composed pass if the entries existed; it does not. **Not remediated by
this session** — it touches credentials and would require rotating and re-scoping a
live secret. Recorded as **OPEN** for the operator.

### 7.3.2 Sequence

```text
Customer browser
      │
      ▼
pCloud static storefront
      │
      ▼
Provider-hosted checkout or approved wire-transfer request
      │
      ▼
Payment provider or reconciliation process
      │
      ▼
Controlled payment ingress adapter
      │
      ▼
Verified payment event
      │
      ▼
Sales API and sales PostgreSQL
      ├── Order record
      ├── Receipt record
      ├── Fulfillment state
      └── Entitlement state
              │
              ▼
Signed receipt manifest
              │
              ▼
Ledger-ingestion gateway
              │
              ▼
Corda receipt and entitlement state
```

The full flow is drawn in the master topology graphic in ES.2. The five numbered steps of
the sale chain — catalogue to checkout, verified payment event, `salesdb` record, signed
receipt manifest, and Corda state — are steps 1 to 5 in the highlighted column below,
which is that same graphic with the chain highlighted:

![Zoom of the full “what actually happens” column of the ES.2 master topology, at readable scale: sale chain, Corda state, CAD and model registry, correlation tuple, the 500GB photogrammetry drive, mapping ingest/process/export, and storage to shelf to robot.](assets/topology-detail-mapping.png)

*Figure 3.3.2 — A **zoom** of the catalogue-to-ledger chain from the ES.2 master
topology, enlarged so the labels are readable. It is a zoom of that one graphic, not a
second diagram.*

Two paths feed that chain, and both are in the same graphic. The **PDF intake path** runs
from `KIT REQUEST PDF intake` into `ao-sales` ("PDF requests in"), which is the public
storefront intake. The **website path** runs from the customer email inbox through the
Cloudflare edge and tunnel into `ao-sales` as a loopback origin. From there `ao-sales`
emits a **signed receipt manifest** into `ao-ledger-ingest`, which performs mTLS,
authorization, idempotency, and audit before passing an **approved state transition** to
`ao-ledger-core`. Ledger state reaches the reporting tools by two separate approved
routes, both drawn in the graphic: `ao-ledger-core` supplies status over a narrow API,
and `salesdb` supplies **read-only views** to Metabase.

---
