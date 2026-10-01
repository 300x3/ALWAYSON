# ALWAYS ON — generated system topology inventory

Generated: `2026-09-29T04:37:11Z`  
Authority: `/ALWAYSON/TOPOLOGY/ALWAYS ON — Architecture, Operations, and Status - v6.md` (README §3.1, §3.3, §5.1, §5.2, §6.A, §9, §20.0)  
Generator: `/ALWAYSON/scripts/operations/generate-topology.py`  
Observed mode: `live inspection`

Networks: **15** (12 live) · containers: **16** declared, 13 running · listeners: **77** (31 loopback) · drift items: **2**

## 1. Podman networks

| Network | Subnet | Gateway | Internal | Kind | Runtime | Status | Members |
|---|---|---|---|---|---|---|---|
| ao-admin | 10.89.9.0/24 | 10.89.9.1 | true | workload | live | implemented | ao-grafana, ao-metabase, ao-node-exporter, ao-prometheus |
| ao-build-update | — | — | ? | adapter | not created | planned | — |
| ao-data | 10.89.8.0/24 | 10.89.8.1 | true | workload | live | implemented | — |
| ao-egress-archive | — | — | ? | adapter | not created | planned | — |
| ao-egress-community | 10.89.11.0/24 | 10.89.11.1 | false | adapter | live | implemented | mastodon-sidekiq, mastodon-web |
| ao-field | 10.89.2.0/24 | 10.89.2.1 | true | workload | live | in_progress | — |
| ao-ingress-payment | — | — | ? | adapter | not created | planned | — |
| ao-ledger-core | 10.89.7.0/24 | 10.89.7.1 | true | workload | live | blocked | — |
| ao-ledger-ingest | 10.89.6.0/24 | 10.89.6.1 | true | workload | live | blocked | — |
| ao-mapping | 10.89.3.0/24 | 10.89.3.1 | true | workload | live | implemented | nodeodm, broker, db, webapp, worker |
| ao-payment | 10.89.1.0/24 | 10.89.1.1 | true | workload | live | planned | — |
| ao-reporting-egress | 10.89.10.0/24 | 10.89.10.1 | false | adapter | live | implemented | ao-grafana, ao-metabase |
| ao-sales | 10.89.0.0/24 | 10.89.0.1 | true | workload | live | in_progress | mastodon-db, mastodon-redis, mastodon-sidekiq, mastodon-streaming, mastodon-web, sales-db, 300x3-redis, 300x3-migrate, 300x3-sidekiq, 300x3-web, 300x3-streaming, 300x3-proxy |
| ao-sim-fabrication | 10.89.5.0/24 | 10.89.5.1 | true | workload | live | implemented | — |
| ao-sim-vehicle | 10.89.4.0/24 | 10.89.4.1 | true | workload | live | implemented | ardupilot-sitl |
| podman | 10.88.0.0/16 | 10.88.0.1 | false | **podman default** (not an ALWAYS ON domain) | live | declared | — |

## 2. Containers, networks, IPs and published ports

