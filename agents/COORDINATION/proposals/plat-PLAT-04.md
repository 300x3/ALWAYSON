---
item: PLAT-04
action: update
evidence: |
  # §12.3's verify block run exactly as written
  $ bash /tmp/verify-asis.sh
  Linger=yes
  cgroups v2 active
  cgroup line rc=0
  --- now simulate the cgroup check FAILING:
  last rc=1  <-- silent, no output, script continues
  OVERALL SCRIPT EXIT=0

  # i.e. the block cannot fail, so it cannot verify anything
  $ cat /tmp/verify-asis.sh | sed -n '5,6p'
  test "$(stat -fc %T /sys/fs/cgroup)" = "cgroup2fs" && echo "cgroups v2 active"
  echo "cgroup line rc=$?"
section: 02-platform-baseline
---
**§12.3's verify block cannot fail, so it verifies nothing.** I ran its five commands as
written and then broke the cgroup check. The output above is the reproduction: the failing
`test` prints nothing, returns 1, nothing reads that return code, and **the script's overall
exit status is 0 either way**.

Two distinct defects:

1. The line `test "$(stat -fc %T /sys/fs/cgroup)" = "cgroup2fs" && echo "cgroups v2 active"` is
   **silent on failure**. The `&&` makes the `echo` conditional, so a failing check produces no
   output at all — indistinguishable from a check that was never run.
2. No `set -e`, no aggregate status, no expected-vs-observed reporting. Even the checks that do
   print (`loginctl show-user -p Linger`) state no expected value, so a reader cannot tell a
   passing check from an unexpected value.

This is the same defect §19 `OPS-15` records — evidence rows without a command, a date, and a
criterion — showing up in the verify block that is supposed to produce that evidence.

**Requirement recorded** in new **§2.4** of my section: the verify block must exit non-zero
when any check fails, and name the expected value beside each observed one. Recorded as a
requirement rather than fixed, because **§12.3 is owned by the OPS-B session** and I do not edit
another group's section file.

**What I got wrong.** My first instinct was to fix the block, since it is a shell snippet and
I could have written a corrected one into a proposal in under a minute. I did not, because the
text that must change is inside §12.3 — a file that belongs to OPS-B and that the compiler
merges. A correct patch sitting in a proposal would not change the document anyone reads, so it
would have looked like a fix while changing nothing. Unblocking OPS-B with a diagnosis was
worth more than a patch to the wrong file.