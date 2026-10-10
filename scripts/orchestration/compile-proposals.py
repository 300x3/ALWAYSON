#!/usr/bin/env python3
"""Merge proposals/*.md into README section 19.2 (completed) and 19.1 (updates).

Single-writer compiler pass. Sessions never edit section 19 directly; they write
a proposal per item, and this folds them in.

  action: close      -> row moves from 19.1 to 19.2, status Implemented
  action: update     -> row stays in 19.1, detail gains the evidence
  action: keep-open  -> row stays, detail notes why it is still open
  action: new        -> NEW row appended to its group's block in 19.1

Never renumbers a work ID. Never drops a row that has no proposal.
"""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# DEPRECATED: section 19 source moved to README-ACTION_ITEMS/status-and-references.md
SEC = os.path.join(ROOT, "README-ACTION_ITEMS/status-and-references.md")
PROP = os.path.join(ROOT, "agents/COORDINATION (README UPDATES)/proposals")

def clean(x):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x)).strip()

def esc(s):
    """Escape markdown-significant chars for an HTML cell, then re-mark code."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

MARK = "<!-- proposal-applied:"

def read_props():
    out = []
    for f in sorted(glob.glob(os.path.join(PROP, "*.md"))):
        if os.path.basename(f) == "README.md":
            continue
        t = open(f, encoding="utf-8").read()
        m = re.match(r"---\n(.*?)\n---\n(.*)", t, re.S)
        if not m:
            print("  SKIP (no frontmatter): %s" % os.path.basename(f)); continue
        fm, body = m.group(1), m.group(2)
        d = {}
        ev = []
        in_ev = False
        for line in fm.split("\n"):
            if line.startswith("evidence:"):
                in_ev = True; continue
            if in_ev:
                if line.startswith("  "):
                    ev.append(line[2:]); continue
                in_ev = False
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                d[k.strip()] = v.strip()
        d["evidence"] = "\n".join(ev)
        d["body"] = body.strip()
        d["file"] = os.path.basename(f)
        out.append(d)
    return out

def main():
    props = read_props()
    if not props:
        print("no proposals"); return 0

    # Idempotence: a ledger of applied proposals. Without it, re-running the
    # compiler re-applied every update (PROGRESS text duplicated) and appended
    # a second OPS-35 row - measured: OPS-35 appeared 3 times and the PROGRESS
    # marker count went 30 -> 87 after two extra runs.
    ledger_path = os.path.join(PROP, ".applied")
    applied = set()
    if os.path.exists(ledger_path):
        applied = {l.strip() for l in open(ledger_path) if l.strip()}
    fresh = [p for p in props if p["file"] not in applied]
    skipped = [p for p in props if p["file"] in applied]
    if skipped:
        print("already applied, skipped : %d" % len(skipped))
    props = fresh
    if not props:
        print("nothing new to apply"); return 0

    t = open(SEC, encoding="utf-8").read()
    i1, i2 = t.index("## 19.1"), t.index("## 19.2")
    # BUG (line 62): was `log1, log2 = t[:i1], t[i1:i2]`, so every close/update
    # search ran against the text BEFORE 19.1, which has no rows, and the pass
    # moved 0 items while reporting nothing wrong. log1 is the 19.1 log itself;
    # head is what precedes it.
    head, log1, tail = t[:i1], t[i1:i2], t[i2:]

    closes = [p for p in props if p.get("action") == "close"]
    others = [p for p in props if p.get("action") in ("update", "keep-open")]
    news   = [p for p in props if p.get("action") == "new"]

    moved, updated = [], []
    for p in closes:
        item = p.get("item", "")
        pat = re.compile(r"<tr>\n<td valign=\"top\">%s</td>.*?</tr>" % re.escape(item), re.S)
        m = pat.search(log1)
        if not m:
            print("  WARN close %s: no 19.1 row found" % item); continue
        row = m.group(0)
        log1 = log1[:m.start()] + log1[m.end():]
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        ev = esc(p["evidence"]).replace("\n", "<br>")
        det = ('<strong>CLOSED %s.</strong> %s<br><br><strong>Evidence:</strong><br>'
               '<code>%s</code>' % (p.get("section", ""), esc(p["body"]), ev))
        newrow = ('<tr>\n<td valign="top">%s</td>\n<td valign="top">%s</td>\n'
                  '<td valign="top">%s</td>\n<td valign="top"><strong>Implemented</strong></td>\n'
                  '<td valign="top">%s</td>\n<td valign="top">%s</td>\n</tr>'
                  % (item, cells[1], cells[2], cells[4], det))
        tb = tail.index("<tbody>") + len("<tbody>")
        tail = tail[:tb] + "\n" + newrow + tail[tb:]
        moved.append(item)

    for p in others:
        item = p.get("item", "")
        pat = re.compile(r"(<td valign=\"top\">%s</td>.*?<td valign=\"top\">)(.*?)(</td>\n</tr>)" % re.escape(item), re.S)
        m = pat.search(log1)
        if not m:
            print("  WARN %s %s: no 19.1 row found" % (p.get("action"), item)); continue
        ev = esc(p["evidence"]).replace("\n", "<br>")
        add = ('<br><br><strong>%s by %s.</strong> %s<br><br><strong>Evidence:</strong><br>'
               '<code>%s</code>'
               % ("STILL OPEN" if p.get("action") == "keep-open" else "PROGRESS",
                  p.get("section", ""), esc(p["body"]), ev))
        log1 = log1[:m.start(2)] + m.group(2) + add + log1[m.end(2):]
        updated.append(item)

    for p in news:
        item = p.get("item", "")
        grp = item.split("-")[0]
        gb = re.search(r'<tr><td colspan="6"[^>]*>%s ·.*?</td></tr>' % re.escape(grp), log1, re.S)
        if not gb:
            print("  WARN new %s: group block %s not found" % (item, grp)); continue
        idx = log1.index("</tr>", gb.start()) + len("</tr>")
        row = ('<tr>\n<td valign="top">%s</td>\n<td valign="top">%s</td>\n'
               '<td valign="top"></td>\n<td valign="top"><strong>Open</strong></td>\n'
               '<td valign="top"></td>\n<td valign="top">%s</td>\n</tr>'
               % (item, esc(p.get("title", "")), esc(p["body"])))
        log1 = log1[:idx] + "\n" + row + log1[idx:]

    open(SEC, "w", encoding="utf-8").write(head + log1 + tail)
    with open(ledger_path, "a") as fh:
        for p in read_props():
            if p["file"] in {q["file"] for q in fresh}:
                fh.write(p["file"] + "\n")
    print("proposals read      : %d" % len(props))
    print("closed -> 19.2      : %d  (%s)" % (len(moved), " ".join(moved)))
    print("updated, stay in 19.1: %d" % len(updated))
    print("new rows added      : %d" % len(news))
    return 0

if __name__ == "__main__":
    sys.exit(main())
