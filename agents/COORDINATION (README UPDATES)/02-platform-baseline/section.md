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

The host baseline the platform requires. Every value below is a **requirement**: a rebuilt host
or a verification step is written against this table. Measured values for a running host are
**not** recorded here — they belong in `README-ACTION_ITEMS/status-and-references.md`. Where the
two disagree, the tracker is the fact and the requirement below is what must be corrected.

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

A package is part of the platform baseline if the platform's own verification asserts on it. The
install list itself is written in §12.3; the requirement is stated here because the two must agree.

Every package below is **required to be reproducible from the repository's own bootstrap chain**
(`scripts/bootstrap/02-install-host-dependencies.sh` and
`scripts/bootstrap/ao-bootstrap-privileged.sh`, documented in §12.3). A host that is correct only
because an operator installed a package by hand does **not** satisfy this requirement — the
provisioning path is the deliverable, not the host's current package list.

| Package | Required for |
|---|---|
| `apparmor-utils` | `aa-enforce`, `aa-decode`, `aa-genprof`, `aa-logprof` — the profile tools §4.1 relies on |
| `nvidia-container-toolkit` (+ `libnvidia-container1`, `libnvidia-container-tools`, `nvidia-container-toolkit-base`) | GPU access from rootless containers via CDI; the `nvidia.com/gpu=0` device the version matrix records |

**Verification rules for the AppArmor tooling.** These are normative, because each one has
defeated a naive check:

- Test for **`aa-enforce`**, not `aa-status`. `aa-status` ships in the base `apparmor` package, so
  `command -v aa-status` succeeds on a host with no profile tooling installed at all.
- A check must **not** wrap its subject in `sudo … || true`. On this host `sudo` requires
  interactive authentication, so the pipeline cannot fail and cannot inspect anything — while
  still reporting success.
- Any check whose subject requires privilege must report the privilege failure as a failure. A
  check that cannot fail verifies nothing.

**Re-verification 2026-10-08 (PLAT-03).** The host-side half of this item is settled and the
provisioning-side half is not. Re-measured from scratch — every figure reproduces:

```
$ dpkg-query -W -f='${Package} ${Version}\n' apparmor-utils
apparmor-utils 5.0.2-0ubuntu1~26.04.1
$ for b in aa-status aa-enforce aa-complain aa-decode aa-logprof aa-genprof; do \
    p=$(command -v $b || echo MISSING); \
    printf '%-11s %-22s %s\n' "$b" "$p" "$(dpkg -S "$p" 2>/dev/null | cut -d: -f1)"; done
aa-status   /usr/sbin/aa-status      apparmor
aa-enforce  /usr/sbin/aa-enforce     apparmor-utils
aa-complain /usr/sbin/aa-complain    apparmor-utils
aa-decode   /usr/sbin/aa-decode      apparmor-utils
aa-logprof  /usr/sbin/aa-logprof     apparmor-utils
aa-genprof  /usr/sbin/aa-genprof     apparmor-utils
$ grep -rn 'apparmor' scripts/bootstrap/ scripts/provision/ 2>&1; echo rc=$?
rc=1
$ grep -c apparmor scripts/provision/provision.sh
0
$ sed -n '6p' scripts/bootstrap/02-install-host-dependencies.sh
pkgs=(podman uidmap slirp4netns fuse-overlayfs containernetworking-plugins nftables ufw git curl jq ca-certificates gnupg openssl restic smartmontools lm-sensors acl python3 python3-venv python3-pip)
```

`apparmor-utils` is installed on this host and all five profile tools resolve, but **no
bootstrap script and no provisioner names it**. A host rebuilt from the repository's own
chain would not get it, and §4.1's profile workflow would have no tooling. The fix is in
§12.3's install lists, which are the OPS-B session's to edit. `nvidia-container-toolkit`
1.20.1-1 and its three dependencies are present; the version matrix's `1.20.0` row is wrong
(matrix file not owned by this session — recorded in §2.5).

## 2.4 Baseline Verification Must Assert

A verification step **asserts**; it does not print. Each requirement below is normative:

1. Every check must compare an observed value against an expected one and **exit non-zero when
   they differ**. A silent non-zero return that nothing reads is not an assertion.
2. The overall block must exit non-zero if any check fails. A block whose exit status is
   unconditionally zero cannot verify anything, and evidence produced by it cannot be re-run and
   trusted.
3. Each observed value must be **printed beside its expected value**, so a failure is readable
   without re-running the check.
4. A check must run a **control case** before a zero is believed. Counting constructs that return
   a constant regardless of input — for example `systemctl list-unit-files 'pattern' | wc -l`,
   which always prints three lines — must not be used as evidence. Use a form that measures the
   thing itself, such as `grep -c '^ao-'`.
5. Every claim cited as evidence must be **reproducible by the command shown**. A citation that
   does not reproduce is not evidence.

The §12.3 verify block is owned by the OPS-B session; the requirements above are what it must
satisfy.

**Re-verification 2026-10-08 (PLAT-04).** §12.3's replacement verifier
(`scripts/validation/verify-host-baseline.sh`) was run as written, and its failure path was
exercised by stubbing `stat` and `loginctl`. Both directions reproduce:

