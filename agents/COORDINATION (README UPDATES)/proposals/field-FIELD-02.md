---
item: FIELD-02
action: blocked
evidence: |
  # Re-verified 2026-10-05. Same root blocker as FIELD-01, unchanged for ten days.
  # There is no link to test: one end of it has never come up.
  $ grep -h 'DRONE-RADIO.*powered up' ~/.reticulum-meshchatx/logs/meshchatx.log* | tail -1
  INFO:meshchatx.rns:[2026-09-25 17:22:28] [Notice]   RNodeInterface[DRONE-RADIO] is configured and powered up
  $ grep -c 'DRONE-RADIO.*powered up' ~/.reticulum-meshchatx/logs/meshchatx.log
  0
  $ grep -h 'PEOPLE-RADIO.*powered up' ~/.reticulum-meshchatx/logs/meshchatx.log.1
  INFO:meshchatx.rns:[2026-10-03 16:57:56] [Notice]   RNodeInterface[PEOPLE-RADIO] is configured and powered up
  $ grep -c 'PEOPLE-RADIO' ~/.reticulum-meshchatx/logs/meshchatx.log
  0                                   # up, and no error line today

  # No unicast/broadcast exchange to observe, on any band:
  $ grep -ohE '(RSSI|SNR)[=: ]+-?[0-9.]+' ~/.reticulum-meshchatx/logs/meshchatx.log | wc -l
  0
  $ grep -cE 'Recieved (broadcast|proof)' ~/.reticulum-meshchatx/logs/meshchatx.log
  0

  # Cause narrowed to the board itself -- adapter alive, port correct, permissions fine,
  # no contention. Full exclusion list in section 09 §9.5.10.
  $ journalctl -k --no-pager | grep -cE 'usb .*disconnect|reset (high|full|super)speed'
  0
  $ ls -la /dev/ttyUSB0
  crw-rw---- 1 root dialout 188, 0 /dev/ttyUSB0
  $ fuser -v /dev/ttyUSB0 /dev/ttyUSB1
                       USER        PID ACCESS COMMAND
  /dev/ttyUSB1:        scottw    840861 F.... ReticulumMeshCh
  (nothing for /dev/ttyUSB0)
section: 09-field-and-lora-architecture
---

**Supersedes:** this file revises the FIELD session's own earlier proposal of this path,
rewritten 2026-10-05 08:12 PDT. The earlier revision was never merged into §19.2, so the
compiler should take this version as the only FIELD proposal for this item.

**FIELD-02 stays BLOCKED, action `blocked`.** New subsection **§9.5.10**.

An end-to-end field link test needs both ends. `PEOPLE-RADIO` is up and clean; `DRONE-RADIO`
has not completed detection since 2026-09-25 17:22:28, so there is no second endpoint and no
exchange of any kind to observe — zero RSSI/SNR lines and zero received broadcasts or proofs in
the current log.

**The new information is the cause, and it is the same cause as FIELD-01**: the CP2102 bridge
for `DRONE-RADIO` enumerates on bus 3 and has never disconnected, the `by-path` name resolves
to the correct board, permissions are correct, and nothing but Reticulum's own retry loop ever
holds the port. The ESP32 on the board does not answer identification. That is a hardware or
firmware condition and cannot be cleared from this host.

**Nothing was done to clear it.** No `udevadm trigger`, no USB bus reset, no manual port probe,
no Reticulum restart. I did not attempt to work around a missing radio by loopback-testing the
one that works, because that would produce a passing test that does not evidence a field link.
