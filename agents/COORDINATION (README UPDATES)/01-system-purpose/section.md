# 1. System Purpose

ALWAYS ON is an on-premises platform supporting an automated modular live/fabricate facility
of roughly 160 square feet, and an accompanying micro-aircraft carrier. Both scale in size
and quantity without changing the architecture.

| Capability | Scope |
|---|---|
| Field | Drone telemetry and field communications over the Reticulum mesh |
| Mapping | Photogrammetry and 3D model production |
| Simulation | Vehicle rehearsal; fabrication, facility, inventory, kitchen and logistics rehearsal |
| Facility | Home automation |
| Commerce | Static storefront, hosted checkout, receipt generation |
| Provenance | Corda-backed receipts, entitlements and approved state transitions |
| Archive | Encrypted pCloud replication and controlled IPFS distribution |
| Content | Static HTML and interactive iframe content from other servers |

**Deployment roles.** The workstation is the development, integration and validation host. It
runs Kubuntu 26.04 LTS on an Intel Core i7-8700K with an NVIDIA GTX 1080. Compute-intensive
production workloads may move to an immersion-cooled server rack and a Raspberry Pi
edge-computing cluster.

Kubuntu is the desktop for four reasons: it is built on Ubuntu LTS with standard security
maintenance to May 2031, giving a predictable maintenance horizon; it carries the ROS 2 and
Gazebo toolchain plus
QGroundControl that the simulation work depends on; KDE Plasma provides the login-gated KDE
Wallet secret flow (§14.1) and Konqueror as the dedicated automation browser; and the KDE
suite covers the desktop and portable hardware this system is built for.

**Container runtime.** Podman is the only supported container runtime. Containers are managed
through systemd Quadlet definitions — never Kubernetes, Docker Compose, a Docker daemon, or
shell-wrapper orchestration (§13).

**Platform identity.** The workstation runs **Ubuntu 26.04 LTS as the base, with KDE Plasma as
the desktop.** Requirements that follow from this, and which the provisioner and any
verification step must be written against:

- The base distribution is Ubuntu 26.04 LTS. The `kubuntu-desktop` metapackage is **not**
  required and must not be assumed installed; only the Kubuntu-flavoured settings packages are
  expected. Verification must not test for `kubuntu-desktop`, `/etc/kubuntu-release`, or any
  `Kubuntu` distributor string — on this platform those correctly read as absent or as
  `Ubuntu`.
- The **KDE Plasma desktop is required**, because the login-gated KDE Wallet secret flow
  (§14.1) and Konqueror as the automation browser depend on it.
- **Support horizon:** standard security maintenance runs to **May 2031**. This is *standard*
  security maintenance, not full support; expanded security maintenance extends to **May 2036**
  under Ubuntu Pro. The 2031 date is therefore when routine maintenance ends, not when the
  release becomes unusable.
- The horizon above is the **Ubuntu LTS base** cycle. Do not substitute a desktop-flavour
  support window for it; flavour cycles are maintained separately and are not covered by the
  base distribution's published dates.

**Toolchain, and how each tool is supplied.** ROS 2 Lyrical is required at `/opt/ros/lyrical`.
Gazebo Sim 10.5.0 is required but runs **containerised**, so `gzserver` must not be expected on
the host `PATH`. QGroundControl is required as an operator tool but **is not a distribution
package**: it is supplied as a user-level AppImage with a `.desktop` launcher under
`~/.local/share/applications`, so neither a `qgroundcontrol` binary on `PATH` nor an entry under
`/usr/share/applications` may be assumed. Any inventory, install list or verification step must
treat AppImage-supplied and locally-built tools as a distinct class from packaged software, and
must not report them as missing merely because no package owns them.

**Why this platform.** The selection rests on: Ubuntu LTS with a published security-maintenance
horizon; the ROS 2 and Gazebo toolchain plus QGroundControl that the simulation work depends on;
KDE Plasma for the Wallet secret flow and Konqueror; and the KDE suite for the desktop and
portable hardware this system is built for.
