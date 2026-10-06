---
item: OPS-19
action: close
evidence: |
  $ python3 -c "import json; p=json.load(open('data/build-update/update-plan.json')); ..."
  schema 2 items 224
  summary {'behind': 1, 'eligible': 0, 'excluded': 224}
  steps non-list: 0

  $ python3 -c "update_steps({'item':'brave','via':'snap/latest/stable'}, None)"
  {'steps': [['snap', 'refresh', 'brave']], 'manual': []}

  $ python3 -m pytest scripts/build-update/test_generators.py -q
  62 passed in 0.73s
section: 12-host-installation-and-configuration
---
`update-plan.json` is now **schema 2**: every step is an argv **array**, never a
string, and prose is carried separately under `manual`. The `eligible` decision
is taken on the strength of `steps` alone, so "eligible" now means *a machine can
carry this out* rather than *no recorded rule forbids it*. `provenance-log.py`
§12.5.3 documents it.

Measured on this host: **0 eligible of 224**, with **0** steps that are not
argv arrays. `_argv_is_safe()` downgrades any argument carrying a shell
metacharacter to prose rather than emitting it, so a plan can never be run
through a shell and an item named `pkg; rm -rf /` produces no executable step.

**What I got wrong, which is the part worth reading.** The section as first
written claimed "`brave` remains genuinely automatable and is emitted as argv".
I checked it instead of repeating it, and it is **false as stated**. The
generator does emit `["snap","refresh","brave"]`, but the plan shows
`"steps": []` for `brave`, because the writer gates on the decision —
`"steps": steps if decision == "eligible" else []` — and `brave`'s verdict is
`?`, not `**NO**`: the snap channel was unreachable, so there is no evidence it
is behind. The two statements answer different questions. `brave` is the only
item whose *source* admits a mechanical step; it is not eligible **today**
because the evidence for updating it does not exist, not because it is
unautomatable. Had the section been left as written, the next reader would
have looked for that argv in the plan, not found it, and concluded the generator
had regressed. The section now states the correction explicitly.

**Consequence for the executor.** Because every item is currently excluded, the
plan publishes **no steps at all**, so nothing is safe to hand to an executor
yet. That is the truth of this host rather than a defect, and the validator
(OPS-20) reports it as such.