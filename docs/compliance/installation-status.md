# ALWAYS ON — Installation Status Report (Section 5)

Date: 2026-08-24 · Operator host: Kubuntu/Ubuntu 26.04 LTS workstation

## Completed deliverables

| # | Section 5 item | Status |
|---|---|---|
| 1 | Host inventory report | ✅ `logs/installation/agent-install.log` |
| 2 | Photogrammetry-drive report | ✅ /dev/sdb1 ext4 UUID 498597d4-9fc8-42cf-8db7-4e71ede53267, 435G free, dir tree + .mounted-ok created, validation script passes |
| 3 | Installed package/version matrix | ✅ `config/platform/version-matrix.yaml` (systemd 259, podman 5.7.0, NVIDIA 580.173.02) |
| 4 | Podman rootless + Quadlet verification | ✅ rootless OK, cgroups v2, linger enabled, 10 networks Internal=true |
| 5 | GPU driver/container-runtime report | ✅ driver working; container GPU toolkit NOT installed (correct per §2.8 step 12) |
| 6 | Podman network list + isolation test | ✅ `config/platform/network-cidrs.yaml`; check-network-isolation.sh PASS |
| 7 | Firewall/listening-port report | ⚠️ ufw active; check-open-ports.sh FAILS by design on unapproved :80/:1716 (see blockers) |
| 8–15 | WebODM/sim/Heltec/ledger/sales/backup/restore smoke tests | ⏸️ blocked below |

## Blockers requiring operator approval (Section 2.2 pause rules)

1. ~~nginx on :80~~ — RESOLVED: stopped and disabled at operator direction; port 80 clear.
   keep+allowlist, repurpose as ALWAYS ON ingress, or stop.
2. **KDE Connect on *:1716** — allowlist or disable.
3. **Existing PostgreSQL 18 cluster + Redis** on host loopback — reuse for domains vs.
   containerize per plan. Document mandates domain-scoped instances.
4. **ROS "lyrical" + Gazebo 10.5 installed** vs spec Jazzy + Harmonic — accept deviation
   or install Jazzy/Harmonic alongside.
5. **WebODM image digests** — no pinned digests approved yet (§3.3 template uses placeholder).
6. **Corda version/cert profile undecided** — ledger-core deployment cannot start.
7. **Secrets provisioning** — restic.env, pCloud archive credential, payment webhook secret,
   Mastodon OAuth, field radio keys (§3.4 table).
8. **Heltec V3 not connected** — no /dev/serial/by-id entries.
9. **Photogrammetry drive ownership model** — service-account review pending (§2.3 note);
   world-permissions removed, scottw-owned interim.

## Deviations recorded

- `check-photogrammetry-mount.sh`: hardened UUID extraction for systemd-autofs stacked mount.
- `ao-bootstrap-privileged.sh` added beyond §4.1 list (installation journaling requirement).
