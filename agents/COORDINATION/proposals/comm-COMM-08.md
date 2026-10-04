---
item: COMM-08
action: new
title: Cloudflare tunnel edge flapping — intermittent 502 to remote federation
evidence: |
  $ systemctl --user show cloudflared-alwayson.service -p NRestarts -p ActiveEnterTimestamp
  NRestarts=1
  ActiveEnterTimestamp=Thu 2026-10-01 15:08:26 PDT
  $ journalctl --user -u cloudflared-alwayson.service --since '60 min ago' \
      | grep -c 'Lost connection with the edge'
  26
  $ journalctl --user -u cloudflared-alwayson.service --since '3 hours ago' \
      | grep -c 'Lost connection with the edge'
  61
  $ journalctl --user -u cloudflared-alwayson.service --since '24 hours ago' \
      | grep -c 'failed to serve incoming request'
  450
  # observed during the burst, /users/bot (the actor endpoint):
  $ for i in 1 2 3 4 5; do curl -s -o /dev/null -m 15 -w '%{http_code} ' \
      -H 'Accept: application/activity+json' https://mastodon.300x3.com/users/bot; done
  502 502 502 502 502
  # /api/v1/instance, /api/v2/instance and / were all 502 at the same moment.
  # origin clean, so this is NOT a Mastodon fault:
  $ podman logs --since 3h mastodon-web | wc -l            # 1161, no 5xx status lines
  $ podman logs --since 3h mastodon-sidekiq | wc -l        # 1872, no delivery errors
  $ podman exec mastodon-redis redis-cli LLEN 'queue:push_public'   # 0
  $ podman exec mastodon-redis redis-cli LLEN 'queue:pull'          # 0
  # MEASUREMENT TRAP - IPv6 confounds this host's probes:
  $ dig +short AAAA mastodon.300x3.com
  2606:4700:3032::6815:2953
  2606:4700:3035::ac43:a342
  $ ip -6 -o addr show scope global | wc -l                # 0
  $ curl -6 -s -o /dev/null -m 10 https://mastodon.300x3.com/api/v1/instance ; echo $?
  7
section: 15-sales-mastodon-openclaw-and-local-ai
---
**New item, raised by the COMM session.** Split out from COMM-06 rather than folded into it,
because it is a distinct fault with a distinct owner: COMM-06 is bootstrap discovery (a
one-time human step), while this is a live availability fault in the federation edge that
is ongoing and will recur until diagnosed.

`cloudflared-alwayson.service` has **not** restarted since 2026-10-01 (`NRestarts=1`), so
every `systemctl is-active` / `NRestarts` check reports this path as healthy. Meanwhile its
four Cloudflare edge connections flap continuously: 26 `Lost connection with the edge`
events in the last hour, 61 in three hours, 450 `failed to serve incoming request` in 24
hours. Each flap drops all four `connIndex` connections simultaneously and re-registers
them ~10 s later, which is exactly why process/unit state cannot detect it.

**Why this is a real fault and not noise.** During the burst, the public edge returned 502
on every path tested: the actor endpoint `/users/bot` five times out of five, plus
`/api/v1/instance`, `/api/v2/instance` and the site root. A 502 on the actor endpoint is
precisely what prevents a remote fediverse server from fetching this instance, so inbound
federation is intermittently unavailable while the instance looks fine locally. The burst
observed this pass ran 2026-10-04T06:21:47Z–19:54:01Z and stopped before the close of this
proposal.

**The origin is not at fault**, which is why this needs its own investigation: zero 5xx in
1,161 lines of `mastodon-web` logs, no delivery errors in 1,872 lines of
`mastodon-sidekiq` logs, and `queue:push_public` / `queue:pull` both at 0. The fault is the
Cloudflare edge-to-tunnel hop.

