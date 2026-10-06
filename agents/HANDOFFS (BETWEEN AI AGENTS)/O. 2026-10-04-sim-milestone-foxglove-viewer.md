# O. ao-sim-fabrication — Gazebo world + local Foxglove viewer complete, tagged as a milestone

**From:** AI-SIM session (2026-10-02 → 2026-10-04)
**Scope:** `ao-sim-fabrication` (Gazebo world, Foxglove bridge, HTML portal, local viewer)
**State:** COMMITTED and PUSHED. Tag `sim-milestone-2026-10-04` on `cad306b`.
`origin/main` 0 ahead / 0 behind at time of writing. Nothing OPEN in this subsystem.

## Read this first

1. **The restore point is `sim-milestone-2026-10-04`.** To roll back:
   `git reset --hard sim-milestone-2026-10-04`. The four commits at the end of
   this document are the whole session's work.
2. **The journal is gitignored and therefore LOCAL ONLY:**
   `logs/operations/sim-fabrication-view-only-2026-10-02.log`, CHANGEs 1–18.
   Every command, measurement and failure is in it. **Copy it somewhere durable
   if a new session needs it** — it will not survive a fresh clone.
3. **Two failed approaches are recorded there so nobody retries them.** Both
   failed for reasons not obvious from the code; see "Two dead ends".
4. **Supersedes nothing.** Documents **C** and **G** describe the Gazebo GUI
   fault and visual-mesh problems; both are fixed and those documents are now
   historical. **G**'s claim that the GUI unit is masked is still wrong — it is
   `generated`/`inactive`. **L** and **M** describe camera placement that has
   since been redone; the camera set below is authoritative.
5. **This branch diverges fast.** With 11 sessions active `main` fell behind
   repeatedly. Always `git fetch && git rebase origin/main` before pushing, and
   never force-push a shared branch.

## What is running (verified at tag time)

| Unit | State | Notes |
|---|---|---|
| `ao-sim-fabrication-gz` | active | server, `factory.world` valid, 8 cameras advertising |
| `ao-sim-fabrication-foxglove` | active | gz→ROS only, view-only enforced |
| `ao-sim-fabrication-portal` | active | python3 host service on `127.0.0.1:8765` |

Operator surfaces: portal `http://127.0.0.1:8765/`, viewer
`http://127.0.0.1:8765/viewer`, bridge `ws://127.0.0.1:8081` (WebSocket only —
no HTML page; a browser pointed at it gets nothing).

## The four faults fixed, in the order they had to be

Every one presented as the *same* symptom — an empty viewer. Each masked the next.

1. **Bridge had no route to the server.** The Quadlet declared only
   `ao-html-window`, so the bridge sat on a different L2 segment. gz-transport
   discovery is UDP multicast, so a matching `GZ_PARTITION` partitions traffic
   but does not route between two `Internal=true` bridges. Fixed with a second
   `Network=` line.
2. **`GZ_IP=127.0.0.1` on the server.** The GUI only ever worked because it
   *shares the server's network namespace*; the bridge does not. Server now
   `GZ_IP=0.0.0.0`.
3. **No camera sensor instantiated.** `$GZHOME/.gz/sim/10/server.config` names
   three systems; without a world-level `<plugin>` block Gazebo loads exactly
   those three. No Sensors system → no render thread → no camera, **silently**,
   while the server looks healthy. Proved by A/B test in throwaway containers
   before touching the live world.
4. **The bridge could not load its own libraries.** `ldconfig -p | grep -c gz`
   returned **0**. `libgz-transport.so.15` and `libgz-msgs.so.12` live in five
   `gz_*_vendor/lib` directories on no loader path, and the ROS middleware
   directory was missing entirely. Process stayed alive, accepted connections,
   bridged nothing, no error anywhere.

Also: wrong binary and wrong type mapping. `bridge_node` creates no publisher at
all; the working spec is
`parameter_bridge '/factory/camera/image@sensor_msgs/msg/Image[gz.msgs.Image'`
(`[` = gz→ROS only).

## View-only, enforced and proved

