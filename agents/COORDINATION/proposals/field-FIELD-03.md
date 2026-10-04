---
item: FIELD-03
action: blocked
evidence: |
  # FIELD-03 wants 915/917 isolation MEASURED. One band has no transmitter on it.
  # Live config, from ~/.reticulum/config:
  #   [[PEOPLE-RADIO]] frequency = 915000000  bandwidth = 125000  spreadingfactor = 7
  #   [[DRONE-RADIO]] frequency = 917000000  bandwidth = 250000  spreadingfactor = 7

  # 917 MHz transmitter: dead. Last successful detection 2026-09-25 16:27.
  $ grep -ch 'unrecoverable error' ~/.reticulum-meshchatx/logs/meshchatx.log{,.1,.2,.3}
  994 / 7800 / 2389 / 29

  # so the 915 MHz receiver has nothing to isolate against — only ambient noise.
  # no interference events were ever logged on the band that IS up:
  $ grep -oh -E '(RSSI|rssi)[=: ]+[-0-9.]+' ~/.reticulum-meshchatx/logs/meshchatx.log* | wc -l
  0
  $ grep -c -iE 'interfer|spurio|harmonic' ~/.reticulum-meshchatx/logs/meshchatx.log*
  0 0 0 0
section: 09-field-and-lora-architecture
---
**FIELD-03 stays OPEN — action `blocked`.** Recorded in the new §9.5.4 in §9.

The criteria require 915/917 isolation to be **measured** and the interference classified as
in-band, adjacent-band, harmonic or spurious. **Isolation is a two-source measurement, and
there is currently only one source.** The 917 MHz transmitter (`DRONE-RADIO`) has not come
up since 2026-09-25 16:27, so the healthy 915 MHz radio is only ever hearing ambient noise.
An ambient noise floor is not an isolation figure, and calling it one would be the specific
error this item exists to prevent.

I want to be explicit about the trap here, because it is an attractive one. It would have
been easy to report "915 MHz shows no interference events in the logs, therefore
cross-band isolation is good." That conclusion is **unsupported**: absence of interference
events in a log is not evidence of isolation when the interfering transmitter is switched
off. The correct reading is that the measurement is *impossible right now*, not that it
returned a good result. The four-way classification the criteria ask for cannot be performed
at all.

The frequency split itself is real and correctly configured — `915000000` and `917000000`
in the live `~/.reticulum/config`, which is what §9.1 and §9.2.2 describe. Configuration
agreement is not measurement, and is not offered here as a substitute.

**What I got wrong, and the reason.** This item did not mislead me, so the honest report is
narrower: I initially treated "FIELD-03 is about interference" and reached for a log grep of
interference words as the primary evidence. **Reason: I let the item's title pick my
method.** The acceptance criteria are about *isolation between two live transmitters*, which
is a different measurement from *interference events on one receiver*. Reading the criteria
before choosing the evidence would have saved the detour — and note this is the same class
of mistake I made on FIELD-01, which is worth the compiler knowing: **twice this session I
picked a method from a title instead of from the criteria.**