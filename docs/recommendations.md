# ALWAYS ON — Update Recommendations

> Generated `2026-10-02T03:46:23+00:00` by `scripts/build-update/recommend.py`.
> Inputs: `docs/drift.md` and `docs/applications.md`.
>
> ```bash
> /ALWAYSON/scripts/build-update/recommend.py --markdown \
>   --out /ALWAYSON/docs/recommendations.md
> ```

## This document is advice, not action

**Nothing in this toolchain updates anything by itself.** This script reads
measurements and writes explanations. It cannot install a package, promote a
digest, edit a Quadlet, deploy a unit, or restart a service, and the commands
below are printed for a human to read and choose to run.

Automatic updates are the **last** thing this system does and they require
review and explicit authorization. They are not built, and this script must
never be extended to perform them. If a future change appears to need this
tool to act, it needs a person and a decision instead.

## What needs you

| Class | Count | What it means |
|---|---|---|
| `SECURITY` | 1 | A security-pocket update is pending. |
| `TAKE_NOW` | 8 | Low risk, human decision. Nothing here applies it for you. |
| `BLOCKED` | 1 | Installed software no repository can deliver an update to. |
| `ORPHANED` | 1 | Installed, but present in no repository index. |
| `UNMANAGED` | 1 | No package manager tracks this at all. |
| `LEAVE` | 14 | Behind upstream with no tracked release. Acting would be a major change, not an update. Explicitly not a to-do. |

**9 items need a decision. 0 have been acted on.**

## SECURITY — A security-pocket update is pending.

### `apt:gstreamer1.0-plugins-good`

- **Subject:** 1.28.2-2ubuntu0.3 -> newer in -security
- **Why:** A security-pocket update is pending. unattended-upgrades is enabled and permitted to install these, so this most likely arrived after its last daily run rather than being missed. Check the log before assuming a failure.
- **Risk:** low, and already automatic by policy
- **If you choose to act:** Confirm it ran: journalctl -u unattended-upgrades. If it did, do nothing - the next apt-daily-upgrade.timer run takes it.

## TAKE_NOW — Low risk, human decision. Nothing here applies it for you.

### `apt:alsa-ucm-conf`

- **Subject:** 1.2.15.3-1ubuntu1.5 -> newer in resolute-updates
- **Why:** An ordinary -updates pocket update is pending. That pocket is deliberately manual, so it waits for a decision rather than installing itself.
- **Risk:** low
- **If you choose to act:** sudo apt upgrade, or leave it - nothing is at risk beyond the benefit

### `apt:drkonqi`

- **Subject:** 6.6.4-0ubuntu1 -> newer in resolute-updates
- **Why:** An ordinary -updates pocket update is pending. That pocket is deliberately manual, so it waits for a decision rather than installing itself.
- **Risk:** low
- **If you choose to act:** sudo apt upgrade, or leave it - nothing is at risk beyond the benefit

### `apt:microsoft-edge-stable`

- **Subject:** 154.0.4258.48-1 -> newer in stable
- **Why:** An ordinary -updates pocket update is pending. That pocket is deliberately manual, so it waits for a decision rather than installing itself.
- **Risk:** low
- **If you choose to act:** sudo apt upgrade, or leave it - nothing is at risk beyond the benefit

### `fabrication/ao-fabrication-db`

- **Subject:** sha256:a65e6a841f6c4dbc4abda3d67fa3bc21824e9611064fcd82e87ea67aad60a0c3
- **Why:** Measured: a newer patch of the SAME major is available. Rolling tags are rebuilt for security fixes, so this is normally a security or correctness patch, not a behaviour change.
- **Risk:** low - same major, so no data format or API break expected
- **If you choose to act:** Re-pin and redeploy when convenient: scripts/build-update/promote-image-digest.sh fabrication ao-fabrication-db.container <image>@sha256:<digest of the tracked tag> then redeploy, restart, and regenerate docs/drift.md

### `mapping/ao-webodm-broker`

- **Subject:** sha256:91d0f7e8c748ec7a4c2b4fb2c4f84edab794dd91d01e095e38dc906db9d684ab
- **Why:** Measured: a newer patch of the SAME major is available. Rolling tags are rebuilt for security fixes, so this is normally a security or correctness patch, not a behaviour change.
- **Risk:** low - same major, so no data format or API break expected
- **If you choose to act:** Re-pin and redeploy when convenient: scripts/build-update/promote-image-digest.sh mapping ao-webodm-broker.container <image>@sha256:<digest of the tracked tag> then redeploy, restart, and regenerate docs/drift.md

### `sales/ao-mastodon-db`

