#!/usr/bin/env bash
# ALWAYS ON - 00-inventory.sh (Section 2.2, non-destructive inventory)
set -Eeuo pipefail
IFS=$'\n\t'

LOG_DIR="/home/scottw/ALWAYSON-staging/logs/installation"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/agent-install.log"

{
  echo "===== Timestamp ====="
  date --iso-8601=seconds

  echo "===== Host ====="
  hostnamectl 2>&1 || true

  echo "===== OS ====="
  cat /etc/os-release

  echo "===== Kernel ====="
  uname -a

  echo "===== CPU / RAM ====="
  lscpu | head -25
  free -h

  echo "===== Storage ====="
  lsblk -o NAME,SIZE,FSTYPE,FSVER,LABEL,UUID,MOUNTPOINTS
  df -hT

  echo "===== Photogrammetry Mount ====="
  findmnt /media/scottw/500GBPHOTOGRAM || true
  blkid /dev/sdb1 2>/dev/null || true

  echo "===== Podman ====="
  command -v podman || echo "podman NOT INSTALLED"
  podman version 2>&1 || true

  echo "===== systemd ====="
  /usr/lib/systemd/systemd --version || true
  systemctl --user is-system-running 2>&1 || true

  echo "===== cgroups ====="
  stat -fc %T /sys/fs/cgroup

  echo "===== GPU ====="
  lspci -nnk 2>/dev/null | grep -A3 -Ei 'VGA|3D|NVIDIA' || true
  nvidia-smi 2>&1 || true
  dpkg -l 2>/dev/null | grep -E 'nvidia-driver|cuda' | head -10 || true

  echo "===== Existing ROS/Gazebo (deviation check vs Jazzy+Harmonic spec) ====="
  ls /opt/ros/ 2>/dev/null || true
  gz sim --version 2>/dev/null | head -1 || true

  echo "===== Network ====="
  ip -brief address
  ss -tulpn 2>/dev/null || ss -tuln 2>/dev/null || true

  echo "===== Firewall ====="
  systemctl is-active ufw nftables 2>&1 || true
  # 'sudo ufw status' intentionally skipped: requires interactive sudo; captured via bootstrap instead.

  echo "===== Existing systemd services ====="
  systemctl --user list-unit-files --type=service 2>&1 | head -30 || true

  echo "===== Existing containers ====="
  podman ps -a 2>&1 || true

  echo "===== Serial devices ====="
  ls -l /dev/serial/by-id/ 2>&1 || echo "No serial devices present (Heltec not connected)"

  echo "===== Inventory complete ====="
} 2>&1 | tee -a "$LOG"

echo
echo "Inventory written to $LOG"