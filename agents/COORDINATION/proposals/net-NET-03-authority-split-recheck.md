---
item: NET-03
action: update
evidence: |
  NET-03 REMAINS OPEN on the unchanged blocker. Re-verified this pass rather than
  cited, because the last four passes all measured the same thing.

  The registry half still holds and is still the single authority:
    $ bash scripts/validation/check-network-isolation.sh
    OK: all domain networks present; isolation domains internal-only;
        3 egress networks non-internal by decision; registry matches host (14 = 11 + 3)
    EXIT=0

  $ python3 agents/COORDINATION/tools/compile.py --check
    identical
  (README.md still matches its own section files - the NET-03 regression of an
   earlier pass has not recurred.)

  The blocker is unchanged: network-cidrs.yaml is authoritative for CIDRs and
  Internal flags only. Attachment, purpose and adapter status live elsewhere, and
  the ao-egress-community retirement was applied to some of those files and not
  others. Re-confirmed still stale this pass:

    $ grep -n 'ao-egress-community' config/platform/topology-model.yaml
      582:  ao-egress-community:
      585:    status: implemented      <-- for a network retired 2026-09-30
      note: "Only Mastodon web/Sidekiq join this adapter network ..."
    $ grep -c 'ao-egress-community' \
        config/platform/monitoring/grafana/provisioning/dashboards/json/ao-topology.json
      4        <-- still drawn on the operator dashboard, in 4 places
    $ grep -n 'ao-egress-community' config/platform/gui-boundary-matrix.yaml
      (still routes external publication through it)
    $ grep -n 'ao-egress-community' docs/runbooks/mastodon.md
      (still requires the scoped route)

  The Grafana JSON is GENERATED from topology-model.yaml by
  scripts/operations/generate-topology.py, so editing the JSON would be undone on
  the next run. The fix belongs in the model. None of these four files is mine.
  Not touched.

  NEW CROSS-CHECK THIS PASS, on the §5.1 attachment column I own. It is a
  structural check, not a re-count, and no prior NET pass ran it: every container
  on the host holding MORE THAN ONE ao-* network, checked against the §5.1 rule
  that permits a second attachment only where the approved path says so.

    $ for c in $(podman ps --format '{{.Names}}'); do ... done
    ao-metabase                   ao-admin ao-reporting-egress
    ao-sim-fabrication-foxglove   ao-html-window ao-sim-fabrication
    ao-grafana                    ao-admin ao-reporting-egress

  Exactly three dual-homed containers, all three already documented: the
  foxglove bridge in §5.1.2, and the grafana/metabase reporting pair on
  ao-reporting-egress (the §5.1 row already says "also on ao-admin"). No
  undocumented dual-homing exists, so the §5.1 rule is being honoured.
section: 05-network-domains-and-controlled-external-access
---
**NET-03 stays open, unchanged, and I am not going to keep re-asserting it in a
way that sounds like progress.** The authority is still split across four files
I do not own, and I re-confirmed this pass that all four still describe a network
retired on 2026-09-30. The registry half is sound and verified above.

The one genuinely new thing I did was stop trusting my own table and check it
structurally. Every prior NET pass verified the §5.1 attachment column *by
re-measuring it*; none ever asked whether any container violates the §5.1
one-network-per-component rule by holding two. Running that check across every
running container found exactly three dual-homed containers, and all three were
already documented — the foxglove bridge in §5.1.2, and grafana/metabase on
`ao-reporting-egress`. So the rule this section states is actually being obeyed,
which no earlier pass had established. That is a small result, but it is a
different kind of result from the fourteen re-measurements that preceded it, and
it is the one that would have caught a real breach.

I am recording this as an update rather than proposing a new item: the split
authority is a known, already-escalated condition, and opening a fifth number for
"the same blocker, still blocked" would add noise to §19 rather than information.

**What I got wrong.** I nearly closed this session having re-run the isolation
check and written "NET-03 unchanged", which would have been true and worthless.
The previous pass had already written those words. Repeating a verification
because it is cheap is not diligence; the question worth asking was always whether
the attachment column *could* be wrong, not whether it currently was.