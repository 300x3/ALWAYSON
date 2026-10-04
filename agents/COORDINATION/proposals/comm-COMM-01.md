---
item: COMM-01
action: update
evidence: |
  $ grep -nE '300x3\.com' /ALWAYSON/config/mastodon/mastodon.env.example | grep -v mastodon\.300x3
  7:LOCAL_DOMAIN=300x3.com

  $ grep -n "MASTODON_SERVER|MASTODON_BOT_EMAIL" /ALWAYSON/scripts/operations/fetch-openclaw-mastodon-env.sh
  17:  printf 'MASTODON_SERVER=https://300x3.com\n'
  19:  printf 'MASTODON_BOT_EMAIL=300x3@posteo.net\n'

  $ grep -rn "fetch-openclaw-mastodon-env.sh" /ALWAYSON/scripts/mastodon
  /ALWAYSON/scripts/mastodon/post.sh:17:/ALWAYSON/scripts/operations/fetch-openclaw-mastodon-env.sh "$ENV" >/dev/null
  $ grep -n 'MASTODON_SERVER' /ALWAYSON/scripts/mastodon/post.sh
  21:SERVER="${MASTODON_SERVER:-http://127.0.0.1:3000}"

  # runtime is CORRECT - the drift is only in docs/helpers:
  $ grep '^LOCAL_DOMAIN=' ~/.local/share/ao-secrets/mastodon.env
  LOCAL_DOMAIN=mastodon.300x3.com
section: 15-sales-mastodon-openclaw-and-local-ai
---
Remains **Open**. The reconciliation audit is done and recorded as new §15.4.8 "Known
Configuration Drift Against `mastodon.300x3.com`", with a nine-row table (D1–D9) giving
exact file, line, current value, correct value and consequence for each.

Key finding for the table: **the service runtime is already correct** — the live instance
is genuinely `mastodon.300x3.com` and federation works. All drift is confined to
`config/mastodon/instance-policy.yaml`, `config/mastodon/mastodon.env.example`,
`scripts/operations/fetch-openclaw-mastodon-env.sh` and a stale note in
`config/platform/version-matrix.yaml`. None of those files is owned by this session, so
none was edited here; the table is written so the owning session can apply the edits
without re-deriving anything.

Highest severity is D1: `mastodon.env.example` line 7 still carries `LOCAL_DOMAIN=300x3.com`.
Most *live* is D2: `post.sh` calls the OpenClaw helper on every invocation and consumes
`MASTODON_SERVER`, so every `post.sh` run currently targets the static storefront
`https://300x3.com` rather than the Mastodon host. D3 replaces a superseded `posteo.net`
mailbox identity.

Two items found during this pass were *not* in the original COMM-01 scope and are
flagged for the owning sessions:

1. **D6** — `instance-policy.yaml` line 24 says `registrations: "open with approval gate
   (approval_required: true)"`, which the live instance contradicts (see COMM-03). Two
   files now disagree with the running service.
2. **D9** — `version-matrix.yaml` line 51 carries the *same* wrong claim I had to correct
   in my own section (§15.4.2: `RAILS_FORCE_SSL/LOCAL_HTTPS are set false`), **and** an
   independent typo: it cites the loopback proxy at port `3300` where the real origin is
   `127.0.0.1:3000`.

**What I got wrong:** my first pass grepped for `300x3.com` with a filter designed to
exclude `mastodon.300x3.com`, and I initially reported `version-matrix.yaml` as needing
no reconciliation. That was wrong — the exclusion filter was right but I stopped at the
first two files and did not read the `sales.mastodon` block. Re-reading it found D8 and D9.
Also, my first two DB queries used `settings.name` and `notifications.status_id`; this is
Mastodon **4.3** where the columns are `settings.var` and there is no `status_id` at all.
Both queries errored before any conclusion was drawn, but a reader skimming my earlier
notes would have seen "no registration setting exists" derived from a query that never ran.
Re-ran correctly: `settings.var='registrations'` is absent, and `users.approved` exists
as a column.

Nothing here needs another session's uncommitted work, and no secret value appears — only
key names and non-secret config lines.