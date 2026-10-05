---
item: PAY-02
action: update
evidence: |
  $ sha256sum scripts/payment/ao-payment-adapter.py
  71a74988b0731695f61a7d56d9580a3c8364a3371906fa333c1784638d399f58  (unchanged from 2026-10-03)

  $ grep -c 'def verify_coinbase' scripts/payment/ao-payment-adapter.py
  0
  $ grep -n 'AUTOMATED' scripts/payment/ao-payment-adapter.py
  43:AUTOMATED = ("paypal", "coinbase")
  208:        if provider in AUTOMATED:
  $ grep -rn 'COINBASE_WEBHOOK_SECRET' --include='*.py' --include='*.sh' \
        --include='*.container' --include='*.service' .
  ./scripts/operations/fetch-kwallet-secret.sh:165:   (writes it; never reads it)

  # normalize() called in-process on realistic payloads; no sink, no row written:
  paypal   -> {'provider':'paypal','provider_ref':'',        'amount_cents':None,'currency':'USD'}
  coinbase -> {'provider':'coinbase','provider_ref':'evt-1', 'amount_cents':None,'currency':'USD'}

  $ sed -n '230,232p' scripts/payment/ao-payment-adapter.py
          n = normalize(provider, event)
          if not n["provider_ref"]:
              self._reply(400, {"error": "missing provider reference"})

  $ curl -sS -X POST http://127.0.0.1:8899/webhook/coinbase \
      -H "x-cc-webhook-signature: <hmac over a throwaway secret>" --data-binary '<charge:confirmed>'
  http=401
  {"error": "signature verification failed"}

  $ podman exec ao-sales-db psql -U sales_migration_role -d salesdb -tAc \
      "select 'rows='||count(*) from payment_provider_events;"
  rows=0
section: 07-public-storefront-and-payment-policy
---

**Revision 2, 2026-10-05. Supersedes the revision of 2026-10-04. Adds a fourth
defect.**

**PAY-02 stays OPEN.** The adapter file is byte-identical
(`sha256:71a74988…f58`), so this is a re-measurement, not a re-fix. All three
previously recorded defects still reproduce, and I have added a fourth that is
worse than the three.

**Defect 4 (new): for PayPal the normalized `provider_ref` is the empty string,
so a genuine PayPal payment is rejected with 400 and no record is created at all.**
Earlier revisions described PayPal as losing only `amount_cents`. That understates
it. A real `PAYMENT.CAPTURE.COMPLETED` carries its id at `resource.id`, which
`normalize()` never reads, so `ref` falls through every branch to `""`; the gate at
line 230 (`if not n["provider_ref"]`) then returns 400. The two providers fail
differently and only one of them is visible: **Coinbase** has a wrong-but-present
ref, so it passes the gate and is *written wrongly*; **PayPal** has no ref, so it
is *dropped*. A wrong value looks like data; a rejection looks like an outage.
Cause is structural: `normalize()` (lines 97–121) reads only top-level
`id`/`txn_id`/`payment_id`/`transaction_id` and top-level `amount`/`currency`, and
neither provider puts either field at the top level.

Defects 1–3 re-confirmed unchanged: no `verify_coinbase` exists (`grep -c` → 0),
`AUTOMATED` still contains `coinbase` and both paths gate through `verify_paypal()`
at line 208, and `COINBASE_WEBHOOK_SECRET` is written by the wallet bridge but read
by nothing.

**What I got wrong:**

1. **I initially planned to re-run the previous session's 18/18 harness and cite
   it.** I did not, because `/tmp` is session-local and the harness is gone — the
   same trap the 2026-10-04 revision already documented. I cited the file hash
   instead to show the candidate is not being re-claimed. I have **not**
   re-verified the prepared correction, and §7.2.1 says so.
2. **My first live probe design would have been ambiguous and I changed it.** I
   originally planned to POST a PayPal-shaped event to `/webhook/coinbase` to
   demonstrate defect 2's "200 accepted". That was a bad idea twice over: a 200
   would mean a row was written into `salesdb`, and re-demonstrating a defect is
   not worth creating business state. I used a deliberately unverifiable
   signature instead, so the probe can only return 401 and provably wrote nothing.
   Confirmed: `payment_provider_events` = 0 rows afterwards. **Choose probes that
   cannot succeed when you are only trying to prove a rejection.**
3. The 401 result is easy to misread as "signature verification works". It does
   not. The Coinbase path is gated by `verify_paypal()`, so it rejects a bad
   signature *and* would reject a genuine Coinbase signature. Right answer, wrong
   reason — I have said so explicitly in §7.2 rather than let the 401 stand as
   evidence of a working control.

Not done, deliberately: **no fix applied to the live adapter.** Correcting the
verifier changes which money-bearing events are accepted — §4.1 rule 14 and the
first stop condition of this brief. Acceptance criterion "a test payment event
produces a verified normalized record" is not met and cannot be met without
operator approval. The prepared correction in §7.2.1 stands, unverified since
2026-10-04.

Cross-item, and new since the last revision: the wallet now holds
`PAYPAL_WEBHOOK_ID`, `PAYPAL_WEBHOOK_SECRET` and `COINBASE_WEBHOOK_SECRET` (see
`pay-PAY-01.md`), so the configuration the correction needs **now exists** — but
none of the three is loaded into the running container, which predates
`payment.env`. So even a corrected adapter would find no secret at runtime until
`ao-ingress-payment` is restarted. See `pay-PAY-01.md`; restarting it is the
operator's call.

