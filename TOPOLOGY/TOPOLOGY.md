# ALWAYS ON — generated system topology inventory

Generated: `2026-10-03T19:52:47Z`  
Authority: `/ALWAYSON/TOPOLOGY/ALWAYS ON — Architecture, Operations, and Status - v6.md` (README §3.1, §3.3, §5.1, §5.2, §6.A, §9, §20.0)  
Generator: `/ALWAYSON/scripts/operations/generate-topology.py`  
Observed mode: `live inspection`

Networks: **17** (14 live) · containers: **22** declared, 25 running · listeners: **53** (30 loopback) · drift items: **4**

## 1. Podman networks

| Network | Subnet | Gateway | Internal | Kind | Runtime | Status | Members |
|---|---|---|---|---|---|---|---|
| ao-admin | 10.89.9.0/24 | 10.89.9.1 | true | workload | live | implemented | ao-grafana, ao-metabase, ao-node-exporter, ao-prometheus |
| ao-build-update | 10.89.13.0/24 | 10.89.13.1 | false | adapter | live | scaffolded | ao-build-update |
| ao-data | 10.89.8.0/24 | 10.89.8.1 | true | workload | live | implemented | — |
| ao-egress-archive | — | — | ? | adapter | not created | planned | — |
| ao-egress-community | — | — | ? | adapter | not created | implemented | — |
| ao-fabrication | 10.89.12.0/24 | 10.89.12.1 | true | workload | live | implemented | ao-fabrication-db |
| ao-field | 10.89.2.0/24 | 10.89.2.1 | true | workload | live | in_progress | — |
| ao-html-window | 10.89.14.0/24 | 10.89.14.1 | true | workload | live | implemented | ao-sim-fabrication-foxglove |
| ao-ingress-payment | — | — | ? | adapter | not created | planned | — |
| ao-ledger-core | 10.89.7.0/24 | 10.89.7.1 | true | workload | live | blocked | — |
| ao-ledger-ingest | 10.89.6.0/24 | 10.89.6.1 | true | workload | live | blocked | — |
| ao-mapping | 10.89.3.0/24 | 10.89.3.1 | true | workload | live | implemented | ao-nodeodm, ao-webodm-broker, ao-webodm-db, ao-webodm-webapp, ao-webodm-worker |
| ao-payment | 10.89.1.0/24 | 10.89.1.1 | true | workload | live | planned | ao-ingress-payment |
| ao-reporting-egress | 10.89.10.0/24 | 10.89.10.1 | false | adapter | live | implemented | ao-grafana, ao-metabase |
| ao-sales | 10.89.0.0/24 | 10.89.0.1 | false | workload | live | in_progress | mastodon-db, mastodon-redis, mastodon-sidekiq, mastodon-streaming, mastodon-web, ao-sales-db |
| ao-sim-fabrication | 10.89.5.0/24 | 10.89.5.1 | true | workload | live | implemented | ao-sim-fabrication-foxglove, ao-sim-fabrication-gz |
| ao-sim-vehicle | 10.89.4.0/24 | 10.89.4.1 | true | workload | live | implemented | ardupilot-sitl |
| podman | 10.88.0.0/16 | 10.88.0.1 | false | **podman default** (not an ALWAYS ON domain) | live | declared | — |

## 2. Containers, networks, IPs and published ports

