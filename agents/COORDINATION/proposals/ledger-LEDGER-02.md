---
item: LEDGER-02
action: update
evidence: |
  $ psql -tAc 'select 1'
  FATAL:  role "scottw" does not exist

  $ sudo -n -u postgres psql -tAc "\du corda"
  sudo: interactive authentication is required

  $ getent passwd ao-ledger
  ao-ledger:x:994:974:ALWAYS ON ledger core service:/home/alwayson-ledger:/usr/sbin/nologin

  $ cd /ALWAYSON/data/corda-install && sha256sum -c corda-combined-worker-5.2.2.0.jar.sha256sum
  corda-combined-worker-5.2.2.0.jar: OK
section: 11-ledger-provenance-archive-and-ipfs
---
**Stays open. Stopped — credential change is a hard stop condition.**

The acceptance criteria require the `cordadb` owner role to have a working
password so that `corda-cli.sh preinstall check-postgres` passes. I did **not**
run `ALTER ROLE corda PASSWORD ...`, did not read the existing credential, and
did not broaden database privileges to get past the error (README §4.1 rules 13
and 14).

## What is verified

- The role password state is **unverifiable** from the agent account. `psql`
  fails at authentication (`role "scottw" does not exist`) and `sudo -u postgres`
  requires interactive authentication. Neither says anything about whether the
  `corda` role has a working password — so §19's claim is carried forward, not
  confirmed.
- The Corda 5.2.2 artifacts are staged and checksum-clean.
- The service account is `ao-ledger`, not `alwayson-ledger` (see the
  LEDGER-01 proposal for the runbook bug and the correction recorded in §11.7).

## What the operator needs to do

```bash
sudo -u postgres psql -tAc "SELECT rolname, rolcanlogin FROM pg_roles WHERE rolname='corda';"   # no password shown
sudo -u postgres psql -c "ALTER ROLE corda PASSWORD '<new>';"
```

The new password must then reach the `ao-ledger` account through KWallet, **not**
through this repository, a script, or a log. Per the KWallet secret-authority
session, agent sessions are **not** authorised to write ledger secrets at all.

## Ordering

This is prerequisite to LEDGER-07's node build, and both sit behind LEDGER-01's
key ceremony. Nothing here can be advanced by an agent without operator
approval.