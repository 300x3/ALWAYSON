---
item: FIELD-07
action: blocked
evidence: |
  # the radio this item needs IS up — this is not a repeat of the FIELD-01 blocker
  $ grep -h 'PEOPLE-RADIO. is configured and powered up' ~/.reticulum-meshchatx/logs/meshchatx.log.1
  [2026-10-03 16:57:56] [Notice] RNodeInterface[PEOPLE-RADIO] is configured and powered up
  $ grep -c 'PEOPLE' ~/.reticulum-meshchatx/logs/meshchatx.log
  0                                   # up, and no error since

  # but a two-way MeshChatX text exchange needs a MESH PEER at the far end.
  # there is none on this host or reachable from it:
  $ getent hosts raspberrypi raspbianpios alwayondrone rpi5
  (no output — not in DNS)
  $ wc -l < /var/lib/misc/dnsmasq.leases
  0
  $ ip neigh
  169.254.207.81 dev eno1 lladdr 30:05:5c:ee:a2:9b STALE
  10.42.0.96   dev eno1 FAILED
  192.168.87.1  dev wlp3s0 lladdr 16:22:3b:67:bd:98 REACHABLE

  # and the only mesh peer traffic visible is PUBLIC backbone auto-connection,
  # not PEOPLE-RADIO traffic:
  $ grep -oh -E 'Auto-connecting discovered [A-Za-z]+' ~/.reticulum-meshchatx/logs/meshchatx.log | sort | uniq -c
        1 Auto-connecting discovered BackboneInterface
section: 09-field-and-lora-architecture
---
**FIELD-07 stays OPEN — action `blocked`.** Recorded in the new §9.5.5 in §9. This item
**differs from FIELD-01/02/03/06 and should not be reported as sharing their blocker**:
`PEOPLE-RADIO` is up and clean, so the radio half of this item is in the best shape of any
field item.

The blocker is the **mesh peer**. The criteria want MeshChatX text carried over
`PEOPLE-RADIO` *in both directions*, which is a two-node exchange. There is no second node:
the Pi5 drone is absent from DNS, from the ARP cache, and from an empty dnsmasq lease file,
and no SSH configuration exists for any Pi. A one-way or loopback demonstration would not
satisfy "both directions" and I did not attempt to manufacture one.

Worth recording plainly for the compiler, because it is easy to misread: **the single
`Auto-connecting discovered BackboneInterface` line in the log is public Reticulum backbone
traffic, not PEOPLE-RADIO traffic.** It must not be cited as evidence that the field radio is
carrying traffic.

**A wording correction for whoever merges this.** The item's title and criteria call this
the "MeshChatX **LoRaWAN** path". Under the rule FIELD-13 established — recorded in §9.4.3 —
this system is **not LoRaWAN**; it is raw LoRa over Reticulum via RNode. The title should
read "PEOPLE-RADIO → MeshChatX raw-LoRa path". The criteria additionally say the exchange is
to be "recorded as LoRaWAN-related communication", which directly contradicts §9.4.3. I
propose the compiler reword both when merging, **and flag that this is §19 text I cannot
edit myself.** I have deliberately not edited the item title.

**What I got wrong, and the reason.** My first instinct was to group FIELD-07 with
FIELD-01/02/03 as "blocked, radio down" — because six of my items share a blocker and
grouping them is the efficient story. That would have been **factually wrong**: I checked
`PEOPLE-RADIO`'s state specifically rather than inferring it from the group, and found it
up. **Reason: I was about to let a convenient shared narrative override a measurement I had
not yet made.** The lesson generalises past this session: a shared root cause across items
is a hypothesis until each item is individually measured, and a wrong grouping propagates a
wrong blocker into the one file all eleven sessions read.