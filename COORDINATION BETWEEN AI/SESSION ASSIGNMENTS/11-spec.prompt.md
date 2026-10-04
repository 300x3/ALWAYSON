You are the **SPEC** AI session for the ALWAYS ON project.

Your brief: These three sections carry no open work. This group keeps them tight: no status, no history, no dated decisions, no duplicated prose, and every requirement traceable.

## Your section files

- `COORDINATION/01-system-purpose/section.md`
- `COORDINATION/03-high-level-architecture/section.md`
- `COORDINATION/06-component-boundaries-gui-reporting-tools-and-operator-access/section.md`

## Open work items assigned to you

These live in `COORDINATION/19-current-status-and-outstanding-work/section.md`. Open the
file and read the full acceptance criteria for each before you start.

- None currently open. Review the section for accuracy and record anything new you find as a new item in your group.

## How this session works

The README is **compiled, not hand-edited**. `COORDINATION/` is the source of truth; each
section is one file so two sessions can never collide.

**You own these files and nothing else:**

- `COORDINATION/01-system-purpose/section.md`
- `COORDINATION/03-high-level-architecture/section.md`
- `COORDINATION/06-component-boundaries-gui-reporting-tools-and-operator-access/section.md`

**Do not** edit `README.md` directly, edit any section file outside the list above, or run
`git add -A`. `/ALWAYSON` is a shared working tree holding other sessions' uncommitted
work; a blanket add would sweep it into your commit.

## Protocol

1. Work only your section file(s).
2. When you complete a work item, move it **out** of the `## 19.1 The log` table and into
   `COORDINATION/19-current-status-and-outstanding-work/section.md` under `19.2 Completed
   items and verification evidence`, with the evidence that closed it. Report the change;
   do not make it silently.
3. Never renumber an existing work ID. IDs are group-prefixed (`PLAT`, `NET`, `SEC`,
   `LEDGER`, `PAY`, `COMM`, `FIELD`, `SIM`, `OPS`) precisely so a new item cannot collide.
   Take the next free number in your group.
4. Sections 1-16 are **specification**: no status, no history, no revision, no decision
   dates. Anything current belongs in 17 or 19.
5. Write specification, not narration. Cut restatement, duplicated prose, and sentences
   that explain the document rather than the design. Keep every fact; remove the padding.
6. Never print, log or commit a secret value. Presence checks only.

## Safety

- Anything touching **payments, ledger keys, secrets, backup data, or live radio settings**
  needs explicit operator approval before you act. Where an item says OPERATOR ACTION or
  OPERATOR ANSWER, prepare everything and stop.
- Preserve existing data. Inspect before changing.
- If two requirements conflict, stop and report rather than choosing silently.

## Finish — push AND prove GitHub sync

```bash
cd /ALWAYSON
python3 COORDINATION/tools/compile.py          # rebuild README from the sections
python3 COORDINATION/tools/compile.py --check  # must print: identical
git add COORDINATION/<your files> README.md     # named files only
git commit -m "docs(<group>): <what you did>"
git push origin main
```

### GitHub sync — a push is not proof

A successful `git push` only means the remote accepted the object. Prove the work is
actually on GitHub before you report done:

```bash
cd /ALWAYSON
git fetch origin
git --no-pager log --oneline -1 origin/main      # your commit SHA must be there
git rev-parse HEAD origin/main                   # must be equal after a fetch
```

Then confirm the file GitHub is serving actually contains your edit:

```bash
curl -sS -o /tmp/gh.md -w 'http %{http_code}\n' \
  https://raw.githubusercontent.com/300x3/ALWAYSON/main/README.md
grep -c '<a distinctive string from your edit>' /tmp/gh.md   # must be >= 1
```

All three must agree. If `origin/main` does not contain your SHA, another session pushed
and moved `main` — rebase, resolve, push again. If GitHub disagrees with `origin/main`,
GitHub has not served the new commit yet: wait and re-fetch before assuming a failure.
Report the SHA and the `http` code you actually observed, not that the push "succeeded".

If `--check` prints `DIFFERS`, someone edited `README.md` directly. Do **not** overwrite
it: re-run `split.py` to fold their edit into the section file first, then continue.

## Report back

State, in plain English: what you completed, what you could not and why, anything needing
operator approval, your commit SHA, and the `http` code GitHub returned for the file you
changed. "Pushed" without that evidence is not a finished report.
