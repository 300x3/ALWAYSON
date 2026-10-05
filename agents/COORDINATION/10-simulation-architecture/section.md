# 10. Simulation Architecture

## 10.1 Vehicle Simulation

```text
ao-sim-vehicle
├── ROS 2 Lyrical
├── Gazebo Sim 10.5.0
├── ArduPilot SITL
├── ROS-Gazebo bridge
├── MAVLink router
├── QGroundControl simulation client
├── Optional Stable-Baselines3 evaluation
├── Mission and scenario runner
└── Vehicle-result exporter
```

```text
ROS_DOMAIN_ID=21
GZ_PARTITION=alwayson_vehicle_sim
```

### 10.1.1 SITL method, verified against ardupilot.org

Verified 2026-09-29 against the ArduPilot developer documentation. SITL
(Software In The Loop) is the autopilot firmware built as an ordinary native C++
executable and run without any hardware; sensor data comes from the simulator.
ArduPilot connects to the simulator over MAVLink, and MAVProxy is the ground
control station.

```text
Gazebo (gz sim -v4 -r <world>.sdf)
   │  ArduPilot Gazebo system plugin
   │  (github.com/ArduPilot/ardupilot_gazebo — does NOT depend on ROS)
   ▼
ArduPilot SITL  (sim_vehicle.py -v ArduCopter -f gazebo-<model> --model JSON --map --console)
   │  MAVLink
   ▼
MAVProxy GCS  ──► QGroundControl (simulation client)
```

Required environment, per the ArduPilot documentation:

- `GZ_VERSION` must be set to the installed Gazebo release.
- `GZ_SIM_SYSTEM_PLUGIN_PATH` must include the built `ardupilot_gazebo`
  plugin directory.
- `GZ_SIM_RESOURCE_PATH` must include the plugin's `models/` and `worlds/`
  directories.
- With ROS 2 in the loop, ArduPilot's DDS support is used: build SITL with DDS
  enabled, set `DDS_ENABLE=1`, and make ArduPilot's `DDS_DOMAIN_ID` match the
  environment's `ROS_DOMAIN_ID`. Set them together and relaunch SITL if they
  change.

The standard example invocations are:

```bash
gz sim -v4 -r iris_runway.sdf
sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --map --console
```

ArduPilot SITL can simulate multi-rotor aircraft, fixed-wing aircraft, ground
vehicles, underwater vehicles, camera gimbals, antenna trackers, and a wide
variety of optional sensors. The vehicle profiles below therefore must be
selectable at run time, ideally at rapid speed, by changing the ArduPilot
vehicle type and the Gazebo model, not by rebuilding anything.

Vehicle profiles must allow for switching between the following, ideally at
rapid speed, by changing the ArduPilot vehicle type and the Gazebo model:

- Bicopter profile.
- Fixed-wing VTOL tailsitter profile.
- Rover (quadcycle) profile.
- Dual-rotating underwater/submersible profile.
- Boat mast/sail control profile.
- Boat bow/stern thruster profile.
- Boat bow/stern airboat fan profile.
- Wind, terrain, obstacles, routing, takeoff, and landing events.
- Camera, GPS, IMU, barometer, rangefinder, battery, and MAVLink behavior.
- GPS loss, packet loss, actuator faults, sensor drift, and failsafe handling.

Vehicle simulation must never connect to live flight controllers, field radios,
real drone telemetry, payment services, customer records, or Corda core.
### 10.1.2 Baseline capability: 3D world, boning, reinforcement learning objects, HTML portal

Required by ES.1 for **both** simulation domains. For `ao-sim-vehicle` these four are
baseline deliverables, not optional extras, and they are tracked as §19.1 SIM-04 (ST-07).

**3D world setup.** The domain stands up its own Gazebo world as a first-class artifact:
the world file, its models, their poses, the lighting and environment, the ground and
surface materials, the physics and collision configuration, and the spawn points. World
setup must be scripted and repeatable from a single entry point rather than assembled by
hand in the GUI, so the same world can be rebuilt identically on any host.

**Boning.** The world carries a boning and alignment structure: a defined datum frame per
model, declared mounting and reference surfaces, joint and axis definitions, and the
tolerances between them. Boning is what makes the world measurable rather than merely
pictorial — a pose is verified against the boning frame instead of being eyeballed, and
a model that has drifted out of tolerance is detectable programmatically. The boning data
must be exported alongside the world so the same checks run against recorded evidence.

**Reinforcement learning objects.** The trainable entities for scenario and policy work:
marked, individually addressable objects with observable state, reward-relevant properties,
and defined reset behaviour. They must be separable from the static world geometry so a
training run can vary object count and placement without rebuilding the world. The optional
Stable-Baselines3 evaluation consumes these objects; the objects are required even where no
trainer is attached yet.

**HTML portal.** The whole environment is exposed through a browser-served HTML portal:
view the live model and sensor state and read back boning and tolerance measurements. The
portal is **view-only** — it exposes no route that can start, stop, reset or otherwise
modify the simulation. World lifecycle is an operator CLI run locally. It runs inside
`ao-sim-vehicle` and is reachable only by the approved local path — the same isolation
rule that forbids this domain from touching live flight controllers applies to the portal
as well. It must never become a path by which the simulation reaches anything outside its
own domain.


