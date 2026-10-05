---
item: FIELD-06
action: blocked
evidence: |
  # BLOCKER 1: the DRONE-RADIO link this item is about has been down since 2026-09-25
  $ grep -ch 'unrecoverable error' ~/.reticulum-meshchatx/logs/meshchatx.log{,.1,.2,.3}
  994 / 7800 / 2389 / 29
  $ grep -h 'is configured and powered up' ~/.reticulum-meshchatx/logs/meshchatx.log* | tail -1
  [2026-09-25 16:27:11] RNodeInterface[DRONE-RADIO] is configured and powered up

  # BLOCKER 2: the Pi5 drone that runs the QGC session is not on this network
  $ getent hosts raspberrypi raspbianpios alwayondrone rpi5
  (no output — not in DNS)
  $ ls ~/.ssh/config
  ls: cannot access '/home/scottw/.ssh/config': No such file or directory
  $ ip neigh
  169.254.207.81 dev eno1 lladdr 30:05:5c:ee:a2:9b STALE
  10.42.0.96   dev eno1 FAILED      <- this is printer-01, not the drone
  192.168.87.1  dev wlp3s0 lladdr 16:22:3b:67:bd:98 REACHABLE
  $ wc -l < /var/lib/misc/dnsmasq.leases
  0

  # BLOCKER 3: the criteria require a mission change demonstrated IN FLIGHT,
  # which is explicitly outside a documentation session.
section: 09-field-and-lora-architecture
---
**FIELD-06 stays OPEN — action `blocked`.** Recorded in the new §9.5.5 / §9.5.6 in §9.

Three blockers, and the third alone would be sufficient. They are listed in order of how
much they can be cleared without the operator:

1. **The link is down.** `DRONE-RADIO` (917 MHz) has not come up since 2026-09-25 16:27 —
   11,212 logged offline events. A mission cannot reach a QGC session over a radio that is
   not transmitting.
2. **The Pi5 drone is absent.** No DNS entry, no SSH config, not in the ARP cache, and the
   dnsmasq lease file is empty. There is no QGC session on the far end to address.
   (`10.42.0.96` is `printer-01`, down — worth stating because it is the only host IP on the
   wired segment and could easily be mistaken for the drone.)
3. **The criteria require an in-flight demonstration.** "A mission change demonstrated *in
   flight*" needs an airborne drone and a pilot. Even with blockers 1 and 2 cleared this
   session could not honestly produce that evidence, and I will not claim it from a desk.

**The second half of the criteria is worth recording as a standing answer, since it is a
question about design rather than about hardware.** The item asks to "record that no IP path
and no mTLS is used on this link". That is confirmed by the configuration and is worth
stating plainly: `DRONE-RADIO` is configured `discoverable = no`, `mode = internal`, and
plain RNode over Reticulum; there is no IP route and no TLS on this path, and §9.2.2
already specifies it that way. **Radio-only is the designed and intended security posture
for this link — the absence of IP and mTLS is not a gap to be closed, it is the point.**
That half of the criteria is satisfied by design and needs no hardware.

**What I got wrong, and the reason.** My first pass treated this as one blocker (the Pi5)
because FIELD-09, which shares the Pi5 dependency, had already recorded it as blocked — and
on that basis I nearly wrote the proposal citing only the missing Pi5. **Reason: I let
FIELD-09's recorded blocker stand in for my own investigation instead of checking the radio
state independently, and the two items do not share all their blockers.** FIELD-09 is
primarily a bridge-to-be-written problem; FIELD-06 has a *currently dead transmitter* that
would block it even with the Pi5 plugged in and reachable. Reusing another item's finding
without re-measuring is the same error the coordination protocol warns about when it says
another document's claim is a hypothesis, not evidence.

---

**RE-VERIFIED 2026-10-04 15:09 — still blocked, nothing recovered.** All prerequisites re-measured before relying on the original finding (full output in §9.5.7). `DRONE-RADIO` has still not come up since 2026-09-25 16:27; the offline-retry total is now **13,885** (was 11,212 at 09:18) and the failure signature is still live at the final log line. The Pi5 drone is still absent from DNS, SSH config and the ARP cache, so there is no peer at the far end of any link. **No new evidence was found and no claim in this proposal has been weakened.** This item cannot be closed or narrowed from the desktop host; it needs the radio board repaired and/or the drone powered and connected.
