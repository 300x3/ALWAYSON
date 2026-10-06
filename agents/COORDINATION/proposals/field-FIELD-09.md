---
item: FIELD-09
action: blocked
evidence: |
  # Re-verified 2026-10-05. FIELD-09 was already deferred by the operator on 2026-09-30,
  # and it remains not started. The Pi5 is still absent.
  $ getent hosts raspberrypi raspbianpios alwayondrone rpi5
  (no output -- not in DNS)
  $ wc -l < /var/lib/misc/dnsmasq.leases
  0
  $ ip neigh
  169.254.207.81 dev eno1 lladdr 30:05:5c:ee:a2:9b STALE

  # No QGC/MAVLink traffic has arrived from any source:
  $ grep -ciE 'mavlink|ground.control' ~/.reticulum-meshchatx/logs/meshchatx.log
  0
section: 09-field-and-lora-architecture
---

**Supersedes:** this file revises the FIELD session's own earlier proposal of this path,
rewritten 2026-10-05 08:12 PDT. The earlier revision was never merged into §19.2, so the
compiler should take this version as the only FIELD proposal for this item.

**FIELD-09 stays BLOCKED, action `blocked`.** No new section text — nothing has changed.

The operator deferred this on 2026-09-30 and the deferral still stands: it is not started, and
the Pi5 remains absent from DNS, dnsmasq and the neighbour table. No QGC or MAVLink traffic has
been received from any source.

**I am not reopening a deferred item and I am not starting it.** The measurements above are a
re-verification that the precondition is still unmet, not an attempt to establish the link. Note
for the compiler: **FIELD-09 and FIELD-06 share this same Pi5 blocker**, so they are likely to
be resolved together — worth a single operator action rather than two.
