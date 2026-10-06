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

  # --- third pass, 2026-10-04: the runbook's "state after scaffold" is wrong
  # in two further places, neither of which any prior pass checked ---
  $ loginctl show-user ao-ledger -p Linger
  Failed to get user: User ID 994 is not logged in or lingering

  $ loginctl list-users
   UID USER   LINGER STATE
  1000 scottw yes    active
  1 users listed.

  $ ls -d /run/user/994
  ls: cannot access '/run/user/994': No such file or directory

  $ systemctl --user list-unit-files | grep -iE 'ledger|corda'   # rc=1, no output
  $ systemctl list-unit-files          | grep -iE 'ledger|corda' # rc=1, no output
  $ find /etc/systemd /usr/lib/systemd ~/.config/systemd \
         -iname '*ledger*' -o -iname '*corda*'                   # no output

  $ find quadlet -iname '*ledger*'
  quadlet/networks/ao-ledger-core.network
  quadlet/networks/ao-ledger-ingest.network

  # the runbook's own step-5 substitution collapses
  $ id -u alwayson-ledger
  id: 'alwayson-ledger': no such user
  $ echo "XDG_RUNTIME_DIR=/run/user/$(id -u alwayson-ledger 2>/dev/null)"
  XDG_RUNTIME_DIR=/run/user/
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

## Third pass, 2026-10-04 — a fourth blocker, and it is not a key ceremony

§11.7 lists three blockers, all of them credential work. There is a fourth that
the first two passes missed, because both checked only the account **name** in
`docs/runbooks/ledger-bootstrap.md` and then stopped.

The runbook opens with a "State after scaffold" block. Two of its assertions are
false:

1. **"(linger enabled)" is false.** `ao-ledger` is absent from
   `loginctl list-users`, and `/run/user/994` does not exist.
2. **"systemd user unit installed: `ao-ledger-core.service` (not started)" is
   false, and self-refuting.** No unit file exists in the user or system unit
   search path, nor on disk under `/etc/systemd`, `/usr/lib/systemd` or
   `~/.config/systemd`. The runbook's own step 5 says
   `systemctl --user enable --now ao-ledger-core.service` — it instructs you to
   enable a unit it simultaneously claims is already installed. The only
   `ao-ledger` files in `quadlet/` are two `.network` files.

Measured consequence: **the runbook's step 5 cannot succeed even after the
account name is corrected.** `id -u alwayson-ledger` exits 1 with empty stdout,
so `XDG_RUNTIME_DIR=/run/user/$(id -u alwayson-ledger)` expands to `/run/user/`
with no uid. Correcting only the name still fails, because `/run/user/994` does
not exist without linger, and without linger there is no `systemd --user` bus for
`ao-ledger` to connect to.

To unblock LEDGER-07 beyond the key ceremony the operator needs to enable linger
for `ao-ledger` and author the `ao-ledger-core.service` unit. **I did neither.**
Enabling linger creates a persistent background session that survives logout,
which is an access-control change to a service identity, and
`docs/runbooks/` is not my file. Recorded in §11.10 as blocker 4.

## What I got wrong

In this pass I started by grepping the runbook for the token I already knew was
wrong (`alwayson-ledger`), reproduced the prior finding, and nearly concluded
nothing new was there. Reading the runbook's state block field by field instead
is what surfaced both new assertions. A document that asserts completed state
has to be verified field by field — searching it for the error you already know
about cannot find the errors you do not.
---

## Fifth pass, 2026-10-05 — still open, and one blocker is now demonstrable

Not re-measured; four prior passes reproduced identically.

The new material this pass is §11.12, and it is **not** a credential blocker, so it can
be worked without operator approval and without touching `cordadb`. Validating against
the real manifest schema shows the ledger format has **no representation of an accounting
posting** and **no representation of a correction**:

```text
--- 11.3.1 posting leg (DR CASH_EU 10000 EUR): REJECTED
     Additional properties are not allowed ('account_code', 'amount',
     'correlation_id', 'currency', 'side' were unexpected)

--- 11.3.1 reversing transaction (object_type=reversal): REJECTED
     'reversal' is not one of ['sales_receipt', 'telemetry_batch', 'map_product',
      'vehicle_simulation', 'fabrication_simulation']
```

A node built on today's manifest could not record a posting at all. So the node build
depends on a format change that has not been made, in a file that is **not mine**
(`config/ledger/manifest-schema.json`). That should be sequenced *before* the operator
ceremony, not after, or the ceremony will be spent building a node onto a format that
cannot carry the ledger's own accounting model.

**Stays open.** Operator-only; no key material generated, exported or activated.
