ALWAYS ON GPU runtime validation captures (README Section 16.3)

One file per GPU runtime validation run, named
  <UTC timestamp>-gpu-runtime.txt
Each capture holds the same fields as ../gpu-runtime-check.log:
GPU name, driver version, memory, temperature, kernel, podman version,
nvidia-container-toolkit presence, and whether GPU access was granted to
the workload.

Created 2026-10-02 during the Section 16.3 audit. Directory was empty:
check-gpu-runtime.sh appends only to ../gpu-runtime-check.log and did not
write per-run captures.

Never record a secret value here (README Section 4.2).
