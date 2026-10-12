![ALWAYS ON — WEBSITEMAIN](assets/WEBSITEMAIN.png)

# ALWAYS ON

| Field | Value |
|---|---|
| Document | Complete single-file architecture, integration, security, operations, evidence, and active-work report |
| License | CC BY-NC-SA — creativecommons.org |
| Project origin | Building ~2010 · Drone ~2012 · Equipment ~2022 · Linux systems ~2023 |
| **Why** | **A fully autonomous live/work/fabricate area supporting air/land/sea vehicles, and the daily-carry equipment that goes with them. The goal: it literally does everything itself — for any business, and any owner, even when the internet turns off — at the size of a small storage unit, a garage, or a parking space.** |
| Website | https://www.300x3.com |
| Supporting plan | https://archive.org/details/@scott_widmann |
| Created with | Bluebeam and LibreDraw (PDF project plan), Perplexity.ai, Cline.bot |
| Revision | 2026-10-02 — GitHub review pass; see `docs/readme-change-log.md` |
| Current main host | ATX desktop - running Linux Kubuntu |
| Peripheral host | Drone — Raspberry Pi 5 and Autopilot Module, running KaliOS |
| Format rule | Tables and topology diagrams are primary; original detailed commands/evidence are retained in-place below for operational completeness |
| Reading order | **ES.1** is the specification of intended architecture and **ES.2** is the master topology. **Sections 1–16 are specification**: the planned future state, stated once, with no status, history, revision, or decision in them. **Section 17** is the current backup/restore/monitoring and completion criteria. The current status log and references have been split into `README-ACTION_ITEMS/status-and-references.md`; no status, history, revision, or decision appears in the compiled README for those. Where §1–16 and §17 differ, §17 is the current fact and §1–16 is the requirement. Revision history for this document is in `docs/readme-change-log.md`, never in the body. |

## Contents

| Section | Title | Page |
|---|---|---:|
| ES | Executive Summary | 3 |
| ES.1 | Current Architecture Corrections | 3 |
| ES.2 | Master Topology | 4 |
| ES.3 | Detailed System Record | 12 |
| 1 | System Purpose | 13 |
| 2 | Platform Baseline | 14 |
| 3 | High-Level Architecture | 16 |
| 4 | Security, Isolation, and Data Policy | 21 |
| 5 | Network Domains and Controlled External Access | 24 |
| 6 | Component Boundaries, GUI Reporting Tools, and Operator Access | 29 |
| 7 | Public Storefront and Payment Policy | 31 |
| 8 | Mapping and Photogrammetry | 36 |
| 9 | Field and LoRa Architecture | 41 |
| 10 | Simulation Architecture | 43 |
| 11 | Ledger, Provenance, Archive, and IPFS | 48 |
| 12 | Host Installation and Configuration | 54 |
| 13 | Podman Runtime and Quadlet Policy | 57 |
| 14 | Secrets and Service Identity | 60 |
| 15 | Sales, Mastodon, OpenClaw, and Local AI | 63 |
| 16 | Scripts and Operational Standards | 68 |
| 16.4 | Document Coordination | 71 |
| 17 | Backup, Restore, Monitoring, and Completion Criteria | 70 |


## Executive Summary

### ES.1 Current Architecture Corrections

| Subject | Current plan; replaces any contrary older text below |
|---|---|
| Social media | Most closely tied to the **remote fediverse**: public marketing/contact across website chat, email, Mastodon, and approved social channels, with the fediverse chatbot eventually routing into other social media systems. **OpenClaw** is the direct Mastodon publisher; its local output is standardized PDFs for order/follow-up/support/payment workflows, processed into the sales, payment, and ledger records. `ao-sales` connects to the remote fediverse only (§4.3) |
| LM Studio | Fundamental local LLM host for OpenClaw |
| Browser | Konqueror — dedicated browser for automation |
| Automated testing | Testing is being done with Playwright and Chrome (see section 20) |
| RNode client A — PEOPLE-RADIO | **MeshChatX**, which is the coordination system for the ALWAYS ON Reticulum network stack and the LoRa radios. It only needs to speak to the **Reticulum network stack**, and the RNode is its radio. **LoRaWAN for communication only** — the public human side (§9.2.2). **End-to-end encryption** is built into the stack: strong modern encryption by default, ephemeral keys, forward secrecy by default, and no unencrypted links or packets possible |
| RNode client B — DRONE-RADIO | **LoRa mesh RNode for drones only** — the private drone side. Carries a **dedicated RNS-enabled connection** from QGroundControl to the drones over DRONE-RADIO, so local QGC missions reach the QGC session on the Pi5 drone and missions can be **updated midflight** (§9.2.2) |
| Radios | **Wi-Fi** — Wi-Fi/Ethernet from the main desktop reaches the main internet; that desktop manages all DHCP. **2 LoRa radios** — `PEOPLE-RADIO` (915 MHz) = public human chat, `DRONE-RADIO` (917 MHz) = authenticated private drone mission/status traffic (§9.2.2) |
| QGroundControl | Desktop primary mission planning; KaliOS RPi5 fallback/out-of-range mission-update operation; and drone — KaliOS on the Raspberry Pi 5 with the Autopilot Module, running ArduPilot. It holds a **dedicated RNS-enabled connection to the drones over DRONE-RADIO**, and so receives **midflight mission updates** relayed by DRONE-RADIO to the QGC session on the Pi5 drone (§9.2.2) |
| **Email endpoint** | The storefront routes the buyer through the **EMAIL TEMPLATE** (not an inbox); the host reviews every purchase request against that template. Complete → published as a PDF, a **WORK ORDER REQUEST**; incomplete → sent back by email requesting the remaining information (§4.3) |
| Prometheus | Prometheus is for security only. It acts alone and independently, operating on the other systems to ensure security and to address any problems: time-series store, rule evaluation, alerting, and security evidence — **continuously hardened over the life of the system via ad-hoc security AI review** |
| Grafana | Dashboards and metrics only; it reads the databases that already exist and does not write to them |
| Metabase | Reporting only, and it does ad-hoc read-only reporting, so it requires **its own dedicated PostgreSQL application database** to hold its Metabase schema, saved questions, dashboards, and subscriptions. That application database holds Metabase's own state only — it is not a system of record for business data, and it never receives data from the reporting sources. Metabase connects to the other PostgreSQL and MySQL databases, and to local desktop-application SQLite files, as a **read-only** user in order to report on them, and it never writes to them. Ad-hoc reports that become recurring are promoted into stable Grafana dashboards |
| Corda | Blockchain-enabled accounting, ledger, receipt, entitlement, fulfillment, provenance, and approved state-transition system. Built on **Corda 5.2.2** against `cordadb` — one database within the regular host PostgreSQL 18 cluster, with its own roles and backup scope (§11.1) |
| IPFS | **File-transfer verification and, potentially, sales listing on a blockchain** for approved map/imagery and telemetry/product-operational packages. **It is not a backup.** No Corda/ledger/accounting dependency |
| Backup/restore | Local authority + **encrypted restic** (§17.1). Independent of IPFS and Corda. This is the *only* backup |
| Sale transfer | `ao-egress-archive` holds packages **"archived for data transfer and sale"** — a transfer copy, **not** a backup. IPFS first (transfer verification + possible blockchain listing), then encrypted pCloud. **Requires `ao-sales` authorisation** first (§11.6) |
| Secret authority | KDE Wallet; services needing Wallet secrets start after KDE login |
| GPU policy | Priority: desktop/Konqueror → SketchUp/SketchUp Web → active LM Studio/OpenClaw → ROS/Gazebo/SITL → WebODM batch |
| Additive fabrication | Real machines, not simulated cells: **MainsailOS/Moonraker/Klipper operate on each individual 3D printing machine**, each on its own BigTreeTech CB1 / Raspberry Pi; individual CNC machines likewise. These are **real peers**, not children of the simulated domain. `ao-sim-fabrication` **rehearses** the flow for the **kitchen, cooler/freezer/pantry carousel, storage carousel, and their robot-arm boxes** (2 arms in 2 boxes at storage, which organize and manage the additive-manufacturing machines; 2 arms on independent rails at the kitchen, which cook); it runs the kitchen and holds no production data. **The simulation does not manage those robot arms or carousels** — they need the separate future `ao-auto(kitchen,cool,store,fab)-` domain (§10.2) |
| **Real fabrication** | **`ao-fabrication`** is the real (non-simulated) fabrication domain, distinct from `ao-sim-fabrication` in every respect (§3.3.0): it **pulls data into its own database** for industrial engineering and fabrication optimisation — per-machine production data lands in **`a_fab`** (`10.89.12.0/24`, `Internal=true`). **bCNC** may be used on individual CNC machines and their own RPis where necessary — ideally tied to Klipper/MainsailOS |
| Simulation (fabrication) | `ao-sim-fabrication` requires, as baseline capability and not optional extras: **3D world setup** (its own world), **boning** (alignment and datum structure built into that world), **reinforcement learning objects** (the trainable entities for scenario and policy work), and an **HTML portal to operation** — set up and operated from a browser, with no desktop GUI client (§10.2) |
| Simulation (vehicles) | `ao-sim-vehicle` requires the same four baseline capabilities as `ao-sim-fabrication` (§10.1) |
| Home automation | Domoticz/RPi for the usual Domoticz home automation features: HVAC, doors/locks/access, security/alarms, lighting/scenes, cameras, weather, environmental sensing, media, and other typical Domoticz device classes; separate from printers and future building robotics |

### ES.2 Master Topology

This is the **single authoritative diagram of the entire project**. Every other
diagram in this document is a detail view of one part of it and must not contradict
it. Domain names, network names, and paths are abbreviated here and defined in full
in the sections referenced.

![ALWAYS ON — complete topology, landscape](assets/ao-single-topology.png)

![ALWAYS ON — topology, columns 1–3: outside world, adapters, workload domains](assets/ao-single-topology-left.png)

![ALWAYS ON — topology, columns 4–9: stores, field, sales, secrets, what actually happens](assets/ao-single-topology-right.png)

The panels above are the same graphic folded at its seam, for reading at a larger
scale. The seam falls on the gutter immediately left of the green section 4
(Stores and reporting) column, so each numbered column sits wholly within one
panel and none is split across the fold. For a fully zoomable,
resolution-independent view, or to open the two portrait panels side by side, use
the vector and self-contained viewer:

**[Open the live topology viewer](https://filedn.com/l5JNexbL2ipFNaQcAkmV7lQ/%2A%2A%2ACURRENT%2A%2A%2A/site/alwayson-single-topology.html)** — the interactive
diagram, hosted and always current (rebuilt 2026-10-02). This link is stable; it is
replaced in place each time the diagram is rebuilt, so it never changes.

| Artefact | Use it for |
|---|---|
| **[Live topology viewer](https://filedn.com/l5JNexbL2ipFNaQcAkmV7lQ/%2A%2A%2ACURRENT%2A%2A%2A/site/alwayson-single-topology.html)** | **Interactive, zoomable, self-contained HTML (rebuilt 2026-10-02). Hover a card to trace its links, click to pin, use find to jump to a node. Hosted copy at a stable link, so it is the one that stays current** |
| [ao-single-topology.svg](assets/ao-single-topology.svg) | Vector master. Scales to any zoom with no loss; opens in a browser or Inkscape |
| [ao-single-topology.html](assets/ao-single-topology.html) | The same viewer, committed here — works offline, no server needed |
| **[Software status — markdown](docs/software-status.md)** | **Every installed package, image, application and tool, in one table: what is installed, whether it is up to date, what is released, and whether it is pinned.** [PDF](docs/software-status.pdf) for printing and offline reading. Generated, not hand-maintained. Refresh with `sudo ./scripts/build-update/refresh-install-log.sh` |

Every detail view in this document is a zoom of that one master graphic, never a
separate diagram.

**The only public entries.** Nothing reaches an internal service directly. There are exactly four, each purpose-built and each carrying nothing but its own approved traffic:

| Entry | Network | What it carries | Direction and status |
|---|---|---|---|
| **Storefront** — `300x3.com` / `www.300x3.com`, static HTML in the pCloud Public Folder | pCloud (not a Podman network) | Products, docs, legal, downloads. Also the hosted-checkout origin and the public PDF intake forms. | Outbound publication; static asset delivery |
| **Federation and chat** — `mastodon.300x3.com`, and `chat.300x3.com` (OpenClaw relay / sitebot) | `ao-sales` via the Cloudflare Tunnel | `ao-sales` coordinates social media, email, and Mastodon; the AI bot and chat; and the order-request and receipt workflows. Mastodon web/streaming and OpenClaw chat. Origin stays loopback (`127.0.0.1:3000`, `:4000`, `:18790`). It is the only domain that touches customers directly. | Inbound via `cloudflared-alwayson.service`; outbound federation via Sidekiq on `ao-sales` |
| **`ao-ingress-payment`** | adapter | **Zelle, PayPal, and Coinbase payment verification.** Receives provider webhook/relay events, verifies the signature, and emits a normalized payment event. | Inbound. Deployable once the provider decision is recorded (§7.2) |
| **`ao-egress-archive`** | adapter | **Moving large data and the image/map/telemetry files into IPFS for transfer after sale**, plus encrypted pCloud replication. Destination allowlist, separate credentials, transfer audit. | Outbound. Deployable once archive credentials are provisioned |
| **`ao-html-window`** | adapter | **A public-facing (egress) window for viewing HTML content on the 300x3.com website.** It behaves like the locally hosted iframes in §7.1.2, but it only ever needs to publish to 300x3.com — not to the local loopback readers. It is view-only: it displays HTML and takes no input. Network `10.89.14.0/24`. | Outbound publication to 300x3.com only. Deployable |
| **`ao-build-update`** | adapter | **Software updates.** Image and package acquisition before controlled promotion, with digest capture and update audit. Never attaches to a workload. | Outbound. **Scaffolded — not enabled** (§5.2.1) |

**AO- means "ALWAYS ON".** Every `ao-*` network is one isolation domain. The internal workloads (`ao-payment`, `ao-field`, `ao-mapping`, `ao-sim-vehicle`, `ao-sim-fabrication`, `ao-ledger-ingest`, `ao-ledger-core`, `ao-data`, `ao-admin`, `ao-fabrication`) are all `Internal=true` with no public listener. `ao-sales` is the deliberate exception: it is `Internal=false` so Sidekiq can deliver ActivityPub to remote instances, and it is held to containment by having no attachment or route to any other `ao-*` domain. The adapters above are the other deliberate exceptions.

| Question | Answer |
|---|---|
| Where does money move? | Hosted checkout at the provider → `ao-ingress-payment` → verified event → `ao-payment`/`salesdb` → signed manifest → `ao-ledger-ingest` → Corda. Cards are never handled locally. |
| Where else does a transaction enter? | From the website: email → PDF → Corda processing. A customer email produces a standardized PDF request which is processed into the ledger workflow. |
| Where is the ledger (the only copy)? | `ao-ledger-core` on `cordadb` in PostgreSQL 18, a separate database with its own roles and backup scope. PostgreSQL is authoritative (§11.1). |
| What can the internet never reach? | The internal `ao-*` workload networks. All are `Internal=true` with no public listener. `ao-sales` is non-internal for ActivityPub delivery only, and still publishes no listener of its own. |
| What crosses a domain boundary? | Only a signed, minimized manifest through `ao-ledger-ingest`, under mTLS with authorization, replay defence, idempotency, and audit. |
| Where do secrets come from? | KDE Wallet, after Plasma login, by design. See §14.1.1. |
| What are the database reporting tools and their functions? | Three tools, and **all three are read-only over the databases that already exist — none of them is a system of record, and none of them ever writes to a source database.** **Prometheus** is the security instrument: it acts alone and independently on the other systems to ensure security and to address problems, and it keeps its own time-series store. **Grafana** is for stable dashboards and metrics. **Metabase** is for ad-hoc reporting by users. A recurring ad-hoc Metabase report that proves its worth is promoted into a stable Grafana dashboard. Each keeps its own application database, separate from every source database. See §3.3 and §6.A.2. |

The five points below are the ones most often asked about. Each is drawn in the master
graphic above.

**Two ALWAYS ON loopback listeners.** The Gazebo world portal (`:8765`) and the
ALWAYS ON operator console (`:8099`) **are part of ALWAYS ON** and are drawn as such in the
master topology. They are listed separately only because they are host services rather
than `ao-*` network members:

| ALWAYS ON loopback listener | Process | Status |
|---|---|---|
| `127.0.0.1:8765` | `ao-sim-fabrication-portal.service` | **Gazebo world portal**, view-only HTML, verified 200. Loopback only. Part of operating `ao-sim-fabrication` (§10.2) |
| `127.0.0.1:8081` | `ao-sim-fabrication-foxglove.service` | **Foxglove bridge**, a WebSocket server only — no HTTP, so a browser pointed at it gets no page. Loopback only. Carries the eight camera feeds to the `/viewer` client. Part of operating `ao-sim-fabrication` (§10.2) |
| `127.0.0.1:8099` | `python3` (`web-console-server.py`) | **ALWAYS ON operator console**, verified 200. **Not a deployed service** — no unit or timer starts it, so it is absent unless an operator runs it by hand. Open item in §19.1. See §19.2 |

**Other listeners on this host that are not part of ALWAYS ON.** The isolation
statements above describe `ao-*` infrastructure. A small number of other services
listen here; they are recorded so the exposure picture is exact rather than
overstated:

| Listener | Process | Status |
|---|---|---|
| `0.0.0.0:4242` | ReticulumMeshChat | Documented, part of the mesh tooling |
| `127.0.0.1:8080` | Domoticz web UI | **Loopback-only 2026-09-30** (operator: needs access from this machine only). Started with `-wwwbind 127.0.0.1 -nomdns`. Verified: loopback 200, LAN address refused. Not an `ao-*` service; intended future use is other equipment on the equipment LAN — see §3.3.0.2. |

The Domoticz UI was moved to loopback on 2026-09-30, so the only remaining
non-loopback listeners are ReticulumMeshChat (documented) and `dnsmasq`/`socat`,
which are bound to the equipment LAN the desktop manages. The "no public
listener" claim is therefore true of every `ao-*` service, of the Gazebo portal,
of the operator console, and of Domoticz.

- **The fabrication machines are real machines, not simulation nodes.** MainsailOS,
  Moonraker, Klipper, the individual additive-manufacturing machines (3D printers and
  CNC), and the BigTreeTech CB1 are therefore not drawn as `ao-sim-fabrication`
  children. `ao-sim-fabrication` coordinates all industrial engineering and production
  related details for the rehearsal, and it runs the kitchen. It receives no production
  data: that is handled by the separate
  `ao-fabrication` domain. See ES.1 and §10.2.
- **Post-sale transfer is authorized-recipient only**, with no Corda or archive
  dependency: an approved map/imagery or telemetry package is transferred as
  package · hash · recipient authorization over IPFS (private swarm, pinning,
  encryption). See §11.
- **Secrets come from KDE Wallet**, which is the authority. Plasma login →
  `kwalletd6` unlock → `fetch-kwallet-secret.sh` (`ExecStartPre`, ≤60s) → a 0600 env
  file per unit. Services needing Wallet secrets start after login **by design**. All
  services run under the operator account; there is no separate service user. See
  §14.1.1.
- **Monitoring is split by purpose.** Prometheus is for security only and acts alone
  and independently on the other systems to ensure security and address any problems.
  Grafana is for stable dashboards and metrics. Metabase is for ad-hoc reporting. Each
  keeps its own application database and reads the business databases read-only; none
  of them is the system of record. See §3.3.2 and §17.
- **Prometheus is isolated, and the isolation is a requirement.** Nothing queries
  Prometheus — no dashboard, service or query may read it. Nothing acts
  on it either: no rule, job or component may reconfigure, reload or silence it.
  Configuration is operator action through §16 only. `ao-admin` is
  `Internal=true`, so there is no egress path, and the boundary to hold is
  lateral and local: anything sharing `ao-admin`, and anything able to reach a
  published Prometheus port (OPS-29).
- **The isolation is one-directional: Prometheus acts outward, nothing acts on it.**
  The access it holds is a working capability, not an exposure. Prometheus does
  security work **on the databases of the system — PostgreSQL and SQLite** — and
  on the services and hosts around them. That outward direction is its purpose
  and is required. What is forbidden is the reverse: no database, service,
  dashboard or operator tool may reach *into* Prometheus to read it, reconfigure
  it, feed it, or influence what it does. Access *to* Prometheus is denied;
  access *from* Prometheus is its job.
- **Topology is input to Prometheus, never its output.** Prometheus does not create
  system topology. It must *know* the topology — which networks, units, ports and
  domains exist, and how they relate — in order to enact security policy, so
  topology is read *into* it. That knowledge is never published back out as
  something another system may query or depend on.
- **Radio profiles** are `PEOPLE-RADIO` 915 MHz/125 kHz (public) and `DRONE-RADIO`
  917 MHz/250 kHz (authenticated). See §9.


### ES.3 Detailed System Record — Start of the README

**Architecture, Installation, Configuration, Operations, and Status**

This is the single authoritative document for the ALWAYS ON project. It contains the
intended architecture, implemented configuration, operational requirements, validation
evidence, approved deviations, known issues, and work queue. The remaining tables,
commands, evidence, paths, full interface inventory, operational requirements,
payment/ledger forms, Mastodon details, installation procedures, backup rules, and
service records follow, numbered 1–21. Where an older statement conflicts with ES.1,
ES.1 governs. When the current implementation differs from an architecture
requirement, the difference must be recorded in **Approved Deviations and Open
Decisions** with a rationale, compensating controls, owner, and resolution condition.

**Last consolidated review:** 2026-09-30

> **Operator warning.** Everything here is difficult until it is easy. These tools
> are sharp and dangerous, and if you disrespect them they will can/will harm you —
> the same as any trip, fall, or car ride. Perhaps not as bad, perhaps worse. In my
> opinion, ignoring them is more dangerous than understanding them.

---


# 1. System Purpose

ALWAYS ON is an on-premises platform supporting an automated modular live/fabricate facility
of roughly 160 square feet, and an accompanying micro-aircraft carrier. Both scale in size
and quantity without changing the architecture.

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

**Deployment roles.** The workstation is the development, integration and validation host. It
runs Kubuntu 26.04 LTS on an Intel Core i7-8700K with an NVIDIA GTX 1080. Compute-intensive
production workloads may move to an immersion-cooled server rack and a Raspberry Pi
edge-computing cluster.

Kubuntu is the desktop for four reasons: it is built on Ubuntu LTS with standard security
maintenance to May 2031, giving a predictable maintenance horizon; it carries the ROS 2 and
Gazebo toolchain plus
QGroundControl that the simulation work depends on; KDE Plasma provides the login-gated KDE
Wallet secret flow (§14.1) and Konqueror as the dedicated automation browser; and the KDE
suite covers the desktop and portable hardware this system is built for.

**Container runtime.** Podman is the only supported container runtime. Containers are managed
through systemd Quadlet definitions — never Kubernetes, Docker Compose, a Docker daemon, or
shell-wrapper orchestration (§13).

**Platform identity.** The workstation runs **Ubuntu 26.04 LTS as the base, with KDE Plasma as
the desktop.** Requirements that follow from this, and which the provisioner and any
verification step must be written against:

- The base distribution is Ubuntu 26.04 LTS. The `kubuntu-desktop` metapackage is **not**
  required and must not be assumed installed; only the Kubuntu-flavoured settings packages are
  expected. Verification must not test for `kubuntu-desktop`, `/etc/kubuntu-release`, or any
  `Kubuntu` distributor string — on this platform those correctly read as absent or as
  `Ubuntu`.
- The **KDE Plasma desktop is required**, because the login-gated KDE Wallet secret flow
  (§14.1) and Konqueror as the automation browser depend on it.
- **Support horizon:** standard security maintenance runs to **May 2031**. This is *standard*
  security maintenance, not full support; expanded security maintenance extends to **May 2036**
  under Ubuntu Pro. The 2031 date is therefore when routine maintenance ends, not when the
  release becomes unusable.
- The horizon above is the **Ubuntu LTS base** cycle. Do not substitute a desktop-flavour
  support window for it; flavour cycles are maintained separately and are not covered by the
  base distribution's published dates.

**Toolchain, and how each tool is supplied.** ROS 2 Lyrical is required at `/opt/ros/lyrical`.
Gazebo Sim 10.5.0 is required but runs **containerised**, so `gzserver` must not be expected on
the host `PATH`. QGroundControl is required as an operator tool but **is not a distribution
package**: it is supplied as a user-level AppImage with a `.desktop` launcher under
`~/.local/share/applications`, so neither a `qgroundcontrol` binary on `PATH` nor an entry under
`/usr/share/applications` may be assumed. Any inventory, install list or verification step must
treat AppImage-supplied and locally-built tools as a distinct class from packaged software, and
must not report them as missing merely because no package owns them.

**Why this platform.** The selection rests on: Ubuntu LTS with a published security-maintenance
horizon; the ROS 2 and Gazebo toolchain plus QGroundControl that the simulation work depends on;
KDE Plasma for the Wallet secret flow and Konqueror; and the KDE suite for the desktop and
portable hardware this system is built for.

# 2. Platform Baseline

## 2.1 Intended Platform Standard

| Area | Architecture requirement |
|---|---|
| Host OS | Kubuntu 26.04 LTS workstation; the selection rationale is in §1 |
| Current CPU/GPU | AMD CPU and EVGA NVIDIA GTX 1080 |
| Future compute | Immersion-cooled server rack and Raspberry Pi edge cluster |
| Container engine | Podman only |
| Container lifecycle | systemd and Podman Quadlet |
| Public website | Static HTML in pCloud Public Folder + Cloudflare domain registration |
| Payments | Provider-hosted checkout and verified payment events; no local card handling; local stablecoin processing |
| Sales and support | Sales API, PostgreSQL, Mastodon integration, OpenClaw, and LM Studio |
| Drone compute | Raspberry Pi 5 with Waveshare SX1262-class LoRa top-hat |
| Drone autopilot | 3DR N1 connected to Raspberry Pi 5 by MAVLink |
| Desktop radios | Two Heltec LoRa 32 V3 (SX1262), distinguished by USB port topology as `/dev/ao-drone-radio` (ttyUSB0, DRONE-RADIO 917 MHz) and `/dev/ao-people-radio` (ttyUSB1, PEOPLE-RADIO 915 MHz) |
| Field protocol | RNS/Reticulum and MeshChatX over raw LoRa unless a true LoRaWAN deployment is selected |
| Mapping | WebODM and supporting services under Podman |
| Mapping storage | `/media/scottw/500GBPHOTOGRAM/` |
| Vehicle simulation | ROS 2 Lyrical, Gazebo Sim 10.5.0, ArduPilot SITL, MAVLink, QGroundControl |
| Fabrication simulation | ROS 2 Lyrical, Gazebo Sim 10.5.0, robot cells, additive manufacturing, storage, kitchen, and logistics models |
| Ledger | Corda core behind a dedicated ledger-ingestion gateway |
| Archive | Local source data, signed manifests, encrypted pCloud replication, private or encrypted IPFS workflow |
| Monitoring | Prometheus-compatible metrics, alerts, health checks, and protected administration access |
| Backup | PostgreSQL/Corda-aware backup, restic or equivalent encrypted backup, and scheduled restore testing |

## 2.2 Platform Baseline

The host baseline the platform requires. Every value below is a **requirement**: a rebuilt host
or a verification step is written against this table. Measured values for a running host are
**not** recorded here — they belong in `README-ACTION_ITEMS/status-and-references.md`. Where the
two disagree, the tracker is the fact and the requirement below is what must be corrected.

| Area | Baseline |
|---|---|
| Kernel | Ubuntu LTS kernel |
| Podman | Rootless for every workload (§13.1, §13.2) |
| Podman networks | **Fourteen** `ao-*` networks, all registered in `config/platform/network-cidrs.yaml`, which is the only authoritative list. **Eleven** are `Internal=true`: the ten workload domains `ao-admin`, `ao-data`, `ao-fabrication`, `ao-field`, `ao-ledger-core`, `ao-ledger-ingest`, `ao-mapping`, `ao-payment`, `ao-sim-fabrication`, `ao-sim-vehicle`, plus `ao-html-window`. **Three** are deliberately `Internal=false`: `ao-sales` for ActivityPub delivery, `ao-reporting-egress` for Grafana and Metabase, and `ao-build-update` for software acquisition |
| GPU | EVGA NVIDIA GTX 1080 |
| NVIDIA driver | Pinned, recorded in the version matrix |
| NVIDIA integration | CDI devices registered, including `nvidia.com/gpu=0`. The authoritative spec is `/var/run/cdi/nvidia.yaml`. `/etc/cdi/nvidia.yaml` is not a source of truth and is regenerated or removed at each driver change. Only the authoritative spec contributes devices |
| Simulation stack | ROS 2 Lyrical at `/opt/ros/lyrical`; Gazebo Sim 10.5.0 |
| Host PostgreSQL | PostgreSQL 18, loopback-only |
| Host Redis | Redis 8, loopback-only |

## 2.3 Packages the Verification Steps Depend On

A package is part of the platform baseline if the platform's own verification asserts on it. The
install list itself is written in §12.3; the requirement is stated here because the two must agree.

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
- A check must **not** wrap its subject in `sudo … || true`. On this host `sudo` requires
  interactive authentication, so the pipeline cannot fail and cannot inspect anything — while
  still reporting success.
- Any check whose subject requires privilege must report the privilege failure as a failure. A
  check that cannot fail verifies nothing.

## 2.4 Baseline Verification Must Assert

A verification step **asserts**; it does not print. Each requirement below is normative:

1. Every check must compare an observed value against an expected one and **exit non-zero when
   they differ**. A silent non-zero return that nothing reads is not an assertion.
2. The overall block must exit non-zero if any check fails. A block whose exit status is
   unconditionally zero cannot verify anything, and evidence produced by it cannot be re-run and
   trusted.
3. Each observed value must be **printed beside its expected value**, so a failure is readable
   without re-running the check.
4. A check must run a **control case** before a zero is believed. Counting constructs that return
   a constant regardless of input — for example `systemctl list-unit-files 'pattern' | wc -l`,
   which always prints three lines — must not be used as evidence. Use a form that measures the
   thing itself, such as `grep -c '^ao-'`.
5. Every claim cited as evidence must be **reproducible by the command shown**. A citation that
   does not reproduce is not evidence.

The §12.3 verify block is owned by the OPS-B session; the requirements above are what it must
satisfy.

## 2.5 Version Matrix Requirements

`config/platform/version-matrix.yaml` is the machine-readable platform baseline and must satisfy:

1. **Every running container image is digest-pinned.** A tag-only image cannot be verified as
   deployed. Only these are permitted exceptions, and both are deliberate:
   - `ardupilot-sitl:latest` — a moving SITL tag by design;
   - the locally built Gazebo Sim image, whose digest records the validated local build.
2. **No stray container may duplicate a Quadlet-managed unit.** Any container whose name is
   generated by `podman run` rather than owned by a Quadlet unit is residue and must be removed.
   Removal is a delete and requires operator approval per §4.1 rule 3.
3. **Every digest the matrix records must be a digest a container actually runs**, and every
   running digest must appear in the matrix. A matrix that names a digest nothing runs cannot be
   used to verify what is deployed.
4. **Kernel and package versions must be captured, not hand-transcribed.** The matrix is to be
   produced by a generator that reads the running host, so it cannot silently drift.

# 3. High-Level Architecture

## 3.1 Isolation Detail View

This is a **detail view of the ingress/egress portion of the master topology in
ES.2** and must not contradict it. For the whole project, read ES.2.

![Zoom of the controlled adapter column of the ES.2 master topology, at readable scale. The adapters are the only processes permitted to cross the host boundary.](assets/topology-detail-adapters.png)

*Figure 3.1 — The controlled adapter column of the ES.2 master topology, enlarged. It is a
zoom of that one graphic, not a separate diagram: the adapter column is the only place a
controlled ingress or egress process may exist, and every route into or out of the host passes
through it.*

The public storefront has no direct route to the host's field, mapping, simulation, database,
AI, Podman or Corda-core services.

## 3.2 Where Status Lives

Sections 1–16 hold no status. **Status and outstanding work are both in §19.1**, the only
place either is recorded. **Verification evidence is §19.2.**

## 3.3 Databases and Data Stores

PostgreSQL is the system-wide relational platform. There is **no single shared cluster**:
a host-managed PostgreSQL 18 cluster, loopback-only, carries host administration and the
Grafana and Metabase application databases, and each domain that owns authoritative data
runs **its own dedicated PostgreSQL container** with its own image and its own version.
Every consumer gets a separate logical database and a separate application role inside its
own container. The measured version behind each row is recorded in §3.3.1.

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
| **Grafana** | Stable, curated, long-lived dashboards and metrics — a number that must stay on a wall or in a briefing | Reads approved PostgreSQL datasources read-only. Keeps its own PostgreSQL application database for users, dashboards and datasource configuration |
| **Metabase** | Ad-hoc reporting: a question asked in the browser, saved, filtered, exported. The saved question, not the dashboard, is the unit of work | Reads the other PostgreSQL and MySQL databases **and** local SQLite files over per-source read-only roles — one read-only role per source, so a badly written query cannot modify a source. Keeps its own PostgreSQL application database for its schema, saved questions, dashboards, filters and subscriptions. That database is not a system of record and is never written to by a reporting source |
| **Prometheus** | Security instrumentation only — time-series store, rule evaluation, alerting | Acts alone and independently. Does security work **outward**, on the PostgreSQL and SQLite databases and the services around them; nothing acts on it or reaches into it (§3.3). Not replaced by PostgreSQL, Grafana or Metabase, and does not depend on any of them |

A recurring ad-hoc Metabase report that proves its worth is **promoted into a Grafana
dashboard**, where it becomes stable and curated.

**Redis** is a low-latency speed and coordination layer — caching, queues, locks, task
brokering, transient coordination. It is not the authoritative system of record; business,
payment, user and application metadata stay in PostgreSQL.

**SQLite and H2** are not approved application databases for Grafana or Metabase. They may
exist only where an individual application requires embedded local storage — the browser,
Akonadi, Podman, MeshChatX, QGroundControl — or in retained migration backups.

**Database and ledger authority.**

| Authority | Owns |
|---|---|
| **PostgreSQL** | Detailed operational data, searchable business records, and reporting projections |
| **Corda** | The complete ledger of debits and credits, final sale and contract state, receipt association, entitlement, and approved ledger state transitions |

Where PostgreSQL holds the detailed operational and searchable business record, Corda holds
the authoritative debit and credit position itself.

### 3.3.0 `a_fab` — the real-fabrication database

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

#### 3.3.0.1 How the domain reaches the equipment LAN (host-mediated)

A container on `ao-fabrication` **cannot** reach `10.42.0.0/24` directly, and this is the
isolation model working correctly rather than a defect. `Internal=true` gives the network
no default route and no NAT, so a container sees only its own subnet:

```
container on ao-fabrication:  eth0 10.89.12.3/24
  /proc/net/route            10.89.12.0/24 dev eth0   (no default route)
  connect 10.42.0.1:5432     unreachable
```

Measured on `ao-fabrication-db`, the container that owns `a_fab`. The routing table holds
exactly one route — its own subnet — so there is no default route and no NAT out of the
domain. This is what `Internal=true` means, and it is the isolation model working rather
than a fault.

The host bridge at `10.89.12.1` **is** reachable from inside the domain — its ARP entry
resolves with a complete MAC (`/proc/net/arp`, flags `0x2`), so the gateway answers at
layer 2 even though no route leaves the subnet. That is the path, and the project already
uses the same shape for PostgreSQL: `ao-postgres-reporting-bridge` runs `socat` on the host
and exposes a host service to containers that could not otherwise reach it.

Note on evidence: a TCP connect test to the bridge fails, because nothing listens there
(`ss -ltn` shows no `10.89.12.*` listener). Reachability must be judged from the ARP table,
not from a refused connect.

**Correction 2026-10-05 — the `ao-postgres-reporting-bridge` does not bind a Podman gateway,
and it is not why the reporting containers reach PostgreSQL.** The paragraph above calls this
"the same shape" as the collector path, and §3.3.1 says the host cluster is "Loopback-only;
containers reach it over the reporting bridge (§3.3.0.1)". Both are true only in a narrower
sense than they read, and the specifics matter because they describe an inbound listener.

The bridge is a `socat` on the host, and it binds **`10.42.0.1`** — which is not an ao-admin
gateway at all:

```
$ ss -ltnp | grep 5432
LISTEN 0 5  10.42.0.1:5432  0.0.0.0:*  users:(("socat",pid=5124,fd=5))
$ tr '\0' ' ' < /proc/5124/cmdline
/usr/bin/socat TCP4-LISTEN:5432,bind=10.42.0.1,reuseaddr,fork TCP4:127.0.0.1:5432
$ podman network inspect ao-admin --format '{{range .Subnets}}{{.Gateway}}{{end}}'
10.89.9.1
```

`10.42.0.1` is the host's own address on the **equipment LAN** (`eno1`, §3.3.0), and the
ao-admin gateway is `10.89.9.1`. The unit and script both *say* otherwise, which is how the
error survived:

```
$ head -4 /ALWAYSON/quadlet/operations/ao-postgres-reporting-bridge
# ALWAYS ON - expose the host PostgreSQL loopback listener only on the internal
# ao-admin Podman gateway. PostgreSQL itself remains bound to localhost.
GATEWAY=10.42.0.1
$ systemctl --user cat ao-postgres-reporting-bridge.service | grep -i 'Starts at'
# Starts at login with the reporting containers it serves (ao-admin gateway
# address only exists once those containers' networks are created).
```

The script's own comment and the unit description both name the ao-admin gateway; the code
binds the equipment LAN. **The comment is wrong, not the address.** This is the same class of
error as the mount-flag and label-key traps in §6: a comment asserted a property that was never
measured, and the property was false.

Three consequences, all measured:

1. **It is not an internal-only listener.** `10.42.0.1:5432` is bound to the wired equipment
   LAN, so the host PostgreSQL cluster is reachable by anything that can route to `10.42.0.1`
   — including the real machines on `10.42.0.0/24`. The Wi-Fi address refuses
   (`192.168.87.135:5432` → connection refused), because `socat` binds `10.42.0.1` explicitly
   and not `0.0.0.0`. PostgreSQL itself *is* still loopback-only
   (`listen_addresses = 'localhost'`, `/etc/postgresql/18/main/postgresql.conf:60`), so the
   claim that stops at "PostgreSQL remains bound to localhost" is accurate — but the net
   effect is that the loopback-only cluster is republished onto the equipment LAN, which is a
   security-boundary question belonging to the SEC/NET groups, not one this section can settle.
   **Reported, not remediated** — changing it touches network configuration (stop condition).
2. **`ao-admin` membership is not what makes it reachable.** A container attached only to
   `ao-admin` gets `Network is unreachable`, because that network is `Internal=true` and has no
   default route:

   ```
   $ podman run --rm --network ao-admin … -c '… >/dev/tcp/10.42.0.1/5432 …'
   AO-ADMIN-ONLY-CLOSED      (bash: /dev/tcp/10.42.0.1/5432: Network is unreachable)
   ```

   Both reporting containers reach it because of their *second* attachment,
   `ao-reporting-egress` (`Internal=false`), whose default route NATs out to the host:

   ```
   $ podman inspect ao-grafana --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}={{$v.IPAddress}} gw={{$v.Gateway}}{{"\n"}}{{end}}'
   ao-admin=10.89.9.61 gw=10.89.9.1
   ao-reporting-egress=10.89.10.58 gw=10.89.10.1
   $ podman exec ao-grafana ip route
   default via 10.89.10.1 dev eth1  metric 100
   10.89.9.0/24 dev eth0 scope link  src 10.89.9.61
   10.89.10.0/24 dev eth1 scope link  src 10.89.10.58
   ```

   This is consistent with §3.3.1's own network table: `ao-admin` is `Internal=true`,
   `ao-reporting-egress` is `Internal=false`. The unit description's stated reason for the
   service ("ao-admin gateway address only exists once those containers' networks are
   created") therefore explains a dependency that does not exist.
3. **This is the `10.42.0.1:5432 unreachable` line above, restated.** The §3.3.0.1 code block
   shows `connect 10.42.0.1:5432 unreachable` for a container on `ao-fabrication`, which
   remains correct — `ao-fabrication` is `Internal=true` with no egress network, so nothing
   routes out. The reachability that does exist is specific to the two containers that also
   hold `ao-reporting-egress`, and it is an egress-NAT fact, not an `ao-admin` fact.

### Never assume a mechanism from a name

An earlier revision of this section described the reporting bridge as the
container-to-host-PostgreSQL mechanism and cited §3.3.0.1 for it without checking what
address it bound. The error class is **assuming a mechanism from a name**: "reporting
bridge" + "ao-admin" implied the Podman gateway, and no `ss -ltnp` was run to see the
actual bind address. **The gateway a name claims to expose and the address it exposes
can differ by two subnets and an entire security boundary.**

**Decision (operator, 2026-09-30): the collector runs on the HOST and pushes into
`a_fab`.** The host already reaches the equipment LAN. A host-side collector polls each
machine's Moonraker API, signs the per-machine record, and pushes it into `a_fab` over
the podman bridge. No relay port is opened, and `ao-fabrication` stays `Internal=true`
with no route off its subnet. Opening the domain, or standing up a socat relay to the
printer, were both considered and rejected: the first breaks §5.1 isolation, the second
adds an unnecessary inbound listener for every machine.

**Direction of travel is pull-only.** The collector reads; it never writes to a machine.
Commanding live machinery is a separate authorisation decision and is out of scope for
this path.

**Verified first machine (2026-09-30).** `10.42.0.96` served Mainsail with Moonraker
`klippy_connected: true`, `klippy_state: ready`, and answered
`/printer/objects/query?print_stats` with `print_duration`, `filament_used` and `state`
— i.e. genuine per-machine production data. Note that Moonraker currently serves
**unauthenticated reads**; see §3.3.0 for the open item on API keys.

**Re-checked 2026-10-04: the machine is not currently reachable.** The host's own address on
the equipment LAN answers normally, so the segment is healthy and the absence is at the
machine end, not a network fault:

```
ping 10.42.0.1     2 received, 0% packet loss        (host, equipment LAN up)
ip neigh 10.42.0.96    dev eno1 FAILED               (no ARP resolution)
connect 10.42.0.96:7125  No route to host
```

The 2026-09-30 verification therefore remains valid as a statement about that machine at that
time; it does **not** establish that a collector today would reach anything.

#### 3.3.0.2 Domoticz for non-fabrication equipment

No device is connected, and none is to be connected before the equipment exists. This
records the design so it is not re-derived later.

Domoticz is expected eventually to cover other directly connected equipment on
the same **equipment LAN** (`10.42.0.0/24`) — the segment the desktop already
manages. It is not part of `ao-fabrication`, is not simulation, and does not
write to `a_fab`; per-machine production data stays with the Moonraker collector
above.

**Why the host is the right place, same as the collector.** The desktop holds
`10.42.0.1/24` on `eno1`, so a host process reaches that LAN directly. A
container on an `Internal=true` domain could not (§3.3.0.1). Domoticz running on
the host therefore needs no relay, no opened domain, and no new listener to reach
those devices — the same conclusion already reached for `ao-fabrication-collect`.

**Listener posture: settled (operator, 2026-09-30).** Domoticz only ever needs to be
reachable from this machine, so it was moved to loopback before any device was
attached:

- the web UI is started `-wwwbind 127.0.0.1 -nomdns` and now serves only
  `127.0.0.1:8080`; the LAN address actively refuses
- the shared server on `*:6144` was disabled outright (`RemoteSharedPort = 0`) and
  there is no shared-server listener

Neither change affects reaching devices on `10.42.0.0/24`, which is a host-side
path independent of the web listeners. Verified after the change: loopback
returns 200 and `10.42.0.1:8080` is refused.

`a_fab` holds per-machine production data only. It is **not** a ledger, **not** a sales
record, and **not** a backup target. Anything that must become provable leaves
`ao-fabrication` as a signed fabrication manifest through `ao-ledger-ingest`, exactly as
the simulation domain does.

**Network:** `ao-fabrication`, `Internal=true`, `10.89.12.0/24`, created and registered in
`/ALWAYSON/config/platform/network-cidrs.yaml` (2026-09-30). The subnet is **pinned** in
`/ALWAYSON/quadlet/networks/ao-fabrication.network` because every other network there lets
Podman auto-assign. See §2.2 for the reconciliation of the adjacent
unregistered `10.89.10.0/24` and `10.89.11.0/24`.
**Correction 2026-10-04 — the adjacent-subnet pointer in this subsection was stale.** The
sentence above ends by pointing at §2.2 for "the reconciliation of the adjacent unregistered
`10.89.10.0/24` and `10.89.11.0/24`". Both halves of that were already wrong, and a later
revision corrected neither. Measured:

```
$ grep -nE 'ao-reporting-egress|ao-sales' /ALWAYSON/config/platform/network-cidrs.yaml
14:ao-reporting-egress internal=false subnets=10.89.10.0/24
15:ao-sales internal=false subnets=10.89.0.0/24
$ grep -c '10.89.11' /ALWAYSON/config/platform/network-cidrs.yaml
0
```

- **`10.89.10.0/24` is registered**, as `ao-reporting-egress` (`Internal=false`, deliberately —
  it is the reporting egress path for `ao-grafana` and `ao-metabase`, §6.A.2). It is not
  "adjacent" and not unregistered, and §2.2 lists it among the three deliberately
  `Internal=false` networks.
- **`10.89.11.0/24` is genuinely unallocated** — no match in the registry that §2.2 makes the
  only authority. It is folded into `ao-sales` and is recorded as such in §5, which is where
  the `ao-egress-community` name question now lives. §2.2 contains no reconciliation text at
  all, so pointing there was never useful.

The one surviving open item is the `ao-egress-community` / `10.89.11.0/24` name-versus-CIDR
reconciliation. That is a rename decision belonging to another group, tracked in §19.1; it is
deliberately left alone here.

**The full network inventory, measured 2026-10-04.** Added because the correction above
names "three deliberately `Internal=false` networks" without naming all three, and because a
reader checking the isolation rule should be able to verify all fourteen at once rather than
trust a count. Live state and `config/platform/network-cidrs.yaml` **agree exactly** — all
fourteen names, all fourteen `internal` flags, all fourteen subnets. That is worth stating
explicitly: the registry is not aspirational, it describes what is actually running.

| Network | `Internal` | Subnet | Note |
|---|---|---|---|
| `ao-payment` | true | 10.89.1.0/24 | |
| `ao-field` | true | 10.89.2.0/24 | |
| `ao-mapping` | true | 10.89.3.0/24 | |
| `ao-sim-vehicle` | true | 10.89.4.0/24 | |
| `ao-sim-fabrication` | true | 10.89.5.0/24 | |
| `ao-ledger-ingest` | true | 10.89.6.0/24 | |
| `ao-ledger-core` | true | 10.89.7.0/24 | |
| `ao-data` | true | 10.89.8.0/24 | |
| `ao-admin` | true | 10.89.9.0/24 | |
| `ao-reporting-egress` | **false** | 10.89.10.0/24 | Egress path for `ao-grafana`, `ao-metabase` (§6.A.2) |
| `ao-sales` | **false** | 10.89.0.0/24 | Egress; absorbs the folded `10.89.11.0/24` |
| `ao-fabrication` | true | 10.89.12.0/24 | §3.3.0.1 |
| `ao-build-update` | **false** | 10.89.13.0/24 | Build/pull egress — the third, and the one §3 never named |
| `ao-html-window` | true | 10.89.14.0/24 | |

```
$ for n in $(podman network ls --format '{{.Name}}' | grep '^ao-'); do
    podman network inspect $n --format 'internal={{.Internal}} subnet={{range .Subnets}}{{.Subnet}}{{end}}'; done
  -> internal=true  x11 (payment, field, mapping, sim-vehicle, sim-fabrication,
                       ledger-ingest, ledger-core, data, admin, fabrication, html-window)
  -> internal=false x3  (reporting-egress, sales, build-update)
```

**Read this before reading the isolation rule as absolute.** The project convention is
`Internal=true` for workload networks, and eleven of fourteen honour it. The three
exceptions are all **egress** networks, which must not be `Internal=true` or they could not
reach anything — so this is the rule working, not a violation. But it does mean "all
workload networks are `Internal=true`" is not literally true of everything called a network,
and a security argument that assumes it is would be wrong by three. The `Internal=true`
guarantee that §3.3.0.1 relies on — no default route, no NAT, no way off the subnet — holds
for `ao-fabrication` and the ten others, and **not** for these three.

**Two claims in the first draft of this paragraph were wrong, and the correction is
recorded because it is the kind of claim that survives into someone else's security
argument.** The block was described as "contiguous and gap-free" and `10.42.0.0/24` as
the only non-`ao-` addressing on the host. Neither held:

1. The block is **not** gap-free. Fourth octet counting is misleading here because every
   subnet is `10.89.<n>.0/24`, so the varying octet is the **third**:

```
$ for n in $(podman network ls --format '{{.Name}}' | grep '^ao-'); do
    podman network inspect $n --format '{{range .Subnets}}{{.Subnet}}{{end}}'; done
third octets in use: 0 1 2 3 4 5 6 7 8 9 10 12 13 14
missing in the 0-14 range: [11]
```

`11` is absent, and that is exactly the folded `10.89.11.0/24` this subsection already
discusses. So the one gap in the block is the one known-unallocated subnet — consistent,
not a second problem. There are **no overlaps** and no duplicates, which is the property
that actually matters.
2. The host carries a **third** address family besides `10.42.0.0/24`:

```
$ ip -4 addr show | grep 'inet ' | grep -v 127.0.0.1
inet 10.42.0.1/24       scope global  noprefixroute  eno1
inet 192.168.87.135/24  scope global  dynamic       wlp3s0
inet 169.254.248.253/16 scope link   noprefixroute  eno1
```

`10.42.0.0/24` is the wired equipment LAN on `eno1`; `192.168.87.0/24` is a **Wi-Fi**
network on `wlp3s0`, and the `169.254.0.0/16` link-local is autoconfigured.

**Correction to the correction — the Wi-Fi address is not undocumented.** A preceding
revision stated that §3 describes the host as having only the equipment LAN. Checking that
against the rest of the document rather than only against this section shows it is
false: **the Wi-Fi address appears in at least two other sections.** A negative claim
about what a document contains must be checked across the whole document, not only in
the section making the claim.

```
README.md:2173  | Host address | `192.168.87.135/24` on `wlp3s0` |
README.md:5572  MeshChatX is bound to 0.0.0.0:4242; the host had 192.168.87.135/24 on Wi-Fi
```

So the accurate statement is narrower: the Wi-Fi interface is documented elsewhere and
**absent from §3**, not absent from the README. That is a consistency gap in one section,
not a gap in the project record — a meaningfully different thing, and the difference
matters for whether anyone needs to act. MeshChatX binding `0.0.0.0` while the host holds a
Wi-Fi address looks like a genuine exposure question, but it belongs to the COMM/NET groups
and the pointer is recorded here rather than the question opened.

The substantive point stands unchanged: `Internal=true` constrains a *container's* view, and
nothing in it constrains what the host's own interfaces reach. §3.3.0.1's "no route off the
subnet" is true of a container and false of the host, and that distinction is worth making
explicit regardless of which addresses the host holds.

### 3.3.1 Program-to-Database Map (single consolidated table)

This is the one table of programs and the databases they use. It is the starting
point for discussing reporting and data integration; it is not a list of every
installed package or desktop settings module.

| Database software | Software/program | Database name or store | Current role and reporting value |
|---|---|---|---|
| **PostgreSQL 18** | Host PostgreSQL service | Host cluster `18-main`; `postgres` | Shared relational platform and administrative/maintenance cluster. Also carries the Grafana and Metabase application databases. PostgreSQL itself is loopback-only (`listen_addresses = 'localhost'`), but the host runs `ao-postgres-reporting-bridge`, a `socat` that republishes it on **`10.42.0.1`** — the equipment LAN, not a Podman gateway (§3.3.0.1) |
| **PostgreSQL 17** | Sales database service | Container `ao-sales-db` on `ao-sales`, database `salesdb` | Authoritative source for customers, orders, products, payments, receipts, entitlements, and audit history |
| **PostgreSQL 17** | Mastodon web/background workers | Container `mastodon-db` on `ao-sales`, database `mastodon` | Accounts, posts, media metadata, federation state, and background-job application data |
| **PostgreSQL 17** | Fabrication database service | Container `ao-fabrication-db` on `ao-fabrication`, database `a_fab`, role `fabrication_role` | Per-machine production data pulled from each individual machine (§3.3.0). Separate from `ao-sim-fabrication`, which holds none |
| **PostgreSQL 9.5** | WebODM web/worker | Container `ao-webodm-db` on `ao-mapping`, database `webodm` (host-side data dir `~/webodm/dbdata`) | Mapping projects, processing state, users, and geospatial data. The app reads database `webodm_dev` in that container. **PostGIS is installed in `webodm_dev` (version 2.3.2) but not in `webodm`** — so the only installed extension in `webodm` is `plpgsql`, and the geospatial extension lives in the database the app actually reads. Re-measured 2026-10-04; an earlier revision of this row said PostGIS was absent from *both* databases, which was wrong |
| **PostgreSQL 9.5** | NodeODM | The same `ao-webodm-db` container, plus filesystem processing data | Processing-node state and coordination; large image/output artifacts remain filesystem data |
| **PostgreSQL 18** | Corda 5 node | `cordadb` (dedicated Corda PostgreSQL database in the host cluster, per §11.1) | Receipt, entitlement, and provenance state. Built on Corda 5 against `cordadb`. |
| **Redis 8** | Host Redis service | Host Redis database 0 | General low-latency cache/coordination layer; no current application data confirmed |
| **Redis 7** | Mastodon cache/queue service | Container `mastodon-redis`, database 0 | Cache, queues, and background-job coordination; not authoritative business data |
| **Redis 7** | WebODM broker | Container `ao-webodm-broker`, database `broker` | Celery/task broker and worker coordination; not authoritative mapping data |
| **PostgreSQL 18** | Grafana | Grafana application database (dedicated) | Grafana users, dashboards, and datasource configuration. Its own application state, not business data |
| **PostgreSQL 18** | Metabase | Metabase application database (dedicated) | Metabase application schema, saved questions, dashboards, filters, and subscriptions. Not a system of record and never written to by a reporting source |
| **PostgreSQL / MySQL (read-only)** | Metabase reporting sources | Per-source read-only roles | Ad-hoc read-only reporting connections to the business databases. One read-only role per source, with no write, DDL, or owner privilege, so a report cannot modify a source |
| **Prometheus TSDB** | Prometheus | `/prometheus` persistent volume | Security evidence only. Time-series metrics, service health, resource usage, and security evidence. Acts alone and independently of Grafana and Metabase. |
| **SQLite** | MeshChatX / Reticulum MeshChatX | Per-identity database at `~/.reticulum-meshchatx/identities/<identity>/database.db` | MeshChatX messages, rooms, and local Reticulum/MeshChatX application state. **Correction 2026-10-04:** this row previously gave no path, and an earlier revision implied a single store under `~/.local/share/`. There is none. The real store is **per identity**, keyed by a hashed directory name — measured: one identity present, 18 MB, 44+ tables (`lxmf_messages`, `lxmf_folders`, `contacts`, `announces`, `crawl_tasks`, `rrc_room_keys`, `map_drawings`, `blocked_destinations`). A separate small store holds declarative-performance-observer reports. Note the content state: `lxmf_messages`, `lxmf_folders` and `lxmf_conversation_summaries` all read **0** rows, while `announces` holds 8862 and `crawl_tasks` 3048 — so the store is populated by network announces and crawling, not by message traffic. There is also a Qt performance-observer store and a plugin-state store. |
| **SQLite** | QGroundControl | **No application database exists.** Settings are in an INI file and map tiles in a tile cache | **Correction 2026-10-04:** this row previously claimed a "QGroundControl SQLite store" holding "plans, waypoints, settings, and vehicle/flight-plan state". Measured, that store does not exist. The only SQLite file QGroundControl creates on this host is a **map tile cache** — `~/.cache/QGroundControl/QGroundControl/QGCMapCache/qgcMapCache.db`, tables `Tiles`, `TileSets`, `SetTiles`, `TilesDownload`, holding 16 tiles in 1 tile set. Settings live in `~/.config/QGroundControl/QGroundControl.ini` (a plain INI, currently just `SettingsVersion=9`), not in SQLite. Mission plans are `.plan` **files**, not database rows, and no live plan store was found. What this row describes is the intended design; what exists is a tile cache. |
| **SQLite** | Akonadi/KDE PIM applications | Akonadi SQLite data | Contacts, calendars, mail indexes, and local personal-information data **Not collected by Prometheus** — excluded by operator instruction 2026-10-03: personal and mail-index material is not security telemetry |
| **SQLite** | OpenClaw agents | `~/.openclaw/agents/{main,sitebot}/agent/openclaw-agent.sqlite` | Sales/social AI agent state. **Correction 2026-10-04 — this contradicts the "filesystem/local metadata — social" row below, which classes OpenClaw as files "not automatically part of SQL reporting".** OpenClaw does not hold state only in files: it has two real SQLite databases, measured at 33 MB (main) and 4.4 MB (sitebot), and both are among the **seven stores actually snapshotted and read by Grafana** (§3.3.1.1). The row below should not be read as excluding OpenClaw from SQL reporting |
| **SQLite** | nPerf | `~/.local/share/nPerf/{history,settings,engine}.db` | Run history and settings; two of the three are snapshotted and read by Grafana. Row counts only — settings values are never selected |
| **SQLite** | Elisa | `~/.local/share/elisa/elisaDatabase.db` | Music library; snapshotted and read by Grafana. Counts only — no titles, artists or paths |
| **SQLite** | Klipper | `~/.local/share/klipper/history3.sqlite` | Clipboard history. **Never snapshotted, metadata only, by design** — a snapshot would copy clipboard content (which can include passwords and tokens) into a world-readable file, which README §4.1 rule 5 forbids |
| **SQLite** | libaccounts-glib | `~/.config/libaccounts-glib/accounts.db` | Account identifiers. **Never snapshotted, metadata only**, same reason as Klipper |
| **SQLite** | Firefox, Brave, Chrome, and Edge | Browser profile SQLite stores | Browser history, site storage, caches, certificates, and profile data **Not collected by Prometheus** — excluded by operator instruction 2026-10-03: browsing material is not security telemetry. **Correction 2026-10-04 — measured, and worth knowing which of these are real.** Chrome and Edge each have a populated `Default` profile with SQLite files present. Firefox is installed **as a snap** (`firefox 1:1snap1`) and its real profile is `~/snap/firefox/common/.mozilla/firefox/<id>/places.sqlite` — *not* the `~/.mozilla/firefox/` path the monitoring collector declares, which is absent, so a collector run would report Firefox absent rather than reading it. Brave is also a snap and **has no profile directory at all**, so it is unpopulated rather than excluded. The exclusion decision is unaffected; only the enumeration was wrong. |
| **SQLite** | Podman | Rootless container metadata store | Container, image, network, and volume metadata; not application data BoltDB, not SQLite, so not a Prometheus collector target |
| **Filesystem/local metadata — social** | LM Studio and OpenClaw | Application files, model settings, and local state | Sales/social AI application state that is not automatically part of SQL reporting. **Caveat added 2026-10-04:** this row is accurate for LM Studio but **must not be read to cover OpenClaw's agent databases**, which are real SQLite stores and are snapshotted into Grafana reporting — see the OpenClaw row in §3.3.1 |
| **Filesystem/local metadata — drone/field** | ArduPilot, MeshChatX/Reticulum field stores, and radio gateway logs | Application files, telemetry spools, and local state | Field operational and engineering data that is not automatically part of SQL reporting |
| **Filesystem/local metadata — sim** | Gazebo, ROS 2, ArduPilot SITL, and simulation tools | Project files, worlds, models, and result artifacts | Simulation operational and engineering data that is not automatically part of SQL reporting |

This table records what each database is and which program uses it. Whether a database is
built and provisioned is status, recorded in §19.1 alongside the work to build it.

**Re-verified 2026-10-04 — every version claim in the rows above, measured in one pass.**
The container rows were the ones most likely to drift, because they are read from the
running container rather than from a manifest. All of them still hold:

```
$ for c in ao-sales-db mastodon-db ao-fabrication-db ao-webodm-broker mastodon-redis; do
    printf '%-20s %s\n' "$c" \
      "$(podman exec $c sh -c 'postgres --version 2>/dev/null || redis-server --version 2>/dev/null')"; done
ao-sales-db            postgres (PostgreSQL) 17.11 (Debian 17.11-1.pgdg13+2)
mastodon-db            postgres (PostgreSQL) 17.11 (Debian 17.11-1.pgdg13+2)
ao-fabrication-db      postgres (PostgreSQL) 17.11 (Debian 17.11-1.pgdg13+2)
ao-webodm-broker       Redis server v=7.4.11
mastodon-redis         Redis server v=7.4.11
$ podman exec ao-webodm-db psql -U postgres -tAc 'select version();'
PostgreSQL 9.5.25 on x86_64-pc-linux-gnu
$ psql --version; redis-cli --version
psql (PostgreSQL) 18.6 (Ubuntu 18.6-0ubuntu0.26.04.1)
redis-cli 8.0.5
```

So **PostgreSQL 17.11** for the three domain databases, **9.5.25** for WebODM/NodeODM,
**18.6** for the host cluster that also carries Grafana and Metabase, **Redis 7.4.11** in
the two containerised Redis services and **8.0.5** on the host — matching §3.3.1 exactly.
The host-cluster figure is now corroborated three independent ways: `psql --version`
locally, Metabase's own startup banner, and Grafana's `dbtype=postgres` connect log
(§6.A.3.1), rather than being inferred from `/etc/postgresql/` alone.

The PostGIS split in the WebODM row is also confirmed the same day, and it is the one row
where the difference between the two databases is the whole point:

```
$ podman exec ao-webodm-db psql -U postgres -d webodm_dev -tAc "select extname,extversion from pg_extension where extname='postgis';"
postgis|2.3.2
$ podman exec ao-webodm-db psql -U postgres -d webodm -tAc "select extname,extversion from pg_extension;"
plpgsql|1.0
```

PostGIS is in `webodm_dev` — the database the app actually reads — and absent from
`webodm`. Two things that were previously asserted without a command are now measured at
the same time: the host-side data dir is `~/webodm/dbdata`, and the host Redis holds no
application data (`redis-cli dbsize` → `0`, `redis_version:8.0.5`), which is what the
"no current application data confirmed" wording in the Redis 8 row above actually means.

#### 3.3.1.1 How SQLite stores reach reporting (measured 2026-10-04)

**Added because §3.3.1 listed the SQLite stores but never said how any of them reach
reporting, and a reader could reasonably conclude none of them do.** Seven of them do,
through a snapshot mechanism that has two properties worth knowing: Grafana **never opens
a live SQLite store**, and the whole path is credential-free.

```
source SQLite  --(VACUUM INTO, source opened mode=ro)-->  snapshot dir
   -> bind-mounted read-only into ao-grafana at /var/lib/ao-sqlite
   -> read by Grafana through the frser-sqlite-datasource plugin
```

Measured:

```
$ ls -la /ALWAYSON/data/monitoring/sqlite-snapshots/
-rw-r--r-- 139264   Oct  4 15:10  db-elisa.db
-rw-r--r-- 2916352  Oct  4 15:10  db-nperf-history.db
-rw-r--r-- 12288    Oct  4 15:10  db-nperf-settings.db
-rw-r--r-- 33259520 Oct  4 15:10  db-openclaw-agent-main.db
-rw-r--r-- 4411392  Oct  4 15:10  db-openclaw-agent-sitebot.db
-rw-r--r-- 532480   Oct  4 15:10  db-podman.db
-rw-r--r-- 32768    Oct  4 15:10  db-reticulum-meshchatx-observer.db

$ podman inspect ao-grafana --format '{{range .Mounts}}{{.Source}} -> {{.Destination}} rw={{.RW}}{{"\n"}}{{end}}'
/ALWAYSON/data/monitoring/sqlite-snapshots -> /var/lib/ao-sqlite rw=false
```

**Why snapshots at all rather than a read-only bind mount of the live stores.** Two
measured reasons, both recorded in the collector: SQLite must write the `-shm` index to
read a WAL-mode database, so a WAL store *cannot* be read through a read-only mount at
all; and `VACUUM INTO` produces a delete-mode file that opens cleanly read-only. The
`immutable=1` workaround was rejected because it ignores the `-wal` file and would have
Grafana reporting stale data while appearing healthy. The consequences are deliberate and
should be read as design, not limitation: no ACL change is applied to any personal store,
Grafana cannot write to or corrupt a live store, and **panel data can lag the live store by
up to one collector interval** — the snapshot age is displayed on the dashboard for exactly
this reason.

**No credentials exist anywhere on this path.** The datasources set only a `path`; there is
no user, password, or any other credential, and none may be added, because SQLite has no
authentication mechanism. Access control is entirely the file mode (`0644`) plus the
read-only mount. That is a real property of SQLite, not an oversight — it also means there
is nothing to protect here beyond filesystem permissions.

**Three stores are deliberately metadata-only and never snapshotted**, because a snapshot
would copy credential-bearing content into a world-readable file (README §4.1 rule 5):
Klipper clipboard history, libaccounts-glib accounts, and — by operator instruction of
2026-10-03 — all mail (Akonadi) and browser stores. Mail and browser material is reported
as present/absent in PostgreSQL but is never snapshotted, never mounted, and never
readable from Grafana. This is the enforcement point behind the "Not collected by
Prometheus" notes in §3.3.1.

**One datasource per snapshot, deliberately.** The `frser-sqlite-datasource` plugin executes
every query against the single `jsonData.path` and treats `jsonData.databases` only as a
picker for its query editor UI. With one datasource carrying several paths, every panel
silently answered from whichever store was in `path` — the measured symptom was the Elisa
panel reporting Podman's container count. Per-snapshot datasources are the only way for a
panel to address the store it names.

**Two boundaries on what crosses.** First, Prometheus does not scrape SQLite at all: its
only jobs are `prometheus` (itself) and `ao-node-exporter`. The SQLite evidence reaches
`ao_status` in PostgreSQL through the collector's own projection, not through Prometheus.
Second, the collector selects **row counts only** — no message bodies, no track titles, no
settings values, no prompt or response payloads, and no browser or mail content ever.

**Not mine to reconcile.** The collector (`scripts/operations/collect-system-health.py`) is
an OPS-group file, so two measured gaps are reported rather than fixed: the declared
MeshChatX and QGroundControl paths do not match where those applications actually keep
their data (§3.3.1), and the declared Firefox path is pre-snap while the snap install
stores the profile elsewhere. In both cases the collector reports the store absent, which is
conservative — it reads nothing it should not — but it means those stores are not actually
covered by the inventory this subsection describes.

### 3.3.2 Data Flow into Reporting and Ledger Records

Corda is not a replacement for the source PostgreSQL databases. The intended
ledger flow is:

The sale chain on the right of the following extract — customer picks to checkout,
verified payment event, salesdb record, signed receipt manifest, and Corda state —
is the same five-step chain drawn in ES.2. Payment intake is shown at the left,
through `ao-ingress-payment` and into `ao-sales`; the reporting projections
(Metabase, Grafana) and the Corda entry are shown in their columns.

![Zoom of the five-step sale chain column of the ES.2 master topology, at readable scale.](assets/topology-detail-salechain.png)

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
reports and receipts where appropriate. Before enabling blockchain-related
flows, complete the Corda key/certificate ceremony and implement the
ledger-ingest manifest, correlation-ID, signature, idempotency, and audit
requirements.

---

# 4. Security, Isolation, and Data Policy

## 4.1 Non-Negotiable Rules

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

## 4.2 Data Classification

| Classification | Examples | Handling requirement |
|---|---|---|
| **Public** | Anything in the pCloud Public Folder, or linked in from it: storefront HTML, intentionally published documentation, approved product data | May be placed in pCloud Public Folder |
| **Internal operational** | The databases — PostgreSQL and SQL — plus non-sensitive configuration, health data, non-sensitive manifests, unit status | Restricted local access; do not publish by default |
| **Sensitive** | Corda blockchain secured data and the accounting ledger, plus customer contact data, payment references, precise telemetry, sensitive imagery, proprietary technical designs | Domain-restricted storage; encrypted backup; no public IPFS |
| **Secret** | Passwords, held in KDE Wallet | KDE Wallet only; delivered to services after Plasma login by design (§14.1.1) |

## 4.3 Prohibited Paths

No component may take any of the following paths. Each prohibition is enforced by the rule
named in the last column; the rule text is in §4.1.

### 4.3.1 Named source-to-target prohibitions

This is the original §4.3 list, recovered verbatim from the superseded v6 archive
(`README - ARCHIVE/ALWAYS ON — Architecture, Operations, and Status - v6.md`,
"## 4.3 Prohibited Paths", added in `b3d35e7`). It states the prohibitions as
concrete source → target pairs, which the rebuilt table below cannot: a rule such
as "one component to a second domain network" says why, not *which* pairs are
named. Both are kept, because the pairs are what an operator checks against a
running host.

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

Two entries in this list have been superseded by later operator decisions and are
marked rather than silently deleted, because deleting them would hide a decision:

- *Field → payment provider* and *Mapping → payment provider* are superseded in
  that payment is now reached through the controlled `ao-ingress-payment` /
  `ao-egress-archive` adapters (§5.2), never directly from a workload network.
  The prohibition still holds in substance: no `ao-field` or `ao-mapping` container
  holds a payment credential.
- *Fabrication simulation → live machinery **during phase one***: the phase-one
  qualifier is historical. The prohibition is absolute in the current design
  (§4.3.2, first row; §10.2).

### 4.3.2 Prohibitions by rule

The rebuilt list, retained because each row names the enforcing rule.

| Prohibited path | Why | Rule |
|---|---|---|
| Simulation domain to live machinery | A rehearsal must never command a real machine, a real robot arm, or a live flight controller | Rule 12, §10.2 |
| Any workload network to the public internet | Public reach exists only through a controlled adapter | Rules 6, §5.2 |
| One component to a second domain network | A service joins exactly one network; a second requires an explicitly approved path | §5.1 |
| Cross-domain traffic without mTLS, a dedicated identity, and a signed payload where provenance matters | Provenance is meaningless if any hop is anonymous | §4.4 |
| Any secret material outside KDE Wallet | Passwords, tokens and keys exist in the wallet only | Rules 7, 4.2 |
| Sensitive or accounting data to public IPFS, or to the pCloud Public Folder | These are not publishable data classes | Rule 7, §4.2 |
| A storefront or public page to any internal service | The public site carries no internal host, port, or path | Rule 6, §7.1 |
| A reporting tool to write into a source database | Grafana and Metabase are read-only over their sources | §3.3, §6.A.2 |
| A wider privilege, mount, or secret to make an error go away | Least privilege is not negotiable to clear a fault | Rules 13, 6.A.3 |
| An adapter to a workload, or a workload to an adapter | The adapter boundary is one-way and holds its own credentials | §5.2 |

### 4.3.3 What was lost, and where it went

The body of this section was at one point overwritten with a duplicate of the
sale-chain diagram. That misplaced content was not lost — it belongs to the sale
chain and is now carried once, in §3.3.2, which holds the sale-chain figure and
the catalogue-to-Corda narrative. The prohibition list itself was lost with it and
is restored above as §4.3.1.

The list above is recovered from the archived v6 document, which is the
operator-approved original named as this document's own ancestor
(`config/platform/topology-model.yaml` records `authority: "... v6.md"`). It has
**not** been independently re-approved by the operator in its current form; §4.3.1
records where two entries were superseded and by what. Confirmation of the
recovered list as the operator-approved original is the one item in this section
that needs a human decision.

**Independent verification 2026-10-05.** A later NET session re-checked the
transcription mechanically, not by eye: it extracted the `## 4.3 Prohibited Paths`
block from the archived v6 document and the `text` block in §4.3.1 with a Python
regex, dropped blank lines, and diffed the two. Nine content lines in, nine out,
zero differences — the list is a byte-exact copy, not a paraphrase. Both
superseded-entry marks were checked in place: the *Fabrication simulation → live
machinery* entry is stated absolutely in §4.3.2, and the *Field/Mapping → payment
provider* entries remain in the list and are marked. Whatever the operator
decides, the transcription itself is proven accurate.

## 4.4 Approved Internal Paths

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

## 5.1 Combined Domain, Adapter, Component, and GUI Matrix

The single table for network domains, controlled adapters, component boundaries, and GUI
attachment. A component's domain, inputs, outputs, data and exposure are read from one row.
Gray bars separate the four groups: **A** workload domains, **B** controlled ingress and
egress adapters, **C** component boundaries, **D** GUI and workflow attachment. Status is not
stated here — it is in §19.1.

**Rules that govern every row.**

- **One network per component.** Each service and each GUI or workflow is attached to exactly
  one owning `ao-*` network and is denied all the others. The denied set is the complement of
  the owning network, so it is not repeated per row. A second network is permitted only where
  the approved access path says so explicitly, never as a broad membership.
- **An associated domain is not a grant.** Naming the workflow a tool serves confers no
  Podman-network membership, database access, host access, shared storage, shared
  credentials, or cross-domain control.
- **Host applications have no attachment.** A desktop application, browser or external
  provider dashboard has no Podman network attachment unless it is itself containerized on
  that network.
- **`ao-admin` is the administration plane.** It hosts Grafana, Metabase and narrowly
  authorised administration tools. It is not a shared universal network. `ao-data` is narrow
  controlled data plumbing, not a default GUI, shared-database or reporting network.
- **External connectivity exists only through group B.** These adapters are architecture-
  controlled exceptions, not general-purpose internet access. No sales, mapping, field,
  simulation, database, AI or ledger-core container may attach to an internet-capable network.
  An adapter must use separate credentials, a destination allowlist, validated DNS/TLS,
  firewall policy, minimal permissions and connection logging.
- **No workload service gets unrestricted internet by joining its application network.**

CIDRs and the `Internal` flag for every network are in
`/ALWAYSON/config/platform/network-cidrs.yaml`, which is the only authority (§2.2).
That registry is hand-maintained and read by the validation script, never
regenerated by it. Community publication and federation are carried inside
`ao-sales`; there is no separate community egress network, and the retired
`ao-egress-community` / `10.89.11.0/24` allocation is deliberately left unallocated
(§5.1.1).

<table>
<thead>
<tr>
<th align="left">Item</th>
<th align="left">Owning domain / network</th>
<th align="left">Purpose, inputs accepted, or approved access path</th>
<th align="left">Outputs allowed / permitted output</th>
<th align="left">Persistent data</th>
<th align="left">External connectivity / public exposure</th>
</tr>
</thead>
<tbody>

<tr><td colspan="6" style="background-color:#c9ccd1; border-top:2px solid #8a8f98; border-bottom:1px solid #8a8f98; padding:5px 8px; font-weight:bold; letter-spacing:0.04em;">A · WORKLOAD DOMAINS — every row is an <code>Internal=true</code> Podman network except <code>ao-sales</code>; CIDRs in <code>/ALWAYSON/config/platform/network-cidrs.yaml</code></td></tr>
<tr><td><code>ao-sales</code></td><td><code>ao-sales</code></td><td>Coordinates social media, email, and Mastodon; the AI bot and chat (OpenClaw/LM Studio); and the order-request and receipt workflows, including the public PDF intake forms and PDF output. The only domain that touches customers directly.</td><td>Signed order, receipt, and entitlement manifests; standardized PDF intake and PDF output; published federation and chat posts</td><td>Sales PostgreSQL</td><td>The public PDF intake forms are the exposure point; Mastodon/chat arrive via the Cloudflare Tunnel to loopback origins</td></tr>
<tr><td><code>ao-payment</code></td><td><code>ao-payment</code></td><td>Provider webhook verifier and payment adapter</td><td>Verified normalized payment state</td><td>Minimal event and audit record</td><td>No direct public exposure</td></tr>
<tr><td><code>ao-field</code></td><td><code>ao-field</code></td><td>Heltec gateway, RNS/MeshChatX, telemetry spool, mission-release service</td><td>Signed telemetry and mission manifests</td><td>Raw packet store and telemetry spool</td><td>No direct public exposure; USB serial and radio only</td></tr>
<tr><td><code>ao-mapping</code></td><td><code>ao-mapping</code></td><td>WebODM, NodeODM, Redis, mapping DB, imagery intake/exporter</td><td>Signed mapping deliverable manifests</td><td>Dedicated photogrammetry volume</td><td><strong>No direct operator/VPN access.</strong> Input is 100% by drone and automated WebODM processing</td></tr>
<tr><td><code>ao-sim-vehicle</code></td><td><code>ao-sim-vehicle</code></td><td>ROS 2, Gazebo, ArduPilot SITL, MAVLink, QGroundControl simulation</td><td>Signed vehicle-simulation manifests</td><td>Vehicle simulation data path</td><td>No direct public exposure</td></tr>
<tr><td><code>ao-sim-fabrication</code></td><td><code>ao-sim-fabrication</code></td><td>ROS 2, Gazebo; <strong>rehearses</strong> the industrial engineering and production flow and runs the kitchen. <strong>Holds no production data and never commands live machinery</strong> — real machines belong to <code>ao-fabrication</code> (§3.3.0)</td><td>Signed fabrication-simulation manifests</td><td>Fabrication simulation data path</td><td>No direct public exposure</td></tr>
<tr><td><code>ao-fabrication</code></td><td><code>ao-fabrication</code> (<code>10.89.12.0/24</code>)</td><td><strong>Real (non-simulated) fabrication.</strong> Pulls per-machine production data from each individual 3D printer and CNC machine &mdash; each running its own MainsailOS / Moonraker / Klipper on its own BigTreeTech CB1 / Raspberry Pi &mdash; <strong>into its own database</strong> (<code>a_fab</code>, §3.3.0) for industrial engineering and fabrication optimisation work. Local switch connects the equipment; the desktop manages all DHCP. Does not command machines through the simulator.</td><td>Signed fabrication manifest toward <code>ao-ledger-ingest</code>; fabrication optimisation reports</td><td>Per-machine production data in <code>a_fab</code></td><td>No direct public exposure. Real machines are reached only over the local equipment switch; they are peers, not children of <code>ao-sim-fabrication</code>.</td></tr>
<tr><td><code>ao-ledger-ingest</code></td><td><code>ao-ledger-ingest</code></td><td>mTLS validation gateway, authorization, audit, idempotency</td><td>Corda receipt IDs and status</td><td>Audit and idempotency state</td><td>No direct public exposure</td></tr>
<tr><td><code>ao-ledger-core</code></td><td><code>ao-ledger-core</code></td><td>Corda node, Corda database, certificate/keystore material</td><td>No direct output</td><td>Corda state and PKI</td><td>No direct public exposure</td></tr>
<tr><td><code>ao-data</code></td><td><code>ao-data</code></td><td>Narrow controlled data plumbing where unavoidable</td><td>Controlled references only</td><td>Host services, loopback-only</td><td>No direct public exposure</td></tr>
<tr><td><code>ao-admin</code></td><td><code>ao-admin</code></td><td>Prometheus security monitoring, Grafana dashboards, Metabase reporting, backup, restore validation, administration</td><td>Metabase reports and the Grafana dashboard only</td><td>Prometheus TSDB; Grafana application database; Metabase application database</td><td><strong>No VPN, no explicit allowlist, no public exposure</strong></td></tr>

<tr><td colspan="6" style="background-color:#c9ccd1; border-top:2px solid #8a8f98; border-bottom:1px solid #8a8f98; padding:5px 8px; font-weight:bold; letter-spacing:0.04em;">B · CONTROLLED INGRESS AND EGRESS ADAPTERS — architecture-controlled exceptions, not general-purpose Internet access</td></tr>
<tr><td><code>ao-ingress-payment</code></td><td><code>ao-payment</code></td><td><strong>Payment verification for Zelle, PayPal, and Coinbase.</strong> Receives the provider webhook or approved relay event, verifies the signature, normalizes it, and emits the verified payment event. Also carries the website path: email &gt; PDF &gt; Corda processing. <strong>Implemented and running</strong> &mdash; corrected 2026-10-04 (§5.2.2)</td><td>Verified normalized payment event</td><td>Minimal event and audit record</td><td>Inbound only. Minimal listener, provider-signature verification, audit log, normalized event output. <strong>No rate limiting is implemented</strong> &mdash; the requirement exists, the code does not (§5.2.2)</td></tr>
<tr><td><code>ao-egress-archive</code></td><td><code>ao-sales</code> (sale-transfer duty)</td><td><strong>ARCHIVED FOR DATA TRANSFER AND SALE &mdash; this is not a backup.</strong> Holds a sold package so it can be <em>transferred</em> to the authorised recipient. IPFS provides file-transfer verification and, where applicable, a blockchain sales listing; encrypted pCloud replication is the second copy. <strong>Requires <code>ao-sales</code> authorisation first</strong> — it is not reached directly from the internet. "Data sales": maps and telemetry/IoT products, not application databases. No restore, no recovery, no retention duty: <strong>restic (§17.1) is the backup</strong>. <strong>Deployable</strong></td><td>Approved encrypted transfer bundle; post-sale IPFS transfer; encrypted pCloud transfer copy</td><td>Staging and transfer log; no backup set, no retention record</td><td>Outbound only, and only after <code>ao-sales</code> authorisation. Destination allowlist, TLS validation, encrypted payloads, separate credentials, transfer audit</td></tr>
<tr><td><code>ao-build-update</code></td><td><code>ao-build-update</code> (10.89.13.0/24, <code>Internal=false</code>)</td><td><strong>Software updates only — all host software.</strong> Image and package acquisition from the upstream software source (package and container registries) before controlled promotion. <strong>It does not touch WebODM or imagery</strong>: all photo processing and verification belongs to <code>ao-mapping</code>. <strong>Scaffolded and deployed, not enabled</strong> (§5.2.1)</td><td>Verified image and package set</td><td>Update audit log</td><td>Outbound only, on its own dedicated egress network. Verified source, digest capture, update audit, no direct workload attachment, and no promotion authority</td></tr>

<tr><td colspan="6" style="background-color:#c9ccd1; border-top:2px solid #8a8f98; border-bottom:1px solid #8a8f98; padding:5px 8px; font-weight:bold; letter-spacing:0.04em;">C · COMPONENT BOUNDARY MATRIX — what each component may accept, emit, store, and reach</td></tr>
<tr><td>Sales API</td><td><code>ao-sales</code></td><td>Verified payment state and approved support requests</td><td>Signed receipt/entitlement manifests</td><td>Sales PostgreSQL</td><td>None directly</td></tr>
<tr><td>Payment verifier</td><td><code>ao-payment</code></td><td>Provider webhook or approved relay event</td><td>Verified normalized payment event</td><td>Minimal event and audit record</td><td>Through <code>ao-ingress-payment</code> only</td></tr>
<tr><td>Mapping intake</td><td><code>ao-mapping</code></td><td>Authenticated imagery upload</td><td>Validated image-set reference</td><td>Intake, validation, quarantine record</td><td>None directly</td></tr>
<tr><td>WebODM/NodeODM</td><td><code>ao-mapping</code></td><td>Validated mapping task input</td><td>Processing output to mapping exporter</td><td>Dedicated photogrammetry volume</td><td>None directly</td></tr>
<tr><td>Field gateway</td><td><code>ao-field</code></td><td>USB serial LoRa frames</td><td>Normalized telemetry manifest</td><td>Raw packet store and telemetry spool</td><td>USB serial and radio only</td></tr>
<tr><td>Vehicle simulator</td><td><code>ao-sim-vehicle</code></td><td>Approved scenario/model artifact</td><td>Signed simulation manifest</td><td>Vehicle simulation data path</td><td>None directly</td></tr>
<tr><td>Fabrication simulator</td><td><code>ao-sim-fabrication</code></td><td>Approved facility/task model</td><td>Signed simulation manifest</td><td>Fabrication simulation data path</td><td>None directly</td></tr>
<tr><td>Real fabrication collector</td><td><code>ao-fabrication</code></td><td>Per-machine production data polled from each machine's own MainsailOS / Moonraker / Klipper</td><td>Signed fabrication manifest; fabrication optimisation reports</td><td>Per-machine production data in <code>a_fab</code></td><td>None directly. Reaches machines only over the local equipment switch, never as a simulator.</td></tr>
<tr><td>Ledger ingestion</td><td><code>ao-ledger-ingest</code></td><td>Signed mTLS manifests</td><td>Receipt/status response</td><td>Audit and idempotency state</td><td>Only to ledger core</td></tr>
<tr><td>Ledger core</td><td><code>ao-ledger-core</code></td><td>Ledger-ingestion gateway requests only</td><td>No direct public output</td><td>Corda state and PKI</td><td>None directly</td></tr>
<tr><td>Archive adapter</td><td><code>ao-egress-archive</code></td><td>Approved encrypted archive bundle</td><td>Replication result/status</td><td>Staging and transfer log</td><td>Outbound only</td></tr>
<tr><td>Community publication</td><td><code>ao-sales</code></td><td>Approved publication or support request</td><td>Remote delivery/status response</td><td>Publication audit log</td><td>Outbound only, via Sidekiq on `ao-sales` (HTTPS/443)</td></tr>

<tr><td colspan="6" style="background-color:#c9ccd1; border-top:2px solid #8a8f98; border-bottom:1px solid #8a8f98; padding:5px 8px; font-weight:bold; letter-spacing:0.04em;">D · GUI AND WORKFLOW ATTACHMENT MAP — each row is attached to exactly <em>one</em> owning network and denied all the others</td></tr>
<tr><td>1 · Mastodon web / Konqueror client</td><td><code>ao-sales</code></td><td>Approved <code>localhost</code> Mastodon web/streaming origin; loopback-only publication when enabled.</td><td>—</td><td>—</td><td>Loopback origin only</td></tr>
<tr><td>2 · WebODM browser UI</td><td><code>ao-mapping</code></td><td><code>ao-webodm-web</code> sets <code>PublishPort=127.0.0.1:8000:8000</code>, so podman reports <code>127.0.0.1:8000-&gt;8000/tcp</code> and the UI opens at <code>http://127.0.0.1:8000/</code> with no SSH tunnel. It is loopback-only: LAN addresses refuse, and <code>ao-mapping</code> stays <code>Internal=true</code>.</td><td>—</td><td>—</td><td>None; internal to <code>ao-mapping</code> only</td></tr>
<tr><td>3 · QGroundControl simulation client</td><td><code>ao-sim-vehicle</code></td><td>Approved local SITL/MAVLink-router endpoint; <code>ROS_DOMAIN_ID=21</code>; <code>GZ_PARTITION=alwayson_vehicle_sim</code>.</td><td>—</td><td>—</td><td>None</td></tr>
<tr><td>4 · Gazebo visualization — vehicle</td><td><code>ao-sim-vehicle</code></td><td>Approved vehicle ROS/Gazebo visualization path; separate DDS/interface policy remains required.</td><td>—</td><td>—</td><td>None</td></tr>
<tr><td>5 · Gazebo visualization — fabrication</td><td><code>ao-sim-fabrication</code></td><td>Approved fabrication ROS/Gazebo visualization path; <code>ROS_DOMAIN_ID=22</code>; <code>GZ_PARTITION=alwayson_fabrication_sim</code>.</td><td>—</td><td>—</td><td>None</td></tr>
<tr><td>6 · LM Studio / OpenClaw support chat</td><td><code>ao-sales</code> (host-local LM Studio) / <code>ao-sales</code> (containerized OpenClaw)</td><td>Host desktop use; approved loopback inference endpoint or narrow authenticated bridge only.</td><td>—</td><td>—</td><td>None</td></tr>
<tr><td>7 · Grafana dashboards and metrics</td><td><code>ao-admin</code></td><td>No VPN, no explicit allowlist, no public exposure. Grafana presents the dashboards and metrics.</td><td>—</td><td>—</td><td>None</td></tr>
<tr><td>8 · Metabase reporting GUI</td><td><code>ao-admin</code></td><td>No VPN, no explicit allowlist, no public exposure. Metabase produces the reports by reading the existing PostgreSQL and MySQL databases over per-source read-only roles, and keeps its own PostgreSQL application database for its saved questions and dashboards.</td><td>—</td><td>—</td><td>None</td></tr>
<tr><td>9 · Sales, receipt, fulfillment, entitlement, return, and approved support reporting</td><td><code>ao-admin</code></td><td>Metabase is for reports, reads the existing PostgreSQL and MySQL databases over per-source read-only roles, and keeps its own application database. PostgreSQL inspection uses pgAdmin over an explicit purpose-limited loopback or approved tunneled connection.</td><td>—</td><td>—</td><td>None</td></tr>
<tr><td>10 · Ledger provenance, receipt, entitlement, approval, release, and ingestion reporting</td><td><code>ao-admin</code></td><td>No VPN. Grafana presents the dashboards and metrics from its own application database plus the approved datasources; Metabase produces the reports by ad-hoc read-only queries against the existing databases.</td><td>—</td><td>—</td><td>None</td></tr>
<tr><td>11 · Backup/restore status display</td><td><code>ao-admin</code></td><td>Shown on the Grafana dashboard; no VPN, no public exposure.</td><td>—</td><td>—</td><td>None</td></tr>
<tr><td>12 · Field gateway / link-quality display</td><td><code>ao-field</code></td><td>Approved USB serial/local diagnostic display or protected Grafana dashboard.</td><td>—</td><td>—</td><td>None</td></tr>
<tr><td>13 · Ledger/Corda console and maintenance</td><td><code>ao-ledger-ingest</code></td><td>Narrow approved operator-management path after key/certificate ceremony; no public access.</td><td>—</td><td>—</td><td>None</td></tr>
<tr><td>14 · PostgreSQL reporting, schema inspection, and controlled administration</td><td>host loopback</td><td>Explicit loopback or approved narrow tunnel/bridge using a dedicated least-privilege database identity.</td><td>—</td><td>—</td><td>None</td></tr>
<tr><td>15 · Redis diagnostic client</td><td><code>ao-data</code> (optional)</td><td>Explicit loopback or approved narrow diagnostic path using a scoped Redis ACL identity.</td><td>—</td><td>—</td><td>None</td></tr>
<tr><td>16 · Payment-provider dashboard</td><td>provider-hosted</td><td>Provider-authenticated browser workflow.</td><td>—</td><td>—</td><td>Provider-hosted only</td></tr>
<tr><td>17 · No GUI — controlled data services</td><td><code>ao-data</code> (narrow only)</td><td>Host services remain loopback-only; administration/reporting uses dedicated host or <code>ao-admin</code> identities and paths.</td><td>—</td><td>—</td><td>None</td></tr>
<tr><td>18 · No GUI — payment verifier</td><td><code>ao-payment</code></td><td>Provider-hosted checkout and provider dashboard; local verifier has no GUI.</td><td>—</td><td>—</td><td>None</td></tr>
</tbody>
</table>

### 5.1.1 Domain Networks

Every `ao-*` network in one place. **There are fourteen: eleven `Internal=true` and
three `Internal=false`.** That count is asserted, not merely stated —
`scripts/validation/check-network-isolation.sh` exits non-zero if the registry and
the running host disagree, and if the total, the internal count, or the egress
count changes without a deliberate decision.

**The registry is the authority and it is hand-maintained.**
`config/platform/network-cidrs.yaml` is the single source of truth for every CIDR
and `Internal` flag (§2.2). The validation script **reads** it; it does not
regenerate it. This was previously reversed — the script rebuilt the registry from
a hardcoded array of network names on every run, which meant the file named as the
authority was in fact derived from the script, and a network created in podman but
absent from that array was silently erased from the authority on the next run.
Adding a network is now a deliberate two-step act: create it, then add its line to
the registry. The script asserts both directions: every registered network must
exist with the recorded CIDR and flag, and every live `ao-*` network must appear in
the registry.

The CIDR and `Internal` columns below are generated from the registry with:

```bash
scripts/validation/check-network-isolation.sh --emit-table
```

which prints one row per registered network and a footer carrying the asserted
counts. The two prose columns — what the network belongs to, and what is attached
to it — are architecture, not runtime state, and are maintained here.

Every network's *Attached now* count below was re-measured against the running
host on **2026-10-04**, and every row now agrees with it.

| Network | Subnet | Internal | Belongs to (§5.1) | Attached now |
|---|---|---|---|---|
| `ao-sales` | 10.89.0.0/24 | **false** | Mastodon stack, `ao-sales-db`, orders and AI chat | `mastodon-web` `-sidekiq` `-db` `-redis` `-streaming`, `ao-sales-db` (6) |
| `ao-payment` | 10.89.1.0/24 | true | Provider webhook verifier, payment adapter | `ao-ingress-payment` (1) |
| `ao-field` | 10.89.2.0/24 | true | Heltec gateway, RNS/MeshChatX, telemetry spool, mission-release | **none** — gateway runs on host USB serial (ST-22) |
| `ao-mapping` | 10.89.3.0/24 | true | WebODM, NodeODM, Redis, mapping DB, imagery intake/exporter | `ao-webodm-webapp` `-worker` `-db` `-broker`, `ao-nodeodm` (5) |
| `ao-sim-vehicle` | 10.89.4.0/24 | true | ROS 2, Gazebo, ArduPilot SITL, MAVLink, QGC | **none** — Gazebo is host-installed; `ao-ardupilot-sitl.container` never deployed |
| `ao-sim-fabrication` | 10.89.5.0/24 | true | ROS 2, Gazebo; rehearses the engineering/production flow | `ao-sim-fabrication-gz`, `ao-sim-fabrication-foxglove` (2) |
| `ao-ledger-ingest` | 10.89.6.0/24 | true | mTLS validation gateway, authorization, audit, idempotency | **none** |
| `ao-ledger-core` | 10.89.7.0/24 | true | Corda node, Corda database, certificate/keystore | **none** |
| `ao-data` | 10.89.8.0/24 | true | Narrow controlled data plumbing **where unavoidable** | **none — correct by design.** ST-29: host services stay loopback-only; §5.1 forbids it becoming a universal shared network |
| `ao-admin` | 10.89.9.0/24 | true | Prometheus, node_exporter, Grafana, Metabase, backup/restore | `ao-grafana`, `ao-metabase`, `ao-prometheus`, `ao-node-exporter` (4) |
| `ao-reporting-egress` | 10.89.10.0/24 | **false** | Egress for reporting sources only | `ao-grafana`, `ao-metabase` (2) (also on `ao-admin`) |
| `ao-fabrication` | 10.89.12.0/24 | true | Real (non-simulated) fabrication; per-machine production data | `ao-fabrication-db` (1) |
| `ao-build-update` | 10.89.13.0/24 | **false** | Controlled software-update acquisition (§5.2.1) | none — scaffolded, not enabled |
| `ao-html-window` | 10.89.14.0/24 | true | Operator-facing read-only display network for local 3D/2D HTML renders; `Internal=true` deliberately, reached by loopback `PublishPort` only | `ao-sim-fabrication-foxglove` (1) — dual-homed with `ao-sim-fabrication`, see below |

Two `ao-*` networks named in earlier drafts appear in the topology but were in no
table; both are now rows above: `ao-html-window` (`10.89.14.0/24`) and
`ao-build-update` (`10.89.13.0/24`).

**The one dual-homed container, and why.** This was numbered §5.1.2 when
first added, which collided with the §5.1.2 *Local Browser Addresses* below.
Two sections shared one number. It is demoted to a bolded lead-in here rather
than given a new number, because it is a continuation of §5.1.1 — it explains a
row of the table immediately above — and because §5.1.2 is already referenced by
name from §7 and §19.1 as *Local Browser Addresses*, so that number belongs to
the other section. Renumbering the browser-address section instead would have
broken those references; renumbering this one would have put a §5.1.3 above a
§5.1.2.

The *one network per component* rule above permits a second attachment only
where the approved access path says so explicitly. Exactly one container holds two:
`ao-sim-fabrication-foxglove`, on `ao-sim-fabrication` (its own domain) and on
`ao-html-window` (the read-only display network).

```text
$ podman inspect ao-sim-fabrication-foxglove \
    --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}'
ao-html-window ao-sim-fabrication
```

Both halves are load-bearing, and the reason is mechanical rather than a
convenience: two `Internal=true` bridges do not route to each other, so a
container on one cannot reach a peer on the other. The bridge must sit on both to
carry Gazebo topics out to the browser-facing surface. The `Network=` lines in
`quadlet/sim-fabrication/ao-sim-fabrication-foxglove.container` state this, and
§10.2 records the operational consequence.

The security consequence is bounded and worth stating plainly: the two networks
are joined by one container, so anything reachable on `ao-sim-fabrication` is
reachable from `ao-html-window` by going through it. Both are `Internal=true`, so
neither carries a route off the host, and the bridge publishes nothing but its
loopback `127.0.0.1:8081` WebSocket. This is a bridge between two internal
segments, not an egress path.

**This row previously said "none" was attached, and that was wrong** — it was
written when the network was empty and never re-measured after the Foxglove
bridge was deployed. The whole *Attached now* column is host state and goes
stale silently; it is stated here as measured on the date below, not as a
permanent fact. `--emit-table` covers only the two generated columns, so the
attachment column must be re-measured directly:

```bash
for n in ao-sales ao-payment ao-field ao-mapping ao-sim-vehicle \
         ao-sim-fabrication ao-ledger-ingest ao-ledger-core ao-data ao-admin \
         ao-reporting-egress ao-fabrication ao-build-update ao-html-window; do
  printf '%-22s %s\n' "$n" \
    "$(podman network inspect "$n" --format \
        '{{range .Containers}}{{.Name}} {{end}}' | wc -w)"
done
```

**`ao-html-window` is not the storefront window.** ES.2 describes it as
public-facing egress to 300x3.com, and this row used to repeat that. The
deployed unit and network file say otherwise: the network is `Internal=true`
with no route off the host, and it serves the operator's own browser over
loopback. ES.2 is not owned by this section and has not been edited; the divergence is
recorded in `proposals/net-NET-05.md` for the executive-summary session and the
operator. Only the row this section owns was corrected, to match the deployed unit.

`10.89.11.0/24` is deliberately unallocated and is reserved for
`ao-egress-community`, which is **retired**. Verified 2026-10-03: no podman
network of that name exists on this host, and the CIDR is allocated to nothing:

```text
$ podman network inspect ao-egress-community
Error: network ao-egress-community: unable to find network with name or ID
ao-egress-community: network not found
```

Community publication and federation are carried inside `ao-sales`
(`Internal=false`, expressly so Sidekiq can deliver ActivityPub), per
`config/mastodon/instance-policy.yaml`. The name survives in the topology model and
the Mastodon runbook as a retired reference; those record the retirement, not a
live network.

`ao-data` carries no containers by design. Which of the remaining networks are
populated is status and is recorded in §19.1.

### 5.1.2 Local Browser Addresses

The loopback address for each GUI above, so the operator does not have to
derive it from the Quadlet units. All are `127.0.0.1`-bound only; the LAN
addresses refuse, and none is published through Podman, nginx, Cloudflare, or a
router. Verified 2026-10-01 by `scripts/validation/check-local-services.js`
(15 pass, 0 fail) and mirrored in the Firefox bookmarks folder
`SERVERS → SERVERS (THIS MACHINE)`.

| Software / GUI | Address | Notes |
|---|---|---|
| ALWAYS ON operator console | `http://127.0.0.1:8099/` | Not a deployed service; started on demand |
| ALWAYS ON sim console (Foxglove + ROS 2) | `http://127.0.0.1:8099/sim` | Same process; the only thing presenting Foxglove |
| Podman / systemd status view | `http://127.0.0.1:8099/podman` | Same process |
| Gazebo factory.world portal | `http://127.0.0.1:8765/` | View-only HTML portal: boning, RL-object and world state |
| Gazebo 3D viewer | `http://127.0.0.1:8765/viewer` | Served by the same portal process; selects any of the eight read-only camera feeds and resizes the 3D view. It connects to the bridge on `ws://127.0.0.1:8081` |
| Mastodon local UI | `https://127.0.0.1:3300/` | **Self-signed cert — accept once.** Terminates TLS because upstream hardcodes `config.force_ssl = true`; `http://127.0.0.1:3000/` 301s to a TLS port that does not exist and hangs the browser |
| Mastodon web origin (transport) | `http://127.0.0.1:3000/` | Answers `301` only; not usable as a browser entry point |
| WebODM | `http://127.0.0.1:8000/` | Redirects to `/login/`. Loopback published 2026-10-01; no SSH tunnel needed |
| Grafana | `http://127.0.0.1:3001/` | Redirects to `/login` |
| Metabase | `http://127.0.0.1:3002/` | |
| Prometheus | `http://127.0.0.1:9090/` | Redirects to `/query` |
| OpenClaw control | `http://127.0.0.1:18789/` | |
| MeshChatX | `https://127.0.0.1:18000/` | **Self-signed cert.** Reticulum; not a public ingress |
| Domoticz | `http://127.0.0.1:8080/` | Host service, not an `ao-*` container |
| CUPS (printers) | `http://127.0.0.1:631/` | Host service |
| LM Studio | `http://127.0.0.1:1234/` | Bearer-token API only — no browsable UI, so not bookmarked |
| Mastodon streaming / OpenClaw chat relay | `http://127.0.0.1:4000/`, `http://127.0.0.1:18790/` | APIs, not UIs; a bare `/` returns `400`/`404` by design |

## 5.2 Controlled Ingress and Egress Adapters

**Combined into the single matrix in §5.1, group B.** The three controlled adapters
(`ao-ingress-payment`, `ao-egress-archive`, `ao-build-update`) are rows in that table along
with their purpose, direction, and mandatory controls.

Their measured state differs, and §5.1 group B previously flattened all three into
"Deployable", which hid both the running adapter and the missing control:

| Adapter | Measured state | Detail |
|---|---|---|
| `ao-ingress-payment` | **Implemented and running** since 2026-10-01; one claimed control absent | §5.2.2 |
| `ao-build-update` | Scaffolded and deployed, **not enabled** | §5.2.1 |
| `ao-egress-archive` | **Not implemented.** No unit, no network, no service | `systemctl --user is-enabled ao-egress-archive.service` → `not-found`; no `quadlet/egress-archive/` directory |

So `ao-egress-archive` is the *only* adapter of the three that genuinely does not exist.
`ao-ingress-payment` was the substantive correction.

### 5.2.1 `ao-build-update` — Controlled Software-Update Acquisition

**The authoritative record of every pinned image and package version is
`/ALWAYSON/config/platform/version-matrix.yaml`.** It is version-controlled, refreshed by
`scripts/validation/capture-version-matrix.sh`, and regenerated from the deployed units
rather than typed by hand. A digest recorded anywhere else is not authoritative (§4.1 rule 9).

**Status: scaffolded and deployed, not enabled.** The unit, its network, its
allowlist, and its acquisition script all exist. The service is deliberately left
disabled, because running it reaches the public internet and that requires
explicit operator authorisation and is never automatic. Measured 2026-10-03:

```text
$ systemctl --user is-enabled ao-build-update.service
generated
$ systemctl --user is-active ao-build-update.service
inactive
```

The unit files are installed at `~/.config/containers/systemd/` (`generated`
means the service is not enabled to start at boot). No container is attached to
`ao-build-update`; the network is allocated and empty.

> **The allowlist is enforced in code, but not by the network.** These are two
> different controls and it matters which one you are relying on.
>
> *Enforced:* `scripts/build-update/ao-build-update.py` reads
> `config/build-update/registry-allowlist.yaml` at runtime and **refuses**
> anything not on it. Verified 2026-10-04 by execution — a denied host, an
> allowed-but-unpinned reference, and an allowed-and-pinned reference:
>
> ```text
> $ python3 scripts/build-update/ao-build-update.py localhost/foo:latest
> allowlist boundary enforced; see the audit record
>   localhost/foo:latest: DENIED: localhost is on the adapter deny list
> EXIT=4
>
> $ python3 scripts/build-update/ao-build-update.py docker.io/library/nginx:latest
> allowlist boundary enforced; see the audit record
>   docker.io/library/nginx: UNPINNED: docker.io is allowed but the reference carries no sha256 digest
> EXIT=4
>
> $ python3 scripts/build-update/ao-build-update.py \
>     'docker.io/library/nginx@sha256:0000…0000'
>   docker.io/library/nginx@sha256:0000…0000: ALLOWED-PINNED
> EXIT=0
> ```
>
> Every run also appends to the append-only audit log and writes a staging
> report. The control is real, and it is a *refusal to plan*, not a refusal to
> route.
>
> *Not enforced:* the network itself. `Internal=false` is an ordinary bridge, so
> **anything else** attached to `ao-build-update` bypasses the allowlist
> completely — it can reach any host on the internet. The allowlist governs this
> one script; it does not govern the segment.
>
> Therefore the *only sanctioned outbound* sentence in **Containment** below is a
> **requirement the adapter must satisfy, not a property the segment currently
> has.** Segment-level enforcement needs a firewall rule set on the bridge, a
> filtering proxy, or per-destination proxies — all firewall policy, all
> requiring explicit operator approval (Rule 6, §4.1 rule 13). Until that is
> approved and built, do not attach any container to this network. NET-01 is open
> on exactly this point; see `proposals/net-NET-01.md`.

**What it is.** `ao-build-update` is the controlled acquisition stage of the
software-update path. It resolves candidate container images and host package
metadata from allowlisted upstream sources, captures the digest of every
candidate, and writes an append-only update audit record, producing a *verified
image and package set* that an operator can review. It is the formalisation of
the manual chain this system has always used — pull, capture the digest, edit the
`Image=` line, redeploy, restart, verify — with the first two steps automated and
the last three deliberately left alone.

**What it is not, by design.** It has no promotion authority. It never installs a
package, never runs `apt`, `dpkg`, or `unattended-upgrades`, never edits a
Quadlet, never restarts a unit, and never redeploys a container. No workload
container is ever attached to its network.
A fetched image is a **candidate**: promotion to a running service is a separate,
human action, and digest pinning (§4.1 rule 9) is what makes that decision
reviewable. This is the same posture the rest of the platform already takes — no
automatic deployment, no `podman auto-update` policy, no Watchtower — expressed as
a component instead of as an absence.

**Network.** The adapter runs on its own egress network, `ao-build-update` at
`10.89.13.0/24`, `Internal=false`, following the `ao-reporting-egress` precedent.
It requires a non-internal network: `Internal=true` provides no external resolver
and no outbound route, so a container on such a network cannot reach a registry
and could not perform acquisition. `ao-admin` is `Internal=true` and is
additionally the monitoring and reporting plane, so an update audit record does
not belong on it. No workload container is attached to this network.

**Containment — enforced in code, unenforced at the segment.** Acquisition over
HTTPS/443 to the registry hosts named in
`config/build-update/registry-allowlist.yaml` is the *only* outbound this
adapter is permitted to make. That restriction **is** a working control in this
script: it reads the allowlist at runtime and refuses anything not on it, and
refuses unpinned references, exiting non-zero on both (verified by execution
above). What is *not* enforced is the network segment — see the status note.
This paragraph previously said the restriction was "not currently enforced by
any mechanism", which contradicted the verified results directly above it and
was wrong; it conflated the two controls the status note separates. The
allowlist is mounted read-only, so the adapter cannot widen its own boundary.
`packages.ros.org` is on an explicit deny list rather than merely absent, because
it fails TLS verification from this host and that verification is deliberately
not disabled. The adapter publishes no port and serves no listener; it runs as a
oneshot and the host reads its exit status and the audit record. Any reference
that is not both allowlisted and digest-pinned is a finding, not a pass, and the
run exits non-zero.

**Scope boundary: builds.** This adapter's role is *updates*, not image builds.
Builds belong to the domain that consumes the image. The Gazebo Containerfiles
under `GAZEBO/containers/` are owned by `ao-sim-fabrication`, which mounts
`/ALWAYSON/GAZEBO` read-only and runs the world from it; this adapter does not
acquire, rebuild, or promote them. `ao-sim-fabrication-gz` is digest-pinned to a
local build, so a Containerfile rebuild changes the digest and fails the unit
until `ao-sim-fabrication` re-pins it. That fail-safe is intended.

**Files.** `quadlet/build-update/ao-build-update.network`,
`quadlet/build-update/ao-build-update.container`,
`config/build-update/registry-allowlist.yaml`, and
`scripts/build-update/ao-build-update.py`. The CIDR is registered in
`config/platform/network-cidrs.yaml`, and `check-network-isolation.sh` asserts it
as an egress network.

**Reporting: pinned vs stable.** `scripts/build-update/drift-report.py` resolves every
pinned image against its upstream registry and compares apt, snap, and flatpak, then
writes `docs/drift.md`. It is read-only — it never pulls, installs, or restarts — and
distinguishes a real DRIFT from a BEHIND-LATEST condition, which for an image held at
an older major on purpose is information rather than a defect.

**Recommendations: advisory only.** `scripts/build-update/recommend.py` turns the
drift report and the inventory into a ranked, explained recommendation — what needs
a decision, why, the risk, and the command to run *if you choose to*. It applies
nothing: it cannot install, promote, deploy, or restart. **Automatic updates are
the last thing this system does and require review and explicit authorization;
they are not built, and the reporting tools are not to be extended to perform
them.**

**The update procedure.** The full operator path — inventory, acquire, promote,
deploy, verify, record, and roll back — is in
`docs/runbooks/software-update.md`. Promotion is done with
`scripts/build-update/promote-image-digest.sh`, which edits exactly one `Image=`
line and refuses an unqualified, unpinned, or cross-registry reference.

**Enabling it.** `systemctl --user start ao-build-update` runs one acquisition
pass. The unit carries no `WantedBy=`, so it will not start on its own. Enabling
it permanently, and any decision to automate acquisition, requires operator
approval.


### 5.2.2 `ao-ingress-payment` — Deployed and running, and one claimed control that is absent

Measured 2026-10-04. §19 and this section previously recorded this adapter as
**"Deployable"** and as one of the two adapters "still requiring
implementation". That was wrong on the first count and misleading on the second.
The adapter is deployed, enabled, active, and answering on loopback:

```text
$ systemctl --user is-enabled ao-ingress-payment.service
generated
$ systemctl --user is-active ao-ingress-payment.service
active
$ systemctl --user status ao-ingress-payment.service --no-pager -n 8 | head -3
● ao-ingress-payment.service - ALWAYS ON payment ingress adapter
     Active: active (running) since Thu 2026-10-01 15:08:41 PDT; 3 days ago
$ podman inspect ao-ingress-payment --format '{{.State.Status}} networks=...'
running networks=ao-payment
$ curl -sS -o /dev/null -w 'http_code=%{http_code}\n' http://127.0.0.1:8899/health
http_code=200
```

**What this adapter does get right, and it is a real control set.** The generic
adapter requirements in **Rules that govern every row** — separate credentials,
minimal permissions, connection logging, inbound-only — are met:

- **Separate credential.** `EnvironmentFile=%h/.local/share/ao-secrets/payment.env`,
  mode `0600`, holding one key, `PAYMENT_DSN`. No provider secret value was read
  or printed. (Key name and length only, per rule 7.)
- **Signature verification before state.** `verify_paypal()` recomputes an
  HMAC-SHA256 over `transmission-id|transmission-time|body` and compares with
  `hmac.compare_digest`; an unverified event is rejected with `401` **before**
  `sink.record()` is ever reached, so an unsigned webhook cannot create business
  state. A 300-second timestamp window is enforced as replay defence.
- **Fail-closed on missing secret.** With no `PAYPAL_WEBHOOK_SECRET` configured
  the function returns `False` and logs `REJECT`, rather than accepting.
- **Zelle is refused, not auto-verified.** `/webhook/Zelle` returns `501`.
  That is §18.4 behaviour, correctly implemented.
- **Least privilege.** `NoNewPrivileges=true`, `ReadOnly=true`, no capabilities
  beyond defaults, `ao-payment` is `Internal=true`, and the published port is
  `127.0.0.1:8899` — loopback only, never LAN-reachable. The host-side relay
  `ao-payment-relay.service` is `enabled`/`active` and also binds `127.0.0.1`
  only.

**The defect: a claimed control that does not exist.** The group B row asserted
**"rate limits"**. There is no rate limiting in the code:

```bash
$ grep -n -i 'ratelimit\|rate_limit\|429\|too many' scripts/payment/ao-payment-adapter.py
EXIT=1 (1 = no match)
$ grep -o -i '[a-z]*rate[a-z]*' scripts/payment/ao-payment-adapter.py | sort -u
deliberately
migrate
```

Both `rate` hits are substrings of unrelated words. The only request-shaping
control present is `MAX_BODY = 256 * 1024`, a body-size cap, which is not rate
limiting. There is no per-IP throttle, no token bucket, no `429` path, and no
`Retry-After`.

This matters more than an ordinary documentation drift, because an inbound
payment webhook endpoint is exactly where an unthrottled listener is worth
attacking, and because the §5.1 table is the artifact an operator reads to
decide whether a control exists. The other controls above are enforced in code;
this one was documentation of intent that nobody implemented.

**Mitigating, and stated so the finding is not overstated.** The endpoint is
bound to `127.0.0.1` and the Cloudflare Tunnel route that would front it is
**not enabled**, per the relay unit's own comment and NET-01's public-surface
rule. So there is no internet-reachable path to this listener today, and the
absence of rate limiting is a latent gap rather than a live exposure. It must be
implemented *before* any tunnel or relay route is enabled, or that enablement
should be refused.

**Not fixed here.** `scripts/payment/` and `quadlet/payment/` are not owned by this
section, and this is payment processing: an explicit stop condition under README §4.1
rules 14 and 15. The measurement was taken, the row this section owns was corrected, and
work stopped there. **The adapter, the unit, the relay and the credential must not be
edited without explicit operator approval.**

#### 5.2.3 The three `Internal=false` networks are a prohibition boundary, and §4.3 now says which rule governs them

Measured 2026-10-05. This section is where the NET-04 completeness check landed,
because the question — *which prohibition covers a non-internal workload network*
— is answerable only by reading §5.1 and §4.3.2 together.

Three registered networks are `Internal=false`, and they are **not** three
instances of one thing. §5.1 group A already splits them:

| Network | Group in §5.1 | Live containers | Why it is non-internal |
|---|---|---|---|
| `ao-sales` | **A — workload domain** | 6 (Mastodon stack + `ao-sales-db`) | Sidekiq must deliver ActivityPub outbound |
| `ao-reporting-egress` | **C — component boundary** | 2 (`ao-grafana`, `ao-metabase`) | Reporting sources are remote |
| `ao-build-update` | **B — controlled adapter** | 0 — scaffolded, not enabled | Registry acquisition needs a resolver and a route |

The distinction matters because §4.3.2 said *"Any workload network to the public
internet"* with no exception, which would have prohibited two of these three by
name. §4.3.4 gap 1 records that and restates the rule as the outbound
restriction that is actually intended and actually held. **The isolation posture of no
network was changed** — no network was created, removed, re-CIDRed, or re-flagged; the
registry is untouched.

The remaining honesty point, unchanged and still true: **non-internal means
anything else attached can reach the internet.** `ao-sales` and
`ao-reporting-egress` have no firewall or destination allowlist between them and
the public internet. Their containment rests on the one-network-per-component
rule (§5.1) plus the fact that nothing else is attached to them — a
convention, not a control. `ao-build-update` is the one case where the
convention is load-bearing and unenforced; §5.2.1 covers it and NET-01 is open
on it.

## 5.3 Approved Local Data Paths

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

These paths must not become public listeners, must use separate credentials,
and must not grant unrelated applications access to each other's owner,
migration, backup, payment, or ledger credentials. Network isolation remains
a defense-in-depth control; PostgreSQL roles and grants are the primary
authorization boundary for database access.

---

# 6. Component Boundaries, GUI Reporting Tools, and Operator Access

## 6.1 Component Boundary Matrix

**Combined into the single matrix in §5.1, group C** — what each component may accept as
input, emit as output, persist and reach externally, on the same row as its owning domain and
its §19.1 status.

## 6.A GUI Reporting Tools and Podman Network Mapping

An **architecture requirement**: the required relationship between operator GUIs, reporting
tools, dashboards, desktop clients, external provider dashboards, workload domains, and Podman
networks. Work remaining against it is in §19.1.

### 6.A.1 GUI ↔ Podman Network Mapping

**Combined into the single matrix in §5.1, group D** — eighteen GUI and workflow rows, each
with its one owning network, its approved access path and its §19.1 status. The attachment
rule in §5.1 governs every one of them.

### 6.A.2 Reporting Tool Roles

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
over TCP to the host's `10.42.0.1` on `ao-reporting-egress`. Measured 2026-10-04; both
containers are also on `ao-admin`. Both are loopback-and-socket scoped, which is why neither
needs a public port. Measured listeners: Grafana `127.0.0.1:3001` and Metabase
`127.0.0.1:3002`, loopback-bound only (`ss -ltn`).

**Re-verified 2026-10-05, with one correction that belongs in §3.** Every claim above holds —
both containers are on `ao-admin` *and* `ao-reporting-egress`, and `3001`/`3002` are
loopback-only:

```
$ for c in ao-grafana ao-metabase; do podman inspect $c \
    --format '{{.Name}} {{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}'; done
ao-grafana  ao-admin ao-reporting-egress
ao-metabase ao-admin ao-reporting-egress
$ ss -ltn | grep -E ':(3001|3002)\s'
LISTEN 0 4096  127.0.0.1:3001  0.0.0.0:*
LISTEN 0 4096  127.0.0.1:3002  0.0.0.0:*
$ podman inspect ao-metabase --format '{{range .Config.Env}}{{println .}}{{end}}' | grep MB_DB_HOST
MB_DB_HOST=10.42.0.1
```

Metabase's `MB_DB_HOST` is `10.42.0.1` — **the equipment LAN address**, reached through
`ao-postgres-reporting-bridge`, not a Podman gateway. §3.3.0.1 records the correction: the
bridge's own comment and unit description both claim it exposes the ao-admin gateway, and it
does not. The consequence for this subsection is that Metabase's reachability depends on
`ao-reporting-egress` being `Internal=false`; `ao-admin` alone cannot reach it. Both networks
are present, so the access path works as designed — but the *stated* reason for it does not,
and a reader trying to tighten `ao-admin` should know that removing `ao-reporting-egress`
would break Metabase's database connection, not `ao-admin` being insufficient.

The Grafana path is unaffected by any of this: it uses a bind-mounted Unix socket
(`/var/run/postgresql -> /var/run/postgresql rw=false`), so it does not traverse the bridge at
all.

**Metabase and Corda.** Metabase may report on approved Corda-derived business and
provenance data only through a deliberate read-only reporting projection, approved views, a
supported status interface, or ledger-ingestion audit and status records. It must not become
the primary interface to Corda's internal persistence tables, administer Corda, hold Corda
private keys or keystores, or create a broad route into `ao-ledger-core`.

### 6.A.3 Conformance Requirements

Every current and future GUI, dashboard, reporting, database-administration and
operator-access implementation must comply with this subsection and §§4, 5, 14 and 17.

- Every tool must have a named operator purpose, runtime placement, approved
  data/status source, documented access path, and a §19.1 status.
- Every containerized GUI must have a documented Podman-network membership,
  listener policy, service owner, image digest, authentication method, and
  least-privilege identity.
- Every host desktop GUI and provider dashboard must be recorded as having no
  Podman network attachment unless it is actually containerized.
- Reporting identities must enforce read-only access to source databases or
  services. Grafana and Metabase each keep their own application database and read the
  business databases over per-source read-only roles, writing to none of them.
  *Verified 2026-10-04 on `salesdb`: `sales_reporting_role` holds `SELECT` on **five views**
  and nothing else — `v_reporting_orders`, `v_reporting_receipts`, `v_reporting_entitlements`,
  `v_reporting_sale_provenance`, `v_corda_entry_readiness`. It is not a superuser and has no
  `CREATE`/`CREATEDB`/`CREATEROLE`. It holds no privilege on any base table: reading `orders`
  directly fails with `permission denied for table orders`, while reading `v_reporting_orders`
  succeeds. That is the read-only boundary holding, not merely declared.*
  *Note the word **views** — an earlier revision of this bullet said "5 tables". The grant is on
  views owned by `sales_migration_role`, and the underlying tables are granted to
  `sales_api_role` and `sales_backup_role`, never to the reporting role.*
  *The separate `metabase_app` role exists **only** on the Metabase application database, not on
  `salesdb`, so the reporting path to the business data is `sales_reporting_role`.*
  *One thing to watch, not a breach: `sales_migration_role` on the same cluster **is** a
  superuser with `CREATEDB` and `CREATEROLE`. That is the migration identity and it is not
  handed to a reporting tool, but any future convenience that grants it to Metabase or
  Grafana would void the read-only boundary above.*

  **Re-verified 2026-10-04 by executing as the reporting role, not by reading a catalog.**
  A catalog view reports what is *granted*; this proves what actually *happens* when the
  reporting identity connects, which is the claim that matters:

  ```
  $ podman exec ao-sales-db psql -U sales_reporting_role -d salesdb -tAc "select count(*) from orders;"
  ERROR:  permission denied for table orders
  $ podman exec ao-sales-db psql -U sales_reporting_role -d salesdb -tAc "select count(*) from v_reporting_orders;"
  1
  $ podman exec ao-sales-db psql -U sales_migration_role -d salesdb -tAc \
      "select rolname,rolsuper,rolcreatedb,rolcreaterole from pg_roles where rolname like 'sales_%';"
  sales_admin_role|f|f|f
  sales_api_role|f|f|f
  sales_backup_role|f|f|f
  sales_migration_role|t|t|t
  sales_reporting_role|f|f|f
  ```

  Denied on the base table, permitted on the view, and `sales_migration_role` is the only
  row with superuser/`CREATEDB`/`CREATEROLE` set — exactly as the watch-note above says.
  The grant set is still exactly the five views, and `metabase_app` still does not exist
  in `salesdb`, so the reporting path remains `sales_reporting_role`.

  **A trap worth naming, because it reads as a broken container.** The obvious probe —
  `psql -U postgres` inside `ao-sales-db` — fails with `role "postgres" does not exist`,
  because that cluster is initialised with `POSTGRES_USER=sales_migration_role` and has no
  `postgres` role at all. The container is not broken and the database is not missing;
  there is simply no `postgres` superuser in it. Use the `sales_migration_role` identity.
  Someone reading "PostgreSQL 17 container", reaching for `-U postgres`, and recording
  "reporting store unreachable" would be wrong, and the fix is to read
  `POSTGRES_USER` from the container env before concluding anything about the data.
- `ao-admin` receives approved PostgreSQL reporting, exporter, status,
  projection, API, relay, tunnel, or push paths. It must not join every
  workload network.
- `ao-data` is not a shared unrestricted database, general-purpose shell, or
  authorization bypass. It may carry narrowly approved local data paths.
- No GUI may add a public listener, broad host networking, unrestricted Podman
  socket access, `--privileged`, shared writable storage, or unrelated-domain
  secret merely to simplify deployment or troubleshooting.
- Any material deviation requires an approved record before a production
  declaration.

The machine-readable inventory that implements this requirement is
`/ALWAYSON/config/platform/gui-boundary-matrix.yaml`.

#### 6.A.3.1 Known staleness in that inventory (re-measured 2026-10-04)

The YAML is **behind both this subsection and the live network list**. It remains a valid
record of the 2026-08-29 review it declares, and these claims no longer hold:

| Field in the YAML | Measured state | Evidence |
|---|---|---|
| `matrix.reviewed: "2026-08-29"` and `podman_networks_verified` lists **10** networks | The host runs **14** `ao-*` networks | `podman network ls` |
| same list | Omits `ao-fabrication`, `ao-html-window`, `ao-build-update`, `ao-reporting-egress` | as above |
| entries (10) name `ao-egress-community` and `ao-ardupilot-sitl` | **Neither network exists** — `ao-egress-community` is not found, and it is not in `network-cidrs.yaml`; `10.89.11.0/24` is unallocated and folded into `ao-sales` | `podman network inspect ao-egress-community` → *network not found*; `grep 10.89.11 config/platform/network-cidrs.yaml` → no match |

**Withdrawn — do not repeat an earlier claim from this subsection.** A previous revision
asserted that `config/platform/monitoring/grafana/provisioning/datasources/` was **empty**,
implying no datasource is provisioned. **That is no longer true**, and it was measured, not
guessed:

```
$ ls config/platform/monitoring/grafana/provisioning/datasources/
postgres-aostatus.yml
sqlite-snapshots.yml
```

`postgres-aostatus.yml` provisions a single `ALWAYS ON Status` PostgreSQL datasource by URL
over the host Unix socket. The current state of the Grafana datasource inventory is a
**monitoring** concern for the OPS group and is deliberately **not** asserted here — verifying
it needs host PostgreSQL access (`sudo -u postgres psql ... grafana`), which did not succeed
non-interactively during this review, so the live DB contents are unconfirmed and the file
alone is not proof of what Grafana has actually loaded.

**The blocker above is still a blocker — re-attempted 2026-10-04, same result.** A second
review tried a different route and also failed:

```
$ sudo -n -u postgres psql -tAc "select datname from pg_database order by 1;"
sudo: interactive authentication is required
$ podman exec ao-grafana sh -c 'psql -h /var/run/postgresql -U "$GF_DATABASE_USER" -d postgres -tAc "..."'
sh: psql: not found
```

The socket is correctly mounted read-only into the container
(`Volume=/var/run/postgresql:/var/run/postgresql:ro`) and `GF_DATABASE_HOST=/var/run/postgresql`,
so the *path* is proven — but the Grafana image ships no `psql` client, and `sudo -n` cannot
authenticate non-interactively. What **is** now proven, from Grafana's own startup log, is that
the application database on the host cluster is real and PostgreSQL, and that Grafana connected to
it:

```
$ podman logs ao-grafana | grep -E 'Connecting to DB|migrator'
logger=sqlstore t=2026-10-03T19:34:26.480251744Z level=info msg="Connecting to DB" dbtype=postgres
logger=migrator t=2026-10-03T19:34:26.486028158Z level=info msg="Locking database"
logger=migrator t=2026-10-03T19:34:26.507162277Z level=info msg="Unlocking database"
```

and Metabase independently reports the host cluster version, corroborating the "host PostgreSQL
18" row in §3.3.1:

```
$ podman logs ao-metabase | grep -i 'verified postgres'
2026-10-01 22:22:54,982 INFO db.setup :: Successfully verified PostgreSQL 18.6 (Ubuntu 18.6-0ubuntu0.26.04.1) application database connection. ✅
```

So the **host PostgreSQL 18** claim in §3.3.1 and §6.A.2 is now measured from two independent
sources rather than inferred from `/etc/postgresql/`. What remains unconfirmed is narrower and is
the OPS group's to answer: *which datasources Grafana actually has loaded*, as distinct from
which files are provisioned. Reading the `grafana` database's `datasource` table needs a
`postgres` superuser role on the host cluster, which no non-interactive route currently reaches.

So §5.1 group D (18 rows, counted) is the current statement, and the YAML is a lagging subset
of it. Reconciling the YAML is **not** in scope here — it is a config file outside the three
section files §6 owns, and the `ao-egress-community` name/CIDR question is an existing §19.1
item belonging to another group. This subsection records the gap so the next reader is not
misled.

#### 6.A.3.2 Four unmanaged Grafana containers are running (measured 2026-10-04)

Measured 2026-10-04 with the correct label key (see the correction immediately
below — an earlier revision used the wrong one):

```
$ podman inspect relaxed_tharp --format '{{index .Config.Labels "PODMAN_SYSTEMD_UNIT"}}'
$ podman inspect ao-grafana     --format '{{index .Config.Labels "PODMAN_SYSTEMD_UNIT"}}'
ao-grafana.service
```

**Correction 2026-10-04 — the ownership evidence in this subsection was gathered with a
label key that does not exist on this host.** The command shown above is what produced
the numbers; an earlier revision of this subsection used
`{{index .Config.Labels "io.podman.annotations.quadlet"}}` and printed `unit=` for every
container. On Podman 5.7.0 that key is never set, so that command proves nothing and
would have reported `ao-grafana` as ownerless too. The key Quadlet actually writes here
is **`PODMAN_SYSTEMD_UNIT`** — measured:

```
$ for c in $(podman ps --format '{{.Names}}'); do u=$(podman inspect $c \
    --format '{{index .Config.Labels "PODMAN_SYSTEMD_UNIT"}}'); \
    printf '%-30s -> %s\n' "$c" "${u:-<none>}"; done
ao-prometheus                  -> ao-prometheus.service
ao-nodeodm                     -> ao-nodeodm.service
ao-webodm-webapp               -> ao-webodm-web.service
ao-webodm-worker               -> ao-webodm-worker.service
ao-webodm-db                   -> ao-webodm-db.service
mastodon-streaming             -> ao-mastodon-streaming.service
ao-ingress-payment             -> ao-ingress-payment.service
mastodon-web                   -> ao-mastodon-web.service
mastodon-sidekiq               -> ao-mastodon-sidekiq.service
ao-metabase                    -> ao-metabase.service
vigorous_shannon               -> <none>
dreamy_rosalind                -> <none>
ao-sales-db                    -> ao-sales-db.service
mastodon-db                    -> ao-mastodon-db.service
ao-fabrication-db              -> ao-fabrication-db.service
mastodon-redis                 -> ao-mastodon-redis.service
ao-webodm-broker               -> ao-webodm-broker.service
ao-sim-fabrication-foxglove    -> ao-sim-fabrication-foxglove.service
relaxed_tharp                  -> <none>
confident_khayyam              -> <none>
ao-node-exporter               -> ao-node-exporter.service
keen_bhabha                    -> <none>
ao-sqli3                       -> <none>
ao-grafana                     -> ao-grafana.service
ao-sim-fabrication-gz          -> ao-sim-fabrication-gz.service
```

**Correction 2026-10-05 — an earlier revision of this block showed only eleven of the
twenty-five running containers while describing itself as the whole-container enumeration.**
The eleven were a hand-picked subset with a reason to be looked at, not what the
command returned, so the claim "rests on … the whole-container enumeration rather than on
a hand-picked subset" was false when written. The full output is the block above:
**25 running, 19 managed, 6 unmanaged**. The *conclusion* survives and is now stronger, because the fourteen containers
the earlier block omitted are all accounted for and all managed:

```
$ podman ps -q | wc -l
25
$ for c in $(podman ps --format '{{.Names}}'); do u=$(podman inspect $c \
    --format '{{index .Config.Labels "PODMAN_SYSTEMD_UNIT"}}'); \
    [ -z "$u" ] && echo "$c"; done
ao-sqli3
confident_khayyam
dreamy_rosalind
keen_bhabha
relaxed_tharp
vigorous_shannon
```

**Why this matters beyond tidiness.** The omitted fourteen were not neutral filler — they
include `ao-ingress-payment`, `ao-sales-db`, `ao-webodm-db`, `mastodon-db` and
`ao-fabrication-db`, every one of which carries authoritative data. Had any of them *also*
been unowned, the finding would have been materially worse than "six duplicate GUIs", and my
truncated block could not have shown that. A partial enumeration cannot distinguish "six
leftovers" from "six leftovers and an unowned database", because it never looks.

This is the third instance of the same error class in this one subsection, and it is worth
stating as a rule rather than a footnote: **a claim of completeness is itself a claim, and it
is the one claim an enumeration cannot check for you.** The loop ran over `podman ps` output,
so the command *was* fleet-wide — but a filtered subset of its output was transcribed into
the section, and the completeness claim was attached to the transcription rather than to
the command. Always paste the raw output
and state the denominator (`podman ps -q | wc -l`) next to it, so a reader can see the ratio
rather than trust it. Where a subset is genuinely intended, say so and give both counts.

The **conclusion is unchanged** — exactly six running containers have no service owner,
and they are the four Grafana duplicates and the two Foxglove duplicates. It now rests on a
key that returns a value, and on an enumeration whose output matches its denominator. A
reader should treat any ownership claim anywhere in this section that does not show
`PODMAN_SYSTEMD_UNIT` as unproven.

**Image pinning, measured the same way.** The managed/unmanaged split is not the same as the
pinned/unpinned split, and §4.1 rule 9 is about the second:

```
$ podman inspect ao-grafana ao-sim-fabrication-foxglove \
    vigorous_shannon dreamy_rosalind relaxed_tharp confident_khayyam \
    keen_bhabha ao-sqli3 --format '{{.Name}} {{.ImageName}}'
ao-grafana docker.io/grafana/grafana-oss@sha256:b739cda4b61ba3b90707578b643a22cd851fecf4498e6c6ec2d8f9d622a5d0b2
ao-sim-fabrication-foxglove localhost/foxglove-bridge@sha256:9acc6d4df749ea10f3e97b4b6676a14d864dcb06781ffe7ad551736af0052c87
vigorous_shannon localhost/foxglove-bridge:latest
dreamy_rosalind localhost/foxglove-bridge:latest
relaxed_tharp docker.io/grafana/grafana:11.6.0
confident_khayyam docker.io/grafana/grafana:11.6.0
keen_bhabha docker.io/grafana/grafana-oss:11.6.0
ao-sqli3 docker.io/grafana/grafana-oss:11.6.0
```

Every managed container here is digest-pinned. **Every one of the six unowned ones is not** —
four on a mutable version tag and two on `:latest`. So the unowned set is simultaneously the
unpinned set, which raises the stakes on cleanup: these are the only containers on the host
whose image content can change underneath them without a service restart.

Beyond the YAML's staleness, `podman ps` shows **four Grafana containers that no Quadlet
unit owns**, alongside the one sanctioned `ao-grafana`. All four are leftovers from
2026-10-03 datasource/plugin investigation, two of them from an unnamed probe. Each was
created on 2026-10-03 (`relaxed_tharp` 08:54:41, `confident_khayyam` 09:00:35,
`keen_bhabha` 11:50:02, `ao-sqli3` 11:50:58), all use rootless `pasta` rather than a
bridge network, and none is privileged:

```
$ podman inspect $c --format '{{.Name}} created={{.Created}} nets={{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}} netmode={{.HostConfig.NetworkMode}} priv={{.HostConfig.Privileged}}'
relaxed_tharp     created=2026-10-03 08:54:41 nets= netmode=pasta priv=false
confident_khayyam created=2026-10-03 09:00:35 nets= netmode=pasta priv=false
keen_bhabha       created=2026-10-03 11:50:02 nets= netmode=pasta priv=false
ao-sqli3          created=2026-10-03 11:50:58 nets= netmode=pasta priv=false
ao-grafana        nets=ao-admin ao-reporting-egress netmode=bridge priv=false
```

Why this belongs in §6 rather than §19 only: §6.A.3 requires every containerized GUI to have a
**documented Podman-network membership, listener policy, service owner and least-privilege
identity**. These four have no service owner (no `PODMAN_SYSTEMD_UNIT` label), no declared network
(`pasta` rootless-NAT, per-process — not any of the fourteen registered `ao-*` networks), and
they are **absent from §5.1 group D**, which claims to enumerate all eighteen GUI and workflow
rows. Two of them mount host paths from `/tmp`, and **one of the two is writable**:

```
$ for c in relaxed_tharp confident_khayyam keen_bhabha ao-sqli3; do
    printf '%-20s mounts=[%s]\n' "$c" \
      "$(podman inspect $c --format '{{range .Mounts}}{{.Source}}:{{.Destination}}:rw={{.RW}};{{end}}')"; done
relaxed_tharp        mounts=[]
confident_khayyam    mounts=[/tmp/tmp.2HBNsh7zgo:/probe:rw=false;]
keen_bhabha          mounts=[]
ao-sqli3             mounts=[/tmp/sqli-plugins2:/var/lib/grafana/plugins:rw=true;]
```

`ao-sqli3` is the writable one: it bind-mounts `/tmp/sqli-plugins2` **read-write** over
Grafana's plugin directory, and that host directory contains the `frser-sqlite-datasource`
plugin alongside two Grafana-authored apps.

**Do not over-read this as "an unsigned plugin got in".** The same plugin is deliberately
used by the sanctioned `ao-grafana` — it is the datasource type behind the five
`ALWAYS ON SQLite (…)` datasources in
`config/platform/monitoring/grafana/provisioning/datasources/sqlite-snapshots.yml`. The
difference is **not** which plugin, it is where it comes from and in which direction it
can be written:

```
sanctioned ao-grafana : /ALWAYSON/data/monitoring/grafana-plugins -> /var/lib/grafana/plugins : ro,Z
unmanaged  ao-sqli3  : /tmp/sqli-plugins2                        -> /var/lib/grafana/plugins : rw
```

So the sanctioned path is a curated, repository-adjacent directory mounted **read-only**
(`ro,Z`, and `rw=false` measured). The unmanaged one is a **`/tmp` directory mounted
read-write**, so the plugin set of a running container can be changed by anything that can
write `/tmp`, and it survives into whatever runs next. That is the real defect — writable
plugin supply, not plugin identity. `confident_khayyam` mounts
`/tmp/tmp.2HBNsh7zgo` at `/probe` **read-only** (`"RW":false`); it is a probe scratch
directory, not a writable attack surface.

**Correction 2026-10-04 — an earlier revision of this paragraph said "both writable,
both from `/tmp`". The second half was right and the first was wrong.** Only `ao-sqli3`
is `RW:true`. The reason the error happened is the same class as the label-key error
below: the earlier revision enumerated the two `/tmp` mounts but never asked for the
`RW` flag, so "two mounts from `/tmp`" was silently promoted to "two writable mounts".
Read the flag, do not infer it from the mount's existence.

Mitigating, measured, and worth stating so this is not over-read:

- **No listener is exposed.** `podman port` reports nothing for all four (`map[]`, pasta
  mode), and `ss -ltn` shows no new Grafana port. The only `3000/3001/3002` listeners belong to
  `mastodon-web` (3000), `ao-grafana` (3001) and `ao-metabase` (3002), all loopback-bound.
- **None is privileged**, none is on an `ao-*` network, and none is quadlet-started.

So this is a **conformance and hygiene defect, not an exposure**: unmanaged duplicate GUIs
outside the inventory, one of them with a writable `/tmp` plugin mount feeding it an
unsigned plugin. **Not mine to remediate.** Stopping containers is destructive, touches
another group's running work, and the `/tmp` plugin mount is the subject of the
unsigned-plugin question that §6.A.3 and the OPS group already track. Recorded here and
reported to the operator; no action taken.

**Trap for the next session — two of them, and the first one cost me a whole review
pass.** `podman ps` is sorted by name, so a `grep grafana` against the **image** column
finds these while a search for `ao-grafana` does not. The Foxglove containers are the same
class of leftover: of three `localhost/foxglove-bridge` containers,
`ao-sim-fabrication-foxglove` is the sanctioned, **digest-pinned** one, while
`vigorous_shannon` and `dreamy_rosalind` are unnamed duplicates on the mutable `:latest` tag
with no `PODMAN_SYSTEMD_UNIT` label — the same §4.1 rule 9 pinning concern.

Enumerate by *label presence*, not by image string — but **look the key up first**. The
instinct is `io.podman.annotations.quadlet`, and on this host it is simply not set on
anything: a query using it returns an empty string for all twenty-five running containers,
including every genuinely managed one. An empty result from that key looks like a finding
("nothing has an owner!") and is indistinguishable from "the wrong question was asked." The
correct key is `PODMAN_SYSTEMD_UNIT`, and the self-check is to run it over the whole
container list and confirm that the containers you believe are managed actually come back
with a service name. If every row is empty, the key is wrong, not the fleet.

### 6.A.3.3 An unmanaged host listener serving the pCloud Public Folder (measured 2026-10-05)

*Numbering note: an earlier revision of this file carried two subsections numbered
`6.A.3.2`. This is the later of them and is renumbered `6.A.3.3` so the two do not collide —
the first remains `6.A.3.2` (the unowned containers above), and no existing cross-reference
points at this one.*

**Found while enumerating listeners rather than containers.** §6.A.3 requires every GUI to have
a documented listener policy, and the container inventory above is complete — but an
`ss -ltnp` sweep of the host shows a listener that no container, unit or section accounts for.

```
$ ss -ltnp | grep -vE '127\.0\.0\.1|\[::1\]|Local'
LISTEN 0 5    10.42.0.1:5432     0.0.0.0:*  users:(("socat",pid=5124,fd=5))
LISTEN 0 5    0.0.0.0:8731       0.0.0.0:*  users:(("python3",pid=1010842,fd=3))
LISTEN 0 32   169.254.248.253:53 0.0.0.0:*
LISTEN 0 32   10.42.0.1:53       0.0.0.0:*
LISTEN 0 4096 127.0.0.54:53      0.0.0.0:*
LISTEN 0 1    0.0.0.0:4242       0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=46))
```

Of the six, `10.42.0.1:5432` is the reporting bridge and `0.0.0.0:4242` is MeshChatX (both
already documented elsewhere); `53` is `systemd-resolved`. **`0.0.0.0:8731` is neither, and it
is not named in any section of this document.**

It is a bare `python3 -m http.server` with its working directory set to the pCloud Public
Folder:

```
$ ps -o pid,lstart,etime,args -p 1010842
    PID   STARTED    ELAPSED COMMAND
1010842  Thu Oct  1 20:09:45 2026  3-11:48:07 python3 -m http.server 8731
$ ls -l /proc/1010842/cwd
… -> /media/scottw/1TBSAMSUNGDATA/PCLOUD-PUBLIC/***CURRENT***
$ ls -A '/media/scottw/1TBSAMSUNGDATA/PCLOUD-PUBLIC/***CURRENT***' | wc -l
5
```

Two facts make this a conformance finding rather than a curiosity. First, `python3 -m
http.server` binds `0.0.0.0` by default and **has no authentication of any kind**, so
`--bind 127.0.0.1` is the only thing standing between this and a LAN-wide read. Second, the
path it serves is the one path README §4.1 rule 5 and §4.2 name as *Public* — "Anything in the
pCloud Public Folder, or linked in from it". Serving it over plain HTTP on every interface
makes locally-served public material reachable by anything that can route to this host, which
includes the Wi-Fi segment `192.168.87.0/24` that §3 notes is absent from that section's own
address table. It answers:

```
$ curl -sI http://192.168.87.135:8731/ | head -2
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.14.4
```

**This is a deliberate operator action most likely, and it is not mine to undo.** The elapsed
time shows it has been running since 2026-10-01, so it is not a stray process from this
session's work. It is also **not** a container, so it is absent from §5.1 group D and from every
container inventory in this subsection — a useful reminder that the group-D row set does not
cover host processes.

**Not remediated, deliberately.** Stopping it is destructive to whatever the operator is
serving, and re-binding it is a firewall/public-port decision requiring explicit operator
approval (README §4.1 rules 6 and 13). Recorded here and reported; no action taken. If the
intent was a local preview, the fix is `--bind 127.0.0.1`; if the intent was genuine LAN
sharing, it should be a Quadlet with a declared listener policy per this subsection. **The
SEC/NET groups own the boundary question.**

**Trap worth naming.** `ss -ltnp` shows process names but only for processes this user owns, so
the port→purpose mapping is *incomplete by construction* for system services — `53` and the
socat's own `5432` appear inconsistently for the same reason. Never conclude a listener is
unattributed because its `users:(…)` field is empty; match on the port and address instead.
The converse also held here: `podman ps` would never have surfaced this listener at all.
---

# 7. Public Storefront and Payment Policy

## 7.1 Storefront Boundary

The public storefront is static HTML hosted in the pCloud Public Folder. It carries no
secrets, no local ports and no internal hosts. What it may and must never contain is listed in
§7.1.1.

## 7.1.1 Frontend Website Details

Source is the [HTML-300X3](https://github.com/300x3/HTML-300X3) repository. It publishes as
a **single self-contained `index.html`** — one page, no build-time subpages. The sections
below are regions of that page; each catalog entry is a `data-item` JSON payload rendered
into a modal.

```text
www.300x3.com
└── index.html                       the entire site, ~85 KB, self-contained
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

The publish folder holds exactly two files:

```text
PCLOUD-PUBLIC/***CURRENT***/site/
├── index.html                       the site
└── alwayson-single-topology.html    the topology viewer (ES.2)
```

Catalog entries are modal payloads inside `index.html`, not directories. Every Equipment,
Buildings and Vehicles entry carries the sales action below. `§7.1.2` lists the additional
live views specified for the product modals that are not in this build.

### Order of follow-up, support, and chat links

The order below is deliberate and is the order presented on the page:

1. Follow-up — order status and follow-up links.
2. Support — support request and help links.
3. Chat — AI-assisted support entry point (OpenClaw), which exposes no private
   infrastructure.

Mastodon/community links follow these three.


### Sales-link integration plan

Each catalog modal under Equipment / Buildings / Vehicles gets a sales action
that stays inside the static-site boundary (no secrets, no local ports, no
internal hosts — see Section 7.1 prohibitions):

1. Modal shows product images, parts list / detailed drawings link, pCloud
   folder link, and IPFS digital-asset mark where applicable.
2. A purchase button routes to provider-hosted checkout (PayPal hosted button
   today; Zelle instructions and Coinbase/USDC flow per §7.2 as
   if built) or to a `mailto:300X3@POSTEO.NET` order-request template
   carrying product name, options, and quantity.
3. Checkout completion returns a provider-signed event (or manual
   reconciliation record for Zelle/wire) into the Section 7.3 sales and
   receipt sequence; Corda records the receipt/entitlement state per
   Section 11.
4. No payment-card data, webhook secrets, OAuth tokens, or ledger keys ever
   appear in the static HTML, pCloud folder, or Git history.



The public site may include:

- Product catalog and documentation.
- Hosted payment checkout links.
- Provider-controlled payment buttons.
- Order follow-up links.
- Support links.
- Chat: AI-assisted support entry points that do not expose private infrastructure.
- Mastodon/community links.
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

### 7.1.2 Live HTML Views for Product Modals

These are the **live HTML views on the product modals** of the storefront. This table is the
requirement list for each one, not a status report.

Every view below must satisfy the same boundary as the rest of §7.1: the public
site carries only public content and interactive iframe content from other
servers, and never a local hostname, LAN address, Podman port, or private API
route (§7.1 prohibitions; ES.1 "Static HTML & interactive iframe content from
other servers"). The Instructables view is the straightforward case — it is an
outbound link and a static image. The remaining eight are not, and that is the
substance of the constraint column.

| # | View | Placement | What it shows | Requirement and constraint |
|---|---|---|---|---|
| 1 | **Instructables — fabrication directions** | Bottom-right of **each** product modal | The robot picture, linked to the operator's Instructables member page. **Not** the "Autodesk Instructables" wordmark | No image asset may be fetched or substituted: the operator supplied an Instructables logo SVG and specified *not* to use it |
| 2 | **MeshChatX — network visualizer** | Modal window area | The Reticulum network stack visualizer, live, plus a direct-messaging entry point | MeshChatX is `https://127.0.0.1:18000/`, loopback-only and **not a public ingress** (§9.2.1), so it cannot be iframed. It must be a static export, an approved published view, or an existing external public visualizer |
| 3 | **IPFS/pCloud — route orthotiff** | Maps / digital | WebODM-processed orthotiff along the 300X3 route, the full way around the county, as a **free download including route times and telemetry data** | A public download must carry no internal host, port, or path; check against §4.2 before publication |
| 4 | **Trimble — San Vicente Reservoir point clouds** | Maps / digital | Point-cloud viewing of the reservoir, from a processed WebODM topography | Requires a completed WebODM task for the reservoir (§8) |
| 5 | **LocusMap** | Maps / digital | Downloadable route around San Diego County in the LocusMap format | Format and licensing of the published tile set must be confirmed before any public link |
| 6 | **Mapbox** | Maps / digital | Mapping tiles, San Vicente Reservoir | Requires a Mapbox account and an access token held **outside** the repository. A public browser token is publishable by design; a secret-classified token is not (§4.2, §7.1) |
| 7 | **Mastodon — live forum** | Discussion | A live forum view inside the modal | `mastodon.social` refuses to be framed, and that refusal is enforced by the remote. The local instance UI is `https://127.0.0.1:3300/`, loopback-only, so it is not a substitute without a new approved public entry |
| 8 | **Gazebo/Foxglove — simulation** | Modal, three views | Kitchen; storage/CNC; vehicle | Both origins are loopback-only (sim console `127.0.0.1:8099/sim`, Gazebo portal `127.0.0.1:8765/` and its `/viewer` 3D view, §5.1.2), as is the bridge on `127.0.0.1:8081`. A live embed is a new public entry requiring explicit operator approval under §4.1 rule 6, and depends on §19.1 |
| 9 | **Trimble SketchUp — grid of 3D views** | Modal grid | The SketchUp model views | SketchUp is a desktop/paid service; what may be linked or embedded publicly must be confirmed before use |

**No public port is opened by this section.** Rows 2, 7 and 8 each require explicit operator
authorisation before any live view is published, and none of them may be satisfied by
publishing a loopback address. Which rows are built is status and is recorded in §19.1 and
§19.1.

### 7.1.3 Build state of the nine views, 2026-10-03

**None of the nine views is built.** The storefront in the pCloud Public Folder
carries `index.html` and `alwayson-single-topology.html` only, and no asset,
export, route or embed for rows 1–9 exists in this repository or in the pCloud
site tree. The table above is a requirement list; it is not a status report, and
it must not be read as one.

Row 1 is the only row with no unresolved technical blocker — it is an outbound
link plus one operator-supplied image, and the constraint is a *negative* one
(do not substitute the Instructables wordmark). Rows 2, 7 and 8 are blocked by the
loopback-only rule and each needs an explicit operator authorisation for a new
public entry before it can be built at all. Rows 3, 4 and 5 are blocked on data
that must be produced and licensed first (§8 WebODM tasks, LocusMap tile terms).
Rows 6 and 9 are blocked on an external account or licence confirmation.

This is recorded as **OPEN**. Building rows 2, 7 or 8 would require opening a
public ingress, which is a §4.1 rule 6 stop condition and is reserved to the
operator; none of them was built. This extends, and does not contradict,
the 2026-10-01 note in PAY-05: the three preconditions recorded there still hold,
and the remaining six rows are blocked for the per-row reasons above.

## 7.2 Payment and Settlement Policy

ALWAYS ON does not process, transmit, or store payment-card numbers, CVV
values, or payment-provider secret material in the storefront, sales database,
Corda, Git repository, logs, pCloud Public Folder, or IPFS.

There are three forms of payment processing:

| # | Form | Providers | Intended use | Required control |
|---|---|---|---|---|
| 1 | **Card / PayPal** | Hosted card checkout and hosted PayPal checkout | Standard online transactions | Provider-hosted checkout, signature-verified webhook, no local card handling |
| 2 | **Wire transfer / Zelle** | Wire transfer and Zelle | Approved high-value and direct-to-bank transactions | Manual reconciliation, operator approval, auditable reference record |
| 3 | **Coinbase / stablecoin (USDC)** | Coinbase or similar | Crypto/stablecoin settlement | Documented provider terms, accounting treatment, refund process, and explicit operator approval |

**In scope, decided, and closed as a policy question: PayPal, Zelle and Coinbase/USDC.**
This is the single normative statement of provider scope for the project. It was
settled when §7.2 was written and it is not open. Earlier wording elsewhere that
treats provider selection as undecided — ES.2's "deployable once the provider
decision is recorded (§7.2)" and ST-27's "open on payment-provider selection" —
refers to the *implementation* being gated, not to the choice being unmade, and
is corrected by this statement. Choosing the providers never authorised accepting
a payment: §4.1 rule 14 still requires explicit operator approval before payment
acceptance is enabled, and ST-12 remains the gate for that.

The default payment model is provider-hosted checkout; the provider is
responsible for card capture and authorization. The local payment verifier
accepts only provider-signed webhook events and stores normalized business state.

`ao-ingress-payment` exposes three webhook paths. Zelle publishes no webhook and
returns 501 on any inbound POST, so Zelle is verified by operator reconciliation
against the provider record. Coinbase is verified against the on-chain settlement
record. Bodies are capped at 256 KiB, only a SHA-256 hash and an opaque reference
are stored, and a raw payload is never persisted.

**Measured state of the automated verifier, 2026-10-03.** The verifier in
`scripts/payment/ao-payment-adapter.py` is *not* conformant with either provider
and must not be treated as a working control. Two defects, both proven by running
the adapter, are recorded as **OPEN**:

1. **The signature scheme is one PayPal does not produce.** The adapter computes
   `HMAC-SHA256(secret, transmission_id | transmission_time | raw_body)`. PayPal
   documents a different construction entirely: the message string is
   `transmissionId | timeStamp | webhookId | crc32` — the CRC-32 of the raw body,
   not the body — and it is verified with the RSA public key from the
   `paypal-cert-url` certificate, not a shared HMAC secret. Tested directly: a
   signature built on PayPal's documented message string is **rejected** by
   `verify_paypal`, and only the adapter's own non-standard construction is
   accepted. Consequence: as written the adapter would reject every genuine PayPal
   delivery. This fails closed, so it is not a money-loss risk, but it means no
   PayPal payment can be accepted and §7.2's "signature-verified webhook" control
   does not exist yet.
2. **Coinbase is verified with the PayPal verifier.** `AUTOMATED = ("paypal",
   "coinbase")` and both branches call `verify_paypal`. Proven over HTTP: a
   PayPal-style signed POST to `/webhook/coinbase` returns **200 accepted**, while
   a Coinbase event carrying its own `x-cc-webhook-signature` header returns
   **401**. `COINBASE_WEBHOOK_SECRET` is provisioned into `payment.env` by the
   wallet bridge but is **never read by any code**. The Coinbase path therefore
   admits PayPal-shaped events and rejects all real Coinbase events.

A third defect sits in the normalized event model rather than the verifier: for a
real PayPal `PAYMENT.CAPTURE.COMPLETED` payload the money is at
`resource.amount.value`, which `normalize()` does not read, so `amount_cents`
comes back `None` and the amount is silently lost. For Coinbase the
money-bearing reference is `charge.id`, which `normalize()` also does not read;
it falls through to the top-level **event** id, so the adapter records the event
that arrived rather than the charge being reconciled. **Correction 2026-10-04:** that
reference is **not** empty, because a real Coinbase payload does carry a top-level `id`, so
the adapter does not reject it with 400. The reference it records is simply the wrong one,
which breaks reconciliation without looking like a failure.

These are payment-verification defects. Correcting them changes how money-bearing
events are accepted, so the fix is prepared and reported for operator approval
rather than applied here.

### 7.2.1 Prepared verifier correction, proven offline 2026-10-04

The correction has been **written and proven, and deliberately not applied.** The
live adapter is unchanged — `scripts/payment/ao-payment-adapter.py` still hashes to
`sha256:71a74988b0731695f61a7d56d9580a3c8364a3371906fa333c1784638d399f58`, its
sha256 as measured before this work began, and the running service still answers
`{"ok": true, "enabled": true}` on `127.0.0.1:8899`.

PayPal's construction was re-read from the vendor rather than from the previous
session's notes. Per developer.paypal.com, "Integrate webhooks" → *Self
verification method*, the signed message is
`transmissionId | timeStamp | webhookId | crc32`, where `crc32` is the CRC-32 of
the **original raw body** in decimal, and the signature is checked with the
**RSA public key** from the certificate at `paypal-cert-url`. `webhookId`
arrives in **no header and no body** — it is listener configuration, which is why
the adapter could not have been correct as written.

The candidate was built in `/tmp` from a copy of the live file and proven two
ways. A unit harness generated a throwaway 2048-bit RSA keypair in-process, stubbed
the certificate fetch so the host allowlist and certificate-to-key extraction
still execute, and ran **18 of 18 checks**: the candidate accepts a
PayPal-documented signature and rejects a tampered body, a wrong `webhookId`, a
stale timestamp, an HMAC forgery in the adapter's *current* scheme, and two
non-PayPal certificate URLs. `verify_coinbase()` accepts a genuine Coinbase HMAC
and rejects a PayPal-shaped event.

The acceptance criterion — "A test payment event produces a verified normalized
record" — was then proven **end to end over HTTP** against the candidate on a
spare loopback port in `--dry-run`, so no row could be written:

| Step | Request | Result |
|---|---|---|
| 1 | Genuine PayPal event, PayPal-documented signature | `200 {"accepted": true}` |
| 2 | Same event, one byte of body tampered | `401 signature verification failed` |
| 3 | Genuine Coinbase event, HMAC over the raw body | `200 {"accepted": true}` |
| 4 | PayPal-shaped event to the Coinbase path | `401` — the 200-from-defect-2 no longer happens |
| 5 | Zelle POST | `501` — still manual-reconciliation only |

and the adapter's own log shows the normalized records it produced, carrying the
amount and currency that the live code drops:

```text
DRY-RUN (no DSN): event provider=paypal type=PAYMENT.CAPTURE.COMPLETED
  ref=paypal:3b97c70f1e963687d2da6dbd62f7d7bd amount_cents=50000 currency=USD verified=True
DRY-RUN (no DSN): event provider=coinbase type=charge:confirmed
  ref=coinbase:9871540c485e614b22a7e30fda45d736 amount_cents=1234 currency=USD verified=True
```

**This is prepared, not applied.** Approving it changes which money-bearing
events are trusted to create business state — README §4.1 rule 14 and the first
stop condition. Deployment also needs
`PAYPAL_WEBHOOK_ID` and `COINBASE_WEBHOOK_SECRET` as real configuration, and
`COINBASE_WEBHOOK_SECRET` is currently provisioned but read by nothing. The
operator decision requested is narrower than "fix the verifier": it is whether to
accept PayPal and Coinbase webhooks at all, because the honest consequence of
today's code is that neither provider can complete a payment.

**Independent re-verification, 2026-10-04.** The `/tmp` harness and candidate
referenced above were session-local and no longer exist on disk, so the candidate's
**18/18** result could not be re-run and is **not** re-claimed here. The three
defects it was built to fix *were* re-derived independently against the live file, and
all three reproduce:

- `verify_paypal()` returns `False` for a signature built on PayPal's documented
  message string (`transmissionId|timeStamp|webhookId|crc32`, with `crc32` the
  CRC-32 of the raw body in decimal) and returns `True` only for the adapter's own
  HMAC construction.
- `verify_coinbase` is **not defined** in the file, `AUTOMATED` still contains
  `coinbase`, and line 209 gates **both** webhook paths through the single
  `verify_paypal()`. `COINBASE_WEBHOOK_SECRET` is referenced **zero** times.
- `normalize()` returns `amount_cents: null` for both providers on realistic
  payloads.

One detail the earlier account did not record, found by re-running: **Coinbase's
`amount_cents` is also lost**, not only its `provider_ref`. A real `charge:confirmed`
carries the money at `charge.amount.amount`, which `normalize()` does not read, so it
returns `null` for the amount *and* records the top-level event `id` in place of
`charge.id`. Coinbase events therefore lose both the money and the reconciled
reference. Reproduced with a throwaway in-memory payload only; no secret, no live
request and no row was written.

**Third re-verification, 2026-10-05 — all three defects still reproduce, and a
fourth is added.** The adapter file is unchanged
(`sha256:71a74988b0731695f61a7d56d9580a3c8364a3371906fa333c1784638d399f58`), so
this is a re-measurement, not a re-fix. Re-derived by loading the module and
calling `normalize()` directly, which touches no sink and writes nothing:

```text
$ grep -c 'def verify_coinbase' scripts/payment/ao-payment-adapter.py
0
$ grep -n 'AUTOMATED' scripts/payment/ao-payment-adapter.py
43:AUTOMATED = ("paypal", "coinbase")
208:        if provider in AUTOMATED:
$ grep -rn 'COINBASE_WEBHOOK_SECRET' --include='*.py' --include='*.sh' \
      --include='*.container' --include='*.service' .
./scripts/operations/fetch-kwallet-secret.sh:165:  (writes it; never reads it)

paypal   -> {'provider': 'paypal',   'provider_ref': '',     'amount_cents': None, 'currency': 'USD'}
coinbase -> {'provider': 'coinbase', 'provider_ref': 'evt-1','amount_cents': None, 'currency': 'USD'}
```

**Defect 4, new, and worse than a lost amount: for PayPal the normalized
`provider_ref` is the empty string.** A real `PAYMENT.CAPTURE.COMPLETED` carries its
identifier at `resource.id`, which `normalize()` does not read, so `ref` falls
through every branch to `""`. The sink gate at line 228 is
`if not n["provider_ref"]: reply 400 "missing provider reference"` — so a genuine
PayPal payment is not merely recorded wrongly, it is **rejected outright with 400**
and no record is created at all. The earlier revisions described PayPal as losing
only `amount_cents`; that understates it. For Coinbase the ref is wrong but
present, so it passes the gate and is written wrongly; for PayPal it is absent and
the event is dropped. The two providers fail in different ways, and only one of
them is visible as a wrong value rather than a rejection.

Reading the code explains the shape: `normalize()` looks only at top-level
`id`/`txn_id`/`payment_id`/`transaction_id` and top-level `amount`/`currency`
(lines 97–121). Neither provider puts either field at the top level.

Live behaviour re-confirmed today, rejection-only, with a deliberately
unverifiable signature so nothing could be written:

```text
$ curl -sS -X POST http://127.0.0.1:8899/webhook/coinbase \
    -H "x-cc-webhook-signature: <hmac over a throwaway secret>" --data-binary '<charge:confirmed>'
http=401
{"error": "signature verification failed"}
```

That 401 is *correct* only by accident: the Coinbase path is gated by
`verify_paypal()`, so it rejects a bad signature and would equally reject a good
Coinbase signature. `payment_provider_events` remains at **0 rows**, so no probe created business state.

**Conclusion unchanged:** PAY-02's acceptance criterion is not met. Nothing in
this section was applied to the live adapter.

**How each form is verified.**

| Form | Verification |
|---|---|
| Card / PayPal | The provider's signature on the webhook. **Not implemented conformantly — see the measured state above.** |
| Wire transfer / Zelle | The operator reconciles settlement against the provider record, because those channels publish no webhook |
| Coinbase / stablecoin | On-chain settlement against the wallet record. The webhook path is non-conformant — see the measured state above |

In every case the verification result, provider reference, amount, currency and UTC
verification timestamp are recorded before the transaction is documented in the ledger, so
that the three evidence gates in §11.2.2 resolve to the same correlation record.

Corda is not a payment processor. It never accepts cards and does not replace the payment
provider, banking, tax, consumer-protection, accounting or refund processing. It records
approved receipt, fulfillment, entitlement and provenance state **after** a payment event is
verified or manually reconciled, correlated to the PostgreSQL operational record per
transaction and per serial number (§3.3.b), and it must be queryable by the authorised
reporting services.

## 7.3 Sales and Receipt Sequence

### 7.3.1 Verified implementation state, 2026-10-03

Measured against the running system, not asserted.

**`salesdb` is live and initialized.** The database holds the 14 core tables named
in §15.1 plus `correlation_records`, `sale_contracts`, `sale_contract_lines` and
`sale_evidence` (18 base tables), and all five §15.1 roles exist with login. The
reporting boundary holds: `sales_reporting_role` holds `SELECT` on exactly the
five `v_reporting_*` / `v_corda_entry_readiness` views and on **zero** base
tables, which is the least-privilege property §6 requires. `sales_migration_role`
holds the full 161 grants needed to administer the schema. The relational half of
the sales pipeline is therefore real and correctly separated.

**The receipt-manifest chain works offline, end to end.** A structurally valid
receipt passes `scripts/validation/validate-sale-receipt.sh`; the same receipt with
a `card_number` field added is rejected with exit 13, so the sensitive-field gate
is live and not decorative. `scripts/ledger/build-manifest.sh sales_receipt` then
produces a manifest whose only fields are the content SHA-256, the content size,
an opaque local storage reference, the transaction ID and empty IPFS/pCloud slots —
verified to contain **no** customer, SKU, serial or card token, and its
`content_hash_sha256` equals `sha256(receipt)` exactly. `sign-manifest.sh` attaches
a detached Ed25519 signature over the manifest digest.

**A trap in that chain, measured.** The signature is computed over the digest of
the manifest *before* the signature is embedded into it, so the signature verifies
against the pre-signing digest and **fails against the final file**
(`Signature Verification Failure`, exit 1). That is self-consistent — signing a file
and then mutating it necessarily changes its hash — but there is no in-tree
verifier that knows to blank `signature` and `producer_key_id` before hashing, and
`grep` finds no `verify-manifest` script anywhere. A verifier written naively
against the final file will reject every validly signed manifest. **Whoever builds
the ingest-side verifier must hash the manifest with those two fields removed.**

Submission to `ao-ledger-ingest` is a separate gate and is **not** claimed here:
the gateway is not deployed and `submit-ledger-event.sh` exits 3 at staging, so
nothing left the host.

**The Sales API does not exist.** §7.3 names a "Sales API and sales PostgreSQL"
as the component that turns a verified event into order, receipt, fulfillment and
entitlement state. There is no such service: no Quadlet unit, script or
configuration anywhere in the tree implements one. The only `ao-sales`
containers are `ao-sales-db` and the five Mastodon containers of §15.3, and
`ao-sales` is the network, not an application. **The step between a verified
payment event and an order/receipt/entitlement record is therefore missing**, and
nothing in the current build can create business state from a payment. This is
recorded as **OPEN**.

**The customer-facing PDF email path is half built, and the sending half does not
exist.** PDF generation is proven: `scripts/sales/intake-to-pdf.sh` runs end to
end and emits the intake record, the work order, and a 10-field fillable
AcroForm overlay, each verified at one page. There is **no mail path of any
kind** — `msmtp`, `sendmail`, `mailx`, `mutt`, `swaks` and `s-nail` are all absent
from the host, no SMTP configuration exists, and no script sends anything. The
existing path is deliberately one-way: its own header states "Nothing is sent
anywhere, no payment is taken, no order is created". So the three customer
messages §7.3 owes — purchase-request confirmation, receipt, and work-order
status with expected delivery — can be **generated** as PDFs but **cannot be
delivered**. Installing an MTA or configuring an SMTP relay is a credentials and
egress decision reserved to the operator, so this is **OPEN** pending approval.

**Re-measured 2026-10-05 — still no mail path, and a near-miss worth naming.**
Nothing changed. No MTA is installed (`msmtp`, `sendmail`, `mail`, `mailx`,
`mutt`, `swaks`, `s-nail`, `postfix` all `ABSENT`), no SMTP configuration exists at
`/etc/msmtprc`, `/etc/s-nail`, `/etc/postfix` or `/etc/exim4`, and a repo-wide
search of `*.py`, `*.sh`, `*.container`, `*.service` for
`smtplib|sendmail|msmtp|SMTPServer|--mail-from` returns **nothing**.

The near-miss: `grep -rniE 'smtp|mailx|sendmail|msmtp|email-relay' quadlet/ config/`
returns **15 hits**, which looks like a mail path exists. All of them are Mastodon's
own `config.action_mailer.smtp_settings` block in
`config/mastodon/patches/production.rb` plus a commented-out placeholder in
`config/mastodon/mastodon.env.example` reading *"Cloudflare Email Routing (pending
dashboard enablement 2026-10-22)"*. It is not a path. Checked, not assumed:

```text
$ podman exec ao-mastodon-web env | cut -d= -f1 | grep -iE 'smtp|mail'
(no output)
$ hasEntry ao-mastodon mastodon-smtp-login    -> (false,)
$ hasEntry ao-mastodon mastodon-smtp-password -> (false,)
$ hasEntry ao-mastodon mastodon-smtp-server   -> (false,)
```

Not one Mastodon SMTP variable is provisioned and no wallet entry exists, so
Mastodon's mailer has nothing to send through either. **Do not read those 15 hits as
a partial delivery path** — a future agent grepping for `smtp` will find them and may
conclude the work is half done. It is not; it is an unrelated component's
unconfigured switch.

**PAY-05 re-measured 2026-10-05 — nothing built, and the boundary still holds.**
The published site is still exactly two files, and `index.html` still contains **no**
loopback or LAN address:

```text
$ find '/home/scottw/pCloudDrive/PUBLIC FOLDER/***CURRENT***/site' -type f
.../site/index.html
.../site/alwayson-single-topology.html
count=2
$ grep -oE '(127\.0\.0\.1|localhost|10\.[0-9]+\.[0-9]+\.[0-9]+|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)' index.html
(no output)
```

The three preconditions recorded on 2026-10-01 all still stand. The Instructables
badge is present as a *reference* (`instructables.com/member/SCOTT%20WIDMANN/…`
and an `instructables-badge.png` asset name) but the operator-supplied image itself
is still not supplied. The Mastodon and MeshChatX entries remain **outbound links,
not iframes** — `meshchatx.com` and a `mastodon.social/search?q=300x3` link are the
only occurrences, and the file contains a single dynamic `iframe` template fed by
`d.embed||d.href`, so no view is actually live. That is the correct outcome given
the constraint: nothing is published, and nothing loopback is exposed. PAY-05 stays
**OPEN**; publishing any of these is a new public entry under §4.1 rule 6.

**`ao-ingress-payment` is running but not reachable from the internet.** Both
`http://127.0.0.1:8899/health` and `http://127.0.0.1:8900/health` return
`{"ok": true, "enabled": true}`, and `ss -ltn` confirms all three listeners —
`127.0.0.1:8899`, `127.0.0.1:8900`, `127.0.0.1:15432` — are bound to loopback
only, so nothing is LAN- or internet-reachable. No Cloudflare Tunnel route
targets port 8900, so the approval gate on enabling the public route has not been
opened. Note that `"enabled": true` means the adapter holds a database DSN, which
contradicts ST-12's statement that it "runs with no DSN"; the credential finding
below explains why.

**Credential finding — CORRECTED 2026-10-05. The previous account of this file is
retracted: `payment.env` is now genuinely wallet-produced, and the four `ao-payment`
entries now exist.** An earlier revision of this section recorded that the four
entries did not exist and that `payment.env` had been hand-written outside the
wallet bridge. Re-measured today, that is no longer true:

```text
$ gdbus call --session --dest org.kde.kwalletd6 --object-path /modules/kwalletd6 \
    --method org.kde.KWallet.hasEntry <handle> ao-payment <key> alwayson-ops
payment-db-password                    (true,)
payment-paypal-webhook-id              (true,)
payment-paypal-webhook-secret          (true,)
payment-coinbase-webhook-secret        (true,)
# negative controls, to rule out a hasEntry that always answers true:
payment-paypal-webhook-idX             (false,)
definitely-not-a-key                   (false,)
payment-db-password read from ao-sales (false,)
```

`payment.env` (`~/.local/share/ao-secrets/payment.env`, mode 0600, mtime
2026-10-04 18:38) now carries **four** keys, not one, and re-composing the file
through the bridge reproduces it byte for byte — which is the test the earlier
revision could not have passed:

```text
$ ./scripts/operations/fetch-kwallet-secret.sh "$T/payment.env" payment-credentials
compose exit=0
  key=PAYMENT_DSN                len=106
  key=PAYPAL_WEBHOOK_ID          len=24
  key=PAYPAL_WEBHOOK_SECRET      len=48
  key=COINBASE_WEBHOOK_SECRET    len=48
  PAYMENT_DSN              match=YES
  PAYPAL_WEBHOOK_ID        match=YES
  PAYPAL_WEBHOOK_SECRET    match=YES
  COINBASE_WEBHOOK_SECRET  match=YES
  whole-file: IDENTICAL
```

The temporary file was shredded immediately after the comparison. No secret value
was printed at any point; only lengths, key names and SHA-256 equality were used.

**Two findings survive the correction, and both are still OPEN:**

1. **`payment-db-password` is byte-identical to `sales-db-password`.** The two
   wallet entries hash the same (48 characters each, identical SHA-256 prefix).
   So the "two secrets are one secret" problem the earlier revision identified is
   real and is now located in the *wallet* rather than in a hand-written file — it
   was seeded by copying, not by the bridge. Compromise of the sales-db password
   yields the payment adapter's database access. **The other three entries are
   genuinely distinct** from it (webhook id, PayPal secret, Coinbase secret all
   hash differently), so this is one duplicated value, not a wholesale reuse.
2. **The DSN still grants `sales_migration_role`** — the full schema-admin role —
   to a payment ingress adapter that needs only INSERT on
   `payment_provider_events`. That §14.1 least-privilege deviation is unchanged.

**A staleness finding neither revision recorded.** The running container was
started `2026-10-01 15:08:41`, but `payment.env` was last written
`2026-10-04 18:38` — the container predates the file it reads. Its environment
reflects the older content:

```text
$ podman inspect ao-ingress-payment --format '{{range .Config.Env}}{{println .}}{{end}}' | cut -d= -f1
container GPG_KEY HOME HOSTNAME PATH PAYMENT_DSN PYTHON_SHA256 PYTHON_VERSION
```

`PAYPAL_WEBHOOK_ID`, `PAYPAL_WEBHOOK_SECRET` and `COINBASE_WEBHOOK_SECRET` are
**absent from the live process** even though they are in the file and in the
wallet. The `ExecStartPre` prefetch is non-fatal (`-` prefix), so the unit started
cleanly on the older file and has not been restarted since. The running adapter's
DSN password does match the current wallet value (identical SHA-256 prefix), so
the database path is consistent; the three webhook secrets simply are not loaded.

**Not remediated here.** Rotating a live password, re-scoping a role, or restarting a
payment unit are §4.1 rule 14 and rule 12 stop conditions and require explicit operator
approval. The
remediation proposed for operator approval is unchanged in shape: rotate
`payment-db-password` to a value distinct from `sales-db-password`, grant a
`sales_api_role` limited to the INSERT the adapter performs, and restart
`ao-ingress-payment` so the prefetch loads the three webhook secrets. Recorded as
**OPEN** for the operator.

### 7.3.2 Sequence

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

![Zoom of the full “what actually happens” column of the ES.2 master topology, at readable scale: sale chain, Corda state, CAD and model registry, correlation tuple, the 500GB photogrammetry drive, mapping ingest/process/export, and storage to shelf to robot.](assets/topology-detail-mapping.png)

*Figure 3.3.2 — A **zoom** of the catalogue-to-ledger chain from the ES.2 master
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

**Validated 2026-10-03 — the tree does not match this specification.** The mount itself is
healthy; the folder layout is not. See §8.5.1 for the per-directory result. The tree below
remains the specification; it is recorded as **not yet satisfied**, not as corrected.

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

## 8.4 Persistent Locations

The directory tree in §8.2 fixes the layout of imagery, projects, deliverables and manifests.
These are the locations the tree does not show.

| Data | Location |
|---|---|
| Mapping PostgreSQL | `~/webodm/dbdata`, bind-mounted on `ao-webodm-db` |
| Redis persistence | A named Podman volume on `ao-webodm-broker` |
| Signed manifests | `/ALWAYSON/artifacts/mapping-manifests/` |

`/ALWAYSON/data/mapping/postgres/` and `/ALWAYSON/data/mapping/redis/` are not part of the
design and must stay empty; neither is a bind mount for the running services.

### 8.4.1 Authoritative mapping database — decided 2026-10-03

The §8.4 table said `~/webodm/dbdata`, ST-03 said the app reads `webodm_dev`, and §3.3.1 named
`webodm`. **One name, one location — decided here:**

| Question | Answer |
|---|---|
| Logical database | **`webodm_dev`** |
| Physical storage | **`/home/scottw/webodm/dbdata`**, bind-mounted at `/var/lib/postgresql/data` on `ao-webodm-db` |
| Backup scope | **Included** — `scripts/backup/dump-all-postgres.sh:18` |

Measured:

```bash
$ podman inspect ao-webodm-db --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{end}}'
/home/scottw/webodm/dbdata -> /var/lib/postgresql/data

$ podman exec ao-webodm-db psql -U postgres -tAc \
    "SELECT datname FROM pg_database WHERE NOT datistemplate ORDER BY 1;"
postgres
webodm
webodm_dev

$ grep -n webodm scripts/backup/dump-all-postgres.sh
15:  # mastodon and webodm live in their own containers; the host dump cannot see them.
18:  bash "$C" mapping ao-webodm-db webodm_dev postgres || { echo "FAIL: webodm"; fail=1; }

$ podman inspect ao-webodm-webapp --format '{{range .Config.Env}}{{println .}}{{end}}' \
    | grep -vi 'password|secret|key' | grep -i database
WO_DATABASE_HOST=ao-webodm-db
```

The `webodm` database still exists but is **not** the authoritative one; per ST-03 it was the
duplicate host-cluster database, migrated into `webodm_dev` and the duplicates dropped
2026-09-30 (backups in `backups/duplicate-db-20260930/`). It is retained only as a rollback
artefact. **Any reader of this README must use `webodm_dev`.** `~/webodm/dbdata` is confirmed
correct and needs no change.

**The §8.1/§8.5 requirement that mapping storage sit on the photogrammetry drive is NOT met,
and is recorded as an approved deviation rather than silently dropped.** The PostgreSQL
data directory is on the root filesystem; the drive holds `webodm/{media,projects,nodeodm,temp,logs}`,
which is where the imagery and processing state actually live. Moving a live PostgreSQL data
directory onto an external drive would change service configuration and is an operator decision.
FIELD-11 is closed on the *name and location* question, which is what the item asked; the
drive-residency half remains an open deviation, recorded here and carried forward as a new
**FIELD** item rather than reopening FIELD-11.

Note that §8.5.2 (measured 2026-10-04) makes the drive-residency question harder than it looks,
not easier. The drive is not operator-writable in its intended ownership arrangement: the mapping
directories are group-owned by `alwayson-mapping` and the operator is not a member of that group,
so `mkdir` on the drive fails even for paths that §8.2 requires to exist. Any decision to move
PostgreSQL storage there has to fix that ownership first, or the database will land on a volume
its own operator cannot manage.

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

### 8.5.1 Validation executed 2026-10-03 — mount passes, tree fails

The shipped validator passes:

```bash
$ bash scripts/validation/check-photogrammetry-mount.sh
OK: photogrammetry mount valid: systemd-1
/dev/sdb1; 434G free
rc=0
```

against `config/mapping/photogrammetry-volume.env`
(`PHOTOGRAM_UUID=498597d4-9fc8-42cf-8db7-4e71ede53267`, `PHOTOGRAM_MIN_FREE_GB=100`). UUID
match, mount-marker and free-space checks all pass. The autofs stacking noted in the script
comment is handled correctly.

**But the validator does not check the directory tree at all**, even though §8.5 lists
"Required directories are missing" as a refusal condition. Enumerating §8.2's required paths
directly:

```bash
$ M=/media/scottw/500GBPHOTOGRAM
$ for d in incoming incoming/drone incoming/operator incoming/quarantine validated rejected \
           webodm webodm/media webodm/projects webodm/nodeodm webodm/temp webodm/logs \
           deliverables manifests manifests/intake manifests/processing \
           manifests/ledger-submissions exports exports/pcloud-staging \
           exports/ipfs-staging backups backups/mapping-db retention \
           retention/pending-review retention/eligible-for-archive tmp tmp/processing \
           README.md .mounted-ok; do
    [ -e "$M/$d" ] && printf 'OK      %s\n' "$d" || printf 'MISSING %s\n' "$d"
  done
```

| Result | Paths |
|---|---|
| **Present** | `incoming`, `validated`, `rejected`, `webodm`, `webodm/{media,projects,nodeodm,temp,logs}`, `deliverables`, `manifests`, `exports`, `backups`, `retention`, `retention/{pending-review,eligible-for-archive}`, `tmp`, `.mounted-ok` |
| **Missing — 11** | `incoming/drone`, `incoming/operator`, `incoming/quarantine`, `manifests/intake`, `manifests/processing`, `manifests/ledger-submissions`, `exports/pcloud-staging`, `exports/ipfs-staging`, `backups/mapping-db`, `tmp/processing`, `README.md` |

Ownership is correct at the top level — every directory is `ao-mapping:alwayson-mapping`
(mode `drwxrws---`, group `rwx`, **world has no permission at all**), and `.mounted-ok` is
`scottw:scottw`. The setgid bit `s` is set, so new files inherit the mapping group, which is
the correct arrangement for a shared mapping volume.

**Correction to an earlier claim in this subsection.** A first pass ran
`find "$M" -maxdepth 4 -type d -perm -0002` and reported "empty", concluding no directory is
world-writable. That conclusion was **not sound**: `find` also emitted
`Permission denied` for 8 of the 10 top-level subtrees, and the exit status was 1. The empty
result meant "none of the two readable subtrees", not "none on the drive".
Re-measured honestly:

```bash
$ id -u
1000
$ M=/media/scottw/500GBPHOTOGRAM
$ ok=0; no=0; for d in incoming validated rejected webodm deliverables manifests \
      exports backups retention tmp; do
    [ -r "$M/$d" ] && ok=$((ok+1)) || no=$((no+1)); done; echo "readable=$ok unreadable=$no"
readable=2 unreadable=8

$ ls -la $M
drwxrws--- 13 scottw     ao-mapping        4096 Aug 26 16:57 .
drwxrws---  3 ao-mapping alwayson-mapping  4096 Aug 23 18:31 backups
drwxrws---  2 ao-mapping alwayson-mapping  4096 Aug 23 18:31 deliverables
drwxrws---  4 ao-mapping alwayson-mapping  4096 Aug 23 18:31 exports
drwxrws---  5 ao-mapping alwayson-mapping  4096 Aug 23 18:31 incoming
drwxrws---  5 ao-mapping alwayson-mapping  4096 Aug 23 18:31 manifests
drwxrws---  2 ao-mapping alwayson-mapping  4096 Aug 23 18:31 rejected
drwxrws---  4 scottw     scottw            4096 Aug 23 18:31 retention
drwxrws---  3 ao-mapping alwayson-mapping  4096 Aug 23 18:31 tmp
drwxrws---  2 ao-mapping alwayson-mapping  4096 Aug 23 18:31 validated
drwxrws---  7 scottw     ao-mapping        4096 Aug 23 18:31 webodm
```

**Correction, 2026-10-04 — see §8.5.2.** The setgid paragraph above reads as if setgid makes the
ownership arrangement correct. It does not. Setgid propagates the *parent's group*, and on this
drive that group is `alwayson-mapping`, a group the operator is not in. The depth-2 audit that could
not perform here is explained there, together with a measured root cause (group membership) that
this section previously reported only as "unverified".

The reserved `data/mapping` paths are correctly **absent**, as §8.4 requires:

```bash
$ ls -la /ALWAYSON/data/mapping/postgres/ /ALWAYSON/data/mapping/redis/
ls: cannot access '/ALWAYSON/data/mapping/postgres/': No such file or directory
ls: cannot access '/ALWAYSON/data/mapping/redis/': No such file or directory
```

The `.mounted-ok` sentinel exists and is empty (`size=0`), owned `scottw:scottw` mode
`rw-rw----` — which is correct: it is a presence marker, not a content marker.

`backups/mapping-db` being missing is the consequential one: it is where the §8.4.1 database
backups would land on the drive. This does **not** put the database outside backup scope —
`scripts/backup/dump-all-postgres.sh:18` already dumps `webodm_dev` — but it does mean there is
currently no on-drive copy.

**Two consequences for the reader:**

1. §8.5's claim that WebODM "must refuse to start" on missing directories is **not enforced by
   any shipped script.** `check-photogrammetry-mount.sh` exits 0 on a drive that is 11 directories
   short of its own specification. A green validator run is therefore **not** evidence that §8.2
   holds, and must not be cited as such.
2. Creating the missing directories would change live storage on the photogrammetry drive,
   which is outside what may be done unprompted. **Not created.** FIELD-10 stays
   **open** with this evidence attached — the validation has now been *run and failed*, which is
   strictly more progress than the prior "unvalidated" state.

### 8.5.2 Why the tree cannot be repaired by the operator's own account — measured 2026-10-04

§8.5.1 left two things unresolved: 11 required paths are missing, and depths 2-4 could not be
audited. **Both now have a single measured root cause, and it is a group-membership fault, not a
missing-permission fault.**

Every `ao-mapping`-owned directory on the drive is mode `770` with group **`alwayson-mapping`
(gid 975)**, and there are no ACLs extending it:

```bash
$ stat -c '%n owner=%U group=%G mode=%a' /media/scottw/500GBPHOTOGRAM/tmp
/media/scottw/500GBPHOTOGRAM/tmp owner=ao-mapping group=alwayson-mapping mode=770

$ getfacl -p /media/scottw/500GBPHOTOGRAM/tmp
# owner: ao-mapping
# group: alwayson-mapping
user::rwx
group::rwx
other::---

$ getent passwd ao-mapping
ao-mapping:x:997:975:ALWAYS ON mapping domain service:/home/alwayson-mapping:/usr/sbin/nologin
$ getent group alwayson-mapping
alwayson-mapping:x:975:              # <- NO members at all
```

`ao-mapping` is a **service account** (uid 997), and the directories are owned by it. The
operator's account is a member of the *other* group:

```bash
$ id -nG scottw | tr ' ' '\n' | grep -xE '1001|975'
1001                                # ao-mapping      - member
                                    # 975 absent      - NOT in alwayson-mapping

$ M=/media/scottw/500GBPHOTOGRAM
$ mkdir "$M/tmp/processing"
mkdir: Permission denied
$ sg ao-mapping -c "mkdir -p '$M/tmp/processing'"
mkdir: Permission denied
```

`sg ao-mapping` still fails, which is the diagnostic that matters: group `ao-mapping` (1001)
grants nothing here because these directories are **group-owned by `alwayson-mapping` (975)**
and the `other` class is `---`. `scottw` therefore falls through to `other` and is denied. This
is why §8.5.1 could not traverse 8 of 10 subtrees — **not** "unverified for want of trying",
but a hard denial.

Every one of the 10 missing sub-directories sits under an identically-blocked parent:

| Required path | Parent owner:group | Parent mode |
|---|---|---|
| `incoming/drone` | `ao-mapping:alwayson-mapping` | `770` |
| `manifests/intake` | `ao-mapping:alwayson-mapping` | `770` |
| `exports/pcloud-staging` | `ao-mapping:alwayson-mapping` | `770` |
| `backups/mapping-db` | `ao-mapping:alwayson-mapping` | `770` |
| `tmp/processing` | `ao-mapping:alwayson-mapping` | `770` |

**A second, independent fault is now visible: ownership at depth 2 is inconsistent with depth 1.**
The top level is uniformly `ao-mapping:alwayson-mapping`, but several existing depth-2
directories are owned by `scottw` instead:

```bash
$ stat -c '%n owner=%U group=%G' /media/scottw/500GBPHOTOGRAM/retention/pending-review \
                               /media/scottw/500GBPHOTOGRAM/webodm/media
.../retention/pending-review owner=scottw group=scottw
.../webodm/media              owner=scottw group=ao-mapping
```

Three different ownership patterns (`ao-mapping:alwayson-mapping`, `scottw:ao-mapping`,
`scottw:scottw`) coexist on one volume. The setgid bit is therefore **not** doing what §8.5.1
claimed: setgid propagates the *parent's group*, and here that group is `alwayson-mapping`,
which is exactly the group the operator cannot write through. Setgid is propagating the fault
as consistently as it propagates the intent.

**What this means for the reader:**

- The §8.5 refusal conditions ("required directories are missing", "mapping service ownership
  or permissions are incorrect") are **both genuinely tripped**. The validator passes only
  because it checks neither. This is no longer a theoretical gap in the validator — it is a
  live instance of the gap, on the live drive, today.
- Repairs require `sudo`, and are **group-membership changes**:
  1. `sudo usermod -aG alwayson-mapping scottw` (then re-login), **or**
  2. create the 11 paths as root and `chgrp alwayson-mapping` them.

  Both are operator actions. Neither is a documentation fix, and neither is attempted here.
- **Security posture is correct, which is worth saying explicitly.** Mode `770` with `other=---`
  and no world-writable directory is the *intended* arrangement per §8.2. The operator being
  locked out is the symptom of that policy working, not of it failing. The fix is to add the
  operator to the mapping group, **not** to relax the mode to `777`.

### 8.5.3 Re-verification 2026-10-04 15:59 — both mapping blockers are still live

§8.5.1 and §8.5.2 were measured earlier the same day. Every prerequisite was re-measured before
relying on them. **Nothing has recovered and no claim is weakened.** One *new* finding is
recorded below: the `title:` key the proposal compiler silently requires.

**FIELD-10 — the validator is still green on a tree that still does not satisfy §8.2:**

```bash
$ bash scripts/validation/check-photogrammetry-mount.sh
OK: photogrammetry mount valid: systemd-1
/dev/sdb1; 434G free
rc=0
```

The validator still exits 0. Per §8.5.1 this must **not** be cited as evidence that §8.2 holds.

**FIELD-10 / FIELD-15 — the operator is still locked out, and the database is still off-drive:**

```bash
$ stat -c '%n owner=%U group=%G mode=%a' /media/scottw/500GBPHOTOGRAM/tmp \
      /media/scottw/500GBPHOTOGRAM/webodm/media \
      /media/scottw/500GBPHOTOGRAM/retention/pending-review
.../tmp                      owner=ao-mapping group=alwayson-mapping mode=770
.../webodm/media             owner=scottw       group=ao-mapping       mode=770
.../retention/pending-review owner=scottw       group=scottw          mode=770

$ getent group alwayson-mapping
alwayson-mapping:x:975:            # still no members

$ mkdir /media/scottw/500GBPHOTOGRAM/tmp/processing
mkdir: Permission denied           # rc=1

$ podman inspect ao-webodm-db --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{end}}'
/home/scottw/webodm/dbdata -> /var/lib/postgresql/data
                               # still the root filesystem, not the photogrammetry drive
```

The three-way depth inconsistency (`alwayson-mapping` / `ao-mapping` / `scottw`) persists, and
the repair remains `sudo usermod -aG alwayson-mapping scottw` — **not** a mode change. See §8.5.2
for why loosening to `777` would be a regression against §8.2.

**FIELD-15 — new: the proposal compiler silently requires a `title:` key on `action: new`, and
omitting it produces an unlabelled row in §19.1.** The FIELD-15 proposal rendered with an
**empty Item cell** and the whole proposal body dumped into the criteria cell as raw markdown:

```bash
$ for f in agents/COORDINATION (README UPDATES)/proposals/*.md; do a=$(grep -m1 '^action:' "$f" | sed 's/action: *//'); \
    [ "$a" = new ] && printf '%-22s title:%s\n' "$(basename $f)" "$(grep -cm1 '^title:' "$f")"; done
field-FIELD-15.md   title:0        # <- mine
ops-a-OPS-35.md     title:0
sec-SEC-04.md       title:0
spec-NET-51.md      title:0
spec-OPS-35.md      title:0
spec-OPS-36.md      title:0
                                     # 6 of 6 omit it

$ # every action:new row in 19.1 with an empty Item cell:
EMPTY ITEM CELL: NET-51
EMPTY ITEM CELL: FIELD-15
EMPTY ITEM CELL: OPS-36
EMPTY ITEM CELL: OPS-35
```

Cause, measured in `scripts/orchestration/compile-proposals.py` lines 133-136:

```python
row = (... % (item, esc(p.get("title", "")), esc(p.get("body"))))
                         ^^^^^^^^^^^^^^^^^^^^^^ absent key -> empty cell, no warning
```

`p.get("title", "")` returns `""` for a missing key, and `proposals/README.md` never documents
`title:` as a field (`grep -n 'title:' proposals/README.md` → no match). **So this is a
documentation gap in a shared file, not a mistake unique to one proposal** — four others
hit it identically. **The `new` action cannot render a usable row without it.** `title:` was
added to the FIELD-15 proposal; the other five belong to their own sections and are reported rather
than edit them. This is a **cross-session finding for the compiler session**, not a FIELD item,
so no new FIELD ID is taken for it.

**Also worth the compiler's attention:** §19.1's FIELD group header still reads *"14 items, all
Open"* while the block now holds **9 open rows** (`FIELD-15, 01, 02, 03, 06, 07, 09, 10, 14`) plus
6 closed in §19.2 (`04, 05, 08, 11, 12, 13`). The header is not recomputed on close or on `new`.

**Not attempted.** No directory created, no group membership changed, no data directory moved,
no profile edited. All remain operator decisions under §4.1 rule 12.

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

**3D objects come and go; the data about them must not.** The identity, the
registry record, and the ledger references must remain consistent for the life
of the object, and must be able to exist in either of two states:

- **With no 3D object at all.** A `model_object_id` may exist with no current
  revision — for example before any geometry is authored, or after every
  revision has been retired. The registry row, its links, and its Corda
  references stay valid and remain the authoritative history.
- **With a connection to a new object.** A replacement object receives its own
  `model_object_id`, and `model_object_links` records the relation between the
  two. The original identity is never overwritten or reused.

Consequently, no business record may depend on the presence of a 3D file.
Serial numbers, receipts, entitlements, manifests, and Corda state reference the
`model_object_id` and its revisions, never a file path. `content_hash_sha256`
is an attribute of a revision, not of the object, and a revision whose artifact
is no longer on disk stays in the registry as a `retired` record with its hash
intact.

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

The model registry is a PostgreSQL schema equivalent to:

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
- A model object may have many revisions, but exactly one is the current revision.
- A physical serial number may have many model revisions over its lifetime.
- A receipt may reference many model objects or serials through the link table.
- A model relationship records `event_timestamp_utc` and its source.
- A retired revision is preserved and marked `retired`, never reused.
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
### 8.5.4 Re-verification 2026-10-04 17:52 — both mapping blockers unchanged

§8.5.2 and §8.5.3 are dated earlier today. Re-measured at **17:52**. Nothing has changed.

**The shipped validator still passes on a drive that fails its own specification.** This is
the standing FIELD-10 finding and it is unchanged:

```bash
$ bash scripts/validation/check-photogrammetry-mount.sh
OK: photogrammetry mount valid: systemd-1
/dev/sdb1; 434G free
rc=0
```

The mount is genuinely present and correct:

```bash
$ findmnt -no SOURCE,FSTYPE,LABEL /media/scottw/500GBPHOTOGRAM
/dev/sdb1 ext4   500GBPHOTOGRAM
```

**The FIELD-15 ordering gate is still shut.** §8.5.2's finding was that any move of the
mapping database onto this drive must fix group membership *first*. That has not happened —
`alwayson-mapping` still has no members, the operator is still not in it, and the paths §8.2
requires still cannot be created:

```bash
$ getent group alwayson-mapping
alwayson-mapping:x:975:                 # no members
$ id -nG scottw
scottw adm tty dialout cdrom sudo dip plugdev input lpadmin sambashare ao-mapping
                                            # 975 absent
$ mkdir /media/scottw/500GBPHOTOGRAM/tmp/processing
mkdir: Permission denied
```

**The mapping database is still off the drive**, which is FIELD-15's premise:

```bash
$ podman inspect ao-webodm-db --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'
/home/scottw/webodm/dbdata -> /var/lib/postgresql/data
```

The database is named `webodm` and the role is `postgres` (names only, no values read):

```bash
$ podman inspect ao-webodm-db --format '{{range .Config.Env}}{{println .}}{{end}}' \
    | grep -vi 'password\|secret\|key' | grep -iE 'POSTGRES_DB|POSTGRES_USER|PGDATA'
POSTGRES_HOST_AUTH_METHOD=trust
POSTGRES_DB=webodm
POSTGRES_USER=postgres
PGDATA=/var/lib/postgresql/data
```

**§8.4.1's decision stands unexecuted.** The name and location are decided (`webodm` at
`/home/scottw/webodm/dbdata`) but the database has not been moved to the photogrammetry
drive, because doing so is an operator decision under §4.1 rule 12 *and* is gated behind the
group-membership fix above.

**Nothing was touched.** No `mkdir`, no `chgrp`, no `usermod`, no database stop, no mount
change. Creating directories on the operator's validated drive without approval is exactly the
rule 2/rule 12 case.

**Second-level directories are missing, and they are exactly the ones the operator cannot create**

### 8.5.5 Re-verification 2026-10-05 07:57

**§8.5.1 and §8.5.3 are now partly stale: directories have appeared since 2026-10-03.**
`incoming/`, `manifests/`, `exports/`, `backups/`, `tmp/`, `webodm/` and `retention/` were all
modified `Oct 4 17:30`. The compiler should not render §8.2's "the tree does not match this
specification" as meaning *nothing* was created — a substantial part now exists. **FIELD-10
stays OPEN.** What changed is the size of the gap, not its existence.

Current state against the §8.2 spec, measured by enumerating rather than assuming:

| Spec directory | State |
|---|---|
| `incoming/`, `validated/`, `rejected/`, `deliverables/`, `manifests/`, `exports/`, `backups/`, `tmp/` | present (top level) |
| `webodm/{media,projects,nodeodm,temp,logs}` | **all five present** — the only complete subtree |
| `retention/{pending-review,eligible-for-archive}` | present |
| `incoming/{drone,operator,quarantine}` | **MISSING** |
| `manifests/{intake,processing,ledger-submissions}` | **MISSING** |
| `exports/{pcloud-staging,ipfs-staging}` | **MISSING** |
| `backups/mapping-db` | **MISSING** |
| `tmp/processing` | **MISSING** |

That is 10 of the 18 specified directories missing. Every one of the ten is a **second-level**
directory, and second level is where the repair fails.

**The precise mechanism, which §8.5.2 described but did not enumerate.** Every missing
directory sits under a parent owned `ao-mapping:alwayson-mapping` with mode `770`. The operator
`scottw` is in group `ao-mapping` (gid 1001) but **not** in `alwayson-mapping` (gid 975), and
`alwayson-mapping` has **no members at all**:

```text
$ getent group alwayson-mapping ao-mapping
alwayson-mapping:x:975:
ao-mapping:x:1001:scottw,ao-mapping
```

So for those parents the operator is neither the owner nor in the owning group, and `other` is
`---`. Measured, not inferred — creation was attempted and refused:

```text
$ M=/media/scottw/500GBPHOTOGRAM
$ for d in incoming/drone incoming/operator incoming/quarantine manifests/intake \
           manifests/processing manifests/ledger-submissions exports/pcloud-staging \
           exports/ipfs-staging backups/mapping-db tmp/processing; do
      printf '%-30s ' $d
      if mkdir $M/$d 2>/dev/null; then echo MKDIR-OK; rmdir $M/$d; else echo MKDIR-DENIED; fi
  done
incoming/drone                   MKDIR-DENIED
incoming/operator                MKDIR-DENIED
incoming/quarantine               MKDIR-DENIED
manifests/intake                 MKDIR-DENIED
manifests/processing             MKDIR-DENIED
manifests/ledger-submissions     MKDIR-DENIED
exports/pcloud-staging           MKDIR-DENIED
exports/ipfs-staging             MKDIR-DENIED
backups/mapping-db               MKDIR-DENIED
tmp/processing                   MKDIR-DENIED
```

The same command **succeeds** under the two parents the operator can write, which is the
control that proves the cause is ownership and not a broken mount:

```text
$ mkdir $M/webodm/projects/__fieldtest && rmdir $M/webodm/projects/__fieldtest   # OK, cleaned up
$ [ -r $M/webodm ] && [ -x $M/webodm ]   # accessible
```

**This confirms and sharpens §8.5.2's ordering claim with a number.** The repair is
`usermod -aG alwayson-mapping scottw` followed by the ten `mkdir`s — two steps, in that order,
and the first is privileged. `sudo -n true` returns "interactive authentication is required",
so neither step can be performed here. §8.2's tree cannot be satisfied by the operator's
own account until that group membership exists.

**Two findings the compiler should not lose.**

1. **The mount validator passes while the tree it guards fails.** `check-photogrammetry-mount.sh`
   returns `OK: photogrammetry mount valid: systemd-1 /dev/sdb1; 434G free`, `rc=0`. It
   validates the *mount* and never inspects the §8.2 tree, so a green result from it is **not**
   evidence for FIELD-10 and must not be quoted as such.
2. **§8.2's "no directory may be world-writable" holds.** `find $M -maxdepth 2 -type d -perm -0002`
   returns nothing. That clause of the spec is satisfied; only the directory *list* is not.

**Why this matters for FIELD-15.** FIELD-15 asks whether the mapping database should move onto
this drive. The measurement above is the answer to its precondition: **the drive is not yet a
place the operator can manage.** Moving PostgreSQL storage onto a volume whose intended operator
cannot create, read or inspect it would convert a documented deviation into an unmanageable one.
The group fix must land first. This is now an ordering constraint with a measured gate, not a
caution.

**The probe file cannot be confirmed gone, and that is not claimed.** A
`touch` inside `incoming/` reported `setting times: Permission denied` and `stat` is refused,
`ls` or `rm` the path afterwards — the directory is unreadable to me. **Treat a possible
zero-byte `/media/scottw/500GBPHOTOGRAM/incoming/.fieldprobe` as present until an operator
checks and removes it.** See housekeeping in the proposals.

**Nothing was changed.** Every probe was a create-then-delete attempt that either succeeded and
was reversed, or was refused by the kernel. No directory on the drive was created, chgrp'd or
removed. `usermod` was not run and no `sudo` was invoked.

---

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
| WebODM web service | Mapping / `ao-mapping` | `127.0.0.1:8000` — **loopback only** | Loopback only; LAN addresses refuse and `ao-mapping` remains `Internal=true`. The UI opens directly at `http://127.0.0.1:8000/` without an SSH tunnel | `ao-webodm-web.container` |
| Reticulum transport | Field / Reticulum | Reticulum-configured interfaces | No HTTP listener | Embedded MeshChatX backend |
| Mastodon local UI proxy | Sales / local operator access | `https://127.0.0.1:3300` — **loopback only, self-signed TLS** | Loopback only; LAN addresses refuse | `scottw` user service (`mastodon-local-proxy.service`) |

MeshChatX uses its self-signed local certificate; clients must use HTTPS and accept it. The
MeshChatX port is not a public ingress and must not be published through Podman, nginx,
Cloudflare or a router. WebODM and MeshChatX must not share a listener, and the desktop
launcher and watchdog must both use port `18000` — changing one without the others is a
configuration error.

The Mastodon local UI proxy on `https://127.0.0.1:3300` also uses a self-signed certificate
and the same acceptance applies. It is loopback-only and not a public ingress.

It exists because upstream Mastodon hardcodes `config.force_ssl = true` and
`https = Rails.env.production?`, neither switchable by environment variable, so Rails always
emits absolute `https://` asset URLs. Over plain HTTP the browser's request for a
render-blocking stylesheet never completes and the page hangs, even though every URL answers
curl in milliseconds. The proxy terminates TLS on loopback and injects
`X-Forwarded-Proto: https`. `mastodon-web` itself is unmodified, and federation through the
Cloudflare Tunnel is unaffected.

**The certificate is pre-trusted — there is no warning to click through.** It is
installed as a trusted CA (`CT,C,C`) in both `~/.pki/nssdb` (shared NSS store)
and the snap Firefox profile's `cert9.db`. Re-import with:

```bash
certutil -d sql:$HOME/.pki/nssdb -A -n "ALWAYS ON local Mastodon" \
  -t "CT,C,C" -i /ALWAYSON/secrets/mastodon/mastodon-local.crt
certutil -d sql:$HOME/.snap/firefox/common/.mozilla/firefox/<profile> \
  -A -n "ALWAYS ON local Mastodon" -t "CT,C,C" \
  -i /ALWAYSON/secrets/mastodon/mastodon-local.crt
```

Firefox must be **closed** before its `cert9.db` is modified. Regenerating the
certificate requires repeating both commands.

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
The host uses two separate raw-LoRa/Reticulum interfaces. This is the single table for both.

| Radio | Hardware | Configured band | Operational state | Remaining observation |
|---|---|---:|---|---|
| `PEOPLE-RADIO` | Heltec LoRa 32 V3, SX1262, RNode firmware 1.85 | 915 MHz | Functional | Characterize feedback observed on this band |
| `DRONE-RADIO` | Heltec LoRa 32 V3, SX1262, RNode firmware 1.85 | 917 MHz | Functional | Characterize feedback observed on this band |

Both RNodes initialize successfully in the active MeshChatX process, confirming device
detection, serial access, and RNode configuration. RF feedback is observable on both bands.

Bandwidth, spreading factor, coding rate, transmit power, and mode are recorded only in the
version-controlled US915 radio profiles in §9.4, not in this README. The two frequencies and
airtimes intentionally separate the public radio from the private drone radio; they must not be
treated as interchangeable or combined into one RF channel without an approved frequency plan.

Host configuration lives under `/home/scottw/.reticulum/`; MeshChatX runs headlessly at
`127.0.0.1:18000` with its Reticulum runtime initialized from `/home/scottw/.reticulum/config`,
and MeshChatX identity, repository, and application state under
`/home/scottw/.reticulum-meshchatx/`.

“Feedback” is an operator observation, not a diagnosed fault. Candidate categories are
self-feedback, nearby RF activity, interference, harmonics, spurious transmission, antenna
coupling, and reflected energy. Do not change power, frequency, bandwidth, spreading factor,
coding rate, antenna, or transmit mode until the source and severity are measured.

Both CP2102 bridges expose the same USB serial descriptor
`Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001`, so device identity must be resolved
through the stable PCI/USB `by-path` location and the recorded SX1262 MAC address. The USB
serial descriptor alone is not a unique radio identity.

### 9.2.2 What each radio is for

The two radios are not interchangeable and are not both "chat". Each has one job:

| Radio | Purpose | Ties to | Notes |
|---|---|---|---|
| **PEOPLE-RADIO** (915 MHz / 125 kHz / SF7 / 17 dBm) | **Raw-LoRa human communication** — public human chat | **MeshChatX** | Carries MeshChatX text over raw LoRa into the local chat service. This is the human communication path over Reticulum; it is **not** LoRaWAN (§9.4.3). |
| **DRONE-RADIO** (917 MHz / 250 kHz / SF7, hidden) | **Local QGroundControl missions** to the drone, over a **dedicated RNS-enabled connection** | **QGroundControl** | Carries a dedicated RNS-enabled QGC link to the **QGC session on the Raspberry Pi 5 drone**, so **missions can be updated midflight**. Radio only: no IP path, no mTLS. |

`QGroundControl` therefore has two roles: it plans and watches missions from the desktop,
and it receives **midflight mission updates** relayed by DRONE-RADIO to its session on the
Pi5. PEOPLE-RADIO has no relationship to the drone.

### 9.2.3 Bounded-ratchet persistence — classified 2026-10-03, **CLASSIFICATION REVERSED 2026-10-05**

> **READ THIS BEFORE THE PARAGRAPHS BELOW.** Everything under this heading up to the
> 2026-10-05 entry was written on 2026-10-03/04 and **two of its claims are now known to be
> wrong**: (1) the `umsgpack` fault is *not* demonstrably historical — the count quoted here
> **reproduces in no retained log today**, so the evidence it rested on was rotation-fragile;
> (2) the causal hypothesis withdrawn below is **re-supported** by fresh data. The
> 2026-10-05 entry supersedes both. FIELD-05 is reopened.

The `umsgpack` error named in FIELD-05 was classified as **historical and resolved**. It is not
occurring. Counts across the whole rotated log set:

```bash
$ cd ~/.reticulum-meshchatx/logs
$ for f in meshchatx.log.2 meshchatx.log.1 meshchatx.log; do
    echo -n "$f: "; grep -c umsgpack "$f"; done
meshchatx.log.2: 12364
meshchatx.log.1: 0
meshchatx.log: 0
```

**2026-10-05: the 12,364 count no longer reproduces in any file, and the error text is absent
everywhere.** Re-measured binary-safe, across all four retained logs:

```bash
$ for f in meshchatx.log.3 meshchatx.log.2 meshchatx.log.1 meshchatx.log; do
    echo "$f: umsgpack=$(grep -ac umsgpack $f)  'No module named'=$(grep -ac 'No module named' $f)"
  done
meshchatx.log.3: umsgpack=0  'No module named'=0
meshchatx.log.2: umsgpack=0  'No module named'=0
meshchatx.log.1: umsgpack=0  'No module named'=0
meshchatx.log:   umsgpack=0  'No module named'=0
```

`No module named 'umsgpack'` — the exact string quoted below — **occurs in no retained log.**
The segment holding those errors has been overwritten by rotation since 2026-10-04. **Reason the
earlier claim was wrong: a count taken from a rotated log filename is not durable evidence,
and is easily read as though it were.** A grep count of 0 in the *current* file proves only that
the current file has none, which is a much weaker claim than "historical and resolved".

All 12,364 occurrences were the identical line, and the block terminated immediately before a
restart — the last error is directly followed by new startup banners:

```text
ERROR:meshchatx.rns_ratchet_persist:Bounded ratchet persist failed: No module named 'umsgpack'
2026-09-24T16:29:19.004Z [electron] Download path set to /home/scottw/Downloads/MeshChatX
2026-09-24T16:51:04.140Z [electron] Download path set to /home/scottw/Downloads/MeshChatX
2026-09-24T16:51:04.672Z [electron] Found executable at: /tmp/.mount_ReticuDLBdLn/resources/backend/ReticulumMeshChatX
INFO:meshchatx.rns_ratchet_persist:Installed bounded RNS ratchet persist worker
```

Classification: a packaging defect in an AppImage build whose bundled Reticulum lacked
`umsgpack`, so the bounded-ratchet persist worker could not serialise. It stopped at the
2026-09-24 rebuild and has never recurred. **Accepted as a historical bounded-ratchet defect.**

**A different and still-live defect is now present, and it is not the same bug.** The current log
records failures with a different cause — `[Errno 9] Bad file descriptor` — and they are not
random. Each one lands in the same second as a `DRONE-RADIO` interface teardown:

```bash
$ grep -o 'Bounded ratchet persist failed: .*' meshchatx.log | sort | uniq -c
      7 Bounded ratchet persist failed: [Errno 9] Bad file descriptor

$ grep -c 'RNodeInterface\[DRONE-RADIO\] experienced an unrecoverable error' meshchatx.log   # 2748
```

```text
2026-10-03 18:04:08 [Error] The interface RNodeInterface[DRONE-RADIO] experienced an unrecoverable error and is now offline.
2026-10-03 18:04:08 [Error] Reticulum will attempt to reconnect the interface periodically.
ERROR:...rns_ratchet_persist:Bounded ratchet persist failed: [Errno 9] Bad file descriptor
```

**CORRECTION 2026-10-04: this cadence figure is wrong by a factor of ~150.** The
"roughly every 30–60 minutes" cadence above was derived from the timestamps of the
*ratchet persist failures* — there are only 13 of those — not from the teardowns
themselves. Counting the teardowns directly:

```bash
$ grep -c 'unrecoverable error' ~/.reticulum-meshchatx/logs/meshchatx.log        # 994
$ grep -c 'Bounded ratchet persist failed' ~/.reticulum-meshchatx/logs/meshchatx.log # 0
$ grep -ch 'unrecoverable error' ~/.reticulum-meshchatx/logs/meshchatx.log{,.1,.2,.3}
994 / 7800 / 2389 / 29                                                        # 11,212 total
```

**2026-10-05: the `0` on line two of that block was TRUE when written, and is no longer true.**
It now reads **4**. The logs are binary to `grep`, so the figure is re-checked with `grep -ac` to rule out a
counting artefact — `grep -c` and `grep -ac` both return 4, so the increase is real, not a
truncation effect. The four are new occurrences dated today; the withdrawal below was sound on
2026-10-04 and is superseded by §9.2.3.1 because the association it denied has since held
again. The teardown counts on lines one and three are unaffected — the cadence conclusion
below stands. (The current log's `DRONE-RADIO` teardown count is now 3889, up from 994 as
measured on 2026-10-04: the figure grows continuously because the radio is still retrying.)

**`DRONE-RADIO` is not dropping hourly — it is retrying roughly every 7 seconds and has
never recovered.** Consecutive events at `07:25:38`, `07:25:44`, `07:25:51`, `07:25:57`.
The conclusion of the paragraph above still stands, and in fact hardens: a link that dies
every *seven seconds* is even less a link one could prove a midflight mission update over.
Only the period was wrong, not the judgement.

**The causal hypothesis above is also not supported, and is withdrawn.** It rested on
"every occurrence is adjacent to a teardown". That is true of the 13 `[Errno 9]` persist
failures, but those were in `meshchatx.log.1`/`.3`; the *current* log has 994 teardowns and
**zero** persist failures, so the association does not hold in the log where the fault is
actually happening now. A shared-fd mechanism remains plausible in principle, but on this
evidence it is **unproven and now positively unsupported**, and the far simpler reading is
the one §9.5.2 reaches: the board is enumerated but does not answer the RNode detection
handshake, and the `[Errno 9]` persist errors are a consequence of the port closing, not a
cause. Recorded rather than deleted, per the rule against editing history quietly.

Original hypothesis, now **withdrawn** on the evidence above and retained only so the
correction is auditable: it attributed both the `[Errno 9]` persist failures and the cadence
to a shared file descriptor — the persist worker writing through an fd it does not own, which
fails when Reticulum tears the interface down and closes the port. That mechanism was never
proven (no stack trace is logged) and is now positively unsupported, since the log where the
fault actually recurs contains no persist failures at all.

The `DRONE-RADIO` fault is a detection failure, not a permissions problem — the port is
openable by the service account:
The `DRONE-RADIO` fault itself is a detection failure, not a permissions problem — the port is
openable by the service account:

```bash
$ id
uid=1000(scottw) ... groups=...,20(dialout),...
$ python3 -c "import os; os.close(os.open('/dev/ttyUSB0', os.O_RDWR|os.O_NOCTTY))"   # OPEN OK
```

**Restart-persistence evidence for the historical defect** (required by FIELD-05): the ratchet
file has not been rewritten since before the current process started.

```bash
$ ps -o pid,lstart -p 840861
    PID STARTED
 840861 Sat Oct  3 16:57:27 2026

$ stat -c '%n mtime=%y' \
    ~/.reticulum-meshchatx/identities/*/lxmf_router/lxmf/ratchets/*.ratchets
...080371582f297fc33dd513b3f9d18c3a.ratchets mtime=2026-10-03 09:51:34 -0700
```

File mtime `09:51:34` precedes process start `16:57:27` by seven hours, and a 20-second
re-sample showed an unchanged sha256 — the persist worker has written nothing since. Ratchet
state is therefore **not** being flushed in the running instance.

No corrective action was taken. Repairing it means touching the serial device and the running
Reticulum stack, which is a stop condition.

#### 9.2.3.1 Classification reversed 2026-10-05 — the persist fault is LIVE, and it tracks
#### the `DRONE-RADIO` teardown

**The 2026-10-03 classification above is withdrawn. FIELD-05 is reopened.** Two separate things
were wrong with it, and the second is the one that matters operationally.

**1. The `umsgpack` evidence does not survive.** The 12,364 count and the string
`No module named 'umsgpack'` reproduce in **no retained log** (counts above). The classification
"historical packaging defect, never recurred" rested entirely on a count taken from a rotated
filename, and rotation has since destroyed the segment it referred to. It cannot now be proved from the current file; the
`umsgpack` fault ever stopped, only that its evidence is gone.

**2. The persist fault is still happening, today.** A withdrawal recorded on 2026-10-04 covered the
shared-file-descriptor explanation, on the grounds that the current log had 994 `DRONE-RADIO`
teardowns and **zero** persist failures. That reading was correct on the day — but the zero was a
*count from an earlier point in a live log*, and the current log is still being appended to. It
now holds four, and the association is exact:

```bash
$ grep -ac 'Bounded ratchet persist failed' meshchatx.log
4                                   # in the current log, i.e. today
$ grep -a 'Bounded ratchet persist failed' meshchatx.log | tail -1
ERROR:meshchatx.rns_ratchet_persist:Bounded ratchet persist failed: [Errno 9] Bad file descriptor
$ grep -an 'Bounded ratchet persist failed' meshchatx.log | cut -d: -f1
8049
12279
16470
19670
```

Every occurrence, with its surrounding lines — note the same second, and the reconnect that
immediately follows:

```text
[2026-10-05 03:15:33] [Error]  The interface RNodeInterface[DRONE-RADIO] experienced an unrecoverable error and is now offline.
[2026-10-05 03:15:33] [Error]  Reticulum will attempt to reconnect the interface periodically.
ERROR:...rns_ratchet_persist:Bounded ratchet persist failed: [Errno 9] Bad file descriptor
[2026-10-05 03:15:33] [Error]  Error while reconnecting port, the contained exception was: 'NoneType' object cannot be interpreted as an integer
[2026-10-05 03:15:38] [Notice] Opening serial port /dev/serial/by-path/pci-0000:05:00.0-usb-0:1:1.0-port0...
```

Identical shape at `04:59:53`, `06:42:08` and `07:59:53`. Counts of this live error per file,
oldest first: `.3` 2, `.2` 13, `.1` 9, current 4.

**Why this is the same defect and not a new one.** `[Errno 9] Bad file descriptor` on a persist
write, firing in the same second as an interface teardown, is consistent with **the ratchet
state file's descriptor being closed as a side effect of the `DRONE-RADIO` reset** — the
hypothesis withdrawn on 2026-10-04. That withdrawal was sound on the evidence available at
the time; it is superseded because that evidence was a snapshot of a file still being
written to. The hypothesis is reinstated as the **leading hypothesis, not a proven
mechanism**: the code path has not been traced and no stack trace is logged.

**The operational consequence, which is the point.** The persistence subsystem is failing daily
and **downstream of the same broken board** that blocks FIELD-01/02/03/06. One board repair may
clear both. That is a stronger result than the closure recorded on 2026-10-04, which noted this
error and then wrote it off as "a different bug, not covered by closing FIELD-05" — which left a
real daily fault with no open item against it.

### A count must be trusted only as far as its scope

Two distinct mistakes arise from trusting a count more than its scope:

1. **A count taken from a rotated log filename.** Rotation destroys the segment it
   described, so a `grep -c` against a file that will be overwritten answers "what is
   in this file now" — not "what is true of the fault". The tell is that the count
   moves when the file is renamed: the `umsgpack` figure lived in `meshchatx.log.2` in
   one pass and `meshchatx.log.3` in the next. **A count that moves when you rename
   the file is not measuring the fault.**
2. **A count of a live, still-growing log**, read as a stable zero. It is correct only
   on the day it was taken and is superseded later; today's non-zero result must not
   be dismissed as a measurement artefact.

**On the binary-grep worry, checked rather than assumed:** these logs *are* binary to
`grep` (`binary file matches`), which is a real trap for anyone counting here. It does
**not** explain the discrepancy — `grep -c` and `grep -ac` both return 4 on the current
log. Use `grep -a` for safety, but a count difference here is not a truncation effect.

**Read-only inspection.** No service restart, no file touched.

## 9.3 Operational Security

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
private, and anyone auditing exposure should expect `:4242` to be visible on the LAN. For
contrast, PostgreSQL is explicitly `5432/tcp DENY` from any non-loopback source, and KDE
Connect `:1716` is denied too.

### 9.3.1 Listener reachability decided 2026-10-03

Re-measured rather than assumed:

```bash
$ ss -ltnp | grep -E '18000|4242'
LISTEN 0 128  127.0.0.1:18000  0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=17))
LISTEN 0 1    0.0.0.0:4242     0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=46))

$ timeout 5 bash -c 'exec 3<>/dev/tcp/127.0.0.1/4242'     && echo loopback-OK
loopback-OK
$ timeout 5 bash -c 'exec 3<>/dev/tcp/192.168.87.135/4242' && echo lan-OK
lan-OK
```

**Decision: `0.0.0.0:4242` stays LAN-reachable and is approved as designed.** It is a Reticulum
protocol listener inside a `user` unit, not a public ingress; §4.1 rule 4 governs *public* ports
and this is not one. The field radios address the mesh by radio, not by TCP, so loopback-only
binding would break the design without reducing exposure.

One caveat is recorded rather than glossed: the §9.3 table claims
`4242/tcp ALLOW Anywhere` is an explicit UFW allow. That claim could **not** be re-verified —
`/etc/ufw/user.rules` is mode `0640 root:root` and `ufw status` needs sudo:

```bash
$ grep -n 4242 /etc/ufw/user.rules
grep: /etc/ufw/user.rules: Permission denied
```

Reachability is proven by the successful TCP connects above; the *mechanism* (that UFW permits
it rather than merely not being loaded) remains unverified from an unprivileged session.

**Re-verified 2026-10-04 15:09 — the decision stands, the caveat is now better characterised.**
Both connects still succeed and the listener is unchanged. The blocker is also confirmed as a
**privilege wall and not a missing file**, which sharpens what is left to check:

```bash
$ ufw status
ERROR: You need to be root to run this script
$ sudo -n true
sudo: interactive authentication is required
$ find <repo>/config -iname '*firewall*' -o -iname '*ufw*'
(no output)
```

So there are **two** distinct things a privileged reviewer must supply, not one:

1. **The mechanism** — whether UFW is loaded and whether `4242/tcp` is an explicit `ALLOW`
   (the §9.3 table asserts this; it remains an assertion). Requires `sudo ufw status` or read
   access to `/etc/ufw/user.rules`.
2. **The policy to review against** — FIELD-04 asks for a review against "field-domain firewall
   policy", and **no such policy document exists in the repository.** `config/field/` contains
   only `heltec-v3`. There is nothing written down for the 4242 exposure to be judged against.

Point 2 is the more useful finding. Even with full root, "reviewed against field-domain firewall
policy" could not be completed as written, because the policy is unwritten. Closing that gap is
a documentation task in a section that does not own it; it is reported rather than edited.

## 9.4 Radio Profile Requirements

Each radio is defined by exactly one version-controlled profile. **The profile is the
specification** — this section states how a profile is accepted, not what fields it contains.

| Profile | Radio |
|---|---|
| `config/field/heltec-v3/radio-profile-us915.yaml` | `PEOPLE-RADIO` (Heltec V3) |
| `config/drone/waveshare-lora/radio-profile-us915.yaml` | `DRONE-RADIO` (Waveshare SX1262) |

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
conditions and not by chip family. Both radio ends must be verified as US915 hardware variants
before use.

### 9.4.1 Profile state measured 2026-10-03

The two profiles were compared byte for byte. They are **not** byte-identical, but they are
**substantively identical** — the only difference is the first-line comment:

```bash
$ diff -u config/field/heltec-v3/radio-profile-us915.yaml \
          config/drone/waveshare-lora/radio-profile-us915.yaml
@@ -1,4 +1,4 @@
-# Heltec WiFi LoRa 32 V3 - desktop gateway profile
+# Waveshare SX1262 LoRa HAT - drone-side profile (must interop with heltec-v3 profile)
 radio_profile:
   region: US915
   frequency_plan: "US915 hybrid-channel raw LoRa (NOT LoRaWAN)"
```

Every radio field after that comment is the same in both files. Neither profile declares
`frequency_mhz`, so the acceptance condition *"different frequency"* is unmet as written. Both
also carry the same `sync_word: 0x12` and the same unresolved `encryption_key_id` and
`device_identity` placeholders, so the *"cannot be confused on air"* and *"device identity is
unique"* conditions are unmet.

**Correction to the standing FIELD-14 wording.** FIELD-14 states that the profiles "also
disagree with `version-matrix.yaml`: profiles say 125 kHz and spreading factor 10, the matrix
and §9.2.1 say 250 kHz and spreading factor 7 for `DRONE-RADIO`". That is wrong.
`config/platform/version-matrix.yaml` contains **no radio, LoRa or field key at all**
(`grep -cn -i 'radio\|lora\|field' config/platform/version-matrix.yaml` → `0`; its top-level keys
are `host`, `gpu`, `mapping`, `simulation`, `sales`, `operations`, `ledger`). The matrix is not
a third opinion here — it is silent. The real disagreement is between the profiles and the
**live** Reticulum configuration, which is the authoritative record of what is on the air.

Measured live values from `~/.reticulum/config`:

| Setting | `PEOPLE-RADIO` (live) | `DRONE-RADIO` (live) | Both profiles claim |
|---|---|---|---|
| `frequency` | `915000000` | `917000000` | **not declared** |
| `bandwidth` | `125000` | `250000` | `bandwidth_khz: 125` |
| `spreadingfactor` | `7` | `7` | `spreading_factor: 10` |
| `codingrate` | `5` | `5` | `coding_rate: "4/5"` |
| `txpower` | `17` | `17` | `tx_power_dbm: 20` |
| `mode` | *(unset)* | `internal` | — |

So the profiles match **neither** radio: they overstate transmit power (20 dBm against a live
17 dBm), they understate spreading factor (SF10 against a live SF7), and they omit the 915/917
split entirely. The 915/917 MHz separation described in §9.1 and §9.2.2 is real and is enforced
by the live config — it simply is not captured in the version-controlled profiles that §9.4
nominates as the specification. Until the profiles are corrected, §9.4's acceptance conditions
cannot be tested against them, so **no profile can currently be accepted.**

Airtime consequence of the live-vs-profile SF difference, for the profile's
`max_packet_bytes: 222` payload at `airtime_limit_pct: 10`. Computed from the Semtech SX1262
LoRa airtime formula (BW-dependent symbol time, SF7-12, explicit header, CR 4/5, low-data-rate
optimisation on):

```bash
$ python3 -c "
import math
def airtime(payload,bw,sf,cr=5):
    Ts=1.0/bw; de=1
    n_sym=8+4*sf+8+math.ceil(math.log2(16*(sf-2*de+4)/4)*de)
    t_pre=(8+4*25+8+8)*Ts
    n_pay=8+math.ceil((8*payload-4*sf+28+16-20)/4*(sf-2*de+4))*de
    t_sym=(1+4+1)*Ts
    return (t_pre+(8+4*sf+n_sym+n_pay)*t_sym)*(4.0/(4+cr))
for name,bw,sf in [('profiles 125k/SF10',125000,10),('PEOPLE 125k/SF7',125000,7),
                   ('DRONE 250k/SF7',250000,7)]:
    t=airtime(222,bw,sf); print('%-22s airtime=%.4f s   pkts/h @10pct=%.0f'%(name,t,36000/t))
"
profiles 125k/SF10     airtime=0.1156 s   pkts/h @10pct=311423
PEOPLE 125k/SF7        airtime=0.0875 s   pkts/h @10pct=411418
DRONE 250k/SF7         airtime=0.0438 s   pkts/h @10pct=822836
```

| Configuration | Airtime | Packets/hour at 10% duty cycle |
|---|---|---|
| Profiles as written (125 kHz, SF10) | 0.1156 s | 311,423 |
| Live `PEOPLE-RADIO` (125 kHz, SF7) | 0.0875 s | 411,418 |
| Live `DRONE-RADIO` (250 kHz, SF7) | 0.0438 s | 822,836 |

The live radios are far inside the airtime limit; the profile values are conservative by a
factor of ~1.3 (PEOPLE) to ~2.6 (DRONE). This is a documentation mismatch, not a regulatory
fault, and **not urgent**.

**Correction to an earlier draft of this table.** It first read 0.240 s / 1,502 packets per
hour, from a spreadsheet-style estimate that could not be reproduced. The numbers above replace
it. The error mattered in principle — a wrong airtime figure is exactly the kind of number
that gets quoted into a regulatory argument — so it is recorded here rather than quietly
swapped.

### 9.4.2 Canonical radio device-name table (measured 2026-10-03)

Three different device paths were in circulation for the same two radios (§2.1 named
`/dev/ao-drone-radio` and `/dev/ao-people-radio`, §19 named `/dev/ttyUSB0` and
`/dev/heltec-v3`, §9.2.1 used `/dev/serial/by-id/...`). Measured state:

| Radio | Live port | `/dev/serial/by-path` | `ID_PATH` | `ID_SERIAL` | SX1262 MAC |
|---|---|---|---|---|---|
| `DRONE-RADIO` (917 MHz) | `/dev/ttyUSB0` | `pci-0000:05:00.0-usb-0:1:1.0-port0` | `pci-0000:05:00.0-usb-0:1:1.0` | `Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001` | **not measured** |
| `PEOPLE-RADIO` (915 MHz) | `/dev/ttyUSB1` | `pci-0000:00:14.0-usb-0:13:1.0-port0` | `pci-0000:00:14.0-usb-0:13:1.0` | `Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001` | **not measured** |

This confirms the §9.2.1 claim that identity **cannot** come from the USB serial descriptor: both
ports report the byte-identical `ID_SERIAL=Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001`.
Only one `by-id` symlink exists
(`usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0 → ../../ttyUSB0`), so
**`by-id` cannot identify `PEOPLE-RADIO` at all.** `by-path` is the only working discriminator,
which is what the live Reticulum config uses.

`/dev/heltec-v3` was never a valid name for this pair. `/etc/udev/rules.d/99-ao-heltec.rules`
deliberately declines to create it — both boards are Heltec V3, so one name could only ever point
at one of them. **§19's `/dev/heltec-v3` reference is wrong and should not be reinstated.**

**The `ao-*` symlinks are specified but not present.** The rule file is installed and is correct;
it simply has not fired:

```bash
$ ls -la /dev/ao-drone-radio /dev/ao-people-radio
ls: cannot access '/dev/ao-drone-radio': No such file or directory
ls: cannot access '/dev/ao-people-radio': No such file or directory
```

The rule is proven able to fire by dry run, which creates nothing:

```bash
$ udevadm test /sys/class/tty/ttyUSB0 2>&1 | grep 99-ao-heltec
ttyUSB0: /etc/udev/rules.d/99-ao-heltec.rules:18 SYMLINK+="ao-drone-radio": Added device node symlink "ao-drone-radio".
$ udevadm test /sys/class/tty/ttyUSB1 2>&1 | grep 99-ao-heltec
ttyUSB1: /etc/udev/rules.d/99-ao-heltec.rules:19 SYMLINK+="ao-people-radio": Added device node symlink "ao-people-radio".
```

The cause is ordering: the rule file was installed `2026-09-30 23:05:58`, after both adapters
were already enumerated, and `udev` applies `add` rules only at enumeration. An
`udevadm trigger` would create both links. **Not performed here** — it is a live serial-device
configuration change and is left for the operator.

MAC column: obtaining the SX1262 MAC requires opening the RNode serial port, which
`ReticulumMeshChatX` (PID 840861) currently holds open. That is live radio configuration, so
the column is left honestly empty rather than guessed.

### 9.4.3 LoRaWAN naming rule

The term **LoRaWAN is not used for this system in any artefact.** The stack is raw LoRa carried
by RNode over Reticulum; it implements no LoRaWAN device, gateway or network-server
architecture. Approved wording is:

> raw LoRa over Reticulum (RNode), **not** LoRaWAN

This rule is applied in this section, and both radio profiles already carry
`frequency_plan: "US915 hybrid-channel raw LoRa (NOT LoRaWAN)"`. One contradiction remains
outside the owning section and is reported rather than edited:
`es-executive-summary/section.md:11` calls `PEOPLE-RADIO` a "LoRaWAN for communication only"
path, and §9.2.2 below inherited that phrasing. Those lines belong to their owning sessions.

**This system is not LoRaWAN.** The field implementation is an RNode-based Reticulum mesh, and
it must not be described as LoRaWAN anywhere unless it implements a true LoRaWAN device, gateway
and network-server architecture. Any separate LoRaWAN or public-discussion service must use
different bands and settings and remain isolated from the field telemetry mesh.

## 9.5 Measured radio link state 2026-10-04

The two RNodes are both physically present and enumerated, but **only one of them is
operational**. `PEOPLE-RADIO` (915 MHz) is up; `DRONE-RADIO` (917 MHz) has been in a hard
reconnect failure since 2026-09-25. This is the dominant constraint on every remaining
field-link item and is recorded here so the next session does not re-derive it.

### 9.5.1 `DRONE-RADIO` has never come up since 2026-09-25 16:27

The last successful detection of either radio is 2026-09-25 16:27:11. Since then every
attempt has failed identically:

```bash
$ grep -h 'is configured and powered up' ~/.reticulum-meshchatx/logs/meshchatx.log* | tail -3
[2026-09-24 11:02:55] RNodeInterface[DRONE-RADIO] is configured and powered up
[2026-09-25 16:27:08] RNodeInterface[PEOPLE-RADIO] is configured and powered up
[2026-09-25 16:27:11] RNodeInterface[DRONE-RADIO] is configured and powered up

$ grep -ch 'unrecoverable error' ~/.reticulum-meshchatx/logs/meshchatx.log{,.1,.2,.3}
994
7800
2389
29
                                                        # 11,212 total.
                                                        # The current log grows live at ~7s per cycle,
                                                        # so this count rises continuously.
```

Every failure has the same three-line signature, repeating about every 7 seconds:

```text
[2026-10-04 07:25:38] [Notice] Opening serial port /dev/serial/by-path/pci-0000:05:00.0-usb-0:1:1.0-port0...
[2026-10-04 07:25:40] [Error]  Could not detect device for RNodeInterface[DRONE-RADIO]
[2026-10-04 07:25:40] [Error]  A serial port error occurred, the contained exception was: [Errno 9] Bad file descriptor
[2026-10-04 07:25:40] [Error]  The interface RNodeInterface[DRONE-RADIO] experienced an unrecoverable error and is now offline.
```

The failure is still live at the time of writing — the last event is 2026-10-04 09:18:25.

### 9.5.2 The fault is the radio board, not the port, the symlink or permissions

Ruled out by measurement, not assumption:

| Candidate cause | Verdict | Evidence |
|---|---|---|
| `by-path` symlink missing | **Ruled out** | `pci-0000:05:00.0-usb-0:1:1.0-port0 -> ../../ttyUSB0` present |
| Permission / `dialout` | **Ruled out** | `id` → `20(dialout)`; device is `crw-rw---- root:dialout` |
| Cable / USB enumeration | **Ruled out** | `cp210x 3-1:1.0: converter now attached to ttyUSB0`, `ID_SERIAL_SHORT=0001` |
| Port contended by another process | **Not the cause** | the same stack owns both radios; `PEOPLE-RADIO` on the other port works |
| **RNode firmware not answering** | **Best supported** | `Could not detect device` with no port-level error before it |

The distinction matters. A port that cannot be opened raises a permission or busy error;
this port opens and then yields `Errno 9` during the RNode detection handshake, which is
what a board that is enumerated but not running RNode firmware does. The kernel logged a
clean attach and has logged no disconnect.

**This is a hardware/firmware fault on the DRONE-RADIO board and needs physical
intervention — reseat the USB cable, or reflash the RNode firmware.** It cannot be fixed
from the documentation side, and it is the reason FIELD-01, FIELD-02, FIELD-03, FIELD-06
and FIELD-07 cannot be closed on evidence.

### 9.5.3 `PEOPLE-RADIO` is up and clean

`PEOPLE-RADIO` came up at 2026-10-03 16:57:56, 29 seconds after the current process
started, and has logged no error since. It is the only radio currently on air.

```bash
$ grep -h 'PEOPLE-RADIO. is configured and powered up' ~/.reticulum-meshchatx/logs/meshchatx.log.1
[2026-10-03 16:57:56] [Notice] RNodeInterface[PEOPLE-RADIO] is configured and powered up
$ grep -c 'PEOPLE' ~/.reticulum-meshchatx/logs/meshchatx.log
0
```

The asymmetry is the whole finding: the 915 MHz radio is healthy, the 917 MHz radio is
dead. Any characterisation of "both bands" is therefore characterisation of one band.

### 9.5.4 A single-radio host cannot measure what FIELD-01 and FIELD-03 ask for

FIELD-01 wants RSSI, SNR, noise floor, packet loss, retry behaviour and airtime **on both
RNodes**. With one radio offline there is no second node to measure against, and no RF
traffic in the logs at all:

```bash
$ grep -oh -E '(RSSI|rssi)[=: ]+[-0-9.]+' ~/.reticulum-meshchatx/logs/meshchatx.log* | wc -l
0
```

FIELD-03 wants 915/917 isolation *measured*. Separation between two bands cannot be
characterised while one band has no transmitter on it; the 915 MHz receiver is only ever
hearing ambient noise, which is not an isolation measurement. **These items cannot be
closed by any amount of further analysis on this host** — they need the DRONE-RADIO board
repaired first.

### 9.5.5 Field items blocked, and on what

| Item | Status | Blocker |
|---|---|---|
| FIELD-01 | Blocked | §9.5.1 — DRONE-RADIO offline; no RF metrics exist to record |
| FIELD-02 | Blocked | §9.5.1 — no end-to-end link over the drone path |
| FIELD-03 | Blocked | §9.5.4 — one band has no transmitter, so isolation is unmeasurable |
| FIELD-06 | Blocked | §9.5.1, plus needs the Pi5 (absent, §9.5.6) and an in-flight test |
| FIELD-07 | Blocked | needs *two* ends of a PEOPLE-RADIO mesh; only the desktop radio exists |
| FIELD-09 | Blocked | §9.5.6 — RPi5 not present on this network at all |

### 9.5.6 The Pi5 drone is absent from this network

FIELD-06 and FIELD-09 both terminate on a Raspberry Pi 5 running the QGC session. There is
no Pi5 reachable:

```bash
$ getent hosts raspberrypi raspbianpios alwayondrone rpi5
(no output — not in DNS)
$ ls ~/.ssh/config
ls: cannot access '/home/scottw/.ssh/config': No such file or directory
$ ip neigh
169.254.207.81 dev eno1 lladdr 30:05:5c:ee:a2:9b STALE
10.42.0.96   dev eno1 FAILED
192.168.87.1  dev wlp3s0 lladdr 16:22:3b:67:bd:98 REACHABLE
```

`10.42.0.96` is `printer-01`, not the drone, and it is down. The dnsmasq lease file is
empty. There is no SSH configuration for any Pi. The drone is simply not connected, so no
QGC session exists to send a mission to, in flight or otherwise.

**Operator input needed for FIELD-06 and FIELD-09:** power and connect the Pi5 drone, and
supply its address or an SSH entry. Until then there is nothing to test against.

### 9.5.7 Re-verification 2026-10-04 15:09 — every blocker above is still live

§9.5.1–§9.5.6 are dated 2026-10-03/04 and their numbers were taken earlier in the day. Before
relying on any of them, all six were re-measured. **Nothing has recovered.** The counts that
move are the offline-retry totals, which grow continuously at roughly one event per 7 seconds:

```bash
$ date -Is
2026-10-04T15:09:41-07:00

$ grep -h 'is configured and powered up' ~/.reticulum-meshchatx/logs/meshchatx.log* | tail -2
[2026-09-25 16:27:08] [Notice]   RNodeInterface[PEOPLE-RADIO] is configured and powered up
[2026-09-25 16:27:11] [Notice]   RNodeInterface[DRONE-RADIO] is configured and powered up
                                 # <- unchanged: still 2026-09-25, still no success since

$ grep -ch 'unrecoverable error' ~/.reticulum-meshchatx/logs/meshchatx.log{,.1,.2,.3}
3667   7800   2389   29          # 13,885 total; was 11,212 at 09:18, 994 in the first pass

$ tail -3 ~/.reticulum-meshchatx/logs/meshchatx.log
[2026-10-04 15:09:36] [Error]    A serial port error occurred, ... [Errno 9] Bad file descriptor
[2026-10-04 15:09:36] [Error]    The interface RNodeInterface[DRONE-RADIO] experienced an unrecoverable error and is now offline.
[2026-10-04 15:09:36] [Notice]   Reticulum will attempt to reconnect the interface periodically.
```

**Drone still absent** (§9.5.6 unchanged, and the neighbour table has since lost an entry —
`10.42.0.5` has appeared as `FAILED` and `10.42.0.96` `printer-01` remains down):

```bash
$ getent hosts raspberrypi raspbianpios alwayondrone rpi5
(no output)
$ ls ~/.ssh/config
ls: cannot access '/home/scottw/.ssh/config': No such file or directory
$ ip neigh
169.254.207.81 dev eno1 lladdr 30:05:5c:ee:a2:9b STALE
10.42.0.96   dev eno1 FAILED
10.42.0.5    dev eno1 FAILED
192.168.87.1  dev wlp3s0 lladdr 16:22:3b:67:bd:98 REACHABLE
```

**The `:4242` decision still holds** (§9.3.1, FIELD-04) — both connects succeed, listener
unchanged:

```bash
$ ss -ltnp | grep -E '18000|4242'
LISTEN 0 128  127.0.0.1:18000  0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=17))
LISTEN 0 1    0.0.0.0:4242     0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=46))
$ timeout 5 bash -c 'exec 3<>/dev/tcp/192.168.87.135/4242' && echo lan-OK
lan-OK
```

**The firewall mechanism is still unverifiable from an unprivileged account**, and this is a privilege
wall rather than a missing file — there is no field-domain firewall policy to review at all:

```bash
$ ufw status
ERROR: You need to be root to run this script
$ sudo -n true
sudo: interactive authentication is required
$ ls /tmp/ao-sessions/wt-field/config/field/
heltec-v3                       # no firewall/ufw file anywhere under config/
$ find /tmp/ao-sessions/wt-field/config -iname '*firewall*' -o -iname '*ufw*'
(no output)
```

**One measurement note, and a correction to the first claim made about it.** `grep` reports
`meshchatx.log.2` as a **binary file**, which was initially taken to mean a bare `grep -c` would
silently under-count it and that quoted totals would disagree between sessions. **That is
wrong, and that was checked before the figure was left in the record:**

```bash
$ for f in ~/.reticulum-meshchatx/logs/meshchatx.log{,.1,.2,.3}; do
    printf '%-16s a=%-6s plain=%s\n' "$(basename $f)" \
      "$(grep -ac 'unrecoverable error' $f)" "$(grep -c 'unrecoverable error' $f)"; done
meshchatx.log    a=3713   plain=3713
meshchatx.log.1  a=7800   plain=7800
meshchatx.log.2  a=2389   plain=2389
meshchatx.log.3  a=29     plain=29
```

The counts are **identical**. `grep -c` reports a count even when it also prints the
`binary file matches` notice; the notice concerns pattern *output*, not `-c`. So the only real
source of disagreement between sessions is the genuine one: **the current log grows ~1 event
per 7 seconds**, so any total is stale within minutes. Quote a total with its timestamp or
quote none.

The reasoning error: a counting error was inferred from an unrelated warning line instead of
running the comparison. The `-a` flag was already the right instinct for *reading* the file, but
Applying it to `-c` as well makes no difference.

### 9.5.8 Second re-verification 2026-10-04 15:59 — all six blockers still live

§9.5.7 was measured at 15:09 the same day. Re-measured at 15:59 before relying on it.
**Nothing recovered.** The only numbers that move are the continuously-growing retry totals.

```bash
$ date -Is
2026-10-04T15:59:52-07:00

$ grep -ah 'is configured and powered up' ~/.reticulum-meshchatx/logs/meshchatx.log* | tail -2
[2026-09-25 16:27:08] [Notice]   RNodeInterface[PEOPLE-RADIO] is configured and powered up
[2026-09-25 16:27:11] [Notice]   RNodeInterface[DRONE-RADIO] is configured and powered up
                                  # unchanged: last success for DRONE-RADIO is still 2026-09-25

$ for f in ~/.reticulum-meshchatx/logs/meshchatx.log{,.1,.2,.3}; do \
    printf '%-16s %s\n' "$(basename $f)" "$(grep -ac 'unrecoverable error' $f)"; done
meshchatx.log    4063      # was 3667 at 15:09
meshchatx.log.1  7800
meshchatx.log.2  2389
meshchatx.log.3  29
                 ----
                 14281     # was 13,885; +396 in 50 minutes, consistent with ~1 per 7s

$ tail -3 ~/.reticulum-meshchatx/logs/meshchatx.log
[2026-10-04 15:59:46] [Error]    The interface RNodeInterface[DRONE-RADIO] experienced an unrecoverable error and is now offline.
[2026-10-04 15:59:46] [Error]    Reticulum will attempt to reconnect the interface periodically.
[2026-10-04 15:59:51] [Notice]   Opening serial port /dev/serial/by-path/pci-0000:05:00.0-usb-0:1:1.0-port0...
```

**The retry loop is the same loop, still cycling, in the same order, 50 minutes later.** This is
the strongest available confirmation that the fault is persistent hardware/software state and not
a transient: an intermittent board would produce intermittent recoveries, and there is not one.

**Drone still absent** (§9.5.6 unchanged — `getent` returns nothing, no `~/.ssh/config`, both
`10.42.0.96` and `10.42.0.5` still `FAILED`):

```bash
$ getent hosts raspberrypi raspbianpios alwayondrone rpi5
(no output)
$ ls ~/.ssh/config
ls: cannot access '/home/scottw/.ssh/config': No such file or directory
$ ip neigh
169.254.207.81 dev eno1 lladdr 30:05:5c:ee:a2:9b STALE
10.42.0.96 dev eno1 FAILED
10.42.0.5    dev eno1 FAILED
192.168.87.1  dev wlp3s0 lladdr 16:22:3b:67:bd:98 REACHABLE
```

**The `:4242` decision still holds** (§9.3.1, FIELD-04) — listener unchanged and still reachable
from the LAN address:

```bash
$ ss -ltnp | grep -E '18000|4242'
LISTEN 0 128  127.0.0.1:18000  0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=17))
LISTEN 0 1    0.0.0.0:4242     0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=46))
$ timeout 5 bash -c 'exec 3<>/dev/tcp/192.168.87.135/4242' && echo lan-OK
lan-OK
```

**The firewall mechanism is still unverifiable from here** — privilege wall, and still no policy
document anywhere under `config/`:

```bash
$ ufw status
ERROR: You need to be root to run this script
$ sudo -n true
sudo: interactive authentication is required
$ find config -iname '*firewall*' -o -iname '*ufw*'
(no output)
```

**The live radio settings are unchanged**, so §9.4.1's profile-vs-live comparison remains valid
as of now — 915 MHz / 125 kHz / SF7 / 17 dBm and 917 MHz / 250 kHz / SF7 / 17 dBm:

```bash
$ grep -A12 'RNodeInterface' ~/.reticulum/config | grep -E 'frequency|bandwidth|spreadingfactor|txpower'
frequency = 915000000
bandwidth = 125000
spreadingfactor = 7
txpower = 17
frequency = 917000000
bandwidth = 250000
spreadingfactor = 7
txpower = 17
```

**Two corrections to how these totals are quoted.** First, §9.5.7's own advice — *quote
a total with its timestamp or quote none* — applies here: the 14,281 figure is only
true at 15:59 and is already wrong. Second, an earlier pass used `grep -ah` on the
glob while §9.5.7 used a per-file loop; the two agree (`4063+7800+2389+29 = 14281`), so the
totals are not sensitive to that choice, but the **`-a` flag is** — see §9.5.7, where a file
that `grep` calls binary is still counted correctly without it.

### 9.5.9 Third re-verification 2026-10-04 17:52 — blockers unchanged, and the port is now *proven* open

§9.5.7 and §9.5.8 are dated 15:09 and 15:59. Re-measured at **17:52**, per §9.5.7's own
rule that a count is quoted with its timestamp or not at all.

**Totals have moved; state has not.** Detection failures, per file, each with its own span:

```bash
$ date -Is
2026-10-04T17:52:44-07:00
$ cd ~/.reticulum-meshchatx/logs
$ for f in meshchatx.log.3 meshchatx.log.2 meshchatx.log.1 meshchatx.log; do \
    printf '%-16s %s .. %s  detect-fail=%s\n' "$f" \
      "$(head -1 $f | grep -oE '\[[0-9-]+ [0-9:]+\]')" \
      "$(tail -1 $f | grep -oE '\[[0-9-]+ [0-9:]+\]')" \
      "$(grep -ac 'Could not detect device' $f)"; done
meshchatx.log.3   .. [2026-09-25 16:27:17]  detect-fail=328
meshchatx.log.2  [2026-09-25 16:27:17] .. [2026-10-03 14:39:54]  detect-fail=2487
meshchatx.log.1  [2026-10-03 14:39:56] .. [2026-10-04 07:25:33]  detect-fail=8270
meshchatx.log    [2026-10-04 07:25:38] .. [2026-10-04 17:52:43]  detect-fail=5155
                                                         # total 16,240 (was 14,281 at 15:59)
```

**The port does open, proved by watching the file descriptors.** §9.5.2 argued
the port opens because the error is `Errno 9` rather than `EACCES`/`EBUSY`. That is
inference from an error string. It can now be observed directly: `DRONE-RADIO`'s descriptor
is repeatedly created and destroyed on the retry cycle, while `PEOPLE-RADIO`'s descriptor is
held open continuously.

```bash
$ (for i in $(seq 1 20); do \
    printf '%s count=%s fds=[%s]\n' "$(date +%T)" \
      "$(ls -l /proc/840861/fd | grep -c ttyUSB)" \
      "$(ls -l /proc/840861/fd | grep ttyUSB | awk '{print $9"="$11}' | tr '\n' ' ')"; \
    sleep 2; done)
17:48:02 count=1 fds=[48=/dev/ttyUSB1 ]
17:48:05 count=2 fds=[30=/dev/ttyUSB0 48=/dev/ttyUSB1 ]
17:48:07 count=1 fds=[48=/dev/ttyUSB1 ]
17:48:13 count=2 fds=[20=/dev/ttyUSB0 48=/dev/ttyUSB1 ]
17:48:19 count=2 fds=[48=/dev/ttyUSB1 64=/dev/ttyUSB0 ]
...
```

`fd 48 -> /dev/ttyUSB1` (`PEOPLE-RADIO`) is present in **every** sample. The `ttyUSB0`
descriptor appears, changes number between attempts (20, 30, 64), and disappears. That is the
signature of a **successful open immediately followed by a close** — the kernel grants the
descriptor and the RNode detection handshake then fails. A permission fault would never
produce a descriptor at all; a contended port would fail at open.

The descriptor is also *not* stale. The inode behind it matches the live device node, so
this is not a leaked handle to a removed device:

```bash
$ stat -c '%n inode=%i' /dev/ttyUSB0 /dev/ttyUSB1
/dev/ttyUSB0 inode=782
/dev/ttyUSB1 inode=786
$ for f in /proc/840861/fd/*; do t=$(readlink $f); case "$t" in *ttyUSB*) \
    echo "fd=$(basename $f) $t inode=$(stat -Lc %i $f)";; esac; done
fd=48 /dev/ttyUSB1 inode=786
```

**Retry cadence is steady at roughly one failure every 7–8 seconds**, consistent since the
fault began and showing no decay, no backoff and no recovery:

```bash
$ tail -2000 ~/.reticulum-meshchatx/logs/meshchatx.log | grep 'unrecoverable error' \
    | grep -oE '\[[0-9-]+ [0-9:]+\]' | cut -c2-17 | cut -c1-16 | uniq -c | tail -5
      8 2026-10-04 17:43
      7 2026-10-04 17:44
      7 2026-10-04 17:45
      8 2026-10-04 17:46
      5 2026-10-04 17:48
```

**Everything else in §9.5 still holds.** `PEOPLE-RADIO` has logged nothing at all in the
current log (0 lines, zero errors). There is still zero RF telemetry — `RSSI`, `SNR`,
`noise floor`, `airtime` and `packet loss` all return 0 matches across all four logs. The Pi5
is still absent. The live radio settings are unchanged (915 MHz / 125 kHz / SF7 / 17 dBm and
917 MHz / 250 kHz / SF7 / 17 dBm), so §9.4.1's profile-vs-live comparison stands.

### A device node's `mtime` measures access, not enumeration

An earlier pass read `Oct 4 17:42` from `ls -la /dev/ttyUSB*` and recorded it as "the USB
devices were re-enumerated at 17:42 today". That would have been a significant claim — a
fresh enumeration would have meant someone had re-plugged the hardware and the radio
still failed — and it was false.

**`mtime` on a device node moves when the node is *accessed***, and the inspecting
commands themselves were reading it. **`ctime` is the field that answers an enumeration
question**, and it has not moved since 2026-10-01 23:53:

```bash
$ stat -c '%n mtime=%y ctime=%z' /dev/ttyUSB0 /dev/ttyUSB1
/dev/ttyUSB0 mtime=2026-10-04 17:51:22 ctime=2026-10-01 23:53:34
/dev/ttyUSB1 mtime=2026-10-04 17:51:20 ctime=2026-10-01 23:53:34
```

**The generalisable rule: a number that appears to corroborate what was expected is the
most dangerous kind of evidence.** The wrong reading here felt like a discovery because it
coincided with the session's own start time. **Verify that a field means what you think it
means before building a finding on it** — this joins the rotated-log-filename lesson in
FIELD-05.

**Nothing may be touched.** No radio, no serial port, no firewall, no config file, no
restart of the Reticulum stack. All six blockers in §9.5.5 remain live.

### 9.5.10 Fourth re-verification 2026-10-05 07:56 — the `DRONE-RADIO` fault narrows to the
### board's own firmware, with every hardware alternative excluded

§9.5.2 concluded the fault "is the radio board, not the port, the symlink or permissions". That
conclusion was reached without enumerating the remaining hardware causes, and **this
re-verification closes that gap.** The exclusion is by measurement, and it is what an operator needs in order to know
whether to reseat a cable, replace a board, or stop looking at this host at all.

`DRONE-RADIO` is still down with zero successful detections and the failure signature is
unchanged — the port opens and the board does not identify itself:

```text
$ tail -6 ~/.reticulum-meshchatx/logs/meshchatx.log
[2026-10-05 07:53:34] [Error]    Could not detect device for RNodeInterface[DRONE-RADIO]
[2026-10-05 07:53:34] [Error]    A serial port error occurred, the contained exception was: [Errno 9] Bad file descriptor
[2026-10-05 07:53:34] [Error]    The interface RNodeInterface[DRONE-RADIO] experienced an unrecoverable error and is now offline.
```

The last successful detection anywhere in the retained logs is still 2026-09-25 17:22:28. Counts
per rotated file, oldest first — the outage has now run **ten days continuously**:

| Log | First line | `DRONE-RADIO` unrecoverable |
|---|---|---|
| `meshchatx.log.3` | 2026-09-25 16:27:17 | 2353 |
| `meshchatx.log.2` | 2026-10-03 14:39:56 | 7798 |
| `meshchatx.log.1` | 2026-10-04 07:25:38 | 7866 |
| `meshchatx.log` | 2026-10-04 23:58:26 | 3777 |

**The last row is a live figure and grows continuously** — it was 3777 when first counted and
3898 on a later count the same morning, because the radio is still retrying every few seconds.
**Treat it as a lower bound, and never cite a count from `meshchatx.log` as a fixed number.**
The three rotated rows are stable. Same caveat applies to the teardown total in §9.2.3.

**Alternative 1 — "the USB adapter is absent." Excluded.** Both `CP2102` bridges are enumerated
on the expected buses and the kernel logged eight `cp210x` lines with **no disconnect or reset
since**:

```text
$ lsusb | grep -i 10c4
Bus 001 Device 010: ID 10c4:ea60 Silicon Labs CP210x UART Bridge
Bus 003 Device 002: ID 10c4:ea60 Silicon Labs CP210x UART Bridge

$ journalctl -k --no-pager | grep -E 'cp210|ttyUSB' | tail -6
Oct 01 15:08:12 kernel: usb 3-1: Product: CP2102 USB to UART Bridge Controller
Oct 01 15:08:12 kernel: usb 1-13: Product: CP2102 USB to UART Bridge Controller
Oct 01 15:08:12 kernel: cp210x 3-1:1.0: cp210x converter detected
Oct 01 15:08:12 kernel: usb 3-1: cp210x converter now attached to ttyUSB0
Oct 01 15:08:12 kernel: cp210x 1-13:1.0: cp210x converter detected
Oct 01 15:08:12 kernel: usb 1-13: cp210x converter now attached to ttyUSB1
```

`ttyUSB0` is the `DRONE-RADIO` port and it is **live**: ctime 2026-10-01 23:53:34, and `ls -la`
shows a present character device.

**Alternative 2 — "the port name is wrong or stale." Excluded.** All `by-path` symlinks resolve,
and the one `DRONE-RADIO` uses is the correct board per §9.4.2 and `~/.reticulum/radio-ids.txt`
(`3-1` = the USB-C port = `pci-0000:05:00.0`):

```text
$ for p in /dev/serial/by-path/*; do printf '%s -> ' "$p"; readlink -f $p; done
/dev/serial/by-path/pci-0000:00:14.0-usb-0:13:1.0-port0  -> /dev/ttyUSB1
/dev/serial/by-path/pci-0000:05:00.0-usb-0:1:1.0-port0  -> /dev/ttyUSB0
```

**Alternative 3 — "permissions or group membership." Excluded.** The operator is in `dialout`
and both nodes are `root:dialout 0660`, readable and writable:

```text
$ ls -la /dev/ttyUSB0 /dev/ttyUSB1
crw-rw---- 1 root dialout 188, 0 /dev/ttyUSB0
crw-rw---- 1 root dialout 188, 1 /dev/ttyUSB1
$ for d in /dev/ttyUSB0 /dev/ttyUSB1; do [ -r $d ] && [ -w $d ] && echo "$d rw OK"; done
/dev/ttyUSB0 rw OK
/dev/ttyUSB1 rw OK
```

**Alternative 4 — "something else is holding the port." Excluded, and this one needed sampling
rather than a single check.** `ReticulumMeshChatX` (PID 840861) holds **only** `ttyUSB1` — the
`PEOPLE-RADIO` port — and nothing else holds `ttyUSB0`. Sampling three times over six seconds
caught `ttyUSB0` momentarily held by Reticulum itself, which is its own retry loop grabbing and
releasing the port, not a third-party conflict:

```text
$ fuser -v /dev/ttyUSB0 /dev/ttyUSB1
                     USER        PID ACCESS COMMAND
/dev/ttyUSB1:        scottw    840861 F.... ReticulumMeshCh
        # nothing listed for /dev/ttyUSB0
```

**What is left, stated precisely.** The USB bridge enumerates and the node opens, but the
**ESP32 on the `DRONE-RADIO` board does not answer the identification RNode sends on that
bridge.** That is a board-side or cable-side condition — the board's own firmware state, a
damaged or charge-only cable, or the board needing a power cycle — and it is **not diagnosable
or repairable from this host.** `DRONE-RADIO` is correctly configured and correctly addressed;
there is nothing in the software configuration to change.

**This is a stop condition and must stop here.** "Live radio, serial or network configuration" is on
the operator-approval list. No `udevadm trigger`, no USB bus cycle, no opening of
either port for a manual probe, and did not restart the Reticulum stack. The MAC in
`radio-ids.txt` dates from 2026-09-21 and it was not re-read from hardware, because that means
opening a serial port the running service owns.
**Nothing was touched.** No radio, no serial port, no firewall, no config file. Every blocker in
§9.5.5 still requires physical repair or operator action.
**Correction to a prior claim in this section, and it is the one most likely to mislead the next
reader.** §9.4.2 and the FIELD-12 proposal record that `by-id` has "exactly ONE link → can only
ever identify `ttyUSB0`". The observation still holds, but the reason was written as though it
were a property of this host's layout. It is not: **both bridges ship with the byte-identical
factory serial descriptor `Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001`**, because
CP2102 serials are programmed at the vendor and a factory-default pair collides by definition.
Re-measured today on both devices:

```text
$ for d in ttyUSB0 ttyUSB1; do udevadm info -q property -n /dev/$d | grep -E '^ID_(SERIAL|PATH)='; done
ID_SERIAL=Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001
ID_PATH=pci-0000:05:00.0-usb-0:1:1.0
ID_SERIAL=Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001
ID_PATH=pci-0000:00:14.0-usb-0:13:1.0
```

So the single `by-id` link is a **consequence of identical hardware**, and no amount of
replugging will ever produce a second `by-id` name. **`by-path` is the only discriminator that
can work for these two boards** — a property of the hardware, not an accident of one boot.
§9.4.2's table should be read that way, and any future suggestion to "just use `by-id` once the
serial is unique" is closed by this.

**Two stale-by-date findings the compiler should re-check rather than copy.**

- **The `ao-*` symlinks from FIELD-12 are still absent**, cause unchanged: the rule is installed
  (`/etc/udev/rules.d/99-ao-heltec.rules`, mtime `2026-09-30 23:05:58`) and both adapters
  enumerated at boot on 2026-10-01, i.e. **after** the rule was written. `ls /dev/ao-*` →
  `No such file or directory`. Creating them still needs an operator `udevadm trigger`, which is
  a live-serial action and was not performed.
- **FIELD-05's `umsgpack` fault has not recurred.** `grep -c umsgpack` on the current log returns
  **0**, with the last occurrence still in `meshchatx.log.2`. That *supports* FIELD-05's closure
  rather than reopening it: the persistence error stopped instead of continuing.

**Nothing was touched.** No radio, no serial port, no `udevadm trigger`, no USB reset, no
firewall change, no config edit, no restart. `PEOPLE-RADIO` is up with zero error lines today
(`grep -c 'PEOPLE-RADIO'` on the current log → `0`).

### An empty result from an unverified query scope is not a negative finding

`journalctl -k --since '2026-10-04'` and `dmesg` both return **empty output** when testing
whether the USB link flapped, which reads exactly like "nothing happened". It is not
evidence of that: `dmesg` is unreadable for this user, and the `--since` window genuinely
contained no kernel messages — while the *unfiltered* query shows the eight lines that do
exist, all from Oct 01.

**This is the third instance of one failure in this section** (after FIELD-05's rotated logs
and the §9.5.9 timestamp error): an empty result from a query whose scope was not verified is
not a negative finding. **Run the unfiltered query and read what it returns before
recording an absence.**
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

### 10.1.1 SITL method, verified against ardupilot.org

Verified 2026-09-29 against the ArduPilot developer documentation. SITL
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

- `GZ_VERSION` must be set to the installed Gazebo release.
- `GZ_SIM_SYSTEM_PLUGIN_PATH` must include the built `ardupilot_gazebo`
  plugin directory.
- `GZ_SIM_RESOURCE_PATH` must include the plugin's `models/` and `worlds/`
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
variety of optional sensors. The vehicle profiles below therefore must be
selectable at run time, ideally at rapid speed, by changing the ArduPilot
vehicle type and the Gazebo model, not by rebuilding anything.

Vehicle profiles must allow for switching between the following, ideally at
rapid speed, by changing the ArduPilot vehicle type and the Gazebo model:

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

Vehicle simulation must never connect to live flight controllers, field radios,
real drone telemetry, payment services, customer records, or Corda core.
### 10.1.2 Baseline capability: 3D world, boning, reinforcement learning objects, HTML portal

Required by ES.1 for **both** simulation domains. For `ao-sim-vehicle` these four are
baseline deliverables, not optional extras, and they are tracked as §19.1 SIM-04 (ST-07).

**3D world setup.** The domain stands up its own Gazebo world as a first-class artifact:
the world file, its models, their poses, the lighting and environment, the ground and
surface materials, the physics and collision configuration, and the spawn points. World
setup must be scripted and repeatable from a single entry point rather than assembled by
hand in the GUI, so the same world can be rebuilt identically on any host.

**Boning.** The world carries a boning and alignment structure: a defined datum frame per
model, declared mounting and reference surfaces, joint and axis definitions, and the
tolerances between them. Boning is what makes the world measurable rather than merely
pictorial — a pose is verified against the boning frame instead of being eyeballed, and
a model that has drifted out of tolerance is detectable programmatically. The boning data
must be exported alongside the world so the same checks run against recorded evidence.

**Reinforcement learning objects.** The trainable entities for scenario and policy work:
marked, individually addressable objects with observable state, reward-relevant properties,
and defined reset behaviour. They must be separable from the static world geometry so a
training run can vary object count and placement without rebuilding the world. The optional
Stable-Baselines3 evaluation consumes these objects; the objects are required even where no
trainer is attached yet.

**HTML portal.** The whole environment is exposed through a browser-served HTML portal:
view the live model and sensor state and read back boning and tolerance measurements. The
portal is **view-only** — it exposes no route that can start, stop, reset or otherwise
modify the simulation. World lifecycle is an operator CLI run locally. It runs inside
`ao-sim-vehicle` and is reachable only by the approved local path — the same isolation
rule that forbids this domain from touching live flight controllers applies to the portal
as well. It must never become a path by which the simulation reaches anything outside its
own domain.


## 10.2 Fabrication and Facility Simulation

Gazebo Sim model views of the fabrication and facility domain. These show the modelled
robot-arm cells, vehicle and shelving layout, and kitchen/storage volumes referenced
below. They are **rendered model views, not operational evidence** — no flight-control
or live-machinery path is enabled by anything shown here.

![Simulated fabrication domain: robot arm, vehicle, and robot arm vehicle work areas](assets/sim-robot-arm-vehicles.png)

*Figure 10.2a — Robot-arm work area, vehicle bay, and robot-arm vehicle bay within the fabrication domain.*

![Simulated shelving and storage elevation with robot-arm cells](assets/sim-shelving-front.png)

*Figure 10.2b — Storage and shelving elevation with robot-arm cells, and the shelving-to-printer aisle.*

![Simulated shelving and kitchen volume from the opposite approach](assets/sim-shelving-rear.png)

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
related details for the **rehearsal**, and it runs the kitchen. It **does not
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

Phase one is simulation only. It must not command live robot arms, 3D printers,
CNC machines, laser powder bed fusion systems, refrigeration, carousels, kitchen
equipment, or other machinery.

LPBF systems, refrigeration, carousels, kitchen equipment, or other machinery.

Vehicle and fabrication simulation domains require separate:

- Podman networks.
- ROS domain IDs.
- Gazebo partitions.
- DDS configuration.
- Service identities.
- Filesystem mounts.
- Result directories.
- Simulation **manifest-signing** certificates only. These sign exported
  artifacts; they must not be Corda client identities, and simulation must never
  open a connection to Corda core (section 10.1).
- Git repositories or clearly separated repository subtrees.
- Artifact manifests.

Use local folder storage under /ALWAYSON, in the Gazebo subfolder (verify its exact
location with the operator), for SDF, URDF/Xacro, world files, robot definitions, safety zones,
task plans, and launch configurations. Use Git LFS or a separate artifact
repository for large meshes, textures, point clouds, and generated results.
### 10.2.1 Baseline capability: 3D world, boning, reinforcement learning objects, HTML portal

The same four deliverables as §10.1.2, tracked as §19.1 SIM-05 (ST-08). What differs is
what the world contains.

**3D world setup.** The fabrication world covers the robot-arm cells, the vehicle and
shelving layout, and the kitchen and storage volumes shown in Figures 10.2a–10.2c, with
safety zones and the printer/CNC and storage footprints.

**Boning.** This is where boning carries the most weight in this domain, because the
modelled cells and machines must line up with the real ones. The world carries a datum
frame per cell, declared mounting and reference surfaces for the robot arms and for the
printer and CNC beds, the shelving and aisle reference planes, and the joint and axis
definitions with their tolerances. This is what lets a simulated reach be checked against
the real machine envelope rather than assumed, and it is exported with the world so the
same check runs against recorded evidence.

**Reinforcement learning objects.** Marked parts, stock items and task targets for cell and
kitchen work. Robot arms and shuttles are the controlled actors; these objects are what they
act on and what reward is measured against.

**HTML portal.** A browser-served portal showing live robot, machine and stock state, the
boning and tolerance measurements, and the world. Reachable only on the approved local path
at `ROS_DOMAIN_ID=22` / `GZ_PARTITION=alwayson_fabrication_sim`, and never a control path to
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
view. Two properties are load-bearing and worth recording. The bridge container must be on
both `ao-html-window` and `ao-sim-fabrication`: a matching `GZ_PARTITION` does not route
between two internal bridges, and gz-transport discovery is link-local multicast. And the
server must set `GZ_IP=0.0.0.0`; the GUI appears to work without it only because it shares
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

The portal is `scripts/simulation/ao-sim-portal.py` and exposes `/api/status`,
`/api/{start,stop,reset,inspect}`, `/api/boning`, `/api/objects` and `/api/health`, restricted
to a single permitted unit.

**Platform.** ROS 2 Lyrical at `/opt/ros/lyrical` and Gazebo Sim 10.5.0 (collection "Jetty") on
Ubuntu 26.04. This is the vendor-supported pairing, not a locally chosen mix: Gazebo Sim 10.5.0
is the ceiling of what the vendor publishes for this platform, and upstream lists ROS 2 Lyrical
(LTS) + Gazebo Jetty (LTS) as the recommended combination for 26.04. Gazebo Classic 11 is
end-of-life and is not a target here; the modern integration is `ros_gz`, not `gazebo_ros_pkgs`.
Simulation images are built from a pinned base-image digest rather than from an apt repository.

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
server must share its network namespace. A GUI client is selected by overriding `ENTRYPOINT` in
the Quadlet unit, not by maintaining a second GUI image.

### 10.3 Verified state, 2026-10-03 (SIM session)

Everything below was measured on this host on 2026-10-03, not inferred from the repository. Two
items in §19.1 were described as absent at the time §19 was compiled and are in fact present and
running; that correction is the reason this subsection exists.

**Delivered and verified live.**

| Item | What was measured |
|---|---|
| 3D world and cameras | `ao-sim-fabrication-gz.service` `ActiveState=active`, `NRestarts=0`, up 31 min. Portal `/api/status` reports `link_count 37`. All eight camera topics present on `ros2 topic list`. |
| Camera frames | `/factory/camera/elev_arms` `average rate: 1.972`, min 0.507 s max 0.507 s. The world's declared rate is 10 Hz; **the bridge delivers ~2 Hz, not 10 Hz.** This is a measured discrepancy, recorded rather than explained. |
| RL objects as world entities | `/api/status` link list contains `part_a1..a3`, `stock_s1..s3`, `target_bin_a`, `target_bin_b`, `target_shelf` — nine live links inside a non-static `rl_objects` model, not a YAML-only catalogue. |
| Safety zones | `/api/safety-zones` returns four resolved zones with computed min/max boxes, and `verify_safety_zones.py` exits 0 printing `4 zones, 2 unresolved dependencies`. |
| Interlocks | Three interlocks declared, every one `enforced_in_simulation: false`. The model **reports**; it actuates nothing, and the printed line `No interlock is enforced in the simulation; they report only.` is the honest boundary. |
| GUI image | `localhost/gz-sim10-resolute:gui-svgfix` carries `qt6-svg-plugins 6.10.2-2` and `/usr/share/gz/gz-rendering` holds `media/ ogre/ ogre2/` — both SIM-06 preconditions satisfied in the image. |
| ROS 2 apt | `openssl s_client -connect packages.ros.org:443` returns `subject=... CN=*.osuosl.org` with `verify return:1`, and `curl` returns HTTP `000`. SIM-07 reproduced exactly as §19 describes. |

**Two defects found, neither of them in §19.**

1. **`build-rl-objects.py --check` reports STALE against the committed world, and `--write`
   relocates the model.** `--check` exits 1 on the committed `factory.world`. The cause is not
   data drift: the committed block carries `<specular>` and `<shininess>` on every material,
   added by commit `fa3f8f6` ("material shininess") and never taught to the generator, while
   `render()` emits bare ambient/diffuse. Nine material lines differ. Worse, `--write` strips the
   existing block and re-appends before `</world>`, so the block moves from line 623 to the end
   of the world, **after** `safety_zones` and `conveyor_loops`. Regeneration is therefore not
   idempotent in *position* even once the material drift is settled. Demonstrated on a copy under
   `/tmp/gen-test`, never on the live tree. Running `--write` against `/ALWAYSON` rewrites the
   world in place and reorders three generated models; it is not a safe routine refresh.
2. **The signed manifest no longer describes the world, and the gap is larger than §19 records.**
   §19 says the manifest records 5371 bytes against a world of "~18 KB". Measured now:
   manifest `content_size_bytes` 5371 and `content_hash_sha256` `64eacbbf…`; the actual file is
   **63205 bytes** with sha256 `bce32f2a…`. Both the size *and* the hash disagree. The manifest
   cannot be repaired by editing a number — it must be re-exported and re-signed with the
   `ao-sim-fabrication` key.

**Corrections to §19 items on the strength of the above.**

- **SIM-13 and SIM-14 were recorded as absent; both are delivered.** The §19 text "nothing in the
  repo implements one" and "That model does not exist" are both false as of these measurements.
  Neither was ever a §19.2-tracked item, which is plausibly why they went stale: they were
  delivered by ordinary commits without a matching §19 row to close.
- **SIM-09 is closed by commit `365bd42`, not outstanding.** The arms datum was corrected to the
  measured as-built centroid and every arm camera re-aimed at it. `cell-arms` now reads
  `origin [5.981314, 1.861669, 0.531531]` with `extent [0.84, 1.672391, 1.238532]`, whose midpoint
  is the centroid `(6.4013, 2.6979, 1.1508)`, and the world comment records that every camera
  sits outside the massing envelope. `elev_arms` is at `6.401 4.056 1.151 0 0.0000 -1.5708`.
  **Superseded in part, 2026-10-04 — see "SIM-09 re-opened and properly closed" below.** The
  arithmetic above was right, but §19 asks for two further things and neither was then true:
  `boning.yaml` stated no `centroid:` at all, and the camera pose was a hand-written literal
  that no code derived from the datum. Both are now done.
- **SIM-06 is partly satisfied and partly untested.** The image carries the SVG plugin and the
  media root is correct, but the GUI unit is `UnitFileState=generated` with no `[Install]`
  section, so it cannot autostart; `ActiveState=inactive`, `NRestarts=0`. A restart count of zero
  on a unit that has never run is not evidence that rendering works. **The GUI unit cannot
  autostart and its render path is unverified** — see the retraction in §10.9.

**Still absent, confirmed.** No facility scheduler exists: a case-insensitive search for
`scheduler` across `GAZEBO/`, `scripts/simulation/` and `quadlet/` returns only an unrelated
comment in `quadlet/sales/ao-mastodon-sidekiq.container`. SIM-12 stands.

**Operator decision outstanding.** SIM-02 — the `/ALWAYSON` Gazebo subfolder path. The repository
uses `GAZEBO/` (present, `12M` of meshes) and every path reference in the world, the boning
file, the portal and the Quadlet units agrees on `/ALWAYSON/GAZEBO`. The implementation is
therefore self-consistent, but §10.2 still says "verify its exact location with the operator",
and §10.2 cannot substitute for that confirmation.

### 10.4 Verified state, 2026-10-04 (SIM session)

Measured on this host on 2026-10-04. One item is closed with commands and output, one defect is
fixed, one false claim is corrected, and one item is prepared and stopped at a stop condition.

**SIM-06 is now established, not inferred.** §10.3 recorded the GUI as untested, with the
correct warning that `NRestarts=0` on a unit that never ran proves nothing. The GUI has now
actually been started and watched:

- `systemctl --user start ao-sim-fabrication-gui-gz.service` → `ActiveState=active`,
  `SubState=running`, `NRestarts=0`, `ExecMainStatus=0`.
- 18 plugins load, including `EntityTree` (the SVG-icon-dependent one) and
  `gz-rendering-ogre2`. A case-insensitive journal grep for `OGRE EXCEPTION`,
  `construction from null`, `Segmentation`, `Failed to load` and `cannot open` returns **0**.
- The window exists and is placed by the KWin script: `xwininfo -root -children` shows
  `"Gazebo Sim": ("gz-sim-gui" "Gazebo GUI") 480x292+24+1502` — bottom-left of DP-3, per
  `~/.local/share/kwin/scripts/ao-gazebo-monitor/`.
- **Positive proof of geometry, not just a live process.** A window capture
  (`import -window 0x120001a`) shows rendered factory geometry on the ground plane, the
  left-hand toolbar icons decoded (so the SVG plugin works, not merely installs), and the sim
  clock advancing at `20.00%`. A second capture 5 s later differs in **294 of 140160** pixels,
  so the view is live rather than a frozen first frame.
- The unit was **re-masked afterwards**, as §19 requires, so it cannot seize keyboard and
  pointer focus: `is-enabled` = `masked`, and `start` then fails with `Unit ... is masked.`

**Fixed: the reproducibility guard that was disarmed.** §10.3 defect 1 found
`build-rl-objects.py --check` exiting 1 against the committed world, so the one check whose
entire purpose is catching divergence could not distinguish real drift from a cosmetic hand
edit. The cause was that `<specular>`/`<shininess>` had been added to `factory.world` *inside
the generated block* and never taught to the generator. The generator now declares
`SPECULAR = (0.30, 0.30, 0.30, 1.0)` and `SHININESS = 24`, so:

- `--check` → `OK: rl_objects block matches objects.yaml`, exit 0;
- `--write` → `rl_objects block already current; nothing written`, with the world sha256
  unchanged either side (`bce32f2a…`), so the world was **not** rewritten;
- the guard is not merely green: a real catalogue drift (moving `part-a1`'s home pose) makes
  `--check` exit 1 with `STALE`, and restoring the file returns it to 0. `objects.yaml`
  sha256 confirmed unchanged afterwards.

**Corrected a false capability claim in the portal.** `/api/objects` served
`"resettable": true` copied verbatim from `objects.yaml`, indistinguishable from a verified
capability, while the portal exposes no reset endpoint and performs no reset — `/api/reset`
returns 404. A consumer could reasonably have read that as "I can reset these objects". The
field is now `resettable_claimed` beside an explicit `reset_available: false` and a
`reset_note` naming the discrepancy, and the HTML portal (its only consumer) was updated to
match so it does not render `undefined`. Verified live on the restarted portal, and
`node --check` on the extracted script reports `PORTAL JS SYNTAX OK`. This corrects a claim;
it does **not** deliver reset, so SIM-14 stays open on that limb.

**SIM-11 is prepared and deliberately NOT executed.** Measured: the manifest records
`content_size_bytes` 5371 and `content_hash_sha256` `64eacbbf…`, while `factory.world` is
**63205 bytes** with sha256 `bce32f2a…`. Size *and* hash disagree, so the manifest cannot be
repaired by editing a number. Repair requires re-export and re-signing with the
`ao-sim-fabrication` producer key (present at `secrets/sim-fabrication/producer.pem`, 119 bytes,
value not printed) via `scripts/ledger/build-manifest.sh`. **Re-signing a provenance record with
a ledger key requires explicit operator approval** (README §4.1 rules 5 and 7), so the change
is prepared and left for the operator. Cosmetic with respect to the running world, which is
valid and serving.

**Unchanged from §10.3.** SIM-07 reproduces exactly: `packages.ros.org` presents
`subject=… CN=*.osuosl.org` and `curl` returns HTTP `000`. Certificate verification must not be
disabled to work around it. SIM-12 (facility scheduler) remains absent. SIM-02 remains an
operator decision. SIM-08 is a publishing decision and was not touched — no public port, route
or Cloudflare config was modified. SIM-03 (QGroundControl) is not installed on this host and
no install was attempted.

### 10.5 SIM-09 re-opened and properly closed, and a cross-session hazard

Measured 2026-10-04 in worktree `/tmp/ao-sessions/wt-sim` (branch `ai-sim`, base `1332005`).

#### SIM-09 is now closed against the actual acceptance criteria

§19 requires the centroid to be *added to the boning data* and the pose *recomputed from it*.
Commit `365bd42` satisfied neither: `boning.yaml` had no `centroid:` field, and the pose was a
literal in `factory.world` — the only file in `GAZEBO/`, `scripts/` or `quadlet/` mentioning
`camera_elev_arms`. So the two could silently disagree again, which is the recurrence the
item exists to prevent. Both are now done:

- `centroid:` added to all three cell datums, each equal to `origin+extent/2`.
- New `scripts/simulation/build-boning-cameras.py` derives each elevation pose from a new
  `elevation_cameras:` block in `boning.yaml` (`centroid_offset` + `yaw`).

The generated poses are byte-identical to the hand-written ones — correct, since §19 records
the three standoffs as already sound. This removes the manual re-aiming step and changes no
rendered view. A semantic XML comparison of the three `<model>` elements, HEAD vs now, is
identical after whitespace normalisation.

Guards, each proved by making it fail: standoff drift → `--check` exits 1; a stated centroid
disagreeing with `origin+extent/2` → refuses to generate; an XML comment containing `--` →
refuses. **The `--` guard is not theoretical** — a generated block containing the literal
`--write` in a comment stops the world parsing, because XML comments may not contain
`--`.

    $ python3 scripts/simulation/build-rl-objects.py --check     -> OK (exit 0)
    $ python3 scripts/simulation/build-boning-cameras.py --check  -> OK (exit 0)
    $ gz sdf -k GAZEBO/worlds/factory.world                      -> Valid.

#### Hazard: `--write` from any worktree was rewriting the LIVE world

`build-rl-objects.py` hardcoded `OBJECTS`/`WORLD` to `/ALWAYSON/...`. With one git worktree
per session, running `--write` from a worktree rewrote the live `/ALWAYSON` world instead of
the checkout in front of you, and `--check` reported on a file the caller was not editing.

Ten of the eleven worktrees still hold that defective copy, **and** they predate main's
`SPECULAR`/`SHININESS` fix (`a05f018`), so `--write` from one of them strips every
`<specular>` from the live world. **This has already fired:** `/ALWAYSON`'s world was
rewritten at 13:12:01 and its `rl_objects` specular count fell from **9 to 0**.

**A generator that writes to an absolute path must derive that path from the checkout in
use, never from a hardcoded constant, and `--check` must report on the file it would
actually write.**

Restored and verified — `/ALWAYSON/GAZEBO/worlds/factory.world` is byte-identical to its
committed state, `bce32f2a…`, 63205 bytes, 9 specular, `--check` OK, `gz sdf -k` Valid:

    $ git -C /ALWAYSON status --short -- GAZEBO/worlds/factory.world   -> empty
    $ sha256sum /ALWAYSON/GAZEBO/worlds/factory.world
      bce32f2a7ff035b4022db82d9a90267ca829261d08038d3e26e5ff3fe5f51053

**`build-rl-objects.py --write` must not be run from a worktree until this is fixed
everywhere.** The remaining defective copies are in other sessions' trees. Correcting a file
outside the owning section's scope requires either that section's own fix or the operator's
explicit approval — it must not be edited unilaterally.

### 10.6 SIM-14 is not closed, and a third generator defect (SIM-15)

Re-audited 2026-10-04 against §19's actual acceptance text rather than against earlier
verdicts. Two earlier conclusions were wrong, and both are retracted here.

**SIM-14 stays Open. §19 asks for objects "addressable and resettable"; only addressable is
delivered.** The `rl_objects` model does exist and §19.1's "That model does not exist" is
retracted — but `/api/reset` returns **404** and the portal performs no reset, so placement
cannot be returned to `home_pose` at run time. The §10.4 portal correction is what makes
this visible: `resettable_claimed` true beside `reset_available` **false**. A `close` was
filed on 2026-10-03 while this section's own text said the opposite. **A closure must be argued from the acceptance text, never from a proxy
property that merely correlates with it.**

    $ curl -s -o /dev/null -w '%{http_code}\n' -m 5 http://127.0.0.1:8765/api/reset   -> 404
    $ curl -s -m 5 .../api/status | python3 -c '...'
      link_count: 37
      rl links: 9 ['part_a1','part_a2','part_a3','stock_s1','stock_s2','stock_s3',
                   'target_bin_a','target_bin_b','target_shelf']

**SIM-13's close stands**, re-checked: 4 zones resolve, 3 interlocks are declared and all carry
`enforced_in_simulation: false`, and the 4 zones are live links in the served world. The model
exists and is honest that it actuates nothing. `printer-01` and `cnc-01` remain `[GAP]` and need
operator-supplied datums.

**SIM-15, new: `--write` is not position-idempotent.** A *correct* regeneration strips the
`rl_objects` block and re-appends it before `</world>`, silently reordering three generated
models in the world the live server has open. Measured on `/tmp/gen-test-sim`, never the live tree:

    $ python3 scripts/simulation/build-rl-objects.py --write   -> "already current; nothing written"
    # make a real catalogue change (part-a1 home_pose 6.20 -> 6.90), then rewrite:
    $ python3 scripts/simulation/build-rl-objects.py --check   -> STALE (exit 1)
    $ python3 scripts/simulation/build-rl-objects.py --write   -> wrote 3 groups / 9 objects
    #   rl_objects           547 -> 1289
    #   safety_zones         695 ->  548
    #   camera_elev_massing 1410 -> 1263
    $ gz sdf -k ...                        -> Valid.
    $ grep -c '<link name=' ...            -> 37 (unchanged; nothing lost)

No content is lost and the world stays valid, so this is a review-integrity hazard rather than a
runtime fault — which is why it survived so long unnoticed. It should replace the block in place.

**A heading inserted into a section file produces no error anywhere** — the compiler
concatenates happily — so prose damage from a bad edit is only visible by reading the
rendered README. An earlier revision of §10.5 had a heading inserted *mid-sentence*,
splitting the SIM-07 paragraph and orphaning its tail ("disabled to work around it.
SIM-12 …") at the far end of the subsection, where it read as part of the generator
hazard. **A rendered README must be read after a structural edit to a section file.**

### GUI verification: a live process is not a rendered geometry

`ActiveState=active` plus a clean error grep is **not** evidence that geometry renders —
this is the mistake §10.3 already warns about. The only reliable answer comes from
capturing the window and diffing two captures. Note also that `gz topic` run inside the
GUI container fails with "cannot find any available 'gz' command" when
`GZ_CONFIG_PATH` is merely unset; **check the environment variable before concluding a
toolchain is missing.**

### A measurement whose inputs may have drifted needs re-derivation, not re-execution

This is the recurring error in this section and is stated once here so it is not
repeated. Re-running a recorded command without re-deriving its assumptions returns a
confident wrong answer. Concretely: `/api/status` returns `links` and `link_count`
*nested* under `world`. A one-liner written before that change reads them at top level,
so it returns `[]` and `None` — zero RL links against a model that is fine and a query
that is stale.

The same class of error recurs in two guises, both of which substitute a proxy for the
criterion:

- verifying the *arithmetic* of a closure and treating that as having read the
  acceptance criteria;
- verifying the *existence* of a field and treating that as having met the criteria.

**A closure must be argued from the acceptance text, not from a property that merely
correlates with it.**

### 10.7 SIM-15 fixed: the generator is position-idempotent, and `--check` now proves it

Fixed 2026-10-04 in worktree `/tmp/ao-sessions/wt-sim`. `build-rl-objects.py --write` now replaces
the generated block at its canonical position instead of stripping it and re-appending it before
`</world>`. The canonical position is defined structurally, not by line number: immediately before
the `safety_zones` region, one of four generated regions the world carries in a fixed order
(`rl_objects`, `safety_zones`, `conveyor_loops`, `elevation cameras`).

A real catalogue edit now touches only the block. Before, the same edit reordered three models:

| | before | after |
|---|---|---|
| `rl_objects` | 547 → 1289 | 543 → 543 |
| `safety_zones` | 695 → 548 | 691 → 691 |
| `camera_elev_massing` | 1410 → 1263 | 1356 → 1356 |
| diff vs committed | whole-file reorder | 4 lines (552, 582) |

**`--check` also detects a reorder now, which it never did.** Content equality cannot see position,
and that is the whole defect. Verified by making it fail on a world reordered exactly the old way:

    $ python3 scripts/simulation/build-rl-objects.py --check
    MISPLACED: rl_objects block is followed by nothing, expected safety_zones.
    A reorder, not a content change. Repair with --write        (exit 1)

    $ python3 scripts/simulation/build-rl-objects.py --write
    wrote 3 groups / 9 objects (relocated before safety_zones)

Repair is exact — healing a reordered world reproduces the committed file byte for byte, which is
the property that makes the fix trustworthy:

    $ sha256sum /tmp/t5/GAZEBO/worlds/factory.world
      5667873ca41968bea3e41b68dbc03321a22e8553059271ec65b522a0657e7b26
    $ cmp GAZEBO/worlds/factory.world /ALWAYSON/... (committed)
      BYTE-IDENTICAL TO COMMITTED
    $ gz sdf -k GAZEBO/worlds/factory.world        -> Valid.
    $ grep -c '<link name=' ...                    -> 37   (unchanged)

Idempotency, staleness and the sibling generators, all on a scratch copy at `/tmp/t5`:

    $ python3 scripts/simulation/build-rl-objects.py --check   -> OK, exit 0
    $ python3 scripts/simulation/build-rl-objects.py --write   -> "already current; nothing written"
    $ sha256sum before/after second --write                    -> identical
    $ python3 scripts/simulation/build-boning-cameras.py --check -> OK, exit 0
    $ python3 scripts/simulation/verify_safety_zones.py         -> exit 0

The **live** tree was never a target: `/ALWAYSON/GAZEBO/worlds/factory.world` is still
`5667873ca41968bea3e41b68dbc03321a22e8553059271ec65b522a0657e7b26` and `git -C /ALWAYSON status`
is empty for both the world and the script. Every measurement above was taken on a scratch copy.

### A guard must be tested against the case it exists to catch

A guard asserting "a rewrite would be a no-op" is worthless: replacing in place is a
*fixed point* of relocation, so a world whose block had merely been moved to the end
still reports OK. **A passing test on the good world proves nothing about a check whose
job is to catch the bad one.**

Three further failure modes are recorded because each produced a file Gazebo could not
read:

- computing an anchor offset on the unmodified string and applying it to the
  already-shortened one, which splits a comment into `<` and `!--`
  (`Error Code 1: Unable to read file`);
- a blanket `\n{3,}` collapse, which eats blank lines across the whole document rather
  than at the seam;
- writing seam handling from intuition instead of measuring the committed file's actual
  spacing.

**A rewritten world must be byte-compared against the committed world after every
attempt**, and the seam must be derived from a measurement of the real file rather than
assumed.

### 10.8 Second pass: the SIM-15 fix re-verified from scratch, and a wrong number in SIM-10

Recorded 2026-10-04 in worktree `/tmp/ao-sessions/wt-sim`. §10.7 was written earlier and
its fix was **uncommitted**. Every claim here is re-derived on a fresh scratch copy at
`/tmp/verify15` rather than trusting recorded output, because **a handoff that says
"verified" is a claim, not evidence.**

**SIM-15 confirmed on all three limbs, reproduced from scratch.** The original defect is
reconstructed deliberately — the `rl_objects` block moved to just before `</world>`, exactly
as the old `--write` did — which confirms the region order inverted (`safety_zones` 544,
`conveyor_loops` 574, `elevation cameras` 1209, `rl_objects` 1285).

1. `--check` **catches** the reorder, which is the half the old guard could never do:

        MISPLACED: rl_objects block is followed by nothing, expected safety_zones.
        A reorder, not a content change. Repair with --write        (exit 1)

2. `--write` **heals it byte for byte** — the property that makes the fix trustworthy:

        wrote 3 groups / 9 objects (relocated before safety_zones)
        5667873ca41968bea3e41b68dbc03321a22e8553059271ec65b522a0657e7b26
        BYTE-IDENTICAL TO COMMITTED

3. A real catalogue edit (`part-a1` home_pose 6.20 → 6.90) is now `replaced in place`, a
   **4-line** diff confined to the two pose lines, with `gz sdf -k` → `Valid.` and
   `grep -c '<link name='` → `37` unchanged. Restoring the catalogue and re-writing returns
   the world to the same sha256.

The live tree was never a target and is provably untouched: `git -C /ALWAYSON status --short --
GAZEBO/worlds/factory.world scripts/simulation/` is empty and `/ALWAYSON`'s world is still
`5667873c…`. Both sibling generators are green in the real worktree
(`build-boning-cameras.py --check` → OK, `verify_safety_zones.py` → exit 0).

**The keep-open findings all still reproduce today**, re-measured rather than assumed:

| item | re-measured |
|---|---|
| SIM-07 | `packages.ros.org` still presents `CN=*.osuosl.org`; `curl` still `http=000` |
| SIM-10 | 34 parts, 33 exact cubes; still no `door`/`wall`/`floor` name |
| SIM-12 | only hit for "scheduler" repo-wide is an unrelated sidekiq comment |
| SIM-01 | `quadlet/sim-vehicle/` holds one file, `ao-ardupilot-sitl.container`; no vehicle GUI unit |
| SIM-03 | no `QGroundControl` on PATH or under `/opt` |
| SIM-14 | `/api/reset` still **404**, `/api/status` 200, `link_count` 37, all 9 RL links live |

**A wrong number in SIM-10, inherited from §19 and then propagated by me.** §19 describes the
parts of `massing_fab.dae` as "anonymous `group_0`–`group_25`". Counted, there are **13**,
`group_0`–`group_12`, in both `massing_fab.dae` and `massing_flat.dae` (the file the world
actually renders). The conclusion is unaffected — no semantic name anywhere and 33 of 34 parts
cubic, both verified directly — but the count is wrong and the compiler should correct it.

### A verification must be confirmed to have been set up before its verdict is accepted

A catalogue-edit test whose `sed` pattern does not match the file reports "already
current; nothing written" and reads as a passing test that changed nothing. `x: 6.20` is
not in `objects.yaml`; the line is `home_pose: [6.20, 2.10, ...]`.

**The tell is two results that cannot both be true:** an empty diff *and* a `--check`
that reports OK after an edit supposedly took effect. **A verification's verdict must not
be accepted until the verification has been shown to have actually run** — here, by
confirming the edit landed with `sed -n '34p'` before trusting the generator's output.

### 10.9 SIM-16: the running simulation is executing a world two commits out of date

Recorded 2026-10-05 in worktree `/tmp/ao-sessions/wt-sim`. Found while re-measuring SIM-06's
evidence, not while looking for it. **This is a new fault, not a restatement of SIM-06.**

The `ao-sim-fabrication-gz` container has been up, un-restarted, since **2026-10-03 18:19:21
PDT**. `factory.world` was modified on **2026-10-04 15:45:38**. The live simulation is therefore
running a **different world file** from the one in the repository — and from the one the portal
reports on.

**The timeline is unambiguous.**

    $ podman inspect ao-sim-fabrication-gz --format '{{.State.StartedAt}} {{.RestartCount}}'
    2026-10-03 18:19:21.186619129 -0700 PDT 0
    $ podman exec ao-sim-fabrication-gz ps -o etimes= -p 1
    136322                                   # 37.9 h, one continuous process
    $ stat -c '%y' /ALWAYSON/GAZEBO/worlds/factory.world
    2026-10-04 15:45:38.213485858 -0700

**The server logged exactly one load, and has not reloaded since.**

    $ grep 'Loading SDF world file' /ALWAYSON/logs/sim-gz-server.log.1 | tail -1
    2026-10-03T18:19:21.216 [info] [ServerPrivate.cc:697] Loading SDF world
    file[/ALWAYSON/GAZEBO/worlds/factory.world].
    # same grep filtered to later than that timestamp -> EMPTY (no reload)
    # rotated-in /ALWAYSON/logs/sim-gz-server.log -> 0 matches

**What is actually running versus what is committed.** The container's `/proc/1/cmdline` is
`gz-sim-server /ALWAYSON/GAZEBO/worlds/factory.world`, and `/ALWAYSON/GAZEBO` is a **bind mount**
into it — so the server reads the file once, at startup, and never again. Comparing that startup
commit against HEAD:

| | loaded (`c24f673`, at 18:19:21) | committed (`78b4e60`) |
|---|---|---|
| massing mesh | `massing_fab.dae` | `massing_flat.dae` |
| `<emissive>` tags | `0.72 0.72 0.74 1` | *none* |
| massing diffuse | `0 0 0 1` | `0.58 0.58 0.60 1` |
| models / links / poses | 61 entries | 61 entries — **identical** |

The last row is the useful part, and it is why this went unnoticed: `model/link+pose` inventory
compares **byte-identical**, so every structural check anyone ran against the file — link counts,
boned poses, RL object presence — passes on the running server too. **Only the rendering differs.**
The building you see live is drawn with the old emissive material and the old mesh, which is
exactly the appearance the commits `dc72f5c` → `c24f673` → `ec34c71` were iterating away from.

**RETRACTION — the visual half of the SIM-06 closure does not hold.** The `import`
capture in the SIM-06 proposal proves the GUI client renders *a* world; it cannot prove it
renders *this* world, and it demonstrably did not. The GUI is running against the server
above, so the screenshot shows `massing_fab.dae`. SIM-06 stays **closed on the
client-build criteria** (unit starts, 18 plugins, ogre2 engine, 6762 distinct colours, no
render errors) and the visual must be re-shot after a restart. **That restart is a live
service restart and requires explicit operator approval** (README §4.1 rule 6).

**A second, smaller instance of the same class: the portal cannot detect this.** `world_summary()`
in `scripts/simulation/ao-sim-portal.py` parses the **file on disk** (line 209-223), and
`objects_summary()` likewise. Neither asks the server what it loaded. So `/api/status` returns
`link_count: 37` from the file while the server holds a different document — the portal will
report "consistent" across a restart-induced divergence. The fix is to have the portal read
`/world/factory/dynamic_pose/info` (which is published and reachable from
`ao-sim-fabrication-foxglove` via `gz topic -e -t /world/factory/dynamic_pose/info -n 1`, returning
`rl_objects` plus per-link poses) and report loaded-vs-committed separately.

### The live world file is not the simulation

Reading the live world *file* and calling it "the simulation" is the error this
subsection is written to prevent. It makes every file-based check — including the
§10.7/§10.8 generator verification — silent about what the server actually holds.
Verification
the repository, which was correct for those questions, but it creates a habit of treating
repository state as simulation state. **They are different objects with a load boundary
between them, and that boundary must be looked for explicitly.**

Two contributing causes are recorded because both will recur:

- `/world/factory/scene/info` returns 0 bytes to a plain subscriber and
  `/world/factory/generate_world_sdf` times out at 20 s, so the obvious direct probes
  both fail;
- when the direct probe fails, the answer is in the log — and the useful log is the
  **rotated** one, one `grep` away (see the traps below).

**Traps for the next session.** `logs/sim-gz-server.log` is **empty**; the useful history is in
`logs/sim-gz-server.log.1`. `gz topic -l` on the host returns nothing — the server advertises
`GZ_IP=10.89.5.10` on an internal bridge, so probes must run from
`ao-sim-fabrication-foxglove`, which shares the L2 segment, and `/opt/ros/lyrical/opt/gz_tools_vendor/bin/gz`
must be called by full path (it is not on `PATH`). `gz service -s /world/factory/generate_world_sdf`
times out; do not build a plan on it.

> **Superseded in part by §10.10.** SIM-16 re-confirmed still open, the restart proven safe to
> perform, and one claim here corrected: `camera_elev_arms` **is** present in the loaded world —
> the 80-line diff hunk is a block relocation, not a deletion.

### 10.10 SIM-16 re-measured, and the restart is now proven safe to perform

Recorded 2026-10-05, second pass in worktree `/tmp/ao-sessions/wt-sim`. SIM-16 **still holds** —
it is not a transient and it does not self-heal. What is new is that the operator's decision can
now be made on evidence rather than on trust, and one of §10.9's claims is corrected.

**SIM-16 re-confirmed, unchanged.** Same numbers as §10.9, re-measured rather than quoted:

    $ podman inspect ao-sim-fabrication-gz --format '{{.State.StartedAt}} restarts={{.RestartCount}}'
    2026-10-03 18:19:21.186619129 -0700 PDT restarts=0
    $ podman exec ao-sim-fabrication-gz ps -o etimes= -p 1
    137327                                   # +1005 s since the §10.9 reading
    $ stat -c '%y %s' /ALWAYSON/GAZEBO/worlds/factory.world
    2026-10-04 15:45:38.213485858 -0700 62883

`podman ps` renders this as `Up 38 hours`, which reads like a recent start and is the reason a
casual glance misses it. The uptime counter keeps counting; the world file does not get re-read.

**"Safe by construction" is an argument, not a measurement.** A restart of a digest-pinned
unit holding a `ro` bind mount is not destructive by construction — the container has no
write access to the world — but that claim must be **demonstrated before a live restart is
requested**, by loading the *current* committed world in a throwaway container from the
**same pinned digest**, on a **separate `GZ_PARTITION`**, with a bounded iteration count and
`--rm` so it cleans itself up:

    $ podman run --rm --name ao-sim-worldcheck \
        -e GZ_PARTITION=ao_sim_worldcheck_$$ -e GZ_SIM_RESOURCE_PATH=/ALWAYSON/GAZEBO/models \
        -e HOME=/tmp -v /ALWAYSON/GAZEBO:/ALWAYSON/GAZEBO:ro \
        --entrypoint /usr/libexec/gz/sim10/gz-sim-server \
        localhost/gz-sim10-server@sha256:55f8dbcf8decb0b97c6be7cf2fde8859b0fd05735c7a759df09a12e091933581 \
        /ALWAYSON/GAZEBO/worlds/factory.world -r -s -v 4 --iterations 400
    exit=0
    $ grep -c '\[err\]' /tmp/worldcheck.log
    0

Clean exit, 400 iterations, zero errors. The world that is committed **is** loadable by the
pinned image; a restart will not fail and will not leave the simulation down. The two warning
classes it does emit (`<gui><camera> can't be converted yet`, and `Ogre2Camera::SetVisibilityMask`
reserved-bit notices from the eight cameras) are pre-existing and are not errors.

Two safety properties must be preserved, because getting either wrong violates a stop
condition rather than merely being untidy:

- **A separate `GZ_PARTITION`.** The live server advertises `alwayson_fabrication_sim` at
  `GZ_IP=10.89.5.10`. A second server on the same partition would have injected a duplicate
  publisher for every topic and every GUI client on the network would have attached to whichever
  answered first. A distinct partition makes the check invisible to the running system.
- **No `--network` join to `ao-sim-fabrication`, and no control of the live unit.** The check ran
  on the default network with no route to the domain. No restart, stop, signal or exec
  into `ao-sim-fabrication-gz` may be performed beyond read-only
  `inspect`/`ps`/`cat` of `/proc/1`.

**Correction to §10.9: `camera_elev_arms` is NOT missing from the loaded world.** A naive
read of the diff suggests the loaded world lacks the SIM-09 elevation camera, because the diff
shows an 80-line block (`542,621d541`) removed. It does not. The camera is present in both, at
an identical pose, and the block is a *relocation* — the comment and model moved position in the
file, which `diff` renders as a delete plus an insert elsewhere:

    $ git show c24f673:GAZEBO/worlds/factory.world | grep -c '<model name="camera_elev_arms"'
    1
    $ git show HEAD:GAZEBO/worlds/factory.world | grep -c '<model name="camera_elev_arms"'
    1
    $ # pose in both, identical:
    <pose>6.401 4.056 1.151 0 0.0000 -1.5708</pose>

**A relocation hunk is not a deletion.** Reading a unified-diff hunk header as a semantic
removal leads to filing a false regression: an 80-line block (`542,621d541`) that is merely
*relocated* reads as removed. SIM-09's fix **is** rendered on the live server. **The correct
check is presence-and-value counts per named entity, not hunk headers** — this is the
diff-shaped version of the same mistake §10.9 describes.

**What actually differs between loaded and committed, measured.** 167 changed lines total, and
they are confined to three things: the massing mesh URI, the massing material block, and the
`camera_elev_arms` block position. The entity inventory is identical, confirmed by hashing the
sorted entity names rather than reading them:

    $ for c in c24f673 78b4e60; do git show $c:GAZEBO/worlds/factory.world \
        | grep -oE '<(model|link) name="[^"]*"' | sort | sha256sum; done
    a95679bcc654bb2a7a5ff97817bfab19bca3918ce56165154343a83f1f066a57   # c24f673 (loaded)
    a95679bcc654bb2a7a5ff97817bfab19bca3918ce56165154343a83f1f066a57   # 78b4e60 (committed)
    # sizes: 63190 vs 62883

Identical hashes. So the blast radius of SIM-16 is **exactly the massing mesh and its material**,
and nothing else. The boned datums, the RL objects, the safety zones, the link poses and all
eight cameras are correct on the live server. That is why the divergence survived a fortnight of
structural checks, and it is also why the restart is low-risk: nothing structural is at stake.

**The portal blind spot is confirmed by reading the code, and the fix belongs to whoever owns
`scripts/simulation/ao-sim-portal.py`.** `world_summary()` parses `WORLD` off disk;
`unit_state()` `os.stat`s the same path and reports `modified_epoch`. Neither has any notion of
a load event, so the portal will report the file as authoritative and stay silent across exactly
the divergence it exists to reveal. The minimal fix, for the portal's owner: stat the world and
compare its mtime against the server's start time, and surface a `stale_since_restart` flag when
`world.mtime > server.started`. That needs no gz-transport probe — the two values are both
already reachable, `os.stat` for one and a read-only `podman inspect` for the other — which keeps
the portal's view-only guarantee intact. The richer version, reading
`/world/factory/dynamic_pose/info` as §10.9 proposed, needs a second hop and is not worth the
complexity for a flag that a timestamp comparison gives directly.

**The restart requires explicit operator approval.** `systemctl --user restart
ao-sim-fabrication-gz` is a live service restart (README §4.1 rule 6). The exact command, once
approved, is that one — no Quadlet edit is needed, because the world file is a bind mount and
the restart picks up the committed file as-is.

### This section's characteristic failure: accepting a representation as the thing

Three successive passes hit the same class of error in three disguises — recorded in §10.5,
§10.8 and here. It is worth naming as one failure:

1. reading the live world *file* and calling it the simulation (§10.9);
2. re-running a recorded command whose inputs had drifted (§10.5);
3. reading a diff hunk header as a semantic deletion (this subsection).

The contributing cause is reaching for a tool optimised for humans skimming changes — `diff`
— when the question is "does entity X exist with value Y in both versions". **A counted grep
answers that directly. Check the value, not the hunk, and never accept a representation's shape
as evidence about the thing it represents.**

---

# 11. Ledger, Provenance, Archive, and IPFS

## 11.1 Ledger Authority Policy

Corda is the authoritative ledger for approved business provenance, receipt, entitlement,
fulfillment-approval and release-approval records. It is **not** the authoritative store for
domain-operational source data — that stays in the related PostgreSQL database (§3.3.b).

**Corda runs on Corda 5 against `cordadb`**, a separate logical database on the host
PostgreSQL 18 cluster with its own roles and backup scope. H2 is not an acceptable backing
store for this node. Roles, host-loopback binding, backup scope, restore procedure, and
separation from the sales and mapping databases are specified in §17.1 and §3.3.1.

| Area | Authoritative operational data | Network |
|---|---|---|
| Sales | Sales PostgreSQL order, fulfillment, and customer-service records | `ao-sales` |
| Payment | Verified provider event record and normalized payment state | `ao-payment` (ingress via `ao-ingress-payment`) |
| Field | Raw packet store, telemetry spool, and mission records | `ao-field` |
| Mapping | Validated imagery, WebODM project data, processing outputs, and deliverables | `ao-mapping` |
| Vehicle simulation | Scenario definitions, run data, and result artifacts | `ao-sim-vehicle` |
| Fabrication simulation | Facility/task models, safety scenarios, and result artifacts | `ao-sim-fabrication` |
| Archive | Encrypted archive objects and retention records | `ao-egress-archive` |
| Ledger | Corda state, PKI, and the complete ledger of debits and credits | `ao-ledger-core` |

Network names are the real Podman names used throughout this document, in the Quadlet
definitions, and in `config/platform/network-cidrs.yaml`. Where an area is served by a
controlled adapter rather than a workload network, the adapter is named in the same cell.

One row is an adapter and has **no network of its own**: `ao-egress-archive` is absent
from both `config/platform/network-cidrs.yaml` and `podman network ls`. Every other
network named in the table above is present in both. This is measured, not inferred:

```text
$ grep -c '^ao-' config/platform/network-cidrs.yaml
14
$ grep -n 'ao-egress-archive' config/platform/network-cidrs.yaml
(no match)

$ podman network ls --format '{{.Name}}' | grep -c '^ao-'
14
$ podman network ls --format '{{.Name}}' | grep -c 'ao-egress-archive'
0
```

The registry and the live host agree on fourteen `ao-*` networks, eleven
`Internal=true` and three `Internal=false` — so the archive row is a genuine
exception, not a counting artefact. `config/platform/topology-model.yaml` already
records it correctly as `adapter: true`, `status: planned`. See §11.6.1.

Corda records signed references, hashes, approved transitions, and entitlement and
provenance data sufficient to verify a claim without duplicating sensitive or high-volume
data.

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
        ├── Metabase  (REPORTING — reads salesdb)
        │       └── sales/marketing reports and PDF exports
        │
        ├── Grafana  (dashboards and metrics — reads approved PostgreSQL)
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
3. Confirm the Metabase reporting identity can read `salesdb` and produce the
   standard PDF reports and receipts, and confirm the Grafana datasource can
   read it for dashboards. Neither tool writes into `salesdb`.
4. Define the signed manifest schema and correlation-ID uniqueness rule.
5. Implement ledger-ingest authorization, signature verification, idempotency,
   replay protection, and audit logging.
6. Complete the Corda key/certificate ceremony.
7. Test the complete correlation path with synthetic data before connecting
   real sales, payment, customer, or product records.

### 11.2.2 Mandatory Corda Entry Evidence

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

The three records must resolve to the same:

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
three gates; it must not store raw payment credentials or unrestricted email
content. PostgreSQL stores the detailed evidence metadata and reporting
projection. Metabase is for reporting and Grafana is for dashboards and metrics;
both show the resulting confirmed state and neither performs or waives the
verification.

Before the three gates can be satisfied, the operator key/certificate ceremony
must be complete and the correlation path must be proven with synthetic data.

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

### 11.2.4 Ledger-Ingest Probe Status

The ingest-path probe `scripts/validation/check-ledger-ingest.sh` is **resolved and
deterministic**, not missing or blocked. It runs unprivileged and requires no
pending operator command:

```text
$ bash /ALWAYSON/scripts/validation/check-ledger-ingest.sh
PENDING: ledger-ingest gateway not deployed yet (Section 2.8 step 3 awaits Corda version approval)
$ echo $?
3
```

Exit `3` is a defined **PENDING** state, distinct from a failure (`44`) and from
healthy (`0`). The script exits `3` before any network call because no container
named `ledger-ingest` exists — confirmed independently:

```text
$ podman ps -a --format '{{.Names}}' | grep -c 'ledger-ingest'
0
```

There is therefore no unresolved socket-bridge fault to diagnose. The probe is
blocked only by the gateway not being deployed, which is downstream of the
Corda 5 node build and the operator key ceremony. No privileged command is
pending for this item.

Signing and submission are likewise staged, not broken:
`scripts/ledger/sign-manifest.sh` signs and `scripts/ledger/submit-ledger-event.sh`
stages unsigned-or-unsubmitted manifests to
`artifacts/pending-ledger-submissions/<YYYYMMDD>/` and exits `3`, so nothing is
lost while the gateway is absent. Ingest security properties (§11.2.1) are
therefore **specified and enforced client-side**, but remain **unproven end to
end** until the gateway exists.

### 11.2.5 Ingest Security Requirements (specified, not yet enforced by a gateway)

The ingest gateway must enforce all of the following. Each maps to a control in
§11.2.1 and §4.4; none is satisfied by the current staging behaviour.

| # | Requirement | Enforced by | Current state |
|---|---|---|---|
| 1 | Mutual TLS; one client certificate per exporter domain | Gateway | Not implemented — no gateway |
| 2 | Path authorization against `config/ledger/authorization-policy.yaml` | Gateway | Policy file exists, no enforcer |
| 3 | JSON Schema validation against `config/ledger/manifest-schema.json` | Gateway | Schema exists; `additionalProperties: false` |
| 4 | Detached signature verification against the exporter's registered key | Gateway | **Signer-side only.** `sign-manifest.sh` signs; nothing verifies |
| 5 | `producer_key_id` must match the mTLS certificate identity | Gateway | Not implemented |
| 6 | Idempotency on `correlation_id` (§11.2.1) | Gateway | Required by policy, unenforced |
| 7 | Replay defence — reject a re-presented digest/timestamp | Gateway | Not implemented |
| 8 | Audit log of accept **and** reject, with reason code | Gateway | Not implemented |

Two design points an implementer should not get wrong:

- **Minimization is enforced at the schema, not by convention.** The manifest
  schema is `additionalProperties: false` and requires no field outside
  `config/ledger/manifest-schema.json`. A payload carrying raw customer PII,
  card data, or telemetry is therefore *rejected*, not merely discouraged.
- **A `sales_receipt` manifest requires `transaction_id`**, enforced by the
  schema's conditional (`if object_type == sales_receipt then required
  [transaction_id]`) and again by `build-manifest.sh`, which rejects a
  `sales_receipt` without an issued `transaction_id` (exit `12`).

Until rows 1–8 exist in a running gateway, **LEDGER-03 stays open**. What is
demonstrable today is only the client half: build → sign → stage. Signing proves
a manifest is well-formed and signed; it proves nothing about acceptance,
authorization, or replay defence, because there is no acceptor to test.

#### What the client half actually does — exercised, not assumed

Run against synthetic content only; no real sales, payment, customer, or product
record was used, and the staged test artifact was deleted afterwards.

```text
$ bash scripts/ledger/build-manifest.sh sales_receipt sales <file> testref
ERROR: sales_receipt requires issued transaction_id          # exit 12

$ bash scripts/ledger/build-manifest.sh telemetry_batch field <file> testref
exit 0; object_type=telemetry_batch, origin_domain=field, content_size_bytes=23, signature=""

$ bash scripts/ledger/submit-ledger-event.sh <unsigned-manifest>
ERROR: manifest is unsigned (run sign-manifest.sh first)      # exit 20

$ bash scripts/ledger/submit-ledger-event.sh <signed-manifest>
PENDING: gateway not deployed; manifest staged for later submission   # exit 3

$ bash scripts/ledger/verify-ledger-receipt.sh RCPT-FAKE-0001 <manifest>
FAIL: receipt mismatch                                        # exit 50
```

So the **unsigned-rejection** and **schema conditional** behaviours are real and
now verified by execution rather than by reading the source.

#### A real weakness: staging does not validate the signature

`submit-ledger-event.sh` checks only that `.signature` is a **non-empty string**
(`jq -r '.signature // empty'`, then `[[ -n "$sig" ]]`). A deliberately bogus
value is accepted and staged:

```text
$ jq '.signature="ed25519:SYNTHETIC_NOT_A_REAL_SIGNATURE"' m.json > m3.json
$ bash scripts/ledger/submit-ledger-event.sh m3.json
PENDING: gateway not deployed; manifest staged for later submission   # exit 3
```

This is **not currently a security hole**, because the manifest goes to a local
staging directory and is never transmitted — there is no gateway to accept it.
It becomes one the moment row 4 (server-side signature verification) is skipped.
Therefore:

- The gateway **must** verify the detached signature cryptographically against
  the exporter's registered key and **must not** trust `producer_key_id` or the
  embedded `signature` field as supplied (row 5).
- Anything replayed out of `artifacts/pending-ledger-submissions/` after the
  gateway comes up is untrusted input and must traverse the full row 1–8 set.
- If a future staging replay tool re-signs locally instead of submitting, it
  creates records that look operator-approved and are not.

The empty `producer_key_id` and `authorization_policy_id` fields that
`build-manifest.sh` emits are currently unpopulated placeholders. They must be
filled by the gateway from the authenticated mTLS identity, never from the
submitted body.

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

Corda tracks the transaction ID, state, hashes, references, and authorized
signatures. PostgreSQL retains the operational/reporting projection keyed by
the same transaction ID. Metabase reports the confirmed state and Grafana shows
it on a dashboard; neither creates or waives payment verification.

### 11.3.1 Accounting Model for the Authoritative Ledger

Corda is the authoritative record of **approved postings**. PostgreSQL remains
authoritative for **source operational data** (§11.1). The two are not in
conflict: a posting is an approved assertion that a business event occurred, and
it exists only after the event is verified and reconciled. The accounting report
required by §4.4 is **computed in reporting**, from approved PostgreSQL rows
joined to approved Corda postings by the correlation tuple — never from a balance
stored as a mutable field on the ledger.

#### Accounts

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

#### Debit/credit entry semantics

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

#### Currency handling

A posting is **single-currency**. Multi-currency is handled by separate postings
plus an explicit `FX_REVALUATION` event carrying `from_currency`,
`to_currency`, `rate_source`, and `rate_as_of_utc`. The rate is a recorded input,
never computed silently. There is no implicit conversion at read time.

#### Posting rule (what may be posted, and when)

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

#### Reconciliation between Corda and `salesdb`

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

#### What the §4.4 accounting report is

`Standard accounting/ledger report PDF → ao-admin reporting output` (§4.4) is a
**computed projection**, built from approved `salesdb` rows joined to approved
Corda postings by the correlation tuple. It reports postings, not stored
balances. It cannot create, waive, or infer a payment state: §11.2.2 gate
evidence and the Corda posting must both be present, or the line does not appear.

## 11.4 Corda Does Not Store

Corda may store approved encrypted private transaction data as described in §11.3. It must
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
  post-sale marking/transfer mechanism only (ES.1); it is not archive, accounting,
  or ledger storage, and Corda has no IPFS dependency.
- **IPFS is for file-transfer verification and, potentially, sales listing on a
  blockchain.** It is not a backup, not a disaster-recovery copy, and not a retention
  store.
- **pCloud replication here is a transfer copy, not the backup set.** The backup set is
  restic (§17.1).
- Archive replication occurs only through `ao-egress-archive`.

### 11.6.1 pCloud Archive Credential Status

`ao-egress-archive` **does not exist as a Quadlet, a container, or a network.**
This is the concrete reason LEDGER-04 cannot progress:

```text
$ find quadlet -ipath '*archive*'          # no output
$ podman ps -a --format '{{.Names}}' | grep -c -E 'archive|egress'
0
```

Only the policy file exists (`config/pcloud/replication-policy.yaml`), which
constrains scope but provisions nothing. **Credentials cannot be provisioned into
a service that has no unit, so the `ao-egress-archive` adapter must be built
before LEDGER-04's acceptance criteria are executable as written.**

Note the naming mismatch for whoever builds it: §11.1 and §4.4 call this
component **`ao-egress-archive`**; the LEDGER-04 acceptance criteria call it
**`ao-archive`**. Use **`ao-egress-archive`** — it is the name used in the
architecture, the network table (§11.1), and the approved-path table (§4.4).

When it is built, credential handling is **presence-only**: prove an entry
exists by name and non-zero length, never print, copy, or export the value.
**No replication test may be run without credentials, which are a stop
condition (README §4.1 rule 14).**

## 11.7 Corda 5 Node Build Status and Blockers

**The node is not built. No Corda 5 node exists, and none can be built by an
agent session.** The artifacts are present and verified, but the remaining steps
are operator-only key ceremonies (§11.2, README §4.1 rule 14).

### What is verified in place

```text
$ sha256sum -c corda-combined-worker-5.2.2.0.jar.sha256sum   # in data/corda-install/
corda-combined-worker-5.2.2.0.jar: OK
```

Corda 5.2.2 worker JAR, CLI installer, and notary plugin are staged in
`data/corda-install/` with checksum sidecars. The Corda 4.14.2 / H2 installation
was retired on 2026-09-29 under operator approval — see
`logs/operations/2026-09-28-corda4-retirement.md`.

### Correction to the bootstrap runbook — service account name

`docs/runbooks/ledger-bootstrap.md` says the service account is
`alwayson-ledger`. **That is wrong**, and an agent that trusts it will build the
node under the wrong identity or wrongly conclude the account is missing. The
account exists as **`ao-ledger`**:

```text
$ getent passwd ao-ledger
ao-ledger:x:994:974:ALWAYS ON ledger core service:/home/alwayson-ledger:/usr/sbin/nologin

$ getent passwd alwayson-ledger ; echo $?
2
```

`alwayson-ledger` is the **home directory**; `ao-ledger` is the **username**.
Two further claims in that same runbook block are also false — "linger enabled"
and "systemd user unit installed" — and the consequence is that its step 5 cannot
succeed even after the name is corrected. See **§11.10**.
`/home/alwayson-ledger` is not readable by the operator's own `scottw` account,
so a direct `ls` returns `Permission denied`. That refusal is correct behaviour,
not a missing account — do not "fix" it by loosening the mode or by running the
node as `scottw`. Note also that the retirement log (`…corda4-retirement.md`)
already used `alwayson-ledger` for uid 994, so this same error is present there.

### The blocking conditions, in order

1. **Ledger keys (LEDGER-01).** The TLS certificate chain and keystores for the
   Corda 5 cluster require the operator to hold the passphrases in KWallet under
   `ao-ledger`. An agent must not generate, export, or activate production ledger
   keys. **Stop condition.**
2. **The `cordadb` owner role password (LEDGER-02, LEDGER-07).** The `corda`
   role has no working password, so `preinstall check-postgres` cannot pass.
   Resetting a role password is a credential change. **Stop condition.**
3. **The encrypted worker config.** Produced by `corda-cli.sh config encrypt`
   from operator-held secrets and installed `0600`. It cannot be generated
   without the operator's key material.
4. **Linger is not enabled for `ao-ledger`, and no `ao-ledger-core.service`
   unit file exists.** Not credential work, but the runbook's start command
   cannot succeed without them. Measured and detailed in §11.10.

Until step 1 completes, the node cannot be created, the ledger is **not
production-ready**, and no receipt, entitlement, or provenance record can be
final (§11.2.3).

### What could not be verified unprivileged

Database state cannot be measured from an unprivileged account. Both PostgreSQL
paths are closed to it, and neither failure means the database is absent:

```text
$ psql -tAc 'select 1'
psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed:
FATAL:  role "scottw" does not exist

$ sudo -n -u postgres psql -tAc "SELECT count(*) FROM pg_tables WHERE schemaname='public';"
sudo: interactive authentication is required
```

The "0 tables in `cordadb`" claim in §19 for LEDGER-07 is therefore **carried
forward from §19 and NOT re-verified here**. It should not be repeated as
established fact until the operator runs:

```bash
sudo -u postgres psql -tAc "SELECT count(*) FROM pg_tables WHERE schemaname='public' AND tablename NOT LIKE 'pg_%';"
sudo -u postgres psql -tAc "\du corda"   # inspect role state; do not print the password
```

### The node build is native, not containerised — and that is deliberate

Corda 5 ships no official container image. Ledger core therefore runs as a native
systemd user unit for `ao-ledger`, bound to loopback PostgreSQL. This is a
**documented deviation** from the Podman-and-Quadlet-only rule (README §4.1 rule
5) and is the single place it applies. It is recorded here so it is not later
mistaken for an oversight. It widens **no** listener and uses **no**
`--privileged`; the node is not reachable from any workload network. The two
`ao-ledger-core` and `ao-ledger-ingest` Quadlet networks are nevertheless
defined in `quadlet/networks/` and remain `Internal=true`, ready for the
gateway.

---
## 11.8 Second-Pass Verification, 2026-10-04 (LEDGER session)

Every factual claim in §11.7 is re-measured from the live system rather than
carried forward from a prior pass. The worker JAR checksum is `OK`, `ao-ledger`
is uid 994, `alwayson-ledger` is not a username, and no Corda node unit exists.

**Measuring "does the ledger unit exist?" — use `LoadState`, not `is-active`.**

```text
$ systemctl --user is-active ao-ledger-core.service
inactive                                  # exit 4  -- MISLEADING

$ systemctl --user show ao-ledger-core.service \
    -p LoadState -p ActiveState -p FragmentPath
LoadState=not-found
ActiveState=inactive
FragmentPath=
```

`is-active` prints the word `inactive` and exits 4 **both** when a unit does not
exist and when it exists but is stopped. Only `LoadState=not-found` with an empty
`FragmentPath` proves the unit was never installed. Here the truth is the latter:
**the ledger core was never built — it is not merely stopped.** Do not attempt to
start or enable it. **This trap is easy to fall into and produces a false
negative about whether a unit was ever installed.**

**Standing correction to §19 (LEDGER-07).** §19 states `cordadb` "holds 0 tables".
That figure remains **carried forward and unverified**. Neither the 2026-10-03
session nor this one could measure it — `psql` fails authentication for `scottw`
and `sudo -u postgres` requires interactive auth. An authentication failure is
**not** evidence that a database is empty, so §19's figure must not be restated
as established fact. To confirm:

```bash
sudo -u postgres psql -tAc \
  "SELECT count(*) FROM pg_tables WHERE schemaname='public' AND tablename NOT LIKE 'pg_%';"
sudo -u postgres psql -tAc "SELECT rolname, rolcanlogin FROM pg_roles WHERE rolname='corda';"
```

The second command deliberately selects no password column.
---

## 11.9 Producer-Key Coverage Gap in the Ingest Path (2026-10-04)

This section records a defect **not** previously documented, found by running the
ingest scripts rather than reading them. It concerns LEDGER-03
("ingest accepts only approved signed data") and is a prerequisite for the
gateway build. `scripts/` is not owned by this specification, so this is a
**report, not a fix**.

### Finding 1 — only 2 of the 6 authoritative domains can sign

§11.1 makes six domains authoritative operational data that feeds the ledger:
Sales, Payment, Field, Mapping, Vehicle simulation, Fabrication simulation.
`sign-manifest.sh` can obtain a key from KDE Wallet for exactly **two** of them:

```text
$ grep -oP 'wallet:ao-[a-z-]+' /ALWAYSON/scripts/ledger/sign-manifest.sh | sort -u
wallet:ao-sim-fabrication
wallet:ao-sim-vehicle
```

The mapping is a literal `case` with two arms. **Sales, Payment, Field and
Mapping have no wallet-backed signing path at all.** A manifest from those domains
can only be signed with a private-key *file path*, which is exactly the path the
script labels "for migration/testing". Since Sales is the domain that actually
produces the `sales_receipt` object type, the strongest provenance guarantee in
§11.2.2 is currently unavailable for the record type that matters most.

### Finding 2 — an unsupported wallet key fails with a misleading error

```text
$ bash /ALWAYSON/scripts/ledger/sign-manifest.sh manifest.json wallet:ao-sales
ERROR: manifest or key missing (keys live in KDE Wallet ao-sim-*; file path accepted for migration/testing)
EXIT=10
```

The `case` falls through, `wallet_key` stays empty, and the literal string
`wallet:ao-sales` is then tested as a **file path**. The operator is told a file is
missing when the real problem is that this wallet key is unimplemented. Exit `10`
is indistinguishable between the two causes.

### Finding 3 — `origin_domain` is never validated

`build-manifest.sh` validates `object_type` against a closed `case` list but
passes `origin_domain` straight through to `jq`:

```text
$ bash /ALWAYSON/scripts/ledger/build-manifest.sh map_product TOTALLY_MADE_UP_DOMAIN p.txt ref://x | jq -r .origin_domain
"TOTALLY_MADE_UP_DOMAIN"
EXIT=0
```

An invented domain is accepted and stamped into the manifest. Since
`origin_domain` drives the §11.1 authority decision, an unvalidated value means a
manifest can claim authority it does not have. It must be validated against the
closed §11.1 set at build time **and** re-derived from the authenticated mTLS
identity at the gateway, never trusted from the body.

### Finding 4 — the staged queue already contains unverified-key material

One manifest is staged from 2026-08-24:

```text
$ jq -r '{producer_key_id, authorization_policy_id, sig_len:(.signature|length)}' \
    /ALWAYSON/artifacts/pending-ledger-submissions/20260824/manifest.json
{ "producer_key_id": "test", "authorization_policy_id": "", "sig_len": 96 }
```

`producer_key_id` is `"test"` and `authorization_policy_id` is empty — neither
identifies a registered producer. Staging performs **no** cryptographic check: a
manifest with a fabricated signature and an invented `producer_key_id` is accepted
and staged, exit `3`.

**A negative test must never use pre-existing project data.** The probe manifest
used to establish this must be created for the test and removed afterwards; the
20260824 manifest is pre-existing project data and must be left untouched.
**Nothing may be signed, transmitted, deleted from the project, or written to any
external system by such a test.**

### What this means for LEDGER-03

§11.2 requires signature verification against the exporter's **registered** key. As
written, the producer-key model cannot satisfy that for four of six domains, and
`producer_key_id` is self-asserted rather than registered. The gateway must not be
built on the assumption that a non-empty `signature` implies an authorised
producer. Recommended, for the operator — each needs approval since keys and
credentials are a stop condition:

1. Provision wallet entries for `ao-sales`, `ao-field`, `ao-mapping` (and
   `ao-payment` if it submits directly) and extend the `case` in
   `sign-manifest.sh`. **Credential work — operator only.**
2. Make an unrecognised `wallet:` argument fail with its own distinct exit code,
   not by masquerading as a missing file.
3. Validate `origin_domain` against the §11.1 closed set in `build-manifest.sh`.
4. Treat everything in `pending-ledger-submissions/` as **untrusted replay input**;
   the 20260824 entry with `producer_key_id: "test"` must not be auto-submitted
   when the gateway comes up.

---

## 11.10 Third-Pass Verification, 2026-10-04 (LEDGER session)

§11.7, §11.8 and §11.9 are re-measured from source rather than trusted, and the
inherited claims reproduce — see the ledger in
`agents/COORDINATION (README UPDATES)/proposals/ledger-LEDGER-0*.md` for the raw command output.

**§11.7 understates the blockers.** It lists three. There are at least five, and
the two added here are not credential work.

### The bootstrap runbook's "State after scaffold" is wrong in two places

`docs/runbooks/ledger-bootstrap.md` opens with a block asserting completed state.
Two of its four assertions are false, and both were carried forward unchallenged
by the first two passes, which checked only the account **name**:

```text
# Runbook line 4:  "- Service account `alwayson-ledger` (linger enabled)"
$ loginctl show-user ao-ledger -p Linger
Failed to get user: User ID 994 is not logged in or lingering

$ loginctl list-users
 UID USER   LINGER STATE
1000 scottw yes    active
1 users listed.

# Runbook line 9:  "- systemd user unit installed: `ao-ledger-core.service` (**not started**)"
$ systemctl --user show ao-ledger-core.service -p LoadState -p FragmentPath
LoadState=not-found
FragmentPath=

$ systemctl --user list-unit-files | grep -iE 'ledger|corda'   # no output, rc=1
$ systemctl list-unit-files          | grep -iE 'ledger|corda' # no output, rc=1
$ find /etc/systemd /usr/lib/systemd ~/.config/systemd \
       -iname '*ledger*' -o -iname '*corda*'                     # no output
```

**Finding A — linger is not enabled.** The runbook says it is. `ao-ledger` does
not appear in `loginctl list-users` at all, and there is no runtime directory for
it:

```text
$ ls -d /run/user/994
ls: cannot access '/run/user/994': No such file or directory
```

**Finding B — no unit file exists anywhere.** The runbook's parenthetical
"(**not started**)" implies an installed-but-stopped unit. That is the same
`is-active` misreading §11.8 warns about, committed to a document: a reader is
told to run `systemctl --user enable --now`, which cannot work because there is
nothing to enable. Only two `ao-ledger` files exist in `quadlet/`, and both are
`.network` files — no `.service` and no `.container`:

```text
$ find quadlet -iname '*ledger*'
quadlet/networks/ao-ledger-core.network
quadlet/networks/ao-ledger-ingest.network
```

### Why this matters more than a naming typo

§11.7 records the wrong-account finding as "an agent could build the node under
the wrong identity". Measured, it is worse: **the runbook's step 5 cannot
succeed even after the name is corrected.**

```bash
# Runbook lines 33-35, as written:
sudo -u alwayson-ledger env HOME=/home/alwayson-ledger \
  XDG_RUNTIME_DIR=/run/user/$(id -u alwayson-ledger) \
  systemctl --user enable --now ao-ledger-core.service
```

`id -u alwayson-ledger` exits 1 and prints nothing, so the substitution collapses:

```text
$ id -u alwayson-ledger
id: 'alwayson-ledger': no such user        # stdout empty
$ echo "XDG_RUNTIME_DIR=/run/user/$(id -u alwayson-ledger 2>/dev/null)"
XDG_RUNTIME_DIR=/run/user/                 # trailing slash, no uid
```

Fixing only the name is still not enough, because `XDG_RUNTIME_DIR=/run/user/994`
does not exist either (§Finding A). Without linger there is no `systemd --user`
instance for `ao-ledger` at all, so `systemctl --user` under `sudo -u ao-ledger`
has no bus to talk to.

**So LEDGER-07 has a fourth blocker that is not a key ceremony:** enable
linger for `ao-ledger`, and write the `ao-ledger-core.service` unit file. Neither
is credential work, but enabling linger for a service account **creates a
persistent background session that survives logout**, which is an access-control
change to a service identity and **must not be performed without explicit operator
approval** (README §4.1 rule 6). `docs/runbooks/` is not owned by this
specification and is reported here, not edited.

The `quadlet/networks/ao-ledger-{core,ingest}.network` files *are* real and
`Internal=true`, matching `config/platform/network-cidrs.yaml:8-9`. §11.7 is
correct on that point, and the networks are definitions with no container
attached — consistent with "the node was never built".

### A document asserting completed state must be verified field by field

Beginning a runbook audit by checking the account **name** — the one thing prior
passes had already established — yields nothing new. Re-reading the runbook line by
line instead of grepping it for the known-wrong token surfaces assertions nobody
had checked, including one that is self-refuting: the runbook tells the reader to
enable a unit it also describes as "not started", while `list-unit-files` shows no
such unit. **Grepping a document for the token already known to be wrong tells you
nothing new; only a field-by-field read finds the untested assertions.**
---

## 11.11 Fourth-Pass Verification, 2026-10-04 (LEDGER session)

Re-running recorded checks against inherited claims reproduces the same blockers
and finds nothing new. The method that yields new findings is to **execute the
ledger scripts against a throwaway key in `/tmp`** and observe what the tooling
does rather than what it says it does. That surfaces **four defects**, none of
which is credential work.

The inherited claims all still reproduce — see
`agents/COORDINATION (README UPDATES)/proposals/ledger-LEDGER-0*.md`. What was missing is that
**"the ingest path has no signature verification" (§11.8/§11.9) undersells the
problem.** The signature that exists is not verifiable by its intended recipient,
the staging queue can silently destroy records, and the manifest carries none of
the correlation identity §11.2.1 declares mandatory.

### Finding A — the signature does not cover the signed file (NEW, most serious)

`sign-manifest.sh:33` hashes the manifest, and `:36` signs the **digest**, then
`:41-42` **rewrites the same file** to embed `producer_key_id` and `signature`.
So the artifact that is signed and the artifact that is delivered are different
bytes:

```text
$ B=$(sha256sum m.json | awk '{print $1}')   # before signing
0c7ac6ba098c736c601112a352eb9a5e2b3dddb9c4d034316b7bc7364e7c9600
$ bash scripts/ledger/sign-manifest.sh m.json /tmp/.../k.pem   # ephemeral throwaway key
OK: detached signature at m.sig and embedded in manifest (digest 0c7ac6ba...)
$ A=$(sha256sum m.json | awk '{print $1}')   # after signing
d240030093a1acfd82e3b2908a4911b0beb271dbc9b8815c06326e2d1a76b76b
DIFFERENT -- signature does not cover the delivered file
```

The signature is valid, but only over the *pre-signature* digest:

```text
$ openssl pkeyutl -verify -pubin -inkey <(openssl pkey -in k.pem -pubout) \
    -rawin -in d.txt -sigfile sig.bin
Signature Verified Successfully
EXIT=0
```

**And the recipient cannot reproduce that digest.** Stripping the two injected
fields does not round-trip, because `jq` re-serialises and the original came
from `jq -n` with different key order/indentation:

```text
$ jq 'del(.producer_key_id,.signature)' m.json > re.json
$ sha256sum re.json
6efd1830b0957a7a9eb1ffcbb787cfc91900a84faf65f231694b578a2165e2b9
DOES NOT ROUND-TRIP -- recipient cannot reproduce the signed digest
```

The digest is printed to stdout and stored **nowhere in the manifest**. So a
gateway given only `manifest.json` has no way to verify it. Concretely, a field
tampered after signing is undetectable from the file alone:

```text
$ jq '.local_storage_reference="refA_TAMPERED"' m.json > t.json
signature UNCHANGED after content tamper
```

**Recommendation, for the operator.** Canonicalise: hash a fixed byte sequence
of the *fields to be signed*, sign that, and store the signed digest **inside**
the manifest as e.g. `signed_payload_sha256`. Verification then re-canonicalises
and compares. This is `scripts/`, which is **not owned by this specification: report only, no
fix is applied here.**

### Finding B — the staging queue is keyed on filename and silently loses records

§11.2 requires **idempotency and replay defence**. `submit-ledger-event.sh:10-11`
stages by `$(date -u +%Y%m%d)/<basename of input>`, so the de-duplication key is
whatever the caller happened to name the file. Two *different* signed manifests
with the same filename collide:

```text
# 1st: telemetry_batch / field  -> staged
after 1st: telemetry_batch/field
# 2nd: map_product / mapping, same filename, submitted
after 2nd, DIFFERENT manifest, SAME filename: map_product/mapping
>>> first manifest is GONE. Silent data loss in the staging queue.
```

Also: `install` is used with no mode, so staged manifests land **`0755`** —
world-readable — rather than the `0600` a ledger artifact should carry:

```text
$ stat -c '%a %U %n' .../20260824/manifest.json
755 scottw /ALWAYSON/artifacts/pending-ledger-submissions/20260824/manifest.json
```

This also refines §11.9 Finding 4: the pre-existing `20260824` manifest is
world-readable, which matters more once a replay tool exists. Recommend keying
on `object_id` and `install -m 0600`.

### Finding C — no idempotency key exists even in principle

Two submissions of the *same* `object_id` both succeed and both stage (the file
is overwritten in place, so the count stays at 1 — but nothing rejects the
duplicate, and nothing records that it was seen). There is no replay ledger, no
`correlation_id` uniqueness constraint, and no audit record of a submission
attempt. §11.2 row 5–6 ("Idempotency", "Audit logging") is **entirely
unimplemented**; the staged file is the only trace.

### Finding D — the manifest carries none of the mandatory correlation tuple

§11.2.1 names `serial_number + receipt_number + event_timestamp_utc` as *the*
primary correlation tuple, and §11.3 lists `correlation_id`, `serial_number`,
`receipt_number` in required Corda state. But `build-manifest.sh` emits:

```text
$ jq -r 'keys_unsorted|join(" ")' m.json
object_id object_type origin_domain created_at_utc schema_version
content_hash_sha256 content_size_bytes local_storage_reference ipfs_cid
pcloud_archive_reference transaction_id authorization_policy_id
producer_key_id signature

correlation_id           false
serial_number            false
receipt_number           false
event_timestamp_utc      false
event_type               false
```

None of the §11.2.1 fields are present, and `transaction_id` is `null` unless
the object type is `sales_receipt`. **§11.5's manifest format is missing them
too** — so this is a specification gap, not just a script gap. A ledger built on
today's manifest cannot be joined by the correlation tuple that §11.2.1 defines
as the join key for reporting and reconciliation. Recommend adding the five
fields to both §11.5 and `build-manifest.sh`, with the domain-appropriate ones
required (not nullable).

### What this means for LEDGER-03

LEDGER-03 asks that ingest "accept only approved signed data, with
authorization, idempotency, replay defence, and audit". Measured against the
current tooling, **all five are absent**: authorization is a non-empty-string
test (§11.8), signature verification is absent *and* the signature is
unverifiable by the recipient (Finding A), idempotency is absent (Findings B,
C), replay defence is absent, and audit is a directory listing. LEDGER-03
cannot be closed by writing gateway code on top of this manifest format —
**Findings A and D must be fixed in the format first.**

### Housekeeping

**Ephemeral test artefacts must be created under `mktemp -d` and removed
afterwards**, and the staging directory must be left containing only the
pre-existing `20260824` directory. Nothing may be signed with, or read from, any
project or ledger key; no file outside the owning section may be modified;
nothing may be transmitted.

### Verifying a recorded claim is worth doing once

Re-running recorded checks a further time produces completeness, not information —
that is how successive passes all concluded "nothing new". New findings come only
from *running* the scripts with an input no prior pass had tried: a throwaway key,
a filename collision, a `keys_unsorted` dump.

---

## 11.12 Fifth-Pass Verification, 2026-10-05 (LEDGER session)

Prior passes re-measured the host. This audit covers the **documents this section
owns for internal consistency**, which none had done, and validates candidates
against the real schema rather than reading it. All three findings are proved by
execution.

### Method note — validate, don't read

`jsonschema` 4.26.0 is available on this host, so a candidate manifest can be tested
against `config/ledger/manifest-schema.json` for real:

```text
$ python3 -c 'import importlib.metadata as m; print(m.version("jsonschema"))'
4.26.0
```

Reading the schema says it has `additionalProperties: false`; validating says which
payloads are *rejected*. The second is evidence.

### Finding A — §11.3.1's posting model has no carrier in the wire format

§11.3.1 defines a posting leg as carrying `account_code`, `side`, `amount`, `currency`,
and `correlation_id`, and §11.5 defines the manifest as the thing submitted to the
gateway. **The manifest format cannot express a posting at all.** Validated:

```text
--- 11.3.1 posting leg (DR CASH_EU 10000 EUR): REJECTED
     Additional properties are not allowed ('account_code', 'amount',
     'correlation_id', 'currency', 'side' were unexpected)
```

None of those five fields appears anywhere in the schema:

```text
$ for k in account_code side amount currency correlation_id; do
      printf '%-16s %s\n' "$k" "$(grep -c "\"$k\"" config/ledger/manifest-schema.json)"; done
account_code     0
side             0
amount           0
currency         0
correlation_id   0
```

This is **worse than §11.11 Finding D**, which found that the correlation tuple is
missing from the manifest. Finding D meant reporting could not join by the tuple. This
means the accounting model §11.3.1 defines has **no object that could ever carry it** —
so §11.3.1 is currently a specification with no implementation surface. §11.5 needs a
posting-leg array, or a distinct posting object type; neither exists. This is a
specification change to §11.5 and to `config/ledger/`, and §11.5 is mine but
`config/ledger/manifest-schema.json` is **not** — so the schema half is reported, not
done.

### Finding B — corrections are unexpressible, so §11.3.1's immutability rule has no mechanism

§11.3.1 requires that a correction be "a **new reversing transaction** referencing the
original `transaction_id`", and that history is never edited or deleted. There is no way
to represent a reversing transaction:

```text
--- 11.3.1 reversing transaction (object_type=reversal): REJECTED
     'reversal' is not one of ['sales_receipt', 'telemetry_batch', 'map_product',
      'vehicle_simulation', 'fabrication_simulation']

--- 11.3.1 correction referencing original: REJECTED
     Additional properties are not allowed ('transaction_ref' was unexpected)
```

So the rule is stated but has no object type and no reference field to implement it
with. An implementer following the schema literally cannot correct a posting at all —
they would have to edit or delete, which the same paragraph forbids. This is the
sharpest form of the §11.2.5 minimization tension: `additionalProperties: false` is
correct for PII minimization, but it also forbids every legitimate bookkeeping field.

### Finding C — `TAX_PAYABLE_<jurisdiction>` is defined but unreachable

The account table declares `TAX_PAYABLE_<jurisdiction>`, but **no row in the posting
rule may post to it**. In the posting-rule table (§11.3.1) the code appears exactly
once, and it is the account-table row that defines it — not a posting row. Measured
before this section was added, so that no self-reference inflates the count:

```text
$ grep -n 'TAX_PAYABLE' agents/COORDINATION (README UPDATES)/11-ledger-provenance-archive-and-ipfs/section.md
528:| `TAX_PAYABLE_<jurisdiction>` | Liability | Tax accrued and owed, per approved jurisdiction |
```

§11.3.1 also states "Corda … cannot … decide tax". Both can be true — Corda records
accrued tax, it does not compute it — but as written the account is unreachable, so no
tax accrual can ever be posted and no tax liability can appear in the §4.4 report.
**No tax posting rule may be invented here**: tax rates, jurisdictions and accrual
timing are pricing and financial-policy decisions belonging to §7.2 and the PAY
group, and setting them is a money-movement-adjacent decision requiring explicit
operator approval (README §4.1 rule 7). **Reported, not decided.**

### Corrections applied inside this section

Finding A also exposed two defects **inside §11.3.1 itself**, which belong to this
section and are corrected here: the posting table used `CASH_*`, `RECEIVABLE` and
`REVENUE`, none of which are account codes in the table directly above it (`RECEIVABLE` and `REVENUE` do not
exist; the codes are `RECEIVABLE_CUSTOMER`, `REVENUE_SALE`, `REVENUE_DIGITAL_TRANSFER`).
The "Funds transfer verified" row also offered "RECEIVABLE **or** REVENUE", which is
ambiguous where the balance invariant requires one answer. The DR/CR columns of two
rows were also presented credit-first. All five rows now name real codes in DR-then-CR
order, each a balanced pair, and the shorthand defects are recorded here rather than
silently repaired.

### The question a specification audit must ask

The default instinct — to re-run the recorded host checks — reproduces the same
result four times over. The question that yields findings is **not "is the host in
the documented state?" but "does this specification agree with the artefacts it
governs?"** The host was consistent in every pass; the documents were not, and no
amount of `sha256sum -c` would have found that.

Equally, a missing tax rule is not a defect to be reported as one without first
establishing *whose* decision it is. An agent that "helpfully" invents a tax
accrual rule would be making a pricing decision it has no authority to make
(README §4.1 rule 14).
---

## 11.13 Sixth-Pass Verification, 2026-10-05 (LEDGER session)

Five passes audited the host (§11.8–§11.11) and then the documents §11 owns (§11.12). This
pass did something none of them did: it looked at the **artefacts that §11 specifies
rules for**, and asked whether the staging queue still matches what §11.11 recorded.

It does not. **§11.11's housekeeping claim is now false, and the reason is worse than
the defect it documented.**

### Finding A — RETRACTION: §11.11's housekeeping statement is superseded

§11.11 (2026-10-04) recorded, in its Housekeeping section:

> `artifacts/pending-ledger-submissions/` again contains **only** the pre-existing
> `20260824` directory.

That was true when written and is **no longer true**. Measured:

```text
$ ls -la /ALWAYSON/artifacts/pending-ledger-submissions/
drwxrwxr-x 4 scottw scottw 4096 Oct  5 07:52 .
drwxr-x--- 8 scottw scottw 4096 Oct  4 08:55 ..
drwxrwxr-x 2 scottw scottw 4096 Aug 23 18:58 20260824
drwxrwxr-x 2 scottw scottw 4096 Oct  4 17:52 20261005
```

A **second** manifest exists, dated today, and it is **not tracked by Git**:

```text
$ git ls-files artifacts/pending-ledger-submissions/
artifacts/pending-ledger-submissions/20260824/manifest.json      # 20261005 absent
$ git check-ignore -v artifacts/pending-ledger-submissions/20261005/manifest.json ; echo $?
1                                                                    # not ignored either
```

So it is an **untracked, unignored** working-tree artefact. Per the coordination
rules it must **not be deleted, moved, or modified**, and the tracked `20260824`
manifest must not be touched either. It is another session's or the operator's
uncommitted work; removing it would violate README §4.1 rules 1 and 2 and hard
rule 1. **Reported, not removed.**

### Finding B — the new manifest would be REJECTED by the schema it claims to satisfy

This is the serious part. `build-manifest.sh` does not validate `origin_domain`
(§11.9 Finding 3), so the value in the file is whatever the caller passed. The
staged value is **`storefront`** — a domain that appears in **no** §11.1 table and
**no** §11.5 enumeration:

```text
$ jq -r '{object_type,origin_domain,producer_key_id}' \
    artifacts/pending-ledger-submissions/20261005/manifest.json
{ "object_type": "sales_receipt", "origin_domain": "storefront", "producer_key_id": "testkey" }

$ python3 -c "...Draft202012Validator(manifest-schema.json).iter_errors(m)..."
REJECTED: 'storefront' is not one of ['sales', 'field', 'mapping', 'sim_vehicle', 'sim_fabrication']
```

**A `sales_receipt` — the one object type that §11.2.2 gates exist to protect — is
sitting in the replay queue attributed to a domain that is not an authoritative
producer at all.** Combined with `producer_key_id: "testkey"`, this is the second
entry (after `20260824`'s `producer_key_id: "test"`) of the same class §11.9
Finding 4 described. **Two of two queued manifests carry unverified key material,
and now one of them also carries an out-of-model origin domain.**

`submit-ledger-event.sh` cannot catch this, because it performs **no schema
validation at all**:

```text
$ grep -nE 'jsonschema|manifest-schema|validat' scripts/ledger/submit-ledger-event.sh
NO schema validation in submit script
```

§11.2.5 row 3 says schema validation is enforced by the *gateway*. Correct — but
nothing validates on the way **in**, so an invalid manifest is written to durable
storage and only ever rejected later, if a gateway ever exists. The queue is
**write-anything, validate-never**.

### Finding C — the staging queue is inside the restic backup set

The restore drill already treats staged manifests as receipts. That makes them
**backed-up data**, which changes the consequences of Finding B from "a local
loose file" to "a record that survives in the backup set and will be restored":

```text
$ grep -n 'artifacts' scripts/backup/restic-run.sh
restic backup ... '$AO_ROOT/artifacts' ...

$ grep -n 'pending-ledger-submissions' scripts/restore/restore-restic-drill.sh
receipts="$(find "$scratch_abs" -path '*pending-ledger-submissions*' -name 'manifest.json' ...)"
echo "  pending-ledger-submission manifests found: $receipts"
```

The drill **counts** staged manifests and reports them as "Corda
receipt/manifests". It never validates them. So a schema-invalid, unverified-key
manifest is counted as a **receipt** during a restore drill. This is a §17.1
interaction, so it belongs to **OPS** as well as LEDGER — reported, not edited.

### Finding D — §11.5 and §11.1 name a smaller domain set than the ledger needs

Comparing the three artefacts by machine rather than by eye:

```text
$ python3  # schema enum vs §11.1 authority table
schema enum : ['field', 'mapping', 'sales', 'sim_fabrication', 'sim_vehicle']
in §11.1 table but NOT submittable: ['archive', 'ledger', 'payment', 'sim-fabrication', 'sim-vehicle']
```

`payment` is an authoritative domain in §11.1 and the **source of the funds-transfer
evidence** that §11.3.1 makes the *only* posting trigger, yet it has no
`origin_domain` and so **cannot submit a manifest at all**. §11.1 also writes the
domains as `ao-sim-vehicle` / `ao-sim-fabrication` while §11.5 and the schema use
`sim_vehicle` / `sim_fabrication` — the two spellings differ, and the producer-key
gap in §11.9 Finding 1 lists them under the `ao-` form. A gateway built by matching
§11.1 names against the schema enum would match nothing.

Additionally, §11.5's example omits two schema fields: `transaction_id` (which the
schema makes **required** for `sales_receipt`) and `content_hash_sha256` (required
for every object). An implementer copying §11.5 would produce a manifest that its
own schema rejects:

```text
schema-only  (undocumented in §11.5): ['content_hash_sha256', 'transaction_id']
doc-only     (not in schema)         : []
```

### What this means for the open items

None of these change a status. They make the **replay path** more dangerous than
§11.9 recorded, and they add three items that are **not** mine to fix:

1. `config/ledger/manifest-schema.json` — add `payment` (and decide `archive`/
   `ledger`), and reconcile the `sim_*` vs `ao-sim_*` naming. **Not owned by this section.**
2. `scripts/ledger/submit-ledger-event.sh` — validate against the schema *before*
   staging. Cheap, unblocked, **not owned by this section** (`scripts/`).
3. `scripts/restore/restore-restic-drill.sh` — a counted "receipt" that is never
   validated. **OPS** group (§17.1), **not owned by this section**.

LEDGER-03 stays open, and its blocker list grows by one item: **the replay queue
must be treated as untrusted input and the invalid 20261005 entry quarantined by
the operator.** Quarantining it is a deletion-adjacent action and is not performed
by this specification.

### A claim in your own document is still a claim, not a measurement

An audit that reads only the subsections no prior pass had read can come back
clean while the actual defect sits elsewhere. The finding here came from running
`ls` on the staging directory as a **closing sanity check** before writing up: the
listing contained a directory the housekeeping note said was not there.

**A housekeeping note written about one's own test artefacts is the record most
likely to be trusted and least likely to be re-checked.** Two prior passes were
about trusting records that had gone stale; this one is about trusting a record
written earlier in the same section. The lesson generalises past staleness: **write
down what was cleaned up, then *still* check.**

Finding B must not be written as "an invalid manifest is staged, someone should
fix the validator." That misses the point: the validator is not the defect, the
**missing `payment` origin_domain plus the unvalidated call-through** is. Adding a
check without closing the model gap would reject more manifests without accepting
the one that matters.

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

Verify — **this block asserts and exits non-zero on failure**:

```bash
./scripts/validation/verify-host-baseline.sh
```

That script is the asserting replacement for the block this section used to
carry. The old block was replaced because it **could not fail**: the cgroup
test `test "$(stat -fc %T /sys/fs/cgroup)" = "cgroup2fs" && echo ...` is
silent when the test fails, nothing read its return code, and the block's
overall exit status was 0 either way. Reproduced 2026-10-03 — breaking the
cgroup check changed nothing and the block still exited 0. A check that
cannot fail verifies nothing, so no §19.2 evidence could rest on it.

The replacement was tested in both directions, because a verifier that only
ever passes is the same defect wearing a new hat:

```
$ ./scripts/validation/verify-host-baseline.sh
  PASS  podman responds (5.7.0)
  PASS  systemd --user manager reachable
  PASS  linger enabled (survives logout)
  PASS  cgroup v2 unified hierarchy
  PASS  aa-status present
  WARN  aa-enforce MISSING - apparmor-utils not installed ...
  --- 5 passed, 0 failed ---
RESULT: PASS                                    # exit 0

# with stat and loginctl stubbed to report a broken host:
  FAIL  linger is 'Linger=no', expected 'yes' - containers stop at logout (OPS-13)
  FAIL  cgroup fs type is 'tmpfs', expected 'cgroup2fs'
  --- 3 passed, 2 failed ---
RESULT: FAIL (2 check(s) failed)                # exit 1
```

It asserts the **value** of `Linger` rather than the presence of the key, and
reports `aa-enforce` as a WARN with the reason, instead of passing on
`aa-status` — which ships in the base `apparmor` package and succeeds even
though no profile can actually be enforced on this host (see §2.3).
### 12.3.1 Linger is a precondition, not a nicety (OPS-13)

**Overlap with the baseline verifier above, stated so the next reader does not
double-count it.** `verify-host-baseline.sh` already asserts `Linger == yes` as
one of its five checks, and that is the check to trust for the yes/no question.
`check-user-linger.sh` is **not** a second opinion on that question - it is a
*diagnostic* for it, reporting the linger state alongside the user-manager
runtime, the deployed unit count and the running `ao-*` service count, so that
when the baseline check fails you can see why. Both agree on the value.

It earns a separate existence because the baseline check is a single boolean over
one account, and this is the one that exits **2** for an account that does not
exist - the failure mode a `[ "$linger" = "yes" ]` test handles worst. See the
bug below.

The `loginctl show-user -p Linger` line that section 12.3 used to carry was
read-only and silent on failure, and linger is a real precondition rather than a
nicety: every workload here is a *rootless user* Quadlet unit under
`~/.config/containers/systemd/`, driven by `systemd --user`, and that instance
only exists for the operator account while a session is open. Log out of KDE and
every container, timer and Quadlet-generated unit for this account stops, and none
of them come back on their own after a reboot. `ao-lmstudio.service` already
depends on this - its own header says "Starts at boot via user lingering".

So the rebuild must **report** linger before it starts any unit, and the
provisioner now does, at stage 20, before stage 50:

```bash
./scripts/validation/check-user-linger.sh          # report
./scripts/validation/check-user-linger.sh --check  # gate: 0 ok, 1 fault, 2 no such account
```

Measured on this host 2026-10-04:

```console
$ bash scripts/validation/check-user-linger.sh
user            : scottw
Linger          : yes
State           : active
OK:   linger enabled
marker file     : present (/var/lib/systemd/linger/scottw)
OK:   user manager runtime /run/user/1000 present
      running user services: 90
deployed units  : 21 .container files in /home/scottw/.config/containers/systemd
generated ao-*  : 48 service units under systemd --user
running ao-*    : 26
```

**The provisioner deliberately does not enable linger.** `loginctl enable-linger`
needs root and writes `/var/lib/systemd/linger/` — a host-level change, which
README §4.1 rules 1 and 3 place with the operator. The stage reports the state
and prints the exact command; it does not run it.

### A false FAIL is the worst kind of checker defect

The checker's first revision reported `FAIL: linger is not enabled` — and exited 1 —
for an account that **does not exist at all**. Measured: `loginctl show-user alwayson-ledger -p Linger` returns
`Failed to look up user ... No such process`, but with `--value` it returns the
literal string `unknown`, which the script compared against `yes`. And
`/var/lib/systemd/linger/` is not proof of existence: `alwayson-ledger`,
`alwayson-mapping` and `alwayson-sales` all have marker files on this host while
`getent passwd` finds none of them, so a leftover marker is misleading. A false
FAIL on a checker is the worst kind of defect, because it teaches the operator to
ignore it — which would hide a genuine `Linger=no`. The check now tests
`getent passwd` first and exits **2** for "no such account", distinct from **1**
for a real fault.

Two earlier counting bugs in the same script are also fixed and worth naming,
because both produced confident, wrong output: it grepped unit files for
`\.container`, a name systemd never creates (Quadlet *generates*
`ao-<name>.service`), so it claimed "21 deployed but none enabled" on a host with
26 containers running; and it called `id -u` with no argument, so checking any
account other than the caller reported `/run/user/-1`.

## 12.4 Rebuilding This Host From Nothing

**Kubuntu 26.04 LTS is the starting point** — <https://kubuntu.org/download/>. Install it
first, then KDE Plasma, Cline CLI and an internet connection are what the provisioner expects.
`scripts/provision/provision.sh` reconstructs everything else the repository already
describes, in stages. It is **dry-run by default**; pass `--yes` to apply.

```bash
./scripts/provision/provision.sh          # dry run: prints every action
./scripts/provision/provision.sh --yes    # apply
```

| Stage | Restores | Notes |
|---|---|---|
| 10 | 7 third-party apt repositories | ROS 2 is registered but **unreachable** (TLS); not worked around |
| 20 | Host dependencies, layout, podman networks, inventory | **Delegates to `scripts/bootstrap/00`, `02`, `03`, `04`** rather than repeating them. Also **reports linger** before any unit starts (§12.3.1) |
| 30 | 16 snaps, 1 flatpak | Enumerated from the installed set |
| 40 | Host applications | Read from `unmanaged-software.yaml`, not hardcoded. Vendor blobs delegated to `install-vendor-binaries.sh` (§12.4.1) |
| 50 | 9 Quadlet domains, **36 Quadlet source units** | **Quadlet deploys flat** — `~/.config/containers/systemd/` holds copies, so the deploy script is mandatory, not optional |
| 60 | Secret presence check | Derived from the units' own `EnvironmentFile=` lines |
| 70 | Data check only | **Never restores.** Restoration is a human decision (rule 2/3) |
| 90 | Verification | Regenerates the inventory for diffing against `docs/software-status.md` |

Two things a rebuild cannot restore from the repository, and must come from
backup: the **10 secret files** in `~/.local/share/ao-secrets/` (outside git by
design) and the **persistent data** in `data/` (ardupilot 2.1G, corda-install
282M). The **AppImages and vendor binaries** were long described here as a third
category "that must be fetched by hand"; §12.4.1 replaces that with a manifest
and an installer that verifies what is already on disk.

### 12.4.2 Every stage has an undo, and the undo is non-destructive (OPS-12)

`scripts/provision/rollback.sh` is the missing half of §12.4. Until now each stage of
`provision.sh` described only what it *built*, and a rebuild that failed halfway left the
operator with no documented way back. The script is **dry-run by default**, mirroring
`provision.sh`, because undo is as dangerous as the action.

```bash
./scripts/provision/rollback.sh --list   # what each stage undoes, and whether it needs an operator
./scripts/provision/rollback.sh         # dry run: prints every action
./scripts/provision/rollback.sh --yes   # apply
```

It runs stages in **descending order (90 → 10)** so dependents go before their
dependencies: units are withdrawn before the repositories that supplied them.

**The rule that shapes it: stages differ in whether their undo is safe to automate.**

| Stage | Undo | Safe to run unattended? |
|---|---|---|
| 90 | nothing — regenerated artefacts | yes, informational |
| 70 | **nothing** — stage 70 never restores | yes, reports `data/` sizes only |
| 60 | **nothing** — stage 60 only checked presence | yes, never touches secrets |
| 55 | restic units: stop, disable, remove the 6 unit files | yes, with a warning that this stops backups |
| 50 | Quadlet files per domain, via `deploy/rollback-domain.sh` | yes |
| 40 | vendor blobs | **no** — prints manifest ids, removes nothing |
| 30 | snaps and flatpak | **no** — prints `snap remove` commands, runs none |
| 20 | apt repo files and keyrings | printed, not executed |
| 10 | nothing — stage 10 only *adds* | n/a |

Three things are deliberately **never** undone, because no script here can undo them
safely: `data/` (rule 2/3), **secrets** (the values live in the wallet and in
`~/.local/share/ao-secrets/`, and are not reproducible from this repository), and
Podman networks (removing one strands whatever containers are attached). A rollback that
"restores the host to bare Ubuntu" would be a data-loss event wearing a rollback's
clothes.

**Verified, dry run.** State is identical before and after, and the summary line is last:

```text
$ bash -n scripts/provision/rollback.sh && echo 'SYNTAX OK'
SYNTAX OK
$ bash scripts/provision/rollback.sh >/tmp/rb5.out 2>&1; echo "rc=$?"
rc=0
$ grep -n '^--- stage' /tmp/rb5.out
5:--- stage 90: verification artefacts (nothing to undo)
8:--- stage 70: persistent data (NEEDS OPERATOR - not undone)
17:--- stage 60: secrets (NEEDS OPERATOR - not undone)
22:--- stage 55: restic backup units
37:--- stage 50: Quadlet unit files (per domain)
51:--- stage 40: vendor blobs (NEEDS OPERATOR - not undone)
56:--- stage 30: snaps and flatpak (NEEDS OPERATOR - commands printed only)
67:--- stage 20: apt repositories added by stage 10
81:--- stage 10: nothing to undo
$ tail -1 /tmp/rb5.out
dry run only. Nothing was changed. Re-run with --yes to apply.
```

```text
# BEFORE: units=85 restic=6 nets=14 timer=enabled
$ bash scripts/provision/rollback.sh >/dev/null 2>&1
# AFTER : units=85 restic=6 nets=14 timer=enabled
```

The only `rm` the script can reach is `sudo rm -f /etc/systemd/system/<unit>`, named from
`systemd/backup/`. Stage 50 delegates to `rollback-domain.sh`, which removes **only** the
unit files named in `quadlet/<domain>/` and never `rm -r`s the flat unit directory — that
directory holds every other domain, plus the networks and volumes they share.

It closes with the provision ledger's own record of which stages actually ran, read from
`logs/operations/provision-ledger.jsonl` rather than assumed:

```text
$ python3 -c "..." # counting stage keys in the ledger
  stage 10: 62 step(s) recorded
  stage 20: 15 step(s) recorded
  stage 50: 78 step(s) recorded
  stage 55: 7 step(s) recorded
  stage 90: 16 step(s) recorded
```

**Still open on this item.** A clean-room rebuild has still never been executed, so the
procedure remains unproven end to end; and `bootstrap/01` photogrammetry verification is
still not gated on §17.3 evidence as §16.1 requires. The rollback half is written and
proven; those two are not mine to close here.

#### A number in the stage table above was wrong

The stage-50 row read "9 Quadlet domains, 22 units". **22 is only the `.container` count.**
Measured across all nine domains the Quadlet *source* units are **36**:

```text
$ find quadlet -type f \( -name '*.container' -o -name '*.network' -o -name '*.volume' -o -name '*.build' \) | wc -l
36
$ find quadlet -type f | grep -oE '\.[a-z]+$' | sort | uniq -c
     22 .container
     15 .network
      1 .path
     16 .service
      1 .sh
      5 .timer
```

An undercount here is not cosmetic: stage 50 deploys **every** source unit, so a reader
trusting "22" would conclude seven network units and six `ao-*` service/timer units were
never deployed.

That comparison is also where the counting trap lies. Comparing *all* 81 deployed files
against the repo's 61 distinct basenames yields **32 apparent orphans** — but they are not
stale copies. Every one of the 32 is a `.service`, and each self-declares as generated:

```text
$ head -3 ~/.config/containers/systemd/ao-sales-db.service
# Automatically generated by /usr/libexec/podman/quadlet
#
# /ALWAYSON/quadlet/sales/ao-sales-db.container
```

Note the generator is Podman's quadlet helper at `/usr/libexec/podman/quadlet`, **not**
`systemd-container-generator` (that path does not exist on this host). Restricted to
source-typed files the two sets agree almost exactly:

```text
$ find ~/.config/containers/systemd -maxdepth 1 -type f \
    \( -name '*.container' -o -name '*.network' -o -name '*.volume' -o -name '*.build' \) \
    -printf '%f\n' | wc -l
30
# deployed source-typed NOT in repo:  (none)
# repo source-typed NOT deployed:
ao-ardupilot-sitl.container
ao-data.network
ao-field.network
ao-ledger-core.network
ao-ledger-ingest.network
ao-sim-vehicle.network
```

Those six are a real, separate finding and are **reported, not fixed**. Five are
`quadlet/networks/*.network` and one is `quadlet/sim-vehicle/`, none is deployed, yet all
five networks exist live under those exact names:

```text
$ podman network ls --format '{{.Name}}' | grep -E '^ao-(data|field|ledger-core|ledger-ingest|sim-vehicle)$'
ao-data
ao-field
ao-ledger-core
ao-ledger-ingest
ao-sim-vehicle
```

They were therefore created by `bootstrap/04-create-operational-layout`'s sibling
`04-create-podman-networks.sh`, which calls `podman network create` directly. **The same
network is described by two owners** — a repo Quadlet file and an imperative bootstrap
script. For `ao-data` the two currently agree, so nothing is broken today:

```text
$ grep -E 'NetworkName|Internal' quadlet/networks/ao-data.network
NetworkName=ao-data
Internal=true
$ podman network inspect ao-data --format '{{.Name}} internal={{.Internal}} subnet={{(index .Subnets 0).Subnet}}'
ao-data internal=true subnet=10.89.8.0/24
```

But a future edit to one file would not change the running network. Deciding the single
owner of network creation is a design decision, it touches live network configuration, and
it is **not mine to settle** — it needs an operator decision and, if adopted, a redeploy of
the flat unit copies (§16.1.1). `ao-ardupilot-sitl.container` being undeployed is
unremarkable: SITL is a simulation container, not an always-on service.

### 12.4.1 Vendor blobs are declared, pinned and verified (OPS-17)

`config/build-update/vendor-binaries.yaml` is the manifest; each entry carries an
`id`, `version`, `install` kind, target `path`, a download `sha256`, an optional
`sha256_published_by_vendor`, and — for archives — the `member` to extract and a
separate `installed_sha256` for the extracted binary.

**Two digests, deliberately not conflated.** `sha256` is what the *download*
must hash to. `installed_sha256` is what the *installed file* must hash to. For
an AppImage these are the same value (the file *is* the download); for an
archive they are not, because the download is a `.tar.gz`/`.zip` and the
installed file is the binary inside it. The first revision used one field for
both and reported a false DRIFT for every archive on a host where the binary was
perfectly correct.

```bash
./scripts/provision/install-vendor-binaries.sh          # dry run (default)
./scripts/provision/install-vendor-binaries.sh --yes    # fetch and install
```

Exit codes: **0** clean, **1** a download or install failed, **2** at least one
entry was refused (DRIFT or an unpinned download). `manual` is deliberately *not*
a failure — it means no vendor publishes an artifact, which is an operator phase,
and counting it would make every run red.

Measured on this host 2026-10-04, dry run against the real manifest:

```console
$ AO_ROOT=/tmp/ao-sessions/wt-ops-b bash scripts/provision/install-vendor-binaries.sh
vendor binaries declared: 8
OK      qgroundcontrol v5.1.0 - present, digest matches
OK      reticulum-meshchatx v4.9.1 - present, digest matches
OK      lm-studio v0.4.20-1 - present, digest matches (no url: not auto-installable)
OK      pcloud v- - present, digest matches (no url: not auto-installable)
OK      nperf v- - present, digest matches (no url: not auto-installable)
OK      gh v2.97.0 - present, digest matches
OK      bun v1.4.2 - present, digest matches
OK      cline v3.0.60 - present, no installed digest recorded to check against
  path: /home/scottw/.local/bin/cline

installed=0  already-present=8  manual=0  refused=0  failed=0
```

**All eight are present on this host and verified.** Five have no vendor URL and
so cannot be fetched unattended even in principle — a property of the vendors,
not a gap in the provisioner, and the honest residue of OPS-17. Three (gh, bun,
cline) are installable; the first two verify against a recorded `installed_sha256`.

### Check presence before reachability

The first revision tested "does this entry have a url?" **before** "is the file already
installed?", and `continue`d out of the loop. The consequence, measured: `lm-studio`, `pcloud` and `nperf` were all reported
`MANUAL ... a human must place this file` while **all three exist on disk and all
three hash to the manifest's own recorded `sha256`**. The report told the operator
to go fetch files that were already installed and verified — "cannot be fetched
automatically" and "is not installed" are different facts, and only the second is
a problem. Presence is now checked first; an entry with no url but a present,
matching file reports OK with the caveat in parentheses.

Two further defects, both found by testing rather than reading:

- **An all-numeric digest was silently erased.** YAML coerces unquoted
  `0000…0` to the integer `0`, and the `or ""` fallbacks then rendered that as
  the empty string, so the entry degraded to "no installed digest recorded" and
  reported **OK** — the one outcome a digest check must never produce. Every
  scalar is now `str()`-ed, so the entry reports DRIFT instead. Real digests in
  the manifest are quoted and contain `a`–`f`, so they round-trip exactly.
- **Every failure exited 0.** A DRIFT and a failed download were both reported
  as text and then succeeded, which is a provisioner whose failure signal is a
  line nobody is reading. Because `provision.sh` calls this through its `run`
  helper, which propagates the return code unguarded, that would have aborted
  stage 40 of the whole rebuild — so the `run` call is now `|| true` as well. A
  drifted AppImage must not leave the host without its Quadlet units; the
  installer refuses to overwrite (README §4.1 rules 2/3), so "carry on and tell
  the operator" is the correct outcome, not "stop the world".

The OK, DRIFT, MANUAL and dry-run paths were each exercised against a throwaway
fixture manifest rather than asserted. The fixture was first written with `kind:`
before the schema key `install:` was checked, which is why its first run reported
two entries as "no installed digest" — the fixture was wrong, not the script, and
re-running with the correct key produced the DRIFT it was built to provoke.

## 12.5 Inventory and Update Management

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

### 12.5.1 The Installed column is ground truth from apt history

The `Installed` column of `docs/software-status.md` is produced by
`apt_date()` in `scripts/build-update/provenance-log.py`, which reads
`/var/log/apt/history.log` and its rotated siblings via
`scripts/build-update/apt_history.py`.

**It used to be wrong, and wrong in a way that mattered.** dpkg keeps no install
timestamp, so the date was inferred from the mtime of
`/var/lib/dpkg/info/<pkg>.list` — a file dpkg rewrites on *every* unpack. The
column therefore displayed the last **upgrade** date under an install heading. An
operator auditing a deployment would read "installed 2026-10-01" for a package
that had in fact been installed in April and merely upgraded that day.

apt's history log does hold the truth, and it separates the two cases: every
transaction records `Start-Date`, the exact `Commandline`, and distinct
`Install:` / `Upgrade:` / `Remove:` / `Purge:` lines. Four facts now reach the
document that did not before:

| Fact | How it is derived |
|---|---|
| install vs upgrade | the item-line keyword, not a file mtime |
| unattended vs operator-initiated | `Commandline` contains `unattended-upgrade` or a packagekit upgrade role |
| removed / purged | a later `Remove:`/`Purge:` wins over the earlier `Install:`; the cell reads `not installed (removed/purged <date>)` |
| who asked | the `Requested-By:` user, where apt recorded one |

Measured against the real log (2026-10-04):

```
$ python3 scripts/build-update/apt_history.py
packages indexed      : 4445
  installed           : 4281
  upgrade-only (pre-window): 86
  installed unattended: 2098
log files read        : ['history.log.1.gz', 'history.log.2.gz', 'history.log']

$ python3 -c "...install_date('dbeaver-ce')..."
dbeaver-ce   None  Purge   unattended=False  removed=True
nginx        None  Purge   unattended=False  upgraded=2026-08-22  removed=True
rclone       2026-10-03  Install  unattended=False
```

Two honest limits, stated rather than papered over:

* **Coverage is bounded by apt's own log retention.** A package installed before
  the oldest surviving stanza is simply absent from the index. Absent means
  *unknown*, never *not installed* — the 86 upgrade-only records above are
  packages whose install predates the retained window.
* **A removal is not an install date.** For a purged package the function
  returns `(None, record)` so the caller can say *why* the cell is empty rather
  than printing a date for software `dpkg -l` no longer lists.

The dpkg-mtime path remains as a fallback and is labelled as such in the cell
(`(dpkg manifest mtime)`) so the two sources are never confused. A genuine
failure to load `apt_history.py` degrades to that fallback and is remembered so
the cost is paid once.

### 12.5.2 Regression tests for the generators

`scripts/build-update/test_generators.py` — run it with
`python3 scripts/build-update/test_generators.py`; no framework is required,
though `pytest` collects it too. **62 tests, all passing**, in about 0.7 s:

```
$ python3 scripts/build-update/test_generators.py
...
Ran 62 tests in 0.73s

OK
```

Three defects had shipped because nothing asserted them, and each now has a
test:

1. **Truncated digests became pull commands.** `update_steps()` checked only the
   `sha256:` prefix, so `sha256:` plus 12 hex characters produced
   `podman pull repo@sha256:<12>`, which a registry rejects with HTTP 400 — a
   command that looked correct and could never work. `is_complete_digest()` now
   checks the algorithm *and* the full body length, and suppresses command
   generation entirely.
2. **Steps built from a display name.** A row for the application "Account
   Wizard" produced `apt install --only-upgrade Account`, which does not exist.
   Steps now use the owning package name.
3. **A prose error string used as a digest.** `"upstream digest unreachable
   (registry refused)"` reached the command generator. Any value that is not a
   complete digest now yields no command.

A fourth defect was found and fixed *by* this suite: `update_steps()` accepted a
12-character digest while a nearby assertion already expected it to be rejected.

Two further tests exist specifically because the fixes were silent when
reverted. `test_apt_history_loads_regardless_of_working_directory` runs the
generator as a subprocess with `cwd=/tmp`: the original `import apt_history`
resolved against `sys.path`, which holds the **current working directory**, not
the script's own directory — and `refresh-install-log.sh` does `cd "$AO_ROOT"`
first. The import therefore raised `ImportError` on every production run and
silently fell back to the dpkg mtime, producing a document that looked normal
and carried the older, less accurate dates. The module is now loaded by
`__file__`. Without the test this regression is invisible: the failure mode is
a plausible-looking document, not an error.

### 12.5.3 `eligible` now means a machine can do it (OPS-19)

`update-plan.json` used to carry a single `steps` list per item, mixing two
things that cannot be combined: commands an executor could run
(`podman pull repo@sha256:<64>`) and prose no executor could ever run
(`edit Image= in quadlet/<domain>/<unit>.container`). An item was marked
**eligible** on the strength of the first while carrying the second, so
"eligible" did not mean "automatable" and **nothing in the file distinguished
them**.

`update_steps()` now returns `{"steps": [...], "manual": [...]}`, and the
`eligible` decision is taken on the strength of `steps` alone:

| Field | Meaning | Contract |
|---|---|---|
| `steps` | argv **arrays**, verb-allowlisted | a machine can run these; nothing needs a shell |
| `manual` | prose for a human | never executed, never silently dropped |

Every step is an argv array (`["podman", "pull", "repo@sha256:<64>"]`), never a
string. This is deliberate: a plan-supplied string can only be run through a
shell, and a plan is generated data, not trusted input. `_argv_is_safe()`
downgrades any argument carrying a shell metacharacter to prose rather than
emitting it — an item literally named `pkg; rm -rf /` produces **no**
executable step and keeps its intent under `manual`.

The consequence is visible and worth stating plainly: on this host the plan now
reports **0 eligible of 224**. That is not a regression, it is the truth. The
old count of 6 was counting items whose only "step" was a sentence about
editing a Quadlet file.

**A correction to what this section claimed when first written.** It said
"`brave` remains genuinely automatable and is emitted as argv". That was
checked rather than assumed, and it is false as stated. `update_steps()`
*does* emit argv for `brave` —

```
$ python3 -c "...update_steps({'item':'brave','via':'snap/latest/stable'}, None)"
{'steps': [['snap', 'refresh', 'brave']], 'manual': []}
```

— but the emitted plan shows `"steps": []` for `brave`, because the writer
gates on the decision:

```
"steps": steps if decision == "eligible" else [],
```

`brave`'s verdict is `?`, not `**NO**`: the snap channel was unreachable, so
there is **no evidence of being behind**. It is excluded as *"no evidence of
being behind"*, and the exclusion blanks its steps. The distinction matters,
because the two statements answer different questions. `brave` is the only item
whose *source* admits a mechanical step; it is not eligible *today* because the
evidence for updating it does not exist, not because it is unautomatable.
Written the other way round — "only brave is automatable" — the next reader
would look for the argv in the plan, not find it, and conclude the generator
had regressed.

So the honest summary of this host is **0 eligible of 224, and 0 of those 224
carry a `steps` array**, because every one of them is excluded, and the writer
deliberately refuses to publish steps for an excluded item. Measured:

```
$ python3 -c "... json.load(update-plan.json) ..."
schema 2 items 224
summary {'behind': 1, 'eligible': 0, 'excluded': 224}
with steps 0
with manual 0
```

### 12.5.4 `apply-plan.py` — the dry-run validator (OPS-20)

`scripts/build-update/apply-plan.py` answers one question: *if an operator
approved this plan, what would it touch?* It loads the plan, hashes it,
snapshots it into the run directory, validates every step against a verb
allowlist, derives blast-radius groups (units sharing a digest or a deploy
domain) and reports the result. **It executes nothing**, and the module docstring
states it must never be extended to.

```
$ AO_ROOT=$PWD python3 scripts/build-update/apply-plan.py --no-snapshot
plan        : /tmp/ao-sessions/wt-ops-b/data/build-update/update-plan.json
sha256      : b753e5dab017df1be539b4b86e26713cc1293d9cde1c034ebb376f78aac9453f
generated   : 2026-10-04T16:55:20+00:00   schema: 2
items       : 224  -> 0 eligible, 224 excluded
would run   : 0 argv steps across 0 item(s)
manual only : 0 item(s) need a human
would touch: NOTHING - no item is eligible
EXECUTED    : nothing. This tool is a validator only.
validation  : OK
```

**Why approval must pin to the plan hash, not the filename.** The plan
regenerates on every refresh, so the file an operator approved is not the file a
tool would run — the `generated` timestamp alone changes the bytes when no item
changed. `--expect-hash` refuses anything else, so an approval can name exactly
the bytes that were reviewed:

```
$ AO_ROOT=$PWD python3 scripts/build-update/apply-plan.py --no-snapshot \
      --expect-hash 0000...0000
MISMATCH_EXIT=4
HASH MISMATCH
  approved : 0000...0000
  on disk  : b753e5dab017df1be539b4b86e26713cc1293d9cde1c034ebb376f78aac9453f
```

Exit codes: `0` well-formed, `2` usage, `3` validation failure, `4` hash
mismatch.

The verb allowlist is **duplicated rather than imported**, so the validator
still runs when `provenance-log.py` is broken — the file most likely to be
broken is the one that produced the plan. That duplication is a drift risk, so
`TestVerbAllowlistAgreesAcrossFiles` asserts the two lists are identical.

Run against the **live** `/ALWAYSON` plan the same tool exits **3** with 33
problems, and the diagnosis is in the output:

```
$ python3 scripts/build-update/apply-plan.py --no-snapshot     # AO_ROOT=/ALWAYSON
  - items[128] ao-build-update: no `manual` key; an eligible item must separate prose from executable steps
  - plan: 193 of 199 items carry no `manual` key. This is a schema-1 plan
    (prose and executable steps are not separated). Every eligible step in it is
    a bare string, so nothing in it is safe to hand to an executor -- this is
    OPS-19, not a per-item defect.
```

That is the validator earning its keep: the live plan is still schema 1 and has
not been regenerated since §12.5.3 landed, so **it is not yet safe to hand to
an executor**. Regenerating it is one `./scripts/build-update/refresh-install-log.sh`.

**A trap worth recording for the next agent.** The validator defaults `AO_ROOT`
to `/ALWAYSON`, so running it from a worktree validates **the live main-repo
plan, not your worktree's** — silently, with a plausible-looking result. This trap is easy to hit
this: a first run reported 199 items and schema 1 while the worktree plan held
224 items and schema 2. Always pass `AO_ROOT=$PWD`, and sanity-check the
`plan :` line in the output against the file you meant. The same class of bug
existed literally in `refresh-install-log.sh`, whose summary-report heredoc
opened a hardcoded `/ALWAYSON/data/build-update/update-plan.json` while the
surrounding script honoured `AO_ROOT`; it now takes the path as `sys.argv[1]`.

### 12.5.5 Image digests are checked against what is deployed (OPS-02)

`config/platform/version-matrix.yaml` records image digests as free text in
YAML strings. Nothing compared those strings to anything, so a row could only
change by a hand edit, and a stale row was indistinguishable from a correct one
by reading it. `capture-version-matrix.sh` does not help: it rewrites five host
facts (systemd, podman, netplan, nvidia) with `sed` and never looks at an
image at all.

The check now exists as `scripts/validation/check-image-digests.sh`, and it
found real drift immediately. **7 matrix rows name a digest no deployed unit
carries, 1 deployed image is not digest-pinned, and 4 deployed digests appear
nowhere in the matrix:**

```
$ AO_ROOT=$PWD bash scripts/validation/check-image-digests.sh --check
deployed units  : 21 in /home/scottw/.config/containers/systemd
distinct digests: 14
UNPINNED  Image=localhost/gz-sim10-resolute:gui-svgfix
DRIFT     mapping.broker_image_digest              sha256:91d0f7e8c748e...
DRIFT     simulation.gazebo_images                 sha256:0c19f326a339e...
DRIFT     simulation.image_foxglove_bridge         sha256:6d3461ddf0277...
DRIFT     sales.mastodon.image_postgres            sha256:a65e6a841f6c4...
DRIFT     sales.mastodon.image_redis               sha256:91d0f7e8c748e...
DRIFT     operations.image_postgres_shared         sha256:a65e6a841f6c4...
matrix digests matched a deployed unit  : 11
matrix digests matching nothing deployed: 7
deployed Image= lines without a digest  : 1
UNLISTED  deployed but absent from the matrix: sha256:d74eeac9a635...   (postgres, 3 units)
UNLISTED  deployed but absent from the matrix: sha256:c6eabf748fc7...   (redis, 2 units)
UNLISTED  deployed but absent from the matrix: sha256:9acc6d4df749...   (foxglove)
UNLISTED  deployed but absent from the matrix: sha256:55f8dbcf8dec...   (gz-sim10-server)
RESULT: DRIFT -- 7 stale matrix row(s), 1 unpinned deployed image(s).
$ echo $?
1
```

The postgres row is the clearest case, and the reason a naive check is not
enough. The matrix records `docker.io/library/postgres@sha256:a65e6a84…` in
two rows — `sales.mastodon.image_postgres` and
`operations.image_postgres_shared` — while **all three** deployed postgres
units (`ao-fabrication-db`, `ao-mastodon-db`, `ao-sales-db`) run
`sha256:d74eeac9…`. Nothing is wrong with either digest; the document and the
live system simply stopped agreeing, and neither could tell the other had
moved.

**Why the check reads the deployed units and not the repository tree.**
Quadlet deploys **flat**: `~/.config/containers/systemd/` holds copies, not
symlinks. Comparing the matrix against `quadlet/` would have reported "no
drift" at precisely the moment the live system had drifted — the repository
copy can be correct while the unit that is actually running is not. The
deployed unit is the only thing that describes what is running, so it is the
authority here.

**The check reports; it never rewrites.** Where a row disagrees with the live
system, deciding which side is right is an operator judgement — it may be a
stale document, an unapproved deploy, or a deliberate change never recorded. A
script that adopted the live digest would make the matrix self-fulfilling and
launder a hand edit into an apparently-captured fact. So the seven rows above
are **reported as findings, not fixed**. That is deliberate, and it is the
part most likely to look like incompleteness.

**A bug this check had on its first run, which the tests caught.** When every
deployed image is unpinned, the digest-extracting `grep` matches nothing and
exits 1; under `set -e` + `pipefail` that aborted the script with **status 1
and no output at all**. A gate that fails without saying why is worse than no
gate, because the next reader cannot tell a real finding from a crash. It is
fixed by tolerating the empty result in collection rather than by loosening
`set -e`, because the unpinned images are precisely what the script most needs
to report.

That is why the five tests drive the **real script** against a synthetic tree
and assert exit codes, rather than testing a Python reimplementation: a check
only ever observed in its failing state proves nothing, because "7 rows
drifted" is exactly what a broken comparison prints too.

```
$ python3 -m pytest scripts/build-update/test_generators.py -q
62 passed in 0.73s
```

Five cases, and the OK path is exercised as carefully as the failing ones:

| Case | Asserts |
|---|---|
| matrix matches deployed | `RESULT: OK`, exit **0** |
| one stale matrix row | `DRIFT` naming `host.images.a`, exit **1** |
| `Image=…:latest` | `UNPINNED`, exit **1** |
| `sha256:` + 12 hex chars | `UNPINNED`, exit **1** |
| stale row, no `--check` | `RESULT: DRIFT` but exit **0** |

The fourth case is the §12.5.2 lesson reused: a `sha256:` prefix is not a
pinned reference, and the same class of bug that produced
`podman pull repo@sha256:<12>` would otherwise let a 12-character digest pass
here. The fifth case exists because a validation script that *always* exits
non-zero stops being run — so reporting is the default and `--check` is the
gate, and that distinction has to live in the exit code rather than only in
the prose.

### 12.5.6 Roll-ups can be drilled into (OPS-23)

`KDE Plasma Desktop` was one row for 191 components, the Ubuntu archive one row
for 3,857 packages, the ROS train one row for 351. "Is the desktop behind" is
answerable; "update ROS 2 rviz" is not. Collapsing those rows is right — they
were 90 percent of the document — but a collapsed row that hides its members is
a dead end. Each roll-up now carries a `members` list and renders it as a
`<details>` drill-down, in Markdown, HTML **and** the PDF:

```
$ grep -o '<summary>[^<]*</summary>' /tmp/ops23v/s.md
<summary>Rolled-up launchers — expand to list every application entry (153 entries across 34 groups)</summary>
<summary>Ubuntu archive packages — expand to list all 3857 packages with their installed versions</summary>
<summary>ROS 2 lyrical (whole train) — expand to list all 351 packages with their installed versions</summary>
<summary>KDE Plasma Desktop — expand to list all 191 components</summary>

$ grep -c "details class='drill'" /tmp/ops23v/s.html
38
```

Reproduce with a scratch render, which touches nothing tracked:

```
$ AO_ROOT=$PWD python3 scripts/build-update/provenance-log.py --offline \
      --out /tmp/ops23v/s.md --html /tmp/ops23v/s.html --plan /tmp/ops23v/p.json
```

**A trap here, and the reason the numbers above were nearly unprovable.** The
tracked render artifacts `docs/software-status.md` and `tmp/software-status.html`
are **stale** — dated 2026-10-03 20:53, while the generator carrying this fix
landed 2026-10-04 10:30. So checking the fix against them shows 2 summaries and
**0** drill-downs, which reads exactly like "the fix does not work":

```
$ grep -o '<summary>[^<]*</summary>' docs/software-status.md
<summary>Rolled-up launchers — expand to list every application entry (153 entries across 34 groups)</summary>
<summary>KDE Plasma Desktop — expand to list all 191 components</summary>
$ grep -c "details class='drill'" tmp/software-status.html
0
```

Both apt roll-ups are missing there too, which is the §12.5.5 pattern in a
different guise: the code is correct and the artifact predates it. The
committed documents have **not** been regenerated, so the shipped PDF still
collapses those rows to bare counts. That is a real outstanding action, and it
is why the evidence above comes from a scratch render rather than from the
tracked files — the claim is about the generator, and it is stated as such.

The HTML drill-down is inline on the row itself, where the count promised it,
and carries every member as its own `<li>`.

Members are rendered with their **own versions** (`libc6 (2.42-1)`), which is
what OPS-23 asks for; a bare list of names would answer "which" but not "which
version".

**The failure this item describes was silent, which is why it was easy to miss.**
The members were computed and carried on the row as `members`, but the HTML
table renderer never emitted them — so the drill-down existed in Markdown only
and the HTML and PDF quietly lost it. Nothing errored; the document just stopped
being able to answer a question. `TestRollupsCanBeDrilledInto` asserts the HTML
path specifically, and that the drill-down survives the print stylesheet,
because a PDF that hides it reintroduces the same dead end. Member names are
HTML-escaped: they come from `.desktop` files on disk and are not trusted.

The two apt roll-ups were still bare counts after that first pass — checked
the rendered output rather than trusting the code, and `Ubuntu archive packages`
and `ROS 2 lyrical (whole train)` carried no members. Both lists are already in
`inv`, so both now attach theirs; the ROS one matters most because the train is
FROZEN, making "which 351 packages are affected" the question an operator will
actually ask. `test_the_apt_rollups_carry_their_members` is the guard, and I
confirmed it is not vacuous by deleting both `members` keys and watching it
fail with `Ubuntu archive packages is a roll-up with no members`.

**A second fix the first one created.** Attaching members made the Markdown
~3× larger, but the existing roll-up renderer joined them into a single table
cell (`', '.join(members)`), so the Ubuntu archive came out as **one
40,000-character line**. That technically satisfied "the members are reachable"
and practically failed the reader as badly as the original count — a single row
you cannot scan is not a drill-down. Package roll-ups now render one member per
row with the version in its own column, in their own collapsible block; the
launcher grouping keeps its joined cell, where members are short and few. The
roll-up emitter was extracted from `render()` into `rollup_details_md()` so this
is unit-testable — `render()` spends hundreds of apt round trips, which no test
should pay to assert a formatting rule.

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

## 13.2 Podman Store Model

**Designated runtime: rootless, single-store.** Every ALWAYS ON workload runs **rootless**
under the operator account `scottw` (uid 1000), with user-level Quadlet units in
`~/.config/containers/systemd/`, exactly as §13.1 prescribes. The system/rootful store is
not used by any workload. **This is a designation, measured 2026-10-03** — the commands and
their output are in `agents/COORDINATION (README UPDATES)/proposals/plat-PLAT-01.md`.

| Question | Measured answer |
|---|---|
| Is the operator Podman rootless? | `podman info --format '{{.Host.Security.Rootless}}'` → `true` |
| Which store backs it? | `podman info --format '{{.Store.GraphRoot}}'` → `/home/scottw/.local/share/containers/storage` |
| Do any Quadlet units name a `User=` or `Group=`? | none — `grep -rn '^User=\|^Group=' quadlet/` returns nothing |
| Are there system-level `.container` or `.network` units? | **No — measured 2026-10-04 16:40.** `systemctl list-unit-files '*.container' --no-legend \| wc -l` → `0`, and `systemctl list-unit-files 'ao-*' --no-legend \| grep -Ec '\.(container\|network)$'` → `0`. Every mapping unit is `systemctl --user`, state `generated` (Quadlet generator output) |
| Are the WebODM containers in the operator store? | `podman ps` lists `ao-webodm-{webapp,worker,db,broker}` and `ao-nodeodm` from the rootless store above |
| Are the declared extra connections real? | `podman system connection list` → header only; `~/.config/containers/podman-connections.json` is `{"Connection":{},"Farm":{}}` |
| Does `/run/ao-podman/` exist? | `ls /run/ao-podman` → `No such file or directory` |
| Is `ao-podman-bridge.service` active? | `systemctl is-enabled ao-podman-bridge.service` → `disabled`; `systemctl --user is-enabled` → `not-found` |
| Does the **rootful** store hold any workload? | **No — measured 2026-10-04.** `/var/lib/containers/storage/db.sql` is world-readable and its `ContainerConfig`, `ContainerState`, `ContainerExitCode`, `VolumeConfig`, `PodConfig` and `ContainerDependency` tables are **all empty** (row count `0` each). Enumerated without `sudo`; see §13.2.1 |

The container store therefore has one owner. Podman Desktop, `podman system connection`,
and any GUI path are all pointed at the operator account's local rootless socket, and
`podman-connections.json` declares no separate connections.

**Rules.**

- No per-service container store is created. No workload runs under a per-service account.
- `ao-podman-bridge.service` is not part of this design and is disabled.
- `/run/ao-podman/` holds no sockets. The directory is `tmpfs`-backed and clears on reboot.

**Compensating controls.** Running every workload as an unprivileged user is the primary
control. The controls that make it sufficient are stated once, in §4.1 — no `--privileged`,
no added capabilities, pinned digests, no direct public listener — and are not repeated
here. Two are specific to this model:

- Explicit bind mounts are limited to approved mapping paths (§5.3).
- systemd resource limits and a restart policy are set on every unit.

### 13.2.1 Recorded deviation — per-service accounts exist but run nothing

The design forbids a per-service store, and no workload uses one. **However, the accounts and
one system unit from that rejected design are still present on the host.** Recording them here
is what closes the disagreement between this section and the §19.2 row that described a
"mixed-store deviation": there is no mixed store. What exists is unused scaffolding.

| Artefact | Measured state | Meaning |
|---|---|---|
| `ao-sales` (uid 993), `ao-ledger` (994), `ao-mapping` (997) | accounts exist with home directories `/home/alwayson-{sales,ledger,mapping}` | accounts only |
| `loginctl show-user ao-mapping` | `Failed to get user: User ID 997 is not logged in or lingering` | not lingering, so it cannot own a user-level Quadlet unit |
| `ps -eo user,comm \| awk '$1 ~ /ao-\|alwayson/'` | no rows | no process runs as any of the three |
| `/etc/systemd/system/ao-podman-bridge.service` | present, `systemctl is-enabled` → `disabled` | the rejected bridge unit, masked by being disabled |
| `/run/ao-podman/` | `No such file or directory` | the rejected socket directory was never created |
| `/var/lib/containers/storage` | exists, `db.sql` last written 2026-09-30 | **enumerated 2026-10-04** — zero containers/pods/volumes; residual images unverified, see below |

**Deviation.** The host carries three unused service accounts and one disabled system unit
that this design does not authorise. They hold no container store, no socket and no process,
so the single-store designation above is unaffected. They are **left in place**: removing an
account or a unit file is a deletion, and README §4.1 rule 3 requires explicit operator
approval. **This is an OPEN item for the operator**, not a defect in the running system.

**CORRECTION 2026-10-04 (measured): the rootful store is *not* inaccessible, and the previous
recording of this OPEN item was wrong.** The section said the store's "contents are
`drwx------ root root`" and that `sudo ls` returned `Permission denied`, so enumeration needed
operator approval. **Both are wrong, and the mistake was generalising a mode from a child
directory to the store root.** Measured:

```
$ stat -c '%A %U:%G %n' /var/lib/containers/storage
drwxr-xr-x root:root /var/lib/containers/storage
$ ls -la /var/lib/containers/storage/ | head -4
-rw-r--r-- 1 root root 114688 Sep 30 20:26 db.sql          # world-READABLE
drwx------ 2 root root   4096 Aug 26 19:13 overlay-images  # the 0700 parts are the CHILDREN
$ stat -c '%A %n' /var/lib/containers/storage/overlay-images/
drwx------                                                 # <- generalised upward from here
```

So the **top level and `db.sql` are readable by uid 1000 with no `sudo` at all**, and the store
can be substantially enumerated. `sqlite3(3)` is not installed, but Python's `sqlite3` module is
sufficient and needs no package:

```
$ python3 -c "import sqlite3; c=sqlite3.connect('file:/var/lib/containers/storage/db.sql?mode=ro',uri=True); print({t: c.execute('select count(*) from '+t).fetchone()[0] for t in ('ContainerConfig','ContainerState','ContainerExitCode','VolumeConfig','PodConfig','ContainerDependency')})"
{'ContainerConfig': 0, 'ContainerState': 0, 'ContainerExitCode': 0,
 'VolumeConfig': 0, 'PodConfig': 0, 'ContainerDependency': 0}
```

**Every container-, pod- and volume-bearing table is empty.** The rootful store holds **no
containers, no pods, no volumes and no dependency records**. It has no `Image` table at all —
in `containers/storage` images live in the `overlay-images/` bolt databases, not in `db.sql`:

```
$ python3 -c "import sqlite3; c=sqlite3.connect('file:/var/lib/containers/storage/db.sql?mode=ro',uri=True); print([r[0] for r in c.execute(\"select name from sqlite_master where type='table'\")])"
['ContainerDependency','ContainerExitCode','PodState','VolumeConfig','DBConfig','IDNamespace',
 'ContainerConfig','ContainerVolume','PodConfig','VolumeState','ContainerState','ContainerExecSession']
any image table: NONE
```

**This materially strengthens the single-store designation.** The store is not merely
"unused by any workload" as the previous revision had to concede — it holds **no workload
records whatsoever**, and the earlier claim that this could only be resolved with operator
approval was wrong on both counts: the mode was misread, and no approval was ever needed.

**Seven `ao-*` unit files exist at system level — none of them is a container.** Re-measured
2026-10-04 16:40 with a deliberately broad pattern, because the row above originally cited only
`ao-webodm*`, which returns `0` even when unrelated system units exist:

```
$ systemctl list-unit-files 'ao-*' | grep '^ao-'
ao-podman-bridge.service   disabled enabled
ao-restic-backup.service   static   -
ao-restic-prefetch.service static   -
ao-restic-verify.service   static   -
ao-restic-backup.timer     enabled  enabled
ao-restic-prefetch.timer   disabled enabled
ao-restic-verify.timer     enabled  enabled
```

The six `ao-restic-*` units are host backup timers, not Quadlet containers, and
`systemctl cat ao-restic-backup.service ao-restic-verify.service | grep -Ec 'podman|containers/storage'`
returns **`0`** — they never touch a container store. The seventh is the rejected bridge unit already
recorded in §13.2.1. The single-store designation is unaffected, but **"no system-level `ao-*`
units" would have been false**; only "no system-level `ao-*` *container* units" is true, and that
is what the design actually prohibits. Those restic units belong to §17 and are another session's.

**Still open, and narrower than stated: residual image data.** `overlay-images/` is mode `0700`
and both `ls` and `du` return `Permission denied` as uid 1000, so **whether any image blobs remain is
still unverified**. This is consistent with the last write being `2026-09-30` (images were pulled
before the rootless migration) but does not prove it. For contrast the rootless store holds **100**
distinct image IDs and is fully enumerable by the operator — measured 2026-10-04 17:05 as
`podman images --all --quiet | sort -u | wc -l` → `100`.

**Correction, 2026-10-04 17:05: "of which 50 are named" was wrong — the figure is 30.** The `100`
count is right and reproduces exactly, but the breakdown attached to it was written without being
measured. `--quiet` emits bare image IDs, so it cannot answer the naming question at all; the
image-name-to-digest mapping had to
to ask it with `--format`:

```
$ podman images --all --quiet | sort -u | wc -l
100
$ podman images --all --format '{{.Repository}}:{{.Tag}}' | sort -u | wc -l
31                                  # distinct Repository:Tag entries
$ podman images --all --format '{{.Repository}}:{{.Tag}}' | sort -u | grep -vc '<none>:<none>'
30                                  # the actually-named ones
```

So **30 images carry a repository:tag name and 70 are intermediate or unreferenced layers** —
not 50/50. Note the two counting questions are different and neither substitutes for the other:
`--quiet | sort -u` counts image *IDs* (100), while `--format | sort -u` counts *name* entries (31).
The retracted "102 image records" figure was wrong for the same reason — it was written without
running the count.

Enumerating the rootful remainder needs
one `sudo` command and operator approval — recommended action, **no automatic action taken**, and
no deletion is proposed.

`ao-sales` and `ao-reporting-egress` are non-internal by recorded decision; that
exception belongs to §5.1, not to the store model.

## 13.3 `/ALWAYSON` Layout

```text
/ALWAYSON/
├── README.md
├── VERSION
├── AGENTS.md
├── quadlet/
│   ├── networks/          # the 14 ao-* .network definitions (see network-cidrs.yaml)
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
├── secrets/               # IGNORED - runtime secret material, never in git
├── data/                  # IGNORED - persistent runtime data (restic, corda-install)
├── logs/                  # IGNORED - operational logs
├── artifacts/  backups/   # IGNORED - generated artefacts and restore material
├── pcloud/  ipfs/         # IGNORED - transfer working areas
└── tmp/                   # IGNORED
```

### 13.3.1 Additional paths

The tree above is the design layout. These paths also exist, and are either generated views
or archived material:

| Path | What it is |
|---|---|
| `TOPOLOGY/` | topology graphic source and review material |
| `LOGS-JOURNALS/` | pointer only — the logs live in `logs/` (§16.3, §16.3) |
| `GAZEBO/`, `SIMULATION.png`, `WEBSITEMAIN.png` | simulation and storefront imagery |
| `README - ARCHIVE/` | archived README versions and review comments |

The storefront is served from filedn and has no local `storefront/` directory. Validation
lives in `scripts/validation/`, not `tests/`. Mastodon Quadlet definitions live in
`quadlet/sales/`.

The repository is on `main`, and `.gitignore` covers every path marked `IGNORED` above, plus
Python bytecode, `*.BAK-*` unit backups, and generated topology binaries. A secret-exposure
check runs over every tracked file:
`scripts/validation/check-secrets-exposure.sh`.

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
# /ALWAYSON/quadlet/mapping/ao-webodm-web.container   (illustrative template)
[Unit]
Description=ALWAYS ON WebODM Web Service
After=network-online.target
Wants=network-online.target

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
WantedBy=default.target
```

This is a structural template only. The exact image, API settings, mounts,
service name, environment, and GPU configuration must be taken from the tested
and approved WebODM version.

---

# 14. Secrets and Service Identity

## 14.1 Secret Delivery

Use Podman secrets or systemd credentials. Prefer file-based secret delivery
rather than environment variables.


### 14.1.1 KDE Wallet Secret Management

KDE Wallet is the operator-side secret and credential store for this host. Section 14.1 is
the policy; this subsection is the integration. The unattended-delivery deviation is recorded
in **§14.1.6**, the rotation and recovery procedure in **§14.2**.

**Runtime.** Daemon `kwalletd6` on the `org.kde.kwalletd6` D-Bus name, wallet `kdewallet`,
auto-unlocked with the operator's Plasma login. `org.kde.kwalletd` and `org.kde.kwalletd5`
are also live; prefer `kwalletd6` in new code.

| Item | Value |
|---|---|
| Object path | `/modules/kwalletd6` |
| `open()` | returns a live handle against wallet `kdewallet` |
| Methods used by `scripts/ops/wallet-read-secret.py` | `hasEntry`, `readPassword` |
| Method used by `scripts/ops/wallet-write-secret.py` | `writePassword` |

**Tooling.**

- Management CLI `scripts/ops/kwallet-provision.sh` (`create-folders`, `put`, `get`), run only
  from the interactive Plasma session while the wallet is unlocked.
- `scripts/operations/fetch-kwallet-secret.sh` runs as a Quadlet `ExecStartPre`: it waits for
  the desktop session and kwalletd (max ~60s), reads the required entries, and writes a
  service-specific `0600` env file the unit consumes via `--env-file`. It serves
  `ao-mastodon-db`, `ao-sales-db`, `ao-webodm-db` and `ao-fabrication-db`. **A new key must be
  added as a `case` branch in that script or the unit fails.**
- Env files materialise under `%h/.local/share/ao-secrets/`, via `ao-wallet-bridge.sh` or the
  unit's own `ExecStartPre`. `~/secrets/` holds unrelated material and is not part of the
  delivery path.

**Login-gated start is intended.** Services that consume wallet secrets start after Plasma
login and are not expected to start unattended before a password is entered. The ~60s wait is
the bounded startup allowance for that login, not a fallback for a passwordless boot. Auto-login
is an operator convenience, not a requirement of this design.

**All services run under the operator's own account.** No service requires a separate
service-account user, and no per-service container store is created (§13.2).

**One folder per domain.** Every credential lives in exactly one `ao-*` folder and its service
reads it from there, so a role and the application connecting to it always share one value.
There is no generic or cross-domain folder.

| Folder | Purpose |
|---|---|
| `ao-mastodon` | Mastodon application secrets (§15.3) and OpenClaw OAuth material; read by `fetch-mastodon-env.sh` and the wallet bridge |
| `ao-sales` | `sales-db-password` |
| `ao-fabrication` | `fabrication-db-password` |
| `ao-mapping` | WebODM postgres password |
| `ao-admin` | `grafana-db-password`, `grafana-admin-password`, `metabase-db-password`, `metaread-password`, `sales-reporting-password`, `restic-repository-password` |
| `ao-sim-vehicle`, `ao-sim-fabrication` | Per-domain credential folders matching the §14.1 authorized-domain table |
| `ao-payment`, `ao-field`, `ao-ledger`, `ao-archive` | Created only when the consumer exists and the credential is provisioned (§14.1.2), never speculatively. `ao-payment` is provisioned as part of ST-12 |

Entries are listed by name only — values are never in Git, logs, or docs. Every key lives in
the `ao-` folder for the domain that owns it.

| Folder | Entries |
|---|---|
| `ao-mastodon` | `mastodon-secret-key-base`, `mastodon-otp-secret`, `mastodon-db-password`, `mastodon-ar-deterministic-key`, `mastodon-ar-primary-key`, `mastodon-ar-derivation-salt`, `mastodon-admin-password`, `openclaw-bot-client-id`, `openclaw-bot-client-secret`, `openclaw-bot-access-token`, `openclaw-bot-password`, `roundtrip`/`roundtrip2` (test artifacts) |
| `ao-sales` | `sales-db-password` |
| `ao-fabrication` | `fabrication-db-password` |
| `ao-mapping` | WebODM postgres password |
| `ao-admin` | `grafana-db-password`, `grafana-admin-password`, `metabase-db-password`, `metaread-password`, `sales-reporting-password`, `restic-repository-password` |

**Rules.**

- Never print, copy, export, or log entry values; confirm presence only, using the D-Bus
  `hasEntry` method on `org.kde.kwalletd6`. (`entryList` takes a further argument and is not
  used by the tooling.)
- Entries are named per service and per purpose; domain folders enforce the §14.1
  authorized-domain boundaries.
- Rotation, revocation, expiration, and recovery procedures must be documented before
  production use.
- **No plaintext duplicate of a wallet entry exists.** Credential material lives in the wallet
  and nowhere else. No file under `secrets/` or `config/` may hold a credential the wallet also
  holds.

**Grafana is wallet-backed like everything else.** Its web admin password is
`ao-admin/grafana-admin-password`; `fetch-kwallet-secret.sh` maps it through `wallet_folder_for`
and emits a `grafana-admin-password` case branch, and `ao-grafana.container` reads two files:
`config/platform/monitoring/grafana-admin.env` for non-secret settings
(`GF_SECURITY_ADMIN_USER`, `GF_USERS_ALLOW_SIGN_UP`, `GF_AUTH_ANONYMOUS_ENABLED`) and
`%h/.local/share/ao-secrets/reporting-grafana-admin.env` for `GF_SECURITY_ADMIN_PASSWORD`,
materialised `0600` by the unit's `ExecStartPre` and never tracked. `/api/health` returns 200
with database ok, and an admin login using the wallet value returns HTTP 200.

**Scripts that need these credentials read them from the wallet at start-up, never from a
plaintext file.**

- `scripts/operations/fetch-kwallet-secret.sh` — carries the `ao-admin` keys in
  `wallet_folder_for`.
- `scripts/ops/provision-metaread.sh`, `provision-sales-reporting.sh` — read the password from
  the wallet and mirror it back instead of seeding it from a file.
- `scripts/ops/provision-reporting-postgres.sh` — reads `metabase-db-password` and
  `grafana-db-password` from `ao-admin`.
- `scripts/mastodon/post.sh` — materialises the bot credential from the wallet into a `0600`
  temp file and shreds it on exit.
- `scripts/mastodon/provision-openclaw-bot.sh` — stores the generated password in the wallet
  only and writes no env file.

`check-secrets-exposure.sh` carries three rule-7 checks: a tracked `.env` must not carry a
credential, a Quadlet `EnvironmentFile` pointing into `config/` or `secrets/` must not be
secret-bearing, and any secret-bearing env file on disk must not be readable by other users.

### 14.1.2 Secret-delivery rules

**One folder per domain.** Each credential lives in exactly one `ao-*` folder, and each
service reads it from there. There is no generic or cross-domain wallet folder, and
`fetch-kwallet-secret.sh` maps each key to its owning folder rather than a hardcoded one.

| Credential | Folder |
|---|---|
| `sales-db-password` | `ao-sales` |
| `fabrication-db-password` | `ao-fabrication` |
| `webodm-postgres-password` | `ao-mapping` |
| `mastodon-db-password` | `ao-mastodon` |
| `payment-db-password`, `payment-paypal-webhook-id`, `payment-paypal-webhook-secret`, `payment-coinbase-webhook-secret` | `ao-payment` |
| `pcloud-webdav-password`, `pcloud-webdav-user` | `ao-archive` |

The last two rows are mapped in `wallet_folder_for`. **Both folders now exist on this host,
and this paragraph's earlier claim that they are absent is retracted.**

Measured 2026-10-05 via the D-Bus `hasFolder(handle, folder, app)` signature, with a control
test that matters more than the numbers:

    ao-admin True  ao-fabrication True  ao-mapping True  ao-mastodon True
    ao-sales True  ao-sim-fabrication True  ao-sim-vehicle True
    ao-payment True  ao-archive True          <- were False on 2026-10-04
    zzz-does-not-exist-9999  False            <- control: the probe is not lying
    ao-totally-made-up       False
    ''                       True             <- empty folder name returns True

All four `ao-payment` entries and both `ao-archive` entries now return `hasEntry = True`
(`payment-db-password`, `payment-paypal-webhook-id`, `payment-paypal-webhook-secret`,
`payment-coinbase-webhook-secret`, `pcloud-webdav-password`, `pcloud-webdav-user`).

**Why the control test is mandatory.** The first two probes returned `True` for
*every* folder, including ones previously recorded as absent, which is exactly the
shape of a broken probe. The nonsense-name control returned `False`, which is what
makes the seven-and-two `True` results believable. **A finding that contradicts a
prior measurement must be earned with a negative control, not asserted.**

**Mapping is not the same as deliverability.** `wallet_folder_for` routes 30-odd entry names,
but a mapping only means the fetcher will *try*. Several entries the fetcher names are read
by other consumers instead — `openclaw-bot-client-secret` and
`cloudflare-tunnel-credentials-json` by `fetch-openclaw-mastodon-env.sh` and
`fetch-cloudflared-env.sh`, `producer-private-key` by `scripts/ledger/sign-manifest.sh` —
and those are not affected by a missing entry in `wallet_folder_for`. Conversely an entry
that *is* mapped but whose folder is absent is a hard fetch failure, which is the
`ao-payment` case.

A role and the application that connects to it must use the same password, so a fresh
`mastodon-dbdata` cannot be created with a different password than the application connects
with.

**One env root.** Every unit that consumes a secret-bearing env file reads
`%h/.local/share/ao-secrets/`: `ao-mastodon-db`, `ao-sales-db`, `ao-webodm-db`,
`ao-webodm-web`, `ao-webodm-worker`, `ao-fabrication-db`, the `ao-mastodon-web` /
`ao-mastodon-streaming` / `ao-mastodon-sidekiq` set, `ao-mastodon-web`'s repair `ExecStartPost`,
`ao-grafana`, `ao-metabase`, `ao-ingress-payment`, `ao-status-collect`,
`ao-db-security-collect` and `ao-fabrication-collect`. No secret-bearing env file is written to
`%h/secrets/`.

The one deliberate exception is `ao-grafana`'s
`EnvironmentFile=/ALWAYSON/config/platform/monitoring/grafana-admin.env`. It sits in the tracked
`config/` tree and is readable by other users (`0644`), which is safe only because it is
non-secret by construction: `GF_SECURITY_ADMIN_USER`, `GF_USERS_ALLOW_SIGN_UP`,
`GF_AUTH_ANONYMOUS_ENABLED` and `GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS` and nothing else. The
admin password is read separately from the `0600` wallet-materialised file. Verify the
non-secreteness by key name, not by assuming it:

    $ sed 's/=.*/=/' config/platform/monitoring/grafana-admin.env | grep -v '^#' | grep -v '^$'
    GF_SECURITY_ADMIN_USER=
    GF_USERS_ALLOW_SIGN_UP=
    GF_AUTH_ANONYMOUS_ENABLED=
    GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS=
    → exactly four keys, no password, token or key name present.

Two stray files under `ao-secrets/` are documented elsewhere: the orphaned
`legacy-alwayson-folder.env` (**§14.1.6**) and the dangling `~/secrets/mastodon.env` symlink,
which is outside this root and inert.

### 14.1.3 One env file, one wallet entry

**There is exactly one env file, and it is the live `EnvironmentFile`.**

| Location | Role |
|---|---|
| `~/.local/share/ao-secrets/mastodon.env` | **The only env file.** Loaded by `EnvironmentFile=` in `quadlet/sales/ao-mastodon-web.container` |
| KDE Wallet `kdewallet` / `ao-mastodon` / `mastodon-env` | Wallet copy of the same content. **Was documented here as "byte-identical by SHA-256 (1043 bytes)". That is wrong — see the correction below.** |
| KDE Wallet `ao-mastodon` / `mastodon-secret-key-base`, `mastodon-otp-secret`, `mastodon-db-password` | Per-key wallet entries |

No second copy of this file is kept anywhere, and nothing may be restored into the
repository. A stale copy is worse than no copy: its `DB_PASS` / `POSTGRES_PASSWORD` would not
match the running instance and its `LOCAL_DOMAIN` would be wrong, so restoring it would
break PostgreSQL auth for `mastodon-db`.

#### The wallet entry and the env file have diverged — corrected 2026-10-05

The claim above that the two are byte-identical was **wrong**, and it was wrong in the
direction that hides a real fault. Re-measured, comparing lengths and SHA-256 prefixes only:

    $ stat -c '%s' ~/.local/share/ao-secrets/mastodon.env            -> 1041
    wallet ao-mastodon/mastodon-env, readPassword                     -> 1043 bytes
    file   sha256[:16] = 07519ca502b612e6
    wallet sha256[:16] = 2dba7da35030466f      (different)
    key names (values stripped, sorted): diff -> IDENTICAL, 23 keys, 24 lines both sides

So the structure is the same and **two values differ**:

| Key | Wallet | Env file |
|---|---|---|
| `LOCAL_HTTPS` | `false` | `true` |
| `RAILS_FORCE_SSL` | `false` | `true` |

Every other key, including all three 64-byte Active Record encryption keys, `SECRET_KEY_BASE`,
`OTP_SECRET`, `DB_PASS` and `POSTGRES_PASSWORD`, compares equal. The 2-byte size delta is
exactly the two `false`→`true` widenings.

**Why this is a security finding and not trivia.** `RAILS_FORCE_SSL=false` is the setting that
tells Mastodon to redirect HTTP to HTTPS. The wallet — the system of record — says `false`;
the file the three Mastodon units actually load says `true`. So the enforced posture and the
recorded posture are opposite, and the file is the one in force. Whichever way the operator
rounds this, one of the two is wrong, and the difference is TLS enforcement on the public
Mastodon instance.

**This also invalidates a rule written above.** §14.1.3's single-file rule and §14.1.6's "every
file is rewritten from the wallet on each refresh" both assume wallet and file agree. They now
disagree, which means either the file was hand-edited after its last fetch or the wallet entry
was changed without a refresh. **Not determined here** — the fetcher's `mastodon-env`
branch and the file's mtime (`2026-10-01 15:08`, the same minute as the Mastodon units' start)
are consistent with a fetch-then-edit, but that is an inference, not a measurement.
**A divergence must not be attributed to a cause until the cause is measured.**

#### RETRACTED 2026-10-05 (second pass): the two values above do not diverge, and there is no TLS fault

**The table above is retained only as a record of the mistake. Its conclusion is wrong and must
not be carried into any operator decision.** The correction was found by asking a question the
first pass never asked: *does anything actually read the wallet entry it was comparing against?*

**Answer: nothing does.** `RAILS_FORCE_SSL` and `LOCAL_HTTPS` are not wallet-held values at all.
They are **hardcoded literals in the fetcher**:

    $ grep -rn 'RAILS_FORCE_SSL\|LOCAL_HTTPS' --include='*.sh' --include='*.container' --include='*.py' .
    ./scripts/operations/fetch-mastodon-env.sh:42:  printf 'RAILS_FORCE_SSL=true\n'
    ./scripts/operations/fetch-mastodon-env.sh:43:  printf 'LOCAL_HTTPS=true\n'

Those two lines are the **only** occurrences in the entire repository. The wallet entry
`kdewallet / ao-mastodon / mastodon-env` is referenced by **no** script, unit or config:

    $ grep -rn 'mastodon-env' scripts/ quadlet/ systemd/ config/
    → only script *filenames* (fetch-mastodon-env.sh) and two prose mentions in
      deploy-mastodon.sh; never as `wallet-read-secret.py … ao-mastodon mastodon-env`

`fetch-mastodon-env.sh` reads six per-key entries — `mastodon-secret-key-base`,
`mastodon-otp-secret`, `mastodon-db-password`, and the three `ACTIVE_RECORD_ENCRYPTION_*`
keys — and **prints the remaining ~17 lines as literals**. `RAILS_FORCE_SSL` and `LOCAL_HTTPS`
are in that literal block.

**So the correct reading is the reverse of what §14.1.3 asserted.** The env file's `true` is not
a hand-edit drifting from the wallet; it is the *repository-controlled, intended* value,
delivered by the fetcher that owns the file. The wallet entry's `false` is not a competing
source of truth — it is an **orphaned blob nothing consumes**. There is no disagreement about
TLS enforcement between two live authorities, because there is only one authority.

**What this does and does not change.**

- **Does:** withdraws the security finding. There is no "enforced posture and recorded posture
  are opposite" condition, and no operator decision is owed on TLS grounds. The `git log -S`
  history explains the literal: commit `5191928` (2026-09-25) introduced
  `RAILS_FORCE_SSL=true`, and `7542394` (2026-09-30) added `ALTERNATE_DOMAINS` alongside it —
  deliberate, with the commit message stating loopback now answers the 301 and public exposure
  is unchanged.
- **Does not:** the byte-identity claim in the table at the top of this subsection is still
  simply **false** (1041 vs 1043 bytes, `07519ca502b612e6` vs `2dba7da35030466f`), and the
  orphaned wallet entry is still a real, if lower-severity, finding — now recorded as stale
  documentation rather than a TLS conflict. See §14.1.3.1.
- **Unchanged and still true:** the six wallet-sourced values (all three 64-byte AR keys,
  `SECRET_KEY_BASE`, `OTP_SECRET`, `DB_PASS`/`POSTGRES_PASSWORD`) do compare equal, and
  §14.1.6's "every file is rewritten from the wallet on each refresh" holds **for those six
  keys** — the fetcher regenerates the whole file from the wallet plus literals on every bridge
  run. It is wrong only as a claim that the file mirrors the `mastodon-env` wallet entry.

**A divergence between a live artifact and an unread store is not a finding
until it has been shown that the store is read.** An earlier pass compared this
file against a wallet entry and reported the difference as a policy conflict
without ever checking that anything consumed the wallet entry; had an operator
acted on that, the likely outcome would have been a change to TLS enforcement on
a live public instance — an unnecessary, possibly harmful change manufactured
from a stale blob. The cheap check is one grep for the entry name across the
repository, and it must come *before* the comparison, not after.

### 14.1.3.1 The orphaned `mastodon-env` wallet entry (downgraded from security finding)

`kdewallet / ao-mastodon / mastodon-env` holds a 1043-byte full-bundle env snapshot that no
component reads (proved above). It is stale relative to the file it was compared with, and it
is the reason §14.1.3's byte-identity claim was ever made. It is a **documentation and
hygiene defect**, not a credential exposure: the secrets inside it are the same six wallet-held
values that are correctly stored, and the file it shadows is `0600`.

**Deleting the wallet entry is not performed here.** It is a change to
secret-classified material and outside this specification's authority (brief stop
conditions; README §4.1 rule 14). **Operator decision requested** — recommend
deletion, or a one-line comment in `fetch-mastodon-env.sh` naming it as retired so
the next auditor does not re-derive this finding from scratch. Note
`deploy-mastodon.sh:46` still *tells the operator* that the file's values are in
`mastodon-env`, which is misleading and is the likely source of the confusion;
correcting that comment is part of the same operator decision.

### 14.1.3.2 The Mastodon containers disagree with each other — live, measured, and a real fault

If §14.1.3's wallet-vs-file comparison is wrong, the question that matters is which value the
**running containers** actually hold. Measured:

    $ for c in mastodon-web mastodon-sidekiq mastodon-streaming; do
        podman inspect $c --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -E '^(RAILS_FORCE_SSL|LOCAL_HTTPS)='
      done
    mastodon-web       RAILS_FORCE_SSL=true   LOCAL_HTTPS=true
    mastodon-sidekiq   RAILS_FORCE_SSL=true   LOCAL_HTTPS=true
    mastodon-streaming RAILS_FORCE_SSL=false  LOCAL_HTTPS=false     ← disagrees

All three units name the **same** `EnvironmentFile=%h/.local/share/ao-secrets/mastodon.env` and
all three deployed copies are identical to the repository. So a single file is being read into
three different environments. **This is a genuine inconsistency, and it is the finding the
retracted table was reaching for but mis-located.**

**Mechanism — a start-order race, measured to the second:**

    mastodon-streaming created  2026-10-01 15:08:39.03
    mastodon.env mtime           2026-10-01 15:08:40.24     ← 1.2s LATER
    mastodon-web created         2026-10-01 15:08:57.25
    mastodon-sidekiq created     2026-10-01 15:21:03.61

`ao-wallet-bridge.service` is a `Type=oneshot` unit that runs `After=graphical-session.target`
and materialises the env file; it then starts the sales stack from the same manager
(`journalctl` at 15:08:40: `OK: wallet-backed Mastodon env materialized`). `mastodon-streaming`
was created **1.2 seconds before** that write completed, so it captured the *previous* file
content (`false`), while `mastodon-web` (18s later) and `mastodon-sidekiq` (12min later)
captured the new content (`true`). **The mastodon units declare no ordering against the
bridge** — `ao-mastodon-web.container` has `After=graphical-session.target ao-mastodon-db.service
ao-mastodon-redis.service ao-sales-network.service` and **no** `Requires=`/`After=` on
`ao-wallet-bridge.service`. Nothing enforces "materialise secrets, then start consumers".

**Severity — lower than it looks, and it must be reported as such.**
`mastodon-streaming` is the Node streaming API; `RAILS_FORCE_SSL` is a **Rails**
setting and the streaming process does not read it, so `false` there has no
HTTP-redirect effect. The inconsistency is real and should be fixed, but it is not
an open-HTTP-port finding and must not be presented as one. `LOCAL_HTTPS=false` is
the more meaningful half, as it governs the instance's own assumption about its
scheme. **No restart may be performed as part of this correction** — restarting
live Mastodon services is a stop condition, and would additionally drop in-flight
streaming connections.

**The ordering dependency is the defect, and it is not fixed by changing the
value.** Nothing enforces "materialise secrets, then start consumers": the three
Mastodon consumer units must carry `Requires=ao-wallet-bridge.service` /
`After=ao-wallet-bridge.service` so the file is written before anything reads it.
That edits three quadlet units and restarts live public-facing services. Prepared,
**not applied**, for the operator.

### 14.1.3.3 Ordering defect in this subsection — corrected 2026-10-05

`14.1.7.2` (the 2026-10-05 pass) had been written **above** `14.1.7.1` (the 2026-10-04 pass),
so the file read newest-then-oldest. The two blocks are now in date order. No content was
altered between them; only their order changed, and this note records why so a later pass does
not "fix" it back.

**`genenv` is non-destructive by rule.** It refuses to run when the env file already exists.
Regenerating it would mint new `SECRET_KEY_BASE` / `OTP_SECRET` / `POSTGRES_PASSWORD`,
invalidate every session, break DB auth, and write `LOCAL_DOMAIN=localhost` — breaking the
instance and its federation.

**`genenv` derives its path from `$HOME`, never `$AO_ROOT`.** The repository root is
`/ALWAYSON`; writing there would place a second, untracked, non-ignored copy of the secrets
inside the working tree. This is the same class of bug as the drift the single-file rule
prevents.

Consumers of the env file are `scripts/mastodon/deploy-mastodon.sh` and
`scripts/mastodon/provision-mastodon-encryption.sh`.

### 14.1.4 KDE Wallet D-Bus access

For services that must read secrets unattended, the wallet is reached over D-Bus as follows.

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

**Three `busctl` pitfalls, all of which produce misleading errors:**

1. `int64` arguments need an explicit type prefix — `open kdewallet x 0 app`.
   Without it: `Unknown signature type k`. Omit `x` and the call fails.
2. Several methods are **overloaded**, and `busctl` picks one signature:
   `isOpen` exists as both `isOpen(i)` and `isOpen(s)`, so
   `isOpen kdewallet` fails with `Too few parameters for signature`.
3. **The same overload trap applies to `dbus-python`, not just `busctl`.**
   dbus-python binds the proxy to the *last declared* signature, so
   `iface.isOpen(handle, 'app')` raises
   `TypeError: Fewer items found in D-Bus signature` — the opposite error text
   from `busctl`, for the same underlying cause. **Use the one-argument
   `isOpen(handle)`.** `folderList` and `entriesList` are also multi-argument:
   `folderList(handle, app)` and `entriesList(handle, folder, app)`.

There is **no `listFolders` method** — the folder enumeration method is
`folderList`. There is also no `introspect` on `org.kde.KWallet`; that lives on
`org.freedesktop.DBus.Introspectable`. Both mistakes were made and corrected
while auditing the Mastodon bridge.

**`folderList` returns DUPLICATE rows — de-duplicate before counting.** Measured
2026-10-01: a raw count reported 990 rows / "972 folders", which looks like
catastrophic duplication. `set()` gives the true **18 folders**; the same applies
to `entriesList`, whose de-duplicated `ao-*` + `Passwords` total is **39 entries**.

**Readiness: use `isOpen`, not daemon presence.** Gating on
`busctl --user list | grep kwalletd6` is wrong — kwalletd6 is D-Bus-activated the
moment anything touches it and appears long before the wallet is unlocked, so the
gate returns true instantly and any timeout behind it never waits. This caused a
login outage on 2026-10-01: `ao-grafana` and `ao-metabase` read a locked wallet,
failed their `ExecStartPre`, exhausted systemd's 5 fast restarts in ~5s and stayed
down. Both fetchers now use `isOpen(handle)` with a 30×2s budget.

**The locked path cannot be tested directly.** KWallet exposes no `lock()`;
`closeAllWallets()` does not leave the wallet locked, because the next `open()`
transparently re-unlocks via PAM. Use the forensic signal instead: a **0-byte
`.tmp`** from a failed fetch proves the wallet was locked, since the write block
never ran.

**Environment is not a barrier.** The systemd user manager carries
`DBUS_SESSION_BUS_ADDRESS`, `DISPLAY`, `WAYLAND_DISPLAY` and
`XDG_RUNTIME_DIR`, so a user unit needs no `Environment=` additions to reach
the wallet.

**Token requirements.** An HTTP 401 from the OpenClaw bridge is a token problem, never a
D-Bus, transport, or token-format problem. The requirements:

1. The systemd user manager carries `DBUS_SESSION_BUS_ADDRESS`, `DISPLAY` and
   `WAYLAND_DISPLAY`. A minimal `Environment=` block does not block wallet access.
2. A Mastodon access token is **43 base64 characters**, not 64 hex characters.
3. A token must be created with `expires_in: nil`. Doorkeeper reads `expires_in: 0` as
   *expires in zero seconds* — already expired — and the API answers
   `{"error":"The access token expired"}`.
4. The bridge owns a Doorkeeper application (`openclaw-mastodon-bridge`) with scopes
   `read:accounts read:notifications write:statuses read:statuses`. The token is stored in
   KDE Wallet at `ao-mastodon` / `openclaw-bot-access-token`, never in a file.

**Re-minting, when needed:** create or reuse the app, revoke prior tokens for
it, then create the token with `expires_in: nil`. Always store the result in
KDE Wallet rather than a file, and shred the temporary copy. Do not copy
existing token-handling scripts without checking for `expires_in: 0`.

### 14.1.5 Minting Mastodon API tokens

```
podman exec -i mastodon-web sh -c 'cat > /tmp/mint.rb' < mint.rb
podman exec mastodon-web sh -c \
  'cd /opt/mastodon && RAILS_ENV=production bundle exec rails runner /tmp/mint.rb'
```

```ruby
bot   = Account.find_by(username: 'bot', domain: nil)   # Mastodon 4.3 has no `local` column
owner = bot.user                                        # Doorkeeper owner_id/resource_owner_id are users.id
SCOPES = 'read:accounts read:notifications write:statuses read:statuses'
app = Doorkeeper::Application.find_by(name: 'openclaw-mastodon-bridge') ||
      Doorkeeper::Application.create!(name: 'openclaw-mastodon-bridge', scopes: SCOPES,
        redirect_uri: 'urn:ietf:wg:oauth:2.0:oob', confidential: false, owner: owner)
Doorkeeper::AccessToken.where(application_id: app.id).update_all(revoked_at: Time.now.utc)
tok = Doorkeeper::AccessToken.create!(application: app, resource_owner_id: owner.id,
  scopes: SCOPES, expires_in: nil, use_refresh_token: false)   # nil, NOT 0
File.write('/tmp/bot_token', tok.token)
```

Three traps: there is no `accounts.local` column;
`owner_id` and `resource_owner_id` reference the **`users`** table, not
`accounts`; and `expires_in: 0` produces an already-expired token.
### 14.1.6 Recorded deviation — env-file delivery instead of Podman secrets

**Orphaned plaintext copy: `%h/.local/share/ao-secrets/legacy-alwayson-folder.env`.** Found
2026-10-04, mode `0600`, holding four credential values by key name —
`mastodon-db-password`, `sales-db-password`, `webodm-postgres-password`,
`fabrication-db-password` — and referenced by **no** quadlet unit, script or section file. It is
a plaintext duplicate of wallet-held credentials, which §14.1.1's rules forbid outright.

Four measured facts, by sha256 prefix and no values printed, comparing each legacy key against
the live env file the owning unit reads:

| Legacy key | vs live env file | Result |
|---|---|---|
| `sales-db-password` | `sales-db.env` `POSTGRES_PASSWORD` | **SAME** (48 chars) — currently valid |
| `webodm-postgres-password` | `webodm.env` `POSTGRES_PASSWORD` | **SAME** (32 chars) — currently valid |
| `fabrication-db-password` | `fabrication-db.env` `POSTGRES_PASSWORD` | **SAME** (32 chars) — currently valid |
| `mastodon-db-password` | `mastodon-db.env` `POSTGRES_PASSWORD` | DIFFERENT (48 vs 40 chars) — stale |

**Three of the four are live database passwords, not historical artefacts.** An earlier draft of
this subsection reported only the `sales-db-password` match and characterised the file as "neither
wholly useless nor wholly current"; that was measured against two keys with the wrong live key
names and understated the exposure by a factor of three. The corrected count is the one above. The
practical consequence is unchanged but sharper: this file is a plaintext store of **three
currently-valid production database credentials** plus one stale one, and it is exactly the
duplication §14.2 exists to prevent.

`check-secrets-exposure.sh` does **not** catch it — that
script checks *tracked* files and file modes, and this file is untracked and correctly `0600`.
It was found by enumerating `ao-secrets/` and comparing against the units that read it, not by
running the guard. The guard's blind spot is itself the finding: **rule 7 compliance is only as
good as the tracked-file assumption**, and a `0600` copy of three live database passwords plus
one stale one sits outside both Git and the units.

Its origin is not recorded anywhere in the repository — no quadlet unit, script or section file
references `legacy-alwayson-folder`. Given the name and the fact that it holds exactly one
password for each of the four DB domains, it appears to be a pre-wallet-folder consolidation
artefact: a moment when the credential layout was one file instead of one folder per domain.

**Deleting the legacy file is not performed here.** Removing it is a deletion of
secret-classified material, which is outside this specification's authority (brief
stop conditions). **Operator decision requested** — recommend deletion. The
reasoning matters and cuts the other way from a first reading: because three of
the four values are **currently valid**, deleting the file removes a real
plaintext store of live credentials, and it loses nothing operationally, because
the wallet remains the system of record and the live env files are re-fetched at
every start (the scope paragraph below). Deleting is therefore strictly safer
than keeping. Rotation is **not** required by the presence of the
file, because nothing outside it uses those values and they were never committed to Git, a
backup set, or an external network; rotation becomes required only if the operator judges the
host's local user account to be untrusted.

**Status: recorded, awaiting operator ratification.** This subsection exists because
§14.1 mandates Podman secrets or systemd credentials while every implemented path is a
wallet-materialised `0600` env file. The deviation is real, and it is documented here rather
than silently left in place. **It is not self-approving** — README §4.1 rule 14 reserves the
decision to the operator.

**Scope of the deviation.** Secret *storage* is the KDE Wallet, encrypted at rest. Secret
*delivery* is a `0600` env file under `%h/.local/share/ao-secrets/`, refreshed at start-up by
`fetch-kwallet-secret.sh`. Env files are **delivery copies, not stores**: the wallet is the
only system of record, and every file is rewritten from the wallet on each refresh, so losing
one costs a re-fetch, not a credential.

The **first draft of this paragraph named only four consumers** —
`ao-mastodon-db`, `ao-sales-db`, `ao-webodm-db` and `ao-fabrication-db`. That understated the
deviation by roughly a factor of three. Measured 2026-10-04, the delivery set is **eight
secret-bearing env files**, not four:

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

Plus `mastodon.env` (1041 bytes, mode `0640`, wallet entry `ao-mastodon/mastodon-env`,
byte-identical to the file per §14.1.3), consumed by `ao-mastodon-web`, `-streaming` and
`-sidekiq` and by the repair `ExecStartPost`. **The operator is therefore being asked to
ratify a deviation covering nine files across fifteen units, not four files across four
units.** The four-database framing was inherited from the SEC-01 acceptance criterion, which
names only mastodon-db, sales-db and webodm-db; the criterion is narrower than the
implementation, and the implementation is what needs approving.

**A mode exception inside that set, stated precisely.** `mastodon.env` is `0640`, not `0600`,
because `ao-wallet-bridge.sh` adds the ACL that lets `ao-sales` read it. Measured:

    $ getfacl -p ~/.local/share/ao-secrets/mastodon.env
    user::rw-  user:ao-sales:r--  group::---  mask::r--  other::---

The other eight env files are `0600 scottw:scottw` with no ACL. So "all delivery copies are
`0600`" is true of eight files and false of the ninth; §14.1.6 previously said so uniformly.

**Why the mandated mechanism is not used.** Podman secrets (`podman secret ls` returns an
empty list; Podman 5.7.0) would have to be populated *from* the wallet by a root or
podman-owned helper at start-up, which relocates the plaintext to a second long-lived store
rather than removing it, and `Secret=` cannot be populated from a login-gated wallet at all.
Systemd `LoadCredential=` is available to the systemd user manager but is not usable by
Podman-managed containers, which take `EnvironmentFile=`/`Secret=`, not systemd credentials.

**Compensating controls actually in place** (each verified, not asserted):

| Control | Evidence |
|---|---|
| Value lives only in the wallet | `fetch_secret` reads via D-Bus `readPassword` and prints nothing; the value is only ever written to the output file |
| Files are `0600`, created under `umask 077` | `umask 077` at `fetch-kwallet-secret.sh` line 14; `chmod 600 "$OUTPUT_FILE"` at end of script |
| Write is atomic, so a partial file is never read | `{ … } > "$OUTPUT_FILE.tmp"` then `mv` then `chmod 600`; `trap cleanup_tmp EXIT` removes a stranded `.tmp` |
| Consumer ACL is narrow, not world-readable | `mastodon.env` ACL is `user:ao-sales:r--`, `group::---`, `other::---`, set by `ao-wallet-bridge.sh` |
| No plaintext copy in the repository | `.gitignore:1` is `secrets/`; env files live under `%h/.local/share/ao-secrets/`, outside the worktree |
| Exposure is checked in CI | `check-secrets-exposure.sh` carries the three rule-7 checks described in §14.1.1 |

**Env-file lifetime and shred-on-exit — stated precisely, because §14.1.1 calls a file here a
plaintext duplicate.** The `0600` env files are **not** shredded on exit; they persist for the
lifetime of the unit and are overwritten in place at the next start. Only the transient `.tmp`
is removed, and only with `rm -f`, not `shred`. The scripts that *do* shred are
`scripts/mastodon/post.sh` (`trap 'shred -u "$ENV"' EXIT`) and `scripts/ledger/sign-manifest.sh`.
So the accurate statement is: **delivery copies persist on disk at `0600` between start-ups and
are replaced, not shredded.** This is the accepted residual exposure of the deviation and is
why the wallet — not these files — is designated the system of record.

**Two stale facts corrected while writing this subsection.**

1. §19 ST-30 records `~/secrets/fabrication-db.env` as a `0600` file. **No such file exists.**
   `find ~/secrets -name '*fabrication-db*'` returns nothing; the live file is
   `~/.local/share/ao-secrets/fabrication-db.env` (`-rw-------`, 100 bytes), matching the
   single-env-root rule in §14.1.2. ST-30's text is stale and should not be read as evidence
   of a second delivery path. The §19 compiler should correct ST-30; it is not a
   file this specification owns.
2. `~/secrets/mastodon.env` is a **dangling symlink** to
   `/ALWAYSON/secrets/mastodon/mastodon.env`, which does not exist
   (`ls: cannot access …: No such file or directory`). It is inert, because
   `quadlet/sales/ao-sales-db.container` and the Mastodon units read
   `EnvironmentFile=%h/.local/share/ao-secrets/…`, not `~/secrets/`. Reported, **not removed** —
   deleting files is outside this specification's authority and it may belong to another
   subsystem.

**Migration remains available if the operator prefers it.** The pinned Postgres image
(`postgres@sha256:d74eeac9a…`) calls `file_env 'POSTGRES_PASSWORD'` at line 235 of
`/usr/local/bin/docker-entrypoint.sh`, so `POSTGRES_PASSWORD_FILE` **is** honoured; a Podman
`Secret=` mounted at `/run/secrets/…` plus `Environment=POSTGRES_PASSWORD_FILE=/run/secrets/…`
would satisfy §14.1 for the database services. It has not been applied: it changes live unit
definitions and live credential delivery, and therefore stops for operator approval.

### 14.1.7 `payment.env` is a stale delivery copy, and §19 ST-12's "runs with no DSN" is wrong

> **Partly resolved 2026-10-05 — read this before acting on the text below.** The `ao-payment`
> folder **now exists with all four entries present**, and `payment.env` has been successfully
> re-fetched (four keys, mtime `2026-10-04 18:38`, no longer the 2026-09-30 file described
> here). **The fault is NOT closed, because the running adapter has never restarted.** It has
> been running since 2026-10-01 15:08:41 and holds only `PAYMENT_DSN`. The delivery copy on disk
> is correct; the process in memory is not. See §14.1.7.2.

Found 2026-10-04. **The payment adapter has been running since 2026-10-01 15:08 with an env
file whose wallet source does not exist.** This is a liveness and correctness fault, not a
documentation drift, and it is in this section because the fault is in secret *delivery*.

The measured chain, each step a command and its output:

**1. The wallet folder the fetcher needs does not exist.**

    $ python3 … folderList(h,'ao-secret-reader')
    ao-payment exists: False
    ao-archive exists: False

`wallet_folder_for` maps `payment-db-password`, `payment-paypal-webhook-id`,
`payment-paypal-webhook-secret` and `payment-coinbase-webhook-secret` to `ao-payment`
(`fetch-kwallet-secret.sh` line 90). §19 ST-12 already recorded that "the four `ao-payment`
wallet entries do not exist yet". Confirmed: the folder is absent, not merely empty.

**2. The env file therefore cannot be refreshed, and has not been.**

    $ stat -c '%n mtime=%y' ~/.local/share/ao-secrets/payment.env
    payment.env mtime=2026-09-30 23:18:29
    $ systemctl --user show ao-ingress-payment.service -p ActiveEnterTimestamp
    ActiveEnterTimestamp=Thu 2026-10-01 15:08:41 PDT 2026

**The file is older than the process reading it by roughly sixteen hours.** Every start since
2026-10-01 has consumed a file frozen at 2026-09-30.

**3. The fetch failure is silenced, so nothing reports it.**

    $ grep -rn 'ExecStartPre=-' quadlet/
    quadlet/payment/ao-ingress-payment.container:63:ExecStartPre=-…fetch-kwallet-secret.sh … payment-credentials

The leading `-` makes systemd ignore the exit status. `fetch_secret` exits 2
("no wallet folder mapped") and 3 ("wallet entry unavailable"), but `ExecStartPre=-` discards
both. Consequently:

    $ journalctl --user -u ao-ingress-payment.service --since 2026-10-01 \
        | grep -cE 'wallet entry unavailable|no wallet folder mapped'
    0

**Zero** occurrences. The failure is real, recurring on every start, and produces no journal
entry at all. This is the same class of fault as the 2026-10-01 grafana/metabase outage
recorded in §14.1.4 — a failed fetch — except that there the fetch was loud and the units
crashed visibly, and here it is silent and the unit runs on stale material. The `-` prefix
converts a loud failure into a silent one.

**4. The stale file is not inert, and §19 ST-12's claim is false.**

ST-12 states the adapter "runs with no DSN and no webhook secret and cannot accept a payment."
Measured, with the password reduced to a length and a sha256 prefix:

    $ sed -n 's|^PAYMENT_DSN=postgresql://[^:]*:\([^@]*\)@.*|\1|p' payment.env | wc -c
    49                                     # 48 chars + newline
    $ sed -n 's|^PAYMENT_DSN=postgresql://[^:]*:\([^@]*\)@.*|\1|p' payment.env \
        | tr -d '\n' | sha256sum | cut -c1-12
    03521083973b

That prefix is **identical to the live `sales-db-password`** recorded in §14.1.6
(`03521083973b`, 48 chars) — the same value the orphaned `legacy-alwayson-folder.env` carries.
So `payment.env` holds a **currently-valid sales database password**, embedded in a DSN as
`postgresql://sales_migration_role:<password>@127.0.0.1:15432/salesdb`.

**The DSN is present and usable. ST-12's "runs with no DSN" is incorrect**, and the
conclusion drawn from it — that the adapter "cannot accept a payment" — rests on a measurement
that does not hold. The three webhook secret lines are genuinely absent (the file has one key,
`PAYMENT_DSN`), so the adapter has a database connection but no webhook verification material.
The correct statement is narrower: **it holds a live sales-DB credential and no webhook
secrets**, which is a different and less safe situation than ST-12 describes, because the
DSN alone grants database access.

**5. `check-secrets-exposure.sh` cannot see it**, for the same reason it missed
`legacy-alwayson-folder.env`: the file is untracked and correctly `0600`, and the guard's
`$secret_key_re` does not match `PAYMENT_DSN` — a deliberate carve-out at
`check-secrets-exposure.sh` line 79, whose comment says `payment.env` "carries a DSN, not a key
name". The carve-out was written so a healthy DSN file would not be flagged as leftover temp
debris; the side effect is that the one file carrying a real password in DSN form is
structurally invisible to the guard.

**Operator decision requested. Not changed here**, because it touches payment
credentials and a live running service (brief stop conditions; README §4.1 rules
12 and 14).

1. **Create the four `ao-payment` wallet entries**, then restart `ao-ingress-payment`. This is
   ST-12's own outstanding action and it also fixes the staleness. Recommended first.
2. **Decide whether the `-` prefix on line 63 should stay.** It was presumably added so a
   missing-wallet fetch would not block the unit — but the result is a unit that runs
   indefinitely on an env file it can never refresh, with no log line. If it stays, the
   staleness needs a separate check; if it goes, a locked wallet takes the unit down with it.
   Either is defensible, but the current state documents neither.
3. **Note for §19**: ST-12's "runs with no DSN" needs correcting, because the file does carry
   a DSN. The row belongs to the §19 compiler, so this is raised as a proposal, not an edit.

Cross-group: the *credential content* of this is PAY territory and the ST-12 row is the
compiler's. The *delivery-mechanism* fault — silent fetch failure on a `0600` stale copy — is
SEC's and is what §14.1.7 records.

#### 14.1.7.1 Re-verification, 2026-10-04 (fourth pass)

Every claim in this subsection is re-measured from its source rather than inherited
from an earlier pass. The figures in §14.1.4, §14.1.6 and §14.1.7 were written by
earlier passes and are the kind of figure that goes stale, so **a re-verification
must re-measure from the live system and not restate a prior number.**

    $ systemctl --user show ao-ingress-payment.service -p ActiveEnterTimestamp -p ExecStartPre
    ActiveEnterTimestamp=Thu 2026-10-01 15:08:41 PDT 2026
    ExecStartPre={ path=/ALWAYSON/scripts/operations/fetch-kwallet-secret.sh ;
                   argv[]=… %h/.local/share/ao-secrets/payment.env payment-credentials ;
                   ignore_errors=yes ; … }
    $ stat -c '%n %y' ~/.local/share/ao-secrets/payment.env
    payment.env 2026-09-30 23:18:29.786526608 -0700

`ignore_errors=yes` is systemd's own rendering of the `-` prefix, so the silencing is confirmed
from the unit's runtime state and not only from the quadlet source. The file is still ~16h older
than the process reading it, and the unit is still `active`.

    $ python3 … hasFolder(h,'sec-verify') for each ao-* folder
    ao-payment False   ao-archive False
    ao-sales True  ao-admin True  ao-mastodon True  ao-mapping True
    ao-fabrication True  ao-sim-vehicle True  ao-sim-fabrication True

Seven `ao-*` folders, `ao-payment` and `ao-archive` absent — unchanged. §14.1.4's count also
re-verified: `folderList` returned **14274 raw rows / 18 unique folders** (7 are `ao-*`), and
`ao-*` entries total **37**; with `Passwords` (2) that is the **39** §14.1.4 states.

The `payment.env` DSN re-measured to the same conclusion, without printing the value:

    $ sed -n 's|^PAYMENT_DSN=postgresql://[^:]*:\([^@]*\)@.*|\1|p' payment.env | wc -c
    49
    $ … | tr -d '\n' | sha256sum | cut -c1-12
    03521083973b
    $ cut -d= -f1 ~/.local/share/ao-secrets/payment.env
    PAYMENT_DSN

`PAYMENT_DSN` is the file's **only** key — the three webhook secrets are genuinely absent, so
§14.1.7 step 4's narrower statement still holds. The role is `sales_migration_role`, a
non-secret field. §14.1.6's legacy-file table also reproduced exactly, `03521083973b` /
`6d174927d250` / `f0d6bb4481fd` SAME and `8c3319896c87` vs `4f090748460c` DIFFERENT.

**A count of zero from a parser must be checked against an independent count
before it is written down.** The pattern `^([A-Za-z0-9_]+)=`, used to enumerate the
legacy file's keys, returns **zero pairs** — because three of the four key names
contain hyphens (`mastodon-db-password`), and the hyphen was missing from the
character class. Taken at face value that reads as "the file is now empty", which
would be a false and alarming claim about a file holding live credentials. The
correct pattern is `^([A-Za-z0-9_-]+)=`. The lesson is narrower than "be careful
with regexes": `wc -l` on the same file answered 4 immediately. **A parser that
reports nothing must be shown to be able to report something before its zero is
recorded as a security improvement.**

**Two further traps, both mine to record.**

1. **`folderList` is unusable as a count.** It returned 14022 rows on one call and 14274 on the
   next, minutes apart, on an unchanged wallet. §14.1.4 already says to de-duplicate; the
   stronger statement is that the row count is not even stable, so only the de-duplicated set is
   meaningful. Use `hasFolder` for existence questions — it is a direct boolean and is what
   `kwallet-provision.sh:42` itself uses.
2. **`entryList` returns `as`, `entriesList` returns `a{sv}`** — two different methods with
   near-identical names. Calling `int()` on the first raises `TypeError`, because it is a list,
   not a number. §14.1.4's signature table documents both correctly; this is a note that the
   names are easy to confuse when scripting an audit.

No credential, file mode, unit or wallet entry was changed by this re-measurement.
The fault in §14.1.7 is **still live and still unreported by any service**, and the
operator decisions in this subsection are still outstanding.

#### 14.1.7.2 Current state 2026-10-05: provisioned and fetched, but the running adapter is still stale

Re-measured from scratch. §14.1.7's finding was that the wallet source did not exist. **That
specific cause is gone**; the operational fault it produced is **still live**.

**Step 1 — the wallet side is now complete.**

    hasFolder(kdewallet, 'ao-payment', app)   -> True      (was False on 2026-10-04)
    hasEntry ao-payment/payment-db-password             -> True
    hasEntry ao-payment/payment-paypal-webhook-id       -> True
    hasEntry ao-payment/payment-paypal-webhook-secret   -> True
    hasEntry ao-payment/payment-coinbase-webhook-secret -> True
    control: hasFolder 'zzz-does-not-exist-9999'        -> False

**Step 2 — the delivery copy is now complete and fresh.**

    $ sed 's/=.*/=/' ~/.local/share/ao-secrets/payment.env | grep -v '^$'
    PAYMENT_DSN=  PAYPAL_WEBHOOK_ID=  PAYPAL_WEBHOOK_SECRET=  COINBASE_WEBHOOK_SECRET=
    $ stat -c '%n %y %s' ~/.local/share/ao-secrets/payment.env
    payment.env  2026-10-04 18:38:34  306

Four keys, not one. This is ST-12's outstanding action, completed by someone other than this
session — **no commit in this repository provisions a wallet folder**, so it was done on the host
directly and cannot be attributed to a session. The `payment-credentials` branch of
`fetch-kwallet-secret.sh` (line 152) writes all four keys in one pass, so a successful run of it
is exactly what this output looks like.

**Step 3 — the running adapter has none of that.** This is the part that matters:

    $ podman inspect ao-ingress-payment --format '{{.State.StartedAt}}'
    2026-10-01 15:08:41.645971245 -0700 PDT
    $ podman inspect ao-ingress-payment --format '{{range .Config.Env}}{{println .}}{{end}}' \
        | sed 's/=.*/=/' | sort
    container=  GPG_KEY=  HOME=  HOSTNAME=  PATH=  PAYMENT_DSN=  PYTHON_SHA256=  PYTHON_VERSION=

**The container holds `PAYMENT_DSN` and none of the three webhook keys**, because
`--env-file` was read at container creation on 2026-10-01, when the file had one key. A
successful re-fetch at 18:38 on 2026-10-04 rewrote the file and changed nothing about the
running container. `Config.Env` is a creation-time snapshot, not a live view of the file.

**So the correct statement of the fault has changed, and the old one is now wrong:**

| | 2026-10-04 (§14.1.7) | 2026-10-05 (now) |
|---|---|---|
| `ao-payment` folder | absent | **present, 4/4 entries** |
| `payment.env` on disk | 1 key, frozen 2026-09-30 | **4 keys, 2026-10-04 18:38** |
| Running adapter's env | `PAYMENT_DSN` only | **`PAYMENT_DSN` only — unchanged** |
| Root cause | fetch impossible | **process never restarted after a successful fetch** |

This is a *new* failure mode from the one §14.1.7 diagnosed, and it is arguably worse: the
on-disk evidence now looks healthy, so a reviewer checking files rather than processes concludes
everything is fixed. The `-` ignore-failure prefix on `ExecStartPre` is what let the original
fault be invisible, and it is still in place — but it is no longer the active cause.

**Operator action required — one restart.** `systemctl --user restart ao-ingress-payment` is
the whole fix; the delivery copy is already correct. **Not performed here**: it is a
restart of a live payment adapter, and the brief's stop conditions name payments explicitly.
Verified absent: no restart has happened since the fetch, per `StartedAt` above.

**A tool that does not exist on the host cannot be used to establish a fact.** An
earlier pass probed folder existence with a CLI
(`kwallet-d6 --folder … --read-password`) that **does not exist on this host** — rc 127. The
shell discarded the failure, so the command "succeeded" and produced an empty string whose
sha256 is `e3b0c442…` (sha256 of the empty input). Run against all nine folder names it
reported every one as "absent", which would have made me *re*-report the already-fixed finding
with fresh evidence and a confident tone. The class of bug is not "check your tools": it is
that a missing binary plus an unguarded pipeline is indistinguishable from a clean negative
result unless you check the exit code and calibrate the probe against a known-positive and a
known-negative input. The `hasFolder` control test is what caught it here.

## 14.2 Credential rotation, revocation and recovery

This subsection exists because §14.1.1 requires rotation, revocation, expiration and recovery
to be documented before production use, and none of it was documented in §14, §16 or §17.
`docs/runbooks/secrets.md` carries a three-line "Rotation" note, but it is stale: it describes
per-service-account homes (`alwayson-mapping`) and a manual copy-out step, both superseded by
§13.2 (all services run under the operator's account) and by the wallet-materialised flow.
**This subsection is the procedure; the runbook's summary is the non-authoritative copy.**

### 14.2.1 Rotation

Rotation is *write the new value to the wallet, then let the fetchers redistribute it*. The
fetchers run as `ExecStartPre`, so the file is rewritten from the wallet on the next start —
rotation is completed by restarting the consuming unit, not by copying a file.

| Step | Action | Verify |
|---|---|---|
| 1 | Operator writes the new value to the owning `ao-*` folder via `scripts/ops/kwallet-provision.sh put` | `hasEntry` true on `org.kde.kwalletd6` |
| 2 | For a **database** password, change the role **first**, so the wallet and the live role never disagree: `ALTER ROLE <role> PASSWORD …` | role login succeeds |
| 3 | Restart the consuming unit; `ExecStartPre` re-fetches and atomically rewrites the `0600` file | `systemctl --user is-active <unit>`; file mtime advanced |
| 4 | Confirm no other copy exists | `find ~/secrets ~/.local/share/ao-secrets -newer <marker>`; `check-secrets-exposure.sh` |

**Never** rotate by editing an env file directly. The file is overwritten at the next start, so
an edit is silently reverted and, worse, leaves the wallet and the running service
disagreeing. **Never** regenerate `mastodon.env` via `genenv` to rotate: it refuses to run when
the file exists and would otherwise mint new `SECRET_KEY_BASE` / `OTP_SECRET`, invalidate every
session, and write `LOCAL_DOMAIN=localhost` (§14.1.3).

Database password rotation ordering matters because `pg_hba` trusts `127.0.0.1` for these
roles: TCP auth can fail while the socket still appears to work. Confirm with a TCP client, not
a socket, after changing a role password.

**Verify the wallet and the file agree *after* the restart, not just that the file changed.**
Step 3's "file mtime advanced" is a weak check. §14.1.3.2 supplies a real, live example of a
check that passes while the service is wrong — and, importantly, this is *not* the wallet-vs-file
divergence the first pass of §14.1.3 alleged (that claim is retracted above): `mastodon.env` was
materialised correctly, and the fault is that `mastodon-streaming` captured the **previous**
file content because it was created 1.2s before the bridge's write completed. The mtime was
legitimate and recent; the consumer still held stale values. The pass condition is therefore
two-part, and the second half is the one that catches this:

    # (a) key names — the file is the shape the consumer expects
    $ sed 's/=.*/=/' ~/.local/share/ao-secrets/<file>.env | sort > /tmp/fk
    # … read the wallet entry the same way, strip values, sort …
    $ diff /tmp/fk /tmp/wk && echo 'key names identical'
    # then compare full-content sha256 — equality is the pass condition

    # (b) THE CHECK THAT MATTERS MOST: what the RUNNING process actually holds.
    $ podman inspect <container> --format '{{range .Config.Env}}{{println .}}{{end}}' \
        | sed 's/=.*/=/' | sort
    # Compare against the file's key list. Config.Env is a creation-time snapshot,
    # so a correct file beside a never-restarted container is still a stale service.

A rotation is complete when the wallet and every delivered copy hash equal **and** the consuming
unit has restarted **and** that container's `Config.Env` reflects the new file. "The file
changed" is not sufficient, neither is "the unit is active", and — per §14.1.7.2 — neither is
"the file on disk is correct".

### 14.2.2 Revocation

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

### 14.2.3 Expiration

No credential on this host has an enforced expiry. Passwords persist until rotated by the
operator. Tokens are the exception and are pinned deliberately: the OpenClaw bridge token is
created with `expires_in: nil`, because Doorkeeper reads `expires_in: 0` as *already expired*
(§14.1.4). **A non-expiring token raises the rotation obligation** — it is a standing item on
the break-glass list in §14.2.5, not a solved one.

### 14.2.4 Wallet backup and restore

**Gap, stated rather than papered over: the wallet is not in the backup set.** The restic
snapshot in `scripts/backup/restic-run.sh` line 30 covers `$AO_ROOT/config`, `artifacts`,
`backups/postgres`, and the `data/*` trees. `~/.local/share/kwalletd/` is **not** on that
list, and it cannot be: a `.kwl` file is encrypted against `kdewallet.salt`, so a snapshot
without the salt is unrestorable, and restoring a `.kwl` alone would not restore the
credential *values* the services consume.

Consequently the current recovery posture is: **the wallet is the single point of failure for
every credential on this host, and it has no automated backup.** Adding one is a backup-data
change and is flagged for the operator rather than applied.

**Restore procedure, for the operator to run interactively** (wallet must be unlocked; never
script it, and never let a value transit a shell argument or a log):

1. Restore the host or the user account. If `~/.local/share/kwalletd/kdewallet.kwl` is
   present and valid, the wallet opens with the Plasma login — verify with `wallets()` returning
   `as 1 "kdewallet"` and `open()` returning a handle ≥ 0.
2. If the wallet file is gone or will not open, the credentials must be re-provisioned from
   their other sources of record, or **rotated**. Rotation is always available and is the
   correct fallback: a database role password is set by `ALTER ROLE`, a token by re-minting
   (§14.1.5), an admin password by `kwallet-provision.sh put`. There is no path that recovers
   an old value, which is a security property, not an outage.
3. After any re-provisioning, run `check-secrets-exposure.sh` and restart the consumers.

**Procedure that is itself inside the backup set.** A credential-recovery runbook that lives
only in an unbacked file does not satisfy §14.2. The procedure above is written into
`agents/COORDINATION (README UPDATES)/14-secrets-and-service-identity/section.md`, which **is** covered by the
restic snapshot via `$AO_ROOT/config` and the repository, so the procedure survives a restore
even though the secrets do not. The deliberate split is: **the procedure is backed up; the
secrets are rotated, never restored.**

### 14.2.5 Break-glass order for the operator

In order, stopping at the first step that resolves the fault. Steps 1–4 are non-destructive;
step 5 changes a live credential and is the operator's alone. Step 2 was added 2026-10-04
after §14.1.7 found a delivery copy that had gone stale without any fault being reported.

1. **Is it the wallet being locked?** Check `isOpen(handle)` — not `busctl --user list |
   grep kwalletd6`, which returns true the instant kwalletd is D-Bus-activated and therefore
   never waits. A `0-byte` `.tmp` under `ao-secrets/` is the forensic signature of a locked
   wallet (§14.1.4). Fix: unlock the wallet from the Plasma session and restart the unit.
2. **Is a delivery copy older than the process reading it?** Compare the two mtimes before
   anything else, because it is the cheapest check and it catches the silent failure mode:

       $ stat -c '%y %n' %h/.local/share/ao-secrets/*.env
       $ systemctl --user show <unit> -p ActiveEnterTimestamp

   An env file older than the unit's start timestamp means the `ExecStartPre` did not rewrite
   it. §14.1.7 documents this happening silently for sixteen hours on `ao-ingress-payment`
   because its `ExecStartPre` carries the `-` ignore-failure prefix. **A fetch that fails on a
   `-`-prefixed `ExecStartPre` leaves no journal entry**, so mtime-versus-start-timestamp is
   the only reliable signal that a delivery copy has gone stale.

   **The converse now needs its own check, added 2026-10-05.** A file *newer* than the
   process is not proof of health — it is the signature of a completed refresh that no running
   service has picked up. The mtime ordering in the table above treats "file older than
   process" as the fault; it misses the newer case entirely, and that is exactly the state
   `ao-ingress-payment` is in right now (§14.1.7.2): a correct four-key file from 2026-10-04
   18:38 behind a container created 2026-10-01 15:08 that still holds one key. **For any
   `--env-file` consumer, compare the file against the process's actual environment**, not the
   file against its own mtime:

       $ podman inspect <container> --format '{{range .Config.Env}}{{println .}}{{end}}' \
           | sed 's/=.*/=/' | sort          # key names only
       $ podman inspect <container> --format '{{.State.StartedAt}}'

   `Config.Env` is a creation-time snapshot. A key present in the file but absent from
   `Config.Env` means the consumer predates the refresh and needs a restart — and a restart is
   the operator's call, not a step to take while diagnosing.
3. **Is the unit simply not started?** These units are `WantedBy=graphical-session.target` and
   are *expected* to be down before Plasma login. That is the login-gated design, not a fault.
4. **Is the entry present?** `hasEntry` on the owning folder via `kwallet-provision.sh get` /
   `fetch_secret`; a missing entry is re-provisioned by the operator with a **new** value.
5. **Rotate, do not restore.** If a value is suspected exposed, or unrecoverable, write a new
   value to the owning `ao-*` folder and restart (§14.2.1). This is the only path for a lost
   wallet, and it does not require the old value.

**Never**, in any break-glass step: print a value to a terminal, log, ticket or chat; restore
an env file from a backup; copy a value between hosts or folders outside its owning `ao-*`
domain; or add a compensating `Environment=` line to a unit to work around a missing fetch.
The last one is the failure mode that turns a five-minute locked wallet into a permanent
plaintext secret in a tracked file.

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
transaction/state reference written back to PostgreSQL. Metabase reports and
Grafana dashboards read the resulting approved projections; neither creates the
sale.

**CONFIRMED SALE PDF OUTPUT.** The same intake path carries the other direction: once a
sale is confirmed and the Corda transaction/state reference exists, the confirmed sale is
emitted as a **PDF** into the intake tree. That PDF is the outward-facing artefact of a
confirmed sale, as opposed to the request PDF, which is an inquiry and never becomes one.
Both are hash-captured into `manifests/`, and the request PDF is preserved in `archive/`
so the two are never confused.

## 15.2 Community and AI Controls

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

Bridge state re-verified 2026-10-03 (evidence for COMM-04):

- **Auth half.** The wallet-held bot token is valid. `verify_credentials` returns
  HTTP 200 for `acct=bot, id=117363090433277638` against
  `https://mastodon.300x3.com`. The token value was never printed — only its length
  (43 characters) was measured.
- **Script identity.** The unit runs `/ALWAYSON/scripts/mastodon/mastodon-openclaw-bridge.py`.
  `~/.local/bin/mastodon-openclaw-bridge.py` is a byte-identical copy, not a symlink —
  `sha256` is `486e7472…99c19` for both. Editing the `/ALWAYSON` copy is therefore *not*
  sufficient to change live behaviour until the unit is restarted; this is the same
  copy-not-symlink trap as Quadlets.
- **Operator decision honoured.** Line 281 of the bridge posts with
  `'visibility': 'public'` and retains the `@author` mention prefix, matching the
  2026-10-01 operator decision. Confirmed in *both* copies above, so no stale
  `unlisted` variant is hiding in the deployed file.
- **Cursor is current but idle.** `~/.openclaw/mastodon-bridge-state.json` holds
  `lastNotificationId: "7"`, while `max(notifications.id)` is 8. The two
  notifications (ids 7 and 8, both `follow` from `300x3@mastodon.social`) are not
  `mention`/`status` types, so the bridge correctly ignores them; the state file is
  simply not rewritten for skipped types. Last write was 2026-10-02 00:27 UTC, ~49.9 h
  before measurement. This is expected idleness, **not** the stale-cursor fault
  described in COMM-04 — that earlier fault (cursor ahead of the newest id) is fixed
  and the bridge's own recovery log line is present in the journal.
- **No 401 crash-loop regression.** `systemctl --user status` shows the unit
  `active (running) since Thu 2026-10-01 18:50:55 PDT`, with no restart loop
  (re-confirmed 2026-10-04, 2 days uptime, `Main PID: 788109`, memory 14.1 M,
  peak 19.8 M, CPU 47.1 s).

## 15.3 Local 300X3 Mastodon Deployment

The 300X3 Mastodon instance (Mastodon 4.3.7, containerized in the authoritative
`ao-sales` rootless Podman store) is publicly federated at
**`https://mastodon.300x3.com`**. The main storefront remains on
`https://300x3.com` and `https://www.300x3.com`; it is not routed to Mastodon.
Operators use Konqueror and OpenClaw on the desktop. 

Architecture requirements and verified state:

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
- Public actor and WebFinger endpoints were verified at
  `https://mastodon.300x3.com/actor` and
  `https://mastodon.300x3.com/.well-known/webfinger`.
- The tunnel currently uses HTTP/2 transport because QUIC stream timeouts were
  observed on this host. Local and public health checks returned HTTP 200.
- **Open registration is closed.** Measured 2026-10-03: `/api/v1/instance` reports
  `registrations=false, approval_required=false`, and no `registrations` row exists in the
  `settings` table. There is no approval queue and no pending registration. Account
  creation on this instance is an operator action performed directly in the admin UI.
  (An earlier revision of this bullet claimed registration was "open with the approval
  gate"; that was contradicted by both the API and the database on 2026-10-03 and has
  been corrected here.)
- No passwords, OAuth secrets, API keys, tunnel credentials, or access tokens
  are committed to Git or recorded in this README.

## 15.4 Federation Publication of the Local 300X3 Instance

**Scope.** Join the fediverse as the 300X3 instance so that public posts from the
local deployment appear on external Mastodon servers, including `mastodon.social`.

Federation is a mutual, inbound-and-outbound protocol: remote servers (including
`mastodon.social`) must reach this instance over the public internet using HTTPS,
and this instance must be able to deliver outbound activity to remote inboxes. Federation
is publicly reachable at `https://mastodon.300x3.com`; the
main storefront remains on the apex/`www` hostnames and is not routed to Mastodon.

### 15.4.1 Architecture Requirements

WebFinger and `/api/v1/instance` both report `mastodon.300x3.com`, while `300x3.com`
serves the static storefront. The `scottw` operator account runs the 5 Mastodon containers
directly; there is no second Mastodon store and no separate service account on this host.
Open configuration drift against these values is tracked in §19.1.

| Area | Architecture requirement |
|---|---|
| Public instance domain | Dedicated `mastodon.300x3.com`; canonical handles are `user@mastodon.300x3.com`. The storefront hostnames remain separate. |
| Storefront preservation | `300x3.com` and `www.300x3.com` retain the filedn static-site redirect; Mastodon is not deployed under a `/mastodon` subpath. |
| TLS | Required at the public edge; Cloudflare terminates TLS for `mastodon.300x3.com`. |
| Inbound reachability | Cloudflare Tunnel connector `cloudflared-alwayson.service` routes only the dedicated hostname to `127.0.0.1:3000`. |
| Outbound reachability | `mastodon-sidekiq` performs federation delivery over HTTPS/443 directly from `ao-sales`, which is `Internal=false`. Community publication is carried inside `ao-sales`; there is no separate egress network for it. Database, Redis, and streaming stay on `ao-sales` and are never attached to an egress network. |
| Isolation | `ao-sales` is `Internal=false` to permit ActivityPub delivery, and carries no attachment or route to any other `ao-*` domain. No database, Redis, or raw origin listener is publicly exposed. |
| Secrets | Tunnel credentials and API keys remain in protected runtime secret storage; never in Git or this README. |
| Operator duties | Registration approval, moderation, reports, and blocklists remain operator responsibilities. |
| Service-account placement | The 5 Mastodon containers run under the `scottw` operator account in the single `ao-sales` rootless store and systemd user manager. No separate service account exists on this host, so no duplicate Mastodon instance or store can exist. |

### 15.4.2 Domain and Mastodon Identity Configuration

The authoritative runtime env (`LOCAL_DOMAIN=mastodon.300x3.com`) as re-measured
2026-10-03, from `~/.local/share/ao-secrets/mastodon.env`, non-secret keys only:

```text
LOCAL_DOMAIN=mastodon.300x3.com
RAILS_FORCE_SSL=true
LOCAL_HTTPS=true
ALTERNATE_DOMAINS=localhost,localhost:3000,127.0.0.1,127.0.0.1:3000
```

> **Correction 2026-10-03 (COMM session).** An earlier revision of this section stated
> `LOCAL_HTTPS=false` and `RAILS_FORCE_SSL=false`, applied "2026-09-24". That was wrong —
> both keys have always been `true` in the runtime env, in the generator
> `scripts/operations/fetch-mastodon-env.sh` (lines 42–43) and in
> `config/mastodon/mastodon.env.example` (lines 36–37). The measurement below proves
> the claim was never needed: upstream hardcodes `config.force_ssl = true`
> (`config/environments/production.rb`) and `https = Rails.env.production?`
> (`config/initializers/1_hosts.rb`), so in production Rails always emits absolute
> `https://` URLs and always redirects plain HTTP. Re-measured 2026-10-03:

```console
$ curl -s -o /dev/null -w '%{http_code} redirect=%{redirect_url}\n' http://127.0.0.1:3000/
301 redirect=https://127.0.0.1:3000/
```

The local UI is therefore served over TLS by the loopback proxy (§9.2.1), not by
relaxing Mastodon. Leaving the keys `true` keeps the env self-describing and matches
what the generator actually writes.

Registration state is also **not** as previously recorded here. Measured
2026-10-03 against the live instance:

```console
$ curl -s https://mastodon.300x3.com/api/v1/instance | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('registrations'), d.get('approval_required'))"
False False
```

Registration is **closed** (`registrations` absent from the `settings` table, which
Mastodon treats as disabled). There is therefore no approval queue to operate. See
COMM-03 in §19.1.

- WebFinger and actor JSON resolve through the public federation hostname.
- The main storefront remains on `300x3.com` / `www.300x3.com`.
- No `/mastodon` path deployment is used; the dedicated hostname provides the
  root paths required by ActivityPub.

### 15.4.3 Edge, TLS, and Network Path

The edge is **Cloudflare Tunnel**, not workstation nginx with Let's Encrypt. Edge TLS is
terminated by Cloudflare and the origin stays loopback-only; there is no second TLS variant
to maintain.

The federation edge path:

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

mastodon-web + mastodon background workers
        │ ao-sales (Sidekiq, HTTPS/443)
        ▼
Remote ActivityPub/WebFinger endpoints
```

The storefront hostnames are not included in this tunnel ingress. Tunnel
credentials remain in protected runtime storage and are never committed.

TLS requirements:

- TLS is mandatory at the edge for all federation traffic (satisfied by
  Cloudflare edge termination for the tunnel-routed apex hostname).
- Tunnel credentials and origin certificate are stored 0400 under
  `~/.cloudflared/` and mirrored to KDE Wallet `ao-mastodon`; never in
  Git or this README. Revoke by deleting/re-creating the tunnel.
- `X-Forwarded-Proto: https` is supplied by cloudflared so Rails
  generates HTTPS URLs and Secure cookies (validated: instance JSON
  reports `streaming_api: wss://mastodon.300x3.com`). Corrected
  2026-10-04: this line previously read `wss://300x3.com`, which is the
  static storefront and is not routed to Mastodon. The validation claim was
  correct but the value quoted was the retired apex host, so the line cited
  as proof that HTTPS rewriting works was itself an instance of the drift
  catalogued in §15.4.8 — a self-contradicting one. Measured:

  ```console
  $ curl -4 -s https://mastodon.300x3.com/api/v1/instance \
      | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['urls'])"
  {'streaming_api': 'wss://mastodon.300x3.com'}
  ```

Outbound delivery path:

- Mastodon background workers deliver public activities to remote inboxes over
  HTTPS/443. **Sidekiq is required** and is the component that performs this
  delivery; it runs as `ao-mastodon-sidekiq` on `ao-sales`.
- Egress is `ao-sales` itself (Section 3), which is non-internal solely for this
  purpose, with HTTPS/443 as the only protocol used. No database, Redis, or
  streaming container is attached to any egress network.
- Rate and retry behavior are Mastodon defaults; no relay subscription is
  approved unless explicitly decided.

### 15.4.4 Federation Enablement Sequence

**This is the specification of the sequence.** Whether each step is done is status and is
recorded once, in §19.1 (component status ST-13 and ST-14, and the work under COMM). No status is
stated here, because a specification does not carry its own status.

1. Dedicated Cloudflare Tunnel `ao-mastodon-federation` and DNS route for
   `mastodon.300x3.com`; storefront hostnames excluded.
2. Cloudflare redirect rule narrowed to exclude `mastodon.300x3.com`; the static
   storefront redirect unchanged.
3. Mastodon identity set to `LOCAL_DOMAIN=mastodon.300x3.com`; actor, WebFinger, and
   local actor documents verified.
4. Community publication carried inside `ao-sales`; database, Redis, and streaming
   remain isolated.
5. Tunnel transport switched to HTTP/2 after QUIC stream timeouts; local and public
   health checks return HTTP 200.
6. `@300x3@mastodon.social` resolved; public followers collection confirms both local
   accounts follow it.
7. Public post fetched; local mention records created and native notification
   processing repaired.
8. Verify reverse follows using the remote following collection and local incoming
   relationship tables, then perform a fresh signed ActivityPub round-trip test.
   Tracked in §19.1 under COMM.
9. Bootstrap discovery: from Konqueror signed in at `https://mastodon.300x3.com`,
   follow at least one account on `mastodon.social`. Remote servers do not index this
   instance until first contact occurs. The storefront host `https://300x3.com` is a
   static site and is **not** routed to Mastodon. Tracked in §19.1 COMM-06.
10. Validate public-post delivery to `mastodon.social` and reply/boost round-trips back
    to the local instance; then submit `300x3.com` to the joinmastodon.org directory
    (operator-authorised). Tracked in §19.1 COMM-07.

Steps 1 through 7 are complete; see §19.1 ST-13 and ST-14 for the evidence and for what
remains on the federation edge.

Step 8 status as measured 2026-10-03: **the reverse-follow verification half is done**
and is recorded in §15.4.9, read from the remote `following` collection of
`300x3@mastodon.social` and cross-checked against the local `follows` table — never from
local outgoing state alone. A *fresh signed* ActivityPub round-trip is **not** re-run
here, because doing so posts publicly and needs operator approval (COMM-07). The
sidekiq queues are empty, which shows nothing is stuck:
`LLEN queue:push_public = 0`, `LLEN queue:pull = 0`, and `redis-cli KEYS 'queue:*'`
returns an empty array.

step 9 status as measured 2026-10-04: first contact **has** occurred, so the instance is
no longer unindexed. Evidence — 10 distinct remote domains are now known locally
(`mastodon.social`, `veganism.social`, `mastodon.online`, `universeodon.com`,
`mastodonapp.uk`, `rivals.space`, `cupoftea.social`, `sekretaerbaer.de`, `fedibook.de`,
`friendicadev.sekretaerbaer.de`) and `mastodon.social` holds our actor, confirmed again by
`lookup?acct=bot@mastodon.300x3.com` → id `117327405745705562` and
`lookup?acct=admin@mastodon.300x3.com` → id `117327389970897359`. The one part of
step 9 not performed is the **human** step — signing in with Konqueror and following from
the browser UI. That requires the operator at the desktop and is not something a headless
session can or should fake. Tracked as COMM-06; status Open.

**Correction to the tunnel-health claim in this step.** An earlier pass recorded here that
the tunnel showed "all 4 connections registered ... no inbound fault". That was a
single-registration reading taken between flaps and it was wrong as a health statement:
the four connections were re-registering continuously. See §15.4.10 — 26 flap events in the
hour, and a 502 on every public path during the burst. Discovery and the remote lookup
above still hold; the claim that the edge path was fault-free does not.

Step 10 has two parts and neither is complete. Public-post delivery and round-trip
re-validation need a **new public post**, which is an external publication and is
withheld pending operator approval; directory submission to joinmastodon.org is
explicitly named in §19.1 as requiring explicit operator approval. Neither was performed.
Tracked as COMM-07; status Open.

### 15.4.5 Operational Boundaries After Enablement

- Only `public` visibility federates; `unlisted`, `private`, and
  `direct` do not appear on remote servers' explore pages. The OpenClaw
  draft-by-default and human-approval controls (Sections 11.2.2 and 15.2)
  remain mandatory for all public publication.
- `post.sh` public-post guard remains the script-level approval gate.
- Federated deletion is best-effort: remote servers may retain cached
  copies. Content published under this section must be treated as
  practically irreversible.
- Publication audit logging (immutable, Section 15.2) must include the
  remote-delivery outcome for federated statuses.

### 15.4.6 Remote Account Approval and Rejection Record

This is the standing moderation record for **remote** accounts contacting this
instance, deliberately kept separate from the local follow relationships in §15.4.4.
It is written here so that an approval or rejection decision is auditable rather than
inferred from follow state.

State measured 2026-10-03 directly from the `mastodon-db` container:

```console
$ podman exec mastodon-db psql -U mastodon -d mastodon -At -c \
  "select 'blocks='||(select count(*) from blocks)
        ||' domain_blocks='||(select count(*) from domain_blocks)
        ||' account_domain_blocks='||(select count(*) from account_domain_blocks)
        ||' email_domain_blocks='||(select count(*) from email_domain_blocks)
        ||' canonical_email_blocks='||(select count(*) from canonical_email_blocks)
        ||' follow_requests='||(select count(*) from follow_requests)
        ||' invites='||(select count(*) from invites)
        ||' ip_blocks='||(select count(*) from ip_blocks)
        ||' user_invite_requests='||(select count(*) from user_invite_requests);"
blocks=0 domain_blocks=0 account_domain_blocks=0 email_domain_blocks=0
canonical_email_blocks=0 follow_requests=0 invites=0 ip_blocks=0 user_invite_requests=0
```

| Date | Remote account | Action | Basis |
|---|---|---|---|
| 2026-10-01 | `300x3@mastodon.social` (remote mirror of the project's own service account, `actor_type=Service`, `bot=true`) | **Accepted** — bidirectional follow established with `bot` and `admin`. No block recorded. | Self-owned account; it is the project's own `300x3` mastodon.social identity, so blocking it would sever the operator's own remote presence. Not a third party. |
| 2026-10-01 | `Gargron@mastodon.social` (remote third party, `actor_type=Person`) | **Accepted as a remote actor, not followed** — `bot` follows `Gargron`; no reverse follow exists and none is expected. No block recorded. | An ordinary public-account follow in the direction local→remote. Not a moderation event. |
| — | All other contacting remote accounts | No action. Discovery relays (`veganism.social`, `mastodon.online`, `universeodon.com`, `mastodonapp.uk`, `rivals.space`, `cupoftea.social`, `friendica@sekretaerbaer.de`, `friendica@fedibook.de`, `friendica@friendicadev.sekretaerbaer.de`) are **automatically fetched service-discovery actors**, not user accounts and not approval candidates. | Discovery contacts are protocol artefacts, not sign-ups. |

There are **no pending remote approval requests**: `follow_requests = 0` and
`user_invite_requests = 0`, which is consistent with registration being closed (§15.4.2).
Nothing in the moderation tables is self-populating, so this table is the record of
record — a future block or approval must be added as a row here by the operator, per
§15.4.1 "Operator duties". No remote account has been rejected to date.

### 15.4.7 Inbound and Outbound Mail for the 300X3 Domain

Mail for `300x3.com` is **not configured and currently cannot be delivered**. This is
recorded here because Mastodon's account-confirmation and password-reset mail depends on
it, and because "no MX" is a decision state, not an oversight.

Measured 2026-10-03:

```console
$ dig +noall +answer MX 300x3.com; echo "answers=$(dig +noall +answer MX 300x3.com | wc -l)"
answers=0
$ dig +noall +answer TXT 300x3.com          # no SPF
$ dig +noall +answer TXT _dmarc.300x3.com   # no DMARC
$ dig +noall +answer A  mail.300x3.com      # no mail host
$ ss -lntp | grep -E ':(25|465|587)\b'      # no local SMTP listener
```

With no MX, RFC 5321 §5.1 falls back to the implicit MX, which is the domain's A record
(the Cloudflare edge addresses). Port 25 to those addresses does not answer:

```console
$ for IP in 172.67.163.66 104.21.41.83; do echo > /dev/tcp/$IP/25 && echo "$IP:25 OPEN" || echo "$IP:25 no-answer/closed"; done
172.67.163.66:25 no-answer/closed
104.21.41.83:25 no-answer/closed
```

Consequence: **all mail to `@300x3.com` is silently undeliverable.** This affects the
local Mastodon accounts, whose registered addresses are `admin@300x3.com` and
`bot@300x3.com`. Password resets and any confirmation mail cannot arrive. Because the
instance has open registration closed and no pending approvals, this is currently
non-blocking for federation, but it is a real gap.

**Outbound is also unconfigured, not merely undeliverable — added 2026-10-05.** The
first pass above only tested *receiving*. Listing the **key names** of the live Mastodon
environment (no values printed) shows there is no mail configuration at all:

```console
$ cut -d= -f1 ~/.local/share/ao-secrets/mastodon.env | sort | grep -iE 'smtp|mail|email'
NO smtp/mail/email key present in live mastodon.env
```

The file holds 24 keys, all of them database, cache, TLS or tuning values. Mastodon
therefore has no `SMTP_ADDRESS`/`SMTP_DOMAIN`/credentials, so it has **no way to submit
mail either**. The practical consequence is wider than "reset mail is undeliverable":
account recovery on this instance is not merely blocked at the receiving hop, there is no
sending path to block. Any resolution chosen under COMM-05 must set **both** directions;
fixing MX alone would leave outbound silent.

Resolution requires an operator decision between the options in §19.1 COMM-05 and is
**not** taken unilaterally here: pointing MX at a hosted relay, standing up a local MTA
(both a new public listener on port 25 and a new package — rule 3 and rule 12), or
formally deferring mail and documenting that address-based recovery is unsupported.
Tracked as COMM-05; status Open.

### 15.4.8 Known Configuration Drift Against `mastodon.300x3.com`

Reconciled audit performed 2026-10-03. **The service runtime is correct** — the live
instance is genuinely `mastodon.300x3.com` and federation works. The drift is confined
to documentation and helper artefacts, all of which emit the superseded apex
`300x3.com`. The entries below are exact so the owning session can apply them without
re-deriving the evidence; none of these files is owned by this section, so none was
edited here.

| # | File | Line | Currently | Should be | Consequence |
|---|---|---|---|---|---|
| D1 | `config/mastodon/mastodon.env.example` | 7 | `LOCAL_DOMAIN=300x3.com` | `LOCAL_DOMAIN=mastodon.300x3.com` | Template would provision a wrong-identity instance. **Highest severity of the four.** |
| D2 | `scripts/operations/fetch-openclaw-mastodon-env.sh` | 17 | `printf 'MASTODON_SERVER=https://300x3.com\n'` | `https://mastodon.300x3.com` | `MASTODON_SERVER` points at the static storefront, so every consumer of this helper posts to a non-Mastodon host. |
| D3 | `scripts/operations/fetch-openclaw-mastodon-env.sh` | 19 | `printf 'MASTODON_BOT_EMAIL=300x3@posteo.net\n'` | `bot@300x3.com` | Superseded third-party mailbox identity. |
| D4 | `config/mastodon/instance-policy.yaml` | 9 | `"https://300x3.com at the Cloudflare edge ... tunnel ao-mastodon-federation"` | `https://mastodon.300x3.com` | Names the retired network name `ao-mastodon-federation` and the apex host. |
| D5 | `config/mastodon/instance-policy.yaml` | 8, 16, 34 | `approved_pub_host: "300x3.com"`; Tokodon origin `https://300x3.com` | `mastodon.300x3.com` | Approved publication host must be the federation host. |
| D6 | `config/mastodon/instance-policy.yaml` | 20 | `registrations: "open with approval gate (approval_required: true)"` | `"closed"` | **Contradicted by the live instance** (`registrations=false`); see §15.4.2. |
| D7 | `config/mastodon/instance-policy.yaml` | 18–19 | `admin@300x3.com`, `bot@300x3.com` | correct — matches the database | No change. |
| D8 | `config/platform/version-matrix.yaml` | 41 | `local_domain: "mastodon.300x3.com"` | correct | Already reconciled 2026-10-01. Images are digest-pinned at v4.3.7, matching the running container. |
| D9 | `config/platform/version-matrix.yaml` | 51 | note: `RAILS_FORCE_SSL/LOCAL_HTTPS are set false but are INERT … loopback proxy at https://127.0.0.1:3300` | only the `set false` → `set true` wording | **Second instance of the same §15.4.2 error.** The `3300` in this note is **correct** and must not be "fixed". **Re-measured 2026-10-05: the values are actually `true`, so this row needs no edit at all** — see §15.4.13 Correction 1. |

**Correction to D9, made 2026-10-04.** An earlier pass recorded D9 as carrying "an
independent port typo: it cites the loopback proxy at port `3300` where the real origin is
`127.0.0.1:3000`", and instructed the owning session to change `3300` → `3000`. **That was
wrong and would have introduced a real fault.** Both ports exist and both are correct for
different processes:

```console
$ ss -ltnp | grep -E ':3000|:3300'
LISTEN 127.0.0.1:3000 users:(("rootlessport",pid=8478))      # podman port publish -> Puma
LISTEN 127.0.0.1:3300 users:(("python3",pid=2385))          # mastodon-local-proxy.py
$ ps -p 2385 -o cmd --no-headers
/usr/bin/python3 /ALWAYSON/scripts/operations/mastodon-local-proxy.py 3300 3000 ...
$ curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/api/v1/instance
301
$ curl -sk -o /dev/null -w '%{http_code}\n' https://127.0.0.1:3300/api/v1/instance
200
```

`mastodon-local-proxy.service` ("ALWAYS ON Mastodon local HTTPS proxy
(127.0.0.1:3300 -> :3000, self-signed TLS)") terminates TLS on `3300` and injects
`X-Forwarded-Proto: https` so Puma's hardcoded `config.force_ssl = true` is satisfied —
which is exactly why plain HTTP to `:3000` answers `301`. So `3300` is the *proxy* and
`3000` is the *origin*, and the version-matrix note names the proxy correctly.

Why this matters beyond the typo: the OpenClaw bridge depends on that distinction. Its
`API` constant is `https://127.0.0.1:3300` with a pinned self-signed CA, and its in-code
comment documents that using `http://…:3000` instead produces a TLS handshake against a
non-TLS Puma and a crash loop. "Reconciling" `3300` to `3000` in the matrix would have
documented a configuration that breaks the bridge. The only genuine drift in that note is
the `set false` wording, which is the same §15.4.2 error as everywhere else.

Proof that D2/D3 are live rather than theoretical: `scripts/mastodon/post.sh` line 17
calls `fetch-openclaw-mastodon-env.sh` on every invocation and line 21 consumes
`MASTODON_SERVER`. Any `post.sh` run therefore targets `https://300x3.com`.

Current versions confirmed correct and needing no change: Mastodon `4.3.7` (§15.3),
`tunnel alwayson-mastodon-federation` running `--protocol http2`, and the runtime
`LOCAL_DOMAIN=mastodon.300x3.com`. Tracked as COMM-01; status Open pending the edits
above, which belong to the session owning `config/` and `scripts/`.

### 15.4.9 Federation Contact Asymmetry (measured, not a fault)

Recorded because it looks like drift and is not. Measured 2026-10-03 from both sides:

```console
$ curl -s 'https://mastodon.social/api/v1/accounts/115945980770248178/following?limit=80'
count= 2
admin@mastodon.300x3.com | https://mastodon.300x3.com/@admin
bot@mastodon.300x3.com   | https://mastodon.300x3.com/@bot
```

The remote `following` collection of `300x3@mastodon.social` confirms **both** local
accounts follow it — the acceptance condition for COMM-02, read from the remote server
rather than inferred locally. The reverse is **not** symmetric: `300x3@mastodon.social`
lists only `bot` among its followers, and local `follows` rows 3 and 4 (`300x3@mastodon.social`
→ `bot`, → `admin`) were created by that remote account's own requests. `admin` has no
outgoing remote follow. `bot` has none either, locally: the only local→remote row is
`bot → admin` (row 1).

`Gargron@mastodon.social` was paginated to exhaustion (25 pages, 2000 follower entries)
and **does not** follow any `300x3.com` account. That is correct and expected: the
`follows` row 2 (`Gargron → bot`) is a record that *Gargron* follows *our bot*, which is
the remote account's business, not a reciprocal requirement.

This asymmetry is a property of how ActivityPub follow requests work, not a defect. It
is written down so a future session does not "fix" it by adding follows.

Re-measured 2026-10-04 and unchanged: the remote `following` collection still returns both
local accounts (`count= 2`), and `followers` still returns only `bot`
(`followers_count= 1`). The asymmetry conclusion stands. Note that the follow
*relationship* is sound while the *edge path* carrying it is currently degraded — see
§15.4.10. Those are independent, and a working `follows` row says nothing about whether
the object can still be fetched.

---

### 15.4.10 Cloudflare Tunnel Edge Instability (measured, and a real availability fault)

This supersedes the "transient 502" reading recorded in §15.4.4 step 8 and in the COMM-02
and COMM-06 evidence. Those passes saw a 502, retried, saw 200, and concluded the tunnel
was healthy. The 502 was not a one-off. It recurred, and the cause is a **sustained
cloudflared edge flap**, not a stray probe.

Measured 2026-10-04 (times UTC):

```console
$ systemctl --user show cloudflared-alwayson.service -p ActiveEnterTimestamp -p NRestarts
ActiveEnterTimestamp=Thu 2026-10-01 15:08:26 PDT
NRestarts=1
```

The unit has **not** restarted since 2026-10-01, so this is invisible to `systemctl` and to
any "is the service up" check. The process stays up while its four edge connections cycle:

```console
$ journalctl --user -u cloudflared-alwayson.service --since '60 min ago' \
    | grep -c 'Lost connection with the edge'
26
$ journalctl --user -u cloudflared-alwayson.service --since '3 hours ago' \
    | grep -c 'Lost connection with the edge'
61
$ journalctl --user -u cloudflared-alwayson.service --since '24 hours ago' \
    | grep -c 'failed to serve incoming request'
450
```

Each flap drops **all four** connections together and re-registers them within ~10 s:

```text
19:54:01 ERR failed to serve incoming request error="Error shutting down control stream: context canceled"
19:54:01 INF Lost connection with the edge connIndex=0
19:54:01 WRN Serve tunnel error error="connection with edge closed" connIndex=0
19:54:02 ERR Connection terminated ... connIndex=1,2,3
19:54:03 INF Registered tunnel connection connIndex=2 ... location=phx01 protocol=http2
19:54:03 INF Registered tunnel connection connIndex=1 ... location=phx01 protocol=http2
19:54:03 INF Registered tunnel connection connIndex=3 ... location=sjc01 protocol=http2
```

That all-connections-at-once pattern is why `NRestarts=1` is not evidence of health:
individual `connIndex` connections are re-established inside the one long-lived process.
**Health of this path must be judged by the flap count in the journal, not by unit state.**

User-visible effect, observed rather than inferred. During a flap window the public edge
returned 502 on every path, including the instance API and the site root:

```console
$ for i in 1 2 3 4 5; do curl -s -o /dev/null -m 15 -w '%{http_code} ' \
    -H 'Accept: application/activity+json' https://mastodon.300x3.com/users/bot; done
502 502 502 502 502
$ # same moment, /api/v1/instance, /api/v2/instance and / all 502
```

A Mastodon actor endpoint answering 502 is exactly the failure that stops remote servers
fetching this instance. Once the flap burst stopped, the same probes returned 200 twelve
times out of twelve, which is why a spot check during recovery reports a healthy system.

**What is *not* affected, measured rather than assumed:** the origin is fine. There were
zero 5xx in three hours of `mastodon-web` logs (1,161 lines, no `" 5xx "` status lines), and
no delivery or fetch errors in 1,872 lines of `mastodon-sidekiq` logs. Queues are empty
(`LLEN queue:push_public = 0`, `LLEN queue:pull = 0`, `KEYS 'queue:*'` → empty array). The
fault is at the Cloudflare edge-to-tunnel hop, not in Mastodon, and it degrades **inbound**
federation (remote servers pulling our objects) more than outbound delivery.

The flap window ran 2026-10-04T06:21:47Z through 19:54:01Z. It is not diagnosed beyond
that: this is the signature of a marginal or throttled tunnel edge connection, and
distinguishing a Cloudflare-side incident from a local network fault needs evidence not
available here. **Changing tunnel transport, protocol, or edge routing is live network
configuration and is therefore a stop condition** (README §4.1 rule 6); it is recorded for
the operator and for the section owning §15.4.3, not actioned here.

#### Trap: probe this host with `curl -4`, or IPv6 confounds every measurement

`mastodon.300x3.com` publishes AAAA records, but this host has **no global IPv6 address**:

```console
$ dig +short AAAA mastodon.300x3.com
2606:4700:3032::6815:2953
2606:4700:3035::ac43:a342
$ ip -6 -o addr show scope global | wc -l
0
$ ping -6 -c 2 2606:4700::6815:2953
ping: connect: Network is unreachable
$ curl -6 -s -o /dev/null -m 10 https://mastodon.300x3.com/api/v1/instance ; echo $?
7
```

A default-`curl` probe tries the AAAA address first, fails, and falls back to IPv4. The
fallback usually succeeds, so a plain probe looks fine. But it makes the measurement
**nondeterministic in a way that mimics the very fault being investigated**: under load or
timing variation the failed v6 attempt can surface as `000` or as a 502 rather than a clean
fallback, and the natural conclusion — "the tunnel is dropping requests" — is wrong. It is
the probe's dead v6 leg.

Use `curl -4` for every measurement against this host. Verified with `curl -4`: 12 of 12
probes returned 200 across the whole of a post-burst window, and IPv4 was what answered
### 15.4.11 The Flap Is Local-Path, Not Cloudflare-Edge (narrowed, 2026-10-04)

§15.4.10 measured *that* the tunnel flaps and correctly declined to name a cause. It is
narrowed here, because the connection topology discriminates between the two candidate
causes and the evidence points one way.

**The discriminator: the four connections are not peers of one edge.** Over 24 hours the
tunnel re-registered against **nine distinct Cloudflare PoPs**, yet always on the same four
edge IPs:

```console
$ journalctl --user -u cloudflared-alwayson.service --since '24 hours ago' -o cat \
    | grep 'Registered tunnel connection' | grep -o 'location=[a-z0-9]*' | sort | uniq -c
    23 location=lax05     17 location=lax07     20 location=lax08
    19 location=lax09     11 location=lax10     15 location=lax11
   224 location=phx01     59 location=sjc01     64 location=sjc06
$ # distinct edge IPs actually in use:
$ ... | grep -oE 'ip=[0-9.]+' | sort -u | wc -l
4
$ # transport is http2 on every single registration, never quic:
$ ... | grep -o 'protocol=[a-z0-9]*' | sort | uniq -c
   452 protocol=http2
```

The four connections terminate on four different edge IPs spread across Phoenix, San Jose
and Los Angeles. A Cloudflare-side edge fault therefore **cannot** explain the observed
pattern: three independent metropolitan PoPs do not lose four unrelated TCP connections
within the same second. Whatever is failing is upstream of the PoP, and common to all four.

**The loss counts confirm they fail as a group, not independently:**

```console
$ journalctl --user -u cloudflared-alwayson.service --since '24 hours ago' -o cat \
    | grep 'Lost connection' | grep -oE 'connIndex=[0-9]' | sort | uniq -c
    96 connIndex=0     94 connIndex=1     95 connIndex=2     99 connIndex=3
```

Nearly identical across four connections to four different cities, dropping in the same
seconds (14 timestamps in the last 6 h carry **three or more** simultaneous losses). Four
independent edges do not fail in lockstep; a shared local resource does.

**And it is not a hard network error.** The journal contains no `network is unreachable`,
`no route to host`, `connection reset` or timeout signature:

```console
$ journalctl --user -u cloudflared-alwayson.service --since '6 hours ago' -o cat \
    | grep -icE 'network is unreachable|no route to host|connection reset|broken pipe|timeout'
0
```

The only errors are the *consequences* of the drop, all downstream of it:

```console
    72 ERR failed to serve incoming request error="Error shutting down control stream: context canceled"
    64 ERR failed to serve incoming request error="Error shutting down control stream: client disconnected"
    31 WRN Serve tunnel error error="connection with edge closed" connIndex=3
```

"context canceled" and "client disconnected" are cloudflared tearing down in-flight streams
because the connection went away. Treating these as the cause — as their count and phrasing
invite — is a trap: they are the flap's shadow, not its origin.

**Conclusion, stated at the strength the evidence supports.** The fault lies on the shared
local path between this host and the tunnel edge — the local uplink, NAT state, or the
host's own network path — and not in Mastodon (origin 5xx = 0, both queues empty), not in
Cloudflare's edge fleet (three PoPs, four IPs, all healthy simultaneously otherwise), and
not in the cloudflared unit state (`NRestarts=1`, `ActiveState=active`). That last point is
the operational trap: **every "is the tunnel up" check passes while this fault is ongoing.**

**Blast radius, re-measured at steady state.** The flap is continuous rather than bursty,
and this corrects a natural misreading of a small sample:

```console
$ for w in '15 min ago' '1 hour ago' '6 hours ago' '24 hours ago'; do
    echo "$w: $(journalctl --user -u cloudflared-alwayson.service --since "$w" \
      | grep -c 'Lost connection with the edge')"; done
15 min ago: 0        # <- the misleading sample
1 hour ago: 26
6 hours ago: 121
24 hours ago: 384
# 384 events across 204 distinct minutes = ~16/hour, i.e. one flap roughly every 4 minutes
```

Sampling a short window is how this looks healthy; over 24 hours it is one flap every few
minutes. **The fifteen-minute window returning zero is not recovery, it is the burstiness
of the aggregate rate** — do not read a quiet minute as a fixed tunnel.

Public impact right now, measured with `curl -4` per the trap above, is currently low —
the edge is answering between flaps:

```console
$ for i in 1 2 3 4 5 6 7 8; do curl -4 -s -o /dev/null -m 15 -w '%{http_code} ' \
    -H 'Accept: application/activity+json' https://mastodon.300x3.com/users/bot; sleep 2; done
200 200 200 200 200 200 200 200
```

That 8/8 is **recovery between flaps, not a fix**, and must not be reported as one: the
same probe returned 502 5/5 during a burst (§15.4.10). Inbound federation is therefore
intermittently unavailable — roughly one short window every few minutes — while every
unit-level and spot-check health indicator reads healthy.

**Not actioned, deliberately.** Isolating the local path means changing live network
configuration (uplink, NAT, or tunnel transport) — a stop condition, and §15.4.3 belongs to
the session that owns edge and network path. The diagnostic the operator needs is cheap
and read-only: compare edge-connection stability against a control long-lived TLS
connection from this host to a fixed destination. If the control is stable while all four
tunnel connections flap in lockstep across nine PoPs, the local path is confirmed and the
tunnel is exonerated. That comparison has not been run, because it is not required to record
the finding and running it well needs a deliberate observation window.
### 15.4.12 Re-Verification Pass, 2026-10-04 (liveness, not a status refresh)

The live claims in this section are re-measured after the §15.4.11 tunnel finding, because
several of them rest on artifacts whose age had grown past 48 h. Two things change the
picture: an earlier claim was wrong, and the tunnel fault in §15.4.11 is **still live**,
not a historical episode.

**`statuses` is empty, and that is the operator's wipe, not data loss.** The table reads
zero, which looks alarming. It reconciles exactly with ST-13's documented 2026-10-01
timeline wipe and its backup:

```console
$ podman exec mastodon-db psql -U mastodon -d mastodon -At -c 'select count(*) from statuses;'
0
$ awk '/^COPY public.statuses /,/^\\\.$/' \
    /ALWAYSON/backups/mastodon-status-wipe-2026-10-01/statuses-before-wipe.sql | grep -c ''
126
$ podman exec mastodon-db psql -U mastodon -d mastodon -At \
    -c "select id,username,coalesce(domain,'LOCAL') from accounts order by id;" | head -4
-99|mastodon.internal|LOCAL                <- tombstone row, precedes every real id
117363090403638110|admin|LOCAL
117363090433277638|bot|LOCAL
117367694533297015|300x3|mastodon.social
$ podman exec mastodon-db psql -U mastodon -d mastodon -At \
    -c 'select (select count(*) from follows), (select count(*) from accounts);'
4|14
```

An earlier draft of this subsection quoted that accounts listing with `head -3` and showed
it starting at `admin`. It does not: there is a `-99` `mastodon.internal` tombstone row
that sorts first. The point — that `admin`, `bot` and the remote `300x3` account survive
the wipe — is unaffected, but **a transcript must be the real one, not a `head -3`
fragment of it.**

126 statuses were deleted from a 126-row pre-wipe dump, and the accounts and follow rows
ST-13 says were preserved are still present (`follows = 4`, `accounts = 14`). Anyone
reading `count(*) = 0` as loss of data should read ST-13 first. Note the operational
consequence: with zero statuses there is no local post for the federation queues to carry,
so an empty `queue:push_public` no longer proves outbound delivery works — it only proves
there is nothing to deliver.

**The bridge is alive and polling; a short liveness sample is not evidence of a stall.**
CPU ticks sampled over 20 s give `delta=0`, which reads as a stalled process. It is not — a
100 s sample shows steady consumption consistent with the 10 s poll loop. **A zero delta on
a short window measures the window, not the process:**

```console
$ systemctl --user show mastodon-openclaw-bridge.service -p MainPID -p ActiveState -p NRestarts
ActiveState=active
MainPID=788109
NRestarts=0
$ ps -p 788109 -o lstart,etime --no-headers
Thu Oct  1 18:50:54 2026    2-21:22:16
$ t1=$(awk '{print $14+$15}' /proc/788109/stat); sleep 100
$ t2=$(awk '{print $14+$15}' /proc/788109/stat); echo "delta_ticks=$((t2-t1))"
delta_ticks=2
$ cat /proc/788109/wchan
hrtimer_nanosleep
```

A 10 s poll doing one HTTPS request per cycle costs ~2 ms per iteration, so **any sample
shorter than about 60 s can read zero on a perfectly healthy process.** `wchan =
hrtimer_nanosleep` and a `MainPID` unchanged since 2026-10-01 corroborate it, and
`NRestarts=0` means the unit has never been restarted into a crash loop. Do not use a
short CPU delta as a liveness test for this unit.

**The idle cursor is real idleness, and the state file explains it.** The cursor is 7, the
database `max(notifications.id)` is 8, and the state file has not been written since
2026-10-01. Querying the API the way the bridge does resolves the apparent contradiction —
notification 8 exists but is **not the bot's**:

```console
$ cat ~/.openclaw/mastodon-bridge-state.json
{
  "lastNotificationId": "7",
  "updatedAt": 1790900850.2506645
}
$ ls -la ~/.openclaw/mastodon-bridge-state.json
-rw-rw-r-- 1 scottw scottw 67 Oct  1 17:27 /home/scottw/.openclaw/mastodon-bridge-state.json
# same call the bridge makes: /api/v1/notifications?limit=40
notifications returned: 1
ids/types: [('7', 'follow')]
max id: 7
$ podman exec mastodon-db psql -U mastodon -d mastodon -At \
    -c "select id,type,account_id from notifications order by id;"
7|follow|117363090433277638      <- bot
8|follow|117363090403638110      <- admin
```

So the newest notification *the bridge can see* is 7, equal to its cursor, and there is
nothing to advance to. The state file is only rewritten when a notification is newer than
the cursor, so its 2026-10-01 mtime is consistent with a healthy idle loop and is **not**
evidence of a stall. This refines the §15.4.9 claim that "max(notifications.id) is 8 while
the cursor is 7" — those two numbers were never comparable, because the API view is
per-account. §5 (README) states the same pairing and should be read with this in mind.

**COMM-08 is still ongoing; §15.4.11 is not stale.** Re-measured the flap rate:

```console
$ for w in '15 min ago' '1 hour ago' '24 hours ago'; do
    printf '%s: ' "$w"; journalctl --user -u cloudflared-alwayson.service --since "$w" \
      | grep -c 'Lost connection with the edge'; done
15 min ago: 7
1 hour ago: 15
24 hours ago: 381    # was 384 at the previous pass, i.e. the rate is NOT decaying
$ systemctl --user show cloudflared-alwayson.service -p NRestarts -p ActiveState
ActiveState=active
NRestarts=1
```

Two corrections apply. First, **a `15 min ago: 0` sample is a quiet window, not the
absence of a fault** — the flap was caught mid-burst at `15 min ago: 7`. That is exactly the
trap §15.4.11 warns about, and it is the reason **a short window must never be quoted on
its own**. Second, 381 in 24 h against 384 previously is steady-state persistence, not
decay — the fault has now run for over two days.

The cheap control comparison §15.4.11 did not have is now available: a long-lived TLS
handshake to the same Cloudflare edge address succeeds cleanly, and a control request to a
non-tunnel external host is stable:

```console
$ openssl s_client -connect 104.21.41.83:443 -servername mastodon.300x3.com </dev/null \
    | grep -E 'Protocol|Verify return'
Protocol: TLSv1.3
Verify return code: 0 (ok)
$ for i in 1 2 3; do curl -4 -s -o /dev/null -m 15 \
    -w '%{http_code} ' https://mastodon.social/api/v2/instance; sleep 3; done
200 200 200
```

This is **not** yet the confirmation §15.4.11 asked for, and must not be reported as one: a
single short-lived TLS handshake succeeding says nothing about connection *stability* over
the minutes-long window a tunnel connector needs. It does exclude "TLS to the edge IP is
broken" and "general outbound HTTPS is broken", which is useful. Diagnosing the local path
and changing tunnel transport remain live network configuration and therefore a stop
condition. Tracked as COMM-08; status Open.
### 15.4.13 Independent Re-Verification, 2026-10-05 (liveness of §15.4.8–§15.4.12)

Every claim in §15.4.8–§15.4.12 rests on measurements taken 2026-10-03/04. Re-measured
from scratch on 2026-10-05 rather than trusting them. Most reproduce exactly. **Three do
not, and all three corrections are mine.**

**Correction 1 — `RAILS_FORCE_SSL`/`LOCAL_HTTPS` are set `true`, not "false".** §15.4.8
row D9 and §15.4.2 both describe these variables as "set false but INERT". That is wrong
in a way that matters, because "set false" implies a deliberate local override that is
then defeated by the upstream default. There is no override — the live values are `true`:

```console
$ grep -E '^(RAILS_FORCE_SSL|LOCAL_HTTPS)=' ~/.local/share/ao-secrets/mastodon.env
RAILS_FORCE_SSL=true
LOCAL_HTTPS=true
$ podman inspect mastodon-web --format '{{range .Config.Env}}{{println .}}{{end}}' \
    | grep -E 'RAILS_FORCE_SSL|LOCAL_HTTPS'
RAILS_FORCE_SSL=true
LOCAL_HTTPS=true
$ grep -n 'force_ssl' /ALWAYSON/config/mastodon/patches/production.rb
config.force_ssl = ENV.fetch('RAILS_FORCE_SSL', 'true') == 'true'
```

The env-file key list contains no `RAILS_FORCE_SSL=false` anywhere. So the sequence is:
the variable is explicitly `true`, the project patch reads it, and the upstream default
agrees. Nothing is inert and nothing is overridden. The corrected D9 "should be" cell is
therefore **no change at all** — the note's substance is right and only its description of
the *mechanism* is wrong. This also means D9 has **no actionable edit**, which lowers the
apparent size of the COMM-01 backlog by one row.

**Correction 2 — port `3300` is real, confirmed a second time, independently.** §15.4.8
already retracted the "3300 typo" claim; it is re-derived from the live system here rather
than restated from that retraction. `mastodon-local-proxy.service` is live, is serving the actual
Mastodon UI, and the proxy process is running exactly as the version-matrix note
describes:

```console
$ ss -lntp | grep -E ':(3000|3300|4000)\b'
LISTEN 127.0.0.1:3000 users:(("rootlessport",pid=8478,fd=5))
LISTEN 127.0.0.1:3300 users:(("python3",pid=2385,fd=3))
LISTEN 127.0.0.1:4000 users:(("rootlessport",pid=5967,fd=5))
$ ps -p 2385 -o lstart,cmd --no-headers
**Correction 3 — the flap is bursty, not steady. §15.4.11 said "NOT bursty" and that is
wrong.** §15.4.11 measured 384 events across 204 distinct minutes and concluded a steady
~16/hour, "one flap roughly every 4 minutes". Re-measured over a fresh 24 h window the
count is higher and the *shape* is different: 444 events, and the minute-level gap
histogram shows the events arrive in **consecutive-minute pairs**.

```console
$ for w in '15 min ago' '1 hour ago' '6 hours ago' '24 hours ago'; do
    printf '%s: ' "$w"; journalctl --user -u cloudflared-alwayson.service --since "$w" \
      | grep -c 'Lost connection with the edge'; done
15 min ago: 6
1 hour ago: 21
6 hours ago: 90
24 hours ago: 444
$ # distinct flap-bearing minutes, then the gap between consecutive ones:
distinct_flap_minutes=139
60s x68   120s x2   180s x1   420s x3   480s x5   540s x4   600s x3   660s x2 ...
median_gap=120s  max_gap=4020s
```

68 of the 138 gaps are **exactly 60 s**, i.e. a flap minute immediately followed by
another flap minute. Aggregated by burst: **387 losses fall in 105 minutes that contain
3+ simultaneous losses, against 53 losses in 34 singleton minutes.** That is the
signature of a periodic multi-connection event, not an independent per-connection
background error rate.

Why this is not a cosmetic correction: §15.4.11's own advice was "do not sample a short
window, the rate is steady". If the truth is bursty, that advice is actively harmful —
during a quiet period a short sample reads 0 and a reader concludes the fault is over,
which is exactly the false-recovery trap §15.4.12 records. **It was hit again:** at 15:03
UTC, `10 minutes ago` returned **0 flaps** while the preceding 15-minute window had
returned 6. **A short window inside a bursty fault is a quiet interval, and a quiet
interval is not a recovery.**

**The §15.4.11 conclusion survives, and the discriminator got stronger.** The PoP
footprint widened from nine to **fourteen** distinct points of presence in 24 h, against
still exactly **four** edge IPs, still 100 % `protocol=http2`, and the per-connection loss
split is still near-uniform (112/111/109/108 across `connIndex` 0–3):

```console
$ journalctl --user -u cloudflared-alwayson.service --since '24 hours ago' -o cat \
    | grep 'Registered tunnel connection' | grep -o 'location=[a-z0-9]*' | sort | uniq -c
  2 lax01  22 lax05  19 lax07  14 lax08  13 lax09  15 lax10  21 lax11  2 lax13
246 phx01  64 sjc01  80 sjc06  2 sjc07  1 sjc08  1 sjc10
**The control experiment §15.4.11 asked for: run, and it came back inconclusive.** It
compared a long-lived TLS handshake to the tunnel edge IP against a handshake to a
non-tunnel destination, 110 ticks at 5 s, and correlated each tick with a 70 s window of
tunnel journal entries:

```console
$ # 110 ticks, edge = 104.21.41.83:443, control = mastodon.social:443
SUMMARY ticks=110 edge_ok=110 edge_fail=0 ctrl_ok=110 ctrl_fail=0 flaps_seen_in_windows=0
```

Both paths were perfect, **because zero flaps occurred during the window** — consistent
with the bursty finding above. This is *not* the confirmation §15.4.11 requested, and I
am not recording it as one. A probe with no events in it cannot discriminate anything: the
result is identical to what a healthy network would have produced, which is precisely why
"both green" must not be read as "fault absent". A second, longer probe was launched to
try to catch a burst deliberately.

### A probe that scores a success as a failure inverts the finding

The first probe treated success as `grep -c 'Verify return code: 0'` being *exactly* `1`.
The control returned `2` on every tick — the string legitimately appears twice (chain and
leaf) — so **every control tick was scored as a failure**. The probe must accept `>= 1`.
Had the `ctrl_ok=2` line not been inspected as a fault, the report would have read "the
control path fails continuously while the edge path succeeds", inverting the
conclusion. **A probe's expected value must be a range, not a point.** The same class of
error as the empty-output-vs-zero-count mistake in the COMM-05 evidence.

**Status of the other COMM items, re-verified 2026-10-05 (no new findings).**

- **COMM-02** — remote `following` still returns `count= 2` (both local accounts); remote
  `followers_count= 1`, listing only `bot`. §15.4.9 unchanged.
- **COMM-03** — all nine moderation tables still `0`; remote actors still 9
  `Application` / 1 `Person` / 1 `Service`; `settings` still holds only
  `reserved_usernames`; both local users `approved=true`, `disabled=false`. D6 unchanged:
  `registrations False approval_required False` against a policy file that says
  "open with approval gate".
- **COMM-04** — token length 43, `verify_credentials` HTTP 200 `acct=bot`
  `id=117363090433277638`; both bridge copies still `sha256 486e7472…99c19`;
  `ActiveState=active`, `NRestarts=0`.
- **COMM-05** — still **no** MX (`answers=0`), and **the live `mastodon.env` contains no
  SMTP, mail or email key at all**, so outbound is not merely undeliverable, it is
  unconfigured. See §15.4.7.
- **COMM-06** — `mastodon.social` still resolves both accounts
  (`bot` id `117327405745705562`, `admin` id `117327389970897359`, 2 followers each);
  10 distinct remote domains known locally. The Konqueror step remains the operator's.
- **COMM-07** — `statuses` is still `0` (the 2026-10-01 wipe; the 126-row pre-wipe dump
  is still present at `backups/mastodon-status-wipe-2026-10-01/`), both queues empty,
  `joinmastodon.org` → 200. **No publication performed.**
$ ... | grep -oE 'ip=[0-9.]+' | sort -u
ip=198.41.192.107  ip=198.41.192.167  ip=198.41.200.13  ip=198.41.200.193
$ ... | grep 'Registered tunnel connection' | grep -o 'protocol=[a-z0-9]*' | sort | uniq -c
502 protocol=http2
$ journalctl ... | grep 'Lost connection' | grep -oE 'connIndex=[0-9]' | sort | uniq -c
112 connIndex=0  111 connIndex=1  109 connIndex=2  108 connIndex=3
$ systemctl --user show cloudflared-alwayson.service -p NRestarts -p ActiveState
ActiveState=active
NRestarts=1
```

Fourteen independent metropolitan PoPs across three regions cannot all lose four
unrelated connections inside the same second. The fault remains **upstream of the PoP and
common to all four connections** — the shared local path. Origin is still clean
(`mastodon-web` 5xx count over 30 m = 0, `error delivering` in `mastodon-sidekiq` = 0,
both queues empty). And the operational trap is unchanged and still the most dangerous
thing in this section: **`NRestarts=1` with `ActiveState=active` while the fault runs.**
Thu Oct  1 15:08:14 2026 /usr/bin/python3 /ALWAYSON/scripts/operations/mastodon-local-proxy.py \
    3300 3000 /ALWAYSON/secrets/mastodon/mastodon-local.crt .../mastodon-local.key
$ systemctl --user show mastodon-local-proxy.service -p NRestarts
NRestarts=0
$ curl -sk -m 10 https://127.0.0.1:3300/ | grep -oiE '<title>[^<]*</title>'
<title>Mastodon</title>
$ curl -sk -m 10 https://127.0.0.1:3300/api/v1/instance   # -> version
4.3.7
```

Two facts make this worth restating. First, `3300` answers **200** and returns the real
Mastodon UI, while `https://127.0.0.1:3000/api/v1/instance` errors at the TLS layer —
the ports are not interchangeable, so any "normalisation" of the matrix note to `3000`
breaks the bridge (see §15.4.8). Second, this is the **Quadlet/copy trap again**: the
live unit at `~/.config/containers/systemd/` is a *copy* of
`/ALWAYSON/quadlet/operations/mastodon-local-proxy.service`. Editing the repo file alone
will not change the running proxy.

# 16. Scripts and Operational Standards

## 16.1 Scripts Layout

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

The tree above was a **partial** listing and understated three directories.
Measured with `ls -1` on 2026-10-04, the entry counts are: `bootstrap` 7,
`deploy` 6, `validation` 11, `backup` 9, `restore` 5, `operations` 21,
`simulation` 15, `ops` 8, `mastodon` 10. `bootstrap` and `deploy` are now
listed in full above; `validation` was already complete. `backup/` and
`restore/` are named in §16.1.2 rather than expanded here, because that is
where the mapping to their systemd units matters. The remaining
count-bearing directories are intentionally summarised as one line each —
they are not part of any acceptance criterion and expanding them would make
this tree go stale on every new script.

`scripts/build-update/` is a further directory holding the software-status
generators (`provenance-log.py`, `inventory-full.py`, `refresh-install-log.sh`,
`apt_history.py`, `test_generators.py`); it predates this section and is
described in §12.5.

### 16.1.1 `build-update/provenance/` — the generator package (OPS-18)

`provenance-log.py` was a single ~2,300-line module holding evidence gathering,
policy, plan generation and rendering in one file. It is now a thin entrypoint
over a package, split by concern:

| Module | Holds | Why it is separate |
|---|---|---|
| `provenance/common.py` | constants, `run()`, `now_utc()`, `norm()`, `is_complete_digest()`, `load_yaml()` | The three primitives everything else needs. No knowledge of provenance, policy or rendering. |
| `provenance/collector.py` | every function that reads local state, spawns a subprocess or queries upstream | The only module with mutable module-level state (`COLLECTED`, `_CACHE_HITS`, `_CAND_VER`, `_CAND_ID`, `OFFLINE`). Those caches exist because the un-cached form spawned ~230 apt subprocesses per run and stopped completing. |
| `provenance/policy.py` | `EXCLUSIONS`, `NEEDS_APPROVAL`, `PIN_POLICY`, `PLAN_VERBS`, `_argv_is_safe()`, `pin_policy()`, `update_risk()` | The updater allowlist and the **recorded reason** for each entry. Stdlib-only, so the safety property can be read and audited without following an import graph. |
| `provenance/plan.py` | `update_steps()`, `write_update_plan()` | Machine-readable plans: each item is either `eligible` with exact ordered argv steps or `excluded` with the rule that excludes it. No third state, no implicit default. |
| `provenance/render.py` | `HEADERS`, `CSS`, `rows_to_html()`, `rollup_details_md()`, `to_html()` | Presentation. Holds no policy and makes no network call, so a column-order change cannot reach back into collection. |

Dependency direction is strictly one way, asserted from the import statements in
`TestProvenancePackageBoundaries`:

```
plan     -> policy, render, common
render   -> collector, policy, common
collector-> common
policy   -> (stdlib only)
```

Two properties of the split are load-bearing and are pinned by tests rather than
left to convention:

**Re-export is a snapshot, not an alias.** `provenance/__init__.py` binds every
top-level name of every submodule so the entrypoint keeps its historical surface,
but those bindings are taken at import time. If the owning module later
*rebinds* its own name with a `global` statement, the copy keeps the old value.
Measured: after `_load_apt_history()` cached the module in `collector`,
`provenance._APT_HISTORY_MODULE` still read `'unset'`. Therefore any state that
crosses a module boundary goes through an accessor owned by the writer —
`cache_ttl()` / `set_cache_ttl()` for the TTL, and `set_offline()` in the
entrypoint for `--offline`. A bare imported `CACHE_TTL` or `OFFLINE` global would
have printed the default 6h TTL on a forced refresh.

**The re-export is built from an explicit namespace walk, not `import *`.**
`from .collector import *` skips underscore-prefixed names, and existing
regression tests reach `_load_apt_history` and `_argv_is_safe` through the
entrypoint; a plain star import turns those into `AttributeError` at the call
site rather than at import. `__all__` is computed after the loop variables are
deleted, because publishing them into the entrypoint's `from provenance import *`
made the star import fail.

`provenance-log.py` remains the executable entrypoint and the documented usage
string, and holds argument parsing and flag wiring only. Measured line counts of
the package (`wc -l`): `collector.py` 1,633, `render.py` 446, `plan.py` 211,
`policy.py` 139, `common.py` 93, `__init__.py` 70; the entrypoint is 133 lines
against the original 2,328.
### 16.1.2 Backup, restore and receipt executors (measured 2026-10-04)

Measured with `ls -1` against the tree, not read off this document. This mapping
was missing: §16.1 named `backup/` and `restore/` as bare directories while §17.1
claimed active timers, so no reader could tell which file a timer actually ran.

`scripts/backup/` holds nine scripts. Which unit runs each:

| Script | Invoked by |
|---|---|
| `restic-run.sh` | `ao-restic-backup.service` — `ExecStart=/ALWAYSON/scripts/backup/restic-run.sh` |
| `verify-backup.sh` | `ao-restic-verify.service` — `ExecStart=/ALWAYSON/scripts/backup/verify-backup.sh` |
| `fetch-restic-env.sh` (in `operations/`, not `backup/`) | `ao-restic-prefetch.service` — `ExecStart=/ALWAYSON/scripts/operations/fetch-restic-env.sh /run/user/1000/ao-restic.env`. It resolves the wallet-backed restic credentials before the other two run; note it lives outside `backup/`, so `ls scripts/backup/` alone does not reveal that the backup path depends on it. |
| `dump-all-postgres.sh` | operator-invoked; dumps every PostgreSQL database in one pass |
| `backup-postgres.sh`, `backup-host-postgres.sh`, `backup-container-postgres.sh` | per-source PostgreSQL dump helpers |
| `backup-corda.sh`, `backup-photogrammetry.sh` | domain backups |
| `pcloud-restic-setup.sh` | one-time pCloud restic repository setup |

`systemd/backup/` is the only systemd tree in the repository and holds exactly six
unit files — `ao-restic-backup`, `ao-restic-verify` and `ao-restic-prefetch`, each
as a `.service` + `.timer` pair. Backup and restore are also the only subsystem
still using plain units rather than Quadlet.

```
$ find systemd -type f | sort
systemd/backup/ao-restic-backup.service
systemd/backup/ao-restic-backup.timer
systemd/backup/ao-restic-prefetch.service
systemd/backup/ao-restic-prefetch.timer
systemd/backup/ao-restic-verify.service
systemd/backup/ao-restic-verify.timer
```

`scripts/restore/` holds five scripts, and this is the honest state of the
seven-step restore test of §17.1:

| Script | §17.1 steps | State |
|---|---|---|
| `verify-hashes-and-receipts.sh` | 3–5 | **Implemented.** Recomputes `sha256sum` over each manifest's `local_storage_reference`, compares against `content_hash_sha256`, then checks receipt linkage. Exits 51 on mismatch, 2 on bad usage. |
| `restore-sales-db-test.sh` | sales DB | PENDING — `exit 3` |
| `restore-corda-test.sh` | Corda | PENDING — `exit 3` |
| `restore-mapping-artifact-test.sh` | mapping | PENDING — `exit 3` |
| `restore-simulation-artifact-test.sh` | simulation | PENDING — `exit 3` |

The seven-step test therefore has a named executor and **one real implementation,
not five**. The four PENDING scripts exit immediately with
`PENDING: <path> requires completed backups plus isolated test-path approval`; they
are honest stubs rather than broken scripts, and `bash -n` passes on all five.
Closing them needs operator approval of an isolated test path and a completed
backup, so they remain stubs until that approval exists.

There is **no restore timer**. `scripts/validation/check-logs-journals.sh` asserts
freshness of `restore-test.log` at 3650 days — a placeholder that can never fail,
not a cadence. The restore test is manual until a timer and interval are approved.

`sales/` and `validate-sale-receipt.sh` both exist. `sales/` holds seven scripts
(`add-pdf-form-fields.py`, `autofill-handoff-form.py`, `intake-kit-request-pdf.sh`,
`intake-request-record.py`, `intake-to-pdf.sh`, `issue-transaction-bundle.sh`,
`validate-transaction-bundle.sh`) and `validate-sale-receipt.sh` lives in
`validation/`. Both were previously reported missing against an earlier snapshot
of this section; that report is stale and is retracted here.

### 16.1.3 Store status has four states, not two (OPS-33)

`scripts/operations/collect-system-health.py` classifies every declared SQLite
store into `ao_status.sqlite_store.status`, and the column is
`CHECK (status IN ('absent','error','excluded','ok'))`. The four states are
deliberate and the distinction between the middle two is the whole point of the
item:

| status | meaning | a human is required |
|---|---|---|
| `absent` | declared, but not installed on this host | no — a `?` in software-status.md |
| `ok` | present and read | no |
| `excluded` | present, but deliberately not snapshotted | no — a decision already taken |
| `error` | present and **unreadable** | **yes** |

`absent` and `error` are the pair that was previously collapsed. OPS-33 asks
that a store declared in the manifest but missing here render as an *error*
rather than silently reading as `absent`; the schema now carries the distinction,
the view exposes `sqlite_stores_absent`, `sqlite_stores_error` and
`sqlite_stores_excluded` as separate counters, and the collector sets `error` for
anything it could not open, stat or parse.

**The classification is keyword-based over `read_error` free text**, which is a
known fragility and is recorded here so the next reader does not trust it
blindly. `sqlite3` reports corruption as `DatabaseError('file is not a
database')` or `'database disk image is malformed'` — sentences containing none
of the usual "…failed" markers.

**A fault list that matches only some failure words is a false-negative generator.** Because the
list matched only `failed` /
`not a sqlite file` / `header read failed` / `open failed` / `read failed` /
`snapshot failed` / `integrity`, a **corrupt database was classified `excluded`**
— that is, an unreadable store was recorded as a *deliberate operator
decision*. Measured before the fix:

```console
$ classify_store({'present': True, 'read_error': 'database disk image is malformed'})
-> 'excluded'      # want 'error'
$ classify_store({'present': True, 'read_error': 'file is not a database'})
-> 'excluded'      # want 'error'
```

That is the more dangerous direction of the two: a fault was reported as intent,
so nobody would ever be paged for it. The same gap existed independently in the
SQL backfill in `config/platform/postgresql/ao-status.sql`, which is the thing
that would have poisoned rows already written to a live database. Both lists now
carry the corruption markers, and the SQL is written to mirror the Python
(`_STORE_ERRORS` + `_STORE_CORRUPT`) so the two cannot silently disagree.

Verified against a throwaway PostgreSQL 18.6 rather than the live Grafana
database. Seeded six rows with `status` dropped and re-ran the migration:

```console
$ psql -v ON_ERROR_STOP=1 -f config/platform/postgresql/ao-status.sql   # rc=0
$ SELECT id, status FROM ao_status.sqlite_store ORDER BY id;
     id      |  status
-------------+----------
 s-absent    | absent
 s-badheader | error      <- not a SQLite file (bad header)
 s-corrupt   | error      <- database disk image is malformed
 s-excluded  | excluded   <- excluded from snapshot by operator decision
 s-notadb    | error      <- file is not a database
 s-ok        | ok
(6 rows)
```

Idempotency and the constraint were both checked: a second run leaves the six
statuses unchanged, and `INSERT … VALUES ('bad', true, 'banana')` is rejected by
`sqlite_store_status_check`. The classifier agrees row-for-row with the SQL
across all 16 cases exercised in Python.


### 16.1.1 Quadlet deploy path

**Quadlet units deploy flat.** `~/.config/containers/systemd/` holds copies, not symlinks,
and Quadlet does not read a per-domain subdirectory. A unit placed in
`~/.config/containers/systemd/<domain>/` is silently ignored, so a deploy can appear to
succeed while changing nothing.

`deploy-quadlet-domain.sh`, `rollback-domain.sh`, `validate-quadlet-domain.sh`, and
`enable-domain-services.sh` all target the flat directory. `rollback-domain.sh` removes only
the named files of the requested domain; it must never `rm -r` the directory, because with
a flat layout that would delete every other domain's units.

Confirm what a deployed unit actually resolved to:

```bash
systemctl --user show ao-grafana.service -p SourcePath
```

Editing `quadlet/<domain>/*.container` in the repository changes nothing on the host until it
is deployed; the live unit is a copy.

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

## 16.3 Logs-Journals

All logs and journals are kept in one place:

```text
/ALWAYSON/logs/
```

`LOGS-JOURNALS/` is **not** the location; it was a name in an earlier draft and
never matched the implementation. Every writer uses `/ALWAYSON/logs/`:
`common.sh` sets `AO_LOG_DIR`, the deployed Gazebo quadlet sets
`--log-opt path=…/logs/sim-gz-server.log`, `ao-build-update` bind-mounts
`logs/operations`, and the §12.1 install step writes
`logs/installation/agent-install.log`. The earlier `LOGS-JOURNALS/` name was never implemented; §16.3 is the single statement.

Rotation: `/etc/logrotate.d/` policy staged at
`config/host/logrotate-alwayson.conf` (daily, 14 kept, no compression — see
§19.1 OPS-25). Subdirectories are not rotated; their retention is OPS-26.

Logs are classified per §4.2 and are never a place to record secrets.

`scripts/validation/check-logs-journals.sh` asserts every entry below exists
and is within its staleness budget: exit 0 pass, 1 missing, 2 stale.

| Log / journal | How often it updates | Purpose |
|---|---|---|
| `installation-journal.log` | Appended during every install or change session | The installation journal required by §4.1 rule 11. Writer: `ao_install`. |
| `operations-journal.log` | Appended on every operational change | Deploys, enable/disable, restarts, and validation-script outcomes. Writer: `ao_operation`. |
| `audit.log` | Appended on every audited operation | Immutable audit trail of operational changes and authorization decisions. Writer: `ao_audit`; `ao_audit_secret` redacts credentials. |
| `backup.log` | After every backup run | Repository, snapshot ID, and success/failure. Writer: `ao_backup_run`, called by `scripts/backup/restic-run.sh`. Dry runs are recorded as `DRY-RUN` and are not counted as backup runs. |
| `restore-test.log` | After every restore test | Source backup ID, operator, result, exceptions. Writer: `ao_restore_test`. No entries yet, and none can exist yet: four of the five scripts under `scripts/restore/` exit 3 as PENDING and `verify-hashes-and-receipts.sh` is a manual command that does not write the journal (see §16.1.2). The freshness threshold of 3650 days is a placeholder, not a cadence. |
| `gpu-runtime-check.log` | On each GPU runtime validation | Driver/CDI state and whether GPU access was granted to the workload. Writer: `scripts/validation/check-gpu-runtime.sh`. |
| `script-runs.log` | On every script invocation | Which script ran, its arguments, exit code, and dry-run status. Writer: `ao_log`. |
| `mastodon-local-proxy.log` | While the local proxy runs | Local Mastodon proxy activity and errors. |
| `meshchatx.log` | Continuously while MeshChatX runs | Pointer to the MeshChatX application log, which the application writes into its own storage dir. Not a second writer. See this document. |
| `sim-gz-server.log` | While the Gazebo server runs | Headless Gazebo simulation output. Written by the deployed quadlet. |
| `sim-foxglove-bridge.log` | While the bridge runs | Foxglove bridge output and connection state. |
| `sim-clock-bridge.log` | While the clock bridge runs | Simulation clock bridge output. |
| `web-console.log` | On console operations | Web console operations and their outcomes. |
| `lmstudio-readme-preset.sha256` | On preset change | Checksum of the LM Studio README preset, for drift detection. |
| `gpu-runtime/` | On each validation | Directory of GPU runtime validation captures, one timestamped file per run. |
| `backup/` | After every backup run | Directory of backup run records and repository metadata. |
| `operations/` | On each operational change | Directory of per-operation journals, one file per operation. Mounted into `ao-build-update`; do not relocate. |
| `installation/` | During install sessions | The install-step output log `agent-install.log` referenced by §12.1. Retained as-is. |

Logs are classified per §4.2 and are never a place to record secrets.

## 16.4 Document Coordination

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

**NOTE (2026-10-06):** earlier drafts of this section carried the source folder name with
extra parentheses; the canonical, tracked name is `agents/COORDINATION (README UPDATES)/` and is used
throughout this section. The earlier parenthesized forms are retired.

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
6. **Sections 1–16 stay specification** — no status, history, revision or
   decision dates. Anything current belongs in §17 or §19.
7. **Commit only your own section file.** `git add -A` sweeps in other
   sessions' work.

**The two roles.**

| Role | Does |
|---|---|
|---|---|
| Section session | Edits exactly one `section.md`; commits only that file |
| Compiler session | Runs `compile.py`, requires `--check` to report `identical`, then pushes |

**If `--check` reports `DIFFERS`**, someone edited `README.md` directly. Do not overwrite
it — that discards their work. Re-run `split.py` to fold their edit into the section file,
confirm the round trip, and continue. This has happened; it is recoverable, and the recovery
is one command.

The split/compile round trip is byte-exact, so the README can always be trusted to equal the
sum of its parts.

This folder is distinct from `COORDINATION BETWEEN AI/`, which holds session handoff
narrative. That folder is prose; `COORDINATION/` is build input.

---

# 17. Backup, Restore, Monitoring, and Completion Criteria

This section states what backup, restore, retention and monitoring **must** do. It
carries no measured state. Outstanding work, current coverage and evidence live in
`README-ACTION_ITEMS/status-and-references.md` (§19.1, `OPS` group); this section is
the requirement those rows are measured against.

## 17.1 Backup and Restore Policy

### 17.1.1 The 3-2-1 target

Maintain **3-2-1**: three copies, on two media types, with one copy off-host or
off-site.

| Copy | Location | Requirement |
|---|---|---|
| Primary | Live system | — |
| Backup | Encrypted restic repository outside the data path | Produce a successful snapshot, verified by hash |
| Off-site | pCloud, as a restic destination | Maintain a second repository, disjoint from the host |

### 17.1.2 Placement rules

1. **Keep the local repository off the data's physical device.** A repository that
   shares the data's device is lost with that device and does not count as a copy.
2. **Do not count an off-host archive as the off-site copy unless it carries a
   restore duty.** `ao-egress-archive` carries none (see §11.6) and must not be
   counted toward 3-2-1.
3. **Record the device id of every backup path**, and re-verify separation after any
   storage, mount or repository change.

| Path | Role | Requirement |
|---|---|---|
| `/ALWAYSON` | the data | protected |
| `/var/backups/alwayson-restic` | local repository | **must not share a device with the data** |
| `/media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS` | off-host repository | must exist, decrypt with the production credential, and verify |
| `/home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS` | replicated cloud copy | must verify |

### 17.1.3 Off-site repository requirements

The off-site repository must satisfy all of the following.

1. **Exist as a valid restic repository** and decrypt with the production
   credential (`restic cat config` succeeds).
2. **Hold a snapshot series, not a single snapshot.** A one-snapshot repository
   proves a copy once; it does not prove a copy is maintained. Schedule it, or
   record an explicit approved deviation.
3. **Cover every path class the nightly repository covers** (see §17.4). A
   repository holding only a subset is not a restore source.
4. **Verify** — `restic check` must pass against it.

### 17.1.4 Named executors

Every backup and restore action must name its executor. An action with no named
executor is unscheduled, and an unscheduled backup satisfies no objective in this
section. Verify the timer, not the script.

| §17.1 requirement | Executor |
|---|---|
| Nightly snapshot | `scripts/backup/restic-run.sh` on `ao-restic-backup.timer` |
| Host PostgreSQL dumps | `scripts/backup/backup-host-postgres.sh` |
| All-database dump series | `scripts/backup/dump-all-postgres.sh` on the nightly timer |
| Off-host repository snapshot | **none scheduled — see §19.1 `OPS-30`** |
| Restore drill | `scripts/restore/restore-restic-drill.sh` |
| Repository integrity | `scripts/backup/verify-backup.sh` on `ao-restic-verify.timer` |

### 17.1.5 Recovery objectives

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

### 17.1.6 Restore ordering

Execute restores in this order. Steps 4, 5 and 6 are order-dependent: **step 4
cannot connect without step 5, and step 5 cannot authenticate without step 6.**

1. **Pin the snapshot by intent.** Select it explicitly and record the id; never let
   a tool choose. After an incident the newest snapshot is the one most likely to
   contain the fault being recovered from.

   ```bash
   set -a; . <envfile>; set +a          # source the env file FIRST
   export RESTIC_REPOSITORY=/var/backups/alwayson-restic   # then override
   restic snapshots --tag alwayson
   SNAP=<short_id>
   ```

   **Set `RESTIC_REPOSITORY` after sourcing the env file.** The env file also
   carries that variable and overrides an earlier export, which surfaces as a
   permission-denied `stat` on the repository config and reads like a credential or
   corruption failure.

2. **Restore into an isolated path, never over the live tree.** The drill script
   enforces this by construction and must keep doing so:
   - require an explicit `--scratch` and never default it to a live path;
   - refuse any scratch path resolving inside `/ALWAYSON` after `readlink -m`, so a
     symlink cannot evade the check;
   - refuse a scratch directory that already contains files.

3. **Restore filesystem paths** from the pinned snapshot:

   ```bash
   restic restore "$SNAP" --target "$scratch_abs" \
       --include /ALWAYSON/config --include /ALWAYSON/artifacts \
       --include /ALWAYSON/backups/postgres
   ```

4. **Restore databases in dependency order** — host cluster roles first, then each
   application database. Test each dump's integrity before loading it, and refuse an
   unrecognised label rather than guessing.

   ```bash
   for f in "$scratch_abs"/ALWAYSON/backups/postgres/*/*.sql.gz; do
       gzip -t "$f" || { echo "STOP: corrupt dump $f"; break; }
       label="$(basename "$(dirname "$f")")"     # the directory is authoritative
       case "$label" in
         metabase)  db=metabase;  user=metabase_app         ;;
         grafana)   db=grafana;   user=grafana_app          ;;
         sales)     db=salesdb;   user=sales_migration_role ;;
         mastodon)  db=mastodon;  user=mastodon             ;;
         webodm)    db=webodm;    user=webodm_app           ;;
         *) echo "STOP: unknown dump label '$label'"; break  ;;
       esac
       gunzip -c "$f" | PGPASSWORD="$pw" psql -h 127.0.0.1 -U "$user" -d "$db"
   done
   ```

   **Read the `(label, database, user)` mapping; never derive the database name from
   the filename.** The mapping is the guard table at the top of
   `scripts/backup/backup-host-postgres.sh`, which is the single source of truth. An
   unexpected label is a **stop**, matching that script's own `*)` guard — a restore
   without the guard loads into whatever it is pointed at.

   These are plain SQL dumps (`pg_dump` with no `-Fc`), so `psql` reads the stream.
   `pg_restore` applies only to custom and directory formats.

5. **Recreate missing roles before loading.** `pg_dump --no-owner --no-privileges`
   emits no `CREATE ROLE`, so ownership handling rests entirely on this step.

   ```bash
   psql -h 127.0.0.1 -U postgres -tAc \
     "select rolname from pg_roles where rolname in
       ('metabase_app','grafana_app','sales_migration_role','mastodon','webodm_app')"
   # any name not returned must be CREATE ROLE'd, with its own wallet password,
   # BEFORE step 4 loads anything
   ```

   **A restore that skips this step loads data successfully into a database no
   application can read**, which presents as a working restore and a broken
   application.

6. **Re-provision credentials from KDE Wallet.** Passwords are not in the backup:
   the dump script reads them at dump time and stores none, and the wallet is not in
   any backup. Re-provision the same `(folder, pass_key)` pairs so the restored roles
   can authenticate. A dump restores data, not access.

7. **Re-verify hashes** against the live tree and the restored dumps, using
   `scripts/restore/verify-hashes-and-receipts.sh` or the drill's own step.

### 17.1.7 The backup journal

1. **Record every snapshot attempt** to `/ALWAYSON/logs/backup.log` with actor,
   script, snapshot id and result. A snapshot with no journal entry is not evidence
   of a backup.
2. **Treat a journal id that does not resolve as a defect, not a stale record.**
   When the journal names a snapshot the repository does not hold, correct the
   journal path or the id; do not leave both standing.
3. **Require the journal to prove an incremental chain.** Successive entries must
   reference a parent snapshot; identical ids across nights mean the repository is
   copying one state, not accumulating.

## 17.2 Monitoring

### 17.2.1 Component responsibilities

| Component | Responsibility | Isolation requirement |
|---|---|---|
| Prometheus | the security instrument | independent of Grafana and Metabase in both directions |
| Grafana | dashboards and metric presentation | application state in its own database |
| Metabase | operator reports | read-only against every source |

Monitoring runs in `ao-admin`, which must have no VPN, no explicit allowlist and no
public exposure. Its only permitted outputs are the Grafana dashboard and the
Metabase reports.

### 17.2.2 Required metrics

Monitor at minimum:

| Component | Required metrics |
|---|---|
| Host | CPU, RAM, storage health, disk usage, temperature, GPU state, kernel errors |
| Podman/systemd | Unit state, restart loops, health, image digest |

### 17.2.3 Alerting rules

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

### 17.2.4 Reporting access

1. **Grant reporting read access and deny write access on the same relations.** A
   read-only reporting identity must read a real source successfully *and* be
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

## 17.3 Completion Evidence

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
16. A current list of unresolved blockers, deviations, risks and actions requiring
    human approval.

## 17.4 Restic path set

### 17.4.1 Required coverage

The nightly repository must cover, at minimum:

- `config`
- `artifacts`
- `backups/postgres`
- the `data/` classes `ardupilot`, `corda-install`, `sim-fabrication`, `sales`,
  `mapping`, `field`, `payment`, `ledger`

### 17.4.2 Exclusions

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

### 17.4.3 Confidentiality

State the confidentiality consequence of the path set explicitly. `data/ledger` and
`data/payment` carry provenance and transactional records and belong in the path set;
because restic stores them as ciphertext in a repository on the same disk as the
source, confidentiality rests on the repository password alone. **A restored copy
carries exactly the sensitivity of the live copy — restore grants no privilege
drop.**

### 17.4.4 Restore-drill contract

`scripts/restore/restore-restic-drill.sh` must implement the §17.1.6 ordering and
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
   drill the repository must report the same snapshot count as before it.
5. **Never create a probe artefact from pre-existing project data.** Create probe
   fixtures for the test and remove them afterwards.
6. **Do not count a passing manual check as a scheduled control.** Integrity checking
   exists to catch bit rot and truncation, which develop *after* a drill; only a
   scheduled run closes that gap.

## 17.5 Log retention and the journal root

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

### 17.5.1 Container logging

For every container that writes to a rotated path, the policy must guarantee the
writer follows the rotation. Either:

- enable `copytruncate` for those files, accepting that it briefly duplicates content
  and briefly races writers; or
- add a `postrotate` that signals the container to reopen its log; or
- move the container to `journald` or `k8s-file` under a path the policy does not
  rotate.

**Choose deliberately and record the choice.** Both active options touch a running
service and require operator approval (README §4.1 rule 6).

## 17.6 Backup integrity

1. **Schedule repository integrity checking.** `restic check` is the only control
   that detects a silently corrupted or truncated repository. The 3-2-1 claim in
   §17.1 and every restore-drill result in §17.4 rest on it.
2. **Run it at least weekly.** A one-off manual check is evidence about that moment
   only.
3. **Supply the credential file the verify unit requires.** A verify script whose
   default env path does not exist must fail closed and be reported, not left to exit
   non-zero unnoticed every week.
4. **Verify the deployed unit, not the staged one.** When the deployed unit lags the
   repository copy, the repository is correct and the running system is not.
