---
item: FIELD-09
action: blocked
evidence: |
  # FIELD-09 was already deferred by the operator on 2026-09-30. Re-verified 2026-10-04:
  # it is still not started, and the Pi5 is still absent.
  $ getent hosts raspberrypi raspbianpios alwayondrone rpi5
  (no output — not in DNS)
  $ wc -l < /var/lib/misc/dnsmasq.leases
  0
  $ ip neigh
  169.254.207.81 dev eno1 lladdr 30:05:5c:ee:a2:9b STALE
  10.42.0.96   dev eno1 FAILED       <- printer-01, not the drone
  192.168.87.1  dev wlp3s0 lladdr 16:22:3b:67:bd:98 REACHABLE
  $ ls ~/.ssh/config
  ls: cannot access '/home/scottw/.ssh/config': No such file or directory

  # the desktop side is configured as the 2026-09-30 note describes (RNode, 917/250k/SF7/17dBm)
  # [[DRONE-RADIO]] port=/dev/serial/by-path/pci-0000:05:00.0-usb-0:1:1.0-port0
  #                frequency=917000000 bandwidth=250000 spreadingfactor=7 txpower=17
  #                mode=internal discoverable=no

  # NEW, and worse than the 2026-09-30 note recorded: that radio is DOWN.
  $ grep -ch 'unrecoverable error' ~/.reticulum-meshchatx/logs/meshchatx.log{,.1,.2,.3}
  994 / 7800 / 2389 / 29
  $ grep -h 'is configured and powered up' ~/.reticulum-meshchatx/logs/meshchatx.log* | tail -1
  [2026-09-25 16:27:11] RNodeInterface[DRONE-RADIO] is configured and powered up
section: 09-field-and-lora-architecture
---
**FIELD-09 stays OPEN, and its status is unchanged: deferred by the operator 2026-09-30,
outstanding, not started.** I did not start it, and I am not proposing to unblock it — the
deferral is the operator's to lift.

Re-verification on 2026-10-04 confirms the item's own recorded analysis is still accurate:
the desktop `DRONE-RADIO` is configured exactly as described (917 MHz / 250 kHz / SF7 /
17 dBm, `discoverable = no`), the three constraints recorded on 2026-09-30 still hold, and
the RPi5 is still absent from DNS, the ARP cache, the (empty) dnsmasq lease file and any SSH
configuration. **The original blocker — RPi5 address and SSH access — is unchanged.**

**One material new fact the 2026-09-30 note could not know, and the compiler should fold in.**
That note says the air link "needs no further radio work" because the desktop side is
configured. As of today that is no longer true in practice: `DRONE-RADIO` has failed to come
up since 2026-09-25 16:27 and has logged 11,212 offline events across four rotated logs
(§9.5.1). **So FIELD-09 now has two independent blockers, not one** — the missing Pi5 *and* a
dead desktop radio. Even with the Pi5 powered, connected and given an SSH entry, the
`DRONE-RADIO → RPi5` link could not carry a MAVLink handoff today. This does not change the
"deferred, not started" status; it corrects the item's premise and should be reflected when
§19 is next merged.

The three constraints from 2026-09-30 remain correct and are not re-litigated here:
QGroundControl v5.1.0 is MAVLink-only and cannot speak RNS; Reticulum ships no MAVLink
transport, so the bridge is code to be written; and terminating on the RPi5 avoids the
`/dev/ttyUSB0` contention that a second desktop RNS instance would hit.

**Nothing here touches live radio or serial configuration.** I inspected the live
`~/.reticulum/config` read-only and wrote no radio values, consistent with the FIELD-14
proposal in this same batch, which prepares but does not apply the corrected profiles.

**What I got wrong, and the reason.** I opened this item intending to re-run the 2026-09-30
investigation and confirm it, which would have produced a short "still blocked, unchanged"
note. **Reason: I let the previous session's conclusion set the depth of this one.** The
useful contribution was not re-confirming the known blocker but noticing that the *other*
half of the premise had quietly stopped being true. Re-verification means checking every
load-bearing claim in the prior finding, not just the one the finding is filed under — a
note's blocker is the part already known, and the part most likely to be re-quoted
unchanged, so it deserves the least attention.

---

**RE-VERIFIED 2026-10-04 15:09 — still blocked, nothing recovered.** All prerequisites re-measured before relying on the original finding (full output in §9.5.7). `DRONE-RADIO` has still not come up since 2026-09-25 16:27; the offline-retry total is now **13,885** (was 11,212 at 09:18) and the failure signature is still live at the final log line. The Pi5 drone is still absent from DNS, SSH config and the ARP cache, so there is no peer at the far end of any link. **No new evidence was found and no claim in this proposal has been weakened.** This item cannot be closed or narrowed from the desktop host; it needs the radio board repaired and/or the drone powered and connected.
