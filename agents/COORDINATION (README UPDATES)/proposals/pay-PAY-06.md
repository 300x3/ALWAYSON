---
item: PAY-06
action: update
evidence: |
  $ for b in msmtp sendmail mail mailx mutt swaks s-nail postfix; do command -v $b; done
  msmtp: ABSENT   sendmail: ABSENT   mail: ABSENT   mailx: ABSENT
  mutt: ABSENT    swaks: ABSENT      s-nail: ABSENT postfix: ABSENT

  $ ls -la /etc/msmtprc /etc/s-nail /etc/postfix /etc/exim4
  ls: cannot access '/etc/msmtprc': No such file or directory
  ls: cannot access '/etc/s-nail': No such file or directory
  ls: cannot access '/etc/postfix': No such file or directory
  ls: cannot access '/etc/exim4': No such file or directory

  $ grep -rEl 'smtplib|sendmail|msmtp|SMTPServer|--mail-from' \
      --include='*.py' --include='*.sh' --include='*.container' --include='*.service' .
  (no output)

  # the near-miss:
  $ grep -rniE 'smtp|mailx|sendmail|msmtp|email-relay' quadlet/ config/
  config/mastodon/mastodon.env.example:34:  # --- smtp: Cloudflare Email Routing (pending ...)
  config/mastodon/patches/production.rb:107,115,116,121,129,132,133,134,135  (config.action_mailer.smtp_settings)

  $ podman exec ao-mastodon-web env | cut -d= -f1 | grep -iE 'smtp|mail'
  (no output)
  $ hasEntry ao-mastodon mastodon-smtp-login    -> (false,)
  $ hasEntry ao-mastodon mastodon-smtp-password -> (false,)
  $ hasEntry ao-mastodon mastodon-smtp-server   -> (false,)
section: 07-public-storefront-and-payment-policy
---

**Revision 2, 2026-10-05. Supersedes the revision of 2026-10-04. Re-measurement
only; no mail path was configured and nothing was sent.**

**PAY-06 stays OPEN on the same single missing piece: delivery.** The generation
half remains proven (`scripts/sales/intake-to-pdf.sh`, exit 0, intake record +
work order + 10-field AcroForm overlay). The delivery half remains absent, now
confirmed three ways: no MTA binary, no SMTP config at any of the four standard
paths, and a repo-wide search for `smtplib|sendmail|msmtp|SMTPServer|--mail-from`
across `*.py`, `*.sh`, `*.container`, `*.service` returning **nothing**.

**The new thing this revision adds is a near-miss I want recorded so the next agent
does not lose an hour to it.** Grepping `quadlet/` and `config/` for
`smtp|mailx|sendmail|msmtp|email-relay` returns **15 hits**, which looks at first
glance like a mail path already exists. Every one of them is Mastodon's own
`config.action_mailer.smtp_settings` block in
`config/mastodon/patches/production.rb`, plus one commented-out placeholder in
`config/mastodon/mastodon.env.example` reading "Cloudflare Email Routing (pending
dashboard enablement 2026-10-22)". It is an unrelated component's unconfigured
switch, not a delivery path for `ao-sales`.

I checked rather than assumed:

```text
$ podman exec ao-mastodon-web env | cut -d= -f1 | grep -iE 'smtp|mail'
(no output)
$ hasEntry ao-mastodon mastodon-smtp-login    -> (false,)
$ hasEntry ao-mastodon mastodon-smtp-password -> (false,)
$ hasEntry ao-mastodon mastodon-smtp-server   -> (false,)
```

Not one Mastodon SMTP variable is provisioned and no wallet entry exists, so
Mastodon's mailer has nothing to send through either. Someone proposing to "reuse
the Mastodon mailer" would find it unconfigured.

**What I got wrong:**

1. **My first search was scoped to `scripts/` and `quadlet/` and returned nothing,
   which felt conclusive — and would have been the wrong conclusion.** I widened it
   to `config/` and found 15 `smtp` hits. The honest reading is the opposite of
   "no mail anywhere": there is mail *configuration surface* for Mastodon that is
   inert. Reporting only the narrow search would have understated the tree and
   invited a later agent to "discover" the same hits and treat them as progress.
   **A null result is only as good as the scope you searched.**
2. I did not, at any point, attempt to send mail or install an MTA. Doing so means
   acquiring relay credentials and opening mail egress — §4.1 rule 14 (production
   credentials) and rule 6 (egress). That is the operator's decision.

