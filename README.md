![ALWAYS ON — WEBSITEMAIN](assets/WEBSITEMAIN.png)

# ALWAYS ON

**License:** CC BY-NC-SA  
**Project origin:** Building ~2010 · Drone ~2012 · Linux systems ~2023  
**Supporting project plan:** https://archive.org/details/@scott_widmann  
**Current project website:** https://www.300x3.com
**CREATED WITH:** BLUEBEAM AND LIBREDRAW (PDF PROJECT PLAN), WWW.PERPLEXITY.AI, WWW.CLINE.BOT
**BE WARNED:** EVERYTHING HERE IS DIFFICULT UNTIL ITS EASY, THESE TOOLS ARE ALL SHARP AND DANGEROUS AND IF YOU DISRESPECT THEM THEY WILL CAN/WILL HARM YOU. THE SAME AS ANY TRIP/FALL OR CAR RIDE. PERHAPS NOT AS BAD, PERHAPS WORSE? IMHO - IGNORING THEM IS MORE DANGEROUS THAN UNDERSTANDING THEM.

---

**Architecture, Installation, Configuration, Operations, and Status**

## Document Status and Reading Guide

This README is the single authoritative document for the ALWAYS ON project. It
contains the intended architecture, implemented configuration, operational
requirements, validation evidence, approved deviations, known issues, and work
queue.

Every material statement in this document belongs to one of the following
categories:

| Category | Meaning |
|---|---|
| **Architecture requirement** | Mandatory final-state design constraint |
| **Implemented** | Verified as deployed or tested on the current host |
| **Planned** | Approved design not yet implemented |
| **Blocked** | Requires an operator decision, credential, key ceremony, hardware connection, or other prerequisite |
| **Deviation** | Approved difference between intended architecture and current implementation |
| **Work item** | A discrete task with acceptance criteria |
| **Issue** | A recorded defect, ambiguity, or implementation risk |

When the current implementation differs from an architecture requirement, the
difference must be recorded in **Approved Deviations and Open Decisions** with
a rationale, compensating controls, owner, and resolution condition.

**Last consolidated review:** 2026-08-31

---

# 1. System Purpose

ALWAYS ON is a compartmentalized, on-premises platform supporting an automated
approximately 160-square-foot modular live/fabricate facility and an
accompanying modular micro-aircraft carrier. Both of which grow to generally any
size / quantity.

The platform supports:

- Drone telemetry and field communications.
- Photogrammetry and mapping.
- Vehicle simulation.
- Fabrication, facility, inventory, kitchen, and logistics simulation.
- Static public sales content.
- Hosted payment checkout and receipt generation.
- Mastodon-based customer and community follow-up.
- Local LM Studio and OpenClaw-assisted support workflows.
- Corda-backed provenance, receipts, entitlements, and approved state records.
- Encrypted pCloud archival replication and controlled IPFS artifact
  distribution.

The system is designed around **strict isolation**. Sales, AI, payments,
mapping, field telemetry, vehicle simulation, fabrication simulation, archive,
and ledger services must not share broad networks, credentials, writable
storage, databases, or unrestricted host access.

The current workstation is a development, integration, and validation host. It
uses Kubuntu 26.04 LTS software, an AMD CPU, and an EVGA NVIDIA GTX 1080.
Future compute-intensive production workloads may move to an immersion-cooled
server rack and a Raspberry Pi edge-computing cluster.

Kubuntu is appropriate for the current workstation role because KDE supports
QGroundControl, Gazebo visualization, GPU diagnostics, Tokodon, and general
engineering workflows while retaining an Ubuntu LTS package base. Ubuntu 26.04
LTS standard support is scheduled through April 2031.

Podman is the only supported container runtime. Containers are managed through
systemd Quadlet definitions rather than Docker Compose, shell-wrapper
orchestration, or a Docker daemon.

---

# 2. Platform Baseline

## 2.1 Intended Platform Standard

| Area | Architecture requirement |
|---|---|
| Host OS | Kubuntu 26.04 LTS workstation |
| Current CPU/GPU | AMD CPU and EVGA NVIDIA GTX 1080 |
| Future compute | Immersion-cooled server rack and Raspberry Pi edge cluster |
| Container engine | Podman only |
| Container lifecycle | systemd and Podman Quadlet |
| Public website | Static HTML in pCloud Public Folder |
| Payments | Provider-hosted checkout and verified payment events; no local card handling; local stablecoin processing |
| Sales and support | Sales API, PostgreSQL, Mastodon integration, OpenClaw, and LM Studio |
| Drone compute | Raspberry Pi 5 with Waveshare SX1262-class LoRa top-hat |
| Drone autopilot | 3DR N1 connected to Raspberry Pi 5 by MAVLink |
| Desktop radio | Heltec WiFi LoRa 32 V3 through stable USB serial path |
| Field protocol | RNS/Reticulum and MeshChatX over raw LoRa unless a true LoRaWAN deployment is selected |
| Mapping | WebODM and supporting services under Podman |
| Mapping storage | `/media/scottw/500GBPHOTOGRAM/` |
| Vehicle simulation | ROS 2 Lyrical, Gazebo Sim 10.5.0, ArduPilot SITL, MAVLink, QGroundControl |
| Fabrication simulation | ROS 2 Lyrical, Gazebo Sim 10.5.0, robot cells, additive manufacturing, storage, kitchen, and logistics models |
| Ledger | Corda core behind a dedicated ledger-ingestion gateway |
| Archive | Local source data, signed manifests, encrypted pCloud replication, private or encrypted IPFS workflow |
| Monitoring | Prometheus-compatible metrics, alerts, health checks, and protected administration access |
| Backup | PostgreSQL/Corda-aware backup, restic or equivalent encrypted backup, and scheduled restore testing |

## 2.2 Current Host Facts

| Area | Verified current value |
|---|---|
| Kernel | `7.0.0-34-generic` |
| Podman | `5.7.0` |
| Podman networks | Ten `ao-*` networks present; internal workload-domain isolation verified |
| GPU | EVGA NVIDIA GTX 1080 |
| NVIDIA driver | `580.178.04` |
| NVIDIA integration | CDI devices registered, including `nvidia.com/gpu=0` |
| Simulation stack | ROS 2 Lyrical at `/opt/ros/lyrical`; Gazebo Sim `10.5.0` |
| Host PostgreSQL | PostgreSQL `18.6`, loopback-only |
| Host Redis | Redis `8.0.5`, loopback-only |
| Mapping drive | ext4 `/dev/sdb1`; UUID verified; approximately 433.9 GB free of 457 GB |
| Mapping mount | `/media/scottw/500GBPHOTOGRAM/` |
| Current runtime model | Mixed rootless and system/rootful Podman evidence; see approved deviation section |
| Desktop OS | Ubuntu 26.04.1 LTS (`resolute`) userland with the Kubuntu desktop |
| Reticulum executable | Standalone RNS `1.4.2` available at `/home/scottw/.local/bin/rnsd`; no standalone `rnsd` process was running during the 2026-09-24 review |
| Active Reticulum runtime | Embedded in the MeshChatX native backend and initialized from `/home/scottw/.reticulum/config` |
| MeshChatX deployment | Native headless backend at `/home/scottw/Applications/meshchatx-native/ReticulumMeshChatX` |
| MeshChatX version evidence | Desktop metadata declares `4.9.1`; the running backend version was not independently established during the review |
| MeshChatX executable verification | SHA-256 `4f403e52b0a5722a49d433f23660b14b43a779fb3cc9a5a90b8f150d77f18890` matches `backend-manifest.json` |
| MeshChatX repository artifact | `reticulum_meshchatx-4.8.4-py3-none-any.whl`; stored in the MeshChatX repository-server identity and not the verified running artifact |
| MeshChatX Reticulum config | `/home/scottw/.reticulum/` |
| MeshChatX state and logs | `/home/scottw/.reticulum-meshchatx/` |
| MeshChatX local UI | `127.0.0.1:18000` |
| Reticulum public gateway listener | `0.0.0.0:4242`; binding verified, while firewall policy and packet reachability remain unverified |

---

# 3. High-Level Architecture

## 3.1 Isolation Diagram

```text
                                  PUBLIC INTERNET
                                         │
                                         ▼
                    ┌─────────────────────────────────────┐
                    │ pCloud Public Folder                │
                    │ Static storefront only              │
                    │ Products - Docs - Legal - Links     │
                    └─────────┬───────────────┬───────────┘
                              │               │
                Hosted checkout               │ Community/support links
                              │               │
                              ▼               ▼
                 ┌────────────────────────────────────────┐
                 │ CONTROLLED INGRESS / EGRESS ADAPTERS    │
                 │ Payment ingress - Archive egress       │
                 │ Community egress - Build/update path   │
                 └───────────────┬────────────────────────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           ▼                     ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ PAYMENT DOMAIN   │  │ SALES / AI DOMAIN│  │ ARCHIVE ADAPTER  │
│ Webhook verifier │  │ Sales API         │  │ pCloud/IPFS      │
│ Normalizer       │  │ Sales PostgreSQL  │  │ encrypted export │
└────────┬─────────┘  │ Mastodon adapter  │  └──────────────────┘
         │            │ OpenClaw/LM Studio│
         │            └────────┬──────────┘
         │                     │ Signed receipt manifests
         ▼                     ▼
             ┌──────────────────────────────────────────┐
             │ LEDGER-INGEST DOMAIN                     │
             │ mTLS - authorization - schema validation │
             │ signatures - idempotency - audit         │
             └──────────────────┬───────────────────────┘
                                │
                                ▼
             ┌──────────────────────────────────────────┐
             │ LEDGER-CORE DOMAIN                       │
             │ Corda node - Corda database - PKI        │
             └──────────────────────────────────────────┘

Drone Pi 5 + Waveshare ─ LoRa ─ Heltec V3 ─► FIELD DOMAIN ─────┐
                                                               │
WebODM/imagery intake ─────────────────────► MAPPING DOMAIN ───┤
                                                               ├─ Signed manifests only
Vehicle ROS/Gazebo/SITL ───────────────────► VEHICLE SIM ──────┤
                                                               │
Fabrication ROS/Gazebo ────────────────────► FABRICATION SIM ──┘
                                                               ▼
                                                    LEDGER-INGEST
```

The public storefront has no direct route to the Kubuntu host’s field,
mapping, simulation, database, AI, Podman, or Corda-core services.

## 3.2 Canonical Implementation Status

| Domain or component | Architecture requirement | Current implementation state | Status | Blocking condition or next action |
|---|---|---|---|---|
| Host platform | Kubuntu, Podman, Quadlet, protected administration | Host inventory and base platform verified | Implemented | Maintain version matrix |
| Domain isolation | Separate workload networks with explicit approved paths | Ten internal workload networks and isolation test verified | Implemented | Add narrow adapters only as required |
| Mapping | Dedicated mapping domain and photogrammetry drive | GPU-enabled WebODM smoke test completed; orthophoto produced | Implemented with deviation | Formalize steady-state rootless/system model |
| Field, Reticulum, and LoRa | Raspberry Pi 5, Waveshare LoRa, Heltec V3 gateway, RNS/Reticulum, and MeshChatX | Both Heltec LoRa 32 V3/SX1262 RNodes are functional and initialized by MeshChatX; `PEOPLE-RADIO` uses 915 MHz/125 kHz and `DRONE-RADIO` uses 917 MHz/250 kHz; 32 interfaces are configured and none are explicitly disabled; RF feedback is observable on both radio bands and requires characterization; end-to-end telemetry, link-quality, and resilience acceptance tests remain pending | In progress | Measure and classify feedback on each band; record RSSI/SNR, noise floor, packet loss, airtime, retries, and cross-band isolation; complete RF telemetry and fail-safe validation |
| Vehicle simulation | Isolated ROS/Gazebo/ArduPilot SITL domain | Headless Gazebo and ROS-Gazebo bridge smoke test passed | Implemented | Add scenario and QGroundControl validation as needed |
| Fabrication simulation | Isolated ROS/Gazebo facility domain | Headless simulation smoke test passed | Implemented | Expand facility models and safety scenarios |
| Ledger | Corda core behind mTLS ingestion gateway | Corda 5.2.2 scaffolded | Blocked | Complete operator key and certificate ceremony |
| Sales and payment | Hosted payment flow and verified events | Sales DB deployed; payment provider and API pending | Planned | Select provider and implement verifier/API |
| Mastodon and OpenClaw | Restricted local support/community workflow | Local stack in progress; OAuth/client issues recorded | In progress | Complete Tokodon and local LLM validation |
| Archive | Encrypted off-host replication and controlled IPFS workflow | Local restic backup and restore validation complete | Partially implemented | Provision pCloud/archive credentials and test replication |
| Backup and restore | Encrypted backup plus recurring restore testing | Encrypted restic snapshot and isolated restore test complete; recurring schedule automated 2026-08-31 (nightly restic 03:30, nightly DB dumps 03:00, weekly verify) | Implemented | Schedule recurring restore tests |


## 3.3 DATABASES AND DATA STORES

PostgreSQL 18 is the system-wide relational database platform. The target is one
host-managed PostgreSQL installation with separate logical databases and separate
application roles. During the current migration, some applications still run
container-scoped PostgreSQL instances; those are current-state implementations,
not the permanent architecture. The database name and role boundary remain
unchanged.

Target logical databases:

```text
salesdb       # Authoritative sales/payment records
mastodon      # Mastodon application state
webodm        # WebODM/PostGIS mapping data
grafana       # Grafana application metadata, users, dashboards, datasources
metabase      # Metabase application metadata, users, questions, dashboards
cordadb       # Corda persistence when the ledger node is activated
postgres      # Administrative/maintenance database
```

Grafana and Metabase each use PostgreSQL for their own application state. They
are not treated as disposable dashboards. Their application databases require
backups, restore testing, migrations, and health checks.

Grafana uses Prometheus as its operational metrics datasource and may use approved
PostgreSQL datasources for business or database reporting. Metabase uses
PostgreSQL source databases through dedicated read-only roles and approved views
or projections.

Redis is a low-latency speed and coordination layer, not the authoritative
system of record. It is used for caching, queues, locks, task brokering, and
transient operational coordination. Important business, payment, user, dashboard,
and application metadata remain in PostgreSQL.

Prometheus TSDB remains separate as the specialized time-series store for
metrics. It is not replaced by PostgreSQL, Grafana, or Metabase.

SQLite and H2 are not approved application databases for Grafana or Metabase.
They may exist only in unrelated desktop/browser applications where embedded
storage is required, or in retained migration backups.


## Database/ledger authority and status legend

- **AUTHORITATIVE RELATIONAL:** PostgreSQL owns detailed operational data,
  searchable business records, and reporting projections.
- **AUTHORITATIVE LEDGER:** Corda owns final sale/contract, receipt association,
  entitlement, and approved ledger state transitions.
- **ACTIVE:** Currently running and verified.
- **CURRENT MIGRATION STATE:** Container-scoped PostgreSQL may still exist for an
  application while its data is being consolidated into the host PostgreSQL
  platform.
- **TARGET:** Documented end-state architecture, not yet fully deployed.
- **BLOCKED:** Requires an operator key/certificate, credential, service, or
  acceptance step.

Do not treat a **TARGET**, **CURRENT MIGRATION STATE**, or **BLOCKED** component as
active production state.

### 3.3.1 Program-to-Database Map

The following table groups the currently identified programs by the database
software they use. It is the starting point for discussing reporting and data
integration; it is not a list of every installed package or desktop settings
module.

| Database software | Software/program | Database name or store | Current role and reporting value |
|---|---|---|---|
| **PostgreSQL 18** | Host PostgreSQL service | Host cluster; `grafana`; `metabase`; `postgres` | Shared relational platform and administrative/maintenance cluster |
| **PostgreSQL 18** | Grafana | `grafana` | Grafana users, dashboards, folders, datasource definitions, preferences, and alert state |
| **PostgreSQL 18** | Metabase | `metabase` | Metabase users, collections, questions, dashboards, database connections, and settings |
| **PostgreSQL 18** | Mastodon web/Sidekiq | `mastodon` in `mastodon-db` | Accounts, posts, media metadata, federation state, and background-job application data |
| **PostgreSQL/PostGIS** | WebODM web/worker | `webodm` or `webodm_dev` in `db` | Mapping projects, processing state, users, and geospatial data |
| **PostgreSQL/PostGIS** | NodeODM | WebODM PostgreSQL plus filesystem processing data | Processing-node state and coordination; large image/output artifacts remain filesystem data |
| **PostgreSQL 18** | Sales database service | `salesdb` in `sales-db` | Target source for customers, orders, products, payments, receipts, entitlements, and audit history. The repository schema is defined; the live `salesdb` application schema still requires explicit initialization. |
| **PostgreSQL 18** | Corda node, when activated | `cordadb` | Intended Corda persistence; not currently active and requires the key/certificate ceremony |
| **Redis 8** | Host Redis service | Host Redis database 0 | General low-latency cache/coordination layer; no current application data confirmed |
| **Redis 8** | Mastodon cache/queue service | `mastodon-redis` database 0 | Cache, queues, and background-job coordination; not authoritative business data |
| **Redis 8** | WebODM broker | `broker` database 0 | Celery/task broker and worker coordination; not authoritative mapping data |
| **Prometheus TSDB** | Prometheus | `/prometheus` persistent volume | Time-series metrics, service health, resource usage, and operational monitoring |
| **Prometheus TSDB** | Grafana metrics datasource | Prometheus at `ao-prometheus:9090` | Grafana visualizes metrics; Prometheus remains the separate metrics store |
| **SQLite** | Akonadi/KDE PIM applications | Akonadi SQLite data | Contacts, calendars, mail indexes, and local personal-information data |
| **SQLite** | Firefox, Brave, Chrome, and Edge | Browser profile SQLite stores | Browser history, site storage, caches, certificates, and profile data |
| **SQLite** | Podman | Rootless container metadata store | Container, image, network, and volume metadata; not application data |
| **SQLite** | Selected ROS/local tools | Application-specific local SQLite files | Local tool state where enabled; not a shared reporting source |
| **Filesystem/local metadata** | LM Studio, OpenClaw, MeshChatX, QGroundControl, ArduPilot, Gazebo, and simulation tools | Application files, logs, project files, and local state | Operational or engineering data that is not automatically part of SQL reporting |
| **H2** | Grafana/Metabase legacy migration data | Retained H2 backup files only | No longer active; retained temporarily for rollback and migration evidence |

### 3.3.2 Data Flow into Reporting and Ledger Records

The intended reporting flow is:

```text
PostgreSQL source databases
  salesdb / mastodon / webodm
          │
          ├── approved read-only roles, views, or projections
          │             │
          │             └── Metabase: business reports and ad hoc analysis
          │
          └── approved PostgreSQL datasource
                        │
                        └── Grafana: business/database dashboards

Prometheus
  time-series metrics
          │
          └── Grafana: operational dashboards and alerts
```

Corda is not a replacement for the source PostgreSQL databases. The intended
flow is:

```text
salesdb
  verified order/payment/receipt event
          │
          └── signed, minimized ledger-ingest manifest
                    │
                    └── Corda transaction/state record
                              │
                              ├── receipt/entitlement/provenance state
                              └── approved reporting projection
                                    │
                                    └── Metabase/Grafana reporting
```

Use stable correlation fields in the source-to-ledger integration, including a
transaction/order reference, serial number where applicable, UTC timestamp,
event type, status, and content hash. Do not copy payment credentials, private
keys, or unrestricted customer datasets into Corda. Corda remains authoritative
for approved ledger/provenance state, while PostgreSQL remains authoritative
for domain-operational source data.

