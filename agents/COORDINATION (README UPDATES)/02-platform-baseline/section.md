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
on it. **Re-measured 2026-10-04 09:22** — the `apparmor-utils` row changed under this section
after it was first written, so both states are recorded:

| Package | Needed by | Installed on this host |
|---|---|---|
| `apparmor-utils` | `aa-enforce`, `aa-decode`, `aa-genprof`, `aa-logprof` — the profile tools §4.1 relies on | **Yes, as of 2026-10-04 09:07.** `dpkg-query -W` → `apparmor-utils 5.0.2-0ubuntu1~26.04.1`; all five binaries resolve under `/usr/sbin/`. *(It was **absent** when this row was first measured on 2026-10-03: `apt-cache policy` → `Installed: (none)` and all five tools `MISSING`.)* |
| `nvidia-container-toolkit` (+ `libnvidia-container1`, `libnvidia-container-tools`, `nvidia-container-toolkit-base`) | GPU access from rootless containers via CDI; the `nvidia.com/gpu=0` device the version matrix records | Yes — all four at **1.20.1-1** |

**How the `apparmor-utils` state changed, and what did not change with it.** `/var/log/apt/history.log`
records the install at `2026-10-04 09:07:11`, `Requested-By: scottw (1000)`, pulling in
`apparmor-utils`, `python3-apparmor` and `python3-libapparmor` at `5.0.2-0ubuntu1~26.04.1`. This
was an **interactive operator action, not a change to any install list** — the gap this section
recorded is therefore still open:

- `scripts/bootstrap/02-install-host-dependencies.sh` line 6 still does not name `apparmor-utils`.
- `scripts/bootstrap/ao-bootstrap-privileged.sh` still does not name it.
- `scripts/provision/provision.sh` contains **zero** occurrences of `apparmor`
  (`grep -c apparmor scripts/provision/provision.sh` → `0`).

So the host is fixed and the **provisioning path is not**. A host rebuilt from the repository's
own bootstrap chain would not get `apparmor-utils`, and §4.1's profile workflow has no tooling.
**This section must not read as "satisfied" on the strength of one host's package list.**

**Correction to a stale claim.** `config/platform/version-matrix.yaml` records
`nvidia-container-toolkit 1.20.0 installed 2026-08-25`. `dpkg-query -W` reports **1.20.1-1**.
The matrix is a version record, so this row is wrong; it is recorded here rather than edited,
because the matrix file is not owned by this session.

**Traps recorded for the next session.**

- **`aa-status` is a misleading success signal.** `dpkg -S /usr/sbin/aa-status` →
  `apparmor: /usr/sbin/aa-status`: it ships in the **base `apparmor` package**, not in
  `apparmor-utils`. Any verification that tests `command -v aa-status` will pass on a host with
  no profile tooling installed at all. Test for `aa-enforce`, not `aa-status`.
- **`aa-status` returns non-zero without privilege, and §12.3 throws that away.**
  Unprivileged it prints `apparmor module is loaded.` on stdout, writes
  `You do not have enough privilege to read the profile set.` to stderr and **exits 4** —
  measured, not assumed. §12.3 line 163 is `sudo aa-status || true`, and the `|| true`
  discards exactly the status that would have told the operator the profile set was
  unreadable. Combined with `sudo` requiring interactive authentication on this host
  (`sudo -n aa-status` → `sudo: interactive authentication is required`, rc=1), the line
  cannot fail. This is the same class of defect as the cgroup check in §2.4.

**Re-measured 2026-10-04 17:05 — every claim in this subsection reproduces, and the gap is
unchanged.** I did not trust the earlier passes on this item, because one of them closed it on a
host measurement and a package installed by hand between two passes then invalidated the close.

```
$ dpkg-query -W -f='${Package} ${Version}\n' apparmor-utils
apparmor-utils 5.0.2-0ubuntu1~26.04.1                       # still installed
$ dpkg -S /usr/sbin/aa-enforce /usr/sbin/aa-genprof 2>/dev/null | cut -d: -f1
apparmor-utils                                               # both resolve to the right package
$ grep -n 'apparmor' scripts/bootstrap/*.sh scripts/provision/*.sh
(no matches, rc=1)                                           # the install lists STILL omit it
$ grep -c apparmor scripts/provision/provision.sh
0
$ sed -n '6p' scripts/bootstrap/02-install-host-dependencies.sh
pkgs=(podman uidmap slirp4netns fuse-overlayfs containernetworking-plugins nftables ufw git curl jq ca-certificates gnupg openssl restic smartmontools lm-sensors acl python3 python3-venv python3-pip)
                                                          # no apparmor-utils
$ aa-status >/tmp/aas.out 2>/tmp/aas.err ; echo "rc=$?"
rc=4                                                         # §12.3 discards this with || true
```

**PLAT-03 therefore cannot close from this session, and the reason is ownership, not effort.**
The acceptance criterion is *"reconcile the install list with the verification steps"* — a property
of the **repository**. The package is on the host; the two install lists that would reproduce it on
a rebuild are `scripts/bootstrap/02-install-host-dependencies.sh` and
`scripts/bootstrap/ao-bootstrap-privileged.sh`, both documented in **§12.3**, which belongs to the
OPS-B session. Editing them here would be editing another group's requirement. **Referred to OPS-B
with this evidence**; see `agents/COORDINATION (README UPDATES) (README UPDATES)/proposals/plat-PLAT-03.md`.

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