| Container | Local software / image | Networks + IP | Published ports | State | Status | systemd unit | Quadlet |
|---|---|---|---|---|---|---|---|
| broker | redis sha256:91d0f7e8c7 | ao-mapping=10.89.3.2 | internal only | running | implemented | active | yes |
| db | webodm_db sha256:03f18ec008 | — | internal only | not running | declared | inactive | yes |
| nodeodm | nodeodm sha256:553fe5cacb | ao-mapping=10.89.3.3 | internal only | running | implemented | active | yes |
| webapp | webodm_webapp sha256:188267c654 | ao-mapping=10.89.3.4 | internal only | running | implemented | active | yes |
| worker | webodm_webapp sha256:188267c654 | ao-mapping=10.89.3.5 | internal only | running | implemented | active | yes |
| ao-grafana | grafana-oss 11.6.0 | ao-admin=10.89.9.4, ao-reporting-egress=10.89.10.2 | 127.0.0.1:3001->3000/tcp | running | implemented | active | yes |
| ao-metabase | metabase v0.54.1 | ao-admin=10.89.9.5, ao-reporting-egress=10.89.10.3 | 127.0.0.1:3002->3000/tcp | running | implemented | active | yes |
| ao-node-exporter | node-exporter v1.9.1 | ao-admin=10.89.9.2 | internal only | running | implemented | active | yes |
| ao-prometheus | prometheus v3.4.1 | ao-admin=10.89.9.3 | 127.0.0.1:9090->9090/tcp | running | implemented | active | yes |
| mastodon-db | postgres sha256:a65e6a841f | ao-sales=10.89.0.10 | internal only | running | implemented | active | yes |
| mastodon-redis | redis sha256:91d0f7e8c7 | ao-sales=10.89.0.2 | internal only | running | implemented | active | yes |
| mastodon-sidekiq | mastodon sha256:76436bccad | ao-egress-community=10.89.11.5, ao-sales=10.89.0.11 | internal only | running | implemented | active | yes |
| mastodon-streaming | mastodon-streaming v4.3.7 | ao-sales=10.89.0.12 | 127.0.0.1:4000->4000/tcp | running | implemented | active | yes |
| mastodon-web | mastodon sha256:76436bccad | ao-egress-community=10.89.11.6, ao-sales=10.89.0.13 | 127.0.0.1:3000->3000/tcp | running | implemented | active | yes |
| sales-db | postgres sha256:a65e6a841f | — | publish 127.0.0.1:15432:5432 | not running | declared | inactive | yes |
| ardupilot-sitl | ardupilot-sitl latest | — | internal only | not running | declared | — | yes |
| 300x3-migrate | mastodon v4.3.7 | ao-sales=— | internal only | exited | unknown | — | **no** |
| 300x3-proxy | nginx alpine | ao-sales=— | 127.0.0.1:3000->80/tcp | exited | unknown | — | **no** |
| 300x3-redis | redis sha256:91d0f7e8c7 | ao-sales=— | internal only | exited | unknown | — | **no** |
| 300x3-sidekiq | mastodon v4.3.7 | ao-sales=— | internal only | exited | unknown | — | **no** |
| 300x3-streaming | mastodon-streaming v4.3.7 | ao-sales=— | internal only | exited | unknown | — | **no** |
| 300x3-web | mastodon v4.3.7 | ao-sales=— | internal only | exited | unknown | — | **no** |

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
| Gazebo Sim 10.5.0 + ROS 2 Lyrical | gz sim 10.5.0, ROS 2 Lyrical, ros_gz_bridge, foxglove_bridge | 127.0.0.1:8765 (foxglove_bridge ws), gz transport TCP/UDP | — | implemented |
| Konqueror (browser; Tokodon removed per ES.1) | Konqueror / KDE WebEngine | — | http://127.0.0.1:3000 (Mastodon), http://127.0.0.1:3001 (Grafana), http://127.0.0.1:3002 (Metabase), http://127.0.0.1:8000 (WebODM) | implemented |
| DBeaver (SQL client) | DBeaver — SQL client for the host PostgreSQL 18 cluster | — | 127.0.0.1:5432 (host PostgreSQL, ao-data reporting) | implemented |
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
| tcp | 10.42.0.1 | 53 | interface | — | — | yes |
| tcp | 127.0.0.1 | 53 | loopback | — | — | yes |
| tcp | 127.0.0.53 | 53 | interface | — | — | yes |
| tcp | 169.254.248.253 | 53 | interface | — | — | yes |
| tcp | 127.0.0.54 | 53 | interface | — | — | yes |
| tcp | [::1] | 53 | interface | — | — | yes |
| tcp | [fe80::b47b:8101:204:7f5b] | 53 | interface | — | — | yes |
| udp | 127.0.0.1 | 53 | loopback | — | — | yes |
| udp | 169.254.248.253 | 53 | interface | — | — | yes |
| udp | 10.42.0.1 | 53 | interface | — | — | yes |
| udp | 127.0.0.54 | 53 | interface | — | — | yes |
| udp | 127.0.0.53 | 53 | interface | — | — | yes |
| udp | [::1] | 53 | interface | — | — | yes |
| udp | [fe80::b47b:8101:204:7f5b] | 53 | interface | — | — | yes |
| udp | 0.0.0.0 | 67 | wildcard | — | — | yes |
| udp | 127.0.0.1 | 323 | loopback | — | — | yes |
| udp | [::1] | 323 | interface | — | — | yes |
| tcp | 127.0.0.1 | 631 | loopback | — | — | yes |
| tcp | [::1] | 631 | interface | — | — | yes |
| tcp | 127.0.0.1 | 1234 | loopback | llmster | 1330357 | no |
| tcp | 127.0.0.1 | 3000 | loopback | rootlessport | 2465061 | no |
| tcp | 127.0.0.1 | 3001 | loopback | rootlessport | 1776865 | no |
| tcp | 127.0.0.1 | 3002 | loopback | rootlessport | 1776899 | no |
| tcp | 127.0.0.1 | 3300 | loopback | python3 | 2714757 | no |
| tcp | 127.0.0.1 | 4000 | loopback | rootlessport | 2465038 | no |
| tcp | 0.0.0.0 | 4242 | wildcard | ReticulumMeshCh | 6562 | no |
| tcp | 127.0.0.1 | 5345 | loopback | — | — | yes |
| udp | 0.0.0.0 | 5353 | wildcard | — | — | yes |
| udp | 0.0.0.0 | 5353 | wildcard | — | — | yes |
| udp | [::] | 5353 | interface | — | — | yes |
| udp | * | 5353 | wildcard | — | — | yes |
| tcp | 127.0.0.1 | 5432 | loopback | — | — | no |
| tcp | 10.42.0.1 | 5432 | interface | socat | 5430 | no |
| tcp | [::1] | 5432 | interface | — | — | no |
| tcp | * | 6144 | wildcard | — | — | no |
| tcp | 127.0.0.1 | 6379 | loopback | — | — | no |
| tcp | [::1] | 6379 | interface | — | — | no |
| udp | 0.0.0.0 | 7000 | wildcard | parameter_bridg | 2749656 | no |
| udp | 0.0.0.0 | 7001 | wildcard | foxglove_bridge | 2749726 | no |
| tcp | 127.0.0.1 | 8000 | loopback | — | — | no |
| tcp | * | 8080 | wildcard | — | — | no |
| tcp | 127.0.0.1 | 8099 | loopback | python3 | 2749616 | no |
| tcp | 127.0.0.1 | 8765 | loopback | foxglove_bridge | 2749726 | no |
| tcp | 127.0.0.1 | 9090 | loopback | rootlessport | 4264 | no |
| udp | 0.0.0.0 | 10317 | wildcard | parameter_bridg | 2749656 | no |
| udp | 0.0.0.0 | 10317 | wildcard | gz-sim-main | 2749614 | no |
| udp | 0.0.0.0 | 10318 | wildcard | parameter_bridg | 2749656 | no |
| udp | 0.0.0.0 | 10318 | wildcard | gz-sim-main | 2749614 | no |
| udp | 0.0.0.0 | 12650 | wildcard | foxglove_bridge | 2749726 | no |
| udp | 0.0.0.0 | 12650 | wildcard | parameter_bridg | 2749656 | no |
| udp | 0.0.0.0 | 12660 | wildcard | parameter_bridg | 2749656 | no |
| udp | 0.0.0.0 | 12661 | wildcard | parameter_bridg | 2749656 | no |
| udp | 0.0.0.0 | 12662 | wildcard | foxglove_bridge | 2749726 | no |
| udp | 0.0.0.0 | 12663 | wildcard | foxglove_bridge | 2749726 | no |
| tcp | 127.0.0.1 | 18000 | loopback | ReticulumMeshCh | 6562 | no |
| tcp | 127.0.0.1 | 18789 | loopback | MainThread | 1386386 | no |
| tcp | [::1] | 18789 | interface | MainThread | 1386386 | no |
| tcp | 127.0.0.1 | 18790 | loopback | python3 | 1386388 | no |
| tcp | 127.0.0.1 | 20241 | loopback | cloudflared | 5038 | no |
| tcp | 127.0.0.1 | 25463 | loopback | cline | 1476278 | no |
| tcp | 127.0.0.1 | 32895 | loopback | parameter_bridg | 2749656 | no |
| tcp | 127.0.0.1 | 33817 | loopback | llama-server | 3747470 | no |
| tcp | 127.0.0.1 | 35731 | loopback | parameter_bridg | 2749656 | no |
| tcp | 127.0.0.1 | 41343 | loopback | llmster | 1330357 | no |
| tcp | 127.0.0.1 | 41489 | loopback | gz-sim-main | 2749614 | no |
| tcp | 127.0.0.1 | 44000 | loopback | podman-desktop | 3161889 | no |
| tcp | 127.0.0.1 | 44897 | loopback | gz-sim-main | 2749614 | no |
| udp | 169.254.248.253 | 46206 | interface | foxglove_bridge | 2749726 | no |
| tcp | 127.0.0.1 | 46229 | loopback | parameter_bridg | 2749656 | no |
| udp | 192.168.87.135 | 46453 | interface | parameter_bridg | 2749656 | no |
| tcp | 127.0.0.1 | 46695 | loopback | gz-sim-main | 2749614 | no |
| udp | 0.0.0.0 | 49653 | wildcard | foxglove_bridge | 2749726 | no |
| udp | 10.42.0.1 | 53355 | interface | parameter_bridg | 2749656 | no |
| udp | 0.0.0.0 | 53857 | wildcard | parameter_bridg | 2749656 | no |
| udp | 10.42.0.1 | 54404 | interface | foxglove_bridge | 2749726 | no |
| udp | 169.254.248.253 | 58217 | interface | parameter_bridg | 2749656 | no |
| udp | 192.168.87.135 | 59006 | interface | foxglove_bridge | 2749726 | no |

