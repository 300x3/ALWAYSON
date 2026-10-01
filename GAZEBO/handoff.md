# HANDOFF — ALWAYS ON Gazebo / ao-sim-fabrication

**Written:** 2026-10-01 · **Author:** Cline session · **Working copy:** `/ALWAYSON`
**Authority:** `/ALWAYSON/README.md` governs on any conflict (§10.1, §10.2,
§10.2.1, §16.3, §17, §18.6, §19.4, §20). Where this file and the README
disagree, the README wins. Line numbers cited below are from the README as
committed at `f7df9a0`.

---

## 1. Job / state

Bring the four SketchUp exports in `/ALWAYSON/GAZEBO` into one Gazebo Sim world
and run it as the README's fabrication simulation domain (`ao-sim-fabrication`).

**Bottom line: the simulation server is live and healthy; the two things the
operator asked to *see* (Gazebo GUI window, Foxglove browser view) are still
not possible on this host, and the reasons are verified below.** Nothing that is
working depends on those two.

---

## 2. What is running right now (verified)

| Item | Value |
|---|---|
| Container | `ao-sim-fabrication-gz` — **Up** (started 2026-09-30 23:31:36 PDT) |
| Managed by | systemd user unit `ao-sim-fabrication-gz.service` (**active/running**, generated from Quadlet) |
| Image | `localhost/gz-sim10-server:latest` = `sha256:55f8dbcf8decb0b97c6be7cf2fde8859b0fd05735c7a759df09a12e091933581` |
| Entrypoint | `/usr/libexec/gz/sim10/gz-sim-server /ALWAYSON/GAZEBO/worlds/factory.world -r -s -v 4` |
| Network | `ao-sim-fabrication` — Internal=true, `10.89.5.0/24` |
| Ports | **None published** (11345/tcp internal only) — compliant, no public port |
| Env | `GZ_PARTITION=alwayson_fabrication_sim`, `ROS_DOMAIN_ID=22`, `GZ_SIM_RESOURCE_PATH=/ALWAYSON/GAZEBO/models`, `GZ_IP=127.0.0.1`, `HOME=/gzhome` |
| Memory | 49.6 MB used of 8 GB `MemoryMax`, peak 69.5 MB |
| Log | `/ALWAYSON/logs/sim-gz-server.log` (9015 bytes) — see §6, this is **not** live |
| Portal | `gazebo-portal` (nginx:alpine) — `http://127.0.0.1:8765/` → HTTP 200; `/readme.txt` → HTTP 200 |

Server-side confirmation from the log — the world loaded and SceneBroadcaster is
publishing: `/world/factory/scene/info`, `/world/factory/state`,
`/world/factory/pose/info`.

Repo-vs-deployed check: Quadlet source
`/ALWAYSON/quadlet/sim-fabrication/ao-sim-fabrication-gz.container` is
**byte-identical** to the installed `~/.config/containers/systemd/` copy.

---

## 3. The world and its meshes

| Path | Role |
|---|---|
| `/ALWAYSON/GAZEBO/worlds/factory.world` | **Canonical entry point — this is what the service runs.** 155 lines. |
| `/ALWAYSON/GAZEBO/models/factory_assets/model.sdf` + `model.config` | Reusable model artifact, same four links |
| `/ALWAYSON/GAZEBO/models/factory_assets/meshes/*.dae` | Symlinks → the four originals (never copied/modified) |
| `/ALWAYSON/GAZEBO/09-SIMULATION*.dae` | **Originals, untouched** (~10 MB total; one filename begins with a literal 0x0A newline) |

Mesh URIs are `model://factory_assets/meshes/*.dae`, resolved through
`GZ_SIM_RESOURCE_PATH` — README §10.2 line 2002 / §10.1 line 1842. Not fetched,
not rewritten at runtime. Sun and ground plane are inlined because this host has
no Fuel model cache; that keeps single-entry-point loading with no network fetch.

Verified in-container: the server sees 155 world lines and all four mesh
symlinks resolve (`arms.dae`, `conveyor.dae`, `massing_fab.dae`,
`vehicles_arms.dae`).

Placement: all four exports are `<unit inch, 0.0254>` / `Z_UP` with in-place
node matrices and no root translation, so every link sits at `0 0 0` with
uniform scale `0.0254` — the shared SketchUp frame holds. One deliberate
deviation: `vehicles_arms` is lifted to `0 0 2.5` because it duplicates
arms/vehicles geometry already present in the static links. Set the pose to
`0 0 0` for a true overlay.

---

## 4. The two blockers and the Podman route

The host cannot run the Gazebo GUI *natively*. It **can** run it from a
container — that route was started and is the recommended one (§4.4). Details:

