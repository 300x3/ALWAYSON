---
item: FIELD-13
action: close
evidence: |
  # every LoRaWAN mention in the source of truth, by section
  $ grep -rc -i 'lorawan' agents/COORDINATION (README UPDATES) (README UPDATES)/*/section.md | grep -v ':0'
  agents/COORDINATION (README UPDATES) (README UPDATES)/02-platform-baseline/section.md:1
  agents/COORDINATION (README UPDATES) (README UPDATES)/09-field-and-lora-architecture/section.md:11
  agents/COORDINATION (README UPDATES) (README UPDATES)/19-current-status-and-outstanding-work/section.md:4
  agents/COORDINATION (README UPDATES) (README UPDATES)/es-executive-summary/section.md:1

  # the one contradiction outside my sections
  $ grep -n -i 'lorawan' agents/COORDINATION (README UPDATES) (README UPDATES)/es-executive-summary/section.md
  11: ... **LoRaWAN for communication only** — the public human side (§9.2.2). ...

  # §02 states the same rule correctly (compliant, no change needed)
  18:| Field protocol | RNS/Reticulum and MeshChatX over raw LoRa unless a true LoRaWAN deployment is selected |

  # both profiles already carry the compliant wording
  $ grep -n frequency_plan config/field/heltec-v3/radio-profile-us915.yaml \
      config/drone/waveshare-lora/radio-profile-us915.yaml
  frequency_plan: "US915 hybrid-channel raw LoRa (NOT LoRaWAN)"
section: 09-field-and-lora-architecture
---
§9 gains a new **§9.4.3** stating the rule the item asks for: whether RNode-over-Reticulum is
*ever* called LoRaWAN in any artefact.

**Decision: it is not. The approved wording is "raw LoRa over Reticulum (RNode), NOT LoRaWAN".**
The stack implements no LoRaWAN device, gateway or network-server architecture, so the term
does not apply to it at any layer. This is not a stylistic preference — §9.4 already forbade
describing the system as LoRaWAN unless a true device/gateway/network-server architecture
exists, and no such deployment is selected.

**Applied within the sections I own.** The rule is now written into §9.4.3, and §9.2.2's
`PEOPLE-RADIO` row was corrected to the approved wording, cross-referencing §9.4.3. That row
previously read `**LoRaWAN-related communication** … This radio is the LoRaWAN path for human
conversation.` and now reads `**Raw-LoRa human communication** … it is **not** LoRaWAN
(§9.4.3)`. Both radio profiles already carried
`frequency_plan: "US915 hybrid-channel raw LoRa (NOT LoRaWAN)"`, so no config file needed
changing.

**Two contradictions remain outside my sections. I did not edit them — they belong to their
owning sessions.** They are reported here so the compiler can route them:

| File | Line | Problem |
|---|---|---|
| `es-executive-summary/section.md` | 11 | calls `PEOPLE-RADIO` "**LoRaWAN for communication only**" — the clearest violation, and the exact one FIELD-13 was raised about |
| `19-.../section.md` | 615, 619 | FIELD-07's own title and criteria say "MeshChatX **LoRaWAN** path" and "recorded as LoRaWAN-related communication" |

`02-platform-baseline/section.md:18` mentions LoRaWAN but is **already compliant** — it says
"over raw LoRa *unless a true LoRaWAN deployment is selected*", which is the rule this item
asked to be decided. No change needed there, and I am not proposing one.

**Why FIELD-13 can close while FIELD-07 stays open.** FIELD-13 asks for a decision and
application. The decision is made, recorded in §9.4.3, and applied everywhere I own. The two
remaining occurrences sit in other sessions' files plus §19 itself, which is single-writer and
which I must not edit — so I report them instead. **The compiler should not read FIELD-13's
closure as "the word has been purged repo-wide"; it has not.**