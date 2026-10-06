---
item: FIELD-14
action: update
evidence: |
  # Re-verified 2026-10-05: the profiles are still substantively identical.
  # Re-read from the live tree, not from the previous pass's notes.
  $ cd /ALWAYSON
  $ diff <(tail -n +2 config/field/heltec-v3/radio-profile-us915.yaml) \
         <(tail -n +2 config/drone/waveshare-lora/radio-profile-us915.yaml)
  (no output -- identical except line 1, the comment)
  $ head -1 config/field/heltec-v3/radio-profile-us915.yaml
  # Heltec WiFi LoRa 32 V3 - desktop gateway profile
  $ head -1 config/drone/waveshare-lora/radio-profile-us915.yaml
  # Waveshare SX1262 LoRa HAT - drone-side profile (must interop with heltec-v3 profile)

  # Every radio field still matches, and neither declares a frequency:
  $ grep -hE 'bandwidth_khz|spreading_factor|tx_power_dbm|sync_word|encryption_key_id|device_identity|^  frequency:' \
      config/field/heltec-v3/radio-profile-us915.yaml config/drone/waveshare-lora/radio-profile-us915.yaml | sort -u
  bandwidth_khz: 125
  spreading_factor: 10
  tx_power_dbm: 20
  sync_word: 0x12
  encryption_key_id: "REPLACE_WITH_KEY_ID"
  device_identity: "REPLACE_WITH_DEVICE_PUBLIC_ID"
  (no output line for '^  frequency:' -- neither file declares a frequency;
   note frequency_plan is the plan NAME, not a channel frequency)

  # The LIVE radios still differ, and the live config is the real authority:
  $ grep -A8 '\[\[PEOPLE-RADIO\]\]' ~/.reticulum/config | grep -E 'frequency|bandwidth|spread'
  frequency = 915000000 / bandwidth = 125000 / spreadingfactor = 7
  $ grep -A9 '\[\[DRONE-RADIO\]\]' ~/.reticulum/config | grep -E 'frequency|bandwidth|spread'
  frequency = 917000000 / bandwidth = 250000 / spreadingfactor = 7
section: 09-field-and-lora-architecture
---

**Supersedes:** this file revises the FIELD session's own earlier proposal of this path,
rewritten 2026-10-05 08:12 PDT. The earlier revision was never merged into §19.2, so the
compiler should take this version as the only FIELD proposal for this item.

**FIELD-14 stays OPEN, action `update`.** §9.4.1 and §9.5.10 now record the re-verification.

Nothing has changed: the two profiles still match on every radio field, still declare **no
frequency at all**, and still carry placeholder identity and key fields. Both still say 125 kHz
/ SF10 / 20 dBm while the live radios run SF7 at 17 dBm and differ from each other by 2 MHz and
125 kHz of bandwidth.

**The item's premise from the previous pass still holds and I re-checked rather than trusting
it:** `version-matrix.yaml` has no radio, LoRa or field key, so the conflict to reconcile is
profile-versus-live-config, not profile-versus-matrix. Anyone "reconciling against the matrix"
would be reconciling against a file that says nothing about radios.

**Why this still cannot be closed by me, stated plainly.** §9.4's acceptance conditions require a
different frequency and a unique device identity per profile. Writing those values means
choosing the sync word, key ID and device identity for two radios — that is radio configuration
and it interacts with the encryption key material, which is on the operator-approval stop list.
A profile file naming frequencies is also only documentation until it is loaded onto hardware,
and the `DRONE-RADIO` board does not currently accept configuration at all. So the honest state
is: **the defect is confirmed and specified, and the fix needs an operator decision on key
material plus a working `DRONE-RADIO` board.**

**No profile file was edited.** No frequency, sync word, key ID or identity was invented.
