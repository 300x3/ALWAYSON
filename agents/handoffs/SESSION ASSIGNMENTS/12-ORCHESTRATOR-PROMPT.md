# Orchestrator prompt — run and supervise all 11 group sessions

Work in `/ALWAYSON`. **Do not touch the shared tree's uncommitted files.** Local `main` is
behind and dirty, with work belonging to other sessions — never rebase, stash, `checkout`,
`clean` or `git add -A` it.

## 1. Preflight

```bash
cd /ALWAYSON && git fetch origin
python3 agents/COORDINATION/tools/compile.py --check   # must print identical
```

If `DIFFERS`, someone hand-edited `README.md`. Run `split.py` to fold their edit into the
correct section file. Never overwrite it.

## 2. Prove the loop on two sessions first

```bash
python3 scripts/orchestration/supervise.py spawn plat net
python3 scripts/orchestration/supervise.py watch
```

Do not spawn all 11 until these two complete cleanly.

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

Each session writes `agents/COORDINATION/proposals/<group>-<ITEM-ID>.md`. You merge them
into `agents/COORDINATION/19-current-status-and-outstanding-work/section.md` §19.2 with the
evidence, then:

```bash
python3 agents/COORDINATION/tools/compile.py --check   # require: identical
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
curl -sS https://raw.githubusercontent.com/300x3/ALWAYSON/main/README.md | grep -c '<ITEM-ID>'
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
