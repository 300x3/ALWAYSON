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
PAGES = "agents/SESSION ASSIGNMENTS (AI WORKGROUPS)"
GROUPS = ["plat","net","sec","ledger","pay","comm","field","sim","ops-a","ops-b","spec"]
# A session with no new event for STUCK_MIN minutes, but no done/error event, is stuck.
STUCK_MIN = 12
MAX_NUDGES = 3
TIMEOUT = 5400  # hard ceiling per session

# ---------------------------------------------------------------------------
# MODEL ASSIGNMENT -- operator instruction 2026-10-08: every workgroup agent
# runs on a FREE Cline-provider model, assigned per group, and only on a model
# proven to work on this host first.
#
# The old default was poolside/laguna-s-2.1:free, an OpenRouter free tier with
# a DAILY quota that killed seven sessions on 2026-10-03 and paced every shift
# after that. That model is retired. The `cline-free/*` models below are served
# by the Cline provider itself: $0 cost (measured totalCost:0 on every run),
# no OpenRouter daily-quota wall, and `--model` selects them per invocation.
#
# VERIFIED 2026-10-08 against cline 3.0.60 on this host. Each model was given a
# real two-part task (fix a wrong-operator bug, overwrite a file, then run the
# fix and report the output). "PASS" means it edited both files correctly and
# reported finishReason=completed with totalCost=0:
#
#   cline-free/step-5-preview             PASS  StepFun flagship, sparse MoE
#   cline-free/mimo-v2.6-flash            PASS  309B MoE, agentic coding
#   cline-free/solar-mini4                PASS  compact 35B MoE
#   cline-free/muse-spark-1.3-contributor FAIL  read-only: never edited either
#                                                file, ran out of time in
#                                                iteration 2. NOT ASSIGNED.
#
# The free list is a rotating promotion, so it is re-read from
# https://api.cline.bot/api/v1/ai/cline/recommended-models rather than assumed.
# If an id in GROUP_MODEL 404s at spawn, reassign from VERIFIED below -- do not
# fall back to a paid model and do not "fix" it by pointing an agent at the
# local nemotron: GPU time is reserved for the coordinator (~4.5 GiB of 8 GiB).
# ---------------------------------------------------------------------------

# Proven on this host, in preference order. AO_FALLBACK forces one for all.
VERIFIED = [
    "cline-free/mimo-v2.6-flash",
    "cline-free/step-5-preview",
    "cline-free/solar-mini4",
]

# Deliberate assignment, not a round-robin. The three approval-gated groups
# (sec, ledger, pay) and spec do judgement-heavy review against acceptance
# criteria, so they get the strongest verified model. The rest are split
# across the remaining two on purpose: each free id is a separate quota bucket,
# so concentrating all eleven on one id means one exhausted bucket takes the
# whole team down again -- the exact failure mode of the old single-model setup.
GROUP_MODEL = {
    "plat":   "cline-free/mimo-v2.6-flash",
    "net":    "cline-free/mimo-v2.6-flash",
    # TEMPORARY 2026-10-09: cline-free/step-5-preview returned
    # INFERENCE_CAP_ERROR 429 (daily free limit, resets ~2026-10-10 15:45 PDT,
    # measured 2026-10-09 19:13 on the pay shift). The four step-5 groups are
    # split across the two buckets that still answered a real probe at
    # totalCost:0 (mimo MIMO-OK, solar SOLAR-OK). REVERT when step-5 refills:
    # probe it first, then restore sec/ledger/pay/spec -> step-5-preview below.
    "sec":    "cline-free/mimo-v2.6-flash",
    "ledger": "cline-free/solar-mini4",
    "pay":    "cline-free/mimo-v2.6-flash",
    "comm":   "cline-free/solar-mini4",
    "field":  "cline-free/mimo-v2.6-flash",
    "sim":    "cline-free/solar-mini4",
    "ops-a":  "cline-free/mimo-v2.6-flash",
    "ops-b":  "cline-free/solar-mini4",
    "spec":   "cline-free/solar-mini4",
}

FALLBACK = os.environ.get("AO_FALLBACK")  # force one verified id for every group
MODEL = os.environ.get("AO_MODEL")        # deliberate experiment override
PROVIDER = "cline"
REASONING = os.environ.get("AO_REASONING", "medium")