| Container | Local software / image | Networks + IP | Published ports | State | Status | systemd unit | Quadlet |
|---|---|---|---|---|---|---|---|
| ao-build-update | python sha256:79e7a9b9ff | — | internal only | not running | declared | — | yes |
| ao-fabrication-db | postgres sha256:d74eeac9a6 | ao-fabrication=10.89.12.3 | 127.0.0.1:15433->5432/tcp | running | implemented | active | yes |
| ao-nodeodm | nodeodm sha256:553fe5cacb | ao-mapping=10.89.3.3 | internal only | running | implemented | active | yes |
| ao-webodm-broker | redis sha256:c6eabf748f | ao-mapping=10.89.3.7 | internal only | running | implemented | active | yes |
| ao-webodm-db | webodm_db sha256:03f18ec008 | ao-mapping=10.89.3.6 | internal only | running | implemented | active | yes |
| ao-webodm-webapp | webodm_webapp sha256:188267c654 | ao-mapping=10.89.3.4 | 127.0.0.1:8000->8000/tcp | running | implemented | active | yes |
| ao-webodm-worker | webodm_webapp sha256:188267c654 | ao-mapping=10.89.3.5 | internal only | running | implemented | active | yes |
| ao-grafana | grafana-oss sha256:b739cda4b6 | ao-admin=10.89.9.61, ao-reporting-egress=10.89.10.58 | 127.0.0.1:3001->3000/tcp | running | implemented | active | yes |
| ao-metabase | metabase sha256:fc96bfa830 | ao-admin=10.89.9.4, ao-reporting-egress=10.89.10.2 | 127.0.0.1:3002->3000/tcp | running | implemented | active | yes |
| ao-node-exporter | node-exporter sha256:863b62ff9f | ao-admin=10.89.9.10 | internal only | running | implemented | active | yes |
| ao-prometheus | prometheus sha256:d47ad27caa | ao-admin=10.89.9.3 | 127.0.0.1:9090->9090/tcp | running | implemented | active | yes |
| ao-ingress-payment | python sha256:79e7a9b9ff | ao-payment=10.89.1.2 | 127.0.0.1:8899->8899/tcp | running | implemented | active | yes |
| ao-sales-db | postgres sha256:d74eeac9a6 | ao-sales=10.89.0.13 | 127.0.0.1:15432->5432/tcp | running | implemented | active | yes |
| mastodon-db | postgres sha256:d74eeac9a6 | ao-sales=10.89.0.14 | internal only | running | implemented | active | yes |
| mastodon-redis | redis sha256:c6eabf748f | ao-sales=10.89.0.15 | internal only | running | implemented | active | yes |
| mastodon-sidekiq | mastodon sha256:76436bccad | ao-sales=10.89.0.9 | internal only | running | implemented | active | yes |
| mastodon-streaming | mastodon-streaming sha256:24834e873c | ao-sales=10.89.0.5 | 127.0.0.1:4000->4000/tcp | running | implemented | active | yes |
| mastodon-web | mastodon sha256:76436bccad | ao-sales=10.89.0.8 | 127.0.0.1:3000->3000/tcp | running | implemented | active | yes |
| ao-sim-fabrication-foxglove | foxglove-bridge sha256:9acc6d4df7 | ao-html-window=10.89.14.60, ao-sim-fabrication=10.89.5.55 | 127.0.0.1:8081->8081/tcp | running | implemented | active | yes |
| ao-sim-fabrication-gui-gz | gz-sim10-resolute gui-svgfix | — | internal only | not running | declared | — | yes |
| ao-sim-fabrication-gz | gz-sim10-server sha256:55f8dbcf8d | ao-sim-fabrication=10.89.5.10 | internal only | running | implemented | active | yes |
| ardupilot-sitl | ardupilot-sitl latest | — | internal only | not running | declared | — | yes |
| ao-sqli3 | grafana-oss 11.6.0 | — | internal only | running | implemented | — | **no** |
| confident_khayyam | grafana 11.6.0 | — | internal only | running | implemented | — | **no** |
| dreamy_rosalind | foxglove-bridge latest | — | internal only | running | implemented | — | **no** |
| keen_bhabha | grafana-oss 11.6.0 | — | internal only | running | implemented | — | **no** |
| relaxed_tharp | grafana 11.6.0 | — | internal only | running | implemented | — | **no** |
| vigorous_shannon | foxglove-bridge latest | — | internal only | running | implemented | — | **no** |

## 3. Databases and data stores (v6 §3.3 / §3.3.1)

