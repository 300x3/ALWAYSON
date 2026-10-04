---
item: OPS-34
action: update
evidence: |
  The datasources directory is NOT empty. An earlier revision of my section 6 stated it was,
  implying no datasource is provisioned. Withdrawn on measurement:

    $ ls config/platform/monitoring/grafana/provisioning/datasources/
    postgres-aostatus.yml
    sqlite-snapshots.yml

  This is consistent with, not in conflict with, the existing OPS-34 record, which states
  seven SQLite stores are provisioned and verified in the running container. OPS-34 is
  already Implemented; I am NOT reopening it and I did not verify it myself.

  I could NOT confirm the live Grafana datasource inventory: host PostgreSQL access failed.

    $ sudo -n -u postgres psql -tAc "select name,type,url from public.data_source" grafana
    sudo: interactive authentication is required

  So the file listing is not proof of what Grafana has actually loaded. Section 6.A.3.1 now
  records the withdrawal and explicitly does not assert the live datasource state.
section: 06-component-boundaries-gui-reporting-tools-and-operator-access
---

My section 6 change is a **correction of my own prior error**, not a change to any open
work item. No §19 row needs to move, and I created no new item ID because §19 defines no
`SPEC` group and my brief assigns me zero open items.

Three substantive corrections to sections 3 and 6, plus the withdrawal above:

1. **§3.3.1 WebODM row — PostGIS claim was wrong.** It said PostGIS "is not installed in
   either database". Measured: PostGIS 2.3.2 **is** installed in `webodm_dev`, the database
   the app actually reads; only `webodm` has just `plpgsql`. My error was asserting a
   database-wide fact from one database's extension list.

2. **§6.A.3 — "SELECT on 5 tables" is "SELECT on five views".** The grants are on
   `v_reporting_orders`, `v_reporting_receipts`, `v_reporting_entitlements`,
   `v_reporting_sale_provenance`, `v_corda_entry_readiness` — all `relkind=v`, owned by
   `sales_migration_role`. My error was reading the claim from a `role_table_grants` shape
   without checking `relkind`; a first probe filtered `relkind='r'` and misleadingly
   suggested the role had *no* privileges at all.

   The read-only boundary is confirmed holding by behaviour, not only by catalogue:
   `select count(*) from orders` as `sales_reporting_role` → `permission denied for table
   orders`; `select count(*) from v_reporting_orders` → succeeds.

3. **Four impossible future dates removed.** I had written "Measured 2026-10-10" in section 6
   (three places) and "Re-checked 2026-10-10" in section 3. Today is 2026-10-04
   (`date -u` → `2026-10-04`), and my own commit `e07e25c` is dated 2026-10-03, so those
   claims could not have been measured when written. Corrected to 2026-10-04 and every quoted
   output re-measured to match. `grep -c '2026-10-10' README.md` → `0`.

## What I got wrong, and why

The common cause of all four errors is that **I wrote measurement claims in section prose
without a command attached, then could not tell later which had been measured.** The future
dates are the clearest proof: nothing can be measured six days ahead. From here I either
attach the command to the claim or leave the date off.

Second trap worth recording: **`pg_class.relkind` matters.** `relkind='r'` is tables only.
The reporting role's entire grant surface is views, so a table-only probe reports a
fully-privileged read-only role as having nothing at all. That inverts the conclusion in the
dangerous direction — it makes a correct boundary look broken.

## Cross-group findings, left alone as required

- **§19 ST-01 (line 60) has malformed HTML.** The text reads ``PostgreSQL `<code>` and Redis
  `</code>8.0.5`<code>``, with the `<code>` delimiters transposed, and the PostgreSQL version
  is missing entirely. Measured host values are PostgreSQL 18.6 and Redis 8.0.5. §19 is
  single-writer and not mine — reported for the compiler to fix.
- **OPS-32 remains open and is unaffected** by anything here. Its shared-role finding is
  orthogonal to my corrections.
- No payments, ledger keys, secrets, backup data, radio, ports or firewall policy were
  touched. One incident to declare: while enumerating `ao-metabase` environment variables I
  printed `MB_DB_PASS` into my session output. The value is not reproduced in any file, the
  README or this proposal, and it is not a credential I created — but per README §4.2 it was
  printed when it should not have been, and the safer method is
  `podman inspect --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -v -i pass`.