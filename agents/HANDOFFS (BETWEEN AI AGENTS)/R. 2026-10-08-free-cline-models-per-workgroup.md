# R. 2026-10-08 — Free Cline models assigned per workgroup; laguna retired

**Scope:** model assignment for the 11 ALWAYS ON workgroup agents.
**Operator instruction:** *"Revise the documents so that the team members work from the free
Cline language model you assign to them, and ensure that you are using reliable free coding
models… do not rely on laguna — make an executive decision and use free models hosted by Cline
that are good at agentic coding in Linux."*

## Decision

`poolside/laguna-s-2.1:free` is **retired**. Every workgroup now runs a **free Cline-provider
model**, assigned per group. The assignment lives in `supervise.py` (`GROUP_MODEL`, with
`model_for()` resolving it); the runbook and roster documents carry the human-readable copy.

| Group | Model |
|---|---|
| `plat` `net` `field` `ops-a` | `cline-free/mimo-v2.6-flash` |
| `comm` `sim` `ops-b` | `cline-free/solar-mini4` |
| `sec` `ledger` `pay` `spec` | `cline-free/step-5-preview` |

Two judgement calls, made deliberately:

1. **The approval-gated groups get the strongest verified model.** `sec`, `ledger` and `pay` are
   required to stop and wait for operator approval, and `spec` reviews acceptance criteria. A
   weaker model reporting "done" on work it never actually changed is the expensive failure here —
   it consumes operator trust, not just tokens.
2. **The models are spread across three ids rather than consolidated onto one "best" model.** Each
   free id is a separate quota bucket. All eleven on one id reproduces the original single point
   of failure: one exhausted bucket kills the whole team. Spread out, a dry bucket costs at most
   its own groups, and `AO_FALLBACK=<id>` moves them without touching the rest.

## Evidence — how the models were chosen

The free list was read from the live endpoint rather than assumed, because it is a rotating
promotion:

```
curl -sS https://api.cline.bot/api/v1/ai/cline/recommended-models
```

That returned four free ids. Each was given a **real two-part task** on this host, not a
"reply OK" prompt — a prompt that only tests connectivity would have passed a model that cannot
edit files, which is precisely the failure mode that matters here:

> *Fix a wrong-operator bug (`add()` returned `a - b`, must return the sum), overwrite a second
> file with exact content, then run the fix and report the output.*

| Model | Result |
|---|---|
| `cline-free/mimo-v2.6-flash` | **PASS** — fixed both files, `finishReason=completed`, `totalCost=0` |
| `cline-free/step-5-preview` | **PASS** — fixed both files, `finishReason=completed`, `totalCost=0` |
| `cline-free/solar-mini4` | **PASS** — fixed both files, `finishReason=completed`, `totalCost=0` |
| `cline-free/muse-spark-1.3-contributor` | **FAIL** — read files, edited neither, timed out in iteration 2 |

All three passing models were then given a harder Linux agentic task (run a `systemctl` command,
count its output with `wc -l`, capture a second value from `uname -m`, write both to a file,
verify by reading it back). All three completed and wrote correct, verified values —
`TIMERS=5` / `MODEL=x86_64`. That is the evidence behind the assignment, and it is why
`muse-spark-1.3-contributor` is excluded despite being free and listed.

**Do not use `cline-free/muse-spark-1.3-contributor`.** A read-only agent that reports success
without changing anything is worse than a crashed one: it consumes a shift and looks healthy.
## Trap retracted — this one was actively harmful

The 2026-10-05 runbook asserted *"cline --json IGNORES --model and reads from globalState.json
instead; the model fix in globalState.json is the actual fix."* **That is false**, and following
it caused harm: it sent coordinators to edit `~/.cline/data/globalState.json`, which governs the
**operator's own interactive sessions**, instead of the script that spawns agents.

Measured on cline 3.0.60 with `actModeClineModelId = cline-free/step-5-preview`:

```
cline --json --provider cline --model cline-free/solar-mini4 ...
  → run_result: model id "cline-free/solar-mini4"
```

`--model` **is** honoured in `--json` mode. `globalState.json` was left untouched. The trap is
marked RETRACTED in the runbook with the measurement beside it, so a future session does not
reinstate it.

Also corrected: the runbook's "the model has a DAILY QUOTA, wait it out" advice described laguna
specifically. It is retired with the model. Section 4 of the runbook now diagnoses in order —
*which model actually ran* → *is the id still offered* → *only then* rate limiting — because
"assume quota" had been used to explain deaths that were actually a stale `.pyc` or a 404.

## Audit trail added

Wrong-model has now caused two separate team-wide deaths (the `space-bunny-alpha` 404s, and the
laguna quota wall), and neither was diagnosable after the fact. Each spawn now:

- prints the model it used,
- records it in `/tmp/ao-sessions/<group>/model`,
- and that file must agree with the `"model"` id on the `run_result` line in `events.jsonl`.

A mismatch means a stale `__pycache__/*.pyc` held the old constants —
`rm -rf /ALWAYSON/scripts/orchestration/__pycache__/` and respawn. The stale `.pyc` files
(`rotate-agents`, `compile-proposals`, dated 2026-10-05) were present on this host and were
cleared during this change.


