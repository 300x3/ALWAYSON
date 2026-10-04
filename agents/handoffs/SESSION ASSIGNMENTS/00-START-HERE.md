# ALWAYS ON — AI session assignments

Eleven sessions. Each owns a set of section files and a set of work items from
README §19.1. **README.md is compiled from `agents/COORDINATION/` — nobody hand-edits it.**

> **Path change (2026-10-10).** These folders were consolidated into `agents/`. Every path
> below is `agents/COORDINATION/…`. The old top-level `COORDINATION/` no longer exists on
> `main`; a prompt still naming it will fail immediately.

## Files here

| File | Session | Work group | Open items |
|---|---|---|---:|
| `01-plat.prompt.md` | Platform, install and runtime | `PLAT` | 4 |
| `02-net.prompt.md` | Networks, adapters and isolation | `NET` | 4 |
| `03-sec.prompt.md` | Secrets, credentials and identity | `SEC` | 3 |
| `04-ledger.prompt.md` | Ledger, accounting and provenance | `LEDGER` | 7 |
| `05-pay.prompt.md` | Payments, sales and storefront | `PAY` | 7 |
| `06-comm.prompt.md` | Community, federation and local AI | `COMM` | 7 |
| `07-field.prompt.md` | Field, radio and drones | `FIELD` | 14 |
| `08-sim.prompt.md` | Simulation and fabrication | `SIM` | 14 |
| `09-ops-a.prompt.md` | Backup, restore and monitoring | `OPS-A` | 13 |
| `10-ops-b.prompt.md` | Install, provisioner, inventory, scripts | `OPS-B` | 21 |
| `11-spec.prompt.md` | Specification review, sections 1–3 and 6 | `SPEC` | 0 |
| | | **Total** | **94** |

All **94** open items in §19.1 are assigned to exactly one session, with **no item assigned
twice** (verified against `main`). `SPEC` has no items: it reviews its three sections for
accuracy and records anything new it finds.

This table replaces an earlier version that claimed 60 items and listed COMM as having
none. That was wrong on both counts — 34 items were never assigned, including all 7 COMM
items.

## Two rules that are not negotiable

**1. §19 is single-writer.** All eleven sessions record progress in §19, which makes it the
one file where sessions collide. So sessions **do not edit**
`agents/COORDINATION/19-current-status-and-outstanding-work/section.md`. They write
`agents/COORDINATION/proposals/<group>-<ITEM-ID>.md` and a twelfth compiler session merges
those into §19.2. Never hand-edit README.md.

**2. Stop for operator approval.** `SEC`, `LEDGER` and `PAY` touch credentials, ledger keys
and money movement. Those sessions prepare and prove, then **stop and wait**. README §4.1
rule 14.

## Running the sessions

Use the supervisor. It spawns, monitors, detects stalls, nudges and stops:

```bash
cd /ALWAYSON
git fetch origin
python3 scripts/orchestration/supervise.py spawn              # all 11
python3 scripts/orchestration/supervise.py status             # health check
python3 scripts/orchestration/supervise.py watch              # poll + auto-nudge
python3 scripts/orchestration/supervise.py report             # results
python3 scripts/orchestration/supervise.py stop               # kill everything
```

Each session gets its own git worktree under `/tmp/ao-sessions/wt-<group>`, branched from
`origin/main`, so concurrent sessions cannot collide on the filesystem.

### Cheaper first run

Prove the loop with `01-plat` and `02-net` (4 items each, low blast radius) before
committing to all 11:

```bash
python3 scripts/orchestration/supervise.py spawn plat net
python3 scripts/orchestration/supervise.py watch
```

## Why nudges, not resumes

Verified against **cline 3.0.60** on this host: `--id <taskId>` **cannot** resume a session.
With `--json` it fails `JSON output mode requires a prompt argument`; without `--json` it
fails `interactive mode requires a TTY`. So un-sticking a session means a **nudge** — a fresh
invocation into the *same worktree* with a continuation prompt that tells the agent to
re-read `git status` and its brief first. The worktree holds the state, so losing the
conversation is survivable. Each session is nudged at most 3 times, then flagged for a human.

## Before you start any of them

1. `cd /ALWAYSON && git fetch origin` — local `main` may be behind and dirty.
2. `python3 agents/COORDINATION/tools/compile.py --check` — must print `identical`.
3. If it prints `DIFFERS`, someone hand-edited `README.md`. Do **not** overwrite it: run
   `split.py` to fold their edit into the section file first.

Note that `--check` compares a generated artifact against its own input. In a worktree
branched from `origin/main` it will pass on arrival and always will — it is a guard against
later hand-edits, not proof that the tree was clean to begin with.

## Not included

A **twelfth session** — the compiler. It owns no section content: it merges
`agents/COORDINATION/proposals/*.md` into §19.2, runs `compile.py --check`, requires
`identical`, and proves the GitHub sync. Run it after every group.
