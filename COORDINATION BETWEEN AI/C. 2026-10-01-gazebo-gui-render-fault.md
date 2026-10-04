# COORDINATION — Gazebo Sim 10 GUI: black viewport, then a render-path abort

**From:** Cline session, 2026-10-01
**Scope:** `ao-sim-fabrication-gui-gz` (Gazebo Sim 10.5.0 client, ROS 2 Lyrical, NVIDIA)
**State:** One fault fixed and verified. Second fault **OPEN**. **NOT committed.**
**Operator constraint:** keep Gazebo and ROS 2 on NVIDIA. Do not fall back to Mesa/software.

---

## Read this first

Three things will confuse you:

1. **The Gazebo GUI is deliberately MASKED.** Do not "fix" that by unmasking it.
   A crash loop was stealing focus and the pointer and blocking the operator.
2. **`README.md` line 376 was wrong and is now corrected.** The authoritative CDI
   spec is `/var/run/cdi/nvidia.yaml`, **not** `/etc/cdi/nvidia.yaml`.
3. **Two claims in earlier notes were retracted.** `libGLX_nvidia` is present
   (a `head`-truncated grep caused the error). `GZ_RENDERING_OGRE2_WORKER_THREAD`
   does not help. Do not retry either.

---

## Symptom

Gazebo GUI window opens full-screen and renders **nothing** (black), or aborts
on its first frame:

```
Qt has caught an exception thrown from an event handler
terminate called after throwing an instance of 'std::logic_error'
  what():  basic_string: construction from null is not valid
```

Reproducible at a fixed **~0.97s after** `Camera pose topic advertised on
[/gui/camera/pose]`. Stack frames name `libQt6Core`, thread 72.

---

## Fault 1 — gz-transport discovery — FIXED, VERIFIED

**Cause:** the server runs `GZ_IP=127.0.0.1`; the GUI did not set it. Both
containers share one network namespace, so gz-transport advertised and bound
different addresses and discovery never completed.

**Symptom:** `[GUI] GUI requesting list of world names` every 5s forever, with a
black viewport while the server was healthy.

**Fix:** `Environment=GZ_IP=127.0.0.1` in
`quadlet/sim-fabrication/ao-sim-fabrication-gui-gz.container`, plus a default in
`scripts/simulation/ao-sim-gui-client.sh`. Deployed to
`~/.config/containers/systemd/`.

**Verified:** client now reaches the world — ogre2 loads, all GUI plugins load,
camera pose advertised.

---

## Fault 2 — render-path abort — OPEN, NO STACK YET

| Hypothesis | Result |
|---|---|
| Offscreen (`QT_QPA_PLATFORM=offscreen`) | **Survives 55s+** → fault is on the real GL/XCB path |
| `GZ_RENDERING_OGRE2_WORKER_THREAD=1` | **No effect** → not a render-thread race. Reverted. |
| `GZ_SIM_SERVER_CONFIG_PATH` / `GZ_SIM_RENDER_ENGINE_PATH` unset | **Not it** — server runs fine without them |
| Coredump via `ulimit -c unlimited` | **Unavailable** — container processes don't reach host systemd-coredump |
| Material spam (1210x) | Cosmetic. `gazebo.material` is at `/usr/share/gz/gz-sim/media/`, which ogre2 never loads. |

---

## NVIDIA status — healthy, keep it that way

Measured inside a container with `--device nvidia.com/gpu=0`:

- Kernel driver `580.178.04`, GPU `NVIDIA GeForce GTX 1080`
- `/dev/nvidia0` injected; 59 NVIDIA libs incl. `libGLX_nvidia.so.580.178.04`
- `eglInitialize` → 1, EGL 1.5, **`eglQueryString(EGL_VENDOR)` = `NVIDIA`**

The `__EGL_VENDOR_LIBRARY_FILENAMES` pin is load-bearing — proven by removing it:
`WITH pin → initialize=1 / vendor=NVIDIA`, `WITHOUT → initialize=0`.

