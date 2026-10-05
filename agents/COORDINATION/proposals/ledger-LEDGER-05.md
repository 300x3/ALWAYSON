---
item: LEDGER-05
action: close
evidence: |
  # Independently re-run by the 2026-10-04 LEDGER session, not carried forward.
  $ bash /ALWAYSON/scripts/validation/check-ledger-ingest.sh
  PENDING: ledger-ingest gateway not deployed yet (Section 2.8 step 3 awaits Corda version approval)
  EXIT=3

  $ podman ps -a --format '{{.Names}}' | grep -c -E 'ledger|archive|egress'
  0

  $ systemctl --user show ao-ledger-core.service \
      -p LoadState -p ActiveState -p SubState -p FragmentPath
  LoadState=not-found
  ActiveState=inactive
  SubState=dead
  FragmentPath=

  # Correction to the 2026-10-03 evidence for this item: see "What I got wrong".
  $ systemctl --user is-active ao-ledger-core.service
  inactive                       # exit 4  -- MISLEADING, see prose
section: 11-ledger-provenance-archive-and-ipfs
---
**Third independent run, 2026-10-04.** Reproduced again:

```text
$ bash /ALWAYSON/scripts/validation/check-ledger-ingest.sh
PENDING: ledger-ingest gateway not deployed yet (Section 2.8 step 3 awaits Corda version approval)
EXIT=3

$ systemctl --user show ao-ledger-core.service -p LoadState -p FragmentPath
LoadState=not-found
FragmentPath=
```

The `LoadState` lesson in "What I got wrong" below cost me a re-check this
session: I reached for `is-active` first, got `inactive` again, and had to
re-run with `LoadState` to get an answer that means anything. Three sessions have
now hit this same trap. **Closure still holds** — the script resolves, it runs
unprivileged, and `EXIT=3` is a defined PENDING state.

`check-ledger-ingest.sh` is resolved and deterministic, and it runs
unprivileged — the acceptance criteria allowed either the script being resolved
**or** a pending privileged command, and the script route is the one that
actually holds. Exit `3` is a defined PENDING state, distinct from healthy (`0`)
and from failure (`44`).

Added §11.2.4 "Ledger-Ingest Probe Status" recording this with the output above.
The diagnosis result is negative and worth stating plainly: **there is no
socket-bridge fault to diagnose.** The probe is blocked solely because the
`ledger-ingest` gateway does not exist yet, which is downstream of the Corda 5
node build and the operator key ceremony.

I also recorded that `submit-ledger-event.sh` stages rather than loses data, so
nothing is at risk while the gateway is absent.

## What I got wrong

I initially tried to write this section assuming there would be a real bridge
fault to diagnose — the item name implies one. There isn't. The honest output is
"the probe works, the service does not exist yet." I also nearly claimed the
client-side behaviour was verified after only *reading* the scripts; I then ran
them, which is what surfaced the signature weakness recorded in §11.2.5.

## Second pass, 2026-10-04 — the `is-active` trap

Re-verifying this item, `systemctl --user is-active ao-ledger-core.service`
printed **`inactive`**, which reads like "the unit exists and is merely stopped".
That is wrong: the unit **does not exist at all**. `is-active` returns exit 4 for
both "not found" and "found but inactive", so the word alone is not evidence.

The disambiguating command is `systemctl --user show <unit> -p LoadState`, which
printed `LoadState=not-found` and an empty `FragmentPath=`. **Use `LoadState`, not
`is-active`, whenever the question is "does this unit exist?"** An agent that
trusts the `inactive` string may conclude the ledger core is installed-but-stopped
and try to start it, instead of concluding it was never built.

This **confirms** rather than contradicts the 2026-10-03 LEDGER-07 proposal,
which reported the unit "could not be found" — that claim was correct.

## Note for the compiler

No §19 wording change needed beyond status; the acceptance criteria stand as
written and are met.