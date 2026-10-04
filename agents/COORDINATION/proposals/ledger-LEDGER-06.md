---
item: LEDGER-06
action: close
evidence: |
  Added §11.3.1 "Accounting Model for the Authoritative Ledger" to
  agents/COORDINATION/11-ledger-provenance-archive-and-ipfs/section.md

  $ grep -n '^### 11.3.1' agents/COORDINATION/11-ledger-provenance-archive-and-ipfs/section.md
  484:### 11.3.1 Accounting Model for the Authoritative Ledger

  $ python3 agents/COORDINATION/tools/compile.py
  wrote README.md from 21 sections
  $ python3 agents/COORDINATION/tools/compile.py --check
  identical
section: 11-ledger-provenance-archive-and-ipfs
---
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