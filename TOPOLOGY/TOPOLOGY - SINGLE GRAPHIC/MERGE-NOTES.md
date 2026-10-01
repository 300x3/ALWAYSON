# Merge notes — single landscape topology

**Graphic:** `alwayson-single-topology.svg` (vector) · `.pdf` · `.png` (200 dpi)
· `.html` (self-contained, works offline) · `.json` (machine contract)
**Generator:** `build_svg.py` — edit this, then re-run `python3 build_svg.py`.

Source: `../ALWAYS ON — Architecture, Operations, and Status - v6.md`.
Nodes are the **expected-to-be-installed** system (v6 §3.2), not the observed
live state. Authority order unchanged: v6 → `/ALWAYSON/README.md` →
`config/platform/topology-model.yaml` → generated output.

## The 17 sources and where each one lives

| Source | Lands in |
|---|---|
| ES.2 Master Topology | the whole six-band spine |
| 3.1 Isolation Detail View | bottom strip "THE ONE ROUTE EVERYTHING TAKES" |
| Pages 12–16 (sheets 3.1.1a–e) | container/CIDR facts folded into the domain nodes |
| 3.3.2 Reporting + Ledger flow | merged with 11.2.1 → one reporting path |
| 4.4 Approved Internal Paths | 6 manifest edges into ingest + the 3 bypass paths |
| 7.1.1 Sales-link plan | flow node "1 · Catalogue to checkout" |
| 7.3 Sales and Receipt Sequence | flow chain 1 → 5 in band 6 |
| 8.2 Required Directory Tree | "500GBPHOTOGRAM drive" node |
| 8.3 Mapping Processing Flow | Mapping · ingest / process / export |
| 8.6.4 Cross-reference Flow | CAD → Model registry → Corda state |
| 9.1 Drone-Side System | Raspberry Pi 5 + ArduPilot 3DR N1 (marked OFF-HOST) |
| 9.2.1 MeshChatX Port | MeshChatX `:18000`, WebODM `:8000`, Reticulum `:4242` |
| 10 Vehicle Simulation | `ao-sim-vehicle` + Gazebo + ROS 2 |
| 10.2.c Storage/Shelving | "Storage to shelf to robot" |
| 11.2 Ledger Flow | `ao-ledger-ingest` gate + the eight mandatory controls |
| 11.2.1 Sales/marketing reporting | Correlation tuple + Metabase read-only views |
| 15.4.3 Edge, TLS, Network Path | Cloudflare edge → cloudflared → 127.0.0.1:3000 |

## Dedup decisions (why nothing is stated twice)

1. **§3.1 + §4.4 + §7.3 + §11.2 are one pipeline.** They are not drawn as four
   flowcharts. There is a single `ao-ledger-ingest` gate; the nine §4.4 paths
   are its edges, and §7.3's ordering is band 6 steps 1–5.
2. **§3.3.2 + §11.2.1 are one reporting flow.** One PostgreSQL → Metabase edge
   (read-only views) and one Prometheus → Grafana edge.
3. **All nine §4.4 paths are approved paths; none of them "bypasses" anything.**
   Six are manifests into the ledger-ingestion gateway and are drawn as such.
   The other three — ledger status → authorised service, signed mission release
   → field mission-release service, validated image set → WebODM intake — are
   drawn separately because they are *not manifests into the ledger*, not because
   they escape the controls: v6 §4.4 places all nine under the same eight
   mandatory controls. Collapsing them would have deleted them.
4. **The eight §4.4 controls are a contract, not decoration** — they are
   rendered as a checklist under the route strip, not as edge labels.
5. **ES.2 + the generated sheets.** ES.2 gives structure; the sheets contribute
   only observed facts not already in ES.2. The README calls the sheets
   "evidence of observed state, not a second source of truth", so they are not
   given their own boxes.

## Deliberate omissions, and why

- **Gazebo render thumbnails (§10.2a/b/c).** The three PNGs are referenced by
  filename in the source; embedding rasters would add ~2 MB and cost
  legibility. The *flow* they illustrate is drawn.
- **`rankdir=TB` layout.** The source records this as tried and rejected
  (v6 §3.1.1, "19–40:1, unreadable"). Layout here is computed, not auto-ranked.
- **Undeclared running containers** (`300x3-web`, `-sidekiq`, `-streaming`,
  `-db`, `-redis`, `-proxy`) are **not** nodes. They have no
  `/ALWAYSON/quadlet/` definition and are drift, not design.

## Known drift NOT resolved here (operator decision)

- `topology-inventory.json` records `mastodon-db-placement` as **drift**: v6 §3.3
  says mastodon state is consolidated onto host PostgreSQL 18.6, but a
  container-scoped `mastodon-db` is running on `ao-sales`. The graphic shows
  **design intent** and does not silently assert either side.
- Network count: README §3.2 and `config/platform/network-cidrs.yaml` say ten
  internal `ao-*` networks; the live inventory counts 15 total (10 internal,
  2 egress, 3 planned adapters). The graphic draws the ten internal domains and
  the adapters separately.
- `Reticulum` `Public Gateway` listens on `0.0.0.0:4242`, which v6 §9.4 notes is
  **not** loopback-restricted. Shown on the node so it is not read as safe.

## Verification performed

