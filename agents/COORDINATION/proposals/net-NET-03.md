---
item: NET-03
action: close
evidence: |
  $ AO_REGISTRY=$PWD/config/platform/network-cidrs.yaml bash scripts/validation/check-network-isolation.sh
  OK: ao-payment (10.89.1.0/24) Internal=true
  OK: ao-field (10.89.2.0/24) Internal=true
  OK: ao-mapping (10.89.3.0/24) Internal=true
  OK: ao-sim-vehicle (10.89.4.0/24) Internal=true
  OK: ao-sim-fabrication (10.89.5.0/24) Internal=true
  OK: ao-ledger-ingest (10.89.6.0/24) Internal=true
  OK: ao-ledger-core (10.89.7.0/24) Internal=true
  OK: ao-data (10.89.8.0/24) Internal=true
  OK: ao-admin (10.89.9.0/24) Internal=true
  OK: ao-fabrication (10.89.12.0/24) Internal=true
  OK: ao-html-window (10.89.14.0/24) Internal=true
  OK: ao-reporting-egress (10.89.10.0/24) Internal=false by decision
  OK: ao-sales (10.89.0.0/24) Internal=false by decision
  OK: ao-build-update (10.89.13.0/24) Internal=false by decision
  OK: all domain networks present; isolation domains internal-only; 3 egress networks non-internal by decision; registry matches host (14 = 11 + 3)
  EXIT=0

  The registry is no longer written by the script:
  $ diff /tmp/registry-before.yaml config/platform/network-cidrs.yaml
  IDENTICAL - script did not rewrite the registry

  NEGATIVE TEST 1 - flip an Internal flag in the registry:
  $ sed 's/^ao-admin internal=true/ao-admin internal=false/' ... > /tmp/bad1.yaml
  $ AO_REGISTRY=/tmp/bad1.yaml bash scripts/validation/check-network-isolation.sh
  ERROR: ao-admin registry says internal=false but podman reports internal=true
  ERROR: registry lists 10 Internal=true, expected 11
  ERROR: registry lists 4 Internal=false, expected 3
  FAILED: 3 isolation assertion(s)
  EXIT=42

  NEGATIVE TEST 2 - wrong CIDR in the registry (this is the exact case the old
  script could not see; it compared only the internal=true/false flag):
  $ AO_REGISTRY=/tmp/bad2.yaml bash scripts/validation/check-network-isolation.sh
  ERROR: ao-field registry says 10.89.99.0/24 but podman reports: ao-field internal=true 10.89.2.0/24
  FAILED: 1 isolation assertion(s)

  NEGATIVE TEST 3 - a live network absent from the registry (the old script was
  structurally blind to this; it only walked its own hardcoded array):
  $ grep -v '^ao-data ' config/platform/network-cidrs.yaml > /tmp/bad3.yaml
  $ AO_REGISTRY=/tmp/bad3.yaml bash scripts/validation/check-network-isolation.sh
  ERROR: live podman network not in the registry: ao-data (10.89.8.0/24)
  ERROR: registry lists 13 ao-* networks, expected 14
  ERROR: registry lists 10 Internal=true, expected 11
  FAILED: 3 isolation assertion(s)

  Inventory rows now generated from the registry, not typed:
  $ bash scripts/validation/check-network-isolation.sh --emit-table
  | `ao-payment` | 10.89.1.0/24 | true |
  ... (14 rows) ...
  <!-- registry: 14 ao-* networks, 11 Internal=true, 3 Internal=false -->
section: 05-network-domains-and-controlled-external-access
---
**The real defect was the direction of authority, and it is fixed.**
`config/platform/network-cidrs.yaml` was documented as the single source of
truth, but `check-network-isolation.sh` overwrote it on every run from a
hardcoded `expected=(...)` array of eleven names plus an `egress=(...)` array of
three. The file named as the authority was derived from the script, so the
script was the real source of truth and the file was a generated artefact wearing
an authority label. Adding a network to podman without also editing that array
would have silently deleted the network from the authority on the next run — the
exact failure mode §19 described as "the named source of truth is not
authoritative."

The script now reads the registry and asserts the host against it, in both
directions. It never writes the file. It asserts the CIDR as well as the
`Internal` flag, it detects any live `ao-*` network missing from the registry,
and it fails if the total (14), internal count (11) or egress count (3) changes
without a deliberate count decision. Negative tests 1-3 above prove each new
assertion actually bites rather than printing and exiting zero.

**The three disagreeing counts are already one count, and it was already
fourteen.** §19 said "§2.2 says twelve, §13.3 says twelve, this document says
thirteen." Measured 2026-10-03, that is stale in §19, not in §2.2 or §13.3:
`02-platform-baseline/section.md` says "Fourteen" and enumerates eleven
internal plus three egress; `13-podman-runtime-and-quadlet-policy/section.md`
says "the 14 ao-*.network definitions"; the live host has exactly 14 `ao-*`
networks with 11 `Internal=true` and 3 `Internal=false`. So no count edit was
needed in §2.2 or §13.3, and I did not edit those files — they are not mine.
§5.1.1 is now a generated inventory with the count asserted by the script rather
than stated in prose, which is what makes it stay true.

`ao-html-window` (10.89.14) and `ao-build-update` (10.89.13) were already rows in
§5.1.1 as it stood — §19's claim that they appear "in no table" was also stale.
They are still rows, and the table's first column was empty on thirteen of
fourteen rows (a rendering bug from the generator); that is fixed.

**What I got wrong.** I first wrote the new script through the editor with
`[[ ... ]] && x=y` compound conditions and a comment-strip line that would have
tripped `set -e` on the first false test, terminating the script silently mid-run
with exit 0. I caught it by reading it back rather than running it, and rewrote it
with explicit `if` blocks. Reason: I optimised for a short diff against the old
script instead of for a script that survives `set -Eeuo pipefail`. Lesson: any
`&&`-chained statement as the *last* command of a loop body under `set -e` is a
silent-truncation bug.

**Assumption stated.** The script keeps its absolute `/ALWAYSON/scripts/lib/common.sh`
source line, so `ao_audit` still writes to the live audit log when run from a
checkout. I added an `AO_REGISTRY` override purely so it can be exercised against
a non-live tree; production calls take the default. I did not change
`check-deployment-conformance.sh`, which independently reads the registry — it is
not my file, and it remains correct because the file format is unchanged.
