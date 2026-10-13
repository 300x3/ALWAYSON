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

## 7.3 Sales and Receipt Sequence

# negative controls, to rule out a hasEntry that always answers true:
payment-paypal-webhook-idX             (false,)
definitely-not-a-key                   (false,)
payment-db-password read from ao-sales (false,)
```

`payment.env` (`~/.local/share/ao-secrets/payment.env`, mode 0600, mtime
2026-10-04 18:38) now carries **four** keys, not one, and re-composing the file
through the bridge reproduces it byte for byte — which is the test the earlier
revision could not have passed:

```text
$ ./scripts/operations/fetch-kwallet-secret.sh "$T/payment.env" payment-credentials
compose exit=0
  key=PAYMENT_DSN                len=106
  key=PAYPAL_WEBHOOK_ID          len=24
  key=PAYPAL_WEBHOOK_SECRET      len=48
  key=COINBASE_WEBHOOK_SECRET    len=48
  PAYMENT_DSN              match=YES
  PAYPAL_WEBHOOK_ID        match=YES
  PAYPAL_WEBHOOK_SECRET    match=YES
  COINBASE_WEBHOOK_SECRET  match=YES
  whole-file: IDENTICAL
```

The temporary file was shredded immediately after the comparison. No secret value
was printed at any point; only lengths, key names and SHA-256 equality were used.

**Two findings survive the correction, and both are still OPEN:**

1. **`payment-db-password` is byte-identical to `sales-db-password`.** The two
   wallet entries hash the same (48 characters each, identical SHA-256 prefix).
   So the "two secrets are one secret" problem the earlier revision identified is
   real and is now located in the *wallet* rather than in a hand-written file — it
   was seeded by copying, not by the bridge. Compromise of the sales-db password
   yields the payment adapter's database access. **The other three entries are
   genuinely distinct** from it (webhook id, PayPal secret, Coinbase secret all
   hash differently), so this is one duplicated value, not a wholesale reuse.
2. **The DSN still grants `sales_migration_role`** — the full schema-admin role —
   to a payment ingress adapter that needs only INSERT on
   `payment_provider_events`. That §14.1 least-privilege deviation is unchanged.

**A staleness finding neither revision recorded.** The running container was
started `2026-10-01 15:08:41`, but `payment.env` was last written
`2026-10-04 18:38` — the container predates the file it reads. Its environment
reflects the older content:

```text
$ podman inspect ao-ingress-payment --format '{{range .Config.Env}}{{println .}}{{end}}' | cut -d= -f1
container GPG_KEY HOME HOSTNAME PATH PAYMENT_DSN PYTHON_SHA256 PYTHON_VERSION
```

`PAYPAL_WEBHOOK_ID`, `PAYPAL_WEBHOOK_SECRET` and `COINBASE_WEBHOOK_SECRET` are
**absent from the live process** even though they are in the file and in the
wallet. The `ExecStartPre` prefetch is non-fatal (`-` prefix), so the unit started
cleanly on the older file and has not been restarted since. The running adapter's
DSN password does match the current wallet value (identical SHA-256 prefix), so
the database path is consistent; the three webhook secrets simply are not loaded.

**Not remediated here.** Rotating a live password, re-scoping a role, or restarting a
payment unit are §4.1 rule 14 and rule 12 stop conditions and require explicit operator
approval. The
remediation proposed for operator approval is unchanged in shape: rotate
`payment-db-password` to a value distinct from `sales-db-password`, grant a
`sales_api_role` limited to the INSERT the adapter performs, and restart
`ao-ingress-payment` so the prefetch loads the three webhook secrets. Recorded as
**OPEN** for the operator.

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