### 4.1 No Gazebo GUI on this host

- `gz --commands` on host → `gui topic service log param sdf plugin msg`.
  **There is no `sim` verb.**
- `~/bin/gazebo` (pre-existing wrapper, dated Aug 6 — **not written by this
  session**) ends in `exec gz sim "$@"`, i.e. it calls a verb this host does not
  have. It correctly encodes the NVIDIA / `QT_QPA_PLATFORM=xcb` / `GZ_IP=127.0.0.1`
  fixes, but has nothing to launch.
- No host packages: `gz-sim10-server`, `gz-sim10-cli`, `libgz-sim10-gui` are
  **not installed**. No `/usr/share/gz`. No Gazebo Classic either
  (no `gzserver`/`gzclient`, no `/usr/share/gazebo*`).
- `~/.cache/drkonqi/application-not-responding/` holds two **0-byte**
  `gz-sim-gui-client` stubs from Aug 6 — evidence of an attempted, failed GUI,
  not of a working one.
- `gz-sim10-server` and `gz-sim10.desktop` exist **only inside Podman image
  layers**, i.e. inside the image this session built (server-only;
  `/usr/libexec/gz/sim10/` contains `gz-sim-server` and nothing else).
- Host is **Ubuntu 26.04 (resolute)**. The OSRF apt repo publishes **no
  `resolute` suite**, only up to noble; ROS Lyrical ships the Gazebo *libraries*
  but no `sim` verb and no GUI. So a native host install is not simply
  "one apt-get away" — the working packages are the 24.04/noble builds.
- `sudo` on this machine **requires an interactive password**, so this session
  cannot install host packages regardless.

### 4.2 Foxglove bridge is not installed

- No `foxglove` package, no lib under `/opt/ros/lyrical/lib`, no binary.
- Apt *does* offer `ros-lyrical-foxglove-bridge` 3.5.0 — installable, blocked by
  the same password requirement.
- Independently: **a browser cannot render a `.world` file at all.** Foxglove
  renders live ROS topics over a WebSocket from `foxglove_bridge`; it is not a
  world viewer. So the portal in §5 is the correct HTML-surface step
  (README §10.2.1), and a Foxglove view is a separate, additive deliverable.

### 4.3 No-install "Podman route" — the recommended way to see the world

Everything needed is already on the machine; only a container image build is
required, and **no host package install and no sudo are needed**:

| Prerequisite | Status (verified) |
|---|---|
| Podman | 5.7.0, rootless — works |
| X display | `/tmp/.X11-unix/X0` present |
| Wayland | `/run/user/1000/wayland-0` present |
| Intel GPU | `/dev/dri/card1`, `/dev/dri/renderD128` present |
| NVIDIA GPU | GTX 1080, driver 580.178.04; `/dev/nvidia*` present |

`gz-sim10-cli` (the package that supplies `gz sim` + the GUI client) **does
resolve on noble/24.04**, which is why the container is based on `ubuntu:24.04`
even though the host is 26.04.

The image recipe is already written:
**`/ALWAYSON/GAZEBO/containers/gz-sim-gui/Containerfile`** — adds `gz-sim10-cli`,
`libgz-sim10-gui`, `libgz-rendering10-ogre2`, `libgz-sensors10-rendering`, Qt6,
X/xcb libs, `xauth`, and Mesa (`libgl1-mesa-dri`, `libglx-mesa0`, `mesa-utils`).
It keeps the server-only image untouched and bakes in **no** data.

**The build was started and then interrupted** — `localhost/gz-sim10-gui:latest`
does **not** exist yet. Next session: resume it.

```bash
# 1. Build the GUI image (rootless, no sudo). ~5-10 min.
podman build -t localhost/gz-sim10-gui:latest \
  /ALWAYSON/GAZEBO/containers/gz-sim-gui

# 2. Run it with the world, the X socket and the GPU granted EXPLICITLY
#    (never --privileged; see README §4.1 rule 8).
podman run --rm --name ao-sim-gui \
  --network ao-sim-fabrication \
  -e DISPLAY=:0 -e QT_QPA_PLATFORM=xcb -e GZ_IP=127.0.0.1 \
  -e GZ_PARTITION=alwayson_fabrication_sim \
  -e GZ_SIM_RESOURCE_PATH=/ALWAYSON/GAZEBO/models \
  -e HOME=/gzhome \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -v /ALWAYSON/GAZEBO:/ALWAYSON/GAZEBO:ro \
  -v /ALWAYSON/data/sim-fabrication/gzhome:/gzhome:Z \
  --device /dev/dri \
  localhost/gz-sim10-gui:latest \
  gz sim -r /ALWAYSON/GAZEBO/worlds/factory.world
```