Before building sales reporting, initialize and verify the `salesdb` schema and
define read-only reporting views. Before enabling blockchain-related flows,
complete the Corda key/certificate ceremony and implement the ledger-ingest
manifest, correlation-ID, signature, idempotency, and audit requirements.

---

# 4. Security, Isolation, and Data Policy

## 4.1 Non-Negotiable Rules

1. Inspect before changing.
2. Preserve existing data.
3. Never format, repartition, delete, prune, or overwrite without explicit
   operator approval.
4. Never install Docker daemon, Docker Compose, or Watchtower.
5. Use Podman and Quadlet only.
6. Never expose a public port without explicit operator approval.
7. Never place secrets in scripts, logs, HTML, Git, pCloud Public Folder, IPFS,
   Corda payloads, shell history, or documentation examples.
8. Never use `--privileged` as a default.
9. Use pinned image digests for operational services.
10. Verify the photogrammetry drive before deploying or operating WebODM.
11. Record commands, versions, significant output, and failures in the
    installation or operational journal.
12. Stop and report conflicts involving services, packages, networks, mounts,
    ports, serial devices, firewall policy, or existing data.
13. Do not broaden network access, database privileges, filesystem access,
    container privileges, or secret access merely to bypass an error. A
    documented local integration path with least-privilege credentials is
    permitted when it is required for PostgreSQL reporting, backup, health
    checking, or application migration.
14. Require explicit human approval before publishing external communications,
    initiating payments, changing production credentials, deleting data, or
    modifying external records.

## 4.2 Data Classification

| Classification | Examples | Handling requirement |
|---|---|---|
| Public | Storefront HTML, intentionally published documentation, approved product data | May be placed in pCloud Public Folder |
| Internal operational | Non-sensitive configuration, health data, non-sensitive manifests, unit status | Restricted local access; do not publish by default |
| Sensitive | Customer contact data, payment references, precise telemetry, sensitive imagery, proprietary technical designs | Domain-restricted storage; encrypted backup; no public IPFS |
| Secret | Passwords, tokens, API keys, private keys, Corda keystores, archive credentials, radio keys | Podman secrets, systemd credentials, or approved secret files only |

## 4.3 Prohibited Paths

```text
Sales/AI → MAVLink, ArduPilot, ROS, Gazebo, LoRa, RNS, MeshChatX
Sales/AI → WebODM workers, raw imagery, Corda core
Payment → OpenClaw, LM Studio, Mastodon, field, mapping, simulation
Field → payment provider, Mastodon, OpenClaw, LM Studio, Corda core
Mapping → flight control, LoRa/RNS, payment provider, Mastodon, Corda core
Vehicle simulation → live drones, live radios, sales, payments, Corda core
Fabrication simulation → live machinery during phase one, sales, payments, Corda core
Public internet → PostgreSQL, Redis, WebODM workers, LM Studio, Corda,
                  ROS, MAVLink, Gazebo, QGroundControl, RNS, MeshChatX
```

## 4.4 Approved Internal Paths

```text
Sales receipt manifest ───────────────► Ledger-ingestion gateway
Verified payment event ───────────────► Sales API and/or ledger-ingestion gateway
Field telemetry manifest ─────────────► Ledger-ingestion gateway
Mapping deliverable manifest ─────────► Ledger-ingestion gateway
Vehicle simulation manifest ──────────► Ledger-ingestion gateway
Fabrication simulation manifest ──────► Ledger-ingestion gateway

Ledger receipt or entitlement status ─► Authorized service through narrow API
Signed mission release ───────────────► Field mission-release service
Validated image set ──────────────────► WebODM intake service
```

All cross-domain requests require:

- Mutual TLS.
- A dedicated service certificate or identity.
- Signed payload where durable provenance is required.
- Schema validation.
- Timestamp and nonce or equivalent replay defense.
- Durable idempotency key handling.
- Audit record.
- Explicit authorization policy.

Mutual TLS authenticates transport peers. Detached manifest signatures permit
independent verification after storage, export, or audit. These are separate
controls and should be used together for provenance-bearing artifacts.

---

# 5. Network Domains and Controlled External Access

## 5.1 Workload Domains

| Podman network | Purpose | Public exposure | Permitted output |
|---|---|---|---|
| `ao-sales` | Sales API, sales PostgreSQL, Mastodon adapter, OpenClaw, LM Studio | No direct public exposure | Signed order, receipt, and entitlement manifests |
| `ao-payment` | Provider webhook verifier and payment adapter | No direct public exposure | Verified normalized payment state |
| `ao-field` | Heltec gateway, RNS/MeshChatX, telemetry spool, mission-release service | No direct public exposure | Signed telemetry and mission manifests |
| `ao-mapping` | WebODM, NodeODM, Redis, mapping DB, imagery intake/exporter | Operator/VPN access only when approved | Signed mapping deliverable manifests |
| `ao-sim-vehicle` | ROS 2, Gazebo, ArduPilot SITL, MAVLink, QGroundControl simulation | No direct public exposure | Signed vehicle-simulation manifests |
| `ao-sim-fabrication` | ROS 2, Gazebo, robot cells, additive manufacturing, facility model | No direct public exposure | Signed fabrication-simulation manifests |
| `ao-ledger-ingest` | mTLS validation gateway, authorization, audit, idempotency | No direct public exposure | Corda receipt IDs and status |
| `ao-ledger-core` | Corda node, Corda database, certificate/keystore material | No direct public exposure | No direct output |
| `ao-data` | Narrow controlled data plumbing where unavoidable | No direct public exposure | Controlled references only |
| `ao-admin` | Monitoring, backup, restore validation, administration | VPN or explicitly allowlisted administration only | Operational reports |

All workload-domain networks are `Internal=true`. CIDRs are recorded in:

```text
/ALWAYSON/config/platform/network-cidrs.yaml
```

No workload service may receive unrestricted Internet access simply by joining
its application-domain network.

## 5.2 Controlled Ingress and Egress Adapters

External connectivity is allowed only through narrowly scoped, independently
reviewed adapters. These adapters are architecture-controlled exceptions, not
general-purpose Internet access.

| Adapter/network | Purpose | Direction | Mandatory controls |
|---|---|---|---|
| `ao-ingress-payment` | Payment-provider webhook receiver or approved relay | Inbound | Minimal listener, provider-signature verification, rate limits, audit log, normalized event output |
| `ao-egress-archive` | Encrypted pCloud replication and approved IPFS operations | Outbound | Destination allowlist, TLS validation, encrypted payloads, separate credentials, transfer audit |
| `ao-egress-community` | Approved Mastodon/community activity when remote connectivity is explicitly enabled | Outbound | Approved host allowlist, minimum OAuth scope, rate limits, publication approval log |
| `ao-build-update` | Image and package acquisition before controlled promotion | Outbound | Verified source, digest capture, update audit, no direct workload attachment |

No sales, mapping, field, simulation, database, AI, or ledger-core container may
attach directly to an Internet-capable network. An external adapter must use
separate credentials, destination allowlists, validated DNS/TLS, firewall
policy, minimal permissions, and connection logging.

### 5.3 Approved Local Data Paths

The following local paths are normal integration paths and do not require a
new architecture decision:

- Application containers to their approved PostgreSQL database endpoint.
- Metabase and Grafana to PostgreSQL through dedicated roles, views, or
  approved reporting interfaces.
- Grafana to Prometheus for operational metrics.
- Host administration and backup jobs to PostgreSQL through loopback or an
  explicitly documented local bridge.
- Application workers to their required Redis queue or broker.

These paths must not become public listeners, must use separate credentials,
and must not grant unrelated applications access to each other's owner,
migration, backup, payment, or ledger credentials. Network isolation remains
a defense-in-depth control; PostgreSQL roles and grants are the primary
authorization boundary for database access.

---

# 6. Component Boundaries, GUI Reporting Tools, and Operator Access

## 6.1 Component Boundary Matrix

| Component | Owning domain | Inputs accepted | Outputs allowed | Persistent data | External connectivity |
|---|---|---|---|---|---|
| Sales API | `ao-sales` | Verified payment state and approved support requests | Signed receipt/entitlement manifests | Sales PostgreSQL | None directly |
| Payment verifier | `ao-payment` | Provider webhook or approved relay event | Verified normalized payment event | Minimal event and audit record | Through `ao-ingress-payment` only |
| Mapping intake | `ao-mapping` | Authenticated imagery upload | Validated image-set reference | Intake, validation, quarantine record | None directly |
| WebODM/NodeODM | `ao-mapping` | Validated mapping task input | Processing output to mapping exporter | Dedicated photogrammetry volume | None directly |
| Field gateway | `ao-field` | USB serial LoRa frames | Normalized telemetry manifest | Raw packet store and telemetry spool | USB serial and radio only |
| Vehicle simulator | `ao-sim-vehicle` | Approved scenario/model artifact | Signed simulation manifest | Vehicle simulation data path | None directly |
| Fabrication simulator | `ao-sim-fabrication` | Approved facility/task model | Signed simulation manifest | Fabrication simulation data path | None directly |
| Ledger ingestion | `ao-ledger-ingest` | Signed mTLS manifests | Receipt/status response | Audit and idempotency state | Only to ledger core |
| Ledger core | `ao-ledger-core` | Ledger-ingestion gateway requests only | No direct public output | Corda state and PKI | None directly |
| Archive adapter | `ao-egress-archive` | Approved encrypted archive bundle | Replication result/status | Staging and transfer log | Outbound only |
| Community adapter | `ao-egress-community` | Approved publication or support request | Remote delivery/status response | Publication audit log | Outbound only |

## 6.A GUI Reporting Tools and Podman Network Mapping

This subsection is an **architecture requirement**. It defines the required
relationship between operator GUIs, reporting tools, dashboards, desktop
clients, external provider dashboards, workload domains, and Podman networks.

WORK 000020 implements, documents, validates, and provides evidence for this
requirement. It does not redefine, weaken, or replace it.

An **associated domain** identifies the operator workflow a tool serves. It does
not grant broad Podman-network membership, database access, host access, shared
storage, shared credentials, or cross-domain control. A host desktop
application, host browser, or external provider dashboard has no Podman network
attachment unless it is itself implemented as a container attached to that
network.

`ao-admin` is the protected administration, monitoring, and reporting plane. It
may host Grafana for operational dashboards and alerts, Metabase for FOSS
accounting/database-heavy reporting, and narrowly authorized administration
tools. It must not become a shared universal network. `ao-data` remains narrow
controlled data plumbing, not a default GUI, shared-database, or reporting
network.

### 6.A.1 GUI ↔ Podman Network Mapping

| # | GUI / workflow | Software or service | Podman network mapping — all ten `ao-*` networks | Approved access path | Status |
|---:|---|---|---|---|---|
| 1 | Mastodon web / Tokodon client | Mastodon web, streaming, Sidekiq, database, Redis; Tokodon host client | **Associated:** `ao-sales`. **Actual attachment:** Mastodon containers: `ao-sales` only; Tokodon: none. **No access:** `ao-admin`, `ao-data`, `ao-field`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-mapping`, `ao-payment`, `ao-sim-fabrication`, `ao-sim-vehicle`. | Approved `localhost` Mastodon web/streaming origin; loopback-only publication when enabled. | In progress; local service model exists. Tokodon/OAuth validation remains under WORK 000010. |
| 2 | WebODM browser UI | WebODM web application, worker, broker, database, NodeODM; host browser | **Associated:** `ao-mapping`. **Actual attachment:** WebODM components: `ao-mapping` only; browser: none. **No access:** `ao-admin`, `ao-data`, `ao-field`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-payment`, `ao-sales`, `ao-sim-fabrication`, `ao-sim-vehicle`. | Approved loopback WebODM listener; VPN/authenticated access only if separately approved. | Implemented with deviation; smoke test and UI path verified. Final rootless/system/mixed designation remains required. |
| 3 | QGroundControl simulation client | QGroundControl host app; ArduPilot SITL and MAVLink router | **Associated:** `ao-sim-vehicle`. **Actual attachment:** QGroundControl: none; simulation services: `ao-sim-vehicle` only. **No access:** `ao-admin`, `ao-data`, `ao-field`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-mapping`, `ao-payment`, `ao-sales`, `ao-sim-fabrication`. | Approved local SITL/MAVLink-router endpoint; `ROS_DOMAIN_ID=21`; `GZ_PARTITION=alwayson_vehicle_sim`. | Planned GUI workflow; headless vehicle simulation and ROS-Gazebo bridge verified. |
| 4 | Gazebo visualization — vehicle | ROS 2 Lyrical and Gazebo Sim 10.5.0 | **Associated:** `ao-sim-vehicle`. **Actual attachment:** Host GUI: none; simulation services: `ao-sim-vehicle` only. **No access:** `ao-admin`, `ao-data`, `ao-field`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-mapping`, `ao-payment`, `ao-sales`, `ao-sim-fabrication`. | Approved vehicle ROS/Gazebo visualization path; separate DDS/interface policy remains required. | Planned GUI; headless runtime verified. |
| 5 | Gazebo visualization — fabrication | ROS 2 Lyrical and Gazebo Sim 10.5.0 | **Associated:** `ao-sim-fabrication`. **Actual attachment:** Host GUI: none; simulation services: `ao-sim-fabrication` only. **No access:** `ao-admin`, `ao-data`, `ao-field`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-mapping`, `ao-payment`, `ao-sales`, `ao-sim-vehicle`. | Approved fabrication ROS/Gazebo visualization path; `ROS_DOMAIN_ID=22`; `GZ_PARTITION=alwayson_fabrication_sim`. | Planned GUI; headless runtime verified. |
| 6 | LM Studio / OpenClaw support chat | LM Studio host-local model server; OpenClaw restricted support service | **Associated:** `ao-sales`. **Actual attachment:** LM Studio: none while host-local; OpenClaw: `ao-sales` only if containerized. **No access:** `ao-admin`, `ao-data`, `ao-field`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-mapping`, `ao-payment`, `ao-sim-fabrication`, `ao-sim-vehicle`. | Host desktop use; approved loopback inference endpoint or narrow authenticated bridge only. | In progress; endpoint and container/host boundary require formalization under WORK 000010. |
| 7 | Grafana operational monitoring dashboard | Grafana plus Prometheus-compatible metrics collector/exporters | **Associated:** `ao-admin`. **Actual attachment:** Grafana and metrics collector containers: `ao-admin` only. **No broad attachment:** `ao-data`, `ao-field`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-mapping`, `ao-payment`, `ao-sales`, `ao-sim-fabrication`, `ao-sim-vehicle`. Read-only metrics/status collection occurs only through documented narrow exporter, relay, scrape, or push paths. | VPN or authenticated, allowlisted administration access only. | Planned; implements Section 17.2 operational monitoring and alerting requirements. |
| 8 | Metabase accounting, sales, and database-heavy reporting GUI | Metabase preferred FOSS BI/reporting service; Apache Superset or Redash may be evaluated only through a documented approved decision | **Associated:** `ao-admin`. **Actual attachment:** Metabase container: `ao-admin` only. **No broad attachment:** `ao-data`, `ao-field`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-mapping`, `ao-payment`, `ao-sales`, `ao-sim-fabrication`, `ao-sim-vehicle`. Metabase receives only approved read-only reporting connections, views, or projections. | VPN or authenticated, allowlisted administration access. Dedicated least-privilege reporting identities use approved loopback/tunnel/bridge paths. | Planned. Implement after reporting views, reporting identities, and sales/payment workflow are approved. |
| 9 | Sales, receipt, fulfillment, entitlement, return, and approved support reporting | Metabase dashboards, saved questions, filters, exports, and approved SQL models; optional DBeaver host client for exceptional analysis | **Associated:** `ao-admin` reporting plane; sales data remains authoritative in the sales system. **Actual attachment:** Metabase: `ao-admin` only; DBeaver host client: none. **No broad attachment:** `ao-data`, `ao-field`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-mapping`, `ao-payment`, `ao-sales`, `ao-sim-fabrication`, `ao-sim-vehicle`. | Metabase uses approved read-only reporting views and identities. DBeaver uses an explicit purpose-limited loopback or approved tunneled connection. | Planned after sales API, payment verifier, reporting schema/views, and payment-provider workflow are implemented. |
| 10 | Ledger provenance, receipt, entitlement, approval, release, and ingestion reporting | Metabase for approved ledger reporting; Grafana for Corda/ingest health; Corda-supported management/API/CLI for administration | **Associated:** `ao-admin` reporting plane; approved data originates through `ao-ledger-ingest`. **Actual attachment:** Metabase/Grafana: `ao-admin` only; ledger-ingestion service: `ao-ledger-ingest`; Corda core: `ao-ledger-core`. **No broad attachment:** `ao-data`, `ao-field`, `ao-mapping`, `ao-payment`, `ao-sales`, `ao-sim-fabrication`, `ao-sim-vehicle`; no browser GUI in `ao-ledger-core`. | VPN or authenticated administration access. Metabase reads approved reporting views/projections through a dedicated reporting identity; Grafana receives supported metrics/status only. | Planned/blocked pending key/certificate ceremony, Corda status/metrics configuration, and approved reporting projection. |
| 11 | Backup/restore status display | Restic plus approved status scripts, Grafana panels, or protected dashboard | **Associated:** `ao-admin`. **Actual attachment:** Dashboard/status service: `ao-admin` only; host-local tool: none. **No broad attachment:** `ao-data`, `ao-field`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-mapping`, `ao-payment`, `ao-sales`, `ao-sim-fabrication`, `ao-sim-vehicle`; approved job/status artifacts only. | Same protected administration boundary as Grafana and Metabase. | Planned; backup and isolated restore evidence already exist. |
| 12 | Field gateway / link-quality display | Heltec V3 gateway service; local display and/or approved Grafana-derived metrics | **Associated:** `ao-field`. **Actual attachment:** Gateway: `ao-field` only; host display: none; Grafana: `ao-admin` only. **No access:** `ao-data`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-mapping`, `ao-payment`, `ao-sales`, `ao-sim-fabrication`, `ao-sim-vehicle`; `ao-admin` receives derived metrics only. | Approved USB serial/local diagnostic display or protected Grafana dashboard. | In progress; Heltec V3 connection and stable serial path verified 2026-08-31; gateway service deployment pending under WORK 000050. |
| 13 | Ledger/Corda console and maintenance | Corda-supported management API/CLI and approved diagnostic tooling; not Metabase | **Associated:** `ao-ledger-ingest` and `ao-ledger-core`. **Actual attachment:** Management/status client: documented narrow path only; ingestion: `ao-ledger-ingest`; Corda core: `ao-ledger-core`; optional dashboard: `ao-admin`. **No access:** `ao-data`, `ao-field`, `ao-mapping`, `ao-payment`, `ao-sales`, `ao-sim-fabrication`, `ao-sim-vehicle`; no browser GUI deployed inside ledger core. | Narrow approved operator-management path after key/certificate ceremony; no public access. | Blocked pending Section 18.3 ceremony and current ledger backend diagnosis. |
| 14 | PostgreSQL reporting, schema inspection, and controlled administration | DBeaver host client preferred for expert SQL; optional pgAdmin in `ao-admin`; Metabase for routine reporting | **Associated:** Approved host-loopback data administration and `ao-admin` reporting. **Actual attachment:** DBeaver: none; optional pgAdmin/Metabase: `ao-admin` only. **No implied attachment:** `ao-data` does not grant general database access; no broad membership in `ao-field`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-mapping`, `ao-payment`, `ao-sales`, `ao-sim-fabrication`, or `ao-sim-vehicle`. | Explicit loopback or approved narrow tunnel/bridge using a dedicated least-privilege database identity. | Planned. PostgreSQL is loopback-only; formal reporting/maintenance roles and views are required. |
| 15 | Redis diagnostic client | Optional Redis Insight or equivalent; not a routine reporting tool | **Associated:** Approved Redis diagnostics only. **Actual attachment:** Host desktop client: none; optional web GUI: `ao-admin` only. **No broad attachment:** All workload networks unless a separate explicit diagnostic endpoint/path is approved. | Explicit loopback or approved narrow diagnostic path using a scoped Redis ACL identity. | Optional/planned only if diagnostic value justifies deployment. |
| 16 | Payment-provider dashboard | Selected external provider hosted dashboard | **Associated:** Provider-hosted payment administration. **Actual attachment:** None. The provider dashboard is not a Podman service. **No access:** No attachment to `ao-admin`, `ao-data`, `ao-field`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-mapping`, `ao-payment`, `ao-sales`, `ao-sim-fabrication`, or `ao-sim-vehicle`. | Provider-authenticated browser workflow. | Blocked/open pending payment-provider selection. |
| 17 | No GUI — controlled data services | Host PostgreSQL 18.6, Redis 8.0.5, and explicitly approved data paths | **Associated:** `ao-data` only where narrow controlled plumbing is required. **Actual attachment:** Only individually approved components. **No GUI access:** `ao-data` is not a general GUI/database network and does not imply access to `ao-admin`, `ao-field`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-mapping`, `ao-payment`, `ao-sales`, `ao-sim-fabrication`, or `ao-sim-vehicle`. | Host services remain loopback-only; administration/reporting uses dedicated host or `ao-admin` identities and paths. | Implemented as intentional GUI-less controlled plumbing. |
| 18 | No GUI — payment verifier | Provider webhook verifier and payment adapter | **Associated:** `ao-payment`. **Actual attachment:** Payment verifier: `ao-payment` only; approved payment-ingress adapter only when implemented. **No access:** `ao-admin`, `ao-data`, `ao-field`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-mapping`, `ao-sales`, `ao-sim-fabrication`, `ao-sim-vehicle`; `ao-admin` may receive derived health metrics only. | Provider-hosted checkout and provider dashboard; local verifier has no GUI. | Blocked/open pending provider decision under Section 18.4. |

### 6.A.2 Reporting Tool Roles

| Tool | Primary purpose | Mandatory boundary |
|---|---|---|
| **Metabase** | FOSS relational reporting: sales, orders, receipts, fulfillment, entitlements, returns, approved support summaries, ledger/provenance projections, saved questions, dashboards, filters, and exports | Runs in `ao-admin`; uses PostgreSQL for its own application state and connects to approved source databases through dedicated read-only roles, views, or projections. It never receives superuser, database-owner, migration, backup, payment-provider, or Corda-key credentials. |
| **Grafana** | Operational monitoring and visualization: metrics, service health, alerts, queue depth, latency, resource use, storage, GPU state, backup age, restore-test status, certificate expiry, ingest failures, and approved PostgreSQL business/database metrics | Runs in `ao-admin`; uses PostgreSQL for its own application state, Prometheus for metrics, and approved PostgreSQL datasources for business/database reporting. It never becomes a shell, container-management, or control path. |
| **Corda management/API/CLI** | Corda lifecycle, configuration, certificate-aware administration, and controlled maintenance | Uses a documented narrow management path after the required ceremony; it is not replaced by Metabase or Grafana. |
| **DBeaver / optional pgAdmin** | Exceptional SQL analysis, schema inspection, backup/restore validation, and controlled database maintenance | Uses an explicit least-privilege identity and loopback or approved narrow tunnel/bridge; it is not the routine accounting/reporting surface. |
| **Payment-provider dashboard** | Provider-authoritative charges, refunds, disputes, payouts, exports, and reconciliation | External provider service; no Podman network attachment and no replacement of local verified-event controls. |

Metabase may report on approved Corda-derived business and provenance data only
through a deliberate read-only reporting projection, approved views, supported
status interface, or ledger-ingestion audit/status records. Metabase must not
become the primary interface to Corda internal persistence tables, administer
Corda, receive Corda private keys/keystores, or create a broad route into
`ao-ledger-core`.

### 6.A.3 Conformance Requirements

All current and future GUI, dashboard, reporting, database-administration, and
operator-access implementations must comply with this subsection and Sections
4, 5, 14, and 17.

- Every tool must have a named operator purpose, actual runtime placement,
  approved data/status source, documented access path, and explicit
  implementation status.
- Every containerized GUI must have documented Podman-network membership,
  listener policy, service owner, image digest, authentication method, and
  least-privilege identity.
- Every host desktop GUI and provider dashboard must be recorded as having no
  Podman network attachment unless it is actually containerized.
- Reporting identities must enforce read-only access to source databases or
  services. This does not make Grafana or Metabase read-only applications:
  each owns a separate PostgreSQL application database and role.
- `ao-admin` receives approved PostgreSQL reporting, exporter, status,
  projection, API, relay, tunnel, or push paths. It must not join every
  workload network.
- `ao-data` is not a shared unrestricted database, general-purpose shell, or
  authorization bypass. It may carry narrowly approved local data paths.
- No GUI may add a public listener, broad host networking, unrestricted Podman
  socket access, `--privileged`, shared writable storage, or unrelated-domain
  secret merely to simplify deployment or troubleshooting.
- Any material deviation requires an approved deviation record under Section
  18 before production declaration.

The machine-readable implementation inventory for this requirement is:

```text
/ALWAYSON/config/platform/gui-boundary-matrix.yaml
```

---

# 7. Public Storefront and Payment Policy

## 7.1 Storefront Boundary

The public storefront is static HTML hosted in the pCloud Public Folder.
HTML project github: https://github.com/300x3/HTML-300X3
Static HTML output folder for pCloud: `public/html/` (generated by
`scripts/build-html.mjs`; dependency-free pages: index, buildings, vehicles,
equipment, maps, discussion, documentation, donate).

## 7.1.1 Frontend Website Details (WORK 000005)

Source: HTML-300X3 repo (React + TanStack Router; static export in
`public/html/`). Navigation is defined in `src/lib/nav.ts` (`NAV` sections
with modal previews, pCloud folder links, and SketchUp/Trimble model links).
The pCloud Public Folder mirrors the static export layout.

Top-level sections and catalog items (modals):

### Equipment (`/equipment`)

- Adapter (soda threads to 0.5" NPT — "TUBER").
- Boiler (water boiler, power production, chemistry set).
- Pneumatic Speargun Ulu (Damascus ulu + forearm pneumatic speargun).
- Structural Battery ("power sandwich" gas/liquid tank + battery case).
- Appliances (12oz micro-appliances — "app cans").
- Computer (12oz-can Raspberry Pi case + wireless HDMI/video-glasses kit).
- Camping (shopping-list discussion, pricing, where-to-buy).

### Buildings (`/buildings`)

- Furniture.
- ADU (80sf and up).
- Mall.
- Tower.
- Concrete Island.

### Vehicles (`/vehicles`)

- Drone (air/land/sea).
- Boat (micro modular aircraft carrier).
- Personal Vehicle.
- Electric Car Wheel.
- Balloon.

Supporting sections: Digital (images, topography/3D points, "Where's My ___?",
route-around-your-county), Discussion (Mastodon forum + 300X3@POSTEO.NET),
Documentation (intro video, working project-plan PDF, server coding, 3D models,
HUD app, simulations, AI/hardware/software/fabrication/raw-material links),
Donate (PayPal hosted button + Zelle + card/other).

### Sales-link integration plan (per WORK 000005)

Each catalog modal under Equipment / Buildings / Vehicles gets a sales action
that stays inside the static-site boundary (no secrets, no local ports, no
internal hosts — see Section 7.1 prohibitions):

1. Modal shows product images, parts list / detailed drawings link, pCloud
   folder link, and IPFS digital-asset mark where applicable.
2. A purchase button routes to provider-hosted checkout (PayPal hosted button
   today; Zelle instructions and Coinbase/USDC flow per Section 18.4 as
   implemented) or to a `mailto:300X3@POSTEO.NET` order-request template
   carrying product name, options, and quantity.
3. Checkout completion returns a provider-signed event (or manual
   reconciliation record for Zelle/wire) into the Section 7.3 sales and
   receipt sequence; Corda records the receipt/entitlement state per
   Section 11.
4. No payment-card data, webhook secrets, OAuth tokens, or ledger keys ever
   appear in the static HTML, pCloud folder, or Git history.

```text
pCloud Public Folder
├── index.html
├── products/
├── catalog/
├── support/
├── community/
├── legal/
│   ├── privacy.html
│   ├── terms.html
│   ├── returns.html
│   └── shipping.html
└── assets/
    ├── css/
    ├── js/
    ├── images/
    └── downloads/
