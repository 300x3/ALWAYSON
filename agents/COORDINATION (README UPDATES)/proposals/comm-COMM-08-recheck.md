---
item: COMM-08
action: update
evidence: |
  # Second pass over the same item, after the COMM-08 flap finding. Everything below was
  # re-measured today rather than carried forward from the earlier proposal.

  # 1. COMM-08 is STILL ongoing. Caught mid-burst this time - the earlier pass happened
  #    to sample a quiet window and I had written "15 min ago: 0" as if it meant calm:
  $ for w in '15 min ago' '1 hour ago' '24 hours ago'; do
      printf '%s: ' "$w"; journalctl --user -u cloudflared-alwayson.service --since "$w" \
        | grep -c 'Lost connection with the edge'; done
  15 min ago: 7
  1 hour ago: 15
  24 hours ago: 381    # was 384 at the previous pass -> persistence, not decay
  $ systemctl --user show cloudflared-alwayson.service -p NRestarts -p ActiveState
  ActiveState=active
  NRestarts=1

  # 2. The OpenClaw bridge is ALIVE and polling. My 20s CPU sample read delta=0 and I
  #    nearly called it stalled; it is a 10s poll loop and short windows read zero:
  $ systemctl --user show mastodon-openclaw-bridge.service -p MainPID -p ActiveState -p NRestarts
  ActiveState=active
  MainPID=788109
  NRestarts=0
  $ t1=$(awk '{print $14+$15}' /proc/788109/stat); sleep 100
  $ t2=$(awk '{print $14+$15}' /proc/788109/stat); echo "delta_ticks=$((t2-t1))"
  delta_ticks=2
  $ cat /proc/788109/wchan
  hrtimer_nanosleep

  # 3. The idle cursor is genuine idleness, NOT a stall. Cursor 7 == newest notification
  #    THE BOT CAN SEE. Notification 8 belongs to the admin account:
  $ cat ~/.openclaw/mastodon-bridge-state.json
  {
    "lastNotificationId": "7",
    "updatedAt": 1790900850.2506645
  }
  $ ls -la ~/.openclaw/mastodon-bridge-state.json
  -rw-rw-r-- 1 scottw scottw 67 Oct  1 17:27 /home/scottw/.openclaw/mastodon-bridge-state.json
  $ podman exec mastodon-db psql -U mastodon -d mastodon -At \
      -c "select id,type,account_id from notifications order by id;"
  7|follow|117363090433277638      <- bot
  8|follow|117363090403638110      <- admin

  # 4. statuses=0 is the documented 2026-10-01 operator wipe, not data loss.
  #    126 rows in the pre-wipe dump; accounts and follows preserved:
  $ podman exec mastodon-db psql -U mastodon -d mastodon -At -c 'select count(*) from statuses;'
  0
  $ awk '/^COPY public.statuses /,/^\\\.$/' \
      /ALWAYSON/backups/mastodon-status-wipe-2026-10-01/statuses-before-wipe.sql | grep -c ''
  126
  $ podman exec mastodon-db psql -U mastodon -d mastodon -At \
      -c 'select (select count(*) from follows), (select count(*) from accounts);'
  4|14

  # 5. D9 port "typo" is RETRACTED - 3300 is correct. Both ports exist and are correct
  #    for different processes. Changing 3300->3000 in the version matrix would have
  #    documented a config that breaks the OpenClaw bridge:
  $ ss -ltnp | grep -E ':3000|:3300'
  LISTEN 127.0.0.1:3000 users:(("rootlessport",pid=8478))   # podman publish -> Puma origin
  LISTEN 127.0.0.1:3300 users:(("python3",pid=2385))       # mastodon-local-proxy.py
  $ ps -p 2385 -o cmd --no-headers
  /usr/bin/python3 /ALWAYSON/scripts/operations/mastodon-local-proxy.py 3300 3000 ...
  $ curl -s  -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/api/v1/instance
  301
  $ curl -sk -o /dev/null -w '%{http_code}\n' https://127.0.0.1:3300/api/v1/instance
  200
  $ grep -n 'API =' /ALWAYSON/scripts/mastodon/mastodon-openclaw-bridge.py
  39:API = 'https://127.0.0.1:3300'
section: 15-sales-mastodon-openclaw-and-local-ai
---
**Status unchanged: COMM-08 stays Open.** My section file gains

---

## Addendum, 2026-10-05 — I retract "NOT bursty", and the control experiment came back inconclusive

