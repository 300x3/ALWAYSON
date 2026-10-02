#!/usr/bin/env bash
# ALWAYS ON - build-update: collect-root-facts.sh
#
# Runs UNPRIVILEGED by default. Verified on this host: lspci, lsusb, ps, lsblk
# and /proc/<pid>/exe are all readable as the operator user, which covers
# everything the inventory actually needs. A root run adds only kernel threads
# hidden from an unprivileged ps, SMART data, and the /etc/shadow ENTRY NAMES.
#
# Run privileged ONLY if the shadow entry names are wanted:
#   pkexec /bin/bash /ALWAYSON/scripts/build-update/collect-root-facts.sh --privileged
# The output records which mode produced it, so a reader never mistakes a
# partial set for a complete one.
#
# PREFER NOT TO. Two reasons, both learned the hard way:
#
#   1. Running this script under pkexec means ROOT executes a file that lives in
#      a directory owned by the operator. That is the classic pkexec anti-pattern:
#      there is no root-owned copy, no polkit action naming a specific command,
#      and no integrity check, so anything that can modify this file gets to run
#      as root the next time it is invoked. Nothing here needs root - the
#      unprivileged path covers the whole inventory - so the default is off and
#      the only thing root adds is the /etc/shadow entry NAMES.
#   2. If a privileged run IS wanted, copy the script to a root-owned location
#      first and run that copy, so root is not executing a user-writable file:
#        pkexec install -m 0755 -o root -g root \
#          /ALWAYSON/scripts/build-update/collect-root-facts.sh /usr/local/sbin/
#        pkexec /bin/bash /usr/local/sbin/collect-root-facts.sh --privileged
#
# The exhaustive inventory needs a small number of facts that cannot be read as
# an unprivileged user. This script collects exactly those and nothing else. It
# is the ONLY privileged step in the inventory, it runs once, and it exits.
#
# WHAT IT COLLECTS (all of it requires root):
#   1. PCI and USB device tree
#   2. Every process's comm/exe name, across ALL users. Argv is NOT collected:
#      it routinely carries secrets passed on a command line.
#   3. Block-device and SMART summary
#   4. /etc/shadow and /etc/gshadow ENTRY NAMES ONLY - never a hash, never a
#      field value. The count and the user names are the inventory fact; the
#      password hashes are not and are not read.
#
# WHAT IT DELIBUTATELY DOES NOT COLLECT:
#   - any value from /etc/shadow or /etc/gshadow
#   - any process argv or environment
#   - any key material, token, credential, or .env content
#   - any file content outside the device tables
#
# Output: JSON at $AO_INVENTORY_ROOT_FACTS (default
# /ALWAYSON/data/build-update/root-facts.json), mode 0644, and nothing else is
# left behind.
set -Eeuo pipefail

PRIVILEGED=0
if [[ "${1:-}" == "--privileged" ]]; then PRIVILEGED=1; fi
if (( PRIVILEGED )) && [[ "$(id -u)" -ne 0 ]]; then
  echo "ERROR: --privileged must run as root: pkexec bash $0 --privileged" >&2
  exit 1
fi
IS_ROOT=0
if [[ "$(id -u)" -eq 0 ]]; then IS_ROOT=1; fi

OUT="${AO_INVENTORY_ROOT_FACTS:-/ALWAYSON/data/build-update/root-facts.json}"
mkdir -p "$(dirname "$OUT")"

# Proper JSON string escaping. A sed one-liner handling quotes and backslashes
# leaves embedded newlines and tabs as raw control characters, which makes the
# output invalid JSON - and the fields here are multi-line command output, so
# that is the normal case, not an edge one. python3 is used because it is the
# thing that is guaranteed to get escaping right.
# jstr emits a COMPLETE JSON string literal, quotes included. Use it with %s
# and no surrounding quotes in the format string.
jstr() {
  printf '%s' "${1:-}" | python3 -c 'import json,sys; sys.stdout.write(json.dumps(sys.stdin.read()))'
}

# ---- 1. PCI / USB device tree -------------------------------------------
pci_list="$(lspci -nn 2>/dev/null || echo 'lspci unavailable')"
usb_list="$(lsusb 2>/dev/null || echo 'lsusb unavailable')"

# ---- 2. all-user process names (comm/exe only, never argv) --------------
# ps with e or args would leak command lines; -o comm= and -o exe= cannot.
procs="$(ps -eo user:12,pid,comm --no-headers 2>/dev/null | head -n 2000 || true)"