```
$ bash scripts/validation/verify-host-baseline.sh
=== ALWAYS ON host baseline verification (asserting) ===
  PASS  podman responds (5.7.0)
  PASS  systemd --user manager reachable
  PASS  linger enabled (survives logout)
  PASS  cgroup v2 unified hierarchy
  PASS  aa-status present
  PASS  aa-enforce present (profile enforcement possible)
--- 6 passed, 0 failed ---
RESULT: PASS
EXIT=0

# failure path: stat() reports tmpfs, loginctl reports Linger=no
$ bash -c 'stat() { if [ "$1" = "-fc" ] && [ "$2" = "%T" ] && [ "$3" = "/sys/fs/cgroup" ]; then echo tmpfs; fi; }; export -f stat; loginctl() { echo Linger=no; }; export -f loginctl; bash scripts/validation/verify-host-baseline.sh; echo "EXIT=$?"' 2>&1
=== ALWAYS ON host baseline verification (asserting) ===
  PASS  podman responds (5.7.0)
  PASS  systemd --user manager reachable
  FAIL  linger is '"'"'Linger=no'"'"', expected '"'"'yes'"'"' - containers stop at logout (OPS-13)
  FAIL  cgroup fs type is '"'"'tmpfs'"'"', expected '"'"'cgroup2fs'"'"'
  PASS  aa-status present
  PASS  aa-enforce present (profile enforcement possible)
--- 4 passed, 2 failed ---
RESULT: FAIL (2 check(s) failed)
EXIT=1
```

The verifier satisfies all five requirements in §2.4: it compares observed against expected,
exits non-zero on failure (1, not 0), prints each observed value beside its expected one, and
the control case above is the proof that a passing result means something. The `sudo … ||
true` defect that §12.3 carried is gone — the replacement never wraps a privileged command in
`sudo`, and `aa-enforce` is reported as a WARN when missing rather than passed on `aa-status`.

**PLAT-04 is closed by this script existing and being tested.** The requirement was "add real
assertions" to the install verification; §12.3 now delegates to an asserting script, and §12.3's
own text records the old block's three defects and the replacement. No further change is
needed in §12.3 — it already names the script and documents the test in both directions.

## 2.5 Version Matrix Requirements

`config/platform/version-matrix.yaml` is the machine-readable platform baseline and must satisfy:

1. **Every running container image is digest-pinned.** A tag-only image cannot be verified as
   deployed. Only these are permitted exceptions, and both are deliberate:
   - `ardupilot-sitl:latest` — a moving SITL tag by design;
   - the locally built Gazebo Sim image, whose digest records the validated local build.
2. **No stray container may duplicate a Quadlet-managed unit.** Any container whose name is
   generated by `podman run` rather than owned by a Quadlet unit is residue and must be removed.
   Removal is a delete and requires operator approval per §4.1 rule 3.
3. **Every digest the matrix records must be a digest a container actually runs**, and every
   running digest must appear in the matrix. A matrix that names a digest nothing runs cannot be
   used to verify what is deployed.
4. **Kernel and package versions must be captured, not hand-transcribed.** The matrix is to be
   produced by a generator that reads the running host, so it cannot silently drift.

**Re-verification 2026-10-08 (PLAT-02 audit).** Every claim in §19 PLAT-02 was re-measured.
All reproduce unchanged — the matrix is still wrong in exactly the ways recorded, and the
fixes belong to a session that owns `config/platform/version-matrix.yaml` (not this one):

```
$ uname -r
7.0.0-38-generic                                  # matrix line 3:  kernel: "7.0.0-34-generic"
$ dpkg-query -W -f='${Package} ${Version}\n' nvidia-container-toolkit
nvidia-container-toolkit 1.20.1-1                 # matrix line 14: "1.20.0 installed 2026-08-25"
$ podman ps --format '{{.Image}}' | grep postgres | sort -u
docker.io/library/postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f
$ grep -n 'a65e6a84\|91d0f7e8' config/platform/version-matrix.yaml | sed 's/: *"docker.*//'
21:  broker_image_digest
47:    image_postgres
48:    image_redis
61:  image_postgres_shared
$ podman ps --format '{{.Image}}' | grep redis | sort -u
docker.io/library/redis@sha256:c6eabf748fc7a61dbb5a705c78bcf3d6377b1127a97d0ce965c11c44ba46896f
$ grep -rh '^Image=' quadlet/ | grep -vc '@sha256:'
2
$ grep -rn '^Image=' quadlet/ | grep -v '@sha256:'
quadlet/sim-vehicle/ao-ardupilot-sitl.container:12:Image=ghcr.io/ardupilot/ardupilot-sitl:latest
quadlet/sim-fabrication/ao-sim-fabrication-gui-gz.container:47:Image=localhost/gz-sim10-resolute:gui-svgfix
$ podman ps --format '{{.Names}}\t{{.Image}}' | grep -v '@sha256:' | wc -l
6
$ podman ps --format '{{.Names}}' | wc -l
19
```

**Drift is four keys across four lines, not three rows.** The redis digest appears in two
matrix keys (`broker_image_digest` line 21, `image_redis` line 48) and postgres in two more
(`image_postgres` line 47, `image_postgres_shared` line 61). Counting *rows* rather than *keys*
is how "three" survived two re-verification passes.

**Still open — two independent reasons, both unchanged:**

1. The corrections belong in `config/platform/version-matrix.yaml`, which this session does not
   own. Recording the drift in §2.5 does not fix the matrix, and a version matrix naming a
   digest nothing runs cannot verify what is deployed.
2. The capture automation the item asks for is `OPS-02`, assigned to OPS-B.

The six tag-only running containers remain **unowned strays** (§19 `OPS-16`). Not removed
here — container deletion requires operator approval under README §4.1 rule 3.
