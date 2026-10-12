---
item: SIM-06
action: update
evidence: |
  Re-verified 2026-10-11 in worktree /tmp/ao-sessions/wt-sim. Image half holds;
  render half cannot be re-proven from this headless worktree session.
  $ grep -n 'qt6-svg-plugins' GAZEBO/containers/gz-sim/Containerfile.resolute GAZEBO/containers/gz-sim-gui/Containerfile
  GAZEBO/containers/gz-sim/Containerfile.resolute:89:      qt6-svg-plugins \
  GAZEBO/containers/gz-sim-gui/Containerfile:17:#      qt6-svg-plugins, without which gz-gui's EntityTree icons fail to decode
  $ grep -n 'GZ_RENDERING_RESOURCE_PATH' quadlet/sim-fabrication/ao-sim-fabrication-gui-gz.container
  Environment=GZ_RENDERING_RESOURCE_PATH=/usr/share/gz/gz-rendering
  $ podman images | grep -e gz-sim10-resolute
  localhost/gz-sim10-resolute  gui-svgfix  835cccfdedd6  2.63 GB
  $ systemctl --user is-enabled ao-sim-fabrication-gui-gz.service
  masked
  $ systemctl --user show ao-sim-fabrication-gui-gz.service -p ActiveState,NRestarts
  ActiveState=inactive / NRestarts=0
  The unit is masked by policy (must not seize focus) so no render proof is
  possible without unmasking + starting it, which needs operator approval. The
  2026-10-04 render evidence (18 plugins, 294/140160 live pixels) stands
  unrebutted but is not re-proven here. Update, not close.
section: 10-simulation-architecture
---
SIM-06's image preconditions are still satisfied in tree and the unit is still
correctly masked. I did not unmask or start the GUI (stop condition: focus
seizure risk, plus a live-service-adjacent action). The compiler should keep
the 2026-10-04 close proposal pending a re-shoot after the SIM-16 restart.

What I got wrong: I first assumed `podman images` output alone could sustain
the close; it proves the image exists, not that geometry renders. Those are
different claims.
