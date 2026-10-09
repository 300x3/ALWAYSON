DASHBOARD: http://127.0.0.1:8766/

  Kept open in a browser for the operator. The KWin rule
  ~/.local/share/kwin/scripts/ao-browser-testing/ parks it bottom-left of the
  main monitor (DP-3) and stops it stealing focus, so it needs no manual
  placement.

  THREE PANELS, top to bottom:

    1. Team updates            standing progress channel. The team posts here.
    2. Decisions you have      the operator's recorded authorisations, read
       already given           from answers.json. Sessions are expected to act
                               on these; they are not waiting on anything.
    3. Decisions needed        only items still blocked on the operator. Empty
       from you                means nothing is blocked.

  Keep 1 and 2 distinct. Routine progress goes in "Team updates"; if it were
  mixed into the decisions panel it would hide the items that actually block
  work.

  POSTING AN UPDATE (from /ALWAYSON):

    python3 scripts/orchestration/dashboard-note.py "text"
    python3 scripts/orchestration/dashboard-note.py --who plat --level done "PLAT-03 closed"
    python3 scripts/orchestration/dashboard-note.py --who coordinator \
        --level action "text needing the operator now"
    python3 scripts/orchestration/dashboard-note.py --list 10

  Levels: info (default), done, warn, action. `action` is the loudest and is
  for something the operator must look at now. The note re-renders the page
  immediately, so it does not wait for the hourly tick.

  WHAT KEEPS IT ALIVE (added 2026-10-08 -- before this there was NO unit, so
  the dashboard only ran when someone remembered to launch it by hand, and by
  2026-10-08 port 8766 was dead, the metrics were four days stale, and the
  "Save decisions" button failed with the writer unreachable):

    ao-dashboard.service        serves the page on 127.0.0.1:8766, Restart=always.
                                Also accepts POST /answers (operator decisions),
                                POST /spawn and POST /stop (team control).
    ao-dashboard-refresh.timer  hourly: metrics snapshot + HTML re-render.

  Both are enabled and survive reboot (Linger=yes). Check with:

    systemctl --user status ao-dashboard.service
    systemctl --user list-timers ao-dashboard-refresh.timer

  If the page will not load, check the writer FIRST -- the page is served by
  that process, not by the HTML file on disk.

  NOTE ON THE DECISIONS PANEL: it is derived from section 19.1, so it shrinks
  as items close, and an answered item leaves the queue. As of 2026-10-08 all
  31 historical decisions are answered (2026-10-04) and appear in panel 2 --
  several are direct authorisations to proceed. Do not read an empty panel 3
  as "nobody has decided anything"; check panel 2.


---------------------------------------------------------------------
1. PASTE THIS INTO A BLANK CLINE CLI SESSION
---------------------------------------------------------------------

Work in /ALWAYSON on the ALWAYS ON project. The agent rotation may be
running, idle, or half-dead. Diagnose FIRST, then restart only what is
actually down. You are the COORDINATOR and you run on the LOCAL model
(section 1A). The workgroup agents run on FREE Cline models (1B).

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

--- 1B. WORKGROUP AGENT MODELS: free Cline models, assigned per group ---

UPDATED 2026-10-08. poolside/laguna-s-2.1:free is RETIRED -- do not use
it, do not put it in a document, do not "restore" it. It was an
OpenRouter free tier with a daily quota wall that killed seven sessions
on 2026-10-03 and paced every shift after that.