# ---- 3. block devices / filesystems / SMART ------------------------------
lsblk_out="$( { lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL 2>/dev/null || true; } || true)"
df_out="$( { df -hP -x tmpfs -x devtmpfs 2>/dev/null || true; } | head -n 60 || true)"
smart_out=""
if command -v smartctl >/dev/null 2>&1; then
  for d in /dev/sd? /dev/nvme?n1; do
    [[ -b "$d" ]] || continue
    m="$( { smartctl -H "$d" 2>/dev/null || true; } | grep -i 'overall-health\|SMART support' | head -2 | tr '\n' ' ' || true)"
    if [[ -n "$m" ]]; then
      smart_out="${smart_out}${d}: ${m}"$'\n'
    fi
  done
fi

# ---- 4. shadow ENTRY NAMES ONLY ----------------------------------------
# `cut -d: -f1` takes the username and discards everything after the first
# colon, so the hash field never enters the output or a variable.
# /etc/shadow is 0640 root:shadow. Names are collected ONLY in a privileged
# run; unprivileged, the count is reported as unavailable rather than guessed.
if (( IS_ROOT )); then
  shadow_users="$(cut -d: -f1 /etc/shadow 2>/dev/null | tr '\n' ' ' || true)"
  shadow_count="$( { wc -w <<<"$shadow_users" 2>/dev/null || true; } || echo 0)"
else
  shadow_users=""
  shadow_count="null"
fi

# ---- write JSON ---------------------------------------------------------
# Create the temp file with mktemp, NOT a predictable "${OUT}.tmp.$$" path.
# This directory is owned by the operator, so in a --privileged run a predictable
# name is a symlink attack: any process running as the operator could pre-create
# "${OUT}.tmp.<pid>" as a symlink to any root-writable path, and root would then
# truncate that file through the redirect and make it durable with the mv below.
# mktemp creates the file with O_EXCL, so the race is not winnable.
# umask 077 keeps the privileged output unreadable to other local accounts from
# the moment it is created, rather than only after the chmod at the end.
umask 077
TMP_OUT="$(mktemp "${OUT}.tmp.XXXXXX")" || {
  echo "ERROR: cannot create a temp file next to $OUT" >&2
  exit 10
}
{
  printf '{\n'
  printf '  "collected_by": "collect-root-facts.sh",\n'
  printf '  "collected_at_utc": "%s",\n' "$(date -u --iso-8601=seconds)"
  if (( IS_ROOT )); then
    printf '  "privilege": "root (privileged run)",\n'
  else
    printf '  "privilege": "unprivileged (shadow names and some kernel threads omitted)",\n'
  fi
  printf '  "pci": %s,\n' "$(jstr "$pci_list")"
  printf '  "usb": %s,\n' "$(jstr "$usb_list")"
  printf '  "processes_comm": %s,\n' "$(jstr "$procs")"
  printf '  "lsblk": %s,\n' "$(jstr "$lsblk_out")"
  printf '  "df": %s,\n' "$(jstr "$df_out")"
  printf '  "smart": %s,\n' "$(jstr "$smart_out")"
  printf '  "shadow_entry_count": %s,\n' "$shadow_count"
  printf '  "shadow_entry_names": %s,\n' "$(jstr "$shadow_users")"
  printf '  "shadow_values_collected": false,\n'
  printf '  "argv_collected": false\n'
  printf '}\n'
} > "$TMP_OUT"
mv -f "$TMP_OUT" "$OUT" 2>/dev/null || {
  echo "ERROR: cannot replace $OUT (it may be owned by another user)." >&2
  echo "       Remove it once as root:  pkexec rm -f $OUT" >&2
  rm -f "$TMP_OUT"
  exit 10
}
# 0600, not 0644. In privileged mode this file carries /etc/shadow entry names,
# and 0644 in a 0755 directory would leave that list world-readable to every
# local account. Unprivileged mode carries nothing sensitive, so 0644 is used
# there to keep the file convenient to read.
if (( IS_ROOT )); then
  chmod 0600 "$OUT" 2>/dev/null || true
else
  chmod 0644 "$OUT" 2>/dev/null || true
fi

echo "wrote $OUT"
if (( IS_ROOT )); then
  echo "mode: privileged; shadow entries: $shadow_count (names only; no values read)"
else
  echo "mode: unprivileged; shadow entry names omitted (needs pkexec --privileged)"
fi
echo "processes: $(wc -l <<<"$procs") comm names (no argv)"
exit 0
