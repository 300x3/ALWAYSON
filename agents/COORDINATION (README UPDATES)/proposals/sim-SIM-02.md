---
item: SIM-02
action: keep-open
evidence: |
  Measured 2026-10-04. The subfolder exists and is populated; §19 asks the operator to
  confirm the path, and I cannot supply that confirmation.

  $ ls -d /ALWAYSON/GAZEBO
  /ALWAYSON/GAZEBO
  $ ls /ALWAYSON/GAZEBO/
  09-SIMULATIONARMS.dae              COMPATIBILITY.md
  09-SIMULATIONCONVEYOR.dae          README-GAZEBO-WORLD_MOVING.txt
  09-SIMULATIONMASSING-ADUDOORS_FABRICATIONAREA.dae
  09-SIMULATIONVEHICLES-ARMS.dae     containers
  handoff.md                         models
  portal                             sim
  worlds                             worlds-run

  Four meshes, the container build inputs, the portal, the sim data
  (objects.yaml, boning.yaml), one world and a worlds-run directory.

  The path is load-bearing and already baked into live configuration, which is why
  the confirmation matters rather than being cosmetic:
  $ grep -n 'GAZEBO' config/platform/loopback-services.yaml
  278:  ... serves GAZEBO/portal/index.html, which is the versioned ...
  285:  ... /ALWAYSON/GAZEBO/worlds/factory.world, lists the four SketchUp mesh ...
  $ grep -n 'image_nginx' config/platform/version-matrix.yaml
  46:  image_nginx: "not in use - the :8765 portal is the
      ao-sim-fabrication-portal.service python3 host process serving
      GAZEBO/portal/index.html"
section: 10-simulation-architecture
---

SIM-02 stays open, and it stays open for the right reason: this is an **operator decision**,
not a defect. §19 says "path confirmed by the operator", and an operator confirmation is the
one thing I cannot manufacture or infer from the filesystem.

What I can report is that the path is already load-bearing. `/ALWAYSON/GAZEBO` exists and
holds the four SketchUp meshes, the container build inputs under `containers/`, the portal,
the simulation data under `sim/`, and `worlds/factory.world`. It is already referenced by
live configuration in `loopback-services.yaml` and `version-matrix.yaml`, so the portal
service resolves it today. That is evidence the layout is in use and working — it is not
evidence the operator approved it, and I am not going to record the second as though it were
the first.

I made no change. Moving the folder is out of scope and would break the live portal, which
serves a path already wired into three config files.

**What I got wrong.** I started this item intending to confirm the path myself, on the
reasoning that the directory existing with the right contents settles the question. That is
exactly backwards: the item asks whether a person agreed to it, and the filesystem is
silent on agreement. Checking that the layout is sane was useful — it is reported above —
but it answers a different question, and I nearly let it stand in for the answer.
