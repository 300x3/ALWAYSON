---
item: COMM-05
action: update
evidence: |
  # The decisive measurement: there is NO MX record at all for 300x3.com
  $ dig +noall +answer MX 300x3.com; echo "answers=$(dig +noall +answer MX 300x3.com | wc -l)"
  answers=0

  # No SPF, no DMARC, no mail host
  $ dig +noall +answer TXT 300x3.com          # (no output)
  $ dig +noall +answer TXT _dmarc.300x3.com   # (no output)
  $ dig +noall +answer A  mail.300x3.com      # (no output)

  # RFC 5321 5.1 implicit-MX fallback (the A record) does not accept SMTP either:
  $ for IP in 172.67.163.66 104.21.41.83; do
      echo > /dev/tcp/$IP/25 && echo "$IP:25 OPEN" || echo "$IP:25 no-answer/closed"
    done
  172.67.163.66:25 no-answer/closed
  104.21.41.83:25 no-answer/closed

  # And nothing local listens to receive it
  $ ss -lntp | grep -E ':(25|465|587)\b'
  no local SMTP listener on 25/465/587

  # Accounts whose mail is therefore undeliverable
  $ podman exec mastodon-db psql -U mastodon -d mastodon -At -c \
    "select u.id, u.email from users u order by u.id;"
  1|admin@300x3.com
  2|bot@300x3.com
section: 15-sales-mastodon-openclaw-and-local-ai
---
Remains **Open, and I am stopping rather than choosing.** The acceptance criterion was
"delivery confirmed or formally deferred" — I can confirm delivery is **impossible** as
currently configured, but I cannot pick a resolution without operator approval, because
every option touches something on the stop list.

My section file gains a new **§15.4.7 "Inbound and Outbound Mail for the 300X3 Domain"**,
which states the measured position plainly: `300x3.com` has **no MX record**, so all mail
to the domain is silently undeliverable.

The finding is stronger than "unconfigured". With no MX, RFC 5321 §5.1 falls back to the
implicit MX — the domain's A record, which is the Cloudflare edge. I tested port 25 to
both edge addresses directly and neither answers, and there is no local MTA. So the mail
path is not merely unconfigured, it is **closed at every hop**. That affects
`admin@300x3.com` and `bot@300x3.com`, the registered addresses of both local Mastodon
accounts: **password resets and confirmation mail cannot arrive.**

Current operational impact is low, and I want to be precise about why rather than call
this harmless: registration is closed (COMM-03) and there are no pending approvals, so
nothing is presently waiting on a confirmation email. The gap becomes live the moment
anyone needs account recovery.

**Why I stopped instead of choosing.** The options are not equivalent in blast radius:

- **Point MX at a hosted relay** — changes external DNS for the domain and starts routing
  mail to a third party. External record modification plus a new data path.
- **Stand up a local MTA** — a new package (rule 3) and a **new public listener on port
  25** (rule 4), plus a firewall policy change. Explicitly prohibited without operator
  approval.
- **Formally defer** — a documentation decision that address-based recovery is
  unsupported. Zero operational risk, but it should be the operator's call, not mine,
  because it silently accepts that both accounts are unrecoverable by email.

I have prepared and proven the change as far as is safe: the measurements above are
complete and reproducible, and §15.4.7 documents the consequence so the decision can be
made without re-deriving anything. I changed no DNS, installed no package and opened no
port.

Related drift found in the same pass and raised under COMM-01 rather than fixed here:
`scripts/operations/fetch-openclaw-mastodon-env.sh` line 19 still emits
`MASTODON_BOT_EMAIL=300x3@posteo.net`, a superseded third-party mailbox identity that
points at an address on a domain this project no longer controls for mail.

**What I got wrong:** I first ran `dig +short MX 300x3.com` and saw empty output, which I
logged as "MX query returned nothing" — correct, but I nearly treated the empty result as
ambiguous. I re-ran with an explicit `answers=$(dig ... | wc -l)` counter to turn "nothing
printed" into a measured `answers=0`. An empty tool output and a zero count look identical
in a terminal and mean very different things in a report. I also would have written a
stale note earlier that port 25 to Cloudflare was "firewalled"; it did not answer at all,
which is a different observation.