| Database / store | Kind | Software | Placement | Authority | Used by | Listens / path | Status | Role |
|---|---|---|---|---|---|---|---|---|
| Host PostgreSQL 18.6 cluster | postgresql | postgresql-18 18.6 + PostGIS 3.6.2 (host systemd service) | host | authoritative relational | — | 127.0.0.1:5432, [::1]:5432, unix:/var/run/postgresql/.s.PGSQL.5432 | active | System-wide relational platform. One cluster, separate logical databases, separate application roles. REVOKE CONNECT FROM PUBLIC enforced. |
| salesdb | postgresql | PostgreSQL 18 (host cluster target) | host | authoritative relational | Sales API, ao-payment (planned), Metabase (reporting) | — | current_migration_state | Authoritative sales/payment records: customers, orders, products, payments, receipts, entitlements, audit history. |
| mastodon | postgresql | PostgreSQL 18 (in container-scoped mastodon-db today) | container | authoritative relational | Mastodon web, Mastodon Sidekiq, Mastodon streaming | — | current_migration_state | Mastodon application state: accounts, posts, media metadata, federation state, background-job data. |
| webodm (PostGIS) | postgis | PostgreSQL/PostGIS (in container-scoped db today) | container | authoritative relational | WebODM webapp, WebODM worker, NodeODM, Metabase (reporting) | — | current_migration_state | Mapping projects, processing state, users, geospatial data. |
| grafana | postgresql | PostgreSQL 18 (host cluster) | host | authoritative relational | Grafana ao-grafana | — | target | Grafana users, dashboards, folders, datasource definitions, preferences, alert state. |
| metabase | postgresql | PostgreSQL 18 (host cluster) | host | authoritative relational | Metabase ao-metabase | — | target | Metabase users, collections, questions, dashboards, database connections, settings. |
| cordadb (Corda persistence) | postgresql | PostgreSQL 18 — separate logical database with its own roles and backup scope | host | authoritative ledger | Corda node ao-ledger-core (planned) | — | blocked | Corda persistence. AUTHORITATIVE LEDGER for sale/contract, receipt association, entitlement, approved state transitions. |
| postgres (administrative) | postgresql | PostgreSQL 18 (host cluster) | host | authoritative relational | Maintenance, backup, restore validation | — | active | Administrative/maintenance database for the shared cluster. |
| Host Redis 8.0.5 (database 0) | redis | redis-server 8.0.5 (host systemd service) | host | not authoritative | general coordination | 127.0.0.1:6379 | active | General low-latency cache/coordination layer. NOT a system of record; no current application data confirmed. |
| mastodon-redis (database 0) | redis | Redis 8 (container-scoped) | container | not authoritative | Mastodon web, Mastodon Sidekiq | — | active | Mastodon cache, queues, background-job coordination. Not authoritative business data. |
| broker (database 0) | redis | Redis 8 (container-scoped) | container | not authoritative | WebODM worker, WebODM broker | — | active | Celery/task broker and worker coordination. Not authoritative mapping data. |
| Prometheus TSDB | tsdb | prometheus v3.4.1 — /prometheus persistent volume | container | not authoritative | Grafana (metrics datasource), alerting, rule evaluation | — | implemented | Specialized time-series store: metrics, service health, resource usage, operational monitoring. Works without Grafana. |
| OpenClaw SQLite state | sqlite | SQLite (desktop application state) | host | not authoritative | OpenClaw gateway, OpenClaw chat relay | ~/.openclaw/state/openclaw.sqlite | active | Local operational state. Not part of SQL reporting. |
| Akonadi / KDE PIM SQLite | sqlite | SQLite (desktop application state) | host | not authoritative | Akonadi, KDE PIM | — | active | Contacts, calendars, mail indexes, local personal-information data. |
| Browser profile SQLite stores | sqlite | SQLite (Konqueror/KDE WebEngine, Firefox, Brave, Chrome, Edge) | host | not authoritative | browsers | — | active | History, site storage, caches, certificates, profile data. |
| Podman rootless metadata store | sqlite | SQLite (rootless Podman) | host | not authoritative | Podman | — | active | Container, image, network, volume metadata. Not application data. |
| ROS / simulation local SQLite | sqlite | SQLite (application-specific local files) | host | not authoritative | ROS 2 Lyrical, Gazebo Sim, ArduPilot SITL, QGroundControl | — | active | Local tool state where enabled. Not a shared reporting source. |
| Filesystem / local application state | filesystem | Application files, logs, project files, local state | host | not authoritative | LM Studio, OpenClaw, MeshChatX, QGroundControl, ArduPilot, Gazebo, simulation tools, restic | — | active | Operational or engineering data that is not automatically part of SQL reporting. |
| Photogrammetry media (filesystem, ext4) | filesystem | /media/scottw/500GBPHOTOGRAM/ — ext4 /dev/sdb1, UUID verified | host | not authoritative | WebODM, NodeODM, imagery intake/exporter | — | implemented | Source imagery, orthophotos, point clouds, 3D model artifacts. Large binaries stay filesystem-resident; only metadata is in webodm. |
| H2 legacy migration backups | h2 | H2 (retained backup files only) | host | not an application db | Grafana/Metabase legacy migration | — | not_active | No longer active; retained temporarily for rollback and migration evidence. |

