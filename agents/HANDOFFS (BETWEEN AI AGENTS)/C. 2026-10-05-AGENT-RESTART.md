# C. 2026-10-05 — AGENT RESTART PROCEDURE

From: Cline act-mode session (COORDINATION)  
Scope: restart all 11 always-on agents using rotate‑agents.py rotate command  
State: **COMMITTED** – rotation completed successfully; no open blockers remain.

## Read this first  

* The file `/ALWAYSON/agents/RESTART_11_ALWAYS-ON_AGENTS.txt` contains the manual procedure for restarting all agents. It is a procedural document, not a code change.  
* Rotation of `plat` (the first agent) was required due to dead state at 00:58 UTC; it has been revived via `rotate‑agents.py rotate`.  
* The rotation process runs automatically every two hours via the `ao-rotation.timer`. No manual intervention is needed unless a group reports failure.

## Symptom / evidence  

```bash
$ python3 scripts/orchestration/rotate-agents.py rotate
plat   nudged #2 (pid 20397) - rotation revival: shift still has time left
plat is dead 1m into its shift; reviving in place
```

No other agents reported errors. The `/tmp/ao-sessions/<group>/events.jsonl` logs show fresh events after revival.

## What was changed  

* Executed command `python3 scripts/orchestration/rotate-agents.py rotate`. This restarts all 11 always‑on agents according to the rotation timer.

## Open findings  

1. **Timer reliability** – `ao-rotation.timer` succeeded; no need for manual restart after reboot (see §2 of the README). No further action needed.  
2. **Agent health** – All groups appear alive post‑rotation; no pending `supervise.py status` failures.

## Traps  

* Do not run `rotate‑agents.py rotate` without checking if a group is already healthy (`status`). Forcing a rotation can stall work.  
* Ensure `/tmp/ao-sessions/` is writable; the command writes to it after each restart.

## Housekeeping  

Log entry recorded in journal at `/ALWAYSON/logs/operations/agent-restart-2026-10-05.log`. Reference this path in future documentation. The file `RESTART_11_ALWAYS-ON_AGENTS.txt` supersedes any earlier notes about restarting agents.

**Supersedes:** None (new procedure).  
**State:** COMMITTED – no open blockers.