Still **Open**. The §15.4.10 conclusion is unchanged and now better supported, but one of
my own supporting claims was wrong and I am retracting it rather than quietly reusing it.
Recorded in section §15.4.13.

```console
$ for w in '15 min ago' '1 hour ago' '6 hours ago' '24 hours ago'; do
    printf '%s: ' "$w"; journalctl --user -u cloudflared-alwayson.service --since "$w" \
      | grep -c 'Lost connection with the edge'; done
15 min ago: 6
1 hour ago: 21
6 hours ago: 90
24 hours ago: 444
$ # distinct flap-bearing minutes + gap histogram between consecutive ones:
distinct_flap_minutes=139
60s x68   120s x2   180s x1   420s x3   480s x5   540s x4   600s x3   660s x2 ...
median_gap=120s  max_gap=4020s
$ journalctl ... -o short-iso | grep 'Lost connection with the edge' | cut -c1-16 \
    | sort | uniq -c | awk '{if($1>=3){g+=$1;n++}else{o+=$1;m++}} \
        END{print "grouped="g" over "n" min"; print "singleton="o" over "m" min"}'
grouped=387 over 105 minutes
singleton=53 over 34 minutes
$ # I fell into the very trap I was documenting, at 15:03 UTC:
$ journalctl --user -u cloudflared-alwayson.service --since '10 minutes ago' \
    | grep -c 'Lost connection with the edge'
0
$ # zero in a 10-min window, five minutes after '15 minutes ago' returned 6.
```

**I retract "NOT bursty".** My previous pass wrote that the loss is "steady, NOT bursty
(~16/hour, one flap roughly every 4 minutes)" and advised future sessions not to sample a
short window because "the rate is steady". Re-measuring the **shape** rather than just the
count shows the opposite: 68 of 138 gaps between flap-bearing minutes are *exactly 60 s*,
and 387 of 444 losses fall in minutes containing 3+ simultaneous losses. The old "every
4 minutes" figure came from dividing total events by hours, which is a *mean* — and a mean
over a bursty process is exactly the statistic that hides burstiness. The advice built on
that mean was actively dangerous, and I demonstrated it on myself: a 0 reading during a
documented active fault is implausible on its face, and I only caught it because the number
was absurd.

**The load-bearing conclusion survives, and the discriminator strengthened.** The PoP
footprint widened from nine to **fourteen** distinct metropolitan points of presence in
24 h (`lax01`–`lax13`, `phx01`, `sjc01`–`sjc10`), against still exactly **four** edge IPs,
still 100 % `protocol=http2`, and a still near-uniform per-connection loss split
(112/111/109/108). Fourteen PoPs across three regions cannot all drop four unrelated
connections inside the same second. The fault remains **upstream of the PoP, common to all
four connections** — the shared local path — and the origin is still exonerated
(`mastodon-web` 5xx in 30 m = 0, sidekiq delivery errors = 0, both queues empty). The
tunnel is exonerated as the origin of the flaps but remains the messenger.

**The control experiment §15.4.11 asked for is now run, and I am recording it as
INCONCLUSIVE, not as a pass.** 110 ticks at 5 s, edge IP against a non-tunnel control,
each tick correlated with a 70 s journal window:

```console
$ # 110 ticks, edge = 104.21.41.83:443, control = mastodon.social:443
SUMMARY ticks=110 edge_ok=110 edge_fail=0 ctrl_ok=110 ctrl_fail=0 flaps_seen_in_windows=0
```

Both paths perfect — because no flaps occurred while it ran. That is not confirmation, and
I have not written it up as such in the section. **A probe whose window contains no events
produces exactly the output a healthy network produces, so it has no discriminating
power.** The honest statement is that the control experiment needs a window containing a
burst, which is now knowable in advance: the burst period is roughly 8–14 minutes, so a
probe must span several burst cycles. A longer probe targeting three bursts is running; if
it also lands in a quiet window the result is again uninformative and I will say so rather
than dress it up.

**A bug in my own probe, recorded because it nearly inverted the conclusion.** My first
probe scored success as `grep -c 'Verify return code: 0'` being *exactly* `1`. The string
legitimately appears **twice** (chain and leaf), so every control tick scored as a failure
— I saw `ctrl_ok=2` and read it as "the control fails continuously while the edge
succeeds", the exact opposite of the truth. I rewrote the check to accept `>= 1`. The
lesson generalises: **a probe's expected value must be a range, not a point**, and a
control arm that is *uniformly* anomalous deserves the same suspicion as one that is
uniformly fine. This is the same class of error as the hostname/seconds field misparse
already recorded above in this file — twice now I have produced a confident number from a
wrong parse, and both times the tell was that the number was absurd or the pattern was too
clean. **Sanity-check the parse before reporting the number.**

