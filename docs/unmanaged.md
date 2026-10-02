# ALWAYS ON — Unmanaged Software Tracking

> Generated `2026-10-02T05:21:33+00:00` by `scripts/build-update/track-unmanaged.py`.
>
> ```bash
> /ALWAYSON/scripts/build-update/track-unmanaged.py --markdown \
>   --out /ALWAYSON/docs/unmanaged.md
> ```

**Read-only.** It queries version endpoints and reads files. It installs
nothing, downloads nothing, and changes nothing.

This exists because the operator decided these files are ours to track
(2026-10-02). They have no package manager, so a stale copy stays invisible
until it fails. Provenance is recorded in
`config/build-update/unmanaged-software.yaml`.

## Summary

| Status | Count | Meaning |
|---|---|---|
| BEHIND | 4 | Upstream offers something newer. |
| UNVERSIONED-LOCAL | 1 | Upstream version known; the local file carries no version to compare. |
| UNCHECKABLE | 4 | No way to check automatically. A known gap, not a pass. |
| CURRENT | 2 | Installed version matches upstream. |

**4 item(s) behind, 0 with no recorded provenance.** 4 cannot be checked automatically at all — those are known gaps, not passes.

## Detail

| Item | Kind | Installed | Upstream | Status | Download | Note |
|---|---|---|---|---|---|---|
| `ReticulumMeshChatX-v4.9.1-linux-x86_64.AppImage` | AppImage | `4.9.1` | `v4.9.3` | BEHIND | [link](https://github.com/Quad4-Software/MeshChatX/releases/download/v4.9.3/ReticulumMeshChatX-v4.9.3-linux-amd64.deb) | CHECKED. Upstream v4.9.3, published 2026-09-30. This AppImage is the SOURCE the running native backend was extracted from, NOT the thing that runs: the service execs ~/Ap |
| `cline` | executable | `3.0.60` | `cli-v3.0.68` | BEHIND | - |  |
| `gh (GitHub CLI)` | executable | `2.97.0` | `v2.102.0` | BEHIND | - |  |
| `pymavlink (mav* tools)` | executable | `2.4.49` | `2.4.50` | BEHIND | - |  |
| `QGroundControl-x86_64.AppImage` | AppImage | `not in filename` | `v5.1.5` | UNVERSIONED-LOCAL | [link](https://github.com/mavlink/qgroundcontrol/releases/download/v5.1.5/QGroundControl-x86_64.AppImage) | CHECKED via the releases API. Upstream v5.1.5, 186 MB AppImage, linux amd64 asset present. Earlier this was recorded as UNCHECKABLE, which was WRONG: the filename carries |
| `LM-Studio-0.4.20-1-x64.AppImage` | AppImage | `0.4.20-1` | `-` | UNCHECKABLE | [link](https://lmstudio.ai/download) | Version IS readable from the filename. The download page resolves (HTTP 200) but is rendered client-side and exposes no version to a plain fetch; their release-notes page |
| `mcp` | executable | `unknown` | `-` | UNCHECKABLE | - | BROKEN as installed. Running it reports "typer is required". Recorded so the fault is visible rather than silently counted as working. |
| `nPerf.AppImage` | AppImage | `not in filename` | `-` | UNCHECKABLE | - | PROVENANCE STILL UNKNOWN, and this one is genuinely not checkable because no vendor can be identified. It is a "Network performance testing tool" per its own .desktop Com |
| `pCloud.AppImage` | AppImage | `not in filename` | `-` | UNCHECKABLE | [link](https://www.pcloud.com/download-free-online-cloud-file-storage) | Download page resolves but carries no machine-readable Linux version. Link recorded so a human can check it. Note pCloud also runs from ~/pCloudDrive, which is a differen |
| `bun` | executable | `1.4.2` | `bun-v1.4.2` | CURRENT | - |  |
| `google-chrome` | executable | `154.0.8037.92` | `154.0.8037.92-1` | CURRENT | - |  |

## What this deliberately does not do

- **It does not update anything.** BEHIND is a finding for a human, not a task.
- **It does not chase UNCHECKABLE items with downloads.** The AppImages with no version in the filename would need a vendor page parsed; that is a deliberate gap, recorded so its absence is visible.
- **It does not track Obsidian or Crossover.** The operator keeps track of those personally.