**Do not remove the pin. Do not add `LIBGL_ALWAYS_SOFTWARE` or
`QT_QUICK_BACKEND=software`** — both were already tried and both prevent the
hardware context.

### CDI spec gotcha
```
/etc/cdi/nvidia.yaml      2026-08-24  pins 580.173.02  STALE — all 29 hostPaths absent
/var/run/cdi/nvidia.yaml  2026-09-30  pins 580.178.04  AUTHORITATIVE
```
The stale file contributes nothing and is silently skipped. If `/var/run/cdi`
is ever cleared, GPU passthrough breaks obscurely. Regenerating the `/etc/cdi`
copy needs root and operator approval — not done.

---

## Desktop safety — check this before launching anything

`ao-sim-fabrication-gui-gz` is **stopped and masked**.

KWin window rule 99 added to `~/.config/kwinrc` (prior file backed up to
`/tmp/kwinrc.bak`):
```
class=^gz-sim-gui   name=.*   fsp=true   act=false
```
**The rule has never been proven against a live Gazebo window.** If you start
the GUI and it seizes focus, that rule did not work — fix it before continuing.

---

## PLAN (operator-approved: reboot first, then a real backtrace)

### Step 1 — Reboot (operator action, no approval needed from me)

A reboot is **already pending**: kernel `7.0.0-38` is installed, `7.0.0-34` is
running, and `/var/run/reboot-required` exists.

The 2026-10-01 13:21 update did **not** touch the render stack
(`nvidia|libdrm|mesa|qt6` → 0 matches), so it is not the cause of the abort.
A reboot gives a clean baseline and a freshly regenerated CDI spec, removing a
variable that cannot currently be distinguished from the pre-existing fault.

### Step 2 — gdb backtrace on a THROWAWAY image tag

Requires **explicit operator approval**: it mutates a pinned image, so README
§4.1 rule 9 applies.

Constraint agreed with the operator: build a **separate tag**, e.g.
`localhost/gz-sim10-resolute:gui-svgfix-gdb`. The operational `:gui-svgfix` tag
that `ao-sim-fabrication-gui-gz.container` references must **not** be modified.

Steps:
1. `FROM localhost/gz-sim10-resolute:gui-svgfix` + `gdb` → throwaway tag
2. Run once with `gdb --args /usr/libexec/gz/sim10/gz-sim-gui-client -v 3`
3. Capture `bt full` at the `std::terminate` to identify the null `std::string`
4. Fix the real cause, then rebuild and re-pin properly

**This is the only route to a definitive answer.** Two hypotheses have already
been disproved; do not spend more effort guessing. The abort is ~0.97s after
camera pose, a strong fingerprint for first render-frame setup.

---

## Files changed (UNCOMMITTED — review before any commit)

```
README.md                                                       (NVIDIA row corrected)
quadlet/sim-fabrication/ao-sim-fabrication-gui-gz.container    (GZ_IP + comment fix)
scripts/simulation/ao-sim-gui-client.sh                        (GZ_IP, coredump ulimit)
GAZEBO/containers/gz-sim/Containerfile.resolute                (Ubuntu 26.04 / resolute)
GAZEBO/containers/gz-sim-gui/Containerfile                     (marked SUPERSEDED)
config/platform/version-matrix.yaml                            (ROS 2 / Gazebo for 26.04)
logs/operations/gazebo-gui-nvidia-verification-2026-10-01.log  (NEW: evidence + negatives)
COORDINATION BETWEEN AI/C. 2026-10-01-gazebo-gui-render-fault.md  (NEW: this file)
```

Also note: `GAZEBO/COMPATIBILITY.md` is **untracked**, carries Perplexity
branding, cites the Fortress docs for Jetty claims, and recommends
`ros-lyrical-ros-gz` — which **cannot be installed here** (`packages.ros.org`
presents a cert for `CN=*.osuosl.org`; verification was deliberately not
disabled). Recommend folding its Gazebo↔ROS compatibility table into README
§10.2.2 and deleting the file.

---

## Journal

`logs/operations/gazebo-gui-nvidia-verification-2026-10-01.log` — full evidence
chain including both retractions and the negative result.