**Third defect, found 2026-10-04: the `aa-status` line discards its own failure.** §12.3
line 163 is `sudo aa-status || true`. Running the block **verbatim** (all six lines,
`sudo` untouched):

```
--- verbatim §12.3 verify block (lines 158-163) ---
podman version rc=0
podman info rc=0
systemctl --user status rc=0
Linger=yes
cgroups v2 active
OVERALL EXIT=0

[stderr]
sudo: A terminal is required to authenticate
```

The AppArmor check **never ran** — `sudo` could not authenticate — and the block still
reported success. An operator reading that output sees six green lines and concludes the
profile set is in enforcing mode. It was not even inspected. Note the interaction with §2.3:
`apparmor-utils` being newly installed makes this line *look* more meaningful than it is,
because the tool now exists and `aa-status` still cannot read anything without privilege.

**Requirement.** The §12.3 verify block must exit non-zero when any check fails, and must name
the expected value beside each observed one so a failure is readable without re-running it.
The block as written cannot be closed by this session: §12.3 is owned by the OPS-B session.
See `agents/COORDINATION (README UPDATES) (README UPDATES)/proposals/plat-PLAT-04.md`.

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

**Re-verified 2026-10-04** by re-running every command in this audit against the live host.
All findings above reproduced unchanged: 2 unpinned `Image=` lines in the repository, the same
six tag-only running containers (`ao-sqli3`, `keen_bhabha`, `confident_khayyam`,
`relaxed_tharp`, `dreamy_rosalind`, `vigorous_shannon`) still present, `kernel` still recorded
as `7.0.0-34-generic` against a live `7.0.0-38-generic`, `nvidia-container-toolkit` still
recorded as `1.20.0` against a live `1.20.1-1`, and `image_postgres_shared` still naming
`postgres@sha256:a65e6a84…` while every running PostgreSQL container uses
`postgres@sha256:d74eeac9…`.

**Trap — `systemctl list-unit-files … | wc -l` is not a count of units.** It always prints
three lines (the header, a blank line, and `0 unit files listed.`), so `wc -l` returns `3`
whether or not any unit exists. Measured, with a control:

```
$ systemctl list-unit-files 'ao-webodm*' | wc -l
3
$ systemctl list-unit-files 'ao-nonexistentxyz*' | wc -l   # control: impossible pattern
3                                    # identical -- so wc -l measures boilerplate
$ systemctl list-unit-files 'ao-webodm*' | grep -c '^ao-'
0                                    # the valid measurement
$ systemctl --user list-unit-files 'ao-webodm*' | grep -c '^ao-'
4                                    # same form, scope where units DO exist
```

This matters because an earlier `PLAT-01` proposal cited the `wc -l` form as evidence of "no
system-level units". The **conclusion was right** — there are none — but the command shown
could not have produced the number reported. A citation that does not reproduce is not
evidence, and it is corrected in `agents/COORDINATION (README UPDATES) (README UPDATES)/proposals/plat-PLAT-01.md`. Reach for
`grep -c '^ao-'`, or `--no-legend`, and always run a control pattern before believing a zero.

**Remaining for `PLAT-02`:** the matrix is still hand-edited rather than captured by a
generator, and these three rows plus the four missing digests need correcting.
Verifying it by hand is what found the drift, so the capture automation matters — but that
automation is `OPS-02`, assigned to OPS-B.

**Fourth pass, 2026-10-04 17:05 — every figure in this audit re-measured. All reproduce.**
Because this audit has already been corrected once for an unsummarised complement, I re-ran each
figure rather than trusting the text:

```
$ uname -r                                    7.0.0-38-generic   # matrix says 7.0.0-34-generic
$ dpkg-query -W -f='${Package} ${Version}\n' nvidia-container-toolkit
nvidia-container-toolkit 1.20.1-1                                        # matrix says 1.20.0
$ podman ps --format '{{.Image}}' | grep postgres | sort -u
docker.io/library/postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f
                                                                 # matrix says a65e6a84 (lines 47 AND 61)
$ podman ps --format '{{.Image}}' | grep redis | sort -u
docker.io/library/redis@sha256:c6eabf748fc7a61dbb5a705c78bcf3d6377b1127a97d0ce965c11c44ba46896f
                                                                 # matrix says 91d0f7e8 (lines 21 AND 48)
$ grep -rh '^Image=' quadlet/ | grep -vc '@sha256:'   2
$ podman ps --format '{{.Names}}\t{{.Image}}' | grep -v '@sha256:' | wc -l   6
$ podman ps --format '{{.Names}}' | wc -l               25
```

The six tag-only strays are the same six by name, and the two deliberate repository exceptions are
the same two files (`ao-ardupilot-sitl.container:12`,
`ao-sim-fabrication-gui-gz.container:47`). **Correction to the count: the stale digests live in
four keys across four lines, not the "three rows" earlier passes reported** —

```
$ grep -n 'a65e6a84\|91d0f7e8' config/platform/version-matrix.yaml | sed 's/: *"docker.*//'
21:  broker_image_digest
47:    image_postgres
48:    image_redis
61:  image_postgres_shared
```

Counting *rows* rather than *keys* is how "three" survived two re-verification passes: `postgres`
appears in two keys and `redis` in two more. With kernel and `nvidia-container-toolkit` that is
**four stale keys carrying four wrong values**, and the two database digests are the serious ones
because every running container disagrees with the recorded pin.