- Bridge: `capabilities` without `clientPublish`/`parameters`/`services`;
  whitelist is the camera topics only. The probe that previously returned
  `SERVER ACCEPTED a new writable channel: /factory/cmd_vel` now returns
  `Server does not support clientPublish capability`.
- Portal: `start`/`stop`/`reset` removed and `unit_action()` **deleted**, so no
  code path connects HTTP to systemd. `do_POST` → 405 for everything. Operator
  lifecycle control is the `ao-`-prefixed CLI
  `scripts/operations/ao-sim-portal.sh {start|stop|reset|inspect|status}`.
- **Rejected:** probing Gazebo's `/server_control` for status. That is the world
  *control* service — probing it from a "read-only" portal would have rebuilt
  the exact write path being removed. Status is filesystem-only.
- **KDE Wallet holds nothing for the viewer.** A loopback WebSocket has no
  account, token or password, so there is no credential to store.

## Camera set

Eight cameras on `/factory/camera/*`, all aimed from `GAZEBO/sim/boning.yaml`
datums. Standoff is `d = (across-frame width / 2) / tan(h_fov / 2)`.

**Trap:** across-frame width is the axis *perpendicular* to the view direction.
An east/west elevation's frame width is the **Y** extent, not X. Using the boned
extent named in the file put the east elevation 5 m too far out.

- Four arm-cell vantages (`arms_ne/n/se/e`) — the cell is in the building's
  north-east corner, so most azimuths are blind. Measured clear: az 65–115 only.
  Vantages therefore differ in **distance and elevation**, not just azimuth.
- Three true elevations at pitch exactly `0.0000` (`elev_arms` north,
  `elev_conveyor` south, `elev_massing` east), `horizontal_fov` 0.6.
- Default camera saved in **both** `factory.world` and
  `~/.local/share/ao-simulation/gui-home/.gz/sim/10/gui.config`.

## Console traps on this host

- **`ao-sim-fabrication-portal.service` is `Type=simple`.** `systemctl restart`
  does **not** replace the process — it needs `stop` + `pkill -9` + `start`.
  This caused a real incident: a live `POST /api/reset` probe restarted the
  running simulation because the old process was still serving.
- **Collada unit trap.** The monolithic exports declare
  `<unit meter="0.0254" name="inch"/>`, so `scale` must be **1.0**. But
  `split-collada-parts.py` emits `<unit meter="1" name="inch"/>`, so its parts
  need **`scale 0.0254`**. Backwards makes geometry invisible — this is what hid
  the entire plant earlier (double unit conversion, `0.0254²`).
- **DP-3 spans y 738–1818**, not 0–1080. "Bottom-left" is near `(0, 1818)`.
  Browser testing is pinned there by
  `~/.local/share/kwin/scripts/ao-browser-testing/` and the Cline rule
  `~/.cline/rules/20-browser-testing-placement.md`.

## Rendering: what actually fixed the shading

**Measured root cause:** the mesh carries **smoothed vertex normals**, not face
normals. `<vertices>` binds a `NORMAL` source and **vertex indices are shared
between triangles**. Corner normals within one triangle disagreed by up to
**56°**, so the engine interpolated a gradient across every triangle.

**Fix:** `scripts/simulation/flatten-panel-normals.py` drops the `NORMAL`
binding from `<vertices>` in the derived `meshes/massing_flat.dae`. The engine
then derives a face normal per triangle. Coplanar triangles in one panel differ
by well under a degree, so a panel reads as one flat polygon, while genuinely
different panels keep distinct normals — which is what lets the edge overlay find
the boundaries. Source export `massing_fab.dae` untouched.

An earlier attempt to shade the massing **emissive-only** (ambient/diffuse zero)
was an over-correction: it removed the very luminance step the edge overlay
depends on, so panel-to-panel boundaries became invisible. Reverted.

### Two dead ends — do not retry

1. **Averaging normals per planar group, written into the existing NORMAL arrays
   in place.** Triangles with corner disagreement only 11436 → 10915, and the
   worst case got *worse*, to **180°**. Cause: indices are shared, so coplanar
   and non-coplanar triangles fight over the same vertex slot and the last writer
   wins with an opposite normal.
