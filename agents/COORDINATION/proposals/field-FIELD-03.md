---
item: FIELD-03
action: blocked
evidence: |
  # Cross-band isolation needs a transmitter on BOTH bands. One band is silent.
  # Live config is still correct and unchanged -- this is a config pass, a link fail:
  $ grep -A8 '\[\[PEOPLE-RADIO\]\]' ~/.reticulum/config | grep -E 'frequency|bandwidth|spread'
  frequency = 915000000
  bandwidth = 125000
  spreadingfactor = 7
  $ grep -A9 '\[\[DRONE-RADIO\]\]' ~/.reticulum/config | grep -E 'frequency|bandwidth|spread'
  frequency = 917000000
  bandwidth = 250000
  spreadingfactor = 7

  # 917 MHz transmitter: dead. Last successful detection 2026-09-25 17:22:28.
  $ grep -h 'DRONE-RADIO.*powered up' ~/.reticulum-meshchatx/logs/meshchatx.log* | tail -1
  INFO:meshchatx.rns:[2026-09-25 17:22:28] [Notice]   RNodeInterface[DRONE-RADIO] is configured and powered up

  # No transmissions observed on either band, so nothing can be compared:
  $ grep -ohE '(RSSI|SNR)[=: ]+-?[0-9.]+' ~/.reticulum-meshchatx/logs/meshchatx.log | wc -l
  0
  $ grep -cE 'Recieved (broadcast|proof)' ~/.reticulum-meshchatx/logs/meshchatx.log
  0
section: 09-field-and-lora-architecture
---

**Supersedes:** this file revises the FIELD session's own earlier proposal of this path,
rewritten 2026-10-05 08:12 PDT. The earlier revision was never merged into §19.2, so the
compiler should take this version as the only FIELD proposal for this item.

**FIELD-03 stays BLOCKED, action `blocked`.** New subsection **§9.5.10**.

Isolation is a comparison between two bands, and the configuration half of this item **passes
today**: the live `~/.reticulum/config` still carries the 915 MHz / 125 kHz and 917 MHz / 250 kHz
split with SF7 on both, so the two radios are still configured to be distinguishable. What is
missing is the measurement half — `DRONE-RADIO` has not detected since 2026-09-25 17:22:28, so
there is no 917 MHz transmission to observe and nothing to compare against 915 MHz.

**A note on scope for the compiler:** this item asks for isolation *between the project's own
two bands*. An external or ambient 917 MHz interferer would still be measurable on a receiver
alone, but `DRONE-RADIO`'s board does not answer identification, so even passive listening on
that band is unavailable until the board is repaired. That is why this stays blocked rather than
being reduced to a one-band test.

**Nothing was changed.** No config edit to either radio block, no restart, no port action.
