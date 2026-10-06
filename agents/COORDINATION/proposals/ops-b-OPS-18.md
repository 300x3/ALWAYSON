---
item: OPS-18
action: close
evidence: |
  Before/after behavioural comparison, same host, same cache, --offline:

  $ sha256sum base.md after2.md base-plan.json after2-plan.json base.html after2.html
  872670ba08a239c8b73d45136d4d61babc5acea868a755b41734fda13240a4c2  base.md
  872670ba08a239c8b73d45136d4d61babc5acea868a755b41734fda13240a4c2  after2.md
  a0d910289d932621fa384fe5424f1785f8a3cb78be86416fc3bc29a9019646e7  base-plan.json
  6572f2573248a60de8c4b6a9ec23ec28b3f0ccc97b32c2da7fb1edd0409ae6e1  after2-plan.json
  72b6bb6c89f5b994246e6bccd05ad1a98450c155551958e0a7fff5f4d30154f7  base.html
  72b6bb6c89f5b994246e6bccd05ad1a98450c155551958e0a7fff5f4d30154f7  after2.html

  Markdown and HTML are byte-identical. The plan JSON differs in exactly one
  field, the run timestamp:

  $ python3 -c "structural diff of the two plan files"
  DIFF /generated '2026-10-05T15:00:12+00:00' -> '2026-10-05T15:08:47+00:00'
  summary base: {'behind': 1, 'eligible': 0, 'excluded': 223}
  summary aft : {'behind': 1, 'eligible': 0, 'excluded': 223}

  Test suite, before and after:

  $ python3 -m pytest scripts/ -q
  62 passed                       # before the split
  74 passed in 0.54s             # after, +12 new tests

  Package layout and line counts:

  $ wc -l scripts/build-update/provenance/*.py scripts/build-update/provenance-log.py
    1633 scripts/build-update/provenance/collector.py
      93 scripts/build-update/provenance/common.py
      70 scripts/build-update/provenance/__init__.py
     211 scripts/build-update/provenance/plan.py
     139 scripts/build-update/provenance/policy.py
     446 scripts/build-update/provenance/render.py
     133 scripts/build-update/provenance-log.py

  $ git show HEAD:scripts/build-update/provenance-log.py | wc -l
  2328

  apt_history still resolves from inside the package (this was broken by the
  split and is now pinned by a test):

  $ python3 -c "import provenance; print(provenance._load_apt_history()); print(provenance.apt_date('rclone'))"
  <module 'ao_apt_history' from '.../scripts/build-update/apt_history.py'>
  2026-10-03 (apt history, Install)
section: 16-scripts-and-operational-standards
---

`provenance-log.py` was a single 2,328-line module. It is now a 133-line
entrypoint over a package split by concern: `common` (primitives), `collector`
(evidence gathering, the only module with mutable caches), `policy` (the updater
allowlist and the recorded reason for each entry), `plan` (machine-readable
update plans), `render` (presentation). Dependency direction is strictly one way
— `plan -> policy, render, common`; `render -> collector, policy, common`;
`collector -> common`; `policy -> stdlib only` — and is asserted from the import
statements themselves rather than from intent.

Output is unchanged: Markdown and HTML are byte-identical to the pre-refactor
baseline and the plan JSON differs only in its generation timestamp. The
existing 62 regression tests still pass, and 12 more were added.

The split also forced two design corrections that are now pinned by tests:

1. **Cross-module state goes through an accessor.** `provenance/__init__.py`
   re-exports every name so the entrypoint keeps its historical surface, but
   those bindings are snapshots taken at import time. When the owning module
   rebinds its own name with `global`, the copy goes stale. Measured: after
   `_load_apt_history()` cached the module in `collector`,
   `provenance._APT_HISTORY_MODULE` still read `'unset'`. A plain imported
   `CACHE_TTL` would likewise have printed the default 6h TTL on `--refresh`.
   Hence `cache_ttl()` / `set_cache_ttl()` and the entrypoint's `set_offline()`.

2. **The re-export is an explicit namespace walk, not `import *`.** Star imports
   skip underscore-prefixed names, and existing tests reach `_load_apt_history`
   and `_argv_is_safe` through the entrypoint — a star import turns those into an
   `AttributeError` at the call site rather than at import time.

## What I got wrong

**I broke `apt_history.py` and every install date in the report, and the failure
was invisible.** The split moved `_load_apt_history()` into
`provenance/collector.py`, but the function loaded
`Path(__file__).parent / "apt_history.py"` — which had been correct when the file
was a sibling, and now pointed *inside* the package. `FileNotFoundError` was
caught by the existing `except` and collapsed to `None`, so every install date
silently reverted to the dpkg mtime. This is the exact defect that function was
written to eliminate, reintroduced by the refactor. Only the two pre-existing
CWD tests caught it, and only because I ran the suite before claiming success.
Cause: I moved code without re-deriving its *relative* paths. Both sibling
locations are now tried, and `test_apt_history_sibling_is_found_after_the_split`
asserts the module is not None rather than merely that the function is callable.

**My first five new tests all failed, and every failure was my own invented
schema, not a real defect.** I guessed row keys (`pin`, `installed`, `upstream`,
`status`, `group`) that do not exist — the real keys are `pinned`, `released`,
`pin_hash`, `rel_hash`, `download` — and I guessed a function signature
(`rollup_details_md(rows, rollup_names)`; it is
`rollup_details_md(rows, kde_members)` where the second argument is
`(name, owning_package)` *pairs*, which raised `too many values to unpack`). I
also asserted `COLLECTED[` and `json.loads(` were absent from the entrypoint,
but both are legitimate flag wiring. Cause: I wrote assertions from a mental
model of the code instead of reading the literals in `collector.py`. The fixtures
are now built from the measured schema, and the comment above `_rows()` records
why.

**I stated two line counts from the generation step rather than re-measuring
after the edits**, and both were wrong (`collector.py` 1,590 vs the real 1,633;
`render.py` 440 vs 446). Corrected against `wc -l` before the commit.

**`_SUBMODULES` leaked into `__all__` and broke collection for the whole test
suite.** I built `__all__` before deleting the loop variables, so the star
import in the entrypoint then looked for names that no longer existed. Ordering
the `del` before `__all__` fixes it; worth knowing if this pattern is reused.
