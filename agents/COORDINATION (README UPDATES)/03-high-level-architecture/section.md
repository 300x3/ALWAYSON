# 3. High-Level Architecture

## 3.1 Isolation Detail View

This is a **detail view of the ingress/egress portion of the master topology in
ES.2** and must not contradict it. For the whole project, read ES.2.

![Zoom of the controlled adapter column of the ES.2 master topology, at readable scale. The adapters are the only processes permitted to cross the host boundary.](assets/topology-detail-adapters.png)

*Figure 3.1 — The controlled adapter column of the ES.2 master topology, enlarged. It is a
zoom of that one graphic, not a separate diagram: the adapter column is the only place a
controlled ingress or egress process SHALL exist, and every route into or out of the host passes
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
own container. The version behind each row is stated in §3.3.1.

| Database | Holds |
|---|---|
| `salesdb` | Authoritative sales and payment records |
| `mastodon` | Mastodon application state |
| `webodm_dev` | WebODM/PostGIS mapping data |
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

The routing table on `ao-fabrication-db`, the container that owns `a_fab`, holds
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

# ALWAYS ON - expose the host PostgreSQL loopback listener only on the internal
# ao-admin Podman gateway. PostgreSQL itself remains bound to localhost.
GATEWAY=10.42.0.1
$ systemctl --user cat ao-postgres-reporting-bridge.service | grep -i 'Starts at'
# Starts at login with the reporting containers it serves (ao-admin gateway
# address only exists once those containers' networks are created).
```

The script's own comment and the unit description both name the ao-admin gateway; the code
binds the equipment LAN. **The comment is wrong, not the address.** This is the same class of
error as the mount-flag and label-key traps in §6: a comment asserted a property that is
false.

Three consequences:

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

A name is not a mechanism. The error class is **assuming a mechanism from a name**:
"reporting bridge" + "ao-admin" implies the Podman gateway, and only `ss -ltnp` shows the
address a process actually binds. **The gateway a name claims to expose and the address it
exposes can differ by two subnets and an entire security boundary** — bind the address
before relying on it.

#### 3.3.0.2 Domoticz for non-fabrication equipment

No device is connected, and none is to be connected before the equipment exists. This
records the design so it is not re-derived later.

Domoticz is expected to cover other directly connected equipment across the same equipment LAN
(`10.42.0.0/24`) on a planned schedule; the exact expansion scope SHALL be decided by the
operator and recorded as an equipment coverage requirement before any additional device is
connected. It is not part of `ao-fabrication`, is not simulation, and does not write to
`a_fab`; per-machine production data stays with the Moonraker collector above.

**Why the host is the right place, same as the collector.** The desktop holds
`10.42.0.1/24` on `eno1`, so a host process reaches that LAN directly. A
container on an `Internal=true` domain could not (§3.3.0.1). Domoticz running on
the host therefore needs no relay, no opened domain, and no new listener to reach
those devices — the same conclusion already reached for `ao-fabrication-collect`.

**Listener posture.** Domoticz only ever needs to be
reachable from this machine:
- the web UI is started `-wwwbind 127.0.0.1 -nomdns` and serves only
  `127.0.0.1:8080`; the LAN address actively refuses
- the shared server on `*:6144` is disabled (`RemoteSharedPort = 0`) and
  there is no shared-server listener

Neither change affects reaching devices on `10.42.0.0/24`, which is a host-side
path independent of the web listeners. Loopback
`10.42.0.1:8080` is refused.

`a_fab` holds per-machine production data only. It is **not** a ledger, **not** a sales
record, and **not** a backup target. Anything that must become provable leaves
`ao-fabrication` as a signed fabrication manifest through `ao-ledger-ingest`, exactly as
the simulation domain does.

**Network:** `ao-fabrication`, `Internal=true`, `10.89.12.0/24`, created and registered in
`/ALWAYSON/config/platform/network-cidrs.yaml` . The subnet is **pinned** in
`/ALWAYSON/quadlet/networks/ao-fabrication.network` because every other network there lets
Podman auto-assign. See §2.2 for the reconciliation of the adjacent
unregistered `10.89.10.0/24` and `10.89.11.0/24`.
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
| **PostgreSQL 9.5** | WebODM web/worker | Container `ao-webodm-db` on `ao-mapping`, database `webodm_dev` (host-side data dir `~/webodm/dbdata`) | Mapping projects, processing state, users, and geospatial data. **PostGIS is installed in `webodm_dev` (version 2.3.2)** — the geospatial extension lives in the database the app actually reads. The empty `webodm` database in the same container is a 2026-09-30 rollback artefact and is not used. |
| **PostgreSQL 9.5** | NodeODM | The same `ao-webodm-db` container, plus filesystem processing data | Processing-node state and coordination; large image/output artifacts remain filesystem data |
| **PostgreSQL 18** | Corda 5 node | `cordadb` (dedicated Corda PostgreSQL database in the host cluster, per §11.1) | Receipt, entitlement, and provenance state. Built on Corda 5 against `cordadb`. |
| **Redis 8** | Host Redis service | Host Redis database 0 | General low-latency cache/coordination layer; no current application data confirmed |
| **Redis 7** | Mastodon cache/queue service | Container `mastodon-redis`, database 0 | Cache, queues, and background-job coordination; not authoritative business data |
| **Redis 7** | WebODM broker | Container `ao-webodm-broker`, database `broker` | Celery/task broker and worker coordination; not authoritative mapping data |
| **PostgreSQL 18** | Grafana | Grafana application database (dedicated) | Grafana users, dashboards, and datasource configuration. Its own application state, not business data |
| **PostgreSQL 18** | Metabase | Metabase application database (dedicated) | Metabase application schema, saved questions, dashboards, filters, and subscriptions. Not a system of record and never written to by a reporting source |
| **PostgreSQL / MySQL (read-only)** | Metabase reporting sources | Per-source read-only roles | Ad-hoc read-only reporting connections to the business databases. One read-only role per source, with no write, DDL, or owner privilege, so a report cannot modify a source |
| **Prometheus TSDB** | Prometheus | `/prometheus` persistent volume | Security evidence only. Time-series metrics, service health, resource usage, and security evidence. Acts alone and independently of Grafana and Metabase. |
| **SQLite** | MeshChatX / Reticulum MeshChatX | Per-identity database at `~/.reticulum-meshchatx/identities/<identity>/database.db` | MeshChatX messages, rooms, and local Reticulum/MeshChatX application state.
| **SQLite** | QGroundControl | **No application database exists.** Settings are in an INI file and map tiles in a tile cache
| **SQLite** | Akonadi/KDE PIM applications | Akonadi SQLite data | Contacts, calendars, mail indexes, and local personal-information data **Not collected by Prometheus** — excluded by operator instruction: personal and mail-index material is not security telemetry |
| **SQLite** | nPerf | `~/.local/share/nPerf/{history,settings,engine}.db` | Run history and settings; two of the three are snapshotted and read by Grafana. Row counts only — settings values are never selected |
| **SQLite** | Elisa | `~/.local/share/elisa/elisaDatabase.db` | Music library; snapshotted and read by Grafana. Counts only — no titles, artists or paths |
| **SQLite** | Klipper | `~/.local/share/klipper/history3.sqlite` | Clipboard history. **Never snapshotted, metadata only, by design** — a snapshot would copy clipboard content (which can include passwords and tokens) into a world-readable file, which README §4.1 rule 5 forbids |
| **SQLite** | libaccounts-glib | `~/.config/libaccounts-glib/accounts.db` | Account identifiers. **Never snapshotted, metadata only**, same reason as Klipper |
| **SQLite** | Firefox, Brave, Chrome, and Edge | Browser profile SQLite stores | Browser history, site storage, caches, certificates, and profile data **Not collected by Prometheus** — excluded by operator instruction: browsing material is not security telemetry.
| **SQLite** | Podman | Rootless container metadata store | Container, image, network, and volume metadata; not application data BoltDB, not SQLite, so not a Prometheus collector target |
| **Filesystem/local metadata — social** | LM Studio and OpenClaw | Application files, model settings, and local state | Sales/social AI application state that is not automatically part of SQL reporting.
| **Filesystem/local metadata — drone/field** | ArduPilot, MeshChatX/Reticulum field stores, and radio gateway logs | Application files, telemetry spools, and local state | Field operational and engineering data that is not automatically part of SQL reporting |
| **Filesystem/local metadata — sim** | Gazebo, ROS 2, ArduPilot SITL, and simulation tools | Project files, worlds, models, and result artifacts | Simulation operational and engineering data that is not automatically part of SQL reporting |

This table records what each database is and which program uses it. Whether a database is
built and provisioned is status, recorded in §19.1 alongside the work to build it.

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
reports and receipts listed in §15.1. Before enabling blockchain-related
flows, complete the Corda key/certificate ceremony and implement the
ledger-ingest manifest, correlation-ID, signature, idempotency, and audit
requirements.

---
