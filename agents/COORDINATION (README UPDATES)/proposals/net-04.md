---
item: NET-04
action: close
evidence: |
  grep -n -A 12 '^## 4.3' agents/COORDINATION\ \(README\ UPDATES\)/04-security-isolation-and-data-policy/section.md
  -> shows rebuilt prohibited-paths list (sim-to-live, cross-isolation, external-device) not a duplicate diagram.
section: 04-security-isolation-and-data-policy
---
Rebuilt §4.3 from prohibitions elsewhere in section.md; original sale-chain content lost with misplacement noted. Confirmed list includes sim-to-live, cross-isolation, external-device paths. No secret or live-change issued.
