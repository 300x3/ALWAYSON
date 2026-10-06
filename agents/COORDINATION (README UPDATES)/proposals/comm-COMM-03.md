---
item: COMM-03
action: close
evidence: |
  $ podman exec mastodon-db psql -U mastodon -d mastodon -At -c \
    "select 'blocks='||(select count(*) from blocks)
          ||' domain_blocks='||(select count(*) from domain_blocks)
          ||' account_domain_blocks='||(select count(*) from account_domain_blocks)
          ||' email_domain_blocks='||(select count(*) from email_domain_blocks)
          ||' canonical_email_blocks='||(select count(*) from canonical_email_blocks)
          ||' follow_requests='||(select count(*) from follow_requests)
          ||' invites='||(select count(*) from invites)
          ||' ip_blocks='||(select count(*) from ip_blocks)
          ||' user_invite_requests='||(select count(*) from user_invite_requests);"
  blocks=0 domain_blocks=0 account_domain_blocks=0 email_domain_blocks=0
  canonical_email_blocks=0 follow_requests=0 invites=0 ip_blocks=0 user_invite_requests=0

  # Every remote actor the instance knows, with type - only TWO are real accounts:
  $ podman exec mastodon-db psql -U mastodon -d mastodon -c \
    "select a.id, a.username||'@'||coalesce(a.domain,'LOCAL') as acct, a.actor_type, left(a.uri,55) from accounts a order by a.id;"
   117363291039359797 | Gargron@mastodon.social                  | Person      | https://mastodon.social/users/Gargron
   117367694533297015 | 300x3@mastodon.social                    | Service     | https://mastodon.social/ap/users/115945980770248178
   117367695188688040 | friendica@sekretaerbaer.de              | Application | https://sekretaerbaer.de/friendica
   117367695212135392 | friendica@fedibook.de                   | Application | https://fedibook.de/friendica
   117367695244881530 | friendica@friendicadev.sekretaerbaer.de | Application | https://friendicadev.sekretaerbaer.de/friendica
   117368179777860689 | veganism.social@veganism.social          | Application | https://veganism.social/actor
   117368179785955239 | mastodon.online@mastodon.online          | Application | https://mastodon.online/actor
   117368179835254487 | universeodon.com@universeodon.com        | Application | https://universeodon.com/actor
   117368179842889957 | mastodonapp.uk@mastodonapp.uk            | Application | https://mastodonapp.uk/actor
   117368179847973497 | rivals.space@rivals.space                | Application | https://rivals.space/actor
   117368179858338456 | cupoftea.social@cupoftea.social          | Application | https://cupoftea.social/actor
  (14 rows total; the 2 not shown are local admin/bot and the internal Application)

  # Local accounts and approval state (users.approved exists in 4.3):
  $ podman exec mastodon-db psql -U mastodon -d mastodon -At -c \
    "select u.id, u.email, a.username||'@'||coalesce(a.domain,'(local)'), coalesce(u.approved::text,'NO-COLUMN'), u.disabled from users u join accounts a on a.id=u.account_id order by u.id;"
  1|admin@300x3.com|admin@(local)|true|f
  2|bot@300x3.com|bot@(local)|true|f
section: 15-sales-mastodon-openclaw-and-local-ai
---
Recommend **close**, with an important contradiction recorded rather than papered over.

The acceptance criterion was "recorded separately from local account follow state", so my
section file gains a new **§15.4.6 "Remote Account Approval and Rejection Record"** — a
standing table, explicitly separate from §15.4.9's follow relationships, holding one row
per remote account with the action taken and its basis. It carries the nine-table row-count
query above as its evidence, and states that nothing in the moderation tables is
self-populating, so a future block or approval must be added as a row by the operator
(per §15.4.1 "Operator duties"). No remote account has been rejected to date.

The judgement call worth the operator's attention: **ten of the twelve remote actors are
`actor_type=Application`, not people.** They are protocol discovery artefacts — a
Mastodon instance or a Friendica node fetching `/actor` during ordinary federation. They
are not sign-ups, not approval candidates, and must not be logged as if they were. §15.4.6
says so explicitly, because "remote account contacted us" and "a user registered" are easy
to conflate when reading an `accounts` table.

Only two remote actors are actual accounts, and both are recorded: `300x3@mastodon.social`
(**accepted**, `actor_type=Service`, `bot=true` — the project's *own* remote identity, so
blocking it would sever the operator's own presence) and `Gargron@mastodon.social`
(**accepted as a remote actor, not followed** — an ordinary local→remote follow, not a
moderation event).

**The contradiction I could not resolve alone.** COMM-03 presupposes an approval workflow,
but registration is closed, so there is no queue to approve from:

```
$ curl -s https://mastodon.300x3.com/api/v1/instance | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('registrations'),d.get('approval_required'))"
False False
```

No `registrations` row exists in `settings` (Mastodon 4.3 treats absent as disabled),
`follow_requests = 0` and `user_invite_requests = 0`. Meanwhile
`config/mastodon/instance-policy.yaml` line 24 still asserts
`registrations: "open with approval gate (approval_required: true)"`. **The policy file and
the running service now disagree.** I corrected my own §15.3 and §15.4.2 to match the
measured service, and raised `instance-policy.yaml` line 24 as drift row **D6** in the
COMM-01 proposal for the session that owns `config/`. I did not edit that file myself.

This does not block the close — the record exists and is now written down — but the
operator should decide whether the intended state is "closed" (in which case D6 is a doc
fix) or "open with approval gate" (in which case **the service configuration is wrong**,
and opening registration is a moderation decision I am not authorised to make).

**What I got wrong:** my first query used `settings.name`, which does not exist in
Mastodon 4.3 — the column is `settings.var`. It returned only `reserved_usernames` via a
fallback and would have supported a false "no registration settings at all". I also queried
`notifications.status_id`, which this schema version does not have. Both errors were loud
(SQL errors, no rows), which is the good case, but for several turns I was reasoning from
empty results as though they were measurements. The `accounts` table also has **no**
`username=''` rows, so an early "orphan account" hypothesis I formed from a count was
simply wrong.