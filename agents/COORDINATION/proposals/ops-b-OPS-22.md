---
item: OPS-22
action: close
evidence: |
  $ python3 scripts/build-update/test_generators.py
  ...
  Ran 29 tests in 0.266s

  OK
section: 12-host-installation-and-configuration
---
`scripts/build-update/test_generators.py` holds **29 passing tests** covering the
three defects the item names, plus defects found while writing them. §12.5.2
documents the suite.

The item's proposed two assertions ("every pull step carries a 64-character
digest", "no step embeds a not-a-value marker") are both present, and the suite
caught a **fourth defect the item did not mention**:

`update_steps()` validated a digest by checking only the `sha256:` prefix.
`sha256:` plus 12 hex characters passes that test, so
`podman pull repo@sha256:<12>` was emitted — a command that reads as correct and
is rejected by any registry with HTTP 400. Length is part of what makes a digest
reference valid, so `is_complete_digest()` now checks algorithm *and* body length.

The three defects named in the item are covered by
`test_truncated_digest_produces_no_step`, `test_prose_error_string_produces_no_step`,
`test_every_pull_step_across_shapes_has_full_hex`,
`test_no_pull_step_embeds_a_not_a_value_marker`,
`test_desktop_app_uses_owning_package`,
`test_display_name_never_reaches_the_command`.

**Repairing the harness was a prerequisite, not a detail.** The file did not run
at all: a stray fragment of a previous test hung off the end of the file *after*
`unittest.main()`, so the block was dead code that never executed, and its four
tests errored. The `TestAptHistoryParsing` fixture called `importlib.reload()` on
a module that was never in `sys.modules`, raising `ImportError` for every test in
that class. The parser now takes an injectable `log_dir`, so the fixture uses a
`tempfile.mkdtemp()` directory instead — the test never touches `/var/log/apt`,
which matters because the real log is system state.

Run the suite after any change to the generators. It is fast enough not to be an
excuse (0.27 s) and it is the only thing standing between the next defect and a
plausible-looking document.