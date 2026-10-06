---
item: LEDGER-06
action: close
evidence: |
  Added §11.3.1 "Accounting Model for the Authoritative Ledger" to
  agents/COORDINATION (README UPDATES) (README UPDATES)/11-ledger-provenance-archive-and-ipfs/section.md

  $ grep -n '^### 11.3.1' agents/COORDINATION (README UPDATES) (README UPDATES)/11-ledger-provenance-archive-and-ipfs/section.md
  484:### 11.3.1 Accounting Model for the Authoritative Ledger

  $ python3 agents/COORDINATION (README UPDATES) (README UPDATES)/tools/compile.py
  wrote README.md from 21 sections
  $ python3 agents/COORDINATION (README UPDATES) (README UPDATES)/tools/compile.py --check
  identical
section: 11-ledger-provenance-archive-and-ipfs
---
**Third pass, 2026-10-04 — no change to this item.** This is a documentation
item and the model is unaffected by the ledger's build state. Confirmed still
present and still correctly placed inside `## 11.3` (not after the `## 11.4`
heading, which was the error in my first attempt):

```text
$ grep -n '^### 11.3.1\|^## 11.4' agents/COORDINATION (README UPDATES) (README UPDATES)/11-ledger-provenance-archive-and-ipfs/section.md
505:### 11.3.1 Accounting Model for the Authoritative Ledger
617:## 11.4 Corda Does Not Store
```
Ordering is correct — §11.3.1 sits between `## 11.3` and `## 11.4`, so the
mis-nesting described below has not recurred. Closure still stands, with the
same caveat recorded there: **no Corda node exists to enforce the model.**

**Third pass, 2026-10-04 — no change to this item.** This is a documentation
item and the model is unaffected by the ledger's build state. Confirmed still
present and still correctly placed inside `## 11.3` (not after the `## 11.4`
heading, which was the error in my first attempt):

```text
$ grep -n '^## 11.3 \|^### 11.3.1\|^## 11.4' agents/COORDINATION (README UPDATES) (README UPDATES)/11-ledger-provenance-archive-and-ipfs/section.md
438:## 11.3 Corda Stores and Private Data
505:### 11.3.1 Accounting Model for the Authoritative Ledger
614:## 11.4 Corda Does Not Store
```

Ordering is correct — §11.3.1 sits between `## 11.3` and `## 11.4`, so the
mis-nesting described below has not recurred. Closure still stands, with the
same caveat recorded there: **no Corda node exists to enforce the model.**

The §19 criteria offered a choice: "Define the model **or** state that the
ledger records references only and accounting is computed in reporting." I took
the first option, because §3.2 and §11.1 both already declare Corda the
"complete ledger of debits and credits", so defining the model makes existing
architecture text true instead of contradicting it.

§11.3.1 now defines, concretely:

- **Accounts** — a closed set of 8 (`CASH_EU`/`CASH_US`, `CASH_PENDING`,
  `RECEIVABLE_CUSTOMER`, `REVENUE_SALE`, `REVENUE_DIGITAL_TRANSFER`,
  `REFUNDS_PAYABLE`, `TAX_PAYABLE_<jurisdiction>`, `EXPENSE_ARCHIVE`), with the
  rejection rule for anything outside it.
- **Debit/credit semantics** — balanced double-entry, `SUM(debits)=SUM(credits)`
  per transaction per currency, integer minor units, no floats, no suspense
  account, no stored running balance.
- **Immutability** — corrections are reversing transactions, never edits or
  deletes.
- **Currency** — single-currency postings, explicit `FX_REVALUATION` with a
  recorded rate source, no implicit read-time conversion.
- **Posting rule** — "NO EVENT, NO POSTING", with a table binding each event to
  its gate. A provider webhook and a payment validation are explicitly *not*
  postings; only all three §11.2.2 gates together allow one.
- **Reconciliation** against `salesdb` per correlation tuple, with four named
  outcomes and an explicit rule that `salesdb_only` blocks a receipt being called
  final (§11.2.3).
- **The §4.4 accounting report** defined as a computed projection, not a stored
  balance.

The §7.2 tension resolves cleanly: Corda is authoritative for *approved
postings*, PostgreSQL for *source operational data*, and the report is computed
in reporting. §7.2's "Corda does not replace accounting processing" is honoured
by the explicit statement that a posting is evidence, never a payment
instruction.

## What I got wrong

