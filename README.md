# ALWAYS ON

Compartmentalized, on-premises platform for drone telemetry/communications,
photogrammetry/mapping, vehicle and fabrication simulation, static public
sales content, hosted payment processing, Mastodon-based customer support,
LM Studio/OpenClaw AI assistance, and Corda-backed provenance, receipts,
entitlement, and data-integrity records; with encrypted pCloud archival
replication and controlled IPFS artifact distribution.

## Domains (strict isolation — §1.3)

| Podman network | Purpose | Public exposure | Permitted output |
|---|---|---|---|
| `ao-sales` | Sales API, sales PostgreSQL, Mastodon adapter, OpenClaw, LM Studio | No direct host exposure by default | Signed order/receipt/entitlement manifests |
| `ao-payment` | Provider webhook verifier, payment adapter | No | Verified payment state only |
| `ao-field` | Heltec gateway, RNS/MeshChatX, telemetry spool, mission-release service | No | Signed telemetry and mission manifests |
| `ao-mapping` | WebODM, NodeODM, Redis, mapping DB, imagery intake/exporter | VPN/operator only if required | Signed mapping-deliverable manifests |
| `ao-sim-vehicle` | ROS 2, Gazebo, ArduPilot SITL, MAVLink, QGroundControl sim | No | Signed vehicle-simulation manifests |
| `ao-sim-fabrication` | ROS 2, Gazebo, robot-arm cells, 3D printer, LPBF, facility model | No | Signed fabrication-simulation manifests |
| `ao-ledger-ingest` | Mutual TLS validation gateway, authorization, audit | No | Corda receipt IDs/statuses |
| `ao-ledger-core` | Corda node, Corda PostgreSQL, certificate/keystore material | No | None directly |
| `ao-data` | Shared data plumbing (narrow) | No | Controlled references only |
| `ao-admin` | Monitoring/backups — VPN or allowlisted only | VPN/allowlist only | Operational reports |

**All networks are `Internal=true`.** CIDRs recorded in
`config/platform/network-cidrs.yaml`.

### Prohibited cross-domain paths (§1.3)

Sales/AI never reaches MAVLink, ArduPilot, ROS, Gazebo, LoRa, RNS, MeshChatX,
WebODM workers, raw imagery, or Corda core. Payment never reaches OpenClaw,
LM Studio, Mastodon, field, mapping, or simulation services. Simulation never
touches live machinery, sales, payments, or Corda core. Public internet never
reaches PostgreSQL, Redis, WebODM workers, LM Studio, Corda, ROS, MAVLink,
Gazebo, QGroundControl, RNS, or MeshChatX.

### Approved data paths (§1.3)

Sales/Payment/Field/Mapping/Simulation event manifests → ledger-ingestion
gateway → Corda transaction → receipt/entitlement/provenance state. All
cross-domain requests require mutual TLS, signed payloads, schema validation,
timestamp, nonce, idempotency key, and audit record.

## Layout (§3.1)

```
/ALWAYSON/
├── README.md
├── VERSION
├── docs/
│   ├── adr/
│   ├── architecture/
│   ├── runbooks/
│   └── compliance/
├── storefront/
│   ├── source/
│   ├── build/
│   ├── releases/
│   ├── manifests/
│   └── pcloud-public-folder/
├── quadlet/
│   ├── networks/
│   ├── volumes/
│   ├── sales/
│   ├── payment/
│   ├── field/
│   ├── mapping/
│   ├── sim-vehicle/
│   ├── sim-fabrication/
│   ├── ledger/
│   └── operations/
├── config/
│   ├── platform/
│   ├── storefront/
│   ├── sales/
│   ├── payment/
│   ├── drone/
│   ├── field/
│   ├── mapping/
│   ├── sim-vehicle/
│   ├── sim-fabrication/
│   ├── ledger/
│   ├── pcloud/
│   └── ipfs/
├── secrets/          # NEVER committed
├── data/
├── artifacts/
├── ipfs/
├── pcloud/
├── backups/
├── logs/
├── scripts/
├── tests/
└── tmp/
```

## Key rules (§2.1, §4)

