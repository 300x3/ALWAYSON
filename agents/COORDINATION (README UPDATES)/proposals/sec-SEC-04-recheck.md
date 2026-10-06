---
item: SEC-04
action: update
evidence: |
  SEC-04's stated action — "provisions the four ao-payment wallet entries" — has been
  DONE, by someone outside this repository (no commit creates a wallet folder), but the
  fault SEC-04 describes is NOT closed. Measured 2026-10-05.

  The folder and entries now exist:

    hasFolder(kdewallet, 'ao-payment', app)                  -> True
    hasEntry ao-payment/payment-db-password                   -> True
    hasEntry ao-payment/payment-paypal-webhook-id             -> True
    hasEntry ao-payment/payment-paypal-webhook-secret         -> True
    hasEntry ao-payment/payment-coinbase-webhook-secret       -> True
    CONTROL: hasFolder 'zzz-does-not-exist-9999'             -> False

  `ao-archive` likewise now exists with both pcloud entries present (hasEntry True),
  so SEC-04's two absent folders are now nine present.

  And the env file was re-fetched successfully — four keys, not one:

    $ sed 's/=.*/=/' ~/.local/share/ao-secrets/payment.env | grep -v '^$'
    PAYMENT_DSN=  PAYPAL_WEBHOOK_ID=  PAYPAL_WEBHOOK_SECRET=  COINBASE_WEBHOOK_SECRET=
    $ stat -c '%n %y %s' ~/.local/share/ao-secrets/payment.env
    payment.env  2026-10-04 18:38:34  306

  BUT the running adapter predates the refresh and holds none of it:

    $ podman inspect ao-ingress-payment --format '{{.State.StartedAt}}'
    2026-10-01 15:08:41.645971245 -0700 PDT
    $ systemctl --user show ao-ingress-payment.service -p ActiveEnterTimestamp
    ActiveEnterTimestamp=Thu 2026-10-01 15:08:41 PDT 2026
    $ podman inspect ao-ingress-payment --format '{{range .Config.Env}}{{println .}}{{end}}' \
        | sed 's/=.*/=/' | sort
    container=  GPG_KEY=  HOME=  HOSTNAME=  PATH=  PAYMENT_DSN=  PYTHON_SHA256=  PYTHON_VERSION=

  → Config.Env is a creation-time snapshot. The container has PAYMENT_DSN and none of
  the three webhook keys, while the file on disk has all four. The unit has not
  restarted since the fetch.
section: 14-secrets-and-service-identity
---
SEC-04 should stay **Open**, but its diagnosis needs rewriting: half of it is resolved and
the remaining half is a *different* fault than the one recorded.

Resolved: the wallet provisioning SEC-04 asked for is done, and the fetch that was failing
silently now succeeds — the file went from one key (frozen 2026-09-30) to four keys
(2026-10-04 18:38). §14.1.7's original premise, "the wallet folder the fetcher needs does
not exist", is no longer true, and I have retracted it in §14.1.2 with the control-test
evidence.

Still open, and this is the part that matters: **the delivery mechanism was fixed but never
exercised.** `ao-ingress-payment` has been running since 2026-10-01 15:08:41 and its
environment is a snapshot from that moment. It holds `PAYMENT_DSN` and none of the webhook
secrets. So the adapter is in exactly the state SEC-04 was opened to prevent, and the
on-disk evidence now actively hides it — the file beside it looks correct.

This is a new failure mode from the one SEC-04 described, and it is more dangerous for
diagnosis: the original fault was visible in file mtimes, whereas this one is only visible
by comparing the file to the running process. §14.2.5 step 2 now carries that comparison,
because its existing mtime check only caught the inverse ordering.

**Operator action, one command, not taken by me:**
`systemctl --user restart ao-ingress-payment`. The delivery copy is already correct; no
provisioning or fetch is needed. Not performed — restarting a live payment adapter is a
named stop condition for this session.

**What I got wrong.** My first existence probe used `kwallet-d6`, which is not installed on
this host (rc 127). The pipeline swallowed the failure and reported all nine folders as
absent, so taken at face value I would have re-asserted this very item as still-unprovisioned
and buried the fact that it had actually been fixed. The `hasFolder` nonsense-name control
returning `False` is what separated the two. **An uncalibrated negative result is worse than
no result, because it agrees with what you already believed.**