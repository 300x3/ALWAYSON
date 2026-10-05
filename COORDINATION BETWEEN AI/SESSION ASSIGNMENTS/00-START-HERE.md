# ALWAYS ON — AI session assignments

Eleven sessions. Each owns a set of section files and a set of work items from
README §19.1. **README.md is compiled from `COORDINATION/` — nobody hand-edits it.**

## Files here

| File | Session | Open items |
|---|---|---:|
| `01-plat.prompt.md` | Platform, install and runtime | 1 |
| `02-net.prompt.md` | Networks, adapters and isolation | 4 |
| `03-sec.prompt.md` | Secrets, credentials and identity | 3 |
| `04-ledger.prompt.md` | Ledger, accounting and provenance | 4 |
| `05-pay.prompt.md` | Payments, sales and storefront | 3 |
| `06-comm.prompt.md` | Community, federation and local AI | 0 |
| `07-field.prompt.md` | Field, radio and drones | 8 |
| `08-sim.prompt.md` | Simulation and fabrication | 9 |
| `09-ops-a.prompt.md` | Backup, restore and monitoring | 11 |
| `10-ops-b.prompt.md` | Install, provisioner, inventory, scripts | 17 |
| `11-spec.prompt.md` | Specification review, sections 1–3 and 6 | 0 |

All 60 open items in §19.1 are assigned to exactly one session. Two sessions (COMM, SPEC)
have no open items — they exist to review their sections for accuracy and to record
anything new they find.

## Running a session

### Option A — dedicated worktree (recommended)

Each session gets its own checkout, so concurrent sessions cannot collide at all. **This
is the safe way to run eleven at once.**

```bash
# once, per session
git -C /ALWAYSON worktree add ~/ao-<group> main
cd ~/ao-<group>
cline --cwd ~/ao-<group> "$(cat '/ALWAYSON/COORDINATION BETWEEN AI/SESSION ASSIGNMENTS/01-plat.prompt.md')"
```

When it finishes, merge back in order and resolve one at a time:

```bash
cd /ALWAYSON && git pull --rebase
git checkout main && git merge ~/ao-plat
```

### Option B — shared tree, one at a time

Use this only when you are running sessions **sequentially**, because `/ALWAYSON` is a
shared working tree and each session must finish, commit and push before the next starts.

```bash
cd /ALWAYSON
git pull --rebase
cline --cwd /ALWAYSON "$(cat 'COORDINATION BETWEEN AI/SESSION ASSIGNMENTS/01-plat.prompt.md')"
```

### Option C — VS Code (ACP)

```bash
cline --acp --cwd /ALWAYSON
```

Then start a Cline session in VS Code and paste the contents of the `.prompt.md` file.

### Useful flags

| Flag | Effect |
|---|---|
| `-p` | Plan mode — read-only. Good for a first read-through. |
| `-i` | Interactive TUI, if you want to watch and intervene. |
| `--thinking high` | Better reasoning on the judgement-heavy items (SIM, FIELD, LEDGER). |
| `-t 3600` | Timeout in seconds. Recommended for the larger sessions. |

## Before you start any of them

1. `cd /ALWAYSON && git pull --rebase` — the local tree is behind remote.
2. `python3 COORDINATION/tools/compile.py --check` — must print `identical`.

If step 2 prints `DIFFERS`, someone hand-edited `README.md`. Do not overwrite it: run
`python3 COORDINATION/tools/split.py` to fold their edit into the section file first.

## Not included

A **twelfth session** — the compiler session. It owns no section content; its only job is
to run `compile.py --check`, confirm it prints `identical`, and push. It should run last,
after every other session has merged and pushed.

## Naming

Note there is an older `ASSIGNMENTS` file in the parent folder, left untouched. It is a
section-to-workgroup map belonging to an earlier session, not these prompts.
