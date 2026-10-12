#!/bin/bash
# ao-coordinator-watch: the coordinator's self-reminder + the team's guard.
# Why this exists: the coordinator (this chat session) only runs when the
# operator sends a message. Between messages it is dormant -- systemd timers
# refresh the dashboard, collect metrics, and (this timer) keep the agent
# sessions alive, but NOTHING wakes the coordinator itself. So "remind
# yourself" was structurally impossible until this timer. It runs every
# 5 minutes and:
#   1. guard pass (parallel doctrine, operator 2026-10-10: all 11 groups run
#      at once; revive dead/errored agents, continue finished ones, capped by
#      MAX_NUDGES; never stop a live session)
#   2. compiler --check (alert if a session hand-edited README.md)
#   3. dashboard note ONLY when something needs the operator (action/warn),
#      plus a heartbeat info note at most once per 2h so the dashboard shows
#      the watch is alive without spamming Team updates.
set -u
cd /ALWAYSON || exit 1
STATE_DIR=/tmp/ao-sessions
HEARTBEAT="$STATE_DIR/coordinator-watch.heartbeat"
NOW=$(date +%s)

# 1. Recovery pass. rotate-agents.py rotate now DELEGATES to supervise.py
# guard (parallel doctrine since 2026-10-10 -- the old one-group-per-shift
# handoff that stopped every other session is gone). guard revives dead or
# errored groups in their own worktree, continues finished ones, respawns
# the whole team only when nothing at all is live, and caps each group at
# MAX_NUDGES so a permanently broken group surfaces as "needs a human"
# instead of spinning.
python3 scripts/orchestration/rotate-agents.py rotate 2>&1 | logger -t ao-coordinator-watch

# 2. Compiler gate: sessions must never hand-edit README.md.
if ! python3 "agents/COORDINATION (README UPDATES)/tools/compile.py" --check 2>/dev/null | grep -q identical; then
  python3 scripts/orchestration/dashboard-note.py --who coordinator --level action \
    "compile gate DIFFERS: a session hand-edited README.md -- needs split.py fold-in"
  exit 0
fi

# 4. Decision/stuck scan: the guard revives dead sessions, but a session can
# be alive yet BLOCKED -- waiting on an operator decision (ask_question /
# approval language in its recent events) or looping without progress
# (high iteration count, no file changes, no proposal output). Scan the
# last 30 events of each live group for decision-request language and for
# idle-loop signatures; post ONE action note naming every blocked group so
# the operator sees it in Team updates immediately (not at the 5pm merge).
# State file keeps this idempotent: a group already alerted is not re-posted
# until its events advance past the alerted point.
SCAN_STATE="$STATE_DIR/decision-scan.json"
python3 - "$SCAN_STATE" <<'PYEOF' 2>&1 | logger -t ao-coordinator-watch
import json, os, sys, glob
state_path = sys.argv[1]
try:
    seen = json.load(open(state_path))
except Exception:
    seen = {}
DECISION_RE = ("ask_question", "approval", "decision needed", "waiting for",
    "need operator", "need the operator", "your approval", "please approve",
    "blocked on", "blocked waiting", "require approval", "needs approval")
def recent_events(g, n=30):
    p = os.path.join("/tmp/ao-sessions", g, "events.jsonl")
    try:
        lines = open(p, errors="replace").read().splitlines()
    except OSError:
        return []
    out = []
    for line in lines[-n:]:
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out
blocked = []
for g in ("plat","net","sec","ledger","pay","comm","field","sim","ops-a","ops-b","spec"):
    ev = recent_events(g)
    if not ev:
        continue
    blob = json.dumps(ev).lower()
    last_ts = ev[-1].get("ts", "")
    if seen.get(g) == last_ts:
        continue
    hits = [d for d in DECISION_RE if d in blob]
    if hits:
        blocked.append("%s(waiting: %s)" % (g, hits[0]))
        seen[g] = last_ts
if blocked:
    json.dump(seen, open(state_path, "w"))
    print("BLOCKED:" + ",".join(blocked))
PYEOF
SCAN_OUT=$(python3 - "$SCAN_STATE" <<'PYEOF' 2>/dev/null
import json, os, sys
state_path = sys.argv[1]
try:
    seen = json.load(open(state_path))
except Exception:
    seen = {}
DECISION_RE = ("ask_question", "approval", "decision needed", "waiting for",
    "need operator", "need the operator", "your approval", "please approve",
    "blocked on", "blocked waiting", "require approval", "needs approval")
def recent_events(g, n=30):
    p = os.path.join("/tmp/ao-sessions", g, "events.jsonl")
    try:
        lines = open(p, errors="replace").read().splitlines()
    except OSError:
        return []
    out = []
    for line in lines[-n:]:
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out
blocked = []
for g in ("plat","net","sec","ledger","pay","comm","field","sim","ops-a","ops-b","spec"):
    ev = recent_events(g)
    if not ev:
        continue
    blob = json.dumps(ev).lower()
    last_ts = ev[-1].get("ts", "")
    if seen.get(g) == last_ts:
        continue
    hits = [d for d in DECISION_RE if d in blob]
    if hits:
        blocked.append("%s(waiting: %s)" % (g, hits[0]))
        seen[g] = last_ts
if blocked:
    json.dump(seen, open(state_path, "w"))
    print("BLOCKED:" + ",".join(blocked))
PYEOF
)
if [ -n "$SCAN_OUT" ]; then
  python3 scripts/orchestration/dashboard-note.py --who coordinator --level action \
    "session(s) waiting on operator decision: $SCAN_OUT -- check their events before 17:00 merge"
fi
# Count groups needing a human (nudge budget spent) via status output.
NEED_HUMAN=$(timeout 30 python3 scripts/orchestration/supervise.py status 2>/dev/null | grep -c -iE 'needs a human|limit.*reached' || true)
if [ "$NEED_HUMAN" -gt 0 ]; then
  python3 scripts/orchestration/dashboard-note.py --who coordinator --level action \
    "$NEED_HUMAN group(s) hit the nudge limit and need the operator -- see supervise.py status"
  exit 0
fi
LAST_HB=0
[ -f "$HEARTBEAT" ] && LAST_HB=$(cat "$HEARTBEAT" 2>/dev/null || echo 0)
if [ $((NOW - LAST_HB)) -ge 7200 ]; then
  CUR=$(python3 scripts/orchestration/rotate-agents.py status 2>/dev/null || echo "parallel status unknown")
  python3 scripts/orchestration/dashboard-note.py --who coordinator --level info \
    "coordinator watch alive -- $CUR" >/dev/null 2>&1
  echo "$NOW" > "$HEARTBEAT"
fi