```

The public site may include:

- Product catalog and documentation.
- Hosted payment checkout links.
- Provider-controlled payment buttons.
- Order follow-up and support links.
- Mastodon/community links.
- AI-assisted support entry points that do not expose private infrastructure.
- Shipping, return, warranty, privacy, and legal content.

The public site must never include:

- Payment-provider secret keys.
- Corda keys, RPC credentials, or node addresses.
- Mastodon OAuth tokens.
- pCloud archive credentials.
- IPFS private keys or swarm keys.
- Local hostnames, LAN addresses, Podman ports, or private API routes.
- Database connection strings.
- Drone radio configuration, control endpoints, or flight-control access.
- Internal service certificates, identifiers, or diagnostic output.

## 7.2 Payment and Settlement Policy

ALWAYS ON does not process, transmit, or store payment-card numbers, CVV
values, or payment-provider secret material in the storefront, sales database,
Corda, Git repository, logs, pCloud Public Folder, or IPFS.

The default payment model is provider-hosted checkout. The selected provider is
responsible for payment-card capture and authorization. The local
payment-verifier service accepts only provider-signed webhook events and stores
normalized business state.

| Payment method | Intended use | Required control |
|---|---|---|
| Hosted card checkout | Standard online transactions | Provider-hosted checkout, signature-verified webhook, no local card handling |
| Hosted PayPal checkout | Optional provider-supported checkout | Provider-controlled flow and verified event |
| Wire transfer | Approved high-value transactions | Manual reconciliation, operator approval, auditable reference record |
| Other payment methods | ARE TO BE PROCESSED BY CORDA - SPECIFICALLY STABLECOIN IN RELATION TO COINBASE OR SIMILAR | Requires documented provider terms, accounting treatment, refund process, and explicit operator approval |   

Corda IS THE CENTRAL SOURCE OF TRUTH FOR ALL FINANCIAL LEDGER INFORMATION AND IS LINKED TO POSTGRESQL ADDITIONAL DATABASE DETAILS ON A PER TRANSACTION AND PER SERIAL NUMBER BASIS. CORDA does not accept payment cards and does not replace payment-provider,
banking, tax, consumer-protection, accounting, refund,  Corda DOES record approved receipt, fulfillment, entitlement, or
provenance state after a payment event has been verified or manually
reconciled. CORDA MUST INCLUDE ALL RELATED TRANSACTION DATA TYPICAL TO FINANCIAL AND PAYMENTS INDUSTRY INCLUDING ALL LEDGER DETAILS AND BE QUERY-ABLE BY THE AUTHORIZED REPORTING SERVICE - METABASE / GRAFANA.

PAYPAL, Zelle, AND STABLE COIN (USDC OR SIMILAR) are THE STANDARD PAYMENT METHODS FOR THE PROJECT AND CORDA MUST 
VERIFY ALL PAYMENTS MADE WITH THEM WHILE DOCUMENTING THOSE TRANSACTIONS WITHIN A SECURE BLOCKCHAIN AND LEDGER.

**Approved 2026-08-28 (§18.4):** ZELLE PROCESSING IS THE SAME AS PAYPAL AND COINBASE/STABLECOIN PROCESSING, THE EXISTING AUTHENTICATION METHOD FOR EACH PAYMENT SERVICE IS TO BE VERIFIED BY CORDA IN SOME MANNER.

## 7.3 Sales and Receipt Sequence

```text
Customer browser
      │
      ▼
pCloud static storefront
      │
      ▼
Provider-hosted checkout or approved wire-transfer request
      │
      ▼
Payment provider or reconciliation process
      │
      ▼
Controlled payment ingress adapter
      │
      ▼
Verified payment event
      │
      ▼
Sales API and sales PostgreSQL
      ├── Order record
      ├── Receipt record
      ├── Fulfillment state
      └── Entitlement state
              │
              ▼
Signed receipt manifest
              │
              ▼
Ledger-ingestion gateway
              │
              ▼
Corda receipt and entitlement state
```

---

# 8. Mapping and Photogrammetry

## 8.1 Dedicated Storage

The dedicated local workspace for WebODM and photogrammetry is:

```text
/media/scottw/500GBPHOTOGRAM/
```

This drive is authoritative for:

- Incoming drone imagery.
- Validated imagery sets.
- Rejected and quarantined uploads.
- WebODM media and project data.
- NodeODM intermediates.
- Mapping deliverables.
- Mapping processing and provenance manifests.
- pCloud/IPFS archive staging.
- Mapping-database backup exports.

WebODM must not use the root filesystem, `$HOME`, or Podman writable container
layers for high-volume processing.

## 8.2 Required Directory Tree

```text
/media/scottw/500GBPHOTOGRAM/
├── README.md
├── .mounted-ok
├── incoming/
│   ├── drone/
│   ├── operator/
│   └── quarantine/
├── validated/
│   └── <mission-id>/
├── rejected/
│   └── <mission-id-or-date>/
├── webodm/
│   ├── media/
│   ├── projects/
│   ├── nodeodm/
│   ├── temp/
│   └── logs/
├── deliverables/
│   └── <mission-id>/
│       ├── orthophoto/
│       ├── point-cloud/
│       ├── dem-dsm/
│       ├── textured-model/
│       ├── reports/
│       └── manifest/
├── manifests/
│   ├── intake/
│   ├── processing/
│   └── ledger-submissions/
├── exports/
│   ├── pcloud-staging/
│   └── ipfs-staging/
├── backups/
│   └── mapping-db/
├── retention/
│   ├── pending-review/
│   └── eligible-for-archive/
└── tmp/
    └── processing/
```

No directory in this tree may be world-writable. Use dedicated mapping
ownership, explicit groups, and ACLs only when necessary.

## 8.3 Mapping Processing Flow

```text
Authenticated drone or operator upload
      │
      ▼
TELEMMETRY DATA INGEST TO IMAGERY-INGEST SERVICE FROM 3DR N1    (AUTOPILOT MODULE)
Imagery-ingest service FROM RASPBERRY PI CAMERA AND SENSOR   (COMPANION COMPUTER)
      ├── File type validation
      ├── SHA-256 checksum
      ├── EXIF and metadata validation
      ├── Mission association (FOR AUTOPILOT MODULE TELEMMETRY DATA INCORPORATION TO EXIF AND WEBODM PROJECT NAME)
      ├── Storage quota check
      ├── File-count validation
      └── Quarantine on failure
              │
              ▼
WebODM API and project task creation
              │
              ▼
Queue / Redis
              │
              ▼
NodeODM processing worker
      ├── Orthomosaic
      ├── Point cloud
      ├── DSM / DEM
      ├── Textured model
      └── Processing report
              │
              ▼
Mapping-result exporter
      ├── Hashes outputs
      ├── Generates signed manifest
      ├── Stages approved archive bundle
      └── Submits signed manifest to ledger ingestion
```

## 8.4 Persistent Locations

| Data | Location |
|---|---|
| Raw images | `/media/scottw/500GBPHOTOGRAM/incoming/` |
| Validated images | `/media/scottw/500GBPHOTOGRAM/validated/` |
| WebODM media/projects | `/media/scottw/500GBPHOTOGRAM/webodm/` |
| Intermediate work | `/media/scottw/500GBPHOTOGRAM/webodm/nodeodm/` and `tmp/` |
| Deliverables | `/media/scottw/500GBPHOTOGRAM/deliverables/` |
| Mapping PostgreSQL | `/ALWAYSON/data/mapping/postgres/` or approved Podman volume |
| Redis persistence | `/ALWAYSON/data/mapping/redis/` |
| Signed manifests | `/ALWAYSON/artifacts/mapping-manifests/` |

## 8.5 Mapping Mount Validation

The drive must be identified by filesystem UUID, not by `/dev/sdX`.

WebODM must refuse to start when:

- The mount is absent.
- The mountpoint resolves to the root filesystem.
- The mounted UUID differs from the approved UUID.
- `.mounted-ok` is absent.
- Available space is below the configured minimum.
- Required directories are missing.
- Mapping service ownership or permissions are incorrect.

Required validation:

```bash
lsblk -f
findmnt /media/scottw/500GBPHOTOGRAM
blkid
df -hT /media/scottw/500GBPHOTOGRAM
```

Begin with CPU-only validation. Enable GTX 1080 access only after validated
container GPU runtime, driver compatibility, measurable workload benefit, and a
documented CPU-only recovery path.

## 8.6 3D Model Identity and Database Cross-Referencing

Every 3D model, model revision, component, assembly, and derived artifact must be
addressable from the same database and ledger correlation system used for sales
and receipts. The model file is not itself the authority; the authoritative
relationship is the PostgreSQL registry entry plus the signed content manifest.

### 8.6.1 Identifier hierarchy

Use a stable, globally unique `model_object_id` for the logical object and a
separate `model_revision_id` for each version:

```text
model_object_id       # Stable identity of the logical 3D object or assembly
model_revision_id     # One specific model revision/artifact
serial_number         # Physical asset, when the model represents a sold product
correlation_id        # Business/event correlation across PostgreSQL and Corda
receipt_number        # Commercial receipt, when the model is sold
event_timestamp_utc   # When the relationship/event was recorded
content_hash_sha256   # Hash of the exact model file or packaged artifact
```

`model_object_id` remains stable across revisions. A revised model must not reuse
an old revision ID. `serial_number` links the model to a physical product; it
is not a replacement for the model object ID.

### 8.6.2 Metadata carried with the 3D model

Each model package must carry a sidecar metadata document or embedded metadata
block containing at least:

```json
{
  "model_object_id": "OBJ-300X3-BATTERY-0001",
  "model_revision_id": "REV-2026-09-25-01",
  "object_type": "cad_assembly",
  "source_system": "cad_release",
  "serial_number": "SN-300X3-000042",
  "correlation_id": "ORDER-2026-000123-A",
  "receipt_number": "RCPT-2026-000123",
  "event_timestamp_utc": "2026-09-25T12:34:56Z",
  "schema_version": "1.0",
  "content_hash_sha256": "SHA256_DIGEST",
  "source_artifact_reference": "opaque internal reference",
  "license_reference": "approved license/terms reference",
  "is_public_proof_eligible": false
}
```

The metadata is cross-referenced, not duplicated wholesale: the model contains
identity and reference fields, PostgreSQL contains the operational record, and
Corda contains the signed state/reference.

### 8.6.3 Database registry

The model registry should be implemented in PostgreSQL with tables equivalent to:

```text
model_objects
  model_object_id, object_type, canonical_name, created_at_utc, created_by,
  current_revision_id

model_revisions
  model_revision_id, model_object_id, revision_number, content_hash_sha256,
  source_artifact_reference, archive_reference, license_reference,
  created_at_utc, created_by

model_object_links
  model_object_id, link_type, serial_number, correlation_id, receipt_number,
  event_timestamp_utc, valid_from_utc, valid_to_utc

model_ledger_references
  model_revision_id, corda_event_type, corda_transaction_id, corda_state,
  corda_confirmed_at_utc, manifest_reference
```

`model_object_links` is the cross-reference table. It relates a model object to
a product, serial number, receipt, order, mapping project, simulation result,
release, or other approved object without embedding the operational record in
the 3D file.

### 8.6.4 Cross-reference flow

```text
CAD/3D authoring tool
        │ model_object_id + model_revision_id
        ▼
