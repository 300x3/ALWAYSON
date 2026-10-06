# 15. Sales, Mastodon, OpenClaw, and Local AI

## 15.1 Sales Database

Use a dedicated sales PostgreSQL database with separate roles:

```text
salesdb
sales_api_role
sales_migration_role
sales_backup_role
sales_reporting_role
sales_admin_role
```

The desktop metadata reports MeshChatX `4.9.1`. The native executable hash
matches `backend-manifest.json`, but its running version was not independently
established. A `reticulum_meshchatx-4.8.4-py3-none-any.whl` artifact also exists
in the local MeshChatX repository-server identity and is not the verified
running artifact.

Core tables:

```text
customers
customer_contacts
products
product_versions
orders
order_lines
payment_provider_events
payment_references
receipts
fulfillment_events
entitlements
returns
support_cases
audit_events
```

### 15.1.1 Three-Form Transaction Bundles

Every purchase transaction uses one ALWAYS ON-issued transaction ID and one
folder containing three forms:

```text
/ALWAYSON/data/sales/transactions/<transaction-id>/
├── 01-purchase-request.html
├── 02-payment-confirmation.html
├── 03-receipt.html
├── BUNDLE-STATUS.txt
└── provider-evidence/
    ├── paypal.*
    ├── zelle.*
    └── coinbase.*
```

Issue a new bundle:

```bash
/ALWAYSON/scripts/sales/issue-transaction-bundle.sh
```

The issuer creates a unique ID, pre-fills that ID into all three forms, and
creates the provider-evidence directory. The three forms are:

1. Purchase request.
2. Payment confirmation, including provider validation and funds-transfer
   settlement.
3. Corda receipt, including the three evidence references and Corda state.

Validate the bundle structure:

```bash
/ALWAYSON/scripts/sales/validate-transaction-bundle.sh \
  /ALWAYSON/data/sales/transactions/<transaction-id>
```

The same issued ID must appear in all three forms and in the bundle status. It is
also required in the Corda sale-receipt event and the PostgreSQL contract
projection. Payment validation must distinguish provider validation from funds
settlement, and the receipt must record the three validated evidence references
before operator handoff to ledger-ingest.

Corda tracks the transaction ID, payment/ledger state, hashes, and approved
references. Detailed private data remains in the encrypted PostgreSQL
projection keyed by the same transaction ID; Corda does not store full customer
records, raw emails, payment credentials, or unrestricted evidence.

### 15.1.2 Website KIT REQUEST PDF Intake

Website-generated PDF requests are accepted at:

```text
/ALWAYSON/data/sales/kit-request-intake/
```

The current `300x3.com` KIT REQUEST flow composes an email with:

```text
SUBJECT: 300X3-WEBREQUEST-
NAME: <name>
EMAIL: <email>
KIT REQUESTED: <selected kits>
COMMENTS: <comments>

THIS IS A REQUEST FOR INFORMATION, NOT A CONTRACT
```

The intake folder separates requests from sales:

```text
inbox/       Original PDFs placed for intake
extracted/   Extracted text
manifests/   Hashes and intake metadata
receipts/    Final receipts/contracts only after Corda confirmation
review/      Human review records
archive/     Preserved processed request PDFs
quarantine/  Invalid, duplicate, or sensitive-pattern PDFs
```

Run the non-destructive intake script:

```bash
/ALWAYSON/scripts/sales/intake-kit-request-pdf.sh \
  /ALWAYSON/data/sales/kit-request-intake/inbox/<request>.pdf
```

The script preserves and hashes the PDF, extracts text, creates a review record,
and explicitly sets:

```text
classification=kit_request_inquiry
sale_logged=false
corda_state=NOT_SUBMITTED
```

It never treats a website request as payment, creates an order, or submits a
Corda transaction. A verified payment event is required before the PostgreSQL
sale projection is created. A final receipt requires a Corda-confirmed
transaction/state reference written back to PostgreSQL. Metabase reports and
Grafana dashboards read the resulting approved projections; neither creates the
sale.

**CONFIRMED SALE PDF OUTPUT.** The same intake path carries the other direction: once a
sale is confirmed and the Corda transaction/state reference exists, the confirmed sale is
emitted as a **PDF** into the intake tree. That PDF is the outward-facing artefact of a
confirmed sale, as opposed to the request PDF, which is an inquiry and never becomes one.
Both are hash-captured into `manifests/`, and the request PDF is preserved in `archive/`
so the two are never confused.

## 15.2 Community and AI Controls

Mastodon/community controls:

- Dedicated OAuth registration.
- Minimum necessary scopes.
- External access only through `ao-sales` itself (HTTPS/443) when
  explicitly enabled.
- Rate limits.
- Separate approval workflow.
- Immutable publication audit log.
- No payment, field, mapping, simulation, or Corda-core access.

OpenClaw uses the local LM Studio model for support drafting and the deployed
`mastodon-openclaw-bridge.service` automatically answers new Mastodon mentions
and replies as `bot`. The bridge polls the local Mastodon API every 10 seconds,
persists its notification cursor, skips historical notifications and its own
posts, and posts threaded public replies locally. It does not publish to any
other service. Human approval remains required for pricing, orders, shipping,
warranties, financial topics, technical claims, safety guidance, legal
statements, and any publication outside the local bridge workflow.

Bridge state re-verified 2026-10-03 (evidence for COMM-04):

- **Auth half.** The wallet-held bot token is valid. `verify_credentials` returns
  HTTP 200 for `acct=bot, id=117363090433277638` against
  `https://mastodon.300x3.com`. The token value was never printed — only its length
  (43 characters) was measured.
- **Script identity.** The unit runs `/ALWAYSON/scripts/mastodon/mastodon-openclaw-bridge.py`.
  `~/.local/bin/mastodon-openclaw-bridge.py` is a byte-identical copy, not a symlink —
  `sha256` is `486e7472…99c19` for both. Editing the `/ALWAYSON` copy is therefore *not*
  sufficient to change live behaviour until the unit is restarted; this is the same
  copy-not-symlink trap as Quadlets.
- **Operator decision honoured.** Line 281 of the bridge posts with
  `'visibility': 'public'` and retains the `@author` mention prefix, matching the
  2026-10-01 operator decision. Confirmed in *both* copies above, so no stale
  `unlisted` variant is hiding in the deployed file.
- **Cursor is current but idle.** `~/.openclaw/mastodon-bridge-state.json` holds
  `lastNotificationId: "7"`, while `max(notifications.id)` is 8. The two
  notifications (ids 7 and 8, both `follow` from `300x3@mastodon.social`) are not
  `mention`/`status` types, so the bridge correctly ignores them; the state file is
  simply not rewritten for skipped types. Last write was 2026-10-02 00:27 UTC, ~49.9 h
  before measurement. This is expected idleness, **not** the stale-cursor fault
  described in COMM-04 — that earlier fault (cursor ahead of the newest id) is fixed
  and the bridge's own recovery log line is present in the journal.
- **No 401 crash-loop regression.** `systemctl --user status` shows the unit
  `active (running) since Thu 2026-10-01 18:50:55 PDT`, with no restart loop
  (re-confirmed 2026-10-04, 2 days uptime, `Main PID: 788109`, memory 14.1 M,
  peak 19.8 M, CPU 47.1 s).

## 15.3 Local 300X3 Mastodon Deployment

The 300X3 Mastodon instance (Mastodon 4.3.7, containerized in the authoritative
`ao-sales` rootless Podman store) is publicly federated at
**`https://mastodon.300x3.com`**. The main storefront remains on
`https://300x3.com` and `https://www.300x3.com`; it is not routed to Mastodon.
Operators use Konqueror and OpenClaw on the desktop. 

Architecture requirements and verified state:

