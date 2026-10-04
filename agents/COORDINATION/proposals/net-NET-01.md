---
item: NET-01
action: update
evidence: |
  NET-01 requires three things and I can do exactly one of them. Two are
  blocked by rules that say stop, not try harder.

  DONE AND VERIFIED - §5.2.1 no longer overclaims enforcement. The section said
  the allowlisted acquisition is "the only sanctioned outbound", which reads as a
  control that is operating. Nothing enforces it. Both the status paragraph and
  the Containment paragraph now say so explicitly, and the measured state is
  recorded:
  $ systemctl --user is-enabled ao-build-update.service
  generated
  $ systemctl --user is-active ao-build-update.service
  inactive
  $ podman network inspect ao-build-update --format '{{.Internal}} {{range .Subnets}}{{.Subnet}}{{end}}'
  false 10.89.13.0/24
  $ ls ~/.config/containers/systemd/ao-build-update.*
  ao-build-update.container  ao-build-update.network  ao-build-update.service
  # unit files are installed; the service is not running and not enabled

  §5.2.1 now carries the measured is-enabled/is-active output, states that no
  container is attached to the network, and carries a status note reading:
  "The allowlist is documentation of intent, not an enforced control."
  Confirmed by the isolation script:
  OK: ao-build-update (10.89.13.0/24) Internal=false by decision

  BLOCKED 1 - destination allowlist is not wired to anything enforceable.
  config/build-update/registry-allowlist.yaml and stable-refs.yaml exist and are
  populated. Nothing reads them at runtime, and there is no network mechanism
  that would make them binding even if something did read them: the network is
  an ordinary podman bridge with Internal=false, so any container attached to it
  can reach any host on the internet. Enforcing the allowlist means either a
  filtering proxy, a firewall rule set on the bridge, or per-destination
  proxies. All three touch firewall policy and public routing.
  Rule 6: never expose a public port without explicit operator approval.
  Rule 13: do not broaden network access to bypass an error.
  Rule 6 / 12 of §4.1: stop and report conflicts involving networks and
  firewall policy - do not force through them.
  -> STOPPED. Needs operator approval of a firewall/proxy design first.

  BLOCKED 2 - the egress adapter would need its own credentials, and creating
  them is an explicit stop condition.
  §5.2.1 requires a destination allowlist plus TLS validation plus SEPARATE
  CREDENTIALS. Acquiring a registry credential means a token, a login, and a
  secret written into KDE Wallet. My instructions for this session stop
  explicitly on "payments, ledger keys, secrets, backup data, live radio or
  ports". A registry token is a secret.
  -> STOPPED. Needs operator approval, and the secret must never appear in a
  proposal, a log line, or a commit.

  BLOCKED 3 - validating "TLS validation" needs a live pull, and a live pull is
  an uncontrolled acquisition from the public internet, which is the thing the
  whole control exists to govern. Circular, and not something to resolve by
  widening access.
  -> STOPPED.
section: 05-network-domains-and-controlled-external-access
---
**NET-01 stays open. I completed the documentation half and stopped at the two
halves that the rules forbid without your approval.**

Done: §5.2.1 no longer implies the build-update adapter can reach the internet
when nothing is running, and — the substantive correction — it no longer claims
the destination allowlist is enforced. It now records the measured state (unit
files installed, `is-enabled` = `generated`, `is-active` = `inactive`, network
allocated at `10.89.13.0/24` with `Internal=false` and zero attached
containers), and it states in two places that the allowlist is documentation of
intent rather than an operating control. I found that second claim while
verifying the first: the old text said allowlisted acquisition is "the only
sanctioned outbound", which is true as a *requirement* and false as a
*description*. A config file in a config tree reads as a boundary, and this one
is not one.

Not done, and deliberately:

1. **The destination allowlist is inert.** `registry-allowlist.yaml` and
   `stable-refs.yaml` are populated config that nothing enforces. The network
   is a plain `Internal=false` bridge, so anything attached to it can reach
   anything on the internet. Making the allowlist binding requires a firewall
   rule set, a filtering proxy, or per-destination proxies — firewall policy and
   public routing, which is Rule 6 and Rule 12 territory. My brief says stop for
   ports; I have stopped.

2. **The required separate credentials are a secret acquisition**, which my
   brief stops on explicitly. Even with approval, the token must go to KDE
   Wallet and must not appear in a log line, a proposal, or a commit.

3. **Verification of "TLS validation" requires a live pull from the public
   internet**, which is an uncontrolled acquisition — the exact thing the
   control exists to prevent. I am not resolving that by widening access.

**Why I am reporting rather than escalating a design.** The three items are
sequential: an allowlist that is not enforced is worse than no allowlist,
because it reads in the config tree as a control that exists. Two options are
honest and both need you: (a) approve a specific enforcement mechanism — a
firewall rule set on the `ao-build-update` bridge is the smallest — and I
implement it; or (b) leave the adapter scaffolded and change §5.2.1 to say the
allowlist is *documentation of intent*, not a control, so no future reader
mistakes a config file for a boundary. I recommend (b) as the current truth and
(a) as the fix. I did not pick one for you because it is firewall policy.

**Assumptions.** I assume `is-enabled: generated` means the unit is not enabled
to start at boot, which is consistent with `is-active: inactive` and with the
absence of any `ao-build-update` container in `podman ps`. If you know a
mechanism that starts it, tell me and I will re-measure.
