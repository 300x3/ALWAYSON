# Gazebo Sim 10 GUI: the abort is Collada `<lines>` in the VISUAL mesh, and the window is on the wrong monitor because KWin matches `resourceName`, not `resourceClass`

**From:** Cline session, Gazebo GUI (continues document C)
**Scope:** `/ALWAYSON/GAZEBO` visual mesh assets, `scripts/simulation/`, and one KWin script under the operator's home config
**State:** **NOT committed**, nothing staged. The crash is **FIXED and VERIFIED**. Placement is **WORKING but NOT PERSISTENT** (see Open 1).

---

## Read this first

1. **Document C is superseded on root cause.** C concluded the offending asset was
   "not yet conclusively identified" and that the fault was reached on a
   collision-ish path. Both are now settled: the fault is in the **visual**
   path, and the cause is the SketchUp `<lines>` elements in **all four**
   exports, not one mystery file.
2. **`compute-mesh-aabb.py`'s docstring was wrong about scope and I corrected it.**
   It said the abort was a collision-loading problem. It is not — a primitive
   collision proxy cannot fix it, because the throw is in the visual mesh. If
   you read that file first, you will draw the wrong conclusion.
3. **A kwinrc `[Window Rules]` `geometry=` entry does not work on KWin 6.6.6.**
   It is accepted silently (reconfigure returns 0, nothing in the journal) and
   does nothing. Do not spend time on it.
4. **The KWin window's `resourceClass` is `Gazebo GUI`, not `gz-sim-gui`.**
   `resourceName` is `gz-sim-gui`. Any matching logic keyed on the class
   silently matches nothing and looks like a no-op bug.
5. `workspace.windowScreenChanged` and `workspace.outputs()` **do not exist** in

---

   KWin 6.6.6. Use `windowAdded` and `workspace.screens`.

---

## What was wrong, and what I changed

### The abort

```
terminate called after throwing an instance of 'std::logic_error'
  what():  basic_string: construction from null is not valid
```

Path (GDB, with `LD_LIBRARY_PATH` cleared for the inferior):

```
gz::sim::v10::RenderUtil::Update()
  -> SceneManager::CreateVisual()          <-- VISUAL path, not collision
  -> SceneManager::LoadGeometry()
  -> gz::sim::v10::loadMesh()
  -> gz::common::MeshManager::Load()
  -> gz::common::ColladaLoader::Load()
  -> ColladaLoader::Implementation::LoadGeometry()   <-- throws
```

The throw is inside a Qt event handler, so the GUI cannot catch it. C's
observation that the abort lands ~1s after "Camera pose topic advertised" is
consistent and explained: that is the first rendered frame.

### The fix

New tool: `scripts/simulation/strip-collada-lines.py` (uncommitted).

| export | `<lines>` blocks removed | bytes |
|---|---|---|
| 09-SIMULATIONARMS.dae | 36 | -6,248 |
| 09-SIMULATIONCONVEYOR.dae | 220 | -59,407 |
| 09-SIMULATIONMASSING-ADUDOORS_FABRICATIONAREA.dae | 107 | -86,417 |
| 09-SIMULATIONVEHICLES-ARMS.dae | 610 | -244,203 |

Output written to `GAZEBO/models/factory_assets/meshes/*.dae`, **replacing four
symlinks**. Original SketchUp exports in `/ALWAYSON/GAZEBO` are untouched — the
tool refuses to edit in place by design.

Two side facts worth knowing:
- **RETRACTED — the `massing_fab.dae` symlink was NOT broken.** My earlier claim
  in this document was wrong. The target filename *legitimately begins with a
  literal newline* (`'\n09-SIMULATIONMASSING-ADUDOORS_FABRICATIONAREA.dae'`) and
  the symlink points at exactly that name, so `os.path.exists()` returns
  `True` and it resolves. My error: I inferred "broken" from the embedded
  newline without calling `exists()`. The newline filename is still a real
  hazard for any script using `glob('*.dae')`, but nothing was broken.
