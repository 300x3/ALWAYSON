---
item: COMM-02
action: close
evidence: |
  # Primary evidence: the REMOTE following collection on mastodon.social, not local state.
  $ curl -s -H 'Accept: application/json' \
    'https://mastodon.social/api/v1/accounts/115945980770248178/following?limit=80' \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print('count=',len(d)); [print(a['acct'],'|',a['url']) for a in d]"
  count= 2
  admin@mastodon.300x3.com | https://mastodon.300x3.com/@admin
  bot@mastodon.300x3.com   | https://mastodon.300x3.com/@bot

  # Cross-check: local relationship table (all 4 rows, both directions)
  $ podman exec mastodon-db psql -U mastodon -d mastodon -c \
    "select f.id, la.username||'@'||coalesce(la.domain,'LOCAL') as local_acct,
            ta.username||'@'||coalesce(ta.domain,'LOCAL') as target_acct, ta.uri
       from follows f join accounts la on la.id=f.account_id
       join accounts ta on ta.id=f.target_account_id order by f.id;"
   id |       local_acct        |       target_acct       |               target_uri
  ----+-------------------------+-------------------------+----------------------------------------
    1 | bot@LOCAL               | admin@LOCAL             | https://mastodon.300x3.com/users/admin
    2 | Gargron@mastodon.social | bot@LOCAL               | https://mastodon.300x3.com/users/bot
    3 | 300x3@mastodon.social   | bot@LOCAL               | https://mastodon.300x3.com/users/bot
    4 | 300x3@mastodon.social   | admin@LOCAL             | https://mastodon.300x3.com/users/admin
  (4 rows)

  # Our remote mirror DOES know us (inbound half):
  $ curl -s .../accounts/115945980770248178/followers?limit=80
  followers_count= 1
   follower: bot@mastodon.300x3.com https://mastodon.300x3.com/@bot

  # Third-party remote account, paginated to exhaustion - correctly NOT following us:
  $ # 25 pages, 2000 follower entries from mastodon.social
  Gargron: pages=25 total_followers_seen=2000 our_accounts_found=[]
section: 15-sales-mastodon-openclaw-and-local-ai
---
Recommend **close**. The acceptance criterion was "confirmed from the remote `following`
collection and local incoming relationship tables, never inferred from local outgoing
state" — and that is exactly the method used. The decisive evidence is the remote side:
`300x3@mastodon.social`'s `following` collection returns both `admin@mastodon.300x3.com`
and `bot@mastodon.300x3.com`, which no amount of local-table reading could have
manufactured.

My section file gains a new **§15.4.9 "Federation Contact Asymmetry (measured, not a
fault)"**, which records a finding I judged too easy to misread in a later session.

What I found is that the relationship is **not** reciprocal, and someone auditing this
later would reasonably mistake that for drift:

- The remote `following` collection lists both local accounts, but the mirror's
  `followers` collection lists **only** `bot`. Local `follows` rows 3 and 4
  (`300x3@mastodon.social` → `bot`, → `admin`) were created by the *remote* account's own
  requests, not by us.
- `admin` has no outgoing remote follow at all. The only local→remote row in the table is
  `bot → admin` (row 1).
- `Gargron@mastodon.social` was paginated to exhaustion — 25 pages, 2000 follower
  entries — and does not follow any `300x3.com` account. This is *correct*: row 2
  (`Gargron → bot`) records that Gargron follows our bot, which is the remote account's
  business, not a reciprocity requirement.

§15.4.9 states plainly that this asymmetry is how ActivityPub follow requests work, not a
defect, so a future session does not "fix" it by adding follows.

Two supporting negatives are also recorded, because a broken pipeline can look identical
to a quiet one: the sidekiq queues are empty (`LLEN queue:push_public = 0`,
`LLEN queue:pull = 0`, `redis-cli KEYS 'queue:*'` → empty array), and the actor endpoint
answers 200 on five consecutive tries.

**What I got wrong:** my first pagination script reported `300x3@mastodon.social` with
`our_accounts_found` listing `bot@mastodon.300x3.com` **25 times**, and
`total_followers_seen=25`. That is not 25 followers. The mirror has exactly one follower.
The bug was mine: I passed `max_id` from the last item of each page but never stopped, so
with a single-item result set the loop re-requested the same page 25 times. I nearly
recorded "the remote mirror has 25 followers of our bot" as evidence. The single
authoritative call (`limit=80`, no pagination) returns `followers_count= 1`, which is what
§15.4.9 records. Lesson: an unpaginated endpoint call should be the *first* measurement,
not the fallback after a paginating one looks odd.

A separate transient also nearly became a false finding: the actor endpoint
`https://mastodon.300x3.com/users/bot` returned **502** on the first probe. Re-probing
five times returned 200 every time, and `/api/v1/instance`, `/api/v2/instance` and `/` all
returned 200. I recorded it as transient rather than as a fault — one observation is not a
finding, and `mastodon.social` WebFinger answering 404 for our accts is likewise normal
(Mastodon does not federate WebFinger for accounts it has no local record of).