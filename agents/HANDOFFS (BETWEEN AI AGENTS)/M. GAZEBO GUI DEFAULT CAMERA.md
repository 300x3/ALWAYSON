# Gazebo Sim GUI default camera: gui.config is authoritative, the world file is inert

`From:` Cline session M, 2026-10-01
`Scope:` `ao-sim-fabrication-gz` (server), `ao-sim-fabrication-gui-gz` (GUI client), `/ALWAYSON/GAZEBO/worlds/factory.world`, `gui.config`
`State:` Camera persistence **VERIFIED through full cold boot**. Not committed. **OPEN:** GUI window geometry (needs operator approval); `/gui/camera/pose` telemetry unreliable.

Journal: `/ALWAYSON/logs/operations/gazebo-gui-default-camera-20261001.log`

## Read this first

1. **The world file cannot set the startup camera on this host.** The GUI runs
   as `gz-sim-gui-client`, which attaches to the running server and never
   parses `factory.world`. Its `<gui>` block is decorative here. If you have
   been editing `factory.world` to chase camera framing, that work has been
   inert — this is what I got wrong for most of this session.
2. **Document `L. GAZEBO CAMERA LOCATION.md` gives advice that cannot work
   here**, and its code samples are corrupted (`amera_pose`, missing the `c`).
   Details in the contradiction section below. I did not edit L.
3. **`gui.config` is authoritative AND is rewritten by the GUI on exit** from
   whatever the viewport currently shows. If the viewport is frozen when the
   GUI shuts down, a stale pose gets persisted over a good one. Verify the
   render *before* letting the GUI exit.
4. **The GUI window opens at 687x330, not the 1000x845 `gui.config` asks
   for.** A small screenshot capture is NOT evidence of a bad camera. I briefly
   concluded the pose had failed from a mis-captured image; check the window id
   before drawing conclusions.

## Symptom / evidence

Authoritative pose, `/home/scottw/.local/share/ao-simulation/gui-home/.gz/sim/10/gui.config` line 44, inside `<plugin filename="MinimalScene" name="3D View">`:

    <camera_pose>9.0 6.5 2.6 0 0.22476 -2.5045</camera_pose>

Format `x y z roll pitch yaw`, metres/radians. `gui.config` line 8-9 requests
`<width>1000</width><height>845</height>`; the window is actually 687x330 at
+582+1422.

Process identity — GUI is a client:

    $ podman exec ao-sim-fabrication-gui-gz ps aux | grep -oE "gz-sim-gui[a-z-]*"
    gz-sim-gui-client

The world's `<gui>` block has no `<plugin>` element at all:

    $ sed -n '69,74p' /ALWAYSON/GAZEBO/worlds/factory.world
        <gui>
          <camera name="user_camera">
            <pose>9.0 6.5 2.6 0 0.22476 -2.5045</pose>
          </camera>
        </gui>

That `<camera name="user_camera">` form is the **Gazebo Classic** idiom.

Verification, full cold boot with NO manual camera command:

    systemctl --user restart ao-sim-fabrication-gz.service
    systemctl --user start  ao-sim-fabrication-gui-gz.service
    # /gui/move_to/pose never called
    import -window 0x100001a png:/tmp/M_cold_full.png

Result: factory mesh renders in the close centred view. `gui.config` mtime
unchanged (18:44:03) across the restart.

## What was changed

- No tracked file was modified by this session's final work.
- Journal added: `/ALWAYSON/logs/operations/gazebo-gui-default-camera-20261001.log`
- Helper tools added earlier this session: `/ALWAYSON/scripts/simulation/gztools/`
- Nothing staged or committed — the working tree holds other sessions'
  uncommitted work.

## Contradiction with document L

I reviewed `L. GAZEBO CAMERA LOCATION.md` (18:55) as requested. It is an
unsourced LLM answer: it contains its own "AS A LANGUAGE MODEL" reply at
line 164 and admits no access to this instance at line 167. Findings:

1. Its central prescription — put `<camera_pose>` in a `<gui><plugin
   filename="MinimalScene" name="3D View">` block in the world SDF (lines
   15-20, 178-191) — cannot work here, because the GUI is a client and never
   reads the world file.
