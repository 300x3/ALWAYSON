---
item: NET-01
action: update
evidence: |
  # NET-01 acceptance has two halves. Both re-measured against the running host,
  # not re-read from the previous session's notes.
  #
  # 1. ao-build-update — deployed, not enabled, allowlist enforced in code.
  $ systemctl --user is-enabled ao-build-update.service
  generated
  $ systemctl --user is-active ao-build-update.service
  inactive
  $ ls quadlet/build-update/
  ao-build-update.container  ao-build-update.network  ao-build-update.service
  $ python3 scripts/build-update/ao-build-update.py localhost/foo:latest
  allowlist boundary enforced; see the audit record
    localhost/foo:latest: DENIED: localhost is on the adapter deny list
  EXIT=4
  $ python3 scripts/build-update/ao-build-update.py docker.io/library/nginx:latest
  allowlist boundary enforced; see the audit record
    docker.io/library/nginx: UNPINNED: docker.io is allowed but the reference carries no sha256 digest
  EXIT=4
  $ python3 scripts/build-update/ao-build-update.py \
      'docker.io/library/nginx@sha256:0000000000000000000000000000000000000000000000000000000000000000'
  docker.io/library/nginx@sha256:…0000: ALLOWED-PINNED
  EXIT=0

  # 2. ao-ingress-payment — implemented and running, loopback only.
  $ systemctl --user is-enabled ao-ingress-payment.service
  generated
  $ systemctl --user is-active ao-ingress-payment.service
  active
  $ curl -sS -o /dev/null -w 'health http_code=%{http_code}\n' http://127.0.0.1:8899/health
  health http_code=200

  # 3. ao-egress-archive — genuinely not implemented, measured the same way.
  $ ls quadlet/egress-archive/ 2>&1
  ls: cannot access 'quadlet/egress-archive/': No such file or directory
  $ systemctl --user is-enabled ao-egress-archive.service 2>&1
  not-found

  # 4. The network registry this section owns is byte-identical.
  $ bash scripts/validation/check-network-isolation.sh >/dev/null 2>&1; echo "isolation EXIT=$?"
  isolation EXIT=0
  $ git --no-pager diff --stat config/ scripts/ quadlet/
  (empty)

  # 5. Community publication is inside ao-sales; there is no separate egress net.
  $ podman network ls --format '{{.Name}} {{.Internal}}' | grep '^ao-' | grep false
  ao-build-update false
  ao-reporting-egress false
  ao-sales false
  $ podman network inspect ao-sales --format '{{range .Containers}}{{.Name}} {{end}}'
  mastodon-redis ao-sales-db mastodon-web mastodon-streaming mastodon-db mastodon-sidekiq
section: 05-network-domains-and-controlled-external-access
---
**NET-01 is not closed, and the reason is in the row itself.** Its acceptance
criterion has two halves: the adapter states (which I re-verified above) and the
remaining items, which the row names explicitly as *operator decision on enabling
it, and the `build`/`update` scope question*, plus implementation of
`ao-ingress-payment` and `ao-egress-archive` with destination allowlists,
validated TLS, separate credentials and connection logging.

Of those, the first is a decision, not a measurement, and the second is work that
requires operator approval on firewall policy and public reach — both stop
conditions under §4.1 rules 6 and 13. I recorded the state a decision would be
made *from* and stopped there. §5.2.1 says the same thing in its own words:
enabling requires explicit operator authorisation and is never automatic.

**What I got wrong.** My first instinct was to re-run `check-network-isolation.sh`
— which I already knew would pass — and to treat "re-verify the adapter states"
as the whole job. It is not. The productive half of this item is the two decisions,
and neither is mine to make. I say so here rather than dressing the row up as
closed, because a tracker row that says `Complete` over an operator decision is
worse than one that says `Open` with the blocker named.

**One dangling reference I noticed and deliberately did not fix.** §5.2.1's
containment paragraph ends by pointing at `proposals/net-NET-01.md` for the
segment-level enforcement gap. That proposal is merged and the pointer now
references an applied row. It is stale, but it is a pointer into the tracker,
which is single-writer; the compiler session owns that resolution. I recorded it
here rather than editing a file outside my ownership.

**Nothing was created, removed, re-CIDRed, re-flagged, enabled, disabled or
restarted.** `git --no-pager diff --stat config/ scripts/ quadlet/` is empty.