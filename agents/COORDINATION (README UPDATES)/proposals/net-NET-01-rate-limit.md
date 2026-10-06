---
item: NET-01
action: update
evidence: |
  NET-01 REMAINS OPEN. Two of its three sub-items are still operator decisions.
  But this pass found that §19's description of the item is materially WRONG, and
  one claimed security control does not exist. Both are corrected in my section file.

  === FINDING 1: ao-ingress-payment is IMPLEMENTED AND RUNNING, not unimplemented ===

  §19 says "ao-ingress-payment and ao-egress-archive still require implementation".
  Half of that is false. The payment ingress adapter has been live since 2026-10-01:

    $ systemctl --user is-enabled ao-ingress-payment.service
    generated
    $ systemctl --user is-active ao-ingress-payment.service
    active
    $ systemctl --user status ao-ingress-payment.service --no-pager -n 8 | head -3
    ● ao-ingress-payment.service - ALWAYS ON payment ingress adapter
         Active: active (running) since Thu 2026-10-01 15:08:41 PDT; 3 days ago
    $ podman inspect ao-ingress-payment \
        --format '{{.State.Status}} networks={{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}'
    running networks=ao-payment
    $ curl -sS -o /dev/null -w 'http_code=%{http_code}\n' http://127.0.0.1:8899/health
    http_code=200

  The host-side relay is live too:
    $ systemctl --user is-enabled ao-payment-relay.service
    enabled
    $ systemctl --user is-active ao-payment-relay.service
    active

  ao-egress-archive, by contrast, genuinely does not exist:
    $ systemctl --user is-enabled ao-egress-archive.service
    not-found
    $ ls quadlet/    # no egress-archive directory

  So of the three controlled adapters: one running, one scaffolded-not-enabled,
  one absent. §19 presented two as absent.

  === FINDING 2: A CONTROL THE DOCUMENT ASSERTS DOES NOT EXIST ===

  The §5.1 group B row for ao-ingress-payment claimed "rate limits".
  There is no rate limiting in the code:

    $ grep -n -i 'ratelimit\|rate_limit\|429\|too many' scripts/payment/ao-payment-adapter.py
    EXIT=1 (1 = no match)
    $ grep -o -i '[a-z]*rate[a-z]*' scripts/payment/ao-payment-adapter.py | sort -u
    deliberately
    migrate

  Both "rate" hits are substrings of unrelated words - I checked what they actually
  were rather than trusting the count. The only request-shaping control present is
  MAX_BODY = 256*1024, a body-size cap, which is not rate limiting. No per-IP
  throttle, no token bucket, no 429 path, no Retry-After.

  MITIGATING, so this is not overstated: the listener is loopback-only
  (PublishPort=127.0.0.1:8899) and the Cloudflare Tunnel route that would front it
  is explicitly NOT enabled. No internet-reachable path exists today. It is a latent
  gap, not a live exposure. It must be implemented BEFORE any tunnel route is enabled.

  === WHAT THE ADAPTER GETS RIGHT (measured, and it is a real control set) ===

  - Separate credential: EnvironmentFile=%h/.local/share/ao-secrets/payment.env,
    mode 0600, one key PAYMENT_DSN. Key name and length only; no value read or printed.
  - Signature verified BEFORE state: verify_paypal() recomputes HMAC-SHA256 over
    "transmission-id|transmission-time|body" and compares with hmac.compare_digest;
    failure returns 401 before sink.record() is reached (ao-payment-adapter.py:86-90,
    209-213). An unsigned webhook cannot create business state.
  - Replay defence: 300-second transmission timestamp window, enforced.
  - Fail-closed on missing secret: returns False and logs REJECT rather than accepting.
  - Zelle refused with 501 - §18.4 behaviour, correctly implemented.
  - Least privilege: NoNewPrivileges=true, ReadOnly=true, no extra capabilities,
    Internal=true network, loopback-bound publish port.

  === UNCHANGED BLOCKERS, still operator decisions ===

  1. Segment-level enforcement for ao-build-update. Unchanged and re-verified:
       $ bash scripts/validation/check-network-isolation.sh
       OK: all domain networks present; isolation domains internal-only;
           3 egress networks non-internal by decision; registry matches host (14 = 11 + 3)
       EXIT=0
     The allowlist is enforced in code and unenforced at the segment. Firewall policy.
  2. Separate ao-build-update credentials - a secret acquisition, explicit stop.

  === WHAT I DID NOT DO ===

  I did not edit scripts/payment/ or quadlet/payment/ - not my files, and payment
  processing is an explicit stop condition (README §4.1 rules 14, 15). No payment
  config, no credential, no tunnel route was touched. I did not implement rate
  limiting, because doing so on a payment path needs the operator.

  I also re-verified the registry first rather than assuming the previous pass was
  still true: 14 ao-* networks, 11 Internal=true, 3 Internal=false, all attachment
  counts still matching §5.1.1. Nothing drifted.