## 4. Host software (non-container)

| Component | Software | Listens | Connects/relays | Status |
|---|---|---|---|---|
| PostgreSQL 18.6 (host cluster) | postgresql-18 18.6 / PostGIS 3.6.2 | 127.0.0.1:5432, [::1]:5432, unix:/var/run/postgresql/.s.PGSQL.5432 | 10.42.0.1:5432 (socat, ao-postgres-reporting-bridge) | implemented |
| Redis 8.0.5 (host service) | redis-server 8.0.5 | 127.0.0.1:6379 | — | implemented |
| ArduPilot SITL (host systemd service) | arducopter SITL, ArduPilot e57b8a47d3 (4.6.0-beta1) | tcp/127.0.0.1:5760 | — | implemented |
| restic encrypted backup (host) | restic — encrypted local snapshots + encrypted pCloud replication | — | — | implemented |
| KDE Wallet (kwalletd6) — secret authority | org.kde.kwalletd6 via Plasma login → kwalletd6 unlock → fetch-kwallet-secret.sh (ExecStartPre, ≤60s) | — | — | implemented |
| MeshChatX native backend / web UI | ReticulumMeshChatX 4.9.1 (native headless) | https://127.0.0.1:18000 | — | implemented |
| Reticulum transport (embedded in MeshChatX) | RNS embedded; standalone rnsd 1.4.2 present but not running | 0.0.0.0:4242 (backbone; NOT loopback-restricted) | — | in_progress |
| OpenClaw AI gateway + CORS relay | OpenClaw gateway (password auth) + chat relay | 127.0.0.1:18789, 127.0.0.1:18790 | — | implemented |
| LM Studio headless inference server | LM Studio (OpenAI-compatible endpoint, REST auth enforced) | 127.0.0.1:1234 | — | implemented |
| QGroundControl GCS (AppImage) | QGroundControl | — | tcp/127.0.0.1:5760 (SITL), MAVLink over DRONE-RADIO | partial |
| Fabrication simulation viewer (Foxglove) | foxglove_bridge 3.5.0, ros_gz_bridge (ros-lyrical-foxglove-bridge) | 127.0.0.1:8081 (foxglove_bridge ws, loopback only) | ao-html-window + ao-sim-fabrication, gz /factory/camera/image | implemented |
| Fabrication simulation portal (view-only HTML) | python3 http.server serving GAZEBO/portal/index.html | 127.0.0.1:8765 (http, loopback only) | — | implemented |
| Konqueror (browser; Tokodon removed per ES.1) | Konqueror / KDE WebEngine | — | http://127.0.0.1:3000 (Mastodon), http://127.0.0.1:3001 (Grafana), http://127.0.0.1:3002 (Metabase), http://127.0.0.1:8000 (WebODM) | implemented |
| SketchUp / SketchUp Web (design, host) | SketchUp desktop + SketchUp Web | — | — | planned |

