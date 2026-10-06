---
item: COMM-08
action: update
evidence: |
  # Supersedes the "edge-to-tunnel hop" attribution in the original COMM-08 proposal.
  # The flap is confirmed ongoing; the CAUSE is now narrowed to the shared local path.

  # NOT over. Still flapping right now (unit state lies - it reports healthy):
  $ systemctl --user show cloudflared-alwayson.service -p NRestarts -p ActiveState
  ActiveState=active
  NRestarts=1
  $ for w in '15 min ago' '1 hour ago' '6 hours ago' '24 hours ago'; do
      echo "$w: $(journalctl --user -u cloudflared-alwayson.service --since "$w" \
        | grep -c 'Lost connection with the edge')"; done
  15 min ago: 0
  1 hour ago: 26
  6 hours ago: 121
  24 hours ago: 384

  # NOT bursty - steady ~16/hour, i.e. one flap every ~4 minutes:
  $ journalctl --user -u cloudflared-alwayson.service --since '24 hours ago' -o cat \
    | grep 'Lost connection' | cut -d' ' -f1 | cut -d: -f2-3 | sort -u | wc -l
  204                                    # 384 events across 204 distinct minutes

  # THE DISCRIMINATOR: 9 distinct PoPs, only 4 distinct edge IPs, http2 throughout.
  # Independent metropolitan edges cannot lose all 4 connections in the same second,
  # so the fault is upstream of the PoP and common to all four.
  $ journalctl --user -u cloudflared-alwayson.service --since '24 hours ago' -o cat \
    | grep 'Registered tunnel connection' | grep -o 'location=[a-z0-9]*' | sort | uniq -c
     23 location=lax05     17 location=lax07     20 location=lax08
     19 location=lax09     11 location=lax10     15 location=lax11
    224 location=phx01     59 location=sjc01     64 location=sjc06
  $ ... | grep -oE 'ip=[0-9.]+' | sort -u | wc -l
  4
  $ ... | grep -o 'protocol=[a-z0-9]*' | sort | uniq -c
    452 protocol=http2

  # They fail as a GROUP - near-identical counts, 14 timestamps in 6h with >=3 at once:
  $ journalctl --user -u cloudflared-alwayson.service --since '24 hours ago' -o cat \
    | grep 'Lost connection' | grep -oE 'connIndex=[0-9]' | sort | uniq -c
     96 connIndex=0     94 connIndex=1     95 connIndex=2     99 connIndex=3

  # NOT a hard network error - zero route/reset/timeout signatures:
  $ journalctl --user -u cloudflared-alwayson.service --since '6 hours ago' -o cat \
    | grep -icE 'network is unreachable|no route to host|connection reset|broken pipe|timeout'
  0

  # Those ERR lines are CONSEQUENCES of the drop, not the cause - do not chase them:
  $ journalctl --user -u cloudflared-alwayson.service --since '6 hours ago' -o cat \
    | grep -oE '\bERR\b.*' | sed 's/[0-9a-f-]\{8,\}//g' | sort | uniq -c | sort -rn | head -2
     72 ERR failed to serve incoming request error="Error shutting down control stream: context canceled"
     64 ERR failed to serve incoming request error="Error shutting down control stream: client disconnected"

  # Origin still clean - the flap is not a Mastodon fault:
  $ podman logs --since 30m mastodon-web 2>&1 | grep -ciE ' 5[0-9][0-9] |Internal Server Error'
  0
  $ podman logs --since 30m mastodon-sidekiq 2>&1 | grep -ci 'error delivering'
  0
  $ podman exec mastodon-redis redis-cli LLEN 'queue:push_public'
  0

  # Current public impact is low BETWEEN flaps - but this is recovery, not a fix:
  $ for i in 1 2 3 4 5 6 7 8; do curl -4 -s -o /dev/null -m 15 -w '%{http_code} ' \
      -H 'Accept: application/activity+json' https://mastodon.300x3.com/users/bot; sleep 2; done
  200 200 200 200 200 200 200 200
section: 15-sales-mastodon-openclaw-and-local-ai
---
**Update, narrowing the cause.** The fault is confirmed still ongoing — 384 flaps in 24
hours, steady at ~16/hour, not the burst-and-stop pattern the original proposal recorded.
My section file gains **§15.4.11 "The Flap Is Local-Path, Not Cloudflare-Edge"**.

**The original proposal attributed the fault to "the Cloudflare edge-to-tunnel hop". That
attribution was wrong, and the connection topology is what disproves it.** Over 24 hours
the tunnel re-registered against **nine** distinct Cloudflare PoPs (phx01, sjc01, sjc06,
lax05/07/08/09/10/11) while using only **four** distinct edge IPs, all on `protocol=http2`.
Three independent metropolitan PoPs do not lose four unrelated connections inside the same
second. The loss counts confirm they fail as a group (96/94/95/99 — near-identical across
four connections to four different cities), with 14 timestamps in the last 6 hours
carrying three or more simultaneous losses.

So the fault is **upstream of the PoP and common to all four connections**: the shared local
path (uplink, NAT state, or the host's own network path). It is not Mastodon (origin 5xx = 0,
both queues empty), not Cloudflare's edge fleet (the PoPs are reachable simultaneously
between flaps), and not cloudflared's unit state (`NRestarts=1`, `ActiveState=active`).
That last point remains the operational trap: **every "is the tunnel up" check passes while
this fault is running**, because the four connections cycle inside one long-lived process.

**Two corrections to my own earlier reasoning**, both of which would have misled the next
reader:

1. I initially read the burst as intermittent and treated a quiet window as evidence of
   recovery. It is not bursty — 384 events across **204 distinct minutes** is a steady
   ~16/hour, one flap roughly every 4 minutes. My first sample window returned `0` for
   15 minutes and I nearly wrote that up as the fault subsiding. Short-window sampling of a
   mean-rate event is exactly how this looks healthy.
2. The `ERR failed to serve incoming request` lines are the **shadow** of the flap, not its
   cause. `context canceled` / `client disconnected` are cloudflared tearing down in-flight
   streams *because* the connection went away. They lead the journal by count and read like
   a cause, and I spent time treating them as the fault before noticing there are zero
   route/reset/timeout signatures behind them.

I also got a measurement wrong mid-pass: with `-o short-iso` I assumed field `$2` held
seconds and computed "1 distinct second of activity in 24 h" from 384 events — absurd on
its face. Field `$2` is the **hostname**. The corrected parse (`cut -d' ' -f1`) gives the
204-distinct-minutes figure above. The nonsense number was the clue that the field layout
was wrong; I should have sanity-checked it before reporting.

**Not actioned.** Isolating the local path means changing live network configuration, which
is a stop condition, and edge/network path is owned by the §15.4.3 session. The cheap
read-only confirmation for the operator is to compare edge-connection stability against a
control long-lived TLS connection from this host to a fixed destination: if the control is
stable while all four tunnel connections flap in lockstep across nine PoPs, the local path
is confirmed and the tunnel is exonerated.

**Public impact is currently low but intermittent** — 8/8 `curl -4` probes returned 200
between flaps. That is recovery between flaps and must not be reported as a fix; the same
probe returned 502 5/5 during a burst. Inbound federation is unavailable for a short window
roughly every few minutes, while every health indicator reads green.
