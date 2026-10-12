---
item: NET-02
action: close
evidence: |
  # NET-02 acceptance: "ao-egress-community name/CIDR reconciliation against
  # instance-policy.yaml, the Grafana topology dashboard, and the Mastodon runbook".
  #
  # 1. The registry is the authority, and it does not contain the retired name.
  $ grep -c 'ao-egress-community' config/platform/network-cidrs.yaml
  0
  $ grep -c '10.89.11' config/platform/network-cidrs.yaml
  0
  $ wc -l config/platform/network-cidrs.yaml
  15 config/platform/network-cidrs.yaml   # 14 networks + 1 comment line

  # 2. The host has no network at the retired CIDR, and the retired name is not
  #    a live network. Both directions checked, because a reconciliation that only
  #    reads one side can miss a live-but-unregistered network.
  $ podman network ls --format '{{.Name}} {{range .Subnets}}{{.Subnet}}{{end}}' | grep 10.89.11
  (no output)
  $ podman network inspect ao-egress-community --format '{{.Name}}' 2>&1
  Error: network ao-egress-community: unable to find network with name or ID: network not found

  # 3. instance-policy.yaml is where the rename decision lives.
  $ sed -n '11,16p' config/mastodon/instance-policy.yaml
    public_federation: true            # ON 2026-09-30 (operator decision). ao-sales is Internal=false, expressly so
                                       # Sidekiq can deliver ActivityPub over outbound HTTPS/443. This replaces the
                                       # retired ao-egress-community network. Containment is by network membership:
                                       # no database, Redis or streaming container is attached to an egress network,
                                       # and ao-sales has no attachment or route to any other ao-* domain. See README 15.4 / 18.5.

  # 4. The Grafana topology dashboard still names the retired network — this is
  #    the row that was missing, and it is in §5.1.1 now.
  $ grep -c 'ao-egress-community' config/platform/monitoring/grafana/provisioning/dashboards/json/ao-topology.json
  4

  # 5. The Mastodon runbook still refers to the old route as a remaining note.
  $ grep -n 'ao-egress-community' docs/runbooks/mastodon.md
  97:- Outbound egress only to approved host (`approved_pub_host: 300x3.com`;
  98:  delivery path requires the scoped `ao-egress-community` Sidekiq route,
  99:  WORK 000060 outstanding).

  # 6. The validation script asserts the count of REGISTERED networks. A retired
  #    allocation is not one, so the script correctly does not see it.
  $ bash scripts/validation/check-network-isolation.sh --emit-table 2>&1 | tail -1
  <!-- registry: 14 ao-* networks, 11 Internal=true, 3 Internal=false -->
  $ bash scripts/validation/check-network-isolation.sh >/dev/null 2>&1; echo "EXIT=$?"
  EXIT=0
section: 05-network-domains-and-controlled-external-access
---
**NET-02 is closed, and the reconciliation is now visible rather than implied.**
Its acceptance criterion named three artifacts: `instance-policy.yaml`, the
Grafana topology dashboard, and the Mastodon runbook. All three were checked, and
the gap was that **none of them was in a table** — §5.1.1 listed fourteen networks
and named every CIDR except the one that had been deliberately vacated, so an
operator checking the running host against the document could not see that
`10.89.11.0/24` was intentionally empty.

The retired network is now a row in the §5.1.1 inventory table, marked
**retired**, with its CIDR and the fact that no network exists at it. The row is
marked rather than deleted for the same reason §4.3.1 marks superseded
prohibitions: an operator needs to see that the CIDR was *intentionally* vacated.

**What the reconciliation is and is not.** It is a documentation row, not a
registry edit. `network-cidrs.yaml` still holds fourteen entries and does not
contain the retired name or CIDR — correctly, because the registry is the list of
*live, registered* networks and a retired allocation is not one. `check-network-isolation.sh`
asserts that count and passes. No network was created, removed, re-CIDRed or
re-flagged.

**Two artifacts this section does not own, and why I did not edit them.** The
Grafana dashboard still names `ao-egress-community` four times, and
`docs/runbooks/mastodon.md` §6 still calls the old route a *remaining* note. Both
are stale, both are outside my ownership, and correcting them is a Mastodon-session
decision (§15). I recorded the staleness in the new paragraph rather than editing
either file, and I say which session owns each correction so the operator can
route it.

**What I got wrong.** My first read of this item treated "reconciliation" as
"make the name and CIDR agree somewhere". That is backwards: they already agree,
in two separate places, and the defect was that the agreement was invisible. The
fix was to surface it in the one table an operator actually checks.