## 7. Documented claim vs observed state (drift)

| Result | Severity | Documented claim | Expected | Observed |
|---|---|---|---|---|
| match | info | v6 2.2/3.2: 'Ten ao-* networks present' | 10 live workload networks | 10 live workload networks (ao-admin, ao-data, ao-field, ao-ledger-core, ao-ledger-ingest, ao-mapping, ao-payment, ao-sales, ao-sim-fabrication, ao-sim-vehicle) |
| drift | attention | v6 3.3: mastodon state consolidated onto Host PostgreSQL 18.6 | no mastodon-db container; mastodon uses host PG 18 database 'mastodon' | mastodon-db container running on ao-sales - container-scoped PostgreSQL |
| match | info | v6 3.3: WebODM backing data consolidated onto Host PG 18 (webodm/PostGIS 3.6.2) | no WebODM database container; webapp/worker use host PG 18 | no WebODM database container running; quadlet still declares ao-webodm-db (container-scoped DB) |
| match | info | v6 ES.1/3.3/18.2: Corda 5.2.2 persists in PostgreSQL 'cordadb'; the Corda 4.14.2 H2 scaffold was retired 2026-09-28 | no running Corda containers; cordadb is the documented persistence target | no running Corda containers (matches the blocked state; Corda 4 H2 scaffold retired 2026-09-28) |
| match | info | v6 5.1: all workload-domain networks are Internal=true | every workload network reports Internal=true | all live workload networks are Internal=true |
| drift | attention | README 4.1 rule 6 + listener-allowlist.yaml (listeners: []) - no public ports without approval | no unapproved non-loopback listener | 0.0.0.0:4242/tcp (ReticulumMeshCh), 10.42.0.1:5432/tcp (socat), [::1]:5432/tcp (unknown), *:6144/tcp (unknown), [::1]:6379/tcp (unknown), 0.0.0.0:7000/udp (parameter_bridg), 0.0.0.0:7001/udp (foxglove_bridge), *:8080/tcp (unknown), 0.0.0.0:10317/udp (parameter_bridg), 0.0.0.0:10317/udp (gz-sim-main), 0.0.0.0:10318/udp (parameter_bridg), 0.0.0.0:10318/udp (gz-sim-main), 0.0.0.0:12650/udp (foxglove_bridge), 0.0.0.0:12650/udp (parameter_bridg), 0.0.0.0:12660/udp (parameter_bridg), 0.0.0.0:12661/udp (parameter_bridg), 0.0.0.0:12662/udp (foxglove_bridge), 0.0.0.0:12663/udp (foxglove_bridge), [::1]:18789/tcp (MainThread), 169.254.248.253:46206/udp (foxglove_bridge), 192.168.87.135:46453/udp (parameter_bridg), 0.0.0.0:49653/udp (foxglove_bridge), 10.42.0.1:53355/udp (parameter_bridg), 0.0.0.0:53857/udp (parameter_bridg), 10.42.0.1:54404/udp (foxglove_bridge), 169.254.248.253:58217/udp (parameter_bridg), 192.168.87.135:59006/udp (foxglove_bridge) |

---

Generated file — do not hand-edit. Re-run `python3 /ALWAYSON/scripts/operations/generate-topology.py` after any change.
