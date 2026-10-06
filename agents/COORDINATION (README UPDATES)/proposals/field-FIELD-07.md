---
item: FIELD-07
action: blocked
evidence: |
  # Re-verified 2026-10-05. The radio this item needs IS up -- still not the FIELD-01 blocker.
  $ systemctl --user is-active reticulum-meshchatx
  active
  $ grep -h 'PEOPLE-RADIO.*powered up' ~/.reticulum-meshchatx/logs/meshchatx.log.1
  INFO:meshchatx.rns:[2026-10-03 16:57:56] [Notice]   RNodeInterface[PEOPLE-RADIO] is configured and powered up
  $ grep -c 'PEOPLE-RADIO' ~/.reticulum-meshchatx/logs/meshchatx.log
  0                                   # up, and no error line since

  # But the far end still does not exist on this network, so no two-way exchange is possible.
  $ getent hosts raspberrypi raspbianpios alwayondrone rpi5
  (no output -- not in DNS)
  $ wc -l < /var/lib/misc/dnsmasq.leases
  0
  $ ip neigh
  169.254.207.81 dev eno1 lladdr 30:05:5c:ee:a2:9b STALE

  # The MeshChatX backend that would carry the message is listening on loopback:
  $ ss -ltnp | grep -E '18000|4242'
  LISTEN 0 128  127.0.0.1:18000  0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=17))
  LISTEN 0 1    0.0.0.0:4242     0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=46))
section: 09-field-and-lora-architecture
---

**Supersedes:** this file revises the FIELD session's own earlier proposal of this path,
rewritten 2026-10-05 08:12 PDT. The earlier revision was never merged into §19.2, so the
compiler should take this version as the only FIELD proposal for this item.

**FIELD-07 stays BLOCKED, action `blocked`.** No new section text this pass — the blocker is
unchanged and already recorded in §9.5.

`PEOPLE-RADIO` is genuinely up and clean, so unlike FIELD-01/02/03/06 this is not the board
fault. The blocker is that **there is no second node to exchange a message with**: the Pi5 is
absent from DNS and from dnsmasq, and the only neighbour entry is link-local. The MeshChatX
backend is healthy and listening, so the local half of the path is proven available — the far
half has no host on it.

**I did not prove the path with a self-exchange.** Two clients on this one host would exercise
the backend and the 915 MHz transceiver, which is tempting, and it is not the item. FIELD-07 asks
for the `PEOPLE-RADIO` → MeshChatX path proven with a second node; a loopback between two local
clients would produce a green result that says nothing about the field link, which is the same
mistake as substituting a mock QGC session for FIELD-06.

**No configuration was changed.** The `0.0.0.0:4242` listener noted in the evidence is
MeshChatX's own Reticulum transport bind and is unchanged from what §9.2.1 and FIELD-04 already
record — I did not open, close or rebind it.
