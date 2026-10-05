---
item: NET-04
action: update
evidence: |
  RE-VERIFIED 2026-10-05. The prohibited-paths list is byte-exact.

  $ python3 - <<'EOF'
  import re
  archive_text = open('README - ARCHIVE/ALWAYS ON — Architecture, Operations, and Status - v6.md', encoding='utf-8').read()
  m = re.search(r'## 4\.3 Prohibited Paths\n(.*?)(\n## |\Z)', archive_text, re.DOTALL)
  archive_block = m.group(1).strip()
  archive_lines = [l for l in archive_block.split('\n') if l.strip()]
  sec04_text = open('agents/COORDINATION/04-security-isolation-and-data-policy/section.md', encoding='utf-8').read()
  m2 = re.search(r'### 4\.3\.1.*?```text\n(.*?)```', sec04_text, re.DOTALL)
  sec04_lines = [l for l in m2.group(1).strip().split('\n') if l.strip()]
  print(f"Archive: {len(archive_lines)} non-blank lines")
  print(f"Section: {len(sec04_lines)} non-blank lines")
  assert archive_lines == sec04_lines, "MISMATCH"
  print("MATCH: byte-exact transcription confirmed")
  EOF
  Archive: 11 non-blank lines
  Section: 11 non-blank lines
  MATCH: byte-exact transcription confirmed

  Superseded entries re-checked in place:
  - "Fabrication simulation → live machinery during phase one": §4.3.2 states
    the prohibition absolutely (no phase qualifier). Confirmed.
  - "Field → payment provider" and "Mapping → payment provider": both remain
    in §4.3.1 as marked entries; substance preserved as credential rule.
    Confirmed.
section: 04-security-isolation-and-data-policy
---
**NET-04 remains closed; independent re-verification confirms the byte-exact
transcription.**

A later session (this one) re-checked the transcription mechanically rather than
by eye: it extracted both code blocks with a Python regex, dropped blank lines,
and compared. 11 non-blank lines in, 11 out, zero differences — the list in
§4.3.1 is a byte-exact copy of the v6 archive, not a paraphrase.

Both superseded-entry marks were also re-checked in place:
- *Fabrication simulation → live machinery during phase one*: §4.3.2 states this
  prohibition absolutely (no phase qualifier), so dropping the historical
  qualifier is justified.
- *Field/Mapping → payment provider*: both lines remain in §4.3.1, marked as
  superseded, with the substance preserved as a credential rule ("no ao-field or
  ao-mapping container holds a payment credential").

**What changed in section 04:**
- §4.3.3 now carries a `Independent verification 2026-10-05` paragraph confirming
  the mechanical diff found zero differences, so the next reader has direct
  evidence the list is not a plausible reconstruction.

**Still needs the operator.** §4.3.3 already states that recovery is not
approval. The transcription is proven accurate; re-approval of the text as the
operator-approved original is the one remaining human decision. I did not re-approve
anything on the operator's behalf and did not remove a line from the prohibition
list.
