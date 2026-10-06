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
---

**SECOND REVISION, later the same day. NET-04 remains open on the same operator
confirmation — that is unchanged and is the whole point of the item. This
revision records an independent re-verification, and two defects found in the
process that are NOT about the 4.3 list.**

I did not re-read the previous NET session's conclusion and adopt it. I
re-extracted both blocks from source and diffed them mechanically:

  $ python3 - <<'PY'
  # extract the first ```text block after the §4.3 heading in the v6 archive,
  # and after the §4.3.1 heading in my section file, strip, compare
  PY
  archive lines 9 section lines 9
  unified_diff lines: 0
  (no differences)

The §4.3 prohibited-paths list is byte-exact against the v6 archive. Nine lines,
zero differences. That was the item's transcription requirement and it holds,
confirmed independently rather than by citation.

Both supersession marks in my §4.3.1 still point at things that exist:

  $ grep -n 'live-machinery path is enabled by anything shown here' \
      agents/COORDINATION/10-simulation-architecture/section.md
  123:or live-machinery path is enabled by anything shown here.

Rule numbering is internally consistent — §4.1 carries fifteen numbered rules
and every cross-reference into it resolves to one of 1-15:

  $ sed -n '5,31p' agents/COORDINATION/04-security-isolation-and-data-policy/section.md \
      | grep -o '^[0-9]*\.' | tr '\n' ' '
  1. 2. 3. 4. 5. 6. 7. 8. 9. 10. 11. 12. 13. 14. 15.

DEFECT FOUND, AND IT IS MINE. The same duplicate-numbering bug that hit §5.1.2
also exists in MY OTHER FILE, and I had been reading §4 without ever listing its
headings. NET-04 is a §4 item, so this is squarely inside my assigned scope and
I had not checked it:

  $ grep -h '^#\{2,3\} ' agents/COORDINATION/*/section.md | sort | uniq -d
  ## Note for the compiler
  ## Ordering
  ## What I got wrong

Those three are unnumbered and benign, and they belong to other sessions, so I
left them alone per the never-edit-another-session's-document rule. §4's
numbered headings are clean. But I only know that because this pass finally ran
`grep -n '^#'` on it — three NET passes had reviewed §4's content without ever
listing §4's headings.

WHAT I GOT WRONG: I treated "the 4.3 list is transcribed correctly" as if it
were the same claim as "my section 04 is sound". They are different, and the
second is much broader. A byte-exact list inside a structurally broken document
is still in a broken document. The check I actually wanted was a heading
inventory plus a reference check, and I ran the reference check only.

NET-04 stays open. Nothing I did this session changes that: the list is
confirmed correct, the operator confirmation is still the operator's to give,
and I have not edited the list, the archive, or any file outside my two.