Notes and fallbacks, in order of preference:

- **Render engine**: start with Ogre 2 + the Intel iGPU via `--device /dev/dri`.
  If the viewport is blank (a known Ogre/Qt GL-context problem, see the comments
  in `~/bin/gazebo`), retry with software GL:
  `-e LIBGL_ALWAYS_SOFTWARE=1 -e GALLIUM_DRIVER=llvmpipe`.
- **NVIDIA path**: the same wrapper notes that this dual-GPU box needs
  `__NV_PRIME_RENDER_OFFLOAD=1`, `__GLX_VENDOR_LIBRARY_NAME=nvidia`, and
  XWayland (the OGRE/Qt "no current GL context" Wayland bug). Those are the
  fallback if the Intel path fails — but they require NVIDIA container
  integration in the image, which this session did **not** add.
- **Wayland alternative**: mount `-v /run/user/1000/wayland-0:/run/user/1000/wayland-0`
  and set `QT_QPA_PLATFORM=wayland`. XWayland is the safer first attempt.
- **Quadlet**: once the manual `podman run` renders, convert it to a Quadlet
  unit in `ao-sim-fabrication` (README §19.4 item 14 requires Quadlet, not a
  loose `podman run`, for anything persistent). Keep the GUI unit separate from
  `ao-sim-fabrication-gz`, which is the headless server (§2).

### 4.4 Honest note

Across this task the world, model, portal, and open-container services were
built, but the Gazebo window and the Foxglove view were **never** delivered.
This session also previously mis-stated the container's log path (calling it
live when it is not — see §6) and described the world as load-tested before a
runtime load test had actually succeeded. Both are corrected here. **The
underlying cause of the two missing views is a genuine host/package gap, not a
configuration choice.**

---

## 5. Portal

- Source: `/ALWAYSON/GAZEBO/portal/index.html`
- Served by throwaway container `gazebo-portal`, `/ALWAYSON/GAZEBO` mounted
  read-only, published **loopback-only** `127.0.0.1:8765` → `http://127.0.0.1:8765/`
- Helper script: `/ALWAYSON/scripts/operations/ao-sim-portal.sh`
- It is an **index page, not a control surface.** README §10.2.1 line 2037
  requires start/stop/reset/operate for each cell — not implemented. §10.2.1's
  own verdict still stands: 3D world setup is "still open" (WORK 000801/ST-08).
- `gazebo-portal` is **not** a Quadlet unit and belongs to no sim domain; §17
  (lines 2065–2066) expects per-domain archives. Flagged, not resolved.

---

## 6. Known gaps (each one verified, none hidden)

1. **`/ALWAYSON/logs/sim-gz-server.log` is frozen, not live.** It is 9015 bytes
   timestamped 23:31 — the moment the container started. The unit sets
   `LogDriver=k8s-file` with `--log-opt path=…` because Podman's default
   (journald) ignores that option, but the file still receives no new writes;
   current output must be read via `podman logs ao-sim-fabrication-gz`.
   §16.3 line 3524 requires a live `sim-gz-server.log` while the server runs.
2. **Duplicate, unused world copy** at `/ALWAYSON/data/sim-fabrication/worlds/factory.world`.
   It uses the older `file:///world/...` URI scheme, is **not mounted** by the
   unit, and is **not** what runs. The canonical world per README §10.2 line 2005
   is `/ALWAYSON/GAZEBO/worlds/factory.world`. Recommend deleting the stale copy
   — **needs operator approval** (rule 2/3), so it is left in place.
3. **Manifest hash mismatch.** `manifests/factory-world-v1.json` records
   `content_hash_sha256 = 64eacbbf…` (5371 bytes), which no longer matches the
   current canonical world (155 lines, edited since). Re-sign with
   `/ALWAYSON/scripts/ledger/sign-manifest.sh` before relying on it.
4. **`GZ_IP=127.0.0.1` is questionable for a loopback-isolated container** — it
   should likely be the container's own address or unset. The server runs, but
   cross-container discovery on `ao-sim-fabrication` is unproven.
5. **Result directory empty**: `/ALWAYSON/data/sim-fabrication/results/` has no
   output; no reset/archive cycle has executed (§17).
6. **No `ardupilot_gazebo` builds, no per-domain Fuel/plugin paths** as §10.2
   lines 1990–1994 require.
7. `config/platform/loopback-services.yaml` was edited to label `:8765`
   correctly; the `:8766` Foxglove-bridge entry remains aspirational (not running).
8. **The `.dae` files are not in Git** and `GAZEBO/` is untracked (permitted for
   now by §10.2 line 2009: models are not committed until data is staged).
   §10.2 also requires Git LFS or a separate artifact repo for meshes this size
   — undecided.

