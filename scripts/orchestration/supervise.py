#!/usr/bin/env python3
"""Supervise the ALWAYS ON group sessions: status, stuck detection, nudge, stop.

Usage:
  supervise.py spawn  [GROUP ...]   start sessions (default: all)
  supervise.py status              one-line health per session
  supervise.py watch               poll until all finished, nudging stuck ones
  supervise.py nudge GROUP         send a continuation prompt to a session
  supervise.py report              final report from each session's done event
  supervise.py stop                terminate every running session

Design notes, all verified against cline 3.0.60:
  * `cline --json` emits one JSON object per line, each with `ts`. That stream is the
    only reliable progress signal, so every session logs to its own file.
  * `--id <taskId>` CANNOT resume a session in 3.0.60: with `--json` it fails
    "JSON output mode requires a prompt argument", and without `--json` it fails
    "interactive mode requires a TTY". So "unsticking" a session means a NUDGE - a fresh
    invocation into the SAME worktree with a continuation prompt. The worktree holds the
    state; the conversation does not need to survive.
  * Therefore every nudge prompt tells the agent to re-read its brief and check git
    status first, so a context-free session does not start over.
"""
import json, os, subprocess, sys, time, signal, glob, shlex

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN = "/tmp/ao-sessions"
PAGES = "agents/handoffs/SESSION ASSIGNMENTS"
GROUPS = ["plat","net","sec","ledger","pay","comm","field","sim","ops-a","ops-b","spec"]
# A session with no new event for STUCK_MIN minutes, but no done/error event, is stuck.
STUCK_MIN = 12
MAX_NUDGES = 3
TIMEOUT = 5400  # hard ceiling per session


def prompt_path(g):
    for p in glob.glob(os.path.join(ROOT, PAGES, "*-%s.prompt.md" % g)):
        return p
    raise SystemExit("no prompt for group %r" % g)


def run_dir(g):
    d = os.path.join(RUN, g)
    os.makedirs(d, exist_ok=True)
    return d


def worktree(g):
    return os.path.join(RUN, "wt-%s" % g)


def spawn(g):
    d, wt = run_dir(g), worktree(g)
    if os.path.exists(os.path.join(d, "pid")):
        pid = int(open(os.path.join(d, "pid")).read())
        if pid_alive(pid):
            print("%-6s already running pid=%d" % (g, pid)); return
    # fresh worktree from origin/main - never from local main
    if not os.path.isdir(wt):
        subprocess.run(["git", "-C", ROOT, "worktree", "add", "-b", "ai-%s" % g, wt,
                        "origin/main"], check=True)
    log = os.path.join(d, "events.jsonl")
    env = dict(os.environ, AO_GROUP=g)
    cmd = ["cline", "--json", "--cwd", wt, "--timeout", str(TIMEOUT),
           "-t", str(TIMEOUT + 300), "--thinking", "high", open(prompt_path(g)).read()]
    with open(log, "ab") as out:
        p = subprocess.Popen(cmd, stdout=out, stderr=subprocess.STDOUT,
                             start_new_session=True, env=env)
    open(os.path.join(d, "pid"), "w").write(str(p.pid))
    open(os.path.join(d, "nudges"), "w").write("0")
    print("%-6s spawned pid=%d -> %s" % (g, p.pid, log))


def pid_alive(pid):
    try:
        os.kill(pid, 0); return True
    except OSError:
        return False


