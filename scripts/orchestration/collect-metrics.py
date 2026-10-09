#!/usr/bin/env python3
"""Snapshot 19.1 outstanding vs 19.2 completed, per work group, per hour.

Writes one JSON record per run to artifacts/dashboard/metrics/19-progress.jsonl. The dashboard
reads that file, so the line graph accumulates real history over time.

There was no history before this was added - the first record is the baseline
and the graph grows from it. It does not invent back-fill.
"""
import json, os, re, sys, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Section 19 source moved out of README.md to README-ACTION_ITEMS/status-and-references.md.
SEC = os.path.join(ROOT, "README-ACTION_ITEMS/status-and-references.md")
OUT = os.path.join(ROOT, "artifacts/dashboard/metrics/19-progress.jsonl")
GROUPS = ["PLAT", "NET", "SEC", "LEDGER", "PAY", "COMM", "FIELD", "SIM", "OPS"]

SEP = re.compile(r"^\|[\s:\-|]+\|$")

def cl(x):
    """Cell text to plain. The tracker is Markdown, so bold markers and code
    ticks have to go as well as any stray HTML tag -- `**Open**` must compare
    equal to "Open"."""
    x = re.sub(r"<[^>]+>", "", x)
    x = x.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", x).strip()

def rows(seg):
    """Six-column Markdown table rows, skipping the header and its separator.

    The tracker was HTML (`<tr>`/`<td>`) when this was written. It became
    Markdown when sections 19-20 moved to README-ACTION_ITEMS. The old HTML
    regex matched nothing against Markdown, so `rows()` returned [] and every
    run recorded open=0 done=0 for all nine groups -- which is what pinned the
    dashboard at 36% and then at 0%. Measured 2026-10-09.
    """
    out = []
    for line in seg.splitlines():
        s = line.strip()
        if not s.startswith("|") or SEP.match(s):
            continue
        c = [cl(x) for x in s.strip("|").split("|")]
        if len(c) == 6:
            out.append(c)
    return out

def main():
    t = open(SEC, encoding="utf-8").read()
    o = rows(t[t.index("## 19.1"):t.index("## 19.2")])
    d = rows(t[t.index("## 19.2"):])

    rec = {"ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "open": {}, "done": {}}
    for g in GROUPS:
        pref = g + "-"
        # an item is outstanding if it is a work ID in 19.1 with status Open
        rec["open"][g] = sum(1 for r in o
                             if re.match(r"^%s\d+$" % pref, r[0]) and r[3] == "Open")
        # completed = work ID rows in 19.2
        rec["done"][g] = sum(1 for r in d if re.match(r"^%s\d+$" % pref, r[0]))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    to, td = sum(rec["open"].values()), sum(rec["done"].values())
    print("recorded %s  open=%d done=%d total=%d" % (rec["ts"], to, td, to + td))
    return 0

if __name__ == "__main__":
    sys.exit(main())
