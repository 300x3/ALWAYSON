# Orchestrator prompt — paste this into a Cline session to run all 11 groups

Work in `/ALWAYSON` on the README workflow assignments. First run `git fetch origin`
and create a fresh isolated worktree — **not** the shared tree, which has uncommitted
files belonging to other sessions and must not be rebased, stashed or `git add -A`'d.
Then read `00-START-HERE.md` in this folder, and execute every `*.prompt.md` in it:
create one worktree per group branched from `origin/main` via
`git -C /ALWAYSON worktree add -b ai-<group> ~/ao-<group> origin/main`, run
`cline --cwd ~/ao-<group>` with each prompt, and merge the results back in order.

Branch from `origin/main`, **never** from local `main` — local `main` predates the
COORDINATION split and has no `COORDINATION/` directory.

Merge order: PLAT, NET, SEC, LEDGER, PAY, COMM, FIELD, SIM, OPS-A, OPS-B, SPEC.

After **every** group, run `python3 COORDINATION/tools/compile.py --check` and require
`identical`. If it prints `DIFFERS`, a session hand-edited `README.md` — run `split.py`
to fold their edit into the section file, never overwrite it.

Each session edits only its own `COORDINATION/*/section.md`, moves completed items from
§19.1 to §19.2 with evidence, never renumbers an existing work ID, pushes only files it
owns, proves GitHub sync after every push (fetch, confirm the SHA is in `origin/main`,
then curl the raw file on GitHub and grep for the edit — report the SHA and the `http`
code, not "pushed"), and stops for operator approval on anything touching payments, ledger keys,
secrets, backup data or live radio settings — prepare it and stop.

## Cheaper first run

Start with `01-plat` and `02-net` (1 and 4 items, low blast radius) to prove the
spawn-and-merge loop before committing to all 11.
