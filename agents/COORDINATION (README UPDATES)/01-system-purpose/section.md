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

**Correction 2026-10-04 — what "Kubuntu" is worth, measured.** The Kubuntu rationale above is
the *selection* rationale and stands. But the running host does not identify itself as Kubuntu,
and a reader checking `lsb_release` will get a different answer than this paragraph gives. It
is KDE Plasma on Ubuntu 26.04.1, not a Kubuntu-flavoured install:

```
$ lsb_release -a
Distributor ID:	Ubuntu
Description:	Ubuntu 26.04.1 LTS
Release:	26.04
Codename:	resolute
$ cat /etc/kubuntu-release
cat: /etc/kubuntu-release: No such file or directory
$ apt-cache policy kubuntu-desktop
kubuntu-desktop:
  Installed: (none)
$ plasmashell --version
plasmashell 6.6.6
$ systemctl is-enabled sddm
enabled
```

Six installed packages carry the Kubuntu name, three named `kubuntu-*` and three not
(`libkubuntu1`, `plymouth-theme-kubuntu-logo`, `plymouth-theme-kubuntu-text`):

```
$ dpkg -l | awk '/^ii/ && $2 ~ /kubuntu/ {print $2}' | sort
kubuntu-notification-helper
kubuntu-settings-desktop
kubuntu-wallpapers
libkubuntu1
plymouth-theme-kubuntu-logo
plymouth-theme-kubuntu-text
```

So: Ubuntu LTS base, KDE Plasma 6.6.6 on SDDM, Kubuntu-flavoured settings only. The
`kubuntu-desktop` metapackage is **not** installed, and `apt-cache show` confirms it sits in
`universe`, not `main` (`Section: universe/metapackages`, candidate `1.496`). Every
functional claim this
section rests on is independently
true — Plasma 6.6.6 is present, `konqueror`, `kwalletmanager5` and `kwallet-query` are
installed (§14.1), ROS 2 Lyrical is at `/opt/ros/lyrical` (§2.2), and the machine is an
i7-8700K with a GeForce GTX 1080. Only the distribution label was loose.

**Toolchain correction, same date.** §1 says the desktop "carries the ROS 2 and Gazebo toolchain
plus QGroundControl". ROS 2 and Gazebo are real: `ros2` resolves to `/opt/ros/lyrical/bin/ros2`
and `gzserver` is not on the host PATH because Gazebo runs containerised
(`ao-sim-fabrication-gz`, carrying `gz` and `gz-msgs_*`; the host keeps a wrapper at
`~/bin/gazebo`). **QGroundControl is an AppImage, not an installed package** — there is no
`qgroundcontrol` binary on the PATH and no `.desktop` entry under
`/usr/share/applications`; the operator runs
`~/Documents/APP IMAGES/QGroundControl-x86_64.AppImage`, which has left state in
`~/.config/QGroundControl` and `~/.cache/QGroundControl`. It does have a **user-level**
launcher, so it is on the desktop menu even though it is not a package:

```
$ find /usr/share/applications ~/.local/share/applications -iname '*ground*'
/home/scottw/.local/share/applications/qgroundcontrol.desktop
$ grep '^Exec' ~/.local/share/applications/qgroundcontrol.desktop
Exec="/home/scottw/Documents/APP IMAGES/QGroundControl-x86_64.AppImage" %U
```

The distinction worth keeping is AppImage-vs-package, not absent-vs-present: the launcher
just invokes the AppImage path, which is why the binary is not on the PATH. Same for the
Foxglove bridge, which is a locally built image (`localhost/foxglove-bridge`) rather than a
pinned upstream digest. Those two are simulation-toolchain facts and belong to the SIM
group's inventory; they are noted here only so §1 does not read as a package manifest.

**Support-horizon correction, same date.** This paragraph previously gave the maintenance
horizon as "April 2031". Canonical's published release-cycle table gives **May 2031**, and
the month was the substance of the claim — a maintenance horizon is only useful if it is the
right one. Measured 2026-10-04 from `ubuntu.com/about/release-cycle`:

```
26.04 LTS   Released: Apr 2026
            Standard security maintenance    May 2031
            Expanded security maintenance    May 2036
```

Two things follow that are worth more than the date. The horizon is **standard security
maintenance, not full support** — extended to May 2036 with Ubuntu Pro, so the 2031
figure is when routine maintenance stops, not when the release stops being usable. And this
section's "Kubuntu" claim is about the *Ubuntu LTS base*, whose cycle is the table above;
flavour cycles are maintained separately by their own communities and are not covered by
Canonical's dates. Since this host is Ubuntu 26.04.1 LTS with KDE Plasma rather than
Kubuntu proper (see the correction above), the base table is in fact the correct one to cite
— but a reader should not take the flavour's support window to be the same number.
