---
item: SEC-02
action: update
evidence: |
  Re-measured 2026-10-05. The four legacy-vs-live key comparisons re-run by sha256
  prefix, no values printed, using a key-name regex that includes hyphens:

    $ sed -n 's/^\([A-Za-z0-9_-]*\)=.*/\1/p' ~/.local/share/ao-secrets/legacy-alwayson-folder.env
    mastodon-db-password
    sales-db-password
    webodm-postgres-password
    fabrication-db-password
    $ wc -l < …legacy-alwayson-folder.env   -> 4

  → reproduces the 10-04 table exactly (3 SAME / 1 DIFFERENT). The orphaned
  plaintext copy of live DB credentials is STILL PRESENT and is now ~4 days old:

    $ stat -c '%n %a %y %s' ~/.local/share/ao-secrets/legacy-alwayson-folder.env
    legacy-alwayson-folder.env 600 2026-09-30 22:05 252

  ST-30's `~/secrets/fabrication-db.env` re-checked — still does not exist:

    $ find ~/secrets -name '*fabrication-db*'
    (no output)
    $ ls -la ~/secrets/fabrication-db.env
    ls: cannot access '…': No such file or directory
    $ stat -c '%a %s' ~/.local/share/ao-secrets/fabrication-db.env
    600 100

  The dangling symlink is also still there, still inert:

    ~/secrets/mastodon.env -> /ALWAYSON/secrets/mastodon/mastodon.env  (dangling)

  §14.1.1's stale pointer is now RESOLVED: the subsections it referenced all exist —
  grep for §14.1.x references returns .1 .2 .3 .4 .5 .6 .7 only, every one defined.

  NEW this pass — the §19 ST-12 correction proposed on 10-04 is now MORE wrong, not less.
  ST-12 says the adapter "runs with no DSN and no webhook secret". On disk it now has all
  four keys; in the running process it has one:

    $ sed 's/=.*/=/' ~/.local/share/ao-secrets/payment.env | grep -v '^$'
    PAYMENT_DSN=  PAYPAL_WEBHOOK_ID=  PAYPAL_WEBHOOK_SECRET=  COINBASE_WEBHOOK_SECRET=
    $ podman inspect ao-ingress-payment --format '{{range .Config.Env}}{{println .}}{{end}}' | sed 's/=.*/=/' | sort
    container=  GPG_KEY=  HOME=  HOSTNAME=  PATH=  PAYMENT_DSN=  PYTHON_SHA256=  PYTHON_VERSION=
section: 14-secrets-and-service-identity
---
`update`. The policy/implementation reconciliation itself is done and recorded in
**§14.1.6**; what remains is operator ratification, identical to SEC-01. The two items
share one decision and should close together.

This pass closes the sub-task ST-30 named that I could actually close: §14.1.1's pointer
to a non-existent subsection is resolved — `§14.1.1` now references §14.1.2 through §14.1.7,
all of which exist. Nothing dangles.

**A correction to my own file that matters.** §14.1.3 asserted the `mastodon.env` delivery
copy and its wallet entry were "verified byte-identical by SHA-256 (1043 bytes)". Measured
today they are **not** — the file is 1041 bytes and hashes `07519ca502b612e6`, the wallet
entry is 1043 bytes and hashes `2dba7da35030466f`. Key names are identical (23 keys); two
values differ:

    LOCAL_HTTPS      wallet='false'  file='true'
    RAILS_FORCE_SSL  wallet='false'  file='true'

This is a policy-relevant finding, not a formatting nit: `RAILS_FORCE_SSL` governs whether
the public Mastodon instance redirects HTTP to HTTPS, the wallet is the system of record,
and the two now disagree — with the file, not the wallet, being the value in force. It also
invalidates the assurance §14.1.6 rests on ("every file is rewritten from the wallet on each
refresh"). Recorded in a new §14.1.3 subsection with the per-key comparison; **not
corrected**, because writing either value changes TLS enforcement on a live public service.

**New, and the most operationally urgent thing I found.** The `ao-payment` wallet folder
that SEC-04 recorded as absent **now exists with all four entries present**, and
`payment.env` was re-fetched successfully at 2026-10-04 18:38 with all four keys. SEC-04's
"provisions the four `ao-payment` wallet entries" action has therefore been done — by
someone outside this repository, since no commit creates a wallet folder. **But the fault it
was meant to fix is not fixed**, because the adapter has not restarted:

    $ podman inspect ao-ingress-payment --format '{{.State.StartedAt}}'
    2026-10-01 15:08:41 -0700 PDT

`Config.Env` is a creation-time snapshot, so the container still holds only `PAYMENT_DSN`
and none of the three webhook secrets, while the file beside it is correct. A reviewer
checking files would conclude this is healthy. §14.2.5 step 2 now carries the missing
converse check (file newer than process ≠ health; compare against `Config.Env`).

**What I got wrong.** I probed folder existence with `kwallet-d6 --folder … --read-password`,
which **is not installed on this host** — rc 127. The unguarded pipeline swallowed the
failure, produced an empty string, and reported all nine folders as "absent", which would
have had me re-assert an already-fixed finding as if it were live. Caught by running the
`hasFolder` probe with a nonsense-name control, which correctly returned `False`. The lesson
generalises past this tool: **a negative result from an uncalibrated probe is not evidence
of absence**, and it is especially dangerous when it agrees with what you already believed.