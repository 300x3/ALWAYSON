# ALWAYS ON — Pinned vs Stable

> Generated `2026-10-02T03:45:47+00:00` by `scripts/build-update/drift-report.py`.

> Read-only. This resolves and compares; it never pulls, installs, or restarts.
> Promotion is a separate, explicit step (`promote-image-digest.sh`).

Two verdicts mean different things, and the difference matters:

- **DRIFT** — behind a *tracked release tag* (Mastodon `v4.3.7`). The host
  intends to be on that release, so this is a real finding.
- **BEHIND LATEST** — the upstream `latest` tag has moved. This is **usually
  not a defect**: an image deliberately held at an older major (Postgres 17
  while `latest` is 18) reports exactly this. Treat it as information, not
  as a to-do. Promoting to `latest` would be a MAJOR version change.

Neither verdict is an instruction to update. A bump may be a major version,
a schema change, or a rebuild with no upstream equivalent.

## 1. Container images

| Unit | Domain | Pinned digest | Upstream stable | Verdict |
|---|---|---|---|---|
| `ao-build-update` | build-update | `79e7a9b9ff1cbcef` | `1ae5b32b33f50233` | BEHIND LATEST (no tracked release tag) |
| `ao-fabrication-db` | fabrication | `a65e6a841f6c4dbc` | `d74eeac9a635390a` | BEHIND TRACKED TAG (17, rolling: newer patch of same major) |
| `ao-nodeodm` | mapping | `553fe5cacb1c248e` | `fcd99eb23d8db194` | BEHIND LATEST (no tracked release tag) |
| `ao-webodm-broker` | mapping | `91d0f7e8c748ec7a` | `c6eabf748fc7a61d` | BEHIND TRACKED TAG (7, rolling: newer patch of same major) |
| `ao-webodm-db` | mapping | `03f18ec0089325ec` | `03f18ec0089325ec` | IN SYNC |
| `ao-webodm-web` | mapping | `188267c654c27a0f` | `8dbc0dcc1fb236c6` | BEHIND LATEST (no tracked release tag) |
| `ao-webodm-worker` | mapping | `188267c654c27a0f` | `8dbc0dcc1fb236c6` | BEHIND LATEST (no tracked release tag) |
| `ao-grafana` | operations | `b739cda4b61ba3b9` | `5dad0df181cb644a` | BEHIND LATEST (no tracked release tag) |
| `ao-metabase` | operations | `fc96bfa830bdc2d6` | `b7c6250d7fd28663` | BEHIND LATEST (no tracked release tag) |
| `ao-node-exporter` | operations | `863b62ff9f392b6f` | `1b4e4438faca4dd7` | BEHIND LATEST (no tracked release tag) |
| `ao-prometheus` | operations | `d47ad27caa12a6f8` | `efd719c99d83b060` | BEHIND LATEST (no tracked release tag) |
| `ao-ingress-payment` | payment | `79e7a9b9ff1cbcef` | `1ae5b32b33f50233` | BEHIND LATEST (no tracked release tag) |
| `ao-mastodon-db` | sales | `a65e6a841f6c4dbc` | `d74eeac9a635390a` | BEHIND TRACKED TAG (17, rolling: newer patch of same major) |
| `ao-mastodon-redis` | sales | `91d0f7e8c748ec7a` | `c6eabf748fc7a61d` | BEHIND TRACKED TAG (7, rolling: newer patch of same major) |
| `ao-mastodon-sidekiq` | sales | `76436bccad38f134` | `76436bccad38f134` | IN SYNC |
| `ao-mastodon-streaming` | sales | `24834e873cc79ae0` | `d2d33ed38313a5a3` | HELD (operator-accepted, tracking v4.3.7) |
| `ao-mastodon-web` | sales | `76436bccad38f134` | `76436bccad38f134` | IN SYNC |
| `ao-sales-db` | sales | `a65e6a841f6c4dbc` | `d74eeac9a635390a` | BEHIND TRACKED TAG (17, rolling: newer patch of same major) |
| `ao-sim-fabrication-foxglove` | sim-fabrication | `latest` | `-` | LOCAL BUILD (no upstream) |
| `ao-sim-fabrication-gui-gz` | sim-fabrication | `gui-svgfix` | `-` | LOCAL BUILD (no upstream) |
| `ao-sim-fabrication-gz` | sim-fabrication | `55f8dbcf8decb0b9` | `-` | LOCAL BUILD (no upstream) |
| `ao-ardupilot-sitl` | sim-vehicle | `latest` | `-` | UNPINNED BY CHOICE (operator wants latest) |

## 2. APT packages

`4229` packages installed, `4` differ from the current
`Candidate`. Policy: `-security` installs unattended; `-updates` and
third-party repositories wait for an operator decision.

| Package | Installed | Candidate | Repository |
|---|---|---|---|
| `alsa-ucm-conf` | `1.2.15.3-1ubuntu1.5` | `1.2.15.3-1ubuntu1.7` | http://us.archive.ubuntu.com/ubuntu resolute-updates/main |
| `drkonqi` | `6.6.4-0ubuntu1` | `6.6.6-0ubuntu0.1` | http://us.archive.ubuntu.com/ubuntu resolute-updates/universe |
| `gstreamer1.0-plugins-good` | `1.28.2-2ubuntu0.3` | `1.28.2-2ubuntu0.4` | http://security.ubuntu.com/ubuntu resolute-security/main |
| `microsoft-edge-stable` | `154.0.4258.48-1` | `154.0.4258.53-1` | https://packages.microsoft.com/repos/edge-stable stable/main |

## 3. Snap

`16` snaps installed. snapd refreshes these **unattended** — the one
category on this host that updates itself.

No pending refreshes: every snap is at its channel revision.

## 4. Flatpak

`1` applications. `flatpak-system.timer` is **not installed**, so these
do not update themselves.

| Application | Version | Branch | Origin |
|---|---|---|---|
| `com.usebottles.bottles` | `66.7` | stable | flathub |

---

## Summary

| Outcome | Count | Meaning |
|---|---|---|
| IN SYNC | 3 | Pinned digest equals upstream stable. Leave alone. |
| **DRIFT** | **0** | Behind a tracked release tag. Needs a decision. |
| HELD | 1 | Deliberately held at this digest by operator decision. Not a finding. |
| BEHIND TRACKED TAG | 5 | Newer **patch of the same major** is out (rolling tag). Safe to take; not a version decision. |
| BEHIND LATEST | 9 | No tracked release tag exists for this image, so `latest` is all there is. **Not a defect.** |
| UNRESOLVED | 0 | Registry did not answer. Retry or investigate. |
| LOCAL BUILD | 3 | Built on this host; no upstream to compare. |
| UNPINNED BY CHOICE | 1 | Floating tag the operator WANTS (most recent). Not a defect. |
| **NOT PINNED** | **0** | Floating tag or missing `Image=`, not chosen. A finding. |

## Keeping this current

```bash
# regenerate
/ALWAYSON/scripts/build-update/drift-report.py --markdown \
  --out /ALWAYSON/docs/drift.md

# apply one decision
/ALWAYSON/scripts/build-update/promote-image-digest.sh <domain> <unit>.container <ref>
```

Run it after a promotion, before deciding an `apt upgrade`, and any time you
want to know whether the host is behind. It is read-only, so running it costs
nothing and changes nothing.
