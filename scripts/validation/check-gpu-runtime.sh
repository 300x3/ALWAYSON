# ALWAYS ON - check-gpu-runtime.sh: record GPU/runtime state (Section 2.5).
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
out="$AO_LOG_DIR/gpu-runtime-check.log"
capture_dir="$AO_LOG_DIR/gpu-runtime"
mkdir -p "$capture_dir"
# README 16.3 requires a per-validation capture directory as well as the
# rolling log. One file per run, named for the UTC second it was taken.
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
{
  date -u --iso-8601=seconds
  nvidia-smi --query-gpu=name,driver_version,memory.total,temperature.gpu --format=csv,noheader 2>/dev/null || echo "GPU QUERY FAILED"
  echo "kernel: $(uname -r)"
  echo "podman: $(podman --version 2>/dev/null || echo missing)"
  command -v nvidia-container-toolkit >/dev/null 2>&1 && echo "nvidia-container-toolkit: present" || echo "nvidia-container-toolkit: NOT INSTALLED"
} | tee -a "$out" > "$capture_dir/${stamp}-gpu-runtime.txt"
tail -5 "$out"
grep -q "NOT INSTALLED" <<<"$(tail -5 "$out")" \
  && echo "NOTE: container GPU integration pending - CPU-only enforced (Section 2.8 step 12)" || true
exit 0
