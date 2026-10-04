---
item: COMM-04
action: close
evidence: |
  # Auth half - wallet-held token, VALUE NEVER PRINTED, only length measured:
  $ /ALWAYSON/scripts/ops/wallet-read-secret.py kdewallet ao-mastodon openclaw-bot-access-token | tr -d '\n' | wc -c
  token length (chars) = 43
  $ curl -s -o /tmp/vc.json -w '%{http_code}' -H "Authorization: Bearer $TOK" \
    'https://mastodon.300x3.com/api/v1/accounts/verify_credentials'
  verify_credentials HTTP = 200
  acct = bot | username = bot | id = 117363090433277638

  # Operator decision 2026-10-01 (public) is what is LIVE - checked in BOTH copies:
  $ grep -n "visibility" /ALWAYSON/scripts/mastodon/mastodon-openclaw-bridge.py ~/.local/bin/mastodon-openclaw-bridge.py
  /home/scottw/.local/bin/mastodon-openclaw-bridge.py:281:  'status': answer, 'in_reply_to_id': sid, 'visibility': 'public',
  /ALWAYSON/scripts/mastodon/mastodon-openclaw-bridge.py:281:  'status': answer, 'in_reply_to_id': sid, 'visibility': 'public',

  # Deployed file is a byte-identical COPY, not a symlink (same trap as Quadlets):
  $ sha256sum ~/.local/bin/mastodon-openclaw-bridge.py /ALWAYSON/scripts/mastodon/mastodon-openclaw-bridge.py
  486e7472a4bb7286caf51e66ba089d0fcd341ddb7120262f119a092146199c19  /home/scottw/.local/bin/mastodon-openclaw-bridge.py
  486e7472a4bb7286caf51e66ba089d0fcd341ddb7120262f119a092146199c19  /ALWAYSON/scripts/mastodon/mastodon-openclaw-bridge.py

  # No 401 crash-loop regression; stable since the last restart:
  $ systemctl --user status mastodon-openclaw-bridge.service --no-pager -n 5
  Active: active (running) since Thu 2026-10-01 18:50:55 PDT; 2 days ago
     Main PID: 788109 (python3)

  # Cursor is idle-by-type, NOT the old stale-cursor fault:
  $ cat ~/.openclaw/mastodon-bridge-state.json
  {"lastNotificationId": "7", "updatedAt": 1790900850.2506645}
  $ podman exec mastodon-db psql ... -c "select id, type, from_account_id from notifications"
   id |  type  |         created_at         |       from_acct
  ----+--------+-----------------------------+-----------------------
    7 | follow | 2026-10-01 23:12:45.661759 | 300x3@mastodon.social
    8 | follow | 2026-10-01 23:30:41.337231 | 300x3@mastodon.social
  $ # max(notifications.id)=8 > cursor 7; both rows are type 'follow', which the
  $ # bridge skips by design (`if notification.get('type') not in ('mention','status'): continue`)
section: 15-sales-mastodon-openclaw-and-local-ai
---
Recommend **close**. Both halves of the item were already done on 2026-10-01; this pass
**re-verified** rather than repeated them, and that distinction matters — no new public
post was made, so no external publication occurred without approval.

My section file gains a five-point re-verification record under §15.2, covering:

1. **Auth half confirmed** — `verify_credentials` returns HTTP 200 for `acct=bot`. Token
   length is 43 characters; the value was never printed, only measured.
2. **Operator decision confirmed live** — line 281 is `'visibility': 'public'` with the
   `@author` mention prefix retained, in **both** the `/ALWAYSON` copy and the deployed
   `~/.local/bin` copy. No stale `unlisted` variant is hiding anywhere.
3. **Deployed file identity** — `sha256` `486e7472…99c19` for both, i.e. a
   byte-identical **copy, not a symlink**. Flagged in §15.2 because editing the
   `/ALWAYSON` copy alone will *not* change live behaviour without a unit restart. This is
   the same load-bearing trap documented for Quadlets, and it now applies to this script.
4. **Cursor is idle by type, not the old fault** — `max(notifications.id)` is 8 while the
   cursor is 7. Both rows are `type=follow`, which the bridge skips by design. The
   previously reported stale-cursor fault (cursor *ahead* of the newest id) is fixed, and
   the bridge's own recovery log line is present in the journal:
   `cursor 68 is ahead of newest notification 7; notification ids were reset`.
5. **No 401 crash-loop regression** — the unit has run 2 days without restarting.

The journal also preserves the original fault history for the next session, including the
run of `failed status … HTTP Error 404: Not Found` and the `cursor 68 is ahead of newest
notification 7` recovery. I left those in place rather than cleaning them.

**What I got wrong:** my first two attempts to measure the cursor used a one-line
`echo '...' | podman exec` combination whose embedded SQL quotes collided with the shell
quoting, producing `unexpected EOF while looking for matching '''` and a syntax error. I
had read those two failed turns as *evidence about the database* before noticing they were
shell parse errors — the worst possible failure mode, because an error message can be
mistaken for a null result. I switched to writing probe scripts to `/tmp` with quoted
heredocs and a `Q()` helper, after which no query failed for quoting reasons.

I also initially reported the notification count as `count=2` alongside
`max_notification_id=8`, and briefly worried the bridge was stalled. It is not: `follow` is
not a type the bridge acts on. Checking the `type` column before calling idleness a fault
is the lesson.