---

## SUPERSEDED — revision 1 (2026-10-04), retained for audit


**SUPERSEDES the evidence block above, 2026-10-04.** The `/tmp/pay02/` harness and
candidate verifier referenced above **no longer exist on disk**:

```text
$ ls -d /tmp/pay02
ls: cannot access '/tmp/pay02': No such file or directory
```

So the headline **18/18** result and the 5-step HTTP table can no longer be
reproduced or re-checked, and **I do not re-claim them.** This is precisely the risk
the earlier note raised against itself ("I deleted my tests immediately... the
evidence was not reproducible as pasted"). It has now materialised. §7.2.1 states
this explicitly instead of leaving an unreproducible number standing as proof.

**The findings still stand, on fresh evidence.** I re-derived the three defects from
scratch against the live file (unchanged,
`sha256:71a74988b0731695f61a7d56d9580a3c8364a3371906fa333c1784638d399f58`,
`git status` clean, `127.0.0.1:8899/health` → `{"ok": true, "enabled": true}`):

```text
$ python3 /tmp/pay-reprove/repro.py
PayPal documented message string: tid-abc|2026-10-04T22:49:12Z|WH-1|1287485002
crc32 of raw body (decimal): 1287485002
NOTE: body length = 179 -> crc32 differs from the body, as documented
[ao-payment] REJECT paypal: signature mismatch
verify_paypal(genuine PayPal sig) -> False
verify_paypal(adapter's own HMAC) -> True
verify_coinbase defined in file: False
COINBASE_WEBHOOK_SECRET references: 0
AUTOMATED = ('paypal', 'coinbase')

normalize(paypal, real PAYMENT.CAPTURE.COMPLETED) ==
  {"provider":"paypal","event_type":"PAYMENT.CAPTURE.COMPLETED",
   "provider_ref":"WH-1","currency":"USD","amount_cents":null}

normalize(coinbase, real charge:confirmed) ==
  {"provider":"coinbase","event_type":"charge:confirmed",
   "provider_ref":"EV-EVENT-ID","currency":"USD","amount_cents":null}
```

```text
$ grep -n 'webhook/\|verify_paypal(' scripts/payment/ao-payment-adapter.py
60:def verify_paypal(headers, body: bytes, secret: str) -> bool:
192:        if self.path == "/webhook/paypal":
194:        elif self.path == "/webhook/coinbase":
209:            if not verify_paypal(self.headers, body, self.secret):
```

**PAY-02 stays OPEN, and the fix stays unapplied** — deploying it changes which
money-bearing events are trusted to create business state (§4.1 rule 14).

## A defect the previous account did not record

Re-running `normalize()` on a realistic Coinbase `charge:confirmed` shows
**`amount_cents` is `null` for Coinbase too**, not only its `provider_ref` being
wrong. The real payload carries money at `charge.amount.amount`, which
`normalize()` does not read. The earlier write-up framed the Coinbase problem as a
wrong-*reference* problem; it is actually **both** a wrong-reference *and* a
lost-amount problem. Coinbase events lose the money *and* the reconciled reference.
Recorded in §7.2.1.

## A date defect in my own section file

§7.2.1 and one correction note were dated **`2026-10-10`, six days in the future**
(`date -u +%F` → `2026-10-04`; `grep -c '2026-10-10'` → `2`). This is the same
defect class `spec-OPS-34.md` records having removed from §3 and §6 — and it is
still present in §7, so **the class is not retired**. Both are now `2026-10-04`.

## What I got wrong

1. **My first re-proof run crashed** with
   `TypeError: '{!r}' is a built-in class` from `inspect.getsource()`. I had loaded
   the adapter with `importlib.util.spec_from_file_location` and then reused a
   source-introspection idiom that assumes a normally-imported module. *Class of
   bug: introspection that depends on how a module was loaded.* Dropping the
   introspection for a plain `grep` answered the question better and gives the
   reader evidence they can repeat.
2. **I nearly treated that crash as disproof.** The traceback printed *after* the
   two most important assertions had already succeeded. A non-zero exit from a
   partially-completed proof neither refutes the lines above it nor licenses quoting
   only those lines — I re-ran clean before writing any of this down.
3. **§7 still carries `Section 18.4` references.** The dangling-reference class
   `pay-PAY-07.md` flagged is **still open repo-wide**. I did not mechanically
   renumber them to §7.2: the same references live in
   `scripts/payment/ao-payment-adapter.py` (lines 2, 11, 42, 215, 217) and
   `quadlet/payment/ao-ingress-payment.container` (line 15), and `scripts/` and
   `quadlet/` are not files I own. Reported, not touched.

## Note for the compiler

`compile.py --check` reports `DIFFERS`. It reported `DIFFERS` on unmodified
`/ALWAYSON` too, so it is **pre-existing and not mine**. Attributing every hunk,
**two belong to other sessions**: one line in `es-executive-summary` and one
trailing blank line in `09-field-and-lora-architecture`. The remaining hunks are my
own §7 edits, which is expected until the README is recompiled.
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
