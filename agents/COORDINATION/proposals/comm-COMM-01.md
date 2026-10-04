---
item: COMM-01
action: update
evidence: |
  # Independent re-verification 2026-10-04. All nine drift rows re-measured against the
  # LIVE tree at /ALWAYSON, not against the previous session's notes. UNCHANGED.

  # D1 - mastodon.env.example line 7
  $ sed -n '7p' /ALWAYSON/config/mastodon/mastodon.env.example
  LOCAL_DOMAIN=300x3.com

  # D2 - fetch-openclaw-mastodon-env.sh line 17 (still the apex, not the Mastodon host)
  $ sed -n '17p' /ALWAYSON/scripts/operations/fetch-openclaw-mastodon-env.sh
    printf 'MASTODON_SERVER=https://300x3.com\n'

  # D3 - same file line 19, superseded posteo.net mailbox identity
  $ sed -n '19p' /ALWAYSON/scripts/operations/fetch-openclaw-mastodon-env.sh
    printf 'MASTODON_BOT_EMAIL=300x3@posteo.net\n'

  # D6 - instance-policy.yaml is line 20, CONFIRMING the earlier correction (24 was wrong)
  $ sed -n '20p' /ALWAYSON/config/mastodon/instance-policy.yaml
    registrations: "open with approval gate (approval_required: true) - operator moderation duties per Section 15.4.1"

  # D8/D9 - version-matrix.yaml
  $ sed -n '41p;51p' /ALWAYSON/config/platform/version-matrix.yaml
    local_domain: "mastodon.300x3.com"   # corrected 2026-10-01; was recorded as 300x3.com
    note: "Federated apex deployment: LOCAL_DOMAIN=mastodon.300x3.com served via the Cloud...

  # D2 IS GENUINELY LIVE - the helper is sourced on every post.sh run, so the
  # safe loopback fallback is unreachable and the apex value always wins:
  $ sed -n '17p;21p' /ALWAYSON/scripts/mastodon/post.sh
  /ALWAYSON/scripts/operations/fetch-openclaw-mastodon-env.sh "$ENV" >/dev/null
  SERVER="${MASTODON_SERVER:-http://127.0.0.1:3000}"
  # helper exports MASTODON_SERVER=https://300x3.com -> SERVER resolves to the
  # static storefront, not the Mastodon host. The :- fallback never fires.

  # Runtime is still CORRECT - drift is confined to config/docs/helpers:
  $ grep '^LOCAL_DOMAIN=' ~/.local/share/ao-secrets/mastodon.env
  LOCAL_DOMAIN=mastodon.300x3.com

  # D6 vs the running service: policy file and live service still disagree.
  $ curl -s -m 20 https://mastodon.300x3.com/api/v1/instance \
    | python3 -c "import sys,json;d=json.load(sys.stdin);print('registrations=',d.get('registrations'),'approval_required=',d.get('approval_required'),'version=',d.get('version'))"
  registrations= False approval_required= False version= 4.3.7
section: 15-sales-mastodon-openclaw-and-local-ai
---
Remains **Open**. This is a **re-verification pass**, not new work: I re-measured every
drift row D1–D9 against the live tree rather than trusting the previous session's writeup,
per the protocol rule that another document's claim is a hypothesis and not evidence. All
nine rows are **unchanged**, and the §15.4.8 table in my section file remains accurate as
written. No file was edited this pass.

Three things I confirmed that the earlier notes left implicit:

1. **D2 is the most consequential row and it is definitely live, not theoretical.** I read
   `scripts/mastodon/post.sh` lines 14–24 rather than just grepping the symbol. Line 17
   runs the helper on **every** invocation into a temp env file, line 19 sources it with
   `set -a`, and line 21 reads `${MASTODON_SERVER:-http://127.0.0.1:3000}`. Because the
   helper always exports `MASTODON_SERVER=https://300x3.com`, the safe loopback fallback is
   unreachable and every `post.sh` run targets the static storefront rather than the
   Mastodon host. The earlier note said "every `post.sh` run currently targets" — correct,
   but now proven by reading the call path rather than by inference from two greps.
2. **The D6 line-number correction is right.** `instance-policy.yaml` line 20 carries
   `registrations`, line 24 is an unrelated `db:` entry. This independently reproduces the
   correction made in the COMM-04 proposal.
3. **D6 is still a live contradiction between two files and the running service.** The
   policy file asserts "open with approval gate" while the service reports
   `registrations=False approval_required=False` on Mastodon 4.3.7. Nothing has changed
   this in the interim.

**What I got wrong:** my first instinct was to re-run the same greps the previous session
ran and confirm the strings were unchanged, which would have produced a "verified, still
Open" proposal that added nothing. Re-reading the *call path* rather than the individual
lines is what turned D2 from a string match into a proven live fault — the greps alone
would never have shown that the safe fallback is dead code. I also nearly reported the
tunnel's 15-minute quiet window as this item's edge being healthy before noticing it was
unrelated evidence gathered for COMM-08 (see that proposal).

**Still blocked, unchanged, and not mine to fix.** None of the four drifted files is owned
by this session (`config/` belongs to another session; the helper is another session's
script), so I have edited none of them. The operator decision outstanding on D6 is unchanged:
either the intended state is "closed" (a doc fix) or "open with approval gate" (in which
case **the service configuration is wrong**, and opening registration is a moderation
decision I am not authorised to make).