**Not actioned, unchanged.** Isolating the local path means changing live network
configuration, which is a stop condition (rule 12), and the edge/network path belongs to
§15.4.3. Public impact remains low but intermittent: inbound federation is unavailable for
a short window at the burst period, while `ActiveState=active` and `NRestarts=1` both read
healthy. **That gap between the health indicators and the actual fault is still the most
dangerous thing in this section**, and the bursty correction makes it worse, because the
quiet periods are exactly when an automated check will pass.
**§15.4.12 "Re-Verification Pass, 2026-10-04 (liveness, not a status refresh)"**. Nothing
here closes the item; it records that the flap has now run for over two days and re-tests
the live claims that rested on artifacts older than 48 h.

**A retraction that must not be actioned: the D9 "port typo" is withdrawn.** My earlier
pass recorded D9 in the drift table as carrying an independent error — "it cites the
loopback proxy at port `3300` where the real origin is `127.0.0.1:3000`" — and told the
owning session to change `3300` → `3000`. **That was wrong and would have introduced a real
fault.** Both ports exist and each is correct for a different process: `3000` is the
Podman-published Puma origin, `3300` is `mastodon-local-proxy.py`, which terminates
self-signed TLS and injects `X-Forwarded-Proto: https`. That is why plain HTTP to `:3000`
answers `301` while `https://…:3300` answers `200`. The OpenClaw bridge's `API` constant is
`https://127.0.0.1:3300` with a pinned CA, and its own comment warns that using `:3000`
produces a TLS handshake against a non-TLS Puma. The version-matrix note names the proxy
correctly, and **the only genuine drift in that note is the `set false` wording** — the
same §15.4.2 error as everywhere else. I got this wrong by assuming an origin port without
checking which process actually listened on each one.

**Second correction: the quoted accounts transcript was inaccurate.** My draft of §15.4.12
showed the `accounts` listing starting at `admin`. It does not — there is a `-99`
`mastodon.internal` tombstone row that sorts first. The conclusion was unaffected (the
`admin`, `bot` and remote `300x3` accounts all survive the wipe, `follows = 4`,
`accounts = 14`), but the transcript in the section is now the real output.

**Three things I got wrong in this pass, recorded because they are the traps:**

1. **A short window read as recovery.** The first flap sample I took returned
   `15 min ago: 0` and the draft called it a quiet window consistent with the known trap.
   On re-measurement the same window read `7`. I had concluded from one sample that the
   window *was* the trap, rather than waiting to see both sides of it.
2. **A 20 s CPU delta called a stall.** `delta_ticks=0` over 20 s on the OpenClaw bridge
   reads as a dead process and is not: a 10 s poll loop doing one HTTPS request per cycle
   costs ~2 ms per iteration, so any window under ~60 s can read zero on a perfectly
   healthy unit. A 100 s sample gives `delta_ticks=2`. Never use a short CPU delta as a
   liveness test for this unit.
3. **The cursor comparison in §15.4.9 was never a valid comparison.** "Cursor is 7,
   `max(notifications.id)` is 8" implies the bridge is one behind. The API view is
   **per-account**: notification 8 is the admin's, so the newest notification the bot can
   see *is* 7, equal to its cursor, and the state file is simply not rewritten when nothing
   newer exists. The 2026-10-01 mtime is expected idleness, not the stale-cursor fault from
   COMM-04 (which is fixed). §5 of the README carries the same pairing and should be read
   with this caveat.

**`statuses` being empty is not data loss.** `count(*) = 0` reconciles exactly with ST-13's
documented 2026-10-01 wipe and its 126-row backup. One operational consequence worth
carrying forward: with zero statuses there is no local post for the federation queues to
carry, so **an empty `queue:push_public` no longer proves outbound delivery works** — it
only proves there is nothing to deliver.

**Not actioned.** Diagnosing the local path and changing tunnel transport remain live
network configuration — a stop condition — and edge/network path belongs to §15.4.3. The
read-only control I ran excludes "TLS to the edge IP is broken" and "general outbound HTTPS
is broken", but it is **not** the confirmation §15.4.11 asked for: a single short-lived
handshake says nothing about stability over the minutes-long window a connector needs. It
needs a deliberate observation window, which no command in this repository provides.
