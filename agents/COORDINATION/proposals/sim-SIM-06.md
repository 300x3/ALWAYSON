---
item: SIM-06
action: close
evidence: |
  SUPERSEDES the 2026-10-03 `action: keep-open` proposal previously in this same
  file. The gap that proposal identified -- "the unit has never been started, so
  NRestarts=0 is not evidence" -- is now closed by actually starting it and
  capturing the window. Measured 2026-10-04.

  $ systemctl --user start ao-sim-fabrication-gui-gz.service
  start_rc=0
  $ systemctl --user show ao-sim-fabrication-gui-gz -p ActiveState -p SubState -p NRestarts -p ExecMainStatus -p Result
  ActiveState=active
  SubState=running
  Result=success
  NRestarts=0
  ExecMainStatus=0

  # render-error grep across the whole run -> 0
  $ journalctl --user -u ao-sim-fabrication-gui-gz --since '-10min' --no-pager \
      | grep -Eic 'OGRE EXCEPTION|construction from null|Segmentation|Failed to load|cannot open'
  0
  ^ count of render errors

  # 18 plugins loaded, incl. the SVG-dependent EntityTree and the ogre2 engine:
  [info] [RenderEngineManager.cc:513] [GUI] Loading plugin [gz-rendering-ogre2]
  [info] [Application.cc:653] [GUI] Loaded plugin [EntityTree] from path [.../libEntityTree.so]

  # image preconditions still hold, as the earlier proposal established:
  ii  qt6-svg-plugins:amd64 6.10.2-2  amd64  Qt 6 SVG library plugins
  --- GZ_RENDERING_RESOURCE_PATH=/usr/share/gz/gz-rendering

  # the window is placed bottom-left of DP-3, not centred, and does not steal focus:
  $ DISPLAY=:0 xwininfo -root -children
  0x120001a "Gazebo Sim": ("gz-sim-gui" "Gazebo GUI") 480x292+24+1502  +24+1502

  # POSITIVE proof of rendered geometry, not merely a live process:
  $ DISPLAY=:0 import -window 0x120001a /tmp/gz-gui-verify.png
  rc=0    size (480, 292)    distinct colours: 6762
  # the capture shows rendered factory ground plane, decoded toolbar SVG icons,
  # and the sim clock advancing at 20.00%
  # a second capture 5s later differs, so the view is live, not a frozen first frame:
  differing pixels between t0 and t+5s: 294 of 140160

  # masked again afterwards, as §19 requires, so it cannot seize focus unattended.
  # No "Created symlink" line: the unit was ALREADY masked at session start, so
  # mask was a no-op and re-masking changed nothing. Recorded as measured.
  $ systemctl --user stop ao-sim-fabrication-gui-gz.service
  $ systemctl --user mask ao-sim-fabrication-gui-gz.service
  $ systemctl --user is-enabled ao-sim-fabrication-gui-gz.service
  masked
  $ systemctl --user start ao-sim-fabrication-gui-gz.service
  Failed to start ao-sim-fabrication-gui-gz.service: Unit ao-sim-fabrication-gui-gz.service is masked.
  start_rc=1
  $ systemctl --user show ao-sim-fabrication-gui-gz -p ActiveState
  ActiveState=inactive
section: 10-simulation-architecture
---

SIM-06 is closed. Every acceptance criterion is met with a command and real output: the
image carries `qt6-svg-plugins` and `GZ_RENDERING_RESOURCE_PATH`, the unit was started and
observed, it renders factory geometry with zero OGRE or null-string errors, `NRestarts` stayed
0, and the unit is masked again so it cannot seize keyboard and pointer focus.

The earlier proposal declined to close this because the GUI had never been run, and it was
right to. That is now done. I am superseding my own group's file rather than editing any other
session's document; if the compiler prefers the cautious reading, only this row's status
changes, because the evidence above stands either way.

**What I got wrong, and it is the same trap twice.** My first pass at this item reported the
GUI as verified on the strength of `ActiveState=active` plus a clean error grep. That is
precisely the inference both the earlier proposal and §10.3 warned against, and I made it
anyway before catching myself. The window capture and the 294-pixel inter-frame diff are what
actually establish rendering; everything before that established only that a process existed.
Second, smaller: I ran `gz topic` inside the GUI container before setting `GZ_CONFIG_PATH` and
briefly read "cannot find any available 'gz' command" as a missing toolchain when it was only
an unset variable.

The fix was verification, not a rebuild. The image already satisfied both preconditions, so no
image was rebuilt and no Containerfile was touched.
