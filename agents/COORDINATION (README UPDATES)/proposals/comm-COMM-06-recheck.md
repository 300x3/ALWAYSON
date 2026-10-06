---
item: COMM-06
action: keep-open
evidence: |
  # The health claim in the earlier comm-COMM-06.md proposal is RETRACTED.
  # It said "all 4 connections registered ... no inbound fault", taken from:
  $ journalctl --user -u cloudflared-alwayson.service -n 40 | grep -c 'Registered tunnel connection'
  4
  # That was a single reading between flaps. The real rate:
  $ journalctl --user -u cloudflared-alwayson.service --since '60 min ago' \
      | grep -c 'Lost connection with the edge'
  26
  $ systemctl --user show cloudflared-alwayson.service -p NRestarts
  NRestarts=1
  # and the edge was genuinely returning 502 during the burst:
  $ for i in 1 2 3 4 5; do curl -s -o /dev/null -m 15 -w '%{http_code} ' \
      -H 'Accept: application/activity+json' https://mastodon.300x3.com/users/bot; done
  502 502 502 502 502
  # discovery claim itself is unaffected and re-verified:
  $ curl -4 -s -m 20 'https://mastodon.social/api/v1/accounts/lookup?acct=bot@mastodon.300x3.com' \
      | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['id'],d['followers_count'])"
  117327405745705562 2
section: 15-sales-mastodon-openclaw-and-local-ai
---
**Retraction of the tunnel-health claim in the applied `comm-COMM-06.md` proposal.** That
proposal recorded the federation path as "all 4 connections registered, `protocol=http2`,
no inbound fault" and explicitly told the next session not to chase the reconnect lines in
the journal. Both parts were wrong. The four connections were re-registering continuously,
and the public edge was returning 502 to remote servers in the meantime. The
"no inbound fault" sentence is the specific error and should not be relied on.

Discovery is not in question and is re-verified above: `mastodon.social` resolves
`bot@mastodon.300x3.com` to id `117327405745705562` with 2 followers. From this item's
original scope only the **human Konqueror step** remains.

What was missed is a separate, ongoing availability fault — the cloudflared edge flap,
now tracked as its own item **COMM-08** rather than folded into COMM-06, because COMM-06 is
a one-time discovery step while COMM-08 is a live fault that will recur until diagnosed.
The short version: `NRestarts=1` since 2026-10-01 makes the unit look healthy to any
`systemctl` check while the edge drops all four connections together and re-registers them
~10 s later, 26 times in the last hour, producing 502 on `/users/bot` and every other public
path. The origin is clean (zero 5xx in `mastodon-web`, empty `queue:push_public` and
`queue:pull`), so this is the Cloudflare edge-to-tunnel hop, not Mastodon.

**Measurement trap that will mislead the next session here specifically.** Probe this host
with `curl -4`. It publishes AAAA records but this machine has no global IPv6 address
(`ip -6 -o addr show scope global | wc -l` → `0`), so a default `curl` tries the AAAA leg,
fails, and falls back to IPv4 — usually succeeding, but nondeterministically, and the dead
v6 leg can surface as `000` or a 502. Judging reachability with a default `curl` risks
concluding "the tunnel is dropping requests" from a fault that is in the probe.

Diagnosing the flap, and changing tunnel transport, protocol or edge routing, is live
network configuration and therefore a stop condition — prepared and evidenced, not
actioned. Full detail in new §15.4.10.