## 5. Field, radio and drone link

| Component | Software | Hardware / path | Status | RF / note |
|---|---|---|---|---|
| Raspberry Pi 5 flight companion | MAVLink collector, telemetry spool, RNS/Reticulum, MeshChatX, packet signing | Waveshare SX1262-class LoRa HAT | planned | Design target; not present on the development workstation (README 9.1) |
| ArduPilot flight controller | 3DR N1 autopilot, MAVLink over UART/USB | — | planned |  |
| PEOPLE-RADIO (Heltec WiFi LoRa 32 V3) | RNodeInterface (RNode firmware 1.85, SX1262) | /dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0 | implemented | 915 MHz / BW 125 kHz / SF7 / CR5 / 17 dBm |
| DRONE-RADIO (Heltec WiFi LoRa 32 V3) | RNodeInterface (RNode firmware 1.85, SX1262, internal) | second CP2102-class serial device | implemented | 917 MHz / BW 250 kHz / SF7 / CR5 / 17 dBm |

## 6. Observed listeners

| Proto | Address | Port | Scope | Process (unprivileged view) | PID | Base-OS noise |
|---|---|---|---|---|---|---|
| tcp | 127.0.0.1 | 53 | loopback | — | — | yes |
| tcp | 169.254.248.253 | 53 | interface | — | — | yes |
| tcp | 10.42.0.1 | 53 | interface | — | — | yes |
| tcp | 127.0.0.54 | 53 | interface | — | — | yes |
| tcp | 127.0.0.53 | 53 | interface | — | — | yes |
| tcp | [fe80::b47b:8101:204:7f5b] | 53 | interface | — | — | yes |
| tcp | [::1] | 53 | interface | — | — | yes |
| udp | 127.0.0.1 | 53 | loopback | — | — | yes |
| udp | 169.254.248.253 | 53 | interface | — | — | yes |
| udp | 10.42.0.1 | 53 | interface | — | — | yes |
| udp | 127.0.0.54 | 53 | interface | — | — | yes |
| udp | 127.0.0.53 | 53 | interface | — | — | yes |
| udp | [fe80::b47b:8101:204:7f5b] | 53 | interface | — | — | yes |
| udp | [::1] | 53 | interface | — | — | yes |
| udp | 0.0.0.0 | 67 | wildcard | — | — | yes |
| udp | 127.0.0.1 | 323 | loopback | — | — | yes |
| udp | [::1] | 323 | interface | — | — | yes |
| tcp | 127.0.0.1 | 631 | loopback | — | — | yes |
| tcp | [::1] | 631 | interface | — | — | yes |
| tcp | 127.0.0.1 | 1234 | loopback | llmster | 2658 | no |
| tcp | 127.0.0.1 | 3000 | loopback | rootlessport | 8478 | no |
| tcp | 127.0.0.1 | 3001 | loopback | rootlessport | 3993374 | no |
| tcp | 127.0.0.1 | 3002 | loopback | rootlessport | 73881 | no |
| tcp | 127.0.0.1 | 3300 | loopback | python3 | 2385 | no |
| tcp | 127.0.0.1 | 4000 | loopback | rootlessport | 5967 | no |
| tcp | 0.0.0.0 | 4242 | wildcard | ReticulumMeshCh | 3637601 | no |
| tcp | 127.0.0.1 | 5345 | loopback | — | — | yes |
| udp | 0.0.0.0 | 5353 | wildcard | — | — | yes |
| udp | [::] | 5353 | interface | — | — | yes |
| tcp | 10.42.0.1 | 5432 | interface | socat | 5124 | no |
| tcp | 127.0.0.1 | 5432 | loopback | — | — | no |
| tcp | [::1] | 5432 | interface | — | — | no |
| tcp | 127.0.0.1 | 6379 | loopback | — | — | no |
| tcp | [::1] | 6379 | interface | — | — | no |
| tcp | 127.0.0.1 | 8000 | loopback | rootlessport | 3741 | no |
| tcp | 127.0.0.1 | 8080 | loopback | — | — | no |
| tcp | 127.0.0.1 | 8081 | loopback | rootlessport | 868063 | no |
| tcp | 0.0.0.0 | 8731 | wildcard | python3 | 1010842 | no |
| tcp | 127.0.0.1 | 8765 | loopback | python3 | 2905855 | no |
| tcp | 127.0.0.1 | 8899 | loopback | rootlessport | 6046 | no |
| tcp | 127.0.0.1 | 8900 | loopback | python3 | 6191 | no |
| tcp | 127.0.0.1 | 8931 | loopback | python3 | 3344577 | no |
| tcp | 127.0.0.1 | 9090 | loopback | rootlessport | 3284 | no |
| tcp | 127.0.0.1 | 15432 | loopback | rootlessport | 1238532 | no |
| tcp | 127.0.0.1 | 15433 | loopback | rootlessport | 1238994 | no |
| tcp | 127.0.0.1 | 18000 | loopback | ReticulumMeshCh | 3637601 | no |
| tcp | 127.0.0.1 | 18789 | loopback | MainThread | 5122 | no |
| tcp | [::1] | 18789 | interface | MainThread | 5122 | no |
| tcp | 127.0.0.1 | 18790 | loopback | python3 | 5123 | no |
| tcp | 127.0.0.1 | 20241 | loopback | cloudflared | 4542 | no |
| tcp | 127.0.0.1 | 25463 | loopback | cline | 9904 | no |
| tcp | 127.0.0.1 | 32941 | loopback | llama-server | 1851267 | no |
| tcp | 127.0.0.1 | 41343 | loopback | llmster | 2658 | no |

