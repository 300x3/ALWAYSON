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
**Re-verified a third time, 2026-10-04, by execution not by reading.** All four
findings reproduced with the same commands and exit codes:

```text
$ bash /ALWAYSON/scripts/ledger/build-manifest.sh map_product TOTALLY_MADE_UP_DOMAIN /tmp/p.txt ref://x | jq -r .origin_domain
TOTALLY_MADE_UP_DOMAIN
EXIT=0

$ bash /ALWAYSON/scripts/ledger/build-manifest.sh not_a_type ao-mapping /tmp/p.txt ref://x
ERROR: bad object_type
EXIT=11                                  # contrast: object_type IS validated

$ bash /ALWAYSON/scripts/ledger/sign-manifest.sh /tmp/p.json wallet:ao-sales
ERROR: manifest or key missing (keys live in KDE Wallet ao-sim-*; file path accepted for migration/testing)
EXIT=10                                 # misleading: the wallet key is unimplemented

$ jq -r '{producer_key_id, authorization_policy_id, sig_len:(.signature|length)}' \
    /ALWAYSON/artifacts/pending-ledger-submissions/20260824/manifest.json
{ "producer_key_id": "test", "authorization_policy_id": "", "sig_len": 96 }
```

The `not_a_type` / `EXIT=11` case is new evidence not in the original report: it
proves the asymmetry is real rather than an omission of validation generally —
`object_type` is checked against a closed list and rejected, while
`origin_domain` passes through untouched. Test files were written to `/tmp` and
removed; `pending-ledger-submissions/` contains only the pre-existing
`20260824` directory, and nothing was signed, staged, or transmitted.

Still open. Items 1–4 above all require either credential work or script
changes outside my file ownership, and item 1 is operator-only.

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
---

## Third pass, 2026-10-04 — producer-key coverage gap

**Stays open**, and is now blocked for a reason §19 does not record. The findings
above still hold, but running the scripts surfaced a **producer-key model defect**
that makes the §11.2 acceptance criteria unachievable as written, independent of
the missing gateway.

Added **§11.9 "Producer-Key Coverage Gap in the Ingest Path"** recording four
findings:

1. `sign-manifest.sh` supports wallet keys for only `ao-sim-vehicle` and
   `ao-sim-fabrication`. **Sales, Payment, Field and Mapping have no wallet-backed
   signing path** — yet Sales produces the `sales_receipt` type that §11.2.2's
   three evidence gates exist to protect.
2. An unsupported `wallet:` argument falls through to a file-path test and reports
   "manifest or key missing" (exit `10`), which is misleading and
   indistinguishable from a genuinely absent file.
3. `origin_domain` is passed straight into `jq` with no validation, unlike
   `object_type`. An invented domain is accepted and stamped into the manifest,
   and that field drives the §11.1 authority decision.
4. The pre-existing 20260824 staged manifest carries `producer_key_id: "test"`
   and an empty `authorization_policy_id` — neither identifies a registered
   producer. Confirmed again that staging performs no cryptographic check.

So the §11.2 requirement to verify against the exporter's **registered** key cannot
be met while `producer_key_id` is self-asserted and four domains have no
registered key at all. This is a **credential task — operator only.**

```text
  $ grep -oP 'wallet:ao-[a-z-]+' /ALWAYSON/scripts/ledger/sign-manifest.sh | sort -u
  wallet:ao-sim-fabrication
  wallet:ao-sim-vehicle

  $ bash /ALWAYSON/scripts/ledger/sign-manifest.sh manifest.json wallet:ao-sales
  ERROR: manifest or key missing (keys live in KDE Wallet ao-sim-*; ...)
  EXIT=10

  $ bash /ALWAYSON/scripts/ledger/build-manifest.sh map_product TOTALLY_MADE_UP_DOMAIN p.txt ref://x | jq -r .origin_domain
  "TOTALLY_MADE_UP_DOMAIN"
  EXIT=0

  $ jq -r '{producer_key_id, authorization_policy_id, sig_len:(.signature|length)}' \
      /ALWAYSON/artifacts/pending-ledger-submissions/20260824/manifest.json
  { "producer_key_id": "test", "authorization_policy_id": "", "sig_len": 96 }
```

## What I got wrong (third pass)

Three mistakes, all from trusting shape instead of behaviour:

1. **I concluded `manifest.json` did not exist because `build-manifest.sh`
   "failed".** It had not failed — it writes JSON to **stdout**, and I had never
   redirected it. My first three test runs were invalid and I nearly recorded a
   "defect" that was my own broken harness. Re-running with `> manifest.json`
   gave clean results.
2. **I ran two dependent commands in parallel.** The `jq` in the second command
   raced ahead of the `build-manifest.sh` in the first, so the file was not there
   yet and I again saw a phantom "missing file". Sequential execution was the fix.
3. **I read `submit-ledger-event.sh`'s exit `2` as "unsigned rejected".** Exit `2`
   was the usage error for a missing file. The real unsigned exit is `20`. Reading
   the script was not enough to get the codes right — only executing it was.

**Trap for the next session:** `data/corda-install/` **does not exist in the
worktree** — `.gitignore:2` ignores `data/`. Any checksum claim must be run
against `/ALWAYSON/data/corda-install/`. All three Corda 5.2.2 artifacts verify
`OK` there. Running the checksum in the worktree returns "No such file or
directory", which reads like a missing artifact but is not.

## Housekeeping

I created one test manifest to prove finding 4 and **removed it**. The 20260824
manifest is pre-existing project data and was not touched. No key was generated,
no signature was produced by a real key, nothing was transmitted, and no external
system was modified.

## Note for the compiler

No status change. Recommend §19's LEDGER-03 criteria note the producer-key gap,
since "authorization, idempotency, replay defence, and audit" is currently
unreachable for four of the six authoritative domains.