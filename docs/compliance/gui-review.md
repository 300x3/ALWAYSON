# WORK 000020 — GUI Operator-Workflow Review

Date: 2026-08-28 · Objective: README §19 WORK 000020 — for each GUI: named
operator purpose, access boundary, startup/health/shutdown, data source, and
no unauthorized cross-domain access.

## Review matrix

| GUI | Purpose | Access boundary | Startup | Health check | Shutdown | Data source | Status / gaps |
|---|---|---|---|---|---|---|---|
| **WebODM** (browser) | Mapping task management: upload imagery, process, view orthophotos | `ao-mapping` only; access via localhost port forward or operator desktop; no public listener | Quadlet `ao-mapping` units; open forwarded URL in browser | HTTP health of web container; task queue depth | `systemctl --user stop` on mapping units | Photogrammetry drive; mapping DB | **Gap:** no documented operator port-forward/URL procedure; add runbook |
| **QGroundControl** | Drone/SITL planning, vehicle setup, mission upload | Local desktop app; connects to SITL (sim) or field link only | Desktop entry present (`qgroundcontrol.desktop`); `~/bin` wrapper check | UDP link status to SITL/gateway; app link indicator | Quit app; stop SITL | Vehicle sim / field gateway | **Gap:** no documented sim-profile (host/ports for ArduPilot SITL); profiles not saved |
| **Gazebo** (`gz sim`) | Vehicle + fabrication simulation visualization | Local desktop; `ao-sim-*` data only | `/opt/ros/lyrical/.../gz sim <world>` headless-vs-GUI documented in sim runbooks | Scene load + `gz topic -l`/bridge topics present | Close GUI; sim units keep headless run | ROS 2 Lyrical / Gazebo 10.5 sim data paths | OK; deviation 18.1 recorded. **Gap:** document which worlds are approved for visualization |
| **Tokodon** | Operator Mastodon client for the federated 300x3.com instance | Public origin (`https://300x3.com` via approved tunnel edge); no other public exposure | `/usr/bin/tokodon` → Add Account `https://300x3.com` | Account panel shows connected admin | Quit; instance stack shuts down separately | Mastodon web API at the public origin | **Done (edge):** WORK 000060 tunnel live; **Pending:** apex DNS cutover before first GUI login |
| **LM Studio** | Load/approve local LLM; expose local OpenAI-compatible endpoint | Local desktop + loopback :1234 only; no LAN binding | Desktop app (`lmstudio.desktop`) | `curl http://127.0.0.1:1234/v1/models` | Quit app (endpoint drops) | `~/.lmstudio/models` | **Gap:** confirm server binds 127.0.0.1 (not 0.0.0.0) before use |
| **OpenClaw** (CLI/daemon) | Bot support conversations, draft responses | Local config `~/.openclaw`; talks to Mastodon origin `https://300x3.com` + LM Studio :1234 only | `openclaw` from `~/.npm-global/bin` (not on default PATH — **gap**) | `openclaw` status/logs under `~/.openclaw/logs` | Stop daemon/process | Mastodon DMs (`bot@300x3.com`), LM Studio | **Gap:** add to PATH or desktop launcher; bot handle updated 2026-09-22 (`bot`); confirm no outbound posting config beyond approved host |
| **Sales/support admin** | Order, receipt, and support handling | `ao-sales` domain; loopback admin route; no public listener | Pending payment-domain implementation (§18.4) | n/a until implemented | n/a | Sales PostgreSQL | **Not implemented** — blocked on payment verifier |
| **Monitoring dashboard** | Host/Podman/mapping/field/sales/ledger metrics | `ao-admin`; VPN/allowlisted admin access only | Not yet implemented (README §17.2 requirement) | n/a | n/a | Per §17.2 metric table | **Not implemented** — largest GUI gap; recommend minimal cockpit/node-exporter stack in `ao-admin` before other dashboards |
| **Backup/restore status display** | Backup last-success, repo health, restore-test result | `ao-admin` only | Not implemented; restic runs via `scripts/backup` | `scripts/backup` summary / journal | n/a | restic repo | **Gap:** wrap existing restic + restore-test logs into a status report script (no GUI needed initially) |
| **Field gateway display** | Link quality: RSSI/SNR, packet rate, spool depth | `ao-field` only | Blocked — Heltec V3 not connected (§18.3 blocker) | n/a | n/a | Raw packet store | **Blocked on hardware** |

## Summary

- **Usable now (2):** Gazebo visualization, LM Studio (after server bind check).
- **Usable after WORK 000010 operator session (3):** Tokodon, OpenClaw, WebODM
  (needs documented access procedure).
- **Configured but undocumented (1):** QGroundControl sim profile.
- **Not implemented (3):** monitoring dashboard, backup status display, sales admin.
- **Blocked on hardware (1):** field gateway display.

## Recommended next actions

1. Document WebODM operator access (port-forward command + URL) in a mapping runbook.
2. Save and document a QGroundControl SITL connection profile.
3. Verify LM Studio server binds loopback only; add to the mastodon-validation checklist.
4. Add `~/.npm-global/bin` to PATH or create an OpenClaw launcher; audit its
   config for outbound posting before enabling.
5. Implement the minimal monitoring stack (§17.2) in `ao-admin`; start with
   host + Podman + backup metrics, then add domain-specific panels.
