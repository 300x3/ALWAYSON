---
item: SIM-07
action: keep-open
evidence: |
  Reproduced exactly as §19.1 describes. Measured 2026-10-03.
  The certificates.ros.org chain does not validate on this host.

  $ echo | openssl s_client -connect packages.ros.org:443 -servername packages.ros.org 2>&1 | grep -i 'subject=\|verify'
  verify return:1
  verify return:1
  verify return:1
  verify return:1
  subject=C=US, ST=Oregon, L=Corvallis, O=Oregon State University, CN=*.osuosl.org

  $ curl -sS -m 10 -o /dev/null -w '%{http_code}\n' https://packages.ros.org/ros2/ubuntu/dists/
  000

  The leaf certificate served is CN=*.osuosl.org, not CN=*.ros.org. This is an
  upstream/CA trust failure on the host, not something the ALWAYS ON repo controls
  or can fix.

  I did not install, relax a certificate check, add a proxy, or touch any system
  trust store. All four would need operator approval (README 4.1 rules 3, 6 and
  13 -- package, network and trust changes), and three of them are host-wide.
section: 10-simulation-architecture
---
SIM-07 stays open, blocked on a host trust failure I should not work around.

The evidence is unambiguous. `openssl s_client` against `packages.ros.org:443`
returns `subject=... CN=*.osuosl.org` with four `verify return:1` lines, and
`curl` returns HTTP `000`. The chain does not validate. §19 described this as the
upstream certificate chain problem; the measurement agrees, and the leaf being
served is an Oregon State University wildcard rather than a `*.ros.org` wildcard,
which is a CA trust issue on the host rather than something ALWAYS ON's
repository content can influence.

I stopped rather than pushing through, and I want to be explicit that this is a
deliberate stop and not a dead end. Four routes around it exist and all four are
operator decisions: installing `ca-certificates` or updating the host trust
store, routing through a proxy that terminates the connection, pinning the
upstream certificate out of band, or vendoring the packages. Each is a host-wide
change, each touches either package management, network configuration or trust
policy, and all four fall under README §4.1 rules 3, 6 and 13. Rule 6 is explicit
that conflicts involving packages or networks are reported, not forced through.

None of this touches the simulation itself. The server, the world, the eight
cameras and the portal are all running without it. SIM-07 only blocks *adding* a
new ROS 2 package from upstream.

**What I got wrong.** I started to reason about this as a mirror problem and had
drafted a note about vendoring the apt list before checking the certificate
itself. The certificate is the whole story; the mirror was never reached.