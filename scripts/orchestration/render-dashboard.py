#!/usr/bin/env python3
"""Render artifacts/dashboard/index.html from artifacts/dashboard/metrics/19-progress.jsonl.

Table = current outstanding vs completed per work group.
Graph  = that split over time, one line per group for each of open/completed.

History only exists from when collect-metrics.py started running. With a single
record the graph has one point and says so, rather than drawing a flat line
that implies a measured trend.
"""
import json, os, re, html, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "artifacts/dashboard/metrics/19-progress.jsonl")
OUT = os.path.join(ROOT, "artifacts/dashboard/index.html")
GROUPS = ["PLAT", "NET", "SEC", "LEDGER", "PAY", "COMM", "FIELD", "SIM", "OPS"]
COL = {"PLAT": "#4c78a8", "NET": "#f58518", "SEC": "#e45756", "LEDGER": "#72b7b2",
       "PAY": "#54a24b", "COMM": "#eeca3b", "FIELD": "#b279a2", "SIM": "#ff9da6",
       "OPS": "#9d755d"}

# Items that cannot proceed without an operator decision. Kept here as data so
# the dashboard derives the questions from the log instead of maintaining a
# separate list that drifts.
DECISIONS = {
 "PLAT-02":  "Approve the version-matrix refresh scope, or defer it?",
 "NET-01":   "Enable ao-build-update egress, or keep it scaffolded and disabled?",
 "SEC-01":   "Migrate the three databases to Podman secrets / systemd credentials, "
             "or record an approved deviation with compensating controls?",
 "SEC-02":   "Record the env-file secret-delivery deviation, or migrate? "
             "(also closes the ~/secrets/fabrication-db.env noted in ST-30)",
 "LEDGER-01": "Perform the Corda key/certificate ceremony, or defer the ledger?",
 "LEDGER-02": "Build Corda 5 against PostgreSQL 18 - approve the build?",
 "LEDGER-03": "Define the approved-signed-data test for ingest, and who signs?",
 "LEDGER-04": "pCloud archive credentials - provision, or defer off-site archiving?",
 "LEDGER-07": "Build the Corda node now, or leave the ledger non-production?",
 "PAY-01":   "Provision payment credentials into KDE Wallet ao-payment?",
 "PAY-02":   "Approve the payment verifier and normalized event model before build?",
 "PAY-05":   "Ship live HTML views for product modals, or keep static?",
 "COMM-01":  "Approve the Mastodon configuration drift reconciliation (D1-D9)?",
 "COMM-05":  "300x3.com has no MX - set mail routing, or accept undeliverable mail?",
 "COMM-06":  "Bootstrap discovery for remote servers - approve the mechanism?",
 "COMM-07":  "Publish publicly: directory submission and live round trips?",
 "SIM-01":   "Set the DDS/Gazebo GUI policy - which clients may connect?",
 "SIM-07":   "ROS 2 package source is unreachable over TLS - mirror, or work around?",
 "SIM-08":   "Publish the Gazebo viewer at www.300x3.com?",
 "OPS-01":   "Metabase: approve the persistence schema and first read-only query?",
 "OPS-07":   "One canonical journal root - which path wins?",
 "OPS-09":   "Approve the restic path set covering every data class?",
 "OPS-11":   "Set alerting thresholds, or accept silent failure?",
 "OPS-13":   "Enable and verify linger (needs a reboot-free change)?",
 "OPS-14":   "Reconcile the Podman store model - rootless single-store, or mixed?",
 "OPS-16":   "Clean up stray simulation containers and world backups in the tree?",
 "OPS-24":   "Approve an isolated restore-test path so the restore drill can run?",
 "OPS-28":   "Prometheus is on a loopback port any local process can query - bind policy?",
 "OPS-30":   "Off-site restic repository: provision, or accept no off-site copy?",
 "OPS-31":   "Backup shares a filesystem with its data - move to separate media?",
 "OPS-29":   "(duplicate of OPS-30 - same question, closing one closes both)",
}

ANSWERS_PATH = os.path.join(ROOT, "artifacts/dashboard/answers.json")
CLAR_PATH = os.path.join(ROOT, "artifacts/dashboard/clarifications.json")
STATE_PATH = os.path.join(ROOT, "artifacts/dashboard/decision-state.json")
UPDATES_PATH = os.path.join(ROOT, "artifacts/dashboard/updates.jsonl")

