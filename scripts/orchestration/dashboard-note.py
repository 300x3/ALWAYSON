#!/usr/bin/env python3
"""Post a standing update to the ALWAYS ON dashboard, then re-render it.

This is the channel for REGULAR UPDATES. The "Decisions needed from you" panel
on the same page is a different thing: that is a queue of items blocked on the
operator, and it only shrinks when an item closes. Routine progress belongs
here, so it does not drown the decisions that actually block work.

    dashboard-note.py "spawned plat on cline-free/mimo-v2.6-flash"
    dashboard-note.py --who plat --level done "PLAT-03 closed with evidence"
    dashboard-note.py --who coordinator --level action "waiting on SEC-01 decision"
    dashboard-note.py --list          # show recent notes
    dashboard-note.py --tail 5        # render only, showing the last 5

Levels: info (default), done, warn, action. Colour and badge follow the level;
`action` is the loudest and is for something the operator must look at now.

Append-only JSONL on purpose: a note cannot be clobbered by a concurrent write,
and a note already posted is never rewritten by a later one. The file is capped
on READ (render-dashboard.py keeps the newest 40), so it grows slowly and is
safe to leave in git.

After writing, this re-runs the renderer so the change is visible immediately
rather than at the next hourly timer tick. It does NOT touch section 19, does
not recompile README.md, and does not renumber any work ID.
"""
import json
import os
import subprocess
import sys
import datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "artifacts/dashboard/updates.jsonl")
RENDER = os.path.join(ROOT, "scripts/orchestration/render-dashboard.py")
LEVELS = ("info", "done", "warn", "action")


def main():
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        return 2

    # --list / --tail N: read-only, no write, no re-render.
    if argv[0] == "--list":
        n = int(argv[1]) if len(argv) > 1 else 10
        if not os.path.exists(OUT):
            print("no updates posted yet")
            return 0
        rows = []
        for line in open(OUT, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    pass
        rows.sort(key=lambda r: r.get("ts", ""), reverse=True)
        for r in rows[:n]:
            print("%s  %-10s %-7s %s" % (r.get("ts", "")[:16].replace("T", " "),
                                         r.get("who", "team"), r.get("level", "info"),
                                         r.get("text", "")))
        print("(%d note%s total)" % (len(rows), "" if len(rows) == 1 else "s"))
        return 0

    who = "coordinator"
    level = "info"
    text = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--who" and i + 1 < len(argv):
            who = argv[i + 1]; i += 2; continue
        if a == "--level" and i + 1 < len(argv):
            level = argv[i + 1]; i += 2; continue
        if a.startswith("--"):
            print("unknown flag: %s" % a)
            return 2
        text = " ".join(argv[i:])
        break

    if not text or not text.strip():
        print("no text given")
        return 2
    if level not in LEVELS:
        print("level must be one of: %s" % ", ".join(LEVELS))
        return 2

    rec = {
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "who": who[:40],
        "level": level,
        # Collapse newlines: one note is one row in the feed, and a multi-line
        # blob would break the layout of every note around it.
        "text": " ".join(text.split())[:1200],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")

    print("posted [%s] %s: %s" % (rec["level"], rec["who"], rec["text"][:90]))

    # Re-render so the note is visible now, not at the next hourly tick. A
    # render failure is reported but does not undo the note: the note is
    # already durable, and the hourly timer will pick it up regardless.
    r = subprocess.run([sys.executable, RENDER], capture_output=True, text=True)
    if r.returncode != 0:
        print("WARNING: re-render failed (rc=%d): %s" % (r.returncode, (r.stderr or "")[-300:]))
        print("the note is saved; the hourly timer will render it")
        return 1
    print((r.stdout or "").strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
