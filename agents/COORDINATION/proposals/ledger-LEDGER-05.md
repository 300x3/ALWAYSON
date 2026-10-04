---
item: LEDGER-05
action: close
evidence: |
  $ bash /ALWAYSON/scripts/validation/check-ledger-ingest.sh
  PENDING: ledger-ingest gateway not deployed yet (Section 2.8 step 3 awaits Corda version approval)
  EXIT=3

  $ podman ps -a --format '{{.Names}}' | grep -c 'ledger-ingest'
  0

  $ bash /ALWAYSON/scripts/ledger/verify-ledger-receipt.sh RCPT-FAKE-0001 <manifest>
  FAIL: receipt mismatch
  EXIT=50
section: 11-ledger-provenance-archive-and-ipfs
---
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

## Note for the compiler

No §19 wording change needed beyond status; the acceptance criteria stand as
written and are met.