def model_for(g):
    """The free Cline model this group runs on.

    Precedence: AO_MODEL (explicit experiment) > AO_FALLBACK (force one) >
    GROUP_MODEL (the assignment above) > first VERIFIED.
    """
    if MODEL:
        return MODEL
    if FALLBACK:
        return FALLBACK
    return GROUP_MODEL.get(g, VERIFIED[0])


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


def ensure_worktree(g):
    """Return wt-<g>, creating it if missing. Safe against a /tmp wipe.

    A reboot (or any /tmp clean) removes the worktree DIRECTORY while the
    ai-<g> branch and the stale `git worktree` registration survive. Two
    measured failures on 2026-10-09: `worktree add -b ai-<g>` dies because the
    branch already exists, and a nudge handed cline a --cwd that did not exist,
    so ledger produced 0 bytes of events and looked "dead". Reuse the existing
    branch, fast-forwarding it to origin/main so the session starts from the
    current tree; only create a branch when there is none.
    """
    wt = worktree(g)
    if os.path.isdir(wt):
        return wt
    br = "ai-%s" % g
    subprocess.run(["git", "-C", ROOT, "worktree", "prune"], check=False)
    has = subprocess.run(["git", "-C", ROOT, "show-ref", "--verify", "--quiet",
                          "refs/heads/%s" % br]).returncode == 0
    if has:
        subprocess.run(["git", "-C", ROOT, "worktree", "add", wt, br], check=True)
        # ff-only: fails harmlessly if the branch has diverged; the session
        # merges main itself, as its brief instructs.
        subprocess.run(["git", "-C", wt, "merge", "--ff-only", "origin/main"],
                       check=False, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    else:
        subprocess.run(["git", "-C", ROOT, "worktree", "add", "-b", br, wt,
                        "origin/main"], check=True)
    return wt


def spawn(g):
    d, wt = run_dir(g), worktree(g)
    if os.path.exists(os.path.join(d, "pid")):
        pid = int(open(os.path.join(d, "pid")).read())
        if pid_alive(pid):
            print("%-6s already running pid=%d" % (g, pid)); return
    # fresh worktree from origin/main - never from local main
    ensure_worktree(g)
    log = os.path.join(d, "events.jsonl")
    env = dict(os.environ, AO_GROUP=g)
    cmd = ["cline", "--json", "--cwd", wt, "--timeout", str(TIMEOUT),
           "-t", str(TIMEOUT + 300), "--thinking", REASONING,
           "--provider", PROVIDER, "--model", model_for(g),
           open(prompt_path(g)).read()]
    with open(log, "ab") as out:
        p = subprocess.Popen(cmd, stdout=out, stderr=subprocess.STDOUT,
                             start_new_session=True, env=env)
    open(os.path.join(d, "pid"), "w").write(str(p.pid))
    open(os.path.join(d, "nudges"), "w").write("0")
    # Record the model beside the pid. A spawn that reports only a pid cannot be
    # audited later for which model actually ran, and "wrong model" has been the
    # cause of two separate team-wide deaths here.
    open(os.path.join(d, "model"), "w").write(model_for(g) + "\n")
    print("%-6s spawned pid=%d model=%s -> %s" % (g, p.pid, model_for(g), log))


def pid_alive(pid):
    """True only if the pid exists AND is not a zombie.

    os.kill(pid, 0) succeeds for a zombie - the entry stays in the table until
    the parent reaps it - so a defunct pid read as "alive" and spawn reported
    ops-b as "already running" when it had been dead for 12 hours. State Z is
    what marks a corpse.
    """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    try:
        with open("/proc/%d/stat" % pid) as fh:
            fields = fh.read().rsplit(")", 1)[-1].split()
        return not (len(fields) > 0 and fields[0] == "Z")
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
    """Return (status, detail). status in never|running|stuck|done|error|dead.

    Ordering matters and was the source of two live bugs:

    * "done" wins even if the process is still up (the final message can flush after
      the pid exits), and
    * an "error" event only means failure if the process is actually gone or stale.
      plat, ledger and spec all logged non-fatal errors ("operation timed out", "hook
      dispatch failed") while still working; treating any error as terminal made the
      watcher nudge a LIVE session and would have started a second agent in the same
      worktree.
    """
    pf = os.path.join(run_dir(g), "pid")
    if not os.path.exists(pf):
        return "never", "not spawned"
    pid = int(open(pf).read())
    ev = events(g)
    alive = pid_alive(pid)
    age = _age_min(ev)

    # 1. completed - highest priority, regardless of liveness
    for e in reversed(ev):
        if e.get("type") == "agent_event" and e["event"].get("type") == "done":
            reason = e["event"].get("reason", "?")
            # reason is not always "completed": plat and ledger ended with a done event
            # carrying reason "error", which must NOT be reported as success.
            if reason in ("completed", "finished"):
                return "done", reason
            return "error", "done with reason=%s" % reason
        if e.get("type") == "run_result":
            fr = e.get("finishReason")
            return ("done", "completed") if fr == "completed" else ("error", str(fr)[:80])

    # 2. error is terminal only when the process is gone or has stopped making progress
    for e in reversed(ev):
        if e.get("type") == "error":
            if not alive:
                return "error", e.get("message", "")[:80]
            if age > STUCK_MIN:
                return "error", e.get("message", "")[:80]
            # live and active: fall through to the running/stuck classification below
            break
        if e.get("type") == "run_result" and e.get("finishReason") != "completed":
            if not alive:
                return "error", str(e.get("finishReason"))[:80]
            break

    # 3. liveness
    if not alive:
        if not ev:
            return "dead", "no events, process gone"
        if age > STUCK_MIN:
            return "dead", "process gone, no terminal event"
        # process just exited; give the log a moment to flush
        return "running", "exited, awaiting final events"

    if not ev:
        return "running", "starting"

    it = [e["event"].get("iteration", 0) for e in ev
          if e.get("type") == "agent_event" and e["event"].get("type") == "iteration_start"]
    det = "iter %s, idle %.1fm" % (it[-1] if it else "?", age)
    if age > STUCK_MIN:
        return "stuck", det
    return "running", det


def _age_min(ev):
    """Minutes since the newest event, or 1e9 when there are none."""
    if not ev:
        return 1e9
    try:
        import datetime as dt
        return ((dt.datetime.now(dt.timezone.utc)
                 - dt.datetime.fromisoformat(ev[-1]["ts"].replace("Z", "+00:00")))
                .total_seconds() / 60)
    except Exception:
        return 1e9


def nudge(g, reason):
    """Fresh invocation into the same worktree. Resume is broken in 3.0.60."""
    d, wt = run_dir(g), worktree(g)
    n = int(open(os.path.join(d, "nudges")).read()) if os.path.exists(os.path.join(d, "nudges")) else 0
    if n >= MAX_NUDGES:
        print("%-6s nudge limit (%d) reached - needs a human" % (g, MAX_NUDGES)); return
    # A nudge REPLACES the session it supersedes. The old pid may still be
    # alive: `state()` returns "error" for a LIVE session whose latest event is
    # a non-fatal provider error and whose output went idle past STUCK_MIN, and
    # "stuck" for a live one with no new event. Spawning without retiring the
    # old process puts two agents in the same worktree editing the same files.
    # Measured 2026-10-05: a guard pass nudged 8 live groups and doubled the
    # team. So terminate the old process GROUP first (SIGTERM, then SIGKILL
    # after 5s), verified dead, before the new invocation is started.
    pf = os.path.join(d, "pid")
    if os.path.exists(pf):
        try:
            oldpid = int(open(pf).read())
        except (ValueError, OSError):
            oldpid = None
        if oldpid is not None and pid_alive(oldpid):
            try:
                pgid = os.getpgid(oldpid)
            except OSError:
                pgid = None
            if pgid is not None:
                try:
                    os.killpg(pgid, signal.SIGTERM)
                except OSError:
                    pass
                deadline = time.time() + 5
                while time.time() < deadline and pid_alive(oldpid):
                    time.sleep(0.2)
                if pid_alive(oldpid):
                    try:
                        os.killpg(pgid, signal.SIGKILL)
                    except OSError:
                        pass
                    time.sleep(0.5)
                if pid_alive(oldpid):
                    print("%-6s old pid %d refused to die - NOT spawning a duplicate" % (g, oldpid)); return
                print("%-6s retired old pid %d" % (g, oldpid))
    # create the worktree BEFORE spending a nudge: a missing /tmp worktree used
    # to burn the nudge on a cline process that died at once (2026-10-09).
    ensure_worktree(g)
    n += 1
    open(os.path.join(d, "nudges"), "w").write(str(n))
    msg = (
        "You are the %s session for ALWAYS ON, continuing after a stall (%s).\n\n"
        "You have no memory of the earlier run. Do this first, before anything else:\n"
        "  1. cd %s && git status --short && git log --oneline -3\n"
        "  2. Re-read your brief: %s\n"
        "  3. Re-read the acceptance criteria for your assigned items in "
        "README-ACTION_ITEMS/status-and-references.md\n\n"
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
                              "-t", str(TIMEOUT + 300), "--thinking", REASONING,
                              "--provider", PROVIDER, "--model", model_for(g), msg],
                             stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
    open(os.path.join(d, "pid"), "w").write(str(p.pid))
    # same audit rule as spawn(): the recorded model and the run_result model
    # must agree. nudge used to leave the file absent or stale, which is how
    # ledger ended up with no model record at all (2026-10-09).
    open(os.path.join(d, "model"), "w").write(model_for(g) + "\n")
    print("%-6s nudged #%d (pid %d) model=%s - %s" % (g, n, p.pid, model_for(g), reason))


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
    for f in sorted(glob.glob(os.path.join(ROOT, "agents/COORDINATION (README UPDATES)/proposals/*.md"))):
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


def cmd_guard():
    """One recovery pass, then EXIT. Designed to be run every 5 minutes.

    Why not just use `watch` on a timer: `watch` LOOPS until every session
    settles, and a systemd timer would then overlap the next run. Worse, the
    operator's team died unattended on 2026-10-04 and the guard that was
    supposed to notice was a Cline cron job whose store had been emptied --
    ~/.cline/cron/ contained only reports/, no jobs. So recovery now lives in
    a systemd USER timer with Linger=yes, which survives logout and reboot and
    does not depend on any session being alive to run it.

    The pass is deliberately conservative:
      * a group that is running or stuck is LEFT ALONE. Never start a second
        agent in a worktree that already has a live one -- that is how you get
        two sessions colliding on the same files.
      * a group that is dead or errored gets `nudge`, which resumes in the
        SAME worktree, and is capped by MAX_NUDGES so a permanently broken
        group cannot be respawned forever every 5 minutes.
      * when NOTHING at all is running, the whole team is respawned and the
        per-group nudge counters are reset, because they are spent and would
        otherwise block recovery indefinitely.
    """
    states = {g: state(g) for g in GROUPS}
    cmd_status()

    live = [g for g in GROUPS if states[g][0] in ("running", "stuck")]
    broken = [g for g in GROUPS if states[g][0] in ("error", "dead", "never")]

    if not live:
        # Whole team is down. Reset the nudge budget or every group would be
        # permanently un-nudgeable after MAX_NUDGES uses.
        for g in GROUPS:
            open(os.path.join(run_dir(g), "nudges"), "w").write("0")
        print("\nno live sessions: respawning all %d" % len(GROUPS))
        for g in GROUPS:
            spawn(g)
        return

    if broken:
        print("\nrecovering: %s" % ", ".join("%s(%s)" % (g, states[g][0]) for g in broken))
        for g in broken:
            # Recover ONLY groups whose process is verifiably GONE.
            # nudge() retires a live pid first, but the automated guard must
            # not be the thing that decides a live (if idle) agent is finished:
            # on 2026-10-05 a guard pass nudged 8 live groups on the strength
            # of non-fatal provider errors. Live agents are left to `watch`
            # and the operator; the guard's job is the dead, not the slow.
            pf = os.path.join(run_dir(g), "pid")
            gone = True
            try:
                oldpid = int(open(pf).read())
                gone = not pid_alive(oldpid)
            except (ValueError, OSError):
                gone = True
            if gone:
                nudge(g, "5-minute guard: process gone (%s)" % states[g][0])
            else:
                print("%-6s live pid kept; needs a manual nudge if it stays %s" % (g, states[g][0]))
    else:
        print("\nall %d sessions healthy; nothing to do" % len(live))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    args = sys.argv[2:]
    if cmd == "spawn":
        for g in (args or GROUPS):
            spawn(g)
    elif cmd == "status": cmd_status()
    elif cmd == "watch":  cmd_watch(int(args[0]) if args else 60)
    elif cmd == "nudge":  nudge(args[0], args[1] if len(args) > 1 else "manual")
    elif cmd == "state1":
        s, d = state(args[0])
        print("%s %s" % (s, d))
    elif cmd == "guard":  cmd_guard()
    elif cmd == "report": cmd_report()
    elif cmd == "stop":   cmd_stop()
    else: raise SystemExit(__doc__)
