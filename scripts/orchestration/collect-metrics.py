#!/usr/bin/env python3
"""Snapshot 19.1 outstanding vs 19.2 completed, per work group, per hour.

Writes one JSON record per run to artifacts/dashboard/metrics/19-progress.jsonl. The dashboard
reads that file, so the line graph accumulates real history over time.

There was no history before this was added - the first record is the baseline
and the graph grows from it. It does not invent back-fill.
"""
import json, os, re, sys, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEC = os.path.join(ROOT, "agents/COORDINATION (README UPDATES)/19-current-status-and-outstanding-work/section.md")
OUT = os.path.join(ROOT, "artifacts/dashboard/metrics/19-progress.jsonl")
GROUPS = ["PLAT", "NET", "SEC", "LEDGER", "PAY", "COMM", "FIELD", "SIM", "OPS"]

def cl(x):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x)).strip()

def rows(seg):
    out = []
    for r in seg.split("<tr>"):
        c = [cl(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
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