- `ao-sales` is `Internal=false` and contains the Mastodon database, Redis,
  streaming service, web origin, and Sidekiq. Database, Redis, and streaming are
  not attached to any egress network; they are reached only over `ao-sales`.
- Federation delivery is carried by Sidekiq on `ao-sales` itself over
  HTTPS/443. No database, Redis, or streaming container is attached to any
  egress network.
- Origin web and streaming remain loopback-only: `127.0.0.1:3000` and
  `127.0.0.1:4000`.
- The sole public Mastodon entry is the dedicated Cloudflare Tunnel hostname
  `mastodon.300x3.com`, routed to `127.0.0.1:3000` by
  `cloudflared-alwayson.service`. The storefront hostnames are excluded from
  the Mastodon tunnel and retain the filedn redirect behavior.
- Mastodon identity is `LOCAL_DOMAIN=mastodon.300x3.com`. Accounts, login emails, and the
  `alsoKnownAs` alias are specified in §15.4.2.
- Public actor and WebFinger endpoints were verified at
  `https://mastodon.300x3.com/actor` and
  `https://mastodon.300x3.com/.well-known/webfinger`.
- The tunnel currently uses HTTP/2 transport because QUIC stream timeouts were
  observed on this host. Local and public health checks returned HTTP 200.
- **Open registration is closed.** Measured 2026-10-03: `/api/v1/instance` reports
  `registrations=false, approval_required=false`, and no `registrations` row exists in the
  `settings` table. There is no approval queue and no pending registration. Account
  creation on this instance is an operator action performed directly in the admin UI.
  (An earlier revision of this bullet claimed registration was "open with the approval
  gate"; that was contradicted by both the API and the database on 2026-10-03 and has
  been corrected here.)
- No passwords, OAuth secrets, API keys, tunnel credentials, or access tokens
  are committed to Git or recorded in this README.

## 15.4 Federation Publication of the Local 300X3 Instance

**Scope.** Join the fediverse as the 300X3 instance so that public posts from the
local deployment appear on external Mastodon servers, including `mastodon.social`.

Federation is a mutual, inbound-and-outbound protocol: remote servers (including
`mastodon.social`) must reach this instance over the public internet using HTTPS,
and this instance must be able to deliver outbound activity to remote inboxes. Federation
is publicly reachable at `https://mastodon.300x3.com`; the
main storefront remains on the apex/`www` hostnames and is not routed to Mastodon.

### 15.4.1 Architecture Requirements

WebFinger and `/api/v1/instance` both report `mastodon.300x3.com`, while `300x3.com`
serves the static storefront. The `scottw` operator account runs the 5 Mastodon containers
directly; there is no second Mastodon store and no separate service account on this host.
Open configuration drift against these values is tracked in §19.1.

| Area | Architecture requirement |
|---|---|
| Public instance domain | Dedicated `mastodon.300x3.com`; canonical handles are `user@mastodon.300x3.com`. The storefront hostnames remain separate. |
| Storefront preservation | `300x3.com` and `www.300x3.com` retain the filedn static-site redirect; Mastodon is not deployed under a `/mastodon` subpath. |
| TLS | Required at the public edge; Cloudflare terminates TLS for `mastodon.300x3.com`. |
| Inbound reachability | Cloudflare Tunnel connector `cloudflared-alwayson.service` routes only the dedicated hostname to `127.0.0.1:3000`. |
| Outbound reachability | `mastodon-sidekiq` performs federation delivery over HTTPS/443 directly from `ao-sales`, which is `Internal=false`. Community publication is carried inside `ao-sales`; there is no separate egress network for it. Database, Redis, and streaming stay on `ao-sales` and are never attached to an egress network. |
| Isolation | `ao-sales` is `Internal=false` to permit ActivityPub delivery, and carries no attachment or route to any other `ao-*` domain. No database, Redis, or raw origin listener is publicly exposed. |
| Secrets | Tunnel credentials and API keys remain in protected runtime secret storage; never in Git or this README. |
| Operator duties | Registration approval, moderation, reports, and blocklists remain operator responsibilities. |
| Service-account placement | The 5 Mastodon containers run under the `scottw` operator account in the single `ao-sales` rootless store and systemd user manager. No separate service account exists on this host, so no duplicate Mastodon instance or store can exist. |

### 15.4.2 Domain and Mastodon Identity Configuration

The authoritative runtime env (`LOCAL_DOMAIN=mastodon.300x3.com`) as re-measured
2026-10-03, from `~/.local/share/ao-secrets/mastodon.env`, non-secret keys only:

```text
LOCAL_DOMAIN=mastodon.300x3.com
RAILS_FORCE_SSL=true
LOCAL_HTTPS=true
ALTERNATE_DOMAINS=localhost,localhost:3000,127.0.0.1,127.0.0.1:3000
```

> **Correction 2026-10-03 (COMM session).** An earlier revision of this section stated
> `LOCAL_HTTPS=false` and `RAILS_FORCE_SSL=false`, applied "2026-09-24". That was wrong —
> both keys have always been `true` in the runtime env, in the generator
> `scripts/operations/fetch-mastodon-env.sh` (lines 42–43) and in
> `config/mastodon/mastodon.env.example` (lines 36–37). The measurement below proves
> the claim was never needed: upstream hardcodes `config.force_ssl = true`
> (`config/environments/production.rb`) and `https = Rails.env.production?`
> (`config/initializers/1_hosts.rb`), so in production Rails always emits absolute
> `https://` URLs and always redirects plain HTTP. Re-measured 2026-10-03:

```console
$ curl -s -o /dev/null -w '%{http_code} redirect=%{redirect_url}\n' http://127.0.0.1:3000/
301 redirect=https://127.0.0.1:3000/
```

The local UI is therefore served over TLS by the loopback proxy (§9.2.1), not by
relaxing Mastodon. Leaving the keys `true` keeps the env self-describing and matches
what the generator actually writes.

Registration state is also **not** as previously recorded here. Measured
2026-10-03 against the live instance:

```console
$ curl -s https://mastodon.300x3.com/api/v1/instance | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('registrations'), d.get('approval_required'))"
False False
```

Registration is **closed** (`registrations` absent from the `settings` table, which
Mastodon treats as disabled). There is therefore no approval queue to operate. See
COMM-03 in §19.1.

- WebFinger and actor JSON resolve through the public federation hostname.
- The main storefront remains on `300x3.com` / `www.300x3.com`.
- No `/mastodon` path deployment is used; the dedicated hostname provides the
  root paths required by ActivityPub.

### 15.4.3 Edge, TLS, and Network Path

The edge is **Cloudflare Tunnel**, not workstation nginx with Let's Encrypt. Edge TLS is
terminated by Cloudflare and the origin stays loopback-only; there is no second TLS variant
to maintain.

The federation edge path:

```text
Remote fediverse servers
        │ HTTPS 443
        ▼
Cloudflare edge: mastodon.300x3.com
        │ HTTP/2 tunnel (QUIC disabled after observed stream timeouts)
        ▼
cloudflared-alwayson.service
        │ 127.0.0.1:3000
        ▼
mastodon-web

mastodon-web + mastodon background workers
        │ ao-sales (Sidekiq, HTTPS/443)
        ▼
Remote ActivityPub/WebFinger endpoints
```

The storefront hostnames are not included in this tunnel ingress. Tunnel
credentials remain in protected runtime storage and are never committed.

TLS requirements:

- TLS is mandatory at the edge for all federation traffic (satisfied by
  Cloudflare edge termination for the tunnel-routed apex hostname).
- Tunnel credentials and origin certificate are stored 0400 under
  `~/.cloudflared/` and mirrored to KDE Wallet `ao-mastodon`; never in
  Git or this README. Revoke by deleting/re-creating the tunnel.
