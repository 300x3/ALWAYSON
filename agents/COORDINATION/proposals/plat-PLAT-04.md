---
item: PLAT-04
action: update
evidence: |
  # §12.3's verify block run VERBATIM (all six lines, sudo untouched), 2026-10-04
  $ bash /tmp/verify-asis2.sh
  --- verbatim §12.3 verify block (lines 158-163) ---
  podman version rc=0
  podman info rc=0
  systemctl --user status rc=0
  Linger=yes
  cgroups v2 active
  OVERALL EXIT=0

  [stderr]
  sudo: A terminal is required to authenticate

  # i.e. the AppArmor check NEVER RAN and the block still reports success

  # and simulate the cgroup check FAILING (2026-10-03):
  last rc=1  <-- silent, no output, script continues
  OVERALL SCRIPT EXIT=0

  # aa-status unprivileged does return non-zero -- my earlier note said 0, it is 4
  $ aa-status > /tmp/aas.out 2> /tmp/aas.err; echo "rc=$?"
  rc=4
  # stdout: apparmor module is loaded.
  # stderr: You do not have enough privilege to read the profile set.
section: 02-platform-baseline
---
**§12.3's verify block cannot fail, so it verifies nothing.** Three of its six checks are
unasserted, and the last one is worse than unchecked. The output above is the reproduction: run
verbatim with `sudo` untouched, `sudo` cannot authenticate, `aa-status` never executes, the
cgroup check fails silently under simulation, and **the block's overall exit status is 0** in
every case.

Three distinct defects, all reproduced above:

1. The line `test "$(stat -fc %T /sys/fs/cgroup)" = "cgroup2fs" && echo "cgroups v2 active"` is
   **silent on failure**. The `&&` makes the `echo` conditional, so a failing check produces no
   output at all — indistinguishable from a check that was never run.
2. No `set -e`, no aggregate status, no expected-vs-observed reporting. Even the checks that do
   print (`loginctl show-user -p Linger`) state no expected value, so a reader cannot tell a
   passing check from an unexpected value.
3. **Found 2026-10-04, and worse than the other two: `sudo aa-status || true` reports success
   for a check that never executed.** Run verbatim, `sudo` prints `A terminal is required to
   authenticate` to stderr, `aa-status` is never invoked, and the block's overall exit is still
   0. The other two defects are *silent on failure*; this one is **actively misleading on
   success** — it prints nothing that failed and looks like the sixth passing check. This is
   the shape a verify block should never have, and it is invisible to anyone reading only
   stdout.

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

Second error, and this one was a **false claim I had already committed**: on 2026-10-03 I
asserted that `aa-status` run without privilege "still exits 0". It exits **4**. I wrote that
into §2.3 as a trap for the next session, which made the trap point the wrong way — it said the
exit code was useless as a signal when in fact the exit code was the *only* working signal and
the `|| true` in §12.3 was discarding it. I did not measure it; I assumed it from the printed
message. The corrected trap is recorded in §2.3: `aa-status` **does** return non-zero without
privilege, and §12.3 throws that away. Lesson worth carrying: when writing a note about *why* a
command is or is not trustworthy, measure that command's exit status rather than inferring it
from its output.