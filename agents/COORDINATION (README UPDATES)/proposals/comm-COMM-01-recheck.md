---
item: COMM-01
action: update
evidence: |
  # 2026-10-05 pass. All drift rows re-measured against the LIVE tree. UNCHANGED,
  # except D9 which is RETRACTED as an actionable item.

  $ sed -n '7p'  /ALWAYSON/config/mastodon/mastodon.env.example
    LOCAL_DOMAIN=300x3.com
  $ sed -n '17p' /ALWAYSON/scripts/operations/fetch-openclaw-mastodon-env.sh
    printf 'MASTODON_SERVER=https://300x3.com\n'
  $ sed -n '19p' /ALWAYSON/scripts/operations/fetch-openclaw-mastodon-env.sh
    printf 'MASTODON_BOT_EMAIL=300x3@posteo.net\n'
  $ sed -n '20p' /ALWAYSON/config/mastodon/instance-policy.yaml
    registrations: "open with approval gate (approval_required: true) - operator moderation duties per Section 15.4.1"
  $ # line 20 is independently confirmed as the `registrations` key:
  $ grep -n 'registrations' /ALWAYSON/config/mastodon/instance-policy.yaml
    20:  registrations: "open with approval gate ..."

  # D9 RETRACTED - the variables are set true, not false. New §15.4.13 Correction 1.
  $ grep -E '^(RAILS_FORCE_SSL|LOCAL_HTTPS)=' ~/.local/share/ao-secrets/mastodon.env
    RAILS_FORCE_SSL=true
    LOCAL_HTTPS=true
  $ podman inspect mastodon-web --format '{{range .Config.Env}}{{println .}}{{end}}' \
      | grep -E 'RAILS_FORCE_SSL|LOCAL_HTTPS'
    RAILS_FORCE_SSL=true
    LOCAL_HTTPS=true
  $ grep -n 'force_ssl' /ALWAYSON/config/mastodon/patches/production.rb
    config.force_ssl = ENV.fetch('RAILS_FORCE_SSL', 'true') == 'true'

  # 3300 is real - re-derived from scratch, not read back from the earlier retraction.
  $ ss -lntp | grep -E ':(3000|3300|4000)\b'
    LISTEN 127.0.0.1:3000 users:(("rootlessport",pid=8478,fd=5))
    LISTEN 127.0.0.1:3300 users:(("python3",pid=2385,fd=3))
    LISTEN 127.0.0.1:4000 users:(("rootlessport",pid=5967,fd=5))
  $ ps -p 2385 -o lstart,cmd --no-headers
    Thu Oct  1 15:08:14 2026 /usr/bin/python3 /ALWAYSON/scripts/operations/mastodon-local-proxy.py 3300 3000 ...
  $ curl -sk -m 10 https://127.0.0.1:3300/ | grep -oiE '<title>[^<]*</title>'
    <title>Mastodon</title>
  $ curl -sk -m 10 https://127.0.0.1:3300/api/v1/instance   # -> version
    4.3.7
  $ # 3000 over TLS does NOT work - the ports are not interchangeable:
    Traceback (most recent call last):   # TLS handshake against non-TLS Puma

  # D2 is still live - the safe loopback fallback is still dead code:
  $ sed -n '17p;21p' /ALWAYSON/scripts/mastodon/post.sh
    /ALWAYSON/scripts/operations/fetch-openclaw-mastodon-env.sh "$ENV" >/dev/null
    SERVER="${MASTODON_SERVER:-http://127.0.0.1:3000}"

  # Runtime still correct; D6 still contradicted by the live service:
  $ grep '^LOCAL_DOMAIN=' ~/.local/share/ao-secrets/mastodon.env
    LOCAL_DOMAIN=mastodon.300x3.com
  $ curl -4 -s -m 20 https://mastodon.300x3.com/api/v1/instance | python3 -c \
      "import sys,json;d=json.load(sys.stdin);print('registrations=',d.get('registrations'),'approval_required=',d.get('approval_required'),'version=',d.get('version'))"
    registrations= False approval_required= False version= 4.3.7
section: 15-sales-mastodon-openclaw-and-local-ai

**The `3300` correction is confirmed a second time, and this time from scratch.** Rather
than re-reading my own retraction I re-measured: port 3300 is bound by
`mastodon-local-proxy.service`, running since 2026-10-01 with `NRestarts=0`, and it serves
the genuine Mastodon UI (`<title>Mastodon</title>`, `version 4.3.7`). The same
measurement shows `https://127.0.0.1:3000/api/v1/instance` **fails at the TLS layer**, so
the two ports are not interchangeable and normalising the matrix note to `3000` would
break the OpenClaw bridge, whose `API` constant is `https://127.0.0.1:3300`.

I also flagged a trap the earlier pass missed: the live proxy unit at
`~/.config/containers/systemd/mastodon-local-proxy.service` is a **copy** of
`/ALWAYSON/quadlet/operations/mastodon-local-proxy.service`. Editing the repo file alone
will not change the running proxy. That is the same load-bearing invariant already
documented for Quadlets, now shown to apply to a user `.service` unit as well.

**D1, D2, D3, D6 are all unchanged** and re-measured line by line. D2 remains the most
consequential row and remains provably live: `post.sh` line 17 runs the helper on every
invocation and line 21 consumes `MASTODON_SERVER`, so the `:-http://127.0.0.1:3000`
fallback can never fire and every run targets the static storefront.

**What I got wrong:** the D9 error was mine and it came from a bad inference. I had
assumed the phrase "set false but INERT" in a config note described the *deployed* state,
when it was describing an *intended* state that was never applied. I never checked the env
file, I only checked that the note existed. The lesson generalises: a drift-table row that
says "the file claims X" must be paired with a measurement of X before it is issued as an
instruction, or the owning session will "fix" a correct file. I have now amended D9 in the
table itself rather than only in this proposal, so the correction travels with the table.

**Actionable backlog for the owning session is now D1, D2, D3, D4, D5, D6 — six rows, not
eight.** D8 was already correct and D9 is retracted. D6 still needs the operator's
moderation decision (is the intended state "closed", or is the *service* misconfigured?);
that is not mine to make and is unchanged.
---
Remains **Open**, with one row of the backlog **retracted** and one row **independently
re-derived from scratch**. My section file gains **§15.4.13**, and §15.4.8 row D9 is
amended in place so the error cannot be re-read as live.

**D9 is retracted as an actionable item.** I previously recorded D9 as needing the wording
"set false" corrected to "set true". The values are already `true`, in both the live env
file and the running container:

    RAILS_FORCE_SSL=true
    LOCAL_HTTPS=true

So there is no override to correct and nothing is inert — the version-matrix note
describes the mechanism wrongly, but **no edit should be made to that row.** If the
owning session applied my earlier instruction, they would have edited a correct file to
match a false premise. That is one fewer row of real work, and one fewer chance to break a
correct configuration.