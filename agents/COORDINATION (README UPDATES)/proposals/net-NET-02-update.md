---
item: NET-02
action: update
evidence: |
  RE-VERIFIED 2026-10-05.

  $ bash scripts/validation/check-network-isolation.sh
  OK: all domain networks present; isolation domains internal-only;
      3 egress networks non-internal by decision; registry matches host (14 = 11 + 3)
  EXIT=0

  $ bash scripts/validation/check-network-isolation.sh --emit-table
  | `ao-payment` | 10.89.1.0/24 | true |
  ... 14 rows ...
  <!-- registry: 14 ao-* networks, 11 Internal=true, 3 Internal=false -->

  Attachment counts re-measured from the host (matching the previous session's
  net-NET-02-followup.md correction):
  $ for n in ao-sales ao-payment ao-field ao-mapping ao-sim-vehicle ao-sim-fabrication ao-ledger-ingest ao-ledger-core ao-data ao-admin ao-reporting-egress ao-fabrication ao-build-update ao-html-window; do
        printf '%-22s %s\n' "$n" \
          "$(podman network inspect "$n" --format '{{range .Containers}}{{.Name}} {{end}}' | wc -w)";
    done
  ao-sales               6
  ao-payment             1
  ao-field               0
  ao-mapping             5
  ao-sim-vehicle         0
  ao-sim-fabrication     2
  ao-ledger-ingest       0
  ao-ledger-core         0
  ao-data                0
  ao-admin               4
  ao-reporting-egress    2
  ao-fabrication         1
  ao-build-update        0
  ao-html-window         1

  Stale references still present in other sessions' files (reported, not touched):
  $ sed -n '580,586p' config/platform/topology-model.yaml  # still declares ao-egress-community status: implemented
  $ sed -n '100,104p' config/platform/gui-boundary-matrix.yaml  # still routes through ao-egress-community when enabled
  $ sed -n '95,100p' docs/runbooks/mastodon.md  # still requires scoped ao-egress-community route, WORK 000060 outstanding
  $ grep -n 'ao-egress-community\|ao-sales' scripts/mastodon/federate-local.sh  # correctly notes retirement
section: 05-network-domains-and-controlled-external-access
---
**NET-02 remains closed; re-verification confirms the registry is correct and complete.**

This session independently re-ran every command from net-NET-02.md and
net-NET-02-followup.md. The registry at `config/platform/network-cidrs.yaml`
matches the live host for all 14 networks (11 Internal=true, 3 Internal=false).
The script reads the registry and asserts against the host — it does not
regenerate the file. The `ao-egress-community` / `10.89.11.0/24` claim was
confirmed false: the network does not exist, the CIDR is unallocated, and the
retirement is correctly recorded in `config/mastodon/instance-policy.yaml` and
`scripts/mastodon/federate-local.sh`.

The attachment counts in §5.1.1 match the live host for all 14 rows. The two
rows the previous session corrected (ao-sim-fabrication, ao-html-window) are
still correct.

The three stale references in files owned by other sessions are unchanged:
`config/platform/topology-model.yaml:582`,
`config/platform/gui-boundary-matrix.yaml:102`, and
`docs/runbooks/mastodon.md:97` all still reference the retired `ao-egress-community`.
These were reported by the previous session and are not mine to edit.

No change to section 05 was needed for NET-02 — the §5.1.1 table and the
check-network-isolation.sh script are correct as they stand.
