---
item: PLAT-04
action: close
evidence: |
  $ bash scripts/validation/verify-host-baseline.sh ; echo "exit=$?"
  === ALWAYS ON host baseline verification (asserting) ===
    PASS  podman responds (5.7.0)
    PASS  systemd --user manager reachable
    PASS  linger enabled (survives logout)
    PASS  cgroup v2 unified hierarchy
    PASS  aa-status present
    WARN  aa-enforce MISSING - apparmor-utils not installed, so no profile can be
    WARN    enforced or inspected. §2.3 records this; install needs operator approval.
  --- 5 passed, 0 failed ---
  RESULT: PASS
  exit=0

  # and the direction that matters - a broken host must NOT pass:
  $ mkdir -p /tmp/fakebin
  $ printf '#!/bin/sh\necho tmpfs\n'    > /tmp/fakebin/stat
  $ printf '#!/bin/sh\necho Linger=no\n' > /tmp/fakebin/loginctl
  $ chmod +x /tmp/fakebin/stat /tmp/fakebin/loginctl
  $ PATH=/tmp/fakebin:$PATH bash scripts/validation/verify-host-baseline.sh ; echo "exit=$?"
    FAIL  linger is 'Linger=no', expected 'yes' - containers stop at logout (OPS-13)
    FAIL  cgroup fs type is 'tmpfs', expected 'cgroup2fs'
  --- 3 passed, 2 failed ---
  RESULT: FAIL (2 check(s) failed)
  exit=1
section: 12-host-installation-and-configuration
---
§12.3's verify block now asserts. The old block is replaced by
`scripts/validation/verify-host-baseline.sh`, which exits non-zero on any
failure and names the check that failed.

The defect was that the block could not fail at all. Its cgroup line was
`test "$(stat -fc %T /sys/fs/cgroup)" = "cgroup2fs" && echo ...`, which is
silent when the test fails; nothing read its return code; and the block's
overall exit status was 0 either way. Reproduced before the change: breaking
the cgroup check left the output unchanged and the script still exited 0.

Two details worth recording. It asserts the **value** of `Linger`, not merely
that the key exists, because without linger every container stops at logout.
And it reports `aa-enforce` as a WARN naming the cause rather than passing on
`aa-status` — `aa-status` ships in the base `apparmor` package and succeeds
even though no profile can be enforced on this host, since `apparmor-utils`
is not installed. That absence is recorded in §2.3 and installing it needs
operator approval, so it is surfaced, not silently passed.

Tested in both directions on purpose: a verifier that only ever passes would
be the same defect in new clothing. The failing case above is a genuine
negative control run with `stat` and `loginctl` stubbed, not a claim about a
host in that state.
