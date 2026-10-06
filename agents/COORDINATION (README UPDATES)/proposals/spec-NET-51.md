---
item: NET-51
action: new
evidence: |
  $ podman inspect $c --format '{{index .Config.Labels "PODMAN_SYSTEMD_UNIT"}}'
  # key does not exist on this host -- returns empty for ALL 25 running containers,
  # including ao-grafana.service, ao-prometheus.service and every other managed one.
  # The key Quadlet actually writes is PODMAN_SYSTEMD_UNIT:
  ao-grafana.service, ao-prometheus.service, ao-metabase.service, ...

  $ for n in $(podman network ls --format '{{.Name}}' | grep '^ao-'); do
      podman network inspect $n --format 'internal={{.Internal}}'; done
  # 11 of 14 networks are internal=true. THREE are internal=false:
  ao-reporting-egress internal=false subnets=10.89.10.0/24
  ao-sales           internal=false subnets=10.89.0.0/24
  ao-build-update    internal=false subnets=10.89.13.0/24

  # live state and the registry agree exactly:
  $ grep -nE 'internal=' /ALWAYSON/config/platform/network-cidrs.yaml
  14:ao-reporting-egress internal=false subnets=10.89.10.0/24
  15:ao-sales internal=false subnets=10.89.0.0/24
  16:ao-build-update internal=false subnets=10.89.13.0/24

  # and the host has a THIRD address family beyond the documented equipment LAN:
  $ ip -4 addr show | grep 'inet ' | grep -v 127.0.0.1
  inet 10.42.0.1/24        scope global  noprefixroute  eno1
  inet 192.168.87.135/24   scope global  dynamic       wlp3s0
  inet 169.254.248.253/16  scope link   noprefixroute  eno1
section: 03-high-level-architecture
---
# Three cross-group findings from the SPEC review, none of them mine to close

## 2. NET-51 — three `Internal=false` networks, and the isolation rule is not absolute

`AGENTS.md` and the workspace rules state flatly that "All workload networks are
`Internal=true`". Measured, **three of fourteen are not**: `ao-reporting-egress`,
`ao-sales`, `ao-build-update`. All three are egress networks, which cannot be `Internal`
and still reach anything, so this is the rule working rather than breaking. But the rule as
written is not literally true, and any security argument that leans on it is wrong by
three. The registry and live state agree exactly, so nothing is out of sync — only the
summary sentence is over-broad. I have documented all fourteen with their flags in §3 so
the exception is visible where the rule is stated.

Related: §3.3.0.1's "no route off the subnet" is a statement about a *container's* view,
not the host's. Nothing in `Internal=true` constrains the host's own interfaces, and the
host has a Wi-Fi interface on `192.168.87.0/24` that §3 does not mention at all.

## What I got wrong

Three things, all caught by re-running my own commands:

1. **The label key.** Spent a full review pass asserting ownership facts from a key that
   is set on nothing. The conclusion held but the evidence did not support it. Recorded in
   §6 with the correction inline.
2. **"Contiguous and gap-free."** I asserted this about the `10.89` block without checking.
   It is false — third octet `11` is absent. It happens to be the one already-known
   unallocated subnet, so it is consistent rather than a new problem, but I would have
   published a false claim. Caught by counting, not by reading.
3. **"The only non-`ao-` addressing is `10.42.0.0/24`."** Also asserted without checking,
   also false — there is a `192.168.87.0/24` Wi-Fi network and a link-local. Both 2 and 3
   are the same failure: writing a general statement about a set I had only partially
   enumerated.
4. **"§3 describes the host as having only the equipment LAN."** This one was wrong in the
   *opposite* direction, which is the more useful kind to catch. I asserted the Wi-Fi
   interface was undocumented project-wide; having recompiled the README I checked the whole
   document instead of only my own section, and it is documented in at least two others
   (§5 host-address row, and the MeshChatX `0.0.0.0:4242` note in §9). The real finding is a
   consistency gap in §3 alone, not a gap in the record. Had I not recompiled before
   committing, that would have gone into the README as a claim that two other sections are
   missing something they are not missing.

The pattern across all four is the same: I generalised from a partial enumeration, and each
time the correction came from running the check rather than from re-reading my own text.
Re-reading is not verification.

I have kept both corrections visible in §3 rather than quietly deleting the wrong text,
because the wrong text was already there and the next reader needs to know it was wrong.
## 1. NET-51 (new) — the Quadlet ownership label is `PODMAN_SYSTEMD_UNIT`, not `io.podman.annotations.quadlet`

This is the most consequential finding of my pass, and it is a **methodology** finding
rather than a defect: on this host the intuitive label key is set on *nothing*, so any
ownership enumeration using it returns all-empty and looks like a discovery.

Every session that has claimed "these containers have no Quadlet label" may have done so
with the wrong key. My own §6 evidence did. The conclusion in that case survived, but only
by luck — I had named the containers by hand, so the correct reading came from the name
list rather than from the query. **A session that enumerated by image string and then
filtered on the label would have concluded that no container on this host has a service
owner, and that is the opposite of the truth.**

I have corrected my own evidence and left a trap note in §6, but other sections may carry
the same bad evidence and those files are not mine. This needs a sweep by whoever owns the
affected sections.