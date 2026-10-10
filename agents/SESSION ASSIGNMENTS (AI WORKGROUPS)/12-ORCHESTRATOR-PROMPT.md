# Orchestrator prompt — run and supervise all 11 group sessions

Work in `/ALWAYSON`. **Do not touch the shared tree's uncommitted files.** Local `main` is
behind and dirty, with work belonging to other sessions — never rebase, stash, `checkout`,
`clean` or `git add -A` it.

## The dashboard is how the operator hears from you

`http://127.0.0.1:8766/` is kept open, parked bottom-left of the main monitor by a KWin rule.
It is served by `ao-dashboard.service` (`Restart=always`, enabled) and refreshed hourly by
`ao-dashboard-refresh.timer`. **Post to it as you work — do not wait to be asked.**

```bash
python3 scripts/orchestration/dashboard-note.py "what you did"
python3 scripts/orchestration/dashboard-note.py --who plat --level done "PLAT-03 closed with evidence"
python3 scripts/orchestration/dashboard-note.py --who coordinator --level action "needs you now"
python3 scripts/orchestration/dashboard-note.py --list 10
```

Levels: `info`, `done`, `warn`, `action`. Use `action` only for something the operator must look
at immediately. Each note re-renders the page at once.

The page has three panels. Keep them straight:

1. **Team updates** — routine progress. Post here.
2. **Decisions you have already given** — the operator's recorded authorisations from
   `answers.json`. Sessions are expected to act on these; they are *not* waiting on anything.
   All 31 historical decisions are answered (2026-10-04) and several are direct permission to
   proceed, e.g. `PAY-01` "OK", `SEC-01` put the credentials in KDE Wallet, `OPS-30` set up the
   pCloud KDE Wallet entry and the operator fills the password. Check this panel before you
   report something as blocked.
3. **Decisions needed from you** — only genuinely outstanding items. Derived from §19.1, so it
   shrinks as items close. **An empty panel 3 does not mean nothing has been decided** — it means
   nothing is currently blocked. Read panel 2 before saying the operator has not decided.

Never post routine progress into the decisions panel, and never post a decision request as a
plain `info` note — it would be read as status and missed.


## 1. Preflight

```bash
cd /ALWAYSON && git fetch origin
python3 agents/COORDINATION (README UPDATES)/tools/compile.py --check   # must print identical
```

If `DIFFERS`, someone hand-edited `README.md`. Run `split.py` to fold their edit into the
correct section file. Never overwrite it.

## 2. Prove the loop on two sessions first

```bash
python3 scripts/orchestration/supervise.py spawn plat net
python3 scripts/orchestration/supervise.py watch
```

Do not spawn all 11 until these two complete cleanly.

### Models: free Cline ids, assigned per group — do not change them casually

Revised 2026-10-08. Every group runs a **free Cline-provider model** chosen by `supervise.py`
(`GROUP_MODEL`); `poolside/laguna-s-2.1:free` is retired. The assignment is evidence-based, not
preference: all four Cline free ids were run through a real edit-and-run task on this host, three
passed at `totalCost:0`, and `cline-free/muse-spark-1.3-contributor` **failed** (read files, edited
nothing, timed out in iteration 2) so it is excluded.

- `plat net field ops-a` → `cline-free/mimo-v2.6-flash`
- `comm sim ops-b` → `cline-free/solar-mini4`
- `sec ledger pay spec` → `cline-free/step-5-preview` (the approval-gated groups; a weaker model
  here risks reporting "done" on work that was never actually changed)

The three ids are separate quota buckets, so a spread-out assignment means one exhausted bucket
costs at most its own groups. Do not "optimise" this by putting all eleven on the model you liked
best — that rebuilds the single point of failure that killed the team before.

**Verify the model actually ran, do not trust the spawn line:**

```bash
cat /tmp/ao-sessions/<group>/model                                  # requested
tail -5 /tmp/ao-sessions/<group>/events.jsonl | grep -o '"model":{[^}]*}'   # actual
```

