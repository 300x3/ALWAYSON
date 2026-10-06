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

  # --- 2026-10-04 re-verification: the two self-corrections, with reproducing commands ---

  # (1) D6 cited instance-policy.yaml line 24 for `registrations`. It is line 20.
  $ sed -n '20p' config/mastodon/instance-policy.yaml
    registrations: "open with approval gate (approval_required: true) - operator moderation duties per Section 15.4.1"
  $ sed -n '24p' config/mastodon/instance-policy.yaml
    db: "mastodon-db (postgres) on ao-sales - does NOT reuse host PG18"      <- unrelated line
  $ # every other drift row re-checked the same way, all correct:
  $ sed -n '7p'  config/mastodon/mastodon.env.example          # D1 -> LOCAL_DOMAIN=300x3.com
  $ sed -n '17p;19p' scripts/operations/fetch-openclaw-mastodon-env.sh  # D2,D3 -> 300x3.com / posteo.net
  $ sed -n '9p'  config/mastodon/instance-policy.yaml          # D4 -> apex + ao-mastodon-federation
  $ sed -n '8p;16p;34p'  config/mastodon/instance-policy.yaml  # D5 -> 300x3.com x3
  $ sed -n '18p;19p'     config/mastodon/instance-policy.yaml  # D7 -> admin/bot correct
  $ sed -n '41p;51p'     config/platform/version-matrix.yaml    # D8 correct, D9 INERT+3300 typo

  # (2) The old "719.9 M peak memory" claim is not reproducible; live value is 14.1M/19.8M.
  $ systemctl --user status mastodon-openclaw-bridge.service --no-pager -n 3
    Active: active (running) since Thu 2026-10-01 18:50:55 PDT; 2 days ago
       Main PID: 788109 (python3)
          Memory: 14.1M (peak: 19.8M, swap: 1.7M, swap peak: 3.5M)
             CPU: 47.247s
  $ systemctl --user show mastodon-openclaw-bridge.service -p MemoryCurrent -p MemoryPeak -p NRestarts
    MemoryCurrent=14839808
    MemoryPeak=20832256
    NRestarts=0
  # 719.9 M appears in no systemd output on this host; it was carried prose, not a measurement.

  # README.md is COMPILED, never hand-edited. Proof this run's README delta is
  # only my own section, generated:
  $ python3 agents/COORDINATION (README UPDATES) (README UPDATES)/tools/compile.py --check
    DIFFERS                      # before recompile: committed README predates c2c5f51's section edits
  $ python3 agents/COORDINATION (README UPDATES) (README UPDATES)/tools/compile.py
    wrote README.md from 21 sections
  $ python3 agents/COORDINATION (README UPDATES) (README UPDATES)/tools/compile.py --check
    identical                    # after recompile: byte-identical to concatenation of sections
  $ git --no-pager diff -U0 -- README.md | grep '^@@'   # all hunks land in 3313..3710
  # section 15 occupies README lines 3140-3712 (computed from MANIFEST.md row order),
  # so every hunk is inside my own section and no other session's text was touched.
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

   **Re-verified independently 2026-10-04 — and two defects in my own section file
   were found and corrected.** Every measurement above reproduced exactly: token
   length 43, `verify_credentials` HTTP 200 `acct=bot`, both copies sha256
   `486e7472…99c19` with `'visibility': 'public'` at line 281, cursor 7 against
   `max(notifications.id)=8` with both rows `type=follow`.

   That re-verification was worth doing even though the item was already done,
   because the previous run's own numbers were not all trustworthy:

   1. §15.4.8 drift row **D6 cited `instance-policy.yaml` line 24** for the
      `registrations` key. It is at **line 20**. `sed -n '24p'` returns an
      unrelated `db:` line. Corrected. Every other line reference in that table
      was re-checked the same way and is correct (D5 lines 8/16/34, D7 lines
      18–19, D8 line 41, D1/D2/D3 lines 7/17/19). This mattered: the table
      exists so another session can apply the edits without re-deriving them,
      and a wrong line number sends them to the wrong line.
   2. §15.2 claimed the service "has consumed 719.9 M peak memory across a clean
      run." Live `systemctl --user status` reports **Memory: 14.1M (peak: 19.8M)**.
      I could not reproduce 719.9 M from any command, so I removed it rather
      than restate it and substituted figures I actually measured.

   **Root cause of both, and the lesson:** the previous run wrote specific numbers
   into prose without a re-readable command attached to each. A drift table is
   only useful if every cell is independently checkable, and a memory figure
   copied from an earlier moment is stale by construction. Rule I am adopting for
   this section: every numeric claim carries the command that reproduces it.

**A third defect found on resume, in the build step rather than the prose.** The
stalled run had edited §15 and left `README.md` uncommitted, but had never
recompiled it, so the committed README did not contain the section work that
commit `c2c5f51` describes. `compile.py --check` returned `DIFFERS` before the
recompile and `identical` after, which is the check the next session should run
first. Had I trusted the working-tree README as current, I would have reported
seven items against a document that did not describe them. README.md is
generated output: the only correct way to change it is to edit the section file
and recompile, never to hand-edit the README.

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