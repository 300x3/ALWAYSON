---
item: NET-03
action: update
evidence: |
  FOLLOW-UP to net-NET-03.md, which I have not modified. NET-03 REMAINS OPEN on
  the same point as before; nothing I found this session moves it.

  Re-verified that the registry is still the single authority and that the
  validation script still asserts rather than regenerates it:
  $ bash scripts/validation/check-network-isolation.sh
  OK: all domain networks present; isolation domains internal-only;
      3 egress networks non-internal by decision; registry matches host (14 = 11 + 3)
  EXIT=0

  The blocker is unchanged. NET-03 asks for ONE authoritative network
  inventory. config/platform/network-cidrs.yaml is authoritative for CIDRs and
  Internal flags. It is NOT authoritative for what is attached to a network,
  for component purpose, or for adapter status - those live in at least four
  other files, and they disagree with each other and with the host. Verified:

  - config/platform/topology-model.yaml:582 still declares ao-egress-community
    with status: implemented, for a network retired 2026-09-30 and which does
    not exist.
    $ sed -n '582,586p' config/platform/topology-model.yaml
      ao-egress-community:
        purpose: "Approved Mastodon/community federation egress adapter"
        adapter: true
        includes: [mastodon-web, mastodon-sidekiq]
        status: implemented
  - config/platform/monitoring/grafana/provisioning/dashboards/json/ao-topology.json
    lines 1447-1448 and 2157-2159 draw that same phantom adapter network, so
    the operator dashboard shows a network that is not there.
  - config/platform/gui-boundary-matrix.yaml:102 still routes external
    publication through it.
  - docs/runbooks/mastodon.md:97 still requires the scoped route.

  Reconciling those means editing four files owned by other sessions, and the
  ao-topology.json one is generated from topology-model.yaml by
  scripts/operations/generate-topology.py - so the fix is in the model, not the
  JSON, and the model is not mine.
section: 05-network-domains-and-controlled-external-access
---
**NET-03 stays open, and the reason is unchanged: the authority is split across
files I do not own, and they disagree with each other and with the host.**

`config/platform/network-cidrs.yaml` is authoritative for CIDRs and `Internal`
flags, and the validation script asserts the host against it rather than
regenerating it. That half is sound and re-verified this session.

It is not authoritative for attachment, component purpose, or adapter status.
Those live in at least four other files, and the `ao-egress-community` retirement
was applied to some of them and not others:

- `config/platform/topology-model.yaml:582` still declares it `status:
  implemented`, for a network retired 2026-09-30 that does not exist on this
  host.
- `config/platform/monitoring/grafana/provisioning/dashboards/json/ao-topology.json`
  draws that phantom network, so the Grafana topology dashboard shows an adapter
  that is not running. That JSON is **generated** by
  `scripts/operations/generate-topology.py` from the topology model, so editing
  the JSON would be overwritten on the next run; the fix belongs in the model,
  which is not mine.
- `config/platform/gui-boundary-matrix.yaml:102` still routes external
  publication through the retired network.
- `docs/runbooks/mastodon.md:97` still requires the scoped route.

All four belong to other sessions and I have not touched any of them. Closing
NET-03 properly means naming which file is the authority for each fact and
deleting the rest, which is a cross-cutting decision I should not make alone.