- Podman + Quadlet only. No Docker daemon, no Docker Compose, no Watchtower.
- No public ports without explicit operator approval.
- Pinned image digests for operational services.
- Photogrammetry drive verified before any mapping operation (§2.3/§3.5).
- Secrets never enter Git, logs, HTML, pCloud Public Folder, or IPFS.
- Rootless Quadlet files live in `~/.config/containers/systemd/`. System-level
  services are used only where host hardware requires it.

## Host facts (§1.1, §2.2)

| Area | Specification |
|---|---|
| Host OS | Kubuntu 26 LTS-class workstation (Ubuntu 26.04 LTS, standard support to April 2031) |
| CPU/GPU | AMD CPU + EVGA NVIDIA GTX 1080 |
| Container engine | Podman only |
| Container lifecycle | systemd Quadlet |
| Container runtime | rootless (user `alwayson-mapping`, `alwayson-sales`, `alwayson-ledger`, etc.) |
| Public website | Static HTML in pCloud Public Folder |
| Payments | Hosted checkout, provider-verified webhooks, no local card handling |
| Sales/customer support | Sales API, PostgreSQL, Mastodon integration, OpenClaw, LM Studio |
| Drone compute | Raspberry Pi 5 + Waveshare SX1262 LoRa top-hat |
| Drone AUTOPILOT MODULE | 3DR N1 CONNECTED TO RPI5 VIA MAVLINK |
| Desktop radio | Heltec WiFi LoRa 32 V3 via USB serial |
| Field protocol | RNS/Reticulum + MeshChatX over raw LoRa (not LoRaWAN unless true gateway/network-server architecture is selected) |
| Mapping | WebODM + NodeODM under Podman |
| Mapping storage | `/media/scottw/500GBPHOTOGRAM/` (UUID `498597d4-9fc8-42cf-8db7-4e71ede53267`) |
| Vehicle simulation | ROS 2 Jazzy, Gazebo Harmonic, ArduPilot SITL, MAVLink, QGroundControl |
| Fabrication simulation | ROS 2 Jazzy, Gazebo Harmonic, robot arms, 3D printer, LPBF, kitchen/facility model |
| Ledger | Corda core behind ledger-ingestion gateway |
| Archive | Local source data, signed manifests, encrypted pCloud replication, private/encrypted IPFS workflow |
| Monitoring | Prometheus-compatible metrics, alerts, systemd/Podman health checks, VPN-only admin access |
| Backup | PostgreSQL/Corda-aware backups, restic encrypted backup, scheduled restore testing |

## Simulation configuration (§1.8, §3.7)

### Vehicle simulation

```
Network:      ao-sim-vehicle
ROS_DOMAIN_ID: 21
GZ_PARTITION: alwayson_vehicle_sim
Data:         /ALWAYSON/data/sim-vehicle/
Exports:      /ALWAYSON/data/sim-vehicle/exports/
```

### Fabrication simulation

```
Network:      ao-sim-fabrication
ROS_DOMAIN_ID: 22
GZ_PARTITION: alwayson_fabrication_sim
Data:         /ALWAYSON/data/sim-fabrication/
Exports:      /ALWAYSON/data/sim-fabrication/exports/
```

Vehicle and fabrication simulations have separate Podman networks, ROS Domain
IDs, Gazebo partitions, service identities, filesystem mounts, result
directories, and ledger client certificates. Use Git for SDF/URDF/world files;
Git LFS or separate artifact repository for large meshes, textures, point
clouds, and generated results.

## Field & LoRa (§1.7)

### Drone-side

ArduPilot → MAVLink → Raspberry Pi 5 (MAVLink collector, RNS/MeshChatX,
Waveshare SX1262 LoRa HAT).

### Desktop gateway

Heltec WiFi LoRa 32 V3 (ESP32-S3 + SX1262) via USB-C serial
(`/dev/serial/by-id/...`).

### Configuration profiles

`/ALWAYSON/config/field/heltec-v3/radio-profile-us915.yaml`
`/ALWAYSON/config/drone/waveshare-lora/radio-profile-us915.yaml`