- `X-Forwarded-Proto: https` is supplied by cloudflared so Rails
  generates HTTPS URLs and Secure cookies (validated: instance JSON
  reports `streaming_api: wss://mastodon.300x3.com`). Corrected
  2026-10-04: this line previously read `wss://300x3.com`, which is the
  static storefront and is not routed to Mastodon. The validation claim was
  correct but the value quoted was the retired apex host, so the line cited
  as proof that HTTPS rewriting works was itself an instance of the drift
  catalogued in §15.4.8 — a self-contradicting one. Measured:

  ```console
  $ curl -4 -s https://mastodon.300x3.com/api/v1/instance \
      | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['urls'])"
  {'streaming_api': 'wss://mastodon.300x3.com'}
  ```

Outbound delivery path:

- Mastodon background workers deliver public activities to remote inboxes over
  HTTPS/443. **Sidekiq is required** and is the component that performs this
  delivery; it runs as `ao-mastodon-sidekiq` on `ao-sales`.
- Egress is `ao-sales` itself (Section 3), which is non-internal solely for this
  purpose, with HTTPS/443 as the only protocol used. No database, Redis, or
  streaming container is attached to any egress network.
- Rate and retry behavior are Mastodon defaults; no relay subscription is
  approved unless explicitly decided.

### 15.4.4 Federation Enablement Sequence

**This is the specification of the sequence.** Whether each step is done is status and is
recorded once, in §19.1 (component status ST-13 and ST-14, and the work under COMM). No status is
stated here, because a specification does not carry its own status.

1. Dedicated Cloudflare Tunnel `ao-mastodon-federation` and DNS route for
   `mastodon.300x3.com`; storefront hostnames excluded.
2. Cloudflare redirect rule narrowed to exclude `mastodon.300x3.com`; the static
   storefront redirect unchanged.
3. Mastodon identity set to `LOCAL_DOMAIN=mastodon.300x3.com`; actor, WebFinger, and
   local actor documents verified.
4. Community publication carried inside `ao-sales`; database, Redis, and streaming
   remain isolated.
5. Tunnel transport switched to HTTP/2 after QUIC stream timeouts; local and public
   health checks return HTTP 200.
6. `@300x3@mastodon.social` resolved; public followers collection confirms both local
   accounts follow it.
7. Public post fetched; local mention records created and native notification
   processing repaired.
8. Verify reverse follows using the remote following collection and local incoming
   relationship tables, then perform a fresh signed ActivityPub round-trip test.
   Tracked in §19.1 under COMM.
9. Bootstrap discovery: from Konqueror signed in at `https://mastodon.300x3.com`,
   follow at least one account on `mastodon.social`. Remote servers do not index this
   instance until first contact occurs. The storefront host `https://300x3.com` is a
   static site and is **not** routed to Mastodon. Tracked in §19.1 COMM-06.
10. Validate public-post delivery to `mastodon.social` and reply/boost round-trips back
    to the local instance; then submit `300x3.com` to the joinmastodon.org directory
    (operator-authorised). Tracked in §19.1 COMM-07.

Steps 1 through 7 are complete; see §19.1 ST-13 and ST-14 for the evidence and for what
remains on the federation edge.

Step 8 status as measured 2026-10-03: **the reverse-follow verification half is done**
and is recorded in §15.4.9, read from the remote `following` collection of
`300x3@mastodon.social` and cross-checked against the local `follows` table — never from
local outgoing state alone. A *fresh signed* ActivityPub round-trip is **not** re-run
here, because doing so posts publicly and needs operator approval (COMM-07). The
sidekiq queues are empty, which shows nothing is stuck:
`LLEN queue:push_public = 0`, `LLEN queue:pull = 0`, and `redis-cli KEYS 'queue:*'`
returns an empty array.

step 9 status as measured 2026-10-04: first contact **has** occurred, so the instance is
no longer unindexed. Evidence — 10 distinct remote domains are now known locally
(`mastodon.social`, `veganism.social`, `mastodon.online`, `universeodon.com`,
`mastodonapp.uk`, `rivals.space`, `cupoftea.social`, `sekretaerbaer.de`, `fedibook.de`,
`friendicadev.sekretaerbaer.de`) and `mastodon.social` holds our actor, confirmed again by
`lookup?acct=bot@mastodon.300x3.com` → id `117327405745705562` and
`lookup?acct=admin@mastodon.300x3.com` → id `117327389970897359`. The one part of
step 9 not performed is the **human** step — signing in with Konqueror and following from
the browser UI. That requires the operator at the desktop and is not something a headless
session can or should fake. Tracked as COMM-06; status Open.

**Correction to the tunnel-health claim in this step.** An earlier pass recorded here that
the tunnel showed "all 4 connections registered ... no inbound fault". That was a
single-registration reading taken between flaps and it was wrong as a health statement:
the four connections were re-registering continuously. See §15.4.10 — 26 flap events in the
hour, and a 502 on every public path during the burst. Discovery and the remote lookup
above still hold; the claim that the edge path was fault-free does not.

Step 10 has two parts and neither is complete. Public-post delivery and round-trip
re-validation need a **new public post**, which is an external publication and is
withheld pending operator approval; directory submission to joinmastodon.org is
explicitly named in §19.1 as requiring explicit operator approval. Neither was performed.
Tracked as COMM-07; status Open.

### 15.4.5 Operational Boundaries After Enablement

- Only `public` visibility federates; `unlisted`, `private`, and
  `direct` do not appear on remote servers' explore pages. The OpenClaw
  draft-by-default and human-approval controls (Sections 11.2.2 and 15.2)
  remain mandatory for all public publication.
- `post.sh` public-post guard remains the script-level approval gate.
- Federated deletion is best-effort: remote servers may retain cached
  copies. Content published under this section must be treated as
  practically irreversible.
- Publication audit logging (immutable, Section 15.2) must include the
  remote-delivery outcome for federated statuses.

### 15.4.6 Remote Account Approval and Rejection Record

This is the standing moderation record for **remote** accounts contacting this
instance, deliberately kept separate from the local follow relationships in §15.4.4.
It is written here so that an approval or rejection decision is auditable rather than
inferred from follow state.

State measured 2026-10-03 directly from the `mastodon-db` container:

```console
$ podman exec mastodon-db psql -U mastodon -d mastodon -At -c \
  "select 'blocks='||(select count(*) from blocks)
        ||' domain_blocks='||(select count(*) from domain_blocks)
        ||' account_domain_blocks='||(select count(*) from account_domain_blocks)
        ||' email_domain_blocks='||(select count(*) from email_domain_blocks)
        ||' canonical_email_blocks='||(select count(*) from canonical_email_blocks)
        ||' follow_requests='||(select count(*) from follow_requests)
        ||' invites='||(select count(*) from invites)
        ||' ip_blocks='||(select count(*) from ip_blocks)
        ||' user_invite_requests='||(select count(*) from user_invite_requests);"
blocks=0 domain_blocks=0 account_domain_blocks=0 email_domain_blocks=0
canonical_email_blocks=0 follow_requests=0 invites=0 ip_blocks=0 user_invite_requests=0
```

