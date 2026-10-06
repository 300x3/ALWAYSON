---
item: PAY-01
action: update
evidence: |
  $ gdbus call --session --dest org.kde.kwalletd6 --object-path /modules/kwalletd6 \
      --method org.kde.KWallet.hasEntry <handle> ao-payment <key> alwayson-ops
  payment-db-password                    (true,)
  payment-paypal-webhook-id              (true,)
  payment-paypal-webhook-secret          (true,)
  payment-coinbase-webhook-secret        (true,)
  # negative controls:
  payment-paypal-webhook-idX             (false,)
  definitely-not-a-key                   (false,)
  payment-db-password read from ao-sales (false,)

  $ ./scripts/operations/fetch-kwallet-secret.sh "$T/payment.env" payment-credentials
  compose exit=0
    key=PAYMENT_DSN                len=106
    key=PAYPAL_WEBHOOK_ID          len=24
    key=PAYPAL_WEBHOOK_SECRET      len=48
    key=COINBASE_WEBHOOK_SECRET    len=48
    PAYMENT_DSN              match=YES
    PAYPAL_WEBHOOK_ID        match=YES
    PAYPAL_WEBHOOK_SECRET    match=YES
    COINBASE_WEBHOOK_SECRET  match=YES
    whole-file: IDENTICAL
  (temp file shredded; no value printed)

  $ podman inspect ao-ingress-payment --format '{{range .Config.Env}}{{println .}}{{end}}' | cut -d= -f1
  container GPG_KEY HOME HOSTNAME PATH PAYMENT_DSN PYTHON_SHA256 PYTHON_VERSION
  $ podman inspect ao-ingress-payment --format 'started={{.State.StartedAt}}'
  started=2026-10-01 15:08:41
  $ stat -c 'payment.env mtime=%y' ~/.local/share/ao-secrets/payment.env
  payment.env mtime=2026-10-04 18:38:34

  $ podman exec ao-sales-db psql -U sales_migration_role -d salesdb -tAc \
      "select 'payment_provider_events rows='||count(*) from payment_provider_events;"
  payment_provider_events rows=0
section: 07-public-storefront-and-payment-policy
---

**Revision 2, 2026-10-05. Supersedes the revision of 2026-10-04, whose central
premise is now false.**

**PAY-01 stays OPEN, but for a materially different reason.** The previous revision
said the four `ao-payment` wallet entries did **not** exist and that `payment.env`
had been hand-written outside the wallet bridge. **That is no longer true and is
retracted in §7.3.1.** All four entries return `true`, negative controls return
`false`, and re-composing `payment.env` through
`fetch-kwallet-secret.sh payment-credentials` reproduces the live file
byte-for-byte. The bridge works and the file is wallet-produced.

Three things remain open, none of them the bridge:

1. **`payment-db-password` is byte-identical to `sales-db-password`** (both 48
   chars, identical SHA-256 prefix). The "two secrets are one secret" problem is
   real but has moved *into the wallet* — seeded by copying. The other three
   entries are genuinely distinct, so this is one duplicated value, not wholesale
   reuse.
2. **The DSN still grants `sales_migration_role`** (full schema-admin) to an
   ingress adapter needing only INSERT on `payment_provider_events`. Unchanged
   §14.1 least-privilege deviation.
3. **NEW — the running container predates its own env file.** Started
   2026-10-01 15:08; `payment.env` last written 2026-10-04 18:38. The live process
   has only `PAYMENT_DSN`; `PAYPAL_WEBHOOK_ID`, `PAYPAL_WEBHOOK_SECRET` and
   `COINBASE_WEBHOOK_SECRET` are **absent from the running adapter** despite being
   in both the file and the wallet. The `ExecStartPre` is non-fatal (`-` prefix), so
   the unit started clean on the older file. A restart is needed to load them; I
   did not restart a payment unit (§4.1 rule 14, rule 12).

**What I got wrong:**

1. **I nearly carried the previous session's "entries do not exist" forward
   without re-measuring.** Had I trusted it, PAY-01 would have been filed on a
   false central premise. Re-running `hasEntry` also walked me straight into a
   trap §7.3.1 already records: `hasEntry`/`hasFolder` take the **handle** as
   parameter 1, not the wallet name; passing `"kdewallet"` gives
   `Error parsing parameter 1 of type "i"`. I had written that trap down myself
   and still hit it, because I composed the command from memory instead of from
   the note.
2. **My first distinctness check was broken and would have produced a false
   "all distinct".** I extracted the password with a greedy `sed` that captured
   `('...',)` including quotes and comma, so every value measured 53 chars — and
   `payment-db-password` vs `sales-db-password` compared **equal for the wrong
   reason**: both were the same mangled string. I caught it only because two
   different keys returning an identical length is implausible. Re-ran with a
   proper `('(.*)',)` capture: real length 48, and the equality is genuine.
   **A comparison that passes for an uninteresting reason is not a passing
   comparison. Always require a negative control to fail.**
