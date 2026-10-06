---
item: NET-02
action: close
evidence: |
  The registry is correct and agrees with the live host, network for network.
  $ AO_REGISTRY=$PWD/config/platform/network-cidrs.yaml bash scripts/validation/check-network-isolation.sh
  OK: all domain networks present; isolation domains internal-only; 3 egress networks non-internal by decision; registry matches host (14 = 11 + 3)
  EXIT=0

  NET-02's remaining claim — that ao-egress-community "is live on 10.89.11.0/24"
  while the name is recorded as folded into ao-sales — is FALSE as of 2026-10-03.
  The network does not exist on this host:
  $ podman network ls --format '{{.Name}}' | grep '^ao-'   # 14 names, no ao-egress-community
  $ podman network inspect ao-egress-community
  Error: network ao-egress-community: unable to find network with name or ID
  ao-egress-community: network not found

  10.89.11.0/24 is allocated to nothing. Full live CIDR map:
  $ for n in $(podman network ls --format '{{.Name}}' | grep '^ao-'); do
      podman network inspect "$n" --format '{{.Name}} internal={{.Internal}} {{range .Subnets}}{{.Subnet}}{{end}}'; done | sort
  ao-admin internal=true 10.89.9.0/24
  ao-build-update internal=false 10.89.13.0/24
  ao-data internal=true 10.89.8.0/24
  ao-fabrication internal=true 10.89.12.0/24
  ao-field internal=true 10.89.2.0/24
  ao-html-window internal=true 10.89.14.0/24
  ao-ledger-core internal=true 10.89.7.0/24
  ao-ledger-ingest internal=true 10.89.6.0/24
  ao-mapping internal=true 10.89.3.0/24
  ao-payment internal=true 10.89.1.0/24
  ao-reporting-egress internal=false 10.89.10.0/24
  ao-sales internal=false 10.89.0.0/24
  ao-sim-fabrication internal=true 10.89.5.0/24
  ao-sim-vehicle internal=true 10.89.4.0/24
  # 1..14 contiguous except 11; internal=true x11, internal=false x3

  The reconciliation §19 asked for is already recorded correctly in
  config/mastodon/instance-policy.yaml:
  "ao-sales is Internal=false, expressly so Sidekiq can deliver ActivityPub over
   outbound HTTPS/443. This replaces the retired ao-egress-community network."
section: 05-network-domains-and-controlled-external-access
---
The CIDR reconciliation §19 left open is closed as a *measurement*, not an edit.
Every registered CIDR matches the running host, and `check-network-isolation.sh`
now asserts it on every run instead of overwriting the registry with whatever
podman happened to report (see net-NET-03.md).

The `ao-egress-community` name/CIDR reconciliation that §19 called "a rename
decision, not a registry edit" turns out not to need a decision at all, because
the premise is wrong: **the network is not live.** §19 says it "is live on
10.89.11.0/24". `podman network inspect` says it does not exist. `10.89.11.0/24`
is a reserved hole, deliberately unallocated. The retirement is already recorded
in `config/mastodon/instance-policy.yaml` and in
`scripts/mastodon/federate-local.sh`. So there is no rename to approve: the
retirement already happened, was already documented, and only §19's description of
it was out of date.

I corrected §5.1 (which said the range was "folded into ao-sales") and §5.1.1 to
state the accurate position: reserved, unallocated, name retired, community
egress carried inside `ao-sales`. Both now carry the `podman network inspect`
evidence.

**Two staleness findings belong to other groups — reported, not edited.**

1. `config/platform/topology-model.yaml:582` still declares `ao-egress-community`
   with `status: implemented` and `includes: [mastodon-web, mastodon-sidekiq]`.
   That is a **live topology model asserting a network that does not exist**, and
   `generate-topology.py` feeds the Grafana dashboard from it, so the dashboard
   will draw a phantom adapter network. This is the "Grafana topology dashboard"
   part of NET-02's remaining list. It is a config file outside my ownership and
   the fix belongs to whoever owns the topology model — flagging, not touching.
2. `config/platform/gui-boundary-matrix.yaml:102` says external publication
   happens "only through ao-egress-community **when enabled**", implying a
   disabled adapter pending enablement. In fact it is retired, not pending.
   Same owner question.

Also stale, and not mine: `docs/runbooks/mastodon.md:97` describes the delivery
path as requiring "the scoped ao-egress-community Sidekiq route, WORK 000060
outstanding", while `instance-policy.yaml` records WORK 000060 as done
(2026-09-30) and `ao-sales` as the live path. An operator following that runbook
would look for a route that does not exist.

**What I got wrong.** My first instinct on reading NET-02 was to treat
"10.89.11 is live" as a fact in the brief and go looking for a registry entry to
fix. The brief was describing a past state. Had I trusted it, I would have
either added a bogus `ao-egress-community` line to the registry or escalated a
phantom "rename decision" to the operator. Lesson: a stale line in §19 is a
hypothesis, not a specification — measure before reconciling.

**Not done, deliberately.** I did not edit the topology model, the GUI boundary
matrix, or the Mastodon runbook. All three are outside my two section files.
