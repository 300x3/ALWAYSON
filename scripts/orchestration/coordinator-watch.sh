#!/bin/bash
# ao-coordinator-watch: the coordinator's self-reminder.
# Why this exists: the coordinator (this chat session) only runs when the
# operator sends a message. Between messages it is dormant -- systemd timers
# move agents (ao-rotation), refresh the dashboard, and collect metrics, but
# NOTHING wakes the coordinator itself. So "remind yourself" was structurally
# impossible until this timer. It runs every 15 minutes and:
#   1. guard pass (revive dead/errored agents, capped by MAX_NUDGES)
#   2. rotation status check (revive current shift in place if dead)
#   3. compiler --check (alert if a session hand-edited README.md)
#   4. dashboard note ONLY when something needs the operator (action/warn),
#      plus a heartbeat info note at most once per 2h so the dashboard shows
#      the watch is alive without spamming Team updates.
set -u
cd /ALWAYSON || exit 1
STATE_DIR=/tmp/ao-sessions
HEARTBEAT="$STATE_DIR/coordinator-watch.heartbeat"
NOW=$(date +%s)

# 1. Rotation revival (NOT `supervise.py guard`).
# guard is built for the old all-11-parallel mode: when anything is live it
# still nudges every dead/never group, which would spawn 10 extra agents and
# break the one-group-per-shift doctrine. `rotate` already revives the current
# holder in place when its shift still has time left, and advances the shift
# when it is over -- so it is the only recovery this watch calls.
python3 scripts/orchestration/rotate-agents.py rotate 2>&1 | logger -t ao-coordinator-watch

# 3. Compiler gate: sessions must never hand-edit README.md.
if ! python3 "agents/COORDINATION (README UPDATES)/tools/compile.py" --check 2>/dev/null | grep -q identical; then
  python3 scripts/orchestration/dashboard-note.py --who coordinator --level action \
    "compile gate DIFFERS: a session hand-edited README.md -- needs split.py fold-in"
  exit 0
fi

# 4. Heartbeat: only escalate to dashboard when attention is needed.
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
  CUR=$(python3 scripts/orchestration/rotate-agents.py status 2>/dev/null || echo "rotation unknown")
  python3 scripts/orchestration/dashboard-note.py --who coordinator --level info \
    "coordinator watch alive -- $CUR" >/dev/null 2>&1
  echo "$NOW" > "$HEARTBEAT"
fi
