---
item: LEDGER-03
action: update
evidence: |
  $ bash /ALWAYSON/scripts/ledger/build-manifest.sh sales_receipt sales <file> testref
  ERROR: sales_receipt requires issued transaction_id
  EXIT=12

  $ bash /ALWAYSON/scripts/ledger/build-manifest.sh telemetry_batch field <file> testref
  EXIT=0; content_size_bytes=23, signature=""

  $ bash /ALWAYSON/scripts/ledger/submit-ledger-event.sh <unsigned-manifest>
  ERROR: manifest is unsigned (run sign-manifest.sh first)
  EXIT=20

  $ bash /ALWAYSON/scripts/ledger/submit-ledger-event.sh <signed-manifest>
  PENDING: gateway not deployed; manifest staged for later submission
  EXIT=3

  $ podman ps -a --format '{{.Names}}' | grep -c 'ledger-ingest'
  0
section: 11-ledger-provenance-archive-and-ipfs
---
**Stays open.** Added §11.2.5 with an 8-row table mapping every requirement to
its enforcer and its current state, so the gap is explicit rather than implied.

Proven by execution (synthetic content only; test artifact deleted afterwards):
the schema conditional rejects a `sales_receipt` without an issued
`transaction_id` (exit 12), and an unsigned manifest is refused (exit 20).

## The finding that matters most

`submit-ledger-event.sh` validates only that `.signature` is a **non-empty
string**. I proved a deliberately bogus value is accepted and staged:

```text
$ jq '.signature="ed25519:SYNTHETIC_NOT_A_REAL_SIGNATURE"' m.json > m3.json
$ bash scripts/ledger/submit-ledger-event.sh m3.json
PENDING: gateway not deployed; manifest staged for later submission   # EXIT=3
```

This is **not a live vulnerability today** — the manifest goes to a local staging
directory and is never transmitted, because no gateway exists to receive it. It
becomes one the moment server-side signature verification is skipped.

Consequently the gateway **must** verify signatures cryptographically and must
**not** trust `producer_key_id` or the embedded `signature` as supplied. The
`producer_key_id` and `authorization_policy_id` fields `build-manifest.sh` emits
are empty placeholders and must be filled from the authenticated mTLS identity,
never from the submitted body. Anything replayed out of
`artifacts/pending-ledger-submissions/` after the gateway comes up is untrusted
input.

Only the client half (build → sign → stage) is demonstrable. Acceptance,
authorization, idempotency and replay defence are **unproven** because there is
no acceptor to test them against.