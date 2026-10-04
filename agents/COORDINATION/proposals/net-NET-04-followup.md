---
item: NET-04
action: update
evidence: |
  FOLLOW-UP to net-NET-04.md, which I have not modified. NET-04 REMAINS OPEN,
  blocked on the operator, not on me. This records independent verification that
  the recovered list is a faithful transcription - a check the earlier session
  asserted but, as far as I can see, did not perform as a mechanical comparison.

  I diffed my section 4.3.1 code block against the archived v6 "## 4.3
  Prohibited Paths" block directly, rather than reading both and judging them
  equal:

  $ python3 - <<'EOF'   # extract both ```text blocks, drop blanks, diff
  ...
  EOF
  archive lines 9 section lines 9
  (unified_diff produced no output)

  So the transcription is byte-exact: 9 lines in, 9 lines out, zero differences.
  Whatever the operator decides about approval, the list in 4.3.1 is not a
  paraphrase or a reconstruction - it is the archived text.

  I also checked the two claimed supersessions rather than taking them on trust:

  - *Fabrication simulation -> live machinery during phase one* is claimed
    superseded because the prohibition is now absolute. Confirmed present in my
    own 4.3.2, unqualified:
      86:| Simulation domain to live machinery | A rehearsal must never command
         a real machine, a real robot arm, or a live flight controller |
         Rule 12, 10.2 |

  - *Field/Mapping -> payment provider* is claimed superseded by the controlled
    adapters in 5.2. Both lines are retained verbatim in 4.3.1 and marked, and
    the substance holds: the prohibition is restated as "no ao-field or ao-mapping
    container holds a payment credential".

  Neither is deleted. The marks are accurate.
section: 04-security-isolation-and-data-policy
---
**NET-04 still needs the operator, and nothing I did this session changes
that. What I added is proof that the recovered list is a faithful
transcription.**

The earlier session recovered the eight prohibition lines from the v6 archive and
marked two entries as superseded. I have verified both claims mechanically
rather than by reading:

- The list in §4.3.1 is byte-identical to the archived v6 block — nine lines in,
  nine lines out, empty diff. It is not a paraphrase or a plausible
  reconstruction, so the only question left about it is approval, not accuracy.
- Both supersession marks are accurate. The *Fabrication simulation → live
  machinery* prohibition is stated absolutely in §4.3.2, so dropping the
  historical "during phase one" qualifier is justified. The *Field/Mapping →
  payment provider* entries remain in the list and are marked, with the
  substance preserved as a credential rule rather than a routing rule, which is
  the correct reading now that payment is reached through the controlled
  adapters.

I did not re-approve anything on the operator's behalf and I did not remove a
line from a prohibition list. §4.3.3 already states that recovery is not
approval, and that remains the one open question on this item. If the operator
confirms the recovered list as the approved original, NET-04 closes with nothing
further; if they have a different original in mind, §4.3.1 is where the
correction goes.