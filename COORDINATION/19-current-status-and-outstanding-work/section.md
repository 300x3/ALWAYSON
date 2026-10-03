# 19. Current Status and Outstanding Work

The single status log. Every component and every item of outstanding work, with nothing
stated twice.

| Part | What it is |
|---|---|
| **19.1** | The log — components with their status, then open work by group |
| **19.2** | Completed items and verification evidence — finished work with the evidence that closed it, then the standing checks |
| **19.3** | Operator setup priorities — the operator's own ordering of the work |

A component appears once, in the COMPONENTS block, and nowhere else. An open task appears
once, in its work group, and nowhere else. A completed item keeps the exact columns of §19.1, so a row moves between the two tables
without rewriting it. The ID is carried across verbatim; rows closed before IDs existed
show `—`.

Items are keyed by work-group prefix, then numbered within the group, so an ID can never
collide and a new item never renumbers an existing one.

| Prefix | Work group |
|---|---|
| `PLAT` | Platform, install and runtime |
| `NET` | Networks, adapters and isolation |
| `SEC` | Secrets, credentials and identity |
| `LEDGER` | Ledger, accounting and provenance |
| `PAY` | Payments, sales and storefront |
| `COMM` | Community, federation and local AI |
| `FIELD` | Field, radio and drones |
| `SIM` | Simulation and fabrication |
| `OPS` | Backup, monitoring, logs and scripts |

## 19.1 The log

