---
item: COMM-06
action: update
evidence: |
  # First contact HAS occurred - 10 remote domains are now known locally:
  $ podman exec mastodon-db psql -U mastodon -d mastodon -At -c \
    "select string_agg(distinct domain,', ') from accounts where domain is not null;"
  cupoftea.social, fedibook.de, friendicadev.sekretaerbaer.de, mastodonapp.uk,
  mastodon.online, mastodon.social, rivals.space, sekretaerbaer.de,
  universeodon.com, veganism.social

  # mastodon.social holds our actor and our accounts resolve on its side:
  $ curl -s -o /dev/null -w '%{http_code}\n' -H 'Accept: application/activity+json' \
    'https://mastodon.300x3.com/users/bot'
  200
  $ curl -s -H 'Accept: application/json' \
    'https://mastodon.social/api/v1/accounts/lookup?acct=bot@mastodon.300x3.com' | ...
  bot@mastodon.300x3.com -> mastodon.social id=117327405745705562
  $ curl -s -H 'Accept: application/json' \
    'https://mastodon.social/api/v1/accounts/lookup?acct=admin@mastodon.300x3.com' | ...
  admin@mastodon.300x3.com -> mastodon.social id=117327389970897359

  # Tunnel is healthy and re-registered on all 4 connections (not a reachability fault):
  $ journalctl --user -u cloudflared-alwayson.service -n 40 | grep -c 'Registered tunnel connection'
  4
  INF Registered tunnel connection connIndex=0 ... location=lax08 protocol=http2
  INF Registered tunnel connection connIndex=1 ... location=phx01 protocol=http2
  INF Registered tunnel connection connIndex=2 ... location=phx01 protocol=http2
  INF Registered tunnel connection connIndex=3 ... location=lax11 protocol=http2

  # Note: mastodon.social WebFinger returns 404 for our accts - this is NORMAL,
  # not a discovery failure (Mastodon does not WebFinger accts it has no record of).
  webfinger bot@mastodon.300x3.com = 404
section: 15-sales-mastodon-openclaw-and-local-ai
---
Remains **Open**, but for one narrow reason: the *technical* precondition named in the item
is satisfied, and only the **human** step is outstanding.

The item's acceptance text is "from Konqueror signed in at `https://mastodon.300x3.com`,
follow at least one account on `mastodon.social`. Remote servers do not index this instance
until first contact occurs." The second sentence — the actual constraint — is satisfied and
measured: 10 distinct remote domains are known locally, and `mastodon.social` resolves both
of our accounts and holds our actor. **The instance is not unindexed.** Discovery contact
has demonstrably happened.

What is not done is the **browser step performed by the operator at the desktop**: signing
in via Konqueror and following from the UI. I did not perform it and did not simulate it.
Two reasons, and the second matters more than the first:

1. It needs the operator's session and credentials at a graphical desktop.
2. More importantly, faking it would corrupt the evidence. An item that says "the operator
   confirmed this in Konqueror" cannot be closed by a headless session asserting the
   account exists. I would rather leave a precise Open item than manufacture a false
   verification.

What I *did* verify from the remote side is stronger than a local table check, so the
remaining work is genuinely small: the relationship already exists bidirectionally (see the
COMM-02 proposal), which is the end state the UI step would produce.

My section file records this status under §15.4.4 step 9, including the health of the
tunnel (all 4 connections registered, `protocol=http2`, no inbound fault) so nobody
re-investigates reachability.

**A trap worth recording, because it looks like a failure and is not.**
`https://mastodon.social/.well-known/webfinger?resource=acct:bot@mastodon.300x3.com`
returns **404**. Read naively that says "the remote server cannot find us" — the exact
failure this item exists to prevent. It is normal: mastodon.social does not perform
WebFinger lookups for accounts it holds no local record of, and it already holds our
actors (confirmed by the `lookup?acct=` calls returning real IDs). Treating that 404 as a
discovery fault would trigger pointless re-work on a healthy federation path.

I also noted the tunnel dropped and re-established all four connections at
2026-10-04T02:18:47Z (`Lost connection with the edge`, then four `Registered tunnel
connection` lines 10 s later). That is normal cloudflared reconnect behaviour under
`Restart=always`, not an incident — all four re-registered and the public endpoints
answered 200 throughout. Recorded so the next session reading the journal does not chase
it.

**What I got wrong:** my very first reachability probe hit
`https://mastodon.300x3.com/users/bot` and got **502**, which I initially logged as
possible federation breakage. It was transient — five consecutive retries all returned
200. I also could not reach the loopback origin directly
(`https://127.0.0.1:3000/users/bot` returned `000`), which looked like a dead origin but is
expected: origin traffic arrives over the tunnel with the tunnel setting Host, and a
direct loopback TLS probe without that arrangement is not a valid test. I dropped that
probe rather than report it as a fault.