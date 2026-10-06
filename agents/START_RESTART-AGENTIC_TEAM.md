DASHBOARD: http://127.0.0.1:8766/


---------------------------------------------------------------------
1. PASTE THIS INTO A BLANK CLINE CLI SESSION
---------------------------------------------------------------------

Work in /ALWAYSON on the ALWAYS ON project. The agent rotation may be
running, idle, or half-dead. Diagnose FIRST, then restart only what is
actually down. You are the COORDINATOR and you run on the LOCAL model
(section 1A). The workgroup agents run on FREE cloud models (1B).

--- 1A. COORDINATOR: verify the local model is yours ---

  lms ps

You must see nvidia/nemotron-3-nano-4b IDLE (ctx ~100000, parallel 2).
If it is missing, the supervisor reloads it by itself within a minute
(ao-lmstudio.service, Restart=always). Wait and re-check; only escalate
if it stays down 5 minutes.

Prove it answers before you coordinate anything:

  echo "Reply with exactly: COORDINATOR-OK" | timeout 100 lms chat nvidia/nemotron-3-nano-4b:2 -p - 2>/dev/null | tail -2

TRAP (measured 2026-10-05): the bare name nvidia/nemotron-3-nano-4b
answers "Model not found". The loaded identifier carries the :2 suffix
(visible in lms ps). Always use the full nvidia/nemotron-3-nano-4b:2.

The API on 127.0.0.1:1234 is token-gated (401 without a token). The
token lives ONLY in KDE Wallet as lmstudio-api-key and already matches
Cline's stored key -- verified 2026-10-05, no rotation occurred. Never
print it, never put it in a file, never pass it on a command line.
Per-invocation local runs use: cline -P lmstudio (verified exit 0).
Do NOT change lastUsedProvider away from cline; the operator's cloud
default stays.

Your job as coordinator: triage rotation state, decide handoffs, merge
proposals, update the dashboard. You do NOT do workgroup tasks yourself
-- you hand them to the shift agent.

--- 1B. WORKGROUP AGENTS: diagnose, then restart only what is down ---

  1. python3 scripts/orchestration/rotate-agents.py status
  2. systemctl --user is-active ao-rotation.timer
  3. python3 scripts/orchestration/supervise.py status

Interpret the three together:

  * status names a group with time left + timer active + that group
    running = HEALTHY. Report that and stop. Do not respawn.
  * status says idle + timer inactive = SHUT DOWN. Restart with:
      systemctl --user enable --now ao-rotation.timer
      systemctl --user start ao-rotation.service
    Then wait 60s and re-run the three checks. The first shift is plat.
    * status names a group but supervise says error/dead/never for it =
    MID-SHIFT DEATH. Revive with:
      python3 scripts/orchestration/rotate-agents.py rotate
    That nudges the current group in its own worktree. Wait 60s, check
    the last 5 lines of /tmp/ao-sessions/<group>/events.jsonl for fresh
    output.

  SPECIAL CASE -- ledger is DEAD (404, pre-fix):
    ledger was spawned before the globalState.json model fix and died
    immediately with "No endpoints found for stealth/space-bunny-alpha".
    It is NOT a mid-shift rotation. To respawn it:
      1. Verify the model fix is in place (see CRITICAL MODEL FIX above)
      2. Clear its stale state:
         rm -f /tmp/ao-sessions/ledger/pid
         echo 0 > /tmp/ao-sessions/ledger/nudges
      3. Spawn it fresh:
         python3 scripts/orchestration/supervise.py spawn ledger
      4. Check: tail -5 /tmp/ao-sessions/ledger/events.jsonl should show
         run_result with model: poolside/laguna-s-2.1:free

    NOTE: spawning ledger starts a NEW 2-hour shift that runs in parallel
    with whichever workgroup agent is currently active (sec). The rotation
    timer is set to single-agent pacing, but a manually-spawned group is a
    one-off override. After ledger finishes, re-merge its branch:
      cd /ALWAYSON && git merge --no-edit local/ai-ledger
    Then run the compile gate:
      python3 agents/COORDINATION (README UPDATES) (README UPDATES)/tools/compile.py --check
  * timer active but rotation.json is stale or missing = state was wiped
    (reboot clears /tmp). The timer's OnStartupSec+Persistent=true
    replays the missed run and starts plat by itself within ~2 minutes.
    Wait, then re-check. Only start manually if nothing appears.

Then verify the agent is real, not a stale pid file:

  p=$(cat /tmp/ao-sessions/<group>/pid); ls /proc/$p