## 10.2 Fabrication and Facility Simulation

Gazebo Sim model views of the fabrication and facility domain. These show the modelled
robot-arm cells, vehicle and shelving layout, and kitchen/storage volumes referenced
below. They are **rendered model views, not operational evidence** — no flight-control
or live-machinery path is enabled by anything shown here.

![Simulated fabrication domain: robot arm, vehicle, and robot arm vehicle work areas](assets/sim-robot-arm-vehicles.png)

*Figure 10.2a — Robot-arm work area, vehicle bay, and robot-arm vehicle bay within the fabrication domain.*

![Simulated shelving and storage elevation with robot-arm cells](assets/sim-shelving-front.png)

*Figure 10.2b — Storage and shelving elevation with robot-arm cells, and the shelving-to-printer aisle.*

![Simulated shelving and kitchen volume from the opposite approach](assets/sim-shelving-rear.png)

*Figure 10.2c — Storage, shelving-to-printer, and kitchen volumes from the reverse approach.*

```text
ao-sim-fabrication
├── ROS 2 Lyrical
├── Gazebo Sim 10.5.0
├── Industrial engineering and production coordination (REHEARSED — no production data;
│   real machines are in ao-fabrication, §3.3.0)
├── Assembly stations
├── Storage and inventory cells
├── Refrigerator, freezer, and pantry models
├── Kitchen and pass-through models
├── Carousels and conveyors
├── Facility scheduler
├── Safety-zone and interlock model
└── Fabrication-result exporter
```

```text
ROS_DOMAIN_ID=22
GZ_PARTITION=alwayson_fabrication_sim
```

The machines — MainsailOS, Moonraker, Klipper on the BigTreeTech CB1/RPi, and the
individual additive-manufacturing machines (3D printers and CNC machines) — are
real machines, not simulation nodes, and they are **not** part of this simulation
domain. `ao-sim-fabrication` coordinates industrial engineering and production
related details for the **rehearsal**, and it runs the kitchen. It **does not
receive production data from any machine**.

Production data from the real machines is handled by the separate **`ao-fabrication`**
domain, which pulls it into its own database (`a_fab`) — see §3.3.0. This
separation is deliberate: a rehearsal that held production data, or a simulation that
commanded a live machine, would breach the §4.3 prohibition on simulation-to-live paths.

```text
Storage
   │
   ▼
Carousel or conveyor
   │
   ▼
Robot-arm pickup
   │
   ├── 3D printing (individual machine)
   ├── Additive manufacturing, laser powder bed fusion
   ├── CNC machining (individual machine)
   ├── Assembly — production data from each machine
   ├── Refrigerator or pantry
   └── Kitchen or pass-through
```

Phase one is simulation only. It must not command live robot arms, 3D printers,
CNC machines, laser powder bed fusion systems, refrigeration, carousels, kitchen
equipment, or other machinery.

LPBF systems, refrigeration, carousels, kitchen equipment, or other machinery.

Vehicle and fabrication simulation domains require separate:

- Podman networks.
- ROS domain IDs.
- Gazebo partitions.
- DDS configuration.
- Service identities.
- Filesystem mounts.
- Result directories.
- Simulation **manifest-signing** certificates only. These sign exported
  artifacts; they must not be Corda client identities, and simulation must never
  open a connection to Corda core (section 10.1).
- Git repositories or clearly separated repository subtrees.
- Artifact manifests.

Use local folder storage under /ALWAYSON, in the Gazebo subfolder (verify its exact
location with the operator), for SDF, URDF/Xacro, world files, robot definitions, safety zones,
task plans, and launch configurations. Use Git LFS or a separate artifact
repository for large meshes, textures, point clouds, and generated results.
### 10.2.1 Baseline capability: 3D world, boning, reinforcement learning objects, HTML portal

The same four deliverables as §10.1.2, tracked as §19.1 SIM-05 (ST-08). What differs is
what the world contains.

**3D world setup.** The fabrication world covers the robot-arm cells, the vehicle and
shelving layout, and the kitchen and storage volumes shown in Figures 10.2a–10.2c, with
safety zones and the printer/CNC and storage footprints.

**Boning.** This is where boning carries the most weight in this domain, because the
modelled cells and machines must line up with the real ones. The world carries a datum
frame per cell, declared mounting and reference surfaces for the robot arms and for the
printer and CNC beds, the shelving and aisle reference planes, and the joint and axis
definitions with their tolerances. This is what lets a simulated reach be checked against
the real machine envelope rather than assumed, and it is exported with the world so the
same check runs against recorded evidence.

**Reinforcement learning objects.** Marked parts, stock items and task targets for cell and
kitchen work. Robot arms and shuttles are the controlled actors; these objects are what they
act on and what reward is measured against.

