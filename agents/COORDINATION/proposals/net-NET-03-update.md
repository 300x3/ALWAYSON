---
item: NET-03
action: update
evidence: |
  RE-VERIFIED 2026-10-05. The registry-authority direction is still correct:

  $ bash scripts/validation/check-network-isolation.sh
  OK: all domain networks present; isolation domains internal-only;
      3 egress networks non-internal by decision; registry matches host (14 = 11 + 3)
  EXIT=0

  $ diff /tmp/registry-before.yaml config/platform/network-cidrs.yaml
  (registry unchanged by the script — confirmed read-only)

  $ bash scripts/validation/check-network-isolation.sh --emit-table
  | `ao-payment` | 10.89.1.0/24 | true |
  ... 14 rows ...
  <!-- registry: 14 ao-* networks, 11 Internal=true, 3 Internal=false -->

  The split-authority issue the net-NET-03-followup flagged is still live:
  $ sed -n '580,586p' config/platform/topology-model.yaml
    ao-egress-community:
      purpose: "Approved Mastodon/community federation egress adapter"
      adapter: true
      includes: [mastodon-web, mastodon-sidekiq]
      status: implemented
  $ sed -n '100,104p' config/platform/gui-boundary-matrix.yaml
    access_boundary: "...external publication only through ao-egress-community when enabled."
  $ sed -n '95,100p' docs/runbooks/mastodon.md
    delivery path requires the scoped ao-egress-community Sidekiq route,
    WORK 000060 outstanding
section: 05-network-domains-and-controlled-external-access
---
**NET-03 was closed for CIDR/Internal flag authority; the split for
attachment/purpose remains and is not mine to resolve.**

The net-NET-03.md close was correct for its stated scope: `config/platform/network-cidrs.yaml`
is authoritative for CIDRs and Internal flags, and `check-network-isolation.sh`
now reads the registry and asserts the host against it instead of regenerating
it. That half is re-verified above and is sound.

The net-NET-03-followup.md correctly flagged that the same file is NOT
authoritative for what is attached to a network, for component purpose, or for
adapter status. Those facts live in at least four other files, and three of them
still carry the retired `ao-egress-community` as `status: implemented`. The
topology model feeds the Grafana dashboard, the GUI boundary matrix routes
external publication through the retired network, and the Mastodon runbook
tells an operator to use a route that does not exist.

I did not touch those files — they belong to other sessions. The §19 entry marks
NET-03 as "Implemented" on the CIDR-authority fix, which is the part I could
close. The remaining split-authority issue is a cross-cutting decision about
which file owns attachment, purpose, and adapter status — I am flagging it, not
resolving it.
