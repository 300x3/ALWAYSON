---
item: LEDGER-07
action: update
evidence: |
  $ psql -tAc 'select 1'
  psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed:
  FATAL:  role "scottw" does not exist

  $ sudo -n -u postgres psql -tAc "SELECT count(*) FROM pg_tables WHERE schemaname='public';"
  sudo: interactive authentication is required

  $ systemctl --user status ao-ledger-core.service
  Unit ao-ledger-core.service could not be found.

  $ id alwayson-ledger
  id: 'alwayson-ledger': no such user

  $ id ao-ledger
  uid=994(ao-ledger) gid=974(ao-ledger) groups=974(ao-ledger)
section: 11-ledger-provenance-archive-and-ipfs
---
**Stays open. Cannot be closed by an agent session at all.**

## Important correction to §19's evidence

§19 states `cordadb` "holds 0 tables and its owner role has no working password".
**I could not verify the 0-tables claim.** Both PostgreSQL paths are closed to
the agent account, and neither failure means the database is absent — `role
"scottw" does not exist` is an authentication outcome, not a missing database,
and `sudo: interactive authentication is required` says nothing about `cordadb`.

I have recorded in §11.7 that this claim is **carried forward from §19 and NOT
re-verified**, so the next agent does not repeat it as established fact. The
operator can confirm with:

```bash
sudo -u postgres psql -tAc "SELECT count(*) FROM pg_tables WHERE schemaname='public' AND tablename NOT LIKE 'pg_%';"
sudo -u postgres psql -tAc "\du corda"   # inspect role state; do not print the password
```

## What I did establish

- `ao-ledger-core.service` **does not exist** as a unit. No node is running.
- `ao-ledger` exists as uid 994 with home `/home/alwayson-ledger`, nologin shell.
- Corda 4/H2 was already retired 2026-09-29 under operator approval, so "remove
  the previous V4 installation and database" is **already done** — no deletion
  work remains and none was performed.

## Ordering

LEDGER-07 is blocked behind LEDGER-01 (key ceremony) and the `cordadb` role
password. Building the node requires operator-held key material, so it is a stop
condition rather than a task. Until then the ledger is **not production-ready**,
as §19 already states.

Also recorded in §11.7: the native-systemd (non-containerised) ledger core is a
**deliberate documented deviation** from the Podman-and-Quadlet-only rule, since
Corda 5 ships no official image. It widens no listener and uses no `--privileged`.
Recorded so it is not later mistaken for an oversight.