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

## Fourth error, found 2026-10-04 on resume: I committed a section edit without recompiling

The commit that added the third defect (`63b0129`) edited
`agents/COORDINATION (README UPDATES) (README UPDATES)/02-platform-baseline/section.md` but did **not** recompile, so
`README.md` — the document operators actually read — did not contain the correction.
`compile.py --check` returned **`DIFFERS`** (rc=1), and the COORDINATION README says a
`DIFFERS` means *"someone edited README.md directly — find them and stop rather than
overwriting their change."* I was that someone, indirectly.

This matters for this item specifically. PLAT-04's whole subject is **the gap between what
a document asserts and what can be re-verified**, and I reproduced that exact gap between
my own section file and the README compiled from it. A fix recorded only in the section file
is not a fix until it is compiled.

Fixed in `d04e594`; `compile.py --check` now returns `identical` (rc=0). The cause was
that I treated the commit as the last step instead of recompile-then-check-then-commit.
Any session owning a section file should run `python3 agents/COORDINATION (README UPDATES) (README UPDATES)/tools/compile.py`
before committing, every time.

## Third error, smaller: I quoted `apt-cache policy` for installed state

Second error, and this one was a **false claim I had already committed**: on 2026-10-03 I
asserted that `aa-status` run without privilege "still exits 0". It exits **4**. I wrote that
into §2.3 as a trap for the next session, which made the trap point the wrong way — it said the
exit code was useless as a signal when in fact the exit code was the *only* working signal and
the `|| true` in §12.3 was discarding it. I did not measure it; I assumed it from the printed
message. The corrected trap is recorded in §2.3: `aa-status` **does** return non-zero without
privilege, and §12.3 throws that away. Lesson worth carrying: when writing a note about *why* a
command is or is not trustworthy, measure that command's exit status rather than inferring it
from its output.

---

# THIRD PASS 2026-10-04 17:05 — reproduced from scratch; §12.3 still defective

I did not reuse the transcript above. I copied §12.3's verify block **verbatim** into a script and
ran it, `sudo` untouched, because this item is specifically about a block that reports success
while checking nothing — inheriting somebody's transcript would be the same error in a new place.

```
$ bash /tmp/plat-verify-asis.sh
podman version rc=0
podman info rc=0
systemctl --user status rc=0
Linger=yes
cgroups v2 active
OVERALL EXIT=0
SCRIPT EXIT=0

[stderr]
sudo: A terminal is required to authenticate
```

**All three defects reproduce.** The block exits **0**; `sudo` could not authenticate;
`aa-status` never ran; the AppArmor line produced no output at all and the block still shows six
green lines. The sixth check is the dangerous one — it is *actively misleading on success*, not
merely silent on failure, and it is invisible to anyone reading stdout.

The cgroup line is confirmed silent-on-failure by construction: `test … && echo …` prints nothing
when the test fails, and nothing reads its status.

```
$ stat -fc %T /sys/fs/cgroup
cgroup2fs                              # the check passes today, so the defect is latent
```

That distinction matters for the compiler. The cgroup defect is **latent** — it would surface only
on a host that is not cgroup v2. The `aa-status` defect is **live right now** on this host.

## Cross-check with PLAT-03

`apparmor-utils 5.0.2-0ubuntu1~26.04.1` is installed and all five profile tools resolve. That makes
the broken sixth line look *more* trustworthy than before — the tool now exists, yet it still
reads nothing. **Installing the package without fixing the assertion shape buys nothing
verifiable.** These two items must be fixed together, not in sequence.

## Action unchanged: `update`, referred to OPS-B

§12.3 is the OPS-B session's file. The requirement is recorded in §2.4 of my section. I have not
patched §12.3, because a correct patch sitting in a proposal changes no document the operator
reads while looking like a fix.

## What I got wrong on this pass

While running the verbatim block I wrote the echo for the cgroup line as `cgroups v2 active` and the
surrounding harness as if all six checks reported a status. It does not: `podman version`,
`podman info` and `systemctl --user status` print **nothing** in the real block — only my harness
added the `rc=` labels, because I redirected their output to `/dev/null` to make the block's own
behaviour visible. The evidence above separates the two honestly: the `rc=` lines are mine, the
stderr is the block's. Anyone reproducing this should expect five silent lines, not six labelled
ones.