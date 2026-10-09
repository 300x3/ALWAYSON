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
WID = re.compile(r"^(PLAT|NET|SEC|LEDGER|PAY|COMM|FIELD|SIM|OPS)-\d+$")

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

    The detail column is LAST and routinely contains a literal `|`, because it
    quotes shell one-liners (`... | grep -vc '@sha256:'`). Splitting on `|` then
    yields eight cells for one row, and a `len(c) == 6` test discards it. That
    discard is the dangerous kind: nothing errors, the row is simply absent, so
    the dashboard quietly disagrees with a manual count of the tracker.
    Measured 2026-10-09: PLAT-02 and PLAT-04 both carry such pipes, so the
    tracker's 98 work items were published as 96.
    """
    out = []
    for line in seg.splitlines():
        s = line.strip()
        if not s.startswith("|") or SEP.match(s):
            continue
        c = [cl(x) for x in s.strip("|").split("|")]
        if len(c) > 6:
            # Columns 0-4 are fixed; everything after them belongs to the
            # trailing detail column, so glue the overflow back together with
            # the pipe that was there in the first place.
            c = c[:5] + [" | ".join(c[5:])]
        if len(c) == 6:
            out.append(c)
    return out


def raw_work_ids(seg):
    """Every work-ID-looking first cell, whatever the row's column count.

    This exists only to police the reconciliation guard. `rows()` legitimately
    drops rows whose ID cell is not a work ID (ST-* component rows, '—'), but it
    must never drop one that is -- and when it does, both sides of the guard are
    computed from `rows()` output, so the guard compares the missing set against
    itself and passes. Reading the IDs independently of the column test is what
    makes the guard able to fail.
    """
    out = set()
    for line in seg.splitlines():
        s = line.strip()
        if not s.startswith("|") or SEP.match(s):
            continue
        first = cl(s.strip("|").split("|")[0])
        if WID.match(first):
            out.add(first)
    return out

def main():
    t = open(SEC, encoding="utf-8").read()
    seg191 = t[t.index("## 19.1"):t.index("## 19.2")]
    seg192 = t[t.index("## 19.2"):t.index("## 19.3")]
    o = rows(seg191)
    d = rows(seg192)

    # A work item is identified by its ID and may legitimately appear in both
    # logs, so dedup by ID or the totals will not match the source:
    #   - 19.2 is the Completed section: every work-ID there is done.
    #   - 19.1 holds live rows; a row is done when its status says Complete.
    # Counting only 19.2 (the old logic) lost items like FIELD-08, which is
    # marked Complete in 19.1 but was never moved to 19.2. Counting both
    # without dedup double-counted PAY-08/09/10, which sit in both. So: a row
    # is done if it is in 19.2 OR its 19.1 status starts with Complete/
    # Implemented; everything else with a work ID is outstanding. Measured
    # 2026-10-09: 96 work items, 4 complete, 92 outstanding.
    wid = WID
    done_ids = {r[0] for r in d if wid.match(r[0])}
    for r in o:
        if wid.match(r[0]) and re.match(r"(?i)^(complete|implemented)", r[3]):
            done_ids.add(r[0])

    rec = {"ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "open": {}, "done": {}}
    for g in GROUPS:
        pref = g + "-"
        ids = {r[0] for r in o if re.match(r"^%s\d+$" % pref, r[0])}
        ids |= {r[0] for r in d if re.match(r"^%s\d+$" % pref, r[0])}
        rec["done"][g] = sum(1 for i in ids if i in done_ids)
        rec["open"][g] = len(ids) - rec["done"][g]


    to, td = sum(rec["open"].values()), sum(rec["done"].values())

    # A guard, because this exact failure already happened once and cost the
    # operator several rounds of "it still says 36%". When sections 19-20 moved
    # out of README.md the tracker became Markdown, the HTML regex in rows()
    # matched nothing, and the collector recorded open=0 done=0 for nine groups
    # on every run without complaining. 49 records on three different counting
    # bases then sat in the history file and the "% completed over time" graph
    # plotted all of them on one axis, so the page read 36% - a number from a
    # counting basis that no longer existed. Nothing flagged it because a
    # record is just a record to whoever appends it.
    #
    # So: refuse to append a record that does not reconcile with the source.
    # The tracker is the authority; if the collector cannot see the items it
    # expects, say so and write nothing rather than publish a number that looks
    # like data.
    # Compare against an ID set read independently of `rows()`. The previous
    # version built `work_ids` from the same filtered rows it then counted, so a
    # row dropped by the column test was missing from BOTH sides and the check
    # passed -- 96 == 96 while the tracker held 98. Measured 2026-10-09.
    work_ids = raw_work_ids(seg191) | raw_work_ids(seg192)
    if to + td == 0 or not work_ids:
        print("REFUSED to record: parsed 0 work items from %s.\n"
              "        The parser and the tracker format have drifted apart.\n"
              "        Nothing was written - a 0/0 record would be plotted as\n"
              "        0%% and would silently corrupt the history graph." % SEC)
        return 1
    # The tracker also carries ST-* component rows and '—' separator rows, which
    # are deliberately NOT work items and are not counted above. So reconcile
    # against the work IDs only: if these two disagree, a row the operator can
    # see in the tracker is missing from the dashboard totals.
    if len(work_ids) != to + td:
        missing = sorted(work_ids - {r[0] for r in o} - {r[0] for r in d})
        print("REFUSED to record: %d work IDs visible in the tracker but %d "
              "counted.\n      A row is being parsed incorrectly, so the "
              "dashboard total would\n      not match a manual count of the "
              "source.\n      first offenders: %s\n      Nothing was written."
              % (len(work_ids), to + td, ", ".join(missing[:8]) or "(none named)"))
        return 1

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print("recorded %s  open=%d done=%d total=%d" % (rec["ts"], to, td, to + td))
    return 0

if __name__ == "__main__":
    sys.exit(main())