If that fails, the pid file lied -- treat as mid-shift death above.

If the events log shows a quota message ("free usage limit"), the free
model is exhausted: report the wait time and stop. Do not burn nudges.
For any OTHER error (404, empty response, auth, abort): save uncommitted
work from /tmp/ao-sessions/wt-<group>/ first, then force the next shift
with rotate-agents.py rotate and report what you found.

Background reading, in order:
  agents/SESSION ASSIGNMENTS (AI WORKGROUPS)/00-START-HERE.md
  agents/SESSION ASSIGNMENTS (AI WORKGROUPS)/12-ORCHESTRATOR-PROMPT.md
  README.md section 19 (the work log)

---------------------------------------------------------------------
2. HOW THE ROTATION WORKS (2026-10-05 and later)
---------------------------------------------------------------------

  * Order: plat, net, sec, ledger, pay, comm, field, sim, ops-a, ops-b,
    spec, then back to plat. Dependency order, not alphabetical.
  * Each group gets a 2-hour shift. Timer ao-rotation.timer fires every 2h
    plus 2min after boot, calling rotate-agents.py rotate: stop current,
    spawn next, record handoff in /tmp/ao-sessions/rotation.json.
  * Reboot wipes /tmp, so the timer's OnStartupSec plus Persistent=true
    replays the missed run and starts plat automatically. Nothing manual
    is needed after a reboot.
  * Manual commands (from /ALWAYSON):
      rotate-agents.py status    who is current, time left
      rotate-agents.py rotate    force a handoff now
      rotate-agents.py stop      stop agent, clear rotation
      supervise.py status        per-group health
      supervise.py nudge GROUP   revive one dead group in its worktree

---------------------------------------------------------------------
3. RULES THE ROTATION DEPENDS ON
---------------------------------------------------------------------

* Each session works in its own git worktree under /tmp/ao-sessions/.
* NEVER start a second agent in a live worktree. nudge() retires the old
  process group (SIGTERM, then SIGKILL after 5s, verified dead) before
  spawning. If the old pid refuses to die, nudge REFUSES to spawn. This
  was a real incident on 2026-10-05, not a hypothetical.
* The guard recovers ONLY processes that are verifiably gone. It never
  touches a live agent. The guard's job is the dead, not the slow.
* Sessions NEVER edit README.md directly, and NEVER edit section 19.
  They write proposals to agents/COORDINATION (README UPDATES) (README UPDATES)/proposals/ instead.
* Uncommitted work lives in /tmp and dies on reboot. Commit early, often.
* Never renumber a work ID. Never git add -A. Never revert another
  session's work.
* SEC, LEDGER and PAY stop and wait for the operator on credentials,
  ledger keys or money. That is not a fault.
* Nudge budget MAX_NUDGES=3 per group. A group that hits it needs a
  human. A full-team respawn resets the counters.

---------------------------------------------------------------------
4. IF THE AGENT LOOKS DEAD, CHECK THIS FIRST
---------------------------------------------------------------------

The model is FREE-TIER (poolside/laguna-s-2.1:free) with a DAILY QUOTA.
Quota death looks like:

  "You've reached today's free usage limit for this model. Try again in Xh Ym"

No restart helps; the rotation revives the shift when quota returns. If it
persists a whole day, report it instead of burning nudges.

BEFORE ANY SPAWN: VERIFY THE MODEL FIX IS IN PLACE:
  python3 -c "import json; d=json.load(open('/home/scottw/.cline/data/
    globalState.json')); print(d.get('actModeClineModelId'),
    d.get('planModeClineModelId'))"
  Both must show: poolside/laguna-s-2.1:free
  If either shows stealth/space-bunny-alpha → DO NOT SPAWN. See
  CRITICAL MODEL FIX section above.

For any OTHER error (404, empty response, auth): save uncommitted work
first, then force the next shift:

  python3 scripts/orchestration/rotate-agents.py rotate

The 2-hour cap IS the quota protection. Do not lengthen shifts or run
groups in parallel without an operator instruction. All shift agents
spawn on the FREE cloud model (poolside/laguna-s-2.1:free, the
supervise.py default -- AO_MODEL overrides only for deliberate
experiments). Never point a workgroup agent at the local model: GPU
time is reserved for coordination, and one nemotron instance already
costs ~4.5 GiB of the 8 GiB card.