**HTML portal.** A browser-served portal showing live robot, machine and stock state, the
boning and tolerance measurements, and the world. Reachable only on the approved local path
at `ROS_DOMAIN_ID=22` / `GZ_PARTITION=alwayson_fabrication_sim`, and never a control path to
the real machines (§10.2).

**3D viewer and camera set.** The world carries eight static cameras, all aimed from the
cell datums in `GAZEBO/sim/boning.yaml` so that every view is derived from boned data
rather than eyeballed, with standoff `d = (across-frame width / 2) / tan(h_fov / 2)`. The
across-frame width is the axis perpendicular to the view direction, not the extent named
in the boning datum. Four vantages look into the robot-arm cell — `arms_ne`, `arms_n`,
`arms_e`, `arms_se`, all at 1.9 m and 22° — and three are true elevations at pitch
exactly `0.0000`: `elev_arms` from the north, `elev_conveyor` from the south, and
`elev_massing` from the east, each level with its subject and face-on to one side. The
remaining `image` view is the default perspective set in both `factory.world` and the GUI
`gui.config`, so it applies whenever the world opens. Each feed is bridged gz→ROS and
served read-only.

The Foxglove bridge is a container, and the browser client that consumes it is
`GAZEBO/portal/viewer/index.html`, served by the portal at `/viewer`. It decodes the
bridge's CDR binary frames, draws the selected feed, and lets the operator resize the 3D
view. Two properties are load-bearing and worth recording. The bridge container must be on
both `ao-html-window` and `ao-sim-fabrication`: a matching `GZ_PARTITION` does not route
between two internal bridges, and gz-transport discovery is link-local multicast. And the
server must set `GZ_IP=0.0.0.0`; the GUI appears to work without it only because it shares
the server's network namespace.

**Files.** The baseline deliverables live under `GAZEBO/sim/` and are read by the portal:

| File | Contents |
|---|---|
| `boning.yaml` | A datum frame per cell, mounting and reference surfaces, joints and axes with tolerances, and the machine beds and storage planes |
| `objects.yaml` | Reinforcement learning objects in groups, plus actors, each with a stable id, a home pose, and reset semantics |

Every boning frame is derived from the AABB of the corresponding collision box in
`factory.world` and is labelled `source: derived-from-mesh-aabb`. A machine absent from the
source exports carries a `declared-by-operator` null, and the portal then reports
`reach_verified_against_machine: false`. **A simulated reach may not be called verified
against a real machine envelope until that machine has been surveyed.**

The portal is `scripts/simulation/ao-sim-portal.py` and exposes `/api/status`,
`/api/{start,stop,reset,inspect}`, `/api/boning`, `/api/objects` and `/api/health`, restricted
to a single permitted unit.

**Platform.** ROS 2 Lyrical at `/opt/ros/lyrical` and Gazebo Sim 10.5.0 (collection "Jetty") on
Ubuntu 26.04. This is the vendor-supported pairing, not a locally chosen mix: Gazebo Sim 10.5.0
is the ceiling of what the vendor publishes for this platform, and upstream lists ROS 2 Lyrical
(LTS) + Gazebo Jetty (LTS) as the recommended combination for 26.04. Gazebo Classic 11 is
end-of-life and is not a target here; the modern integration is `ros_gz`, not `gazebo_ros_pkgs`.
Simulation images are built from a pinned base-image digest rather than from an apt repository.

**Three environment traps.**

1. `GZ_RENDERING_RESOURCE_PATH` **replaces** Gazebo's packaged Ogre2 media root; it is not a
   search list, and a colon-separated value is treated as one directory name. Point it at the
   stock media root `/usr/share/gz/gz-rendering`. Project models are found through
   `GZ_SIM_RESOURCE_PATH` / `GZ_SIM_SYSTEM_PLUGIN_PATH`. Getting this wrong raises
   `OGRE EXCEPTION(6:FileNotFoundException)` and leaves the render engine uninitialised, so the
   viewport shows background colour and no geometry.
2. gz-gui's EntityTree icons require `qt6-svg-plugins`. Without it the image-format plugin
   fails to decode and the client aborts with
   `basic_string: construction from null is not valid`.
3. GPU rendering requires CDI passthrough (`nvidia.com/gpu=0` plus `/dev/dri`) with the EGL
   vendor pinned via `__EGL_VENDOR_LIBRARY_FILENAMES`. Without the pin, Mesa's dri2 platform
   claims the NVIDIA render node, logs `egl: failed to create dri2 screen` and never defers to
   the NVIDIA vendor. Software fallback is refused: `LIBGL_ALWAYS_SOFTWARE` is rejected once a
   hardware device is selected, and `QT_QUICK_BACKEND=software` renders the Qt interface but
   segfaults in `QOpenGLContext::done` before the 3D scene.

gz-transport discovery does not cross Podman's per-container bridge, so a GUI client sharing a
server must share its network namespace. A GUI client is selected by overriding `ENTRYPOINT` in
the Quadlet unit, not by maintaining a second GUI image.

### 10.3 Verified state, 2026-10-03 (SIM session)

