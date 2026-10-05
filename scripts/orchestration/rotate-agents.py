#!/usr/bin/env python3
"""Rotate ONE ALWAYS ON agent at a time through the 11 groups, 2 hours each.

Operator instruction 2026-10-05: run one at a time for 2-hour periods on the
free model. Two constraints drive this design:

  1. The `stealth/space-bunny-alpha` model returns 404 on OpenRouter, so every
     agent spawned against it died at iteration 1 (measured 2026-10-05). The
     only model verified working for agents is `poolside/laguna-s-2.1:free`.
  2. That model has a DAILY quota. Running all 11 at once burns it in hours
     and the whole team dies together. One agent at a time spends quota at
     roughly 1/11 the rate, and the 2-hour cap bounds each group's share so a
     chatty group cannot eat the day.

How it runs: a systemd user timer fires every 2 hours and calls `rotate`.
The script reads the rotation state (which group is current, when it started),
stops the current agent if one is running, spawns the next group, and records
the handoff. It exits immediately -- agents keep running unattended between
ticks. Linger=yes means this survives logout and reboot.

The order follows dependency sense, not alphabet: platform and network first
(everything sits on them), then security and ledger (gates for the rest), then
payment and comm (external surface), then field and sim (heavy compute), then
the two ops batches, then spec.

Usage:
  rotate-agents.py rotate      one handoff (called by the timer)
  rotate-agents.py status      who is current, how long they have left
  rotate-agents.py stop        stop the current agent and clear the rotation
"""
import json
import os
import subprocess
import sys
import time

SUPERVISE = "/ALWAYSON/scripts/orchestration/supervise.py"
STATE = "/tmp/ao-sessions/rotation.json"
SHIFT_SEC = 2 * 3600  # 2 hours per group, operator instruction

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
    st = load()
    cur = st.get("current")
    if not cur:
        print("rotation: idle, no agent running")
        return
    left = SHIFT_SEC - (time.time() - st.get("started", 0))
    mins = max(0, int(left // 60))
    print("rotation: %s current, ~%dh%02dm left of its 2h shift"
          % (cur, mins // 60, mins % 60))


def cmd_stop():
    st = load()
    cur = st.get("current")
    if cur:
        subprocess.run([sys.executable, SUPERVISE, "stop"], check=False)
    save({"current": None, "started": 0})
    print("rotation stopped")


def cmd_rotate():
    st = load()
    cur = st.get("current")
    elapsed = time.time() - st.get("started", 0)

    if cur and elapsed < SHIFT_SEC:
        # Shift not over. The only legitimate reason to touch anything early
        # is a dead agent -- revive it in place so the shift is not wasted.
        out = subprocess.run([sys.executable, SUPERVISE, "state1", cur],
                             capture_output=True, text=True).stdout.split(None, 1)
        st1 = out[0] if out else "unknown"
        if st1 in ("error", "dead", "never"):
            mins = int(elapsed // 60)
            print("%s is %s %dm into its shift; reviving in place" % (cur, st1, mins))
            subprocess.run([sys.executable, SUPERVISE, "nudge", cur,
                            "rotation revival: shift still has time left"],
                           check=False)
        else:
            mins = int((SHIFT_SEC - elapsed) // 60)
            print("%s still on shift (%s, ~%dm left); nothing to do" % (cur, st1, mins))
        return

    if cur:
        print("ending %s's shift" % cur)
        subprocess.run([sys.executable, SUPERVISE, "stop"], check=False)

    nxt = ORDER[(ORDER.index(cur) + 1) % len(ORDER)] if cur in ORDER else ORDER[0]
    # Reset its nudge budget; a revive that hit the cap would otherwise leave
    # the next shift permanently un-nudgeable.
    npath = "/tmp/ao-sessions/%s/nudges" % nxt
    try:
        with open(npath, "w") as fh:
            fh.write("0")
    except OSError:
        pass
    subprocess.run([sys.executable, SUPERVISE, "spawn", nxt], check=False)
    save({"current": nxt, "started": time.time()})
    print("started %s (shift %d of %d)"
          % (nxt, ORDER.index(nxt) + 1, len(ORDER)))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "rotate":
        cmd_rotate()
    elif cmd == "stop":
        cmd_stop()
    else:
        cmd_status()
