---
item: OPS-13/17/33-README-merge
action: resolve-conflicts
files:
  - README.md
  - agents/COORDINATION (README UPDATES)/12-host-installation-and-configuration/section.md
evidence: |
  $ git status --short
  UU README.md
  UU agents/COORDINATION (README UPDATES)/12-host-installation-and-configuration/section.md

  $ git ls-files -u README.md
  100644 6cf7a8d8f31e98dffd8e0ba82e3b65ec65e39d3c 1	README.md
  100644 d54ed10f5a40ecd7235cb7adf2a5a44f03bbd5d5 2	README.md
  100644 54d70f18220bfeb52ee4ab018bda238ae2703f90 3	README.md

  $ grep -n '<<<<<<<\|=======\|>>>>>>>' README.md
  5460:<<<<<<< HEAD
  5494:=======
  5554:>>>>>>> 7dd0f77 (ops(host): verify linger, pin vendor blobs, split store status (OPS-13/17/33))
  7933:<<<<<<< HEAD
  7935:=======
  7938:>>>>>>> 7dd0f77 (...)
  8043:<<<<<<< HEAD
  8044:=======
  8115:>>>>>>> 7dd0f77 (...)
section: 12-host-installation-and-configuration
---

**OPEN — needs operator action, because it is README.md and my brief forbids me
editing README.md directly.** `git status` shows `UU README.md`: the working tree
has conflict markers and the index still holds all three stages. There is no
`MERGE_HEAD` (`ls .git/MERGE_HEAD` → absent), so this is **not** an in-progress
merge — it is a leftover conflicted state that will block the next commit.

## Every one of the three conflicts resolves to a UNION

I read all three. In each case HEAD and my side add *different* text and neither
side contradicts the other, so the correct resolution is to keep both. No
content should be dropped.

**Conflict 1 — README.md:5460-5554, §12.3.** HEAD carries the
`verify-host-baseline.sh` rationale (the old block "could not fail"; the
cgroup test was silent; 5-pass/2-fail evidence). My side carries `### 12.3.1
Linger is a precondition, not a nicety (OPS-13)`. Keep HEAD's prose, then my
§12.3.1 after it. They are complementary, and §12.3.1 has since been rewritten
in the section file to say so explicitly and to point at the baseline verifier
rather than claiming credit for the check.

**Conflict 2 — README.md:7933-7938, the scripts tree.** A one-line `└──` vs a
two-line `├──`. Resolution is to keep **both** entries — `capture-version-matrix.sh`
*and* `check-user-linger.sh`:

```
│   ├── capture-version-matrix.sh
│   └── check-user-linger.sh
```

**Conflict 3 — README.md:8043-8115, §16.1.3.** HEAD side is empty; my side is
the whole `### 16.1.3 Store status has four states, not two (OPS-33)` block.
Take my side verbatim. No conflict.

## What is already done on my side

`agents/COORDINATION (README UPDATES)/12-host-installation-and-configuration/section.md` is
**resolved** — markers removed, both sides' content kept, and my §12.3.1 rewritten
so it credits the baseline verifier instead of duplicating it:

```console
$ grep -c '<<<<<<<\|>>>>>>>\|^=======$' agents/COORDINATION (README UPDATES)/12-host-installation-and-configuration/section.md
0
```

Its index stages still need clearing (`git add` that one file by name).

## Verification already run against the resolved section

```console
$ python3 -m pytest scripts/ -q
62 passed in 0.63s
$ bash scripts/validation/check-user-linger.sh --check ; echo rc=$?
rc=0
$ AO_LINGER_USER=alwayson-ledger bash scripts/validation/check-user-linger.sh --check ; echo rc=$?
rc=2          # nonexistent account, distinct from a real fault
```
