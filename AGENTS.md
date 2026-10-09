# ALWAYSON — Project Rules for Agents

> Global always-on rules are injected in every session from
> `/home/scottw/.agents/AGENTS.md`. This file adds ALWAYS ON project-specific
> rules. Read it before every task; `/ALWAYSON/README.md` is the single
> authoritative architecture/operations/status document.

## The agents folder — one home for everything

- All agent rule files, coordination, handoff narratives, runbooks and
  dashboards live in **`/ALWAYSON/agents/`** — the single home after the Oct 6
  restructure. Nothing under `/ALWAYSON/` may reference the old names:
  `agents/handoffs/`, `agents/COORDINATION/`, `agents/GRADER/`, or any other
  stale folder.
- Path rules live in the rules folder itself
  (`agents/COORDINATION (README UPDATES)/16-scripts-and-operational-standards/section.md`
  §16.4 and §16.5) and are compiled into the README from the sections by
  `tools/compile.py` / `split.py`. **Never hand-edit `README.md`;** regenerate
  it from the sections instead (`--check` must print `identical`).
- Reference the folders, not the legacy names, in every script, runbook and rule
  file: `agents/SESSION ASSIGNMENTS (AI WORKGROUPS)`,
  `agents/HANDOFFS (BETWEEN AI AGENTS)`,
  `agents/COORDINATION (README UPDATES)/<nn-slug>/section.md`, and
  `proposals/` inside that folder.

## Layout (post-restructure)

| Path | Purpose |
|---|---|
| `agents/AGENTS.md` | this file |
| `README.md` | compiled master doc (regenerate only via tools/compile.py) |
| `agents/COORDINATION (README UPDATES)/` | per-section rules + evidence (section.md per section, MANIFEST.md) |
| `agents/HANDOFFS (BETWEEN AI AGENTS)/` | agent-to-agent handoff narratives (tracked) |
| `agents/SESSION ASSIGNMENTS (AI WORKGROUPS)/` | per-session assignment sheets |
| `agents/START_RESTART-AGENTIC_TEAM.md` | team restart entry point |
| `agents/COORDINATION (README UPDATES)/tools/` | split.py / compile.py (README <-> section round trip) |; `scripts/orchestration/` | collect-metrics.py / render-dashboard.py / supervise.py |
| `logs/operations/rules-review-agents-folder-2026-10-06.log` | rules-review journal |

## Handoff rules

- Handoffs go through `agents/HANDOFFS (BETWEEN AI AGENTS)/` only; the old
  `agents/handoffs/` name was renamed during the Oct 6 restructure and is retired.
  Treat section files in `agents/COORDINATION (README UPDATES)/` as the reference
  set; never overwrite them unilaterally — coordinate conflicts and keep one
  canonical writer per section.

## Focus rule — /ALWAYSON/README.md

- Agents must always focus on `/ALWAYSON/README.md` as the single authoritative
  architecture/operations/status document of the ALWAYSON project. Nothing else
  in the repo replaces it.
- This document is generated ONLY from the sections under
  `agents/COORDINATION (README UPDATES)/` by
  `python3 agents/COORDINATION (README UPDATES)/tools/compile.py`
  (`--check` must print `identical`). **Never hand-edit README.md.**
- Keep README.md up to date with its GitHub copy at
  https://filedn.com/l5JNexbL2ipFNaQcAkmV7lQ/**CURRENT**/site/index.html.
  Whatever diverges, reconcile to this local document (the agents' source of
  truth) and update the copy at that URL. Report the discrepancy to the
  operator immediately.
- If the GitHub copy at that URL is unreachable, stale, or belongs to a
  different project, treat the local README as authoritative and ask the
  operator for the correct sync target before making changes.