def events(g):
    """Events for the CURRENT run only.

    events.jsonl is append-only across nudges, so a stale `error` or `done` from an
    earlier run would otherwise match on the reverse scan and report the previous run's
    outcome as this run's state - which is what kept `sec` in error while it was actually
    running fine, and burned nudges against a live session. Truncate at the last
    agent_start so only the current run is read.
    """
    f = os.path.join(run_dir(g), "events.jsonl")
    if not os.path.exists(f):
        return []
    out = []
    for line in open(f, errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    # run boundary = last agent_start hook
    start = 0
    for i, e in enumerate(out):
        if e.get("type") == "hook_event" and e.get("hookEventName") == "agent_start":
            start = i
    return out[start:]


def state(g):
    """Return (status, detail). status in running|done|error|dead|stuck|never."""
    pf = os.path.join(run_dir(g), "pid")
    if not os.path.exists(pf):
        return "never", "not spawned"
    pid = int(open(pf).read())
    ev = events(g)
    for e in reversed(ev):
        if e.get("type") == "agent_event" and e["event"].get("type") == "done":
            return "done", e["event"].get("reason", "?")
        if e.get("type") == "error":
            return "error", e.get("message", "")[:80]
        if e.get("type") == "run_result":
            return ("done" if e.get("finishReason") == "completed" else "error"), e.get("finishReason", "")
    # liveness first: a live pid with no terminal event is running/stuck, NOT dead.
    # (Checking pid before the event scan misreported live sessions as dead.)
    if not ev:
        return ("running" if pid_alive(pid) else "dead"), ("starting" if pid_alive(pid) else "no events, process gone")
    if not pid_alive(pid):
        return "dead", "process gone, no done event"
    import datetime as dt
    last = ev[-1].get("ts", "")
    try:
        age = (dt.datetime.now(dt.timezone.utc)
               - dt.datetime.fromisoformat(last.replace("Z", "+00:00"))).total_seconds() / 60
    except ValueError:
        age = 0
    it = [e["event"].get("iteration", 0) for e in ev
          if e.get("type") == "agent_event" and e["event"].get("type") == "iteration_start"]
    det = "iter %s, idle %.1fm" % (it[-1] if it else "?", age)
    return ("stuck" if age > STUCK_MIN else "running"), det


def nudge(g, reason):
    """Fresh invocation into the same worktree. Resume is broken in 3.0.60."""
    d, wt = run_dir(g), worktree(g)
    n = int(open(os.path.join(d, "nudges")).read()) if os.path.exists(os.path.join(d, "nudges")) else 0
    if n >= MAX_NUDGES:
        print("%-6s nudge limit (%d) reached - needs a human" % (g, MAX_NUDGES)); return
    n += 1
    open(os.path.join(d, "nudges"), "w").write(str(n))
    msg = (
        "You are the %s session for ALWAYS ON, continuing after a stall (%s).\n\n"
        "You have no memory of the earlier run. Do this first, before anything else:\n"
        "  1. cd %s && git status --short && git log --oneline -3\n"
        "  2. Re-read your brief: %s\n"
        "  3. Re-read the acceptance criteria for your assigned items in "
        "agents/COORDINATION/19-current-status-and-outstanding-work/section.md\n\n"
        "Then continue the work. Do not start items you already completed - git status and\n"
        "your proposals directory show what is already done. If you were mid-way through an\n"
        "item, finish that one first.\n\n"
        "Rules unchanged: edit only your own section files, never README.md directly, never\n"
        "edit section 19 (write proposals instead), never renumber anything, never git add -A,\n"
        "and stop for operator approval on payments, ledger keys, secrets, backup data, live\n"
        "radio or ports. Prove every claim with a command and its real output.\n"
    ) % (g, reason, wt, prompt_path(g))
    with open(os.path.join(d, "events.jsonl"), "ab") as out:
        p = subprocess.Popen(["cline", "--json", "--cwd", wt, "--timeout", str(TIMEOUT),
                              "-t", str(TIMEOUT + 300), msg],
                             stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
    open(os.path.join(d, "pid"), "w").write(str(p.pid))
    print("%-6s nudged #%d (pid %d) - %s" % (g, n, p.pid, reason))


def cmd_status():
    print("%-7s %-8s %s" % ("GROUP", "STATE", "DETAIL"))
    for g in GROUPS:
        s, d = state(g)
        print("%-7s %-8s %s" % (g, s, d))


def cmd_watch(interval=60):
    nudged = set()
    while True:
        states = {g: state(g) for g in GROUPS}
        cmd_status()
        # A dead or errored session is NOT settled - it is a session that needs
        # recovery. Treating it as inactive made `watch` report "all sessions
        # settled" while a session sat dead and unrecovered.
        NEEDS = ("running", "stuck", "error", "dead", "never")
        active = [g for g in GROUPS if states[g][0] in NEEDS]
        for g in GROUPS:
            s, d = states[g]
            if s in ("stuck", "error", "dead") and g not in nudged:
                nudge(g, d); nudged.add(g)
        if not active:
            print("\nall sessions settled.")
            cmd_report(); return
        time.sleep(interval)


def cmd_report():
    print("\n%-7s %-8s %s" % ("GROUP", "STATE", "RESULT"))
    for g in GROUPS:
        s, d = state(g)
        print("%-7s %-8s %s" % (g, s, d[:100]))
    print("\nproposals written:")
    for f in sorted(glob.glob(os.path.join(ROOT, "agents/COORDINATION/proposals/*.md"))):
        print("  ", os.path.basename(f))


def cmd_stop():
    for g in GROUPS:
        pf = os.path.join(run_dir(g), "pid")
        if os.path.exists(pf):
            pid = int(open(pf).read())
            if pid_alive(pid):
                try:
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                    print("%-6s stopped pid=%d" % (g, pid))
                except OSError as e:
                    print("%-6s stop failed: %s" % (g, e))
            os.remove(pf)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    args = sys.argv[2:]
    if cmd == "spawn":
        for g in (args or GROUPS):
            spawn(g)
    elif cmd == "status": cmd_status()
    elif cmd == "watch":  cmd_watch(int(args[0]) if args else 60)
    elif cmd == "nudge":  nudge(args[0], args[1] if len(args) > 1 else "manual")
    elif cmd == "report": cmd_report()
    elif cmd == "stop":   cmd_stop()
    else: raise SystemExit(__doc__)
