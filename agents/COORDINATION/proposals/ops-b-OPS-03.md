---
item: OPS-03
action: close
evidence: |
  $ ls -1 scripts/sales/ | wc -l
  7
  $ ls -1 scripts/sales/
  add-pdf-form-fields.py
  autofill-handoff-form.py
  intake-kit-request-pdf.sh
  intake-request-record.py
  intake-to-pdf.sh
  issue-transaction-bundle.sh
  validate-transaction-bundle.sh
  $ ls -l scripts/validation/validate-sale-receipt.sh
  -rwxrwxr-x 1 scottw scottw 1893 Oct  3 18:48 scripts/validation/validate-sale-receipt.sh
section: 16-scripts-and-operational-standards
---
§16.1 now carries **§16.1.2** naming `scripts/sales/` and
`scripts/validation/validate-sale-receipt.sh` as they actually are.

**The item's premise was a stale measurement, and it is retracted.** Both paths
exist and hold the expected content: `sales/` has seven scripts and
`validate-sale-receipt.sh` is present and executable. The "missing" report
predates the scripts landing — `validate-sale-receipt.sh` was written on
2026-10-03 at 18:48, which is after the report was filed. The correct action was
neither "add" nor "repoint" but to re-measure and retract.

The full measured layout of all eighteen `scripts/` subdirectories is now in
§16.1.2 so the next reader does not re-derive it: `bootstrap` 7, `deploy` 6,
`validation` 11, `mapping` 5, `radio` 4, `simulation` 15, `storefront` 4,
`ledger` 4, `backup` 9, `restore` 5, `maintenance` 5, `mastodon` 10,
`operations` 21, `ops` 8, `openclaw` 1, `payment` 3, `sales` 7, `lib` 1, plus
one top-level file `sync-lmstudio-readme-preset.sh`.

Worth flagging to the compiler: the section previously listed directories as
empty while other sections referenced files inside them. That is the failure
mode OPS-03 was created to catch, and it recurs whenever a document is written
from intent rather than from `ls`.