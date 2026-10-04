---
item: COMM-07
action: update
evidence: |
  # NOTHING WAS PUBLISHED. This proposal records a stop, not a delivery.
  # --- Half 1: public-post delivery + round trip. Requires a NEW public post. ---
  # Existing evidence is from 2026-10-01 and is NOT re-run here; re-validating it
  # means posting publicly, which needs approval.
  # Delivery pipeline is idle and healthy, so any failure would be new, not inherited:
  $ podman exec mastodon-redis redis-cli LLEN 'queue:push_public'
  0
  $ podman exec mastodon-redis redis-cli LLEN 'queue:pull'
  0
  $ podman exec mastodon-redis redis-cli --no-raw KEYS 'queue:*'
  (empty array)
  # Actor fetch is healthy (502 seen once, then 200 on 5/5 retries):
  try1 actor = 200 ... try5 actor = 200
  api/v1/instance = 200 ; api/v2/instance = 200 ; root page = 200

  # --- Half 2: directory submission. Read-only reconnaissance only. ---
  $ curl -s -o /dev/null -w '%{http_code}\n' 'https://joinmastodon.org/'
  200
  # (https://joinmastodon.org/instances returned 404 - listing is not exposed at that path;
  #  no submission was attempted, no form submitted, no data transmitted)
section: 15-sales-mastodon-openclaw-and-local-ai
---
Remains **Open. I stopped at the operator-approval gate and performed no publication.**
The item's own text states directory submission "is an external publication and requires
explicit operator approval". I do not have that approval, so neither half was executed.

**Half 1 — public-post delivery and round trips.** Not re-run. The existing evidence
(status text in §19.1, and §15.4.4 step 10) is from 2026-10-01 and is not mine to discard,
but re-validating delivery requires posting a **new** public status to `mastodon.social`,
which is an external publication. I did not post. What I did instead is establish that
nothing is currently stuck, so if the operator approves, the test starts from a clean
state: both sidekiq queues are empty (`push_public` and `pull` both `0`,
`KEYS 'queue:*'` returns an empty array), the tunnel has all 4 connections registered, and
`/api/v1/instance`, `/api/v2/instance` and `/` all answer 200.

Worth flagging for whoever runs it: **§15.4.9 documents that the follow relationship is
not reciprocal** (our remote mirror lists only `bot` among its followers). A round-trip
test that assumes reciprocal follows will appear to fail for reasons that are not faults.
Test with `bot`, which has the established relationship.

**Half 2 — joinmastodon.org directory submission.** Not attempted. I confirmed only that
the site is reachable (`https://joinmastodon.org/` → 200). I did **not** fill in or submit
any form, and transmitted nothing. Note for the operator: `joinmastodon.org/instances`
returns 404 — the public instance listing is not exposed at that path — so the submission
route needs to be established at the site itself.

One substantive observation, offered as a question rather than a recommendation, because
it is a content question I should not answer alone: the directory submission is for
`300x3.com`, but `300x3.com` is the **static storefront and is not routed to Mastodon**
(confirmed in `~/.cloudflared/config.yml` ingress — only `chat.300x3.com` and
`mastodon.300x3.com` are routed, with a `404` catch-all). The federation instance is
`mastodon.300x3.com`. Submitting the apex may be what was intended for the *brand*, or it
may be a leftover of the pre-migration apex deployment. Since a directory listing is
permanent and externally visible, **this should be confirmed before submission rather
than after.**

**What I got wrong:** I set out to close this item by running a delivery test and found
myself about to make a public post to prove a pipeline works — which is exactly the kind
of irreversible external action the approval rule exists to prevent. "It is only a test
post" is how public publication starts. I also have a mild temptation to treat the
joinmastodon.org reachability check as partial progress; it is reconnaissance, not
delivery, and the proposal says so rather than letting the 200 stand in for progress.