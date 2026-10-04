# 2. Platform Baseline

## 2.1 Intended Platform Standard

| Area | Architecture requirement |
|---|---|
| Host OS | Kubuntu 26.04 LTS workstation; the selection rationale is in §1 |
| Current CPU/GPU | AMD CPU and EVGA NVIDIA GTX 1080 |
| Future compute | Immersion-cooled server rack and Raspberry Pi edge cluster |
| Container engine | Podman only |
| Container lifecycle | systemd and Podman Quadlet |
| Public website | Static HTML in pCloud Public Folder + Cloudflare domain registration |
| Payments | Provider-hosted checkout and verified payment events; no local card handling; local stablecoin processing |
| Sales and support | Sales API, PostgreSQL, Mastodon integration, OpenClaw, and LM Studio |
| Drone compute | Raspberry Pi 5 with Waveshare SX1262-class LoRa top-hat |
| Drone autopilot | 3DR N1 connected to Raspberry Pi 5 by MAVLink |
| Desktop radios | Two Heltec LoRa 32 V3 (SX1262), distinguished by USB port topology as `/dev/ao-drone-radio` (ttyUSB0, DRONE-RADIO 917 MHz) and `/dev/ao-people-radio` (ttyUSB1, PEOPLE-RADIO 915 MHz) |
| Field protocol | RNS/Reticulum and MeshChatX over raw LoRa unless a true LoRaWAN deployment is selected |
| Mapping | WebODM and supporting services under Podman |
| Mapping storage | `/media/scottw/500GBPHOTOGRAM/` |
| Vehicle simulation | ROS 2 Lyrical, Gazebo Sim 10.5.0, ArduPilot SITL, MAVLink, QGroundControl |
| Fabrication simulation | ROS 2 Lyrical, Gazebo Sim 10.5.0, robot cells, additive manufacturing, storage, kitchen, and logistics models |
| Ledger | Corda core behind a dedicated ledger-ingestion gateway |
| Archive | Local source data, signed manifests, encrypted pCloud replication, private or encrypted IPFS workflow |
| Monitoring | Prometheus-compatible metrics, alerts, health checks, and protected administration access |
| Backup | PostgreSQL/Corda-aware backup, restic or equivalent encrypted backup, and scheduled restore testing |

## 2.2 Platform Baseline

The host baseline this design assumes. This is the requirement; the measured values for the
running host are in §19.1, and where the two differ §19.1 is the fact.