<table>
<thead>
<tr>
<th align="left" width="4%">ID</th>
<th align="left" width="13%">Item</th>
<th align="left" width="5%">Component</th>
<th align="left" width="7%">Status</th>
<th align="left" width="11%">Standard served</th>
<th align="left" width="60%">Current state or acceptance criteria</th>
</tr>
</thead>
<tbody>
<tr>
<td valign="top"><strong>COMPONENTS</strong></td>
<td valign="top">The state of each component. Source of truth for what is built.</td>
<td valign="top"></td>
<td valign="top"></td>
<td valign="top"></td>
<td valign="top"></td>
</tr>
<tr>
<td valign="top">ST-01</td>
<td valign="top">Host platform — Kubuntu, Podman, Quadlet, protected administration</td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">—</td>
<td valign="top">Host inventory and base platform verified. <strong>Measured baseline:</strong> kernel <code>7.0.0-34-generic</code>; Podman <code>5.7.0</code>; <strong>fourteen</strong> <code>ao-*</code> networks — eleven <code>Internal=true</code> and three <code>Internal=false</code> (<code>ao-sales</code>, <code>ao-reporting-egress</code>, <code>ao-build-update</code>) — matching <code>config/platform/network-cidrs.yaml</code> (§2.2); NVIDIA GTX 1080 on driver <code>580.178.04</code> with CDI devices registered and <code>/var/run/cdi/nvidia.yaml</code> authoritative; ROS 2 Lyrical + Gazebo Sim <code>10.5.0</code>; PostgreSQL `<code> and Redis </code>8.0.5<code>, both loopback-only. The </code>/etc/cdi/nvidia.yaml` copy is not authoritative and is regenerated or removed at each driver change</td>
</tr>
<tr>
<td valign="top">ST-02</td>
<td valign="top">Domain isolation — eleven internal workload networks</td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">—</td>
<td valign="top">Isolation test verified; all workload networks <code>Internal=true</code> except <code>ao-sales</code>, which is non-internal for ActivityPub delivery only</td>
</tr>
<tr>
<td valign="top">ST-03</td>
<td valign="top">Mapping — WebODM and the photogrammetry drive</td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented with deviation</strong></td>
<td valign="top">—</td>
<td valign="top">GPU-enabled smoke test completed, orthophoto produced. Five <code>ao-</code> Quadlet units on <code>ao-mapping</code> (<code>Internal=true</code>): <code>ao-webodm-{webapp,worker,db,broker}</code> and <code>ao-nodeodm</code>. No published port; images enter and leave via local folders on <code>/media/scottw/500GBPHOTOGRAM</code> (<code>incoming/</code> -&gt; <code>webodm/</code> -&gt; <code>exports/</code>,<code>deliverables/</code>). The app reads database <code>webodm_dev</code> in <code>ao-webodm-db</code>; the 10 projects/10 tasks that lived in a duplicate host-cluster <code>webodm</code> database were migrated in and the duplicates dropped 2026-09-30, backups in <code>backups/duplicate-db-20260930/</code></td>
</tr>
<tr>
<td valign="top">ST-04</td>
<td valign="top">Field, Reticulum, and LoRa — RPi5, Waveshare LoRa, Heltec V3, MeshChatX</td>
<td valign="top">—</td>
<td valign="top"><strong>In progress</strong></td>
<td valign="top">—</td>
<td valign="top">Both Heltec LoRa 32 V3/SX1262 RNodes functional and initialized by MeshChatX; <code>PEOPLE-RADIO</code> 915 MHz/125 kHz, <code>DRONE-RADIO</code> 917 MHz/250 kHz; 32 interfaces configured, none explicitly disabled; RF feedback observable on both bands</td>
</tr>
<tr>
<td valign="top">ST-05</td>
<td valign="top">Reticulum runtime and connectivity</td>
<td valign="top">—</td>
<td valign="top"><strong>Partial</strong></td>
<td valign="top">—</td>
<td valign="top">Auto-connections, peering, and announces work; timeouts, network-unreachable errors, and refusals also appear. 29 TCP clients enabled. Evidence in §19.2</td>
</tr>
<tr>
<td valign="top">ST-06</td>
<td valign="top">MeshChatX version provenance</td>
<td valign="top">—</td>
<td valign="top"><strong>Complete with verification pending</strong></td>
<td valign="top">—</td>
<td valign="top">Declared 4.9.1; hash matches the local manifest. Evidence in §19.2</td>
</tr>
<tr>
<td valign="top">ST-07</td>
<td valign="top">Vehicle simulation — <code>ao-sim-vehicle</code></td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented (headless runtime)</strong></td>
<td valign="top">—</td>
<td valign="top">Headless Gazebo 300-iteration and ROS-Gazebo bridge tests passed; ArduPilot SITL HEARTBEAT validated over MAVLink. <code>ao-ardupilot-sitl</code> is <strong>enabled=false and stopped by design</strong> — the simulator is started on demand, so <code>inactive</code> here is the expected state, not a fault. The four baseline capabilities required by ES.1 — 3D world setup, boning, reinforcement learning objects, and an HTML portal to operation — are outstanding</td>
</tr>
<tr>
<td valign="top">ST-08</td>
<td valign="top">Fabrication and facility simulation — <code>ao-sim-fabrication</code></td>
<td valign="top">—</td>
<td valign="top"><strong>Partly implemented</strong></td>
<td valign="top">—</td>
<td valign="top">Delivered: the 3D world and its boned cell datums, eight cameras derived from those datums, the view-only HTML portal, and the local Foxglove 3D viewer. Headless Gazebo 300-iteration and bridge test passed; model views rendered in §10.2. <strong>Not delivered</strong>, though named in the §10.2 component tree: the facility scheduler (item 81), the safety-zone and interlock model (item 82), and RL objects as world entities rather than a catalogue (item 83)</td>
</tr>
<tr>
<td valign="top">ST-09</td>
<td valign="top">Ledger core — Corda on <code>cordadb</code></td>
<td valign="top">—</td>
<td valign="top"><strong>Blocked</strong></td>
<td valign="top">—</td>
<td valign="top">Corda 5.2.2 <strong>CLI installed</strong> 2026-09-30, SHA-256 verified; <strong>no node</strong> — <code>cordadb</code> holds 0 tables and its owner role has no working password, so <code>preinstall check-postgres</code> cannot pass. Details in this document.1. Corda 4 and its H2 database were removed 2026-09-28 with no data migrated Outstanding: <strong>Deferred by operator 2026-09-30 until the rest of the system is complete</strong>, so the ledger opens with real entries rather than test data. Then complete the key and certificate ceremony (§11.1) and create the node</td>
</tr>
<tr>
<td valign="top">ST-10</td>
<td valign="top">Ledger ingestion gateway — <code>ao-ledger-ingest</code></td>
<td valign="top">—</td>
<td valign="top"><strong>Planned</strong></td>
<td valign="top">—</td>
<td valign="top">mTLS validation, authorization, audit, and idempotency specified; not deployed</td>
</tr>
<tr>
<td valign="top">ST-11</td>
<td valign="top">Sales and orders — <code>ao-sales</code> database</td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">—</td>
<td valign="top">Sales DB deployed; order, receipt, and fulfillment records supported</td>
</tr>
<tr>
<td valign="top">ST-12</td>
<td valign="top">Payment adapters — <code>ao-ingress-payment</code></td>
<td valign="top">—</td>
<td valign="top"><strong>In progress</strong></td>
<td valign="top">—</td>
<td valign="top"><strong>Deployed 2026-10-01</strong> on <code>ao-payment</code> (its own domain, §5.1 one-network rule respected). Adapter, host relay, and reconciliation CLI written; PayPal signature verification, replay guard, and Zelle manual-only refusal tested and passing. Schema: Zelle casing normalised to <code>Zelle</code> across DB and JSON schema; reconciliation columns added to <code>payment_references</code>. <strong>Not enabled against live traffic</strong> — the four <code>ao-payment</code> wallet entries do not exist yet, so it runs with no DSN and no webhook secret and cannot accept a payment Outstanding: Create the four <code>ao-payment</code> wallet entries, then approve enabling the Cloudflare Tunnel route to <code>127.0.0.1:8900</code> (§7.2)</td>
</tr>
<tr>
<td valign="top">ST-13</td>
<td valign="top">Mastodon local stack</td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented (live on <code>scottw</code>)</strong></td>
<td valign="top">—</td>
<td valign="top"><strong>2026-10-01 load test: 100 signed mentions from <code>300x3@mastodon.social</code> -&gt; local instance, all delivered, processed and answered by the bot with zero container restarts, zero OOM kills and all six sidekiq queues draining to 0. Timeline then wiped by operator instruction: keep only 2026-09-03..09-11, delete everything else. Local: 124 statuses/mentions destroyed via <code>Status#destroy</code> (federated Deletes sent), accounts and follow relationships preserved. mastodon.social: originals deleted through the operator's authenticated session in three rate-limited windows (~40 deletions per 30-minute window). Verified after the final pass: the profile retains only 3 Sept, 4 Sept and 11 Sept posts, with </strong>no posts outside the 09-03..09-11 keep range<strong>. Backup: <code>backups/mastodon-status-wipe-2026-10-01/</code>. All 5 containers active under <code>scottw</code> in the single <code>ao-sales</code> store; <code>ao-sales</code> is <code>Internal=false</code> so Sidekiq can deliver ActivityPub. Database migrated (100 tables). <code>LOCAL_DOMAIN=mastodon.300x3.com</code> (300x3.com is the filedn storefront and is not routed here). Env wallet-backed via <code>%h/.local/share/ao-secrets/</code>, <code>RAILS_FORCE_SSL=false</code> (inert — upstream hardcodes <code>config.force_ssl = true</code>; see §9.2.1 for why the local UI is served over TLS by the loopback proxy instead). v4.3.7; WebFinger resolves; Sidekiq 6.5.12 processing; outbound 443 open. Accounts <code>@admin</code> (Owner, renamed from <code>aoadmin</code> on 2026-10-01) and <code>@bot</code> verified authenticating with KDE Wallet passwords — the email stays <code>admin@300x3.com</code>. <code>admin</code> is a reserved username only via this instance's <code>reserved_usernames</code> </strong>setting<strong>, which was edited to free the name; the old <code>.../users/aoadmin</code> URI is retained as <code>alsoKnownAs</code> so remote servers follow the rename. </strong>Rename trap:<strong> a Mastodon rename does </strong>not** rewrite <code>inbox_url</code>/<code>outbox_url</code> either — the first attempt left the account advertising a dead <code>.../users/aoadmin/inbox</code> (404), so inbound follows were silently dropped with no error on either side. Always cross-check <code>inbox_url</code> against <code>uri</code> after any rename Outstanding: Confirm remote-to-remote delivery and a reverse follow</td>
</tr>
<tr>
<td valign="top">ST-14</td>
<td valign="top">Mastodon federation edge — Cloudflare Tunnel</td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented (bidirectional)</strong></td>
<td valign="top">—</td>
<td valign="top">Tunnel active; HTTP/2 connector up; WebFinger 200 for <code>acct:admin@mastodon.300x3.com</code>. <strong>Inbound proven</strong>: signed <code>POST /inbox</code> from <code>mastodon.social</code> and <code>avision-it.social</code> return 202. <strong>Outbound proven</strong>: <code>@bot</code> follows <code>@Gargron@mastodon.social</code> and the remote returned a signed activity recorded as a reverse follow. The earlier silent outbound failure was an instance actor with empty <code>uri</code>/<code>inbox</code>, now repaired on every web start</td>
</tr>
<tr>
<td valign="top">ST-15</td>
<td valign="top">OpenClaw and LM Studio support chat</td>
<td valign="top">—</td>
<td valign="top"><strong>In progress</strong></td>
<td valign="top">—</td>
<td valign="top">Local stack in progress; OAuth/client issues recorded</td>
</tr>
<tr>
<td valign="top">ST-16</td>
<td valign="top">Konqueror — dedicated automation browser</td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">—</td>
<td valign="top">Designated as the automation browser in ES.1</td>
</tr>
<tr>
<td valign="top">ST-30</td>
<td valign="top">Real fabrication — <code>ao-fabrication</code></td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented — network, database and collector operational; machines are on only while in use</strong></td>
<td valign="top">—</td>
<td valign="top">Network <code>Internal=true</code> on the pinned <code>10.89.12.0/24</code>, registered (§2.2). Host-side pull-only collector writes into <code>a_fab</code> (loopback 127.0.0.1:15433, role <code>fabrication_role</code>); <code>ao-fabrication-db</code> and the collector timer are active. Machines are powered on only while in use, so an unreachable machine is expected: the collector reports it as <code>offline</code> and exits 0 rather than as a failure. Credential created 2026-09-30 in KDE Wallet (<code>fabrication-db-password</code>); <code>~/secrets/fabrication-db.env</code> is 0600. Note <code>pg_hba</code> trusts 127.0.0.1, so the role password must be set explicitly or TCP auth fails while the socket appears to work</td>
</tr>
<tr>
<td valign="top">ST-17</td>
<td valign="top">Sale-transfer egress — <code>ao-egress-archive</code></td>
<td valign="top">—</td>
<td valign="top"><strong>Partially implemented</strong></td>
<td valign="top">—</td>
<td valign="top">Local <strong>restic backup and restore validation complete</strong> (§17.1 — this is the backup). IPFS/pCloud <strong>sale transfer</strong> not yet exercised. <strong>Not a backup by design</strong> (§11.6).</td>
</tr>
<tr>
<td valign="top">ST-18</td>
<td valign="top">Backup and restore</td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">—</td>
<td valign="top">Restic repository <code>/var/backups/alwayson-restic</code> holds <strong>24 snapshots</strong>; cited IDs <code>548d9910</code> and <code>32be2a1c</code> both verified present. Hash validated; database 14/14 tables restored. Schedule automated: <code>ao-restic-backup</code> nightly 03:30, <code>ao-restic-verify</code> weekly Sun 04:30, DB dumps 03:00. <strong>Timers renamed today and have not yet fired</strong>, so the newest snapshot is still 2026-09-24. The 03:00 dump path was rebuilt the same day after dropping duplicate host databases broke it</td>
</tr>
<tr>
<td valign="top">ST-19</td>
<td valign="top">Monitoring — Prometheus, node_exporter, Grafana</td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented (data collection)</strong></td>
<td valign="top">—</td>
<td valign="top">All three run as <code>scottw</code> Quadlet units on <code>ao-admin</code>; all targets scrape <code>up</code>. <strong>Prometheus is isolated: nothing queries it and nothing acts on it</strong> (§17.2). It now holds 13 <code>alwayson_db_*</code> series covering PostgreSQL and SQLite, collected read-only on the host every 60s. Evidence in §19.2</td>
</tr>
<tr>
<td valign="top">ST-20</td>
<td valign="top">Metabase ad-hoc reporting</td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented (login surface); application database outstanding</strong></td>
<td valign="top">—</td>
<td valign="top">Runs on the host and serves its login page in the browser, which is the expected operator surface. It reports ad-hoc and read-only over the PostgreSQL and MySQL databases and local SQLite files, so it needs <strong>its own PostgreSQL application database</strong> for its schema, saved questions, dashboards, and subscriptions (§3.3). Evidence in §19.2</td>
</tr>
<tr>
<td valign="top">ST-21</td>
<td valign="top">QGroundControl mission planning</td>
<td valign="top">—</td>
<td valign="top"><strong>Planned</strong></td>
<td valign="top">—</td>
<td valign="top">Desktop primary planning with a KaliOS RPi5 fallback; headless simulation and the ROS-Gazebo bridge verified</td>
</tr>
<tr>
<td valign="top">ST-22</td>
<td valign="top">Field gateway and link-quality display</td>
<td valign="top">—</td>
<td valign="top"><strong>In progress</strong></td>
<td valign="top">—</td>
<td valign="top">Heltec V3 connection and a stable serial path verified 2026-08-31; gateway service deployment pending</td>
</tr>
<tr>
<td valign="top">ST-23</td>
<td valign="top">Reporting and database administration identities</td>
<td valign="top">—</td>
<td valign="top"><strong>Planned</strong></td>
<td valign="top">—</td>
<td valign="top">PostgreSQL is loopback-only. Metabase needs one read-only role per reporting source; Grafana reads approved existing datasources; both keep their own application databases separate from every source database Outstanding: Define the Metabase application database, the per-source least-privilege read-only roles, and the Grafana/Metabase administration roles and views</td>
</tr>
<tr>
<td valign="top">ST-24</td>
<td valign="top">KDE Wallet secret delivery to Quadlet services</td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">—</td>
<td valign="top">Services consuming Wallet secrets start after Plasma login; the ~60s wait is the bounded startup allowance</td>
</tr>
<tr>
<td valign="top">ST-25</td>
<td valign="top">GPU scheduling and admission</td>
<td valign="top">—</td>
<td valign="top"><strong>Planned</strong></td>
<td valign="top">—</td>
<td valign="top">Driver and CDI verified; CPU baseline and GPU smoke completed. Evidence in §19.2</td>
</tr>
<tr>
<td valign="top">ST-26</td>
<td valign="top">Ledger/Corda operator console</td>
<td valign="top">—</td>
<td valign="top"><strong>Blocked</strong></td>
<td valign="top">—</td>
<td valign="top">Narrow operator-management path specified; no public access</td>
</tr>
<tr>
<td valign="top">ST-27</td>
<td valign="top">Payment-provider dashboard</td>
<td valign="top">—</td>
<td valign="top"><strong>Blocked</strong></td>
<td valign="top">—</td>
<td valign="top">Provider-hosted, provider-authenticated workflow Outstanding: Open on payment-provider selection (ST-12)</td>
</tr>
<tr>
<td valign="top">ST-28</td>
<td valign="top">Home automation — Domoticz on RPi</td>
<td valign="top">—</td>
<td valign="top"><strong>Planned</strong></td>
<td valign="top">—</td>
<td valign="top">Specified in ES.1 as the usual Domoticz feature set including cameras and weather</td>
</tr>
<tr>
<td valign="top">ST-29</td>
<td valign="top">GUI-less controlled data services (<code>ao-data</code>)</td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented as intentional design</strong></td>
<td valign="top">—</td>
<td valign="top">Host services remain loopback-only; administration uses dedicated host or <code>ao-admin</code> identities</td>
</tr>
<tr>
<td valign="top"><strong>OPEN WORK</strong></td>
<td valign="top">Everything still to be done, by group.</td>
<td valign="top"></td>
<td valign="top"><strong>Open</strong></td>
<td valign="top"></td>
<td valign="top"></td>
</tr>
<tr>
<td valign="top"><strong>PLAT</strong></td>
<td valign="top">Platform, install and runtime</td>
<td valign="top"></td>
<td valign="top"><strong>Open</strong></td>
<td valign="top"></td>
<td valign="top"></td>
</tr>
<tr>
<td valign="top">PLAT-01</td>
<td valign="top"><strong>Mapping runtime designation</strong></td>
<td valign="top">ST-03</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§13.2</td>
<td valign="top">WebODM runtime finally designated rootless, system-level, or mixed, and the mixed-store deviation in §13.2 closed or confirmed.</td>
</tr>
<tr>
<td valign="top">PLAT-02</td>
<td valign="top">Version matrix refresh</td>
<td valign="top">ST-01, ST-25</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§4.1 rule 9</td>
<td valign="top"><strong>Partly done 2026-10-01.</strong> The <code>mastodon</code> rows now record the digests actually in use (they recorded tags, understating the pinning), <code>local_domain</code> corrected to <code>mastodon.300x3.com</code>, and the <code>RAILS_FORCE_SSL=true</code> note replaced — those switches are inert, and the local UI is served over TLS by the loopback proxy at <code>https://127.0.0.1:3300</code>. A new <code>operations</code> section records the Grafana/Metabase/Prometheus/node-exporter digests. <strong>Remaining:</strong> still hand-edited rather than captured, and the Gazebo <code>nginx:alpine</code> row is knowingly unpinned.</td>
</tr>
<tr>
<td valign="top">PLAT-03</td>
<td valign="top"><code>apparmor-utils</code> and GPU toolkit packages</td>
<td valign="top">ST-01, ST-25</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§12.3</td>
<td valign="top">Install list omits packages that later verification blocks assume exist (<code>aa-status</code> check, CDI/GPU access). Reconcile the install list with the verification steps.</td>
</tr>
<tr>
<td valign="top">PLAT-04</td>
<td valign="top">Asserting install verification</td>
<td valign="top">ST-01, ST-25</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§12.3</td>
<td valign="top">The §12.3 verify block prints values without asserting them, and the cgroup check is silent on failure. Add real assertions.</td>
</tr>
<tr>
<td valign="top"><strong>NET</strong></td>
<td valign="top">Networks, adapters and isolation</td>
<td valign="top"></td>
<td valign="top"><strong>Open</strong></td>
<td valign="top"></td>
<td valign="top"></td>
</tr>
<tr>
<td valign="top">NET-01</td>
<td valign="top"><strong>Controlled ingress/egress adapters</strong></td>
<td valign="top">ST-12, ST-17</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§5.2</td>
<td valign="top"><code>ao-build-update</code> <strong>scaffolded and deployed, not enabled</strong> (§5.2.1): its own <code>Internal=false</code> egress network at <code>10.89.13.0/24</code>, digest-pinned unit, read-only registry allowlist, and acquisition script that resolves candidates, captures digests, and writes an update audit record with no promotion authority. <strong>Remaining:</strong> operator decision on enabling it, and the <code>build</code>/<code>update</code> scope question. <code>ao-ingress-payment</code> and <code>ao-egress-archive</code> still require implementation with destination allowlists, validated TLS, separate credentials, and connection logging. Community publication is carried inside <code>ao-sales</code>.</td>
</tr>
<tr>
<td valign="top">NET-02</td>
<td valign="top"><strong>CIDR reconciliation in <code>network-cidrs.yaml</code></strong></td>
<td valign="top">ST-02</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§2.2</td>
<td valign="top"><strong>Partly done 2026-09-30:</strong> all three CIDRs registered and validation green (<code>OK: all domain networks present; isolation domains internal-only</code>); the generated-registry list in <code>check-network-isolation.sh</code> updated so the entries persist. <strong>Remaining:</strong> the <code>ao-egress-community</code> name/CIDR reconciliation against <code>instance-policy.yaml</code>, the Grafana topology dashboard, and the Mastodon runbook — the network is live on <code>10.89.11.0/24</code> while the name is recorded as folded into <code>ao-sales</code>, which is a rename decision, not a registry edit.</td>
</tr>
<tr>
<td valign="top">NET-03</td>
<td valign="top"><strong>Single authoritative network inventory</strong></td>
<td valign="top">ST-01, ST-02</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§2.2, §5.1.2</td>
<td valign="top">One list of every <code>ao-*</code> network with its CIDR, <code>Internal</code> flag and owning component, generated from <code>config/platform/network-cidrs.yaml</code>, which both §2.2 and §5.1 cite. It must account for <code>ao-html-window</code> (10.89.14) and <code>ao-build-update</code> (10.89.13), which appear in the topology but in no table. §2.2 says twelve, §13.3 says twelve, this document says thirteen — all three become one asserted count. <code>check-network-isolation.sh</code> must not regenerate the CIDR file from a hardcoded list, or the named source of truth is not authoritative.</td>
</tr>
<tr>
<td valign="top">NET-04</td>
<td valign="top"><strong>Confirm the 4.3 prohibited-paths list</strong></td>
<td valign="top">ST-01, ST-02</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§4.3</td>
<td valign="top">§4.3 was titled "Prohibited Paths" and is cited elsewhere as the prohibition on simulation-to-live paths and as a pair with §4.4, but its body had been replaced by a duplicate of the sale-chain diagram. The list now in §4.3 was rebuilt from prohibitions stated elsewhere in this document and is <strong>not</strong> the operator-approved original. Confirm it is complete and correct, and supply anything that was lost with the misplaced content</td>
</tr>
<tr>
<td valign="top"><strong>SEC</strong></td>
<td valign="top">Secrets, credentials and identity</td>
<td valign="top"></td>
<td valign="top"><strong>Open</strong></td>
<td valign="top"></td>
<td valign="top"></td>
</tr>
<tr>
<td valign="top">SEC-01</td>
<td valign="top"><strong>Unattended secret delivery decision</strong></td>
<td valign="top">ST-24</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§14.1</td>
<td valign="top">Either migrate mastodon-db, sales-db, and webodm-db to Podman secrets or systemd credentials, or record an approved deviation with compensating controls, before any production declaration.</td>
</tr>
<tr>
<td valign="top">SEC-02</td>
<td valign="top"><strong>Reconcile secret-delivery policy with the implementation</strong></td>
<td valign="top">ST-24, ST-30</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§14.1, §14.1.1</td>
<td valign="top">§14.1 mandates Podman secrets or systemd credentials; every implemented path is a wallet-materialised <code>0600</code> env file, which the same subsection calls a plaintext duplicate. Either move to Podman/systemd credentials or record the deviation in this document with env-file lifetime and shred-on-exit behaviour, and close the <code>~/secrets/fabrication-db.env</code> recorded in ST-30. §14.1.1 points at a this document subsection that does not exist.</td>
</tr>
<tr>
<td valign="top">SEC-03</td>
<td valign="top"><strong>Documented credential rotation, revocation and recovery</strong></td>
<td valign="top">ST-24</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§14.1.1</td>
<td valign="top">§14.1.1 requires rotation, revocation, expiration and recovery to be documented before production use. None exists in §14, §16, §17 or this document. Include a wallet backup and restore procedure that is itself inside the backup set, and a break-glass order for the operator.</td>
</tr>
<tr>
<td valign="top"><strong>LEDGER</strong></td>
<td valign="top">Ledger, accounting and provenance</td>
<td valign="top"></td>
<td valign="top"><strong>Open</strong></td>
<td valign="top"></td>
<td valign="top"></td>
</tr>
<tr>
<td valign="top">LEDGER-07</td>
<td valign="top"><strong>Corda node must be built on Corda 5 against <code>cordadb</code></strong></td>
<td valign="top">ST-09</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§11.1, §17.1</td>
<td valign="top">The Corda CLI is installed but no node exists: <code>cordadb</code> holds 0 tables and its owner role has no working password, so <code>preinstall check-postgres</code> cannot pass. Build the node on Corda 5 against <code>cordadb</code> — no data migration is required — after the operator key/certificate ceremony. Until then the ledger is not production-ready</td>
</tr>
<tr>
<td valign="top">LEDGER-01</td>
<td valign="top"><strong>Corda key/certificate ceremony</strong></td>
<td valign="top">ST-09, ST-10</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§11.1</td>
<td valign="top">Operator ceremony performed and output recorded. No production ledger keys generated, replaced, exported, or activated without explicit operator approval.</td>
</tr>
<tr>
<td valign="top">LEDGER-02</td>
<td valign="top"><strong>Corda 5 build on PostgreSQL</strong></td>
<td valign="top">ST-09, ST-10</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§11.1</td>
<td valign="top">Node built on Corda 5 against <code>cordadb</code> in PostgreSQL 18, with the previous V4 installation and database removed and no data migrated; correlation join by receipt number, serial number, and UTC timestamp proven.</td>
</tr>
<tr>
<td valign="top">LEDGER-03</td>
<td valign="top">Corda ingest accepts only approved signed data</td>
<td valign="top">ST-09, ST-10</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§4.4, §11.2</td>
<td valign="top">Ledger-ingest receives signed, minimized manifests only, with authorization, idempotency, replay defence, and audit.</td>
</tr>
<tr>
<td valign="top">LEDGER-04</td>
<td valign="top">pCloud archive credentials</td>
<td valign="top">ST-12, ST-17</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§11.6, §17.1</td>
<td valign="top">Credentials provisioned into <code>ao-archive</code>; non-destructive encrypted replication test approved and run. <strong>Presence-only checks — never print, copy, or export values.</strong></td>
</tr>
<tr>
<td valign="top">LEDGER-05</td>
<td valign="top">Ledger socket-bridge diagnosis</td>
<td valign="top">ST-09, ST-10</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§17.1</td>
<td valign="top"><code>scripts/validation/check-ledger-ingest.sh</code> resolved, or the pending operator-run privileged command executed.</td>
</tr>
<tr>
<td valign="top">LEDGER-06</td>
<td valign="top"><strong>Accounting model for the authoritative ledger</strong></td>
<td valign="top">ST-09, ST-10</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§11.1, §11.3, §4.4, §7.2</td>
<td valign="top">Corda is declared the authoritative ledger of debits and credits and §4.4 requires an accounting report, but §11.3 defines no accounts, no debit/credit entry semantics, no posting rule, no currency handling, and no reconciliation between Corda state and <code>salesdb</code>. §7.2 calls Corda the source of truth for financial ledger information while §11.1 makes PostgreSQL authoritative for source data. Define the model or state that the ledger records references only and accounting is computed in reporting.</td>
</tr>
<tr>
<td valign="top"><strong>PAY</strong></td>
<td valign="top">Payments, sales and storefront</td>
<td valign="top"></td>
<td valign="top"><strong>Open</strong></td>
<td valign="top"></td>
<td valign="top"></td>
</tr>
<tr>
<td valign="top">PAY-01</td>
<td valign="top">Payment credentials into KDE Wallet <code>ao-payment</code></td>
<td valign="top">ST-24</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§14.1</td>
<td valign="top">Folder provisioned per §14.1.1; entry stored through <code>kwallet-provision.sh</code>; no secret in Git, logs, HTML, or Corda.</td>
</tr>
<tr>
<td valign="top">PAY-02</td>
<td valign="top">Payment verifier and normalized event model</td>
<td valign="top">ST-11, ST-12</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§7.2, §7.3</td>
<td valign="top">A test payment event produces a verified normalized record.</td>
</tr>
<tr>
<td valign="top">PAY-03</td>
<td valign="top">Sales API and receipt/fulfillment workflow</td>
<td valign="top">ST-11, ST-12</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§7.3, §15.1</td>
<td valign="top">A sales receipt manifest can be generated without exposing sensitive data.</td>
</tr>
<tr>
<td valign="top">PAY-04</td>
<td valign="top"><code>salesdb</code> schema initialization</td>
<td valign="top">ST-11, ST-12</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§3.3.1, §15.1</td>
<td valign="top">Live application schema initialized; read-only reporting views defined.</td>
</tr>
<tr>
<td valign="top">PAY-05</td>
<td valign="top"><strong>Live HTML views for product modals</strong></td>
<td valign="top">ST-11</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§7.1.2</td>
<td valign="top">The nine operator-requested views (Instructables robot link; MeshChatX visualizer/messaging; IPFS-pCloud route orthotiff with times and telemetry; Trimble San Vicente point clouds; LocusMap; Mapbox; Mastodon live forum; Gazebo/Foxglove kitchen, storage/CNC, and vehicle; Trimble SketchUp grid) are built and reachable from the modals, <strong>each published as a static export, an approved published view, or an external service</strong> — never by exposing a loopback address. <strong>Recorded 2026-10-01; nothing is built.</strong> Three preconditions are open and need operator decisions: the Instructables robot image asset does not exist, the Mastodon and MeshChatX iframes have no publishable origin, and the three simulation views are gated on §19.1 SIM-04 and SIM-05. Publishing any live view is a new public entry requiring explicit operator approval under §4.1 rule 6.</td>
</tr>
<tr>
<td valign="top">PAY-06</td>
<td valign="top"><strong>Customer-facing PDF email path proven</strong></td>
<td valign="top">—</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§4.3, §4.4</td>
<td valign="top">Purchase-request confirmation, receipt, and work-order status (including expected delivery) each demonstrably sent from <code>ao-sales</code> to a customer <strong>as PDF by email</strong>.</td>
</tr>
<tr>
<td valign="top">PAY-07</td>
<td valign="top"><strong>Reconcile the payment-provider decision</strong></td>
<td valign="top">ST-12, ST-27</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§7.2, §7.3</td>
<td valign="top">§7.2 records PayPal, Zelle and Coinbase as decided; ST-27 and ES.2 still treat the provider as undecided. State once which providers are in scope now and make every other reference match, so the sales pipeline is not gated on a decision that already exists.</td>
</tr>
<tr>
<td valign="top"><strong>COMM</strong></td>
<td valign="top">Community, federation and local AI</td>
<td valign="top"></td>
<td valign="top"><strong>Open</strong></td>
<td valign="top"></td>
<td valign="top"></td>
</tr>
<tr>
<td valign="top">COMM-01</td>
<td valign="top">Mastodon configuration drift reconciliation</td>
<td valign="top">ST-13, ST-14</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§15.4</td>
<td valign="top"><code>config/mastodon/instance-policy.yaml</code>, <code>mastodon.env.example</code>, <code>version-matrix.yaml</code>, <code>secrets/mastodon/mastodon.env</code>, and <code>fetch-mastodon-env.sh</code> all reconciled to <code>mastodon.300x3.com</code>. <strong>Do this before the next Mastodon restart</strong> — the helper emits the superseded apex value unconditionally.</td>
</tr>
<tr>
<td valign="top">COMM-02</td>
<td valign="top">Reverse-follow validation</td>
<td valign="top">—</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§15.4.4</td>
<td valign="top">Confirmed from the remote <code>following</code> collection and local incoming relationship tables, never inferred from local outgoing state.</td>
</tr>
<tr>
<td valign="top">COMM-03</td>
<td valign="top">Remote account approval/rejection record</td>
<td valign="top">—</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§15.4.5</td>
<td valign="top">Recorded separately from local account follow state.</td>
</tr>
<tr>
<td valign="top">COMM-04</td>
<td valign="top">OpenClaw OAuth and conversation validation</td>
<td valign="top">ST-15</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§15.2</td>
<td valign="top"><strong>Operator decision 2026-10-01: the bot posts replies <code>public</code>.</strong> The bridge was briefly set to <code>unlisted</code> for the load test so 100 replies would not flood public timelines; that is reverted and line 251 of <code>~/.local/bin/mastodon-openclaw-bridge.py</code> is back to <code>visibility: public</code>. The operator explicitly authorised the bot to post to visitors in a public manner, so replies are visible in public timelines, trends and search. The <code>@author</code> mention prefix is retained — it is load-bearing for federation, not decoration. Original status:  <strong>BOTH halves done 2026-10-01, verified from <code>mastodon.social</code>'s own API.</strong> *Auth half:* app <code>openclaw-mastodon-bridge</code>, token in KDE Wallet (<code>ao-mastodon</code>/<code>openclaw-bot-access-token</code>), <code>verify_credentials</code> → <code>200 bot</code>, zero restarts after <strong>5,119</strong> 401 crash-loops. Recipe in §14.1.4/§14.1.5. *Conversation half:* a real mention was answered and the reply is visible publicly — <code>replies_count: 1</code> on status <code>117368106037492186</code>, descendant <code>…/users/bot/statuses/117368165343122068</code>. Two faults had to be fixed. <strong>(a)</strong> <code>~/.openclaw/mastodon-bridge-state.json</code> held <code>lastNotificationId: 13</code> while the newest notification was <code>5</code> (the <code>notifications</code> table was repopulated directly in PostgreSQL, restarting the id sequence at 1), so <strong>every</strong> notification was skipped by <code>int(nid) &lt;= int(last_id)</code> with no error and no log line since 2026-09-25. <strong>(b)</strong> A Mastodon reply only federates to a remote inbox if the parent author is <strong>@mentioned</strong> in it, or follows the bot — the bot has <strong>zero</strong> followers, so a mention-less public reply produced an <strong>empty delivery set</strong> and silently stayed local while <code>DistributionWorker</code> still logged <code>done</code>. The bridge now prepends <code>@author</code>; verified by a real <code>DeliveryWorker</code> and by the remote's <code>replies_count</code>. <strong>Two process traps:</strong> notification ids are <strong>processing order, not chronological</strong> (never infer "newest" from the highest id), and <strong><code>DeliveryWorker ... done</code> is not proof of delivery</strong> — confirm from the remote server's view. Journals: <code>…-mastodon-inbound-federation-ingress.log</code>, <code>…-openclaw-bridge-stale-cursor.log</code>. Bridge script and unit are tracked: <code>scripts/mastodon/mastodon-openclaw-bridge.py</code> and <code>quadlet/operations/mastodon-openclaw-bridge.service</code> (the unit runs the repo path). <strong>The dead <code>ENV_FILE</code> fallback is removed</strong> — it pointed at a file document B shredded, so a wallet failure would have died on a file that must not return. The wallet is now the only source; on failure the bridge waits and logs instead of crash-looping. Bulk mastodon.social cleanup: <code>scripts/mastodon/mastodon-social-purge.py</code> (needs an access token; the session cookie is rejected by their API).</td>
</tr>
<tr>
<td valign="top">COMM-05</td>
<td valign="top"><code>300x3.com</code> email routing / MX</td>
<td valign="top">ST-13, ST-14</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§15.3</td>
<td valign="top">Delivery confirmed or formally deferred.</td>
</tr>
<tr>
<td valign="top">COMM-06</td>
<td valign="top">Bootstrap discovery for remote servers</td>
<td valign="top">ST-13, ST-14</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§15.4.4 step 9</td>
<td valign="top">From Konqueror signed in at <code>https://mastodon.300x3.com</code>, follow at least one account on <code>mastodon.social</code>. Remote servers do not index this instance until first contact occurs. <code>https://300x3.com</code> is a static storefront and is not routed to Mastodon.</td>
</tr>
<tr>
<td valign="top">COMM-07</td>
<td valign="top">Public-post delivery, round trips, and directory submission</td>
<td valign="top">ST-13, ST-14</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§15.4.4 step 10</td>
<td valign="top">Public-post delivery to <code>mastodon.social</code> and reply/boost round-trips back to the local instance are validated; then <code>300x3.com</code> is submitted to the joinmastodon.org directory. Directory submission is an external publication and requires explicit operator approval.</td>
</tr>
<tr>
<td valign="top"><strong>FIELD</strong></td>
<td valign="top">Field, radio and drones</td>
<td valign="top"></td>
<td valign="top"><strong>Open</strong></td>
<td valign="top"></td>
<td valign="top"></td>
</tr>
<tr>
<td valign="top">FIELD-01</td>
<td valign="top">RF characterization on both bands</td>
<td valign="top">ST-04, ST-05, ST-06</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§9.4</td>
<td valign="top">RSSI, SNR, noise floor, packet loss, retry behaviour, and airtime recorded on both RNodes. <strong>Closure is a recorded finding, not a fix</strong> — if the interference is benign ambient noise, record that. No corrective action unless measurement shows a real fault.</td>
</tr>
<tr>
<td valign="top">FIELD-02</td>
<td valign="top">End-to-end field link test</td>
<td valign="top">—</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§9.2, §9.4</td>
<td valign="top">Unicast and broadcast proven over each RF path; fail-safe verified on radio, serial-path, and peer loss; no live flight-control path enabled during testing.</td>
</tr>
<tr>
<td valign="top">FIELD-03</td>
<td valign="top">Cross-band isolation</td>
<td valign="top">—</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§9.4</td>
<td valign="top">915 MHz and 917 MHz isolation measured; interference classified as in-band, adjacent-band, harmonic, or spurious.</td>
</tr>
<tr>
<td valign="top">FIELD-04</td>
<td valign="top">Reticulum gateway listener review</td>
<td valign="top">ST-04, ST-05, ST-06</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§9.3, §9.4</td>
<td valign="top"><code>0.0.0.0:4242</code> reviewed against field-domain firewall policy; reachability decided rather than left unverified.</td>
</tr>
<tr>
<td valign="top">FIELD-05</td>
<td valign="top"><code>umsgpack</code> persistence error</td>
<td valign="top">ST-04, ST-05, ST-06</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§9.2</td>
<td valign="top">Classified, or formally accepted as a historical bounded-ratchet defect with restart-persistence evidence.</td>
</tr>
<tr>
<td valign="top">FIELD-06</td>
<td valign="top"><strong>DRONE-RADIO → QGC midflight mission update proven</strong></td>
<td valign="top">ST-04, ST-05, ST-06</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§9.2.2</td>
<td valign="top">A local QGC mission is shown reaching the <strong>QGC session on the Pi5 drone</strong> over DRONE-RADIO, and a mission change is demonstrated <strong>in flight</strong>. Radio only: recorded that no IP path and no mTLS is used on this link.</td>
</tr>
<tr>
<td valign="top">FIELD-07</td>
<td valign="top"><strong>PEOPLE-RADIO → MeshChatX LoRaWAN path proven</strong></td>
<td valign="top">ST-04, ST-05, ST-06</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§9.2.2</td>
<td valign="top">MeshChatX text carried over PEOPLE-RADIO in both directions, recorded as LoRaWAN-related communication, with the separate 915/917 MHz bands maintained.</td>
</tr>
<tr>
<td valign="top">FIELD-08</td>
<td valign="top"><strong><code>ao-fabrication</code> deployed with <code>a_fab</code></strong></td>
<td valign="top">ST-30</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§3.3.0, ES.1</td>
<td valign="top">Domain created on <code>10.89.12.0/24</code> (<code>Internal=true</code>); <strong>per-machine production data pulled from at least one individual machine into <code>a_fab</code></strong>; separation from <code>ao-sim-fabrication</code> demonstrated (simulation holds no production data); <code>a_fab</code> registered in <code>network-cidrs.yaml</code>.</td>
</tr>
<tr>
<td valign="top">FIELD-09</td>
<td valign="top"><strong>QGC over LoRa to the RPi5</strong></td>
<td valign="top">ST-21</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§9.2.2</td>
<td valign="top"><strong>Deferred by the operator 2026-09-30 — outstanding, not started.</strong> The desktop <code>DRONE-RADIO</code> is already configured as a Reticulum <code>RNodeInterface</code> (917 MHz / 250 kHz / SF7 / 17 dBm, <code>discoverable = no</code>, <code>/dev/ttyUSB0</code>) so the air link is RNS-encrypted and needs no further radio work. What is missing is the MAVLink handoff, and the <strong>RPi5 Waveshare end is the agreed place for the bridge</strong>. Three constraints found on 2026-09-30 and worth not re-deriving: (1) QGroundControl v5.1.0 cannot speak RNS — it is MAVLink-only, with UDP/TCP/serial/SiK links, so something must translate; (2) Reticulum ships no MAVLink transport, so the bridge is code to be written; (3) the desktop's Reticulum stack runs <strong>inside</strong> <code>ReticulumMeshChatX</code>, which holds <code>/dev/ttyUSB0</code> open, and a second RNS instance would contend for the same port. Terminating on the RPi5 avoids all three and matches §9.2.2, which already describes a QGC session on the RPi5 for out-of-range operation. Blocked on: RPi5 address and SSH access (absent from dnsmasq leases, the ARP cache, and every config).</td>
</tr>
<tr>
<td valign="top">FIELD-10</td>
<td valign="top">WebODM folder validation</td>
<td valign="top">ST-03</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§8.5</td>
<td valign="top">Tree, ownership, sentinel, and checks validated; WebODM starts only with required validated storage.</td>
</tr>
<tr>
<td valign="top">FIELD-11</td>
<td valign="top"><strong>Authoritative mapping database name and location</strong></td>
<td valign="top">ST-03</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§8.1, §8.4, §8.5, §3.3.1</td>
<td valign="top">§8.4 places the mapping PostgreSQL at <code>~/webodm/dbdata</code> and §3.3.1 names the logical database <code>webodm</code> on the host cluster, while ST-03 says the app reads <code>webodm_dev</code> in <code>ao-webodm-db</code>. §8.1 and §8.5 require all mapping storage on the validated photogrammetry drive, which as written contains neither. State one name and one location and confirm it is inside the backup scope.</td>
</tr>
<tr>
<td valign="top">FIELD-12</td>
<td valign="top"><strong>One canonical radio device-name table</strong></td>
<td valign="top">ST-04</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§2.1, §9.2.1, §9.4</td>
<td valign="top">Three different device paths are given for the same two radios, and §9.2.1 states both CP2102 bridges expose an identical USB serial descriptor so identity must come from by-path plus the SX1262 MAC. Publish one table mapping radio to device path, by-path and MAC.</td>
</tr>
<tr>
<td valign="top">FIELD-13</td>
<td valign="top"><strong>Rule on LoRaWAN naming</strong></td>
<td valign="top">ST-04</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">ES.1, §9.4</td>
<td valign="top">ES.1 calls PEOPLE-RADIO a LoRaWAN path while §9.4 says not to describe the system as LoRaWAN unless it implements a true device, gateway and network-server architecture. Decide whether RNode-over-Reticulum is ever called LoRaWAN in any artefact and apply it everywhere.</td>
</tr>
<tr>
<td valign="top">FIELD-14</td>
<td valign="top"><strong>The two radio profiles are identical</strong></td>
<td valign="top">ST-04</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§9.4</td>
<td valign="top"><code>config/field/heltec-v3/radio-profile-us915.yaml</code> and <code>config/drone/waveshare-lora/radio-profile-us915.yaml</code> are byte-identical: same sync word <code>0x12</code>, same encryption key ID, same device identity placeholder, and neither declares a frequency. The two radios therefore cannot be told apart on air, which contradicts §9.2.1 and the 915/917 MHz split in §9.1. The profiles also disagree with <code>version-matrix.yaml</code>: profiles say 125 kHz and spreading factor 10, the matrix and §9.2.1 say 250 kHz and spreading factor 7 for <code>DRONE-RADIO</code>. Give each profile its own frequency, sync word, key ID and device identity, reconcile the bandwidth and spreading factor against the matrix, and confirm on air that <code>DRONE-RADIO</code> carries missions only</td>
</tr>
<tr>
<td valign="top"><strong>SIM</strong></td>
<td valign="top">Simulation and fabrication</td>
<td valign="top"></td>
<td valign="top"><strong>Open</strong></td>
<td valign="top"></td>
<td valign="top"></td>
</tr>
<tr>
<td valign="top">SIM-01</td>
<td valign="top">Gazebo GUI clients and DDS policy</td>
<td valign="top">ST-07, ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.1, §10.2</td>
<td valign="top">Vehicle and fabrication GUI clients deployed; separate DDS/interface policy decided.</td>
</tr>
<tr>
<td valign="top">SIM-02</td>
<td valign="top"><code>/ALWAYSON</code> Gazebo subfolder</td>
<td valign="top">ST-07, ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2</td>
<td valign="top">Path confirmed by the operator. Currently recorded as an open decision, not a guess.</td>
</tr>
<tr>
<td valign="top">SIM-03</td>
<td valign="top">QGroundControl interactive workflow</td>
<td valign="top">ST-21</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.1</td>
<td valign="top">Interactive SITL workflow validated end to end.</td>
</tr>
<tr>
<td valign="top">SIM-04</td>
<td valign="top">Vehicle 3D world, boning, RL objects, HTML portal</td>
<td valign="top">ST-07</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">ES.1, §10.1.2</td>
<td valign="top">World setup scripted and repeatable; boning frame and tolerances measurable and exported; RL objects addressable and resettable; the world fully settable and operable from the browser-served HTML portal.</td>
</tr>
<tr>
<td valign="top">SIM-05</td>
<td valign="top">Fabrication 3D world, boning, RL objects, HTML portal</td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">ES.1, §10.2.1</td>
<td valign="top">As item 28, for <code>ao-sim-fabrication</code>, with cell and machine datum frames and boning checked against the real machine envelopes.</td>
</tr>
<tr>
<td valign="top">SIM-06</td>
<td valign="top"><strong>Rebuild and verify the Gazebo GUI client</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2.1</td>
<td valign="top">Rebuild the image with <code>qt6-svg-plugins</code> and <code>GZ_RENDERING_RESOURCE_PATH=/usr/share/gz/gz-rendering</code>, then start it and confirm it renders factory geometry with no OGRE or null-string errors and a stable <code>NRestarts</code>. Until then "rendering works" is not established. The unit stays masked so it cannot seize keyboard and pointer focus</td>
</tr>
<tr>
<td valign="top">SIM-07</td>
<td valign="top"><strong>Working ROS 2 package source</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2.1</td>
<td valign="top"><code>packages.ros.org</code> fails TLS verification from this host because its certificate is issued for <code>*.osuosl.org</code>. Certificate verification must not be disabled to work around it. The installed ROS 2 Lyrical stack and <code>ros_gz</code> bridge are unaffected; installing or updating packages is not. Use a reachable mirror or the pinned base-image digest</td>
</tr>
<tr>
<td valign="top">SIM-08</td>
<td valign="top"><strong>Publish the Gazebo viewer at <code>www.300x3.com</code></strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2.1</td>
<td valign="top">The 3D viewer and its eight read-only camera feeds are verified working on the local path and <strong>not published</strong> (operator decision 2026-10-02). <code>ao-html-window</code> (<code>10.89.14.0/24</code>, <code>Internal=true</code>) exists for public-facing windows on local services and is the network the Foxglove bridge joins for this purpose. Outstanding when it proceeds: confirm the hostname, add the ingress route to <code>~/.cloudflared/config.yml</code> (a customer-facing production config, not changed unilaterally), and decide whether the viewer alone or the portal too is published, since the portal renders boning derived from real machines</td>
</tr>
<tr>
<td valign="top">SIM-09</td>
<td valign="top"><strong><code>elev_arms</code> framing uses the boned datum, not the as-built arms</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2.1</td>
<td valign="top">The arms elevation is centred on the boned arms-cell centre <code>(6.821, 3.534)</code>, which is narrower than the as-built arm cluster, so the arms sit right of centre and the building's north wall intrudes at frame left. <code>boning.yaml</code> does not carry the as-built arm centroid, and it is not estimated from a render. Add the centroid to the boning data, then recompute the pose from it. The three elevation standoffs are otherwise correct</td>
</tr>
<tr>
<td valign="top">SIM-10</td>
<td valign="top"><strong>Doors are not separately colourable</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2.1</td>
<td valign="top">Walls, conveyor belts, arms and conveyor gears carry distinct materials; doors do not, because <code>massing_fab.dae</code> has no semantic part names (anonymous <code>group_0</code>–<code>group_25</code>) and <code>split-collada-parts.py</code> returns a degenerate cube signature for every part of that file, so no size distinguishes a door. Re-export the model from SketchUp with named groups (<code>door</code>, <code>wall</code>, <code>floor</code>) and the splitter will separate it. Until then doors keep the wall material rather than being guessed at</td>
</tr>
<tr>
<td valign="top">SIM-11</td>
<td valign="top"><strong>Signed world manifest is stale</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2.1, §16.3</td>
<td valign="top"><code>artifacts/fabrication-simulation-manifests/factory-world-v1.json</code> records a 5371-byte world; <code>factory.world</code> is now ~18 KB after the camera set, materials and the unit-scale fix, so the signature no longer describes the exported artifact. Cosmetic with respect to the running world, which is valid and serving. Re-export and re-sign with the <code>ao-sim-fabrication</code> key when that is scheduled</td>
</tr>
<tr>
<td valign="top">SIM-12</td>
<td valign="top"><strong>Facility scheduler absent</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2</td>
<td valign="top">The §10.2 component tree names a facility scheduler for <code>ao-sim-fabrication</code>; nothing in the repo implements one, and no §19.2 item tracked it. Closing it means a scheduler that sequences cell and kitchen work against the boned cell datums. Distinct from the RL objects (item 83), which are the entities such a scheduler would move</td>
</tr>
<tr>
<td valign="top">SIM-13</td>
<td valign="top"><strong>Safety-zone and interlock model absent</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2</td>
<td valign="top">The §10.2 component tree names a safety-zone and interlock model; nothing in the repo implements one — <code>factory.world</code> contains no safety-zone or interlock entity, and no §19.2 item tracked it. This is the safety-relevant component of the domain, so it is recorded separately from the other absent ones. The simulation is rehearsal only and holds no production data (§10.2), which is the current mitigation; the model itself remains undelivered</td>
</tr>
<tr>
<td valign="top">SIM-14</td>
<td valign="top"><strong>RL objects are a catalogue, not world entities</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2.1, §19.1 SIM-05</td>
<td valign="top"><code>GAZEBO/sim/objects.yaml</code> is a 104-line catalogue that declares the objects live in a non-static <code>rl_objects</code> model, written to for spawn, pose and delete so placement varies without rebuilding the world. <strong>That model does not exist</strong> — <code>factory.world</code> defines no <code>rl_objects</code> model, and <code>/api/objects</code> therefore serves objects Gazebo has never instantiated. §10.2.1 requires them individually addressable, observable and resettable; today they are addressable only in YAML. Closing it means adding the model to the world, which changes <code>factory.world</code> and therefore the signed manifest (item 72)</td>
</tr>
<tr>
<td valign="top"><strong>OPS</strong></td>
<td valign="top">Backup, monitoring, logs and scripts</td>
<td valign="top"></td>
<td valign="top"><strong>Open</strong></td>
<td valign="top"></td>
<td valign="top"></td>
</tr>
<tr>
<td valign="top">OPS-01</td>
<td valign="top">Metabase persistence and first read-only query</td>
<td valign="top">ST-20</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§15.1, §17.2</td>
<td valign="top"><strong>Provision the Metabase application database</strong> (dedicated PostgreSQL database for the Metabase schema, saved questions, dashboards, and subscriptions) and the per-source <strong>read-only</strong> reporting roles, one per PostgreSQL and MySQL source with no write, DDL, or owner privilege. Then confirm state survives restart and a protected ad-hoc read-only reporting query succeeds with no source writes. The application database must never be written to by a reporting source.</td>
</tr>
<tr>
<td valign="top">OPS-02</td>
<td valign="top">Version-matrix capture automation</td>
<td valign="top">—</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§4.1 rule 9, §16</td>
<td valign="top"><code>scripts/validation/capture-version-matrix.sh</code> documented as the producer, with a stated refresh requirement. <strong>Now the more urgent half of item 34:</strong> six services were digest-pinned and five rows corrected by hand, so the next hand edit can equally re-introduce a stale row. Capture digests from the deployed units instead of typing them.</td>
</tr>
<tr>
<td valign="top">OPS-03</td>
<td valign="top">Scripts layout completeness</td>
<td valign="top">ST-01, ST-25</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§16.1</td>
<td valign="top">Layout is missing the <code>sales/</code> directory and <code>validate-sale-receipt.sh</code>, both referenced elsewhere. Add or repoint them.</td>
</tr>
<tr>
<td valign="top">OPS-04</td>
<td valign="top">Restore-test script contract</td>
<td valign="top">ST-18</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§17.1</td>
<td valign="top">The seven-step restore test is unowned; state that the <code>check-*.sh</code> scripts implement it, or the requirement has no executor.</td>
</tr>
<tr>
<td valign="top">OPS-05</td>
<td valign="top">GPU scheduling and admission policy</td>
<td valign="top">ST-01, ST-25</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">ES.1</td>
<td valign="top">LM Studio, SketchUp, Gazebo, and WebODM batch scheduling matches the documented priority order.</td>
</tr>
<tr>
<td valign="top">OPS-06</td>
<td valign="top">ALWAYS ON operator console has no unit</td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">ES.2</td>
<td valign="top"><code>scripts/operations/web-console-server.py</code> on <code>127.0.0.1:8099</code> is part of ALWAYS ON and verified 200 when run by hand, but no systemd unit or timer starts it. Give it a unit or record an approved deviation stating it is operator-run only.</td>
</tr>
<tr>
<td valign="top">OPS-07</td>
<td valign="top"><strong>One canonical journal root</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§16.3, §12.1, §13.3.1</td>
<td valign="top"><strong>Root decided 2026-10-02: <code>/ALWAYSON/logs/</code></strong> (§16.3). §16.3 and §13.3.1 corrected and the <code>LOGOS-JOURNALS</code> typo fixed; the 2 766-line operational journal merged and verified identical; five entries that existed nowhere created and given writers; <code>check-logs-journals.sh</code> asserts existence and freshness for all 18. <strong>Remaining:</strong> add <code>logs/</code> to the restic path set; physically merging the two trees would mean redeploying the *flat* deployed unit copies (§16.1.1) and restarting Gazebo and <code>ao-build-update</code>, so it was not done. Retention is item 85; the missing backup timer is item 57.</td>
</tr>
<tr>
<td valign="top">OPS-08</td>
<td valign="top"><strong>Executable restore runbook with RPO and RTO</strong></td>
<td valign="top">ST-18</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§17.1</td>
<td valign="top">§17.1 is policy only: no restic command sequence, no restore ordering between filesystem and PostgreSQL dumps, no <code>pg_restore</code> or role-recreation step, no ownership handling, and no RPO or RTO stated per data class. Write the preflight, snapshot selection, filesystem restore, database restore in dependency order, credential re-provision and hash re-verification steps.</td>
</tr>
<tr>
<td valign="top">OPS-09</td>
<td valign="top"><strong>Restic path set covers every data class</strong></td>
<td valign="top">ST-18, ST-03</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§17.1, §3.3.1, §8.4</td>
<td valign="top"><strong><code>data/</code> added to the path set 2026-10-02.</strong> <code>data/</code> was excluded and is now in the path set: <code>data/ardupilot</code> (2.1 GB), <code>data/corda-install</code> (282 MB), plus <code>sim-fabrication</code>, <code>sales</code>, <code>mapping</code>, <code>field</code>, <code>payment</code>, <code>ledger</code>. Snapshot <code>fb52984b</code> is the first to include it. Photogrammetry drive still deliberately excluded. <strong>Still open:</strong> <code>data/build-update/cache</code> is excluded as regenerable, and the set should be re-checked whenever a new <code>data/</code> class appears.</td>
</tr>
<tr>
<td valign="top">OPS-10</td>
<td valign="top"><strong>Named backup and restore executors</strong></td>
<td valign="top">ST-18</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§16.1, §17.1</td>
<td valign="top">§16.1 lists <code>scripts/backup/</code> and <code>scripts/restore/</code> as empty directories while ST-18 claims active <code>ao-restic-backup</code>, <code>ao-restic-verify</code> and dump timers. Name the script paths and the systemd unit and timer names that implement §17.1, and give the seven-step restore test a named executor and cadence.</td>
</tr>
<tr>
<td valign="top">OPS-11</td>
<td valign="top"><strong>Alerting mechanism and thresholds</strong></td>
<td valign="top">ST-19</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§17.2</td>
<td valign="top">§17.2 requires alerts for disk pressure, backup failure, restart loops, unexpected listeners, radio loss, certificate expiry and cross-domain denials, but no alertmanager or notification target is specified anywhere, and ST-19 records no rules or dashboards built. Name the alerting component, the routing target per severity, and a threshold per rule.</td>
</tr>
<tr>
<td valign="top">OPS-12</td>
<td valign="top"><strong>End-to-end install procedure with rollback</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§12.1, §12.3, §12.4, §13.3, §16.1</td>
<td valign="top"><strong>Partly done 2026-10-03:</strong> §12.4 now gives an ordered, staged procedure from a bare Ubuntu 26.04 + KDE + Cline CLI + internet, implemented by <code>scripts/provision/provision.sh</code> (dry-run by default). It <strong>delegates</strong> to <code>scripts/bootstrap/00</code>, <code>02</code>, <code>03</code>, <code>04</code> rather than repeating them, so the two chains no longer duplicate a package list. <strong>Remaining:</strong> the rollback half is not written - no stage documents how to undo itself non-destructively; <code>bootstrap/01</code> photogrammetry verification is not yet gated on §17.3 evidence as §16.1 requires; and a clean-room rebuild has <strong>never been executed</strong>, so the procedure is unproven.</td>
</tr>
<tr>
<td valign="top">OPS-13</td>
<td valign="top"><strong>Enable and verify linger</strong></td>
<td valign="top">ST-01, ST-24</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§12.3, §13.2</td>
<td valign="top">§12.3 checks <code>loginctl show-user -p Linger</code> read-only but nothing enables it, while §13.2 requires user-level Quadlet units and wallet-gated services start only after Plasma login. After a reboot every Quadlet unit and every wallet-backed service stays down. Add the enable step, or record an approved this document deviation stating the host is login-gated by design with the recovery procedure.</td>
</tr>
<tr>
<td valign="top">OPS-14</td>
<td valign="top"><strong>Reconcile the Podman store model</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§13.2</td>
<td valign="top">§13.2 states the system store is unused by any workload while a mixed-store deviation is recorded in §19.2 and §19.1 PLAT-01 still has the runtime designation open. Record the deviation in this document or remove the claim; the isolation evidence cannot be trusted while the store model disagrees with itself.</td>
</tr>
<tr>
<td valign="top">OPS-15</td>
<td valign="top"><strong>Re-runnable verification entries</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§19.2</td>
<td valign="top">Most rows carry an outcome but no date, no command and no criterion for deciding when to re-run, so the evidence cannot be re-verified. One row claims the backup schedule was automated 2026-08-31 while ST-18 records the renamed timers have not yet fired. Add the command and the date to each check, and re-run the evidence before relying on it.</td>
</tr>
<tr>
<td valign="top">OPS-16</td>
<td valign="top"><strong>Simulation work leaves stray containers and world backups in the tree</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§16.1</td>
<td valign="top">Two debug containers from 2026-10-01 (<code>vigorous_shannon</code>, <code>dreamy_rosalind</code>, both <code>--help</code> probes) still run with no restart policy, and eight <code>GAZEBO/worlds/factory.world.bak.*</code> files plus a <code>topology-v2-viewer.png</code> sit untracked. Removal is a delete and needs operator approval per README §4.1 rule 3</td>
</tr>
<tr>
<td valign="top">OPS-17</td>
<td valign="top"><strong>AppImages and vendor binaries are not installable by the provisioner</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§12.4</td>
<td valign="top"><code>provision.sh</code> can restore repositories, packages, snaps, flatpak and Quadlet units, but 5 AppImages and several vendor tools (LM Studio, pCloud, nPerf, QGroundControl, Reticulum MeshChatX, cline, bun, pymavlink) have no package source and are listed as manual fetches. A rebuild cannot complete unattended until their download-and-verify steps exist, or the manual list is explicitly accepted as an operator phase.</td>
</tr>
<tr>
<td valign="top">OPS-18</td>
<td valign="top"><strong><code>provenance-log.py</code> is a single large file</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§12.4, §12.5</td>
<td valign="top">Roughly 1,900 lines holding collection, policy, plan generation and rendering in one module. Editing it repeatedly caused several malformed edits that only surfaced at compile time. Split into collector / policy / plan / render, with the render path covered by a test, before it grows further.</td>
</tr>
<tr>
<td valign="top">OPS-19</td>
<td valign="top"><strong>Update-plan steps are prose, not executable</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§12.5</td>
<td valign="top"><code>update-plan.json</code> marks 6 items eligible, but 5 of them contain a step like <code>edit Image= in quadlet/&lt;domain&gt;/&lt;unit&gt;.container</code>, which no executor can run. Split the schema into executable <code>steps</code> (argv arrays, verb-allowlisted) and prose <code>manual</code>, so "eligible" means a machine can actually do it. Only <code>brave</code> is genuinely automatable today. Plan-supplied shell strings must never reach <code>sh -c</code>.</td>
</tr>
<tr>
<td valign="top">OPS-20</td>
<td valign="top"><strong><code>apply-plan.py</code> dry-run validator</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§12.5</td>
<td valign="top">Loads the plan, computes its SHA-256, snapshots it into the run directory, validates every step against a verb allowlist, derives blast-radius groups (units sharing a digest or a deploy domain), and reports what a run would touch - executing nothing. Approval must pin to the plan hash, because the live plan regenerates on every refresh, so the file the operator approved is not the file a tool would run.</td>
</tr>
<tr>
<td valign="top">OPS-21</td>
<td valign="top"><strong>Install dates are inferred, not recorded</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§12.5</td>
<td valign="top">The <code>Installed</code> column derives its date from dpkg <code>.list</code> mtimes, which cannot distinguish install from last upgrade; dpkg records no install timestamp. <code>/var/log/apt/history.log</code> holds 13 dated transactions with the exact commandline, including <code>unattended-upgrade</code> runs. Parse it so the column is ground truth and an operator can tell an unattended upgrade from a manual one.</td>
</tr>
<tr>
<td valign="top">OPS-22</td>
<td valign="top"><strong>No regression tests for the inventory generator</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§12.5</td>
<td valign="top">Three defects shipped because nothing asserted them: <code>podman pull</code> steps carrying a 12-character truncated digest (every such step returned HTTP 400); steps built from the application display name, producing <code>apt install --only-upgrade Account</code> for "Account Wizard"; and a prose error string used as a digest. Two assertions would have caught all three - every pull step carries a 64-character digest, and no step embeds a not-a-value marker.</td>
</tr>
<tr>
<td valign="top">OPS-23</td>
<td valign="top"><strong>Roll-ups cannot be drilled into</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§12.5</td>
<td valign="top"><code>KDE Plasma Desktop</code> is one row for 191 components, the Ubuntu archive one row for 3,863 packages, ROS one row for 351. "Is the desktop behind" is answerable; "update ROS 2 rviz" is not. Each roll-up needs a drill-down to its members with their own versions, not a prose count.</td>
</tr>
<tr>
<td valign="top">OPS-24</td>
<td valign="top"><strong>Restore drill for the restic backup</strong></td>
<td valign="top">ST-18</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§17.1, §19.2</td>
<td valign="top"><strong>Restore drill passed 2026-10-02; still open on redundancy.</strong> Restored snapshot <code>fb52984b</code> to a scratch directory and compared against live: <code>data/sales</code> and <code>data/corda-install</code> file counts match and spot checksums are byte-identical; <code>data/ardupilot/Tools</code> restored 1,967 files / 368 MiB. <code>restic check</code> reports no errors across 26 snapshots. Backup history is real: 23 daily snapshots 2026-08-25 to 09-24, an 8-day outage, then <code>fb52984b</code>. <strong>Still open:</strong> only one snapshot included <code>data/</code> at the time of the drill, so a single bad night is not yet survivable. Consecutive <code>data/</code>-inclusive snapshots are required.</td>
</tr>
<tr>
<td valign="top">OPS-25</td>
<td valign="top"><strong>Install the logrotate policy</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§16.3</td>
<td valign="top"><code>config/host/logrotate-alwayson.conf</code> is staged and syntax-checked but <strong>not installed</strong>: <code>/etc/logrotate.d/</code> needs root and <code>pkexec</code> would raise a GUI prompt unattended. Install it, then confirm one rotation actually occurs. Overhead is not the obstacle — a full system pass measured 0.008s and <code>logrotate.timer</code> runs once daily. Compression is deliberately omitted because it is the only step that reads whole files. Until installed, nothing in <code>logs/</code> is rotated and <code>sim-gz-server.log</code> grows continuously.</td>
</tr>
<tr>
<td valign="top">OPS-26</td>
<td valign="top"><strong>Retention for the log subdirectories and for journald</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§16.3, §17.2</td>
<td valign="top">OPS-25 covers the top-level <code>*.log</code> files only. The subdirectories (<code>operations/</code>, <code>gpu-runtime/</code>, <code>backup/</code>, <code>installation/</code>) hold per-operation audit records that must not simply be truncated, and have no retention at all. Separately, <code>journalctl --disk-usage</code> reports 4 GB with no explicit <code>SystemMaxUse</code>, so journald is on its built-in default while carrying 32 of 33 units. State a retention period per subdirectory and an explicit journald cap.</td>
</tr>
<tr>
<td valign="top">OPS-27</td>
<td valign="top"><strong>Prometheus collects host metrics only; §17.2 requires eleven domains</strong></td>
<td valign="top">ST-19</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§17.2</td>
<td valign="top">Measured 2026-10-02 against the live API: two scrape targets (<code>node-host</code>, <code>prometheus</code>), 547 metric names, <strong>zero alert rules and zero recording rules</strong>, and no metric outside node_exporter and Prometheus's own internals. <code>ao-admin</code> collects host telemetry and stores it without evaluating any of it. §17.2 requires metrics for Host, Podman/systemd, Mapping, Field, Sales, AI/community, Vehicle simulation, Fabrication simulation, Ledger and Backup, plus alerts for disk pressure, backup failure, failed restore tests, restart loops, unexpected listeners, failed payment verification, radio loss, WebODM backlog, GPU contention, expired certificates and denied cross-domain traffic. <strong>Available now at no new exposure:</strong> <code>node_filesystem_avail_bytes</code>, <code>node_filesystem_size_bytes</code> and <code>node_memory_MemAvailable_bytes</code> are already scraped, so disk-pressure and memory alerts are writable today on the existing <code>ao-admin</code> job. <code>node_systemd_unit_state</code> is absent, so the systemd collector is off and restart-loop alerting needs it enabled on <code>ao-node-exporter</code>. GPU, Corda, radio, WebODM and payment metrics have no exporter deployed; each needs one named, internal-only. <code>--storage.tsdb.retention</code> is unset, so retention is the implicit default. Alertmanager is still unspecified.</td>
</tr>
<tr>
<td valign="top">OPS-28</td>
<td valign="top"><strong>Prometheus is published on a loopback port, so any local process can query it</strong></td>
<td valign="top">ST-19</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§17.2</td>
<td valign="top"><code>ao-prometheus.container</code> carries <code>PublishPort=127.0.0.1:9090:9090</code>, and §5.2 lists <code>http://127.0.0.1:9090/</code> as a documented listener. Loopback is not isolation: every process on the host, including any container with a host network, can query Prometheus and read its security evidence, which §17.2 forbids. <code>ao-admin</code> is <code>Internal=true</code> so there is no egress path; the boundary to close is lateral and local. Removing the publish also removes browser-based inspection, so name the replacement inspection path first — <code>podman exec</code> into the container is the obvious candidate. Needs an explicit operator decision; do not remove the port without one.</td>
</tr>
<tr>
<td valign="top">OPS-30</td>
<td valign="top"><strong>Off-site restic repository does not exist</strong></td>
<td valign="top">ST-18</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§17.1</td>
<td valign="top"><strong>Repository exists and verifies; deliberately not scheduled. 2026-10-03.</strong> Merged with the earlier duplicate of this item. The operator chose <code>/media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS</code>, which sits inside the running pCloud sync root, so the repository replicates to pCloud without a separate rclone remote. Initialised and proven: snapshot <code>56bf1af5</code>, 63 files, <code>restic check</code> no errors. It reuses the local repository password, so the existing <code>ao-admin/restic-repository-password</code> wallet entry governs both. <strong>Deliberately not live:</strong> no timer, no cron, no reference from <code>restic-run.sh</code> — the nightly job still writes only to the local repository. Enabling it is an operator decision.</td>
</tr>
<tr>
<td valign="top">OPS-31</td>
<td valign="top"><strong>The backup shares a filesystem with the data it protects</strong></td>
<td valign="top">ST-18</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§17.1</td>
<td valign="top">**Mitigated by the off-site repository, not closed. Measured by device id: <code>/ALWAYSON</code> and <code>/var/backups/alwayson-restic</code> are both device <code>66306</code>, so the local repository cannot survive loss of the root disk; the pCloud-rooted repository is device <code>2049</code>, different physical media. Because it is not yet scheduled, that copy is not yet maintained, so this stays open until off-site is enabled and holds consecutive snapshots. <code>ao-egress-archive</code> is not a substitute: §11.6 makes it a sale-transfer store with no restore duty.</td>
</tr>
<tr>
<td valign="top">OPS-29</td>
<td valign="top"><strong>Off-site restic repository does not exist</strong></td>
<td valign="top">ST-18</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§17.1, §11.6</td>
<td valign="top">The pCloud folder <code>ALWAYSON-RESTIC2PCLOUD</code> exists at the account root but is empty and nothing has been uploaded. Point the restic repository at it (rclone WebDAV or SFTP) so a second, host-disjoint copy exists. The repository is encrypted client-side, so pCloud holds ciphertext only, which stays inside the §11.6 boundary</td>
</tr>
<tr>
<td valign="top">OPS-32</td>
<td valign="top"><strong>The health projection writer shares Grafana's own application role instead of holding a dedicated least-privilege writer role</strong></td>
<td valign="top">ST-19</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§6.A.3, §4.1 rule 1</td>
<td valign="top">The 60s <code>ao-status-collect</code> projection writes schema <code>ao_status</code> inside the existing <code>grafana</code> database, so <strong>no new database, role, listener or network was needed</strong> — which is why the work could proceed without a superuser. <code>CREATEDB</code> is required for a new database and <code>CREATEROLE</code> for a new role, and <code>grafana_app</code> has neither (measured 2026-10-02: <code>select rolsuper, rolcreatedb from pg_roles where rolname='grafana_app'</code> → `f</td>
</tr>
<tr>
<td valign="top">OPS-33</td>
<td valign="top"><strong>Declared SQLite stores that are absent on this host render as absent, not as an error</strong></td>
<td valign="top">ST-19</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§4.2, §4.3, §17.2</td>
<td valign="top">The README §4.3 SQLite rows are all projected to <code>ao_status.sqlite_store</code> with `present=true</td>
</tr>
<tr>
<td valign="top">OPS-34</td>
<td valign="top"><strong>Grafana reads SQLite through snapshots, never the live personal databases</strong></td>
<td valign="top">ST-19</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§6.A.2, §6.A.3, §4.3</td>
<td valign="top"><strong>Superseded 2026-10-03 by operator directive: Grafana must have a real SQLite datasource.</strong> The reasoning that produced the snapshot design is retained here, not the earlier rejection. Grafana OSS 11.6.0 ships 19 bundled datasources and <strong>none is SQLite</strong> (verified in the running container: <code>ls /usr/share/grafana/public/app/plugins/datasource/</code>), so the <strong>community plugin <code>frser-sqlite-datasource</code></strong> is installed and named in <code>GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS</code> (allow-list of that one id, deliberately not <code>*</code>). It <strong>is unsigned</strong> — measured 2026-10-03: <code>plugin.json</code> carries <code>signature: null</code>, <code>signedByOrg: null</code>, and Grafana refuses to load it without the allow-list. That is the deviation, and it is bounded three ways: the id is named individually, the plugin is a <strong>pinned reviewed copy</strong> under <code>/ALWAYSON/data/monitoring/grafana-plugins</code> rather than fetched at start-up, and it is reachable only through read-only snapshots. One read-only datasource is provisioned <strong>per snapshot</strong> under <code>/var/lib/ao-sqlite</code>. <strong>Snapshots, not live files, is what makes this safe.</strong> The collector copies each permitted store with <code>VACUUM INTO</code> — which forces a non-WAL <code>delete</code>-mode output — into <code>/ALWAYSON/data/monitoring/sqlite-snapshots/</code>, so the plugin never opens a WAL database read-only (a WAL open needs a writable <code>-shm</code>) and never touches the original. Measured 2026-10-03: 7 snapshots integrated (<code>db-podman</code> 12 tables, <code>db-elisa</code> 12, <code>db-openclaw-agent-main</code> 21, <code>db-openclaw-agent-sitebot</code> 21, <code>db-nperf-history</code> 2, <code>db-nperf-settings</code> 1, <code>db-reticulum-meshchatx-observer</code> 4). This avoided the alternative the earlier row rejected: <strong>no ACL, no mode change and no bind mount of any personal file</strong> — the sources are opened only by the host collector, and <code>integrated=false</code> rows are never snapshotted. <strong>Mail and browser stores are excluded by operator instruction</strong>: no Akonadi mail database, no Chrome/Edge/Brave/Firefox history, cookies, autofill or <code>Login Data</code>. Only the non-personal system stores above are integrated. One datasource per snapshot is required because the plugin executes against the datasource's single <code>path</code> — its <code>databases</code> list is a UI picker only (measured: panels naming a different target returned the default <code>db-podman</code> rows).</td>
</tr>
</table>

## 19.2 Completed items and verification evidence

Finished work, kept once with the evidence that closed it, followed by the standing
verification checks against the running system. Nothing listed here is outstanding.

<table>
<thead>
<tr>
<th align="left" width="4%">ID</th>
<th align="left" width="13%">Item</th>
<th align="left" width="5%">Component</th>
<th align="left" width="7%">Status</th>
<th align="left" width="11%">Standard served</th>
<th align="left" width="60%">Current state or acceptance criteria</th>
</tr>
</thead>
<tbody>
<tr>
<td valign="top">—</td>
<td valign="top">Prometheus access to the databases</td>
<td valign="top">ST-19</td>
<td valign="top"><strong>Complete</strong></td>
<td valign="top">§17.2, §3.3</td>
<td valign="top">COMPLETE — verified 2026-10-03. Prometheus now holds <code>alwayson_db_*</code> series over <strong>every</strong> database declared in §3.3.1 — seven PostgreSQL targets and three SQLite stores, each reporting its own reachability. Mail (Akonadi/KDE PIM) and browser profile stores are excluded by operator instruction and are not touched. <code>scripts/operations/collect-db-security.py</code> is a host-side read-only pass that writes node_exporter textfile format to <code>data/prometheus-textfile/</code>, run every 60s by <code>ao-db-security-collect.timer</code> and surfaced through the already-scraped <code>node-host</code> job. Measured: <code>curl -s localhost:9090/api/v1/label/__name__/values</code> returns the 13 series; <code>alwayson_db_postgres_backends{db="grafana"}</code> reads 21; <code>alwayson_db_sqlite_integrity_ok{db="meshchatx",result="ok"}</code> is 1 over a 43-table store. <strong>Three constraints were measured, not assumed, and each changed the design.</strong> Every container on <code>ao-admin</code> is <code>Internal=true</code> and cannot reach the databases — TCP probes from <code>ao-prometheus</code> and <code>ao-node-exporter</code> to the host PostgreSQL both returned NOT-reachable — so the collector must be a host process, not a container. The same isolation blocks the gateway: a probe from inside <code>ao-prometheus</code> to <code>10.89.9.1:9101</code> returned NOT-reachable, so a separate exporter port cannot be scraped at all. The textfile collector exists only in node_exporter (the <code>prom/prometheus</code> binary has none), which is why these metrics ride the existing job instead of a new one. Connection detail worth recording: <code>pg_hba.conf</code> grants the application roles <code>scram-sha-256</code> on <code>host 127.0.0.1</code> but <code>peer</code> on the local socket for non-superusers, so a unix-socket connection fails as <code>Peer authentication failed</code> however correct the password is; TCP is the path scram accepts. No credential is given to Prometheus — the collector holds the wallet-backed read identity and emits metric lines only, verified by grepping the output for the password value (absent).</td>
</tr>
<tr>
<td valign="top">—</td>
<td valign="top">Prometheus isolation from Grafana</td>
<td valign="top">ST-19</td>
<td valign="top"><strong>Complete</strong></td>
<td valign="top">§17.2, §3.3</td>
<td valign="top">COMPLETE — verified 2026-10-02. Grafana no longer has any Prometheus source: <code>prometheus.yml</code> deleted, <code>Requires=ao-prometheus.service</code> removed (<code>systemctl --user show ao-grafana.service -p Requires -p After -p Wants</code> returns 0 prometheus references), and the 23 dashboard panels are served by a 60s host projection in schema <code>ao_status</code>. Prometheus reports only to itself.</td>
</tr>
<tr>
<td valign="top">—</td>
<td valign="top">Fresh signed ActivityPub round trip</td>
<td valign="top">ST-13, ST-14</td>
<td valign="top"><strong>Complete</strong></td>
<td valign="top">§15.4.4</td>
<td valign="top">COMPLETE — verified end-to-end 2026-10-01 22:53 UTC. Inbound federation had produced zero remote statuses for the life of the instance. Cause: <code>ao-mastodon-sidekiq</code> overrode the queue list with <code>-q</code> flags, which makes sidekiq ignore <code>config/sidekiq.yml</code> entirely. <code>ActivityPub::ProcessingWorker</code> targets the <code>ingress</code> queue, which was absent from the list, so jobs were enqueued and accepted but never polled. The same line misspelled <code>pull</code> as <code>pull_request</code>, orphaning 33 more workers. Fixed by removing the <code>-q</code> flags so the image's own config is authoritative. Proof: a probe job sat in <code>queue:ingress</code> (depth 1) before the fix and was consumed on boot after it; a real signed post from <code>mastodon.social</code> then produced a remote status plus 5 mention notifications, moving <code>from REMOTE accounts</code> from 0 to 8. The restart also drained a backlog of 7 posts from 21:18–21:28 that had been delivered and verified all along but unread — confirming the fault was a missing consumer, not a delivery or signature problem. Evidence: <code>logs/operations/2026-10-01-mastodon-inbound-federation-ingress.log</code>. Do not set <code>ALLOWED_PRIVATE_ADDRESSES</code> to make a test pass — the private-address 401 is the SSRF guard working.</td>
</tr>
<tr>
<td valign="top">—</td>
<td valign="top">Mastodon service-account consolidation</td>
<td valign="top">ST-13</td>
<td valign="top"><strong>Complete</strong></td>
<td valign="top">§14.1.1, §19 row 17</td>
<td valign="top">Complete. The <code>alwayson-sales</code> (UID 993) placement has been folded back to the operator account <code>scottw</code> and the duplicate store retired. No separate service-account user is used.</td>
</tr>
<tr>
<td valign="top">—</td>
<td valign="top">Per-modal purchase buttons, HTML-300X3</td>
<td valign="top">ST-11</td>
<td valign="top"><strong>Complete</strong></td>
<td valign="top">§7.1.1</td>
<td valign="top">Implemented in the repo and the static export mirrored to the pCloud Public Folder.</td>
</tr>
<tr>
<td valign="top">—</td>
<td valign="top">kwalletd6 D-Bus access details</td>
<td valign="top">ST-24</td>
<td valign="top"><strong>Complete</strong></td>
<td valign="top">§14.1.1</td>
<td valign="top">Done 2026-10-01. Verified and recorded in §14.1.4: bus <code>org.kde.kwalletd6</code>, object <code>/modules/kwalletd6</code>, interface <code>org.kde.KWallet</code>, plus the <code>wallets</code> / <code>open</code> / <code>readPassword</code> / <code>writePassword</code> / <code>folderList</code> / <code>hasFolder</code> / <code>entriesList</code> signatures and two <code>busctl</code> pitfalls.</td>
</tr>
<tr>
<td valign="top">—</td>
<td valign="top"><code>foxglove_bridge</code> unavailable</td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Complete</strong></td>
<td valign="top">§10.2.1</td>
<td valign="top">Complete 2026-10-02. The bridge is built locally as <code>localhost/foxglove-bridge</code> (own Containerfile, digest-pinned) rather than installed from <code>packages.ros.org</code>, which stays unreachable per item 48 — so that blocker no longer gates Foxglove views. Two silent faults had to be cleared first. The gz→ROS hop needs the five <code>gz_*_vendor/lib</code> directories and <code>/opt/ros/lyrical/lib</code> on <code>LD_LIBRARY_PATH</code>; without them the process stayed up, accepted connections, bridged nothing, and logged no error. And the server must set <code>GZ_IP=0.0.0.0</code> — the GUI appeared to work without it only because it shares the server's network namespace, which masked a container with no route. The bridge must also be on both <code>ao-html-window</code> and <code>ao-sim-fabrication</code>: a matching <code>GZ_PARTITION</code> does not route between two internal bridges. Verified 2026-10-02: <code>Advertising new channel 4 for topic "/factory/camera/image"</code>, <code>sensor_msgs/msg/Image</code> publisher count 1, frames at the world's 10 Hz.</td>
</tr>
<tr>
<td valign="top">—</td>
<td valign="top">Digest-pinning of operational images</td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Complete</strong></td>
<td valign="top">§4.1 rule 9</td>
<td valign="top">Complete 2026-10-01. <code>ao-grafana</code>, <code>ao-metabase</code>, <code>ao-prometheus</code>, <code>ao-node-exporter</code> and <code>mastodon-streaming</code> pinned to the digests of the images already validated in place (streaming was tag-only while its siblings were pinned). <code>ao-sim-fabrication-gz</code> is a local build, so its digest records the validated build and a rebuild now fails the unit by design. The last floating tag, <code>nginx:alpine</code> on <code>gazebo-portal</code>, disappeared with that container's retirement — the <code>:8765</code> portal is now a python3 host process, so every running image is digest-pinned. Re-run the audit command in §19.1 to confirm.</td>
</tr>
</table>

**Verification evidence.** These are checks run against the running system, not completed work items. Each row records the outcome of a check.

<table>
<thead>
<tr>
<th align="left" width="24%">Check</th>
<th align="left" width="62%">Evidence</th>
<th align="left" width="14%">Component</th>
</tr>
</thead>
<tbody>
<tr>
<td valign="top">Host inventory</td>
<td valign="top">Inventory report completed</td>
<td valign="top">ST-01</td>
</tr>
<tr>
<td valign="top">Loopback service reachability</td>
<td valign="top"><code>scripts/validation/check-local-services.js</code> drives Chrome under Playwright against the inventory in <code>config/platform/loopback-services.yaml</code>; <strong>15 pass, 0 fail, 0 unverifiable</strong> (2026-10-01, re-run after the WebODM loopback publication and the Mastodon proxy TLS change; earlier runs were 14 pass / 1 unverifiable). The previous UNVERIFIABLE entry is gone: WebODM now publishes <code>127.0.0.1:8000</code> and is checked like any other loopback service, its expectation being the followed <code>200</code> on <code>/login/</code>. The Mastodon proxy is now <code>https://127.0.0.1:3300</code> and passes because the harness already sets <code>--ignore-certificate-errors</code> and <code>ignoreHTTPSErrors: true</code> for the self-signed certificate. Every loopback service also refuses on the LAN address <code>10.42.0.1</code>, so the loopback boundary holds</td>
<td valign="top">ST-01</td>
</tr>
<tr>
<td valign="top">Operator console <code>:8099</code> and Gazebo portal <code>:8765</code></td>
<td valign="top">Both verified 200. The console has no unit and is started by hand for the check, then stopped. <strong>Discrepancy:</strong> <code>config/platform/topology-model.yaml</code> and <code>config/platform/version-matrix.yaml</code> record <code>:8765</code> as <code>foxglove_bridge</code>; it is the <code>gazebo-portal</code> container and <code>foxglove_bridge</code> was not listening. To reconcile when the Gazebo work lands</td>
<td valign="top">ST-05, ST-08</td>
</tr>
<tr>
<td valign="top">Photogrammetry drive</td>
<td valign="top">UUID verified; directory tree created</td>
<td valign="top">ST-03</td>
</tr>
<tr>
<td valign="top">Package/version matrix</td>
<td valign="top">Captured and refreshed</td>
<td valign="top">ST-01</td>
</tr>
<tr>
<td valign="top">GUI boundary matrix (section 19)</td>
<td valign="top"><code>config/platform/gui-boundary-matrix.yaml</code> created; 10 entries validated (YAML), covering all Section 6.A scope items</td>
<td valign="top">Partial — §19 documentation artifact, no component status</td>
</tr>
<tr>
<td valign="top">Rootless Podman and Quadlet</td>
<td valign="top">Verified; mixed-store deviation documented</td>
<td valign="top">ST-01</td>
</tr>
<tr>
<td valign="top">GPU runtime</td>
<td valign="top">Driver/CDI verified; CPU baseline and GPU smoke completed</td>
<td valign="top">ST-25</td>
</tr>
<tr>
<td valign="top">Domain network isolation</td>
<td valign="top">Internal workload networks and test verified</td>
<td valign="top">ST-02</td>
</tr>
<tr>
<td valign="top">Firewall and ports</td>
<td valign="top">UFW active; prior <code>:80</code> and <code>:1716</code> exposure cleared</td>
<td valign="top">ST-01</td>
</tr>
<tr>
<td valign="top">WebODM smoke test</td>
<td valign="top"><code>apt-76</code>; 76 images; GPU-enabled orthophoto produced</td>
<td valign="top">ST-03</td>
</tr>
<tr>
<td valign="top">Vehicle simulation</td>
<td valign="top">Headless Gazebo 300-iteration and ROS-Gazebo bridge test</td>
<td valign="top">ST-07</td>
</tr>
<tr>
<td valign="top">Fabrication simulation</td>
<td valign="top">Headless Gazebo 300-iteration and bridge test</td>
<td valign="top">ST-08</td>
</tr>
<tr>
<td valign="top">Heltec/LoRa detection</td>
<td valign="top">Heltec V3 connected; stable by-id + <code>/dev/heltec-v3</code> path, udev rule installed, <code>detect-heltec.sh</code> OK, serial probe received c0-framed packets 2026-08-31; LoRa-link test pending ao-field gateway</td>
<td valign="top">ST-04, ST-22</td>
</tr>
<tr>
<td valign="top">Corda receipt</td>
<td valign="top">Corda 5.2.2 <strong>CLI installed</strong>; no node, <code>cordadb</code> empty, key ceremony pending</td>
<td valign="top">ST-09</td>
</tr>
<tr>
<td valign="top">Sales receipt manifest</td>
<td valign="top">Sales DB deployed; provider/API pending</td>
<td valign="top">ST-11, ST-12</td>
</tr>
<tr>
<td valign="top">Backup</td>
<td valign="top">Encrypted restic snapshot <code>548d9910</code> completed; recurring schedule automated 2026-08-31 (restic nightly 03:30 timer, weekly integrity verify Sun 04:30, nightly domain DB dumps 03:00 for mastodon/sales/webodm); verification snapshot <code>32be2a1c</code> saved</td>
<td valign="top">ST-18</td>
</tr>
<tr>
<td valign="top">Restore</td>
<td valign="top">File hash validated; database 14/14 tables restored</td>
<td valign="top">ST-18</td>
</tr>
<tr>
<td valign="top">Monitoring stack (ao-admin)</td>
<td valign="top">Prometheus + node_exporter + Grafana run as <code>scottw</code> Quadlet units on <code>ao-admin</code>. Grafana application state is genuinely PostgreSQL-backed against the host cluster over the <code>/var/run/postgresql</code> socket (<code>/api/health</code> reports <code>database: ok</code>). Prometheus is isolated and reports only to itself (§17.2). Both Prometheus targets scrape <code>up</code></td>
<td valign="top">ST-19</td>
</tr>
<tr>
<td valign="top">Metabase reporting (ao-admin)</td>
<td valign="top"><strong>Working.</strong> Metabase runs on the host and serves its login page in the browser, which is the expected operator surface. <strong>Operator-confirmed 2026-09-28; this supersedes the earlier "not serving" finding.</strong> The earlier record described a containerised <code>ao-metabase</code> instance failing during application-database setup and cycling under <code>Restart=on-failure</code>; that container and that fault are not the service the operator uses</td>
<td valign="top">ST-20</td>
</tr>
<tr>
<td valign="top">Mastodon local stack (ao-sales)</td>
<td valign="top">All 5 containers run under the <code>scottw</code> operator account in the single <code>ao-sales</code> store (Section 20.0); the former <code>alwayson-sales</code> account and its duplicate store are retired. Web <code>127.0.0.1:3000</code> and streaming <code>127.0.0.1:4000</code> verified; <code>/api/v1/instance</code> reports <code>mastodon.300x3.com</code> v4.3.7</td>
<td valign="top">ST-13</td>
</tr>
<tr>
<td valign="top">Mastodon federation edge</td>
<td valign="top">Dedicated Cloudflare Tunnel <code>ao-mastodon-federation</code> for <code>mastodon.300x3.com</code>; HTTP/2 connector active; actor and WebFinger 200; storefront hostnames preserved; <code>LOCAL_DOMAIN=mastodon.300x3.com</code>; canonical accounts <code>admin@mastodon.300x3.com</code> and <code>bot@mastodon.300x3.com</code> (<strong>Owner handle is <code>admin@mastodon.300x3.com</code></strong> — renamed from <code>aoadmin</code> on 2026-10-01; <code>admin</code> was freed by removing it from the instance's <code>reserved_usernames</code> <strong>setting</strong>, which is configurable, not hardcoded. The old <code>.../users/aoadmin</code> URI is published as <code>alsoKnownAs</code> so existing links and followers redirect); community publication carried inside <code>ao-sales</code> on web/background-workers only; local-to-remote follows confirmed; reverse-follow validation pending</td>
<td valign="top">ST-14</td>
</tr>
<tr>
<td valign="top">WebODM operator workflow restart</td>
<td valign="top">Stack is rootless (scottw/mapping store); system-store recovery step correctly found no system-store containers — no action needed</td>
<td valign="top">ST-03</td>
</tr>
<tr>
<td valign="top">ArduPilot SITL MAVLink</td>
<td valign="top">ao-ardupilot-sitl.service flags fixed; HEARTBEAT (sysid 1, QUADROTOR, ArduPilot) validated over tcp:127.0.0.1:5760 via pymavlink</td>
<td valign="top">ST-07</td>
</tr>
<tr>
<td valign="top">Heltec firmware</td>
<td valign="top">RNode firmware 1.85 recorded via rnodeconf; EEPROM valid; signature unverified (operator signing option)</td>
<td valign="top">ST-04</td>
</tr>
<tr>
<td valign="top">Reticulum executable</td>
<td valign="top">Standalone RNS 1.4.2 available at <code>/home/scottw/.local/bin/rnsd</code>; active Reticulum runtime is embedded in MeshChatX</td>
<td valign="top">ST-05</td>
</tr>
<tr>
<td valign="top">MeshChatX deployment</td>
<td valign="top">Native headless backend running since 2026-09-24 11:02 local time; local UI bound to <code>127.0.0.1:18000</code>; desktop metadata declares 4.9.1</td>
<td valign="top">ST-06</td>
</tr>
<tr>
<td valign="top">Reticulum interface configuration</td>
<td valign="top">29 TCP clients use <code>interface_enabled = true</code>; two RNodes use <code>interface_enabled = true</code>; one Backbone uses <code>enabled = yes</code>; zero explicitly disabled</td>
<td valign="top">ST-05</td>
</tr>
<tr>
<td valign="top">Reticulum runtime participation</td>
<td valign="top">Logs show auto-connections, peering, announces, and LXMF/Nomad network announcements</td>
<td valign="top">ST-05</td>
</tr>
<tr>
<td valign="top">Reticulum connectivity</td>
<td valign="top">Startup logs contain timeouts, network-unreachable errors, connection refusals, and reconnect cycles for named and discovered interfaces</td>
<td valign="top">ST-05</td>
</tr>
<tr>
<td valign="top">Reticulum public gateway</td>
<td valign="top">MeshChatX is bound to <code>0.0.0.0:4242</code>; the host had <code>192.168.87.135/24</code> on Wi-Fi</td>
<td valign="top">ST-05</td>
</tr>
<tr>
<td valign="top">Two-radio Reticulum initialization</td>
<td valign="top">Both serial paths exist and MeshChatX logged both RNodes as configured and powered up on 2026-09-24</td>
<td valign="top">ST-04</td>
</tr>
<tr>
<td valign="top">RNode band feedback</td>
<td valign="top">Functional feedback observed on both 915 MHz and 917 MHz paths</td>
<td valign="top">ST-04</td>
</tr>
<tr>
<td valign="top">MeshChatX cryptographic-state persistence</td>
<td valign="top">12,364 historical <code>umsgpack</code> errors; error block ends before newer 16:29Z and 16:51Z startup entries</td>
<td valign="top">ST-05</td>
</tr>
<tr>
<td valign="top">MeshChatX version provenance</td>
<td valign="top">Desktop metadata declares 4.9.1; executable hash matches the local manifest; running version remains unverified; repository cache contains a 4.8.4 wheel</td>
<td valign="top">ST-06</td>
</tr>
</table>

## 19.3 Operator setup priorities

The operator's own ordering of the work above. Priority here does not change what §19.1
requires — it is the order the operator intends to work in.

| Order | Priority |
|---:|---|
| 1 | Sales pipeline |
| 2 | Gazebo simulation boning |
| 3 | RPi5 LoRa connection |
| 4 | 3D printer fan repair |
| 5 | Instructables outlining |

---