## 7. Documented claim vs observed state (drift)

| Result | Severity | Documented claim | Expected | Observed |
|---|---|---|---|---|
| drift | attention | v6 2.2/3.2: 'Ten ao-* networks present' | 10 live workload networks | 12 live workload networks (ao-admin, ao-data, ao-fabrication, ao-field, ao-html-window, ao-ledger-core, ao-ledger-ingest, ao-mapping, ao-payment, ao-sales, ao-sim-fabrication, ao-sim-vehicle) |
| drift | attention | v6 3.3: mastodon state consolidated onto Host PostgreSQL 18.6 | no mastodon-db container; mastodon uses host PG 18 database 'mastodon' | mastodon-db container running on ao-sales - container-scoped PostgreSQL |
| match | info | v6 3.3: WebODM backing data consolidated onto Host PG 18 (webodm/PostGIS 3.6.2) | no WebODM database container; webapp/worker use host PG 18 | no WebODM database container running; quadlet still declares ao-webodm-db (container-scoped DB) |
| match | info | v6 ES.1/3.3/18.2: Corda 5.2.2 persists in PostgreSQL 'cordadb'; the Corda 4.14.2 H2 scaffold was retired 2026-09-28 | no running Corda containers; cordadb is the documented persistence target | no running Corda containers (matches the blocked state; Corda 4 H2 scaffold retired 2026-09-28) |
| drift | mismatch | v6 5.1: all workload-domain networks are Internal=true | every workload network reports Internal=true | workload networks with Internal=false: ao-sales |
| drift | attention | README 4.1 rule 6 + listener-allowlist.yaml (listeners: []) - no public ports without approval | no unapproved non-loopback listener | 0.0.0.0:4242/tcp (ReticulumMeshCh), 10.42.0.1:5432/tcp (socat), [::1]:5432/tcp (unknown), [::1]:6379/tcp (unknown), 0.0.0.0:8731/tcp (python3), [::1]:18789/tcp (MainThread) |

---

Generated file — do not hand-edit. Re-run `python3 /ALWAYSON/scripts/operations/generate-topology.py` after any change.