| Area | Baseline |
|---|---|
| Kernel | Ubuntu LTS kernel |
| Podman | Rootless for every workload (§13.1, §13.2) |
| Podman networks | **Fourteen** `ao-*` networks, all registered in `config/platform/network-cidrs.yaml`, which is the only authoritative list. **Eleven** are `Internal=true`: the ten workload domains `ao-admin`, `ao-data`, `ao-fabrication`, `ao-field`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-mapping`, `ao-payment`, `ao-sim-fabrication`, `ao-sim-vehicle`, plus `ao-html-window`. **Three** are deliberately `Internal=false`: `ao-sales` for ActivityPub delivery, `ao-reporting-egress` for Grafana and Metabase, and `ao-build-update` for software acquisition |
| GPU | EVGA NVIDIA GTX 1080 |
| NVIDIA driver | Pinned, recorded in the version matrix |
| NVIDIA integration | CDI devices registered, including `nvidia.com/gpu=0`. The authoritative spec is `/var/run/cdi/nvidia.yaml`. `/etc/cdi/nvidia.yaml` is not a source of truth and is regenerated or removed at each driver change. Only the authoritative spec contributes devices |
| Simulation stack | ROS 2 Lyrical at `/opt/ros/lyrical`; Gazebo Sim 10.5.0 |
| Host PostgreSQL | PostgreSQL 18, loopback-only |
| Host Redis | Redis 8, loopback-only |

## 2.3 Packages the Verification Steps Depend On

The install list is written in §12.3, which another session owns. The requirement belongs here,
because a package is part of the platform baseline if the platform's own verification asserts
on it. Measured 2026-10-03:

| Package | Needed by | Installed on this host |
|---|---|---|
| `apparmor-utils` | `aa-enforce`, `aa-decode`, `aa-genprof`, `aa-logprof` — the profile tools §4.1 relies on | **No.** `dpkg -S /usr/sbin/aa-status` returns `apparmor: /usr/sbin/aa-status`, i.e. `aa-status` ships in the base `apparmor` package; `apt-cache policy apparmor-utils` → `Installed: (none)`. `aa-enforce`, `aa-complain`, `aa-decode`, `aa-logprof` and `aa-genprof` are all `MISSING` |
| `nvidia-container-toolkit` (+ `libnvidia-container1`, `libnvidia-container-tools`, `nvidia-container-toolkit-base`) | GPU access from rootless containers via CDI; the `nvidia.com/gpu=0` device the version matrix records | Yes — all four at **1.20.1-1** |

**Consequence.** The §12.3 verify block runs `sudo aa-status`, which succeeds today only
because the base `apparmor` package happens to provide that one binary. Any assertion that
actually *changes* or *inspects* a profile — `aa-enforce`, `aa-complain` — would fail on a
freshly provisioned host. `apparmor-utils` is therefore required by §12.3's own verification,
and its absence from the install list is a real gap, not a cosmetic one.

**Correction to a stale claim.** `config/platform/version-matrix.yaml` records
`nvidia-container-toolkit 1.20.0 installed 2026-08-25`. `dpkg-query -W` reports **1.20.1-1**.
The matrix is a version record, so this row is wrong; it is recorded here rather than edited,
because the matrix file is not owned by this session.

## 2.4 Baseline Verification Must Assert

§12.3's verify block currently **prints**; it does not **assert**. Reproduced 2026-10-03 by
running its five commands as written:

```
Linger=yes
cgroups v2 active
cgroup line rc=0
--- now simulate the cgroup check FAILING:
last rc=1  <-- silent, no output, script continues
OVERALL SCRIPT EXIT=0
```

Two defects, both reproduced above:

1. The cgroup line `test "$(stat -fc %T /sys/fs/cgroup)" = "cgroup2fs" && echo "..."` is
   **silent on failure** — it prints nothing and returns non-zero, and nothing reads that
   return code.
2. The block's **overall exit status is 0 either way**. A script that cannot fail cannot
   verify anything, so the §19.2 evidence it supports cannot be re-run and trusted (this is
   the same defect `OPS-15` records).

**Requirement.** The §12.3 verify block must exit non-zero when any check fails, and must name
the expected value beside each observed one so a failure is readable without re-running it.
The block as written cannot be closed by this session: §12.3 is owned by the OPS-B session.
See `agents/COORDINATION/proposals/plat-PLAT-04.md`.

## 2.5 Version Matrix Audit

`config/platform/version-matrix.yaml` is the machine-readable baseline. It is not owned by
this session, so the audit result is recorded here and the file left untouched. Run
2026-10-03.

**Six of the 25 running containers are tag-only, and all six are strays, not Quadlet units.**
`podman ps --format '{{.Names}}\t{{.Image}}' | grep -v '@sha256:'` returns six rows — four
Grafana containers on `:11.6.0` tags and two on `localhost/foxglove-bridge:latest` — and
**every one has a generated `podman run` name** (`ao-sqli3`, `keen_bhabha`, `confident_khayyam`,
`relaxed_tharp`, `dreamy_rosalind`, `vigorous_shannon`), so no Quadlet unit owns them. They
are residue from earlier manual runs and duplicate the pinned `ao-grafana` and
`ao-sim-fabrication-foxglove`. **They are not removed here** — that is container deletion and
README §4.1 rule 3 requires operator approval; §19 `OPS-16` already tracks stray containers.

In the repository, `grep -rh '^Image=' quadlet/ | grep -vc '@sha256:'` → **2**: the deliberate
`ardupilot-sitl:latest` (a moving SITL tag) and the local `localhost/gz-sim10-resolute:gui-svgfix`
build. Every other unit image is digest-pinned.

**The `nginx:alpine` row named in `PLAT-02` no longer exists as an unpinned image.**
`grep -rn 'nginx:alpine' . --exclude-dir=.git` returns **no file under `quadlet/` or
`config/`** — only historical mentions in `docs/compliance/installation-status.md`,
`GAZEBO/`, an archived `TOPOLOGY/` JSON, and the §19 text itself. `quadlet/sim-fabrication/ao-sim-fabrication-portal.service`
records why: the throwaway `gazebo-portal` nginx container was replaced by a `python3` host
process. **That half of `PLAT-02` is already satisfied**; §19.2 said as much on 2026-10-01
and `PLAT-02` was not updated to match.

**Drift found between the matrix and the running host** — three rows are stale:

| Matrix row | Records | Actually is |
|---|---|---|
| `host.kernel` | `7.0.0-34-generic` | `7.0.0-38-generic` (`uname -r`) |
| `gpu.container_runtime_integration` | `nvidia-container-toolkit 1.20.0` | `1.20.1-1` (`dpkg-query -W`) |
| `operations.image_postgres_shared` | `postgres@sha256:a65e6a84…` | `postgres@sha256:d74eeac9…` is what `ao-sales-db`, `mastodon-db` and `ao-fabrication-db` actually run |

The PostgreSQL row is the one that matters: the matrix names a digest no container is
running, so it cannot be used to verify what is deployed. Note also that four digests are
running but absent from the matrix — `gz-sim10-server`, `foxglove-bridge`, and the two Redis
digests `c6eabf74…` (used by both `ao-webodm-broker` and `mastodon-redis`, while the matrix
records the older `91d0f7e8…`).

**Remaining for `PLAT-02`:** the matrix is still hand-edited rather than captured by a
generator, and these three rows plus the four missing digests need correcting.
Verifying it by hand is what found the drift, so the capture automation matters — but that
automation is `OPS-02`, assigned to OPS-B.
