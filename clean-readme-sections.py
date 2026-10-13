#!/usr/bin/env python3
"""Remove status/re-vision/diagnostic content from ALWAYSON section sources so the
compiled README (sections 1-16) stays prescriptive. Run from /ALWAYSON.

Two mechanisms:
  1. WHOLE_SUBSECTIONS: exact subsection heading text -> remove the entire block
     from that heading up to (not including) the next heading of the same or
     higher level. Used for dated diagnostic/verification subsections whose facts
     are already recorded in README-ACTION_ITEMS/status-and-references.md (section 19).
  2. STANDALONE: regex over a single line -> remove the paragraph that starts on
     that line, up to the next heading. Used for inline status/correction notes.
Inline corrections inside a table row are trimmed in place.

Blocks that carry genuine *normative* decisions (e.g. section 11.7 native-vs-containerised
deviation, section 8.4.1 authoritative DB, section 10.1.1 SITL method) are NOT removed
wholesale; only unambiguous progress/status/verification narrative is removed here.
"""
import re
from pathlib import Path

BASE = Path("agents/COORDINATION (README UPDATES)")

# folder -> list of heading-text prefixes. Match: heading body startswith the text.
# Block removed from this heading to the next heading whose level is <= this level.
WHOLE_SUBSECTIONS = {
    "03-high-level-architecture": [
        "3.3.1.1 How SQLite stores reach reporting",
    ],
    "04-security-isolation-and-data-policy": [
        "4.3.4 Completeness outcome of the NET-04 check",
    ],
    "06-component-boundaries-gui-reporting-tools-and-operator-access": [
        "6.A.3.1 Known staleness in that inventory",
        "6.A.3.2 Four unmanaged Grafana containers are running",
        "6.A.3.3 An unmanaged host listener serving the pCloud Public Folder",
    ],
    "07-public-storefront-and-payment-policy": [
        "7.1.3 Build state of the nine views",
        "7.2.1 Prepared verifier correction, proven offline",
        "7.3.1 Verified implementation state",
    ],
    "08-mapping-and-photogrammetry": [
        "8.5.1 Validation executed",
        "8.5.2 Why the tree cannot be repaired",
        "8.4.1 Authoritative mapping database — decided",  # duplicate of normative 8.4.1
    ],
    "09-field-and-lora-architecture": [
        "9.2.3 Bounded-ratchet persistence",
        "9.2.3.1 Classification reversed",
        "9.3.1 Listener reachability decided",
        "9.4.1 Profile state measured",
        "9.4.2 Canonical radio device-name table",
        "9.5 Measured radio link state",
    ],
    "10-simulation-architecture": [
        "10.3 Verified state, 2026-10-03",
        "10.4 Verified state, 2026-10-04",
        "10.5 SIM-09 re-opened",
        "10.6 SIM-14 is not closed",
        "10.8 Second pass:",
        "10.10 SIM-16 re-measured",
        "SIM-16 status, 2026-10-11",
        "Verified state, 2026-10-11",
        "GUI verification: a live process is not a rendered geometry",
        "A measurement whose inputs may have drifted",
        "A guard must be tested against the case it exists to catch",
        "A verification must be confirmed to have been set up",
        "The live world file is not the simulation",
        "This section's characteristic failure:",
        "10.7 SIM-15 fixed:",
        "10.9 SIM-16: the running simulation",
    ],
    "11-ledger-provenance-archive-and-ipfs": [
        "11.8 Second-Pass Verification",
        "11.9 Producer-Key Coverage Gap",
        "11.10 Third-Pass Verification",
        "11.11 Fourth-Pass Verification",
        "11.12 Fifth-Pass Verification",
        "11.13 Sixth-Pass Verification",
        "A document asserting completed state must be verified",
        "A claim in your own document is still a claim",
        "Verifying a recorded claim is worth doing once",
        "The question a specification audit must ask",
        "Ledger responsibility: integrity and provenance, not general encryption",
    ],
    "12-host-installation-and-configuration": [
        "A false FAIL is the worst kind of checker defect",
        "A number in the stage table above was wrong",
        "Check presence before reachability",
    ],
    "14-secrets-and-service-identity": [
        "The wallet entry and the env file have diverged",
        "RETRACTED 2026-10-05 (second pass)",
        "14.1.3.1 The orphaned `mastodon-env` wallet entry",
        "14.1.3.2 The Mastodon containers disagree",
        "14.1.3.3 Ordering defect in this subsection",
        "14.1.7.2 Current state 2026-10-05",
        "14.1.7 `payment.env` is a stale delivery copy",
    ],
    "15-sales-mastodon-openclaw-and-local-ai": [
        "15.4.9 Federation Contact Asymmetry",
        "15.4.10 Cloudflare Tunnel Edge Instability",
        "15.4.11 The Flap Is Local-Path",
        "15.4.12 Re-Verification Pass",
        "15.4.13 Independent Re-Verification",
        "A probe that scores a success as a failure",
    ],
    "16-scripts-and-operational-standards": [
        "16.1.2 Backup, restore and receipt executors",
    ],
}