| Date | Remote account | Action | Basis |
|---|---|---|---|
| 2026-10-01 | `300x3@mastodon.social` (remote mirror of the project's own service account, `actor_type=Service`, `bot=true`) | **Accepted** — bidirectional follow established with `bot` and `admin`. No block recorded. | Self-owned account; it is the project's own `300x3` mastodon.social identity, so blocking it would sever the operator's own remote presence. Not a third party. |
| 2026-10-01 | `Gargron@mastodon.social` (remote third party, `actor_type=Person`) | **Accepted as a remote actor, not followed** — `bot` follows `Gargron`; no reverse follow exists and none is expected. No block recorded. | An ordinary public-account follow in the direction local→remote. Not a moderation event. |
| — | All other contacting remote accounts | No action. Discovery relays (`veganism.social`, `mastodon.online`, `universeodon.com`, `mastodonapp.uk`, `rivals.space`, `cupoftea.social`, `friendica@sekretaerbaer.de`, `friendica@fedibook.de`, `friendica@friendicadev.sekretaerbaer.de`) are **automatically fetched service-discovery actors**, not user accounts and not approval candidates. | Discovery contacts are protocol artefacts, not sign-ups. |

There are **no pending remote approval requests**: `follow_requests = 0` and
`user_invite_requests = 0`, which is consistent with registration being closed (§15.4.2).
Nothing in the moderation tables is self-populating, so this table is the record of
record — a future block or approval must be added as a row here by the operator, per
§15.4.1 "Operator duties". No remote account has been rejected to date.

### 15.4.7 Inbound and Outbound Mail for the 300X3 Domain

Mail for `300x3.com` is **not configured and currently cannot be delivered**. This is
recorded here because Mastodon's account-confirmation and password-reset mail depends on
it, and because "no MX" is a decision state, not an oversight.

Measured 2026-10-03:

```console
$ dig +noall +answer MX 300x3.com; echo "answers=$(dig +noall +answer MX 300x3.com | wc -l)"
answers=0
$ dig +noall +answer TXT 300x3.com          # no SPF
$ dig +noall +answer TXT _dmarc.300x3.com   # no DMARC
$ dig +noall +answer A  mail.300x3.com      # no mail host
$ ss -lntp | grep -E ':(25|465|587)\b'      # no local SMTP listener
```

With no MX, RFC 5321 §5.1 falls back to the implicit MX, which is the domain's A record
(the Cloudflare edge addresses). Port 25 to those addresses does not answer:

```console
$ for IP in 172.67.163.66 104.21.41.83; do echo > /dev/tcp/$IP/25 && echo "$IP:25 OPEN" || echo "$IP:25 no-answer/closed"; done
172.67.163.66:25 no-answer/closed
104.21.41.83:25 no-answer/closed
```

Consequence: **all mail to `@300x3.com` is silently undeliverable.** This affects the
local Mastodon accounts, whose registered addresses are `admin@300x3.com` and
`bot@300x3.com`. Password resets and any confirmation mail cannot arrive. Because the
instance has open registration closed and no pending approvals, this is currently
non-blocking for federation, but it is a real gap.

**Outbound is also unconfigured, not merely undeliverable — added 2026-10-05.** The
first pass above only tested *receiving*. Listing the **key names** of the live Mastodon
environment (no values printed) shows there is no mail configuration at all:

```console
$ cut -d= -f1 ~/.local/share/ao-secrets/mastodon.env | sort | grep -iE 'smtp|mail|email'
NO smtp/mail/email key present in live mastodon.env
```

The file holds 24 keys, all of them database, cache, TLS or tuning values. Mastodon
therefore has no `SMTP_ADDRESS`/`SMTP_DOMAIN`/credentials, so it has **no way to submit
mail either**. The practical consequence is wider than "reset mail is undeliverable":
account recovery on this instance is not merely blocked at the receiving hop, there is no
sending path to block. Any resolution chosen under COMM-05 must set **both** directions;
fixing MX alone would leave outbound silent.

Resolution requires an operator decision between the options in §19.1 COMM-05 and is
**not** taken unilaterally here: pointing MX at a hosted relay, standing up a local MTA
(both a new public listener on port 25 and a new package — rule 3 and rule 12), or
formally deferring mail and documenting that address-based recovery is unsupported.
Tracked as COMM-05; status Open.

### 15.4.8 Known Configuration Drift Against `mastodon.300x3.com`

Reconciled audit performed 2026-10-03. **The service runtime is correct** — the live
instance is genuinely `mastodon.300x3.com` and federation works. The drift is confined
to documentation and helper artefacts, all of which emit the superseded apex
`300x3.com`. The entries below are exact so the owning session can apply them without
re-deriving the evidence; none of these files is owned by this session, so none was
edited here.

| # | File | Line | Currently | Should be | Consequence |
|---|---|---|---|---|---|
| D1 | `config/mastodon/mastodon.env.example` | 7 | `LOCAL_DOMAIN=300x3.com` | `LOCAL_DOMAIN=mastodon.300x3.com` | Template would provision a wrong-identity instance. **Highest severity of the four.** |
| D2 | `scripts/operations/fetch-openclaw-mastodon-env.sh` | 17 | `printf 'MASTODON_SERVER=https://300x3.com\n'` | `https://mastodon.300x3.com` | `MASTODON_SERVER` points at the static storefront, so every consumer of this helper posts to a non-Mastodon host. |
| D3 | `scripts/operations/fetch-openclaw-mastodon-env.sh` | 19 | `printf 'MASTODON_BOT_EMAIL=300x3@posteo.net\n'` | `bot@300x3.com` | Superseded third-party mailbox identity. |
| D4 | `config/mastodon/instance-policy.yaml` | 9 | `"https://300x3.com at the Cloudflare edge ... tunnel ao-mastodon-federation"` | `https://mastodon.300x3.com` | Names the retired network name `ao-mastodon-federation` and the apex host. |
| D5 | `config/mastodon/instance-policy.yaml` | 8, 16, 34 | `approved_pub_host: "300x3.com"`; Tokodon origin `https://300x3.com` | `mastodon.300x3.com` | Approved publication host must be the federation host. |
| D6 | `config/mastodon/instance-policy.yaml` | 20 | `registrations: "open with approval gate (approval_required: true)"` | `"closed"` | **Contradicted by the live instance** (`registrations=false`); see §15.4.2. |
| D7 | `config/mastodon/instance-policy.yaml` | 18–19 | `admin@300x3.com`, `bot@300x3.com` | correct — matches the database | No change. |
| D8 | `config/platform/version-matrix.yaml` | 41 | `local_domain: "mastodon.300x3.com"` | correct | Already reconciled 2026-10-01. Images are digest-pinned at v4.3.7, matching the running container. |
| D9 | `config/platform/version-matrix.yaml` | 51 | note: `RAILS_FORCE_SSL/LOCAL_HTTPS are set false but are INERT … loopback proxy at https://127.0.0.1:3300` | only the `set false` → `set true` wording | **Second instance of the same §15.4.2 error.** The `3300` in this note is **correct** and must not be "fixed". **Re-measured 2026-10-05: the values are actually `true`, so this row needs no edit at all** — see §15.4.13 Correction 1. |

**Correction to D9, made 2026-10-04.** An earlier pass recorded D9 as carrying "an
independent port typo: it cites the loopback proxy at port `3300` where the real origin is
`127.0.0.1:3000`", and instructed the owning session to change `3300` → `3000`. **That was
wrong and would have introduced a real fault.** Both ports exist and both are correct for
different processes:

```console
$ ss -ltnp | grep -E ':3000|:3300'
LISTEN 127.0.0.1:3000 users:(("rootlessport",pid=8478))      # podman port publish -> Puma
LISTEN 127.0.0.1:3300 users:(("python3",pid=2385))          # mastodon-local-proxy.py
$ ps -p 2385 -o cmd --no-headers
/usr/bin/python3 /ALWAYSON/scripts/operations/mastodon-local-proxy.py 3300 3000 ...
$ curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/api/v1/instance
301
$ curl -sk -o /dev/null -w '%{http_code}\n' https://127.0.0.1:3300/api/v1/instance
200
```

`mastodon-local-proxy.service` ("ALWAYS ON Mastodon local HTTPS proxy
(127.0.0.1:3300 -> :3000, self-signed TLS)") terminates TLS on `3300` and injects
`X-Forwarded-Proto: https` so Puma's hardcoded `config.force_ssl = true` is satisfied —
which is exactly why plain HTTP to `:3000` answers `301`. So `3300` is the *proxy* and
`3000` is the *origin*, and the version-matrix note names the proxy correctly.

Why this matters beyond the typo: the OpenClaw bridge depends on that distinction. Its
`API` constant is `https://127.0.0.1:3300` with a pinned self-signed CA, and its in-code
comment documents that using `http://…:3000` instead produces a TLS handshake against a
non-TLS Puma and a crash loop. "Reconciling" `3300` to `3000` in the matrix would have
documented a configuration that breaks the bridge. The only genuine drift in that note is
the `set false` wording, which is the same §15.4.2 error as everywhere else.

Proof that D2/D3 are live rather than theoretical: `scripts/mastodon/post.sh` line 17
calls `fetch-openclaw-mastodon-env.sh` on every invocation and line 21 consumes
`MASTODON_SERVER`. Any `post.sh` run therefore targets `https://300x3.com`.

Current versions confirmed correct and needing no change: Mastodon `4.3.7` (§15.3),
`tunnel alwayson-mastodon-federation` running `--protocol http2`, and the runtime
`LOCAL_DOMAIN=mastodon.300x3.com`. Tracked as COMM-01; status Open pending the edits
above, which belong to the session owning `config/` and `scripts/`.

### 15.4.9 Federation Contact Asymmetry (measured, not a fault)

Recorded because it looks like drift and is not. Measured 2026-10-03 from both sides:

```console
$ curl -s 'https://mastodon.social/api/v1/accounts/115945980770248178/following?limit=80'
count= 2
admin@mastodon.300x3.com | https://mastodon.300x3.com/@admin
bot@mastodon.300x3.com   | https://mastodon.300x3.com/@bot
```

The remote `following` collection of `300x3@mastodon.social` confirms **both** local
accounts follow it — the acceptance condition for COMM-02, read from the remote server
rather than inferred locally. The reverse is **not** symmetric: `300x3@mastodon.social`
lists only `bot` among its followers, and local `follows` rows 3 and 4 (`300x3@mastodon.social`
→ `bot`, → `admin`) were created by that remote account's own requests. `admin` has no
outgoing remote follow. `bot` has none either, locally: the only local→remote row is
`bot → admin` (row 1).

`Gargron@mastodon.social` was paginated to exhaustion (25 pages, 2000 follower entries)
and **does not** follow any `300x3.com` account. That is correct and expected: the
`follows` row 2 (`Gargron → bot`) is a record that *Gargron* follows *our bot*, which is
the remote account's business, not a reciprocal requirement.

This asymmetry is a property of how ActivityPub follow requests work, not a defect. It
is written down so a future session does not "fix" it by adding follows.

Re-measured 2026-10-04 and unchanged: the remote `following` collection still returns both
local accounts (`count= 2`), and `followers` still returns only `bot`
(`followers_count= 1`). The asymmetry conclusion stands. Note that the follow
*relationship* is sound while the *edge path* carrying it is currently degraded — see
§15.4.10. Those are independent, and a working `follows` row says nothing about whether
the object can still be fetched.

---

### 15.4.10 Cloudflare Tunnel Edge Instability (measured, and a real availability fault)

This supersedes the "transient 502" reading recorded in §15.4.4 step 8 and in the COMM-02
and COMM-06 evidence. Those passes saw a 502, retried, saw 200, and concluded the tunnel
was healthy. The 502 was not a one-off. It recurred, and the cause is a **sustained
cloudflared edge flap**, not a stray probe.

Measured 2026-10-04 (times UTC):

```console
$ systemctl --user show cloudflared-alwayson.service -p ActiveEnterTimestamp -p NRestarts
ActiveEnterTimestamp=Thu 2026-10-01 15:08:26 PDT
NRestarts=1
```

The unit has **not** restarted since 2026-10-01, so this is invisible to `systemctl` and to
any "is the service up" check. The process stays up while its four edge connections cycle:

```console
$ journalctl --user -u cloudflared-alwayson.service --since '60 min ago' \
    | grep -c 'Lost connection with the edge'
26
$ journalctl --user -u cloudflared-alwayson.service --since '3 hours ago' \
    | grep -c 'Lost connection with the edge'
61
$ journalctl --user -u cloudflared-alwayson.service --since '24 hours ago' \
    | grep -c 'failed to serve incoming request'
450
```

Each flap drops **all four** connections together and re-registers them within ~10 s:

```text
19:54:01 ERR failed to serve incoming request error="Error shutting down control stream: context canceled"
19:54:01 INF Lost connection with the edge connIndex=0
19:54:01 WRN Serve tunnel error error="connection with edge closed" connIndex=0
19:54:02 ERR Connection terminated ... connIndex=1,2,3
19:54:03 INF Registered tunnel connection connIndex=2 ... location=phx01 protocol=http2
19:54:03 INF Registered tunnel connection connIndex=1 ... location=phx01 protocol=http2
19:54:03 INF Registered tunnel connection connIndex=3 ... location=sjc01 protocol=http2
```

That all-connections-at-once pattern is why `NRestarts=1` is not evidence of health:
individual `connIndex` connections are re-established inside the one long-lived process.
**Health of this path must be judged by the flap count in the journal, not by unit state.**

User-visible effect, observed rather than inferred. During a flap window the public edge
returned 502 on every path, including the instance API and the site root:

```console
$ for i in 1 2 3 4 5; do curl -s -o /dev/null -m 15 -w '%{http_code} ' \
    -H 'Accept: application/activity+json' https://mastodon.300x3.com/users/bot; done
502 502 502 502 502
$ # same moment, /api/v1/instance, /api/v2/instance and / all 502
```

A Mastodon actor endpoint answering 502 is exactly the failure that stops remote servers
fetching this instance. Once the flap burst stopped, the same probes returned 200 twelve
times out of twelve, which is why a spot check during recovery reports a healthy system.

**What is *not* affected, measured rather than assumed:** the origin is fine. There were
zero 5xx in three hours of `mastodon-web` logs (1,161 lines, no `" 5xx "` status lines), and
no delivery or fetch errors in 1,872 lines of `mastodon-sidekiq` logs. Queues are empty
(`LLEN queue:push_public = 0`, `LLEN queue:pull = 0`, `KEYS 'queue:*'` → empty array). The
fault is at the Cloudflare edge-to-tunnel hop, not in Mastodon, and it degrades **inbound**
federation (remote servers pulling our objects) more than outbound delivery.

The flap window observed during this pass ran 2026-10-04T06:21:47Z through
19:54:01Z. It has not been diagnosed beyond that: this is the signature of a marginal or
throttled tunnel edge connection, and distinguishing a Cloudflare-side incident from a local
network fault needs evidence this session does not have. Changing tunnel transport, protocol,
or edge routing is **live network configuration** and is therefore a stop condition; it is
recorded for the operator and for the session owning §15.4.3, not actioned here.

#### Trap: probe this host with `curl -4`, or IPv6 confounds every measurement

`mastodon.300x3.com` publishes AAAA records, but this host has **no global IPv6 address**:

```console
$ dig +short AAAA mastodon.300x3.com
2606:4700:3032::6815:2953
2606:4700:3035::ac43:a342
$ ip -6 -o addr show scope global | wc -l
0
$ ping -6 -c 2 2606:4700::6815:2953
ping: connect: Network is unreachable
$ curl -6 -s -o /dev/null -m 10 https://mastodon.300x3.com/api/v1/instance ; echo $?
7
```

A default-`curl` probe tries the AAAA address first, fails, and falls back to IPv4. The
fallback usually succeeds, so a plain probe looks fine. But it makes the measurement
**nondeterministic in a way that mimics the very fault being investigated**: under load or
timing variation the failed v6 attempt can surface as `000` or as a 502 rather than a clean
fallback, and the natural conclusion — "the tunnel is dropping requests" — is wrong. It is
the probe's dead v6 leg.

Use `curl -4` for every measurement against this host. Verified with `curl -4`: 12 of 12
probes returned 200 across the whole of a post-burst window, and IPv4 was what answered
### 15.4.11 The Flap Is Local-Path, Not Cloudflare-Edge (narrowed, 2026-10-04)

§15.4.10 measured *that* the tunnel flaps and correctly declined to name a cause. This pass
narrows it, because the connection topology discriminates between the two candidate causes
and the evidence points one way.

**The discriminator: the four connections are not peers of one edge.** Over 24 hours the
tunnel re-registered against **nine distinct Cloudflare PoPs**, yet always on the same four
edge IPs:

```console
$ journalctl --user -u cloudflared-alwayson.service --since '24 hours ago' -o cat \
    | grep 'Registered tunnel connection' | grep -o 'location=[a-z0-9]*' | sort | uniq -c
    23 location=lax05     17 location=lax07     20 location=lax08
    19 location=lax09     11 location=lax10     15 location=lax11
   224 location=phx01     59 location=sjc01     64 location=sjc06
$ # distinct edge IPs actually in use:
$ ... | grep -oE 'ip=[0-9.]+' | sort -u | wc -l
4
$ # transport is http2 on every single registration, never quic:
$ ... | grep -o 'protocol=[a-z0-9]*' | sort | uniq -c
   452 protocol=http2
```

The four connections terminate on four different edge IPs spread across Phoenix, San Jose
and Los Angeles. A Cloudflare-side edge fault therefore **cannot** explain the observed
pattern: three independent metropolitan PoPs do not lose four unrelated TCP connections
within the same second. Whatever is failing is upstream of the PoP, and common to all four.

**The loss counts confirm they fail as a group, not independently:**

```console
$ journalctl --user -u cloudflared-alwayson.service --since '24 hours ago' -o cat \
    | grep 'Lost connection' | grep -oE 'connIndex=[0-9]' | sort | uniq -c
    96 connIndex=0     94 connIndex=1     95 connIndex=2     99 connIndex=3
```

Nearly identical across four connections to four different cities, dropping in the same
seconds (14 timestamps in the last 6 h carry **three or more** simultaneous losses). Four
independent edges do not fail in lockstep; a shared local resource does.

**And it is not a hard network error.** The journal contains no `network is unreachable`,
`no route to host`, `connection reset` or timeout signature:

```console
$ journalctl --user -u cloudflared-alwayson.service --since '6 hours ago' -o cat \
    | grep -icE 'network is unreachable|no route to host|connection reset|broken pipe|timeout'
0
```

The only errors are the *consequences* of the drop, all downstream of it:

```console
    72 ERR failed to serve incoming request error="Error shutting down control stream: context canceled"
    64 ERR failed to serve incoming request error="Error shutting down control stream: client disconnected"
    31 WRN Serve tunnel error error="connection with edge closed" connIndex=3
```

"context canceled" and "client disconnected" are cloudflared tearing down in-flight streams
because the connection went away. Treating these as the cause — as their count and phrasing
invite — is a trap: they are the flap's shadow, not its origin.

**Conclusion, stated at the strength the evidence supports.** The fault lies on the shared
local path between this host and the tunnel edge — the local uplink, NAT state, or the
host's own network path — and not in Mastodon (origin 5xx = 0, both queues empty), not in
Cloudflare's edge fleet (three PoPs, four IPs, all healthy simultaneously otherwise), and
not in the cloudflared unit state (`NRestarts=1`, `ActiveState=active`). That last point is
the operational trap: **every "is the tunnel up" check passes while this fault is ongoing.**

**Blast radius, re-measured at steady state.** The flap is continuous rather than bursty,
and this corrects a natural misreading of a small sample:

```console
$ for w in '15 min ago' '1 hour ago' '6 hours ago' '24 hours ago'; do
    echo "$w: $(journalctl --user -u cloudflared-alwayson.service --since "$w" \
      | grep -c 'Lost connection with the edge')"; done
15 min ago: 0        # <- the misleading sample
1 hour ago: 26
6 hours ago: 121
24 hours ago: 384
# 384 events across 204 distinct minutes = ~16/hour, i.e. one flap roughly every 4 minutes
```

Sampling a short window is how this looks healthy; over 24 hours it is one flap every few
minutes. **The fifteen-minute window returning zero is not recovery, it is the burstiness
of the aggregate rate** — do not read a quiet minute as a fixed tunnel.

Public impact right now, measured with `curl -4` per the trap above, is currently low —
the edge is answering between flaps:

```console
$ for i in 1 2 3 4 5 6 7 8; do curl -4 -s -o /dev/null -m 15 -w '%{http_code} ' \
    -H 'Accept: application/activity+json' https://mastodon.300x3.com/users/bot; sleep 2; done
200 200 200 200 200 200 200 200
```

That 8/8 is **recovery between flaps, not a fix**, and must not be reported as one: the
same probe returned 502 5/5 during a burst (§15.4.10). Inbound federation is therefore
intermittently unavailable — roughly one short window every few minutes — while every
unit-level and spot-check health indicator reads healthy.

**Not actioned, deliberately.** Isolating the local path means changing live network
configuration (uplink, NAT, or tunnel transport) — a stop condition, and §15.4.3 belongs to
the session that owns edge and network path. The diagnostic the operator needs is cheap
and read-only: compare edge-connection stability against a control long-lived TLS
connection from this host to a fixed destination. If the control is stable while all four
tunnel connections flap in lockstep across nine PoPs, the local path is confirmed and the
tunnel is exonerated. I have not run that comparison because it is not required to record
the finding, and running it well needs a deliberate observation window.
### 15.4.12 Re-Verification Pass, 2026-10-04 (liveness, not a status refresh)

Re-measured the live claims in this section after the §15.4.11 tunnel finding, because
several of them rest on artifacts whose age had grown past 48 h. Two things changed the
picture: one of my own claims was wrong, and the tunnel fault in §15.4.11 is **still
live**, not a historical episode.

**`statuses` is empty, and that is the operator's wipe, not data loss.** The table reads
zero, which looks alarming. It reconciles exactly with ST-13's documented 2026-10-01
timeline wipe and its backup:

```console
$ podman exec mastodon-db psql -U mastodon -d mastodon -At -c 'select count(*) from statuses;'
0
$ awk '/^COPY public.statuses /,/^\\\.$/' \
    /ALWAYSON/backups/mastodon-status-wipe-2026-10-01/statuses-before-wipe.sql | grep -c ''
126
$ podman exec mastodon-db psql -U mastodon -d mastodon -At \
    -c "select id,username,coalesce(domain,'LOCAL') from accounts order by id;" | head -4
-99|mastodon.internal|LOCAL                <- tombstone row, precedes every real id
117363090403638110|admin|LOCAL
117363090433277638|bot|LOCAL
117367694533297015|300x3|mastodon.social
$ podman exec mastodon-db psql -U mastodon -d mastodon -At \
    -c 'select (select count(*) from follows), (select count(*) from accounts);'
4|14
```

An earlier draft of this subsection quoted that accounts listing with `head -3` and showed
it starting at `admin`. It does not: there is a `-99` `mastodon.internal` tombstone row
that sorts first. The point I was making — that `admin`, `bot` and the remote `300x3`
account survive the wipe — is unaffected, but the transcript must be the real one.

126 statuses were deleted from a 126-row pre-wipe dump, and the accounts and follow rows
ST-13 says were preserved are still present (`follows = 4`, `accounts = 14`). Anyone
reading `count(*) = 0` as loss of data should read ST-13 first. Note the operational
consequence: with zero statuses there is no local post for the federation queues to carry,
so an empty `queue:push_public` no longer proves outbound delivery works — it only proves
there is nothing to deliver.

**The bridge is alive and polling; my first liveness measurement was wrong.** I sampled
CPU ticks over 20 s, got `delta=0`, and read that as a stalled process. It is not. A 100 s
sample shows steady consumption consistent with the 10 s poll loop:

```console
$ systemctl --user show mastodon-openclaw-bridge.service -p MainPID -p ActiveState -p NRestarts
ActiveState=active
MainPID=788109
NRestarts=0
$ ps -p 788109 -o lstart,etime --no-headers
Thu Oct  1 18:50:54 2026    2-21:22:16
$ t1=$(awk '{print $14+$15}' /proc/788109/stat); sleep 100
$ t2=$(awk '{print $14+$15}' /proc/788109/stat); echo "delta_ticks=$((t2-t1))"
delta_ticks=2
$ cat /proc/788109/wchan
hrtimer_nanosleep
```

A 10 s poll doing one HTTPS request per cycle costs ~2 ms per iteration, so **any sample
shorter than about 60 s can read zero on a perfectly healthy process.** `wchan =
hrtimer_nanosleep` and a `MainPID` unchanged since 2026-10-01 corroborate it, and
`NRestarts=0` means the unit has never been restarted into a crash loop. Do not use a
short CPU delta as a liveness test for this unit.

**The idle cursor is real idleness, and the state file explains it.** The cursor is 7, the
database `max(notifications.id)` is 8, and the state file has not been written since
2026-10-01. Querying the API the way the bridge does resolves the apparent contradiction —
notification 8 exists but is **not the bot's**:

```console
$ cat ~/.openclaw/mastodon-bridge-state.json
{
  "lastNotificationId": "7",
  "updatedAt": 1790900850.2506645
}
$ ls -la ~/.openclaw/mastodon-bridge-state.json
-rw-rw-r-- 1 scottw scottw 67 Oct  1 17:27 /home/scottw/.openclaw/mastodon-bridge-state.json
# same call the bridge makes: /api/v1/notifications?limit=40
notifications returned: 1
ids/types: [('7', 'follow')]
max id: 7
$ podman exec mastodon-db psql -U mastodon -d mastodon -At \
    -c "select id,type,account_id from notifications order by id;"
7|follow|117363090433277638      <- bot
8|follow|117363090403638110      <- admin
```

So the newest notification *the bridge can see* is 7, equal to its cursor, and there is
nothing to advance to. The state file is only rewritten when a notification is newer than
the cursor, so its 2026-10-01 mtime is consistent with a healthy idle loop and is **not**
evidence of a stall. This refines the §15.4.9 claim that "max(notifications.id) is 8 while
the cursor is 7" — those two numbers were never comparable, because the API view is
per-account. §5 (README) states the same pairing and should be read with this in mind.

**COMM-08 is still ongoing; §15.4.11 is not stale.** Re-measured the flap rate:

```console
$ for w in '15 min ago' '1 hour ago' '24 hours ago'; do
    printf '%s: ' "$w"; journalctl --user -u cloudflared-alwayson.service --since "$w" \
      | grep -c 'Lost connection with the edge'; done
15 min ago: 7
1 hour ago: 15
24 hours ago: 381    # was 384 at the previous pass, i.e. the rate is NOT decaying
$ systemctl --user show cloudflared-alwayson.service -p NRestarts -p ActiveState
ActiveState=active
NRestarts=1
```

Two corrections to what I wrote before the stall. First, **the `15 min ago: 0` sample I
reported in the draft of this subsection was a quiet window, and I have now caught the flap
mid-burst (`15 min ago: 7`).** That is exactly the trap §15.4.11 warns about, and it is
the reason the short window must not be quoted on its own. Second, 381 in 24 h against 384
previously is steady-state persistence, not decay — the fault has now run for over two days.

I also ran the cheap control comparison §15.4.11 said it had not done: a long-lived TLS
handshake to the same Cloudflare edge address succeeds cleanly, and a control request to a
non-tunnel external host is stable:

```console
$ openssl s_client -connect 104.21.41.83:443 -servername mastodon.300x3.com </dev/null \
    | grep -E 'Protocol|Verify return'
Protocol: TLSv1.3
Verify return code: 0 (ok)
$ for i in 1 2 3; do curl -4 -s -o /dev/null -m 15 \
    -w '%{http_code} ' https://mastodon.social/api/v2/instance; sleep 3; done
200 200 200
```

This is **not** yet the confirmation §15.4.11 asked for, and must not be reported as one: a
single short-lived TLS handshake succeeding says nothing about connection *stability* over
the minutes-long window a tunnel connector needs. It does exclude "TLS to the edge IP is
broken" and "general outbound HTTPS is broken", which is useful. Diagnosing the local path
and changing tunnel transport remain live network configuration and therefore a stop
condition. Tracked as COMM-08; status Open.
### 15.4.13 Independent Re-Verification, 2026-10-05 (liveness of §15.4.8–§15.4.12)

Every claim in §15.4.8–§15.4.12 rests on measurements taken 2026-10-03/04. Re-measured
from scratch on 2026-10-05 rather than trusting them. Most reproduce exactly. **Three do
not, and all three corrections are mine.**

**Correction 1 — `RAILS_FORCE_SSL`/`LOCAL_HTTPS` are set `true`, not "false".** §15.4.8
row D9 and §15.4.2 both describe these variables as "set false but INERT". That is wrong
in a way that matters, because "set false" implies a deliberate local override that is
then defeated by the upstream default. There is no override — the live values are `true`:

```console
$ grep -E '^(RAILS_FORCE_SSL|LOCAL_HTTPS)=' ~/.local/share/ao-secrets/mastodon.env
RAILS_FORCE_SSL=true
LOCAL_HTTPS=true
$ podman inspect mastodon-web --format '{{range .Config.Env}}{{println .}}{{end}}' \
    | grep -E 'RAILS_FORCE_SSL|LOCAL_HTTPS'
RAILS_FORCE_SSL=true
LOCAL_HTTPS=true
$ grep -n 'force_ssl' /ALWAYSON/config/mastodon/patches/production.rb
config.force_ssl = ENV.fetch('RAILS_FORCE_SSL', 'true') == 'true'
```

The env-file key list contains no `RAILS_FORCE_SSL=false` anywhere. So the sequence is:
the variable is explicitly `true`, the project patch reads it, and the upstream default
agrees. Nothing is inert and nothing is overridden. The corrected D9 "should be" cell is
therefore **no change at all** — the note's substance is right and only its description of
the *mechanism* is wrong. This also means D9 has **no actionable edit**, which lowers the
apparent size of the COMM-01 backlog by one row.

**Correction 2 — port `3300` is real, confirmed a second time, independently.** §15.4.8
already retracted the "3300 typo" claim; this pass re-derived it from scratch rather than
re-reading the retraction. `mastodon-local-proxy.service` is live, is serving the actual
Mastodon UI, and the proxy process is running exactly as the version-matrix note
describes:

```console
$ ss -lntp | grep -E ':(3000|3300|4000)\b'
LISTEN 127.0.0.1:3000 users:(("rootlessport",pid=8478,fd=5))
LISTEN 127.0.0.1:3300 users:(("python3",pid=2385,fd=3))
LISTEN 127.0.0.1:4000 users:(("rootlessport",pid=5967,fd=5))
$ ps -p 2385 -o lstart,cmd --no-headers
**Correction 3 — the flap is bursty, not steady. §15.4.11 said "NOT bursty" and that is
wrong.** §15.4.11 measured 384 events across 204 distinct minutes and concluded a steady
~16/hour, "one flap roughly every 4 minutes". Re-measured over a fresh 24 h window the
count is higher and the *shape* is different: 444 events, and the minute-level gap
histogram shows the events arrive in **consecutive-minute pairs**.

```console
$ for w in '15 min ago' '1 hour ago' '6 hours ago' '24 hours ago'; do
    printf '%s: ' "$w"; journalctl --user -u cloudflared-alwayson.service --since "$w" \
      | grep -c 'Lost connection with the edge'; done
15 min ago: 6
1 hour ago: 21
6 hours ago: 90
24 hours ago: 444
$ # distinct flap-bearing minutes, then the gap between consecutive ones:
distinct_flap_minutes=139
60s x68   120s x2   180s x1   420s x3   480s x5   540s x4   600s x3   660s x2 ...
median_gap=120s  max_gap=4020s
```

68 of the 138 gaps are **exactly 60 s**, i.e. a flap minute immediately followed by
another flap minute. Aggregated by burst: **387 losses fall in 105 minutes that contain
3+ simultaneous losses, against 53 losses in 34 singleton minutes.** That is the
signature of a periodic multi-connection event, not an independent per-connection
background error rate.

Why this is not a cosmetic correction: §15.4.11's own advice was "do not sample a short
window, the rate is steady". If the truth is bursty, that advice is actively harmful —
during a quiet period a short sample reads 0 and a reader concludes the fault is over,
which is exactly the false-recovery trap §15.4.12 already fell into once. I fell into it
again in this very pass: at 15:03 UTC, `10 minutes ago` returned **0 flaps** while the
preceding 15-minute window had returned 6.

**The §15.4.11 conclusion survives, and the discriminator got stronger.** The PoP
footprint widened from nine to **fourteen** distinct points of presence in 24 h, against
still exactly **four** edge IPs, still 100 % `protocol=http2`, and the per-connection loss
split is still near-uniform (112/111/109/108 across `connIndex` 0–3):

```console
$ journalctl --user -u cloudflared-alwayson.service --since '24 hours ago' -o cat \
    | grep 'Registered tunnel connection' | grep -o 'location=[a-z0-9]*' | sort | uniq -c
  2 lax01  22 lax05  19 lax07  14 lax08  13 lax09  15 lax10  21 lax11  2 lax13
246 phx01  64 sjc01  80 sjc06  2 sjc07  1 sjc08  1 sjc10
**The control experiment §15.4.11 asked for: run, and it came back inconclusive.** It
compared a long-lived TLS handshake to the tunnel edge IP against a handshake to a
non-tunnel destination, 110 ticks at 5 s, and correlated each tick with a 70 s window of
tunnel journal entries:

```console
$ # 110 ticks, edge = 104.21.41.83:443, control = mastodon.social:443
SUMMARY ticks=110 edge_ok=110 edge_fail=0 ctrl_ok=110 ctrl_fail=0 flaps_seen_in_windows=0
```

Both paths were perfect, **because zero flaps occurred during the window** — consistent
with the bursty finding above. This is *not* the confirmation §15.4.11 requested, and I
am not recording it as one. A probe with no events in it cannot discriminate anything: the
result is identical to what a healthy network would have produced, which is precisely why
"both green" must not be read as "fault absent". A second, longer probe was launched to
try to catch a burst deliberately.

**A bug in my own probe, worth recording because it nearly produced a false reading.** My
first probe treated success as `grep -c 'Verify return code: 0'` being *exactly* `1`.
The control returned `2` on every tick — the string legitimately appears twice (chain and
leaf) — so every control tick was scored as a failure. I killed and rewrote it to accept
`>= 1`. Had I not inspected a `ctrl_ok=2` line and taken it as a fault, I would have
reported "the control path fails continuously while the edge path succeeds", inverting the
conclusion. **A probe's expected value must be a range, not a point.** The same class of
error as the empty-output-vs-zero-count mistake in the COMM-05 evidence.

**Status of the other COMM items, re-verified 2026-10-05 (no new findings).**

- **COMM-02** — remote `following` still returns `count= 2` (both local accounts); remote
  `followers_count= 1`, listing only `bot`. §15.4.9 unchanged.
- **COMM-03** — all nine moderation tables still `0`; remote actors still 9
  `Application` / 1 `Person` / 1 `Service`; `settings` still holds only
  `reserved_usernames`; both local users `approved=true`, `disabled=false`. D6 unchanged:
  `registrations False approval_required False` against a policy file that says
  "open with approval gate".
- **COMM-04** — token length 43, `verify_credentials` HTTP 200 `acct=bot`
  `id=117363090433277638`; both bridge copies still `sha256 486e7472…99c19`;
  `ActiveState=active`, `NRestarts=0`.
- **COMM-05** — still **no** MX (`answers=0`) and a **new** finding this pass: the live
  `mastodon.env` contains **no SMTP, mail or email key at all**, so outbound is not
  merely undeliverable, it is unconfigured. See §15.4.7.
- **COMM-06** — `mastodon.social` still resolves both accounts
  (`bot` id `117327405745705562`, `admin` id `117327389970897359`, 2 followers each);
  10 distinct remote domains known locally. The Konqueror step remains the operator's.
- **COMM-07** — `statuses` is still `0` (the 2026-10-01 wipe; the 126-row pre-wipe dump
  is still present at `backups/mastodon-status-wipe-2026-10-01/`), both queues empty,
  `joinmastodon.org` → 200. **No publication performed.**
$ ... | grep -oE 'ip=[0-9.]+' | sort -u
ip=198.41.192.107  ip=198.41.192.167  ip=198.41.200.13  ip=198.41.200.193
$ ... | grep 'Registered tunnel connection' | grep -o 'protocol=[a-z0-9]*' | sort | uniq -c
502 protocol=http2
$ journalctl ... | grep 'Lost connection' | grep -oE 'connIndex=[0-9]' | sort | uniq -c
112 connIndex=0  111 connIndex=1  109 connIndex=2  108 connIndex=3
$ systemctl --user show cloudflared-alwayson.service -p NRestarts -p ActiveState
ActiveState=active
NRestarts=1
```

Fourteen independent metropolitan PoPs across three regions cannot all lose four
unrelated connections inside the same second. The fault remains **upstream of the PoP and
common to all four connections** — the shared local path. Origin is still clean
(`mastodon-web` 5xx count over 30 m = 0, `error delivering` in `mastodon-sidekiq` = 0,
both queues empty). And the operational trap is unchanged and still the most dangerous
thing in this section: **`NRestarts=1` with `ActiveState=active` while the fault runs.**
Thu Oct  1 15:08:14 2026 /usr/bin/python3 /ALWAYSON/scripts/operations/mastodon-local-proxy.py \
    3300 3000 /ALWAYSON/secrets/mastodon/mastodon-local.crt .../mastodon-local.key
$ systemctl --user show mastodon-local-proxy.service -p NRestarts
NRestarts=0
$ curl -sk -m 10 https://127.0.0.1:3300/ | grep -oiE '<title>[^<]*</title>'
<title>Mastodon</title>
$ curl -sk -m 10 https://127.0.0.1:3300/api/v1/instance   # -> version
4.3.7
```

Two facts make this worth restating. First, `3300` answers **200** and returns the real
Mastodon UI, while `https://127.0.0.1:3000/api/v1/instance` errors at the TLS layer —
the ports are not interchangeable, so any "normalisation" of the matrix note to `3000`
breaks the bridge (see §15.4.8). Second, this is the **Quadlet/copy trap again**: the
live unit at `~/.config/containers/systemd/` is a *copy* of
`/ALWAYSON/quadlet/operations/mastodon-local-proxy.service`. Editing the repo file alone
will not change the running proxy.