They must match. If they do not, delete `scripts/orchestration/__pycache__/` and respawn — a
stale `.pyc` holds the old constants. A 404 naming a model means the id left the free promotion:
re-read `curl -sS https://api.cline.bot/api/v1/ai/cline/recommended-models`, then reassign from a
verified id after testing it. Never substitute a paid model, and never point a workgroup at the
local nemotron — GPU time is reserved for the coordinator (~4.5 GiB of 8 GiB).

Note the 2026-10-05 trap "`cline --json` ignores `--model`, edit globalState.json" is **retracted**
and was wrong: `--model` is honoured in `--json` on 3.0.60 (measured). Do not edit
`~/.cline/data/globalState.json` — that is the operator's own interactive config.

## 3. Run the rest

```bash
python3 scripts/orchestration/supervise.py spawn comm sec ledger pay field sim ops-a ops-b spec
python3 scripts/orchestration/supervise.py watch
```

## What supervision means

`supervise.py` reads each session's `--json` event stream and classifies it:

| State | Meaning | Action |
|---|---|---|
| `running` | events within 12 min | leave alone |
| `stuck` | no new event for 12 min, no terminal event | auto-nudge (max 3) |
| `done` | `done` event, `reason: completed` | read its proposals |
| `error` | `error` event or non-completed finish | investigate, then nudge or stop |
| `dead` | process gone with no terminal event | restart with a nudge |

**You check in.** `watch` handles the mechanical polling, but between polls you must read
what each session actually did: open its `events.jsonl`, read the last `done` text, and read
the proposal files it wrote. A session that reports success while its proposals are empty,
or that wrote a file outside its own section, has gone wrong — catch that yourself rather
than trusting the exit code.

**Nudges, not resumes.** `--id` cannot resume in cline 3.0.60 (verified: with `--json` it
errors `JSON output mode requires a prompt argument`; without, `interactive mode requires a
TTY`). Un-sticking means a fresh invocation into the same worktree with a continuation
prompt. The nudge prompt tells the agent to re-read `git status` and its brief first, so a
context-free session does not start over. After 3 nudges, stop and bring it to the operator.

**Stop a session that is out of bounds.** Kill it if it edits `README.md`, edits §19
directly, touches another group's section file, renumbers any ID, or pushes without proving
the sync. Then read its diff before restarting it.

## 4. After every group — the compiler pass

Each session writes `agents/COORDINATION (README UPDATES)/proposals/<group>-<ITEM-ID>.md`. You merge them
into the §19.2 rows of `README-ACTION_ITEMS/status-and-references.md` with the
evidence, then:

```bash
python3 agents/COORDINATION (README UPDATES)/tools/compile.py --check   # require: identical
```

`DIFFERS` means a session hand-edited `README.md` — fold it in with `split.py`, never
overwrite.

Merge order: PLAT, NET, SEC, LEDGER, PAY, COMM, FIELD, SIM, OPS-A, OPS-B, SPEC.

## 5. Prove every push

Sessions commit and push **only files they own**. After each push, verify yourself — do not
take "pushed" as evidence:

```bash
git fetch origin
git rev-parse --short HEAD; git rev-parse --short origin/main
curl -sS -o /dev/null -w '%{http_code}\n' https://raw.githubusercontent.com/300x3/ALWAYSON/main/README.md
# Work items live in status-and-references.md since ebdf215 -- grep'ing README.md
# for an ITEM-ID returns 0 on a healthy push (measured 2026-10-09, caused a
# false alarm). Grep the tracker, not the README:
curl -sS https://raw.githubusercontent.com/300x3/ALWAYSON/main/README-ACTION_ITEMS/status-and-references.md | grep -c '<ITEM-ID>'
```

Report the SHA and the HTTP code.

## Hard stops — bring these to the operator, do not proceed

Anything touching payments, pricing or money movement; ledger keys or provenance records
already committed externally; secrets, credentials or tokens; backup or restore data, or
deleting anything; live radio, serial or network configuration; a public port or firewall
policy; another session's uncommitted work.

`SEC`, `LEDGER` and `PAY` are expected to hit these — that is by design. Prepare the change,
prove it as far as is safe, then stop and wait for explicit human approval (README §4.1
rule 14).

## 6. Final report

Per session: items closed with evidence, items blocked and why, files changed, commit SHAs,
GitHub HTTP codes, anything found belonging to another group, and anything you had to stop.