- **Subject:** sha256:a65e6a841f6c4dbc4abda3d67fa3bc21824e9611064fcd82e87ea67aad60a0c3
- **Why:** Measured: a newer patch of the SAME major is available. Rolling tags are rebuilt for security fixes, so this is normally a security or correctness patch, not a behaviour change.
- **Risk:** low - same major, so no data format or API break expected
- **If you choose to act:** Re-pin and redeploy when convenient: scripts/build-update/promote-image-digest.sh sales ao-mastodon-db.container <image>@sha256:<digest of the tracked tag> then redeploy, restart, and regenerate docs/drift.md

### `sales/ao-mastodon-redis`

- **Subject:** sha256:91d0f7e8c748ec7a4c2b4fb2c4f84edab794dd91d01e095e38dc906db9d684ab
- **Why:** Measured: a newer patch of the SAME major is available. Rolling tags are rebuilt for security fixes, so this is normally a security or correctness patch, not a behaviour change.
- **Risk:** low - same major, so no data format or API break expected
- **If you choose to act:** Re-pin and redeploy when convenient: scripts/build-update/promote-image-digest.sh sales ao-mastodon-redis.container <image>@sha256:<digest of the tracked tag> then redeploy, restart, and regenerate docs/drift.md

### `sales/ao-sales-db`

- **Subject:** sha256:a65e6a841f6c4dbc4abda3d67fa3bc21824e9611064fcd82e87ea67aad60a0c3
- **Why:** Measured: a newer patch of the SAME major is available. Rolling tags are rebuilt for security fixes, so this is normally a security or correctness patch, not a behaviour change.
- **Risk:** low - same major, so no data format or API break expected
- **If you choose to act:** Re-pin and redeploy when convenient: scripts/build-update/promote-image-digest.sh sales ao-sales-db.container <image>@sha256:<digest of the tracked tag> then redeploy, restart, and regenerate docs/drift.md

## BLOCKED — Installed software no repository can deliver an update to.

### `351 ROS packages`

- **Subject:** packages.ros.org
- **Why:** This host fails TLS verification against packages.ros.org, so no new or updated ROS package can be fetched. Disabling verification was considered and rejected. This is the largest block of software on the machine that currently cannot be updated by anyone.
- **Risk:** n/a - there is no working update path to have risk from
- **If you choose to act:** Repair the repository's certificate path, or accept that the ROS stack is frozen at its current versions. Do NOT work around it by disabling TLS verification.

## ORPHANED — Installed, but present in no repository index.

### `crossover, foxglove-studio, obsidian`

- **Subject:** installed, absent from every apt index
- **Why:** These are installed but appear in no downloaded repository index, so no apt operation will ever offer them an update. They came from a local file or a source that has since been removed.
- **Risk:** unknown - they receive no security updates at all
- **If you choose to act:** Decide per application: reinstall from a real repository, accept it as frozen, or remove it.

## UNMANAGED — No package manager tracks this at all.

### `16 applications, 88 local executables`

- **Subject:** no package manager tracks these
- **Why:** AppImages, /opt trees and ~/.local/bin executables are tracked by nothing. Several are load-bearing for this project. A stale copy is invisible until it fails, and the inventory cannot tell you one is old because there is nothing to compare it against.
- **Risk:** unknown until something breaks
- **If you choose to act:** Review by hand. A version in the file name, as most AppImages carry, is the only signal available.

## LEAVE — Behind upstream with no tracked release. Acting would be a major change, not an update. Explicitly not a to-do.

### `build-update/ao-build-update`

- **Subject:** docker.io/library/python@sha256:79e7a9b9ff1cbceff819f856fb374477792a5967759d94df266de7b7b4120e6f
- **Why:** No declared stable channel for this image, so there is no release to be behind. For a base image a digest change is often a rebuild with no functional change.
- **Risk:** n/a
- **If you choose to act:** Nothing.

### `mapping/ao-nodeodm`

- **Subject:** opendronemap/nodeodm@sha256:553fe5cacb1c248e3740e07e58cb4edc42c48b86aee229555dc9dc49edb09024
- **Why:** No declared stable channel for this image, so there is no release to be behind. For a base image a digest change is often a rebuild with no functional change.
- **Risk:** n/a
- **If you choose to act:** Nothing.

### `mapping/ao-webodm-web`

- **Subject:** webodm/webodm_webapp@sha256:188267c654c27a0f5352b0ff27ebe777788637df06d948d80ccb8513c72abd38
- **Why:** No declared stable channel for this image, so there is no release to be behind. For a base image a digest change is often a rebuild with no functional change.
- **Risk:** n/a
- **If you choose to act:** Nothing.

### `mapping/ao-webodm-worker`

