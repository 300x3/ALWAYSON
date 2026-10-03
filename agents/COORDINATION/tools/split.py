#!/usr/bin/env python3
"""Split README.md into agents/COORDINATION/<nn-slug>/section.md, one per section.

Lossless: compiling the parts back must reproduce README.md byte for byte.
Run from the repository root:  python3 agents/COORDINATION/tools/split.py
"""
import re, sys, pathlib

SRC = pathlib.Path("README.md")
OUT = pathlib.Path("agents/COORDINATION")
FRONT = "00-frontmatter"

def slug(t):
    t = re.sub(r'^#+\s*', '', t)
    t = re.sub(r'^\d+(\.\d+)*\.?\s*', '', t)
    t = re.sub(r'[^A-Za-z0-9 ]+', ' ', t)
    return re.sub(r'\s+', '-', t.strip().lower())

def main():
    lines = SRC.read_text(encoding="utf-8").split("\n")
    starts = [i for i, l in enumerate(lines)
              if re.match(r'^# \d+\. ', l) or l == "## Executive Summary"]
    parts = []
    head = "\n".join(lines[:starts[0]])
    parts.append((FRONT, "Document front matter", head))
    for n, i in enumerate(starts):
        j = starts[n + 1] if n + 1 < len(starts) else len(lines)
        body = "\n".join(lines[i:j])
        title = lines[i].lstrip("# ").strip()
        if lines[i] == "## Executive Summary":
            folder = "es-executive-summary"
        else:
            num = re.match(r'^# (\d+)\.', lines[i]).group(1)
            folder = "%02d-%s" % (int(num), slug(title))
        parts.append((folder, title, body))
    for folder, title, body in parts:
        d = OUT / folder
        d.mkdir(parents=True, exist_ok=True)
        (d / "section.md").write_text(body, encoding="utf-8")
    order = "\n".join("| `%s` | %s |" % (f, t) for f, t, _ in parts)
    (OUT / "MANIFEST.md").write_text(
        "# Section manifest\n\nOrder is fixed. The compiler concatenates these in "
        "this order to produce `README.md`.\n\n| Folder | Section heading |\n|---|---|\n"
        + order + "\n", encoding="utf-8")
    print("wrote %d section folders" % len(parts))

if __name__ == "__main__":
    main()
