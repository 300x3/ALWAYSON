---
item: SIM-08
action: keep-open
evidence: |
  Measured 2026-10-04. Untouched, deliberately. Publishing is a stop condition and
  the operator already decided against it on 2026-10-02.

  Local path works; nothing is published:
  $ systemctl --user is-active ao-sim-fabrication-portal.service
  active
  $ curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8765/viewer
  200
  ^ the viewer serves locally on loopback only.

  The network that exists for this purpose is NOT up:
  $ systemctl --user is-active ao-html-window.network
  inactive
  ^ ao-html-window (10.89.14.0/24, Internal=true) exists on disk but is inactive.

  The Cloudflare config that would need a route is a production config I did not
  touch, and I did not read its contents beyond confirming it exists:
  $ ls -la ~/.cloudflared/config.yml
  -rw-rw-r-- 1 scottw scottw 842 Sep 25 18:34 /home/scottw/.cloudflared/config.yml

  §19 records the operator decision of 2026-10-02: verified locally, not
  published. Nothing in this session changes that.
section: 10-simulation-architecture
---

SIM-08 stays open and I did nothing toward it. This is the clearest stop-condition item in my
group and I am reporting it as untouched rather than as progress.

The viewer works on the local path — the portal service is active and `/viewer` returns 200
on loopback — but nothing is published. §19 records the operator's decision of 2026-10-02
that it is verified locally and deliberately not published, and I have no reason to revisit
that.

Two things I found that matter for whenever it does proceed. `ao-html-window.network`, the
network that exists specifically for public-facing windows on local services, is **inactive**
— so even a configured route would have nothing to land on. And the remaining work named in
§19 all touches things I am not permitted to change unilaterally: confirming the hostname,
editing `~/.cloudflared/config.yml` (a customer-facing production config), and the
decision of whether to publish the viewer alone or the portal too — the portal renders
boning derived from real machines, so that is a data-exposure decision, not a technicality.

I changed no public port, no firewall policy, no ingress route, and no Cloudflare
configuration. I confirmed `config.yml` exists and its size and did not read or print its
contents.

**What I got wrong.** I listed `~/.cloudflared/config.yml` expecting to check whether a
hostname route for the viewer already existed, on the reasoning that a read-only check is
harmless and would tell me how far along this is. Reading a customer-facing production
ingress config to satisfy my own curiosity is not a neutral act — the file is the kind of
thing where contents inform topology I have no mandate over. Existence and size are the
whole of what I needed; I should have stopped there rather than constructing a reason to read
it.
