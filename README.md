![ALWAYS ON — WEBSITEMAIN][figure-01]

# ALWAYS ON

## Detailed system specification

| Field | Required definition |
|---|---|
| Document role | Prescriptive architecture, configuration, interface, data, operational-control and acceptance specification |
| Scope | Local live/work/fabricate platform, vehicles, equipment, commerce and supporting infrastructure |
| Normative language | SHALL / SHALL NOT = mandatory; SHOULD = recommendation; MAY = permitted option |
| Configuration interpretation | Component tables, addresses, paths, schemas, directory trees and interface definitions are normative unless explicitly labeled an example or a deployment parameter |
| Current workstation | Existing Intel CPU; NVIDIA GTX 1080; AMD preferred for future CPU procurement |
| Peripheral host | Drone Raspberry Pi 5 with Autopilot Module, KaliOS; field hardware/integration in §9 |
| Desktop identity | Kubuntu 26.04 LTS base with KDE Plasma; source Kubuntu labels SHALL be reconciled as inventory, not force an OS replacement or flavour-metapackage assumption |
| Container policy | Podman with systemd Quadlet for suitable services, including Corda; appropriate host-native services permitted |
| Credential gate | Authenticated operator login and authorized credential availability before protected workload startup |
| Public simulation | Approved read-only Foxglove/Gazebo view through `ao-html-window`; never a public control/admin path |
| License notice | CC BY-NC-SA as identified by the source; exact version is not silently changed |

The following sections SHALL define the required system, not the state of a particular deployment. Specific settings and structures SHALL remain in this document; a tracker item SHALL NOT substitute for their specification. Implementation gaps and completion evidence SHALL remain in `README-ACTION_ITEMS/status-and-references.md` (the repository tracker path). The [separate companion](README-COMPANION.md) contains historical records, rationale, runbook material and source preservation; §3.2 defines the status/evidence boundary.

A genuine unspecified parameter SHALL be labeled narrowly at the affected interface. This document SHALL NOT invent a credential, image digest, surveyed datum, public hostname or migration target absent from the supplied design. The seven operator clarifications in this document govern contrary historical wording.

## Contents

