# ALWAYS ON - check-gpu-runtime.sh: record GPU/runtime state (Section 2.5).
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
out="$AO_ROOT/logs/gpu-runtime-check.log"
{
  date -u --iso-8601=seconds
  nvidia-smi --query-gpu=name,driver_version,memory.total,temperature.gpu --format=csv,noheader 2>/dev/null || echo "GPU QUERY FAILED"
  echo "kernel: $(uname -r)"
  echo "podman: $(podman --version 2>/dev/null || echo missing)"
  command -v nvidia-container-toolkit >/dev/null 2>&1 && echo "nvidia-container-toolkit: present" || echo "nvidia-container-toolkit: NOT INSTALLED"
} >> "$out"
tail -5 "$out"
grep -q "NOT INSTALLED" <<<"$(tail -5 "$out")" \
  && echo "NOTE: container GPU integration pending - CPU-only enforced (Section 2.8 step 12)" || true
exit 0
