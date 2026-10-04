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