Workgroup agents now run on FREE models served by the Cline provider
itself, selected with --model at spawn. The assignment lives in
supervise.py (GROUP_MODEL); this section is the human-readable copy.

  VERIFIED FREE MODELS (measured 2026-10-08, cline 3.0.60, $0 cost)
  -------------------------------------------------------------------
  Each was given a real two-part task: fix a wrong-operator bug, write a
  file, then run the fix and report the output. All three edited both
  files correctly and finished with finishReason=completed, totalCost=0.

    cline-free/mimo-v2.6-flash     PASS  309B MoE, agentic coding
    cline-free/step-5-preview      PASS  StepFun flagship, sparse MoE
    cline-free/solar-mini4         PASS  compact 35B MoE
    cline-free/muse-spark-1.3-contributor
                                   FAIL  read-only: edited neither file,
                                        timed out in iteration 2.
                                        NOT ASSIGNED - do not use it.

  ASSIGNMENT
  -------------------------------------------------------------------
    step-5-preview    sec, ledger, pay, spec
                      (judgement-heavy review against acceptance
                       criteria; sec/ledger/pay also gate on operator
                       approval, so a weaker model risks a wrong "done")
    mimo-v2.6-flash   plat, net, field, ops-a
    solar-mini4       comm, sim, ops-b

  Why spread across three ids instead of one "best" model: each free id
  is a SEPARATE quota bucket. Concentrating all eleven groups on one id
  recreates the original failure -- one exhausted bucket takes the whole
  team down at once. Splitting means a bucket running dry costs at most
  its own groups, and AO_FALLBACK moves them.

  The free list is a rotating promotion. Re-read it rather than assuming:

    curl -sS https://api.cline.bot/api/v1/ai/cline/recommended-models

  Read the "free" array. If an assigned id has gone, reassign from the
  VERIFIED list above -- after testing it with the two-part task
  described here. Never substitute a paid model, and never point a
  workgroup at the local nemotron: GPU time is reserved for coordination
  and one nemotron instance already costs ~4.5 GiB of the 8 GiB card.

  OVERRIDES (deliberate experiments only, documented before use)
  -------------------------------------------------------------------
    AO_MODEL=<id>        one model for every group
    AO_FALLBACK=<id>     force one VERIFIED id for every group
    AO_REASONING=<lvl>   none|low|medium|high|xhigh (default medium)

  Every spawn records the model beside its pid in
  /tmp/ao-sessions/<group>/model and prints it. If a team-wide death is
  ever traced to the wrong model again, that file is the audit trail --
  the run_result line in events.jsonl is the confirmation.