Everything below was measured on this host on 2026-10-03, not inferred from the repository. Two
items in §19.1 were described as absent at the time §19 was compiled and are in fact present and
running; that correction is the reason this subsection exists.

**Delivered and verified live.**

| Item | What was measured |
|---|---|
| 3D world and cameras | `ao-sim-fabrication-gz.service` `ActiveState=active`, `NRestarts=0`, up 31 min. Portal `/api/status` reports `link_count 37`. All eight camera topics present on `ros2 topic list`. |
| Camera frames | `/factory/camera/elev_arms` `average rate: 1.972`, min 0.507 s max 0.507 s. The world's declared rate is 10 Hz; **the bridge delivers ~2 Hz, not 10 Hz.** This is a measured discrepancy, recorded rather than explained. |
| RL objects as world entities | `/api/status` link list contains `part_a1..a3`, `stock_s1..s3`, `target_bin_a`, `target_bin_b`, `target_shelf` — nine live links inside a non-static `rl_objects` model, not a YAML-only catalogue. |
| Safety zones | `/api/safety-zones` returns four resolved zones with computed min/max boxes, and `verify_safety_zones.py` exits 0 printing `4 zones, 2 unresolved dependencies`. |
| Interlocks | Three interlocks declared, every one `enforced_in_simulation: false`. The model **reports**; it actuates nothing, and the printed line `No interlock is enforced in the simulation; they report only.` is the honest boundary. |
| GUI image | `localhost/gz-sim10-resolute:gui-svgfix` carries `qt6-svg-plugins 6.10.2-2` and `/usr/share/gz/gz-rendering` holds `media/ ogre/ ogre2/` — both SIM-06 preconditions satisfied in the image. |
| ROS 2 apt | `openssl s_client -connect packages.ros.org:443` returns `subject=... CN=*.osuosl.org` with `verify return:1`, and `curl` returns HTTP `000`. SIM-07 reproduced exactly as §19 describes. |

**Two defects found, neither of them in §19.**

1. **`build-rl-objects.py --check` reports STALE against the committed world, and `--write`
   relocates the model.** `--check` exits 1 on the committed `factory.world`. The cause is not
   data drift: the committed block carries `<specular>` and `<shininess>` on every material,
   added by commit `fa3f8f6` ("material shininess") and never taught to the generator, while
   `render()` emits bare ambient/diffuse. Nine material lines differ. Worse, `--write` strips the
   existing block and re-appends before `</world>`, so the block moves from line 623 to the end
   of the world, **after** `safety_zones` and `conveyor_loops`. Regeneration is therefore not
   idempotent in *position* even once the material drift is settled. Demonstrated on a copy under
   `/tmp/gen-test`, never on the live tree. Running `--write` against `/ALWAYSON` rewrites the
   world in place and reorders three generated models; it is not a safe routine refresh.
2. **The signed manifest no longer describes the world, and the gap is larger than §19 records.**
   §19 says the manifest records 5371 bytes against a world of "~18 KB". Measured now:
   manifest `content_size_bytes` 5371 and `content_hash_sha256` `64eacbbf…`; the actual file is
   **63205 bytes** with sha256 `bce32f2a…`. Both the size *and* the hash disagree. The manifest
   cannot be repaired by editing a number — it must be re-exported and re-signed with the
   `ao-sim-fabrication` key.

**Corrections to §19 items on the strength of the above.**

- **SIM-13 and SIM-14 were recorded as absent; both are delivered.** The §19 text "nothing in the
  repo implements one" and "That model does not exist" are both false as of these measurements.
  Neither was ever a §19.2-tracked item, which is plausibly why they went stale: they were
  delivered by ordinary commits without a matching §19 row to close.
- **SIM-09 is closed by commit `365bd42`, not outstanding.** The arms datum was corrected to the
  measured as-built centroid and every arm camera re-aimed at it. `cell-arms` now reads
  `origin [5.981314, 1.861669, 0.531531]` with `extent [0.84, 1.672391, 1.238532]`, whose midpoint
  is the centroid `(6.4013, 2.6979, 1.1508)`, and the world comment records that every camera
  sits outside the massing envelope. `elev_arms` is at `6.401 4.056 1.151 0 0.0000 -1.5708`.
  **Superseded in part, 2026-10-04 — see "SIM-09 re-opened and properly closed" below.** The
  arithmetic above was right, but §19 asks for two further things and neither was then true:
  `boning.yaml` stated no `centroid:` at all, and the camera pose was a hand-written literal
  that no code derived from the datum. Both are now done.
- **SIM-06 is partly satisfied and partly untested.** The image carries the SVG plugin and the
  media root is correct, but the GUI unit is `UnitFileState=generated` with no `[Install]`
  section, so it cannot autostart; `ActiveState=inactive`, `NRestarts=0`. A restart count of zero
  on a unit that has never run is not evidence that rendering works. **The GUI has not been
  started in this session and its render path remains unverified.**

