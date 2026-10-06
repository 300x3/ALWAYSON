# NET Session — 2026-10-05 — Re-verification of NET-01 through NET-04

## Commands run and results

### NET-01: Controlled ingress/egress adapters

ao-build-update: is-enabled=generated, is-active=inactive, Internal=false at 10.89.13.0/24, 0 containers
Allowlist: 3 test cases verified (DENIED/UNPINNED/ALLOWED-PINNED, exit 4/4/0)
ao-ingress-payment: is-enabled=generated, is-active=active, running python@sha256:79e7a9b9, on ao-payment (Internal=true), 127.0.0.1:8899 only
ao-payment-relay: is-enabled=enabled, is-active=active
ao-egress-archive: NOT FOUND (no quadlet, no container, no network)

### NET-02: CIDR reconciliation
check-network-isolation.sh: EXIT=0, 14 networks, 11 Internal=true, 3 Internal=false
Attachment counts re-measured from host — all match §5.1.1
Stale references still present in topology-model.yaml:582, gui-boundary-matrix.yaml:102, mastodon.md:97

### NET-03: Single authoritative inventory
Script asserts (does not regenerate) — confirmed
Split authority for attachment/purpose remains in topology-model.yaml, grafana JSON, gui-boundary-matrix.yaml, mastodon.md

### NET-04: Prohibited paths list
Byte-exact transcription verified by Python diff (11 lines in, 11 out, 0 diff)
Both superseded-entry marks verified accurate

## Files changed
- agents/COORDINATION/05-network-domains-and-controlled-external-access/section.md (§5.2.2, §5.2.3, matrix row)
- agents/COORDINATION/04-security-isolation-and-data-policy/section.md (§4.3.3 verification note)
- README.md (recompiled from 21 sections)
- 4 proposal files in agents/COORDINATION/proposals/

## NOT touched
- TOPOLOGY/* files (other sessions)
- config/platform/topology-model.yaml (other session — stale ao-egress-community)
- config/platform/gui-boundary-matrix.yaml (other session)
- docs/runbooks/mastodon.md (other session)
- No firewall policy, no secrets created, no tunnels enabled
