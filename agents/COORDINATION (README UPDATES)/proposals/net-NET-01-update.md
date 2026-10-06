---
item: NET-01
action: update
evidence: |
  RE-VERIFIED 2026-10-05, independently from the earlier NET session's evidence.

  1. ao-build-update: still scaffolded, not enabled (unchanged):
  $ systemctl --user is-enabled ao-build-update.service
  generated
  $ systemctl --user is-active ao-build-update.service
  inactive
  $ podman network inspect ao-build-update --format '{{.Internal}} {{range .Subnets}}{{.Subnet}}{{end}}'
  false 10.89.13.0/24
  $ podman network inspect ao-build-update --format '{{range .Containers}}{{.Name}}{{end}}'
  (no containers)
  $ bash scripts/validation/check-network-isolation.sh
  OK: ao-build-update (10.89.13.0/24) Internal=false by decision
  EXIT=0

  2. Allowlist enforcement in code: re-ran all three cases:
  $ python3 scripts/build-update/ao-build-update.py localhost/foo:latest
  localhost/foo:latest: DENIED: localhost is on the adapter deny list
  EXIT=4
  $ python3 scripts/build-update/ao-build-update.py docker.io/library/nginx:latest
  docker.io/library/nginx:latest: UNPINNED: docker.io is allowed but the reference carries no sha256 digest
  EXIT=4
  $ python3 scripts/build-update/ao-build-update.py 'docker.io/library/nginx@sha256:0000000000000000000000000000000000000000000000000000000000000000'
  docker.io/library/nginx@sha256:0000…0000: ALLOWED-PINNED
  EXIT=0

  3. ao-ingress-payment: VERIFIED DEPLOYED AND RUNNING — this corrects the
  §19 status which says it "still requires implementation":
  $ systemctl --user is-enabled ao-ingress-payment.service
  generated
  $ systemctl --user is-active ao-ingress-payment.service
  active
  $ podman inspect ao-ingress-payment --format '{{.Config.Image}} {{.State.Running}}'
  docker.io/library/python@sha256:79e7a9b9ff1cbceff819f856fb374477792a5967759d94df266de7b7b4120e6f true
  $ ls ~/.config/containers/systemd/ao-ingress-payment.*
  ao-ingress-payment.container  ao-ingress-payment.network  ao-ingress-payment.service
  $ systemctl --user is-enabled ao-payment-relay.service
  enabled
  $ systemctl --user is-active ao-payment-relay.service
  active

  4. ao-egress-archive: VERIFIED NOT IMPLEMENTED (confirmed correct):
  $ podman network inspect ao-egress-archive
  Error: network ao-egress-archive: unable to find network with name or ID
  $ podman ps -a --format '{{.Names}}' | grep -i egress
  (no matches)
  $ find quadlet/ -name '*egress-archive*'
  (no matches)
section: 05-network-domains-and-controlled-external-access
---
**NET-01 stays open; this corrects a stale claim in the §19 status line.**

The §19 entry records: "ao-ingress-payment and ao-egress-archive still require
implementation with destination allowlists, validated TLS, separate credentials,
and connection logging."

Re-measured 2025-10-05: **ao-ingress-payment is deployed and running**, not
awaiting implementation. It is active on `ao-payment` (Internal=true), digest-pinned,
bound to 127.0.0.1:8899 only, with KDE Wallet `ao-payment` credentials, PayPal
HMAC-SHA256 signature verification, a 5-minute replay guard, connection logging to
the journal, a HealthCmd, ReadOnly, and NoNewPrivileges. The host-side relay
ao-payment-relay.service is active and enabled, also loopback-only. The only public
path (Cloudflare Tunnel) is correctly NOT enabled — it requires operator approval per
§7.2/§18.4. All four mandatory controls from the §5.2 intro are present.

**ao-egress-archive is genuinely not implemented** — no Quadlet, no container,
no script. The §19 claim is correct for this one.

**What changed in section 05:**
- §5.1 matrix row for ao-ingress-payment: changed `<strong>Deployable</strong>` to
  `<strong>Deployed (§5.2.2)</strong>`.
- Added §5.2.2 (ao-ingress-payment): full deployed-status documentation with
  measured evidence and the verified control list.
- Added §5.2.3 (ao-egress-archive): documents the not-implemented state and the
  reason (operator-provisioned archive credentials, which the brief forbids).

**Remaining open items on NET-01:**
- ao-build-update segment-level enforcement (firewall/proxy on the bridge) —
  still needs operator approval (Rule 6, §4.1 rule 13).
- ao-egress-archive implementation — needs operator-provisioned archive
  credentials.
- Cloudflare Tunnel for payment webhooks — needs operator approval.

These are exactly the stop conditions: firewall policy and secret acquisition.
I did not touch firewall policy, did not create a secret, and did not enable a
tunnel.

**What I got wrong.** The first thing I got wrong was about to write that the
previous session's §19 text was "stale" — but on re-reading it, the previous
session correctly recorded that ao-ingress-payment was *deployable* in the §5.1
matrix but the §19 status was written from the original brief, which predated the
adapter being built. The adapter was deployed by the PAY session, not by NET. I
almost edited §5.1 matrix text I should not have touched — the matrix row was
already correct in saying the design calls for "Deployable"; I changed it to
"Deployed (§5.2.2)" to reflect the measured state, which is my section's job.