Not done, deliberately: no MTA installed, no SMTP relay configured, no credential
created, no message sent. The operator's decision remains one of: an SMTP relay
credential plus a sending script, or an API-based transactional mail provider.
Either way the recipient addresses are customer PII and must be checked against
§4.2/§4.3 before anything is sent, which is why the item cannot self-close.

---

## SUPERSEDED — revision 1 (2026-10-04), retained for audit


  $ cd /ALWAYSON && bash scripts/sales/intake-to-pdf.sh \
      /tmp/pay06proof/request.txt /tmp/pay06proof/out
  OK: /tmp/pay06proof/out/request-record.json
  request_number=REQ-2026-10-04033100
  items=1 unresolved=1
  READY: complete request, awaiting operator review
  OK: /tmp/pay06proof/out/00-kit-request-intake-record.pdf
  OK: /tmp/pay06proof/out/00-kit-request-intake-record.html
  OK: /tmp/pay06proof/out/01-kit-request-work-order.pdf
  OK: /tmp/pay06proof/out/01-kit-request-work-order.html
  OK: /tmp/pay06proof/out/00-kit-request-intake-record-fillable.pdf
  fields=10 page=792x612pt
  OK: 1 page - /tmp/pay06proof/out/00-kit-request-intake-record-fillable.pdf
  OK: 1 page - /tmp/pay06proof/out/00-kit-request-intake-record.pdf
  OK: 1 page - /tmp/pay06proof/out/01-kit-request-work-order.pdf
  exit=0

  # outputs: two records + a 10-field fillable AcroForm overlay
  $ ls -l /tmp/pay06proof/out
  -rw-rw-r-- 56043 00-kit-request-intake-record-fillable.pdf
  -rw-rw-r-- 13358 00-kit-request-intake-record.html
  -rw-rw-r-- 48960 00-kit-request-intake-record.pdf
  -rw-rw-r-- 12852 01-kit-request-work-order.html
  -rw-rw-r-- 46136 01-kit-request-work-order.pdf
  -rw-rw-r--  1284 request-record.json

  # the outputs are explicitly non-transactional
  $ grep -oiE 'sale_logged|corda_state|NOT_SUBMITTED|no payment' request-record.json | sort -u
  corda_state
  no payment
  NOT_SUBMITTED
  sale_logged

  # ---------- delivery half: DOES NOT EXIST ----------
  $ for b in msmtp sendmail mailx mail mutt swaks s-nail; do
      printf '%-8s %s\n' "$b" "$(command -v $b || echo ABSENT)"; done
  msmtp    ABSENT
  sendmail ABSENT
  mailx    ABSENT
  mail     ABSENT
  mutt     ABSENT
  swaks    ABSENT
  s-nail   ABSENT

  $ ls -la ~/.msmtprc /etc/msmtprc /etc/postfix /etc/exim4
  ls: cannot access '/home/scottw/.msmtprc': No such file or directory
  ls: cannot access '/etc/msmtprc': No such file or directory
  ls: cannot access '/etc/postfix': No such file or directory
  ls: cannot access '/etc/exim4': No such file or directory

  # nothing in the repo attempts to send anything
  $ grep -rniE 'smtplib|sendmail|msmtp|SMTPServer|--mail-from' \
      --include='*.py' --include='*.sh' --include='*.container' --include='*.service' .
  (no output)

  # the script's own header states the path is one-way
  $ head -18 scripts/sales/intake-to-pdf.sh
  # ALWAYS ON - email intake to printed PDF forms.
  # ...
  # sent anywhere, no payment is taken, no order is created and no Corda state
  # changes: every output carries sale_logged=false, corda_state=NOT_SUBMITTED.
section: 07-public-storefront-and-payment-policy
---
**INDEPENDENT RE-VERIFICATION 2026-10-04 — item still OPEN on the mail path.**

Both halves re-measured today rather than carried forward:

```text
# generation half still works, exit 0, all three PDFs at one page
$ bash scripts/sales/intake-to-pdf.sh /tmp/pay06proof/request.txt /tmp/pay06proof/out2
OK: /tmp/pay06proof/out2/00-kit-request-intake-record-fillable.pdf
fields=10 page=792x612pt
OK: 1 page - /tmp/pay06proof/out2/00-kit-request-intake-record-fillable.pdf
OK: 1 page - /tmp/pay06proof/out2/00-kit-request-intake-record.pdf
OK: 1 page - /tmp/pay06proof/out2/01-kit-request-work-order.pdf
record: /tmp/pay06proof/out2/request-record.json
exit=0

# delivery half still absent
$ for b in msmtp sendmail mailx mutt swaks s-nail; do
      printf '%-8s %s\n' "$b" "$(command -v $b || echo ABSENT)"; done
msmtp    ABSENT
sendmail ABSENT
mailx    ABSENT
mail     ABSENT
mutt     ABSENT
swaks    ABSENT
s-nail   ABSENT
```