| Section | Subject |
|---|---|
| [ES.1](#section-es-1) | Architecture requirements |
| [ES.2](#section-es-2) | Master topology and presentation boundaries |
| [ES.3](#section-es-3) | Detailed System Record and operator warning |
| [1](#section-1) | System purpose and platform identity |
| [2](#section-2) | Platform baseline and version requirements |
| [3](#section-3) | Architecture, fabrication and database map |
| [4](#section-4) | Security, classifications and allowed/prohibited paths |
| [5](#section-5) | Detailed network, adapter, component and GUI matrices |
| [6](#section-6) | Reporting and operator access |
| [7](#section-7) | Storefront, modal views, payments and receipts |
| [8](#section-8) | Mapping storage, directory tree and processing |
| [9](#section-9) | Field, radios and mission transport |
| [10](#section-10) | Simulation worlds, boning, RL, cameras, portals and public view |
| [11](#section-11) | Corda, manifests, provenance and accounting |
| [12](#section-12) | Provisioning, vendor artifacts and software inventory |
| [13](#section-13) | Rootless runtime, repository layout and Quadlet templates |
| [14](#section-14) | Wallet, delivery map, D-Bus, tokens and recovery |
| [15](#section-15) | Sales, local AI, Mastodon, federation and mail |
| [16](#section-16) | Script layout, generator package, journals and compilation |
| [17](#section-17) | Backup, restore, security monitoring, retention and acceptance |


<a id="section-es-1"></a>

## ES.1 Architecture requirements

The complete architecture summary below SHALL remain part of the specification. The numbered sections provide its detailed configuration and interfaces; the table SHALL NOT substitute for those details. Dated implementation observations SHALL remain separate.

| Subject | Required architecture; implementation evidence is separate |
|---|---|
| Social media | Most closely tied to the **remote fediverse**: public marketing/contact across website chat, email, Mastodon, and approved social channels, with the fediverse chatbot routing into other social media systems. **OpenClaw** is the direct Mastodon publisher; its local output is standardized PDFs for order/follow-up/support/payment workflows, processed into the sales, payment, and ledger records. `ao-sales` connects to the remote fediverse only (§4.3) |
| LM Studio | Fundamental local LLM host for OpenClaw |
| Browser | Konqueror — dedicated browser for automation |
| Automated testing | Playwright and Chrome verify loopback service reachability per `config/platform/loopback-services.yaml`; results are recorded in §19.2 |
| RNode client A — PEOPLE-RADIO | **MeshChatX**, which is the coordination system for the ALWAYS ON Reticulum network stack and the LoRa radios. It only needs to speak to the **Reticulum network stack**, and the RNode is its radio. **Raw LoRa over Reticulum (RNode), not LoRaWAN** — the public human side (§9.2.2). Reticulum end-to-end confidentiality, authentication and approved key/forward-secrecy behavior SHALL be enforced for this path; plaintext or unauthenticated mission traffic SHALL NOT be accepted |
| RNode client B — DRONE-RADIO | **LoRa mesh RNode for drones only** — the private drone side. Carries a **dedicated RNS-enabled connection** from QGroundControl to the drones over DRONE-RADIO, so local QGC missions reach the QGC session on the Pi5 drone and missions can be **updated midflight** (§9.2.2) |
| Radios | **Wi-Fi** — Wi-Fi/Ethernet from the main desktop reaches the main internet; that desktop manages all DHCP. **2 LoRa radios** — `PEOPLE-RADIO` (915 MHz) = public human chat, `DRONE-RADIO` (917 MHz) = authenticated private drone mission/status traffic (§9.2.2) |
| QGroundControl | Desktop primary mission planning; KaliOS RPi5 fallback/out-of-range mission-update operation; and drone — KaliOS on the Raspberry Pi 5 with the Autopilot Module, running ArduPilot. It holds a **dedicated RNS-enabled connection to the drones over DRONE-RADIO**, and so receives **midflight mission updates** relayed by DRONE-RADIO to the QGC session on the Pi5 drone (§9.2.2) |
| **Email endpoint** | The storefront routes the buyer through the **EMAIL TEMPLATE** (not an inbox); the host reviews every purchase request against that template. Complete → published as a PDF, a **WORK ORDER REQUEST**; incomplete → sent back by email requesting the remaining information (§4.3) |
| Prometheus | Prometheus is for security only. It acts alone and independently, operating on the other systems to ensure security and to address any problems: time-series store, rule evaluation, alerting, and security evidence; operated under the §17 security controls |
| Grafana | Dashboards and metrics only; it reads the databases that already exist and does not write to them |
| Metabase | Reporting only, and it does ad-hoc read-only reporting, so it requires **its own dedicated PostgreSQL application database** to hold its Metabase schema, saved questions, dashboards, and subscriptions. That application database holds Metabase's own state only — it is not a system of record for business data, and it never receives data from the reporting sources. Metabase connects to the other PostgreSQL and MySQL databases, and to local desktop-application SQLite files, as a **read-only** user in order to report on them, and it never writes to them. Ad-hoc reports that become recurring are promoted into stable Grafana dashboards |
| Corda | Blockchain-enabled accounting, ledger, receipt, entitlement, fulfillment, provenance, and approved state-transition system. SHALL run under Podman/Quadlet on **Corda 5.2.2** against `cordadb` — one database within the regular host PostgreSQL 18 cluster, with its own roles and backup scope (§11.1) |
| IPFS | **File-transfer verification and sales listing on a blockchain** for approved map/imagery and telemetry/product-operational packages. **It is not a backup.** No Corda/ledger/accounting dependency |
| Backup/restore | Local authority + **encrypted restic** (§17.1). Independent of IPFS and Corda. This is the *only* backup |
| Sale transfer | `ao-egress-archive` holds packages **"archived for data transfer and sale"** — a transfer copy, **not** a backup. IPFS first (transfer verification **and** blockchain listing), then encrypted pCloud. **Requires `ao-sales` authorisation** first (§11.6) |
| Secret authority | KDE Wallet; services needing Wallet secrets start after KDE login |
| GPU policy | Priority: desktop/Konqueror → SketchUp/SketchUp Web → active LM Studio/OpenClaw → ROS/Gazebo/SITL → WebODM batch |
| Additive fabrication | Real machines, not simulated cells: **MainsailOS/Moonraker/Klipper operate on each individual 3D printing machine**, each on its own BigTreeTech CB1 / Raspberry Pi; individual CNC machines likewise. These are **real peers**, not children of the simulated domain. `ao-sim-fabrication` **rehearses** the flow for the **kitchen, cooler/freezer/pantry carousel, storage carousel, and their robot-arm boxes** (2 arms in 2 boxes at storage, which organize and manage the additive-manufacturing machines; 2 arms on independent rails at the kitchen, which cook); it rehearses the kitchen and holds no production data. **The simulation does not manage those robot arms or carousels** — they need the separate future `ao-auto(kitchen,cool,store,fab)-` domain (§10.2) |
| **Real fabrication** | **`ao-fabrication`** is the real (non-simulated) fabrication domain, distinct from `ao-sim-fabrication` in every respect (§3.3.0): it **pulls data into its own database** for industrial engineering and fabrication optimisation — per-machine production data lands in **`a_fab`** (`10.89.12.0/24`, `Internal=true`). Individual CNC machines on their own RPis SHALL run **bCNC** where a machine-side sender is required, tied to Klipper/MainsailOS where the machine supports it |
| Simulation (fabrication) | `ao-sim-fabrication` requires, as baseline capability and not optional extras: **3D world setup** (its own world), **boning** (alignment and datum structure built into that world), **reinforcement learning objects** (the trainable entities for scenario and policy work), and an **HTML portal to operation** — set up and operated from a browser, with no desktop GUI client (§10.2) |
| Simulation (vehicles) | `ao-sim-vehicle` requires the same four baseline capabilities as `ao-sim-fabrication` (§10.1) |
| Home automation | Domoticz/RPi for the Domoticz home automation features: HVAC, doors/locks/access, security/alarms, lighting/scenes, cameras, weather, environmental sensing, media, and other Domoticz device classes; separate from printers and future building robotics |
| Public simulation view | `ao-html-window` SHALL provide a public read-only Foxglove/Gazebo presentation. Backend lifecycle/control, command publication and administration SHALL remain private (§10.2.2). |
| CPU procurement | Existing Intel workstation accepted; AMD preferred for future procurement, not a required current replacement. |
| Network simplicity | Explicit least-privilege boundaries SHALL govern attachments; multiple required attachments MAY be used; detailed CIDRs SHALL remain unless approved changes replace them. |
| Credential startup | All protected services/dependents SHALL load/start after authenticated operator login and usable authorized credentials; no stale-file/timer/linger bypass. |



<a id="section-es-2"></a>

## ES.2 Master topology

The master topology SHALL represent the detailed interfaces in the numbered specification. Existing graphics are retained as design illustrations; a graphic SHALL NOT override a corrected written interface, authorize a route or serve as deployment evidence.

![ALWAYS ON — complete topology, landscape][figure-02]

![ALWAYS ON — topology, columns 1–3: outside world, adapters, workload domains][figure-03]

![ALWAYS ON — topology, columns 4–9: stores, field, sales, secrets, what actually happens][figure-04]

| Asset | Role |
|---|---|
| `assets/ao-single-topology.svg` | Vector topology source/view |
| `assets/ao-single-topology.html` | Offline self-contained topology viewer |
| `config/platform/topology-model.yaml` | Structured topology model |
| `config/platform/network-cidrs.yaml` | Approved network/CIDR/internal-flag registry |
| `config/platform/gui-boundary-matrix.yaml` | Approved tool/access boundary map |
| `config/platform/version-matrix.yaml` | Captured platform/image identity baseline |

The public boundaries SHALL be distinct: static storefront, approved federation/chat, verified payment entry and public read-only simulation presentation. Authorized sale transfer and update acquisition SHALL be controlled outbound functions. Internal processing, databases, live control, wallet and security monitoring SHALL NOT become public through these interfaces.


<a id="section-es-3"></a>

## ES.3 Detailed System Record

This document SHALL define the complete system architecture, installation/configuration contract, interfaces, operating constraints and acceptance requirements. Technical tables, directory trees, configuration blocks, schema definitions and executable checks SHALL remain beside the design they specify. They SHALL NOT be replaced with a work queue.

The companion SHALL preserve non-normative operational evidence, troubleshooting, historical corrections and supporting explanation with source references. The status tracker SHALL identify actual implementation gaps and closure evidence. A historical measurement SHALL NOT override a requirement; a required feature SHALL NOT be claimed implemented solely because it appears here.

> **Operator warning.** Everything here is difficult until it is easy. These tools
> are sharp and dangerous, and if you disrespect them they will harm you —
> the same as any trip, fall, or car ride. Ignoring them is more dangerous than
> understanding them.


<a id="section-1"></a>

## 1. System Purpose

ALWAYS ON SHALL provide an on-premises platform for an automated modular live/work/fabricate facility of 160 square feet and an accompanying micro-aircraft carrier. Both SHALL scale in size and quantity within this architecture.

| Capability | Scope |
|---|---|
| Field | Drone telemetry and field communications over the Reticulum mesh |
| Mapping | Photogrammetry and 3D model production |
| Simulation | Vehicle rehearsal; fabrication, facility, inventory, kitchen and logistics rehearsal |
| Facility | Home automation |
| Commerce | Static storefront, hosted checkout, receipt generation |
| Provenance | Corda-backed receipts, entitlements and approved state transitions |
| Archive | Encrypted pCloud replication and controlled IPFS distribution |
| Content | Static HTML and interactive iframe content from other servers |


### Deployment and desktop baseline

The workstation SHALL be the development, integration and validation host. Its accepted hardware baseline SHALL be the existing Intel CPU (source baseline: Core i7-8700K) and NVIDIA GTX 1080. AMD SHALL be preferred for future CPU procurement; the existing Intel workstation SHALL NOT require replacement to conform. Compute-intensive production workloads SHALL be deployable to an immersion-cooled rack and Raspberry Pi edge cluster.

Kubuntu 26.04 LTS SHALL be the base distribution and KDE Plasma SHALL be the desktop. The platform SHALL provide KDE Wallet for login-gated credentials, Konqueror for automation, the KDE desktop/portable environment, and ROS 2/Gazebo/QGroundControl integration. Verification SHALL NOT require the `kubuntu-desktop` metapackage, `/etc/kubuntu-release`, or a Kubuntu distributor string. Base-distribution maintenance and desktop-flavour maintenance SHALL be tracked separately; support-calendar commentary belongs in the companion.

Podman SHALL be the preferred runtime for container-suitable platform services, including Corda. systemd Quadlet SHALL manage those containers. Suitable host-native desktop, hardware-facing and system services MAY remain native; this is not a requirement to containerize every process. Docker daemon, Docker Compose, Watchtower and Kubernetes SHALL NOT substitute for the specified orchestration.

ROS 2 Lyrical SHALL be installed at `/opt/ros/lyrical`; Gazebo Sim 10.5.0 SHALL run containerized. Checks SHALL NOT assume host `gzserver` on PATH. QGroundControl SHALL be supplied as a user-level AppImage with a `.desktop` launcher under `~/.local/share/applications`; package ownership or a binary in `/usr/share/applications` SHALL NOT be prerequisites. Inventory SHALL distinguish packages, AppImages and local builds.

All workloads requiring protected credentials SHALL start only after authenticated operator login and authorized credential availability (§14).


<a id="section-2"></a>

## 2. Platform Baseline


<a id="section-2-1"></a>

### 2.1 Intended Platform Standard

| Area | Architecture requirement |
|---|---|
| Host OS | Kubuntu 26.04 LTS workstation with KDE Plasma desktop; the platform identity is defined in §1 (Kubuntu 26.04 LTS base + KDE Plasma; `kubuntu-desktop` not required) |
| Accepted CPU/GPU | Intel CPU and EVGA NVIDIA GTX 1080; AMD preferred for future procurement |
| Future compute | Immersion-cooled server rack and Raspberry Pi edge cluster |
| Container engine | Podman for container-suitable services; host-native applications permitted |
| Container lifecycle | systemd and Podman Quadlet |
| Public website | Static HTML in pCloud Public Folder + Cloudflare domain registration |
| Payments | Provider-hosted checkout and verified payment events; no local card handling; local stablecoin processing |
| Sales and support | Sales API, PostgreSQL, Mastodon integration, OpenClaw, and LM Studio |
| Drone compute | Raspberry Pi 5 with Waveshare SX1262-class LoRa top-hat |
| Drone autopilot | 3DR N1 connected to Raspberry Pi 5 by MAVLink |
| Desktop radios | Two Heltec LoRa 32 V3 (SX1262), distinguished by USB port topology as `/dev/ao-drone-radio` (ttyUSB0, DRONE-RADIO 917 MHz) and `/dev/ao-people-radio` (ttyUSB1, PEOPLE-RADIO 915 MHz) |
| Field protocol | RNS/Reticulum and MeshChatX over raw LoRa, SHALL be the active field protocol; a true LoRaWAN deployment, if ever selected, requires its own requirement row and verification before it replaces raw LoRa |
| Mapping | WebODM and supporting services under Podman |
| Mapping storage | `/media/scottw/500GBPHOTOGRAM/` |
| Vehicle simulation | ROS 2 Lyrical, Gazebo Sim 10.5.0, ArduPilot SITL, MAVLink, QGroundControl |
| Fabrication simulation | ROS 2 Lyrical, Gazebo Sim 10.5.0, robot cells, additive manufacturing, storage, kitchen, and logistics models |
| Ledger | Corda core behind a dedicated ledger-ingestion gateway |
| Archive | Local source data, signed manifests, encrypted pCloud replication, private or encrypted IPFS workflow |
| Monitoring | Prometheus-compatible metrics, alerts, health checks, and protected administration access |
| Backup | PostgreSQL/Corda-aware backup via restic (single named tool), encrypted restic; restore testing SHALL run monthly and after every backup-format change, tied to a unit/timer |


<a id="section-2-2"></a>

### 2.2 Platform Baseline

Every value below SHALL be a rebuild/validation requirement, not a report of measured host state.

| Area | Required baseline |
|---|---|
| Kernel | Ubuntu 26.04 LTS kernel consistent with §1 |
| Podman | Rootless operator-owned workload store (§13) |
| Networks | Explicit CIDR/flag allocations in §5.1.1 and hand-maintained `config/platform/network-cidrs.yaml`; counts derived from the approved registry, not a fixed architectural goal |
| CPU | Existing Intel workstation; AMD preferred only for future procurement |
| GPU | EVGA NVIDIA GTX 1080 |
| NVIDIA driver | Pinned and recorded in version matrix |
| NVIDIA CDI | `nvidia.com/gpu=0`; authoritative `/var/run/cdi/nvidia.yaml`; stale `/etc/cdi/nvidia.yaml` SHALL NOT contribute duplicate definitions |
| Simulation | ROS 2 Lyrical at `/opt/ros/lyrical`; Gazebo Sim 10.5.0 |
| Host PostgreSQL | PostgreSQL 18; loopback-only source listener; any relay separately constrained |
| Host Redis | Redis 8; loopback-only |

Driver changes SHALL regenerate/remove obsolete CDI specifications and validate container GPU access. Every registered network SHALL match its declared CIDR/flag, and every runtime `ao-*` network SHALL be registered.


<a id="section-2-3"></a>

### 2.3 Packages the Verification Steps Depend On

A package is part of the platform baseline if the platform's own verification asserts on it. The
install list itself is written in §12.3; the requirement is stated here because the two SHALL agree.

Every package below is **required to be reproducible from the repository's own bootstrap chain**
(`scripts/bootstrap/02-install-host-dependencies.sh` and
`scripts/bootstrap/ao-bootstrap-privileged.sh`, documented in §12.3). A host that is correct only
because an operator installed a package by hand does **not** satisfy this requirement — the
provisioning path is the deliverable, not the host's current package list.

| Package | Required for |
|---|---|
| `apparmor-utils` | `aa-enforce`, `aa-decode`, `aa-genprof`, `aa-logprof` — the profile tools §4.1 relies on |
| `nvidia-container-toolkit` (+ `libnvidia-container1`, `libnvidia-container-tools`, `nvidia-container-toolkit-base`) | GPU access from rootless containers via CDI; the `nvidia.com/gpu=0` device the version matrix records |

**Verification rules for the AppArmor tooling.** These are normative, because each one has
defeated a naive check:

- Test for **`aa-enforce`**, not `aa-status`. `aa-status` ships in the base `apparmor` package, so
  `command -v aa-status` succeeds on a host with no profile tooling installed at all.
- A check SHALL **not** wrap its subject in `sudo … || true`. On this host `sudo` requires
  interactive authentication, so the pipeline cannot fail and cannot inspect anything — while
  still reporting success.
- Any check whose subject requires privilege SHALL report the privilege failure as a failure. A
  check that cannot fail verifies nothing.


<a id="section-2-4"></a>

### 2.4 Baseline Verification Must Assert

A verification step **asserts**; it does not print. Each requirement below is normative:

1. Every check SHALL compare an observed value against an expected one and **exit non-zero when
   they differ**. A silent non-zero return that nothing reads is not an assertion.
2. The overall block SHALL exit non-zero if any check fails. A block whose exit status is
   unconditionally zero cannot verify anything, and evidence produced by it cannot be re-run and
   trusted.
3. Each observed value SHALL be **printed beside its expected value**, so a failure is readable
   without re-running the check.
4. A check SHALL run a **control case** before a zero is believed. Counting constructs that return
   a constant regardless of input — for example `systemctl list-unit-files 'pattern' | wc -l`,
   which always prints three lines — SHALL NOT be used as evidence. Use a form that measures the
   thing itself, such as `grep -c '^ao-'`.
5. Every claim cited as evidence SHALL be **reproducible by the command shown**. A citation that
   does not reproduce is not evidence.

The §12.3 verify block is owned by the OPS-B session; the requirements above are what it SHALL
satisfy.


<a id="section-2-5"></a>

### 2.5 Version Matrix Requirements

`config/platform/version-matrix.yaml` is the machine-readable platform baseline and SHALL satisfy:

1. **Every running container image is digest-pinned.** A tag-only image cannot be verified as
   deployed. Only these are permitted exceptions, and both are deliberate:
   - `ardupilot-sitl:latest` — a moving SITL tag by design;
   - the locally built Gazebo Sim image, whose digest records the validated local build.
2. **No stray container may duplicate a Quadlet-managed unit.** Any container whose name is
   generated by `podman run` rather than owned by a Quadlet unit is residue and SHALL be removed.
   Removal is a delete and requires operator approval per §4.1 rule 3.
3. **Every digest the matrix records SHALL be a digest a container actually runs**, and every
   running digest SHALL appear in the matrix. A matrix that names a digest nothing runs cannot be
   used to verify what is deployed.
4. **Kernel and package versions SHALL be captured, not hand-transcribed.** The matrix is to be
   produced by a generator that reads the running host, so it cannot silently drift.


<a id="section-3"></a>

## 3. High-Level Architecture


<a id="section-3-1"></a>

### 3.1 Isolation Detail View

This is a **detail view of the ingress/egress portion of the master topology in
ES.2** and SHALL NOT contradict it. For the whole project, read ES.2.

![Zoom of the controlled adapter column of the ES.2 master topology, at readable scale. The adapters are the only processes permitted to cross the host boundary.][figure-05]

*Figure 3.1 — The controlled adapter column of the ES.2 master topology, enlarged. It is a
zoom of that one graphic, not a separate diagram: the adapter column is the only place a
controlled ingress or egress process SHALL exist, and every route into or out of the host passes
through it.*

The public storefront has no direct route to the host's field, mapping, simulation, database,
AI, Podman or Corda-core services.


<a id="section-3-2"></a>

### 3.2 Where Status Lives

Sections 1–16 SHALL define the required system and SHALL NOT claim deployment completion. Status and outstanding work SHALL live in §19.1 of `README-ACTION_ITEMS/status-and-references.md`; verification evidence SHALL live in its evidence sections. The implementation tracker SHALL NOT override the specification or substitute for a concrete configuration definition.

Executable acceptance checks MAY remain beside their requirements. Captured outputs, historical failures and measurements SHALL be preserved in the companion or linked tracker evidence, not silently discarded. A required enum, service or executor SHALL NOT be described as deployed merely because this document specifies it.


<a id="section-3-3"></a>

### 3.3 Databases and Data Stores

PostgreSQL is the system-wide relational platform. Business domains SHALL NOT be collapsed into one shared database authority:
a host-managed PostgreSQL 18 cluster, loopback-only, carries host administration and the
Grafana and Metabase application databases, and each domain that owns authoritative data
runs **its own dedicated PostgreSQL container** with its own image and its own version.
Every consumer gets a separate logical database and a separate application role inside its
own container. The version behind each row is stated in §3.3.1.

| Database | Holds |
|---|---|
| `salesdb` | Authoritative sales and payment records |
| `mastodon` | Mastodon application state |
| `webodm` | WebODM/PostGIS mapping data |
| `cordadb` | Corda 5, with its own roles and backup scope (§11.1) |
| `a_fab` | Real-machine production data for `ao-fabrication` (§3.3.0) |
| `postgres` | Administration and maintenance |

**Reporting and coordination stores.** Three stores sit alongside PostgreSQL. **All three are read-only over the databases above;
none is a system of record, and none ever writes to a source database.**

| Store | Purpose | Boundary |
|---|---|---|
| **Grafana** | Stable, curated, long-lived dashboards and metrics — a number that SHALL stay on a wall or in a briefing | Reads approved PostgreSQL datasources read-only. Keeps its own PostgreSQL application database for users, dashboards and datasource configuration |
| **Metabase** | Ad-hoc reporting: a question asked in the browser, saved, filtered, exported. The saved question, not the dashboard, is the unit of work | Reads the other PostgreSQL and MySQL databases **and** local SQLite files over per-source read-only roles — one read-only role per source, so a badly written query cannot modify a source. Keeps its own PostgreSQL application database for its schema, saved questions, dashboards, filters and subscriptions. That database is not a system of record and is never written to by a reporting source |
| **Prometheus** | Security instrumentation only — time-series store, rule evaluation, alerting | Acts alone and independently. Does security work **outward**, on the PostgreSQL and SQLite databases and the services around them; nothing acts on it or reaches into it (§3.3). Not replaced by PostgreSQL, Grafana or Metabase, and does not depend on any of them |

A recurring ad-hoc Metabase report that proves its worth is **promoted into a Grafana
dashboard**, where it becomes stable and curated.

**Redis** is a low-latency speed and coordination layer — caching, queues, locks, task
brokering, transient coordination. It is not the authoritative system of record; business,
payment, user and application metadata stay in PostgreSQL.

**SQLite and H2** are not approved application databases for Grafana or Metabase. They SHALL
exist only where an individual application requires embedded local storage — the browser,
Akonadi, Podman, MeshChatX, QGroundControl — or in retained migration backups.

**Database and ledger authority.**

| Authority | Owns |
|---|---|
| **PostgreSQL** | Detailed operational data, searchable business records, and reporting projections |
| **Corda** | The complete ledger of debits and credits, final sale and contract state, receipt association, entitlement, and approved ledger state transitions |

Where PostgreSQL holds the detailed operational and searchable business record, Corda holds
the authoritative debit and credit position itself.


Corda's specified `cordadb` in the host PostgreSQL 18 cluster (§11.1) SHALL be the explicit database-placement exception to general per-domain database containers; the Corda application SHALL still run under Podman. Dedicated role/backup and restricted host-mediated access SHALL preserve ledger separation.


<a id="section-3-3-0"></a>

#### 3.3.0 `a_fab` — the real-fabrication database

**`a_fab` is the database of `ao-fabrication`, the real (non-simulated) fabrication
domain.** It is a separate logical database with its own application role, and it is
not shared with `ao-sim-fabrication`.

The distinction that matters:

- **`ao-sim-fabrication`** rehearses the fabrication flow. It holds no production data
  and never commands live machinery.
- **`ao-fabrication`** pulls real production data **from each individual machine into its
  own database** for industrial engineering and fabrication optimisation work.

Each real machine runs **its own** MainsailOS / Moonraker / Klipper on its own
BigTreeTech CB1 / Raspberry Pi. The machines are peers: none of them is a child of the
simulated fabrication domain, and none is drawn as a simulated cell. They sit on the
**equipment LAN** (`10.42.0.0/24`, the wired segment whose DHCP the desktop manages).
That LAN is *ingress* — local equipment — not egress, and it is deliberately not a
workload network.


<a id="section-3-3-0-1"></a>

##### 3.3.0.1 How the domain reaches the equipment LAN (host-mediated)

`ao-fabrication` SHALL use `Internal=true` and `10.89.12.0/24`. Its production collector SHALL run on the host as `ao-fabrication-collect`, poll approved Moonraker/machine endpoints on equipment LAN `10.42.0.0/24`, and write authorized per-machine records into `a_fab` using scoped credentials. It SHALL NOT enable unrestricted forwarding from the application domain onto the equipment LAN.

| Interface | Required use | Boundary |
|---|---|---|
| Desktop `eno1`, `10.42.0.1/24` | Equipment LAN and DHCP | Local equipment, not public egress or a general database-admin network |
| `ao-fabrication`, `10.89.12.0/24` | `ao-fabrication-db` / `a_fab` | Internal production-data domain |
| `ao-fabrication-collect` host process | Poll approved machines; authenticated database write | Explicit machine list and least-privilege database identity |
| Host PostgreSQL `127.0.0.1:5432` | Host administration/reporting application stores | Loopback source listener |
| `ao-postgres-reporting-bridge.service` / `socat` | Purpose-limited reporting relay only | Effective binding and allowed callers SHALL be explicit; source loopback binding SHALL NOT imply relay isolation |

The reporting bridge SHALL NOT expose general PostgreSQL administration to equipment-LAN devices. An equipment-LAN binding such as `10.42.0.1:5432` SHALL be subject to explicit authorized-caller enforcement and negative reachability tests; it SHALL NOT be described as an `ao-admin` gateway binding. Reporting containers SHALL use only their approved access path, not acquire blanket workload membership. Address bindings, routes and accepted callers SHALL be verified independently of unit names/comments.


<a id="section-3-3-0-2"></a>

##### 3.3.0.2 Domoticz for non-fabrication equipment

Domoticz SHALL cover operator-approved HVAC, access/locks, alarms, lighting/scenes, cameras, weather, environmental sensing, media and other approved non-fabrication equipment. It SHALL remain separate from simulation and `a_fab` production collection. New equipment SHALL have approved coverage before connection.

| Setting | Required value / behavior |
|---|---|
| Host equipment interface | `eno1`, `10.42.0.1/24` |
| Equipment network | `10.42.0.0/24` |
| Web arguments | `-wwwbind 127.0.0.1 -nomdns` |
| Web UI | `127.0.0.1:8080` only; equipment/Wi-Fi addresses SHALL refuse UI access |
| Shared server | `RemoteSharedPort = 0`; no `*:6144` listener |
| Production data | SHALL NOT write `a_fab`; Moonraker collector owns machine-production intake |

`a_fab` SHALL contain per-machine production data, not a ledger, sales record or backup repository. Provable production events SHALL be signed fabrication manifests delivered to `ao-ledger-ingest`. The `ao-fabrication` subnet SHALL be pinned in `quadlet/networks/ao-fabrication.network` and registered in `config/platform/network-cidrs.yaml`.


<a id="section-3-3-1"></a>

#### 3.3.1 Program-to-Database Map (single consolidated table)

This is the one table of programs and the databases they use. It is the starting
point for discussing reporting and data integration; it is not a list of every
installed package or desktop settings module.

| Database software | Software/program | Database name or store | Required role and reporting boundary |
|---|---|---|---|
| **PostgreSQL 18** | Host PostgreSQL service | Host cluster `18-main`; `postgres` | Administration plus Grafana/Metabase application databases; PostgreSQL SHALL bind `localhost`. Any reporting relay SHALL meet §3.3.0.1 and SHALL NOT grant equipment-LAN administration. |
| **PostgreSQL 17** | Sales database service | Container `ao-sales-db` on `ao-sales`, database `salesdb` | Authoritative source for customers, orders, products, payments, receipts, entitlements, and audit history |
| **PostgreSQL 17** | Mastodon web/background workers | Container `mastodon-db` on `ao-sales`, database `mastodon` | Accounts, posts, media metadata, federation state, and background-job application data |
| **PostgreSQL 17** | Fabrication database service | Container `ao-fabrication-db` on `ao-fabrication`, database `a_fab`, role `fabrication_role` | Per-machine production data pulled from each individual machine (§3.3.0). Separate from `ao-sim-fabrication`, which holds none |
| **PostgreSQL 9.5** | WebODM web/worker | `ao-webodm-db`, active database `webodm_dev`; bind mount `/var/lib/postgresql/data` | Mapping projects, tasks, users and geospatial state; PostGIS 2.3.2 compatibility baseline. Persistence SHALL meet §8.4; `webodm` SHALL NOT be treated as the active database. |
| **PostgreSQL 9.5** | NodeODM | The same `ao-webodm-db` container, plus filesystem processing data | Processing-node state and coordination; large image/output artifacts remain filesystem data |
| **PostgreSQL 18** | Corda 5 node | `cordadb` (dedicated Corda PostgreSQL database in the host cluster, per §11.1) | Receipt, entitlement, and provenance state. Built on Corda 5 against `cordadb`. |
| **Redis 8** | Host Redis service | Host Redis database 0 | General low-latency cache/coordination layer; not authoritative |
| **Redis 7** | Mastodon cache/queue service | Container `mastodon-redis`, database 0 | Cache, queues, and background-job coordination; not authoritative business data |
| **Redis 7** | WebODM broker | Container `ao-webodm-broker`, database `broker` | Celery/task broker and worker coordination; not authoritative mapping data |
| **PostgreSQL 18** | Grafana | Grafana application database (dedicated) | Grafana users, dashboards, and datasource configuration. Its own application state, not business data |
| **PostgreSQL 18** | Metabase | Metabase application database (dedicated) | Metabase application schema, saved questions, dashboards, filters, and subscriptions. Not a system of record and never written to by a reporting source |
| **PostgreSQL / MySQL (read-only)** | Metabase reporting sources | Per-source read-only roles | Ad-hoc read-only reporting connections to the business databases. One read-only role per source, with no write, DDL, or owner privilege, so a report cannot modify a source |
| **Prometheus TSDB** | Prometheus | `/prometheus` persistent volume | Security evidence only. Time-series metrics, service health, resource usage, and security evidence. Acts alone and independently of Grafana and Metabase. |
| **SQLite** | MeshChatX / Reticulum MeshChatX | Per-identity database at `~/.reticulum-meshchatx/identities/<identity>/database.db` | MeshChatX messages, rooms, and local Reticulum/MeshChatX application state. |
| **INI / tile cache** | QGroundControl | User settings INI and map-tile cache | Inventory/backup SHALL cover actual settings/cache; SHALL NOT assume a business application SQLite database. |
| **SQLite** | Akonadi/KDE PIM applications | Akonadi SQLite data | Contacts, calendars, mail indexes, and local personal-information data **Not collected by Prometheus** — excluded by operator instruction: personal and mail-index material is not security telemetry |
| **SQLite** | nPerf | `~/.local/share/nPerf/{history,settings,engine}.db` | Run history and settings; two of the three are snapshotted and read by Grafana. Row counts only — settings values are never selected |
| **SQLite** | Elisa | `~/.local/share/elisa/elisaDatabase.db` | Music library; snapshotted and read by Grafana. Counts only — no titles, artists or paths |
| **SQLite** | Klipper | `~/.local/share/klipper/history3.sqlite` | Clipboard history. **Never snapshotted, metadata only, by design** — a snapshot would copy clipboard content (which can include passwords and tokens) into a world-readable file, which README §4.1 rule 5 forbids |
| **SQLite** | libaccounts-glib | `~/.config/libaccounts-glib/accounts.db` | Account identifiers. **Never snapshotted, metadata only**, same reason as Klipper |
| **SQLite** | Firefox, Brave, Chrome, and Edge | Browser profile SQLite stores | Browser history, site storage, caches, certificates, and profile data **Not collected by Prometheus** — excluded by operator instruction: browsing material is not security telemetry. |
| **Container runtime metadata** | Podman | Approved rootless runtime metadata backend | SHALL be inventoried as runtime metadata, not an application reporting database; backend type SHALL be detected rather than assumed. |
| **Filesystem/local metadata — social** | LM Studio and OpenClaw | Application files, model settings, and local state | Sales/social AI application state that is not automatically part of SQL reporting. |
| **Filesystem/local metadata — drone/field** | ArduPilot, MeshChatX/Reticulum field stores, and radio gateway logs | Application files, telemetry spools, and local state | Field operational and engineering data that is not automatically part of SQL reporting |
| **Filesystem/local metadata — sim** | Gazebo, ROS 2, ArduPilot SITL, and simulation tools | Project files, worlds, models, and result artifacts | Simulation operational and engineering data that is not automatically part of SQL reporting |


<a id="section-3-3-2"></a>

#### 3.3.2 Data Flow into Reporting and Ledger Records

Corda is not a replacement for the source PostgreSQL databases. The intended
ledger flow is:

The sale chain on the right of the following extract — customer picks to checkout,
verified payment event, salesdb record, signed receipt manifest, and Corda state —
is the same five-step chain drawn in ES.2. Payment intake is shown at the left,
through `ao-ingress-payment` and into `ao-sales`; the reporting projections
(Metabase, Grafana) and the Corda entry are shown in their columns.

![Zoom of the five-step sale chain column of the ES.2 master topology, at readable scale.][figure-06]

*Zoom of the ES.2 master topology, cropped to the five-step sale chain and enlarged so
every label is readable.*

**Where the blockchain entry is recorded.** The entry itself is created by
Corda 5 in `cordadb` (§3.3, §11.1). The approved projection of that state is
recorded in the corresponding PostgreSQL database, keyed by the same
transaction/receipt reference, and the PDF receipts and reports that describe it
are written to the transaction folder under
`/ALWAYSON/data/sales/transactions/<transaction-id>/`.

Use stable correlation fields in the source-to-ledger integration, including a
transaction/order reference, serial number where applicable, UTC timestamp,
event type, status, and content hash. Do not copy payment credentials, private
keys, or unrestricted customer datasets into Corda. Corda remains authoritative
for approved ledger/provenance state, while PostgreSQL remains authoritative
for domain-operational source data.

Before building sales reporting, initialize and verify the `salesdb` schema and
confirm that the reporting identity can read it and produce the standard PDF
reports and receipts listed in §15.1. Before enabling blockchain-related
flows, complete the Corda key/certificate ceremony and implement the
ledger-ingest manifest, correlation-ID, signature, idempotency, and audit
requirements.

---


<a id="section-4"></a>

## 4. Security, Isolation, and Data Policy


<a id="section-4-1"></a>

### 4.1 Non-Negotiable Rules

1. Inspect before changing.
2. Preserve existing data.
3. Never format, repartition, delete, prune, or overwrite without explicit
   operator approval.
4. Never install Docker daemon, Docker Compose, Watchtower, or Kubernetes.
5. Use Podman and Quadlet only.
6. Never expose a public port without explicit operator approval.
7. Never place secrets in scripts, logs, HTML, Git, pCloud Public Folder, IPFS,
   Corda payloads, shell history, or documentation examples. Only use KDE Wallet
   for passwords, tokens, keys, and other secret material.
8. Never use `--privileged` as a default.
9. Use pinned image digests for operational services (§5.2.1).
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
14. Require explicit human approval before initiating payments.
15. Require explicit human approval before publishing external communications,
    changing production credentials, deleting data, or modifying external
    records.


<a id="section-4-2"></a>

### 4.2 Data Classification

| Classification | Examples | Handling requirement |
|---|---|---|
| **Public** | Anything in the pCloud Public Folder, or linked in from it: storefront HTML, intentionally published documentation, approved product data | SHALL be placed in pCloud Public Folder |
| **Internal operational** | The databases — PostgreSQL and SQL — plus non-sensitive configuration, health data, non-sensitive manifests, unit status | Restricted local access; do not publish by default |
| **Sensitive** | Corda blockchain secured data and the accounting ledger, plus customer contact data, payment references, precise telemetry, sensitive imagery, proprietary technical designs | Domain-restricted storage; encrypted backup; no public IPFS |
| **Secret** | Passwords, held in KDE Wallet | KDE Wallet only; delivered to services after Plasma login by design (§14.1.1) |


<a id="section-4-3"></a>

### 4.3 Prohibited Paths

The following source-to-target prohibitions SHALL apply independently of network membership. Required manifest/status exchanges SHALL use §4.4 rather than direct control or database access.


<a id="section-4-3-1"></a>

#### 4.3.1 Named source-to-target prohibitions

```text
Sales/AI -> MAVLink, ArduPilot, ROS/Gazebo control, LoRa, RNS, MeshChatX
Sales/AI -> WebODM workers, raw imagery, Corda core
Payment -> OpenClaw, LM Studio, Mastodon, field, mapping, simulation
Field -> payment provider, Mastodon, OpenClaw, LM Studio, Corda core
Mapping -> flight control, LoRa/RNS, payment provider, Mastodon, Corda core
Vehicle simulation -> live drones, live radios, sales/payment control, Corda core
Fabrication simulation -> live machines/arms/carousels, sales/payment control, Corda core
Public internet -> PostgreSQL, Redis, WebODM workers, LM Studio, Corda core,
                   ROS, MAVLink, Gazebo control, QGroundControl, RNS, MeshChatX
```

`ao-html-window` SHALL publish only the approved simulation-view output, not relax the public-to-control prohibitions. Mapping SHALL permit administrator-only processing and approved output publication/sale (§8). Radio mission transport SHALL follow §9 rather than assuming IP/mTLS on raw RF.


<a id="section-4-3-2"></a>

#### 4.3.2 Prohibitions by rule

| Prohibited behavior | Required enforcement | Enforcing reference |
|---|---|---|
| Simulation commands live machinery | No simulation-to-live control route; production peers separate | §4.3.1; §10.2; §4.1 rule 12 |
| Unapproved internet access | Explicit destination/protocol policy; federation/reporting/update exceptions scoped in §5 | §4.1 rules 6, 13; §5.1–§5.2 |
| Unrelated cross-domain access | Least-privilege peer/interface rules; multiple attachments only where their function is bounded | §4.1 rule 13; §5.1; §6.A.3 |
| Anonymous cross-domain IP request | mTLS and dedicated identity; signed provenance, replay defense, idempotency and audit | §4.4; §11.2.5 |
| Secret leakage | Wallet authority; approved runtime delivery only; no public/source-controlled secret values | §4.1 rule 7; §4.2; §14.1 |
| Sensitive plaintext to public IPFS/Public Folder | Classification, encryption and recipient authorization | §4.1 rule 7; §4.2; §11.6 |
| Public page to internal management/control | Separate public presentation/checkout interfaces; no private addresses or control APIs | §4.1 rule 6; §7.1; §10.2.2 |
| Reporting writes into sources | Read-only source identities with denied-write tests | §3.3; §6.A.3; §17.2.4 |
| Privilege widening to bypass error | Stop/report rather than widening access | §4.1 rules 8, 13; §6.A.3 |
| Adapter becomes a general router | Narrow application contract, credentials and allowed traffic; no blanket forwarding | §4.1 rule 13; §5.1–§5.2 |



<a id="section-4-3-3"></a>

#### 4.3.3 Prohibited-path provenance

The source records recovery of the named-pair list from the archived v6 document and an unresolved operator-confirmation item under NET-04. That provenance SHALL remain available in [the companion](README-COMPANION.md#prohibited-path-provenance). Formatting or restructuring this specification SHALL NOT be treated as re-approval of recovered historical text. The explicit functional restrictions above SHALL be read with the operator's clarified public-view/private-control and secure-network boundaries.


<a id="section-4-4"></a>

### 4.4 Approved Internal Paths

```text
PDF INTAKE
Website KIT REQUEST / order-request email ─► Public PDF intake form
  ─► standardized PDF request ─► kit-request-intake/ inbox
  ─► extracted text + manifests ─► operator review ─► transaction bundle
Sales receipt PDF ────────────────────────► Ledger-ingestion gateway
Verified payment event ───────────────────► Sales API and/or ledger-ingestion gateway
Field telemetry manifest ─────────────────► Ledger-ingestion gateway
Mapping deliverable manifest ─────────────► Ledger-ingestion gateway
Vehicle simulation manifest ──────────────► Ledger-ingestion gateway
Fabrication simulation manifest ──────────► Ledger-ingestion gateway

PDF OUTPUT
Signed receipt / contract PDF ────────────► Transaction folder + operator archive
Standard sales report PDF ─────────────────► ao-admin reporting output
Standard accounting/ledger report PDF ─────► ao-admin reporting output
Mapping deliverable report PDF ────────────► Deliverables folder + customer transfer
Field telemetry report PDF ───────────────► Field reporting output
Simulation result report PDF ──────────────► Simulation results directory

Purchase-request / receipt / work-order status PDF ────────────────────────────────► Customer, by email
Real-machine production data ─────────────────────────────────────────────► ao-fabrication (pulled into a_fab)
Fabrication manifest ──────────────────────────────────────────────────► Ledger-ingestion gateway
Sales authorisation ────────────────────────────────────────────────────► ao-egress-archive (sale transfer)

Ledger receipt or entitlement status ─────► Authorized service through narrow API
Signed mission release ───────────────────► Field mission-release service
Validated image set ──────────────────────► WebODM intake service
```

All IP-based cross-domain service requests SHALL require:

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
controls and SHALL be used together for provenance-bearing artifacts.

---


The dedicated raw-Reticulum drone link in §9.2.2 SHALL use its authenticated encrypted RF/mission-authorization contract rather than an invented IP/mTLS link. This transport distinction SHALL NOT waive signature, replay, authorization or audit requirements where applicable.


<a id="section-5"></a>

## 5. Network Domains and Controlled External Access


<a id="section-5-1"></a>

### 5.1 Combined Domain, Adapter, Component, and GUI Matrix

The tables below SHALL define owning domains, inputs, outputs, persistent stores and exposure. Each row SHALL be interpreted with these access rules:

- Network design SHALL minimize complexity while maintaining clear trust and control boundaries.
- A component MAY have more than one required network attachment. Every attachment SHALL have a declared purpose and permitted peers/ports/direction; no attachment SHALL imply unrelated access or general routing.
- Host desktop applications/provider dashboards SHALL have no Podman membership merely because they serve a workflow.
- `ao-admin` SHALL remain a limited administration/reporting plane; `ao-data` SHALL remain purpose-limited plumbing.
- Internet access SHALL use the stated federation/reporting/adaptor exceptions, with explicit destinations, TLS, credentials and audit. Egress-capable membership alone SHALL NOT authorize arbitrary outbound traffic.
- Prometheus SHALL retain an independently enforced security boundary even where administration infrastructure is shared.


#### A · WORKLOAD DOMAINS — every row is an `Internal=true` Podman network except `ao-sales` ; CIDRs in `/ALWAYSON/config/platform/network-cidrs.yaml`

| Item | Owning domain / network | Required purpose / inputs | Required outputs | Persistent data | Exposure / access |
|---|---|---|---|---|---|
| `ao-sales` | `ao-sales` | Coordinates social media, email, and Mastodon; the AI bot and chat (OpenClaw/LM Studio); and the order-request and receipt workflows, including the public PDF intake forms and PDF output. The only domain that touches customers directly. | Signed order, receipt, and entitlement manifests; standardized PDF intake and PDF output; published federation and chat posts | Sales PostgreSQL | The public PDF intake forms are the exposure point; Mastodon/chat arrive via the Cloudflare Tunnel to loopback origins |
| `ao-payment` | `ao-payment` | Provider webhook verifier and payment adapter | Verified normalized payment state | Minimal event and audit record | No direct public exposure |
| `ao-field` | `ao-field` | Heltec gateway, RNS/MeshChatX, telemetry spool, mission-release service | Signed telemetry and mission manifests | Raw packet store and telemetry spool | No direct public exposure; USB serial and radio only |
| `ao-mapping` | `ao-mapping` | WebODM, NodeODM, Redis, mapping DB, imagery intake/exporter | Signed mapping deliverable manifests | Dedicated photogrammetry volume | Administrator-only processing and control; authenticated drone/operator intake; approved final outputs may be published or sold |
| `ao-sim-vehicle` | `ao-sim-vehicle` | ROS 2, Gazebo, ArduPilot SITL, MAVLink, QGroundControl simulation | Signed vehicle-simulation manifests | Vehicle simulation data path | No direct public exposure |
| `ao-sim-fabrication` | `ao-sim-fabrication` | ROS 2, Gazebo; rehearses the industrial engineering and production flow and rehearses the kitchen. Holds no production data and never commands live machinery — real machines belong to `ao-fabrication` (§3.3.0) | Signed fabrication-simulation manifests | Fabrication simulation data path | No direct public exposure |
| `ao-fabrication` | `ao-fabrication` ( `10.89.12.0/24` ) | Real (non-simulated) fabrication. Pulls per-machine production data from each individual 3D printer and CNC machine — each running its own MainsailOS / Moonraker / Klipper on its own BigTreeTech CB1 / Raspberry Pi — into its own database ( `a_fab` , §3.3.0) for industrial engineering and fabrication optimisation work. Local switch connects the equipment; the desktop manages all DHCP. Does not command machines through the simulator. | Signed fabrication manifest toward `ao-ledger-ingest` ; fabrication optimisation reports | Per-machine production data in `a_fab` | No direct public exposure. Real machines are reached only over the local equipment switch; they are peers, not children of `ao-sim-fabrication` . |
| `ao-ledger-ingest` | `ao-ledger-ingest` | mTLS validation gateway, authorization, audit, idempotency | Corda receipt IDs and status | Audit and idempotency state | No direct public exposure |
| `ao-ledger-core` | `ao-ledger-core` | Corda node, Corda database, certificate/keystore material | No direct output | Corda state and PKI | No direct public exposure |
| `ao-data` | `ao-data` | Narrow controlled data plumbing where unavoidable | Controlled references only | Host services, loopback-only | No direct public exposure |
| `ao-admin` | `ao-admin` | Prometheus security monitoring, Grafana dashboards, Metabase reporting, backup, restore validation, administration | Metabase reports and the Grafana dashboard only | Prometheus TSDB; Grafana application database; Metabase application database | No public exposure; approved local operator access only |

#### B · CONTROLLED INGRESS AND EGRESS ADAPTERS — architecture-controlled exceptions, not general-purpose Internet access

| Item | Owning domain / network | Required purpose / inputs | Required outputs | Persistent data | Exposure / access |
|---|---|---|---|---|---|
| `ao-ingress-payment` | `ao-payment` | Payment verification for Zelle, PayPal, and Coinbase. Receives the provider webhook or approved relay event, verifies the signature, normalizes it, and emits the verified payment event. Also carries the website path: email > PDF > Corda processing. | Verified normalized payment event | Minimal event and audit record | Inbound only. Minimal listener, provider-signature verification, audit log, normalized event output. Rate limiting is required and SHALL be in place before any tunnel or relay route is enabled (see §5.2.2) |
| `ao-egress-archive` | `ao-sales` (sale-transfer duty) | ARCHIVED FOR DATA TRANSFER AND SALE — this is not a backup. Holds a sold package so it can be transferred to the authorised recipient. IPFS provides file-transfer verification and, where applicable, a blockchain sales listing; encrypted pCloud replication is the second copy. Requires `ao-sales` authorisation first — it is not reached directly from the internet. "Data sales": maps and telemetry/IoT products, not application databases. No restore, no recovery, no retention duty: restic (§17.1) is the backup .  | Approved encrypted transfer bundle; post-sale IPFS transfer; encrypted pCloud transfer copy | Staging and transfer log; no backup set, no retention record | Outbound only, and only after `ao-sales` authorisation. Destination allowlist, TLS validation, encrypted payloads, separate credentials, transfer audit |
| `ao-build-update` | `ao-build-update` (10.89.13.0/24, `Internal=false` ) | Software updates only — all host software. Image and package acquisition from the upstream software source (package and container registries) before controlled promotion. It does not touch WebODM or imagery : all photo processing and verification belongs to `ao-mapping` .  (§5.2.1) | Verified image and package set | Update audit log | Outbound only, on its own dedicated egress network. Verified source, digest capture, update audit, no direct workload attachment, and no promotion authority |

#### C · COMPONENT BOUNDARY MATRIX — what each component may accept, emit, store, and reach

| Item | Owning domain / network | Required purpose / inputs | Required outputs | Persistent data | Exposure / access |
|---|---|---|---|---|---|
| Sales API | `ao-sales` | Verified payment state and approved support requests | Signed receipt/entitlement manifests | Sales PostgreSQL | None directly |
| Payment verifier | `ao-payment` | Provider webhook or approved relay event | Verified normalized payment event | Minimal event and audit record | Through `ao-ingress-payment` only |
| Mapping intake | `ao-mapping` | Authenticated imagery upload | Validated image-set reference | Intake, validation, quarantine record | None directly |
| WebODM/NodeODM | `ao-mapping` | Validated mapping task input | Processing output to mapping exporter | Dedicated photogrammetry volume | None directly |
| Field gateway | `ao-field` | USB serial LoRa frames | Normalized telemetry manifest | Raw packet store and telemetry spool | USB serial and radio only |
| Vehicle simulator | `ao-sim-vehicle` | Approved scenario/model artifact | Signed simulation manifest | Vehicle simulation data path | None directly |
| Fabrication simulator | `ao-sim-fabrication` | Approved facility/task model | Signed simulation manifest | Fabrication simulation data path | None directly |
| Real fabrication collector | `ao-fabrication` | Per-machine production data polled from each machine's own MainsailOS / Moonraker / Klipper | Signed fabrication manifest; fabrication optimisation reports | Per-machine production data in `a_fab` | None directly. Reaches machines only over the local equipment switch, never as a simulator. |
| Ledger ingestion | `ao-ledger-ingest` | Signed mTLS manifests | Receipt/status response | Audit and idempotency state | Only to ledger core |
| Ledger core | `ao-ledger-core` | Ledger-ingestion gateway requests only | No direct public output | Corda state and PKI | None directly |
| Archive adapter | `ao-egress-archive` | Approved encrypted archive bundle | Replication result/status | Staging and transfer log | Outbound only |
| Community publication | `ao-sales` | Approved publication or support request | Remote delivery/status response | Publication audit log | Outbound only, via Sidekiq on `ao-sales` (HTTPS/443) |

#### D · GUI AND WORKFLOW ACCESS MAP — explicit purpose-limited access; host tools do not imply network membership

| Item | Owning domain / network | Required purpose / inputs | Required outputs | Persistent data | Exposure / access |
|---|---|---|---|---|---|
| 1 · Mastodon web / Konqueror client | `ao-sales` | Approved `localhost` Mastodon web/streaming origin; loopback-only publication when enabled. | — | — | Loopback origin only |
| 2 · WebODM browser UI | `ao-mapping` | `ao-webodm-web` sets `PublishPort=127.0.0.1:8000:8000` , so podman reports `127.0.0.1:8000->8000/tcp` and the UI opens at `http://127.0.0.1:8000/` with no SSH tunnel. It is loopback-only: LAN addresses refuse, and `ao-mapping` stays `Internal=true` . | — | — | None; internal to `ao-mapping` only |
| 3 · QGroundControl simulation client | `ao-sim-vehicle` | Approved local SITL/MAVLink-router endpoint; `ROS_DOMAIN_ID=21` ; `GZ_PARTITION=alwayson_vehicle_sim` . | — | — | None |
| 4 · Gazebo visualization — vehicle | `ao-sim-vehicle` | Approved vehicle ROS/Gazebo visualization path; separate DDS/interface policy remains required. | — | — | None |
| 5 · Gazebo visualization — fabrication | `ao-sim-fabrication` | Approved fabrication ROS/Gazebo visualization path; `ROS_DOMAIN_ID=22` ; `GZ_PARTITION=alwayson_fabrication_sim` . | — | — | None |
| 6 · LM Studio / OpenClaw support chat | `ao-sales` (host-local LM Studio) / `ao-sales` (containerized OpenClaw) | Host desktop use; approved loopback inference endpoint or narrow authenticated bridge only. | — | — | None |
| 7 · Grafana dashboards and metrics | `ao-admin` | No public exposure; approved local operator access only. Grafana presents the dashboards and metrics. | — | — | None |
| 8 · Metabase reporting GUI | `ao-admin` | No public exposure; approved local operator access only. Metabase produces the reports by reading the existing PostgreSQL and MySQL databases over per-source read-only roles, and keeps its own PostgreSQL application database for its saved questions and dashboards. | — | — | None |
| 9 · Sales, receipt, fulfillment, entitlement, return, and approved support reporting | `ao-admin` | Metabase is for reports, reads the existing PostgreSQL and MySQL databases over per-source read-only roles, and keeps its own application database. PostgreSQL inspection uses pgAdmin over an explicit purpose-limited loopback or approved tunneled connection. | — | — | None |
| 10 · Ledger provenance, receipt, entitlement, approval, release, and ingestion reporting | `ao-admin` | No VPN. Grafana presents the dashboards and metrics from its own application database plus the approved datasources; Metabase produces the reports by ad-hoc read-only queries against the existing databases. | — | — | None |
| 11 · Backup/restore status display | `ao-admin` | Shown on the Grafana dashboard; no VPN, no public exposure. | — | — | None |
| 12 · Field gateway / link-quality display | `ao-field` | Approved USB serial/local diagnostic display or protected Grafana dashboard. | — | — | None |
| 13 · Ledger/Corda console and maintenance | `ao-ledger-ingest` | Narrow approved operator-management path after key/certificate ceremony; no public access. | — | — | None |
| 14 · PostgreSQL reporting, schema inspection, and controlled administration | host loopback | Explicit loopback or approved narrow tunnel/bridge using a dedicated least-privilege database identity. | — | — | None |
| 15 · Redis diagnostic client | `ao-data` (optional) | Explicit loopback or approved narrow diagnostic path using a scoped Redis ACL identity. | — | — | None |
| 16 · Payment-provider dashboard | provider-hosted | Provider-authenticated browser workflow. | — | — | Provider-hosted only |
| 17 · No GUI — controlled data services | `ao-data` (narrow only) | Host services remain loopback-only; administration/reporting uses dedicated host or `ao-admin` identities and paths. | — | — | None |
| 18 · No GUI — payment verifier | `ao-payment` | Provider-hosted checkout and provider dashboard; local verifier has no GUI. | — | — | None |


#### Public simulation presentation adapter

| Item | Owning presentation domain | Inputs | Outputs | Persistence | Exposure |
|---|---|---|---|---|---|
| `ao-html-window` | `ao-html-window`, `10.89.14.0/24` | Approved read-only Foxglove/Gazebo model/camera outputs | Public kitchen, storage/CNC and vehicle presentation | Presentation configuration and non-secret delivery audit | Approved public viewing origin only; no command, topic publication, service invocation or administration |


<a id="section-5-1-1"></a>

#### 5.1.1 Domain Networks

`config/platform/network-cidrs.yaml` SHALL be the hand-maintained authority. Validation SHALL assert every registered network's CIDR/flag and reject every unregistered runtime `ao-*` network. The validator SHALL NOT overwrite the registry from a hardcoded runtime list.

The following detailed allocations SHALL be retained until explicitly revised. They are not a requirement to keep an arbitrary number of networks: consolidation SHALL be driven by approved security boundaries, with coordinated registry/service/diagram changes and rollback. Counts SHALL be derived from the approved registry.

| Network | Subnet allocation | Internal | Required purpose |
|---|---|---|---|
| `ao-sales` | 10.89.0.0/24 | **false** | Mastodon stack, `ao-sales-db`, orders and AI chat |
| `ao-payment` | 10.89.1.0/24 | true | Provider webhook verifier, payment adapter |
| `ao-field` | 10.89.2.0/24 | true | Heltec gateway, RNS/MeshChatX, telemetry spool, mission-release |
| `ao-mapping` | 10.89.3.0/24 | true | WebODM, NodeODM, Redis, mapping DB, imagery intake/exporter |
| `ao-sim-vehicle` | 10.89.4.0/24 | true | ROS 2, Gazebo, ArduPilot SITL, MAVLink, QGC |
| `ao-sim-fabrication` | 10.89.5.0/24 | true | ROS 2, Gazebo; rehearses the engineering/production flow |
| `ao-ledger-ingest` | 10.89.6.0/24 | true | mTLS validation gateway, authorization, audit, idempotency |
| `ao-ledger-core` | 10.89.7.0/24 | true | Corda node, Corda database, certificate/keystore |
| `ao-data` | 10.89.8.0/24 | true | Narrow controlled data plumbing **where unavoidable** |
| `ao-admin` | 10.89.9.0/24 | true | Prometheus, node_exporter, Grafana, Metabase, backup/restore |
| `ao-reporting-egress` | 10.89.10.0/24 | **false** | Egress for reporting sources only |
| `ao-fabrication` | 10.89.12.0/24 | true | Real (non-simulated) fabrication; per-machine production data |
| `ao-build-update` | 10.89.13.0/24 | **false** | Controlled software-update acquisition (§5.2.1) |
| `ao-html-window` | 10.89.14.0/24 | true | Read-only presentation segment for the public Foxglove/Gazebo view; public edge/relay SHALL expose only approved output, not backend control |

`10.89.11.0/24` SHALL remain unallocated/reserved unless explicitly reassigned; federation SHALL use `ao-sales`, not a separate `ao-egress-community` network.

`ao-grafana` and `ao-metabase` MAY use `ao-admin` plus scoped `ao-reporting-egress` access for approved sources. `ao-sim-fabrication-foxglove` SHALL have the simulation/presentation connectivity needed for the declared bridge, including `ao-sim-fabrication` and `ao-html-window` in the source layout. Such attachments SHALL NOT authorize arbitrary forwarding. Two attached bridges SHALL NOT be assumed routed merely because one application joins both.

The internal flag on `ao-html-window` constrains its backend segment; the required public view SHALL be delivered by the controlled presentation edge, not by declaring an unrestricted simulation/backend listener public. Public origins SHALL NOT expose private loopback addresses to visitors.

Validation interface:

```bash
scripts/validation/check-network-isolation.sh --emit-table
```

Emitted CIDRs/flags SHALL be derived from the registry; observed attachment counts SHALL remain operational evidence outside this specification.


<a id="section-5-1-2"></a>

#### 5.1.2 Local Browser Addresses

The following addresses SHALL define the local operator/application interfaces. They SHALL bind loopback, except that Prometheus SHALL retain its stricter isolated access policy. Controlled public publication SHALL use distinct approved origins and SHALL NOT expose these addresses as customer URLs.

| Software / GUI | Address | Notes |
|---|---|---|
| ALWAYS ON operator console | `http://127.0.0.1:8099/` | Operator console service; loopback only |
| ALWAYS ON sim console (Foxglove + ROS 2) | `http://127.0.0.1:8099/sim` | Operator console simulation page; public presentation uses ao-html-window separately |
| Podman / systemd status view | `http://127.0.0.1:8099/podman` | Same process |
| Gazebo factory.world portal | `http://127.0.0.1:8765/` | View-only HTML portal: boning, RL-object and world state |
| Gazebo 3D viewer | `http://127.0.0.1:8765/viewer` | Served by the same portal process; selects any of the eight read-only camera feeds and resizes the 3D view. It connects to the bridge on `ws://127.0.0.1:8081` |
| Mastodon local UI | `https://127.0.0.1:3300/` | **Self-signed cert — accept once.** Terminates TLS because upstream hardcodes `config.force_ssl = true`; `http://127.0.0.1:3000/` 301s to a TLS port that does not exist and hangs the browser |
| Mastodon web origin (transport) | `http://127.0.0.1:3000/` | Transport origin; browser operator entry SHALL use the local TLS proxy |
| WebODM | `http://127.0.0.1:8000/` | Administrator login; loopback-published |
| Grafana | `http://127.0.0.1:3001/` | Authenticated operator login |
| Metabase | `http://127.0.0.1:3002/` | |
| Prometheus | Internal service port `9090` | No general host/browser/public query access; authorized operator inspection only (§17.2) |
| OpenClaw control | `http://127.0.0.1:18789/` | |
| MeshChatX | `https://127.0.0.1:18000/` | **Self-signed cert.** Reticulum; not a public ingress |
| Domoticz | `http://127.0.0.1:8080/` | Host service, not an `ao-*` container |
| CUPS (printers) | `http://127.0.0.1:631/` | Host service |
| LM Studio | `http://127.0.0.1:1234/` | Bearer-token API only — no browsable UI, so not bookmarked |
| Mastodon streaming / OpenClaw chat relay | `http://127.0.0.1:4000/`, `http://127.0.0.1:18790/` | APIs, not UIs; a bare `/` returns `400`/`404` by design |


<a id="section-5-2"></a>

### 5.2 Controlled Ingress and Egress Adapters

**Combined into the single matrix in §5.1, group B.** The three controlled adapters
(`ao-ingress-payment`, `ao-egress-archive`, `ao-build-update`) are rows in that table along
with their purpose, direction, and mandatory controls.

Each adapter is specified in its own subsection. All three are required, and each SHALL
satisfy its mandatory controls before it carries any traffic:

| Adapter | Specification |
|---|---|
| `ao-ingress-payment` | §5.2.2 — signature verification, audit log, rate limiting in place before any tunnel or relay route is enabled |
| `ao-build-update` | §5.2.1 — allowlist enforced in code, disabled until the operator authorises a run |
| `ao-egress-archive` | §11.6 — SHALL exist as a Quadlet, container, and network before any credential is provisioned |


<a id="section-5-2-1"></a>

#### 5.2.1 `ao-build-update` — Controlled Software-Update Acquisition

`ao-build-update` SHALL be a controlled software-acquisition stage, not an installer, build service or promotion authority.

| Property | Required definition |
|---|---|
| Network | `ao-build-update`, `10.89.13.0/24`, `Internal=false` |
| Runtime | Oneshot; no published port/listener; no automatic activation without approval |
| Definition | `quadlet/build-update/ao-build-update.network`; `quadlet/build-update/ao-build-update.container` |
| Source policy | `config/build-update/registry-allowlist.yaml`, read-only mount |
| Acquisition script | `scripts/build-update/ao-build-update.py` |
| Identity authority | `/ALWAYSON/config/platform/version-matrix.yaml`, captured by `scripts/validation/capture-version-matrix.sh` |
| Allowed outbound | Approved registry/package metadata sources over HTTPS/443; validated TLS |
| Outputs | Candidate image/package metadata, full digests, append-only acquisition audit and staging report |
| Prohibited authority | Package installation, `apt`/`dpkg`/unattended upgrades, Quadlet edits, restart, redeploy and promotion |

The adapter SHALL reject a denied host, an unpinned reference or an invalid digest with nonzero exit status. A code allowlist SHALL NOT be represented as network enforcement: segment-level policy SHALL constrain actual outbound destinations, and unapproved containers SHALL NOT attach. TLS verification SHALL NOT be disabled to reach a failing source; explicit source-deny policy SHALL be honored.

Builds SHALL belong to the consuming domain. `GAZEBO/containers/` Containerfiles SHALL remain simulation-owned; local image rebuilds SHALL require validated digest capture and approved repinning before deployment.

`drift-report.py` SHALL write `docs/drift.md` without pulling, installing or restarting. It SHALL distinguish DRIFT from intentional BEHIND-LATEST. `recommend.py` SHALL produce ranked advisory recommendations without applying them.

Promotion SHALL use `scripts/build-update/promote-image-digest.sh`, edit exactly one approved `Image=` line, and reject unqualified, unpinned and cross-registry substitutions. `docs/runbooks/software-update.md` SHALL describe inventory, acquisition, review, promotion, deployment, verification and rollback. A oneshot acquisition run SHALL NOT grant permanent automation authority.

##### Package-manager and acquisition traceability

The inventory/drift scope SHALL include apt, snap and flatpak as described by the supplied update tooling; package-manager visibility SHALL NOT grant installation authority to the acquisition adapter. Digest capture, read-only `registry-allowlist.yaml`, controlled promotion through `promote-image-digest.sh` and `docs/runbooks/software-update.md` SHALL remain the concrete acquisition-to-promotion contract. Adapter enablement/segment enforcement remains owned by NET-01; a code allowlist SHALL NOT be reported as completed network enforcement.


<a id="section-5-2-2"></a>

#### 5.2.2 `ao-ingress-payment` — controlled payment ingress

`ao-ingress-payment` SHALL be the controlled payment event interface on `ao-payment`; providers SHALL be PayPal, Zelle and Coinbase/USDC (§7.2). The adapter SHALL preserve the internal payment boundary and SHALL NOT expose a general sales/database interface.

| Control | Required behavior |
|---|---|
| Provider verification | Provider-specific documented signature validation before recording an accepted normalized event |
| Zelle | Manual reconciliation; unsolicited webhook POST SHALL be refused, not treated as verified payment |
| Input size | Maximum 256 KiB |
| Rate control | Enforced request-rate policy and rejection behavior before any public tunnel/relay enablement |
| Replay | Bounded timestamp window plus durable replay/idempotency controls |
| Persistence | Approved normalized fields, SHA-256 and opaque reference; no raw persisted provider payload |
| Credentials | Wallet-delivered after login; absent/failed refresh SHALL block startup |
| Audit | Accepted/rejected decision, reason and non-secret correlation reference |

Loopback-only origin binding SHALL NOT substitute for rate limiting when a tunnel is enabled. The relay/tunnel and adapter SHALL use one explicit matching origin-port contract; discrepant historical `8899`/`8900` references SHALL NOT be silently used interchangeably. No new payment activation is authorized by this specification.


<a id="section-5-2-3"></a>

#### 5.2.3 The three `Internal=false` networks are a prohibition boundary, and §4.3 states which rule governs them

The explicitly non-internal baseline networks SHALL be `ao-sales` for federation, `ao-reporting-egress` for scoped reporting sources, and `ao-build-update` for approved acquisition. Any revision SHALL update the registry and traffic policy together. None SHALL authorize unrestricted workload egress. These functional exceptions SHALL coexist with §4.3 prohibited paths and §5.1 attachment rules; a fixed total SHALL NOT replace reachability validation.


<a id="section-5-3"></a>

### 5.3 Approved Local Data Paths

The following local paths are normal integration paths and do not require a
new architecture decision:

- Application containers to their approved PostgreSQL database endpoint.
- Metabase to its own application database on PostgreSQL, and from there to the PostgreSQL
  and MySQL reporting sources over per-source read-only roles, where Metabase is for
  reports. The read-only role is what enforces that a report cannot modify a source.
- Grafana to the existing PostgreSQL databases, where Grafana is
  for dashboards and metrics. Grafana does not read Prometheus; Prometheus is
  the isolated security layer (§17.2).
- Host administration and backup jobs to PostgreSQL through loopback or an
  explicitly documented local bridge.
- Application workers to their required Redis queue or broker.

These paths SHALL NOT become public listeners, SHALL use separate credentials,
and SHALL NOT grant unrelated applications access to each other's owner,
migration, backup, payment, or ledger credentials. Network isolation remains
a defense-in-depth control; PostgreSQL roles and grants are the primary
authorization boundary for database access.

---


<a id="section-6"></a>

## 6. Component Boundaries, GUI Reporting Tools, and Operator Access


<a id="section-6-1"></a>

### 6.1 Component Boundary Matrix

**Combined into the single matrix in §5.1, group C** — what each component may accept as
input, emit as output, persist and reach externally, on the same row as its owning domain and
its §19.1 status.


<a id="section-6-a"></a>

### 6.A GUI Reporting Tools and Podman Network Mapping

An **architecture requirement**: the required relationship between operator GUIs, reporting
tools, dashboards, desktop clients, external provider dashboards, workload domains, and Podman
networks. Work remaining against it is in §19.1.


<a id="section-6-a-1"></a>

#### 6.A.1 GUI ↔ Podman Network Mapping

**Combined into the single matrix in §5.1, group D** — eighteen GUI and workflow rows, each
with its one owning network, its approved access path and its §19.1 status. The attachment
rule in §5.1 governs every one of them.


<a id="section-6-a-2"></a>

#### 6.A.2 Reporting Tool Roles

Each tool has one purpose and one hard boundary. Grafana and Metabase are specified in
detail in §3.3; this table records only what is unique to each tool's role here.

| Tool | Role | Hard boundary |
|---|---|---|
| **Grafana** | Stable, curated dashboards and metrics | Never becomes a shell, container-management or control path |
| **Metabase** | Ad-hoc reporting by users | Never receives superuser, database-owner, migration, backup, payment-provider or Corda-key credentials |
| **Corda management / API / CLI** | Corda lifecycle, configuration, certificate-aware administration, controlled maintenance | Uses a documented narrow management path after the required ceremony (§11.1); not replaced by Metabase or Grafana |
| **Payment-provider dashboard** | Provider-authoritative charges, refunds, disputes, payouts, exports, reconciliation | External provider service with no Podman network attachment, and no replacement of local verified-event controls |

**Both application databases live on the host PostgreSQL 18 cluster**, not in their own
containers, and are reached differently. Grafana mounts the host's `/var/run/postgresql` and
connects over the Unix socket with `GF_DATABASE_HOST=/var/run/postgresql`. Metabase connects
over TCP to the host's `10.42.0.1` on `ao-reporting-egress`; both containers are also on
`ao-admin`. Both are loopback-and-socket scoped, which is why neither needs a public port:
Grafana on `127.0.0.1:3001` and Metabase on `127.0.0.1:3002`, loopback-bound only (`ss -ltn`).


<a id="section-6-a-3"></a>

#### 6.A.3 Conformance Requirements

Every GUI, reporting, administration and operator-access implementation SHALL have a named purpose, runtime placement, source, access path, listener policy, service owner, digest where containerized, authentication and least-privilege identity.

| Role / interface | Required permission boundary |
|---|---|
| `sales_reporting_role` on `salesdb` | `SELECT` on `v_reporting_orders`, `v_reporting_receipts`, `v_reporting_entitlements`, `v_reporting_sale_provenance`, `v_corda_entry_readiness`; no base-table read/write grant |
| Reporting role capabilities | No superuser, `CREATE`, `CREATEDB`, `CREATEROLE` or owner privileges |
| `metabase_app` | Metabase application database only; SHALL NOT be substituted for `sales_reporting_role` |
| Migration/admin identities | SHALL NOT be handed to Grafana/Metabase as convenience reporting credentials |
| `ao-admin` | Approved reporting/exporter/status/projection/API paths only; SHALL NOT join every workload |
| `ao-data` | Narrow authorized plumbing, not a general shell/database/authorization bypass |
| Machine-readable boundary map | `/ALWAYSON/config/platform/gui-boundary-matrix.yaml` |

Acceptance SHALL connect as the actual reporting role, successfully query an approved view, deny a base-table access where not granted, and deny write/DDL on demonstrably existing objects. Role-catalog declarations alone SHALL NOT establish behavior. Database admin probes SHALL use the actual configured cluster identity (`sales_migration_role` where the image uses that `POSTGRES_USER`), not assume a `postgres` role exists.

No GUI SHALL add public exposure, unrestricted host networking/Podman socket access, privileged execution, shared writable storage or unrelated credentials to simplify troubleshooting. Material gaps SHALL remain in the status tracker rather than replace these definitions.

##### Reporting-role executable verification

The exact source verification commands SHALL remain available:

```bash
podman exec ao-sales-db psql -U sales_reporting_role -d salesdb -tAc "select count(*) from orders;"
podman exec ao-sales-db psql -U sales_reporting_role -d salesdb -tAc "select count(*) from v_reporting_orders;"
podman exec ao-sales-db psql -U sales_migration_role -d salesdb -tAc \
  "select rolname,rolsuper,rolcreatedb,rolcreaterole from pg_roles where rolname like 'sales_%';"
```

| Check | Acceptance condition |
|---|---|
| Base-table `orders` access as reporting role | Denied where the approved view-only grant policy applies |
| `v_reporting_orders` access | Successful read; actual row count is data-dependent, not a fixed expected value |
| Role capability query | Reporting identity is not superuser and has no `CREATEDB`/`CREATEROLE`; privileged identities are identified separately |
| Write/DDL control | Denied on a demonstrably existing relation/object under the reporting identity |

The five approved views SHALL remain `v_reporting_orders`, `v_reporting_receipts`, `v_reporting_entitlements`, `v_reporting_sale_provenance`, `v_corda_entry_readiness`. `metabase_app` SHALL be an application-database identity, not a replacement business-source reporting role.

The source cluster uses `POSTGRES_USER=sales_migration_role`; a `psql -U postgres` failure can therefore mean the role does not exist, not that the database/container is unavailable. Inspection SHALL use the actual approved identity. Historical superuser/`CREATEDB`/`CREATEROLE` observations about the migration role SHALL NOT grant those powers to reporting tools or create a new requirement for unnecessary privilege. Exact observed results remain in the companion.


<a id="section-7"></a>

## 7. Public Storefront and Payment Policy


<a id="section-7-1"></a>

### 7.1 Storefront Boundary

The public storefront is static HTML hosted in the pCloud Public Folder. It carries no
secrets, no local ports and no internal hosts. Its permitted and forbidden content is listed in
§7.1.1.


<a id="section-7-1-1"></a>

#### 7.1.1 Frontend Website Details

Source is the [HTML-300X3](https://github.com/300x3/HTML-300X3) repository. It publishes as
a **single self-contained `index.html`** — one page, no build-time subpages. The sections
below are regions of that page; each catalog entry is a `data-item` JSON payload rendered
into a modal.

```text
www.300x3.com
└── index.html                       the entire site, self-contained
    ├── MAIN PAGE                    hero, project introduction, status highlights
    │   └── navigation to every section below
    ├── EQUIPMENT                    Camping (Walk&Car) Essentials · Adapter · Boiler
    │   │                             Pneumatic Speargun Ulu · Structural Battery
    │   │                             Appliances · Computer
    ├── BUILDINGS                    Furniture · ADU (80sf and up) · Mall · Tower
    │                                 Concrete Island
    ├── VEHICLES                     Drone (air/land/sea) · Boat (micro modular
    │                                 aircraft carrier) · Personal Vehicle
    │                                 Electric Car Wheel · Balloon
    ├── DIGITAL                      Images (Reality Capture) · Topography (3D points)
    │                                 Route Around Your County (turn-by-turn)
    │                                 Where's My ______? (telemetry)
    ├── DISCUSSION                   Forum (Mastodon) · RNS MeshChatX (+LoRa)
    ├── DOCUMENTATION                 Introductory Video · Project Plan (Working PDF)
    │                                 Server Coding · 3D Models · Heads Up Display App
    │                                 Simulations · AI Systems · Hardware · Software
    │                                 Fabrication · Raw Material
    ├── DONATE                       PayPal button; Zelle; Coinbase / stablecoin;
    │                                 other — customisation at 300X3@POSTEO.NET
    ├── KIT REQUEST                  written request form, composed to the operator
    └── CHAT                         OpenClaw assistant panel, exposes no infrastructure
```

The site entry files SHALL be:

```text
PCLOUD-PUBLIC/***CURRENT***/site/
├── index.html                       the site
└── alwayson-single-topology.html    the topology viewer (ES.2)
```

Catalog entries are modal payloads inside `index.html`, not directories. Every Equipment,
Buildings and Vehicles entry carries the sales action below. `§7.1.2` lists the additional
live views specified for the product modals required for publication.

##### Order of follow-up, support, and chat links

The order below is deliberate and is the order presented on the page:

1. Follow-up — order status and follow-up links.
2. Support — support request and help links.
3. Chat — AI-assisted support entry point (OpenClaw), which exposes no private
   infrastructure.

Mastodon/community links follow these three.

##### Sales-link integration plan

Each catalog modal under Equipment / Buildings / Vehicles gets a sales action
that stays inside the static-site boundary (no secrets, no local ports, no
internal hosts — see Section 7.1 prohibitions):

1. Modal shows product images, parts list / detailed drawings link, pCloud
   folder link, and IPFS digital-asset mark where applicable.
2. A purchase button routes to provider-hosted checkout (PayPal hosted button;
   Zelle instructions and Coinbase/USDC flow per §7.2) or to a `mailto:300X3@POSTEO.NET` order-request template
   carrying product name, options, and quantity.
3. Checkout completion returns a provider-signed event (or manual
   reconciliation record for Zelle/wire) into the Section 7.3 sales and
   receipt sequence; Corda records the receipt/entitlement state per
   Section 11.
4. No payment-card data, webhook secrets, OAuth tokens, or ledger keys ever
   appear in the static HTML, pCloud folder, or Git history.

The public site SHALL contain only:

- Product catalog and documentation.
- Hosted payment checkout links.
- Provider-controlled payment buttons.
- Order follow-up links.
- Support links.
- Chat: AI-assisted support entry points that do not expose private infrastructure.
- Mastodon/community links.
- Shipping, return, warranty, privacy, and legal content.

The public site SHALL never include:

- Payment-provider secret keys.
- Corda keys, RPC credentials, or node addresses.
- Mastodon OAuth tokens.
- pCloud archive credentials.
- IPFS private keys or swarm keys.
- Local hostnames, LAN addresses, Podman ports, or private API routes.
- Database connection strings.
- Drone radio configuration, control endpoints, or flight-control access.
- Internal service certificates, identifiers, or diagnostic output.

Referenced product PDFs, images and other approved assets SHALL be included under their declared published paths; the entry-file list SHALL NOT prohibit required supporting assets.


<a id="section-7-1-2"></a>

#### 7.1.2 Live HTML Views for Product Modals

These are the **live HTML views on the product modals** of the storefront. This table is the
requirement list for each one, not a status report.

Every view below SHALL satisfy the same boundary as the rest of §7.1: the public
site carries only public content and interactive iframe content from other
servers, and never a local hostname, LAN address, Podman port, or private API
route (§7.1 prohibitions; §1 "Static HTML & interactive iframe content from
other servers"). The Instructables view is the straightforward case — it is an
outbound link and a static image. The remaining eight are not, and that is the
substance of the constraint column.

| # | View | Placement | What it shows | Requirement and constraint |
|---|---|---|---|---|
| 1 | **Instructables — fabrication directions** | Bottom-right of **each** product modal | The robot picture, linked to the operator's Instructables member page. **Not** the "Autodesk Instructables" wordmark | No image asset may be fetched or substituted: the operator supplied an Instructables logo SVG and specified *not* to use it |
| 2 | **MeshChatX — network visualizer** | Modal window area | The Reticulum network stack visualizer, live, plus a direct-messaging entry point | MeshChatX is `https://127.0.0.1:18000/`, loopback-only and **not a public ingress** (§9.2.1), so it cannot be iframed. It SHALL be a static export, an approved published view, or an existing external public visualizer |
| 3 | **IPFS/pCloud — route orthotiff** | Maps / digital | WebODM-processed orthotiff along the 300X3 route, the full way around the county, as a **free download including route times and telemetry data** | A public download SHALL carry no internal host, port, or path; check against §4.2 before publication |
| 4 | **Trimble — San Vicente Reservoir point clouds** | Maps / digital | Point-cloud viewing of the reservoir, from a processed WebODM topography | Requires a completed WebODM task for the reservoir (§8) |
| 5 | **LocusMap** | Maps / digital | Downloadable route around San Diego County in the LocusMap format | Format and licensing of the published tile set SHALL be confirmed before any public link |
| 6 | **Mapbox** | Maps / digital | Mapping tiles, San Vicente Reservoir | Requires a Mapbox account and an access token held **outside** the repository. A public browser token is publishable by design; a secret-classified token is not (§4.2, §7.1) |
| 7 | **Mastodon — live forum** | Discussion | A live forum view inside the modal | `mastodon.social` refuses to be framed, and that refusal is enforced by the remote. The local instance UI is `https://127.0.0.1:3300/`, loopback-only, so it is not a substitute without a new approved public entry |
| 8 | **Gazebo/Foxglove — simulation** | Modal, three views | Kitchen; storage/CNC; vehicle | `ao-html-window` SHALL publish read-only kitchen, storage/CNC and vehicle views through an approved public origin. Local console `127.0.0.1:8099/sim`, portal `127.0.0.1:8765/`/`viewer` and bridge `127.0.0.1:8081` remain backend/operator interfaces, not public embed URLs. Public clients SHALL have no command/topic publication, simulation-control service or administration path (§10.2.2). |
| 9 | **Trimble SketchUp — grid of 3D views** | Modal grid | The SketchUp model views | SketchUp is a desktop/paid service; no SketchUp view SHALL be linked or embedded publicly without explicit operator confirmation before use |

**No public port is opened by this section.** Rows 2, 7 and 8 each require explicit operator
authorisation before any live view is published, and none of them may be satisfied by
publishing a loopback address. Publication state SHALL be recorded only in the status tracker.


<a id="section-7-2"></a>

### 7.2 Payment and Settlement Policy

ALWAYS ON does not process, transmit, or store payment-card numbers, CVV
values, or payment-provider secret material in the storefront, sales database,
Corda, Git repository, logs, pCloud Public Folder, or IPFS.

There are three forms of payment processing:

| # | Form | Providers | Intended use | Required control |
|---|---|---|---|---|
| 1 | **Card / PayPal** | Hosted card checkout and hosted PayPal checkout | Standard online transactions | Provider-hosted checkout, signature-verified webhook, no local card handling |
| 2 | **Wire transfer / Zelle** | Wire transfer and Zelle | Approved high-value and direct-to-bank transactions | Manual reconciliation, operator approval, auditable reference record |
| 3 | **Coinbase / stablecoin (USDC)** | Coinbase or similar | Crypto/stablecoin settlement | Documented provider terms, accounting treatment, refund process, and explicit operator approval |

PayPal, Zelle and Coinbase/USDC SHALL be the provider scope. Selection SHALL NOT constitute authorization to enable payment acceptance.

The default payment model is provider-hosted checkout; the provider is
responsible for card capture and authorization. The local payment verifier
accepts only provider-signed webhook events and stores normalized business state.

`ao-ingress-payment` exposes three webhook paths. Zelle publishes no webhook and
returns 501 on any inbound POST, so Zelle is verified by operator reconciliation
against the provider record. Coinbase is verified against the on-chain settlement
record. Bodies are capped at 256 KiB, only a SHA-256 hash and an opaque reference
are stored, and a raw payload is never persisted.

The local verifier SHALL conform to each provider’s documented signature scheme and read every provider secret it is provisioned, and `normalize()` SHALL preserve the money-bearing fields of every accepted event.


<a id="section-7-3"></a>

### 7.3 Sales and Receipt Sequence

Sequence requirements are defined below.


<a id="section-7-3-2"></a>

#### 7.3.2 Sequence

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

The full flow is drawn in the master topology graphic in ES.2. The five numbered steps of
the sale chain — catalogue to checkout, verified payment event, `salesdb` record, signed
receipt manifest, and Corda state — are steps 1 to 5 in the highlighted column below,
which is that same graphic with the chain highlighted:

![Zoom of the full “what actually happens” column of the ES.2 master topology, at readable scale: sale chain, Corda state, CAD and model registry, correlation tuple, the 500GB photogrammetry drive, mapping ingest/process/export, and storage to shelf to robot.][figure-07]

*Figure 7.3.2 — A **zoom** of the catalogue-to-ledger chain from the ES.2 master
topology, enlarged so the labels are readable. It is a zoom of that one graphic, not a
second diagram.*

Two paths feed that chain, and both are in the same graphic. The **PDF intake path** runs
from `KIT REQUEST PDF intake` into `ao-sales` ("PDF requests in"), which is the public
storefront intake. The **website path** runs from the customer email inbox through the
Cloudflare edge and tunnel into `ao-sales` as a loopback origin. From there `ao-sales`
emits a **signed receipt manifest** into `ao-ledger-ingest`, which performs mTLS,
authorization, idempotency, and audit before passing an **approved state transition** to
`ao-ledger-core`. Ledger state reaches the reporting tools by two separate approved
routes, both drawn in the graphic: `ao-ledger-core` supplies status over a narrow API,
and `salesdb` supplies **read-only views** to Metabase.

---


<a id="section-8"></a>

## 8. Mapping and Photogrammetry


<a id="section-8-1"></a>

### 8.1 Dedicated Storage

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

WebODM SHALL NOT use the root filesystem, `$HOME`, or Podman writable container
layers for high-volume processing.


<a id="section-8-2"></a>

### 8.2 Required Directory Tree

The tree below is the specification. Compliance on the live drive is tracked in
§19.1 FIELD-10.

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


<a id="section-8-3"></a>

### 8.3 Mapping Processing Flow

```text
Authenticated drone or operator upload
      │
      ▼
Telemetry data ingest to imagery-ingest service, from 3DR N1 (autopilot module)
Imagery-ingest service from Raspberry Pi camera and sensor (companion computer)
      ├── File type validation
      ├── SHA-256 checksum
      ├── EXIF and metadata validation
      ├─── Mission association (autopilot telemetry incorporated
      │   and the WebODM project name)
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


<a id="section-8-4"></a>

### 8.4 Persistent Locations

The persistent locations SHALL be explicit and SHALL NOT be changed by a documentation rewrite.

| Data | Persistent location / required treatment |
|---|---|
| Mapping PostgreSQL | `~/webodm/dbdata` (`/home/scottw/webodm/dbdata`), bind-mounted into `ao-webodm-db` at `/var/lib/postgresql/data`; active database `webodm_dev` |
| Redis persistence | Dedicated named Podman volume on `ao-webodm-broker` |
| Signed manifests | `/ALWAYSON/artifacts/mapping-manifests/` |
| Imagery, working projects and deliverables | Dedicated `/media/scottw/500GBPHOTOGRAM/` tree in §8.2 |
| Mapping database dumps | Active `webodm_dev` through the approved dump executor; explicit restore identity/path mapping |

The source also states a dedicated-volume database-placement objective. That objective SHALL remain a tracked placement conflict under FIELD-11, not an implicit approved move. Until an explicit migration target and action are approved, the documented PostgreSQL binding above SHALL be preserved. No exact destination, deletion or service restart is authorized by this specification.


<a id="section-8-4-1"></a>

#### 8.4.1 Authoritative mapping database name and location

The authoritative application database SHALL be `webodm_dev` in `ao-webodm-db`. Inventory, application connection settings, reporting and dump/restore mappings SHALL use the actual active name. `WO_DATABASE_NAME` SHALL explicitly select `webodm_dev` or resolve to that tested default. `POSTGRES_DB=webodm` SHALL NOT be used to infer that the application reads `webodm`.

| Identity / path | Required interpretation |
|---|---|
| `webodm_dev` | Active application database; backup SHALL include it |
| `webodm` | Duplicate/rollback database in the supplied record, not the authoritative application database; no deletion without approval |
| `~/webodm/dbdata` | Preserved PostgreSQL source bind until an approved migration changes it |
| `/ALWAYSON/data/mapping/postgres/`, `/ALWAYSON/data/mapping/redis/` | Not alternative approved live stores |
| Dedicated-drive placement | FIELD-11 conflict/decision; SHALL NOT be represented as an already approved migration |

Directory ownership, setgid inheritance, ACLs and the administrator's effective group memberships SHALL agree with the actual machine/service identity. Missing directory or denied write tests SHALL fail mapping admission; permissions SHALL NOT be relaxed to world-writable merely to clear a fault.

Historical top-level `scottw:ao-mapping`/`2770`, subtree `ao-mapping:alwayson-mapping`/`770`, missing-directory measurements and remediation alternatives are retained in [the companion](README-COMPANION.md#mapping-storage-evidence). They are evidence, not permanent assertions about the live drive. FIELD-10 owns the mount/tree/permission acceptance and FIELD-11 owns name/location/backup reconciliation.


<a id="section-8-5"></a>

### 8.5 Mapping Mount Validation

The drive SHALL be identified by filesystem UUID, not by `/dev/sdX`.

WebODM SHALL refuse to start when:

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


<a id="section-9"></a>

## 9. Field and LoRa Architecture


<a id="section-9-1"></a>

### 9.1 Drone-Side System

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


<a id="section-9-2"></a>

### 9.2 Desktop Gateway


<a id="section-9-2-1"></a>

#### 9.2.1 MeshChatX Local Service Port

The MeshChatX native backend/UI SHALL use `https://127.0.0.1:18000`, distinct from WebODM `127.0.0.1:8000`. Its launcher and watchdog SHALL use the same port. MeshChatX UI SHALL NOT be published through Podman, nginx, Cloudflare or a router.

| Service | Listener | Owning runtime / exposure |
|---|---|---|
| MeshChatX native backend / UI | HTTPS `127.0.0.1:18000` | `scottw` user service, loopback only |
| WebODM administrator UI | HTTP `127.0.0.1:8000` | `ao-mapping`; administrator authentication; no public processing access |
| Reticulum transport | Approved Reticulum interfaces | Not an HTTP UI; interface policy in `/home/scottw/.reticulum/config` |
| Mastodon local TLS proxy | HTTPS `127.0.0.1:3300` | `mastodon-local-proxy.service`; local operator use |

Local self-signed certificates SHALL be explicitly trusted by approved clients; trust installation and regeneration SHALL preserve the origin binding. The local Mastodon certificate path SHALL be `/ALWAYSON/secrets/mastodon/mastodon-local.crt`; applicable NSS stores SHALL include `~/.pki/nssdb` and the active snap Firefox profile's `cert9.db`. Firefox SHALL be closed for direct certificate-store edits. The proxy SHALL supply `X-Forwarded-Proto: https` and SHALL NOT change the public federation origin.

```text
Heltec WiFi LoRa 32 V3
       | USB-C serial; stable verified by-path identity
       v
Heltec gateway service
       +-- Serial framing
       +-- Link-health and RSSI/SNR metrics
       +-- Packet authentication
       +-- Duplicate and replay detection
       +-- RNS / MeshChatX adapter
       +-- Raw-packet storage
       +-- Telemetry normalization
       +-- Signed telemetry-manifest exporter
```

| Desktop radio | Hardware baseline | Band | Stable role |
|---|---|---|---|
| `PEOPLE-RADIO` | Heltec LoRa 32 V3 / SX1262; RNode firmware 1.85 baseline | 915 MHz | Human Reticulum/MeshChatX traffic |
| `DRONE-RADIO` | Heltec LoRa 32 V3 / SX1262; RNode firmware 1.85 baseline | 917 MHz | Authenticated private drone mission/status traffic |

Reticulum configuration SHALL reside under `/home/scottw/.reticulum/`; MeshChatX identity/repository/application state SHALL reside under `/home/scottw/.reticulum-meshchatx/`. Bandwidth, SF, coding rate, power, mode and airtime SHALL be controlled by the versioned profiles (§9.4). The two roles SHALL NOT be merged/interchanged without approved frequency/interface policy.

CP2102 bridges sharing descriptor `Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001` SHALL be distinguished through verified PCI/USB by-path identity and recorded radio identity. The serial descriptor alone SHALL NOT be accepted as unique. Changes to RF parameters SHALL follow characterization and authorized profile changes, not unexplained observed feedback.


<a id="section-9-2-2"></a>

#### 9.2.2 What each radio is for

The two radios are not interchangeable and are not both "chat". Each has one job:

| Radio | Purpose | Ties to | Notes |
|---|---|---|---|
| **PEOPLE-RADIO** (915 MHz / 125 kHz / SF7 / 17 dBm) | **Raw-LoRa human communication** — public human chat | **MeshChatX** | Carries MeshChatX text over raw LoRa into the local chat service. This is the human communication path over Reticulum; it is **not** LoRaWAN (§9.4.3). |
| **DRONE-RADIO** (917 MHz / 250 kHz / SF7, hidden) | **Local QGroundControl missions** to the drone, over a **dedicated RNS-enabled connection** | **QGroundControl** | Carries a dedicated RNS-enabled QGC link to the **QGC session on the Raspberry Pi 5 drone**, so **missions can be updated midflight**. Radio only: no IP path, no mTLS. |

`QGroundControl` therefore has two roles: it plans and watches missions from the desktop,
and it receives **midflight mission updates** relayed by DRONE-RADIO to its session on the
Pi5. PEOPLE-RADIO has no relationship to the drone.


<a id="section-9-3"></a>

### 9.3 Operational Security

The MeshChatX web interface is restricted to `127.0.0.1:18000`.

The Reticulum `Public Gateway` listens on `0.0.0.0:4242` and is **deliberately
LAN-reachable**: the mesh protocol is intended to be reachable by peers.

| Fact | Value |
|---|---|
| Listener | `0.0.0.0:4242` — all IPv4 interfaces, not loopback-restricted |
| Host address | `192.168.87.135/24` on `wlp3s0` |
| UFW rule | `4242/tcp ALLOW Anywhere` — an explicit allow, not a default |
| Reachability test | connecting to `192.168.87.135:4242` **succeeds** |
| Web UI | `127.0.0.1:18000` only; `192.168.87.135:18000` correctly refused |

So `:4242` is reachable from the local network by design. This is **not** a finding against
the isolation model, which governs `ao-*` workloads: Reticulum and MeshChatX are separate
host tooling. It does mean that a loopback-only web UI does not make the underlying gateway
private, and anyone auditing exposure SHALL treat `:4242` as visible on the LAN. For
contrast, PostgreSQL is explicitly `5432/tcp DENY` from any non-loopback source, and KDE
Connect `:1716` is denied too.


<a id="section-9-4"></a>

### 9.4 Radio Profile Requirements

Each radio is defined by exactly one version-controlled profile. **The profile is the
specification** — this section states how a profile is accepted, not what fields it contains.

| Profile | Radio | SX1262 MAC |
|---|---|---|
| `config/field/heltec-v3/radio-profile-us915.yaml` | `PEOPLE-RADIO` (Heltec V3) | `RECORD_FROM_HARDWARE` — read from physical radio |
| `config/drone/waveshare-lora/radio-profile-us915.yaml` | `DRONE-RADIO` (Waveshare SX1262) | `RECORD_FROM_HARDWARE` — read from physical radio |

**A profile is accepted only when all of the following hold.** These are testable conditions;
any one failing rejects the profile rather than falling back to a default.

| Condition | Test |
|---|---|
| Region and frequency plan are US915 | `region: US915`; the plan matches an approved entry in `config/platform/listener-allowlist.yaml` |
| The two radios cannot be confused on air | Different frequency, different sync word, different encryption key ID, different device identity |
| Radio parameters interoperate | Bandwidth, spreading factor, coding rate and preamble match across both profiles, or the difference is recorded in the profile as intentional |
| Transmit power is legal | At or below the US915 ceiling for the band |
| Packet fits one airtime window | `max_packet_bytes` is deliverable at the profile's bandwidth and spreading factor within `airtime_limit_pct` |
| Device identity is unique | Not derived from the USB serial descriptor, which both CP2102 bridges share (§9.2.1) |
| Retry and replay are bounded | Retry count and backoff are both set; the sequence window is stated |

Matching SX1262-family chips do not guarantee protocol compatibility, so acceptance is by these
conditions and not by chip family. Both radio ends SHALL be verified as US915 hardware variants
before use.


<a id="section-9-4-3"></a>

#### 9.4.3 LoRaWAN naming rule

The system SHALL be described as raw LoRa over Reticulum (RNode), not LoRaWAN. Profiles SHALL use the raw-LoRa frequency-plan terminology. A separate true LoRaWAN service SHALL require its own requirements and verified device/gateway/network-server architecture and SHALL remain isolated from the field telemetry mesh.


<a id="section-10"></a>

## 10. Simulation Architecture


<a id="section-10-1"></a>

### 10.1 Vehicle Simulation

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


<a id="section-10-1-1"></a>

#### 10.1.1 SITL integration method

SITL
(Software In The Loop) is the autopilot firmware built as an ordinary native C++
executable and run without any hardware; sensor data comes from the simulator.
ArduPilot connects to the simulator over MAVLink, and MAVProxy is the ground
control station.

```text
Gazebo (gz sim -v4 -r <world>.sdf)
   │  ArduPilot Gazebo system plugin
   │  (github.com/ArduPilot/ardupilot_gazebo — does NOT depend on ROS)
   ▼
ArduPilot SITL  (sim_vehicle.py -v ArduCopter -f gazebo-<model> --model JSON --map --console)
   │  MAVLink
   ▼
MAVProxy GCS  ──► QGroundControl (simulation client)
```

Required environment, per the ArduPilot documentation:

- `GZ_VERSION` SHALL be set to the installed Gazebo release.
- `GZ_SIM_SYSTEM_PLUGIN_PATH` SHALL include the built `ardupilot_gazebo`
  plugin directory.
- `GZ_SIM_RESOURCE_PATH` SHALL include the plugin's `models/` and `worlds/`
  directories.
- With ROS 2 in the loop, ArduPilot's DDS support is used: build SITL with DDS
  enabled, set `DDS_ENABLE=1`, and make ArduPilot's `DDS_DOMAIN_ID` match the
  environment's `ROS_DOMAIN_ID`. Set them together and relaunch SITL if they
  change.

The standard example invocations are:

```bash
gz sim -v4 -r iris_runway.sdf
sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --map --console
```

ArduPilot SITL can simulate multi-rotor aircraft, fixed-wing aircraft, ground
vehicles, underwater vehicles, camera gimbals, antenna trackers, and a wide
variety of optional sensors. The vehicle profiles below SHALL therefore be
selectable at run time, at rapid speed, by changing the ArduPilot
vehicle type and the Gazebo model, not by rebuilding anything.

Vehicle profiles SHALL switch between the following at rapid speed, by changing the ArduPilot vehicle type and the Gazebo model:

- Bicopter profile.
- Fixed-wing VTOL tailsitter profile.
- Rover (quadcycle) profile.
- Dual-rotating underwater/submersible profile.
- Boat mast/sail control profile.
- Boat bow/stern thruster profile.
- Boat bow/stern airboat fan profile.
- Wind, terrain, obstacles, routing, takeoff, and landing events.
- Camera, GPS, IMU, barometer, rangefinder, battery, and MAVLink behavior.
- GPS loss, packet loss, actuator faults, sensor drift, and failsafe handling.

Vehicle simulation SHALL never connect to live flight controllers, field radios,
real drone telemetry, payment services, customer records, or Corda core.


<a id="section-10-1-2"></a>

#### 10.1.2 Baseline capability: 3D world, boning, reinforcement learning objects, HTML portal

Required for both simulation domains. For `ao-sim-vehicle` these four are
baseline deliverables, not optional extras. Each SHALL be a first-class artifact
for its simulation domain, created and scripted from a single entry point rather
than assembled by hand.
the world file, its models, their poses, the lighting and environment, the ground and
surface materials, the physics and collision configuration, and the spawn points. World
setup SHALL be scripted and repeatable from a single entry point rather than assembled by
hand in the GUI, so the same world can be rebuilt identically on any host.

**Boning.** The world carries a boning and alignment structure: a defined datum frame per
model, declared mounting and reference surfaces, joint and axis definitions, and the
tolerances between them. Boning is what makes the world measurable rather than merely
pictorial — a pose is verified against the boning frame instead of being eyeballed, and
a model that has drifted out of tolerance is detectable programmatically. The boning data
SHALL be exported alongside the world so the same checks run against recorded evidence.

**Reinforcement learning objects.** The trainable entities for scenario and policy work:
marked, individually addressable objects with observable state, reward-relevant properties,
and defined reset behaviour. They SHALL be separable from the static world geometry so a
training run can vary object count and placement without rebuilding the world. The optional
Stable-Baselines3 evaluation consumes these objects; the objects are required even where no
trainer is attached yet.

**HTML portal.** The whole environment is exposed through a browser-served HTML portal:
view the live model and sensor state and read back boning and tolerance measurements. The
portal is **view-only** — it exposes no route that can start, stop, reset or otherwise
modify the simulation. World lifecycle is an operator CLI run locally. Its control/lifecycle interfaces SHALL remain private inside `ao-sim-vehicle`; the approved view-only output MAY be presented publicly through `ao-html-window` — the same isolation
rule that forbids this domain from touching live flight controllers applies to the portal
as well. It SHALL never become a path by which the simulation reaches anything outside its
own domain.


<a id="section-10-2"></a>

### 10.2 Fabrication and Facility Simulation

Gazebo Sim model views of the fabrication and facility domain. These show the modelled
robot-arm cells, vehicle and shelving layout, and kitchen/storage volumes referenced
below. They are **rendered model views, not operational evidence** — no flight-control
or live-machinery path is enabled by anything shown here.

![Simulated fabrication domain: robot arm, vehicle, and robot arm vehicle work areas][figure-08]

*Figure 10.2a — Robot-arm work area, vehicle bay, and robot-arm vehicle bay within the fabrication domain.*

![Simulated shelving and storage elevation with robot-arm cells][figure-09]

*Figure 10.2b — Storage and shelving elevation with robot-arm cells, and the shelving-to-printer aisle.*

![Simulated shelving and kitchen volume from the opposite approach][figure-10]

*Figure 10.2c — Storage, shelving-to-printer, and kitchen volumes from the reverse approach.*

```text
ao-sim-fabrication
├── ROS 2 Lyrical
├── Gazebo Sim 10.5.0
├── Industrial engineering and production coordination (REHEARSED — no production data;
│   real machines are in ao-fabrication, §3.3.0)
├── Assembly stations
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

The machines — MainsailOS, Moonraker, Klipper on the BigTreeTech CB1/RPi, and the
individual additive-manufacturing machines (3D printers and CNC machines) — are
real machines, not simulation nodes, and they are **not** part of this simulation
domain. `ao-sim-fabrication` coordinates industrial engineering and production
related details for the **rehearsal**, and it rehearses the kitchen. It **does not
receive production data from any machine**.

Production data from the real machines is handled by the separate **`ao-fabrication`**
domain, which pulls it into its own database (`a_fab`) — see §3.3.0. This
separation is deliberate: a rehearsal that held production data, or a simulation that
commanded a live machine, would breach the §4.3 prohibition on simulation-to-live paths.

```text
Storage
   │
   ▼
Carousel or conveyor
   │
   ▼
Robot-arm pickup
   │
   ├── 3D printing (individual machine)
   ├── Additive manufacturing, laser powder bed fusion
   ├── CNC machining (individual machine)
   ├── Assembly — production data from each machine
   ├── Refrigerator or pantry
   └── Kitchen or pass-through
```

Simulation SHALL remain rehearsal-only and SHALL NOT command live robot arms, 3D printers,
CNC machines, laser powder bed fusion systems, refrigeration, carousels, kitchen
equipment, or other machinery.


Vehicle and fabrication simulation domains require separate:

- Podman networks.
- ROS domain IDs.
- Gazebo partitions.
- DDS configuration.
- Service identities.
- Filesystem mounts.
- Result directories.
- Simulation **manifest-signing** certificates only. These sign exported
  artifacts; they SHALL NOT be Corda client identities, and simulation SHALL never
  open a connection to Corda core (section 10.1).
- Git repositories or clearly separated repository subtrees.
- Artifact manifests.

Use local folder storage under `/ALWAYSON/GAZEBO/`, for SDF, URDF/Xacro, world files, robot definitions, safety zones,
task plans, and launch configurations. Use Git LFS or a separate artifact
repository for large meshes, textures, point clouds, and generated results.


<a id="section-10-2-1"></a>

#### 10.2.1 Baseline capability: 3D world, boning, reinforcement learning objects, HTML portal

The same four deliverables as §10.1.2, each SHALL be a separate and first-class
artifact in the fabrication world, covering the robot-arm cells, the vehicle and
shelving layout, and the kitchen and storage volumes. What differs is what the
world contains.

**3D world setup.** The fabrication world covers the robot-arm cells, the vehicle and
shelving layout, and the kitchen and storage volumes shown in Figures 10.2a–10.2c, with
safety zones and the printer/CNC and storage footprints.

**Boning.** This is where boning carries the most weight in this domain, because the
modelled cells and machines SHALL line up with the real ones. The world carries a datum
frame per cell, declared mounting and reference surfaces for the robot arms and for the
printer and CNC beds, the shelving and aisle reference planes, and the joint and axis
definitions with their tolerances. This is what lets a simulated reach be checked against
the real machine envelope rather than assumed, and it is exported with the world so the
same check runs against recorded evidence.

**Reinforcement learning objects.** Marked parts, stock items and task targets for cell and
kitchen work. Robot arms and shuttles are the controlled actors; these objects are what they
act on and what reward is measured against.

**HTML portal.** A browser-served portal showing live robot, machine and stock state, the
boning and tolerance measurements, and the world. Private lifecycle/control access SHALL remain on the approved local path at `ROS_DOMAIN_ID=22` / `GZ_PARTITION=alwayson_fabrication_sim`, and never a control path to
the real machines (§10.2).

**3D viewer and camera set.** The world carries eight static cameras, all aimed from the
cell datums in `GAZEBO/sim/boning.yaml` so that every view is derived from boned data
rather than eyeballed, with standoff `d = (across-frame width / 2) / tan(h_fov / 2)`. The
across-frame width is the axis perpendicular to the view direction, not the extent named
in the boning datum. Four vantages look into the robot-arm cell — `arms_ne`, `arms_n`,
`arms_e`, `arms_se`, all at 1.9 m and 22° — and three are true elevations at pitch
exactly `0.0000`: `elev_arms` from the north, `elev_conveyor` from the south, and
`elev_massing` from the east, each level with its subject and face-on to one side. The
remaining `image` view is the default perspective set in both `factory.world` and the GUI
`gui.config`, so it applies whenever the world opens. Each feed is bridged gz→ROS and
served read-only.

The Foxglove bridge is a container, and the browser client that consumes it is
`GAZEBO/portal/viewer/index.html`, served by the portal at `/viewer`. It decodes the
bridge's CDR binary frames, draws the selected feed, and lets the operator resize the 3D
view. Two properties are load-bearing and worth recording. The bridge container SHALL be on
both `ao-html-window` and `ao-sim-fabrication`: a matching `GZ_PARTITION` does not route
between two internal bridges, and gz-transport discovery is link-local multicast. And the
server SHALL set `GZ_IP=0.0.0.0`; the GUI appears to work without it only because it shares
the server's network namespace.

**Files.** The baseline deliverables live under `GAZEBO/sim/` and are read by the portal:

| File | Contents |
|---|---|
| `boning.yaml` | A datum frame per cell, mounting and reference surfaces, joints and axes with tolerances, and the machine beds and storage planes |
| `objects.yaml` | Reinforcement learning objects in groups, plus actors, each with a stable id, a home pose, and reset semantics |

Every boning frame is derived from the AABB of the corresponding collision box in
`factory.world` and is labelled `source: derived-from-mesh-aabb`. A machine absent from the
source exports carries a `declared-by-operator` null, and the portal then reports
`reach_verified_against_machine: false`. **A simulated reach may not be called verified
against a real machine envelope until that machine has been surveyed.**

The portal SHALL be `scripts/simulation/ao-sim-portal.py`. Its interface contract SHALL separate:

| Route | Required audience / permission |
|---|---|
| `/viewer` | Approved read-only camera/model presentation |
| `/api/status`, `/api/boning`, `/api/objects`, `/api/health` | Private operator access; only explicitly approved non-sensitive subsets may be relayed to the public view |
| `/api/start`, `/api/stop`, `/api/reset` | Authenticated local operator lifecycle control, restricted to the single permitted simulation unit; never public |
| `/api/inspect` | Local operator inspection unless a separately minimized read-only output is explicitly published |

Public routes SHALL NOT expose command-capable WebSocket operations or inherit lifecycle authority.

**Platform.** ROS 2 Lyrical at `/opt/ros/lyrical` and Gazebo Sim 10.5.0 (collection "Jetty") on
Ubuntu 26.04. The required integration SHALL be modern `ros_gz`, not `gazebo_ros_pkgs` or Gazebo Classic 11. Simulation images are built from a pinned base-image digest rather than from an apt repository.

**Three environment traps.**

1. `GZ_RENDERING_RESOURCE_PATH` **replaces** Gazebo's packaged Ogre2 media root; it is not a
   search list, and a colon-separated value is treated as one directory name. Point it at the
   stock media root `/usr/share/gz/gz-rendering`. Project models are found through
   `GZ_SIM_RESOURCE_PATH` / `GZ_SIM_SYSTEM_PLUGIN_PATH`. Getting this wrong raises
   `OGRE EXCEPTION(6:FileNotFoundException)` and leaves the render engine uninitialised, so the
   viewport shows background colour and no geometry.
2. gz-gui's EntityTree icons require `qt6-svg-plugins`. Without it the image-format plugin
   fails to decode and the client aborts with
   `basic_string: construction from null is not valid`.
3. GPU rendering requires CDI passthrough (`nvidia.com/gpu=0` plus `/dev/dri`) with the EGL
   vendor pinned via `__EGL_VENDOR_LIBRARY_FILENAMES`. Without the pin, Mesa's dri2 platform
   claims the NVIDIA render node, logs `egl: failed to create dri2 screen` and never defers to
   the NVIDIA vendor. Software fallback is refused: `LIBGL_ALWAYS_SOFTWARE` is rejected once a
   hardware device is selected, and `QT_QUICK_BACKEND=software` renders the Qt interface but
   segfaults in `QOpenGLContext::done` before the 3D scene.

gz-transport discovery does not cross Podman's per-container bridge, so a GUI client sharing a
server SHALL share its network namespace. A GUI client is selected by overriding `ENTRYPOINT` in
the Quadlet unit, not by maintaining a second GUI image.


<a id="section-10-2-2"></a>

#### 10.2.2 Public Foxglove/Gazebo presentation

`ao-html-window` SHALL provide the public view into the simulation on the website. The presentation SHALL include the required kitchen, storage/CNC and vehicle views and the approved camera/model outputs defined above.

```text
Gazebo world + ROS sensor topics (private simulation)
        -> approved read-only Foxglove/presentation bridge
        -> ao-html-window controlled presentation
        -> approved public web origin linked/embedded on 300x3.com
```

The backend source interfaces SHALL remain `127.0.0.1:8765` portal, `/viewer`, and `127.0.0.1:8081` Foxglove WebSocket where specified. Public clients SHALL use a public origin, not their own loopback address. Exact public hostname/path SHALL be a declared publication configuration parameter; it SHALL NOT be invented by the specification editor.

The public edge SHALL permit only approved read-only protocol operations/content. It SHALL deny topic/command publication, service calls, simulation start/stop/reset/configuration, credential access and traversal into ROS/Gazebo/host administration. Simply proxying an unrestricted Foxglove bridge SHALL NOT satisfy view-only operation.

Public acceptance SHALL demonstrate content rendering from outside the host and rejected control/admin operations. Real-machine-derived datum/safety information SHALL receive sensitivity review before publication. Private operator lifecycle interfaces SHALL remain separately authenticated.


<a id="section-11"></a>

## 11. Ledger, Provenance, Archive, and IPFS


<a id="section-11-1"></a>

### 11.1 Ledger Authority Policy

Corda is the authoritative ledger for approved business provenance, receipt, entitlement,
fulfillment-approval and release-approval records. It is **not** the authoritative store for
domain-operational source data — that stays in the related PostgreSQL database (§3.3).

**Corda SHALL run under Podman/Quadlet on Corda 5.2.2 against `cordadb`**, a separate logical database on the host
PostgreSQL 18 cluster with its own roles and backup scope. H2 is not an acceptable backing
store for this node. Roles, host-loopback binding, backup scope, restore procedure, and
separation from the sales and mapping databases are specified in §17.1 and §3.3.1.

| Area | Authoritative operational data | Network | Origin Domain |
|---|---|---|---|
| Sales | Sales PostgreSQL order, fulfillment, and customer-service records | `ao-sales` | `sales` |
| Payment | Verified provider event record and normalized payment state | `ao-payment` (ingress via `ao-ingress-payment`) | `payment` |
| Field | Raw packet store, telemetry spool, and mission records | `ao-field` | `field` |
| Mapping | Validated imagery, WebODM project data, processing outputs, and deliverables | `ao-mapping` | `mapping` |
| Vehicle simulation | Scenario definitions, run data, and result artifacts | `ao-sim-vehicle` | `sim_vehicle` |
| Fabrication simulation | Facility/task models, safety scenarios, and result artifacts | `ao-sim-fabrication` | `sim_fabrication` |
| Archive | Encrypted archive objects and retention records | `ao-egress-archive` | `archive` |
| Ledger | Corda state, PKI, and the complete ledger of debits and credits | `ao-ledger-core` | `ledger` |

Network names are the real Podman names used throughout this document, in the Quadlet
definitions, and in `config/platform/network-cidrs.yaml`. Where an area is served by a
controlled adapter rather than a workload network, the adapter is named in the same cell.

**Origin Domain naming convention.** The `Origin Domain` column shows the logical
identifier used in the `origin_domain` field of ledger manifests (§11.5). Network names
use the `ao-` prefix with hyphens (e.g., `ao-sim-vehicle`); origin domains drop the
prefix and use underscores for simulation domains (`sim_vehicle`, `sim_fabrication`).
`payment`, `archive`, `ledger` and real-fabrication producers SHALL be represented explicitly by the approved schema and authenticated authorization policy; submitted origin fields SHALL NOT grant authority.

| Deployment property | Required definition |
|---|---|
| Runtime | Rootless operator-owned Podman store; systemd Quadlet lifecycle |
| Application persistence | Explicit mounted state/PKI paths; container replacement SHALL preserve state |
| Database | `cordadb`, PostgreSQL 18 host cluster in the supplied design; dedicated roles and backup scope |
| Network | `ao-ledger-core` plus only the explicitly approved narrow database/ingest/maintenance paths; no public core port |
| Resources | Declared memory/CPU/start timeout/restart/health policy in the unit |
| Credentials | Login-gated wallet/PKI delivery; no unattended pre-login protected startup |
| Acceptance | Restart/persistence, isolated access, ingestion/receipt correlation, backup and restore |

The containerized node SHALL NOT gain unrestricted host networking to reach a loopback source database. An approved host-mediated database path SHALL preserve the database's effective access boundary. This requirement does not silently move `cordadb` or authorize a database migration.

#### Origin-domain implementation status boundary

The domain table specifies required authority, not completed schema support. In the supplied implementation record, `payment`, `archive` and `ledger` are absent from the manifest enum and LEDGER-03 remains open. This README SHALL NOT declare that gap closed. Real-fabrication producer coverage SHALL likewise pass the approved schema, identity and signing tests before production acceptance. The dated record and original enum caveats are preserved in [the companion](README-COMPANION.md#ledger-schema-evidence).


<a id="section-11-2"></a>

### 11.2 Ledger Flow

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


<a id="section-11-2-1"></a>

#### 11.2.1 Cross-System Correlation and Provenance Model

The primary business correlation tuple is:

```text
serial_number + receipt_number + event_timestamp_utc
```

These fields link records across PostgreSQL domains and approved ledger records:

- `serial_number` identifies the physical product, vehicle, component, or asset.
- `receipt_number` identifies the approved commercial transaction or receipt.
- `event_timestamp_utc` identifies when the source event occurred, using ISO-8601 UTC.

The tuple SHOULD be accompanied by a source event identifier and schema version:

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

The same correlation fields SHOULD be carried into approved records from sales,
mapping, field, fulfillment, simulation, and release workflows where the event
is relevant. A database view or reporting projection SHOULD join the records by
the correlation tuple rather than by free-text names or presentation labels.

##### Ledger responsibility: integrity and provenance, not general encryption

Corda/blockchain records SHOULD contain the minimum data needed to verify that
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

The ledger SHOULD not contain:

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

##### Sales and marketing reporting flow

```text
Sales PostgreSQL salesdb
  order, product, serial, receipt, payment, fulfillment, entitlement
        │
        ├── correlation tuple:
        │     serial_number + receipt_number + event_timestamp_utc
        │
        ├── Metabase  (REPORTING — reads salesdb)
        │       └── sales/marketing reports and PDF exports
        │
        ├── Grafana  (dashboards and metrics — reads approved PostgreSQL)
        │       └── sales/fulfillment/provenance dashboards
        │
        └── signed minimized manifest
                └── Corda receipt/entitlement/provenance state
```

Marketing and sales reporting SHOULD use approved PostgreSQL views or
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

It SHALL NOT infer that a product is fulfilled, entitled, paid, or blockchain-verified
solely from a marketing label. Those states SHALL come from the authoritative
PostgreSQL event and the approved ledger projection.

##### Implementation preconditions

Before enabling this flow:

1. Initialize and verify the `salesdb` schema.
2. Define canonical `serial_number`, `receipt_number`, and UTC timestamp fields.
3. Confirm the Metabase reporting identity can read `salesdb` and produce the
   standard PDF reports and receipts, and confirm the Grafana datasource can
   read it for dashboards. Neither tool writes into `salesdb`.
4. Define the signed manifest schema and correlation-ID uniqueness rule.
5. Implement ledger-ingest authorization, signature verification, idempotency,
   replay protection, and audit logging.
6. Complete the Corda key/certificate ceremony.
7. Test the complete correlation path with synthetic data before connecting
   real sales, payment, customer, or product records.


<a id="section-11-2-2"></a>

#### 11.2.2 Mandatory Corda Entry Evidence

A sale is eligible for Corda submission only when all three evidence classes are present for
the same business correlation record:

1. **Sale-request email**
   - Customer-originated sale/KIT REQUEST email or approved equivalent.
   - Captures requester, requested items/SKUs, comments, and request timestamp.
   - Does not by itself prove a contract or payment.

2. **Payment-validation email**
   - Provider-specific validation for PayPal, Zelle, or Coinbase.
   - Identifies the provider, provider reference, amount, currency, validation
     status, and validation timestamp.
   - Does not by itself prove that funds settled into the approved account.

3. **Funds-transfer verification**
   - Operator/provider reconciliation evidence that the funds actually
     transferred and settled.
   - Records settlement/available state, transfer reference, amount, currency,
     and verification timestamp.
   - Must not be treated as verified merely because a payment was initiated.

The three records SHALL resolve to the same:

```text
correlation_id
receipt_number
serial_number(s)
event_timestamp_utc
```

Evidence record:

```text
evidence_id
evidence_type = sale_request | payment_validation | funds_transfer_verification
provider = website | paypal | zelle | coinbase | bank | manual_reconciliation
source_reference
received_at_utc
validated_by
content_hash_sha256
```

An evidence record counts only once it carries all of the following. Anything short of all of
them does not count, and no partial record is stored as though it did:

```text
sale_request.present                = true
payment_validation.present          = true
funds_transfer_verification.present = true
```


Corda records references, hashes, states, and operator authorization for these
three gates; it SHALL NOT store raw payment credentials or unrestricted email
content. PostgreSQL stores the detailed evidence metadata and reporting
projection. Metabase is for reporting and Grafana is for dashboards and metrics;
both show the resulting confirmed state and neither performs or waives the
verification.

Before the three gates can be satisfied, the operator key/certificate ceremony
SHALL be complete and the correlation path SHALL be proven with synthetic data.


<a id="section-11-2-3"></a>

#### 11.2.3 Corda-Managed Sale and Receipt Process

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
Corda, process payments, or create a public proof. Submission SHALL go through
the authorized ledger-ingest workflow after operator review.


<a id="section-11-2-5"></a>

#### 11.2.5 Ingest Security Requirements

The gateway SHALL enforce every control below before accepting an event. Client-side signing/staging SHALL NOT constitute acceptance.

| # | Requirement | Enforced by |
| --- | --- | --- |
| 1 | Mutual TLS; one client certificate per exporter domain | Gateway |
| 2 | Path authorization against `config/ledger/authorization-policy.yaml` | Gateway |
| 3 | JSON Schema validation against `config/ledger/manifest-schema.json` | Gateway |
| 4 | Detached signature verification against the exporter's registered key | Gateway |
| 5 | `producer_key_id` SHALL match the mTLS certificate identity | Gateway |
| 6 | Idempotency on `correlation_id` (§11.2.1) | Gateway |
| 7 | Replay defence — reject a re-presented digest/timestamp | Gateway |
| 8 | Audit log of accept **and** reject, with reason code | Gateway |

The JSON Schema SHALL use `additionalProperties: false` and explicitly contain every approved field. Raw PII, card/provider secrets, unrestricted telemetry and imagery SHALL be rejected, not merely discouraged. A `sales_receipt` SHALL require an issued `transaction_id`; `build-manifest.sh` SHALL reject its absence with exit `12`.

Cryptographic verification SHALL bind the actual immutable signed payload bytes/digest to the registered producer key and authenticated identity. Gateway-derived authority SHALL NOT trust submitted `producer_key_id` or `authorization_policy_id` without verification. Untrusted staged material under `artifacts/pending-ledger-submissions/` SHALL traverse the entire verification contract on replay; replay tooling SHALL NOT re-sign old input as if operator-approved.

Queue keys SHALL prevent filename collisions/data loss; staged artifacts SHALL use sensitive-data permissions, not executable/world-readable defaults. Unknown wallet producer keys SHALL return an explicit unsupported-key error, distinct from missing file errors. All approved producer domains SHALL have wallet-backed signing paths; fallback test keys SHALL NOT authorize production events.


<a id="section-11-3"></a>

### 11.3 Corda Stores and Private Data

Corda may retain approved private transaction data as an encrypted private
payload or encrypted attachment. Corda does not make plaintext private data
safe merely by being on a ledger: confidentiality depends on encryption,
authorized recipients, key management, access policy, and audit controls.

#### Corda contract state

Corda state SHOULD contain the small, shared, verifiable business facts:

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

#### Encrypted private payload

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

The private payload envelope SHALL include:

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

The encryption key SHALL be held by the approved KMS/wallet/key-management
process and SHALL never be stored in Corda, PostgreSQL, Git, HTML, logs, or the
transaction bundle.

Corda tracks the transaction ID, state, hashes, references, and authorized
signatures. PostgreSQL retains the operational/reporting projection keyed by
the same transaction ID. Metabase reports the confirmed state and Grafana shows
it on a dashboard; neither creates or waives payment verification.


<a id="section-11-3-1"></a>

#### 11.3.1 Accounting Model for the Authoritative Ledger

Corda is the authoritative record of **approved postings**. PostgreSQL remains
authoritative for **source operational data** (§11.1). The two are not in
conflict: a posting is an approved assertion that a business event occurred, and
it exists only after the event is verified and reconciled. The accounting report
required by §4.4 is **computed in reporting**, from approved PostgreSQL rows
joined to approved Corda postings by the correlation tuple — never from a balance
stored as a mutable field on the ledger.

##### Accounts

The account set is deliberately small and closed. Anything that is not one of
these is rejected at ingest.

| Code | Type | Meaning |
|---|---|---|
| `CASH_EU` / `CASH_US` | Asset | Funds received and settled into the approved account |
| `CASH_PENDING` | Asset | Payment validated but **not** yet funds-transfer verified (§11.2.2 gate 3) |
| `RECEIVABLE_CUSTOMER` | Asset | Entitlement issued, payment not yet verified |
| `REVENUE_SALE` | Revenue | Value of a confirmed sale |
| `REVENUE_DIGITAL_TRANSFER` | Revenue | Value of a post-sale archive/IPFS transfer |
| `REFUNDS_PAYABLE` | Liability | Refunds approved and owed |
| `TAX_PAYABLE_<jurisdiction>` | Liability | Tax accrued and owed, per approved jurisdiction |
| `EXPENSE_ARCHIVE` | Expense | pCloud/IPFS replication cost attributed to a delivery |

##### Debit/credit entry semantics

Every posting is a **balanced double-entry** of two or more legs against one
`transaction_id`. Each leg carries `account_code`, `side` (`DEBIT` | `CREDIT`),
`amount`, `currency`, and `correlation_id`. The invariant, enforced at ingest and
re-checked in reporting:

```text
SUM(debits) = SUM(credits)   per transaction_id, per currency
```

A posting that does not balance, or that mixes currencies within one leg set, is
**rejected**. There is no unbalanced posting and no "plug" or suspense account
that exists to absorb a difference.

- Amounts are stored in **minor units as integers** (cents). No floats.
- Amounts and balances are immutable once a posting is confirmed. A correction is
  a **new reversing transaction** referencing the original `transaction_id`;
  history is never edited and never deleted (§11.6, rule: no data deletion).
- Corda records **no running balance**. A balance is a query result over the
  posting set, so a balance can never disagree with its postings.

##### Currency handling

A posting is **single-currency**. Multi-currency is handled by separate postings
plus an explicit `FX_REVALUATION` event carrying `from_currency`,
`to_currency`, `rate_source`, and `rate_as_of_utc`. The rate is a recorded input,
never computed silently. There is no implicit conversion at read time.

##### Posting rule (what may be posted, and when)

```text
NO EVENT, NO POSTING
```

| Event | May post to | Gate |
|---|---|---|
| Payment provider event received | — | None. This is **not** a posting. It only advances `CASH_PENDING`. |
| Payment validated | — | Still not a posting; §11.2.2 gate 2 alone is insufficient |
| Funds transfer verified | `CASH_EU`/`CASH_US` DR / `RECEIVABLE_CUSTOMER` CR | **All three** §11.2.2 gates |
| Entitlement issued | `RECEIVABLE_CUSTOMER` DR / `REVENUE_SALE` CR | Sale confirmed on the ledger |
| Post-sale transfer authorised | `CASH_EU`/`CASH_US` DR / `REVENUE_DIGITAL_TRANSFER` CR | `ao-sales` authorisation (§11.6) |
| Refund approved | `CASH_EU`/`CASH_US` DR / `REFUNDS_PAYABLE` CR | Explicit operator approval |
| Archive replication cost | `EXPENSE_ARCHIVE` DR / `CASH_EU`/`CASH_US` CR | Verified provider cost |

Every row above names exactly two legs and they are the DR/CR pair required by the
balance invariant, so each row is a balanced posting on its own. `CASH_PENDING` is
named only in the "not a posting" rows and is deliberately **absent** from this table;
`TAX_PAYABLE_<jurisdiction>` has no posting rule here — see §11.12, finding 3.

**Corda is not a payment processor and does not create funds.** It cannot move
money, initiate a refund, set a price, or decide tax. It records that an approved
event happened and was authorised by whom. A posting is evidence, never a
payment instruction (§7.2).

##### Reconciliation between Corda and `salesdb`

Both sides are compared **per correlation tuple** and reported as a difference,
never auto-corrected:

```text
for each (receipt_number, serial_number, event_timestamp_utc):
  ledger_posting_set   := approved Corda postings
  salesdb_record_set   := verified + operator-reconciled salesdb rows
  reconcile            := matched | ledger_only | salesdb_only | amount_mismatch | currency_mismatch
```

Rules:

1. A `salesdb` row with **no** approved Corda posting is `salesdb_only`. It is a
   missing posting and is an **exception that blocks the receipt being called
   final** (§11.2.3).
2. A Corda posting with **no** `salesdb` row is `ledger_only` and is a provenance
   defect. It is investigated; it is not deleted.
3. Amount or currency disagreement is `amount_mismatch` / `currency_mismatch` and
   is resolved by a reversing transaction plus a corrected posting (§11.2.2 gate
   evidence is re-checked), never by editing either side.
4. Reconciliation is a **read-only report**. Metabase surfaces it; Grafana
   dashboards it. Neither writes to `salesdb` or to Corda.

##### What the §4.4 accounting report is

`Standard accounting/ledger report PDF → ao-admin reporting output` (§4.4) is a
**computed projection**, built from approved `salesdb` rows joined to approved
Corda postings by the correlation tuple. It reports postings, not stored
balances. It cannot create, waive, or infer a payment state: §11.2.2 gate
evidence and the Corda posting SHALL both be present, or the line does not appear.


The event/account table above SHALL be retained as the source-defined mapping, not silently replaced with generic accounting tasks. Its refund cash direction, tax posting carrier and cash-pending semantics SHALL require explicit accounting approval before automatic production posting; balanced arithmetic alone SHALL NOT establish correct economic meaning. Until that narrow ambiguity is resolved, affected automatic postings SHALL be blocked, without deleting the defined account set, leg schema, currency or reconciliation rules.


<a id="section-11-4"></a>

### 11.4 Corda Does Not Store

Corda may store approved encrypted private transaction data as described in §11.3. It SHALL
never store plaintext secrets or unencrypted credentials.

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


<a id="section-11-5"></a>

### 11.5 Manifest Format

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


The example above SHALL NOT be treated as the complete JSON Schema. The canonical schema SHALL additionally define these fields and conditions:

| Field / structure | Required contract |
|---|---|
| `transaction_id` | ALWAYS ON-issued ID; mandatory for `sales_receipt` |
| `correlation_id` | Durable event correlation and idempotency key subject to declared uniqueness scope |
| `serial_number`, `receipt_number`, `event_timestamp_utc` | Cross-system tuple (§11.2.1); explicit applicability/nullability per event |
| `event_type`, `source_domain`, `source_record_id` | Typed source event/identity linkage |
| `signed_payload_sha256` or equivalent declared canonical signed representation | Reproducible verification of the actual signed fields; embedding signature metadata SHALL NOT change signed meaning |
| Posting leg array | `account_code`, `side`, integer minor-unit `amount`, `currency`, `correlation_id`; at least two balanced legs per transaction/currency |
| Reversal reference | New reversal transaction referencing the original `transaction_id`; immutable original history |
| FX evidence | `from_currency`, `to_currency`, `rate_source`, `rate_as_of_utc` when conversion/revaluation applies |
| Producer/event enums | Sales, payment, field, mapping, vehicle/fabrication simulation, real fabrication and approved archive/ledger events; explicit types for postings/reversals |

Schema version/signature encoding/canonicalization SHALL be explicit deployed contract parameters; the editor SHALL NOT claim that a historically shown `1.0` example already implements these extensions. Unknown fields/types SHALL be rejected; approved extensions SHALL be versioned and migrate producers/validators together.


<a id="section-11-6"></a>

### 11.6 pCloud and IPFS Rules

**What "archived" means here.** A package held by `ao-egress-archive` is **"archived for
data transfer and sale"**. It is **not a backup**. It exists so a sold map, imagery set, or
telemetry/IoT package can be *transferred* to the authorised recipient, and verified in
transfer, with a blockchain sales listing where applicable. There is **no restore duty, no
recovery duty, and no retention duty** attached to it.

**The backup is restic.** Host-wide encrypted backup and restore validation are governed by
§17.1. If `ao-egress-archive` is lost, nothing is "recovered" from it — the backup
set is what protects the data, and the backup set lives under restic, not IPFS and not
pCloud archival staging.

**Authorisation.** `ao-egress-archive` requires **`ao-sales` authorisation** first. It is
never reached directly from the internet and it does not originate a transfer on its own.

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
- For post-sale transfer of sensitive artifacts, use a private IPFS swarm,
  controlled pinning, or encryption before any public IPFS distribution.
- Record content hash and CID separately.
- Post-sale, store only CIDs and encrypted package references in Corda. IPFS is a
  post-sale marking/transfer mechanism only (§1); it is not archive, accounting,
  or ledger storage, and Corda has no IPFS dependency.
- **IPFS is for file-transfer verification and, potentially, sales listing on a
  blockchain.** It is not a backup, not a disaster-recovery copy, and not a retention
  store.
- **pCloud replication here is a transfer copy, not the backup set.** The backup set is
  restic (§17.1).
- Archive replication occurs only through `ao-egress-archive`.


<a id="section-12"></a>

## 12. Host Installation and Configuration


<a id="section-12-1"></a>

### 12.1 Installation Journal

Every installation/change session SHALL create `/ALWAYSON/logs/installation/agent-install.log` and update the canonical installation journal, recording UTC time, actor, commands, versions, results and failures without secrets. Inventory SHALL precede any installation or mutation. Destructive changes SHALL require explicit approval.


<a id="section-12-2"></a>

### 12.2 Initial Non-Destructive Inventory

The following non-destructive inventory SHALL run before an approved installation/change session. It is a collection script, not an asserting acceptance test: `|| true` retains collection after unavailable commands; failures SHALL be recorded and SHALL NOT become passing verification. Access to privileged observations SHALL require the operator's authorized context. Sensitive process/log/configuration output SHALL be reviewed/redacted before sharing; the journal SHALL NOT contain secret values.

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


<a id="section-12-3"></a>

### 12.3 Host Dependencies

Bootstrap SHALL install the following declared package dependencies from approved sources after inventory and installation approval:

```text
podman
uidmap
slirp4netns
fuse-overlayfs
containernetworking-plugins
nftables
ufw
git
curl
jq
ca-certificates
gnupg
openssl
restic
smartmontools
lm-sensors
acl
python3
python3-venv
python3-pip
apparmor-utils
nvidia-container-toolkit
libnvidia-container1
libnvidia-container-tools
nvidia-container-toolkit-base
```

`scripts/bootstrap/02-install-host-dependencies.sh`, `scripts/bootstrap/ao-bootstrap-privileged.sh` and `scripts/provision/provision.sh` SHALL reproduce the dependency set rather than assume hand-installed packages.

`./scripts/validation/verify-host-baseline.sh` SHALL assert Podman responsiveness, user manager reachability, required session persistence, cgroup v2 and AppArmor tooling. It SHALL distinguish `aa-status` from `aa-enforce`, print expected/observed values, return nonzero on failure and include a known-failure test. Privileged checks unable to authenticate SHALL be blocked/failing, never hidden by `sudo ... || true`.


<a id="section-12-3-1"></a>

#### 12.3.1 User-session persistence and startup ordering

The operator's user manager MAY use linger for persistent systemd/Quadlet management. Provisioning SHALL inspect `loginctl show-user -p Linger scottw` and assert the required `Linger=yes` value rather than key presence alone. Linger SHALL NOT authorize credential-dependent startup before authenticated Plasma login. Every wallet-backed service SHALL additionally satisfy §14 even if user targets/timers are active at boot.


<a id="section-12-4"></a>

### 12.4 Rebuilding This Host From Nothing

The clean host prerequisite SHALL be Kubuntu 26.04 LTS with KDE Plasma, approved Cline CLI/operator tooling and approved internet access. `scripts/provision/provision.sh` SHALL reconstruct the declared system in stages, default to dry run and require `--yes` for apply.

| Stage | Required output / behavior |
|---|---|
| 10 | Approved third-party apt repositories, including ROS source policy; TLS verification SHALL NOT be bypassed |
| 20 | Host dependencies, operational layout, Podman networks and inventory; delegates to `scripts/bootstrap/00`, `02`, `03`, `04`; reports session persistence and credential-start gates |
| 30 | Declared snaps/flatpaks from inventory/manifests, not a stale count |
| 40 | Host applications from `unmanaged-software.yaml`; vendor blobs through `install-vendor-binaries.sh` |
| 50 | Declared domain Quadlet source units copied into the flat user deployment directory |
| 60 | Secret presence and authorized delivery check derived from actual consumers' `EnvironmentFile=` declarations; after login |
| 70 | Data presence/check only; SHALL NOT restore data automatically |
| 90 | Asserting verification and regenerated inventory compared with `docs/software-status.md` |

Persistent application data SHALL come from approved backups. Protected credentials SHALL come from the authorized wallet/recovery path after login, not by restoring stale plaintext env files from Git or backup. Vendor binaries SHALL follow the digest-verified manifest contract (§12.4.1).


<a id="section-12-4-1"></a>

#### 12.4.1 Vendor artifact manifest and digest contract

`config/build-update/vendor-binaries.yaml` SHALL declare each artifact's `id`, `version`, install kind, target `path`, download `sha256`, optional `sha256_published_by_vendor`, and, for archives, selected `member` and `installed_sha256`.

The download digest and installed-file digest SHALL be distinct where extraction changes the artifact. AppImages MAY use the same digest for both. `scripts/provision/install-vendor-binaries.sh` SHALL default to dry run; `--yes` SHALL authorize only the reviewed install plan. It SHALL verify existing files and refuse mismatched/unpinned artifacts instead of overwriting them.

| Exit | Meaning |
|---|---|
| `0` | Declared checks/install outcomes clean |
| `1` | Download/install failure |
| `2` | At least one refusal, including DRIFT or unpinned download |

The manifest SHALL cover QGroundControl, ReticulumMeshChatX, LM Studio, pCloud, nPerf, gh, bun and Cline where supplied as vendor/non-package artifacts. An absent automated download URL SHALL be reported as a manual supply requirement, not converted into fabricated installation success. All required artifacts SHALL have actual supply/identity acceptance.


<a id="section-12-4-2"></a>

#### 12.4.2 Provisioning rollback contract

Every provisioning stage SHALL declare its before-state capture, changed files/units, non-destructive undo, prerequisites and validation. Rollback SHALL restore only the requested domain/stage and SHALL NOT remove unrelated flat-deployed units, delete persistent volumes, reformat storage or silently overwrite data. Irreversible data/schema changes SHALL have an approved backup/restore plan rather than a fictitious undo command. A clean-room rebuild and rollback exercise SHALL establish reproducibility; source-file presence alone SHALL NOT do so.


<a id="section-12-5"></a>

### 12.5 Inventory and Update Management

The provisioned host is then verified against the committed inventory, and kept
current from it.

```bash
sudo ./scripts/build-update/refresh-install-log.sh --refresh
```

Regenerates `docs/software-status.md` (229 rows, every cell populated),
`update-plan.json`, the HTML and the PDF. The plan marks every item either
**eligible** with exact ordered steps, or **excluded** with the rule that
excludes it — the payment path (rule 7/14), WebODM and nodeodm (rule 10), the
production databases (rule 14), and the deliberate Mastodon and ArduPilot
decisions. Nothing is executed by the tooling; applying anything is an operator
decision. Ubuntu archive security updates are already handled automatically by
`unattended-upgrades` and need no action here.


<a id="section-12-5-1"></a>

#### 12.5.1 Installation-date provenance

`scripts/build-update/apt_history.py` SHALL derive installation dates from `/var/log/apt/history.log` and rotated `.gz` histories, distinguish `Install:` from `Upgrade:`, and identify unattended versus human changes. Packages outside retained history SHALL report no recorded install date. Dpkg `.list` mtime SHALL NOT be presented as an installation date. `provenance/collector.py` SHALL consume this ground-truth history consistently for package inventory.


<a id="section-12-5-2"></a>

#### 12.5.2 Generator regression requirements

`scripts/build-update/test_generators.py` SHALL test generated plan safety and rendering, including:

- Every emitted container-pull step SHALL carry a complete 64-character SHA-256 digest, not a truncated hash.
- Unknown/unreachable/refused/not-found/not-recorded/error markers SHALL NOT become install arguments.
- Apt actions SHALL use package identifiers, not desktop display names.
- Module/import boundaries, allowlists, source-of-truth paths and roll-up member visibility SHALL have regression tests.

Tests SHALL run without applying upgrades, publication, restarts or production data mutation, and return nonzero for each deliberate failure/control case.


<a id="section-12-5-3"></a>

#### 12.5.3 Executable update-plan schema

`provenance/plan.py` SHALL emit a machine-readable plan distinguishing `eligible` from `excluded`, with exclusion/approval reasons. An eligible action SHALL have ordered exact argv arrays under `steps` and separate human prose under `manual`.

Allowed verbs SHALL be explicitly constrained to approved `podman`, `snap`, `flatpak`, `apt`, `apt-get`, `systemctl` and named deploy-script operations. `_argv_is_safe()` SHALL reject unsafe arguments/shell metacharacters; unsafe proposals SHALL be downgraded to explained manual work, not executable shell text. Empty executable steps SHALL NOT claim automatic eligibility. Manual `Image=` editing or approval SHALL remain a human phase rather than masquerade as executable automation.


<a id="section-12-5-4"></a>

#### 12.5.4 Dry-run plan validator contract

`scripts/build-update/apply-plan.py` SHALL validate, never execute. It SHALL load `data/build-update/update-plan.json`, compute SHA-256, optionally snapshot the reviewed plan under `data/build-update/runs/`, validate schema and argv allowlists, derive shared-image/deploy-domain blast radius, and report exactly what would be touched.

| Interface | Required behavior |
|---|---|
| `AO_ROOT` | Explicit project/worktree root; report actual resolved plan path |
| `--no-snapshot` | Validate without writing a plan snapshot |
| `--expect-hash` | Reject any bytes other than the approved plan hash |
| Exit `0` | Well-formed plan |
| Exit `2` | Usage error |
| Exit `3` | Schema/safety validation failure |
| Exit `4` | Approved hash mismatch |

Schema-1 prose steps SHALL NOT be accepted as safe argv plans. Plan-hash approval SHALL bind exact bytes, not a mutable filename. Validator allowlists SHALL remain independently usable if the producer is broken, with `TestVerbAllowlistAgreesAcrossFiles` preventing drift. Worktree invocations SHALL set `AO_ROOT` explicitly; summary/render scripts SHALL use that root rather than a hidden `/ALWAYSON` literal.


<a id="section-12-5-5"></a>

#### 12.5.5 Deployed-image identity capture

`scripts/validation/capture-version-matrix.sh` SHALL capture `podman inspect` deployed image identities and map container names to version-matrix fields for Mastodon web/streaming/Sidekiq/database/Redis, Grafana, Metabase, Prometheus, node exporter, Gazebo, Foxglove, WebODM web/database/broker/NodeODM and payment ingress.

Every recorded running digest SHALL match the actual container, every operational running digest SHALL be represented, and tag-only or unmanaged duplicates SHALL be findings. Absent/non-running instances SHALL be distinguished from verified running images; failed digest lookup SHALL NOT silently certify completeness. Package/kernel versions SHALL be captured, not transcribed. Approval SHALL precede deletion of stray containers. Generated inventory/PDF/HTML SHALL be refreshed before serving as deployment evidence.


<a id="section-12-5-6"></a>

#### 12.5.6 Inventory roll-up representation

Every aggregate inventory row SHALL retain a `members` list carrying individual names and installed versions. Ubuntu archive, frozen ROS train, KDE components and grouped desktop launchers SHALL remain drillable in Markdown, HTML and print/PDF output.

Package roll-ups SHALL render one member per row with a version column inside a collapsible section; they SHALL NOT become a single unscannable joined text cell. HTML member values SHALL be escaped. `rollup_details_md()` SHALL remain independently testable without expensive collection. `TestRollupsCanBeDrilledInto` and `test_the_apt_rollups_carry_their_members` SHALL fail if a member list disappears or print CSS hides it. Generated artifacts SHALL be regenerated with the current renderer before acceptance.


<a id="section-13"></a>

## 13. Podman Runtime and Quadlet Policy


<a id="section-13-1"></a>

### 13.1 Rootless and System-Level Podman

Ordinary application workloads SHALL use rootless Podman and user-level
Quadlet units.

Rootless Quadlet definitions SHALL be stored in:

```text
~/.config/containers/systemd/
```

System-level Quadlet definitions SHALL be stored in:

```text
/etc/containers/systemd/
```

System-level services are permitted only where a documented host-hardware,
GPU, storage, networking, or service-management requirement makes rootless
operation unsuitable.


<a id="section-13-2"></a>

### 13.2 Podman Store Model

The designated container runtime SHALL be one rootless store owned by operator `scottw` (uid 1000), with graph root `/home/scottw/.local/share/containers/storage` and flat user Quadlets under `~/.config/containers/systemd/`. Suitable host-native services SHALL remain outside that container store.

| Interface / state | Required value |
|---|---|
| `podman info` rootless | `true` |
| Workload ownership | Operator account; no per-service workload store |
| Quadlet `User=` / `Group=` | SHALL NOT substitute separate workload identities for the operator model without approved exception |
| Rootful/system store | No ALWAYS ON workload containers/volumes/pods |
| Podman GUI/connections | Operator-local rootless connection; no undeclared remote/additional store |
| `ao-podman-bridge.service` | Not an active part of this design |
| `/run/ao-podman/` | No operational per-service sockets |
| Unit resources | Explicit systemd resource and restart policy |

Corda SHALL use the same managed rootless Podman approach rather than a special unmanaged native node. All credential-bearing containers SHALL remain login-gated. Explicit bind mounts SHALL be purpose-limited; rootless ownership SHALL NOT excuse privileged containers, added capabilities, uncontrolled source access or general public listeners.

#### Rootless-store verification commands

The source verification interfaces SHALL remain accessible. The following table defines checks and expected boundaries; it is not new evidence that they passed today.

| Verification subject | Source command / expected boundary |
|---|---|
| Is the operator Podman rootless? | `podman info --format '{{.Host.Security.Rootless}}'` → `true` |
| Which store backs it? | `podman info --format '{{.Store.GraphRoot}}'` → `/home/scottw/.local/share/containers/storage` |
| Do any Quadlet units name a `User=` or `Group=`? | none — `grep -rn '^User=\|^Group=' quadlet/` returns nothing |
| Are there system-level `.container` or `.network` units? | **No.** `systemctl list-unit-files '*.container' --no-legend \| wc -l` → `0`, and `systemctl list-unit-files 'ao-*' --no-legend \| grep -Ec '\.(container\|network)$'` → `0`. Every mapping unit is `systemctl --user`, state `generated` (Quadlet generator output) |
| Are the WebODM containers in the operator store? | `podman ps` lists `ao-webodm-{webapp,worker,db,broker}` and `ao-nodeodm` from the rootless store above |
| Are the declared extra connections real? | `podman system connection list` → header only; `~/.config/containers/podman-connections.json` is `{"Connection":{},"Farm":{}}` |
| Does `/run/ao-podman/` exist? | `ls /run/ao-podman` → `No such file or directory` |
| Is `ao-podman-bridge.service` active? | `systemctl is-enabled ao-podman-bridge.service` → `disabled`; `systemctl --user is-enabled` → `not-found` |
| Does the **rootful** store hold any workload? | **No.** `/var/lib/containers/storage/db.sql` is world-readable and its `ContainerConfig`, `ContainerState`, `ContainerExitCode`, `VolumeConfig`, `PodConfig` and `ContainerDependency` tables are **all empty** (row count `0` each). Enumerated without `sudo`; see §13.2.1 |

A missing table, unavailable metadata backend or privilege-denied observation SHALL be reported as blocked/error—not assumed empty. Runtime metadata backend/type SHALL be checked before relying on legacy SQLite paths. Mutable counts and rootful-store observations SHALL be refreshed for acceptance. A user-owned rootless runtime SHALL NOT bypass the login gate for protected workloads.


<a id="section-13-3"></a>

### 13.3 `/ALWAYSON` Layout

```text
/ALWAYSON/
├── README.md
├── VERSION
├── AGENTS.md
├── quadlet/
│   ├── networks/          # approved ao-* .network definitions (see network-cidrs.yaml)
│   ├── sales/             # ao-mastodon-{db,redis,web,sidekiq,streaming}, ao-sales-db
│   ├── mapping/           # ao-webodm-{webapp,worker,db,broker}, ao-nodeodm
│   ├── operations/        # grafana, metabase, prometheus, node-exporter, bridges
│   ├── fabrication/       # ao-fabrication-db and the host-side collector
│   ├── payment/           # ao-ingress-payment and ao-payment-relay
│   └── sim-vehicle/       # ao-ardupilot-sitl
├── config/
│   ├── platform/          # network CIDRs, version matrix, topology model,
│   │                      # GUI boundary matrix, monitoring
│   ├── sales/  mastodon/  mapping/  field/  drone/  ledger/
│   ├── sim-vehicle/  sim-fabrication/  models/  storefront/
│   └── pcloud/  ipfs/
├── scripts/               # operations, mastodon, backup, restore, validation, deploy
├── docs/                  # runbooks, compliance, faith
├── forms/                 # Corda sale-receipt forms
├── assets/                # README diagrams
├── agents/                # agent instructions
├── secrets/               # IGNORED - approved non-authoritative runtime/PKI material only; wallet delivery under §14
├── data/                  # IGNORED - persistent runtime data (restic, corda-install)
├── logs/                  # IGNORED - operational logs
├── artifacts/  backups/   # IGNORED - generated artefacts and restore material
├── pcloud/  ipfs/         # IGNORED - transfer working areas
└── tmp/                   # IGNORED
```


<a id="section-13-3-1"></a>

#### 13.3.1 Additional paths

The tree above is the design layout. The following additional paths SHALL have these roles:

| Path | What it is |
|---|---|
| `TOPOLOGY/` | topology graphic source and review material |
| `LOGS-JOURNALS/` | pointer only — the logs live in `logs/` (§16.3, §16.3) |
| `GAZEBO/`, `SIMULATION.png`, `WEBSITEMAIN.png` | simulation and storefront imagery |
| `README - ARCHIVE/` | archived README versions and review comments |

The storefront is served from filedn and has no local `storefront/` directory. Validation
lives in `scripts/validation/`, not `tests/`. Mastodon Quadlet definitions live in
`quadlet/sales/`.

The repository baseline branch SHALL be `main`; `.gitignore` SHALL cover every path marked `IGNORED` above, plus
Python bytecode, `*.BAK-*` unit backups, and generated topology binaries. A secret-exposure
check runs over every tracked file:
`scripts/validation/check-secrets-exposure.sh`.


<a id="section-13-4"></a>

### 13.4 Quadlet Network Template

```ini
# /ALWAYSON/quadlet/networks/ao-mapping.network
[Network]
NetworkName=ao-mapping
Driver=bridge
Internal=true
```


<a id="section-13-5"></a>

### 13.5 Quadlet Service Template

```ini
# /ALWAYSON/quadlet/mapping/ao-webodm-web.container   (illustrative template)
[Unit]
Description=ALWAYS ON WebODM Web Service
After=network-online.target graphical-session.target
Wants=network-online.target
PartOf=graphical-session.target

[Container]
Image=REPLACE_WITH_APPROVED_IMAGE_DIGEST
ContainerName=ao-webodm-web
Network=ao-mapping.network
Volume=/media/scottw/500GBPHOTOGRAM/webodm/media:/webodm/app/media:Z
Volume=REPLACE_WITH_APPROVED_CONFIG_PATH:/config:ro,Z
NoNewPrivileges=true

[Service]
Restart=on-failure
RestartSec=15
MemoryMax=12G
CPUQuota=600%
TimeoutStartSec=180

[Install]
WantedBy=graphical-session.target
```

This is a structural template only. The exact image, API settings, mounts,
service name, environment, and GPU configuration SHALL be taken from the tested
and approved WebODM version.

---


This structural template SHALL NOT omit required credential delivery in a concrete database/application unit. Credential-consuming units SHALL have fail-closed wallet/readiness ordering before container creation; the session target alone SHALL NOT prove wallet unlock or fetch success. `EnvironmentFile=` SHALL reference the scoped delivered file and SHALL NOT carry inline secrets.


<a id="section-14"></a>

## 14. Secrets and Service Identity


<a id="section-14-1"></a>

### 14.1 Secret Delivery

KDE Wallet SHALL be the encrypted-at-rest credential authority. Every process, service, container and dependent workload requiring protected credentials SHALL load/start only after authenticated operator login and authorized wallet access.

The gate SHALL apply to databases, Corda/PKI, payment, AI/social, monitoring, backup and their protected dependencies. Linger, boot targets, retained env files, restart loops and timers SHALL NOT authorize pre-login protected startup. Non-secret prerequisite services MAY run before login where explicitly approved.

| Control | Required contract |
|---|---|
| Session ordering | Wallet-backed units SHALL be associated with `graphical-session.target`; runtime SHALL additionally verify authenticated session and usable wallet |
| Readiness | `isOpen(handle)` / authorized entry access, not mere daemon presence |
| Fetch budget | Bounded approximately 60 seconds (`30 × 2s`); fail closed when unavailable |
| Delivery root | `%h/.local/share/ao-secrets/` |
| File creation | `umask 077`, atomic temp write/rename and least-privilege permissions |
| Startup | `ExecStartPre` fetch/readiness SHALL succeed before container creation; ignore-failure `-` prefix SHALL NOT bypass required credentials |
| Stale files | SHALL NOT authorize startup before login or after a failed refresh |
| Runtime adoption | Restart/recreate consumer after approved rotation; verify actual adopted credentials, not only file mtime |
| Exposure | No secret values in logs, Git, shell arguments/history, HTML or diagnostic output |

Approved environment files SHALL be delivery copies, not independent credential authorities. Their persistent on-disk lifetime SHALL be explicit; cleanup of `.tmp` SHALL NOT be represented as shredding the main file. Screen-lock/logout stop/revocation behavior is not specified by the startup-gate requirement and SHALL NOT be invented. Protected missed timers SHALL use approved post-login catch-up rather than secret access before login.

#### Secret-control acceptance map

| Control | Required behavior | Executable / observable verification |
|---|---|---|
| Authenticated-login gate | Required secrets and protected dependents SHALL remain unavailable before login | Controlled pre-login/post-login test; `systemctl --user show <unit> -p WantedBy,PartOf` is supporting configuration evidence, not sufficient alone |
| Normal env-file permissions | Scoped operator-owned `0600`, unless a separately approved narrow named-reader ACL applies | `stat -c '%a %n' ~/.local/share/ao-secrets/*.env`; inspect approved ACL without values |
| Delivery/adoption lifetime | Fresh authorized fetch before consumer creation and after rotation | `podman inspect <container> --format '{{.State.StartedAt}}'`; compare protected non-disclosing adoption checks, not timestamps alone |
| Temporary-file cleanup | `.tmp` cleanup SHALL NOT be described as shredding the persistent env file | Inspect `cleanup_tmp`/trap; verify no orphan temp and enforce the selected lifetime policy |
| No secret in journal | Fetch errors SHALL be visible without values; required fetch failure SHALL block startup | Inspect `ExecStartPre`; no ignored required fetch; test unavailable credential path |
| Domain ownership | No generic cross-domain folder/read grant | Presence-only owning-folder/entry tests with absent-entry negative controls |
| Wallet recovery | A recoverable approved backup or actual-authority reprovision/rotation path SHALL be tested | Check backup path/configuration and run approved isolated recovery; do not assume wallet files are covered |

`post.sh` and signing helpers that use transient shredding SHALL retain their explicit cleanup contract. Persistent env copies SHALL NOT be falsely reported shredded on exit. The source wallet-backup gap is retained in [the companion](README-COMPANION.md#wallet-recovery-evidence), with SEC-03 as existing owner; this requirement does not claim the backup is installed.


<a id="section-14-1-1"></a>

#### 14.1.1 KDE Wallet Secret Management

The wallet service SHALL use `kwalletd6`, D-Bus `org.kde.kwalletd6`, object `/modules/kwalletd6`, wallet `kdewallet`. New tooling SHALL prefer that interface over legacy aliases. Management SHALL run from the authorized interactive Plasma session.

| Tool | Required responsibility |
|---|---|
| `scripts/ops/kwallet-provision.sh` | Create approved folders and provision entries; presence checks without exposing values |
| `scripts/ops/wallet-read-secret.py` | Authorized `hasEntry`/`readPassword` access |
| `scripts/ops/wallet-write-secret.py` | Authorized `writePassword` access |
| `scripts/operations/fetch-kwallet-secret.sh` | Login/wallet wait; explicit key/folder case mapping; per-consumer atomic env materialization |
| `ao-wallet-bridge.sh` | Approved consumer env materialization, never a generic cross-domain secret dump |

All services SHALL use the operator-owned runtime model in §13.2 unless an explicit identity exception is approved. Credentials SHALL live in exactly one owning folder; the database role and consumer SHALL share the same authorized source value.

| Folder | Purpose |
|---|---|
| `ao-mastodon` | Mastodon application secrets (§15.3) and OpenClaw OAuth material; read by `fetch-mastodon-env.sh` and the wallet bridge |
| `ao-sales` | `sales-db-password` |
| `ao-fabrication` | `fabrication-db-password` |
| `ao-mapping` | WebODM postgres password |
| `ao-admin` | `grafana-db-password`, `grafana-admin-password`, `metabase-db-password`, `metaread-password`, `sales-reporting-password`, `restic-repository-password` |
| `ao-sim-vehicle`, `ao-sim-fabrication` | Per-domain credential folders matching the §14.1 authorized-domain table |
| `ao-payment`, `ao-field`, `ao-ledger`, `ao-archive` | Created only when the consumer exists and the credential is provisioned (§14.1.2), never speculatively. Provisioning SHALL follow the actual approved payment consumer |

| Folder | Entries |
|---|---|
| `ao-mastodon` | `mastodon-secret-key-base`, `mastodon-otp-secret`, `mastodon-db-password`, `mastodon-ar-deterministic-key`, `mastodon-ar-primary-key`, `mastodon-ar-derivation-salt`, `mastodon-admin-password`, `openclaw-bot-client-id`, `openclaw-bot-client-secret`, `openclaw-bot-access-token`, `openclaw-bot-password`, `roundtrip`/`roundtrip2` (test artifacts) |
| `ao-sales` | `sales-db-password` |
| `ao-fabrication` | `fabrication-db-password` |
| `ao-mapping` | WebODM postgres password |
| `ao-admin` | `grafana-db-password`, `grafana-admin-password`, `metabase-db-password`, `metaread-password`, `sales-reporting-password`, `restic-repository-password` |

Test artifacts such as `roundtrip`/`roundtrip2` SHALL NOT become production credentials. New consumers SHALL have explicit folder/key mappings before startup. No generic cross-domain wallet folder or unused plaintext credential collection SHALL be created.

Grafana web administration SHALL use `ao-admin/grafana-admin-password`; non-secret `config/platform/monitoring/grafana-admin.env` SHALL remain separate from `%h/.local/share/ao-secrets/reporting-grafana-admin.env`. Database/reporting provisioners SHALL read passwords from the wallet, not seed authority from an old env file. `scripts/mastodon/post.sh` SHALL protect transient credentials and remove them on exit; `provision-openclaw-bot.sh` SHALL store new credentials in the wallet, not a persistent extra plaintext store.

`check-secrets-exposure.sh` SHALL reject secret-bearing tracked env files, secret-bearing `EnvironmentFile=` references into tracked `config/` or `secrets/`, and overbroad file/ACL readability. DSN-shaped credentials SHALL NOT evade inspection. Approved runtime delivery copies are the only exception to the prohibition on duplicate plaintext storage.


<a id="section-14-1-2"></a>

#### 14.1.2 Secret-delivery rules

Each consumer SHALL read its owning folder/key mapping:

| Credential | Folder |
|---|---|
| `sales-db-password` | `ao-sales` |
| `fabrication-db-password` | `ao-fabrication` |
| `webodm-postgres-password` | `ao-mapping` |
| `mastodon-db-password` | `ao-mastodon` |
| `payment-db-password`, `payment-paypal-webhook-id`, `payment-paypal-webhook-secret`, `payment-coinbase-webhook-secret` | `ao-payment` |
| `pcloud-webdav-password`, `pcloud-webdav-user` | `ao-archive` |

Every presence probe SHALL include a known-absent folder/entry negative control. An empty folder name or a daemon responding SHALL NOT establish correct folder authority. Mapped keys SHALL be distinguished from successfully provisioned/deliverable entries.

OpenClaw OAuth/client credentials, Cloudflare tunnel JSON and producer signing keys SHALL be handled by their explicit consumers (`fetch-openclaw-mastodon-env.sh`, `fetch-cloudflared-env.sh`, `scripts/ledger/sign-manifest.sh`) without a generic credential grant.

All secret-bearing delivered env files SHALL use `%h/.local/share/ao-secrets/`. `config/platform/monitoring/grafana-admin.env` MAY contain only non-secret settings `GF_SECURITY_ADMIN_USER`, `GF_USERS_ALLOW_SIGN_UP`, `GF_AUTH_ANONYMOUS_ENABLED`, `GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS`; its public readability SHALL NOT be justification for storing an admin password there.

Database initialization and application connection SHALL use the same wallet-authoritative role password. Consumer credential refresh/adoption SHALL precede production acceptance.


<a id="section-14-1-3"></a>

#### 14.1.3 One env file, one wallet entry

The Mastodon application env SHALL have one live delivery path: `~/.local/share/ao-secrets/mastodon.env`, consumed by `EnvironmentFile=` in the Mastodon web/streaming/Sidekiq Quadlets. The wallet authority SHALL be `kdewallet / ao-mastodon / mastodon-env`, with service-specific entries including `mastodon-secret-key-base`, `mastodon-otp-secret`, `mastodon-db-password`.

No unapproved second file copy SHALL be retained or restored into the repository. Wallet-to-file equivalence SHALL be verified without exposing values, and running consumer adoption SHALL be tested separately. Changing the file after container creation SHALL NOT count as credential rotation completion.


<a id="section-14-1-4"></a>

#### 14.1.4 KDE Wallet D-Bus access

| Element | Value |
|---|---|
| Bus name | `org.kde.kwalletd6` (also answers `org.kde.kwalletd`, `org.kde.kwalletd5`) |
| Object path | `/modules/kwalletd6` |
| Interface | `org.kde.KWallet` |
| Wallet in use | `kdewallet` (`wallets()` returns `as 1 "kdewallet"`) |

Signatures for the methods the tooling actually uses:

```
wallets()                      -> as
open(s wallet, x appId, s app)  -> i handle      (-1 = unavailable/locked)
close(i handle, s app, b forget) -> i
readPassword(i, s folder, s key, s app)  -> s
writePassword(i, s folder, s key, s value, s app) -> i
folderList(i handle, s app)     -> as
hasFolder(i, s folder, s app)   -> b
createFolder(i, s folder, s app) -> b
entriesList(i, s folder, s app) -> a{sv}
```


D-Bus calls SHALL use the actual declared argument types/overloads; `open` SHALL carry the `int64` application argument, `isOpen(handle)` SHALL be selected correctly, `folderList(handle, app)` and `entriesList(handle, folder, app)` SHALL not be confused with nonexistent `listFolders` or wrong signatures. Introspection SHALL use `org.freedesktop.DBus.Introspectable`. Returned folders/entries SHALL be deduplicated before counts are reported.

Readiness SHALL wait on usable/unlocked wallet state for the bounded budget, not `busctl ... list` daemon discovery. The user-manager session environment SHALL carry the required `DBUS_SESSION_BUS_ADDRESS`, `DISPLAY`, `WAYLAND_DISPLAY`, `XDG_RUNTIME_DIR` for the approved consumer. Tests SHALL exercise unavailable/locked credential behavior safely; a transient empty file SHALL NOT itself prove complete gate behavior.


<a id="section-14-1-5"></a>

#### 14.1.5 Minting Mastodon API tokens

The local Mastodon bridge SHALL own/reuse Doorkeeper application `openclaw-mastodon-bridge` with:

```text
read:accounts read:notifications write:statuses read:statuses
redirect_uri=urn:ietf:wg:oauth:2.0:oob
confidential=false
expires_in=nil
use_refresh_token=false
wallet_folder=ao-mastodon
wallet_entry=openclaw-bot-access-token
```

The local bot account SHALL be selected as `Account.find_by(username: 'bot', domain: nil)` for the source Mastodon 4.3 model; application owner/resource-owner references SHALL use `bot.user` / `users.id`, not `accounts.id`. A nonexpiring policy SHALL use `expires_in: nil`, not zero-second expiry. Actual token validity SHALL be tested through the authenticated local API, not inferred from an assumed token length.

Mint/revoke operations SHALL require explicit operator approval and remain in the operational runbook, not execute as part of reading this specification. Tokens SHALL be stored in the wallet; transient delivery SHALL be protected and removed, never printed or committed. Revocation/replacement SHALL preserve only the approved app/scopes/consumer authority.


<a id="section-14-1-6"></a>

#### 14.1.6 Specified delivery — env-file delivery via Podman `EnvironmentFile`

Secret storage SHALL remain KDE Wallet; approved delivery SHALL be wallet-materialized env files consumed through Podman `EnvironmentFile=`. The detailed consumer map SHALL be:

| Env file | Produced by | Consumer |
|---|---|---|
| `mastodon-db.env` | `fetch-kwallet-secret.sh … mastodon-db-password` | `ao-mastodon-db` |
| `sales-db.env` | `… sales-db-password` | `ao-sales-db` |
| `webodm.env` | `… webodm-postgres-password` | `ao-webodm-db` |
| `fabrication-db.env` | `… fabrication-db-password` | `ao-fabrication-db` |
| `payment.env` | `… payment-credentials` | `ao-ingress-payment` |
| `reporting-grafana-admin.env` | `… grafana-admin-password` | `ao-grafana` |
| `reporting-grafana-postgres.env` | `fetch-reporting-env.sh grafana` | `ao-grafana`, `ao-status-collect`, `ao-db-security-collect` |
| `reporting-metabase.env` | `fetch-reporting-env.sh metabase` | `ao-metabase` |

In addition, `mastodon.env` SHALL be delivered from `ao-mastodon/mastodon-env` to Mastodon web, streaming, Sidekiq and the authorized repair operation. Inventory SHALL enumerate actual files/consumers rather than use a stale four/nine/fifteen count.

| Permission/lifetime aspect | Required contract |
|---|---|
| Normal env files | `0600`, operator-owned; no unrelated ACL readership |
| Mastodon named-reader exception | If a separate authorized `ao-sales` reader remains explicitly approved, narrow `user:ao-sales:r--`, `group::---`, `other::---` ACL; otherwise use operator-only `0600` under the single-owner model |
| Atomic materialization | Write scoped `.tmp` under `umask 077`, rename atomically, verify mode/ACL; cleanup stranded temp files |
| Main delivery lifetime | May persist between starts as approved delivery copies; SHALL be freshly authorized/refreshed at startup and SHALL NOT bypass the login gate |
| Forbidden generic copy | `%h/.local/share/ao-secrets/legacy-alwayson-folder.env` SHALL NOT be an authorized delivery source |
| Forbidden alternate roots | No fabrication credentials under `~/secrets/`; no tracked credential copy under repository `config/` or `secrets/` |
| Exposure scan | Enumerate consumers and files, including untracked `0600` orphans and password-bearing DSNs; mode checks alone are insufficient |

Removing existing orphan files, changing ACLs, switching to Podman `Secret=`/`POSTGRES_PASSWORD_FILE`, or adopting systemd credentials SHALL require an approved concrete migration. These alternatives SHALL NOT be represented as implemented merely because supported by an image. No absolute tooling limitation from the historical rationale SHALL replace validation of the selected actual runtime.

File-based `_FILE` credentials MAY be used where explicitly verified for the image and populated only after login; any selected mechanism SHALL preserve wallet authority, scope, dependency ordering and fail-closed startup.


<a id="section-14-2"></a>

### 14.2 Credential rotation, revocation and recovery

§14.1.1 requires rotation, revocation, expiration and recovery to be documented before
production use; this subsection is that documentation.
`docs/runbooks/secrets.md` carries a three-line "Rotation" note that describes
per-service-account homes (`alwayson-mapping`) and a manual copy-out step, both superseded by
§13.2 (all services run under the operator's account) and by the wallet-materialised flow.
**This subsection is the procedure; the runbook's summary is the non-authoritative copy.**


<a id="section-14-2-1"></a>

#### 14.2.1 Rotation

Rotation SHALL be an approved coordinated change to the wallet-authoritative value, live credential authority (database/provider), delivered files and every consumer.

| Phase | Required result |
|---|---|
| Preparation | Identify owning folder/key, authority, every consumer, rollback/recovery and approval |
| Authority change | Update database/provider credential and wallet coherently; temporary disagreement SHALL NOT be called complete |
| Redistribution | Re-fetch atomically after login; do not hand-edit env files |
| Consumer adoption | Restart/recreate authorized consumers after refresh; verify actual adopted configuration/credential validity |
| Verification | Authenticated TCP/API test as applicable, non-secret equivalence check and exposure scan |

Changing file mtime, finding a unit active or hashing only the file SHALL NOT prove adoption. Database checks SHALL use the intended TCP authentication path, not a trusted socket that masks password failure. `genenv` SHALL NOT be used as a convenient rotation substitute that regenerates Mastodon identity/session keys or canonical domain. Secrets SHALL never be printed by `podman inspect` or placed in shell arguments/history.


<a id="section-14-2-2"></a>

#### 14.2.2 Revocation

Revocation is credential-specific; there is no single "revoke everything" switch.

- **Wallet entry** — overwrite the entry with a fresh unusable value via
  `kwallet-provision.sh put`, then restart every unit that reads it. The wallet is the system
  of record, so this is the revocation.
- **Mastodon access token** (§14.1.5) — `Doorkeeper::AccessToken.where(application_id: …)
  .update_all(revoked_at: Time.now.utc)` revokes every prior token for the bridge application.
  Store any replacement in KDE Wallet, never a file.
- **Mastodon sessions** — changing `SECRET_KEY_BASE` invalidates every session. Treat it as a
  deliberate operator action, not routine rotation, and warn before doing it.
- **Exposed secret** — revocation is incomplete until the old value is also removed from every
  artefact that ever held it: env files, backups, Git history, logs. Backup snapshots taken
  while the old value was live still contain it (§14.2.4).


<a id="section-14-2-3"></a>

#### 14.2.3 Expiration

No credential on this host has an enforced expiry. Passwords persist until rotated by the
operator. Tokens are the exception and are pinned deliberately: the OpenClaw bridge token is
created with `expires_in: nil`, because Doorkeeper reads `expires_in: 0` as *already expired*
(§14.1.4). **A non-expiring token raises the rotation obligation** — it is a standing item on
the break-glass list in §14.2.5, not a solved one.


<a id="section-14-2-4"></a>

#### 14.2.4 Wallet backup and restore

Credential recovery SHALL be executable after authenticated login and SHALL not depend solely on unrecoverable delivery env files. An approved wallet backup SHALL include all files/metadata needed to decrypt the selected wallet, including the relevant `.kwl` and salt material; restoration SHALL be tested rather than inferred from file presence.

Where no recoverable wallet backup is available, credentials SHALL be re-provisioned/rotated at their actual authority: database role password reset, provider token replacement, approved Mastodon token minting, and wallet entry provisioning. Recovering an old unknown secret SHALL NOT be assumed possible. Corda signing/PKI material SHALL have its own approved recovery policy rather than be casually rotated as a database password.

Recovery instructions SHALL themselves be in repository/backup scope. An unbacked source-section path SHALL NOT be claimed protected merely because a different `config/` path is backed up. Wallet coverage changes SHALL receive approval and sensitivity protection. Neither backup nor recovery SHALL create an unattended pre-login credential path.


<a id="section-14-2-5"></a>

#### 14.2.5 Break-glass order for the operator

Break-glass handling SHALL follow this dependency order without printing secrets or bypassing authorization:

1. Establish authenticated operator session and usable wallet via `isOpen(handle)`, not daemon presence.
2. Verify owning folder/entry through non-secret presence probes with negative controls.
3. Verify that delivery completed atomically after authorized readiness and that consumer adoption occurred after the relevant refresh.
4. Compare wallet/delivery/consumer validity through non-disclosing checks; key-name/file-time checks alone SHALL NOT establish value adoption.
5. Perform approved restart/recreation only after diagnosis and authorization.
6. If exposed/unrecoverable, rotate/re-provision through the actual authority and update all dependents; follow separate signing-key/PKI recovery policy.

The procedure SHALL NOT restore stale plaintext env files, copy secrets between unrelated domains/hosts, insert a compensating tracked `Environment=` secret or widen access to hide delivery failures. Protected units being stopped before login SHALL be expected behavior, not a fault to bypass.


<a id="section-15"></a>

## 15. Sales, Mastodon, OpenClaw, and Local AI


<a id="section-15-1"></a>

### 15.1 Sales Database

`salesdb` SHALL have separate identities:

```text
sales_api_role
sales_migration_role
sales_backup_role
sales_reporting_role
sales_admin_role
```

Its core tables SHALL include:

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

Reporting roles SHALL use the exact view permissions in §6.A.3; schema definitions SHALL remain in the sales init/migration files and be tested on rebuild.


<a id="section-15-1-1"></a>

#### 15.1.1 Three-Form Transaction Bundles

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

The same issued ID SHALL appear in all three forms and in the bundle status. It is
also required in the Corda sale-receipt event and the PostgreSQL contract
projection. Payment validation SHALL distinguish provider validation from funds
settlement, and the receipt SHALL record the three validated evidence references
before operator handoff to ledger-ingest.

Corda tracks the transaction ID, payment/ledger state, hashes, and approved
references. Detailed private data remains in the encrypted PostgreSQL
projection keyed by the same transaction ID; Corda does not store full customer
records, raw emails, payment credentials, or unrestricted evidence.


<a id="section-15-1-2"></a>

#### 15.1.2 Website KIT REQUEST PDF Intake

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
transaction/state reference written back to PostgreSQL. Metabase reports and
Grafana dashboards read the resulting approved projections; neither creates the
sale.

**CONFIRMED SALE PDF OUTPUT.** The same intake path carries the other direction: once a
sale is confirmed and the Corda transaction/state reference exists, the confirmed sale is
emitted as a **PDF** into the intake tree. That PDF is the outward-facing artefact of a
confirmed sale, as opposed to the request PDF, which is an inquiry and never becomes one.
Both are hash-captured into `manifests/`, and the request PDF is preserved in `archive/`
so the two are never confused.


<a id="section-15-2"></a>

### 15.2 Community and AI Controls

Mastodon/community controls:

- Dedicated OAuth registration.
- Minimum necessary scopes.
- External access only through `ao-sales` itself (HTTPS/443) when
  explicitly enabled.
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

Bridge requirements — COMM-04 verification evidence is recorded in
`README-ACTION_ITEMS/status-and-references.md`:

- **Auth.** The wallet-held bot token SHALL pass `verify_credentials` against
  `https://mastodon.300x3.com` with HTTP 200 for `acct=bot`. The token value SHALL never
  be printed — measure its length only.
- **Script identity.** The unit SHALL run `/ALWAYSON/scripts/mastodon/mastodon-openclaw-bridge.py`.
  A copy under `~/.local/bin/` is a byte-identical copy, not a symlink, so editing the
  `/ALWAYSON` copy does not change live behaviour until the unit restarts — the same
  copy-not-symlink trap as Quadlets.
- **Visibility.** Every deployed copy SHALL post with `'visibility': 'public'` and retain
  the `@author` mention prefix, per the operator decision (§15.4.5).
- **Cursor.** Notifications that are not `mention`/`status` types SHALL be ignored without
  rewriting the cursor, and a stale cursor SHALL self-recover with a journal log line.
- **No crash loop.** The unit SHALL stay `active (running)` with no restart loop; a 401
  regression SHALL NOT recur. Verify with `systemctl --user status mastodon-openclaw-bridge`.


<a id="section-15-3"></a>

### 15.3 Local 300X3 Mastodon Deployment

Mastodon 4.3.7 SHALL run in the approved rootless `ao-sales` container stack, publicly federated at `https://mastodon.300x3.com`. `300x3.com` and `www.300x3.com` SHALL remain the static storefront and SHALL NOT route to Mastodon. Operators SHALL use Konqueror and the approved OpenClaw interface.

Architecture requirements:

- `ao-sales` is `Internal=false` and contains the Mastodon database, Redis,
  streaming service, web origin, and Sidekiq. Database, Redis, and streaming are
  not attached to any egress network; they are reached only over `ao-sales`.
- Federation delivery is carried by Sidekiq on `ao-sales` itself over
  HTTPS/443. No database, Redis, or streaming container is attached to any
  egress network.
- Origin web and streaming remain loopback-only: `127.0.0.1:3000` and
  `127.0.0.1:4000`.
- The sole public Mastodon entry is the dedicated Cloudflare Tunnel hostname
  `mastodon.300x3.com`, routed to `127.0.0.1:3000` by
  `cloudflared-alwayson.service`. The storefront hostnames are excluded from
  the Mastodon tunnel and retain the filedn redirect behavior.
- Mastodon identity is `LOCAL_DOMAIN=mastodon.300x3.com`. Accounts, login emails, and the
  `alsoKnownAs` alias are specified in §15.4.2.
- Public actor and WebFinger endpoints SHALL resolve at
  `https://mastodon.300x3.com/actor` and
  `https://mastodon.300x3.com/.well-known/webfinger`.
- The tunnel uses HTTP/2 transport; QUIC is not used. Local and public health checks
  SHALL return HTTP 200.
- **Open registration is closed.** `/api/v1/instance` SHALL report `registrations=false,
  approval_required=false`, with the tested disabled-registration application configuration. No registration approval queue SHALL be used under the closed-registration baseline. Account creation on this instance is an operator
  action performed directly in the admin UI.
- No passwords, OAuth secrets, API keys, tunnel credentials, or access tokens
  are committed to Git or recorded in this README.


<a id="section-15-4"></a>

### 15.4 Federation Publication of the Local 300X3 Instance

**Scope.** Join the fediverse as the 300X3 instance so that public posts from the
local deployment appear on external Mastodon servers, including `mastodon.social`.

Federation is a mutual, inbound-and-outbound protocol: remote servers (including
`mastodon.social`) SHALL reach this instance over the public internet using HTTPS,
and this instance SHALL be able to deliver outbound activity to remote inboxes. Federation
is publicly reachable at `https://mastodon.300x3.com`; the
main storefront remains on the apex/`www` hostnames and is not routed to Mastodon.


<a id="section-15-4-1"></a>

#### 15.4.1 Architecture Requirements

| Area | Required definition |
|---|---|
| Public instance | `mastodon.300x3.com`; handles `user@mastodon.300x3.com` |
| Storefront | `300x3.com` / `www.300x3.com` static filedn redirect; no `/mastodon` subpath |
| TLS | Cloudflare edge termination; HTTPS required |
| Ingress | Dedicated `cloudflared-alwayson.service` route to `127.0.0.1:3000`; storefront excluded |
| Egress | Sidekiq ActivityPub/WebFinger over approved HTTPS/443 on `ao-sales`; no unrestricted provider/database egress |
| Network isolation | No unrelated workload routes; database/Redis/raw origins not publicly exposed |
| Streaming | Local `127.0.0.1:4000`; public approved WSS origin on federation hostname |
| Ownership | `scottw` single rootless Podman store/user manager; no duplicate Mastodon instance/store |
| Credentials | Wallet-backed protected delivery after login, including tunnel and API secrets |
| Registration/moderation | Closed registration; account creation and moderation are operator responsibilities |

Canonical identity SHALL agree across WebFinger, actor JSON, local env, policy/templates, streaming URL and helper scripts. Unapproved canonical-domain drift SHALL be corrected through the approved change process within one business day of detection. Runtime results/measurements SHALL be recorded outside this specification.


<a id="section-15-4-2"></a>

#### 15.4.2 Domain and Mastodon Identity Configuration

`~/.local/share/ao-secrets/mastodon.env` SHALL supply the non-secret identity settings alongside scoped secret delivery:

```text
LOCAL_DOMAIN=mastodon.300x3.com
RAILS_FORCE_SSL=true
LOCAL_HTTPS=true
ALTERNATE_DOMAINS=localhost,localhost:3000,127.0.0.1,127.0.0.1:3000
```

The public API SHALL report closed registration and no approval queue using the application's tested disabled-registration state. WebFinger and actor JSON SHALL resolve through the federation hostname; the storefront SHALL remain separate. Actor URI, inbox/outbox and any approved rename alias SHALL agree; a UI rename SHALL NOT be assumed to update every federated endpoint. Operator identities SHALL use approved `admin`/`bot` accounts with mail endpoints `admin@300x3.com` and `bot@300x3.com`; old aliases SHALL not silently become active canonical routes.


<a id="section-15-4-3"></a>

#### 15.4.3 Edge, TLS, and Network Path

The edge is **Cloudflare Tunnel**, not workstation nginx with Let's Encrypt. Edge TLS is
terminated by Cloudflare and the origin stays loopback-only; there is no second TLS variant
to maintain.

The federation edge path:

```text
Remote fediverse servers
        │ HTTPS 443
        ▼
Cloudflare edge: mastodon.300x3.com
        │ HTTP/2 tunnel (HTTP/2 required)
        ▼
cloudflared-alwayson.service
        │ 127.0.0.1:3000
        ▼
mastodon-web

mastodon-web + mastodon background workers
        │ ao-sales (Sidekiq, HTTPS/443)
        ▼
Remote ActivityPub/WebFinger endpoints
```

The storefront hostnames are not included in this tunnel ingress. Tunnel
credentials remain in protected runtime storage and are never committed.

TLS requirements:

- TLS is mandatory at the edge for all federation traffic; Cloudflare SHALL terminate
  TLS for the tunnel-routed `mastodon.300x3.com` hostname.
- Tunnel credentials and origin certificate are stored 0400 under
  `~/.cloudflared/` and mirrored to KDE Wallet `ao-mastodon`; never in
  Git or this README. Revocation SHALL use the approved tunnel-credential recovery procedure.
- `X-Forwarded-Proto: https` SHALL be supplied by cloudflared so Rails
  generates HTTPS URLs and Secure cookies; instance JSON SHALL report
  `streaming_api: wss://mastodon.300x3.com` — the federation host, never the apex
  `300x3.com` (the static storefront, which is not routed to Mastodon). The public instance SHALL report `streaming_api: wss://mastodon.300x3.com`.

Outbound delivery path:

- Mastodon background workers deliver public activities to remote inboxes over
  HTTPS/443. **Sidekiq is required** and is the component that performs this
  delivery; it runs as `ao-mastodon-sidekiq` on `ao-sales`.
- Egress is `ao-sales` itself (Section 3), which is non-internal solely for this
  purpose, with HTTPS/443 as the only protocol used. No database, Redis, or
  streaming container is attached to any egress network.
- Rate and retry behavior are Mastodon defaults; no relay subscription is
  approved unless explicitly decided.


<a id="section-15-4-4"></a>

#### 15.4.4 Federation Enablement Sequence

**This is the specification of the sequence.** Whether each step is done is status and is
recorded once, in §19.1 (component status ST-13 and ST-14, and the work under COMM). No status is
stated here, because a specification does not carry its own status.

1. Dedicated Cloudflare Tunnel `ao-mastodon-federation` and DNS route for
   `mastodon.300x3.com`; storefront hostnames excluded.
2. Cloudflare redirect rule narrowed to exclude `mastodon.300x3.com`; the static
   storefront redirect unchanged.
3. Mastodon identity set to `LOCAL_DOMAIN=mastodon.300x3.com`; actor, WebFinger, and
   local actor documents SHALL resolve and verify.
4. Community publication carried inside `ao-sales`; database, Redis, and streaming
   remain isolated.
5. Tunnel transport is HTTP/2, not QUIC (stream timeouts); local and public
   health checks SHALL return HTTP 200.
6. `@300x3@mastodon.social` resolved; public followers collection confirms both local
   accounts follow it.
7. Public post fetched; local mention records created; native notification
   processing operating.
8. Verify reverse follows using the remote following collection and local incoming
   relationship tables, then perform a fresh signed ActivityPub round-trip test. The
   round-trip test SHALL post publicly and confirm receipt at the remote inbox before
   the step is complete.
9. Bootstrap discovery: from Konqueror signed in at `https://mastodon.300x3.com`,
   follow at least one account on `mastodon.social`. Remote servers do not index this
   instance until first contact occurs. The storefront host `https://300x3.com` is a
   static site and is **not** routed to Mastodon. Storefront isolation SHALL be verified by
   confirming `https://300x3.com` returns the static site and not Mastodon content.
10. Validate public-post delivery to `mastodon.social` and reply/boost round-trips back
    to the local instance; then submit `300x3.com` to the joinmastodon.org directory
    (operator-authorised). Directory submission SHALL require explicit operator approval
    and SHALL not be performed by an agent session on its own authority.

Step 8 verification SHALL read reverse follows from the remote `following` collection of
`300x3@mastodon.social` and cross-check them against the local `follows` table — never from
local outgoing state alone. A *fresh signed* ActivityPub round-trip posts publicly, so it
requires operator approval before it is run. The sidekiq queues SHALL be
empty, which shows nothing is stuck: `LLEN queue:push_public = 0`, `LLEN queue:pull = 0`,
and `redis-cli KEYS 'queue:*'` SHALL return an empty array.

The operator SHALL perform required browser sign-in/follow steps from Konqueror; a headless script SHALL NOT falsely claim a completed human desktop interaction.

Tunnel stability SHALL be evaluated over a defined observation window with control traffic; one registration snapshot or successful short handshake SHALL NOT establish persistent stability or uniquely identify cause. External tests/public posts and directory submission SHALL require explicit action approval.


<a id="section-15-4-5"></a>

#### 15.4.5 Operational Boundaries After Enablement

- Only `public` visibility federates; `unlisted`, `private`, and
  `direct` do not appear on remote servers' explore pages. The OpenClaw
  draft-by-default and human-approval controls (Sections 11.2.2 and 15.2)
  remain mandatory for all public publication.
- `post.sh` public-post guard remains the script-level approval gate.
- Federated deletion is best-effort: remote servers may retain cached
  copies. Content published under this section SHALL be treated as
  practically irreversible.
- Publication audit logging (immutable, Section 15.2) SHALL include the
  remote-delivery outcome for federated statuses.


<a id="section-15-4-7"></a>

#### 15.4.7 Inbound and Outbound Mail for the 300X3 Domain

Mail for `300x3.com` SHALL either support both required directions or be explicitly declared unsupported; address-based account recovery SHALL NOT be claimed while mail is unavailable.

| Function | Required definition / acceptance |
|---|---|
| Inbound routing | Approved MX/SMTP acceptance path for `300x3.com`; SPF/DMARC and applicable `mail.300x3.com` records consistent with provider |
| Outbound submission | `SMTP_ADDRESS`, `SMTP_DOMAIN` and authorized credentials in wallet-delivered Mastodon env; no secret in DNS/source/public files |
| Recovery | End-to-end password reset/account confirmation for `admin@300x3.com` and `bot@300x3.com`, or explicit unsupported-recovery declaration |
| Verification | MX/TXT/DMARC/mail-host resolution, actual inbound/outbound delivery and applicable local port `25`/`465`/`587` only if a local MTA is approved |

A hosted relay or local MTA SHALL be an explicit operator-selected deployment; a local MTA/public port SHALL NOT be installed unilaterally. MX alone SHALL NOT be counted as outbound submission. Credentials and mail services SHALL obey the login gate.


<a id="section-16"></a>

## 16. Scripts and Operational Standards


<a id="section-16-1"></a>

### 16.1 Scripts Layout

```text
/ALWAYSON/scripts/
├── bootstrap/
│   ├── 00-inventory.sh
│   ├── 01-verify-photogrammetry-mount.sh
│   ├── 02-install-host-dependencies.sh
│   ├── 03-create-operational-layout.sh
│   ├── 04-create-podman-networks.sh
│   ├── ao-bootstrap-privileged.sh
│   └── install-heltec-udev.sh
├── deploy/
│   ├── deploy-quadlet-domain.sh
│   ├── validate-quadlet-domain.sh
│   ├── enable-domain-services.sh
│   ├── rollback-domain.sh
│   ├── ao-podman-bridge.sh
│   └── bootstrap-sales-db.sh
├── validation/
│   ├── check-photogrammetry-mount.sh
│   ├── check-open-ports.sh
│   ├── check-network-isolation.sh
│   ├── check-secrets-exposure.sh
│   ├── check-gpu-runtime.sh
│   ├── check-ledger-ingest.sh
│   ├── check-deployment-conformance.sh
│   ├── check-local-services.js
│   ├── check-logs-journals.sh
│   ├── validate-sale-receipt.sh
│   ├── capture-version-matrix.sh
│   └── check-user-linger.sh
├── mapping/         # imagery intake, deliverable archive, manifest export
├── radio/           # heltec detect, radio-profile validate, LoRa link test
├── simulation/
├── storefront/
├── ledger/
├── backup/          # restic backup + verify; executors named in 16.1.2
├── restore/         # restore tests; executors named in 16.1.2
├── maintenance/
├── mastodon/        # deploy, federation runnerbook helpers, instance actor repair
├── operations/      # wallet bridge, service start helpers, local proxy, collectors
├── ops/             # wallet read/write helpers, kwallet provisioning
├── openclaw/        # chat relay for the ao-sales chat path
├── payment/         # ao-ingress-payment adapter, host relay, reconciliation CLI
├── provision/      # provision.sh, install-vendor-binaries.sh
├── sales/           # sales-domain helpers
├── lib/             # shared shell library (common.sh)
└── sync-lmstudio-readme-preset.sh
```

`mastodon/` holds `repair-instance-actor.rb` and the deploy scripts, `operations/` holds the
KWallet bridge and `start-sales-stack.sh`, `ops/` holds `wallet-read-secret.py` and
`wallet-write-secret.py`, and `lib/common.sh` is sourced by every script in
`scripts/validation/`.

`ops/` and `operations/` are distinct and both current: `ops/` is Python
D-Bus wallet tooling, `operations/` is the bash service layer.

`scripts/build-update/` SHALL also contain `provenance-log.py`, `inventory-full.py`, `refresh-install-log.sh`, `apt_history.py`, `test_generators.py` and the generator package in §16.1.1. Backup/restore executable-to-unit mappings SHALL be defined in §17.1.4, not inferred from directory existence.


<a id="section-16-1-1"></a>

#### 16.1.1 Software-status generator package

`scripts/build-update/provenance-log.py` SHALL be the executable entrypoint for argument parsing and flag wiring over the separated generator package:

| Module | Holds | Why it is separate |
|---|---|---|
| `provenance/common.py` | constants, `run()`, `now_utc()`, `norm()`, `is_complete_digest()`, `load_yaml()` | The three primitives everything else needs. No knowledge of provenance, policy or rendering. |
| `provenance/collector.py` | every function that reads local state, spawns a subprocess or queries upstream | The only module with mutable module-level state (`COLLECTED`, `_CACHE_HITS`, `_CAND_VER`, `_CAND_ID`, `OFFLINE`). Those caches exist because the un-cached form spawned ~230 apt subprocesses per run and stopped completing. |
| `provenance/policy.py` | `EXCLUSIONS`, `NEEDS_APPROVAL`, `PIN_POLICY`, `PLAN_VERBS`, `_argv_is_safe()`, `pin_policy()`, `update_risk()` | The updater allowlist and the **recorded reason** for each entry. Stdlib-only, so the safety property can be read and audited without following an import graph. |
| `provenance/plan.py` | `update_steps()`, `write_update_plan()` | Machine-readable plans: each item is either `eligible` with exact ordered argv steps or `excluded` with the rule that excludes it. No third state, no implicit default. |
| `provenance/render.py` | `HEADERS`, `CSS`, `rows_to_html()`, `rollup_details_md()`, `to_html()` | Presentation. Holds no policy and makes no network call, so a column-order change cannot reach back into collection. |

Required dependency direction:

```text
plan      -> policy, render, common
render    -> collector, policy, common
collector -> common
policy    -> stdlib only
```

`TestProvenancePackageBoundaries` SHALL assert import boundaries. Collection caches SHALL remain owned by `collector`; cross-module mutable state SHALL use writer-owned accessors such as `cache_ttl()`, `set_cache_ttl()` and `set_offline()`, not stale imported scalar bindings.

Package re-export SHALL use an explicit namespace walk preserving required underscore-prefixed compatibility symbols such as `_load_apt_history` and `_argv_is_safe`; plain `import *` SHALL NOT silently omit them. `__all__` SHALL be computed after temporary loop names are removed. Snapshot/rebinding behavior SHALL be pinned by regression tests, not assumed alias semantics. Line-count history SHALL remain in the companion, not become a module-size requirement.


<a id="section-16-1-2"></a>

#### 16.1.2 Quadlet deploy path

**Quadlet units deploy flat.** `~/.config/containers/systemd/` holds copies, not symlinks,
and Quadlet does not read a per-domain subdirectory. A unit placed in
`~/.config/containers/systemd/<domain>/` is silently ignored, so a deploy can appear to
succeed while changing nothing.

`deploy-quadlet-domain.sh`, `rollback-domain.sh`, `validate-quadlet-domain.sh`, and
`enable-domain-services.sh` all target the flat directory. `rollback-domain.sh` removes only
the named files of the requested domain; it SHALL never `rm -r` the directory, because with
a flat layout that would delete every other domain's units.

Confirm what a deployed unit actually resolved to:

```bash
systemctl --user show ao-grafana.service -p SourcePath
```

Editing `quadlet/<domain>/*.container` in the repository changes nothing on the host until it
is deployed; the live unit is a copy.


<a id="section-16-1-3"></a>

#### 16.1.3 SQLite store-state classification

`scripts/operations/collect-system-health.py` SHALL classify each declared SQLite store into `ao_status.sqlite_store.status` with:

```sql
CHECK (status IN ('absent','error','excluded','ok'))
```

| Status | Required meaning | Human intervention |
|---|---|---|
| `absent` | Declared but not installed / does not exist by approved inventory | Not inherently required |
| `ok` | Present and read successfully | Not required |
| `excluded` | Deliberately omitted under recorded approved sensitivity policy | Not inherently required |
| `error` | Present but cannot be statted, opened, parsed or verified | Required |

Views SHALL expose separate `sqlite_stores_absent`, `sqlite_stores_error`, `sqlite_stores_excluded` counters. Python classifier and `config/platform/postgresql/ao-status.sql` backfill SHALL agree. Corruption phrases including `failed`, `not a sqlite file`, `header read failed`, `open failed`, `read failed`, `snapshot failed`, `integrity`, `database disk image is malformed`, and `file is not a database` SHALL NOT classify as deliberate exclusion.

Tests SHALL cover absent, valid, deliberate exclusion, bad header and corrupt inputs; SQL backfill SHALL be idempotent, reject unknown statuses and agree with classifier cases. Missing-installation and unreadable-present cases SHALL remain distinct.


<a id="section-16-2"></a>

### 16.2 Script Standard

Every Bash script SHALL begin with:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'
```

Every script SHALL:

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


<a id="section-16-3"></a>

### 16.3 Logs-Journals

The canonical journal root SHALL be `/ALWAYSON/logs/`; `LOGS-JOURNALS/` SHALL be a pointer only, never an independent writer root. `lib/common.sh` SHALL set `AO_LOG_DIR`; install, operation, audit, backup, restore and container writers SHALL use that root.

| Log class | Required retention |
|---|---|
| `logs/*.log` | Daily rotation; fourteen rotations; no compression |
| `logs/operations/*.log` | 400 days, age-based |
| `logs/backup/*.log` | 400 days, age-based |
| `logs/installation/*.log` | 400 days, age-based |
| `logs/gpu-runtime/*.log` | 400 days, age-based |

Repository rotation source SHALL be `config/host/logrotate-alwayson.conf`; installed policy SHALL be `/etc/logrotate.d/alwayson`. Journald SHALL have effective `/etc/systemd/journald.conf.d/alwayson-journald.conf` values `SystemMaxUse=500M`, `SystemKeepFree=1G`. Configuration existence SHALL NOT substitute for installed/scheduled operation.

`check-logs-journals.sh` SHALL validate required entries and explicit freshness budgets: exit `0` pass, `1` missing, `2` stale. Writer-handle/rotation checks SHALL distinguish an idle log from a detached live writer (§17.5).

| Log / journal | How often it updates | Purpose |
|---|---|---|
| `installation-journal.log` | Appended during every install or change session | The installation journal required by §4.1 rule 11. Writer: `ao_install`. |
| `operations-journal.log` | Appended on every operational change | Deploys, enable/disable, restarts, and validation-script outcomes. Writer: `ao_operation`. |
| `audit.log` | Appended on every audited operation | Immutable audit trail of operational changes and authorization decisions. Writer: `ao_audit`; `ao_audit_secret` redacts credentials. |
| `backup.log` | After every backup run | Repository, snapshot ID, and success/failure. Writer: `ao_backup_run`, called by `scripts/backup/restic-run.sh`. Dry runs are recorded as `DRY-RUN` and are not counted as backup runs. |
| `restore-test.log` | After every restore test | Source backup ID, operator, result, exceptions. Writer: `ao_restore_test`. Restore test entries SHALL be written to the journal after every restore test. The freshness threshold SHALL be a defined cadence, not a placeholder. |
| `gpu-runtime-check.log` | On each GPU runtime validation | Driver/CDI state and whether GPU access was granted to the workload. Writer: `scripts/validation/check-gpu-runtime.sh`. |
| `script-runs.log` | On every script invocation | Which script ran, its arguments, exit code, and dry-run status. Writer: `ao_log`. |
| `mastodon-local-proxy.log` | While the local proxy runs | Local Mastodon proxy activity and errors. |
| `meshchatx.log` | Continuously while MeshChatX runs | Pointer to the MeshChatX application log, which the application writes into its own storage dir. Not a second writer. See this document. |
| `sim-gz-server.log` | While the Gazebo server runs | Headless Gazebo simulation output. SHALL be written by the approved Quadlet. |
| `sim-foxglove-bridge.log` | While the bridge runs | Foxglove bridge output and connection state. |
| `sim-clock-bridge.log` | While the clock bridge runs | Simulation clock bridge output. |
| `web-console.log` | On console operations | Web console operations and their outcomes. |
| `lmstudio-readme-preset.sha256` | On preset change | Checksum of the LM Studio README preset, for drift detection. |
| `gpu-runtime/` | On each validation | Directory of GPU runtime validation captures, one timestamped file per run. |
| `backup/` | After every backup run | Directory of backup run records and repository metadata. |
| `operations/` | On each operational change | Directory of per-operation journals, one file per operation. Mounted into `ao-build-update`; do not relocate. |
| `installation/` | During install sessions | The install-step output log `agent-install.log` referenced by §12.1. Retained as-is. |


All logs SHALL follow §4.2 sensitivity classification and SHALL NOT contain secret values.


<a id="section-16-4"></a>

### 16.4 Document Coordination

`README.md` is **compiled, not hand-edited**. The source of truth is
`agents/COORDINATION (README UPDATES)/`, which holds one folder per section.
Each session edits only its own file, so two sessions can never collide on the
same 4,000-line document.

| Path | Role |
|---|---|
| `agents/COORDINATION (README UPDATES)/MANIFEST.md` | The fixed section order the compiler concatenates in |
| `agents/COORDINATION (README UPDATES)/<nn>-<slug>/section.md` | One README section, beginning with its own `# N. Title` heading |
| `agents/COORDINATION (README UPDATES)/tools/split.py` | `README.md` → the section folders |
| `agents/COORDINATION (README UPDATES)/tools/compile.py` | The section folders → `README.md`; `--check` verifies without writing |

**Rules.**

1. **Edit one file.** A session owns one section folder and changes nothing else.
2. **Never edit `README.md` directly.** Edit the section file, then recompile.
3. **Keep the heading.** Each `section.md` opens with its section heading.
   Renaming a section means renaming its folder *and* its row in `MANIFEST.md`.
4. **Never renumber `19.x` item IDs.** Items are keyed by group prefix (`PLAT`,
   `NET`, `SEC`, `LEDGER`, `PAY`, `COMM`, `FIELD`, `SIM`, `OPS`) precisely so a
   new item cannot collide and adding one never renumbers another. Take the next
   free number in its group.
5. **New work goes in §19.1 only.** It is the single status log; never start a
   parallel list.
7. **Commit only your own section file.** `git add -A` sweeps in other
   sessions' work.

**The two roles.**

| Role | Does |
|---|---|
| Section session | Edits exactly one `section.md`; commits only that file |
| Compiler session | Runs `compile.py`, requires `--check` to report `identical`, then pushes |

**If `--check` reports `DIFFERS`**, someone edited `README.md` directly. Do not overwrite
it — that discards their work. Re-run `split.py` to fold their edit into the section file,
confirm the round trip, and continue. The split/compile recovery SHALL preserve intervening edits and verify the round trip.

The split/compile round trip is byte-exact, so the README can always be trusted to equal the
sum of its parts.

This folder is distinct from `COORDINATION BETWEEN AI/`, which holds session handoff
narrative. That folder is prose; `COORDINATION/` is build input.

---


<a id="section-17"></a>

## 17. Backup, Restore, Monitoring, and Completion Criteria

This section SHALL define backup, recovery, monitoring, retention and acceptance behavior; implementation state SHALL remain in the status tracker.


<a id="section-17-1"></a>

### 17.1 Backup and Restore Policy


<a id="section-17-1-1"></a>

#### 17.1.1 The 3-2-1 target

Maintain **3-2-1**: three copies, on two media types, with one copy off-host or
off-site.

| Copy | Location | Requirement |
|---|---|---|
| Primary | Live system | — |
| Backup | Encrypted restic repository outside the data path | Produce a successful snapshot, verified by hash |
| Off-site | pCloud, as a restic destination | Maintain a second repository, disjoint from the host |


<a id="section-17-1-2"></a>

#### 17.1.2 Placement rules

1. **Keep the local repository off the data's physical device.** A repository that
   shares the data's device is lost with that device and does not count as a copy.
2. **Do not count an off-host archive as the off-site copy unless it carries a
   restore duty.** `ao-egress-archive` carries none (see §11.6) and SHALL NOT be
   counted toward 3-2-1.
3. **Record the device id of every backup path**, and re-verify separation after any
   storage, mount or repository change.

| Path | Role | Requirement |
|---|---|---|
| `/ALWAYSON` | the data | protected |
| `/var/backups/alwayson-restic` | local repository | **SHALL NOT share a device with the data** |
| `/media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS` | off-host repository | SHALL exist, decrypt with the production credential, and verify |
| `/home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS` | replicated cloud copy | SHALL verify |


<a id="section-17-1-3"></a>

#### 17.1.3 Off-site repository requirements

The off-site repository SHALL satisfy all of the following.

1. **Exist as a valid restic repository** and decrypt with the production
   credential (`restic cat config` succeeds).
2. **Hold a snapshot series, not a single snapshot.** A one-snapshot repository
   proves a copy once; it does not prove a copy is maintained. The repository
   SHALL be on a schedule; until a verified restore test exists on that schedule,
   the off-site copy is not yet a completed restore source.
3. **Cover every path class the nightly repository covers** (see §17.4). A
   repository holding only a subset is not a restore source.
4. **Verify** — `restic check` SHALL pass against it.


<a id="section-17-1-4"></a>

#### 17.1.4 Named executors

Every backup and restore action SHALL name its executor. An action with no named
executor is unscheduled, and an unscheduled backup satisfies no objective in this
section. Verify the timer, not the script.

| §17.1 requirement | Executor |
|---|---|
| Nightly snapshot | `scripts/backup/restic-run.sh` on `ao-restic-backup.timer` |
| Host PostgreSQL dumps | `scripts/backup/backup-host-postgres.sh` |
| All-database dump series | `scripts/backup/dump-all-postgres.sh` on the nightly timer |
| Off-host repository snapshot | Explicit approved off-host snapshot executor and timer SHALL be declared; SHALL honor login gating |
| Restore drill | `scripts/restore/restore-restic-drill.sh`; monthly and after backup-format change |
| Repository integrity | `scripts/backup/verify-backup.sh` on `ao-restic-verify.timer` |


| Baseline scheduled action | Declared schedule |
|---|---|
| Database dumps | Nightly 03:00 local time |
| Restic snapshot | Nightly 03:30 local time |
| Restic integrity | Weekly Sunday 04:30 local time, with approved jitter/persistence |
| Restore drill | Monthly and after every backup-format change |

Timers SHALL NOT run protected jobs before authenticated login. Missed-run catch-up SHALL be explicit and measured against the 24-hour RPO; absent login availability SHALL be a coverage/RPO limitation, not authorization for unattended secret access.

##### Required versus scheduled executors

The off-host entry above is a requirement, not a deployment declaration. The supplied record says no off-host snapshot executor/timer is scheduled and assigns that gap to OPS-30. That gap SHALL remain open until approved scheduling, protected post-login behavior, maintained snapshots and recovery evidence exist. Current scheduling evidence is retained in [the companion](README-COMPANION.md#backup-executor-evidence). Neither this table nor the named script's existence SHALL constitute proof of an active schedule.


<a id="section-17-1-5"></a>

#### 17.1.5 Recovery objectives

| Class | RPO requirement | RTO target |
|---|---|---|
| Project data under `/ALWAYSON` | 24 h | 4 h |
| Application databases | 24 h | 2 h |

1. **Treat the RPO column as a requirement and the RTO column as a target.** Only
   the RPO column is checkable against the schedule; the RTO column requires a
   timed drill.
2. **Do not claim an RPO the configuration cannot deliver.** Without WAL or
   continuous archiving, no class achieves an RPO better than the dump interval.
   State the achievable figure.
3. **Never widen a repository's permissions to make a drill pass.** A drill that
   needs broader access is a blocked drill; record the blocker instead
   (README §4.1 rule 3).


<a id="section-17-1-6"></a>

#### 17.1.6 Restore ordering

Restoration SHALL execute in dependency order:

1. Authenticate the operator and establish approved wallet/credential recovery. Protected services SHALL remain gated until their credentials are available.
2. Select the intended restic repository and explicit snapshot ID, record both, and verify repository decryption/integrity. Environment sourcing SHALL occur before any deliberate `RESTIC_REPOSITORY` override; incidental `latest` selection SHALL NOT choose recovery state.
3. Validate the explicit empty scratch target outside `/ALWAYSON`, canonicalizing with `readlink -m` or equivalent and rejecting symlink/path escapes and pre-existing content.
4. Restore required filesystem/configuration/artifacts/database-dump paths into scratch only. Validate hashes and compressed dump integrity before database loading.
5. Recreate required database roles and authorize credential delivery BEFORE loading application databases. Restore host/cluster role dependencies before their databases; credentials SHALL not be assumed contained in a data dump.
6. Load validated plain SQL dumps through `psql` using the explicit approved mapping below. `pg_restore` SHALL be used only for its supported custom/directory formats, not a plain SQL stream.
7. Validate database/application/receipt state and hashes independently of the restored tree, record timed outcome and exceptions, and clean only approved drill fixtures/scratch paths without modifying repository snapshots.

| Dump label | Database | Restore identity |
|---|---|---|
| `metabase` | `metabase` | `metabase_app` |
| `grafana` | `grafana` | `grafana_app` |
| `sales` | `salesdb` | `sales_migration_role` |
| `mastodon` | `mastodon` | Approved `mastodon` restore identity |
| `webodm` | `webodm_dev` | Approved `webodm_app` restore identity for actual container database |

The guard mapping in `scripts/backup/backup-host-postgres.sh` SHALL reconcile with container-specific restore executors and active names. Unknown labels SHALL stop; filename guessing SHALL NOT select a database. `cordadb`, `a_fab` and other authoritative stores SHALL have equally explicit role/database/format mappings before their recovery is accepted. `pg_dump --no-owner --no-privileges` SHALL NOT be assumed to create roles or grants.

Restic restore arguments SHALL include approved paths such as `/ALWAYSON/config`, `/ALWAYSON/artifacts`, `/ALWAYSON/backups/postgres` and the required data classes; a narrow example SHALL NOT replace full §17.4 coverage. Hash verification SHALL use `scripts/restore/verify-hashes-and-receipts.sh` or an equivalent independently tested step.


<a id="section-17-1-7"></a>

#### 17.1.7 The backup journal

1. **Record every snapshot attempt** to `/ALWAYSON/logs/backup.log` with actor,
   script, snapshot id and result. A snapshot with no journal entry is not evidence
   of a backup.
2. **Treat a journal id that does not resolve as a defect, not a stale record.**
   When the journal names a snapshot the repository does not hold, correct the
   journal path or the id; do not leave both standing.
3. **Require the journal to prove an incremental chain.** Successive attempts SHALL record actual snapshot/time/content lineage where supported. Repeated content or identifier alone SHALL NOT be interpreted as failed maintenance without checking the backup tool semantics; expected successful coverage/schedule SHALL be demonstrated.


<a id="section-17-2"></a>

### 17.2 Monitoring


<a id="section-17-2-1"></a>

#### 17.2.1 Component responsibilities

| Component | Responsibility | Isolation requirement |
|---|---|---|
| Prometheus | the security instrument | independent of Grafana and Metabase in both directions |
| Grafana | dashboards and metric presentation | application state in its own database |
| Metabase | operator reports | read-only against every source |

Prometheus SHALL remain an isolated security instrument even if infrastructure is grouped under `ao-admin`. No public or general application query/administration access SHALL be provided. Grafana/Metabase SHALL use independent approved read-only sources, not the protected Prometheus store. Authorized telemetry input, alert delivery and operator maintenance SHALL be explicit purpose-limited interfaces.


Security collection SHALL act outward on approved PostgreSQL/SQLite and service/host telemetry, excluding browser and personal mail/PIM content. Topology SHALL be approved configuration input, not an externally queryable topology authority. Any security-response actuator SHALL have explicit bounded authority; the Prometheus name SHALL NOT be treated as proof of remediation capability. All credential-dependent security collection/monitoring SHALL obey the authenticated-login gate.


<a id="section-17-2-2"></a>

#### 17.2.2 Required metrics

Monitor at minimum:

| Component | Required metrics |
|---|---|
| Host | CPU, RAM, storage health, disk usage, temperature, GPU state, kernel errors |
| Podman/systemd | Unit state, restart loops, health, image digest |


<a id="section-17-2-3"></a>

#### 17.2.3 Alerting rules

1. **Ship every alert rule as a deployed file, not merely a staged one.** A rule
   present in the repository and absent from the deployed unit provides no coverage.
   Edit the repository copy and reinstall; never edit the live unit.
2. **Re-read names and thresholds from the deployed rules before changing them.** Do
   not reconstruct a metric name or a threshold from what a rule appears to be for;
   the deployed `expr:` line is the only authority.
3. **Load rules with a glob that matches the file actually installed.** A
   `rule_files` glob matching nothing is not a Prometheus startup failure, so it
   survives unnoticed. Verify the glob resolves.
4. **Never count an unwired rule as coverage.** A rule whose metric nothing exports
   can never fire, and a rule that can never fire is not alerting. Document it as
   unwired and record the missing collector as outstanding work.
5. **Never raise an alert on an absent metric.** An alert on a metric with no
   exporter either fires forever or never fires, which is worse than an acknowledged
   gap. Record the gap with the named missing exporter.

| Rule | Expression basis | Threshold | For | Severity |
|---|---|---|---|---|
| `AoBackupStale` | `ao_backup_last_success_timestamp_seconds` | `> 93600` | 1 h | warning |
| `AoRestoreTestStale` | `ao_restore_test_last_run_timestamp_seconds` | `> 3024000` | 1 h | warning |
| `AoRepositoryVerifyStale` | `ao_backup_last_verify_timestamp_seconds` | `> 777600` | 1 h | warning |
| `AoMemoryLow` | `MemAvailable / MemTotal` | `< 0.10` | 15 m | warning |
| `AoLoadHigh` | `node_load1 / count(node_cpu_seconds_total{mode="idle"})` | `> 1.5` | 30 m | warning |
| `AoExporterDown` | `up == 0` | any target | 5 m | critical |
| `AoDbSecurityCollectorStale` | textfile collector mtime | `> 900 s` | 30 m | warning |

**Do not exempt the photogrammetry drive from filesystem rules.** It is the WebODM
target volume, so filling it stops mapping. Excluding it because it is large is the
wrong trade.


<a id="section-17-2-4"></a>

#### 17.2.4 Reporting access

1. **Grant reporting read access and deny write access on the same relations.** A
   read-only reporting identity SHALL read a real source successfully *and* be
   refused a write against a relation that demonstrably exists.
2. **Qualify the schema before concluding a view is unreadable.** A reporting
   identity's `search_path` may exclude the schema holding the view, so an
   unqualified query fails with `relation does not exist` while the view is
   perfectly readable.
3. **Never treat `relation does not exist` as evidence about privileges.** Run the
   write test against a relation that exists; a missing relation proves nothing.
4. **Do not infer an unreachable fact from an unread store.** Before reporting a
   divergence between a live artefact and a stored value, establish that something
   reads the stored value. One grep for the entry name, run before the comparison.
5. **Require a negative control for any probe that contradicts a prior measurement.**
   A probe returning the same answer for every input is broken; confirm it returns
   the opposite answer for a known-absent input before believing the positive
   results.


<a id="section-17-3"></a>

### 17.3 Completion Evidence

No installation or deployment agent may claim completion until it produces all of
the following.

1. Host inventory report.
2. Photogrammetry-drive report with mount source, UUID, filesystem, free space,
   ownership and permission validation.
3. Installed package and version matrix.
4. Rootless and/or system Podman/Quadlet verification.
5. GPU driver and container-runtime validation.
6. Podman network list and domain-isolation results.
7. IPv4 and IPv6 firewall and listening-port report.
8. WebODM CPU-only smoke-test result using the dedicated drive.
9. Vehicle-simulation smoke-test result.
10. Fabrication-simulation smoke-test result.
11. Heltec stable serial-device detection and LoRa-link test result.
12. Ledger-ingestion test and Corda receipt result.
13. Sales receipt-manifest test without payment secrets.
14. Backup execution result.
15. At least one isolated restore-test result.
16. A current list of unresolved blockers, open work items, risks and actions
    requiring human approval.


<a id="section-17-4"></a>

### 17.4 Restic path set


<a id="section-17-4-1"></a>

#### 17.4.1 Required coverage

The nightly repository SHALL cover, at minimum:

- `config`
- `artifacts`
- `backups/postgres`
- the `data/` classes `ardupilot`, `corda-install`, `sim-fabrication`, `sales`,
  `mapping`, `field`, `payment`, `ledger`


<a id="section-17-4-2"></a>

#### 17.4.2 Exclusions

1. **Justify every exclusion in writing.** An exclusion with no recorded reason is an
   omission, not a decision.
2. **Never exclude a path because it is large when the excluded data cannot be
   regenerated.** Size is not a reason to lose irreplaceable data.
3. **Enumerate the path set mechanically, not from memory.** Derive it from the
   backup script and the directory listing, and record both the covered and the
   excluded count:

   ```bash
   ls /ALWAYSON/data/ | wc -l
   grep -oE '/ALWAYSON/data/[a-z-]+' scripts/backup/restic-run.sh | sort -u
   ```

   A count asserted from memory goes stale when a directory is added.


<a id="section-17-4-3"></a>

#### 17.4.3 Confidentiality

State the confidentiality consequence of the path set explicitly. `data/ledger` and
`data/payment` carry provenance and transactional records and belong in the path set;
restic repositories SHALL encrypt them and meet the independent-device placement rule in §17.1. Repository password/key security SHALL protect stored ciphertext. **A restored copy
carries exactly the sensitivity of the live copy — restore grants no privilege
drop.**


<a id="section-17-4-4"></a>

#### 17.4.4 Restore-drill contract

`scripts/restore/restore-restic-drill.sh` SHALL implement the §17.1.6 ordering and
enforce the three scratch refusals in §17.1.6 step 2.

1. **Run the drill against the off-host repository**, restoring only into a path
   outside `/ALWAYSON`.
2. **Require the drill's comparison step to be able to fail.** A comparison that
   cannot return a difference is a false pass, and a false pass is worse than a
   failure because it would be filed as evidence. Prove it can fail by running it
   once against data known to have changed.
3. **Resolve the live file independently of the restored tree.** Comparing a restored
   file against another restored file reports every file identical.
4. **Remove the scratch directory and leave the repository unmodified.** After a
   drill the repository SHALL report the same snapshot count as before it.
5. **Never create a probe artefact from pre-existing project data.** Create probe
   fixtures for the test and remove them afterwards.
6. **Do not count a passing manual check as a scheduled control.** Integrity checking
   exists to catch bit rot and truncation, which develop *after* a drill; only a
   scheduled run closes that gap.


<a id="section-17-5"></a>

### 17.5 Log retention and the journal root

§16.3 fixes `/ALWAYSON/logs/` as the single journal root.

1. **Keep one canonical journal root.** A second root anywhere on the host is a
   defect; a subdirectory of the canonical root is not a second root.
2. **Include `logs/` in the restic path set.** A restore that returns without the
   operational history cannot be diagnosed.
3. **Install the logrotate policy from the repository copy**, never by editing the
   deployed file, and keep the deployed file byte-identical to the repository copy.
4. **State a retention budget for every log class**, and record any class whose
   budget is unmet.
5. **Retain the per-operation subdirectories far longer than the top-level logs.**
   They hold audit evidence §16.3 exists to keep; truncating or compressing them
   destroys it. Apply a single flat age budget to them rather than the
   rotation-count budget used for top-level files.
6. **Omit compression from the policy.** It is the only step that reads whole files,
   and the daily pass is cheap without it.
7. **Confirm rotation works unattended.** A rotation demonstrated only by a forced or
   hand-invoked run proves nothing about the scheduled path. Verify from the journal
   that a rotation occurred with no privileged invocation in the window.
8. **Attribute a rotated file only to a rotator proven to have produced it.** A file
   count cannot establish which rotator created a given file; a rotated file whose
   mtime predates the policy was produced by an earlier mechanism.
9. **Validate staleness against a held write handle, not against mtime.** Confirm per
   log that a live process holds a write handle on the path being checked, using
   `fuser` or `lsof`. An mtime-only check reports a recreated live file as fresh while
   its writer stays attached to the rotated inode, and that writer's output is
   discarded at the next rotation.
10. **Keep any safety justification in a policy comment true for every writer it
    claims to cover.** A comment verified against one library and worded as "every
    writer" is a false claim in a file an operator will believe. Verify against all
    writers, including container runtimes that open a log path once at start and
    never reopen it.
11. **Require journald caps to be installed, not merely configured.** A drop-in
    directory that does not exist means nothing was installed, and the shipped
    defaults apply. Verify the directory and the effective values.


<a id="section-17-5-1"></a>

#### 17.5.1 Container logging

For every container that writes to a rotated path, the policy SHALL guarantee the
writer follows the rotation. Either:

- enable `copytruncate` for those files, accepting that it briefly duplicates content
  and briefly races writers; or
- add a `postrotate` that signals the container to reopen its log; or
- move the container to `journald` or `k8s-file` under a path the policy does not
  rotate.

**Choose deliberately and record the choice.** Both active options touch a running
service and require operator approval (README §4.1 rule 6).


<a id="section-17-6"></a>

### 17.6 Backup integrity

1. **Schedule repository integrity checking.** `restic check` is the only control
   that detects a silently corrupted or truncated repository. The 3-2-1 claim in
   §17.1 and every restore-drill result in §17.4 rest on it.
2. **Run it at least weekly.** A one-off manual check is evidence about that moment
   only.
3. **Supply the credential file the verify unit requires.** A verify script whose
   default env path does not exist SHALL fail closed and be reported, not left to exit
   non-zero unnoticed every week.
4. **Verify the deployed unit, not the staged one.** When the deployed unit lags the
   repository copy, the repository is correct and the running system is not.


<!-- Image targets are relative to the repository-root README. -->
[figure-01]: ./assets/WEBSITEMAIN.png
[figure-02]: ./assets/ao-single-topology.png
[figure-03]: ./assets/ao-single-topology-left.png
[figure-04]: ./assets/ao-single-topology-right.png
[figure-05]: ./assets/topology-detail-adapters.png
[figure-06]: ./assets/topology-detail-salechain.png
[figure-07]: ./assets/topology-detail-mapping.png
[figure-08]: ./assets/sim-robot-arm-vehicles.png
[figure-09]: ./assets/sim-shelving-front.png
[figure-10]: ./assets/sim-shelving-rear.png
