# Issue tracking — §§19.1–19.2 are authoritative

**Rule: every issue, defect, gap, and unit of outstanding work MUST be tracked in `/ALWAYSON/README-ACTION_ITEMS/status-and-references.md` — open work in §19.1, finished work with evidence in §19.2. No other file, chat log, dashboard, or handoff is an issue tracker.**

This is a Cline **workspace rule** (lives in this repo under `.cline/rules/`), so it loads automatically in both **VSCodium (Cline extension)** and **Cline CLI** when the working directory is `/ALWAYSON`. No per-IDE or per-user config is needed.

## Authoritative file

- Absolute path: `/ALWAYSON/README-ACTION_ITEMS/status-and-references.md`
- Front matter declares it split out from `README.md` §§19–20 and the authoritative source for what is built today.
- The pre-split section files are archived copies — do not edit them directly.
- This rule does not override `/ALWAYSON/AGENTS.md` or the compiled-README rule (never hand-edit `/ALWAYSON/README.md`; regenerate via `tools/compile.py`). When a status change also belongs in the compiled README, add it to the appropriate section source (e.g. §17) and regenerate; do not recreate §§19–20.

## Where each issue goes

- **§19.1 Current status log** — everything still to be done or in flight:
  - `ST-XX` component rows (e.g. `ST-03`, `ST-07`) carry overall component state.
  - Grouped open-work rows carry the detailed gaps, prefixed by group: `PLAT`, `NET`, `SEC`, `LEDGER`, `PAY`, `COMM`, `FIELD`, `SIM`, `OPS` (group header rows are `**OPEN WORK**`, `**PLAT**`, `**NET**`, etc.).
  - A newly discovered issue MUST get a new row here before any other work continues.
- **§19.2 Completed items and verification evidence** — finished work only, kept once with the evidence that closed it. Nothing listed here is outstanding.
- **Status vocabulary (§Status vocabulary)** — the only legal `Status` values. `Open` means outstanding; `Complete` / `Implemented` (plus qualifiers such as `Complete with verification pending`, `In progress`, `Partial`, `Blocked`) record delivery state. Use the vocabulary table verbatim; do not invent new keywords.
- **§19.3 Verification evidence / §19.4 priorities / §20 references** — evidence detail, operator ordering, and read-before-changing references. Priority in §19.4 never changes what §19.1 requires.

## Schema (both tables)

Every row carries the same six columns, in this order. Rows are unique by `ID`:

`| ID | Item | Component | Status | Standard served | Current state or acceptance criteria |`

- `ID`: next free ID in its group (`NET-07`, `OPS-26`, …) or the `ST-XX` component ID. Never reuse an ID.
- `Item`: short bold title of the gap or deliverable.
- `Component`: the owning `ST-XX` row (e.g. `ST-01`, `ST-18`). Never leave it blank on a group row.
- `Status`: one vocabulary keyword, bold (e.g. `**Open**`, `**Complete**`).
- `Standard served`: the requirement section(s) it serves (e.g. `§5.2`, `§17.1, §19.2`). Never leave it blank on a group row.
- `Current state or acceptance criteria`: ground truth — what was measured, what remains, exact commands/dates where applicable, and what "done" means. No secrets (see below).

## Required workflow for every Cline session (VSCodium or CLI)

1. **Read the tracker first.** Before planning or editing, read `/ALWAYSON/README-ACTION_ITEMS/status-and-references.md` §§19.1–19.2 and confirm whether the task already has a row.
2. **New issue found → add a §19.1 row immediately.** Pick the owning group and next ID, link the `ST-XX` component, cite the requirement section, set `**Open**` (or `In progress`/`Blocked` with the blocker named), and describe current state + acceptance criteria.
3. **Work the issue** against its acceptance criteria, recording commands, versions, output, and failures.
4. **Close the issue → record evidence in §19.2.** Add (or promote) the §19.2 row with `**Complete**`, date, verification command, and measured outcome; update the §19.1 row (close the group row, update the owning `ST-XX` state) so §§19.1–19.2 never disagree. Where §§1–16 and §§17–19 differ, §§17–19 is current fact.
5. **Never close an issue in chat alone.** A task is not done until its §19.1/§19.2 rows say so. Handoffs (`agents/HANDOFFS (BETWEEN AI AGENTS)/`), dashboards, logs, and proposals may reference an ID but must never replace its tracker row.

## Hard constraints

- Never place secrets in the tracker (or in this rule, logs, Git, or docs examples) — no API keys, passwords, tunnel credentials, or wallet material. Reference the holder (e.g. KDE Wallet entry) instead.
- Never expose a public port, use Docker/Compose, `--privileged`, format/repartition/delete data, or publish external communications without explicit operator approval (README §4.1).
- Inspect before changing; preserve existing data. Stop and report conflicts rather than forcing through them.
