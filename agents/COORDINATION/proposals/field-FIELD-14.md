---
item: FIELD-14
action: update
evidence: |
  $ diff -u config/field/heltec-v3/radio-profile-us915.yaml \
            config/drone/waveshare-lora/radio-profile-us915.yaml
  @@ -1,4 +1,4 @@
  -# Heltec WiFi LoRa 32 V3 - desktop gateway profile
  +# Waveshare SX1262 LoRa HAT - drone-side profile (must interop with heltec-v3 profile)
   radio_profile:
     region: US915
     frequency_plan: "US915 hybrid-channel raw LoRa (NOT LoRaWAN)"
  diff-rc=1        # only the first-line comment differs

  # FIELD-14 blames version-matrix.yaml; it contains no radio/LoRa/field key AT ALL
  $ grep -cn -i 'radio\|lora\|field' config/platform/version-matrix.yaml
  0
  $ grep -n '^[a-z_]*:' config/platform/version-matrix.yaml
  1:host:  11:gpu:  17:mapping:  27:simulation:  39:sales:  53:operations:  65:ledger:

  # the real third opinion is the LIVE Reticulum config
  $ grep -A12 'RNodeInterface' ~/.reticulum/config
  frequency = 915000000   bandwidth = 125000   spreadingfactor = 7   codingrate = 5   txpower = 17
  frequency = 917000000   bandwidth = 250000   spreadingfactor = 7   codingrate = 5   txpower = 17
  mode = internal
section: 09-field-and-lora-architecture
---
**FIELD-14 stays OPEN, action `update`.** §9.4.1 now records the measured profile state. The
profiles genuinely are substantively identical, so the item's core concern is confirmed — but
**its stated evidence is wrong, and correcting that changes what the fix actually is.**

**Correction to the item's premise.** FIELD-14 says the profiles "also disagree with
`version-matrix.yaml`: profiles say 125 kHz and spreading factor 10, the matrix and §9.2.1 say
250 kHz and spreading factor 7". The matrix is **not a third opinion — it is silent.** It has
zero radio/LoRa/field keys and its only top-level keys are `host, gpu, mapping, simulation,
sales, operations, ledger`. Anyone fixing this by reconciling against the matrix would be
reconciling against a file that says nothing about radios. **The real third opinion is the live
`~/.reticulum/config`**, which is the authoritative record of what is actually on the air.

| Setting | `PEOPLE-RADIO` (live) | `DRONE-RADIO` (live) | Both profiles claim |
|---|---|---|---|
| `frequency` | `915000000` | `917000000` | **not declared** |
| `bandwidth` | `125000` | `250000` | `125` |
| `spreadingfactor` | `7` | `7` | `10` |
| `codingrate` | `5` | `5` | `"4/5"` |
| `txpower` | `17` | `17` | `20` |

The 915/917 MHz split described in §9.1 and §9.2.2 is **real and enforced by the live config**
— it simply is not captured in the version-controlled profiles §9.4 nominates as the
specification. So the profiles match **neither** radio: they overstate transmit power (20 vs
live 17 dBm), understate spreading factor (SF10 vs live SF7), and omit the frequency entirely.

**Consequence for §9.4:** its acceptance conditions *"different frequency"* and *"device
identity is unique"* are unmet as written, and since the profiles declare no frequency at all,
**no profile can currently be accepted under §9.4's own rules.** That is a stronger statement
than the item made and it is now recorded.

**Severity: documentation mismatch, not a regulatory fault.** §9.4.1 computes the airtime
consequence for the profile's `max_packet_bytes: 222` at `airtime_limit_pct: 10` from the SX1262
airtime formula: profiles as written 0.1156 s (311,423 packets/hour), live `PEOPLE-RADIO`
0.0875 s (411,418/hour), live `DRONE-RADIO` 0.0438 s (822,836/hour). **The live radios are far
inside the airtime limit; the profile values are merely conservative by ~1.3x to ~2.6x.**
Nothing on air is at risk of a duty-cycle breach, so this is not urgent.

**What I got wrong — two corrections, both now in the section.**

1. **The item's premise was false and I checked it instead of repeating it.** FIELD-14 blames
   `version-matrix.yaml` for the bandwidth/SF disagreement. That file contains **no radio, LoRa
   or field key at all**. Had I trusted the item and "reconciled against the matrix", I would
   have reconciled against silence and reported a phantom conflict. The real conflict is
   profile-vs-live-config.
2. **My first airtime table was wrong and I could not reproduce it.** It read 0.240 s / 1,502
   packets/hour. When I recomputed it properly I found the estimate was off by ~2x, and my first
   re-implementation was wrong *again* because it hardcoded the 125 kHz symbol time — which made
   the 250 kHz `DRONE-RADIO` row come out identical to the 125 kHz row, an obvious internal
   contradiction I should have caught from the output alone. **Reason: I published a computed
   number whose formula I had not written down, so I could not audit it.** The numbers above now
   come with the script inline. The conclusion (not urgent) survived; the figures did not, and
   an airtime number is exactly what gets quoted into a regulatory argument later.

**I did not edit the profiles.** Writing real frequencies, sync words, key IDs and device
identities into version-controlled radio configuration, and confirming on air that
`DRONE-RADIO` carries missions only, is live radio configuration and a stop condition. The last
half of the acceptance criteria — "confirm on air" — additionally requires a flight test, which
is explicitly outside this session.

**Ready for the operator, if they approve:** the four corrected values per profile are
tabulated in §9.4.1, so the edit is prepared but unapplied.