2. **ElementTree round-trip of the whole Collada document** to add a new NORMAL
   source. Emitted malformed output — namespace handling did not survive, and
   `<vertices>` picked up a stray NORMAL input. Derived mesh was deleted rather
   than shipped into a live world.

### Edge linework is viewer-side, not in the render engine

gz-sim 10 has **no outline or post-process pass**. `gazebo.material` ships 90
materials; the only wireframe support is a single `polygon_mode wireframe` pass
inside `Gazebo/TurquoiseGlowOutline`, which draws every DAE **triangle** rather
than real edges. `libgz-rendering10` exports no outline symbol.

So the linework is a **Sobel pass in the viewer** (`applySobel()` in
`GAZEBO/portal/viewer/index.html`, `edge lines` checkbox, on by default).
Consequence: **Gazebo's own GUI shows the flat colour but not the linework.**

Two bugs worth not repeating:
- `applySobel()` was first called *after* `dctx.putImageData()`, so the modified
  pixels never reached the canvas and the view was pixel-identical with the
  toggle on and off. It must run **before** the blit.
- At ink 0.97 nearly every detected pixel went black and the small arms and
  conveyor detail became solid blobs. Capped to 0.80, range 9–52.

Shadow casting is **off** (operator decision): the geometry is flat interior wall
panels, so a shadow map produced acne and banding rather than form.

## Open findings

1. **Blue doors not implemented.** `massing_fab.dae` has no semantic part names
   (anonymous `group_0`–`group_25`), and the splitter returns a degenerate
   signature — every part comes back as a cube. Needs the model re-exported from
   the CAD tool with named groups. **Needs operator approval.**
2. **Signed world manifest is stale.** Records 5371 bytes; the world is now
   ~18 KB. Cosmetic — it describes an exported artifact, not the running world.
   Re-signing needs the `ao-sim-fabrication` key: **operator decision.**
3. **Panels are still 2–5 triangles each in the file.** Fixed visually, not
   topologically. True single-polygon panels need welding in the source CAD and
   a re-export.
4. **RL objects are a catalogue, not world entities.** `objects.yaml` declares
   the objects live in a non-static `rl_objects` model written to for
   spawn/pose/delete. That model is **not in `factory.world`**, so `/api/objects`
   serves objects Gazebo has never instantiated. README §19.2 item 83.
5. **Facility scheduler and safety-zone/interlock model absent.** Named in the
   §10.2 architecture tree, not in the repo. README §19.2 items 81 and 82. The
   interlock model is the safety-relevant one.
6. **Not published.** The viewer is not exposed at `www.300x3.com`. README §19.2
   item 69. Needs the hostname and a change to `~/.cloudflared/config.yml`,
   which is customer-facing production config.
7. **Stray debug containers** `vigorous_shannon` and `dreamy_rosalind` still
   running from 2026-10-01. README §19.2 item 73. Deletion needs operator
   approval per rule 3.
8. **`elev_arms` frames the boned arms-cell datum**, which is narrower than the
   as-built arm cluster, so the arms sit right-of-centre. Fixing it needs the
   as-built arm centroid, which `boning.yaml` does not carry.

## Housekeeping

- `GAZEBO/sim/conveyor_loops.yaml` tracked as of `cad306b`.
- `factory.world.bak.*` backups and stray screenshots cleaned up earlier;
  `logs/` is gitignored.
- Untracked in the tree at tag time and **not mine**: `COORDINATION BETWEEN AI/`
  (this folder), `TOPOLOGY/*` (~25 files), `README.pdf`.

## The four commits in this milestone

```
cad306b chore(sim-fabrication): track the conveyor loop layout data
ec34c71 fix(sim-fabrication): flat-shade the structure mesh so panels read as single planes
c24f673 fix(sim-fabrication): shade the massing emissive-only so panels read flat
dc72f5c feat(sim-fabrication): flat neutral structure with edge linework
```

Conveyor loops built by `scripts/simulation/build-conveyor-loops.py`: 10 loops,
one motorbox each — two pairs low/high at storage, three pairs low/mid/high
across the freezer, fridge and pantry area. **The loads/sleds are deliberately
not modelled** — the operator is modelling those.