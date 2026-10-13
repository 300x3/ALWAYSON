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
- **Open registration is closed.** `/api/v1/instance` reports `registrations=false,
  approval_required=false`, with no `registrations` row in the `settings` table. There is no
  approval queue and no pending registration. Account creation on this instance is an operator
  action performed directly in the admin UI.
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
  reports `streaming_api: wss://mastodon.300x3.com`). The validation claim was
  correct but the value quoted must be the federation host `mastodon.300x3.com`,
  not the retired apex `300x3.com` (the static storefront, which is not routed to
  Mastodon). Verify with:

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

Step 8: **the reverse-follow verification half is done**, read from the remote `following`
collection of `300x3@mastodon.social` and cross-checked against the local `follows` table —
never from local outgoing state alone. A *fresh signed* ActivityPub round-trip is **not** re-run
here, because doing so posts publicly and needs operator approval (COMM-07). The
sidekiq queues must be empty, which shows nothing is stuck:
`LLEN queue:push_public = 0`, `LLEN queue:pull = 0`, and `redis-cli KEYS 'queue:*'`
returns an empty array.

Step 9: first contact confirms the instance is indexed. Evidence is 10 distinct remote domains
known locally (`mastodon.social`, `veganism.social`, `mastodon.online`, `universeodon.com`,
`mastodonapp.uk`, `rivals.space`, `cupoftea.social`, `sekretaerbaer.de`, `fedibook.de`,
`friendicadev.sekretaerbaer.de`) and `mastodon.social` holding our actor, confirmed by
`lookup?acct=bot@mastodon.300x3.com` → id `117327405745705562` and
`lookup?acct=admin@mastodon.300x3.com` → id `117327389970897359`. The one part of
step 9 not performed is the **human** step — signing in with Konqueror and following from
the browser UI. That requires the operator at the desktop and is not something a headless
session can or should fake. Tracked as COMM-06; status Open.

**Tunnel health must not be read from a single registration snapshot.** A reading of "all 4
connections registered … no inbound fault" taken between flaps is not a health statement —
the four connections re-register continuously. Confirm stability over a window before
asserting the edge path is fault-free (see §19.1 COMM-08).

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

