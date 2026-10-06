---
item: FIELD-06
action: blocked
evidence: |
  # BLOCKER 1 UNCHANGED: the DRONE-RADIO link has been down for ten days.
  $ grep -h 'DRONE-RADIO.*powered up' ~/.reticulum-meshchatx/logs/meshchatx.log* | tail -1
  INFO:meshchatx.rns:[2026-09-25 17:22:28] [Notice]   RNodeInterface[DRONE-RADIO] is configured and powered up
  $ grep -h 'DRONE-RADIO.*unrecoverable' ~/.reticulum-meshchatx/logs/meshchatx.log | tail -1
  INFO:meshchatx.rns:[2026-10-05 07:53:56] [Error]  The interface RNodeInterface[DRONE-RADIO] experienced an unrecoverable error and is now offline.

  # Cause narrowed to the board -- see section 09 §9.5.10 for the full exclusion list.
  $ journalctl -k --no-pager | grep -cE 'usb .*disconnect|reset (high|full|super)speed'
  0
  $ lsusb | grep -ci 10c4
  2
  $ ls -la /dev/ttyUSB0
  crw-rw---- 1 root dialout 188, 0 /dev/ttyUSB0

  # BLOCKER 2 UNCHANGED: the Pi5 drone is still not on this network.
  $ getent hosts raspberrypi raspbianpios alwayondrone rpi5
  (no output)
  $ wc -l < /var/lib/misc/dnsmasq.leases
  0
  $ ip neigh
  169.254.207.81 dev eno1 lladdr 30:05:5c:ee:a2:9b STALE
section: 09-field-and-lora-architecture
---

**Supersedes:** this file revises the FIELD session's own earlier proposal of this path,
rewritten 2026-10-05 08:12 PDT. The earlier revision was never merged into §19.2, so the
compiler should take this version as the only FIELD proposal for this item.

**FIELD-06 stays BLOCKED, action `blocked`.** New subsection **§9.5.10**.

Both blockers are unchanged and independent, so this item needs two separate fixes:

1. **`DRONE-RADIO` has never come up since 2026-09-25 17:22:28** and is still erroring as of
   07:53 today. Cause is now narrowed to the board: the CP2102 bridge enumerates on bus 3 with
   zero USB disconnects, the `by-path` name resolves to the correct board, permissions are
   correct, and nothing but Reticulum's own retry loop holds the port. The ESP32 does not answer
   identification.
2. **The Pi5 that runs the QGC session is still absent from this network** — not in DNS, no
   dnsmasq lease, and the only neighbour is a link-local address.

Neither is reachable from this host, and both are live radio/network conditions, so I attempted
no repair on either.

**I did not substitute a desktop-side simulation for the missing QGC session.** A mission update
exchanged with a local mock would prove the message format and not the midflight link, which is
what this item is for.
