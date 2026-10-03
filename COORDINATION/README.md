# COORDINATION

This folder is the source of truth for `README.md`. The README is **compiled**, not
hand-edited.

## Why

The README is ~4,000 lines. When several AI sessions edit it at once they collide on the
same file: two sessions rebase over each other, pushes are rejected, and work is lost. This
folder removes that. **Each section is one file. A session edits only its own file, so two
sessions can never collide.**

## Layout

| Path | What it is |
|---|---|
| `MANIFEST.md` | The fixed section order. The compiler concatenates in this order. |
| `00-frontmatter/section.md` | Title block and the Contents table. |
| `es-executive-summary/section.md` | ES.1 architecture corrections, ES.2 master topology, ES.3 record. |
| `01-…` through `20-…` | One folder per numbered README section, named with its number and title. |
| `tools/split.py` | Splits `README.md` into these folders. |
| `tools/compile.py` | Rebuilds `README.md` from these folders. `--check` verifies without writing. |

This is **not** the same as `COORDINATION BETWEEN AI/`, which holds session handoff
documents. That folder is narrative; this one is the build input.

## Rules

1. **Edit one file.** Your session owns one section folder. Change nothing else here.
2. **Never edit `README.md` directly.** It is generated. Edit the section file.
3. **Keep the heading.** Each `section.md` begins with the section's own `# N. Title`
   heading. Renaming means renaming the folder *and* `MANIFEST.md`.
4. **Do not renumber `19.x` item IDs.** Work items are keyed by group prefix
   (`PLAT`, `NET`, `SEC`, `LEDGER`, `PAY`, `COMM`, `FIELD`, `SIM`, `OPS`) so a new item
   never collides. Add the next free number in its group.
5. **Record new work in `19-current-status-and-outstanding-work/section.md`** — it is the
   single status log. Do not create a parallel list.
6. **Sections 1–16 are specification.** No status, history, revision or decision dates.
   Everything current belongs in 17 or 19.
7. **Commit only your section file.** Never `git add -A`; it sweeps in other sessions' work.

## Who does what

| Role | Does |
|---|---|
| **Section session** | Edits exactly one `section.md`. Commits only that file. |
| **Compiler session** | Runs `python3 COORDINATION/tools/compile.py`, checks `--check` passes, and pushes. |

The compiler must run `compile.py --check` and get `identical` before pushing. If it says
`DIFFERS`, someone edited `README.md` directly — find them and stop rather than
overwriting their change.

## Verifying

```bash
python3 COORDINATION/tools/compile.py --check
# -> identical   (safe to push)
# -> DIFFERS     (someone bypassed the split; do not overwrite)
```

The split/compile round-trip is byte-exact, so the compiled README can always be trusted
to equal the sum of its parts.
