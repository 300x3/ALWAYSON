---
item: PAY-04
action: close
evidence: |
  $ psql -h 127.0.0.1 -p 15432 -d salesdb -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY 1;"
         table_name
  -----------------------
   audit_events
   correlation_records
   customer_contacts
   customers
   entitlements
   fulfillment_events
   order_lines
   orders
   payment_provider_events
   payment_references
   product_versions
   products
   receipts
   returns
   sale_contract_lines
   sale_contracts
   sale_evidence
   support_cases
  (18 rows)

  $ psql ... -c "SELECT table_name FROM information_schema.views WHERE table_schema='public';"
   v_corda_entry_readiness
   v_reporting_entitlements
   v_reporting_orders
   v_reporting_receipts
   v_reporting_sale_provenance
  (5 rows)

  # least privilege: reporting role touches views only, zero base tables
  $ psql ... -c "SELECT table_name FROM information_schema.role_table_grants WHERE grantee='sales_reporting_role' ... AND table_name NOT IN (SELECT ... views);"
   table_name
  ------------
  (0 rows)

  $ psql ... -c "SELECT table_name FROM information_schema.role_table_grants WHERE grantee='sales_reporting_role' AND privilege_type='SELECT' AND table_name LIKE 'v\_%';"
   v_corda_entry_readiness
   v_reporting_entitlements
   v_reporting_orders
   v_reporting_receipts
   v_reporting_sale_provenance
  (5 rows)
section: 07-public-storefront-and-payment-policy
---
**PAY-04's acceptance criterion is met and I recommend closing it.** "Live
application schema initialized; read-only reporting views defined" — both halves
are measured true against the running database, not asserted.

§7.3.1 now records the state: 18 base tables (the 14 core tables of §15.1 plus
`correlation_records`, `sale_contracts`, `sale_contract_lines`, `sale_evidence`),
5 reporting views, and the least-privilege reporting boundary — `sales_reporting_role`
has `SELECT` on exactly the five views and on **zero** base tables, which is the
§6 separation the architecture requires.

What I got wrong:

1. **My first two psql attempts failed and I misread why.** I sourced
   `sales-db.env` and exported `PGUSER`, but the shell already had `PGUSER=scottw`
   from the environment and the error was `password authentication failed for user
   "scottw"` — not a missing-variable error, so the obvious cause was wrong. Two
   things bit me: `sales-db.env` has no `POSTGRES_USER` key (I assumed it did),
   and an inherited `PGUSER` beats nothing. The fix was to set `PGUSER` explicitly
   in the same command rather than trusting the sourced file to be complete.
2. **No writes were issued against `salesdb` at any point in this session.** Every
   statement was a `SELECT` against `information_schema`. I deliberately did not
   run the migration files to "make sure" they applied — the database was already
   live and re-running `config/sales/init/*.sql` would be an unapproved write to
   production data for no informational gain.

Scope note for the compiler: PAY-03's *stated criterion* is met and proven, but
its *title* names a Sales API that does not exist. I propose closing PAY-03 on its
criterion and raising a separate new PAY item for the missing API, rather than
holding PAY-03 open against a criterion it already passes. See `pay-PAY-03.md`.

Not done, and deliberately: PAY-04 is closed, but **PAY-03 is not**, and they are
adjacent. The schema is initialized and the reporting views are correct, but the
service that would *use* them does not exist — see `pay-PAY-03.md`.