2. Every code sample is corrupted: `amera_pose>` instead of
   `<camera_pose>` (lines 19, 41, 106, 116, 117). Copy-pasting yields invalid
   SDF.
3. It never addresses a world whose `<gui>` block contains no `<plugin>` —
   ours has none.
4. Its live commands do not exist in these containers: `gz topic -e -t
   /gui/camera/pose` and `gz service -s /gui/move_to/pose` (lines 52, 61). The
   in-container `gz` CLI has no working transport plugin.

What L got right, and which is the actual answer: `gui.config` under
`~/.gz/sim/<major>/` is the persistent location (lines 335, 343), the field is
`x y z roll pitch yaw` in radians, and "Save client configuration" is the GUI
menu path to write it (line 328). L's line 402 — an explicit `--gui-config`
takes highest priority — is directionally correct about precedence and matches
what I measured.

## Open findings

1. **GUI window geometry is wrong and unfixable without approval.** Opens at
   687x330 at +582+1422 despite `gui.config` requesting 1000x845. Needs a
   window manager override or `xdotool`/`wmctrl`, neither of which is
   installed. Installing packages requires explicit operator approval.
2. **`/gui/camera/pose` telemetry does not match commanded positions.** It
   cannot be used as proof of camera placement; screenshot pixel comparison is
   the only method that has worked. Needs investigation, no fix attempted.
3. **`/gui/move_to/pose` can return OK while the viewport does not repaint.**
   A 0.9-radian yaw test produced zero differing pixels. A screenshot check
   after every move is mandatory until this is understood.

## Traps

- `import -window root` fails ("missing an image filename"). Use
  `import -window <id> png:/path.png`.
- `xdotool`, `wmctrl`, `kdotool` are all absent on the host.
- The `gz` CLI inside containers is a stub — use the compiled helpers in
  `/ALWAYSON/scripts/simulation/gztools/`.
- Unit names are `ao-sim-fabrication-gz` (server) and
  `ao-sim-fabrication-gui-gz` (GUI). Guessing `ao-sim-fabrication` for the
  server returns `inactive` and looks like an outage.
- Screenshot windows must be located with `xwininfo -root -children`, not
  assumed to be `0x100001a`.

## Housekeeping

- `/tmp/M_cold_full.png` (the valid one), `/tmp/M_live_now.png` (byte-identical
  except the zoom readout), `/tmp/M_coldboot.png`. Safe to delete.

## ADDENDUM 19:20 — ao-html-window network created

Operator requested a new network `ao-html-window`, clarified as a VIEW-ONLY
surface: displays 2D/3D HTML render, takes no input, no interaction.

Created:

    podman network create --internal --subnet 10.89.14.0/24 ao-html-window

Verified:

    $ podman network inspect ao-html-window --format '{{.Name}} internal={{.Internal}} subnet={{range .Subnets}}{{.Subnet}}{{end}}'
    ao-html-window internal=true driver=bridge subnet=10.89.14.0/24

Registered in `/ALWAYSON/config/platform/network-cidrs.yaml` as
`ao-html-window internal=true subnets=10.89.14.0/24` with a comment recording
why internal=true is correct for a read-only display.

Subnet choice: 10.89.14.0/24. 10.89.11.0/24 was also unallocated; 14 was taken
to match the "next after highest" convention (highest was 13). No host
interface holds any 10.89.x.x address, so no collision.

`/ALWAYSON/scripts/validation/check-network-isolation.sh` re-run after the
change:

    OK: all domain networks present; isolation domains internal-only;
    ao-sales + ao-reporting-egress non-internal by decision

Key design point — view-only resolves the earlier reachability objection.
The previous concern was that an internal network could never be reached by a
viewer. That is false for a LOOPBACK publish. Precedent measured:
`ao-mapping` is internal=true and `ao-webodm-web` publishes
`127.0.0.1:8000:8000` to the host browser. Reachability comes from the
loopback publish, not from network egress. internal=true therefore costs this
workload nothing and still prevents it routing off-host.

NOT DONE, needs operator approval (rule 4 — no public port without approval):
no container, no quadlet unit, no PublishPort chosen. 8080 is already taken by
domoticz; 8081/8088/8090/8099 measured free. Recommended 8081. Any such
publish MUST be `127.0.0.1:<port>:<port>` only, never `0.0.0.0`.