- All four now verify: 0 `<lines>`, `<triangles>` preserved (462/140/196/572),
  XML parses. The tool is idempotent (rerun removes 0 blocks) and refuses to
  write if no `<triangles>` survives.

### Superseding revision — 2026-10-01T23:00Z (SketchUp edges removed from ALL copies)

**Supersedes:** the "Original SketchUp exports are untouched" statement above.
On operator instruction, the strip was then applied to the source exports and
to the stale `worlds-run` copies as well. Every `.dae` in the tree is now clean.

- Backups first, hash-verified before any write:
  `/ALWAYSON/backups/sketchup-dae-edges-20261001T225802Z/` — 8 files
  (4 source exports + 4 under `worlds-run-meshes/`). Restorable.
- **973 `<lines>` blocks removed total, −397,275 bytes.** Triangle counts
  unchanged in all 8 files (196/462/572/140). Written via same-dir temp +
  `os.replace`; no `.tmp` residue; perms restored `0664`.
- Full-tree audit: **0 `<lines>` remain** anywhere under `GAZEBO/`; all 16
  `.dae` paths parse as well-formed XML; all 4 `worlds-run` symlinks resolve
  to clean targets.
- Re-verified against the production world headlessly
  (`gz-sim-server` v10.5.0, `factory.world -r -v 4`): 0 `logic_error` /
  `Aborted` / `terminate called` / `Failed to load` / `Unable to find`.
- **Trap for the next agent:** `worlds-run/models/meshes/` holds *real copies*,
  not symlinks, and they were byte-identical to the exports (backup sha256s
  match pairwise). Stripping only the symlinked path looks complete but is not.
- **Open:** SketchUp is not installed on this host, so this is post-processing
  only. The next re-export from the `.skp` originals reintroduces `<lines>`
  unless edges are disabled in the Collada export dialog. Needs the owner of
  the source models — **operator action, not agent action.**

### Verification against the production world

Against `partition=alwayson_fabrication_sim` (not a test world):

- GUI alive well past the ~1s abort point
- `grep -c 'logic_error|Aborted'` → **0**
- `grep -c 'Failed to load|Unable to find'` → **0**
- entity tree showed `ground_plane`, `factory`, `sun` — the real world
- screenshot `/tmp/ao-gz-placement.png` shows rendered factory geometry

### Monitor placement

Main monitor measured: **DP-3**, priority 1, `0,738 1920x1080`.
DP-1 is portrait, `1920,0 1080x1920`. Confirmed by both `xrandr --listmonitors`
and `qdbus6 org.kde.KWin /KWin org.kde.KWin.supportInformation`.

Three attempts failed before one worked — details in the journal, but the
load-bearing one is the property mismatch:

- kwinrc `geometry=` rule → accepted, no effect. Removed.
- KWin script on `windowScreenChanged` / `outputs()` → both undefined. Fixed to
  `windowAdded` / `workspace.screens`.
- Script matching `client.resourceClass === "gz-sim-gui"` → matched nothing;
  live value is `Gazebo GUI`. Now matches `client.resourceName`.

Working script: `~/.local/share/kwin/scripts/ao-gazebo-monitor/`
(`contents.js` + `metadata.json`, needs `"KPackageStructure": "KWin/Script"`).

Evidence, cold start:
```
js: ao-gazebo-monitor: placed gz-sim-gui on DP-3 1920x1080+0+738
xwininfo: "Gazebo Sim" 1920x1052+0+766      (was 1200x1000+1800+474)
```
`+766` vs `+738` and `1052` vs `1080` are the window frame/title bar.

---

## Open findings

1. **The placement script is runtime-loaded and will not survive a KWin
   restart.** `qdbus6 ... /Scripting loadScript` is not persistent. It needs a
   real autostart wiring (KWin script autostart dir or a user unit).
   **Needs operator approval** — it touches desktop session startup, and I did
   not want to add a startup unit unasked. Recommend this as the next step.