3. I could not determine *who* created the wallet entries or *when* — KWallet
   exposes no entry list (`listEntries` → `UnknownMethod`) and no audit log. I am
   not claiming the operator created them; only that they exist now and that this
   session did not create them.

Not done, deliberately: no credential created, written, rotated or deleted; no role
altered; no payment unit restarted; no secret value printed;
`payment_provider_events` still 0 rows. All three remediations need explicit
operator approval and I stopped before them.

Not mine, reported not edited: the comment block in
`quadlet/payment/ao-ingress-payment.container` (~lines 48–58) still says "The
wallet entries for ao-payment do not exist yet" and "Create these four entries
under the ao-payment KDE Wallet folder". Both are now false. `quadlet/` is outside
my owned file list. Worth fixing, because that comment is what would tell the next
agent no restart was needed.

---

## SUPERSEDED — revision 1 (2026-10-04), retained for audit


**INDEPENDENT RE-VERIFICATION 2026-10-04 — findings still hold, item still OPEN.**

I did not take the evidence above on trust. Re-measured read-only:

```text
$ h=$(gdbus call --session --dest org.kde.kwalletd6 --object-path /modules/kwalletd6 \
      --method org.kde.KWallet.open kdewallet 0 alwayson-ops | grep -oE '[0-9]{6,}')
handle=775185618
payment-db-password                (false,)
payment-paypal-webhook-id          (false,)
payment-paypal-webhook-secret      (false,)
payment-coinbase-webhook-secret    (false,)
CONTROL ao-sales/sales-db-password (true,)
```

All four `ao-payment` entries are still absent, and the known-true control still
returns `(true,)` — so the negative results come from a query I have validated, not
from a malformed call. `podman ps` still shows `ao-ingress-payment` up, and
`/health` still returns `{"ok": true, "enabled": true}`.

**No credential was created, read, moved or modified by this session either.** The
four wallet entries must be created by the operator. The remediation proposed above
(distinct `payment-db-password`, a least-privilege role, removal of the hand-written
`payment.env`) is untouched and still needs explicit approval.

---
**PAY-01 stays OPEN. No credential was created, read, moved or modified by this
session.** I am filing this as `update` rather than `close` because the item
cannot be completed by me — the wallet entries must be created by the operator.

The finding that changes the picture: **ST-12's central premise is false.** ST-12
says `ao-ingress-payment` "runs with no DSN" because the `ao-payment` wallet
entries do not exist. The entries indeed do not exist — proven above. But a
`payment.env` exists anyway, mode 0600, containing `PAYMENT_DSN`, and the running
container has it injected. So the adapter is **not** running DSN-less; it is
running with a hand-made DSN whose password is **byte-identical to the
`sales-db` wallet password** (48 chars, identical SHA-256 prefix).

Three consequences, all recorded in §7.3.1 as OPEN:

1. `payment.env` was written by hand on 2026-09-30, **outside** the wallet bridge.
   If the operator ever creates the four `ao-payment` entries, the next
   `ExecStartPre` will overwrite this file in one composed pass and the DSN will
   change to whatever `payment-db-password` holds.
2. The DSN grants `ao-ingress-payment` the **`sales_migration_role`** — the full
   161-grant schema-admin role — where the ingress adapter needs only INSERT on
   `payment_provider_events`. That is a §14.1 least-privilege deviation, and it
   currently hands a payment-facing component schema-admin on the sales database.
3. Two secrets are now one secret. A payment credential duplicating the sales-db
   password means a single compromise of the sales-db password also yields the
   payment adapter's database access. §14.1 treats these as separate credentials.

**I did not remediate any of this.** Rotating a live password, re-scoping a role,
or rewriting a 0600 secrets file are §4.1 rule 14 and rule 12 stop conditions. The
remediation I would propose for approval is: operator creates the four
`ao-payment` entries with a **distinct** `payment-db-password`, a dedicated
`sales_api_role` is granted only the INSERT the adapter needs, and the hand-made
`payment.env` is removed once the wallet path is proven. **That needs explicit
operator approval and I stopped before it.**

What I got wrong:

1. **I got the argument order of `KWallet.hasFolder` wrong on the first attempt**
   and got `Error parsing parameter 1 of type "i"` for all three folder names —
   because the handle is parameter 1, not the folder. The `hasEntry` calls
   happened to have the right order, which is why they returned `(false,)` rather
   than an error. Had I not added a control query (`ao-sales`/`sales-db-password`
   → `(true,)`) I would have been unable to distinguish "the entry is absent" from
   "my query is malformed". **A false result from a query you have not validated
   against a known-true case is not evidence.**
2. **I initially took §7.2's and §19's framing at face value** — that the adapter
   was correctly inert because it had no DSN — and only inspected the container
   when the Quadlet's own comment predicted the opposite of the README. Trusting a
   document that describes live runtime state over measuring the runtime is the
   error here.