**PAY-06 stays OPEN.** Generation is proven and reproducible; delivery does not
exist. No MTA was installed, no SMTP relay configured, no credential created and
nothing sent. The decision between an SMTP relay, an API mail provider, or manual
operator delivery remains the operator's — each carries a different §4.1
exposure, which is why this session does not choose.

The caveat recorded above still applies and still belongs to whoever implements
delivery: the Public Folder is an initialised git working tree with no commits, so
a customer-bearing PDF must be generated into a non-committed path and handed to
the mailer, never into the Public Folder (§4.1 rule 7, §4.2).

---
**PAY-06 stays OPEN, and it is OPEN on a single missing piece: the mail path.**
The criterion is "purchase-request confirmation, receipt, and work-order status
(including expected delivery) each demonstrably sent from `ao-sales` to a
customer **as PDF by email**". Generation is proven; sending does not exist.

**Generation half — PROVEN today, above.** `scripts/sales/intake-to-pdf.sh` runs
end to end at `exit=0` and emits the intake record, the work order, and a
10-field fillable AcroForm overlay, each verified at one page. That is real and
reproducible.

**Delivery half — absent, proven three ways.** No MTA binary on the host, no SMTP
configuration file at any of the four standard paths, and a whole-repo grep for
`smtplib|sendmail|msmtp|SMTPServer|--mail-from` across `*.py`, `*.sh`,
`*.container` and `*.service` returns **nothing**. The path is also deliberately
one-way: the script's own header says "Nothing is sent anywhere, no payment is
taken, no order is created", and the emitted record carries
`sale_logged=false` / `corda_state=NOT_SUBMITTED`.

**I stopped here deliberately.** Installing an MTA or configuring an SMTP relay
means acquiring and storing relay credentials and opening mail egress. That is a
§4.1 rule 14 stop condition (production credentials) and rule 6 (egress/public
entry), and it is the operator's decision, not mine. **No mail was configured, no
credential was created, and nothing was sent.**

What I recorded in **§7.3.1** is the split: the three customer messages §7.3 owes
— purchase-request confirmation, receipt, and work-order status with expected
delivery — can be **generated** as PDFs but **cannot be delivered**. For the
operator's decision, the missing piece is precisely one of: an SMTP relay
credential plus a sending script, or an API-based transactional mail provider,
or a deliberate decision that delivery happens manually by the operator with the
PDFs as the artefact. Each carries a different cost and a different §4.1 exposure,
which is why I am not choosing.

One further finding that belongs to PAY-03, recorded but not acted on: **the
customer-facing receipt and work-order status PDFs that §7.3 owes are not the
same documents this script produces.** This script produces a *Kit Request*
intake record and work order — an information request awaiting operator review,
explicitly not an order. There is no receipt generator, because there is no order
and no Sales API (see `pay-PAY-03.md`). So even once mail exists, two of the three
PAY-06 messages still have no producer.

Two things I got wrong:

1. **My first verification run used a free-form request body and appeared to
   fail** — `items=0`, `INCOMPLETE - missing name, email`, `exit=4`. I nearly
   wrote "the intake path is broken". It is not broken: `intake-request-record.py`
   documents a fixed labelled format (`SUBJECT:` / `NAME:` / `EMAIL:` /
   `KIT REQUESTED:` / `COMMENTS:`), and `exit=4` is the *documented* incomplete
   code. In the correct format it exits 0 and produces all three PDFs. **I should
   have read the script's header before interpreting the first non-zero exit as a
   fault.**
2. **I searched for the storefront at `~/pCloud Drive/Public Folder`** while
   checking whether any deployment had published a customer-facing PDF page. The
   real path is `~/pCloudDrive/PUBLIC FOLDER` (no space, caps), so my search
   returned nothing and would have supported a false "no public artifacts exist"
   claim. Recorded in full in `pay-PAY-05.md`.

Note for whoever picks this up: the pCloud Public Folder has a **`.git`
directory** (`/home/scottw/pCloudDrive/PUBLIC FOLDER/.git`, branch `master`), so
it is an initialised git working tree that any future commit would pick up. It
has **no commits yet**, so nothing is currently tracked — but that is a
protection that rests on nobody running `git add` there, not on a policy. **A PDF
containing a customer's name, email or order detail must not be committed there**
(§4.1 rule 7 and §4.2). Whoever implements delivery should generate PDFs into a
non-committed path and hand them to the mailer, not into the Public Folder.