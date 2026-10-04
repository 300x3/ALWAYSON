---
item: PAY-02
action: update
evidence: |
  # The correction is now WRITTEN and PROVEN, and deliberately NOT APPLIED.

  # 1. Live file untouched - sha256 identical to the pre-work measurement.
  $ sha256sum scripts/payment/ao-payment-adapter.py
  71a74988b0731695f61a7d56d9580a3c8364a3371906fa333c1784638d399f58  scripts/payment/ao-payment-adapter.py
  $ git --no-pager status --short scripts/payment/
  (no output - scripts/payment/ is clean; the only M under scripts/ is
   scripts/simulation/build-rl-objects.py, another session's uncommitted work)
  $ curl -s -m5 http://127.0.0.1:8899/health
  {"ok": true, "enabled": true}
  $ ss -ltn | grep 18899 || echo "18899 not listening - test server stopped"

  # 2. Unit harness 18/18. Throwaway RSA keypair generated in-process; cert
  # fetch stubbed so the REAL host allowlist and cert->key extraction still run.
  $ python3 /tmp/pay02/test-verifier.py
  [PASS] current verify_paypal rejects PayPal-documented sig
  [PASS] candidate accepts correct PayPal sig
  [PASS] tampered body rejected
  [PASS] wrong webhookId rejected
  [PASS] stale timestamp rejected
  [PASS] current-scheme HMAC forgery rejected by candidate
  [PASS] cert host not permitted: https://evil.example.com/c.pem
  [PASS] cert host not permitted: http://api.paypal.com/c.pem
  [PASS] candidate verify_coinbase accepts real Coinbase event
  [PASS] candidate verify_coinbase rejects PayPal-shaped event
  [PASS] current verify_paypal REJECTS the real Coinbase event (the bug)
  [PASS] current verify_paypal ACCEPTS a PayPal-shaped event (coinbase-path bug)
  [PASS] current normalize amount_cents (None == lost)
  [PASS] current normalize coinbase returns EVENT id, not charge.id
  [PASS] candidate normalize paypal amount_cents: 50000
  [PASS] candidate normalize paypal currency: USD
  [PASS] candidate normalize coinbase provider_ref: chr_123
  [PASS] candidate normalize coinbase amount_cents: 1234
  === SUMMARY === 18/18 checks passed   EXIT=0

  # 3. ACCEPTANCE CRITERION end to end over HTTP. Candidate on spare loopback
  #    port 18899 in --dry-run, so no salesdb row could be written.
  $ python3 /tmp/pay02/e2e-proof.py
  GET /health -> 200 {"ok": true, "enabled": false}
  1. genuine PayPal event, PayPal-documented signature
     POST /webhook/paypal   -> 200 {"accepted": true, "provider": "paypal"}
  2. same event, one byte of body tampered
     POST /webhook/paypal   -> 401 {"error": "signature verification failed"}
  3. genuine Coinbase event, HMAC over the raw body
     POST /webhook/coinbase -> 200 {"accepted": true, "provider": "coinbase"}
  4. PayPal-shaped event posted to the Coinbase path
     POST /webhook/coinbase -> 401 {"error": "signature verification failed"}
  5. Zelle remains manual-only
     POST /webhook/Zelle    -> 501 {"error": "Zelle is manual-reconciliation only (Section 18.4)"}

  # the adapter's own log - the normalized record, with the amount and currency
  # the live code drops:
  DRY-RUN (no DSN): event provider=paypal type=PAYMENT.CAPTURE.COMPLETED
    ref=paypal:3b97c70f1e963687d2da6dbd62f7d7bd amount_cents=50000 currency=USD verified=True
  DRY-RUN (no DSN): event provider=coinbase type=charge:confirmed
    ref=coinbase:9871540c485e614b22a7e30fda45d736 amount_cents=1234 currency=USD verified=True

  # 4. Coinbase is still verified with the PayPal verifier in the LIVE file.
  $ grep -n 'AUTOMATED =' scripts/payment/ao-payment-adapter.py
  AUTOMATED = ("paypal", "coinbase")
  $ grep -c 'COINBASE_WEBHOOK_SECRET' scripts/payment/ao-payment-adapter.py
  0
section: 07-public-storefront-and-payment-policy
---
**PAY-02 stays OPEN. The correction is written and proven; applying it is blocked
on operator approval.**

I previously wrote "I have not written that patch" and cited a test whose output
was confounded. Both statements are now superseded. What changed: I re-read
PayPal's construction from the vendor instead of trusting my own notes, built a
candidate adapter from a copy of the live file in `/tmp`, and proved it twice —
18/18 unit checks, then the acceptance criterion end to end over HTTP in
`--dry-run`.

Three defects in the live code, all still present:

1. **Wrong signature scheme.** The adapter computes
   `HMAC-SHA256(secret, transmission_id | transmission_time | raw_body)`. PayPal
   documents `transmissionId | timeStamp | webhookId | crc32` — CRC-32 of the raw
   body in decimal, verified with the **RSA public key** from the certificate at
   `paypal-cert-url`. It is not a shared-secret HMAC. `webhookId` appears in no
   header and no body; it is listener configuration, which is why the adapter
   could not have been right as written. **As written it rejects every genuine
   PayPal delivery.** This fails *closed*, so it is no-payments-possible rather
   than money-loss.
2. **Coinbase is verified with the PayPal verifier.** `AUTOMATED = ("paypal",
   "coinbase")` and both branches call `verify_paypal`, so `/webhook/coinbase`
   accepts PayPal-shaped events and rejects real Coinbase ones. Step 4 above is
   the regression test for this. `COINBASE_WEBHOOK_SECRET` is provisioned into
   `payment.env` but is referenced **zero** times in the file — a dead secret that
   looks like a live control.
3. **The normalized event model loses the money.** PayPal's amount is at
   `resource.amount.value`, unread, so `amount_cents` is `None`. Coinbase's
   money-bearing reference is `charge.id`, also unread, so the adapter records the
   top-level **event** id instead of the charge — a wrong reference that never
   looks like a failure.

## Why I stopped rather than deploying

Rewriting the verification path changes which money-bearing events are trusted to
create business state — §4.1 rule 14 and this session's first stop condition. The
live file is byte-identical to how I found it.

The decision actually requested is narrower than "ship the fix": it is whether to
accept PayPal and Coinbase webhooks at all. Today's honest consequence is that
**neither provider can complete a payment**, so the fix is not merely an
improvement — it is the precondition for either channel working. Deployment also
needs `PAYPAL_WEBHOOK_ID` and a `COINBASE_WEBHOOK_SECRET` that something reads.

## What I got wrong, and the class of bug behind it

1. **I nearly drew the wrong conclusion from a confounded test.** Both earlier
   attempts printed `REJECT paypal: stale transmission (51806s)`, which looks like
   a signature failure and would have "confirmed" the defect. In fact the
   **freshness check fired first** and neither signature was ever evaluated, so
   that run proved nothing about the scheme. *Class of bug: an assertion in the
   code path under test fired before the one actually being tested, so the test
   measured the wrong thing and still "passed". Anyone acting on PAY-02 should
   check which check fired before trusting the message.* Step 2 above is the
   corrected version and shows the signature check firing for the right reason
   (`signature verification failed`, not `stale transmission`).
2. **I asserted a Coinbase reference was empty. It is not.** I claimed
   `provider_ref` comes back `""` and the adapter answers 400. Real Coinbase
   payloads *do* carry a top-level `id`, so it is recorded — just the **event** id
   rather than the `charge.id` being reconciled. My first test asserted `""` and
   failed; I had written the expectation from the payload shape I imagined rather
   than checking the one PayPal/Coinbase actually send. *Class of bug: writing a
   test expectation from an assumed shape instead of the observed one.* The
   corrected assertion pins the real defect, which is why step 4 and the
   `chr_123` check are stronger than what I originally proposed.
3. **My first cross-provider test could not have worked.** I signed a PayPal
   event with PayPal's RSA scheme and asserted the *current* HMAC verifier would
   accept it — impossible by construction. To demonstrate the defect it had to be
   re-signed with the current adapter's own scheme.
4. **I deleted my tests immediately.** Right for hygiene, wrong for the handoff:
   the evidence was not reproducible as pasted. The harness, the candidate
   builder and the end-to-end proof are now left in `/tmp/pay02/` for the next
   session. They are deliberately **not** committed under `scripts/`, because a
   payment-verification test encodes operator policy, and which providers to
   accept is exactly what is still undecided.
