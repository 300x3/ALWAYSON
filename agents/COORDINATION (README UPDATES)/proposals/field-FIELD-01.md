---
item: FIELD-01
action: blocked
evidence: |
  # Re-verified 2026-10-05. The blocker is UNCHANGED and now ten days old.
  $ grep -h 'DRONE-RADIO.*powered up' ~/.reticulum-meshchatx/logs/meshchatx.log* | tail -1
  INFO:meshchatx.rns:[2026-09-25 17:22:28] [Notice]   RNodeInterface[DRONE-RADIO] is configured and powered up

  # Ten days of continuous failure, per rotated log, oldest first
  $ for f in meshchatx.log.3 meshchatx.log.2 meshchatx.log.1 meshchatx.log; do
      printf '%s first=' $f
      grep -ho '\[2026-[0-9-]* [0-9:]*\].*DRONE-RADIO.*unrecoverable' ~/.reticulum-meshchatx/logs/$f | head -1 | grep -o '2026-[0-9-]* [0-9:]*'
      printf '   count='; grep -c 'DRONE-RADIO.*unrecoverable' ~/.reticulum-meshchatx/logs/$f
  done
  meshchatx.log.3 first=2026-09-25 16:53:45   count=2353
  meshchatx.log.2 first=2026-10-03 14:39:57   count=7798
  meshchatx.log.1 first=2026-10-04 07:25:40   count=7866
  meshchatx.log   first=2026-10-04 23:58:26   count=3777

  # Still zero RF observations of any kind, so nothing can be characterised on either band.
  $ grep -ohE '(RSSI|SNR)[=: ]+-?[0-9.]+' ~/.reticulum-meshchatx/logs/meshchatx.log | wc -l
  0

  # BUT the cause is now narrowed to the BOARD, with every alternative measured out.
  # The adapter enumerates and has never flapped:
  $ lsusb | grep -i 10c4
  Bus 001 Device 010: ID 10c4:ea60 Silicon Labs CP210x UART Bridge
  Bus 003 Device 002: ID 10c4:ea60 Silicon Labs CP210x UART Bridge
  $ journalctl -k --no-pager | grep -cE 'usb .*disconnect|reset (high|full|super)speed'
  0
  # The port name resolves to the correct board (3-1 = USB-C = pci-0000:05:00.0):
  $ readlink -f /dev/serial/by-path/pci-0000:05:00.0-usb-0:1:1.0-port0
  /dev/ttyUSB0
  # Permissions are fine:
  $ ls -la /dev/ttyUSB0
  crw-rw---- 1 root dialout 188, 0 /dev/ttyUSB0
  # And nothing but Reticulum's own retry loop ever holds it:
  $ fuser -v /dev/ttyUSB0 /dev/ttyUSB1
                       USER        PID ACCESS COMMAND
  /dev/ttyUSB1:        scottw    840861 F.... ReticulumMeshCh
  (nothing listed for /dev/ttyUSB0)
section: 09-field-and-lora-architecture
---

**Supersedes:** this file revises the FIELD session's own earlier proposal of this path,
rewritten 2026-10-05 08:12 PDT. The earlier revision was never merged into §19.2, so the
compiler should take this version as the only FIELD proposal for this item.

**FIELD-01 stays BLOCKED, action `blocked`.** New subsection **§9.5.10**.

Closure needs RSSI/SNR/noise-floor/packet-loss/airtime on *both* bands. `DRONE-RADIO` (917 MHz)
has produced **zero** RF observations since 2026-09-25 17:22:28, so one of the two bands cannot
be measured at all and there is nothing to record.

**What is genuinely new this pass is the narrowing of the cause, which is what unblocks the
operator rather than the item.** The previous state of the record was "the board is at fault".
It is now the specific claim: *the USB bridge enumerates, the node opens, and the ESP32 on the
`DRONE-RADIO` board does not answer the identification RNode sends on that bridge.* All four
alternative explanations were tested and excluded by measurement — adapter absent (both
enumerate, zero USB disconnects), stale port name (resolves to the correct board per
`radio-ids.txt`), permissions (correct `root:dialout 0660`, operator in `dialout`), and port
contention (only Reticulum's own retry loop touches `ttyUSB0`). That points at the board's own
firmware state, a cable, or a power cycle — none of which is reachable from this host, and none
of which I attempted, because it is live serial/radio configuration.

**What I got wrong, and it is the same class of error three times in this section now.** I
tested for USB flapping with `journalctl -k --since '2026-10-04'` and with `dmesg`, and both
returned **empty**, which looks like proof the link never moved. It is not: `dmesg` is
unreadable for this user, and the `--since` window genuinely held no kernel messages. The
unfiltered `journalctl -k | grep -E 'cp210|ttyUSB'` returned the eight real lines, all from
Oct 01. **An empty result from a query whose scope I did not verify is not a negative finding.**
I only reached the correct answer by widening the query and reading what it actually said.