Model registry (PostgreSQL)
        ├── serial_number → product/asset record
        ├── correlation_id + receipt_number → sale contract record
        ├── content_hash → exact model artifact
        └── manifest reference → signed ledger event
                                  │
                                  ▼
                             Corda state
```

A viewer, CAD tool, WebODM/NodeODM exporter, or marketing application resolves
a model by reading its object/revision IDs, validating the content hash, looking
up the PostgreSQL registry, following approved links to the serial/receipt
record, following the Corda projection, and returning only fields permitted for
that audience.

### 8.6.5 Integrity and relationship rules

- A model revision has exactly one `model_revision_id`.
- A model revision has one immutable `content_hash_sha256`.
- A revision ID cannot point to different content hashes.
- A model object may have many revisions, but only one current revision.
- A physical serial number may have many model revisions over its lifetime.
- A receipt may reference many model objects or serials through the link table.
- A model relationship records `event_timestamp_utc` and its source.
- Superseded revisions are preserved and marked `superseded`, never reused.
- A Corda reference is required before a model is called provenance-verified.
- A content hash proves file integrity, not authenticity or publication safety.

### 8.6.6 Public and private model metadata

Internal metadata may contain serial numbers, correlation IDs, and opaque
references. Public marketing metadata should contain only approved fields:

```text
model_object_id or public proof ID
product/SKU
approved serial or proof token
revision label
provenance status
public verification reference
content hash or public proof hash
license/terms reference
```

Do not publish customer identity, receipt totals, addresses, payment references,
private simulation data, internal paths, or Corda transaction details unless that
disclosure is explicitly approved.

### 8.6.7 Relationship to the sale/receipt process

For a sold product, the 3D model metadata (`model_object_id`,
`model_revision_id`, `serial_number`) resolves to the PostgreSQL model registry,
`sale_contract_lines`, receipt/correlation projection, and signed Corda
provenance reference. The receipt and model may each show a reference to the
same correlation record. Neither file is the authoritative sale ledger.

---

# 9. Field and LoRa Architecture

## 9.1 Drone-Side System

```text
ArduPilot flight controller
       │ MAVLink through UART or USB
       ▼
Raspberry Pi 5
       ├── MAVLink collector and mission agent
       ├── Local encrypted telemetry spool
       ├── RNS / Reticulum node
       ├── MeshChatX application
       ├── Packet signing and acknowledgement
       └── Waveshare SX1262-class LoRa HAT
                  │
                  ▼
              LoRa RF link
```

## 9.2 Desktop Gateway

### 9.2.1 MeshChatX Local Service Port

The desktop MeshChatX application uses the dedicated loopback port
`https://127.0.0.1:18000` for its native backend and local web UI. This port is
separate from the ALWAYS ON mapping service listener on `127.0.0.1:8000`.

| Service | Domain | Listener | Exposure | Ownership |
|---|---|---|---|---|
| MeshChatX native backend / web UI | Field / Reticulum | `https://127.0.0.1:18000` | Loopback only | `scottw` user service |
| WebODM web service | Mapping / `ao-mapping` | `127.0.0.1:8000` | Loopback only | `ao-webodm-web.service` |
| Reticulum transport | Field / Reticulum | Reticulum-configured interfaces | No HTTP listener | Embedded MeshChatX backend |

MeshChatX uses its self-signed local certificate; clients must use HTTPS and accept the local certificate. The MeshChatX port is not a public ingress and must not be published through
Podman, nginx, Cloudflare, or a router. WebODM and MeshChatX must not share a
listener. The desktop launcher and watchdog must use port `18000`; changing one
without the others is a configuration error.

```text
Heltec WiFi LoRa 32 V3
       │ USB-C serial
       ▼
/dev/serial/by-id/...
       │
       ▼
Heltec gateway service
       ├── Serial framing
       ├── Link-health and RSSI/SNR metrics
       ├── Packet authentication
       ├── Duplicate and replay detection
       ├── RNS / MeshChatX adapter
       ├── Raw-packet storage
       ├── Telemetry normalization
       └── Signed telemetry-manifest exporter
```
The current host uses two separate raw-LoRa/Reticulum interfaces:

| Interface | Hardware | Frequency | Bandwidth | SF | CR | TX power | Mode |
|---|---|---:|---:|---:|---:|---:|---|
| `PEOPLE-RADIO` | Heltec LoRa 32 V3, SX1262, RNode firmware 1.85 | 915 MHz | 125 kHz | 7 | 5 | 17 dBm | `selected_interface_mode = 1` |
| `DRONE-RADIO` | Heltec LoRa 32 V3, SX1262, RNode firmware 1.85 | 917 MHz | 250 kHz | 7 | 5 | 17 dBm | `mode = internal`; `selected_interface_mode = 7`; `discoverable = no` |

The different frequencies and airtimes intentionally separate the public
people-facing radio from the private drone/IoT radio. They must not be treated as
interchangeable interfaces or combined into one RF channel without an approved
frequency plan.

The live host configuration is under `/home/scottw/.reticulum/`. MeshChatX runs
headlessly at `127.0.0.1:18000`. Its embedded Reticulum runtime is initialized
from `/home/scottw/.reticulum/config`, while MeshChatX identity, repository, and
application state are stored under `/home/scottw/.reticulum-meshchatx/`.

Both RNodes are functional and initialize successfully in the active MeshChatX
process. This confirms local device detection, serial access, and RNode
configuration. RF feedback is observable on both configured bands:

| Radio | Configured band | Operational state | Remaining observation |
|---|---:|---|---|
| `PEOPLE-RADIO` | 915 MHz | Functional | Characterize feedback observed on this band |
| `DRONE-RADIO` | 917 MHz | Functional | Characterize feedback observed on this band |

“Feedback” is an operator observation, not yet a diagnosed fault. Potential
categories include self-feedback, nearby RF activity, interference, harmonics,
spurious transmission, antenna coupling, or reflected energy. Do not change
power, frequency, bandwidth, spreading factor, coding rate, antenna, or
transmit mode until the source and severity are measured.

Both CP2102 bridges expose the same USB serial descriptor
`Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001`. Device identity must
therefore be resolved through the stable PCI/USB `by-path` location and the
recorded SX1262 MAC address. The USB serial descriptor alone is not a unique
radio identity.

## 9.3 Reticulum Interface Inventory

As reviewed on 2026-09-24, `/home/scottw/.reticulum/config` contained 32
configured interfaces:

- Modified: `2026-09-24 10:43:59-07:00`.
- Size: `7942` bytes.
- SHA-256: `2df6a8d9fc2037d9e316ac910ec1721c3b5b6af5e301a50b0e92656226cc4098`.
- 29 enabled `TCPClientInterface` connections.
- Two enabled `RNodeInterface` entries: `PEOPLE-RADIO` and `DRONE-RADIO`.
- One enabled `BackboneInterface` named `Public Gateway`.
- No interface explicitly labeled or configured as disabled.

The configured TCP client interfaces are:

- DX.PE Los Angeles Backbone
- ViscousBits
- Panic Public PDX
- KetronKlassik Oakland Gateway
- hownotbrowncrow
- CenTex1
- jsreed5.org Reticulum Entrypoint
- Unbound Hive TCP
- NecroNet RNS Gateway
- fools-gold-gateway
- CDQ-Drummondville
- Washmesh Gateway
- RazzTech Gateway
- Minuteman RNS West
- rns.amilia.zip
- Montgomery
- GhostMesh ATL IPv6
- CCLLC-Net Public TCP Gateway
- CORE - Central Ohio Radio Enthusiasts
- Mitigomish Public Gateway
- MattInTech Backbone
- rns.quacksradio.com
- Red Nova Gateway
- SCR
- GhostMesh WTX IPv4IPv6
- Parallel RNS-1 Public Hub
- thefossrant us-east-1
- topkeksec
- Simply Equipped US Cloud

“Enabled” records configuration intent only. It does not prove that an interface
is connected, reachable, or carrying traffic. Current startup evidence includes
successful peering and announces as well as timeouts, unreachable-network errors,
connection refusals, and reconnect loops. Historical radio logs also contain
`Could not detect device`, `Radio state mismatch`, and retry cycles; the current
process later initialized both radios, so those historical events must not be
reported as the current state without a fresh capture. Discovered interfaces
also appear at runtime and are not a one-to-one match with the static
configuration.

The configuration fingerprint identifies only the reviewed static inventory. It
does not identify the runtime state of discovered interfaces.

Future interface reports must distinguish:

| Field | Required meaning |
|---|---|
| Interface name | Stable configured or discovered name |
| Type | TCP client, RNode, backbone, or other transport |
| Enabled | Configuration intent |
| Initialized | Device detection and interface configuration completed |
| Connected | Current socket/interface state |
| Operational | Recent traffic with no fatal state |
| Reachable | Successful traffic or peer exchange |
| Last error | Most recent failure, if any |
| Last checked | Timestamp of evidence |

## 9.4 Operational Security

The MeshChatX web interface is restricted to `127.0.0.1:18000`.

The Reticulum `Public Gateway` is configured to listen on `0.0.0.0:4242`.
Because this listener binds all local IPv4 interfaces, it is not
loopback-restricted. Whether it is reachable from the LAN or Internet depends
on firewall and upstream controls, which could not be verified without root
privileges during the review. The host had `192.168.87.135/24` on `wlp3s0`,
making `192.168.87.135:4242` a potential LAN path unless blocked. This does not
prove successful external access. A loopback-only web UI does not make the
underlying Reticulum gateway private.

## 9.5 Radio Profile Requirements

Both radio ends must be verified as compatible US915 hardware variants.
Matching SX1262-family radio chips do not guarantee protocol compatibility.

Version-controlled profiles:

```text
/ALWAYSON/config/field/heltec-v3/radio-profile-us915.yaml
/ALWAYSON/config/drone/waveshare-lora/radio-profile-us915.yaml
```

The profiles must define identical or explicitly interoperable values for:

- Frequency or channel plan.
- Bandwidth.
- Spreading factor.
- Coding rate.
- Preamble length.
- Transmit power.
- Sync word or network identifier.
- Packet framing.
- Maximum packet size.
- Encryption key identifier.
- Device public identity.
- Sequence number and replay-protection policy.
- Acknowledgement policy.
- Retry and backoff policy.
- Airtime limits.

Do not describe this system as LoRaWAN unless it implements a true LoRaWAN
device, gateway, and network-server architecture. The field implementation is
primarily an RNode-based Reticulum mesh. The Heltec V3 and Raspberry Pi/Waveshare
radios must use matched, approved US915 channel plans. Any separate LoRaWAN or
public-discussion service must use different radio bands and settings and remain
isolated from the field telemetry mesh.

---

# 10. Simulation Architecture

## 10.1 Vehicle Simulation

```text
ao-sim-vehicle
├── ROS 2 Lyrical
├── Gazebo Sim 10.5.0
├── ArduPilot SITL
├── ROS-Gazebo bridge
├── MAVLink router
├── QGroundControl simulation client
├── Optional Stable-Baselines3 evaluation
├── Mission and scenario runner
└── Vehicle-result exporter
```

```text
ROS_DOMAIN_ID=21
GZ_PARTITION=alwayson_vehicle_sim
```

Vehicle profiles MUST ALLOW FOR SWITCHING BETWEEN THE FOLLOWING, IDEALLY AT RAPID SPEED:

- bicopter profile.
- Fixed-wing VTOL tailsitter profile.
- RoveR (QUADCYCLE) profile.
- Dual-rotating underwater/submersible profile.
- BOAT MAST/SAIL CONTROL PROFILE
- BOAT BOW/STERN THRUSTER PROFILE
- BOAT BOW/STERN AIRBOAT FAN PROFILE
- Wind, terrain, obstacles, routing, takeoff, and landing EVENTS
- Camera, GPS, IMU, barometer, rangefinder, battery, and MAVLink behavior.
- GPS loss, packet loss, actuator faults, sensor drift, and failsafe handling.

Vehicle simulation must never connect to live flight controllers, field radios,
real drone telemetry, payment services, customer records, or Corda core.

## 10.2 Fabrication and Facility Simulation

```text
ao-sim-fabrication
├── ROS 2 Lyrical
├── Gazebo Sim 10.5.0
├── Robot-arm cells and assembly stations
├── 3D-printer cells
├── LPBF cells
├── Storage and inventory cells
├── Refrigerator, freezer, and pantry models
├── Kitchen and pass-through models
├── Carousels and conveyors
├── Facility scheduler
├── Safety-zone and interlock model
└── Fabrication-result exporter
```

```text
ROS_DOMAIN_ID=22
GZ_PARTITION=alwayson_fabrication_sim
```

```text
Storage
   │
   ▼
Carousel or conveyor
   │
   ▼
Robot-arm pickup
   │
   ├── 3D printing
   ├── LPBF process area
   ├── Assembly
   ├── Refrigerator or pantry
   └── Kitchen or pass-through
```

Phase one is simulation only. It must not command live robot arms, printers,
LPBF systems, refrigeration, carousels, kitchen equipment, or other machinery.

Vehicle and fabrication simulation domains require separate:

- Podman networks.
- ROS domain IDs.
- Gazebo partitions.
- DDS configuration.
- Service identities.
- Filesystem mounts.
- Result directories.
- Ledger client certificates.
- Git repositories or clearly separated repository subtrees.
- Artifact manifests.

Use LOCAL FOLDER STORAGE AT /ALWAYSON  AT THE GAZEBO SUBFOLDER (VERIFY ITS LOCATION WITH THE USER) for SDF, URDF/Xacro, world files, robot definitions, safety zones,
task plans, and launch configurations. Use Git LFS or a separate artifact
repository for large meshes, textures, point clouds, and generated results.

---

# 11. Ledger, Provenance, Archive, and IPFS

## 11.1 Ledger Authority Policy

Corda is the authoritative ledger for approved business provenance, receipt,
entitlement, fulfillment-approval, and release-approval records.

Corda is not the authoritative store for domain-operational source data (THAT DATA IS TO BE STORED IN THE RELATED POSTGRESQL DATABASE.)

| Domain | Authoritative operational data |
|---|---|
| Sales | Sales PostgreSQL order, fulfillment, and customer-service records |
| Payment | Verified provider event record and normalized payment state |
| Field | Raw packet store, telemetry spool, and mission records |
| Mapping | Validated imagery, WebODM project data, processing outputs, and deliverables |
| Vehicle simulation | Scenario definitions, run data, and result artifacts |
| Fabrication simulation | Facility/task models, safety scenarios, and result artifacts |
| Archive | Encrypted archive objects and retention records |

Corda records signed references, hashes, approved transitions, and
entitlement/provenance data that permit verification without duplicating
sensitive or high-volume data.

## 11.2 Ledger Flow

```text
Domain event or artifact
      │
      ▼
SHA-256 content hash
      │
      ▼
Signed manifest
      │
      ▼
Ledger-ingestion gateway
      ├── Mutual TLS
      ├── Authorization
      ├── Schema validation
      ├── Signature verification
      ├── Idempotency
      └── Audit logging
              │
              ▼
Corda transaction
              │
              ▼
Receipt, entitlement, provenance, or approval state
```

### 11.2.1 Cross-System Correlation and Provenance Model

The primary business correlation tuple is:

```text
serial_number + receipt_number + event_timestamp_utc
```

These fields link records across PostgreSQL domains and approved ledger records:

- `serial_number` identifies the physical product, vehicle, component, or asset.
- `receipt_number` identifies the approved commercial transaction or receipt.
- `event_timestamp_utc` identifies when the source event occurred, using ISO-8601 UTC.

The tuple should be accompanied by a source event identifier and schema version:

```text
correlation_id
serial_number
receipt_number
event_timestamp_utc
event_type
source_domain
source_record_id
schema_version
content_hash_sha256
```

Example:

```json
{
  "correlation_id": "ORDER-2026-000123-LOT-A",
  "serial_number": "SN-300X3-000042",
  "receipt_number": "RCPT-2026-000123",
  "event_timestamp_utc": "2026-09-25T12:34:56.000Z",
  "event_type": "entitlement_issued",
  "source_domain": "sales",
  "source_record_id": "order-line-000123-01",
  "schema_version": "1.0",
  "content_hash_sha256": "SHA256_DIGEST"
}
```

The same correlation fields should be carried into approved records from sales,
mapping, field, fulfillment, simulation, and release workflows where the event
is relevant. A database view or reporting projection should join the records by
the correlation tuple rather than by free-text names or presentation labels.

### Ledger responsibility: integrity and provenance, not general encryption

Corda/blockchain records should contain the minimum data needed to verify that
an approved event, artifact, receipt, entitlement, or state transition occurred:

```text
serial_number
receipt_number
event_timestamp_utc
event_type
state or status
content_hash_sha256
opaque source reference
signature/authorization metadata
```

The ledger should not contain:

```text
card numbers, CVV, payment secrets, private keys,
full customer PII, raw telemetry, imagery, point clouds,
or large operational payloads
```

Encryption is performed before sensitive data leaves its authoritative store,
for example before pCloud archival replication or private IPFS distribution.
Corda then records the encrypted-object reference and content hash. This gives
integrity and provenance for the encrypted object without putting the plaintext
payload on the ledger.

### Sales and marketing reporting flow

```text
Sales PostgreSQL salesdb
  order, product, serial, receipt, payment, fulfillment, entitlement
        │
        ├── correlation tuple:
        │     serial_number + receipt_number + event_timestamp_utc
        │
        ├── approved read-only reporting views
        │       └── Metabase sales/marketing reports
        │
        ├── Grafana PostgreSQL datasource
        │       └── sales/fulfillment/provenance dashboards
        │
        └── signed minimized manifest
                └── Corda receipt/entitlement/provenance state
```

Marketing and sales reporting should use approved PostgreSQL views or
projections. The reporting layer may join:

```text
product/SKU
serial number
receipt number
order and order-line state
entitlement state
Corda receipt/provenance status
event timestamp
```

It must not infer that a product is fulfilled, entitled, paid, or blockchain-verified
solely from a marketing label. Those states must come from the authoritative
PostgreSQL event and the approved ledger projection.

### Implementation preconditions

Before enabling this flow:

1. Initialize and verify the `salesdb` schema.
2. Define canonical `serial_number`, `receipt_number`, and UTC timestamp fields.
3. Create read-only reporting views for Metabase and Grafana.
4. Define the signed manifest schema and correlation-ID uniqueness rule.
5. Implement ledger-ingest authorization, signature verification, idempotency,
   replay protection, and audit logging.

6. Complete the Corda key/certificate ceremony.
7. Test the complete correlation path with synthetic data before connecting
   real sales, payment, customer, or product records.

### 11.2.2 Mandatory Corda Entry Evidence

Corda entry is blocked until all three evidence classes are present for the same
business correlation record:

1. **Sale-request email**
   - Customer-originated sale/KIT REQUEST email or approved equivalent.
   - Captures requester, requested items/SKUs, comments, and request timestamp.
   - Does not by itself prove a contract or payment.

2. **Payment-validation email**
   - Provider-specific validation for PayPal, Zelle, or Coinbase/stablecoin.
   - Identifies the provider, provider reference, amount, currency, validation
     status, and validation timestamp.
   - Does not by itself prove that funds settled into the approved account.

3. **Funds-transfer verification**
   - Operator/provider reconciliation evidence that the funds actually
     transferred and settled.
   - Records settlement/available state, transfer reference, amount, currency,
     and verification timestamp.
   - Must not be treated as verified merely because a payment was initiated.

The three records must resolve to the same:

```text
correlation_id
receipt_number
serial_number(s)
event_timestamp_utc
```

