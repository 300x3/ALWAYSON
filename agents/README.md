# `agents/` — everything AI agents need to work this project

Consolidated 2026-10-10. Three previously separate top-level folders now live here:

| Was | Is now | Tracked in git? |
|---|---|---|
| `COORDINATION/` | `agents/COORDINATION/` | **Yes** — it is build input |
| `COORDINATION BETWEEN AI/` | `agents/handoffs/` | **No — deliberately ignored** |
| `agents/AGENTS.md` | unchanged | Yes |

## The one rule that matters

**`agents/COORDINATION/` is source. `agents/handoffs/` is never source.**

- `agents/COORDINATION/` holds the 21 section files that `README.md` is compiled from,
  plus `MANIFEST.md` (the fixed section order) and `tools/`. It is tracked, diffable and
  reviewed. **Never hand-edit `README.md`** — edit the section file and recompile.
- `agents/handoffs/` holds session-to-session narrative. **This repository is public**
  and those files name the host, the operator account, versions and open security
  findings, so the whole folder is ignored by `.gitignore`. Four of them were tracked
  and pushed by mistake on 2026-10-01 and untracked afterwards; untracking stopped
  further exposure but did **not** remove them from history.

The old folder name contained spaces, which silently broke `git check-ignore` whenever
the path was quoted — git treats the quote characters as part of the pattern. The new
path has no spaces. Never reintroduce a space in a path you intend to `check-ignore`.

## The README compile workflow

Run from the repository root (`/ALWAYSON`):

```bash
python3 agents/COORDINATION/tools/compile.py --check   # verify, writes nothing
python3 agents/COORDINATION/tools/compile.py          # rebuild README.md
python3 agents/COORDINATION/tools/split.py            # README.md -> section files
```

`--check` must print `identical`. If it prints `DIFFERS`, someone hand-edited
`README.md`; run `split.py` to fold their edit into the correct section file, never
overwrite it.

## Work IDs

Items in README §19.1 are keyed by group prefix then a number within the group, so an
ID can never collide and closing an item never renumbers another:

`PLAT` `NET` `SEC` `LEDGER` `PAY` `COMM` `FIELD` `SIM` `OPS`

**Never renumber an existing ID.** If an item is partly done, keep the row and record
what remains — do not close it and lose the remainder. Take the next free number in
the group for anything genuinely new.

## Session assignments

`agents/handoffs/SESSION ASSIGNMENTS/` holds the per-session runbooks and the
orchestrator prompt. Because it sits inside the ignored folder, **these runbooks are
local only and are not on GitHub.** Copy them to the agent that must run them.

## Rules

`AGENTS.md` in this folder holds the project rules. The authoritative operation and
governance document is `/ALWAYSON/README.md`; its §16.4 documents this compile
workflow and the recovery when `--check` reports `DIFFERS`.