2. **`ao-sim-fabrication-gui-gz.service` is still MASKED.** I left it exactly as
   found. The crash that justified masking is now fixed, so the reason for the
   mask is gone. Unmasking is an operator decision, not mine.
3. **The symlink→regular-file change in `models/factory_assets/meshes/` is a
   structural change** to how those assets are served. If the project wants the
   SketchUp exports to stay canonical, the right long-term shape is a build
   step that regenerates the sanitised meshes, not hand-maintained copies.
   Worth an operator decision on which is intended.
4. **Root cause upstream is unaddressed.** The SketchUp exports still carry the
   `<lines>` blocks; we sanitise on consumption. A re-export without edge
   geometry would remove the need for the tool entirely.

# Gazebo Sim 10 GUI: the abort is Collada `<lines>` in the VISUAL mesh, and the window is on the wrong monitor because KWin matches `resourceName`, not `resourceClass`

**From:** Cline session, Gazebo GUI (continues document C)

---

---

## Traps

- **An isolated mesh test proves nothing if the mount is missing.** My first
  comparison run mounted the server's `/t` but not the GUI's, so every mesh was
  "unable to find file" and the GUI did not abort — which looked like success.
  The GUI reported no throw only because it had nothing to load. Always confirm
  the GUI container can see the test assets, and check the
  `Failed to load mesh` count, not just the absence of a crash.
- **Headless `gz sim -s` does not load visuals**, so it cannot reproduce or
  disprove a visual-mesh fault. `-s` is a useless control for this bug.
- **A container that has exited is not a passing test.** One run failed with
  `cannot execute binary file` purely because I overrode `--entrypoint
  /bin/bash` and made the client binary a bash argument. Always check the log
  for *why* the container ended before treating "no crash" as success.
- KWin scripts fail **loudly and specifically** — read
  `journalctl --user | grep kwin_scripting`; the messages name the exact line.
  Do not assume a silent rule is a working rule.
- `spectacle -b -n` can return an all-black PNG when the screen has blanked.
  A black screenshot is not proof of a black render; confirm with `xwininfo`
  and process liveness, which is what I relied on.

---

## Housekeeping (mine)

- `/tmp/ao-mesh-test/`, `/tmp/ao-strip-out/`, `/tmp/ao-gui-test.sh`,
  `/tmp/ao-probe*.js`, `/tmp/notamesh.dae`, `/tmp/out.dae`,
  `/tmp/ao-*-*.png`, `/tmp/ao-*.log` — all disposable, safe to delete.
- `/tmp/ao-gdb-libs` and `/tmp/ao-gdb/` — the sideloaded GDB used for the
  backtrace. Keep if a future session wants another coredump; otherwise remove.
- `/tmp/kwinrc.bak.152854` — backup of `~/.config/kwinrc`. **`kwinrc` is now
  byte-identical to it** (verified by `diff`); rule 99 is intact and untouched.
- All ad-hoc containers removed. `ao-sim-fabrication-gz.service` never stopped.

## Files

- New, uncommitted: `scripts/simulation/strip-collada-lines.py`
- Modified, uncommitted: `scripts/simulation/compute-mesh-aabb.py` (docstring scope correction only)
- Replaced symlinks: `GAZEBO/models/factory_assets/meshes/{arms,conveyor,massing_fab,vehicles_arms}.dae`
- New journal: `logs/operations/gazebo-gui-visual-mesh-and-monitor-placement-2026-10-01.log`
- Outside the repo: `~/.local/share/kwin/scripts/ao-gazebo-monitor/`

**Nothing staged or committed.** The working tree holds many modified files
belonging to other sessions (mastodon, wallet, grafana, kwallet); I did not
`git add` anything and did not touch those files.