section: 05-network-domains-and-controlled-external-access
---
**NET-01 stays open, but §19's description of it was wrong in a way that
understates the system's maturity and, separately, overstated one control. Both
are corrected.**

The substantive finding is one I did not expect to find. NET-01 has said, across
four passes, that `ao-ingress-payment` and `ao-egress-archive` "still require
implementation". One of those adapters has been deployed, enabled, active and
serving health checks since 2026-10-01. `ao-egress-archive` is the only one that
genuinely does not exist. The item's real remaining scope is narrower than §19
describes: it is the `ao-build-update` segment-enforcement decision, the separate
adapter credential, and building `ao-egress-archive` from nothing.

The second finding is the one that should worry the operator. The §5.1 matrix
asserted that `ao-ingress-payment` enforces **"rate limits"**. It does not. There
is no rate limiting in the adapter at all — I confirmed the two `rate` grep hits
were substrings of "deliberately" and "migrate" before reporting the absence. Every
other control that row claims *is* enforced in code: HMAC-SHA256 signature
verification via `hmac.compare_digest` returning 401 before any row is written, a
300-second replay window, fail-closed behaviour when the webhook secret is absent,
Zelle refused with 501, and least-privilege hardening. Rate limiting was the one
line in that row that described an intention rather than an implementation.

I have kept the severity honest: the listener binds `127.0.0.1:8899` and the
Cloudflare Tunnel route that would front it is not enabled, so this is a latent gap
and not a live exposure. The correct reading is a **precondition on any future
public-route enablement** — rate limiting needs to exist before that route does, or
the enablement should be refused. I did not implement it: `scripts/payment/` is not
mine and this is payment processing, an explicit stop condition in my brief and
README §4.1 rules 14 and 15.

**What I got wrong, and the reason, because it generalises.** Four previous NET
passes had treated NET-01 as "one adapter done, two not" and re-verified
`ao-build-update` each time without asking whether the *other two adapters* in the
same group had changed state. I nearly did the same — my first command was a
re-run of `check-network-isolation.sh`, the check I already knew would pass. The
defect was that I started from the previous session's framing of the item instead of
from the item's acceptance criteria. A status table that has said "Deployable" three
times should be the thing you distrust, not the thing you confirm. The re-measure
that mattered took one command; the verification I was about to lead with would have
found nothing.

**This is a cross-group finding and I am reporting rather than acting on it.**
`scripts/payment/ao-payment-adapter.py` and `quadlet/payment/` belong to the PAY
group. The missing rate limiting is theirs to fix and is escalated to them; the
§5.1 matrix row is mine and I corrected it. NET-03's blocker (the phantom
`ao-egress-community` in `topology-model.yaml`, `gui-boundary-matrix.yaml`, and the
generated Grafana JSON) is unchanged and still owned by others — I re-confirmed it
and did not touch it.