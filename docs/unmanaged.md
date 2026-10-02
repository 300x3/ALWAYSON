# ALWAYS ON — Unmanaged Software Tracking

> Generated `2026-10-02T05:06:20+00:00` by `scripts/build-update/track-unmanaged.py`.
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
| BEHIND | 3 | Upstream offers something newer. |
| UNCHECKABLE | 6 | No way to check automatically. A known gap, not a pass. |
| CURRENT | 2 | Installed version matches upstream. |

**3 item(s) behind, 0 with no recorded provenance.** 6 cannot be checked automatically at all — those are known gaps, not passes.

## Detail

| Item | Kind | Installed | Upstream | Status | Note |
|---|---|---|---|---|---|
| `cline` | executable | `3.0.60` | `cli-v3.0.68` | BEHIND |  |
| `gh (GitHub CLI)` | executable | `2.97.0` | `v2.102.0` | BEHIND |  |
| `pymavlink (mav* tools)` | executable | `2.4.49` | `2.4.50` | BEHIND |  |
| `LM-Studio-0.4.20-1-x64.AppImage` | AppImage | `0.4.20-1` | `-` | UNCHECKABLE | Version is readable from the filename, but there is no feed to compare it to. |
| `QGroundControl-x86_64.AppImage` | AppImage | `not in filename` | `-` | UNCHECKABLE | Filename carries no version, so freshness cannot be inferred from it. Would need the download page parsed. Tracked, but reported as UNCHECKABLE. |
| `ReticulumMeshChatX-v4.9.1-linux-x86_64.AppImage` | AppImage | `4.9.1` | `-` | UNCHECKABLE | This AppImage is the SOURCE the running native backend was extracted from, not the thing that runs. The service execs ~/Applications/meshchatx-native/ |
| `mcp` | executable | `unknown` | `-` | UNCHECKABLE | BROKEN as installed. Running it reports "typer is required". Recorded so the fault is visible rather than silently counted as working. |
| `nPerf.AppImage` | AppImage | `not in filename` | `-` | UNCHECKABLE | Provenance UNKNOWN. This is a finding: nothing records where it came from. |
| `pCloud.AppImage` | AppImage | `not in filename` | `-` | UNCHECKABLE |  |
| `bun` | executable | `1.4.2` | `bun-v1.4.2` | CURRENT |  |
| `google-chrome` | executable | `154.0.8037.92` | `154.0.8037.92-1` | CURRENT |  |

## What this deliberately does not do

- **It does not update anything.** BEHIND is a finding for a human, not a task.
- **It does not chase UNCHECKABLE items with downloads.** The AppImages with no version in the filename would need a vendor page parsed; that is a deliberate gap, recorded so its absence is visible.
- **It does not track Obsidian or Crossover.** The operator keeps track of those personally.