**Still absent, confirmed.** No facility scheduler exists: a case-insensitive search for
`scheduler` across `GAZEBO/`, `scripts/simulation/` and `quadlet/` returns only an unrelated
comment in `quadlet/sales/ao-mastodon-sidekiq.container`. SIM-12 stands.

**Operator decision outstanding.** SIM-02 — the `/ALWAYSON` Gazebo subfolder path. The repository
uses `GAZEBO/` (present, `12M` of meshes) and every path reference in the world, the boning
file, the portal and the Quadlet units agrees on `/ALWAYSON/GAZEBO`. The implementation is
therefore self-consistent, but §10.2 still says "verify its exact location with the operator",
and this session cannot substitute for that confirmation.

### 10.4 Verified state, 2026-10-04 (SIM session)

Measured on this host on 2026-10-04. One item is closed with commands and output, one defect is
fixed, one false claim is corrected, and one item is prepared and stopped at a stop condition.

**SIM-06 is now established, not inferred.** §10.3 recorded the GUI as untested, with the
correct warning that `NRestarts=0` on a unit that never ran proves nothing. The GUI has now
actually been started and watched:

- `systemctl --user start ao-sim-fabrication-gui-gz.service` → `ActiveState=active`,
  `SubState=running`, `NRestarts=0`, `ExecMainStatus=0`.
- 18 plugins load, including `EntityTree` (the SVG-icon-dependent one) and
  `gz-rendering-ogre2`. A case-insensitive journal grep for `OGRE EXCEPTION`,
  `construction from null`, `Segmentation`, `Failed to load` and `cannot open` returns **0**.
- The window exists and is placed by the KWin script: `xwininfo -root -children` shows
  `"Gazebo Sim": ("gz-sim-gui" "Gazebo GUI") 480x292+24+1502` — bottom-left of DP-3, per
  `~/.local/share/kwin/scripts/ao-gazebo-monitor/`.
- **Positive proof of geometry, not just a live process.** A window capture
  (`import -window 0x120001a`) shows rendered factory geometry on the ground plane, the
  left-hand toolbar icons decoded (so the SVG plugin works, not merely installs), and the sim
  clock advancing at `20.00%`. A second capture 5 s later differs in **294 of 140160** pixels,
  so the view is live rather than a frozen first frame.
- The unit was **re-masked afterwards**, as §19 requires, so it cannot seize keyboard and
  pointer focus: `is-enabled` = `masked`, and `start` then fails with `Unit ... is masked.`

**Fixed: the reproducibility guard that was disarmed.** §10.3 defect 1 found
`build-rl-objects.py --check` exiting 1 against the committed world, so the one check whose
entire purpose is catching divergence could not distinguish real drift from a cosmetic hand
edit. The cause was that `<specular>`/`<shininess>` had been added to `factory.world` *inside
the generated block* and never taught to the generator. The generator now declares
`SPECULAR = (0.30, 0.30, 0.30, 1.0)` and `SHININESS = 24`, so:

- `--check` → `OK: rl_objects block matches objects.yaml`, exit 0;
- `--write` → `rl_objects block already current; nothing written`, with the world sha256
  unchanged either side (`bce32f2a…`), so the world was **not** rewritten;
