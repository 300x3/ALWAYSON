#!/usr/bin/env bash
# Asserting replacement for the §12.3 verify block. PLAT-04 / OPS-15.
#
# The original block PRINTED values without asserting them: the cgroup test
# was silent on failure and the block's overall exit status was 0 either way.
# Measured 2026-10-03: breaking the cgroup check changed nothing and the
# script still exited 0, so it verified nothing.
#
# This version asserts. It exits non-zero on any failure, names the failing
# check, and never reports success it did not measure.
set -uo pipefail

pass=0; fail=0
ok()   { printf '  PASS  %s\n' "$1"; pass=$((pass+1)); }
bad()  { printf '  FAIL  %s\n' "$1"; fail=$((fail+1)); }
warn() { printf '  WARN  %s\n' "$1"; }

printf '=== ALWAYS ON host baseline verification (asserting) ===\n'

# 1. podman present and usable
if command -v podman >/dev/null 2>&1 && podman version >/dev/null 2>&1; then
  ok "podman responds ($(podman version --format '{{.Client.Version}}' 2>/dev/null))"
else
  bad "podman missing or non-functional (required by every workload)"
fi

# 2. systemd user manager reachable
if systemctl --user status >/dev/null 2>&1; then
  ok "systemd --user manager reachable"
else
  bad "systemd --user manager not reachable (Quadlets cannot run without it)"
fi

# 3. linger must be yes - without it the user manager dies at logout and
#    every container stops. Assert the VALUE, not just that the key exists.
linger="$(loginctl show-user "$USER" -p Linger --value 2>/dev/null)"
if [ "$linger" = "yes" ]; then
  ok "linger enabled (survives logout)"
else
  bad "linger is '${linger:-unset}', expected 'yes' - containers stop at logout (OPS-13)"
fi

# 4. cgroup v2 - the original line failed SILENTLY. This one reports.
cg="$(stat -fc %T /sys/fs/cgroup 2>/dev/null)"
if [ "$cg" = "cgroup2fs" ]; then
  ok "cgroup v2 unified hierarchy"
else
  bad "cgroup fs type is '${cg:-unknown}', expected 'cgroup2fs'"
fi

# 5. apparmor profile tooling. aa-status ships in the base apparmor package;
#    aa-enforce/aa-complain ship in apparmor-utils and are MISSING on this host
#    (measured 2026-10-03). Report honestly rather than passing on aa-status.
if command -v aa-status >/dev/null 2>&1; then
  ok "aa-status present"
else
  bad "aa-status missing - apparmor not installed"
fi
if command -v aa-enforce >/dev/null 2>&1; then
  ok "aa-enforce present (profile enforcement possible)"
else
  warn "aa-enforce MISSING - apparmor-utils not installed, so no profile can be"
  warn "  enforced or inspected. §2.3 records this; install needs operator approval."
fi

printf -- '--- %d passed, %d failed ---\n' "$pass" "$fail"

# The whole point of PLAT-04: this must be able to return non-zero.
if [ "$fail" -ne 0 ]; then
  printf 'RESULT: FAIL (%d check(s) failed)\n' "$fail"
  exit 1
fi
printf 'RESULT: PASS\n'
exit 0
