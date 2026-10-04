---
item: FIELD-02
action: blocked
evidence: |
  # same root blocker as FIELD-01 — DRONE-RADIO offline since 2026-09-25 16:27
  $ grep -ch 'unrecoverable error' ~/.reticulum-meshchatx/logs/meshchatx.log{,.1,.2,.3}
  891 / 7800 / 2389 / 29      # 11109 total offline events
  $ grep -h 'is configured and powered up' ~/.reticulum-meshchatx/logs/meshchatx.log* | tail -1
  [2026-09-25 16:27:11] RNodeInterface[DRONE-RADIO] is configured and powered up

  # no RF traffic at all, so no unicast/broadcast exchange to observe
  $ grep -oh -E '(RSSI|rssi)[=: ]+[-0-9.]+' ~/.reticulum-meshchatx/logs/meshchatx.log* | wc -l
  0

  # a link test also needs a peer at the far end; the Pi5 drone is not on this network
  $ getent hosts raspberrypi raspbianpios alwayondrone rpi5
  (no output — not in DNS)
  $ ls ~/.ssh/config
  ls: cannot access '/home/scottw/.ssh/config': No such file or directory
  $ ip neigh
  169.254.207.81 dev eno1 lladdr 30:05:5c:ee:a2:9b STALE
  10.42.0.96   dev eno1 FAILED
  192.168.87.1  dev wlp3s0 lladdr 16:22:3b:67:bd:98 REACHABLE
section: 09-field-and-lora-architecture
---
**FIELD-02 stays OPEN — action `blocked`.** Recorded in the new §9.5 / §9.5.5 in §9.

This item has **two** independent blockers, and both must clear before an end-to-end test is
possible:

1. **No drone-side RF path.** `DRONE-RADIO` (917 MHz) has failed to come up since
   2026-09-25 16:27, 11,109 logged offline events across four rotated logs. One of the two
   paths the item wants tested does not exist on air.
2. **No peer at the far end.** Unicast and broadcast need two ends. The Pi5 drone is not
   connected: no DNS entry, no SSH config, absent from the ARP cache, and the dnsmasq lease
   file is empty. `10.42.0.96` is `printer-01` (down), not the drone.

The fail-safe half of the criteria — verified on radio, serial-path and peer loss — is
likewise untestable: with only one radio on the host there is no peer to lose and no second
path to fail over to.

**One genuinely useful thing this session established**, and the reason the item is `blocked`
rather than merely untouched: **peer loss *is* being observed continuously, and the system is
not recovering from it.** The reconnect loop in §9.5.1 is exactly the peer/serial-loss
fail-safe path, and it has been running for ten days without ever succeeding. That is a real
finding about fail-safe behaviour, just not the pass the criteria ask for. I record it as a
finding and **not** as a closure, because the criteria require unicast *and* broadcast to be
proven, which needs the radio back.

**I did not restart the stack to "clear" the loop.** Killing `ReticulumMeshChatX`
(PID 840861) would drop the live `0.0.0.0:4242` listener that FIELD-04 decided is
LAN-reachable, and would touch live radio and serial state. That is a stop condition, and
doing it to make a test *look* runnable would be worse than leaving the item open.

**What I got wrong, and the reason.** I nearly recorded the ten-day reconnect loop as
evidence that the fail-safe criteria were satisfied, because the criteria mention "peer loss"
and I had ten days of peer loss on record. **Reason: I was pattern-matching my evidence onto
the item's wording instead of testing it against the wording.** A criterion that says fail-safe
must be *verified* wants a demonstration that the system recovers; what I have is proof that
it does not. Recording that as a pass would have inverted the finding — which is the specific
failure mode this single-writer proposal process exists to prevent.