---------------------------------------------------------------------
--- END OF CURRENT INSTRUCTIONS (2026-10-05). Old 11-parallel notes follow
--- for history only. Do not act on anything below this line.
---

TRAPS ADDED 2026-10-05:
  * STALE __pycache__: supervise.py caches MODEL in
    __pycache__/supervise.cpython-314.pyc. If you edit AO_MODEL or the
    default MODEL constant, DELETE the .pyc or Python will use the stale
    value. Always: rm -rf /ALWAYSON/scripts/orchestration/__pycache__/
  * cline --json IGNORES --model: cline 3.0.60 in --json mode ignores
    the --model CLI flag and reads from globalState.json instead. The
    model fix in globalState.json is the actual fix, not the --model
    flag in supervise.py.
  * 404 vs timeout: a 404 "No endpoints found" is a MODEL problem
    (fix globalState.json). A timeout after N iterations is QUOTA pacing
    (wait for daily reset). Do not confuse the two.

---------------------------------------------------------------------
1. HOW TO RESTART THE ALWAYS-ON AGENTS FROM A BLANK CLINE CLI SESSION  [CURRENT]
=====================================================================
HISTORICAL - SUPERSEDED 2026-10-05. Kept so a future session can see what
changed and why, not as instructions.


Everything you need is in the GitHub repo. A blank session with no memory
of the previous conversation can pick this up.

---------------------------------------------------------------------
1. OPEN A BLANK CLINE CLI SESSION AND PASTE THIS
---------------------------------------------------------------------

Work in /ALWAYSON on the ALWAYS ON project. Start by running:

  cd /ALWAYSON && git pull --shortstat
  python3 scripts/orchestration/supervise.py status

That shows the health of the 11 group sessions. Then read
"agents/SESSION ASSIGNMENTS (AI WORKGROUPS)/00-START-HERE.md" for the full
brief, and "12-ORCHESTRATOR-PROMPT.md" for how to supervise them.

---------------------------------------------------------------------
2. THE FIVE COMMANDS THAT MATTER
---------------------------------------------------------------------

All are run from /ALWAYSON:

  python3 scripts/orchestration/supervise.py status   <- health of all 11
  python3 scripts/orchestration/supervise.py watch    <- poll + auto-restart stalls
  python3 scripts/orchestration/supervise.py spawn    <- start all 11 (only if none running)
  python3 scripts/orchestration/supervise.py report   <- results + proposals written
  python3 scripts/orchestration/supervise.py stop     <- kill everything

Start with:   status
Then:         watch        (this is the one that runs unattended)

---------------------------------------------------------------------
3. WHAT THE STATUSES MEAN
---------------------------------------------------------------------

  running  still working, leave it alone
  stuck    idle over 12 minutes - the watcher auto-nudges it (max 3 nudges)
  error    it crashed - the watcher restarts it into the same worktree
  dead     process gone - the watcher restarts it
  done     finished, read its output

---------------------------------------------------------------------
4. IMPORTANT RULES
---------------------------------------------------------------------

* Each session works in its own git worktree under /tmp/ao-sessions/.
  They cannot collide on the filesystem.

* Sessions NEVER edit README.md directly, and NEVER edit section 19.
  They write proposal files to agents/COORDINATION (README UPDATES) (README UPDATES)/proposals/ instead.
  A 12th "compiler" session merges those into the README.

* A wiped /tmp (reboot) destroys the worktrees. Any session that had not
  committed yet loses its work - that is why sessions should commit and
  push early and often.

* Never renumber a work ID. Never git add -A. Never revert another
  session's work.

* SEC, LEDGER and PAY sessions are SUPPOSED to stop and wait for you on
  anything touching credentials, ledger keys or money. That is not a fault.

---------------------------------------------------------------------
5. READ FIRST IF YOU ARE A NEW SESSION
---------------------------------------------------------------------

  agents/SESSION ASSIGNMENTS (AI WORKGROUPS)/00-START-HERE.md
  agents/SESSION ASSIGNMENTS (AI WORKGROUPS)/12-ORCHESTRATOR-PROMPT.md
  README.md section 19 (the work log)

---------------------------------------------------------------------
6. SAFE ORDER OF OPERATIONS
---------------------------------------------------------------------

  a) git pull
  b) python3 scripts/orchestration/supervise.py status
  c) if nothing is running:  python3 scripts/orchestration/supervise.py spawn
  d) python3 scripts/orchestration/supervise.py watch

Then leave it running and check back periodically.

