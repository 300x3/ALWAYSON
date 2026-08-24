# ALWAYS ON

Compartmentalized, on-premises platform per the Final Architecture report
(`/home/scottw/Desktop/WOW2/WOW2.txt`).

## Domains (strict isolation — Section 1.3)

| Podman network | Purpose |
|---|---|
| `ao-sales` | Sales API, sales PostgreSQL |
| `ao-payment` | Webhook verifier, payment adapter |
| `ao-field` | Heltec gateway, RNS/MeshChatX, telemetry spool |
| `ao-mapping` | WebODM/NodeODM/Redis/mapping DB |
| `ao-sim-vehicle` | ROS 2 + Gazebo + ArduPilot SITL (DOMAIN_ID=21) |
| `ao-sim-fabrication` | ROS 2 + Gazebo facility sim (DOMAIN_ID=22) |
| `ao-ledger-ingest` | mTLS validation gateway |
| `ao-ledger-core` | Corda node + DB (no direct output) |
| `ao-data` | Shared data plumbing (narrow) |
| `ao-admin` | Monitoring/backups - VPN or allowlisted only |

All networks are `Internal=true`. See `config/platform/network-cidrs.yaml`.

## Layout

- `quadlet/` - source-controlled Quadlet definitions; deploy with
  `scripts/deploy/deploy-quadlet-domain.sh <domain>` into `~/.config/containers/systemd/`.
- `config/` - versioned configuration and policies (Section 4.3).
- `secrets/` - NEVER committed. Podman secrets / file-based only.
- `scripts/` - bootstrap/deploy/validation/domain tooling (Section 4.1).
- `artifacts/` - signed manifests and releases.
- `logs/installation/agent-install.log` - full installation journal.

## Key rules

- Podman + Quadlet only. No Docker daemon, no Watchtower.
- No public ports without explicit operator approval.
- Pinned image digests for operational services.
- Verify the photogrammetry drive before any mapping operation.
- Secrets never enter Git, logs, HTML, scripts, pCloud Public Folder, or IPFS.

## Photogrammetry drive

UUID `498597d4-9fc8-42cf-8db7-4e71ede53267`, mounted at `/media/scottw/500GBPHOTOGRAM`,
validated by `scripts/validation/check-photogrammetry-mount.sh`.

## Status

See `VERSION` and `git log`. Open blockers are tracked in the installation journal.
