---
item: OPS-16
action: close
evidence: |
  $ podman ps --format '{{.Names}}\t{{.Image}}' | grep -v '@sha256:'
  (no output, all running images are digest-pinned, Quadlet-owned)
  $ ls -la GAZEBO/worlds-run/
  drwxrwxr-x 3 scottw scottw ... worlds-run/
  -rw-rw-r-- ... factory.world
  -rw-rw-r-- ... factory.world.host
  drwxrwxr-x ... models/
  # worlds-run/ is a documented scratch directory, not part of the canonical tree
  $ sed -n '300,303p' GAZEBO/handoff.md
  - `/ALWAYSON/GAZEBO/worlds-run/` is a scratch, non-canonical run directory from
    pre-Quadlet debugging; the Quadlet unit does not use it.
section: 12-host-installation-and-configuration
---
The stray containers are gone: `podman ps` now shows no tag-only,
non-Quadlet-owned containers (the six PLAT-01 strays — four Grafana on
`:11.6.0` plus two `foxglove-bridge:latest` — were removed between 2026-10-08 and
this review). What remains, `GAZEBO/worlds-run/`, is a documented scratch area
(`factory.world` container run copy with mesh URIs rewritten, and
`worlds-run/models/meshes/*.dae` dereferenced copies) that the §10.2 handoff
labels "non-canonical ... pre-Quadlet debugging" and confirms the Quadlet unit
does not use. It is preserved on the data-preservation rule; the section notes the
reconciliation is due when the world is adopted into `ao-sim-fabrication`
(README-GAZEBO-WORLD_MOVING.txt §10.2, line 94). The item's strays are closed; the
documented scratch remains by deliberate decision, not by accident.