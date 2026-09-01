#!/usr/bin/env bash
# ALWAYS ON - bootstrap/install-heltec-udev.sh (privileged; requires root)
# Installs the Heltec V3 udev rule so the desktop gateway gets:
#   - a stable /dev/heltec-v3 symlink (Section 9.2 architecture requirement)
#   - ModemManager exclusion (prevents port grabbing on the CP2102 bridge)
#   - dialout group ownership + 0660 mode on the tty
# Run via:  pkexec bash /ALWAYSON/scripts/bootstrap/install-heltec-udev.sh
set -Eeuo pipefail

SRC=/ALWAYSON/config/field/heltec-v3/udev/99-alwayson-heltec.rules
DST=/etc/udev/rules.d/99-alwayson-heltec.rules

[ "$(id -u)" -eq 0 ] || { echo "ERROR: must run as root (pkexec)" >&2; exit 1; }
[ -f "$SRC" ] || { echo "ERROR: rule source missing: $SRC" >&2; exit 1; }

install -m 0644 -o root -g root "$SRC" "$DST"
udevadm control --reload
udevadm trigger --subsystem-match=tty || true
udevadm settle || true

echo "--- installed rule ---"
cat "$DST"
echo "--- resulting device nodes ---"
ls -l /dev/heltec-v3 /dev/serial/by-id/ 2>&1 || true

# Re-apply ModemManager ignore if the daemon already grabbed the port
if systemctl is-active --quiet ModemManager; then
  systemctl restart ModemManager || true
  echo "ModemManager restarted to release/re-evaluate the port"
fi
echo "OK: Heltec udev rule installed"