Recommended evidence record:

```text
evidence_id
evidence_type = sale_request | payment_validation | funds_transfer_verification
provider = website | paypal | zelle | coinbase | bank | manual_reconciliation
source_reference
received_at_utc
validated_by
content_hash_sha256
status = received | validated | rejected | superseded
```

A sale is not eligible for Corda submission unless:

```text
sale_request.status = validated
payment_validation.status = validated
funds_transfer_verification.status = validated
```

Corda records references, hashes, states, and operator authorization for these
three gates; it must not store raw payment credentials or unrestricted email
content. PostgreSQL stores the detailed evidence metadata and reporting
projection. Metabase and Grafana report the resulting confirmed state; they do
not perform or waive the verification.

6. Complete the Corda key/certificate ceremony.
7. Test the complete correlation path with synthetic data before connecting
   real sales, payment, customer, or product records.

### 11.2.3 Corda-Managed Sale and Receipt Process

The detailed process, state machine, correlation model, and activation gate are
maintained in the canonical runbook:

```text
/ALWAYSON/docs/runbooks/corda-sale-receipt-process.md
```

The short rule is:

```text
KIT REQUEST/inquiry
  → verified payment
  → PostgreSQL provisional projection
  → signed sale-contract manifest
  → ledger-ingest gateway
  → Corda transaction/state
  → PostgreSQL final projection
  → receipt and reporting views
```

A receipt is not final until Corda has returned a confirmed transaction/state
reference and the PostgreSQL projection records that reference. The intake,
form, schema, and validator artifacts are:

```text
/ALWAYSON/data/sales/kit-request-intake/
/ALWAYSON/forms/three-column-corda-sale-receipt-form.html
/ALWAYSON/forms/three-column-corda-sale-receipt-form.pdf
/ALWAYSON/forms/corda-sale-receipt.html
/ALWAYSON/config/sales/sale-receipt.schema.json
/ALWAYSON/config/sales/sale-receipt.example.json
/ALWAYSON/scripts/validation/validate-sale-receipt.sh
```

The form is an internal operator form. It does not write to PostgreSQL, contact
Corda, process payments, or create a public proof. Submission must go through
the authorized ledger-ingest workflow after operator review.


## 11.3 Corda Stores and Private Data

Corda may retain approved private transaction data as an encrypted private
payload or encrypted attachment. Corda does not make plaintext private data
safe merely by being on a ledger: confidentiality depends on encryption,
authorized recipients, key management, access policy, and audit controls.

### Corda contract state

Corda state should contain the small, shared, verifiable business facts:

```text
transaction_id
correlation_id
receipt_number
order_id
serial_number(s)
sku
model_object_id / model_revision_id
payment provider
payment-validation reference/hash
funds-transfer reference/hash
payment/settlement state
entitlement/fulfillment/delivery state
Corda transaction ID
timestamps
signatures/authorization metadata
```

### Encrypted private payload

Approved private data may be encrypted before submission and stored as a
private attachment or confidential private-state object:

```text
customer identity and contact details
purchase-request email/content
payment-validation email/content
funds-transfer verification content
full receipt and contract
fulfillment, delivery, return, and support records
private 3D model files and attachments
```

The private payload envelope must include:

```text
transaction_id
data_classification = PRIVATE
schema_version
encryption algorithm
encryption key identifier
authorized recipients
payload SHA-256
retention policy identifier
created_at_utc
```

The encryption key must be held by the approved KMS/wallet/key-management
process and must never be stored in Corda, PostgreSQL, Git, HTML, logs, or the
transaction bundle.

### Never store in Corda

```text
card numbers
CVV
bank credentials
payment-provider secret keys
passwords
OAuth tokens
private keys
TLS private keys
KMS master keys
data-encryption keys
recovery phrases
```

Corda tracks the transaction ID, state, hashes, references, and authorized
signatures. PostgreSQL retains the operational/reporting projection keyed by
the same transaction ID. Metabase and Grafana report the confirmed state; they
do not create or waive payment verification.


## 11.4 Corda Does Not Store

Corda may store approved encrypted private transaction data as described in
Section 11.3. It must never store plaintext secrets or unencrypted credentials.

Never store:

```text
card numbers
CVV
bank credentials
payment-provider secret keys
passwords
OAuth tokens
private keys
TLS private keys
KMS master keys
data-encryption keys
recovery phrases
```


## 11.5 Manifest Format

```json
{
  "object_id": "UUID",
  "object_type": "sales_receipt | telemetry_batch | map_product | vehicle_simulation | fabrication_simulation",
  "origin_domain": "sales | field | mapping | sim_vehicle | sim_fabrication",
  "created_at_utc": "ISO-8601 UTC timestamp",
  "schema_version": "1.0",
  "content_hash_sha256": "HEX_DIGEST",
  "content_size_bytes": 0,
  "local_storage_reference": "opaque internal reference",
  "ipfs_cid": "optional encrypted CID",
  "pcloud_archive_reference": "optional opaque encrypted reference",
  "authorization_policy_id": "policy ID",
  "producer_key_id": "service key ID",
  "signature": "detached signature"
}
```

## 11.6 pCloud and IPFS Rules

```text
Local source data
      │
      ├── Content hash
      ├── Signed manifest
      ├── Corda receipt or approval state
      ├── Encrypted pCloud archive
      └── Private or encrypted IPFS distribution
```

- Local source data remains authoritative.
- Encrypt before pCloud archival replication unless an explicitly approved
  equivalent encryption control applies.
- Do not place private data, PII, payment data, private keys, raw telemetry,
  sensitive imagery, or proprietary technical designs on public IPFS.
- Use a private IPFS swarm, controlled pinning, or encryption before IPFS for
  sensitive artifacts.
- Record content hash and CID separately.
- Store only CIDs and encrypted archive references in Corda.
- Archive replication occurs only through `ao-egress-archive`.

---

# 12. Host Installation and Configuration

## 12.1 Installation Journal

Create the journal before installation activity:

```bash
sudo install -d -m 0750 -o "$USER" -g "$USER" /ALWAYSON/logs/installation
touch /ALWAYSON/logs/installation/agent-install.log
chmod 0640 /ALWAYSON/logs/installation/agent-install.log
```

## 12.2 Initial Non-Destructive Inventory

Run before installing or changing anything:

```bash
{
  echo "===== Timestamp ====="
  date --iso-8601=seconds

  echo "===== Host ====="
  hostnamectl

  echo "===== OS ====="
  cat /etc/os-release

  echo "===== Kernel ====="
  uname -a

  echo "===== CPU / RAM ====="
  lscpu
  free -h

  echo "===== Storage ====="
  lsblk -o NAME,SIZE,FSTYPE,FSVER,LABEL,UUID,MOUNTPOINTS
  df -hT

  echo "===== Photogrammetry Mount ====="
  findmnt /media/scottw/500GBPHOTOGRAM || true

  echo "===== Podman ====="
  command -v podman || true
  podman version 2>&1 || true
  podman info 2>&1 || true

  echo "===== systemd ====="
  systemd --version

  echo "===== cgroups ====="
  stat -fc %T /sys/fs/cgroup

  echo "===== GPU ====="
  lspci -nnk | grep -A3 -Ei 'VGA|3D|NVIDIA' || true
  command -v nvidia-smi && nvidia-smi || true

  echo "===== Network ====="
  ip -brief address
  ss -tulpn
  ss -tulpn6

  echo "===== Firewall ====="
  sudo ufw status verbose 2>&1 || true
  sudo nft list ruleset 2>&1 || true

  echo "===== Existing systemd services ====="
  systemctl --user list-unit-files --type=service 2>&1 || true

  echo "===== Existing containers: current user ====="
  podman ps -a 2>&1 || true

  echo "===== Existing containers: system store ====="
  sudo podman ps -a 2>&1 || true

  echo "===== Existing Podman networks: current user ====="
  podman network ls 2>&1 || true

  echo "===== Existing Podman networks: system store ====="
  sudo podman network ls 2>&1 || true

  echo "===== Reticulum and MeshChatX ====="
  command -v rnsd || true
  rnsd --version 2>&1 || true
  pgrep -a -f 'rnsd|ReticulumMeshChatX' || true
  ss -ltnp 2>/dev/null | grep -E '(:18000|:4242)' || true

  if [ -f "$HOME/.reticulum/config" ]; then
    echo "--- Reticulum configuration ---"
    grep -nE '^\[\[|^type =|^(interface_enabled|enabled) =|^target_host =|^target_port =|^port =|^mode =' \
      "$HOME/.reticulum/config"
  fi

  if [ -d "$HOME/.reticulum-meshchatx/logs" ]; then
    echo "--- Recent MeshChatX errors and warnings ---"
    tail -n 500 "$HOME/.reticulum-meshchatx/logs/meshchatx.log" \
      | grep -Ei 'error|warning|disabled|interface|umsgpack' || true
  fi

  echo "===== Serial devices ====="
  ls -l /dev/serial/by-id/ 2>&1 || true
} | tee -a /ALWAYSON/logs/installation/agent-install.log
```

Pause and report if:

- The photogrammetry drive is not mounted.
- The mountpoint is an ordinary root-filesystem directory.
- Mapping storage is below 100 GB free.
- Existing WebODM, Podman, Docker, Corda, PostgreSQL, ROS, Gazebo, or related
  services conflict.
- NVIDIA driver state is broken.
- cgroups v2 or the selected Podman runtime mode does not work.
- Firewall policy conflicts with intended isolation.
- A proposed service port is already bound.
- Heltec cannot be found through a stable `/dev/serial/by-id/` path.
- MeshChatX or Reticulum is unexpectedly absent after installation approval.
- The Reticulum configuration contains an interface not present in the approved
  inventory.
- A supposedly enabled interface repeatedly fails without a documented
  compensating control.
- The Reticulum gateway listener is reachable from an unapproved network.
- MeshChatX reports persistence, cryptographic-state, or repository-integrity
  errors.

## 12.3 Host Dependencies

After inventory review and explicit operator approval:

```bash
sudo apt update

sudo apt install -y \
  podman \
  uidmap \
  slirp4netns \
  fuse-overlayfs \
  containernetworking-plugins \
  nftables \
  ufw \
  git \
  curl \
  jq \
  ca-certificates \
  gnupg \
  openssl \
  restic \
  smartmontools \
  lm-sensors \
  acl \
  python3 \
  python3-venv \
  python3-pip
```

Verify:

```bash
podman version
podman info --debug
systemctl --user status
loginctl show-user "$USER" -p Linger
test "$(stat -fc %T /sys/fs/cgroup)" = "cgroup2fs" && echo "cgroups v2 active"
sudo aa-status || true
```

---

# 13. Podman Runtime and Quadlet Policy

## 13.1 Rootless and System-Level Podman

Ordinary application workloads should use rootless Podman and user-level
Quadlet units.

Rootless Quadlet definitions are normally stored in:

```text
~/.config/containers/systemd/
```

System-level Quadlet definitions are stored in:

```text
/etc/containers/systemd/
```

System-level services are permitted only where a documented host-hardware,
GPU, storage, networking, or service-management requirement makes rootless
operation unsuitable.

## 13.2 Approved Deviation: Mixed Podman Stores

**Architecture requirement:** Rootless Podman is the preferred default for
ordinary workloads.

**Current implementation:** Mapping smoke-test evidence indicates that at least
some WebODM operations executed through the system/rootful Podman store. The
evidence includes root-owned mapping backup artifacts and system-side container
storage. An empty `podman ps -a` result from an operator shell does not mean
system-store containers, images, volumes, or networks are absent.

**Compensating controls:**

- No `--privileged` containers.
- Internal mapping network only.
- Explicit bind mounts limited to approved mapping paths.
- Pinned image digests.
- systemd resource limits and restart policy.
- Validated NVIDIA CDI access only where required.
- No direct public listener.
- Backup and restore evidence retained.

**Resolution condition:** Before production declaration, record the approved
steady-state model for every domain: rootless, system-level, or mixed. Record
the unit owner, Quadlet location, storage path, network owner, GPU access
method, and rationale.

## 13.3 `/ALWAYSON` Layout

```text
/ALWAYSON/
├── README.md
├── VERSION
├── docs/
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
│   ├── archive/
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
│   ├── mastodon/
│   ├── pcloud/
│   └── ipfs/
├── secrets/
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

Initialize source control:

```bash
cd /ALWAYSON
git init
git branch -M main

cat > .gitignore <<'EOF'
secrets/
data/
logs/
tmp/
backups/
pcloud/restore-cache/
EOF

git add .gitignore
git commit -m "Initialize ALWAYS ON configuration repository"
```

## 13.4 Quadlet Network Template

```ini
# /ALWAYSON/quadlet/networks/ao-mapping.network
[Network]
NetworkName=ao-mapping
Driver=bridge
Internal=true
```

## 13.5 Quadlet Service Template

```ini
# /ALWAYSON/quadlet/mapping/webodm-web.container
[Unit]
Description=ALWAYS ON WebODM Web Service
After=network-online.target
Wants=network-online.target

[Container]
Image=REPLACE_WITH_APPROVED_IMAGE_DIGEST
ContainerName=webodm-web
Network=ao-mapping.network
Volume=/media/scottw/500GBPHOTOGRAM/webodm/media:/webodm/app/media:Z
Volume=/ALWAYSON/config/mapping/webodm:/config:ro,Z
NoNewPrivileges=true

[Service]
Restart=on-failure
RestartSec=15
MemoryMax=12G
CPUQuota=600%
TimeoutStartSec=180

[Install]
WantedBy=default.target
```

This is a structural template only. The exact image, API settings, mounts,
service name, environment, and GPU configuration must be taken from the tested
and approved WebODM version.

---

# 14. Secrets, Service Identity, and Version Controls

## 14.1 Secret Delivery

Use Podman secrets or systemd credentials. Prefer file-based secret delivery
rather than environment variables.

| Secret | Authorized domain |
|---|---|
| Sales database password | Sales only |
| Payment webhook secret | Payment verifier only |
| Payment-provider API secret | Payment adapter only |
| Mastodon OAuth credential | Community adapter only |
| Local AI credential/configuration if required | AI service only |
| Field radio key | Field only |
| Drone signing key | Drone device only |
| Corda certificates and keystores | Ledger core only |
| Ledger client certificates | One distinct certificate per exporter/domain |
| pCloud archive credential | Archive adapter only |
| IPFS private-swarm/pinning credential | Archive adapter only |

Example:

```ini
[Container]
Secret=sales_db_password,target=/run/secrets/db_password,uid=10001,gid=10001,mode=0400
```

KDE Wallet may hold interactive operator credentials, but unattended production
services must use systemd credentials, Podman secrets, or approved
service-specific secret files. Secret rotation, revocation, expiration, and
recovery procedures must be documented before production use.

### 14.1.1 KDE Wallet Secret Management (Implemented)

KDE Wallet is the operator-side secret and credential store for this host.
This subsection records the implemented integration; the Section 14.1 policy
above remains authoritative, and the unattended-delivery deviation is tracked
in Section 18 (Open Decisions).

Runtime and tooling:

- Wallet daemon: `kwalletd6` (also registers the `org.kde.kwalletd5` D-Bus
  name for compatibility; both names refer to the same daemon). Wallet:
  `kdewallet`, auto-unlocked with the operator's Plasma login.
- Management CLI: `scripts/ops/kwallet-provision.sh` (`create-folders`,
  `put`, `get`). Run only from the interactive Plasma session while the
  wallet is unlocked.
- Boot-time delivery: `scripts/operations/fetch-kwallet-secret.sh` runs as a
  Quadlet `ExecStartPre`, waits for the desktop session and kwalletd (max
  ~60s), reads the required entries, and writes a service-specific `0600`
  env file under the unit owner's `~/secrets/` for the unit to consume via
  `--env-file`. Used by `ao-mastodon-db`, `ao-sales-db`, and
  `ao-webodm-db` (verified at boot; see the installation journal).

Wallet layout (folder: purpose):

| Folder | Purpose |
|---|---|
| `ALWAYSON` | Boot-time delivery entries consumed by Quadlet units |
| `ao-mastodon` | Local 300X3 Mastodon application secrets (Section 15.3) and Tokodon/OpenClaw OAuth material (WORK 000010) |
| `ao-sales`, `ao-payment`, `ao-field`, `ao-mapping`, `ao-ledger`, `ao-archive`, `ao-admin`, `ao-sim-vehicle`, `ao-sim-fabrication` | Per-domain credential folders matching the Section 14.1 authorized-domain table (provisioned empty 2026-08-31) |

Current entry inventory (names only; values never in Git, logs, or docs):

| Folder | Entries |
|---|---|
| `ALWAYSON` | `mastodon-db-password`, `sales-db-password`, `webodm-postgres-password` |
| `ao-mastodon` | `mastodon-secret-key-base`, `mastodon-otp-secret`, `mastodon-db-password`, `mastodon-ar-deterministic-key`, `mastodon-ar-primary-key`, `mastodon-ar-derivation-salt`, `mastodon-admin-password`, `tokodon-client-id`, `tokodon-client-secret`, `openclaw-bot-client-id`, `openclaw-bot-client-secret`, `openclaw-bot-access-token`, `openclaw-bot-password`, `roundtrip`/`roundtrip2` (test artifacts) |

Rules:

- Never print, copy, export, or log entry values; confirm presence only
  (same rule as WORK 000040). Presence checks use the D-Bus
  `entryList`/`hasEntry` methods on `org.kde.kwalletd6`.
- Entries are named per service and per purpose; domain folders enforce the
  Section 14.1 authorized-domain boundaries.
- Rotation, revocation, expiration, and recovery procedures must be
  documented before production use (Section 14.1 requirement).

## 14.2 Version Matrix

Maintain:

```text
/ALWAYSON/config/platform/version-matrix.yaml
```

```yaml
host:
  os_release: ""
  kernel: ""
  systemd: ""
  podman: ""
  quadlet_capability: ""
  netplan: ""
  nftables: ""
  ufw: ""

gpu:
  model: "EVGA NVIDIA GTX 1080"
  nvidia_driver: ""
  container_runtime_integration: ""
  cuda_runtime_image_digest: ""

mapping:
  webodm_image_digest: ""
  nodeodm_image_digest: ""
  postgresql_version: ""
  redis_version: ""
  processing_profiles_commit: ""

simulation:
  ros2_distribution: "lyrical"
  gazebo_release: "10.5.0"
  ardupilot_commit: ""
  qgroundcontrol_version: ""
  sb3_version: ""
field_chat:
  standalone_rnsd_version: "1.4.2"
  standalone_rnsd_executable: "/home/scottw/.local/bin/rnsd"
  standalone_rnsd_running: false
  active_reticulum_runtime: "embedded in MeshChatX native backend"
  active_embedded_rns_version: "unverified"
  reticulum_config: "/home/scottw/.reticulum/config"
  reticulum_config_sha256: "2df6a8d9fc2037d9e316ac910ec1721c3b5b6af5e301a50b0e92656226cc4098"
  meshchatx_launcher_metadata_version: "4.9.1"
  meshchatx_running_version: "unverified"
  meshchatx_executable: "/home/scottw/Applications/meshchatx-native/ReticulumMeshChatX"
  meshchatx_executable_sha256: "4f403e52b0a5722a49d433f23660b14b43a779fb3cc9a5a90b8f150d77f18890"
  meshchatx_manifest_sha256_match: true
  meshchatx_storage: "/home/scottw/.reticulum-meshchatx"
  meshchatx_local_ui: "127.0.0.1:18000"
  reticulum_public_listener: "0.0.0.0:4242"
  repository_cached_artifact: "reticulum_meshchatx-4.8.4-py3-none-any.whl"
  repository_cached_artifact_running: false
  people_radio:
    hardware: "Heltec WiFi LoRa 32 V3 / SX1262"
    rnode_firmware: "1.85"
    frequency_hz: 915000000
    bandwidth_hz: 125000
    spreading_factor: 7
    coding_rate: 5
    txpower_dbm: 17
  drone_radio:
    hardware: "Heltec WiFi LoRa 32 V3 / SX1262"
    rnode_firmware: "1.85"
    frequency_hz: 917000000
    bandwidth_hz: 250000
    spreading_factor: 7
    coding_rate: 5
    txpower_dbm: 17
    mode: "internal"
    discoverable: false