- the guard is not merely green: a real catalogue drift (moving `part-a1`'s home pose) makes
  `--check` exit 1 with `STALE`, and restoring the file returns it to 0. `objects.yaml`
  sha256 confirmed unchanged afterwards.

**Corrected a false capability claim in the portal.** `/api/objects` served
`"resettable": true` copied verbatim from `objects.yaml`, indistinguishable from a verified
capability, while the portal exposes no reset endpoint and performs no reset — `/api/reset`
returns 404. A consumer could reasonably have read that as "I can reset these objects". The
field is now `resettable_claimed` beside an explicit `reset_available: false` and a
`reset_note` naming the discrepancy, and the HTML portal (its only consumer) was updated to
match so it does not render `undefined`. Verified live on the restarted portal, and
`node --check` on the extracted script reports `PORTAL JS SYNTAX OK`. This corrects a claim;
it does **not** deliver reset, so SIM-14 stays open on that limb.

**SIM-11 is prepared and deliberately NOT executed.** Measured: the manifest records
`content_size_bytes` 5371 and `content_hash_sha256` `64eacbbf…`, while `factory.world` is
**63205 bytes** with sha256 `bce32f2a…`. Size *and* hash disagree, so the manifest cannot be
repaired by editing a number. Repair requires re-export and re-signing with the
`ao-sim-fabrication` producer key (present at `secrets/sim-fabrication/producer.pem`, 119 bytes,
value not printed) via `scripts/ledger/build-manifest.sh`. Re-signing a provenance record with a
ledger key is a stop condition for this session, so the change is prepared and left for the
operator. Cosmetic with respect to the running world, which is valid and serving.

**Unchanged from §10.3.** SIM-07 reproduces exactly: `packages.ros.org` presents
`subject=… CN=*.osuosl.org` and `curl` returns HTTP `000`. Certificate verification must not be
disabled to work around it. SIM-12 (facility scheduler) remains absent. SIM-02 remains an
operator decision. SIM-08 is a publishing decision and was not touched — no public port, route
or Cloudflare config was modified. SIM-03 (QGroundControl) is not installed on this host and
no install was attempted.

### 10.5 SIM-09 re-opened and properly closed, and a cross-session hazard

Measured 2026-10-04 in worktree `/tmp/ao-sessions/wt-sim` (branch `ai-sim`, base `1332005`).

#### SIM-09 is now closed against the actual acceptance criteria

§19 requires the centroid to be *added to the boning data* and the pose *recomputed from it*.
Commit `365bd42` satisfied neither: `boning.yaml` had no `centroid:` field, and the pose was a
literal in `factory.world` — the only file in `GAZEBO/`, `scripts/` or `quadlet/` mentioning
`camera_elev_arms`. So the two could silently disagree again, which is the recurrence the
item exists to prevent. Both are now done:

- `centroid:` added to all three cell datums, each equal to `origin+extent/2`.
- New `scripts/simulation/build-boning-cameras.py` derives each elevation pose from a new
  `elevation_cameras:` block in `boning.yaml` (`centroid_offset` + `yaw`).

The generated poses are byte-identical to the hand-written ones — correct, since §19 records
the three standoffs as already sound. This removes the manual re-aiming step and changes no
rendered view. A semantic XML comparison of the three `<model>` elements, HEAD vs now, is
identical after whitespace normalisation.

Guards, each proved by making it fail: standoff drift → `--check` exits 1; a stated centroid
disagreeing with `origin+extent/2` → refuses to generate; an XML comment containing `--` →
refuses. **The last one I hit for real** — my first generated block contained the literal
`--write` in a comment, and XML comments may not contain `--`, so the world stopped parsing.

    $ python3 scripts/simulation/build-rl-objects.py --check     -> OK (exit 0)
    $ python3 scripts/simulation/build-boning-cameras.py --check  -> OK (exit 0)
    $ gz sdf -k GAZEBO/worlds/factory.world                      -> Valid.

#### Hazard: `--write` from any worktree was rewriting the LIVE world

`build-rl-objects.py` hardcoded `OBJECTS`/`WORLD` to `/ALWAYSON/...`. With one git worktree
per session, running `--write` from a worktree rewrote the live `/ALWAYSON` world instead of
the checkout in front of you, and `--check` reported on a file the caller was not editing.

Ten of the eleven worktrees still hold that defective copy, **and** they predate main's
`SPECULAR`/`SHININESS` fix (`a05f018`), so `--write` from one of them strips every
`<specular>` from the live world. This fired during this session: `/ALWAYSON`'s world was
rewritten at 13:12:01 and its `rl_objects` specular count fell from **9 to 0**.

Restored and verified — `/ALWAYSON/GAZEBO/worlds/factory.world` is byte-identical to its
committed state, `bce32f2a…`, 63205 bytes, 9 specular, `--check` OK, `gz sdf -k` Valid:

    $ git -C /ALWAYSON status --short -- GAZEBO/worlds/factory.world   -> empty
    $ sha256sum /ALWAYSON/GAZEBO/worlds/factory.world
      bce32f2a7ff035b4022db82d9a90267ca829261d08038d3e26e5ff3fe5f51053

**Nobody should run `build-rl-objects.py --write` from a worktree until this is fixed
everywhere.** The remaining copies are in other sessions' trees; correcting them needs either
each session fixing its own, or the operator's explicit approval for me to touch them.

### 10.6 SIM-14 is not closed, and a third generator defect (SIM-15)

Re-audited 2026-10-04 against §19's actual acceptance text rather than against my own earlier
verdicts. Two of my own conclusions were wrong.

**SIM-14 stays Open. §19 asks for objects "addressable and resettable"; only addressable is
delivered.** The `rl_objects` model does exist and §19.1's "That model does not exist" is
retracted — but `/api/reset` returns **404** and the portal performs no reset, so placement
cannot be returned to `home_pose` at run time. The portal field I corrected in §10.4 is what made
this visible: `resettable_claimed` true beside `reset_available` **false**. I filed `close` on
2026-10-03 while my own section file said the opposite.

    $ curl -s -o /dev/null -w '%{http_code}\n' -m 5 http://127.0.0.1:8765/api/reset   -> 404
    $ curl -s -m 5 .../api/status | python3 -c '...'
      link_count: 37
      rl links: 9 ['part_a1','part_a2','part_a3','stock_s1','stock_s2','stock_s3',
                   'target_bin_a','target_bin_b','target_shelf']

**SIM-13's close stands**, re-checked: 4 zones resolve, 3 interlocks are declared and all carry
`enforced_in_simulation: false`, and the 4 zones are live links in the served world. The model
exists and is honest that it actuates nothing. `printer-01` and `cnc-01` remain `[GAP]` and need
operator-supplied datums.

**SIM-15, new: `--write` is not position-idempotent.** A *correct* regeneration strips the
`rl_objects` block and re-appends it before `</world>`, silently reordering three generated
models in the world the live server has open. Measured on `/tmp/gen-test-sim`, never the live tree:

    $ python3 scripts/simulation/build-rl-objects.py --write   -> "already current; nothing written"
    # make a real catalogue change (part-a1 home_pose 6.20 -> 6.90), then rewrite:
    $ python3 scripts/simulation/build-rl-objects.py --check   -> STALE (exit 1)
    $ python3 scripts/simulation/build-rl-objects.py --write   -> wrote 3 groups / 9 objects
    #   rl_objects           547 -> 1289
    #   safety_zones         695 ->  548
    #   camera_elev_massing 1410 -> 1263
    $ gz sdf -k ...                        -> Valid.
    $ grep -c '<link name=' ...            -> 37 (unchanged; nothing lost)

No content is lost and the world stays valid, so this is a review-integrity hazard rather than a
runtime fault — which is why it survived so long unnoticed. It should replace the block in place.

**A structural defect in this very subsection, found while auditing my own prose.** §10.5's
heading had been inserted *mid-sentence*, splitting the SIM-07 paragraph and orphaning its tail
("disabled to work around it. SIM-12 …") at the far end of §10.5, where it read as part of the
generator hazard. Repaired. Worth noting for other sessions: a heading inserted into a section
file produces no error anywhere — the compiler concatenates happily — so prose damage from a bad
edit is only visible by reading the rendered README.

**What I got wrong this session.** I first reported the GUI as verified on the strength of
`ActiveState=active` plus a clean error grep. That is the exact mistake §10.3 warned about: a
live process and an absence of errors is not proof that geometry renders. I only reached a real
answer by capturing the window and diffing two captures. Smaller error: I ran `gz topic` inside
the GUI container before checking `GZ_CONFIG_PATH`, and briefly read "cannot find any available
'gz' command" as a missing toolchain when it was only an unset variable.

**The recurring error, stated once so it is not repeated: I re-ran my own old commands without
re-deriving their assumptions, and briefly believed the wrong answer.** `/api/status` now returns
`links` and `link_count` *nested* under `world`. My 2026-10-03 one-liner reads them at top level,
so it now returns `[]` and `None`. I ran it unchanged, saw zero RL links, and for a moment
concluded the model had vanished — when the model was fine and my query was stale. A measurement
whose inputs may have drifted needs re-derivation, not just re-execution. I made the same class of
error twice: verifying the arithmetic of SIM-09 last session and treating that as equivalent to
having read the acceptance criteria, then verifying the existence of `rl_objects` for SIM-14 and
treating that as equivalent to having met the criteria.

### 10.7 SIM-15 fixed: the generator is position-idempotent, and `--check` now proves it

Fixed 2026-10-04 in worktree `/tmp/ao-sessions/wt-sim`. `build-rl-objects.py --write` now replaces
the generated block at its canonical position instead of stripping it and re-appending it before
`</world>`. The canonical position is defined structurally, not by line number: immediately before
the `safety_zones` region, one of four generated regions the world carries in a fixed order
(`rl_objects`, `safety_zones`, `conveyor_loops`, `elevation cameras`).

A real catalogue edit now touches only the block. Before, the same edit reordered three models:

| | before | after |
|---|---|---|
| `rl_objects` | 547 → 1289 | 543 → 543 |
| `safety_zones` | 695 → 548 | 691 → 691 |
| `camera_elev_massing` | 1410 → 1263 | 1356 → 1356 |
| diff vs committed | whole-file reorder | 4 lines (552, 582) |

**`--check` also detects a reorder now, which it never did.** Content equality cannot see position,
and that is the whole defect. Verified by making it fail on a world reordered exactly the old way:

    $ python3 scripts/simulation/build-rl-objects.py --check
    MISPLACED: rl_objects block is followed by nothing, expected safety_zones.
    A reorder, not a content change. Repair with --write        (exit 1)

    $ python3 scripts/simulation/build-rl-objects.py --write
    wrote 3 groups / 9 objects (relocated before safety_zones)

Repair is exact — healing a reordered world reproduces the committed file byte for byte, which is
the property that makes the fix trustworthy:

    $ sha256sum /tmp/t5/GAZEBO/worlds/factory.world
      5667873ca41968bea3e41b68dbc03321a22e8553059271ec65b522a0657e7b26
    $ cmp GAZEBO/worlds/factory.world /ALWAYSON/... (committed)
      BYTE-IDENTICAL TO COMMITTED
    $ gz sdf -k GAZEBO/worlds/factory.world        -> Valid.
    $ grep -c '<link name=' ...                    -> 37   (unchanged)

Idempotency, staleness and the sibling generators, all on a scratch copy at `/tmp/t5`:

    $ python3 scripts/simulation/build-rl-objects.py --check   -> OK, exit 0
    $ python3 scripts/simulation/build-rl-objects.py --write   -> "already current; nothing written"
    $ sha256sum before/after second --write                    -> identical
    $ python3 scripts/simulation/build-boning-cameras.py --check -> OK, exit 0
    $ python3 scripts/simulation/verify_safety_zones.py         -> exit 0

The **live** tree was never a target: `/ALWAYSON/GAZEBO/worlds/factory.world` is still
`5667873ca41968bea3e41b68dbc03321a22e8553059271ec65b522a0657e7b26` and `git -C /ALWAYSON status`
is empty for both the world and the script. Every measurement above was taken on a scratch copy.

**What I got wrong here, and it took three attempts.** My first guard asserted "a rewrite would be
a no-op", which is worthless: replacing in place is a *fixed point* of relocation, so a world whose
block had been moved to the end still reported OK. I only found this because I tested the guard
against a deliberately broken world instead of assuming it worked — a passing test on the good world
proves nothing about a check whose job is to catch the bad one. My first relocate implementation
then computed the anchor offset on the unmodified string and applied it to the already-shortened
one, splitting a comment into `<` and `!--` and producing a file Gazebo could not read
(`Error Code 1: Unable to read file`); the second attempt's blanket `\n{3,}` collapse then ate
blank lines across the whole document. The file was byte-compared against the committed world after
every attempt, which is the only reason those showed up at all. Three errors, one class: I wrote
the seam handling from intuition instead of measuring the committed file's actual spacing, and I
validated on the happy path instead of on the broken case.

### 10.8 Second pass: the SIM-15 fix re-verified from scratch, and a wrong number in SIM-10

Recorded 2026-10-04 in worktree `/tmp/ao-sessions/wt-sim`. §10.7 was written by the previous
wave of this session and its fix was **uncommitted**. I re-derived every claim on a fresh
scratch copy at `/tmp/verify15` rather than trusting the recorded output, because a handoff that
says "verified" is a claim, not evidence.

**SIM-15 confirmed on all three limbs, reproduced from scratch.** I reconstructed the original
defect deliberately — moved the `rl_objects` block to just before `</world>`, exactly as the old
`--write` did — and confirmed the region order inverted (`safety_zones` 544, `conveyor_loops`
574, `elevation cameras` 1209, `rl_objects` 1285).

1. `--check` **catches** the reorder, which is the half the old guard could never do:

        MISPLACED: rl_objects block is followed by nothing, expected safety_zones.
        A reorder, not a content change. Repair with --write        (exit 1)

2. `--write` **heals it byte for byte** — the property that makes the fix trustworthy:

        wrote 3 groups / 9 objects (relocated before safety_zones)
        5667873ca41968bea3e41b68dbc03321a22e8553059271ec65b522a0657e7b26
        BYTE-IDENTICAL TO COMMITTED

3. A real catalogue edit (`part-a1` home_pose 6.20 → 6.90) is now `replaced in place`, a
   **4-line** diff confined to the two pose lines, with `gz sdf -k` → `Valid.` and
   `grep -c '<link name='` → `37` unchanged. Restoring the catalogue and re-writing returns
   the world to the same sha256.

The live tree was never a target and is provably untouched: `git -C /ALWAYSON status --short --
GAZEBO/worlds/factory.world scripts/simulation/` is empty and `/ALWAYSON`'s world is still
`5667873c…`. Both sibling generators are green in the real worktree
(`build-boning-cameras.py --check` → OK, `verify_safety_zones.py` → exit 0).

**The keep-open findings all still reproduce today**, re-measured rather than assumed:

| item | re-measured |
|---|---|
| SIM-07 | `packages.ros.org` still presents `CN=*.osuosl.org`; `curl` still `http=000` |
| SIM-10 | 34 parts, 33 exact cubes; still no `door`/`wall`/`floor` name |
| SIM-12 | only hit for "scheduler" repo-wide is an unrelated sidekiq comment |
| SIM-01 | `quadlet/sim-vehicle/` holds one file, `ao-ardupilot-sitl.container`; no vehicle GUI unit |
| SIM-03 | no `QGroundControl` on PATH or under `/opt` |
| SIM-14 | `/api/reset` still **404**, `/api/status` 200, `link_count` 37, all 9 RL links live |

**A wrong number in SIM-10, inherited from §19 and then propagated by me.** §19 describes the
parts of `massing_fab.dae` as "anonymous `group_0`–`group_25`". Counted, there are **13**,
`group_0`–`group_12`, in both `massing_fab.dae` and `massing_flat.dae` (the file the world
actually renders). The conclusion is unaffected — no semantic name anywhere and 33 of 34 parts
cubic, both verified directly — but the count is wrong and the compiler should correct it.

**What I got wrong this wave.** I wrote a catalogue-edit test whose `sed` pattern did not
match the file, so the run reported "already current; nothing written" and I nearly recorded a
passing test that had changed nothing. `x: 6.20` is not in `objects.yaml`; the line is
`home_pose: [6.20, 2.10, ...]`. The tell was that the diff was empty *and* `--check` said OK
after I had supposedly edited the catalogue — two results that cannot both be true. The
underlying habit is the one already recorded twice in this section: I accepted a verification's
verdict instead of confirming the verification had actually been set up. The corrected run,
shown above, edits line 34 and confirms the edit took effect with `sed -n '34p'` before
trusting the generator's output.

---