**Stop condition — not actioned.** Diagnosing this further and changing tunnel transport,
protocol or edge routing is **live network configuration** (README §4.1 rule 12). Prepared
and evidenced, then stopped, per the coordination protocol. This needs the operator and
the session owning §15.4.3. Suggested first step, not yet done: monitor the flap count as
the health signal, and determine whether this is a Cloudflare-side incident or a local
network fault — the current evidence does not distinguish them.

**Traps recorded so the next session does not reach the wrong conclusion (1) and (2).**

1. **Use `curl -4` for every measurement against `mastodon.300x3.com`.** The host
   publishes AAAA records but this machine has no global IPv6 address
   (`ip -6 -o addr show scope global | wc -l` → `0`; `curl -6` exits 7). A default `curl`
   tries the AAAA leg first, fails, then falls back to IPv4 — usually succeeding, so the
   probe *looks* fine, but nondeterministically. That dead v6 leg can surface as `000` or
   as a 502, mimicking the very fault under investigation and inviting the false
   conclusion "the tunnel is dropping requests".
2. **`is-active` and `NRestarts` are not health signals for this unit.** Use the journal
   flap count. Spot-checking between flaps reports a healthy system, which is how the
   earlier COMM-06 proposal wrongly recorded this path as fault-free.

Full detail in new §15.4.10 of the section 15 file.
**Retracting the tunnel-health claim in the earlier `comm-COMM-06.md` proposal.** That
proposal recorded the path as "all 4 connections registered, `protocol=http2`, no inbound
fault" and told the next session not to chase the reconnect lines. Both parts were wrong.
The four connections were re-registering continuously, and the path was returning 502 to
remote servers for stretches at a time. This proposal supersedes that paragraph.

Discovery itself remains confirmed and is not in question: 10 remote domains are known
locally, and `mastodon.social` resolves `bot@mastodon.300x3.com` to id `117327405745705562`
(followers 2) and `admin@mastodon.300x3.com` to id `117327389970897359`. Only the human
Konqueror step remained outstanding from this item's original scope.

**New blocker.** `cloudflared-alwayson.service` has not restarted since 2026-10-01
(`NRestarts=1`), so it looks healthy to every `systemctl` check while its four edge
connections flap: 26 `Lost connection with the edge` events in the hour, 61 in three hours,
450 `failed to serve incoming request` in 24 hours. Each flap drops all four `connIndex`
connections together and re-registers them ~10 s later, so unit state cannot detect it —
**health has to be judged from the journal flap count**.

Observed user-visible effect: during the burst, `/users/bot` returned 502 five times out of
five, and `/api/v1/instance`, `/api/v2/instance` and `/` were all 502 at the same moment.
A 502 on the actor endpoint is exactly what prevents a remote server fetching this
instance. After the burst stopped, the same probes returned 200 twelve times out of twelve,
which is why a spot check during recovery reports a healthy system.

The origin is exonerated: zero 5xx in 1,161 lines of `mastodon-web` logs, no delivery errors
in 1,872 lines of `mastodon-sidekiq` logs, and both push queues empty. The fault is the
Cloudflare edge-to-tunnel hop, and it hits **inbound** federation harder than outbound.

**Measurement trap that will mislead the next session.** `mastodon.300x3.com` publishes AAAA
records but this host has no global IPv6 address (`ip -6 -o addr show scope global | wc -l`
→ `0`; `curl -6` exits 7; `ping -6` → "Network is unreachable"). A default `curl` tries the
AAAA leg first, fails, and falls back to IPv4 — usually succeeding, so the probe looks fine,
but nondeterministically. That failed v6 leg can surface as `000` or as a 502, and the
natural conclusion ("the tunnel is dropping requests") is then wrong. **Use `curl -4` for
every measurement against this host.**

Diagnosing the flap further, and changing tunnel transport, protocol or edge routing, is
**live network configuration** and therefore a stop condition — prepared, not actioned.
New §15.4.10 records it for the operator and the §15.4.3 owner.
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