## Files changed

| File | Change |
|---|---|
| `scripts/orchestration/supervise.py` | `GROUP_MODEL` + `VERIFIED` + `model_for()`; laguna default removed; both spawn and nudge paths use `model_for(g)`; model recorded and printed |
| `scripts/orchestration/rotate-agents.py` | docstring: per-group free Cline assignment replaces "the only model verified working is laguna" |
| `agents/START_RESTART-AGENTIC_TEAM.md` | new §1B (models, verification, overrides); §4 rewritten to diagnose model-first; §7 marked superseded; the `--json`-ignores-`--model` trap RETRACTED |
| `agents/SESSION ASSIGNMENTS (AI WORKGROUPS)/00-START-HERE.md` | "Which model each session runs on" table + the muse-spark exclusion |
| `agents/SESSION ASSIGNMENTS (AI WORKGROUPS)/12-ORCHESTRATOR-PROMPT.md` | model verification step; do-not-edit-globalState warning |

No section file under `agents/COORDINATION (README UPDATES)/` was touched, so **README.md was not
recompiled** and no work ID was renumbered. The compile gate was already `DIFFERS` before this
change, for an unrelated reason — a bulk path rename left doubled
`agents/COORDINATION (README UPDATES) (README UPDATES)/` strings. That is still open and is
neither caused by nor fixed by this work.

## Overrides

| Variable | Effect |
|---|---|
| `AO_MODEL=<id>` | one model for every group (deliberate experiment) |
| `AO_FALLBACK=<id>` | force one **verified** id for every group — the quota-shift lever |
| `AO_REASONING=<lvl>` | `none` / `low` / `medium` / `high` / `xhigh` (default `medium`) |

Both overrides were exercised after the edit and resolve correctly, with `AO_MODEL` taking
precedence over `AO_FALLBACK`, which takes precedence over `GROUP_MODEL`.

## Standing rule for whoever reads this next

Before assigning a new model id to any group, run it through the two-part edit-and-run task
described above. A model that only *talks* about editing is not an agentic coding model, and this
team's whole output is file edits. When the free list rotates, reassign from tested ids — do not
substitute a paid model, and never point a workgroup at the local nemotron: GPU time is reserved
for the coordinator (~4.5 GiB of the 8 GiB card).


## Follow-up, same day — the dashboard is now a live channel

Operator instruction: *"Keep the dashboard open and use it to communicate any required decisions
as well as regular updates."*

The dashboard was fully built but **nothing ran it**. There was no systemd unit at all, so port
8766 was dead, the metrics file was four days stale (last record 2026-10-04), `index.html` was
from 2026-10-05, and the "Save decisions" button failed with *writer unreachable*. A channel the
operator is told to rely on must not depend on anyone remembering to launch it.

**Made it self-sustaining:**

| Unit | Role |
|---|---|
| `ao-dashboard.service` | serves the page on 127.0.0.1:8766; `Restart=always`; enabled |
| `ao-dashboard-refresh.timer` | hourly metrics snapshot + HTML re-render; enabled |

Both enabled, both survive reboot (Linger=yes). Verified by killing the writer process: it came
back and answered `/health` in under 8 seconds.

**Added a standing updates channel.** New `scripts/orchestration/dashboard-note.py` appends to
`artifacts/dashboard/updates.jsonl` and re-renders immediately, so an update does not wait for the
hourly tick. Levels: `info`, `done`, `warn`, `action`. Append-only on purpose — a note cannot be
clobbered by a concurrent write.

Deliberately kept separate from the decisions panel. That panel is a queue of things *waiting on
the operator*; mixing routine progress into it would hide the items that actually block work. The
page now reads, top to bottom: **Team updates** → **Decisions you have already given** →
**Decisions needed from you**.

**A wrong reading, corrected.** While wiring this up I reported "31 items blocked on an operator
decision" — inherited from the old runbook text. That was wrong, and the dashboard proved it:
`answers.json` holds 31 substantive answers, all dated 2026-10-04, and `decision-state.json`
marks all 31 as answered. The decisions panel was correctly empty. Several are direct
authorisations to proceed — `PAY-01` is simply "OK"; `SEC-01` says put the credentials in KDE
Wallet; `OPS-30` says set up the pCloud KDE Wallet entry and the operator will supply the
password.

The real defect was that those authorisations were **invisible**: once an item left the queue it
appeared nowhere, so an agent could not see permission it had already been given, and a human
reading the page would conclude nothing had been decided. A new panel now lists all 31 with their
text, and the runbook states plainly that an empty decisions panel means *nothing is blocked*, not
*nothing has been decided*.

**Verification:** all four endpoints return 200; all three panels render (6 notes, 31
authorisations, 0 outstanding); the renderer is deterministic across repeated runs; an invalid
level is rejected with rc=2. No section file was touched, so `README.md` was not recompiled — the
compile gate was already `DIFFERS` before this work, for the unrelated doubled-path reason noted
above.