ledger:
  corda_version: ""
  cordapp_hashes: ""
  postgres_version: ""
  certificate_profile_version: ""
```

---

# 15. Sales, Mastodon, OpenClaw, and Local AI

## 15.1 Sales Database

Use a dedicated sales PostgreSQL database with separate roles:

```text
salesdb
sales_api_role
sales_migration_role
sales_backup_role
sales_reporting_role
sales_admin_role
```

The desktop metadata reports MeshChatX `4.9.1`. The native executable hash
matches `backend-manifest.json`, but its running version was not independently
established. A `reticulum_meshchatx-4.8.4-py3-none-any.whl` artifact also exists
in the local MeshChatX repository-server identity and is not the verified
running artifact.

Core tables:

```text
customers
customer_contacts
products
product_versions
orders
order_lines
payment_provider_events
payment_references
receipts
fulfillment_events
entitlements
returns
support_cases
audit_events
```

### 15.1.1 Three-Form Transaction Bundles

Every purchase transaction uses one ALWAYS ON-issued transaction ID and one
folder containing three forms:

```text
/ALWAYSON/data/sales/transactions/<transaction-id>/
├── 01-purchase-request.html
├── 02-payment-confirmation.html
├── 03-receipt.html
├── BUNDLE-STATUS.txt
└── provider-evidence/
    ├── paypal.*
    ├── zelle.*
    └── coinbase.*
```

Issue a new bundle:

```bash
/ALWAYSON/scripts/sales/issue-transaction-bundle.sh
```

The issuer creates a unique ID, pre-fills that ID into all three forms, and
creates the provider-evidence directory. The three forms are:

1. Purchase request.
2. Payment confirmation, including provider validation and funds-transfer
   settlement.
3. Corda receipt, including the three evidence references and Corda state.

Validate the bundle structure:

```bash
/ALWAYSON/scripts/sales/validate-transaction-bundle.sh \
  /ALWAYSON/data/sales/transactions/<transaction-id>
```

The same issued ID must appear in all three forms and in the bundle status. It is
also required in the Corda sale-receipt event and the PostgreSQL contract
projection. Payment validation must distinguish provider validation from funds
settlement, and the receipt must record the three validated evidence references
before operator handoff to ledger-ingest.

Corda tracks the transaction ID, payment/ledger state, hashes, and approved
references. Detailed private data remains in the encrypted PostgreSQL
projection keyed by the same transaction ID; Corda does not store full customer
records, raw emails, payment credentials, or unrestricted evidence.



### 15.1.2 Website KIT REQUEST PDF Intake

Website-generated PDF requests are accepted at:

```text
/ALWAYSON/data/sales/kit-request-intake/
```

The current `300x3.com` KIT REQUEST flow composes an email with:

```text
SUBJECT: 300X3-WEBREQUEST-
NAME: <name>
EMAIL: <email>
KIT REQUESTED: <selected kits>
COMMENTS: <comments>

THIS IS A REQUEST FOR INFORMATION, NOT A CONTRACT
```

The intake folder separates requests from sales:

```text
inbox/       Original PDFs placed for intake
extracted/   Extracted text
manifests/   Hashes and intake metadata
receipts/    Final receipts/contracts only after Corda confirmation
review/      Human review records
archive/     Preserved processed request PDFs
quarantine/  Invalid, duplicate, or sensitive-pattern PDFs
```

Run the non-destructive intake script:

```bash
/ALWAYSON/scripts/sales/intake-kit-request-pdf.sh \
  /ALWAYSON/data/sales/kit-request-intake/inbox/<request>.pdf
```

The script preserves and hashes the PDF, extracts text, creates a review record,
and explicitly sets:

```text
classification=kit_request_inquiry
sale_logged=false
corda_state=NOT_SUBMITTED
```

It never treats a website request as payment, creates an order, or submits a
Corda transaction. A verified payment event is required before the PostgreSQL
sale projection is created. A final receipt requires a Corda-confirmed
transaction/state reference written back to PostgreSQL. Metabase and Grafana
read the resulting approved projections; they do not create the sale.

## 15.2 Community and AI Controls

Mastodon/community controls:

- Dedicated OAuth registration.
- Minimum necessary scopes.
- External access only through `ao-egress-community` when explicitly enabled.
- Rate limits.
- Separate approval workflow.
- Immutable publication audit log.
- No payment, field, mapping, simulation, or Corda-core access.

OpenClaw uses the local LM Studio model for support drafting and the deployed
`mastodon-openclaw-bridge.service` automatically answers new Mastodon mentions
and replies as `bot`. The bridge polls the local Mastodon API every 10 seconds,
persists its notification cursor, skips historical notifications and its own
posts, and posts threaded public replies locally. It does not publish to any
other service. Human approval remains required for pricing, orders, shipping,
warranties, financial topics, technical claims, safety guidance, legal
statements, and any publication outside the local bridge workflow.

## 15.3 Local 300X3 Mastodon Deployment

The 300X3 Mastodon instance (Mastodon 4.3.7, containerized in the authoritative
`alwayson-sales` rootless Podman store) is publicly federated at
**`https://mastodon.300x3.com`**. The main storefront remains on
`https://300x3.com` and `https://www.300x3.com`; it is not routed to Mastodon.
Operators use Tokodon and OpenClaw on the desktop.

Architecture requirements and verified state:

- `ao-sales` remains `Internal=true` and contains the Mastodon database, Redis,
  streaming service, and web origin. Database and Redis are not attached to
  the egress network.
- `ao-egress-community` is a separate non-internal bridge attached only to
  `mastodon-web` and `mastodon-sidekiq`. It provides controlled outbound
  federation delivery; no database, Redis, or streaming container is attached.
- Origin web and streaming remain loopback-only: `127.0.0.1:3000` and
  `127.0.0.1:4000`.
- The sole public Mastodon entry is the dedicated Cloudflare Tunnel hostname
  `mastodon.300x3.com`, routed to `127.0.0.1:3000` by
  `cloudflared-alwayson.service`. The storefront hostnames are excluded from
  the Mastodon tunnel and retain the filedn redirect behavior.
- Mastodon identity is `LOCAL_DOMAIN=mastodon.300x3.com`. The local user
  records retain login emails `admin@300x3.com` and `bot@300x3.com`, while
  their canonical ActivityPub identities are
  `admin@mastodon.300x3.com` and `bot@mastodon.300x3.com`.
- Public actor and WebFinger endpoints were verified at
  `https://mastodon.300x3.com/actor` and
  `https://mastodon.300x3.com/.well-known/webfinger`.
- The tunnel currently uses HTTP/2 transport because QUIC stream timeouts were
  observed on this host. Local and public health checks returned HTTP 200.
- Open registration remains enabled with the approval gate; approval applies
  to new account registration, not to following an existing local account.
- No passwords, OAuth secrets, API keys, tunnel credentials, or access tokens
  are committed to Git or recorded in this README.

## 15.4 Federation Publication of the Local 300X3 Instance

**Category:** In progress (WORK 000060; started 2026-09-22). Approved design
for joining the fediverse as the 300X3 instance so that public posts from the
local deployment appear on external Mastodon servers, including
`mastodon.social`.

Federation is a mutual, inbound-and-outbound protocol: remote servers
(including `mastodon.social`) must reach this instance over the public
internet using HTTPS, and this instance must be able to deliver outbound
activity to remote inboxes. The former loopback-only validation stage
(Section 15.3) has been superseded: the Cloudflare Tunnel edge
**Status:** Implemented and operational on the dedicated federation hostname
(WORK 000060, 2026-09-24). Federation is publicly reachable at
`https://mastodon.300x3.com`; the main storefront remains on the apex/`www`
hostnames and is not routed to Mastodon.

### 15.4.1 Architecture Requirements

Identity is verified against the live instance: WebFinger and
`/api/v1/instance` both report `mastodon.300x3.com`, while `300x3.com` serves
the static storefront. The `scottw` and `alwayson-sales` service accounts are
separated so the desktop user cannot start a second Mastodon (Section 20.0).
Open configuration drift against these values is tracked in ISSUE 000600.

| Area | Architecture requirement |
|---|---|
| Public instance domain | Dedicated `mastodon.300x3.com`; canonical handles are `user@mastodon.300x3.com`. The storefront hostnames remain separate. |
| Storefront preservation | `300x3.com` and `www.300x3.com` retain the filedn static-site redirect; Mastodon is not deployed under a `/mastodon` subpath. |
| TLS | Required at the public edge; Cloudflare terminates TLS for `mastodon.300x3.com`. |
| Inbound reachability | Cloudflare Tunnel connector `cloudflared-alwayson.service` routes only the dedicated hostname to `127.0.0.1:3000`. |
| Outbound reachability | `mastodon-web` and `mastodon-sidekiq` use `ao-egress-community` for federation delivery; database, Redis, and streaming remain isolated on `ao-sales`. |
| Isolation | `ao-sales` remains `Internal=true`; no database, Redis, or raw origin listener is publicly exposed. |
| Secrets | Tunnel credentials and API keys remain in protected runtime secret storage; never in Git or this README. |
| Operator duties | Registration approval, moderation, reports, and blocklists remain operator responsibilities. |
| Service-account placement | The 5 Mastodon containers run under `alwayson-sales` (UID 993) in a **separate rootless store and systemd user manager**, not under `scottw`. `ao-mastodon-web.service` / `ao-mastodon-streaming.service` are masked in the `scottw` manager to prevent a duplicate instance (ISSUE 000600). |

### 15.4.2 Domain and Mastodon Identity Configuration

Environment changes applied to the authoritative service-account
`mastodon.env` on 2026-09-24:

```text
LOCAL_DOMAIN=mastodon.300x3.com
LOCAL_HTTPS=true
RAILS_FORCE_SSL=false  # Cloudflare edge terminates public TLS
ALTERNATE_DOMAINS=localhost,127.0.0.1
```

- Login emails remain `admin@300x3.com` and `bot@300x3.com`.
- Canonical ActivityPub identities are
  `admin@mastodon.300x3.com` and `bot@mastodon.300x3.com`.
- WebFinger and actor JSON were verified through the public federation
  hostname.
- The main storefront remains on `300x3.com` / `www.300x3.com`.
- No `/mastodon` path deployment is used; the dedicated hostname provides the
  root paths required by ActivityPub.

### 15.4.3 Edge, TLS, and Network Path

Implemented path (2026-09-22, operator-approved Cloudflare Tunnel variant;
workstation-nginx + Let's Encrypt variant below superseded — see
Section 18.5):

```text
Remote fediverse servers
        │ HTTPS 443
        ▼
Cloudflare edge: mastodon.300x3.com
        │ HTTP/2 tunnel (QUIC disabled after observed stream timeouts)
        ▼
cloudflared-alwayson.service
        │ 127.0.0.1:3000
        ▼
mastodon-web

mastodon-web + mastodon-sidekiq
        │ ao-egress-community
        ▼
Remote ActivityPub/WebFinger endpoints
```

The storefront hostnames are not included in this tunnel ingress. Tunnel
credentials remain in protected runtime storage and are never committed.

```text
Superseded design (retained for history): workstation nginx
  - listen 443 ssl; Let's Encrypt certificate (DNS-01)
  - port 80 only as ACME/redirect listener
  Not required with the tunnel path: edge TLS is provided by Cloudflare
  and the origin stays loopback-only (Section 18.5).
```

TLS requirements:

- TLS is mandatory at the edge for all federation traffic (satisfied by
  Cloudflare edge termination for the tunnel-routed apex hostname).
- Tunnel credentials and origin certificate are stored 0400 under
  `~/.cloudflared/` and mirrored to KDE Wallet `ao-mastodon`; never in
  Git or this README. Revoke by deleting/re-creating the tunnel.
- `X-Forwarded-Proto: https` is supplied by cloudflared so Rails
  generates HTTPS URLs and Secure cookies (validated: instance JSON
  reports `streaming_api: wss://300x3.com`).

Outbound delivery path:

- Sidekiq delivers public activities to remote inboxes over HTTPS/443.
- Egress is restricted to `ao-egress-community` (Section 3) with HTTPS as
  the only approved protocol; no broad network membership.
- Rate and retry behavior are Mastodon defaults; no relay subscription is
  approved unless explicitly decided.

### 15.4.4 Federation Enablement Sequence

Status as of 2026-09-24:

1. **Done** — dedicated Cloudflare Tunnel `alwayson-mastodon-federation` and
   DNS route for `mastodon.300x3.com` created; storefront hostnames excluded.
2. **Done** — Cloudflare redirect rule narrowed to exclude
   `mastodon.300x3.com`; the static storefront redirect remains unchanged.
3. **Done** — Mastodon identity set to `LOCAL_DOMAIN=mastodon.300x3.com`;
   actor, WebFinger, and local actor documents verified.
4. **Done** — `ao-egress-community` attached to web/Sidekiq only; database,
   Redis, and streaming remain isolated.
5. **Done** — tunnel transport switched to HTTP/2 after QUIC stream timeouts;
   local and public health checks return HTTP 200.
6. **Done** — `@300x3@mastodon.social` resolved; public followers collection
   confirms both local accounts follow it.
7. **Done** — public post fetched; local mention records created and native
   notification processing repaired.
8. **Pending** — verify reverse follows using the remote following collection
   and local incoming relationship tables, then perform a fresh signed
   ActivityPub round-trip test.
6. **Pending (after step 2)** — bootstrap discovery: from Tokodon signed
   in at `https://300x3.com`, follow at least one account on
   `mastodon.social`. Remote servers do not index this instance until
   first contact occurs.
7. **Pending** — validate public-post delivery to `mastodon.social` and
   reply/boost round-trips back to the local instance; then submit
   `300x3.com` to the joinmastodon.org directory (operator-approved).

### 15.4.5 Operational Boundaries After Enablement

- Only `public` visibility federates; `unlisted`, `private`, and
  `direct` do not appear on remote servers' explore pages. The OpenClaw
  draft-by-default and human-approval controls (Sections 3.8 and 15.2)
  remain mandatory for all public publication.
- `post.sh` public-post guard remains the script-level approval gate.
- Federated deletion is best-effort: remote servers may retain cached
  copies. Content published under this section must be treated as
  practically irreversible.
- Publication audit logging (immutable, Section 15.2) must include the
  remote-delivery outcome for federated statuses.

---

# 16. Scripts and Operational Standards

## 16.1 Scripts Layout

```text
/ALWAYSON/scripts/
├── bootstrap/
│   ├── 00-inventory.sh
│   ├── 01-verify-photogrammetry-mount.sh
│   ├── 02-install-host-dependencies.sh
│   ├── 03-create-operational-layout.sh
│   └── 04-create-podman-networks.sh
├── deploy/
│   ├── deploy-quadlet-domain.sh
│   ├── validate-quadlet-domain.sh
│   ├── enable-domain-services.sh
│   └── rollback-domain.sh
├── validation/
│   ├── check-photogrammetry-mount.sh
│   ├── check-open-ports.sh
│   ├── check-network-isolation.sh
│   ├── check-secrets-exposure.sh
│   ├── check-gpu-runtime.sh
│   ├── check-ledger-ingest.sh
│   └── capture-version-matrix.sh
├── mapping/
├── radio/
├── simulation/
├── storefront/
├── ledger/
├── backup/
├── restore/
└── maintenance/
```

## 16.2 Script Standard