Both profiles define identical or interoperable: frequency/channel plan,
bandwidth, spreading factor, coding rate, preamble length, TX power, sync word,
packet framing, max packet size, encryption key ID, device public identity,
sequence-number/replay policy, ACK policy, retry/backoff, airtime limits.

## Ledger flow (§1.9)

Domain event/artifact → SHA-256 content hash → signed manifest →
ledger-ingestion gateway (mutual TLS, authorization, schema validation,
signature verification, idempotency, audit) → Corda transaction → receipt/
entitlement/provenance state.

Corda transaction object types: sales orders, telemetry batches, map products,
simulation results, and release artifacts. Corda never stores card data, full
customer PII, raw telemetry, drone images, GeoTIFFs/point clouds, ROS bags,
large simulation outputs, sensitive LLM data, or private keys. CORDA MANAGES SALES OF DIGITAL DATA, NOT 
SALES OF PHYSICAL ITEMS LIKE BUILDINGS OR PRODUCTS.

## Photogrammetry drive (§1.5, §3.5)

Drive `/media/scottw/500GBPHOTOGRAM/` (ext4, UUID `498597d4-9fc8-42cf-8db7-4e71ede53267`)
is the authoritative workspace for imagery intake, WebODM media, NodeODM
intermediates, deliverables, manifests, and archive staging. Validation
required before WebODM starts — mount presence, UUID match, `.mounted-ok`
marker, and free-space threshold. Directory tree created per §2.3.

## Backup & archive (§4.4, §4.5)

| Schedule | Content |
|---|---|
| Hourly | PostgreSQL/Corda-aware dumps |
| Daily | Mapping manifests, simulation exports, storefront releases |
| Weekly | Repository integrity check + off-host copy validation |
| Monthly | Isolated restore test |
| Quarterly | Full disaster-recovery exercise |

Restore testing: isolated environment → database integrity → hash
recalculation → manifest comparison → Corda receipt verification → operator/
source/timestamp recording → alert on failure.

## Status

See `VERSION`, `git log`, and `docs/compliance/installation-status.md`.

## Current status (as of 2026-08-25)

| §5 item | Description | Status |
|---|---|---|
| 1 | Host inventory report | ✅ Done |
| 2 | Photogrammetry-drive report | ✅ Done (UUID verified, dir tree created) |
| 3 | Installed package/version matrix | ✅ Done |
| 4 | Podman rootless + Quadlet | ✅ Done (rootless OK, 10 internal networks) |
| 5 | GPU driver/runtime validation | ✅ Done (driver verified; CPU-only baseline proven; GPU enabled) |
| 6 | Podman network list + isolation | ✅ Done (all Internal=true; isolation test passes) |
| 7 | Firewall & listening-port report | ✅ Done (ufw active; :80/:1716 cleared) |
| 8 | WebODM smoke test | ✅ Done (apt-76, 76 images, GPU-enabled, ortho produced) |
| 9 | Vehicle simulation smoke test | ✅ Done (headless Gazebo 300 iterations, ROS↔GZ bridge) |
| 10 | Fabrication simulation smoke test | ✅ Done (headless Gazebo 300 iterations, bridge) |
| 11 | Heltec detection + LoRa link test | ⏸️ Deferred (Heltec V3 not connected) |
| 12 | Ledger-ingest + Corda receipt | ⏸️ Corda 5.2.2 scaffolded; node deployment awaits operator key ceremony |
| 13 | Sales receipt-manifest test | ⚠️ DB deployed (14 tables, 3 roles); payment/Mastodon/sales API pending |
| 14 | Backup execution | ✅ Done (restic snapshot `548d9910`, encrypted) |
| 15 | Isolated restore test | ✅ Done (file hash OK; DB 14/14 tables restored) |
| 16 | Blockers/deviations/risks | ✅ Maintained in installation-status.md |

### Outstanding items
- Sales/payment/Mastodon: need payment-provider selection, pCloud credentials,
  Mastodon OAuth, and sales API implementation
- Ledger: Corda node requires operator key/cert ceremony (§7 of runbook)
- Field domain: Heltec V3 deferred pending physical connection
- Backups: pCloud off-host replication pending credential provisioning
