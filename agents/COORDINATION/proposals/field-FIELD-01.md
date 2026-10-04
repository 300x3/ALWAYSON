---
item: FIELD-01
action: blocked
evidence: |
  # BLOCKER: DRONE-RADIO (917 MHz) has never come up since 2026-09-25 16:27
  $ grep -h 'is configured and powered up' ~/.reticulum-meshchatx/logs/meshchatx.log* | tail -3
  [2026-09-24 11:02:55] RNodeInterface[DRONE-RADIO] is configured and powered up
  [2026-09-25 16:27:08] RNodeInterface[PEOPLE-RADIO] is configured and powered up
  [2026-09-25 16:27:11] RNodeInterface[DRONE-RADIO] is configured and powered up
  $ grep -ch 'unrecoverable error' ~/.reticulum-meshchatx/logs/meshchatx.log{,.1,.2,.3}
  994
  7800
  2389
  29

  # the failure loop, still live at the last log line (2026-10-04 09:18:25)
  [2026-10-04 07:25:38] [Notice] Opening serial port /dev/serial/by-path/pci-0000:05:00.0-usb-0:1:1.0-port0...
  [2026-10-04 07:25:40] [Error]  Could not detect device for RNodeInterface[DRONE-RADIO]
  [2026-10-04 07:25:40] [Error]  A serial port error occurred, ... [Errno 9] Bad file descriptor
  [2026-10-04 07:25:40] [Error]  The interface RNodeInterface[DRONE-RADIO] experienced an unrecoverable error and is now offline.

  # the metrics FIELD-01 asks for do not exist anywhere in the logs
  $ grep -oh -E '(RSSI|rssi)[=: ]+[-0-9.]+' ~/.reticulum-meshchatx/logs/meshchatx.log* | wc -l
  0

  # not a symlink / permission / enumeration fault — all ruled out by measurement
  $ ls -la /dev/serial/by-path/
  pci-0000:05:00.0-usb-0:1:1.0-port0 -> ../../ttyUSB0
  $ ls -la /dev/ttyUSB0
  crw-rw---- 1 root dialout 188, 0 Oct  4 09:17 /dev/ttyUSB0
  $ id
  uid=1000(scottw) ... groups=...,20(dialout),...
  $ journalctl -k | grep cp210x
  cp210x 3-1:1.0: cp210x converter detected
  usb 3-1: cp210x converter now attached to ttyUSB0

  # PEOPLE-RADIO (915 MHz) is UP on the same stack, same code path, other port
  $ grep -h 'PEOPLE-RADIO. is configured and powered up' ~/.reticulum-meshchatx/logs/meshchatx.log.1
  [2026-10-03 16:57:56] [Notice] RNodeInterface[PEOPLE-RADIO] is configured and powered up
  $ grep -c 'PEOPLE' ~/.reticulum-meshchatx/logs/meshchatx.log
  0
section: 09-field-and-lora-architecture
---
**FIELD-01 stays OPEN — action `blocked`.** §9 gains a new **§9.5** recording the measured
link state, so this does not have to be re-derived next session.

The item asks for RSSI, SNR, noise floor, packet loss, retry behaviour and airtime
**recorded on both RNodes**. One of the two radios has been dead for ten days, so "both
bands" is not measurable. The decisive evidence is not the error itself but its
**asymmetry**: `PEOPLE-RADIO` came up 29 seconds after the same process started and has
logged no error since, on the same stack, over the other USB port. That isolates the fault
to the DRONE-RADIO board.

I ruled out the boring causes rather than assuming them — missing `by-path` symlink,
`dialout` permission, and USB enumeration failure are each contradicted by direct output
above. What remains is the board answering on USB but not answering the RNode detection
handshake (`Could not detect device` preceded by no port-level error). **Best supported
cause: the RNode firmware on the board is not running or is wedged.** The remedy is
physical — reseat the cable, or reflash — which is outside what I can or should do.

**I did not attempt any corrective action.** Repowering the radio, reflowing it, or
restarting the stack are all live radio configuration, and README §4.1 rule 6 makes touching
live serial devices a stop condition. This is a hand-off, not a fix.

**What I got wrong, and the reason.** My first instinct on reading "RF characterization"
was to look for an RF measurement *tool* to run — something like a spectrum sweep — and my
first two commands went looking for the hardware and the running stack instead of the
logs. **Reason: I optimised for producing a measurement rather than for asking whether a
measurement is even possible.** The logs answered the question in one grep, because a radio
that has never come up cannot have an RSSI distribution. Check whether the thing you are
measuring exists before you go measuring it.