--- 1C. WORKGROUP AGENTS: diagnose, then restart only what is down ---

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
    HISTORICAL, 2026-10-05 only. ledger was spawned against
    stealth/space-bunny-alpha, which 404s on OpenRouter ("No endpoints
    found"), and died at iteration 1. That model is gone from every
    script; ledger now runs on cline-free/step-5-preview.
    If a 404 still names a model, the fix is the model, not the group:
    check the assigned id against section 1B and reassign it. To respawn:
      1. Check the assignment: grep -A4 'GROUP_MODEL' scripts/orchestration/supervise.py
      2. Clear its stale state:
         rm -f /tmp/ao-sessions/ledger/pid
         echo 0 > /tmp/ao-sessions/ledger/nudges
      3. Spawn it fresh:
         python3 scripts/orchestration/supervise.py spawn ledger
      4. Check: tail -5 /tmp/ao-sessions/ledger/events.jsonl should show
         run_result with model: cline-free/step-5-preview
         The model on that line MUST match the one in
         /tmp/ao-sessions/ledger/model. If they disagree, the spawn used
         a stale value -- delete scripts/orchestration/__pycache__/ and
         respawn (see the STALE __pycache__ trap below).

    NOTE: spawning ledger starts a NEW 2-hour shift that runs in parallel
    with whichever workgroup agent is currently active (sec). The rotation
    timer is set to single-agent pacing, but a manually-spawned group is a
    one-off override. After ledger finishes, re-merge its branch:
      cd /ALWAYSON && git merge --no-edit local/ai-ledger
    Then run the compile gate:
      python3 agents/COORDINATION (README UPDATES)/tools/compile.py --check
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
  They write proposals to agents/COORDINATION (README UPDATES)/proposals/ instead.
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

UPDATED 2026-10-08. The old "daily quota wall" advice described
poolside/laguna-s-2.1:free and is RETIRED with it. That model is gone
from every script; nothing here should be read as permission to put it
back.

The workgroup models are now free ids on the Cline provider (section 1B).
They measured totalCost:0 and did not hit a daily wall during
verification. So do NOT assume a death is quota exhaustion -- that
assumption cost real shifts before. Diagnose in this order:

  1. WHICH MODEL actually ran, and was it the assigned one?
     cat /tmp/ao-sessions/<group>/model          # what was requested
     tail -5 /tmp/ao-sessions/<group>/events.jsonl | grep -o '"model":{[^}]*}'
                                                  # what really ran
     The two MUST match. A mismatch means a stale cached value was used:
       rm -rf /ALWAYSON/scripts/orchestration/__pycache__/
     then respawn. This is the STALE __pycache__ trap below.

  2. Is the id still offered? The free list is a rotating promotion.
       curl -sS https://api.cline.bot/api/v1/ai/cline/recommended-models
     Read the "free" array. If the assigned id is absent, reassign from the
     VERIFIED list in section 1B -- after testing it. Do not substitute a
     paid model.

  3. Only then consider rate limiting. If a message says a free usage
     limit was reached, report the wait time and stop. Do not burn nudges
     on it -- three nudges against a limit that has not lifted spends the
     budget for nothing. AO_FALLBACK=<verified id> moves the affected
     groups to a different bucket without touching the others.

A 404 naming a model is a MODEL problem, not a group problem: fix the
assignment. An empty response or an abort is a session problem: save
uncommitted work from the worktree FIRST, then nudge.

NEVER point a workgroup agent at the local nemotron as a "fix". GPU time
is reserved for the coordinator, and one nemotron instance already costs
~4.5 GiB of the 8 GiB card.

For any OTHER error (404, empty response, auth): save uncommitted work
first, then force the next shift:

  python3 scripts/orchestration/rotate-agents.py rotate

The 2-hour cap bounds each group's share of the shift. Do not lengthen
shifts or run groups in parallel without an operator instruction. Each
group spawns on its assigned FREE Cline model -- see section 1B for the
table; supervise.py (GROUP_MODEL) is authoritative, AO_MODEL and
AO_FALLBACK override it only for deliberate experiments. Never point a
workgroup agent at the local model: GPU time is reserved for
coordination, and one nemotron instance already costs ~4.5 GiB of the
8 GiB card.

---------------------------------------------------------------------
--- END OF CURRENT INSTRUCTIONS (2026-10-05). Old 11-parallel notes follow
--- for history only. Do not act on anything below this line.
---

TRAPS ADDED 2026-10-05:
  * STALE __pycache__: supervise.py caches its module constants in
    __pycache__/*.pyc. If you edit GROUP_MODEL, AO_MODEL or the
    fallback, DELETE the .pyc or Python will import the stale value.
    Always: rm -rf /ALWAYSON/scripts/orchestration/__pycache__/
    Confirmed present on this host 2026-10-08 (rotate-agents and
    compile-proposals .pyc files, dated 2026-10-05).
  * "--json IGNORES --model" -- RETRACTED 2026-10-08. This trap was
    wrong and acting on it was actively harmful: it sent coordinators to
    edit ~/.cline/data/globalState.json, which governs the OPERATOR'S
    own interactive sessions, instead of the script that spawns agents.
    Measured: with actModeClineModelId set to cline-free/step-5-preview,
    a spawn with --model cline-free/solar-mini4 reported
    run_result model id "cline-free/solar-mini4". --model IS honoured in
    --json mode on 3.0.60. The script is the fix; leave globalState.json
    alone unless the operator asks.
  * 404 vs timeout: a 404 "No endpoints found" is a MODEL problem
    (reassign in section 1B -- no globalState edit needed). A timeout
    after N iterations is usually a SLOW model on a long task, not
    quota: muse-spark-1.3-contributor did exactly this and was
    rejected for it. Do not confuse the three.

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
  They write proposal files to agents/COORDINATION (README UPDATES)/proposals/ instead.
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
7. IF THE TEAM LOOKS DEAD, CHECK THIS FIRST   [SUPERSEDED 2026-10-08]
---------------------------------------------------------------------

The text that was here described poolside/laguna-s-2.1:free and its
daily quota. That model is RETIRED and the section has been replaced by
section 4 above, which keeps the parts that still apply and drops the
quota-first assumption. Read section 4, not this.

Only one thing here is still unconditionally true and is worth repeating,
because losing /tmp work is unrecoverable:

  SAVE UNCOMMITTED WORK FIRST, BEFORE ANY RESTART.

  Worktrees live in /tmp. A reboot, a wipe, or a supervisor that stops the
  wrong thing destroys anything not committed.

    for g in plat net sec ledger pay comm field sim ops-a ops-b spec; do
      cp -n /tmp/ao-sessions/wt-$g/agents/COORDINATION (README UPDATES)/proposals/*.md \
         /ALWAYSON/agents/COORDINATION (README UPDATES)/proposals/ 2>/dev/null
    done
    cd /ALWAYSON && git add "agents/COORDINATION (README UPDATES)/proposals/" \
      && git commit -m "save: proposals from live worktrees"

  Note the worktrees were all missing on this host on 2026-10-08 (git
  worktree list showed every wt-* as prunable) while the ai-* branches
  were already merged into main. Check `git worktree list` before
  assuming there is worktree state to save.

The old closing advice -- "run the sessions in smaller batches, not all
11 at once" -- is still correct, and is now structural rather than
advisory: the rotation runs ONE group per 2-hour shift, and the three
model ids are deliberately split across groups so no single bucket
carries the whole team.

---------------------------------------------------------------------
8. MERGING SESSION WORK (the compiler pass)
---------------------------------------------------------------------

After sessions finish, their branches must be merged and their proposals
folded into the README. Both are done by the orchestrator, one at a
time, with the compile gate checked after each step:

  cd /ALWAYSON
  git merge --no-edit local/ai-<group>     # or the pushed origin/ai-<group>
  python3 agents/COORDINATION (README UPDATES)/tools/compile.py --check   # must say identical

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
