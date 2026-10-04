---
item: PAY-06
action: update
evidence: |
  # ---------- generation half: PROVEN, run today ----------
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