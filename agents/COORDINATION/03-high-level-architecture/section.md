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

**What I got wrong earlier, and why.** This section previously described the reporting bridge
as the container-to-host-PostgreSQL mechanism and cited §3.3.0.1 for it without checking what
address it bound. The error class is assuming a mechanism from a name: "reporting bridge" +
"ao-admin" implied the Podman gateway, and I never ran `ss -ltnp` to see the actual bind
address. The gateway it claims to expose and the address it exposes differ by two subnets and
an entire security boundary.

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

**Correction to my own text, immediately after writing it.** The first draft of this
paragraph said the block was "contiguous and gap-free" and that `10.42.0.0/24` was the only
non-`ao-` addressing on the host. **Both statements are wrong**, and I am recording that
because they are the kind of claim that survives into someone else's security argument.

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

**Correction to that correction — the Wi-Fi address is not undocumented.** I wrote that §3
describes the host as having only the equipment LAN, and having just recompiled the README I
checked whether that was true elsewhere in the document rather than only in my own section.
It is not: the Wi-Fi address appears in at least two other sections.

```
README.md:2173  | Host address | `192.168.87.135/24` on `wlp3s0` |
README.md:5572  MeshChatX is bound to 0.0.0.0:4242; the host had 192.168.87.135/24 on Wi-Fi
```

So the accurate statement is narrower: the Wi-Fi interface is documented elsewhere and
**absent from §3**, not absent from the README. That is a consistency gap in one section,
not a gap in the project record — a meaningfully different thing, and the difference
matters for whether anyone needs to act. MeshChatX binding `0.0.0.0` while the host holds a
Wi-Fi address looks like a genuine exposure question, but it belongs to the COMM/NET groups
and I am recording the pointer rather than opening it.

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