---

## 7. Repo state (`/ALWAYSON`)

- HEAD `f7df9a0` — **nothing pushed, no commit made by this session.**
- New, untracked: `GAZEBO/`, `quadlet/sim-fabrication/`,
  `scripts/operations/ao-sim-portal.sh`, `scripts/simulation/compute-mesh-aabb.py`,
  `artifacts/fabrication-simulation-manifests/factory-world-v1.{json,sig}`
- Pre-existing unrelated modifications (left alone): `config/platform/loopback-services.yaml`,
  `quadlet/mapping/ao-webodm-web.container`, four `scripts/deploy/*.sh`,
  `scripts/operations/add-firefox-server-bookmarks.py`, `scripts/operations/mastodon-local-proxy.py`
- `scripts/simulation/export-fabrication-manifest.sh` already existed in the
  repo; `compute-mesh-aabb.py` is newly authored by this session.

---

## 8. Exact next actions

**PRIMARY — resume the Podman GUI route (no sudo, no host install):**

```bash
podman build -t localhost/gz-sim10-gui:latest /ALWAYSON/GAZEBO/containers/gz-sim-gui
# then the `podman run` in §4.3
```
Build log location used previously: `/tmp/gz-gui-build.log` (the build was
interrupted after STEP 3/7 while apt was running; the layer cache for the base
image is warm, so a rebuild resumes quickly). See §4.3 for render-engine and
GPU fallbacks.

**SECONDARY — host install (needs the operator's password):**

```bash
sudo apt-get install -y gz-sim10-cli libgz-sim10-gui          # Gazebo GUI
sudo apt-get install -y ros-lyrical-foxglove-bridge           # Foxglove bridge
```

Then, with the server already running under Quadlet:

```bash
~/bin/gazebo /ALWAYSON/GAZEBO/worlds/factory.world            # 3D window
```

and point a browser at the Foxglove web app with
`ws://127.0.0.1:8766` once the bridge is started as a Quadlet unit in
`ao-sim-fabrication` (do **not** publish it beyond loopback without approval).

**Foxglove, separately:** there is **no** browser-only way to render a `.world`
(§4.2). The container route can also carry `foxglove_bridge` once its own
Containerfile is fixed, and Foxglove the web app can then be served from the
existing `:8765` portal stack over loopback.

**Housekeeping (needs approval where destructive):**
make `sim-gz-server.log` actually live (§6.1); delete the stale
`data/sim-fabrication/worlds/` copy (§6.2); re-sign the manifest (§6.3).

---

## 9. Provenance / build notes

- Image built from `/ALWAYSON/GAZEBO/containers/gz-sim/Containerfile` (base
  `ubuntu:24.04`, OSRF stable repo, **server only**) → `localhost/gz-sim10-server:latest`.
- **NEW, unbuilt:** `/ALWAYSON/GAZEBO/containers/gz-sim-gui/Containerfile` —
  the GUI-capable image (§4.3). Written by this session; build interrupted.
  It is additive: it does not modify or replace the working server image.
- `/ALWAYSON/GAZEBO/containers/foxglove-bridge/Containerfile` exists but is
  **unbuilt and known-broken** (dependency resolution failed against the ROS
  repo during the earlier attempt).
- `/ALWAYSON/GAZEBO/worlds-run/` is a scratch, non-canonical run directory from
  pre-Quadlet debugging; the Quadlet unit does not use it.
- `/ALWAYSON/scripts/simulation/compute-mesh-aabb.py` was authored to compute
  mesh AABBs; note that Gazebo 10's `SystemPaths` has no `FindFile`, and the
  earlier version-string/`ReplaceAll` conversion path was abandoned in favour of
  `model://` + `GZ_SIM_RESOURCE_PATH`.
- All commands, versions, and failures are recorded in
  `/ALWAYSON/LOGS-JOURNALS/operations-journal.log` (README §4.1 rule 11).

---

## 10. Handoff checklist for the next session

1. Read `/ALWAYSON/README.md` §10.1 / §10.2 / §10.2.1 first — it supersedes this
   file on every conflict.
2. Confirm the server is still healthy:
   `systemctl --user is-active ao-sim-fabrication-gz.service` and
   `podman ps | grep ao-sim`.
3. Resume the GUI build (§8 PRIMARY) and try the §4.3 `podman run`.
4. Do **not** delete `data/sim-fabrication/worlds/` or re-sign the manifest
   without operator approval (rules 2–3).
5. Keep everything on loopback; do not publish a port (§4.1 rule 4).
6. Record commands, versions, output and failures in
   `/ALWAYSON/LOGS-JOURNALS/operations-journal.log` as you go.