My first edit placed §11.3.1 *after* the `## 11.4` heading, producing a
duplicated `## 11.4` and a mis-nested subsection. I caught it by re-grepping
headings after the edit rather than trusting the diff, and fixed it. Worth
remembering: the editor replaced the first `old_text` match, so anchoring on a
heading that was about to be duplicated is fragile.

## Note for the compiler

This item closes on documentation, not on running code. The model is now
defined; **no Corda node exists to enforce it**. If the operator intends the
weaker reading ("references only"), this is the section to revisit.
---

## Fifth pass, 2026-10-05 — closure survives, but the model has no carrier

Method changed again. Four prior passes re-measured the host and all four reproduced;
I instead audited **§11 against the artefacts it governs**, validating candidates
against `config/ledger/manifest-schema.json` with the real `jsonschema` library rather
than reading the schema.

```text
$ python3 -c 'import importlib.metadata as m; print(m.version("jsonschema"))'
4.26.0

$ for k in account_code side amount currency correlation_id; do
      printf '%-16s %s\n' "$k" "$(grep -c "\"$k\"" config/ledger/manifest-schema.json)"; done
account_code     0
side             0
amount           0
currency         0
correlation_id   0

--- 11.3.1 posting leg (DR CASH_EU 10000 EUR): REJECTED
     Additional properties are not allowed ('account_code', 'amount',
     'correlation_id', 'currency', 'side' were unexpected)

--- 11.3.1 reversing transaction (object_type=reversal): REJECTED
     'reversal' is not one of ['sales_receipt', 'telemetry_batch', 'map_product',
      'vehicle_simulation', 'fabrication_simulation']

--- 11.3.1 correction referencing original: REJECTED
     Additional properties are not allowed ('transaction_ref' was unexpected)
```

**Closure stands** — the §19 criteria are "define the model **or** state references
only", and the model is defined and now internally consistent. But the operator should
know the honest caveat, which is stronger than the earlier "no node enforces it":

- **The model has no implementation surface at all.** Not one of the five fields a
  posting leg is defined to carry exists in the manifest schema. §11.3.1 describes
  something the current wire format cannot express. This is worse than §11.11's
  Finding D (missing correlation tuple) — Finding D broke the *join*; this breaks the
  *posting*.
- **The immutability rule has no mechanism.** Corrections are required to be reversing
  transactions, but `object_type: "reversal"` is not in the enum and `transaction_ref`
  is rejected. An implementer following the schema literally cannot correct a posting
  without doing the thing the rule forbids.
- **`TAX_PAYABLE_<jurisdiction>` is unreachable.** Declared as an account, but no
  posting rule may post to it, and it appears nowhere else in §11.

### Two defects I did fix, inside my own section

Both were in §11.3.1 and both were mine, so both are corrected in this commit:

1. The posting table used `CASH_*`, `RECEIVABLE` and `REVENUE` — **none of which are
   account codes** in the table immediately above it. `RECEIVABLE` and `REVENUE` do
   not exist; the codes are `RECEIVABLE_CUSTOMER`, `REVENUE_SALE`,
   `REVENUE_DIGITAL_TRANSFER`. "Funds transfer verified" also offered "`RECEIVABLE`
   **or** `REVENUE`", which is ambiguous where the balance invariant demands one
   answer.
2. Two rows presented their legs credit-first (`REFUNDS_PAYABLE` CR / `CASH_*` DR),
   which reads as reversed double-entry.

All five posting rows now name real account codes in DR-then-CR order, each a balanced
pair, and §11.3.1 states that explicitly.

### What I got wrong

My first instinct was, again, to re-run the recorded host checks — that is exactly what
four prior passes did. I caught myself because §11.11 had already written the lesson
down: *re-verifying a recorded claim is worth doing once; doing it again is how four
passes in a row all concluded "nothing new"*. The findings came from a question nobody
had asked — **not "is the host in the documented state?" but "does the spec I own
agree with the artefacts it governs?"**

I also nearly invented a tax posting rule to close Finding C. I stopped: tax rates,
jurisdictions and accrual timing are §7.2 / PAY-group decisions and money-adjacent
(README §4.1 rule 14). **Reported, not decided.** Recommend the operator route Finding
C to PAY; it is not a LEDGER item to fix.

### Note for the compiler

Keep LEDGER-06 closed. Recommend §19's note for LEDGER-03 gain: the manifest schema
has **no posting representation**, which blocks the §4.4 accounting report
independently of the gateway being absent. `config/ledger/manifest-schema.json` is not
my file, so I did not edit it.