- SVG parses as valid XML; PNG/PDF render without error.
- 58 nodes, 68 edges. No duplicate titles, no duplicate ids, no duplicate
  edges, no dangling references.
- 40 distinct v6 sections cited across nodes; every requested section is
  represented (4.4 via the route strip).
- **Role split, corrected 2026-09-29: Grafana is METRICS, Metabase is REPORTS.**
  The two node captions and the `SQL, by local program` line were transposed
  and now read: Metabase = "REPORTS — business and ad hoc analysis" (SQL over
  read-only views, sales/orders/marketing); Grafana = "METRICS — operational,
  live and business" (dashboards, alerts, PDF export; Prometheus + PostgreSQL
  sources); SQL line = "metrics → grafana · reports → metabase". Authority is
  v6 §6.A, which defines Grafana as operational monitoring and visualization
  ("metrics, service health, alerts, queue depth, latency, resource use…") and
  Metabase as FOSS relational reporting ("sales, orders, receipts, fulfillment,
  entitlements, returns, approved support summaries…"). The edges were already
  correct and were not changed: Prometheus → Grafana = metrics, PostgreSQL →
  Metabase = read-only views, PostgreSQL → Grafana = datasource.
- **Node `d_sql` retitled to SQLite, 2026-09-29.** It read "SQL, by local program"
  with purpose "Which database answers which program" and a program → database
  routing list. That routing duplicated the PostgreSQL node's job (whose details
  already list `salesdb · mastodon · webodm · grafana · metabase · cordadb ·
  postgres`) and said nothing about SQLite. It is now: title **SQLite**, purpose
  "The database engine itself — one file per program, never the record",
  details "MeshChatX · QGroundControl · and the other local tools that keep
  state", sec `3.3` (the `6.A.2` GUI-tools reference went with the routing list).
  "Never the record" is the standing rule from v6 §3.3 and
  `config/platform/topology-model.yaml`, which classifies every SQLite store as
  `authority: not_authoritative` / `not_an_application_db`.
  **Evidence asymmetry, recorded deliberately:** MeshChatX is confirmed by file
  probe — `~/.reticulum-meshchatx/plugins/plugin_state.db` and
  `~/.reticulum-meshchatx/identities/<id>/database.db` are both "SQLite 3.x
  database" per `file`. QGroundControl has **no** SQLite store on this host; only
  `~/.config/QGroundControl/QGroundControl.ini` (531 bytes) and an empty cache
  exist, with no reference to a database in the ini. Naming it is therefore
  design intent (v6 lists QGC under filesystem/local metadata and the AppImage
  is installed at `~/Applications/QGroundControl-x86_64.AppImage`), consistent
  with this graphic being the expected-to-be-installed system, not observed
  state. Re-verify with `file` before treating QGC as evidenced.
- **`ao-sim-fabrication` described, 2026-09-29.** Now "Rehearses robot-arm
  maintenance and assembly, and runs the kitchen", details `MainsailOS per
  machine · 3D printers, CNC`, note "Headless verified; GUI workflow pending
  (6.A.1)" taken from `config/platform/topology-model.yaml`. Authority: v6 §10.2
  (robot-arm cells and assembly stations, 3D-printer / LPBF / storage / kitchen /
  pass-through models, `ROS_DOMAIN_ID=22`, `GZ_PARTITION=alwayson_fabrication_sim`)
  and v6 line 60, which places MainsailOS / Mainsail / Moonraker / Klipper on
  printer-local BigTreeTech CB1 / RPi. **Open question for the operator:** v6 line
  61 records "CNC | No bCNC or current CNC software claim", so CNC is drawn as a
  machine class only and no CNC software is asserted anywhere.
- **Addresses belong to nodes, not pathway lines, 2026-09-29.** Three edge labels
  carried socket addresses: `a_tun → w_sales` "127.0.0.1:3000", `h_pg → d_pg`
  "127.0.0.1:5432", `h_webodm → w_map` "127.0.0.1:8000". The last two were pure
  duplicates — the address already sat on the owning node. `ao-sales` now carries
  "Web origin 127.0.0.1:3000" (v6 §15.4.3; verified live — Mastodon web
  `127.0.0.1:3000`, streaming `:4000`), `cloudflared-alwayson` keeps only
  "Cloudflared connector / Origin stays loopback", and the three labels became
  relational: "tunnel to loopback origin", "local socket only", "loopback UI". The
  four `DOMAIN_ID=21/22` edge labels were duplicates of node details and are now
  "flight rehearsal", "factory rehearsal", "flight world", "factory world"; the
  IDs remain on the `ao-sim-vehicle` / `ao-sim-fabrication` nodes.
- **The "deliberately bypass the gate" claim was false and is removed,
  2026-09-29.** v6 §4.4 never uses the word: it lists nine approved internal
  paths and then states "All cross-domain requests require" the same eight
  controls. The operator further confirmed all three are gated in practice —
  ledger status leaves a core that sits behind the ingest gate; the signed
  mission release travels MeshChatX (local) → QGroundControl on the Raspberry Pi
  for each drone when a message is sent; validated image sets are already gated
  and move by WiFi into a WebODM folder only after the drone lands at the hangar,
  over a dedicated drone → desktop sync network, then WebODM processing. The strip
  now reads "Three more approved paths, same eight controls:".
