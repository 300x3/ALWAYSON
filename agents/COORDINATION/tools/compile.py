#!/usr/bin/env python3
"""Rebuild README.md from agents/COORDINATION/<nn-slug>/section.md.

Verifies the result is byte-identical to what split.py last produced.
Run from the repository root:  python3 agents/COORDINATION/tools/compile.py [--check]
"""
import sys, pathlib, re

OUT = pathlib.Path("agents/COORDINATION")

def main():
    check = "--check" in sys.argv
    rows = re.findall(r'^\| `([^`]+)` \|', (OUT / "MANIFEST.md").read_text(encoding="utf-8"), re.M)
    parts = [(OUT / r / "section.md").read_text(encoding="utf-8") for r in rows]
    text = "\n".join(parts)
    if not text.endswith("\n"):
        text += "\n"
    cur = pathlib.Path("README.md")
    if check:
        same = cur.read_text(encoding="utf-8") == text
        print("identical" if same else "DIFFERS")
        sys.exit(0 if same else 1)
    cur.write_text(text, encoding="utf-8")
    print("wrote README.md from %d sections" % len(parts))

if __name__ == "__main__":
    main()
