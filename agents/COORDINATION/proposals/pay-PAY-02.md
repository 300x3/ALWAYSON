---
item: PAY-02
action: update
evidence: |
  # 1. The signature scheme is not one PayPal produces.
  # PayPal's documented message string (developer.paypal.com, "Integrate webhooks",
  # Self verification method): transmissionId | timeStamp | webhookId | crc32
  # crc32 = CRC-32 of the RAW BODY in decimal; verified with the RSA public key
  # from the paypal-cert-url certificate. It is NOT an HMAC with a shared secret.
  $ python3   # ran the adapter's verify_paypal against both constructions
  adapter-scheme sig accepted by verify_paypal: False
  PayPal documented message string: tid-abc|2026-10-03T12:00:00Z|WEBHOOK_ID|3222702821
  PayPal-style sig accepted by verify_paypal: False
  [stderr] [ao-payment] REJECT paypal: stale transmission (51806s)

  # 2. Coinbase is verified with the PayPal verifier.
  $ grep -n 'AUTOMATED\|PROVIDERS' scripts/payment/ao-payment-adapter.py
  PROVIDERS = ("website", "paypal", "Zelle", "coinbase", "bank", "manual_reconciliation")
  AUTOMATED = ("paypal", "coinbase")
  # both branches of the handler call verify_paypal(...)

  $ grep -n 'COINBASE_WEBHOOK_SECRET\|PAYPAL_WEBHOOK_ID' scripts/payment/ao-payment-adapter.py
  247: ap.add_argument("--webhook-secret", default=os.environ.get("PAYPAL_WEBHOOK_SECRET", ""))
  256:     if not args.webhook_secret:
  259:     Handler.secret = args.webhook_secret
  # COINBASE_WEBHOOK_SECRET is never referenced anywhere in the file

  # 3. Normalized event model loses the amount and the reference (code reading):
  #    real PayPal PAYMENT.CAPTURE.COMPLETED: money is at resource.amount.value,
  #      normalize() does not read it  -> amount_cents is None
  #    real Coinbase event: reference is at charge.id, normalize() does not read it
  #      -> provider_ref empty -> adapter rejects with 400
section: 07-public-storefront-and-payment-policy
---
**PAY-02 stays OPEN. Its acceptance criterion — "A test payment event produces a
verified normalized record" — is not met, and cannot be met without a change to
how money-bearing events are accepted. I stopped rather than making it.**

The verifier is not conformant with either provider it claims to verify. Three
defects:

1. **Wrong signature scheme.** The adapter computes
   `HMAC-SHA256(secret, transmission_id | transmission_time | raw_body)`. PayPal
   documents `transmissionId | timeStamp | webhookId | crc32` — CRC-32 of the raw
   body, not the body — verified with the RSA public key from the `paypal-cert-url`
   certificate, not a shared HMAC secret. Tested directly: a signature on PayPal's
   documented message string is **rejected** by `verify_paypal`; only the adapter's
   own non-standard construction is accepted. **As written the adapter would reject
   every genuine PayPal delivery.** This fails *closed*, so it is a
   no-payments-possible defect rather than a money-loss one — but it means §7.2's
**Why I did not fix it.** Rewriting the verification path changes which
money-bearing events are trusted to create business state. That is squarely a §4.1
rule 14 stop condition and the brief's first stop condition. I prepared the
finding and stopped. If the operator approves, the fix is: implement the PayPal
documented construction (RSA public key from `paypal-cert-url`, `crc32` of the raw
body, `webhookId` from config, verify `PAYPAL-TRANSMISSION-SIG`), split
`verify_coinbase()` out of the PayPal path against `COINBASE_WEBHOOK_SECRET`, and
fix `normalize()` to read `resource.amount.value` and `charge.id`. **I have not
written that patch** — an unproven change to payment verification sitting in the
tree is worse than an open item.

What I got wrong:

1. **My verifier test was confounded, and I nearly drew the wrong conclusion from
   it.** Both attempts printed `REJECT paypal: stale transmission (51806s)`, which
   looks like the signature check failing and would have supported "confirmed: the
   adapter rejects PayPal-style signatures". In fact the **freshness check fired
   first** and neither signature was ever evaluated, so that run proved nothing
   about the scheme. The first line (`adapter-scheme sig ... False`) is `False` for
   the same reason. I stated this in §7.2 as if it were a clean demonstration and
   it was not — the honest basis for the defect is the code reading plus PayPal's
   own documentation. **Anyone acting on PAY-02 should re-run this with a fresh
   `paypal-transmission-time`**; do not trust the pasted output as a signature
   result.
2. **I built the test in `/tmp` and deleted it immediately after.** Right for
   hygiene, but it means the evidence is not reproducible as pasted. A named test
   under `scripts/validation/` would be better; I did not add one because a
   payment-verification test that encodes a wrong expectation is a liability.
   "signature-verified webhook" control does not exist yet, and `PAYPAL_WEBHOOK_ID`
   and `PAYPAL_WEBHOOK_SECRET` in the Quadlet are the wrong shape for PayPal
   anyway (PayPal needs the cert URL and the webhook ID, not a shared secret).
2. **Coinbase is verified with the PayPal verifier.** `AUTOMATED = ("paypal",
   "coinbase")` and both branches call `verify_paypal`, so the Coinbase endpoint
   accepts PayPal-shaped events and rejects real Coinbase ones.
   `COINBASE_WEBHOOK_SECRET` is provisioned into `payment.env` by the wallet
   bridge but is **never read by any code** — a dead secret that looks like a live
   control.
3. **The normalized event model silently loses the money.** For a real PayPal
   `PAYMENT.CAPTURE.COMPLETED` the amount is at `resource.amount.value`, which
   `normalize()` does not read, so `amount_cents` is `None`. Coinbase nests its
   reference at `charge.id`, also unread, giving an empty `provider_ref` and a 400.