STANDALONE = [
    re.compile(r"^\*\*Re-verification 2026-10-08 \(PLAT-0[342][^ ]*\)\.\*\*"),
    re.compile(r"^\*\*Correction 2026-10-05 —"),
    re.compile(r"^\*\*Decision \(operator, 2026-09-30\)"),
    re.compile(r"^\*\*Correction 2026-10-04 —\s*(?:the adjacent-subnet|this row previously|OpenClaw agents|browser profile)"),
    re.compile(r"^\*\*Caveat added 2026-10-04:", re.I),
    re.compile(r"^> \*\*Correction 2026-10-03 \(COMM session\)\.\*\*"),
    re.compile(r"^\*\*Correction 1 —"),
    re.compile(r"^\*\*Correction 2 —"),
    re.compile(r"^\*\*Correction 3 —"),
    re.compile(r"^\d\. \*\*Sections 1–16 stay specification"),
    re.compile(r"^\*\*Alternative [234] —"),
    re.compile(r"^\*\*Re-verified 2026"),
    re.compile(r"^\*\*Re-measured 2026"),
    re.compile(r"^\*\*Independent verification 2026"),
]


def heading_level(line):
    m = re.match(r"^(#{1,6})\s", line)
    return len(m.group(1)) if m else None


def remove_whole_subsections(lines, targets):
    """Remove blocks whose heading body startswith one of `targets`.
    Block spans from the heading to the next heading of level <= this level."""
    out = []
    i = 0
    n = len(lines)
    removed = []
    while i < n:
        line = lines[i]
        lvl = heading_level(line)
        matched = None
        if lvl is not None:
            body = line[lvl:].strip()
            for t in targets:
                if body.startswith(t):
                    matched = t
                    break
        if matched is not None:
            removed.append(line.strip())
            j = i + 1
            while j < n:
                nlvl = heading_level(lines[j])
                if nlvl is not None and nlvl <= lvl:
                    break
                j += 1
            i = j
            continue
        out.append(line)
        i += 1
    return out, removed


def remove_block(lines, i):
    n = len(lines)
    while i < n:
        if re.match(r"^#{1,4}\s", lines[i]):
            return i
        i += 1
    return i


def strip_standalone(lines):
    out = []
    i = 0
    n = len(lines)
    removed = 0
    while i < n:
        line = lines[i]
        # Inline correction inside a table row: cut the correction span.
        idx = line.find("**Correction")
        if idx != -1 and "|" in line:
            j = idx
            while j > 0 and line[j - 1] == " ":
                j -= 1
            if j > 0 and line[j - 1] == "|":
                line = line[: j - 1].rstrip()
                out.append(line)
                i += 1
                continue
        for pat in STANDALONE:
            if re.match(pat, line):
                i = remove_block(lines, i)
                removed += 1
                break
        else:
            out.append(line)
            i += 1
    return out, removed


def collapse_blanks(text):
    return re.sub(r"\n{3,}", "\n\n", text)


def process(path, targets):
    lines = path.read_text(encoding="utf-8").split("\n")
    lines, whole = remove_whole_subsections(lines, targets)
    lines, standalone = strip_standalone(lines)
    text = collapse_blanks("\n".join(lines))
    if not text.endswith("\n"):
        text += "\n"
    return text, whole, standalone


def main():
    total_whole = 0
    total_standalone = 0
    for name, targets in WHOLE_SUBSECTIONS.items():
        p = BASE / name / "section.md"
        before = p.read_text(encoding="utf-8")
        after, whole, standalone = process(p, targets)
        if after != before:
            p.write_text(after, encoding="utf-8")
        total_whole += len(whole)
        total_standalone += standalone
        print(f"{name}: -{len(whole)} subsections, -{standalone} standalone notes")
    print(f"TOTAL: -{total_whole} subsections, -{total_standalone} standalone notes")


if __name__ == "__main__":
    main()
