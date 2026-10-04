#!/usr/bin/env python3
"""Render artifacts/dashboard/index.html from artifacts/dashboard/metrics/19-progress.jsonl.

Table = current outstanding vs completed per work group.
Graph  = that split over time, one line per group for each of open/completed.

History only exists from when collect-metrics.py started running. With a single
record the graph has one point and says so, rather than drawing a flat line
that implies a measured trend.
"""
import json, os, html, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "artifacts/dashboard/metrics/19-progress.jsonl")
OUT = os.path.join(ROOT, "artifacts/dashboard/index.html")
GROUPS = ["PLAT", "NET", "SEC", "LEDGER", "PAY", "COMM", "FIELD", "SIM", "OPS"]
COL = {"PLAT": "#4c78a8", "NET": "#f58518", "SEC": "#e45756", "LEDGER": "#72b7b2",
       "PAY": "#54a24b", "COMM": "#eeca3b", "FIELD": "#b279a2", "SIM": "#ff9da6",
       "OPS": "#9d755d"}

def load():
    recs = []
    if os.path.exists(SRC):
        for line in open(SRC, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    recs.append(json.loads(line))
                except ValueError:
                    pass
    recs.sort(key=lambda r: r["ts"])
    # collapse to one record per hour (keep the latest in each hour)
    byhour = {}
    for r in recs:
        h = r["ts"][:13]
        byhour[h] = r
    return [byhour[k] for k in sorted(byhour)]

def series(recs, kind, g):
    return [r[kind][g] for r in recs]

def main():
    recs = load()
    if not recs:
        print("no metrics recorded yet"); return 1
    last = recs[-1]
    to = sum(last["open"].values()); td = sum(last["done"].values())
    when = last["ts"][:16].replace("T", " ")

    rows = []
    for g in GROUPS:
        o, d = last["open"][g], last["done"][g]
        tot = o + d
        pct = (100.0 * d / tot) if tot else 0
        bar = '<div class="bar"><i style="width:%.0f%%"></i></div>' % pct
        rows.append(
            "<tr><td class=g><span class=sw style='background:%s'></span>%s</td>"
            "<td class=n>%d</td><td class=n>%d</td><td class=n>%d</td>"
            "<td class=w>%.0f%%%s</td><td class=n>%d</td></tr>"
            % (COL[g], g, o, d, tot, pct, bar, tot))
    rows.append(
        "<tr class=tot><td class=g>TOTAL</td><td class=n>%d</td><td class=n>%d</td>"
        "<td class=n>%d</td><td class=w></td><td class=n>%d</td></tr>"
        % (to, td, to + td, to + td))

    # ---- graph ----
    W, H, PL, PR, PT, PB = 1180, 480, 60, 150, 28, 46
    iw, ih = W - PL - PR, H - PT - PB
    n = len(recs)
    maxv = max([max(r["open"].values()) for r in recs] +
               [max(r["done"].values()) for r in recs] + [1])
    maxv = max(5, int(maxv * 1.15))

    def X(i): return PL + (iw * i / max(1, n - 1)) if n > 1 else PL + iw / 2
    def Y(v): return PT + ih - (ih * v / maxv)

    svg = ['<svg viewBox="0 0 %d %d" class="svg">' % (W, H)]
    # gridlines + y axis
    for k in range(0, maxv + 1, max(1, maxv // 5)):
        y = Y(k)
        svg.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" class="grid"/>' % (PL, y, PL + iw, y))
        svg.append('<text x="%d" y="%.1f" class="ax" text-anchor="end">%d</text>' % (PL - 8, y + 4, k))
    # x labels (first, last, and a few between)
    idx = sorted(set([0, n - 1] + [round(i * (n - 1) / 4) for i in range(5)])) if n > 1 else [0]
    for i in idx:
        lab = recs[i]["ts"][11:16]
        svg.append('<text x="%.1f" y="%d" class="ax" text-anchor="middle">%s</text>'
                   % (X(i), PT + ih + 20, lab))
    svg.append('<text x="%d" y="%d" class="axt">items per work group</text>' % (PL, H - 8))
    svg.append('<text x="%.1f" y="%.1f" class="ttl">outstanding vs completed over time'
               '</text>' % (PL + iw / 2, 18))

    for kind, dash, op in (("open", "6 3", 0.95), ("done", "", 1.0)):
        for g in GROUPS:
            pts = " ".join("%.1f,%.1f" % (X(i), Y(v)) for i, v in enumerate(series(recs, kind, g)))
            if n == 1:
                svg.append('<circle cx="%.1f" cy="%.1f" r="4" fill="%s" opacity="%.2f"/>'
                           % (X(0), Y(series(recs, kind, g)[0]), COL[g], op))
            else:
                svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" '
                           'opacity="%.2f"%s/>'
                           % (pts, COL[g], op, ' stroke-dasharray="%s"' % dash if dash else ""))
                svg.append('<circle cx="%.1f" cy="%.1f" r="3.2" fill="%s"/>'
                           % (X(n - 1), Y(series(recs, kind, g)[-1]), COL[g]))

    # legend - 9 groups then the two line-style keys, spaced so nothing
    # overlaps: a previous version put the keys at fixed +68/+84 offsets while
    # the group list ran to +120, so COMM/FIELD printed through them.
    lx = PL + iw + 16
    ly = PT + 6
    PITCH = 14
    for i, g in enumerate(GROUPS):
        yy = ly + i * PITCH
        svg.append('<rect x="%d" y="%d" width="11" height="3" fill="%s"/>' % (lx, yy - 4, COL[g]))
        svg.append('<text x="%d" y="%d" class="lg">%s</text>' % (lx + 15, yy, g))
    ky = ly + len(GROUPS) * PITCH + 10
    svg.append('<line x1="%d" y1="%d" x2="%d" y2="%d" class="k" stroke-dasharray="6 3"/>'
               % (lx, ky, lx + 11, ky))
    svg.append('<text x="%d" y="%d" class="lg">dashed = outstanding</text>' % (lx + 15, ky + 4))
    svg.append('<line x1="%d" y1="%d" x2="%d" y2="%d" class="k"/>' % (lx, ky + 18, lx + 11, ky + 18))
    svg.append('<text x="%d" y="%d" class="lg">solid = completed</text>' % (lx + 15, ky + 22))
    svg.append("</svg>")
    graph = "".join(svg)

    hist = ("history: %d hourly record%s%s" % (n, "" if n == 1 else "s",
            " — the graph fills in as the hourly job runs"
            if n == 1 else ""))

    PAGE = """<!doctype html><html lang=en><meta charset=utf-8>
<title>ALWAYS ON - section 19 progress</title><style>
*{box-sizing:border-box}
body{margin:0;background:#f6f7f9;color:#1b1f24;font:14px/1.45 "DejaVu Sans",system-ui,sans-serif}
.wrap{padding:18px 22px}
h1{font-size:19px;margin:0 0 2px}
.sub{color:#5b6472;font-size:12.5px;margin-bottom:14px}
.cards{display:flex;gap:12px;margin-bottom:14px}
.card{background:#fff;border:1px solid #dfe3e8;border-radius:8px;padding:10px 16px;min-width:150px}
.card .k{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:#6b7280}
.card .v{font-size:27px;font-weight:600;line-height:1.15}
.card.o .v{color:#b45309}.card.d .v{color:#15803d}
.panel{background:#fff;border:1px solid #dfe3e8;border-radius:8px;padding:14px 16px;margin-bottom:14px}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{padding:6px 9px;text-align:left;border-bottom:1px solid #eef0f3}
th{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:#6b7280;font-weight:600}
td.n{text-align:right;font-variant-numeric:tabular-nums;width:84px}
td.w{width:170px;white-space:nowrap}
td.g{font-weight:600}
tr.tot td{border-top:2px solid #dfe3e8;font-weight:700;background:#fafbfc}
.sw{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:7px}
.bar{background:#e8ebef;height:7px;border-radius:4px;overflow:hidden;margin-top:5px}
.bar i{display:block;height:100%;background:#15803d}
.svg{width:100%;height:auto}
.grid{stroke:#eceff3;stroke-width:1}
.ax{fill:#8b95a3;font-size:11px}
.axt{fill:#8b95a3;font-size:11px}
.ttl{fill:#1b1f24;font-size:13px;font-weight:600}
.lg{fill:#5b6472;font-size:11px}
.k{stroke:#9aa3b0;stroke-width:2}
.note{color:#6b7280;font-size:12px;margin-top:8px}
</style><div class=wrap>
<h1>ALWAYS ON &mdash; section 19 work items</h1>
<div class=sub>outstanding (19.1) vs completed (19.2) per work group &middot; snapshot @WHEN@ UTC</div>
<div class=cards>
 <div class="card o"><div class=k>Outstanding</div><div class=v>@OPEN@</div></div>
 <div class="card d"><div class=k>Completed</div><div class=v>@DONE@</div></div>
 <div class=card><div class=k>Total items</div><div class=v>@TOTAL@</div></div>
 <div class=card><div class=k>Completed</div><div class=v>@PCT@%</div></div>
</div>
<div class=panel><table>
<thead><tr><th>Work group</th><th>Outstanding</th><th>Completed</th><th>Total</th>
<th>Done</th><th>Items</th></tr></thead><tbody>@ROWS@</tbody></table></div>
<div class=panel>@GRAPH@<div class=note>@HIST@</div></div>
</div></html>"""
    # Token substitution, not %-formatting: the stylesheet is full of literal
    # % and {} which %-formatting and str.format both mangle.
    page = (PAGE
            .replace("@WHEN@", when)
            .replace("@OPEN@", str(to))
            .replace("@DONE@", str(td))
            .replace("@TOTAL@", str(to + td))
            .replace("@PCT@", str(int(100.0 * td / (to + td)) if (to + td) else 0))
            .replace("@ROWS@", "".join(rows))
            .replace("@GRAPH@", graph)
            .replace("@HIST@", hist))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(page)
    print("wrote %s  (open=%d done=%d, %d record(s))" % (OUT, to, td, n))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
