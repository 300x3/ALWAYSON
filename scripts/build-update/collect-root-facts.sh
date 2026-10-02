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
} > "${OUT}.tmp.$$"
mv -f "${OUT}.tmp.$$" "$OUT" 2>/dev/null || {
  echo "ERROR: cannot replace $OUT (it may be owned by another user)." >&2
  echo "       Remove it once as root:  pkexec rm -f $OUT" >&2
  rm -f "${OUT}.tmp.$$"
  exit 10
}
chmod 0644 "$OUT" 2>/dev/null || true

echo "wrote $OUT"
if (( IS_ROOT )); then
  echo "mode: privileged; shadow entries: $shadow_count (names only; no values read)"
else
  echo "mode: unprivileged; shadow entry names omitted (needs pkexec --privileged)"
fi
echo "processes: $(wc -l <<<"$procs") comm names (no argv)"
exit 0
