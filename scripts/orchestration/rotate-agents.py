#!/usr/bin/env python3
"""Recovery/activation tick for the ALWAYS ON team -- PARALLEL mode.

History: 2026-10-05 the operator ran ONE agent at a time in 2-hour shifts.
SUPERSEDED 2026-10-10 by the operator instruction "ASSIGN MORE FREE AI
AGENTIC CODERS TO SPECIFIC WORKGROUPS AND TO ACTIVATE THOSE SESSIONS /
MANAGE THEM." Each of the 11 groups now keeps its own worktree, its own
ledger-PASS free model bucket (GROUP_MODEL in supervise.py) and its own
live session, all running at once. What still needs a periodic tick is
RECOVERY: dead/errored sessions revived in their own worktree, finished
sessions nudged on to the next piece of their brief, every revival under
the MAX_NUDGES cap.

`rotate` therefore delegates to supervise.py guard -- one recovery pass,
exiting immediately, and NEVER stops a live session (the old
stop-current/spawn-next handoff is gone). Callers:
  * ao-coordinator-watch.timer, every 5 minutes -- primary
  * ao-rotation.timer, every 2h + 2min after boot -- backup and
    post-boot catch-up (rotation.json no longer tracks shifts; a reboot
    wipes /tmp and guard respawns the whole team with fresh counters)
Linger=yes means the timers survive logout and reboot.

The order below follows dependency sense, not alphabet: platform and
network first (everything sits on them), then security and ledger (gates
for the rest), then payment and comm (external surface), then field and
sim (heavy compute), then the two ops batches, then spec. It is now the
display order for status output only.

Usage:
  rotate-agents.py rotate      one guard pass (called by the timers)
  rotate-agents.py status      how many sessions are live
  rotate-agents.py stop        stop every session, clear rotation state
"""
import json
import os
import subprocess
import sys

SUPERVISE = "/ALWAYSON/scripts/orchestration/supervise.py"
STATE = "/tmp/ao-sessions/rotation.json"

ORDER = ["plat", "net", "sec", "ledger", "pay", "comm",
         "field", "sim", "ops-a", "ops-b", "spec"]


def load():
    try:
        with open(STATE) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {"current": None, "started": 0}


def save(st):
    tmp = STATE + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(st, fh)
    os.replace(tmp, STATE)


def cmd_status():
    """Parallel summary: how many of the 11 sessions are live right now."""
    r = subprocess.run([sys.executable, SUPERVISE, "status"],
                       capture_output=True, text=True)
    if r.returncode != 0 and not r.stdout.strip():
        print("parallel mode: supervise status failed: %s"
              % ((r.stderr or "no output")[:200]))
        return
    live = sum(1 for line in r.stdout.splitlines()
               if len(line.split()) > 1 and line.split()[1] in ("running", "stuck"))
    print("parallel mode (since 2026-10-10, no shifts): %d/%d sessions live"
          % (live, len(ORDER)))


def cmd_stop():
    """Stop every session (the team runs in parallel) and clear old state."""
    subprocess.run([sys.executable, SUPERVISE, "stop"], check=False)
    save({"current": None, "started": 0})
    print("all sessions stopped")


def cmd_rotate():
    """One recovery pass. Never stops a live session (parallel doctrine).

    The 2026-10-05 stop-current/spawn-next handoff is gone: with all 11
    groups live on their own buckets there is no shift to hand off. guard
    revives dead/errored sessions in their own worktree, continues finished
    ones, respawns the whole team only when nothing at all is live, and
    caps every group at MAX_NUDGES so this cannot spin forever.
    """
    print("parallel doctrine (operator 2026-10-10): running one guard pass")
    subprocess.run([sys.executable, SUPERVISE, "guard"], check=False)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "rotate":
        cmd_rotate()
    elif cmd == "stop":
        cmd_stop()
    else:
        cmd_status()