def load_updates(limit=40):
    """Progress notes the team posts, newest first.

    This is the dashboard's standing channel for REGULAR UPDATES, as distinct
    from the "Decisions needed from you" panel below it, which is only for
    things blocked on the operator. It is append-only JSONL so a note cannot be
    lost by a concurrent write, and it is capped on read so the file cannot
    grow without bound.

    Written by scripts/orchestration/dashboard-note.py, which is what an agent
    or the coordinator calls to report progress.
    """
    out = []
    if os.path.exists(UPDATES_PATH):
        for line in open(UPDATES_PATH, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    out.sort(key=lambda r: r.get("ts", ""), reverse=True)
    return out[:limit]

def load_state():
    """Which decisions still need the operator. An answer that is sufficient to act
    on removes the item from the list; only unanswered or operator-action items stay."""
    if os.path.exists(STATE_PATH):
        try:
            d = json.load(open(STATE_PATH, encoding="utf-8"))
            return d.get("needs_action", {}), set(d.get("answered", []))
        except ValueError:
            return {}, set()
    return {}, set()

NEEDS_ACTION, ANSWERED = load_state()

def load_clarifications():
    """Items where the operator's answer is ambiguous, asks me a question back,
    or contradicts another answer. Rendered highlighted with a reworded question."""
    if os.path.exists(CLAR_PATH):
        try:
            return json.load(open(CLAR_PATH, encoding="utf-8")).get("items", {})
        except ValueError:
            return {}
    return {}

CLAR = load_clarifications()

def load_answers():
    if os.path.exists(ANSWERS_PATH):
        try:
            return json.load(open(ANSWERS_PATH, encoding="utf-8"))
        except ValueError:
            return {}
    return {}

ANSWERS = load_answers()

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
    # One line per work group, plotting PERCENT COMPLETED. The previous
    # version drew two lines per group (absolute open + absolute done); the
    # operator asked for % completed only. Percent also makes groups of very
    # different sizes directly comparable, which absolute counts were not:
    # OPS has 38 items and NET has 4, so on a count axis OPS always dominated.
    W, H, PL, PR, PT, PB = 1180, 480, 60, 110, 28, 46
    iw, ih = W - PL - PR, H - PT - PB
    n = len(recs)
    maxv = 100

    def X(i): return PL + (iw * i / max(1, n - 1)) if n > 1 else PL + iw / 2
    def Y(v): return PT + ih - (ih * v / maxv)

    def pct_series(g):
        out = []
        for r in recs:
            o, d = r["open"][g], r["done"][g]
            tot = o + d
            out.append(100.0 * d / tot if tot else 0.0)
        return out

    svg = ['<svg viewBox="0 0 %d %d" class="svg">' % (W, H)]
    # gridlines every 10%, labelled
    for k in range(0, 101, 10):
        y = Y(k)
        svg.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" class="grid"/>' % (PL, y, PL + iw, y))
        svg.append('<text x="%d" y="%.1f" class="ax" text-anchor="end">%d%%</text>' % (PL - 8, y + 4, k))
    idx = sorted(set([0, n - 1] + [round(i * (n - 1) / 4) for i in range(5)])) if n > 1 else [0]
    for i in idx:
        lab = recs[i]["ts"][11:16]
        svg.append('<text x="%.1f" y="%d" class="ax" text-anchor="middle">%s</text>'
                   % (X(i), PT + ih + 20, lab))
    svg.append('<text x="%d" y="%d" class="axt">%% completed per work group</text>' % (PL, H - 8))
    svg.append('<text x="%.1f" y="%.1f" class="ttl">percent completed over time</text>'
               % (PL + iw / 2, 18))

    for g in GROUPS:
        ser = pct_series(g)
        pts = " ".join("%.1f,%.1f" % (X(i), Y(v)) for i, v in enumerate(ser))
        if n == 1:
            svg.append('<circle cx="%.1f" cy="%.1f" r="4" fill="%s"/>' % (X(0), Y(ser[0]), COL[g]))
        else:
            svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>'
                       % (pts, COL[g]))
        # label the current value at the right-hand end so the graph is
        # readable without cross-referencing the table above it
        svg.append('<circle cx="%.1f" cy="%.1f" r="3.2" fill="%s"/>' % (X(n - 1), Y(ser[-1]), COL[g]))
        svg.append('<text x="%.1f" y="%.1f" class="ax" text-anchor="end" fill="%s">%.0f%%</text>'
                   % (X(n - 1) - 6, Y(ser[-1]) - 5, COL[g], ser[-1]))

    lx = PL + iw + 16
    ly = PT + 6
    PITCH = 14
    for i, g in enumerate(GROUPS):
        yy = ly + i * PITCH
        svg.append('<rect x="%d" y="%d" width="11" height="3" fill="%s"/>' % (lx, yy - 4, COL[g]))
        svg.append('<text x="%d" y="%d" class="lg">%s</text>' % (lx + 15, yy, g))
    svg.append("</svg>")
    graph = "".join(svg)

    # ---- approval questions: always rendered, derived from the log ----
    # DEPRECATED: old section 19 source; use the tracker
    sec = open(os.path.join(ROOT, "README-ACTION_ITEMS/status-and-references.md"), encoding="utf-8").read()
    def cl(x): return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x)).strip()
    orows = [[cl(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
             for r in sec[sec.index("## 19.1"):sec.index("## 19.2")].split("<tr>")]
    open_ids = {r[0] for r in orows
                if len(r) == 6 and re.match(r"^[A-Z]+-\d+$", r[0]) and r[3] == "Open"}
    qs = []
    for item in sorted(DECISIONS):
        if item in ANSWERED:
            continue
        if item in open_ids:
            prev = ANSWERS.get(item, {}).get("answer", "")
        done = ANSWERS.get(item, {}).get("answered_at", "")
        mark = " answered %s" % done[:10] if done else ""
        note = ANSWERS.get(item, {}).get("agent_note", "")
        noteblk = ('<p class=agentnote><strong>Answer from the team:</strong> %s</p>'
                   % html.escape(note)) if note else ""
        act = NEEDS_ACTION.get(item)
        actblk = ('<p class=action"><strong>Waiting on you:</strong> %s</p>'
                  % html.escape(act)) if act else ""
        clar = CLAR.get(item)
        cls = "ansrow unclear" if clar else "ansrow"
        badge = ('<span class=flag>needs clarification</span>' if clar else "")
        why = ('<p class=why><strong>Why this is unclear:</strong> %s</p>'
               '<p class=reword><strong>My reworded question:</strong> %s</p>'
               % (html.escape(clar["why"]), html.escape(clar["q"]))) if clar else ""
        qs.append(
            '<li class=%s><div class=qline><span class=qid>%s</span> %s'
            '<span class=when>%s</span>%s</div>%s%s%s'
            '<input class=ans id="a_%s" placeholder="type your decision here&hellip;" value="%s">'
            '<input type=hidden class=ts id="t_%s" value="%s"></li>'
            % (cls, html.escape(item), html.escape(DECISIONS[item]), mark, badge, noteblk, actblk, why,
               html.escape(item), html.escape(prev), html.escape(item), html.escape(done)))
    if qs:
        questions = (
            '<div class=panel id=approvals>'
            '<h2>Decisions needed from you</h2>'
            '<p class=note2>These %d items are blocked on an operator decision and cannot '
            'be completed by an agent. Answer any of them and the owning session can '
            'proceed. Items disappear from this list as they close.</p>'
            '<div class=form><ol class=qs>%s</ol>'
            '<div class=savebar><button id=save>Save decisions</button>'
            '<button class=ghost id=clearall>Clear</button>'
            '<span class=status id=st></span></div></div></div>' % (len(qs), "".join(qs)))
    else:
        questions = ('<div class=panel id=approvals><h2>Decisions needed from you</h2>'
                     '<p class=note2>Nothing is blocked on a decision right now.</p></div>')

    # ---- answered decisions ----
    # When nothing is outstanding the old page showed only "Nothing is blocked",
    # which read as "the operator has not decided anything" when the truth was
    # the opposite: 31 decisions were answered and simply left the queue. An
    # agent cannot act on an authorisation it cannot see, so the answered set is
    # listed here, newest first, collapsed by default.
    answered_rows = []
    for item in sorted(ANSWERS, key=lambda k: ANSWERS[k].get("answered_at", ""), reverse=True):
        rec = ANSWERS[item]
        val = str(rec.get("answer", "")).strip()
        if not val:
            continue
        when = str(rec.get("answered_at", ""))[:16].replace("T", " ")
        answered_rows.append(
            '<li class=answered><div class=ahead><span class=qid>%s</span>'
            '<span class=updwhen>answered %s</span></div>'
            '<div class=atext>%s</div></li>'
            % (html.escape(item), html.escape(when), html.escape(val)))
    if answered_rows:
        answered_panel = (
            '<div class=panel id=answered><h2>Decisions you have already given '
            '(%d)</h2>'
            '<p class=note2>These are recorded in answers.json and are the '
            'operator&rsquo;s standing authorisations. Sessions are expected to act '
            'on them; none of these is waiting on anything.</p>'
            '<ul class=answeredlist>%s</ul></div>'
            % (len(answered_rows), "".join(answered_rows)))
    else:
        answered_panel = ""

    hist = ("history: %d hourly record%s%s" % (n, "" if n == 1 else "s",
            " — the graph fills in as the hourly job runs"
            if n == 1 else ""))

    # ---- standing updates feed ----
    # Deliberately separate from the approvals panel: that one is a queue of
    # things WAITING on the operator, and mixing routine progress into it would
    # hide the decisions that actually block work. This one is one-way: the team
    # reports, the operator reads. No inputs, so nothing here can be mis-saved.
    ups = load_updates()
    if ups:
        lvl_class = {"info": "", "done": "ok", "warn": "warn", "action": "action"}
        items = []
        for r in ups:
            lv = r.get("level", "info")
            who = html.escape(str(r.get("who", "team")))
            when = html.escape(str(r.get("ts", ""))[:16].replace("T", " "))
            txt = html.escape(str(r.get("text", "")))
            items.append(
                '<li class="upd %s"><div class=updhead><span class=who>%s</span>'
                '<span class=updwhen>%s</span><span class=lvl>%s</span></div>'
                '<div class=updtext>%s</div></li>'
                % (lvl_class.get(lv, ""), who, when, html.escape(lv), txt))
        updates = ('<div class=panel id=updates><h2>Team updates</h2>'
                   '<p class=note2>Standing progress channel. Decisions that need '
                   'you are in the panel below, not here.</p>'
                   '<ul class=updates>%s</ul></div>' % "".join(items))
    else:
        updates = ('<div class=panel id=updates><h2>Team updates</h2>'
                   '<p class=note2>No updates posted yet. The coordinator posts '
                   'them with scripts/orchestration/dashboard-note.py.</p></div>')

    PAGE = """<!doctype html><html lang=en><meta charset=utf-8>
<title>ALWAYS ON - section 19 progress</title><style>
*{box-sizing:border-box}
body{margin:0;background:#f6f7f9;color:#1b1f24;font:14px/1.45 "DejaVu Sans",system-ui,sans-serif}
.wrap{padding:18px 22px}
.cols{display:grid;grid-template-columns:minmax(0,1fr) 430px;gap:14px;align-items:start}
@media (max-width:1250px){.cols{grid-template-columns:1fr}}
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
#approvals{border-color:#e0c48c;background:#fffdf7}
#approvals h2{font-size:15px;margin:0 0 4px;color:#7a5c15}
.note2{color:#6b5a2e;font-size:12.5px;margin:0 0 10px}
ol.qs{margin:0;padding-left:0;list-style:none;counter-reset:q}
ol.qs li{padding:7px 10px;border-left:3px solid #e0c48c;background:#fff;margin-bottom:6px;
 font-size:13.5px;line-height:1.5}
.ansrow.unclear{background:#fff8d6;border:1px solid #e0c14f;border-left:5px solid #e0a800;
 border-radius:4px;padding:9px 11px}
.when{margin-right:2px}
.ansrow.unclear .flag{margin-left:10px;background:#e0a800;color:#221c00;font-size:10px;font-weight:700;
 text-transform:uppercase;letter-spacing:.04em;padding:2px 7px;border-radius:9px;white-space:nowrap}
.action{margin:6px 0 0;font-size:12px;line-height:1.4;color:#5a3a00;background:#fdf4e3;border-left:3px solid #c08a2e;padding:6px 9px;border-radius:0 3px 3px 0}
.agentnote{margin:6px 0 0;font-size:12px;line-height:1.4;color:#0b3d2e;background:#eef7f2;border-left:3px solid #4c9a76;padding:6px 9px;border-radius:0 3px 3px 0}
.why,.reword{margin:5px 0 0;font-size:12px;line-height:1.4;color:#4a3f16}
.reword{color:#2d2606;background:#fffdf0;border-left:3px solid #e0c14f;padding:5px 8px;border-radius:0 3px 3px 0}
.qid{display:inline-block;min-width:82px;font-weight:700;color:#7a5c15;
 font-family:"DejaVu Sans Mono",monospace;font-size:12px}
#approvals .form{display:flex;flex-direction:column;gap:10px}
ol.qs{display:grid;grid-template-columns:1fr;gap:12px}
ol.qs li{margin-bottom:0}
.ans{width:100%;box-sizing:border-box;padding:6px 8px;font:13px/1.4 inherit;
 border:1px solid #d8cdb0;border-radius:5px;background:#fff;color:#1b1f24}
.ans:focus{outline:2px solid #c8a54a;outline-offset:-1px;border-color:#c8a54a}
.ans.saved{border-color:#15803d;background:#f2fbf4}
.ansrow{display:flex;flex-direction:column;gap:4px}
.savebar{position:static;display:flex;gap:9px;align-items:center;
 margin-top:14px;padding:12px 0 2px;border-top:1px solid #e6dcc2;background:#fffdf7}
button{font:600 13px/1 inherit;padding:9px 16px;border-radius:6px;cursor:pointer;
 border:1px solid #7a5c15;background:#7a5c15;color:#fff}
button:hover{background:#6a4f11}
button.ghost{background:#fff;color:#7a5c15}
.status{font-size:12px;color:#6b5a2e}
.status.ok{color:#15803d}
.status.bad{color:#b91c1c}
.ctl{display:flex;gap:9px;align-items:center;margin:0 0 14px}
#updates{border-color:#c9d6e2;background:#fbfdff}
#updates h2{font-size:15px;margin:0 0 4px;color:#1e4b6e}
ul.updates{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:7px}
li.upd{border-left:3px solid #c9d6e2;background:#fff;border-radius:0 4px 4px 0;
 padding:7px 10px;font-size:13px;line-height:1.5}
li.upd.ok{border-left-color:#15803d;background:#f4fbf6}
li.upd.warn{border-left-color:#b45309;background:#fffaf2}
li.upd.action{border-left-color:#7a5c15;background:#fffdf5}
.updhead{display:flex;gap:9px;align-items:baseline;margin-bottom:3px}
.upd .who{font-weight:700;font-size:12px;color:#1e4b6e;font-family:"DejaVu Sans Mono",monospace}
.updwhen{color:#8b95a3;font-size:11px}
.upd .lvl{font-size:10px;text-transform:uppercase;letter-spacing:.04em;color:#6b7280;
 background:#eef1f5;border-radius:8px;padding:1px 7px}
li.upd.ok .lvl{background:#dcf3e4;color:#14532d}
li.upd.warn .lvl{background:#fdecd2;color:#7c3d05}
li.upd.action .lvl{background:#f6e9c6;color:#5c4409}
.updtext{color:#24292f}
#answered{border-color:#bfe0cd;background:#f7fcf9}
#answered h2{font-size:15px;margin:0 0 4px;color:#14532d}
ul.answeredlist{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:7px;
 max-height:30em;overflow:auto}
li.answered{border-left:3px solid #bfe0cd;background:#fff;border-radius:0 4px 4px 0;
 padding:6px 10px;font-size:12.5px;line-height:1.5}
.ahead{display:flex;gap:9px;align-items:baseline}
li.answered .qid{color:#14532d}
.atext{color:#2c333b;margin-top:2px}
</style><div class=wrap>
<h1>ALWAYS ON &mdash; section 19 work items</h1>
<div class=ctl>
 <button id=ctlspawn>Next shift / revive agent</button>
 <button class=ghost id=ctlstop>Stop everything</button>
 <span class=status id=ctlst>checking&hellip;</span>
</div>
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
@UPDATES@
@ANSWERS@
@QUESTIONS@
<script>
// Save writes each non-empty answer to artifacts/dashboard/answers.json via a
// POST to the local writer. It never silently loses text: the button reports
// what it saved and what it could not.
(function(){
  var st=document.getElementById('st');
  function collect(){
    var out=[];
    document.querySelectorAll('input.ans').forEach(function(inp){
      var v=inp.value.trim();
      if(v) out.push({item:inp.id.slice(2), answer:v});
    });
    return out;
  }
  function mark(saved){
    document.querySelectorAll('input.ans').forEach(function(inp){
      if(inp.value.trim()) inp.classList.add('saved');
    });
    st.textContent=saved; st.className='status ok';
  }
  document.getElementById('save').addEventListener('click',function(){
    var rows=collect();
    if(!rows.length){ st.textContent='nothing filled in yet'; st.className='status'; return; }
    st.textContent='saving '+rows.length+'…';
    var ep = (location.protocol==='file:') ? 'http://127.0.0.1:8766/answers'
                                           : 'answers';
    if (location.protocol==='file:')
      st.textContent = 'page opened from disk - posting to the local writer at 8766. '+
                       'If this fails, run:  python3 scripts/orchestration/dashboard-writer.py';
    fetch(ep,{method:'POST',headers:{'Content-Type':'application/json'},
              body:JSON.stringify({answers:rows})})
      .then(function(r){ if(!r.ok) throw new Error('HTTP '+r.status);
                          return r.text(); })
      .then(function(){ mark('saved '+rows.length+' decision(s) at '+new Date().toLocaleTimeString()); })
      .catch(function(e){
        // Never lose typed text: fall back to a download the operator can drop in.
        try{
          var blob=new Blob([JSON.stringify({answers:rows},null,1)],
                            {type:'application/json'});
          var a=document.createElement('a');
          a.href=URL.createObjectURL(blob);
          a.download='answers.json'; a.click();
          st.textContent='writer unreachable ('+e.message+') - downloaded answers.json '+
                         'instead; save it to artifacts/dashboard/answers.json';
        }catch(_){}
        st.textContent='NOT saved - '+e.message+
                                    ' (is the writer running? see scripts/orchestration/dashboard-writer.py)';
                          st.className='status'; });
  });
  document.getElementById('clearall').addEventListener('click',function(){
    if(!confirm('Clear every answer field? Saved answers in answers.json are kept until you press Save.')) return;
    document.querySelectorAll('input.ans').forEach(function(i){ i.value=''; i.classList.remove('saved'); });
    st.textContent='cleared - press Save to write'; st.className='status';
  });

  /* ---- team control: spawn / stop ----
     Same file:// problem as Save: a relative fetch cannot resolve from a page
     opened off disk, so point at the writer's absolute address instead. There is
     no offline fallback here and there must not be - spawning sessions is a
     side effect on the machine, not a file the browser could hold for you. If
     the writer is unreachable the button says so rather than pretending. */
  var ctl = document.getElementById('ctlst');
  function ep(p){ return (location.protocol==='file:') ? 'http://127.0.0.1:8766/'+p : p; }
  function ctlCall(path, label, confirmMsg){
    if(confirmMsg && !confirm(confirmMsg)) return;
    ctl.textContent = label + '…'; ctl.className='status';
    fetch(ep(path), {method:'POST'})
      .then(function(r){ return r.json().then(function(j){ return {ok:r.ok, j:j}; }); })
      .then(function(x){
        if(!x.ok){ ctl.textContent = label+' FAILED: '+(x.j.error||'http error'); ctl.className='status bad'; return; }
        var n = x.j.live;
        ctl.textContent = path==='/spawn'
          ? ('rotation — '+(x.j.rotation||'unknown')+', '+x.j.live+' live processes' + (x.j.returncode?' (rc '+x.j.returncode+')':''))
          : ('stopped — '+x.j.signalled+' processes signalled, '+x.j.live+' live now');
        ctl.className = (n>0?'status ok':'status');
        setTimeout(refreshCtl, 15000);
      })
      .catch(function(e){
        ctl.textContent = label+' FAILED: ' + e.message +
          ' — is dashboard-writer.py running on 8766?';
        ctl.className='status bad';
      });
  }
  function refreshCtl(){
    fetch(ep('health')).then(function(r){ return r.json(); }).then(function(j){
      ctl.textContent = j.live + ' session process' + (j.live===1?'':'es') + ' running';
      ctl.className = j.live>0 ? 'status ok' : 'status bad';
    }).catch(function(){ ctl.textContent='writer unreachable'; ctl.className='status bad'; });
  }
  document.getElementById('ctlspawn').addEventListener('click',function(){
    ctlCall('/spawn','spawning');
  });
  document.getElementById('ctlstop').addEventListener('click',function(){
    ctlCall('/stop','stopping',
      'Stop every agent session, the supervisor watcher, the metrics collector and the 30-minute loop?\n\n' +
      'Work already committed in the worktrees is kept. Uncommitted work in /tmp is not.');
  });
  refreshCtl();
  setInterval(refreshCtl, 60000);
  document.querySelectorAll('input.ans').forEach(function(i){
    if(i.value.trim()) i.classList.add('saved');
  });
})();
</script>
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
            .replace("@HIST@", hist)
            .replace("@UPDATES@", updates)
            .replace("@ANSWERS@", answered_panel)
            .replace("@QUESTIONS@", questions))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(page)
    print("wrote %s  (open=%d done=%d, %d record(s))" % (OUT, to, td, n))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