- **Subject:** webodm/webodm_webapp@sha256:188267c654c27a0f5352b0ff27ebe777788637df06d948d80ccb8513c72abd38
- **Why:** No declared stable channel for this image, so there is no release to be behind. For a base image a digest change is often a rebuild with no functional change.
- **Risk:** n/a
- **If you choose to act:** Nothing.

### `operations/ao-grafana`

- **Subject:** docker.io/grafana/grafana-oss@sha256:b739cda4b61ba3b90707578b643a22cd851fecf4498e6c6ec2d8f9d622a5d0b2
- **Why:** No declared stable channel for this image, so there is no release to be behind. For a base image a digest change is often a rebuild with no functional change.
- **Risk:** n/a
- **If you choose to act:** Nothing.

### `operations/ao-metabase`

- **Subject:** docker.io/metabase/metabase@sha256:fc96bfa830bdc2d65362a02b75c21bbe159bfd0347927c0b1dd58b4864fe2e16
- **Why:** No declared stable channel for this image, so there is no release to be behind. For a base image a digest change is often a rebuild with no functional change.
- **Risk:** n/a
- **If you choose to act:** Nothing.

### `operations/ao-node-exporter`

- **Subject:** docker.io/prom/node-exporter@sha256:863b62ff9f392b6f472e22b4b670ad1cabb66b3042502ebd4b2cd192733e1bce
- **Why:** No declared stable channel for this image, so there is no release to be behind. For a base image a digest change is often a rebuild with no functional change.
- **Risk:** n/a
- **If you choose to act:** Nothing.

### `operations/ao-prometheus`

- **Subject:** docker.io/prom/prometheus@sha256:d47ad27caa12a6f81491a5f6e0d724d6eee5954b4e1bf23961ef13666fc23679
- **Why:** No declared stable channel for this image, so there is no release to be behind. For a base image a digest change is often a rebuild with no functional change.
- **Risk:** n/a
- **If you choose to act:** Nothing.

### `payment/ao-ingress-payment`

- **Subject:** docker.io/library/python@sha256:79e7a9b9ff1cbceff819f856fb374477792a5967759d94df266de7b7b4120e6f
- **Why:** No declared stable channel for this image, so there is no release to be behind. For a base image a digest change is often a rebuild with no functional change.
- **Risk:** n/a
- **If you choose to act:** Nothing.

### `sales/ao-mastodon-streaming`

- **Subject:** sha256:24834e873cc79ae0677c7e5938e575b4367f2c1c6df46376eb7aa937ee467f4b
- **Why:** DELIBERATE HOLD: the operator accepted this digest and asked that it be left alone rather than verified now. Being behind the tracked release is expected, not a gap.
- **Risk:** n/a
- **If you choose to act:** Nothing. Revisit when the Mastodon stack is next verified.

### `sim-fabrication/ao-sim-fabrication-foxglove`

- **Subject:** localhost/foxglove-bridge:latest
- **Why:** Built on this host by ao-sim-fabrication; a rebuild changes the digest and fails the unit until re-pinned, which is the intended fail-safe.
- **Risk:** n/a
- **If you choose to act:** Nothing.

### `sim-fabrication/ao-sim-fabrication-gui-gz`

- **Subject:** localhost/gz-sim10-resolute:gui-svgfix
- **Why:** Built on this host by ao-sim-fabrication; a rebuild changes the digest and fails the unit until re-pinned, which is the intended fail-safe.
- **Risk:** n/a
- **If you choose to act:** Nothing.

### `sim-fabrication/ao-sim-fabrication-gz`

- **Subject:** localhost/gz-sim10-server@sha256:55f8dbcf8decb0b97c6be7cf2fde8859b0fd05735c7a759df09a12e091933581
- **Why:** Built on this host by ao-sim-fabrication; a rebuild changes the digest and fails the unit until re-pinned, which is the intended fail-safe.
- **Risk:** n/a
- **If you choose to act:** Nothing.

### `sim-vehicle/ao-ardupilot-sitl`

- **Subject:** ghcr.io/ardupilot/ardupilot-sitl:latest
- **Why:** DELIBERATE: the operator wants the most recent build, so the floating tag is intentional. Pinning it would be wrong, not a fix. The unit is not deployed, so nothing runs from it today.
- **Risk:** accepted deliberately
- **If you choose to act:** Nothing.

## What was deliberately not recommended

- **Promoting to `latest` for images held at an older major.** PostgreSQL 17, Redis 7, Prometheus 3 are deliberate holds. Moving to `latest` is a major version change needing a dump/restore or a compatibility check, not an update.
- **Re-pinning the local Gazebo builds.** Those belong to `ao-sim-fabrication`, which re-pins after its own rebuild.
- **Disabling TLS verification for packages.ros.org** to unblock 351 packages. That converts a transport fault into a trust fault.
- **Any unattended application of the above.** Not built, by decision.

