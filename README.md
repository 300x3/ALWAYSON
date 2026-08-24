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

## Mapping domain service account (autonomous operation)

WebODM runs under the dedicated **`alwayson-mapping`** system account
(uid 997), created 2026-08-24 by operator decision:

- Rootless Podman with subordinate UID range `165536-196607`
- Linger enabled → services run autonomously at boot, no login required
- Owns the photogrammetry working directories per §3.5 writers model:
  `incoming/ validated/ rejected/ webodm/ deliverables/ manifests/ exports/ backups/ tmp/`
- Secrets in `/home/alwayson-mapping/secrets/webodm.env` (0600, outside Git)
- Quadlet units: `/ALWAYSON/quadlet/mapping/` → deployed to
  `/home/alwayson-mapping/.config/containers/systemd/mapping/`
- All images pinned by digest; stack = db + broker(redis) + webapp + worker +
  nodeodm on the internal-only `ao-mapping` network

### Autonomous processing flow

When imagery lands in `incoming/drone|operator` and the operator authorizes a
job (via WebODM API over SSH tunnel — there is deliberately no public port):

1. `scripts/mapping/intake-imagery.sh` validates type/checksums/quota → `validated/`
2. `scripts/mapping/submit-webodm-task.sh` creates the WebODM task with profile
   from `config/mapping/processing-profiles/`
3. Worker processes to **orthomosaic / point cloud** outputs into `webodm/media`
4. `scripts/mapping/export-mapping-manifest.sh` hashes outputs, writes signed
   manifest to `manifests/`, stages archives in `exports/`

Operator access without exposing ports:
`ssh -L 8000:webapp.ao-mapping:8000 scottw@<host>` then browse localhost:8000.
(Actual tunnel target is the podman user socket of `alwayson-mapping`; see
docs/runbooks/mapping-access.md for the exact command.)

## Status

See `VERSION`, `git log`, and `docs/compliance/installation-status.md`.

