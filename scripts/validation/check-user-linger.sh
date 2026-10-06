#!/usr/bin/env bash
# ALWAYS ON - validation: check-user-linger.sh (OPS-13).
#
# Every workload here is a ROOTLESS user Quadlet unit under
# ~/.config/containers/systemd/. Those units are started by `systemd --user`,
# and `systemd --user` only exists for the operator account while a session is
# open. Log out of KDE and every container, timer and Quadlet-generated unit
# for this account stops. Linger is what keeps the user manager alive with no
# session at all.
#
# So this is not a nicety. A host with linger off comes back from a reboot with
# zero workloads, and nothing anywhere logged WHY - the units simply were not
# running. ao-lmstudio.service already depends on this behaviour (its own header
# says "Starts at boot via user lingering").
#
# Read-only. It reports, it never enables: `loginctl enable-linger` needs root
# and is a host-level change, so the operator makes it (README 4.1 rule 1/3).
#
# `--check` exit codes, so a timer or CI can gate on it without parsing text:
#   0  linger is enabled and the user manager is up
#   1  a real fault (linger off, no user manager, units deployed but not running)
#   2  the named account does not exist - nothing to check, NOT a fault
#   10 the user could not be determined at all (internal error)
set -Eeuo pipefail
IFS=$'\n\t'

# An explicit AO_LINGER_USER wins, so the failure path can be exercised against
# an account that genuinely has no linger (the service accounts) without
# creating a throwaway user, which needs root.
USER_NAME="${AO_LINGER_USER:-${SUDO_USER:-${USER:-}}}"
[ -n "$USER_NAME" ] || { echo "ERROR: cannot determine user" >&2; exit 10; }

check_only=0
[ "${1:-}" = "--check" ] && check_only=1

rc=0

# --- 0. does the account exist at all? -----------------------------------
# Measured 2026-10-04: `loginctl show-user alwayson-ledger -p Linger` returns
# "Failed to look up user ... No such process" and rc=1, while
# `loginctl show-user -p Linger --value` yields the literal string `unknown`.
#
# The first revision folded that into the "linger is not enabled" branch, so
# asking about an account that simply does not exist printed a scary FAIL and
# exited 1. That is the worst possible failure for a checker: it trains the
# operator to ignore it, so it would hide a genuine Linger=no.
#
# `/var/lib/systemd/linger/<name>` is NOT proof of existence - the marker
# files for alwayson-ledger, alwayson-mapping and alwayson-sales survive on
# this host while getent finds no such user. So test the account, not the
# marker.
if ! getent passwd "$USER_NAME" >/dev/null 2>&1; then
  echo "SKIP: no such account '$USER_NAME' (getent passwd found nothing)."
  echo "      This is NOT a linger finding. The account may have been removed"
  echo "      while its stale marker file remained in /var/lib/systemd/linger/."
  [ "$check_only" -eq 1 ] && exit 2
  exit 0
fi

# --- 1. the login manager's own view -------------------------------------
linger="$(loginctl show-user "$USER_NAME" -p Linger --value 2>/dev/null || echo unknown)"
state="$(loginctl show-user "$USER_NAME" -p State --value 2>/dev/null || echo unknown)"
printf 'user            : %s\n' "$USER_NAME"
printf 'Linger          : %s\n' "$linger"
printf 'State           : %s\n' "$state"

if [ "$linger" != "yes" ]; then
  echo "FAIL: linger is not enabled for $USER_NAME."
  echo "      Rootless Quadlet units stop when the last session closes, and do"
  echo "      not come back on their own after a reboot."
  echo "      Fix (needs root): sudo loginctl enable-linger $USER_NAME"
  rc=1
else
  echo "OK:   linger enabled"
fi

# --- 2. the on-disk marker ----------------------------------------------
# loginctl answers from the daemon, the marker file is what it reads. Both
# should agree; a disagreement means one of them is stale.
marker="/var/lib/systemd/linger/$USER_NAME"
if [ -e "$marker" ]; then
  printf 'marker file     : present (%s)\n' "$marker"
else
  echo "NOTE: $marker absent but loginctl says Linger=$linger."
  echo "      Normally harmless (logd may not have flushed); treat as OK."
fi

# --- 3. the user manager actually exists now ---------------------------
# Linger=yes with no /run/user/<uid> means the user manager is not up, which is
# the state that actually breaks the workloads.
# Look the uid up for the USER actually being checked, not the invoking one.
# The first revision called `id -u` with no argument, so checking any other
# account reported /run/user/-1 and printed a FAIL that was about the wrong
# user entirely.
uid="$(id -u "$USER_NAME" 2>/dev/null || echo -1)"
if [ "$uid" = "-1" ]; then
  echo "WARN: no uid for '$USER_NAME'; skipping the user-manager check."
  uid=""
fi
if [ -z "$uid" ]; then
  :
elif [ -d "/run/user/$uid" ]; then
  echo "OK:   user manager runtime /run/user/$uid present"
  if command -v systemctl >/dev/null 2>&1; then
    n="$(systemctl --user list-units --type=service --state=running --no-legend --plain 2>/dev/null | wc -l)"
    echo "      running user services: $n"
  fi
else
  echo "FAIL: /run/user/$uid does not exist, so systemd --user is not running."
  echo "      Rootless containers are down regardless of the linger setting."
  echo "      Fix: log in once, or check 'systemctl --user status'."
  rc=1
fi

# --- 4. are the workloads that need it actually enabled? ---------------
# Linger only helps if the units are enabled. Count, do not start anything.
if command -v systemctl >/dev/null 2>&1; then
  deployed="${QUADLET_DEPLOY_DIR:-$HOME/.config/containers/systemd}"
  if [ -d "$deployed" ]; then
    n_units="$(find "$deployed" -maxdepth 1 -name '*.container' | wc -l)"
    # Quadlet GENERATES ao-<name>.service from <name>.container; there is no
    # unit file literally named *.container under systemd --user. The first
    # revision of this check grepped for '\.container' and reported "21 units
    # deployed but none enabled" on a host with 25 containers running, because
    # it was looking for a filename systemd never creates. Match the generated
    # names instead.
    n_on="$(systemctl --user list-unit-files --no-legend 2>/dev/null \
            | grep -cE '^ao-.*\.service' || true)"
    n_running="$(systemctl --user list-units --type=service --state=running --no-legend \
            --plain 2>/dev/null | grep -cE '^ao-.*\.service' || true)"
    printf 'deployed units  : %s .container files in %s\n' "$n_units" "$deployed"
    printf 'generated ao-*  : %s service units under systemd --user\n' "$n_on"
    printf 'running ao-*    : %s\n' "$n_running"
    if [ "$n_units" -gt 0 ] && [ "$n_on" -eq 0 ]; then
      echo "FAIL: $n_units container units are deployed but systemd --user has"
      echo "      no ao-* service units, so quadlet never generated them."
      echo "      Fix: systemctl --user daemon-reload"
      rc=1
    fi
    if [ "$n_on" -gt 0 ] && [ "$n_running" -eq 0 ]; then
      echo "FAIL: $n_on ao-* units exist but NONE are running."
      echo "      Linger is on, so this is a genuine service failure, not a"
      echo "      login problem. Check: systemctl --user --failed"
      rc=1
    fi
  fi
fi

[ "$check_only" -eq 1 ] && exit "$rc"
exit 0