---------------------------------------------------------------------
7. IF THE TEAM LOOKS DEAD, CHECK THIS FIRST
---------------------------------------------------------------------

The model in use is a FREE-TIER model (poolside/laguna-s-2.1:free).
It has a DAILY QUOTA. When it runs out, sessions die with:

  "You've reached today's free usage limit for this model.
   Try again in 22h 46m"

This is the most common reason the team dies. It is NOT a stall and no
amount of restarting helps - the message says how long to wait.

If you see that message, do this:

  1. Save any uncommitted work FIRST. It lives in /tmp and a reboot or
     a wipe destroys it:
       for g in plat net sec ledger pay comm field sim ops-a ops-b spec; do
         cp -n /tmp/ao-sessions/wt-$g/agents/COORDINATION (README UPDATES) (README UPDATES)/proposals/*.md \
            /ALWAYSON/agents/COORDINATION (README UPDATES) (README UPDATES)/proposals/ 2>/dev/null
       done
       cd /ALWAYSON && git add agents/COORDINATION (README UPDATES) (README UPDATES)/proposals/ && git commit -m "save"
  2. Wait out the quota, or switch to a model with quota.
  3. Restart the dead sessions:
       for g in plat net sec ledger pay comm field sim ops-a ops-b spec; do
         echo 0 > /tmp/ao-sessions/$g/nudges
         python3 scripts/orchestration/supervise.py nudge $g "quota reset"
       done

To avoid this: run the sessions in smaller batches, not all 11 at once.

---------------------------------------------------------------------
8. MERGING SESSION WORK (the compiler pass)
---------------------------------------------------------------------

After sessions finish, their branches must be merged and their proposals
folded into the README. Both are done by the orchestrator, one at a
time, with the compile gate checked after each step:

  cd /ALWAYSON
  git merge --no-edit local/ai-<group>     # or the pushed origin/ai-<group>
  python3 agents/COORDINATION (README UPDATES) (README UPDATES)/tools/compile.py --check   # must say identical

If it says DIFFERS, a session edited a section file and did not
recompile. That is expected and safe: run compile.py to regenerate, then
verify no work ID was lost or duplicated before committing.

Then fold the proposals in:

  python3 scripts/orchestration/compile-proposals.py

That moves closed items into 19.2, appends evidence to updated items, and
never renumbers anything. It prints how many moved; if it prints 0
closed when proposals exist, something is wrong.

---------------------------------------------------------------------
9. DASHBOARD - progress table, line graph, and decisions needed
---------------------------------------------------------------------

Open it:

  google-chrome file:///ALWAYSON/artifacts/dashboard/index.html

It shows three things:

  * the counts: outstanding (19.1) vs completed (19.2), per work group
  * a line graph of that split over time, one line per group
  * "Decisions needed from you" at the BOTTOM - 31 items blocked on an
    operator decision that no agent can resolve

The question list is derived from section 19.1 automatically, so it shrinks
as items close. It never shows an item that is already closed.

To refresh it manually:

  /ALWAYSON/scripts/orchestration/dashboard.sh

It records an hourly snapshot and re-renders. Metrics live in
artifacts/dashboard/metrics/19-progress.jsonl - one JSON record per run,
collapsed to one per hour. History started 2026-10-03; there is nothing
before that and nothing is back-filled.

NOTE: the history only grows while something re-runs dashboard.sh. A flat
graph means no new snapshot was taken, not that no work happened - check
"git" and "gate" on the same line.

---------------------------------------------------------------------
10. OTHER THINGS SET UP SINCE (so you know they exist)
---------------------------------------------------------------------

SECTION 19.2 COMPILER PASS
  python3 scripts/orchestration/compile-proposals.py
  Sessions never edit section 19. They write proposals; this merges them.
  It is IDEMPOTENT - running it twice changes nothing. If it prints
  "already applied, skipped: N", that is correct, not a failure.

ASSERTING HOST VERIFIER
  bash scripts/validation/verify-host-baseline.sh
  Replaces the old 12.3 block that could not fail. Exits non-zero on any
  failure and names the check. Currently 6 passed, 0 failed.

DAILY 30-MIN REPORT
  /tmp/work30.log - session health, open/completed counts, compile gate,
  git sync, and the next ungated candidates.

ROOT MAINTENANCE (only when I ask for it)
  pkexec /ALWAYSON/scripts/operations/0700-maintenance-pkexec.sh
  Already run once on 2026-10-04: apparmor-utils installed, logrotate
  policy synced, 0 parse errors.