Every script begins with:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'
```

Every script must:

- Use absolute paths.
- Validate prerequisites.
- Log in UTC.
- Avoid secrets.
- Support `--dry-run` for external or destructive activity.
- Use locks where concurrent invocation could corrupt data.
- Return meaningful exit codes.
- Avoid `eval`.
- Avoid unexamined `|| true`.
- Validate canonical paths before move or delete activity.
- Verify the photogrammetry mount before mapping activity.
- Refuse to delete outside explicitly approved and validated paths.
- Write an audit entry for operational changes.

---

# 17. Backup, Restore, Monitoring, and Completion Criteria

## 17.1 Backup and Restore Policy

Use a 3-2-1 strategy: three copies, two media types, and one off-host/off-site
copy.

| Frequency | Required activity |
|---|---|
| Continuous or 15-minute where enabled | Database WAL/archive strategy for critical recovery objectives |
| Hourly incremental | Configuration, manifests, sales records, field telemetry, current project data |
| Daily | PostgreSQL dumps for `salesdb`, `mastodon`, `webodm`, `grafana`, and `metabase` when active; Corda backup; mapping manifests; simulation exports; storefront releases |
| Weekly | Repository integrity check and off-host copy validation |
| Monthly | Isolated restore test |
| Quarterly | Full disaster-recovery exercise |

Restore testing must:

1. Restore to an isolated test path or test host.
2. Validate database integrity.
3. Recalculate artifact hashes.
4. Compare hashes with stored manifests.
5. Verify associated Corda receipt/manifests where available.
6. Record operator, source backup ID, result, and exceptions.
7. Alert on failure.

## 17.2 Monitoring

Monitoring runs in `ao-admin` and is exposed only through VPN or authenticated
administration access.

Monitor at minimum:

| Component | Required metrics |
|---|---|
| Host | CPU, RAM, storage health, disk usage, temperature, GPU state, kernel errors |
| Podman/systemd | Unit state, restart loops, health, image digest |
| Mapping | Queue depth, failures, duration, disk space, CPU/GPU use |
| Field | Packet rate, RSSI, SNR, retries, replay rejections, spool depth, gateway uptime |
| Sales | Payment-verification failures, receipt failures, orders, API latency |
| AI/community | Model latency, request count, GPU use, approval queue, OAuth failures |
| Vehicle simulation | Scenario success, SITL/ROS/Gazebo health, result export |
| Fabrication simulation | Task state, collision/safety events, result export |
| Ledger | Corda health, ingest failures, certificate expiry, backup age |
| Backup | Last success, repository health, restore-test result, queue age |

Alerts must cover disk pressure, backup failure, failed restore tests, container
restart loops, unexpected listeners, failed payment verification, radio
disconnection, WebODM backlog, GPU contention, expired certificates, and denied
cross-domain traffic.

## 17.3 Completion Evidence

No installation or deployment agent may claim completion until it produces:

1. Host inventory report.
2. Photogrammetry-drive report with mount source, UUID, filesystem, free space,
   ownership, and permission validation.
3. Installed package and version matrix.
4. Rootless and/or system Podman/Quadlet verification.
5. GPU driver and container-runtime validation.
6. Podman network list and domain-isolation results.
7. IPv4 and IPv6 firewall/listening-port report.
8. WebODM CPU-only smoke-test result using the dedicated drive.
9. Vehicle-simulation smoke-test result.
10. Fabrication-simulation smoke-test result.
11. Heltec stable serial-device detection and LoRa-link test result.
12. Ledger-ingestion test and Corda receipt result.
13. Sales receipt-manifest test without payment secrets.
14. Backup execution result.
15. At least one isolated restore-test result.
16. A current list of unresolved blockers, deviations, risks, and actions
    requiring human approval.

---

# 18. Approved Deviations and Open Decisions

## 18.1 Simulation Baseline Deviation

**Decision:** ROS 2 Lyrical and Gazebo Sim 10.5.0 are the installed baseline.

**Status:** Approved on 2026-08-24.

**Rationale:** The installed and smoke-tested environment differs from an
earlier Jazzy/Harmonic draft.

**Required control:** Record versions, image digests, compatibility test
results, and any future migration plan in the version matrix.

## 18.2 Corda Database Placement Deviation

**Decision:** `cordadb` is provisioned on the host PostgreSQL 18 cluster as a
separate logical database with separate roles and backup scope.

**Status:** Approved and recorded in the ledger scaffold journal. 2026.09.21 - THE INTENT IS TO HAVE DEDICATED DATABASES WITHIN POSTGRESQL AND TO BE ABLE TO RELATE BETWEEN THEM VIA RECEIPT NUMBER, SERIAL NUMBER, DATE AND TIME STAMPING, ETC. A DEDICATED CORDA DATABASE IS STILL PREFERRED.

**Required control:** Document database roles, host-loopback binding, backup
scope, restore procedure, and separation from sales/mapping databases.

## 18.3 Corda Deployment Blocker

**Status:** Blocked. MUST BE ADDRESSED BEFORE ADDITIONAL CORDA DEVELOPMENT

**Condition:** Corda node deployment requires the operator key and certificate
ceremony.

**Rule:** Do not generate, replace, export, or activate production ledger keys
without explicit operator approval and recorded ceremony output.

## 18.4 Payment Provider Decision

**Status:** Decided 2026-08-28.

**Decision:** PayPal (hosted checkout, provider-signed webhooks) plus **Zelle**
for direct US payments PLUS COINBASE STABLECOIN (USDC), used from an operator-built custom HTML storefront.
The storefront HTML will be developed externally (lovable.dev) and linked into
this project; it remains static and is served from the pCloud Public Folder.

**Controls required before enabling:**

- PayPal: hosted checkout only; signature-verified webhook via
  `ao-ingress-payment` -> `ao-payment` verifier; credentials via §14.1 secret
  delivery; no PayPal secret material in the repo, logs, or pCloud.
- Zelle: manual reconciliation path only (equivalent to the wire-transfer
  policy in §7.2): operator-verified receipt, auditable reference record,
  explicit operator approval per §7.2. Zelle provides no public webhooks/API,
  so no automated verification is permitted until a documented control exists.
- Storefront: static HTML only; no server-side code in the pCloud Public
  Folder; all dynamic behavior goes through the payment and community
  adapters. Evaluate the lovable.dev-produced HTML against §4 data policy and
  the prohibited-paths list before linking.

The prior provider-evaluation draft is retained at
`docs/compliance/payment-provider-evaluation.md` for record.

## 18.5 Mastodon Federation Edge and Identity Decision

**Status:** Decided and applied 2026-09-24 (WORK 000060).

**Decision (operator):**

- Serve Mastodon publicly at the dedicated hostname
  **`mastodon.300x3.com`** through Cloudflare Tunnel.
- Keep `300x3.com` and `www.300x3.com` on the existing static-site redirect;
  do not route the main website hostname to Mastodon.
- Edge transport is **HTTP/2** because QUIC stream timeouts were observed on
  this host. The tunnel service is `cloudflared-alwayson.service`.
- Mastodon identity is `LOCAL_DOMAIN=mastodon.300x3.com`; canonical accounts
  are `admin@mastodon.300x3.com` and `bot@mastodon.300x3.com`.
- `ao-egress-community` is attached only to `mastodon-web` and
  `mastodon-sidekiq`; database, Redis, and streaming remain on internal
  `ao-sales`.
- Origin ports remain loopback-only. TLS terminates at Cloudflare.

**Verified state:**

- Public actor and WebFinger endpoints return HTTP 200.
- The local web and health endpoints return HTTP 200.
- The remote account `@300x3@mastodon.social` lists both local accounts as
  followers, confirming local-to-remote follows. Its `following` collection is
  empty; reverse remote-to-local follows are not yet recorded.
- A public remote post was fetched and its local mention records were created;
  notification delivery was repaired through Mastodon’s native notification
  service after the asynchronous worker failed to materialize the rows.

**Resolution condition:** verify reverse follows using the remote account’s
`following` collection and the local incoming relationship tables. Do not mark
the reverse direction complete based only on a local outgoing request.

---

# 19. Work Queue and Issue Log

## work 000005 - UPDATE README WITH ACTUAL FRONTEND WEBSITE DETAILS
UPDATE THIS README, SECTION 7.1 TO INCLUDE THE ACTUAL FRONTEND WEBSITE DETAILS AS
LISTED HERE: https://github.com/300x3/HTML-300X3   INCLUDING THE WEBSITE LAYOUT, AND
PLAN TO INTEGRATE A SALES LINK BEHIND / WITHIN THE MODAL FOR EVERY ITEM LISTED IN "EQUIPMENT"
"BUILDING" "VEHICLE" SECTIONS.

**Status:** Complete 2026-09-21 — Section 7.1.1 documents the HTML-300X3
layout (Equipment 7 items, Buildings 5 items, Vehicles 5 items, plus Digital /
Discussion / Documentation / Donate) and the static-boundary sales-link plan.
Remaining: implement the per-modal purchase buttons in the HTML-300X3 repo and
mirror the static export to the pCloud Public Folder.

## WORK 000010 — Validate Tokodon, Local Mastodon, OpenClaw, and Local LLM

**Status:** In progress — local and public Mastodon origins are healthy;
OpenClaw is connected to Granite; operator-led Tokodon/OAuth validation remains.

**Current local AI/Mastodon bridge (2026-09-24):** NVIDIA Nemotron 3 Nano 4B
runs through LM Studio with a 100,096-token live context, two parallel slots,
and the configured 70% RAM / 80% VRAM policy. `mastodon-openclaw-bridge.service`
is enabled and active; it polls local notifications every 10 seconds and answers
new mentions/replies as `bot`. The bridge is local-instance only and does not
publish to other services.

**Precondition check 2026-08-31 (historical loopback stage):** Mastodon web and streaming healthy on
loopback (web 200 via `http://localhost:3000`; streaming health 200 on
`127.0.0.1:4000`); Tokodon OAuth client credentials and administrator account
material present in KDE Wallet `ao-mastodon` (Section 14.1.1); LM Studio
server running headless on `127.0.0.1:1234` with model `ibm/granite-3.2-8b`
loaded (verification default — final model selection remains the operator's);
REST API is auth-enforced (Bearer token required; obtain the token from the
LM Studio Developer tab and store it in the KDE Wallet `ao-sales` folder for
OpenClaw wiring).

**Current update 2026-09-24:** the public federation origin is
`https://mastodon.300x3.com`; the storefront remains on `300x3.com` and
`www.300x3.com`. The `admin` and `bot` login emails remain
`admin@300x3.com` and `bot@300x3.com`, while their canonical federated
identities are `admin@mastodon.300x3.com` and `bot@mastodon.300x3.com`.
Tokodon should use the dedicated federation origin.

**Objective:** Validate that the 300X3 Mastodon instance at
`https://mastodon.300x3.com` can be opened in Tokodon using the designated
administrator account (`admin`), and validate a conversation workflow with the
OpenClaw bot (`bot`) backed by the explicitly selected local Granite model.

**Preconditions:**

- Mastodon web and streaming services are healthy; the public federation origin
  is now `https://mastodon.300x3.com`, while the storefront remains separate.
- The `admin` account is approved and its password is stored in KDE Wallet.
- The `bot` account is approved and its password is stored in KDE Wallet.
- OpenClaw is connected to the running LM Studio Granite model through the
  local OpenAI-compatible endpoint at `127.0.0.1:32811/v1`; the API key is
  configured in the protected OpenClaw configuration and is not recorded here.
- A direct Granite completion returned `LMSTUDIO_OK`; OpenClaw gateway health
  is `ok`. Long existing sessions may require reset because the model's
  effective context budget is limited.

**Acceptance criteria:**

- Tokodon connects using the approved federation origin
  (`https://mastodon.300x3.com`).
- OAuth completes over HTTPS (normal flow).
- OpenClaw generates and posts a local threaded reply through the configured
  local model for each new mention/reply; response latency is the 10-second
  notification poll interval plus model inference time.
- The automatic bridge posts only to the local Mastodon instance; it does not
  publish to other services.

## WORK 000020 — Graphic User Interface Review

**Status:** In progress — Part A delivered; admin-plane monitoring/Metabase
 deployed on PostgreSQL; reporting identities and PostgreSQL application
 databases are provisioned. The Corda key/certificate ceremony and final
 sale-contract/ledger-ingest path remain blocked. Remaining scope (field link
 test, Gazebo GUI clients, and the final sales/Corda end-to-end test) is tracked
 in the outstanding items below.

**Objective:** Identify GUI components that remain unimplemented or lack an
operator workflow ACCORDING TO SECTION 6.A OF THIS README.

**Scope:**

- WebODM operator workflow.
- QGroundControl simulation workflow.
- Gazebo visualization workflow.
- Tokodon/Mastodon workflow.
- Local LM Studio/OpenClaw workflow.
- Sales/support administration workflow.
- Monitoring dashboard.
- Backup/restore status display.
- Field gateway/link-quality display.

**Acceptance criteria:**

- Each GUI has a named operator purpose.
- Each GUI has an access boundary.
- Each GUI has a startup, health-check, and shutdown procedure.
- Each GUI has a documented data source and no unauthorized cross-domain access.

**Review findings (2026-08-29):**

- WebODM UI: implemented with deviation (smoke test apt-76 passed); operator
  workflow recorded with startup/health/shutdown procedures.
- QGroundControl: AppImage installed
  (`~/Applications/QGroundControl-x86_64.AppImage`) but interactive workflow
  unvalidated; sim-vehicle Quadlet definition created
  (`quadlet/sim-vehicle/ao-ardupilot-sitl.container`, containerized variant not
  deployed). Host `ao-ardupilot-sitl.service` MAVLink telemetry validated
  2026-08-31: HEARTBEAT (sysid 1, MAV_TYPE_QUADROTOR, ArduPilot) received over
  `tcp:127.0.0.1:5760` via pymavlink; broken unit flags (`--console`,
  unsupported `--out`) removed — QGC connects via TCP 5760 (autoconnect);
  optional UDP 14550/14551 bridging deferred to MAVProxy (not installed).
- Gazebo visualization (vehicle and fabrication): headless runtimes verified;
  GUI clients planned; separate DDS/interface policy still required.
- Tokodon/Mastodon: Tokodon installed; Mastodon stack runs under the
  alwayson-sales store (db/redis/sidekiq healthy; web 127.0.0.1:3000,
  streaming 127.0.0.1:4000, streaming health 200); duplicate desktop-user
  Quadlet units disabled 2026-08-31 after a loopback port conflict
  (see ISSUE 000600); OAuth validation blocked under WORK 000010.
- LM Studio/OpenClaw: LM Studio server running on `127.0.0.1:1234` with
  `nvidia/nemotron-3-nano-4b` loaded at 100,096 context tokens and two parallel
  slots; REST API auth-enforced. OpenClaw gateway on `127.0.0.1:18789`
  (`openclaw-gateway.service`); `mastodon-openclaw-bridge.service` is enabled
  and active, polling local Mastodon notifications every 10 seconds.
- Sales/support administration: Metabase deployed and healthy
  (127.0.0.1:3002); reporting roles/views per Section 15.1 required.
- Monitoring dashboard: Prometheus + node_exporter + Grafana deployed
  (127.0.0.1:9090 and 127.0.0.1:3001).
- Backup/restore status: CLI-only (restic snapshot `548d9910` verified);
  dashboard display planned.
- Field gateway/link-quality: two Heltec V3 radios detected and enabled in
  Reticulum; gateway service deployment and end-to-end LoRa link test remain
  open under WORK 000050; MeshChatX native headless backend 4.9.1 running.
- Every entry declares its Podman network mapping (or explicit no-attachment),
  no-access network list, data source, and procedures; no entry grants
  cross-domain access or an `ao-admin` broad membership.

## WORK 000030 — Sales, Payment, Mastodon, and Ledger Readiness

**Status:** In progress.

**Outstanding items:**

- ~~Select payment provider.~~ Decided 2026-08-28: PayPal hosted checkout
  plus Zelle AND COINBASE PAYMENTS WITH CORDA AS LEDGER OF ALL CONTRACTS/SALES AND DETAILS. (Section 18.4).
- Provision payment credentials through approved secret delivery (KDE Wallet
  `ao-payment` folder provisioned per Section 14.1.1; entry not yet stored).
- Implement payment verifier and normalized event model.
- Implement sales API and receipt/fulfillment workflow.
- Provision pCloud credentials for archive replication (wallet-side
  confirmation complete under WORK 000040: `ao-archive` empty).
- Complete Mastodon OAuth validation (WORK 000010).
- Complete Corda operator key and certificate ceremony (Section 18.3).

**Acceptance criteria:**

- No payment secret appears in Git, logs, HTML, or Corda.
- A test payment event produces a verified normalized record.
- A sales receipt manifest can be generated without exposing sensitive data.
- Corda ingest receives only approved signed manifest data.
- Mastodon/OpenClaw operation remains restricted to approved paths.

## WORK 000040 — Off-Host Archive Credential Review

**Status:** In progress. Wallet-side confirmation completed 2026-08-31.

**Completed 2026-08-31:** Presence-only check (D-Bus `entryList`/`hasFolder`,
no values read) confirms the KDE Wallet contains **no** pCloud/archive
credentials: the `ao-archive` domain folder exists (provisioned empty
2026-08-31 per Section 14.1.1) with zero entries. Credential values must be
provisioned into `ao-archive` via `scripts/ops/kwallet-provision.sh` before
the encrypted replication test. The operator must still confirm whether
credentials exist outside the wallet and approve the replication test.

**Objective:** Confirm whether required pCloud/archive credentials exist in the
approved KDE Wallet location and/or approved service-secret store.

**Rules:**

- Do not print, copy, export, or expose credential values.
- Confirm only credential presence, account purpose, expiration state, and
  whether a service-specific secret can be provisioned.
- Perform a non-destructive encrypted replication test only after approval.

## WORK 000050 — Heltec V3 Connection and Field Link Test

**Status:** PARTIAL — both local RNodes are functional and initialize
successfully. RF feedback is observable on both configured bands, but its source
and severity have not been characterized. End-to-end field-link, telemetry,
interference, and fail-safe acceptance testing remain outstanding.

**Completed 2026-08-31:**

- One Heltec WiFi LoRa 32 V3 was connected by USB-C.
- Stable USB identification and the `/dev/heltec-v3` udev symlink were verified.
- The udev rule was installed at
  `/etc/udev/rules.d/99-alwayson-heltec.rules`.
- `scripts/radio/detect-heltec.sh` returned `OK`.
- A 115200 8N1 serial probe received `c0`-framed RNode traffic.
- RNode firmware 1.85, valid EEPROM state, and CP2102 bridge identity were
  recorded.

**Additional implementation verified 2026-09-21 through 2026-09-24:**

- Two Heltec LoRa 32 V3/SX1262 radios are recorded in
  `/home/scottw/.reticulum/radio-ids.txt`.
- Both `PEOPLE-RADIO` and `DRONE-RADIO` are confirmed functional; their
  current serial paths exist and the active MeshChatX process initialized both
  interfaces successfully.
- Feedback has been observed on both configured radio bands.
- The feedback has not yet been classified as self-coupling, external
  interference, harmonic/spurious transmission, antenna coupling, reflected
  energy, or another condition.
- MeshChatX is running headlessly at `127.0.0.1:18000`; its embedded Reticulum
  runtime was initialized from `/home/scottw/.reticulum/config`.
- Reticulum log evidence shows peer establishment and mesh announcements.

**Outstanding acceptance criteria:**

- Validate the Raspberry Pi/Waveshare profile against both Heltec profiles.
- Prove unicast and broadcast traffic over each RF path.
- Capture baseline noise floor and signal levels with each RNode idle.
- Repeat measurements while each radio transmits.
- Record whether feedback appears in-band, on the adjacent radio band, or
  through harmonics/spurious emissions.
- Measure isolation between the 915 MHz and 917 MHz RNode paths.
- Record RSSI, SNR, packet-loss percentage, retry behavior, and airtime.
- Test with antennas disconnected or replaced only under approved RF safety and
  hardware procedures.
- Do not increase transmit power or alter channel parameters until the source
  of the feedback is understood.
- Verify duplicate/replay rejection and signed telemetry-manifest export.
- Verify fail-safe behavior when a radio, serial path, or Reticulum peer is lost.
- Confirm that no live flight-control command path is enabled during testing.
- Classify or formally accept the historical
  `No module named 'umsgpack'` bounded-ratchet persistence error.
- Review the `0.0.0.0:4242` Reticulum gateway listener against the field-domain
  firewall policy.
- Capture a timestamped connected/disabled/error report for all 32 configured
  interfaces.

## WORK 000060 — Federation Publication of the Local 300X3 Mastodon Instance

**Status:** Implemented and operational 2026-09-24. The dedicated federation
endpoint is live; reverse-follow and complete cross-server interaction
validation remain outstanding.

**Objective:** Publish the local Mastodon instance at
`https://mastodon.300x3.com` without replacing the static storefront at
`300x3.com` or `www.300x3.com`.

**Completed 2026-09-24:**

- Created dedicated Cloudflare Tunnel `alwayson-mastodon-federation` and DNS
  route for `mastodon.300x3.com`; storefront hostnames were excluded from the
  Mastodon tunnel.
- Added the Cloudflare redirect-rule exception for the dedicated hostname.
- Configured `LOCAL_DOMAIN=mastodon.300x3.com`; local login emails remain
  `admin@300x3.com` and `bot@300x3.com`, while canonical federated accounts
  are `admin@mastodon.300x3.com` and `bot@mastodon.300x3.com`.
- Enabled controlled outbound federation through `ao-egress-community` on
  web/Sidekiq only; database, Redis, and streaming remain on internal
  `ao-sales`.
- Switched the tunnel from QUIC to HTTP/2 after QUIC stream timeouts.
- Verified public actor, WebFinger, local actor documents, local health, and
  tunnel HTTP 200 responses.
- Resolved `@300x3@mastodon.social`; its public followers collection contains
  both local accounts, confirming local-to-remote follows.
- Fetched public post
  `https://mastodon.social/@300x3/117327609018447382`; local mention records
  were created for both accounts, and native notification processing was
  repaired after the asynchronous worker failed to create notification rows.

**Outstanding:**

- Confirm reverse follows using the remote `following` collection and local
  incoming relationship tables; do not infer them from local outgoing state.
- Complete a new signed ActivityPub round-trip test after the notification
  worker fix.
- Record remote-account approval/rejection behavior separately from local
  account follow state.

**Acceptance criteria:**

- All steps of the Section 15.4.4 enablement sequence are completed in
  order and evidenced.
- A public post from the local instance is visible on `mastodon.social`,
  and a reply or boost round-trip is received locally.
- No credential, certificate key, or tunnel secret appears in Git, logs,
  or this README.
- `config/mastodon/instance-policy.yaml` reflects the Section 15.4.1
  requirements, and Section 18 records the retirement of the loopback
  `RAILS_FORCE_SSL=false` deviation for the federated deployment.

## ISSUE 000100 — Host Runtime Re-Check

**Status:** Verified 2026-08-26.

| Item | Verified value |
|---|---|
| Kernel | `7.0.0-31-generic` |
| Podman | `5.7.0`; rootless operation as `scottw`; ten `ao-*` workload networks recorded |
| GPU | GTX 1080; driver `580.178.04`; CDI devices registered |
| Simulation | ROS 2 Lyrical at `/opt/ros/lyrical`; Gazebo Sim `10.5.0` |
| Host data services | PostgreSQL `18.6` and Redis `8.0.5`, loopback-only |
| Photogrammetry drive | ext4 `/dev/sdb1`; UUID verified; approximately 433.9 GB free of 457 GB |

## ISSUE 000200 — Podman Store Visibility

**Status:** Documented.

Rootless and system/rootful Podman use separate stores. Container, image, and
volume visibility depends on the invoking identity and storage location. An
empty `podman ps -a` under an operator account does not prove that system-level
containers are missing.

The mapping smoke-test evidence, retained backups, and orthophoto deliverables
indicate that system/rootful WebODM activity occurred during validation. See
the mixed-Podman deviation in Section 13.

## ISSUE 000300 — Photogrammetry Tree Addendum

**Status:** Resolved 2026-08-26.

The empty stray directory:

```text
/media/scottw/500GBPHOTOGRAM/incom/
```

was identified as an unused typo duplicate of `incoming/` and removed with
operator approval. The drive tree now matches the required structure.

## ISSUE 000400 — Remediation Record

**Status:** Partially resolved.

- Podman socket bridges: mapping and sales tunnels verified; ledger backend EOF
  diagnosis remains pending an operator-run privileged command.
- Quadlet image sources: six container units carry recorded SHA-256 image
  digests.
- Secret wiring: intentionally incomplete until secret provisioning is approved.
- Listener policy: prior `:80` nginx and `:1716` KDE Connect exposure issues
  resolved; current listener state must continue to be monitored.
- MeshChatX port assignment: the field-domain MeshChatX backend and local web
  UI are assigned `127.0.0.1:18000`; WebODM retains `127.0.0.1:8000`.
  Both are loopback-only and must not share a listener.
- GPU documentation: toolkit/CDI/smoke-test state reconciled with version
  matrix.
- Backup summary: aligned with hourly incremental and daily dump policy.
- Version matrix: refreshed with kernel, Quadlet capability, and ArduPilot
  commit information; QGroundControl and Stable-Baselines3 remain
  not-installed markers where applicable.

## ISSUE 000500 — Architecture and Deployment Decisions

**Status:** Open and tracked.

- Simulation baseline is ROS 2 Lyrical and Gazebo Sim 10.5.0.
- `cordadb`, when activated, uses the host PostgreSQL 18 cluster.
- Corda node deployment remains blocked pending the operator key/certificate
  ceremony.
- Mapping runtime model requires final designation as rootless, system-level,
  or mixed.
- Controlled ingress/egress adapters remain architecture requirements and must
  be implemented before enabling external payment, archive, or community
  connectivity.
- Unattended Quadlet services currently source secrets from KDE Wallet at
  startup (`scripts/operations/fetch-kwallet-secret.sh` writes service-specific
  0600 env files for mastodon-db, sales-db, and webodm-db). Section 14.1 states
  unattended production services must use systemd credentials, Podman secrets,
  or approved service-specific secret files; record an approved deviation with
  compensating controls or migrate to Podman secrets/systemd credentials before
  production declaration.

## ISSUE 000600 — Mastodon Setup

**Status:** In progress — dedicated federation endpoint is live; reverse-follow
and full cross-server interaction validation remain outstanding.

- Placement (durable): the authoritative Mastodon stack runs under the
  `alwayson-sales` service account (UID 993) in its own rootless container
  store and linger-enabled systemd user manager. The `ao-mastodon-web` /
  `ao-mastodon-streaming` units in the `scottw` manager are **masked**
  (`ln -s /dev/null`) purely as a duplicate-instance guard. Consequence for
  operators: `podman ps` as `scottw` will not show `mastodon-web` or
  `mastodon-streaming` even when they are healthy; inspect them via the
  `alwayson-sales` manager. See Section 20.0.
- Open (config drift): the live instance identity is `mastodon.300x3.com`,
  but `config/mastodon/instance-policy.yaml`, `mastodon.env.example`,
  `config/platform/version-matrix.yaml`, `secrets/mastodon/mastodon.env`, and
  `scripts/operations/fetch-mastodon-env.sh` still declare the superseded apex
  value `300x3.com`. The helper is invoked by service units and emits
  `LOCAL_DOMAIN=300x3.com` unconditionally, so a re-provision or restart can
  push the apex identity back into the live environment and break WebFinger
  against the tunnel hostname. Reconcile all of the above to
  `mastodon.300x3.com` before the next Mastodon restart.
- Resolved 2026-08-31: duplicate Mastodon Quadlet stack under the desktop
  user crash-looped against the authoritative alwayson-sales store
  (rootlessport bind conflict on 127.0.0.1:3000/4000, restart counter 160+).
  Desktop-user units disabled and moved to
  `~/.config/containers/systemd/disabled/`; scottw-store DB dumped to
  `/ALWAYSON/backups/mastodon/` before teardown; sales-store stack
  confirmed authoritative per `scripts/mastodon/deploy-mastodon.sh`.
- Public federation endpoint: `https://mastodon.300x3.com`; storefront
  hostnames remain separate. Actor and WebFinger return HTTP 200.
- Canonical federated accounts: `admin@mastodon.300x3.com` and
  `bot@mastodon.300x3.com`; login emails remain `admin@300x3.com` and
  `bot@300x3.com`.
- The local instance uses `ao-egress-community` for outbound web/Sidekiq
  federation; database, Redis, and streaming remain isolated on `ao-sales`.
- The tunnel uses HTTP/2 after QUIC stream timeouts; local and public health
  checks return HTTP 200.
- The remote account `@300x3@mastodon.social` lists both local accounts as
  followers, confirming local-to-remote follows. Its following collection is
  empty; reverse follows are not yet recorded locally.
- A public remote mention was fetched; local mention records were created and
  native notification processing was repaired after the asynchronous worker
  failed to create notification rows.
- New registrations require explicit approval (`approval_required: true`).
- OAuth password grant is unavailable in the documented version; use an
  operator-controlled authorization-code flow.
- `300x3.com` email routing/MX delivery remains a separate operator task.

---
## ISSUE 000601 — Metabase Cannot Reach the Reporting PostgreSQL Socket

**Status:** OPEN — service not serving.

Metabase is deployed on `ao-admin` against the host PostgreSQL 18 cluster
(§3.3) and **does not currently start**. `ao-metabase.service` comes up,
initialises, fails during application-database setup, and is restarted by
`Restart=on-failure`, so the failure is easy to miss: the container shows as
recently started, and `127.0.0.1:3002` only exists in the window between
restarts. `/api/health` returns 503 during initialisation and the UI is not
reachable in any stable sense.

**Already ruled out** (verified directly against the running host):

- The host cluster is online (`18/main`, `5432`) and the `metabase` database
  and `metabase_app` role exist.
- `metabase_app` authenticates successfully to the `metabase` database over
  the `/var/run/postgresql` UNIX socket, using the wallet-sourced credential
  that `scripts/operations/fetch-reporting-env.sh` materialises.
- The container has the socket bind-mounted and the driver classes load.

**The defect is the JDBC connection string, not the database.** Metabase builds
its connection URL from `MB_DB_*`, and a UNIX socket *directory* is not a
valid URL host. The `?host=` query-parameter form is not a workaround:
Metabase strips the parameter before pgjdbc sees it, leaving pgjdbc with no
host (`protocol = socket host = null`). Any working configuration must both
produce a parseable URL and keep pgjdbc on the UNIX-socket transport, since the
host intentionally publishes **no TCP listener** for reporting (§11.2.1).

**Operator note:** until this is resolved, treat the Metabase row in Section 20
as not-serving. Grafana and Prometheus are unaffected and verified healthy, as
they consume the same host cluster successfully.

---
## ISSUE 000700 — MeshChatX Reticulum Interface, RF, and Persistence Status

**Status:** OPEN — PARTIAL VERIFICATION

### Interface finding

The active Reticulum configuration contains 32 interfaces and no interface
explicitly configured as disabled:

- 29 TCP clients with `interface_enabled = true`.
- `PEOPLE-RADIO` and `DRONE-RADIO` with `interface_enabled = true`.
- `Public Gateway` with `enabled = yes`.

The MeshChatX web interface is bound to `127.0.0.1:18000`. The Reticulum
Backbone interface is bound to `0.0.0.0:4242`. Binding was verified; firewall
policy and packet reachability were not verified without root privileges.

“Enabled” describes configuration intent only. It does not prove that an
interface is connected, reachable, carrying traffic, or suitable for a particular
service. Discovered interfaces are not a one-to-one match with the static file.

### RF feedback on both RNode bands

Both RNodes are functional and initialized successfully. Feedback is observable
on both the 915 MHz and 917 MHz paths, but it has not been classified as a
hardware fault, interference, self-coupling, harmonic/spurious transmission,
antenna coupling, reflected energy, or normal local RF activity.

Required characterization:

1. Idle noise-floor and signal measurements for each radio.
2. Transmit-state spectrum and power measurements for each radio.
3. In-band and adjacent-band feedback identification.
4. Separation of 915 MHz and 917 MHz path behavior.
5. Controlled antenna changes only under approved RF procedures.
6. Packet delivery, retries, RSSI, SNR, and airtime with and without the
   feedback source.
7. A documented decision to mitigate, accept, or monitor the condition.

### Historical persistence defect

The current log contains 12,364 occurrences of:

```text
Bounded ratchet persist failed: No module named 'umsgpack'
```

The final occurrence is immediately before newer MeshChatX startup events at
2026-09-24 16:29:19Z and 16:51:04Z. No `umsgpack` error was observed after
those newer starts in the reviewed log. The defect remains open, but continuous
recurrence in the current native process has not been established.

Before production use, verify whether the native bundle omitted a dependency,
ratchet state is lost between restarts, session continuity is affected, and a
controlled restart preserves the expected state without errors.

### Reproducible status report

Save timestamped reports under:

```text
/ALWAYSON/artifacts/field-chat/reticulum-interface-status-YYYYMMDD-HHMMSS.txt
```

Each report must include config and executable hashes, process identity,
listeners, static and discovered interfaces, enabled/initialized/connected/
operational/reachable state, peer or announce activity, last error, and last
check time.

### Required closure evidence

- Timestamped status for every configured interface.
- Successful traffic test through each retained interface.
- Documented decision for every unavailable public peer.
- Firewall and packet-reachability review for TCP/4242.
- RF feedback characterization and disposition.
- Root-cause or formal acceptance of the historical `umsgpack` errors.
- Controlled-restart verification that MeshChatX state persists.
- Independently verified running MeshChatX and embedded-RNS versions.

---

## 20.0 Runtime Placement by Execution Account

Durable topology facts. These do not change between runs; the verification
table in Section 20.1 carries the per-check status.

| Component | Execution account | Network | Notes |
|---|---|---|---|
| Mastodon (5 containers) | `alwayson-sales` (UID 993) | `ao-sales` | Own rootless container store (`/home/alwayson-sales/.local/share/containers/storage`, runtime dir `/run/user/993`) and its own linger-enabled systemd user manager. **Not** visible to `podman ps` as `scottw`. |
| Mastodon (duplicate guard) | `scottw` | — | `ao-mastodon-web.service` / `ao-mastodon-streaming.service` are **masked** (`ln -s /dev/null`) so the desktop-user manager cannot start a second instance (ISSUE 000600). |
| Cloudflare Tunnel | `scottw` | — | `cloudflared-alwayson.service`; publishes the federation hostname only. |
| Prometheus, node_exporter, Grafana, Metabase | `scottw` | `ao-admin` (+ `ao-reporting-egress`) | Reporting tools reach the host PostgreSQL cluster through the bind-mounted `/var/run/postgresql` **UNIX socket**; no TCP listener is published. |
| PostgreSQL 18 host cluster | system (`postgres`) | — | `18/main` on `5432`; authoritative store for `grafana` and `metabase` reporting DBs. |
| WebODM (`webapp`, `worker`, `broker`, `db`, `nodeodm`) | `scottw` | `ao-mapping` | UI on `127.0.0.1:8000`. |
| Sales DB | `scottw` | `ao-sales` | Container-scoped `sales-db`. |
| MeshChatX / Reticulum, OpenClaw, LM Studio | `scottw` | loopback | UI `127.0.0.1:18000`, gateway `0.0.0.0:4242`, LM Studio `127.0.0.1:1234`. |

**Operational note:** because Mastodon runs under a separate account and store,
rootless `podman ps` as `scottw` will not list `mastodon-web` or
`mastodon-streaming` even when they are healthy. Inspect them through the
`alwayson-sales` user manager. Legacy `300x3-*` containers in the `scottw`
store are inactive and are not part of the deployment.

# 20. Current Verification Evidence

**Status as of 2026-09-25.** Each row records the outcome of a check against
the running system, not design intent. Where a component is misleading in the
operator surface, the discrepancy is stated.

| Item | Evidence | Status |
|---|---|---|
| Host inventory | Inventory report completed | Complete |
| Photogrammetry drive | UUID verified; directory tree created | Complete |
| Package/version matrix | Captured and refreshed | Complete |
| GUI boundary matrix (WORK 000020) | `config/platform/gui-boundary-matrix.yaml` created; 10 entries validated (YAML), covering all Section 6.A scope items | Partial |
| Rootless Podman and Quadlet | Verified; mixed-store deviation documented | Complete with deviation |
| GPU runtime | Driver/CDI verified; CPU baseline and GPU smoke completed | Complete |
| Domain network isolation | Internal workload networks and test verified | Complete |
| Firewall and ports | UFW active; prior `:80` and `:1716` exposure cleared | Complete |
| WebODM smoke test | `apt-76`; 76 images; GPU-enabled orthophoto produced | Complete |
| Vehicle simulation | Headless Gazebo 300-iteration and ROS-Gazebo bridge test | Complete |
| Fabrication simulation | Headless Gazebo 300-iteration and bridge test | Complete |
| Heltec/LoRa detection | Heltec V3 connected; stable by-id + `/dev/heltec-v3` path, udev rule installed, `detect-heltec.sh` OK, serial probe received c0-framed packets 2026-08-31; LoRa-link test pending ao-field gateway | Partial |
| Corda receipt | Corda 5.2.2 scaffolded; key ceremony pending | Blocked |
| Sales receipt manifest | Sales DB deployed; provider/API pending | Partial |
| Backup | Encrypted restic snapshot `548d9910` completed; recurring schedule automated 2026-08-31 (restic nightly 03:30 timer, weekly integrity verify Sun 04:30, nightly domain DB dumps 03:00 for mastodon/sales/webodm); verification snapshot `32be2a1c` saved | Complete |
| Restore | File hash validated; database 14/14 tables restored | Complete |
| Monitoring stack (ao-admin) | Prometheus + node_exporter + Grafana run as `scottw` Quadlet units on `ao-admin`. Grafana application state is genuinely PostgreSQL-backed against the host cluster over the `/var/run/postgresql` socket (`/api/health` reports `database: ok`), and Prometheus is its only registered datasource. Both Prometheus targets scrape `up` | Complete |
| Metabase reporting (ao-admin) | **Not serving.** The container starts, reaches the host PostgreSQL 18 cluster, then exits during DB setup; `Restart=on-failure` cycles it, so `127.0.0.1:3002` is absent between restarts and `/api/health` only ever returns 503. Not a database, credential, or network fault: `metabase_app` authenticates to the `metabase` database over the `/var/run/postgresql` socket, and the host publishes no TCP listener by design. The fault is the JDBC connection string Metabase builds from `MB_DB_*` — a socket directory in `MB_DB_HOST` is not parseable as a URL host, and the `?host=` form is stripped by Metabase before pgjdbc sees it. See ISSUE 000601 | Blocked — awaiting socket-transport fix in `scripts/operations/fetch-reporting-env.sh` |
| Mastodon local stack (ao-sales) | All 5 containers run under the `alwayson-sales` service account in a separate rootless store and systemd user manager (Section 20.0); `ao-mastodon-web` / `ao-mastodon-streaming` are masked in the `scottw` manager as a duplicate guard (ISSUE 000600). Web `127.0.0.1:3000` and streaming `127.0.0.1:4000` verified; `/api/v1/instance` reports `mastodon.300x3.com` v4.3.7 | Complete (live, federated) |
| Mastodon federation edge (WORK 000060) | Dedicated Cloudflare Tunnel `alwayson-mastodon-federation` for `mastodon.300x3.com`; HTTP/2 connector active; actor and WebFinger 200; storefront hostnames preserved; `LOCAL_DOMAIN=mastodon.300x3.com`; canonical accounts `admin@mastodon.300x3.com` and `bot@mastodon.300x3.com`; `ao-egress-community` attached to web/Sidekiq only; local-to-remote follows confirmed; reverse-follow validation pending | Partial — signed round-trip and reverse-follow evidence remain |
| WebODM operator workflow restart | Stack is rootless (scottw/mapping store); system-store recovery step correctly found no system-store containers — no action needed | Complete |
| ArduPilot SITL MAVLink | ao-ardupilot-sitl.service flags fixed; HEARTBEAT (sysid 1, QUADROTOR, ArduPilot) validated over tcp:127.0.0.1:5760 via pymavlink | Complete |
| Heltec firmware | RNode firmware 1.85 recorded via rnodeconf; EEPROM valid; signature unverified (operator signing option) | Partial |
| Reticulum executable | Standalone RNS 1.4.2 available at `/home/scottw/.local/bin/rnsd`; active Reticulum runtime is embedded in MeshChatX | Complete with embedded version pending |
| MeshChatX deployment | Native headless backend running since 2026-09-24 11:02 local time; local UI bound to `127.0.0.1:18000`; desktop metadata declares 4.9.1 | Complete with running-version verification pending |
| Reticulum interface configuration | 29 TCP clients use `interface_enabled = true`; two RNodes use `interface_enabled = true`; one Backbone uses `enabled = yes`; zero explicitly disabled | Complete |
| Reticulum runtime participation | Logs show auto-connections, peering, announces, and LXMF/Nomad network announcements | Partial — per-interface health not yet captured |
| Reticulum connectivity | Startup logs contain timeouts, network-unreachable errors, connection refusals, and reconnect cycles for named and discovered interfaces | Partial |
| Reticulum public gateway | MeshChatX is bound to `0.0.0.0:4242`; the host had `192.168.87.135/24` on Wi-Fi | Partial — binding verified; firewall and packet reachability not verified |
| Two-radio Reticulum initialization | Both serial paths exist and MeshChatX logged both RNodes as configured and powered up on 2026-09-24 | Complete |
| RNode band feedback | Functional feedback observed on both 915 MHz and 917 MHz paths | Issue — source and severity uncharacterized |
| MeshChatX cryptographic-state persistence | 12,364 historical `umsgpack` errors; error block ends before newer 16:29Z and 16:51Z startup entries | Issue — controlled-restart test required |
| MeshChatX version provenance | Desktop metadata declares 4.9.1; executable hash matches the local manifest; running version remains unverified; repository cache contains a 4.8.4 wheel | Partial |

---

# 21. Status References

Review the following before changing the platform:

```text
README.md
VERSION
git log
docs/compliance/installation-status.md
/ALWAYSON/
```

The current repository README, local working folder, verification evidence,
version matrix, and issue log must be reviewed before beginning new work.

Current implementation references:

```text
/home/scottw/.openclaw/openclaw.json
quadlet/sales/ao-egress-community.network
quadlet/sales/ao-mastodon-web.container
quadlet/sales/ao-mastodon-sidekiq.container
scripts/mastodon/federate-local.sh
/home/scottw/.cloudflared/config.yml
```

Do not add API keys, passwords, tunnel credential JSON, or other secrets to
this reference list.

---

![SIMULATION](assets/SIMULATION.png)
