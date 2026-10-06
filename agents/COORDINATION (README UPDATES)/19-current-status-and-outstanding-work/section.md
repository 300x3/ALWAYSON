## 19.1 The log

<table>
<thead>
<tr>
<th align="left" width="7%">ID</th>
<th align="left" width="12%">Item</th>
<th align="left" width="9%">Component</th>
<th align="left" width="11%">Status</th>
<th align="left" width="8%">Standard served</th>
<th align="left" width="53%">Current state or acceptance criteria</th>
</tr>
</thead>
<tbody>
<tr>
<td valign="top">—</td>
<td valign="top"><strong>COMPONENTS</strong> — The state of each component. Source of truth for what is built.</td></td>
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
<td valign="top">Delivered: the 3D world and its boned cell datums, eight cameras derived from those datums, the view-only HTML portal, and the local Foxglove 3D viewer. Headless Gazebo 300-iteration and bridge test passed; model views rendered in §10.2. <strong>Not delivered</strong>, though named in the §10.2 component tree: the facility scheduler (SIM-12), the safety-zone and interlock model (SIM-13), and RL objects as world entities rather than a catalogue (SIM-14)</td>
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
<td valign="top">—</td>
<td valign="top"><strong>OPEN WORK</strong> — Everything still to be done, by group.</td></td>
<td valign="top"></td>
<td valign="top"><strong>Open</strong></td>
<td valign="top"></td>
<td valign="top"></td>
</tr>
<tr><td colspan="6" style="background-color:#c9ccd1; border-top:2px solid #8a8f98; border-bottom:1px solid #8a8f98; padding:5px 8px; font-weight:bold; letter-spacing:0.04em;">PLAT · Platform, install and runtime — 4 items, all Open</td></tr>

<tr>
<td valign="top">PLAT-02</td>
<td valign="top">Version matrix refresh</td>
<td valign="top">ST-01, ST-25</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§4.1 rule 9</td>
<td valign="top"><strong>Partly done 2026-10-01.</strong> The <code>mastodon</code> rows now record the digests actually in use (they recorded tags, understating the pinning), <code>local_domain</code> corrected to <code>mastodon.300x3.com</code>, and the <code>RAILS_FORCE_SSL=true</code> note replaced — those switches are inert, and the local UI is served over TLS by the loopback proxy at <code>https://127.0.0.1:3300</code>. A new <code>operations</code> section records the Grafana/Metabase/Prometheus/node-exporter digests. <strong>Remaining:</strong> still hand-edited rather than captured, and the Gazebo <code>nginx:alpine</code> row is knowingly unpinned.<br><br><strong>PROGRESS by 02-platform-baseline.</strong> **Half of this item was already done and the item was never updated to say so.** The
`nginx:alpine` row PLAT-02 exists to fix has not existed in `quadlet/` or `config/` since the
`gazebo-portal` container was retired — `grep -rn 'nginx:alpine' . --exclude-dir=.git` returns
only historical mentions in `docs/compliance/installation-status.md`, `GAZEBO/`, an archived
`TOPOLOGY/` JSON, and the §19 text itself. §19.2 stated this on 2026-10-01; PLAT-02 was left
open against the old wording.

§2.5 of my section records the audit. Findings:

- **Repository is clean.** Only two tag-only `Image=` lines, both deliberate (`ardupilot-sitl:latest`,
  a local `localhost/` build).
- **Six running containers are tag-only** — four Grafana on `:11.6.0`, two on
  `localhost/foxglove-bridge:latest`. All six have `podman run`-generated names, so **no
  Quadlet unit owns them**; they duplicate the pinned `ao-grafana` and
  `ao-sim-fabrication-foxglove`. They are §19 `OPS-16` strays and are **not removed here** —
  container deletion needs operator approval.
- **Three matrix rows are stale**, and the PostgreSQL one is the serious: the matrix records
  `postgres@sha256:a65e6a84…` while `ao-sales-db`, `mastodon-db` and `ao-fabrication-db`
  actually run `postgres@sha256:d74eeac9…`. A version matrix naming a digest nothing runs
  cannot verify what is deployed. `host.kernel` records `7.0.0-34-generic` against a live
  `7.0.0-38-generic`, and the toolkit row records `1.20.0` against `1.20.1-1`. Four further
  running digests are absent from the matrix entirely.

**What I got wrong.** I first wrote "all 25 running containers are digest-pinned" from reading
the `sort -u` digest list rather than counting the exceptions, and only caught it when I ran
`podman ps ... | grep -v '@sha256:'` to cite a figure — it returned six. The reason I got it
wrong: I summarised the digest-pinned list and never enumerated its complement. §2.5 now states
six, names them, and says why none of them belongs to a unit.

**Not closed.** `PLAT-02` also asks for capture automation, which is `OPS-02` and belongs to
OPS-B; and the matrix rows need editing, and `config/platform/version-matrix.yaml` is not mine
to edit. Recorded in §2.5, left for the compiler and OPS-B.<br><br><strong>Evidence:</strong><br><code># the nginx:alpine row PLAT-02 names is already gone<br>$ grep -rn 'nginx:alpine' . --exclude-dir=.git | grep -E '^\./(quadlet|config)/'<br>(no output)<br>$ sed -n '6,7p' quadlet/sim-fabrication/ao-sim-fabrication-portal.service<br># THIS REPLACES "gazebo-portal". That container was a throwaway nginx whose<br># docroot was the stock /usr/share/nginx/html<br>$ grep -n 'image_nginx' config/platform/version-matrix.yaml<br>46:  image_nginx: "not in use - the :8765 portal is the ao-sim-fabrication-portal.service python3 host process"</code></td>
</tr>


<tr><td colspan="6" style="background-color:#c9ccd1; border-top:2px solid #8a8f98; border-bottom:1px solid #8a8f98; padding:5px 8px; font-weight:bold; letter-spacing:0.04em;">NET · Networks, adapters and isolation — 4 items, all Open</td></tr>
<tr>
<td valign="top">NET-51</td>
<td valign="top"></td>
<td valign="top"></td>
<td valign="top"><strong>Open</strong></td>
<td valign="top"></td>
<td valign="top"># Three cross-group findings from the SPEC review, none of them mine to close

## 2. NET-51 — three `Internal=false` networks, and the isolation rule is not absolute

`AGENTS.md` and the workspace rules state flatly that "All workload networks are
`Internal=true`". Measured, **three of fourteen are not**: `ao-reporting-egress`,
`ao-sales`, `ao-build-update`. All three are egress networks, which cannot be `Internal`
and still reach anything, so this is the rule working rather than breaking. But the rule as
written is not literally true, and any security argument that leans on it is wrong by
three. The registry and live state agree exactly, so nothing is out of sync — only the
summary sentence is over-broad. I have documented all fourteen with their flags in §3 so
the exception is visible where the rule is stated.

Related: §3.3.0.1's "no route off the subnet" is a statement about a *container's* view,
not the host's. Nothing in `Internal=true` constrains the host's own interfaces, and the
host has a Wi-Fi interface on `192.168.87.0/24` that §3 does not mention at all.

## What I got wrong

Three things, all caught by re-running my own commands:

1. **The label key.** Spent a full review pass asserting ownership facts from a key that
   is set on nothing. The conclusion held but the evidence did not support it. Recorded in
   §6 with the correction inline.
2. **"Contiguous and gap-free."** I asserted this about the `10.89` block without checking.
   It is false — third octet `11` is absent. It happens to be the one already-known
   unallocated subnet, so it is consistent rather than a new problem, but I would have
   published a false claim. Caught by counting, not by reading.
3. **"The only non-`ao-` addressing is `10.42.0.0/24`."** Also asserted without checking,
   also false — there is a `192.168.87.0/24` Wi-Fi network and a link-local. Both 2 and 3
   are the same failure: writing a general statement about a set I had only partially
   enumerated.
4. **"§3 describes the host as having only the equipment LAN."** This one was wrong in the
   *opposite* direction, which is the more useful kind to catch. I asserted the Wi-Fi
   interface was undocumented project-wide; having recompiled the README I checked the whole
   document instead of only my own section, and it is documented in at least two others
   (§5 host-address row, and the MeshChatX `0.0.0.0:4242` note in §9). The real finding is a
   consistency gap in §3 alone, not a gap in the record. Had I not recompiled before
   committing, that would have gone into the README as a claim that two other sections are
   missing something they are not missing.

The pattern across all four is the same: I generalised from a partial enumeration, and each
time the correction came from running the check rather than from re-reading my own text.
Re-reading is not verification.

I have kept both corrections visible in §3 rather than quietly deleting the wrong text,
because the wrong text was already there and the next reader needs to know it was wrong.
## 1. NET-51 (new) — the Quadlet ownership label is `PODMAN_SYSTEMD_UNIT`, not `io.podman.annotations.quadlet`

This is the most consequential finding of my pass, and it is a **methodology** finding
rather than a defect: on this host the intuitive label key is set on *nothing*, so any
ownership enumeration using it returns all-empty and looks like a discovery.

Every session that has claimed "these containers have no Quadlet label" may have done so
with the wrong key. My own §6 evidence did. The conclusion in that case survived, but only
by luck — I had named the containers by hand, so the correct reading came from the name
list rather than from the query. **A session that enumerated by image string and then
filtered on the label would have concluded that no container on this host has a service
owner, and that is the opposite of the truth.**

I have corrected my own evidence and left a trap note in §6, but other sections may carry
the same bad evidence and those files are not mine. This needs a sweep by whoever owns the
affected sections.</td>
</tr>
<tr>
<td valign="top">NET-01</td>
<td valign="top"><strong>Controlled ingress/egress adapters</strong></td>
<td valign="top">ST-12, ST-17</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§5.2</td>
<td valign="top"><code>ao-build-update</code> <strong>scaffolded and deployed, not enabled</strong> (§5.2.1): its own <code>Internal=false</code> egress network at <code>10.89.13.0/24</code>, digest-pinned unit, read-only registry allowlist, and acquisition script that resolves candidates, captures digests, and writes an update audit record with no promotion authority. <strong>Remaining:</strong> operator decision on enabling it, and the <code>build</code>/<code>update</code> scope question. <code>ao-ingress-payment</code> and <code>ao-egress-archive</code> still require implementation with destination allowlists, validated TLS, separate credentials, and connection logging. Community publication is carried inside <code>ao-sales</code>.<br><br><strong>PROGRESS by 05-network-domains-and-controlled-external-access.</strong> **NET-01 stays open. I completed the documentation half and stopped at the two
halves that the rules forbid without your approval.**

Done: §5.2.1 no longer implies the build-update adapter can reach the internet
when nothing is running, and — the substantive correction — it no longer claims
the destination allowlist is enforced. It now records the measured state (unit
files installed, `is-enabled` = `generated`, `is-active` = `inactive`, network
allocated at `10.89.13.0/24` with `Internal=false` and zero attached
containers), and it states in two places that the allowlist is documentation of
intent rather than an operating control. I found that second claim while
verifying the first: the old text said allowlisted acquisition is "the only
sanctioned outbound", which is true as a *requirement* and false as a
*description*. A config file in a config tree reads as a boundary, and this one
is not one.

Not done, and deliberately:

1. **The destination allowlist is inert.** `registry-allowlist.yaml` and
   `stable-refs.yaml` are populated config that nothing enforces. The network
   is a plain `Internal=false` bridge, so anything attached to it can reach
   anything on the internet. Making the allowlist binding requires a firewall
   rule set, a filtering proxy, or per-destination proxies — firewall policy and
   public routing, which is Rule 6 and Rule 12 territory. My brief says stop for
   ports; I have stopped.

2. **The required separate credentials are a secret acquisition**, which my
   brief stops on explicitly. Even with approval, the token must go to KDE
   Wallet and must not appear in a log line, a proposal, or a commit.

3. **Verification of "TLS validation" requires a live pull from the public
   internet**, which is an uncontrolled acquisition — the exact thing the
   control exists to prevent. I am not resolving that by widening access.

**Why I am reporting rather than escalating a design.** The three items are
sequential: an allowlist that is not enforced is worse than no allowlist,
because it reads in the config tree as a control that exists. Two options are
honest and both need you: (a) approve a specific enforcement mechanism — a
firewall rule set on the `ao-build-update` bridge is the smallest — and I
implement it; or (b) leave the adapter scaffolded and change §5.2.1 to say the
allowlist is *documentation of intent*, not a control, so no future reader
mistakes a config file for a boundary. I recommend (b) as the current truth and
(a) as the fix. I did not pick one for you because it is firewall policy.

**Assumptions.** I assume `is-enabled: generated` means the unit is not enabled
to start at boot, which is consistent with `is-active: inactive` and with the
absence of any `ao-build-update` container in `podman ps`. If you know a
mechanism that starts it, tell me and I will re-measure.<br><br><strong>Evidence:</strong><br><code>NET-01 requires three things and I can do exactly one of them. Two are<br>blocked by rules that say stop, not try harder.</code><br><br><strong>PROGRESS by 05-network-domains-and-controlled-external-access.</strong> **NET-01 stays open; this corrects the evidence, not the status.** I had
recorded the destination allowlist as unenforced. It is enforced in code -
verified above by execution, three cases, exit 4/4/0. The gap is narrower
than I wrote: the script is a genuine control, not documentation of intent.

§5.2.1's blockquote now distinguishes the two controls instead of conflating
them. The allowlist governs *this script*; it does not govern the segment.
`Internal=false` means anything else attached to `ao-build-update` reaches the
internet without consulting the list at all. So "the only sanctioned outbound"
in **Containment** is still a requirement the adapter must satisfy rather than
a property the network has, and the standing instruction not to attach a
container to this network still stands.

The two stop conditions are unchanged and still operator decisions: a
firewall/proxy design for segment-level enforcement, and separate adapter
credentials. I did not author either, did not touch firewall policy, and did
not create a credential.<br><br><strong>Evidence:</strong><br><code>CORRECTION TO MY OWN EARLIER CLAIM. net-NET-01.md says, and §5.2.1 said<br>until this commit, "Nothing at runtime reads registry-allowlist.yaml".<br>That is FALSE. The allowlist IS read at runtime and it DOES refuse<br>disallowed references. Measured 2026-10-04:</code><br><br><strong>PROGRESS by 05-network-domains-and-controlled-external-access.</strong> **NET-01 stays open. What changed is that my section no longer contradicts
itself about whether the allowlist works.**

The corrected **Containment** paragraph now reads "enforced in code, unenforced
at the segment", matching the verified evidence above it, and states plainly
that its previous wording was wrong. The substance of the item is unchanged and
still blocked:

- **Segment-level enforcement is absent.** `ao-build-update` is an ordinary
  `Internal=false` bridge; anything else attached to it reaches the internet
  without consulting the allowlist. Closing this needs firewall or proxy policy,
  which is Rule 6 and §4.1 rule 13 territory. Not authored, not touched.
- **Separate adapter credentials** are a secret acquisition, an explicit stop
  condition. Not created.
- **`ao-ingress-payment` and `ao-egress-archive`** remain unimplemented, needing
  destination allowlists, validated TLS, separate credentials and connection
  logging.

All three remain operator decisions. I did not touch firewall policy, did not
create a credential, and did not enable the unit.<br><br><strong>Evidence:</strong><br><code>FOLLOW-UP to net-NET-01.md and net-NET-01-correction.md, neither of which I<br>have modified. NET-01 REMAINS OPEN. This records a contradiction between two<br>paragraphs of my own section file, which the earlier corrections left behind.</code></td>
</tr>



<tr><td colspan="6" style="background-color:#c9ccd1; border-top:2px solid #8a8f98; border-bottom:1px solid #8a8f98; padding:5px 8px; font-weight:bold; letter-spacing:0.04em;">SEC · Secrets, credentials and identity — 3 items, all Open</td></tr>
<tr>
<td valign="top">SEC-04</td>
<td valign="top"></td>
<td valign="top"></td>
<td valign="top"><strong>Open</strong></td>
<td valign="top"></td>
<td valign="top">**New item, not a closure.** SEC-01 through SEC-03 are policy/documentation items blocked on
one operator decision. This is a different kind of thing: a live fault in the delivery
mechanism, found by re-measuring rather than inherited, and it is not covered by any of the
three.

Recorded as **§14.1.7**. What that subsection contains, all of it measured above: the absent
`ao-payment` folder; the file-older-than-process staleness; the `ExecStartPre=-` prefix that
silences the failure; the live `sales-db-password` embedded in the stale DSN and the resulting
correction to ST-12; and the guard carve-out that makes the file invisible.

Also added to §14.2.5 as **break-glass step 2**: compare env-file mtime against the unit's
`ActiveEnterTimestamp`. This is now the cheapest check in the list and the only reliable
signal for this class of fault, because a fetch failing under `-` produces no log line at
all. Existing steps renumbered 3–5 to make room; no step was removed.

Why this is not folded into SEC-01: SEC-01 asks the operator to ratify a deviation or
authorise a migration. This is a service running now on stale credential material, and it
needs a decision independently of how the deviation is ratified — the answer could be "create
the four wallet entries" whether or not the deviation is ever approved.

**Not fixed. Not touched.** The fix touches payment credentials and a running payment
service: a stop condition in this session's brief, and README §4.1 rules 12 and 14.
Specifically not done: creating the `ao-payment` folder or its four entries; removing or
altering the `-` prefix on line 63; restarting the unit; deleting `payment.env`. All four
are the operator's.

Recommended order, in the section and here: create the four `ao-payment` entries first — it
is ST-12's own outstanding action and fixes staleness as a side effect — then decide whether
the `-` prefix stays. Rotation of `sales-db-password` is **not** required: the value was
never committed to Git, a backup set, or an external network, and the exposure is a local
`0600` file. Rotation becomes required only if the operator judges the host account
untrusted.

Cross-group: the ST-12 row needs its "runs with no DSN" text corrected and ST-12 is the
compiler's, not mine. The `ao-payment` wallet-entry provisioning is already ST-12's
outstanding action.

What I got wrong: my first draft of the §14.1.7 evidence block quoted

    sed -n 's|^PAYMENT_DSN=.*|\1|p' payment.env

which is wrong twice — there is no capture group in that pattern, so `sed` exits with
"invalid reference \1", and even if it ran it would replace the whole line with the empty
string. I had pasted the pattern from memory instead of from the shell. I caught it because
the documented `wc -c` output was 49 and I re-ran the command to check; the bad form returns
0 *and* errors, so it could not have produced a wrong-but-plausible number silently.
Corrected in the section to the form actually run, and re-run to confirm 49 / `03521083973b`.

What I got wrong, second: I initially recorded the seven `ao-*` folders as holding "39
entries". Measured, it is **37**; 39 is `ao-*` (37) plus `Passwords` (2), which is how §14.1.4
phrases it. The number I gave was wrong, but the conclusion drawn from it — that §14.1.4's 39
is still current — survived, because 37+2=39 exactly. I only caught this because the count
felt high and I re-measured instead of asserting it. Total across all 15 folders is 52,
including 11 unrelated application folders; an unqualified "entries in the wallet" count is
meaningless, and that is the trap.


  ### Supporting measurement detail

`grep -rn 'ExecStartPre=-' quadlet/` returns exactly one hit — this line. The `-`
makes systemd discard the exit status, converting a recurring hard fetch
failure into silence.

The stale file is NOT inert, and §19 ST-12's "runs with no DSN" is wrong:

    $ sed -n 's|^PAYMENT_DSN=postgresql://[^:]*:\([^@]*\)@.*|\1|p' payment.env | wc -c
    49
    $ … | tr -d '\n' | sha256sum | cut -c1-12
    03521083973b

48-char password, sha256 prefix identical to the LIVE `sales-db-password`
(§14.1.6 records `03521083973b`, len 48). The DSN is
`postgresql://sales_migration_role:&lt;password&gt;@127.0.0.1:15432/salesdb` and it is
present. ST-12's conclusion that the adapter "cannot accept a payment" rests
on a measurement that does not hold.

`check-secrets-exposure.sh` cannot see the file either:

    $ bash scripts/validation/check-secrets-exposure.sh
    OK: no secret-shaped content in tracked files      (rc=0)

Cause is the carve-out at `check-secrets-exposure.sh:79` — `PAYMENT_DSN` is not
in `$secret_key_re` because the key name is a DSN, not a "secret-shaped" name.

## Third pass, 2026-10-04 (this session)

### This proposal did not parse until this pass

**The defect, and it mattered.** When I read this file back to merge it, `yaml.safe_load` on its
frontmatter failed outright:

    YAML ERROR: while scanning an alias
      in "&lt;unicode string&gt;", line 37, column 1:
    **New item, not a closure.** SEC ...
    expected alphabetic or numeric character, but found '*'

`grep -n '^---'` returned exactly two hits — line 1 and line 119. The closing fence was
missing, so lines 37–117 (the entire prose body) were absorbed into the `evidence:` block scalar,
and a bare `**bold**` line is not valid YAML. Any merge script that parses these proposals would
have raised on this file, or silently skipped it. **The one proposal describing a live
unreported payment fault was the one that could not be read.**

Fixed: the frontmatter now closes after the evidence, and the orphaned duplicate evidence block
that had been stranded after the body (lines 94–119, a second copy of the `-`-prefix and DSN
measurements) is re-indented into prose under a "Supporting measurement detail" heading. Nothing
was deleted; the duplicated measurements were kept because they are evidence. Verified by
parsing all four `sec-*.md` files:

    sec-SEC-01.md OK action=update item=SEC-01
    sec-SEC-02.md OK action=update item=SEC-02
    sec-SEC-03.md OK action=close  item=SEC-03
    sec-SEC-04.md OK action=new    item=SEC-04

**I own this defect.** The file is a `sec-*` proposal, so it is mine; I am not reporting it as
someone else's.

### Re-verification: the fault is still live

Re-measured from scratch, not inherited:

    $ systemctl --user is-active ao-ingress-payment.service
    active
    $ systemctl --user show ao-ingress-payment.service -p ExecStartPre
    ExecStartPre={ … ignore_errors=yes ; … }

`ignore_errors=yes` is systemd's own rendering of the `-`, so the silencing is confirmed from
runtime state, not only from the quadlet source. `payment.env` mtime is still 2026-09-30
23:18:29 against an `ActiveEnterTimestamp` of 2026-10-01 15:08:41. `hasFolder` confirms
`ao-payment` and `ao-archive` absent, the other seven `ao-*` folders present.

### What I got wrong

A regex. I enumerated `legacy-alwayson-folder.env` with `^([A-Za-z0-9_]+)=` and got **zero
pairs**, when `wc -l` says the file has 4 lines and 3 of the 4 key names contain hyphens. Read
literally, "zero pairs" would have meant the file holding three live database passwords was now
empty — a false claim about a security improvement that never happened. Corrected to
`^([A-Za-z0-9_-]+)=`, which reproduces §14.1.6's table exactly. **A zero from a parser needs an
independent check before it is recorded.**

Two API traps, also recorded in §14.1.7.1: `folderList` returned 14022 rows on one call and
14274 on the next on an unchanged wallet, so it is unusable as a count — use `hasFolder`, which
is what `kwallet-provision.sh:42` uses. And `entryList` (`as`) is not `entriesList` (`a{sv}`);
calling `int()` on the former raises `TypeError`.</td>
</tr>
<tr>
<td valign="top">SEC-01</td>
<td valign="top"><strong>Unattended secret delivery decision</strong></td>
<td valign="top">ST-24</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§14.1</td>
<td valign="top">Either migrate mastodon-db, sales-db, and webodm-db to Podman secrets or systemd credentials, or record an approved deviation with compensating controls, before any production declaration.<br><br><strong>PROGRESS by 14-secrets-and-service-identity.</strong> `update`, not `close` — the item asks for one of two things and only the second is
mine to do. The acceptance criterion is "either migrate … **or** record an approved
deviation with compensating controls". I have recorded the deviation in **§14.1.6**,
but **recorded is not approved**: §14.1.6 is headed "Recorded deviation" and opens
by stating the decision is reserved to the operator.

So SEC-01 should stay **Open** until the operator ratifies or rejects, at which
point the action becomes `close` either way. What changed is that the decision is
now fully evidenced and needs only a yes or no.

§14.1.6 records:

- **Why the mandated mechanism is unused.** Podman secrets would have to be
  populated *from* the wallet by a root or podman-owned helper at start-up, which
  relocates plaintext to a second long-lived store instead of removing it, and
  `Secret=` cannot be populated from a login-gated wallet at all. systemd
  `LoadCredential=` exists on the user manager but is not consumed by
  Podman-managed containers.
- **Six compensating controls**, each with the command that proves it: `umask 077`
  at fetcher line 14; `chmod 600`; atomic `.tmp`→`mv` write so a partial file is
  never read; `mastodon.env` ACL `user:ao-sales:r-- / group::--- / other::---`;
  `.gitignore:1` = `secrets/` with env files outside the worktree;
  `check-secrets-exposure.sh` for CI.
- **Env-file lifetime, stated precisely.** The item specifically asked for this
  and the honest answer is not the flattering one: the `0600` env files are **not
  shredded on exit**. They persist between starts and are overwritten in place;
  only the `.tmp` is removed, with `rm -f`, not `shred`. Only `post.sh` and
  `sign-manifest.sh` shred. §14.1.1 calls these files "a plaintext duplicate" —
  the deviation accepts that exposure and designates the wallet as system of
  record instead. I did not want to paper over this, since it is the weakest part
  of the deviation and the operator should see it plainly.
- **The migration path, proven available** (above): `Secret=` mounted at
  `/run/secrets/…` plus `Environment=POSTGRES_PASSWORD_FILE=/run/secrets/…`
  satisfies §14.1 for the four database services. Prepared, not applied.

**Operator decision requested — one of:**

1. **Ratify the §14.1.6 deviation** as written, including the non-shreded
   delivery-copy exposure. Then SEC-01 closes with no code change.
2. **Authorise the Podman-secret migration** for `ao-mastodon-db`, `ao-sales-db`,
   `ao-webodm-db`, `ao-fabrication-db`. Requires new credential delivery while
   services are live, so it needs a maintenance window.

I recommend (2) for the four database services only, since `file_env` is proven
to work there; the remaining consumers are not all `file_env`-aware and would
need separate handling.<br><br><strong>Evidence:</strong><br><code>$ podman version --format '{{.Client.Version}}'<br>5.7.0<br>$ podman secret ls<br>ID          NAME        DRIVER      CREATED     UPDATED<br>→ zero Podman secrets exist on this host.</code></td>
</tr>
<tr>
<td valign="top">SEC-02</td>
<td valign="top"><strong>Reconcile secret-delivery policy with the implementation</strong></td>
<td valign="top">ST-24, ST-30</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§14.1, §14.1.1</td>
<td valign="top">§14.1 mandates Podman secrets or systemd credentials; every implemented path is a wallet-materialised <code>0600</code> env file, which the same subsection calls a plaintext duplicate. Either move to Podman/systemd credentials or record the deviation in this document with env-file lifetime and shred-on-exit behaviour, and close the <code>~/secrets/fabrication-db.env</code> recorded in ST-30. §14.1.1 points at a this document subsection that does not exist.<br><br><strong>PROGRESS by 14-secrets-and-service-identity.</strong> `update`. The policy/implementation reconciliation itself is done and is recorded in
**§14.1.6**; what remains is operator ratification, exactly as in SEC-01. Both items
share one decision, so they should close together.

Handled in this section file:

- **The reconciliation.** §14.1 mandates Podman secrets or systemd credentials;
  every implemented path is a wallet-materialised `0600` env file, which §14.1.1
  itself calls a plaintext duplicate. §14.1.6 records the deviation, states the
  compensating controls, and states env-file lifetime and shred-on-exit behaviour
  in full — including that env files are **not** shredded and persist between
  starts. The alternative (migrate to Podman/systemd credentials) is shown to be
  technically available for the database services and is **not applied**, because
  it changes live credential delivery.
- **The dangling §14.1.1 cross-reference.** The item notes "§14.1.1 points at a
  this document subsection that does not exist." Fixed: §14.1.1 now names **§14.1.6**
  and **§14.2** explicitly, and both now exist. That was the one pre-existing line
  I modified in §14.1.1 — everything else I added is below §14.1.5.

**`~/secrets/fabrication-db.env` (ST-30) — no such file exists.** The `find` above
returns nothing. The live file is `~/.local/share/ao-secrets/fabrication-db.env` at
`0600`, which matches §14.1.2's single-env-root rule. ST-30's text is stale and
should not be read as evidence of a second delivery path. **I did not edit ST-30** —
it is not mine — so this correction needs the §19 compiler to apply. This is
adverse-to-ST-30 rather than adverse-to-me, so I want it explicit: the honest
reading is that §14.1.2 was right and ST-30's note drifted, not that a secret is
sitting in a second location.

**Also found, not fixed: `~/secrets/mastodon.env` is a dangling symlink** to
`/ALWAYSON/secrets/mastodon/mastodon.env`, which does not exist. It is inert —
`quadlet/sales/ao-sales-db.container` and the Mastodon units all read
`EnvironmentFile=%h/.local/share/ao-secrets/…`, never `~/secrets/`. **I did not
remove it**: deletion is outside this session's authority (brief stop conditions)
and it may be another session's artifact. Reporting it for the operator.

What I got wrong: I first edited §14.1.6's heading to "Approved deviation" while
its own first line said "awaiting operator ratification" — the heading claimed an
approval that does not exist. I changed it to "Recorded deviation". A heading that
asserts operator consent is exactly the kind of thing this session must not
produce unprompted.<br><br><strong>Evidence:</strong><br><code>$ find ~/secrets -name 'fabrication*' -o -name '*fabrication-db*'<br>(no output — the file ST-30 records does not exist)</code></td>
</tr>

<tr><td colspan="6" style="background-color:#c9ccd1; border-top:2px solid #8a8f98; border-bottom:1px solid #8a8f98; padding:5px 8px; font-weight:bold; letter-spacing:0.04em;">LEDGER · Ledger, accounting and provenance — 7 items, all Open</td></tr>
<tr>
<td valign="top">LEDGER-07</td>
<td valign="top"><strong>Corda node must be built on Corda 5 against <code>cordadb</code></strong></td>
<td valign="top">ST-09</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§11.1, §17.1</td>
<td valign="top">The Corda CLI is installed but no node exists: <code>cordadb</code> holds 0 tables and its owner role has no working password, so <code>preinstall check-postgres</code> cannot pass. Build the node on Corda 5 against <code>cordadb</code> — no data migration is required — after the operator key/certificate ceremony. Until then the ledger is not production-ready<br><br><strong>PROGRESS by 11-ledger-provenance-archive-and-ipfs.</strong> **Stays open. Cannot be closed by an agent session at all.**

## Important correction to §19's evidence

§19 states `cordadb` "holds 0 tables and its owner role has no working password".
**I could not verify the 0-tables claim.** Both PostgreSQL paths are closed to
the agent account, and neither failure means the database is absent — `role
"scottw" does not exist` is an authentication outcome, not a missing database,
and `sudo: interactive authentication is required` says nothing about `cordadb`.

I have recorded in §11.7 that this claim is **carried forward from §19 and NOT
re-verified**, so the next agent does not repeat it as established fact. The
operator can confirm with:

```bash
sudo -u postgres psql -tAc "SELECT count(*) FROM pg_tables WHERE schemaname='public' AND tablename NOT LIKE 'pg_%';"
sudo -u postgres psql -tAc "\du corda"   # inspect role state; do not print the password
```

## What I did establish

- `ao-ledger-core.service` **does not exist** as a unit. No node is running.
- `ao-ledger` exists as uid 994 with home `/home/alwayson-ledger`, nologin shell.
- Corda 4/H2 was already retired 2026-09-29 under operator approval, so "remove
  the previous V4 installation and database" is **already done** — no deletion
  work remains and none was performed.

## Ordering

LEDGER-07 is blocked behind LEDGER-01 (key ceremony) and the `cordadb` role
password. Building the node requires operator-held key material, so it is a stop
condition rather than a task. Until then the ledger is **not production-ready**,
as §19 already states.

Also recorded in §11.7: the native-systemd (non-containerised) ledger core is a
**deliberate documented deviation** from the Podman-and-Quadlet-only rule, since
Corda 5 ships no official image. It widens no listener and uses no `--privileged`.
Recorded so it is not later mistaken for an oversight.<br><br><strong>Evidence:</strong><br><code>$ psql -tAc 'select 1'<br>psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed:<br>FATAL:  role "scottw" does not exist</code></td>
</tr>
<tr>
<td valign="top">LEDGER-01</td>
<td valign="top"><strong>Corda key/certificate ceremony</strong></td>
<td valign="top">ST-09, ST-10</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§11.1</td>
<td valign="top">Operator ceremony performed and output recorded. No production ledger keys generated, replaced, exported, or activated without explicit operator approval.<br><br><strong>PROGRESS by 11-ledger-provenance-archive-and-ipfs.</strong> **Stays open. Stopped deliberately — this is a hard stop condition.** The
acceptance criteria permit closure only after an operator ceremony is performed
and recorded, and explicitly forbid generating, replacing, exporting or
activating production ledger keys without explicit approval (README §4.1
rule 14). I did neither.

Added §11.7 recording the three ordered blockers: the TLS chain/keystores
(operator-held KWallet passphrases under `ao-ledger`), the `cordadb` owner role
password, and the encrypted worker config.

## Documentation bug found — wrong service account name

`docs/runbooks/ledger-bootstrap.md` says the service account is
**`alwayson-ledger`**. That account **does not exist**. The real account is
**`ao-ledger`** (uid 994). `alwayson-ledger` is the *home directory*, not a
username:

```text
$ getent passwd ao-ledger
ao-ledger:x:994:974:ALWAYS ON ledger core service:/home/alwayson-ledger:/usr/sbin/nologin
```

An agent trusting the runbook would build the node under the wrong identity, or
conclude the account is missing and create a duplicate. `/home/alwayson-ledger`
is unreadable by `scottw`, so a direct `ls` returns `Permission denied` — that
is **correct**, not a fault. Do not "fix" it by loosening the mode or running the
node as `scottw`.

The same error appears in `logs/operations/2026-09-28-corda4-retirement.md`,
which refers to uid 994 as `alwayson-ledger`. **Both files are outside my
ownership, so I have not edited them — reporting instead.** The correction is
recorded in §11.7 of my own section.

Artifacts verified present: Corda 5.2.2 worker JAR, CLI installer, notary
plugin, all with checksum sidecars, `sha256sum -c` OK.<br><br><strong>Evidence:</strong><br><code>$ cd /ALWAYSON/data/corda-install &amp;&amp; sha256sum -c corda-combined-worker-5.2.2.0.jar.sha256sum<br>corda-combined-worker-5.2.2.0.jar: OK</code></td>
</tr>
<tr>
<td valign="top">LEDGER-02</td>
<td valign="top"><strong>Corda 5 build on PostgreSQL</strong></td>
<td valign="top">ST-09, ST-10</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§11.1</td>
<td valign="top">Node built on Corda 5 against <code>cordadb</code> in PostgreSQL 18, with the previous V4 installation and database removed and no data migrated; correlation join by receipt number, serial number, and UTC timestamp proven.<br><br><strong>PROGRESS by 11-ledger-provenance-archive-and-ipfs.</strong> **Stays open. Stopped — credential change is a hard stop condition.**

The acceptance criteria require the `cordadb` owner role to have a working
password so that `corda-cli.sh preinstall check-postgres` passes. I did **not**
run `ALTER ROLE corda PASSWORD ...`, did not read the existing credential, and
did not broaden database privileges to get past the error (README §4.1 rules 13
and 14).

## What is verified

- The role password state is **unverifiable** from the agent account. `psql`
  fails at authentication (`role "scottw" does not exist`) and `sudo -u postgres`
  requires interactive authentication. Neither says anything about whether the
  `corda` role has a working password — so §19's claim is carried forward, not
  confirmed.
- The Corda 5.2.2 artifacts are staged and checksum-clean.
- The service account is `ao-ledger`, not `alwayson-ledger` (see the
  LEDGER-01 proposal for the runbook bug and the correction recorded in §11.7).

## What the operator needs to do

```bash
sudo -u postgres psql -tAc "SELECT rolname, rolcanlogin FROM pg_roles WHERE rolname='corda';"   # no password shown
sudo -u postgres psql -c "ALTER ROLE corda PASSWORD '&lt;new&gt;';"
```

The new password must then reach the `ao-ledger` account through KWallet, **not**
through this repository, a script, or a log. Per the KWallet secret-authority
session, agent sessions are **not** authorised to write ledger secrets at all.

## Ordering

This is prerequisite to LEDGER-07's node build, and both sit behind LEDGER-01's
key ceremony. Nothing here can be advanced by an agent without operator
approval.<br><br><strong>Evidence:</strong><br><code>$ psql -tAc 'select 1'<br>FATAL:  role "scottw" does not exist</code></td>
</tr>
<tr>
<td valign="top">LEDGER-03</td>
<td valign="top">Corda ingest accepts only approved signed data</td>
<td valign="top">ST-09, ST-10</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§4.4, §11.2</td>
<td valign="top">Ledger-ingest receives signed, minimized manifests only, with authorization, idempotency, replay defence, and audit.<br><br><strong>PROGRESS by 11-ledger-provenance-archive-and-ipfs.</strong> **Stays open.** Added §11.2.5 with an 8-row table mapping every requirement to
its enforcer and its current state, so the gap is explicit rather than implied.

Proven by execution (synthetic content only; test artifact deleted afterwards):
the schema conditional rejects a `sales_receipt` without an issued
`transaction_id` (exit 12), and an unsigned manifest is refused (exit 20).

## The finding that matters most

`submit-ledger-event.sh` validates only that `.signature` is a **non-empty
string**. I proved a deliberately bogus value is accepted and staged:

```text
$ jq '.signature="ed25519:SYNTHETIC_NOT_A_REAL_SIGNATURE"' m.json &gt; m3.json
$ bash scripts/ledger/submit-ledger-event.sh m3.json
PENDING: gateway not deployed; manifest staged for later submission   # EXIT=3
```

This is **not a live vulnerability today** — the manifest goes to a local staging
directory and is never transmitted, because no gateway exists to receive it. It
becomes one the moment server-side signature verification is skipped.

Consequently the gateway **must** verify signatures cryptographically and must
**not** trust `producer_key_id` or the embedded `signature` as supplied. The
`producer_key_id` and `authorization_policy_id` fields `build-manifest.sh` emits
are empty placeholders and must be filled from the authenticated mTLS identity,
never from the submitted body. Anything replayed out of
`artifacts/pending-ledger-submissions/` after the gateway comes up is untrusted
input.

Only the client half (build → sign → stage) is demonstrable. Acceptance,
authorization, idempotency and replay defence are **unproven** because there is
no acceptor to test them against.<br><br><strong>Evidence:</strong><br><code>$ bash /ALWAYSON/scripts/ledger/build-manifest.sh sales_receipt sales &lt;file&gt; testref<br>ERROR: sales_receipt requires issued transaction_id<br>EXIT=12</code></td>
</tr>
<tr>
<td valign="top">LEDGER-04</td>
<td valign="top">pCloud archive credentials</td>
<td valign="top">ST-12, ST-17</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§11.6, §17.1</td>
<td valign="top">Credentials provisioned into <code>ao-archive</code>; non-destructive encrypted replication test approved and run. <strong>Presence-only checks — never print, copy, or export values.</strong><br><br><strong>PROGRESS by 11-ledger-provenance-archive-and-ipfs.</strong> **Stays open, and is blocked earlier than §19 suggests.** §19 frames this as
"credentials provisioned into `ao-archive`". The acceptance criteria cannot be
met as written, because **`ao-egress-archive` does not exist** — no Quadlet, no
container, no network. Only the policy file
(`config/pcloud/replication-policy.yaml`) exists, and it constrains scope without
provisioning anything.

**Credentials cannot be provisioned into a service that has no unit.** Building
that adapter is separate work outside my ownership (`quadlet/` is not my file),
so I have stopped here rather than building it.

## Naming discrepancy for the operator

§11.1 and §4.4 name the component **`ao-egress-archive`**; the LEDGER-04
acceptance criteria name it **`ao-archive`**. I have recorded
**`ao-egress-archive`** as correct, since that is the name used in the
architecture, the network table, and the approved-path table.

## Secret handling

**No credential was read, printed, copied, or exported, and no replication test
was run.** Presence-only handling applies when this is unblocked: prove an entry
exists by name and non-zero length, never its value. A non-destructive
encrypted replication test is a stop condition requiring operator approval.<br><br><strong>Evidence:</strong><br><code>$ find quadlet -ipath '*archive*'<br>(no output)</code></td>
</tr>


<tr><td colspan="6" style="background-color:#c9ccd1; border-top:2px solid #8a8f98; border-bottom:1px solid #8a8f98; padding:5px 8px; font-weight:bold; letter-spacing:0.04em;">PAY · Payments, sales and storefront — 7 items, all Open</td></tr>
<tr>
<td valign="top">PAY-01</td>
<td valign="top">Payment credentials into KDE Wallet <code>ao-payment</code></td>
<td valign="top">ST-24</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§14.1</td>
<td valign="top">Folder provisioned per §14.1.1; entry stored through <code>kwallet-provision.sh</code>; no secret in Git, logs, HTML, or Corda.<br><br><strong>PROGRESS by 07-public-storefront-and-payment-policy.</strong> **PAY-01 stays OPEN. No credential was created, read, moved or modified by this
session.** I am filing this as `update` rather than `close` because the item
cannot be completed by me — the wallet entries must be created by the operator.

The finding that changes the picture: **ST-12's central premise is false.** ST-12
says `ao-ingress-payment` "runs with no DSN" because the `ao-payment` wallet
entries do not exist. The entries indeed do not exist — proven above. But a
`payment.env` exists anyway, mode 0600, containing `PAYMENT_DSN`, and the running
container has it injected. So the adapter is **not** running DSN-less; it is
running with a hand-made DSN whose password is **byte-identical to the
`sales-db` wallet password** (48 chars, identical SHA-256 prefix).

Three consequences, all recorded in §7.3.1 as OPEN:

1. `payment.env` was written by hand on 2026-09-30, **outside** the wallet bridge.
   If the operator ever creates the four `ao-payment` entries, the next
   `ExecStartPre` will overwrite this file in one composed pass and the DSN will
   change to whatever `payment-db-password` holds.
2. The DSN grants `ao-ingress-payment` the **`sales_migration_role`** — the full
   161-grant schema-admin role — where the ingress adapter needs only INSERT on
   `payment_provider_events`. That is a §14.1 least-privilege deviation, and it
   currently hands a payment-facing component schema-admin on the sales database.
3. Two secrets are now one secret. A payment credential duplicating the sales-db
   password means a single compromise of the sales-db password also yields the
   payment adapter's database access. §14.1 treats these as separate credentials.

**I did not remediate any of this.** Rotating a live password, re-scoping a role,
or rewriting a 0600 secrets file are §4.1 rule 14 and rule 12 stop conditions. The
remediation I would propose for approval is: operator creates the four
`ao-payment` entries with a **distinct** `payment-db-password`, a dedicated
`sales_api_role` is granted only the INSERT the adapter needs, and the hand-made
`payment.env` is removed once the wallet path is proven. **That needs explicit
operator approval and I stopped before it.**

What I got wrong:

1. **I got the argument order of `KWallet.hasFolder` wrong on the first attempt**
   and got `Error parsing parameter 1 of type "i"` for all three folder names —
   because the handle is parameter 1, not the folder. The `hasEntry` calls
   happened to have the right order, which is why they returned `(false,)` rather
   than an error. Had I not added a control query (`ao-sales`/`sales-db-password`
   → `(true,)`) I would have been unable to distinguish "the entry is absent" from
   "my query is malformed". **A false result from a query you have not validated
   against a known-true case is not evidence.**
2. **I initially took §7.2's and §19's framing at face value** — that the adapter
   was correctly inert because it had no DSN — and only inspected the container
   when the Quadlet's own comment predicted the opposite of the README. Trusting a
   document that describes live runtime state over measuring the runtime is the
   error here.<br><br><strong>Evidence:</strong><br><code># KDE Wallet, read-only. hasEntry over the ao-payment folder.<br>$ h=$(gdbus call --session --dest org.kde.kwalletd6 --object-path /modules/kwalletd6 \<br>      --method org.kde.KWallet.open kdewallet 0 alwayson-ops)<br>handle=841343774</code></td>
</tr>
<tr>
<td valign="top">PAY-02</td>
<td valign="top">Payment verifier and normalized event model</td>
<td valign="top">ST-11, ST-12</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§7.2, §7.3</td>
<td valign="top">A test payment event produces a verified normalized record.<br><br><strong>PROGRESS by 07-public-storefront-and-payment-policy.</strong> **PAY-02 stays OPEN. Its acceptance criterion — "A test payment event produces a
verified normalized record" — is not met, and cannot be met without a change to
how money-bearing events are accepted. I stopped rather than making it.**

The verifier is not conformant with either provider it claims to verify. Three
defects:

1. **Wrong signature scheme.** The adapter computes
   `HMAC-SHA256(secret, transmission_id | transmission_time | raw_body)`. PayPal
   documents `transmissionId | timeStamp | webhookId | crc32` — CRC-32 of the raw
   body, not the body — verified with the RSA public key from the `paypal-cert-url`
   certificate, not a shared HMAC secret. Tested directly: a signature on PayPal's
   documented message string is **rejected** by `verify_paypal`; only the adapter's
   own non-standard construction is accepted. **As written the adapter would reject
   every genuine PayPal delivery.** This fails *closed*, so it is a
   no-payments-possible defect rather than a money-loss one — but it means §7.2's
**Why I did not fix it.** Rewriting the verification path changes which
money-bearing events are trusted to create business state. That is squarely a §4.1
rule 14 stop condition and the brief's first stop condition. I prepared the
finding and stopped. If the operator approves, the fix is: implement the PayPal
documented construction (RSA public key from `paypal-cert-url`, `crc32` of the raw
body, `webhookId` from config, verify `PAYPAL-TRANSMISSION-SIG`), split
`verify_coinbase()` out of the PayPal path against `COINBASE_WEBHOOK_SECRET`, and
fix `normalize()` to read `resource.amount.value` and `charge.id`. **I have not
written that patch** — an unproven change to payment verification sitting in the
tree is worse than an open item.

What I got wrong:

1. **My verifier test was confounded, and I nearly drew the wrong conclusion from
   it.** Both attempts printed `REJECT paypal: stale transmission (51806s)`, which
   looks like the signature check failing and would have supported "confirmed: the
   adapter rejects PayPal-style signatures". In fact the **freshness check fired
   first** and neither signature was ever evaluated, so that run proved nothing
   about the scheme. The first line (`adapter-scheme sig ... False`) is `False` for
   the same reason. I stated this in §7.2 as if it were a clean demonstration and
   it was not — the honest basis for the defect is the code reading plus PayPal's
   own documentation. **Anyone acting on PAY-02 should re-run this with a fresh
   `paypal-transmission-time`**; do not trust the pasted output as a signature
   result.
2. **I built the test in `/tmp` and deleted it immediately after.** Right for
   hygiene, but it means the evidence is not reproducible as pasted. A named test
   under `scripts/validation/` would be better; I did not add one because a
   payment-verification test that encodes a wrong expectation is a liability.
   "signature-verified webhook" control does not exist yet, and `PAYPAL_WEBHOOK_ID`
   and `PAYPAL_WEBHOOK_SECRET` in the Quadlet are the wrong shape for PayPal
   anyway (PayPal needs the cert URL and the webhook ID, not a shared secret).
2. **Coinbase is verified with the PayPal verifier.** `AUTOMATED = ("paypal",
   "coinbase")` and both branches call `verify_paypal`, so the Coinbase endpoint
   accepts PayPal-shaped events and rejects real Coinbase ones.
   `COINBASE_WEBHOOK_SECRET` is provisioned into `payment.env` by the wallet
   bridge but is **never read by any code** — a dead secret that looks like a live
   control.
3. **The normalized event model silently loses the money.** For a real PayPal
   `PAYMENT.CAPTURE.COMPLETED` the amount is at `resource.amount.value`, which
   `normalize()` does not read, so `amount_cents` is `None`. Coinbase nests its
   reference at `charge.id`, also unread, giving an empty `provider_ref` and a 400.<br><br><strong>Evidence:</strong><br><code># 1. The signature scheme is not one PayPal produces.<br># PayPal's documented message string (developer.paypal.com, "Integrate webhooks",<br># Self verification method): transmissionId | timeStamp | webhookId | crc32<br># crc32 = CRC-32 of the RAW BODY in decimal; verified with the RSA public key<br># from the paypal-cert-url certificate. It is NOT an HMAC with a shared secret.<br>$ python3   # ran the adapter's verify_paypal against both constructions<br>adapter-scheme sig accepted by verify_paypal: False<br>PayPal documented message string: tid-abc|2026-10-03T12:00:00Z|WEBHOOK_ID|3222702821<br>PayPal-style sig accepted by verify_paypal: False<br>[stderr] [ao-payment] REJECT paypal: stale transmission (51806s)</code></td>
</tr>


<tr>
<td valign="top">PAY-05</td>
<td valign="top"><strong>Live HTML views for product modals</strong></td>
<td valign="top">ST-11</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§7.1.2</td>
<td valign="top">The nine operator-requested views (Instructables robot link; MeshChatX visualizer/messaging; IPFS-pCloud route orthotiff with times and telemetry; Trimble San Vicente point clouds; LocusMap; Mapbox; Mastodon live forum; Gazebo/Foxglove kitchen, storage/CNC, and vehicle; Trimble SketchUp grid) are built and reachable from the modals, <strong>each published as a static export, an approved published view, or an external service</strong> — never by exposing a loopback address. <strong>Recorded 2026-10-01; nothing is built.</strong> Three preconditions are open and need operator decisions: the Instructables robot image asset does not exist, the Mastodon and MeshChatX iframes have no publishable origin, and the three simulation views are gated on §19.1 SIM-04 and SIM-05. Publishing any live view is a new public entry requiring explicit operator approval under §4.1 rule 6.<br><br><strong>PROGRESS by 07-public-storefront-and-payment-policy.</strong> **PAY-05 stays OPEN. Nothing was built, published, or exposed.** I am filing
`update`, not `close`, because the criterion ("the nine views ... are built and
reachable from the modals") is not met and cannot be met by me — six of the nine
rows are blocked on an operator decision or on data that does not exist yet.

I added **§7.1.3** to my section file, which did not previously distinguish the
requirement table from the build state. The table in §7.1.2 lists nine views as a
*requirement*; read alone it looks like a status report. §7.1.3 now states
plainly that **none of the nine is built**, enumerates the storefront tree to
prove it, and gives the per-row blocker for all nine:

| Row | View | Blocker |
|---|---|---|
| 1 | Instructables robot link | **No technical blocker** — outbound link plus one operator-supplied image. Needs the asset and a check that the Instructables wordmark is not substituted. |
| 2 | MeshChatX visualizer | `127.0.0.1:18000/`, loopback-only. Needs a new public ingress (§4.1 rule 6). |
| 3 | IPFS-pCloud orthotiff | Data must be produced and licensed first (§8 WebODM). |
| 4 | Trimble San Vicente | Same — point clouds must be produced. |
| 5 | LocusMap | LocusMap tile terms must be confirmed. |
| 6 | Mapbox | External account/token confirmation. |
| 7 | Mastodon live forum | `mastodon.social` refuses framing; local instance is `127.0.0.1:3300/`, loopback-only. Needs a new public entry. |
| 8 | Gazebo/Foxglove | Three loopback-only origins; also gated on §19.1 SIM-04/SIM-05. |
| 9 | Trimble SketchUp grid | Licence confirmation. |

Row 1 is the only row I could build without a new authority, and I did not build
it, because it requires an **operator-supplied image asset that does not exist**
and publishing it is still a new public entry under §4.1 rule 6.

**This extends the 2026-10-01 PAY-05 note rather than contradicting it.** That
note recorded three preconditions; those three (Instructables image absent, no
publishable Mastodon/MeshChatX origin, sim views gated on SIM-04/05) all still
hold, and I re-measured rather than assuming. What I added is the reason they
hold and the status of the other six rows, which no one had recorded.

Two things I got wrong:

1. **I first looked for the storefront at `~/pCloud Drive/Public Folder` and got
   nothing.** The real path is `~/pCloudDrive/PUBLIC FOLDER` — no space, and
   `PUBLIC FOLDER` in caps. A `find` that returns no results is indistinguishable
   from "the storefront does not exist", and I nearly wrote the weaker and wrong
   claim "no storefront exists at all" into §7.1.3. **I should have resolved the
   path from the repo before searching the filesystem** — `publish-pcloud-storefront.sh`
   was the file to read, and reading it first would have avoided the false
   negative entirely.
2. **My first verification run of the sales PDF used a free-form request body
   and the parser returned `items=0 ... INCOMPLETE`.** The script did not fail
   loudly — it produced a valid JSON record and exited **4**, which is an expected
   "incomplete request" code, not a crash. Had I stopped there I would have
   written "the intake path is broken" into §7.3.1. The real constraint is a fixed
   labelled format (`SUBJECT:`/`NAME:`/`EMAIL:`/`KIT REQUESTED:`/`COMMENTS:`)
   documented in `scripts/sales/intake-request-record.py`. Re-running in that
   shape gave `exit=0` and all three PDFs. **A non-zero exit from these scripts is
   a documented outcome, not necessarily a fault — read the header before
   concluding anything.**

Not mine to fix, reported rather than touched: `publish-pcloud-storefront.sh`
still references "Section 3.4", which is part of the repo-wide dangling
`Section 18.x`-style cross-reference problem raised in `pay-PAY-07.md`. §3.4 is a
real section, so this one resolves; I did not edit the script because
`scripts/` is outside my owned file list.<br><br><strong>Evidence:</strong><br><code># The public storefront site tree, enumerated<br>$ find '/home/scottw/pCloudDrive/PUBLIC FOLDER/***CURRENT***/site' -type f<br>/home/scottw/pCloudDrive/PUBLIC FOLDER/***CURRENT***/site/index.html<br>/home/scottw/pCloudDrive/PUBLIC FOLDER/***CURRENT***/site/alwayson-single-topology.html<br>count=2</code></td>
</tr>
<tr>
<td valign="top">PAY-06</td>
<td valign="top"><strong>Customer-facing PDF email path proven</strong></td>
<td valign="top">—</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§4.3, §4.4</td>
<td valign="top">Purchase-request confirmation, receipt, and work-order status (including expected delivery) each demonstrably sent from <code>ao-sales</code> to a customer <strong>as PDF by email</strong>.<br><br><strong>PROGRESS by 07-public-storefront-and-payment-policy.</strong> **PAY-06 stays OPEN, and it is OPEN on a single missing piece: the mail path.**
The criterion is "purchase-request confirmation, receipt, and work-order status
(including expected delivery) each demonstrably sent from `ao-sales` to a
customer **as PDF by email**". Generation is proven; sending does not exist.

**Generation half — PROVEN today, above.** `scripts/sales/intake-to-pdf.sh` runs
end to end at `exit=0` and emits the intake record, the work order, and a
10-field fillable AcroForm overlay, each verified at one page. That is real and
reproducible.

**Delivery half — absent, proven three ways.** No MTA binary on the host, no SMTP
configuration file at any of the four standard paths, and a whole-repo grep for
`smtplib|sendmail|msmtp|SMTPServer|--mail-from` across `*.py`, `*.sh`,
`*.container` and `*.service` returns **nothing**. The path is also deliberately
one-way: the script's own header says "Nothing is sent anywhere, no payment is
taken, no order is created", and the emitted record carries
`sale_logged=false` / `corda_state=NOT_SUBMITTED`.

**I stopped here deliberately.** Installing an MTA or configuring an SMTP relay
means acquiring and storing relay credentials and opening mail egress. That is a
§4.1 rule 14 stop condition (production credentials) and rule 6 (egress/public
entry), and it is the operator's decision, not mine. **No mail was configured, no
credential was created, and nothing was sent.**

What I recorded in **§7.3.1** is the split: the three customer messages §7.3 owes
— purchase-request confirmation, receipt, and work-order status with expected
delivery — can be **generated** as PDFs but **cannot be delivered**. For the
operator's decision, the missing piece is precisely one of: an SMTP relay
credential plus a sending script, or an API-based transactional mail provider,
or a deliberate decision that delivery happens manually by the operator with the
PDFs as the artefact. Each carries a different cost and a different §4.1 exposure,
which is why I am not choosing.

One further finding that belongs to PAY-03, recorded but not acted on: **the
customer-facing receipt and work-order status PDFs that §7.3 owes are not the
same documents this script produces.** This script produces a *Kit Request*
intake record and work order — an information request awaiting operator review,
explicitly not an order. There is no receipt generator, because there is no order
and no Sales API (see `pay-PAY-03.md`). So even once mail exists, two of the three
PAY-06 messages still have no producer.

Two things I got wrong:

1. **My first verification run used a free-form request body and appeared to
   fail** — `items=0`, `INCOMPLETE - missing name, email`, `exit=4`. I nearly
   wrote "the intake path is broken". It is not broken: `intake-request-record.py`
   documents a fixed labelled format (`SUBJECT:` / `NAME:` / `EMAIL:` /
   `KIT REQUESTED:` / `COMMENTS:`), and `exit=4` is the *documented* incomplete
   code. In the correct format it exits 0 and produces all three PDFs. **I should
   have read the script's header before interpreting the first non-zero exit as a
   fault.**
2. **I searched for the storefront at `~/pCloud Drive/Public Folder`** while
   checking whether any deployment had published a customer-facing PDF page. The
   real path is `~/pCloudDrive/PUBLIC FOLDER` (no space, caps), so my search
   returned nothing and would have supported a false "no public artifacts exist"
   claim. Recorded in full in `pay-PAY-05.md`.

Note for whoever picks this up: the pCloud Public Folder has a **`.git`
directory** (`/home/scottw/pCloudDrive/PUBLIC FOLDER/.git`, branch `master`), so
it is an initialised git working tree that any future commit would pick up. It
has **no commits yet**, so nothing is currently tracked — but that is a
protection that rests on nobody running `git add` there, not on a policy. **A PDF
containing a customer's name, email or order detail must not be committed there**
(§4.1 rule 7 and §4.2). Whoever implements delivery should generate PDFs into a
non-committed path and hand them to the mailer, not into the Public Folder.<br><br><strong>Evidence:</strong><br><code># ---------- generation half: PROVEN, run today ----------<br>$ cd /ALWAYSON &amp;&amp; bash scripts/sales/intake-to-pdf.sh \<br>    /tmp/pay06proof/request.txt /tmp/pay06proof/out<br>OK: /tmp/pay06proof/out/request-record.json<br>request_number=REQ-2026-10-04033100<br>items=1 unresolved=1<br>READY: complete request, awaiting operator review<br>OK: /tmp/pay06proof/out/00-kit-request-intake-record.pdf<br>OK: /tmp/pay06proof/out/00-kit-request-intake-record.html<br>OK: /tmp/pay06proof/out/01-kit-request-work-order.pdf<br>OK: /tmp/pay06proof/out/01-kit-request-work-order.html<br>OK: /tmp/pay06proof/out/00-kit-request-intake-record-fillable.pdf<br>fields=10 page=792x612pt<br>OK: 1 page - /tmp/pay06proof/out/00-kit-request-intake-record-fillable.pdf<br>OK: 1 page - /tmp/pay06proof/out/00-kit-request-intake-record.pdf<br>OK: 1 page - /tmp/pay06proof/out/01-kit-request-work-order.pdf<br>exit=0</code></td>
</tr>

<tr><td colspan="6" style="background-color:#c9ccd1; border-top:2px solid #8a8f98; border-bottom:1px solid #8a8f98; padding:5px 8px; font-weight:bold; letter-spacing:0.04em;">COMM · Community, federation and local AI — 7 items, all Open</td></tr>
<tr>
<td valign="top">COMM-01</td>
<td valign="top">Mastodon configuration drift reconciliation</td>
<td valign="top">ST-13, ST-14</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§15.4</td>
<td valign="top"><code>config/mastodon/instance-policy.yaml</code>, <code>mastodon.env.example</code>, <code>version-matrix.yaml</code>, <code>secrets/mastodon/mastodon.env</code>, and <code>fetch-mastodon-env.sh</code> all reconciled to <code>mastodon.300x3.com</code>. <strong>Do this before the next Mastodon restart</strong> — the helper emits the superseded apex value unconditionally.<br><br><strong>PROGRESS by 15-sales-mastodon-openclaw-and-local-ai.</strong> Remains **Open**. The reconciliation audit is done and recorded as new §15.4.8 "Known
Configuration Drift Against `mastodon.300x3.com`", with a nine-row table (D1–D9) giving
exact file, line, current value, correct value and consequence for each.

Key finding for the table: **the service runtime is already correct** — the live instance
is genuinely `mastodon.300x3.com` and federation works. All drift is confined to
`config/mastodon/instance-policy.yaml`, `config/mastodon/mastodon.env.example`,
`scripts/operations/fetch-openclaw-mastodon-env.sh` and a stale note in
`config/platform/version-matrix.yaml`. None of those files is owned by this session, so
none was edited here; the table is written so the owning session can apply the edits
without re-deriving anything.

Highest severity is D1: `mastodon.env.example` line 7 still carries `LOCAL_DOMAIN=300x3.com`.
Most *live* is D2: `post.sh` calls the OpenClaw helper on every invocation and consumes
`MASTODON_SERVER`, so every `post.sh` run currently targets the static storefront
`https://300x3.com` rather than the Mastodon host. D3 replaces a superseded `posteo.net`
mailbox identity.

Two items found during this pass were *not* in the original COMM-01 scope and are
flagged for the owning sessions:

1. **D6** — `instance-policy.yaml` line 24 says `registrations: "open with approval gate
   (approval_required: true)"`, which the live instance contradicts (see COMM-03). Two
   files now disagree with the running service.
2. **D9** — `version-matrix.yaml` line 51 carries the *same* wrong claim I had to correct
   in my own section (§15.4.2: `RAILS_FORCE_SSL/LOCAL_HTTPS are set false`), **and** an
   independent typo: it cites the loopback proxy at port `3300` where the real origin is
   `127.0.0.1:3000`.

**What I got wrong:** my first pass grepped for `300x3.com` with a filter designed to
exclude `mastodon.300x3.com`, and I initially reported `version-matrix.yaml` as needing
no reconciliation. That was wrong — the exclusion filter was right but I stopped at the
first two files and did not read the `sales.mastodon` block. Re-reading it found D8 and D9.
Also, my first two DB queries used `settings.name` and `notifications.status_id`; this is
Mastodon **4.3** where the columns are `settings.var` and there is no `status_id` at all.
Both queries errored before any conclusion was drawn, but a reader skimming my earlier
notes would have seen "no registration setting exists" derived from a query that never ran.
Re-ran correctly: `settings.var='registrations'` is absent, and `users.approved` exists
as a column.

Nothing here needs another session's uncommitted work, and no secret value appears — only
key names and non-secret config lines.<br><br><strong>Evidence:</strong><br><code>$ grep -nE '300x3\.com' /ALWAYSON/config/mastodon/mastodon.env.example | grep -v mastodon\.300x3<br>7:LOCAL_DOMAIN=300x3.com</code></td>
</tr>



<tr>
<td valign="top">COMM-05</td>
<td valign="top"><code>300x3.com</code> email routing / MX</td>
<td valign="top">ST-13, ST-14</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§15.3</td>
<td valign="top">Delivery confirmed or formally deferred.<br><br><strong>PROGRESS by 15-sales-mastodon-openclaw-and-local-ai.</strong> Remains **Open, and I am stopping rather than choosing.** The acceptance criterion was
"delivery confirmed or formally deferred" — I can confirm delivery is **impossible** as
currently configured, but I cannot pick a resolution without operator approval, because
every option touches something on the stop list.

My section file gains a new **§15.4.7 "Inbound and Outbound Mail for the 300X3 Domain"**,
which states the measured position plainly: `300x3.com` has **no MX record**, so all mail
to the domain is silently undeliverable.

The finding is stronger than "unconfigured". With no MX, RFC 5321 §5.1 falls back to the
implicit MX — the domain's A record, which is the Cloudflare edge. I tested port 25 to
both edge addresses directly and neither answers, and there is no local MTA. So the mail
path is not merely unconfigured, it is **closed at every hop**. That affects
`admin@300x3.com` and `bot@300x3.com`, the registered addresses of both local Mastodon
accounts: **password resets and confirmation mail cannot arrive.**

Current operational impact is low, and I want to be precise about why rather than call
this harmless: registration is closed (COMM-03) and there are no pending approvals, so
nothing is presently waiting on a confirmation email. The gap becomes live the moment
anyone needs account recovery.

**Why I stopped instead of choosing.** The options are not equivalent in blast radius:

- **Point MX at a hosted relay** — changes external DNS for the domain and starts routing
  mail to a third party. External record modification plus a new data path.
- **Stand up a local MTA** — a new package (rule 3) and a **new public listener on port
  25** (rule 4), plus a firewall policy change. Explicitly prohibited without operator
  approval.
- **Formally defer** — a documentation decision that address-based recovery is
  unsupported. Zero operational risk, but it should be the operator's call, not mine,
  because it silently accepts that both accounts are unrecoverable by email.

I have prepared and proven the change as far as is safe: the measurements above are
complete and reproducible, and §15.4.7 documents the consequence so the decision can be
made without re-deriving anything. I changed no DNS, installed no package and opened no
port.

Related drift found in the same pass and raised under COMM-01 rather than fixed here:
`scripts/operations/fetch-openclaw-mastodon-env.sh` line 19 still emits
`MASTODON_BOT_EMAIL=300x3@posteo.net`, a superseded third-party mailbox identity that
points at an address on a domain this project no longer controls for mail.

**What I got wrong:** I first ran `dig +short MX 300x3.com` and saw empty output, which I
logged as "MX query returned nothing" — correct, but I nearly treated the empty result as
ambiguous. I re-ran with an explicit `answers=$(dig ... | wc -l)` counter to turn "nothing
printed" into a measured `answers=0`. An empty tool output and a zero count look identical
in a terminal and mean very different things in a report. I also would have written a
stale note earlier that port 25 to Cloudflare was "firewalled"; it did not answer at all,
which is a different observation.<br><br><strong>Evidence:</strong><br><code># The decisive measurement: there is NO MX record at all for 300x3.com<br>$ dig +noall +answer MX 300x3.com; echo "answers=$(dig +noall +answer MX 300x3.com | wc -l)"<br>answers=0</code></td>
</tr>
<tr>
<td valign="top">COMM-06</td>
<td valign="top">Bootstrap discovery for remote servers</td>
<td valign="top">ST-13, ST-14</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§15.4.4 step 9</td>
<td valign="top">From Konqueror signed in at <code>https://mastodon.300x3.com</code>, follow at least one account on <code>mastodon.social</code>. Remote servers do not index this instance until first contact occurs. <code>https://300x3.com</code> is a static storefront and is not routed to Mastodon.<br><br><strong>PROGRESS by 15-sales-mastodon-openclaw-and-local-ai.</strong> Remains **Open**, but for one narrow reason: the *technical* precondition named in the item
is satisfied, and only the **human** step is outstanding.

The item's acceptance text is "from Konqueror signed in at `https://mastodon.300x3.com`,
follow at least one account on `mastodon.social`. Remote servers do not index this instance
until first contact occurs." The second sentence — the actual constraint — is satisfied and
measured: 10 distinct remote domains are known locally, and `mastodon.social` resolves both
of our accounts and holds our actor. **The instance is not unindexed.** Discovery contact
has demonstrably happened.

What is not done is the **browser step performed by the operator at the desktop**: signing
in via Konqueror and following from the UI. I did not perform it and did not simulate it.
Two reasons, and the second matters more than the first:

1. It needs the operator's session and credentials at a graphical desktop.
2. More importantly, faking it would corrupt the evidence. An item that says "the operator
   confirmed this in Konqueror" cannot be closed by a headless session asserting the
   account exists. I would rather leave a precise Open item than manufacture a false
   verification.

What I *did* verify from the remote side is stronger than a local table check, so the
remaining work is genuinely small: the relationship already exists bidirectionally (see the
COMM-02 proposal), which is the end state the UI step would produce.

My section file records this status under §15.4.4 step 9, including the health of the
tunnel (all 4 connections registered, `protocol=http2`, no inbound fault) so nobody
re-investigates reachability.

**A trap worth recording, because it looks like a failure and is not.**
`https://mastodon.social/.well-known/webfinger?resource=acct:bot@mastodon.300x3.com`
returns **404**. Read naively that says "the remote server cannot find us" — the exact
failure this item exists to prevent. It is normal: mastodon.social does not perform
WebFinger lookups for accounts it holds no local record of, and it already holds our
actors (confirmed by the `lookup?acct=` calls returning real IDs). Treating that 404 as a
discovery fault would trigger pointless re-work on a healthy federation path.

I also noted the tunnel dropped and re-established all four connections at
2026-10-04T02:18:47Z (`Lost connection with the edge`, then four `Registered tunnel
connection` lines 10 s later). That is normal cloudflared reconnect behaviour under
`Restart=always`, not an incident — all four re-registered and the public endpoints
answered 200 throughout. Recorded so the next session reading the journal does not chase
it.

**What I got wrong:** my very first reachability probe hit
`https://mastodon.300x3.com/users/bot` and got **502**, which I initially logged as
possible federation breakage. It was transient — five consecutive retries all returned
200. I also could not reach the loopback origin directly
(`https://127.0.0.1:3000/users/bot` returned `000`), which looked like a dead origin but is
expected: origin traffic arrives over the tunnel with the tunnel setting Host, and a
direct loopback TLS probe without that arrangement is not a valid test. I dropped that
probe rather than report it as a fault.<br><br><strong>Evidence:</strong><br><code># First contact HAS occurred - 10 remote domains are now known locally:<br>$ podman exec mastodon-db psql -U mastodon -d mastodon -At -c \<br>  "select string_agg(distinct domain,', ') from accounts where domain is not null;"<br>cupoftea.social, fedibook.de, friendicadev.sekretaerbaer.de, mastodonapp.uk,<br>mastodon.online, mastodon.social, rivals.space, sekretaerbaer.de,<br>universeodon.com, veganism.social</code><br><br><strong>STILL OPEN by 15-sales-mastodon-openclaw-and-local-ai.</strong> **Retraction of the tunnel-health claim in the applied `comm-COMM-06.md` proposal.** That
proposal recorded the federation path as "all 4 connections registered, `protocol=http2`,
no inbound fault" and explicitly told the next session not to chase the reconnect lines in
the journal. Both parts were wrong. The four connections were re-registering continuously,
and the public edge was returning 502 to remote servers in the meantime. The
"no inbound fault" sentence is the specific error and should not be relied on.

Discovery is not in question and is re-verified above: `mastodon.social` resolves
`bot@mastodon.300x3.com` to id `117327405745705562` with 2 followers. From this item's
original scope only the **human Konqueror step** remains.

What was missed is a separate, ongoing availability fault — the cloudflared edge flap,
now tracked as its own item **COMM-08** rather than folded into COMM-06, because COMM-06 is
a one-time discovery step while COMM-08 is a live fault that will recur until diagnosed.
The short version: `NRestarts=1` since 2026-10-01 makes the unit look healthy to any
`systemctl` check while the edge drops all four connections together and re-registers them
~10 s later, 26 times in the last hour, producing 502 on `/users/bot` and every other public
path. The origin is clean (zero 5xx in `mastodon-web`, empty `queue:push_public` and
`queue:pull`), so this is the Cloudflare edge-to-tunnel hop, not Mastodon.

**Measurement trap that will mislead the next session here specifically.** Probe this host
with `curl -4`. It publishes AAAA records but this machine has no global IPv6 address
(`ip -6 -o addr show scope global | wc -l` → `0`), so a default `curl` tries the AAAA leg,
fails, and falls back to IPv4 — usually succeeding, but nondeterministically, and the dead
v6 leg can surface as `000` or a 502. Judging reachability with a default `curl` risks
concluding "the tunnel is dropping requests" from a fault that is in the probe.

Diagnosing the flap, and changing tunnel transport, protocol or edge routing, is live
network configuration and therefore a stop condition — prepared and evidenced, not
actioned. Full detail in new §15.4.10.<br><br><strong>Evidence:</strong><br><code># The health claim in the earlier comm-COMM-06.md proposal is RETRACTED.<br># It said "all 4 connections registered ... no inbound fault", taken from:<br>$ journalctl --user -u cloudflared-alwayson.service -n 40 | grep -c 'Registered tunnel connection'<br>4<br># That was a single reading between flaps. The real rate:<br>$ journalctl --user -u cloudflared-alwayson.service --since '60 min ago' \<br>    | grep -c 'Lost connection with the edge'<br>26<br>$ systemctl --user show cloudflared-alwayson.service -p NRestarts<br>NRestarts=1<br># and the edge was genuinely returning 502 during the burst:<br>$ for i in 1 2 3 4 5; do curl -s -o /dev/null -m 15 -w '%{http_code} ' \<br>    -H 'Accept: application/activity+json' https://mastodon.300x3.com/users/bot; done<br>502 502 502 502 502<br># discovery claim itself is unaffected and re-verified:<br>$ curl -4 -s -m 20 'https://mastodon.social/api/v1/accounts/lookup?acct=bot@mastodon.300x3.com' \<br>    | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['id'],d['followers_count'])"<br>117327405745705562 2</code></td>
</tr>
<tr>
<td valign="top">COMM-07</td>
<td valign="top">Public-post delivery, round trips, and directory submission</td>
<td valign="top">ST-13, ST-14</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§15.4.4 step 10</td>
<td valign="top">Public-post delivery to <code>mastodon.social</code> and reply/boost round-trips back to the local instance are validated; then <code>300x3.com</code> is submitted to the joinmastodon.org directory. Directory submission is an external publication and requires explicit operator approval.<br><br><strong>PROGRESS by 15-sales-mastodon-openclaw-and-local-ai.</strong> Remains **Open. I stopped at the operator-approval gate and performed no publication.**
The item's own text states directory submission "is an external publication and requires
explicit operator approval". I do not have that approval, so neither half was executed.

**Half 1 — public-post delivery and round trips.** Not re-run. The existing evidence
(status text in §19.1, and §15.4.4 step 10) is from 2026-10-01 and is not mine to discard,
but re-validating delivery requires posting a **new** public status to `mastodon.social`,
which is an external publication. I did not post. What I did instead is establish that
nothing is currently stuck, so if the operator approves, the test starts from a clean
state: both sidekiq queues are empty (`push_public` and `pull` both `0`,
`KEYS 'queue:*'` returns an empty array), the tunnel has all 4 connections registered, and
`/api/v1/instance`, `/api/v2/instance` and `/` all answer 200.

Worth flagging for whoever runs it: **§15.4.9 documents that the follow relationship is
not reciprocal** (our remote mirror lists only `bot` among its followers). A round-trip
test that assumes reciprocal follows will appear to fail for reasons that are not faults.
Test with `bot`, which has the established relationship.

**Half 2 — joinmastodon.org directory submission.** Not attempted. I confirmed only that
the site is reachable (`https://joinmastodon.org/` → 200). I did **not** fill in or submit
any form, and transmitted nothing. Note for the operator: `joinmastodon.org/instances`
returns 404 — the public instance listing is not exposed at that path — so the submission
route needs to be established at the site itself.

One substantive observation, offered as a question rather than a recommendation, because
it is a content question I should not answer alone: the directory submission is for
`300x3.com`, but `300x3.com` is the **static storefront and is not routed to Mastodon**
(confirmed in `~/.cloudflared/config.yml` ingress — only `chat.300x3.com` and
`mastodon.300x3.com` are routed, with a `404` catch-all). The federation instance is
`mastodon.300x3.com`. Submitting the apex may be what was intended for the *brand*, or it
may be a leftover of the pre-migration apex deployment. Since a directory listing is
permanent and externally visible, **this should be confirmed before submission rather
than after.**

**What I got wrong:** I set out to close this item by running a delivery test and found
myself about to make a public post to prove a pipeline works — which is exactly the kind
of irreversible external action the approval rule exists to prevent. "It is only a test
post" is how public publication starts. I also have a mild temptation to treat the
joinmastodon.org reachability check as partial progress; it is reconnaissance, not
delivery, and the proposal says so rather than letting the 200 stand in for progress.<br><br><strong>Evidence:</strong><br><code># NOTHING WAS PUBLISHED. This proposal records a stop, not a delivery.<br># --- Half 1: public-post delivery + round trip. Requires a NEW public post. ---<br># Existing evidence is from 2026-10-01 and is NOT re-run here; re-validating it<br># means posting publicly, which needs approval.<br># Delivery pipeline is idle and healthy, so any failure would be new, not inherited:<br>$ podman exec mastodon-redis redis-cli LLEN 'queue:push_public'<br>0<br>$ podman exec mastodon-redis redis-cli LLEN 'queue:pull'<br>0<br>$ podman exec mastodon-redis redis-cli --no-raw KEYS 'queue:*'<br>(empty array)<br># Actor fetch is healthy (502 seen once, then 200 on 5/5 retries):<br>try1 actor = 200 ... try5 actor = 200<br>api/v1/instance = 200 ; api/v2/instance = 200 ; root page = 200</code></td>
</tr>
<tr><td colspan="6" style="background-color:#c9ccd1; border-top:2px solid #8a8f98; border-bottom:1px solid #8a8f98; padding:5px 8px; font-weight:bold; letter-spacing:0.04em;">FIELD · Field, radio and drones — 14 items, all Open</td></tr>
<tr>
<td valign="top">FIELD-15</td>
<td valign="top"></td>
<td valign="top"></td>
<td valign="top"><strong>Open</strong></td>
<td valign="top"></td>
<td valign="top">New item, next free number in the FIELD group (FIELD-01..FIELD-14 are all taken; no renumbering).

**Title: mapping database does not reside on the validated photogrammetry drive.**

§8.4.1 closes FIELD-11 on the *name and location* question and explicitly declines to close the
drive-residency half, promising to "carry it forward as a new FIELD item rather than reopening
FIELD-11". That promise had no corresponding item in §19 — it was recorded only as prose in
§8.4.1, where nothing tracks it. This proposal is that item.

**Why it needs its own ID rather than living inside FIELD-10.** FIELD-10 is about the *directory
tree* and ownership of the drive. This is about *where a database's data directory sits*. They
are adjacent but distinct, and the fix for one does not fix the other: FIELD-10 is repaired by
`usermod -aG alwayson-mapping scottw` plus `mkdir`, and this item would still be open
afterwards, because the PostgreSQL data directory stays on the root filesystem regardless.

**The ordering constraint is new and worth the operator knowing.** §8.5.2 measured today shows
the drive is group-owned by `alwayson-mapping` and the operator is not in that group, so `mkdir`
fails even on paths §8.2 already requires. **Any decision to relocate PostgreSQL storage onto
this drive must fix that ownership first**, or the database lands on a volume that its own
operator cannot create, back up or inspect. The relocation is therefore not a single decision
but two, in this order: group membership, then data-directory move.

**Not attempted.** Moving a live PostgreSQL data directory changes service configuration and is
an operator decision under §4.1 rule 12. Nothing was created, moved or chgrp'd on the drive or
in `~/webodm/dbdata`.</td>
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
<td valign="top">Tree, ownership, sentinel, and checks validated; WebODM starts only with required validated storage.<br><br><strong>PROGRESS by 08-mapping-and-photogrammetry.</strong> **FIELD-10 stays OPEN, action `update`.** The validation has now been *run and it fails*, which
is further progress than the previous "unvalidated" state — but the item cannot close.

§8.5.1 now records the executed validation with the per-directory result. The decisive finding
for the compiler:

**The shipped validator passes on a drive that does not satisfy its own specification.**
`scripts/validation/check-photogrammetry-mount.sh` exits 0 (UUID match, mount marker, 434G
free) while **11 of the 32 required paths in §8.2 are missing**. The script never inspects the
directory tree at all, even though §8.5 lists "Required directories are missing" as a refusal
condition. Consequence for the README: **a green validator run is not evidence that §8.2
holds and must not be cited as such.** If any other session has quoted that green run as
storage validation, that citation is now known to be unsupported.

Of the four acceptance criteria: *tree* fails (11 missing); *sentinel* passes; *checks* pass
mechanically but do not cover the tree; *ownership* is confirmed at depth 1 (`ao-mapping` /
`alwayson-mapping`, mode `drwxrws---`, setgid set) but **unverified at depths 2-4**; and
"WebODM starts only with validated storage" is **unprovable here**, because the validator
cannot fail on a missing directory, so there is no enforced gate.

**I did not create the missing directories.** That would be a live storage change on the
photogrammetry drive — a stop condition, and the operator's call, not a documentation fix.
`backups/mapping-db` is the consequential one: it is where the §8.4.1 database dumps would land
on-drive. This does not put the database outside backup scope (`dump-all-postgres.sh:18` already
dumps `webodm_dev`), but there is currently no on-drive copy.

**What I got wrong, and the reason — read this one.** My first pass ran
`find "$M" -maxdepth 4 -type d -perm -0002`, saw empty output, and wrote "no directory is
world-writable". That was unsound: `find` *also* printed `Permission denied` for 8 of the 10
subtrees and exited 1. The empty result meant "none of the two readable subtrees", not "none on
the drive". **Reason: I read an empty result as a negative finding without reading the exit
status or the stderr.** I had to correct §8.5.1. The correction is in place in the section and
the ownership claim is now scoped honestly by depth.<br><br><strong>Evidence:</strong><br><code># the shipped validator passes<br>$ bash scripts/validation/check-photogrammetry-mount.sh<br>OK: photogrammetry mount valid: systemd-1<br>/dev/sdb1; 434G free<br>rc=0</code></td>
</tr>



<tr>
<td valign="top">FIELD-14</td>
<td valign="top"><strong>The two radio profiles are identical</strong></td>
<td valign="top">ST-04</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§9.4</td>
<td valign="top"><code>config/field/heltec-v3/radio-profile-us915.yaml</code> and <code>config/drone/waveshare-lora/radio-profile-us915.yaml</code> are byte-identical: same sync word <code>0x12</code>, same encryption key ID, same device identity placeholder, and neither declares a frequency. The two radios therefore cannot be told apart on air, which contradicts §9.2.1 and the 915/917 MHz split in §9.1. The profiles also disagree with <code>version-matrix.yaml</code>: profiles say 125 kHz and spreading factor 10, the matrix and §9.2.1 say 250 kHz and spreading factor 7 for <code>DRONE-RADIO</code>. Give each profile its own frequency, sync word, key ID and device identity, reconcile the bandwidth and spreading factor against the matrix, and confirm on air that <code>DRONE-RADIO</code> carries missions only<br><br><strong>PROGRESS by 09-field-and-lora-architecture.</strong> **FIELD-14 stays OPEN, action `update`.** §9.4.1 now records the measured profile state. The
profiles genuinely are substantively identical, so the item's core concern is confirmed — but
**its stated evidence is wrong, and correcting that changes what the fix actually is.**

**Correction to the item's premise.** FIELD-14 says the profiles "also disagree with
`version-matrix.yaml`: profiles say 125 kHz and spreading factor 10, the matrix and §9.2.1 say
250 kHz and spreading factor 7". The matrix is **not a third opinion — it is silent.** It has
zero radio/LoRa/field keys and its only top-level keys are `host, gpu, mapping, simulation,
sales, operations, ledger`. Anyone fixing this by reconciling against the matrix would be
reconciling against a file that says nothing about radios. **The real third opinion is the live
`~/.reticulum/config`**, which is the authoritative record of what is actually on the air.

| Setting | `PEOPLE-RADIO` (live) | `DRONE-RADIO` (live) | Both profiles claim |
|---|---|---|---|
| `frequency` | `915000000` | `917000000` | **not declared** |
| `bandwidth` | `125000` | `250000` | `125` |
| `spreadingfactor` | `7` | `7` | `10` |
| `codingrate` | `5` | `5` | `"4/5"` |
| `txpower` | `17` | `17` | `20` |

The 915/917 MHz split described in §9.1 and §9.2.2 is **real and enforced by the live config**
— it simply is not captured in the version-controlled profiles §9.4 nominates as the
specification. So the profiles match **neither** radio: they overstate transmit power (20 vs
live 17 dBm), understate spreading factor (SF10 vs live SF7), and omit the frequency entirely.

**Consequence for §9.4:** its acceptance conditions *"different frequency"* and *"device
identity is unique"* are unmet as written, and since the profiles declare no frequency at all,
**no profile can currently be accepted under §9.4's own rules.** That is a stronger statement
than the item made and it is now recorded.

**Severity: documentation mismatch, not a regulatory fault.** §9.4.1 computes the airtime
consequence for the profile's `max_packet_bytes: 222` at `airtime_limit_pct: 10` from the SX1262
airtime formula: profiles as written 0.1156 s (311,423 packets/hour), live `PEOPLE-RADIO`
0.0875 s (411,418/hour), live `DRONE-RADIO` 0.0438 s (822,836/hour). **The live radios are far
inside the airtime limit; the profile values are merely conservative by ~1.3x to ~2.6x.**
Nothing on air is at risk of a duty-cycle breach, so this is not urgent.

**What I got wrong — two corrections, both now in the section.**

1. **The item's premise was false and I checked it instead of repeating it.** FIELD-14 blames
   `version-matrix.yaml` for the bandwidth/SF disagreement. That file contains **no radio, LoRa
   or field key at all**. Had I trusted the item and "reconciled against the matrix", I would
   have reconciled against silence and reported a phantom conflict. The real conflict is
   profile-vs-live-config.
2. **My first airtime table was wrong and I could not reproduce it.** It read 0.240 s / 1,502
   packets/hour. When I recomputed it properly I found the estimate was off by ~2x, and my first
   re-implementation was wrong *again* because it hardcoded the 125 kHz symbol time — which made
   the 250 kHz `DRONE-RADIO` row come out identical to the 125 kHz row, an obvious internal
   contradiction I should have caught from the output alone. **Reason: I published a computed
   number whose formula I had not written down, so I could not audit it.** The numbers above now
   come with the script inline. The conclusion (not urgent) survived; the figures did not, and
   an airtime number is exactly what gets quoted into a regulatory argument later.

**I did not edit the profiles.** Writing real frequencies, sync words, key IDs and device
identities into version-controlled radio configuration, and confirming on air that
`DRONE-RADIO` carries missions only, is live radio configuration and a stop condition. The last
half of the acceptance criteria — "confirm on air" — additionally requires a flight test, which
is explicitly outside this session.

**Ready for the operator, if they approve:** the four corrected values per profile are
tabulated in §9.4.1, so the edit is prepared but unapplied.<br><br><strong>Evidence:</strong><br><code>$ diff -u config/field/heltec-v3/radio-profile-us915.yaml \<br>          config/drone/waveshare-lora/radio-profile-us915.yaml<br>@@ -1,4 +1,4 @@<br>-# Heltec WiFi LoRa 32 V3 - desktop gateway profile<br>+# Waveshare SX1262 LoRa HAT - drone-side profile (must interop with heltec-v3 profile)<br> radio_profile:<br>   region: US915<br>   frequency_plan: "US915 hybrid-channel raw LoRa (NOT LoRaWAN)"<br>diff-rc=1        # only the first-line comment differs</code></td>
</tr>
<tr><td colspan="6" style="background-color:#c9ccd1; border-top:2px solid #8a8f98; border-bottom:1px solid #8a8f98; padding:5px 8px; font-weight:bold; letter-spacing:0.04em;">SIM · Simulation and fabrication — 14 items, all Open</td></tr>
<tr>
<td valign="top">SIM-01</td>
<td valign="top">Gazebo GUI clients and DDS policy</td>
<td valign="top">ST-07, ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.1, §10.2</td>
<td valign="top">Vehicle and fabrication GUI clients deployed; separate DDS/interface policy decided.<br><br><strong>STILL OPEN by 10-simulation-architecture.</strong> SIM-01 stays open on both limbs, and neither is close to done.

The **DDS policy** limb has no artifact. I grepped both Quadlet directories for
`CYCLONEDDS`, `RMW_IMPLEMENTATION`, `FASTRTPS` and `dds` and got nothing. There is no
documented middleware choice and no `Environment=` line enforcing one, so each container
falls back to its own compiled-in default. That is not necessarily broken today — the
fabrication pair works because `GZ_PARTITION` and `GZ_IP` isolate them and they share a
network — but "it happens to work" is not a decided policy, and it will not survive
adding the vehicle side.

The **GUI clients** limb is half done. `ao-sim-fabrication-gz` and
`ao-sim-fabrication-foxglove` are both up and have been for 15 and 38 hours. The vehicle
side has **no GUI client container at all** — `quadlet/sim-vehicle/` holds exactly one file,
`ao-ardupilot-sitl.container`, which is the SITL process, not a viewer. So there is nothing
to decide the policy for until that is built.

I did not build the vehicle GUI client: it is new Quadlet work on a network I have not been
asked to extend, and SIM-08/SIM-04 gate what should be exposed. I did not modify any
network, no `Environment=` line, and no running container.

**What I got wrong.** I first ran the GUI-client grep expecting to find a vehicle viewer,
because §19 phrases SIM-01 as "clients deployed" and I had assumed the vehicle side was
merely unverified like the fabrication side had been. Listing the Quadlet directory is what
showed the file does not exist at all. Absent is a different finding from inactive, and I
nearly filed them as the same thing.<br><br><strong>Evidence:</strong><br><code>Measured 2026-10-04. The fabrication GUI client exists and runs; the vehicle one<br>does not, and the DDS/interface policy is unwritten in both places it would live.</code></td>
</tr>
<tr>
<td valign="top">SIM-02</td>
<td valign="top"><code>/ALWAYSON</code> Gazebo subfolder</td>
<td valign="top">ST-07, ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2</td>
<td valign="top">Path confirmed by the operator. Currently recorded as an open decision, not a guess.<br><br><strong>STILL OPEN by 10-simulation-architecture.</strong> SIM-02 stays open, and it stays open for the right reason: this is an **operator decision**,
not a defect. §19 says "path confirmed by the operator", and an operator confirmation is the
one thing I cannot manufacture or infer from the filesystem.

What I can report is that the path is already load-bearing. `/ALWAYSON/GAZEBO` exists and
holds the four SketchUp meshes, the container build inputs under `containers/`, the portal,
the simulation data under `sim/`, and `worlds/factory.world`. It is already referenced by
live configuration in `loopback-services.yaml` and `version-matrix.yaml`, so the portal
service resolves it today. That is evidence the layout is in use and working — it is not
evidence the operator approved it, and I am not going to record the second as though it were
the first.

I made no change. Moving the folder is out of scope and would break the live portal, which
serves a path already wired into three config files.

**What I got wrong.** I started this item intending to confirm the path myself, on the
reasoning that the directory existing with the right contents settles the question. That is
exactly backwards: the item asks whether a person agreed to it, and the filesystem is
silent on agreement. Checking that the layout is sane was useful — it is reported above —
but it answers a different question, and I nearly let it stand in for the answer.<br><br><strong>Evidence:</strong><br><code>Measured 2026-10-04. The subfolder exists and is populated; §19 asks the operator to<br>confirm the path, and I cannot supply that confirmation.</code></td>
</tr>
<tr>
<td valign="top">SIM-03</td>
<td valign="top">QGroundControl interactive workflow</td>
<td valign="top">ST-21</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.1</td>
<td valign="top">Interactive SITL workflow validated end to end.<br><br><strong>STILL OPEN by 10-simulation-architecture.</strong> SIM-03 stays open. There is no QGroundControl workflow to validate, because neither end of it
exists in a running state.

QGroundControl is not installed — not on the host, not as a container. The SITL unit it
would attach to, `ao-ardupilot-sitl.service`, is present but both **masked and inactive**.
That is a deliberate state, not a fault: an outward-facing radio-ish control link that
nobody has asked to expose stays masked, and I am not unmasking it to see what happens.

I did not install QGroundControl. It is a large GUI application with its own network
behaviour and a MAVLink link to a SITL instance; installing it unattended is a
configuration change to a masked unit's counterpart that §4.1 rule 12 covers, and SIM-03's
own acceptance criteria are about *validating* a workflow rather than provisioning one. The
validation has to be human-in-the-loop anyway — it ends with someone flying the vehicle.

**What I got wrong.** I checked `which` and `/opt` and concluded "not installed", then began
drafting as if a Quadlet might already be staged for it under a name I had not guessed. I
should have listed the Quadlet directory and grepped the container set in one pass, as I did
for SIM-01, instead of assuming a hidden unit existed. The two items share the same lesson:
a name I did not try is not an absence, and `podman ps -a` plus `ls quadlet/` settles it.<br><br><strong>Evidence:</strong><br><code>Measured 2026-10-04. QGroundControl is not on this host in any form, and the SITL<br>stack it would attach to is not started.</code></td>
</tr>
<tr>
<td valign="top">SIM-04</td>
<td valign="top">Vehicle 3D world, boning, RL objects, HTML portal</td>
<td valign="top">ST-07</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">ES.1, §10.1.2</td>
<td valign="top">World setup scripted and repeatable; boning frame and tolerances measurable and exported; RL objects addressable and resettable; the world fully settable and operable from the browser-served HTML portal.<br><br><strong>STILL OPEN by 10-simulation-architecture.</strong> SIM-04 stays open, and unlike most of my group it is not partially done — **the vehicle 3D
world does not exist**. `GAZEBO/worlds/` contains exactly one file, `factory.world`, which is
the fabrication world. There is no vehicle world, so all four acceptance limbs are unmet
rather than partly met: there is nothing to script, no vehicle boning data to export, no
vehicle RL objects, and the portal serves the fabrication world only.

Worth recording because it is the opposite of what the item's wording suggests: the
*scaffolding* for the vehicle side is well advanced. `GAZEBO/` holds
`09-SIMULATIONVEHICLES-ARMS.dae`, and `scripts/simulation/` contains both
`run-vehicle-scenario.sh` and `export-vehicle-manifest.sh`. So this is a missing
assembly rather than a project that never started, and that is a real distinction for whoever
picks it up.

I did not build a vehicle world. That is new Gazebo content, it needs the real vehicle
geometry and a boned frame agreed against the actual airframe, and fabricating a plausible
world file here would produce exactly the kind of invented geometry this session is supposed
to be eliminating.

**What I got wrong.** I opened SIM-04 planning to check whether the *boning* was right,
carrying SIM-09's framing across from the fabrication side. On the vehicle side there is no
boning to check — no world, no `boning.yaml`, no datum. I was auditing the correctness of
something that had not been built, which is the §10.3 lesson again: establish that the
artifact exists before measuring it.<br><br><strong>Evidence:</strong><br><code>Measured 2026-10-04. The vehicle 3D world does not exist. There is one world in the<br>repository and it is the fabrication one.</code></td>
</tr>
<tr>
<td valign="top">SIM-05</td>
<td valign="top">Fabrication 3D world, boning, RL objects, HTML portal</td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">ES.1, §10.2.1</td>
<td valign="top">As SIM-04, for <code>ao-sim-fabrication</code>, with cell and machine datum frames and boning checked against the real machine envelopes.<br><br><strong>STILL OPEN by 10-simulation-architecture.</strong> SIM-05 stays open. It is the most nearly-complete item in my group, and the reason it
cannot close is not effort — it is that **the fourth acceptance limb asks for something the
portal is architected to refuse.**

The criteria require the world to be "fully settable and operable from the browser-served
HTML portal". The portal is deliberately view-only: `do_POST` returns 405 for every write
verb and `/api/health` advertises `view_only: true, controls: null`. Those are good
properties for a service that reports on a facility, and I am not proposing to weaken them
to satisfy a line of an acceptance table. Making the portal able to set and operate the
world is a change to the safety posture of a browser-reachable service, and it needs the
operator to say yes explicitly. That is a decision, not a ticket.

The other three limbs are genuinely advanced. The world exists and renders (SIM-06, verified
today). Boning is measurable and served at `/api/boning` with real datum frames, and the
safety-zone check passes on all four zones with honest GAPs for the two machines whose datum
origin is operator-declared rather than measured. RL objects are addressable as nine live
links. What is missing is export — `find artifacts -iname '*boning*'` returns nothing, so
boning is servable but not exported — and the runner script, which is a stub exiting 3.

One correction from this session: `/api/objects` was serving `"resettable": true` copied
from the YAML, which read as a verified capability when the portal exposes no reset endpoint
at all. It now sits beside `reset_available: false` and a note naming the discrepancy. That
makes the portal honest; it does not deliver reset, so this limb stays open on both counts.

**What I got wrong.** I opened by reading limb 4 as "the portal needs a few control routes
added" and started costing that out. Reading the handler changed my mind entirely: the
refusal is a documented design decision with a comment explaining why, not an oversight. I
was about to recommend removing a safety property of a browser-reachable service because an
acceptance table mentioned the word "operable". Matching the requirement's wording against
its actual intent is a step I skipped.<br><br><strong>Evidence:</strong><br><code>Measured 2026-10-04. Three of four limbs are delivered; the fourth is not merely<br>missing but contradicted by the portal's own design, which makes this a decision<br>for the operator rather than work for me.</code></td>
</tr>
<tr>
<td valign="top">SIM-06</td>
<td valign="top"><strong>Rebuild and verify the Gazebo GUI client</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2.1</td>
<td valign="top">Rebuild the image with <code>qt6-svg-plugins</code> and <code>GZ_RENDERING_RESOURCE_PATH=/usr/share/gz/gz-rendering</code>, then start it and confirm it renders factory geometry with no OGRE or null-string errors and a stable <code>NRestarts</code>. Until then "rendering works" is not established. The unit stays masked so it cannot seize keyboard and pointer focus<br><br><strong>STILL OPEN by 10-simulation-architecture.</strong> SIM-06 stays open. I am not able to close it in this session and I want to be
precise about which half is why.

The image half is done and verified. `localhost/gz-sim10-resolute:gui-svgfix`
carries `qt6-svg-plugins 6.10.2-2` and `/usr/share/gz/gz-rendering` holds `media/`,
`ogre/` and `ogre2/`. Those are exactly the two conditions §19 names as the cause
of the abort -- the missing SVG plugin and the missing media root -- so the image
that will be used is no longer the one that failed.

The runnability half is not done, and this is the part that matters. The unit is
`UnitFileState=generated` with no `[Install]` section, so it cannot autostart, and
it reports `ActiveState=inactive`, `NRestarts=0`. That last figure is the trap: a
restart count of zero on a unit that has never been started is not a pass. If I
had reported SIM-06 as verified on the strength of `NRestarts=0` I would have
reported success for something I never ran.

I did not start the GUI. It renders into a window on the operator's live desktop,
which under the placement rule has to be anchored bottom-left of DP-3 via the
`ao-gazebo-monitor` KWin script and must not raise itself or steal focus. Launching
it unattended is a visible action on someone's screen, and the `ao-gazebo-monitor`
script is installed and present but I have not confirmed it catches this unit in
this session.

To close SIM-06 someone needs to start the unit with the operator present and
confirm the window lands bottom-left of DP-3 with no focus steal. That is a
human-in-the-loop check, not something I should claim from a container image
listing.

**What I got wrong.** `systemctl is-enabled` returned `generated` and I read it
as a failure; I should have asked what `generated` means for a Quadlet unit before
concluding anything from it. The actual blocker turned out to be the missing
`[Install]` section, which `is-enabled` does not tell you.<br><br><strong>Evidence:</strong><br><code>Half the item is satisfied and half is untested. Measured 2026-10-03.</code></td>
</tr>
<tr>
<td valign="top">SIM-07</td>
<td valign="top"><strong>Working ROS 2 package source</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2.1</td>
<td valign="top"><code>packages.ros.org</code> fails TLS verification from this host because its certificate is issued for <code>*.osuosl.org</code>. Certificate verification must not be disabled to work around it. The installed ROS 2 Lyrical stack and <code>ros_gz</code> bridge are unaffected; installing or updating packages is not. Use a reachable mirror or the pinned base-image digest<br><br><strong>STILL OPEN by 10-simulation-architecture.</strong> SIM-07 stays open, blocked on a host trust failure I should not work around.

The evidence is unambiguous. `openssl s_client` against `packages.ros.org:443`
returns `subject=... CN=*.osuosl.org` with four `verify return:1` lines, and
`curl` returns HTTP `000`. The chain does not validate. §19 described this as the
upstream certificate chain problem; the measurement agrees, and the leaf being
served is an Oregon State University wildcard rather than a `*.ros.org` wildcard,
which is a CA trust issue on the host rather than something ALWAYS ON's
repository content can influence.

I stopped rather than pushing through, and I want to be explicit that this is a
deliberate stop and not a dead end. Four routes around it exist and all four are
operator decisions: installing `ca-certificates` or updating the host trust
store, routing through a proxy that terminates the connection, pinning the
upstream certificate out of band, or vendoring the packages. Each is a host-wide
change, each touches either package management, network configuration or trust
policy, and all four fall under README §4.1 rules 3, 6 and 13. Rule 6 is explicit
that conflicts involving packages or networks are reported, not forced through.

None of this touches the simulation itself. The server, the world, the eight
cameras and the portal are all running without it. SIM-07 only blocks *adding* a
new ROS 2 package from upstream.

**What I got wrong.** I started to reason about this as a mirror problem and had
drafted a note about vendoring the apt list before checking the certificate
itself. The certificate is the whole story; the mirror was never reached.<br><br><strong>Evidence:</strong><br><code>Reproduced exactly as §19.1 describes. Measured 2026-10-03.<br>The certificates.ros.org chain does not validate on this host.</code></td>
</tr>
<tr>
<td valign="top">SIM-08</td>
<td valign="top"><strong>Publish the Gazebo viewer at <code>www.300x3.com</code></strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2.1</td>
<td valign="top">The 3D viewer and its eight read-only camera feeds are verified working on the local path and <strong>not published</strong> (operator decision 2026-10-02). <code>ao-html-window</code> (<code>10.89.14.0/24</code>, <code>Internal=true</code>) exists for public-facing windows on local services and is the network the Foxglove bridge joins for this purpose. Outstanding when it proceeds: confirm the hostname, add the ingress route to <code>~/.cloudflared/config.yml</code> (a customer-facing production config, not changed unilaterally), and decide whether the viewer alone or the portal too is published, since the portal renders boning derived from real machines<br><br><strong>STILL OPEN by 10-simulation-architecture.</strong> SIM-08 stays open and I did nothing toward it. This is the clearest stop-condition item in my
group and I am reporting it as untouched rather than as progress.

The viewer works on the local path — the portal service is active and `/viewer` returns 200
on loopback — but nothing is published. §19 records the operator's decision of 2026-10-02
that it is verified locally and deliberately not published, and I have no reason to revisit
that.

Two things I found that matter for whenever it does proceed. `ao-html-window.network`, the
network that exists specifically for public-facing windows on local services, is **inactive**
— so even a configured route would have nothing to land on. And the remaining work named in
§19 all touches things I am not permitted to change unilaterally: confirming the hostname,
editing `~/.cloudflared/config.yml` (a customer-facing production config), and the
decision of whether to publish the viewer alone or the portal too — the portal renders
boning derived from real machines, so that is a data-exposure decision, not a technicality.

I changed no public port, no firewall policy, no ingress route, and no Cloudflare
configuration. I confirmed `config.yml` exists and its size and did not read or print its
contents.

**What I got wrong.** I listed `~/.cloudflared/config.yml` expecting to check whether a
hostname route for the viewer already existed, on the reasoning that a read-only check is
harmless and would tell me how far along this is. Reading a customer-facing production
ingress config to satisfy my own curiosity is not a neutral act — the file is the kind of
thing where contents inform topology I have no mandate over. Existence and size are the
whole of what I needed; I should have stopped there rather than constructing a reason to read
it.<br><br><strong>Evidence:</strong><br><code>Measured 2026-10-04. Untouched, deliberately. Publishing is a stop condition and<br>the operator already decided against it on 2026-10-02.</code></td>
</tr>

<tr>
<td valign="top">SIM-10</td>
<td valign="top"><strong>Doors are not separately colourable</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2.1</td>
<td valign="top">Walls, conveyor belts, arms and conveyor gears carry distinct materials; doors do not, because <code>massing_fab.dae</code> has no semantic part names (anonymous <code>group_0</code>–<code>group_25</code>) and <code>split-collada-parts.py</code> returns a degenerate cube signature for every part of that file, so no size distinguishes a door. Re-export the model from SketchUp with named groups (<code>door</code>, <code>wall</code>, <code>floor</code>) and the splitter will separate it. Until then doors keep the wall material rather than being guessed at<br><br><strong>STILL OPEN by 10-simulation-architecture.</strong> SIM-10 stays open, blocked on a SketchUp re-export that only the operator can perform.
§19's diagnosis is confirmed precisely rather than approximately.

The massing mesh has **34 parts and 33 of them are exact cubes** — `size(n, n, n)` for
n = 81, 149, 150, 151, 152, 153, 154, 157, 158, 159, 161, 162, 163, 165, 167, 170, 173,
190, 191, 215, 269/271, 274 and others. The single exception is `size(56, 56, 61)`. The
splitter separates parts by size precisely because the parts are anonymous (`group_0`
through `group_25` plus the rest), and a door standing in a wall is not smaller than the
wall in a way that survives rounding to an integer cube.

The remedy is already understood by the tooling and needs no code change: re-export
`massing_fab.dae` from SketchUp with semantic group names — door, wall, floor — and
`split-collada-parts.py` will separate them by name instead of by size. That is a modelling
action on the operator's file. I did not re-export it, did not modify the mesh, and did not
hand-assign a door material.

I want to be explicit about what I did **not** do. It would have been easy to make one of
those 33 cubes render a different colour and call the item done. That would be a guess
dressed as a fix: I cannot tell which cube is the door, I would be choosing on no evidence,
and a wrong guess is harder to detect later than an obviously-unresolved wall. Doors
keeping the wall material is the accurate state of the world, and §10 records it as such.

**What I got wrong.** I ran the splitter with no arguments first and got an argparse usage
error, and I recorded its `echo "exit=$?"` as `0` because the pipeline through `head` masked
the real exit status. The fault is measuring `$?` after a pipe instead of inside it — it
would have let me write "exit 0" as evidence of success for a command that never ran. I
re-ran it properly with `--list` and a real file argument; every result in this proposal
comes from that second run.<br><br><strong>Evidence:</strong><br><code>Measured 2026-10-04. §19's diagnosis reproduces exactly: the massing mesh has<br>34 parts and every one is a cube signature, so size cannot distinguish a door.</code></td>
</tr>
<tr>
<td valign="top">SIM-11</td>
<td valign="top"><strong>Signed world manifest is stale</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2.1, §16.3</td>
<td valign="top"><code>artifacts/fabrication-simulation-manifests/factory-world-v1.json</code> records a 5371-byte world; <code>factory.world</code> is now ~18 KB after the camera set, materials and the unit-scale fix, so the signature no longer describes the exported artifact. Cosmetic with respect to the running world, which is valid and serving. Re-export and re-sign with the <code>ao-sim-fabrication</code> key when that is scheduled<br><br><strong>PROGRESS by 10-simulation-architecture.</strong> SIM-11 is real and I am escalating it rather than closing it, because closing it
would require a signing operation I am not permitted to perform unattended.

The §19 description understates the drift. It records a size mismatch -- 5371
bytes recorded against a world of roughly 18 KB. The world is now **63205 bytes**,
almost twelve times the recorded size, and the `content_hash_sha256` no longer
matches either. Recorded hash `64eacbbf…`, actual `bce32f2a…`. Both fields are
wrong, which means this cannot be closed by correcting a number in the manifest.
The manifest has to be re-exported from the current world and re-signed.

That is why I stopped. Re-signing uses the `ao-sim-fabrication` key and is a
signing operation covered by README §4.1 rule 7; it needs explicit human approval
before it touches anything. I did not read the key, locate it, or attempt the
export.

The underlying cause is structural and worth recording: the manifest is signed
against a file that then keeps changing. Camera re-aiming, three generated model
blocks and four mesh-shading commits all landed after it was signed. Until
signing is tied to the export step rather than run by hand, this item will
reopen every time anyone edits the world.

§10.3 in my section file records the measured sizes and hashes.<br><br><strong>Evidence:</strong><br><code>§19.1 describes the manifest as recording 5371 bytes against a world of "~18 KB".<br>The drift is larger than recorded: the SIZE AND THE HASH both disagree.<br>Measured 2026-10-03.</code></td>
</tr>
<tr>
<td valign="top">SIM-12</td>
<td valign="top"><strong>Facility scheduler absent</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§10.2</td>
<td valign="top">The §10.2 component tree names a facility scheduler for <code>ao-sim-fabrication</code>; nothing in the repo implements one, and no §19.2 item tracked it. Closing it means a scheduler that sequences cell and kitchen work against the boned cell datums. Distinct from the RL objects (SIM-14), which are the entities such a scheduler would move<br><br><strong>STILL OPEN by 10-simulation-architecture.</strong> SIM-12 stands, and I am confirming rather than closing it because confirming is
what the evidence supports.

A case-insensitive search for `scheduler` across `GAZEBO/`, `scripts/simulation/`
and `quadlet/` returns exactly one hit: a comment in
`quadlet/sales/ao-mastodon-sidekiq.container`, which is the sales domain and has
nothing to do with facility scheduling. There is no scheduler script in
`scripts/simulation/`, no scheduler unit in `quadlet/sim-fabrication/`, and no
schedule data file next to the four simulation data files that do exist.

That absence is at least documented rather than silent, which is more than most
gaps of this size manage. But the acceptance criteria ask for a scheduler that can
drive the simulation, and there is nothing to drive. This is a build item, not a
defect, and it is not blocked on anything external -- unlike SIM-07 it needs no
operator approval and no network. It simply has not been started.

§10.3 in my section file records the search and the negative result so the next
session does not re-run it from scratch.

**Note for the compiler.** SIM-12, SIM-13 and SIM-14 are contiguous in the
simulation domain and now have very different states: one is a build item, two are
delivered but were recorded as absent. If §19 groups these under a single
"absent" narrative it will be misleading, which is why all three carry measured
evidence in their proposals rather than a status change alone.<br><br><strong>Evidence:</strong><br><code>Confirmed absent, 2026-10-03. No facility scheduler exists anywhere in the repo.</code></td>
</tr>


<tr><td colspan="6" style="background-color:#c9ccd1; border-top:2px solid #8a8f98; border-bottom:1px solid #8a8f98; padding:5px 8px; font-weight:bold; letter-spacing:0.04em;">OPS · Backup, monitoring, logs and scripts — 34 items, all Open</td></tr>
<tr>
<td valign="top">OPS-36</td>
<td valign="top"></td>
<td valign="top"></td>
<td valign="top"><strong>Open</strong></td>
<td valign="top"></td>
<td valign="top"># The monitoring collector declares four store paths that do not exist on this host

`scripts/operations/collect-system-health.py` is an OPS-group file, so I report rather than
fix. Four of its declared stores point at paths that are absent:

| Declared store | Declared path | Reality |
|---|---|---|
| `db-meshchatx` | `~/.local/share/MeshChatX/meshchatx.sqlite`, `~/.local/share/meshchatx/meshchatx.db` | **both absent**; the real store is `~/.reticulum-meshchatx/identities/&lt;hash&gt;/database.db` — 18 MB, 44+ tables |
| `db-qgroundcontrol` | `~/.local/share/QGroundControl.org/QGroundControl.db`, `~/.config/QGroundControl.org/QGroundControl.db` | **both absent**; QGroundControl has **no application database at all** |
| `db-browser-firefox-places` | `~/.mozilla/firefox/*/places.sqlite` | absent — Firefox is a **snap**; the profile is `~/snap/firefox/common/.mozilla/firefox/&lt;id&gt;/places.sqlite` |
| `db-browser-brave-history` | `~/.config/BraveSoftware/Brave-Browser/Default/History` | absent — Brave is a snap with **no profile directory at all** |

**The failure direction is safe, and that matters for how this gets prioritised.** The
collector reports an absent store as absent and reads nothing. So this does not cause a
privacy leak and needs no emergency handling — but it does mean four entries in the declared
inventory report a wrong answer, and two stores are effectively unobserved despite §3.3.1
listing them as SQLite stores in the program-to-database map.

The MeshChatX case is the significant one: there is a live 18 MB database holding 8862
announces and 3048 crawl tasks that reporting does not currently cover. The QGroundControl
case is different in kind — there is nothing to cover, because the database §3.3.1 described
does not exist. I have corrected both rows in §3.3.1 to say what actually exists.

**Two judgement calls for whoever picks this up, not decisions I should make:**

- **The Firefox and Brave fixes are browser stores**, which are under an explicit operator
  exclusion from collection (2026-10-03). Correcting the *path* is a fidelity fix; it
  would also make the collector start finding stores that are currently reported absent.
  That is arguably what the inventory intends, but it touches the exclusion decision, so I
  have left it alone rather than quietly widening what is read.
- **MeshChatX and QGroundControl are not excluded** and fixing their paths only widens
  accurate coverage of already-declared stores — lower risk, and probably the right first
  move.

## What I got wrong

See `spec-NET-51.md` for the full list. The one relevant here: I asserted a general claim
about the collector's coverage without first enumerating what it actually covers, and the
enumeration is what found the gap. Same failure mode twice this pass.</td>
</tr>
<tr>
<td valign="top">OPS-35</td>
<td valign="top"></td>
<td valign="top"></td>
<td valign="top"><strong>Open</strong></td>
<td valign="top"></td>
<td valign="top"># What I got wrong, and why

**I repeated a mistake my own prior session had already declared.** In enumerating the
Metabase environment I ran `podman inspect ao-metabase --format '{{range .Config.Env}}...'`
unfiltered and printed `MB_DB_PASS` into session output. My previous proposal recorded this
exact incident and named the safe method (`| grep -v -i pass`). I read that file and still did
it. The value is not reproduced in any section file, the README, or this proposal, and it is
not a credential I created — but it was printed when it should not have been, and knowing the
fix is not the same as applying it. The filter is now the first thing I type, not a
correction I read afterwards.

**I nearly repeated a different overclaim.** I first wrote "the four
`localhost/foxglove-bridge` containers". `podman ps -a | grep -c foxglove` returns **3**, of
which one is the sanctioned digest-pinned `ao-sim-fabrication-foxglove`. I had counted by
remembering the earlier `podman ps` listing rather than by re-running the count. Same failure
class as the four errors recorded in the previous proposal: a number in prose that no command
produced. Corrected before commit, and the count is stated here so a later reader can check it.

**One stale cross-reference survived two prior revisions.** §3.3.0 ended by pointing at §2.2 to
reconcile "the adjacent unregistered `10.89.10.0/24` and `10.89.11.0/24`". `10.89.10.0/24` has
been registered as `ao-reporting-egress` since §2.2 was rewritten, and §2.2 contains no
reconciliation text at all. The previous session corrected PostGIS, the reporting grants, and
four impossible dates in these same sections and passed over this sentence. Lesson for me: a
# Other corrections made this session

**§1 — the host is not Kubuntu.** `lsb_release -a` reports Ubuntu 26.04.1 LTS "resolute";
`/etc/kubuntu-release` does not exist; `kubuntu-desktop` is `Installed: (none)` and lives in
`universe`. Three `kubuntu-*` packages are installed. The host is Ubuntu LTS with KDE Plasma
6.6.6 on SDDM. Every functional claim §1 rests on is independently true and was verified
(`konqueror`, `kwalletmanager5`, `kwallet-query` present; `ros2` at `/opt/ros/lyrical/bin/ros2`;
i7-8700K; GeForce GTX 1080). Only the distribution label was loose. §1 now records this rather
than leaving a reader to discover it.

**§1 — QGroundControl is an AppImage, not a package.** No `qgroundcontrol` binary on PATH, no
entry in `/usr/share/applications`; it runs from
`~/Documents/APP IMAGES/QGroundControl-x86_64.AppImage`. `gzserver` is absent from the host PATH
because Gazebo runs containerised. Noted so §1 does not read as a package manifest.

**§6.A.3.1 — the Grafana datasource blocker re-attempted, still blocked, but the host-version
claim is now proven.** `sudo -n -u postgres psql` → `interactive authentication is required`;
`podman exec ao-grafana psql` → `sh: psql: not found` (the image ships no client). What I could
prove: Grafana's own log shows `Connecting to DB dbtype=postgres` with successful migrator lock
and unlock, and Metabase logs `Successfully verified PostgreSQL 18.6 (Ubuntu
# Claims re-verified as correct, with no change made

Proving these took as long as the corrections did, so they are recorded:

- **14 `ao-*` networks**, matching §2.2 and the §6.A.3.1 staleness table.
- **`ao-egress-community` and `ao-ardupilot-sitl` both do not exist** —
  `unable to find network with name or ID ...: network not found`. The §6.A.3.1 claim stands.
- **`10.89.11` absent from the registry** (`grep -c` → 0), folded into `ao-sales` as §5 records.
- **`sales_reporting_role` holds SELECT on exactly five views and no base table** —
  `v_reporting_orders`, `v_reporting_receipts`, `v_reporting_entitlements`,
  `v_reporting_sale_provenance`, `v_corda_entry_readiness`;
  `has_table_privilege(...,'SELECT')` returns `f` for all 17 base tables including `orders`.
  The §6.A.3 read-only claim is correct.
- **`sales_migration_role` is a superuser** with Create role, Create DB, Replication, Bypass RLS
  — matching the §6.A.3 watch-note.
- **Grafana/Metabase reach paths:** `ao-grafana` and `ao-metabase` both on `ao-admin` and
  `ao-reporting-egress`; `GF_DATABASE_HOST=/var/run/postgresql`; `MB_DB_HOST=10.42.0.1`;
  listeners `127.0.0.1:3001` and `127.0.0.1:3002`, loopback-bound only. §6.A.2 is correct.
- **Per-domain PostgreSQL versions in §3.3.1 all confirmed:** `ao-sales-db` 17.11,
  `mastodon-db` 17.11, `ao-fabrication-db` 17.11, `ao-webodm-db` 9.5.25, host cluster 18-main
  online.
- **PostGIS placement in §3.3.1 confirmed:** `webodm` has only `plpgsql`; `webodm_dev` has
  `plpgsql` plus `postgis 2.3.2`.
- **§3.3.0.1 isolation:** inside `ao-fabrication-db`, `/proc/net/route` holds exactly one route
  (its own subnet, no default) and `/proc/net/arp` resolves `10.89.12.1` with flags `0x2`. The
  "judge reachability from ARP, not a refused connect" note is correct.
- **§3.3.0.2 Domoticz posture holds:** `127.0.0.1:8080` open, `10.42.0.1:8080` refused, and no
  `:6144` listener at all.
- **§3.3.0 machine reachability:** `10.42.0.1` answers (0% loss), `10.42.0.96` shows
  `dev eno1 FAILED` in `ip neigh` and 100% loss on ping. The "not currently reachable" caveat
  remains accurate.

# Not touched

No payments, ledger keys, provenance records, secrets, backup/restore data, radio, serial or
firewall configuration, public ports, or any section file outside the three I own. §19 was not
edited. No container was started, stopped or removed. The `ao-egress-community` name/CIDR
decision and the `gui-boundary-matrix.yaml` reconciliation both belong to other groups and were
left untouched.
18.6-0ubuntu0.26.04.1) application database connection`. So the "host PostgreSQL 18" claim in
§3.3.1 is now measured from two independent sources rather than inferred from
`/etc/postgresql/`. Still unconfirmed, and the OPS group's to answer: which datasources Grafana
has actually *loaded*, as distinct from which files are provisioned.
cross-reference into another session's file is a claim about that file, and it goes stale
silently. Cross-references need the same re-verification as the prose around them.
Four unmanaged Grafana containers (`relaxed_tharp`, `confident_khayyam`, `keen_bhabha`,
`ao-sqli3`), created 2026-10-03 during datasource/plugin investigation, are running with no
Quadlet owner and are absent from the §5.1 group D inventory that §6.A.3 declares complete at
eighteen rows. Two of them mount writable `/tmp` paths, and `ao-sqli3` supplies the unsigned
`frser-sqlite-datasource` plugin to a Grafana instance that does not carry the signed instance's
allow-list policy.

**Not remediated by me, deliberately.** Stopping containers is a destructive action on running
state (README §4.1 rule 3), touches other sessions' work, and the unsigned-plugin question is
already tracked by the OPS group. Recorded in §6 as §6.A.3.2 with the full measurement, and
reported to the operator. Needs operator approval before removal.</td>
</tr>
<tr>
<td valign="top">OPS-01</td>
<td valign="top">Metabase persistence and first read-only query</td>
<td valign="top">ST-20</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§15.1, §17.2</td>
<td valign="top"><strong>Provision the Metabase application database</strong> (dedicated PostgreSQL database for the Metabase schema, saved questions, dashboards, and subscriptions) and the per-source <strong>read-only</strong> reporting roles, one per PostgreSQL and MySQL source with no write, DDL, or owner privilege. Then confirm state survives restart and a protected ad-hoc read-only reporting query succeeds with no source writes. The application database must never be written to by a reporting source.<br><br><strong>PROGRESS by 17-backup-restore-monitoring-and-completion-criteria.</strong> **Half done, and I stopped at the half that needs credentials.** No §17 edit;
this records measured state so the compiler can correct the OPS-01 row.

**Half 1 — the application database exists and is in use.** Measured, not
assumed: `ao-metabase` logs `Successfully verified PostgreSQL 18.6 … application
database connection` and `Database Migrations Current`, and its app data is on
the named volume `ao-metabase-postgres-data`, so state survives restart.
`MB_DB_DBNAME/HOST/USER/PASS/…` are set in the container. **No secret value was
printed** — names only, values redacted.

I nearly filed the opposite conclusion. `podman logs ao-metabase` is full of
`h2 Database 1 'Sample Database'` lines, which reads like Metabase running on
an embedded H2 file with no PostgreSQL at all — and H2 would fail the
persistence requirement outright. It is not: the h2 lines are Metabase's
bundled *sample dataset* being synced as a source, not its application store.
The application store is the PostgreSQL 18.6 line above. Lesson: a log grep
that matches the wrong subsystem produces a confident false alarm.

**Half 2 — the per-source read-only reporting role does not exist, and creating
it is a stop condition I did not cross.** Measured: `metaread` is absent and
the `reporting_sales` schema it would read from is absent too.
`scripts/ops/provision-sales-reporting.sh` is supposed to provision this and is
**broken in two ways, both found by reading it rather than running it**:

1. `install -m 0600 /tmp/reporting-hub.sql /tmp/reporting-hub.sql` — identical
   source and destination, so it is a no-op that appears to "install" the file.
2. The SQL it feeds to `psql` lives at
   `config/platform/postgresql/reporting-hub.sql` in the repo, not at
   `/tmp/reporting-hub.sql`. Measured: `/tmp/reporting-hub.sql` → *No such file
   or directory*. So the script's final `psql -f` would fail even if the file
   were staged there by hand.

The wrapper also provisions `sales_reporting_role`, which is a **different**
role from the read-only `metaread` that OPS-01 asks for, and it never grants
`SELECT`. Read-only reporting is therefore not delivered on this path.

**Why I stopped rather than fixed it.** Provisioning the role means reading a
credential from KDE Wallet, creating a login role, and granting it access to
reporting data — credentials and database privileges, both explicit stop
conditions in my brief. The two script defects are safe to fix in themselves
(stale path, no-op `install`), but fixing them without the operator's approval
would leave a script that *looks* runnable for a privilege change nobody
approved, which is worse than leaving it visibly broken.

**Operator decision required:** approve provisioning the `metaread` read-only
role (one per source, `CONNECT` + `USAGE` + `SELECT` only, no write, DDL or
owner) and confirm whether `sales_reporting_role` should be replaced by it or
kept as a separate write-capable role. The SQL already exists in-tree and
grants exactly the right privileges.

**Also belongs to another group, reported not touched:** the sales domain owns
`provision-sales-reporting.sh` and the `sales_reporting_role` grant. Fixing its
broken paths is arguably a PAY/SALES item, not an OPS one. I did not renumber
or edit anything outside §17.

Files changed: none for this item (measurement only).<br><br><strong>Evidence:</strong><br><code># HALF 1 — the Metabase application database exists and is in use.<br># (names only, no credential values)<br>$ podman logs ao-metabase | grep -i 'application database'<br>2026-10-01 22:22:54 INFO db.setup :: Successfully verified PostgreSQL 18.6<br>    (Ubuntu 18.6-0ubuntu0.26.04.1) application database connection.<br>2026-10-01 22:22:56 INFO db.setup :: Database Migrations Current ...<br>$ podman exec ao-metabase sh -c 'env | sed "s/=.*/=&lt;redacted&gt;/"' | grep MB_DB<br>MB_DB_DBNAME  MB_DB_HOST  MB_DB_PASS  MB_DB_PORT<br>MB_DB_SSL  MB_DB_TYPE  MB_DB_USER          # all values redacted<br>$ podman inspect ao-metabase --format '{{range .Mounts}}…'<br>/metabase-postgres-data &lt;- …/volumes/ao-metabase-postgres-data/_data<br># a named volume, so state survives restart</code><br><br><strong>PROGRESS by 17-backup-restore-monitoring-and-completion-criteria.</strong> Adds **§17.2.0**, recording that the persistence half of OPS-01 is already met
and — more usefully — that `ao-metabase-postgres-data` is a **vestigial, never-written
volume**. It is 4 KB, empty, and has been since it was created on 2026-09-24.

That is correct, not a fault. `MB_DB_HOST=10.42.0.1` points Metabase at the host
PostgreSQL cluster via the `metabase_app` role created by
`scripts/ops/provision-reporting-postgres.sh`, so saved questions, dashboards
and subscriptions live in the `metabase` database on the host. The deployment
migrated off embedded H2 on 2026-09-25 (liquibase `v47.00-002` is the last H2
migration in `metabase-h2-migrate-final.log.1`).

The reason this is worth writing down: **the mount is declared in both the
repository Quadlet and the deployed copy, and an agent auditing persistence by
volume size would correctly conclude that Metabase is losing all its state.** It
is not. Flagged for removal as separate cleanup — deliberately **not** done here,
because removing a declared volume mount is a container-definition change outside
the backup/monitoring remit.

**OPS-01 stays OPEN, blocked, on the read-only half.** Creating the per-source
read-only roles means running `config/platform/postgresql/metaread-grants.sql` as
the PostgreSQL superuser with a bound password, and all three escalation routes
are refused to this session (evidence above). Running the verification query also
requires a `metaread` password from KDE Wallet and a Metabase session — inside the
"secrets and credentials" stop condition. Neither step is guessed at or marked
done. The remaining work for whoever picks this up: create `metaread`, restart
`ao-metabase`, confirm state survives, then run one ad-hoc `SELECT` and confirm
zero source writes.

What I got worth recording: I opened this item expecting the empty volume to be
the bug, because "container app-data volume is empty" is a familiar failure shape
and I had a plausible story ready for it — H2 never migrated. The migration logs
show the opposite migration direction (H2 **out**, PostgreSQL **in**, on
2026-09-25) and the env vars settle it. Checking the direction of a migration
before theorising about it cost one command; assuming it would have cost a
false finding filed as fact.<br><br><strong>Evidence:</strong><br><code># The Metabase persistence half of OPS-01 is ALREADY SATISFIED, and the reason<br># is counter-intuitive enough to record: the app-data volume is empty.</code></td>
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
<td valign="top"><strong>Root decided 2026-10-02: <code>/ALWAYSON/logs/</code></strong> (§16.3). §16.3 and §13.3.1 corrected and the <code>LOGOS-JOURNALS</code> typo fixed; the 2 766-line operational journal merged and verified identical; five entries that existed nowhere created and given writers; <code>check-logs-journals.sh</code> asserts existence and freshness for all 18. <strong>Remaining:</strong> add <code>logs/</code> to the restic path set; physically merging the two trees would mean redeploying the *flat* deployed unit copies (§16.1.1) and restarting Gazebo and <code>ao-build-update</code>, so it was not done. Retention is OPS-26; the missing backup timer is tracked by no ID and needs one.<br><br><strong>PROGRESS by 17-backup-restore-monitoring-and-completion-criteria.</strong> **Half met, half open — recorded as such rather than closed.** Re-measured
2026-10-03: `/ALWAYSON/logs/` is the single journal root. There is no second
root, `logs/installation/` is a subdirectory of it and not a sibling, and the
`LOGS-JOURNALS/` draft name appears nowhere on disk. The canonical-root half of
this item is therefore satisfied.

**The outstanding half is that `logs/` is still absent from the restic path
set.** Measured directly: the nightly job passes 11 paths and none is
`logs/`. The consequence is stated plainly in §17.5 — a restore to a new host
comes back with **no operational history at all**, which undercuts §16.3's
entire purpose.

I did not add it. It is a one-line change to an approved path list, but it
enlarges what the nightly job copies, and the journals are the fastest-growing
thing in `logs/`. That is an operator decision, and it is why this item is
`update`, not `close`.

Also new in §17.5: the retention policy that OPS-25/OPS-26 previously left
unowned, staged and parse-verified (see the OPS-26 proposal).

Files changed: `agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md` (§17.5).<br><br><strong>Evidence:</strong><br><code># one canonical root: no sibling, no LOGOS-JOURNALS draft directory anywhere<br>$ cd /ALWAYSON &amp;&amp; find . -maxdepth 2 -iname '*LOGOS*'<br>(no output)<br>$ cd /ALWAYSON &amp;&amp; ls logs/ | head<br>README.txt  audit.log  backup  backup.log  gpu-runtime  gpu-runtime-check.log<br>installation  installation-journal.log  lmstudio-readme-preset.sha256  mastodon-local-proxy.log<br># logs/installation is a SUBDIRECTORY of logs/, not a sibling root</code></td>
</tr>

<tr>
<td valign="top">OPS-09</td>
<td valign="top"><strong>Restic path set covers every data class</strong></td>
<td valign="top">ST-18, ST-03</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§17.1, §3.3.1, §8.4</td>
<td valign="top"><strong><code>data/</code> added to the path set 2026-10-02.</strong> <code>data/</code> was excluded and is now in the path set: <code>data/ardupilot</code> (2.1 GB), <code>data/corda-install</code> (282 MB), plus <code>sim-fabrication</code>, <code>sales</code>, <code>mapping</code>, <code>field</code>, <code>payment</code>, <code>ledger</code>. Snapshot <code>fb52984b</code> is the first to include it. Photogrammetry drive still deliberately excluded. <strong>Still open:</strong> <code>data/build-update/cache</code> is excluded as regenerable, and the set should be re-checked whenever a new <code>data/</code> class appears.<br><br><strong>PROGRESS by 17-backup-restore-monitoring-and-completion-criteria.</strong> **Stays OPEN, but the exclusion set is now an explicit decision rather than an
omission.** New §17.4 enumerates the whole path set and accounts for what is
missing, which is what the "re-checked whenever a new `data/` class appears"
half of the item actually asks for.

Enumerated: `config`, `artifacts`, `backups/postgres`, and nine `data/` classes
(`ardupilot`, `corda-install`, `sim-fabrication`, `sales`, `mapping`, `field`,
`payment`, `ledger`). Deliberately excluded, each with a stated reason:

- `data/build-update/cache` — regenerable build output; backing it up spends
  repository space on something that can be rebuilt.
- The photogrammetry drive — excluded because it is large and holds source
  imagery. **§17.4 calls this the weakest exclusion in the set**, because that
  drive holds the mapping source data and §17.1's copy table treats "current
  project data" as hourly-backup material. It is recorded rather than quietly
  accepted.

**Four `data/` subdirectories are in no path set and are not yet classified:**
`cache` (4 KB), `monitoring` (269 MB), `prometheus-textfile` (8 KB),
`sim-vehicle` (8 KB). `data/monitoring` at 269 MB is the only one that matters:
it is generated metric history, so losing it is acceptable, but at that size
the exclusion should be a decision on record. Two of the small ones are
trivially justifiable (`prometheus-textfile` is regenerated by the collector,
`cache` by definition) and `sim-vehicle` is 8 KB, so leaving 8 KB classes
unbacked is not a storage decision — it is simply not done yet. **Requires
operator decision**, because adding `data/monitoring` at 269 MB to a nightly
job is a change in what the backup costs.

Not done by me, deliberately: no path was added or removed. Enlarging the
nightly set is the operator's call.

Files changed: `agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md` (§17.4).<br><br><strong>Evidence:</strong><br><code># the current path set, one path per line, from the live script:<br>$ grep -o "restic backup.*" scripts/backup/restic-run.sh | tr ' ' '\n' | grep ALWAYSON<br>/ALWAYSON/config<br>/ALWAYSON/artifacts<br>/ALWAYSON/backups/postgres<br>/ALWAYSON/data/ardupilot<br>/ALWAYSON/data/corda-install<br>/ALWAYSON/data/sim-fabrication<br>/ALWAYSON/data/sales<br>/ALWAYSON/data/mapping<br>/ALWAYSON/data/field<br>/ALWAYSON/data/payment<br>/ALWAYSON/data/ledger<br># 11 paths; `logs/` is NOT among them.</code></td>
</tr>

<tr>
<td valign="top">OPS-11</td>
<td valign="top"><strong>Alerting mechanism and thresholds</strong></td>
<td valign="top">ST-19</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§17.2</td>
<td valign="top">§17.2 requires alerts for disk pressure, backup failure, restart loops, unexpected listeners, radio loss, certificate expiry and cross-domain denials, but no alertmanager or notification target is specified anywhere, and ST-19 records no rules or dashboards built. Name the alerting component, the routing target per severity, and a threshold per rule.<br><br><strong>PROGRESS by 17-backup-restore-monitoring-and-completion-criteria.</strong> **Stays OPEN.** Two of the three parts of this item are now done; the third is
blocked on an operator decision.

Done in §17.2.1 and §17.2.2: the alerting component is named (Prometheus rule
evaluation, explicitly not Alertmanager, which is measured absent), the
thresholds are stated per rule in a ten-rule table, and the rules exist as a
validated file — `config/platform/monitoring/alwayson-alerts.yml`, mounted
read-only by `ao-prometheus.container` and loaded via `rule_files`.

Why it is not closed: **there is no routing target.** The item asks for "the
routing target per severity" and none exists — no Alertmanager container, no
image, no receiver anywhere. Rules evaluate and show up in Grafana, but nothing
reaches an operator who is not already looking at the dashboard. Adding
Alertmanager plus a delivery target means a new component, a new network path
and very likely a new credential, which is §4.1 rule 6/7 territory and needs
explicit operator approval. I stopped there rather than build it.

Also honest about partial coverage, recorded in §17.2.2 and §17.2.3: three of
the ten rules (`AoBackupStale`, `AoRestoreTestStale`,
`AoRepositoryVerifyStale`) reference metric names nothing currently exports, so
they cannot fire yet; and seven of the eleven required conditions have no
exporter at all, measured by `node_systemd_unit_state` returning 0 series and
only two scrape jobs existing. A rule that can never fire is not alerting, so
these are documented as unwired rather than counted as coverage.

**What I got wrong, twice, both worth reading.** First, I inlined a top-level
`groups:` block into `prometheus.yml` because that is how rule files normally
look; `promtool` rejected it with `field groups not found in type
config.plain`, and the rules had to be split into a second file that
`prometheus.yml` references through `rule_files`. Second, while fixing the YAML
indentation I ran a `sed` that stripped the two leading spaces from every line
in a range, which broke the block structure, and then a second `sed` that added
them back to a range whose start line I had miscomputed. Both produced
plausible-looking files that failed validation. Lesson: validate YAML with a
real parser after every reindent, and never fix indentation with a blind
line-range `sed`.

Files changed: `config/platform/monitoring/alwayson-alerts.yml` (new),
`config/platform/monitoring/prometheus.yml` (rule_files + moved comment),
`quadlet/operations/ao-prometheus.container` (second read-only mount).<br><br><strong>Evidence:</strong><br><code>$ curl -s http://127.0.0.1:9090/api/v1/rules | python3 -c '...print("groups:",len(...))'<br>groups: 0</code><br><br><strong>PROGRESS by 17-backup-restore-monitoring-and-completion-criteria.</strong> **Supersedes** the evidence line `groups: 0` in `ops-a-OPS-11.md` of this date.
That earlier proposal is left in place rather than edited, per the rule that a
session does not rewrite its own prior record — but its first evidence line is
wrong and this corrects it.

**I filed `groups: 0` as evidence that the rules were loaded. It is the
opposite.** `data.groups` having length zero means Prometheus is evaluating no
rule groups at all. I read a healthy-looking integer as proof of success without
asking what the number meant. The rest of that proposal is fine — `promtool`
against a throwaway container does prove the two *files* are valid and contain
10 rules — but it says nothing about the running service, which is the entire
point of this item.

Re-measuring properly found **two independent deployment faults**, neither
visible from the repository:

1. **The mount was never deployed.** `quadlet/operations/ao-prometheus.container`
   declares two `Volume=` lines; the deployed copy at
   `~/.config/containers/systemd/ao-prometheus.container` declares one. Quadlets
   deploy as flat copies, so editing the in-tree file changed nothing live, and
   the alerts file is absent from the running container.
2. **The mounted config is stale by inode.** Even the mount that does exist is
   bound to the old inode (18219046, 1881 B) rather than the current one
   (18223436, 2503 B). A file bind mount follows the inode, not the path, so
   replacing the file in place — which an editor or `git checkout` does — leaves
   the container reading the previous version indefinitely. The container's copy
   has no `rule_files:` key at all.

Fault 2 is the more dangerous, because it is invisible: the mount looks correct,
and `promtool check config` on the container's own copy returns SUCCESS, since
the stale file is a perfectly valid config — just not the one on disk. A future
fix that adds the alerts mount without restarting the container would appear to
work and still evaluate no rules.

**The generalisable lesson**, since this is the second time this session filed a
number that could not fail. The drill in OPS-24 compared the restored tree with
itself and reported `identical: 63`. Here a zero was read as healthy. In both
cases the measurement was structurally incapable of signalling the fault it was
being used to rule out. A verification has to be asked "what result would prove
this broken?", and the answer has to be checked against something real.

I did not redeploy. Restarting `ao-prometheus` interrupts its scrape targets,
and adding a mount to a deployed Quadlet is an operator action. **OPS-11 now has
three open grounds, not one:** no routing target (unchanged), the alerts mount
not deployed (new), and the stale config inode (new).

Unchanged and still true: the alerting component is Prometheus rule evaluation,
the ten thresholds stand, and `AoBackupStale` / `AoRestoreTestStale` /
`AoRepositoryVerifyStale` still reference metric names nothing exports — so even
once deployed, those three cannot fire.

Files changed: `agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md` (§17.2.1 rewritten;
§17.2.2 and §17.2.3 unchanged and still accurate).<br><br><strong>Evidence:</strong><br><code># *** THE PRIOR PROPOSAL'S FIRST EVIDENCE LINE WAS A FALSE PASS. ***<br># It cited `groups: 0` as proof the rules were loaded. data.groups having<br># length zero means Prometheus is evaluating NO RULE GROUPS AT ALL.<br># The remaining lines in it (promtool on a --rm throwaway container) are<br># valid evidence that the FILES are correct. They say nothing about the<br># RUNNING service, which is what this correction is about.<br>$ curl -s http://127.0.0.1:9090/api/v1/rules \<br>    | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["data"]["groups"]))'<br>0</code><br><br><strong>PROGRESS by 17-backup-restore-monitoring-and-completion-criteria.</strong> Adds **§17.2.1.1**, which takes the "three rules reference metrics nothing
exports" note that both prior OPS-11 proposals mention in passing and makes it
the measured, primary statement.

`AoBackupStale`, `AoRestoreTestStale` and `AoRepositoryVerifyStale` are the only
three of the ten rules built from custom series rather than `node_*`/`up`, and
**no exporter, textfile collector, recording rule or scrape job produces any
`ao_*` series anywhere in the repository.** The single repo-wide grep returns
exactly one file: the rule file that consumes them. Prometheus currently holds
zero `ao_*` series.

Consequence, which is the point: adding the missing `Volume=` line and
restarting `ao-prometheus` would load all ten rules, but these three would
evaluate to an **empty vector**. An expression over a non-existent series does
not fire and does not report "no data" — it is silent. So the redeploy does not
fix OPS-11; the remaining work is a missing collector, not a threshold and not a
deployment. The `data/prometheus-textfile/` channel already used by
`ao-db-security.prom` is the obvious implementation. I have not written it,
because it changes what `ops` emits into a shared monitoring path and it is the
mechanism by which an operator would be paged about backup failure — new
alerting behaviour, which is operator territory.

**Also corrected the §17.2.2 threshold table, now transcribed from the `expr:`
lines.** The previous entry claimed `AoBackupStale` fires at 900 s (15 m); the
file says 93600 s (26 h). The old names (`ao_restic_backup_last_success`,
`ao_restore_test_last_run`, `ao_repository_verify_last_success`) were likewise
reconstructed rather than read, and were wrong the same way.

What I got wrong, and it is the same failure mode twice in one session: I wrote
a threshold table from what the rules are *for* instead of reading the values.
The invented 900 s against a nightly job was **twenty-six times tighter** than
the real threshold — a reader tuning against it would have concluded the nightly
backup breaches its own SLO on every run. The real 93600 s is a 26 h threshold
against a 24 h job: a 2 h grace window, which is a deliberate decision someone
made. My "sensible" number was the wrong one. A retuned table must be diffed
against its source, however confident it feels; and a threshold that looks loose
deserves a question rather than a correction.

Files changed: `agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md` (new §17.2.1.1;
§17.2.2 table corrected).<br><br><strong>Evidence:</strong><br><code># THIRD proposal on OPS-11. Corrects a table in the section file and adds the<br># open ground that survives the redeploy OPS-11 already requires.</code></td>
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
<td valign="top">OPS-24</td>
<td valign="top"><strong>Restore drill for the restic backup</strong></td>
<td valign="top">ST-18</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§17.1, §19.2</td>
<td valign="top"><strong>Restore drill passed 2026-10-02; still open on redundancy.</strong> Restored snapshot <code>fb52984b</code> to a scratch directory and compared against live: <code>data/sales</code> and <code>data/corda-install</code> file counts match and spot checksums are byte-identical; <code>data/ardupilot/Tools</code> restored 1,967 files / 368 MiB. <code>restic check</code> reports no errors across 26 snapshots. Backup history is real: 23 daily snapshots 2026-08-25 to 09-24, an 8-day outage, then <code>fb52984b</code>. <strong>Still open:</strong> only one snapshot included <code>data/</code> at the time of the drill, so a single bad night is not yet survivable. Consecutive <code>data/</code>-inclusive snapshots are required.<br><br><strong>PROGRESS by 17-backup-restore-monitoring-and-completion-criteria.</strong> **Progress, still OPEN.** New §17.4 records a restore drill actually executed
by `scripts/restore/restore-restic-drill.sh` (new this session) against the
off-host repository, with the per-measure table.

Why it does not close, and the two limits are recorded rather than buried:

1. **The drill had no database dumps to validate** — step 2 of the seven-step
   test had nothing to work on, because the off-host repository holds a single
   proof snapshot covering only `config` and `artifacts`, while the `pg_dump`
   output lives in the local repository. Reporting "0 dumps, 0 problems" as a
   pass would overstate the result, so it is reported as a scoped pass.
2. **It still has no cadence** — §17.1 requires a monthly restore test and
   nothing schedules it. Installing a timer would restart nothing and touch no
   data, but it creates a recurring privileged job on backup material, so it is
   left as an operator decision rather than done unasked.

**The most important thing I got wrong, and it is worth the whole session.**
The drill's comparison step first resolved the live file as
`$live_root/$rel` and fell back to `/ALWAYSON/…` only when that path was
absent — but `$live_root` **is** the restored tree, so it compared every
restored file with itself and reported `identical: 63, changed: 0`. A perfect
score from a test that cannot fail. Corrected, the same snapshot reports
`identical: 59, changed: 4`, which matches an independent manual `sha256sum`
comparison done outside the script. A false pass is worse than a failure
because it gets filed as evidence. The lesson is now a comment in the script:
**a comparison step must be able to fail**, and the cheapest proof is to run it
once against data already known to have changed.

Safety is by construction rather than by care: the script requires an explicit
`--scratch`, refuses any path inside `/ALWAYSON` after resolving it with
`readlink -m`, and refuses a scratch directory that is not empty. All three
refusals are shown in the OPS-08 evidence above.

Files changed: `scripts/restore/restore-restic-drill.sh` (new),
`agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md` (§17.4).<br><br><strong>Evidence:</strong><br><code># the drill ran against the off-host repository; table in 17.4:<br>#   snapshot 56bf1af5, 63 files, 304.564 KiB<br>#   hash-identical to live: 59 of 63<br>#   changed since snapshot: 4 (all config/, all mtime AFTER the snapshot)<br>#   changed with mtime BEFORE the snapshot (corruption signature): 0<br>#   database dumps in this snapshot: 0<br>#   result: PASS<br>$ export RESTIC_REPOSITORY=/media/scottw/…/ALWAYSON-BACKUPS<br>$ restic check --read-data-subset=1/10<br>no errors were found</code></td>
</tr>

<tr>
<td valign="top">OPS-26</td>
<td valign="top"><strong>Retention for the log subdirectories and for journald</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§16.3, §17.2</td>
<td valign="top">OPS-25 covers the top-level <code>*.log</code> files only. The subdirectories (<code>operations/</code>, <code>gpu-runtime/</code>, <code>backup/</code>, <code>installation/</code>) hold per-operation audit records that must not simply be truncated, and have no retention at all. Separately, <code>journalctl --disk-usage</code> reports 4 GB with no explicit <code>SystemMaxUse</code>, so journald is on its built-in default while carrying 32 of 33 units. State a retention period per subdirectory and an explicit journald cap.<br><br><strong>PROGRESS by 17-backup-restore-monitoring-and-completion-criteria.</strong> **Retention is now stated per class; installation still needs root.** §17.5
carries a table giving each log class its rotation policy, its budget and
whether it is active. Measured and stated:

| Class | Budget |
|---|---|
| `logs/*.log` top level | 14 rotations, daily |
| `logs/{operations,installation,backup,gpu-runtime}/` | 400 rotations, daily |
| journald | `SystemMaxUse=4G`, `MaxRetentionSec=90day`, `SystemKeepFree=8G` |

Two decisions worth defending, because both look wrong at a glance:

- **The subdirectories get 400 days, not 14.** They hold per-operation audit
  records that §16.3 exists to preserve; rotating them on the same schedule as
  top-level files would destroy the evidence. 400 days covers four quarterly
  DR exercises plus margin. It is *age*-based (`rotate 400` with `daily`) and
  not `maxsize`, because `maxsize` evicts the **newest** file when a threshold
  is exceeded — precisely backwards for an audit trail.
- **The budgets are generous headroom, not a disk-pressure response.** Measured
  sizes are `backup` 28K, `gpu-runtime` 12K, `installation` 288K, `operations`
  580K on a 458G filesystem with 127G free. If a future measurement shows
  `operations/` growing large, the budget can be narrowed per directory;
  nothing today justifies it.

`MaxRetentionSec=90day` is the setting that actually changes behaviour.
`SystemMaxUse=4G` alone is roughly what is already in use (4G measured), so it
evicts nothing on a normal day. What is being removed today is the
**unbounded** forensic window: the shipped `journald.conf` has every cap
commented out, so the effective ceiling is a size-based default with no age
limit at all. Backup and restore evidence is **not** lost to the 90-day cap —
it lives in `/ALWAYSON/logs/` and `/ALWAYSON/backups/` on the 400-day budget,
not in journald.

**Measurement error I made and corrected:** I first ran `du -sh logs/...` from
the session worktree and got `No such file or directory` for all four, then
almost recorded the sizes from the worktree as absent. The live tree at
`/ALWAYSON` is the authority and returns the values above. Re-measuring also
showed `operations/` had grown 572K → 580K as concurrent sessions logged,
which is itself evidence these directories are append-only and live — so the
§17.5 text was updated rather than left quoting the stale figure.

The drop-in is staged as `journald-alwayson.conf` for installation at
`/etc/systemd/journald.conf.d/60-alwayson-retention.conf`, deliberately **not**
as an edit of the shipped `journald.conf`, which a package upgrade overwrites.

**Consequence while this stays uninstalled**, recorded in §17.5:
`sim-gz-server.log` has no size cap — the top-level policy rotates by age, not
by size — so a chatty Gazebo session grows that file without bound, and the
subdirectories grow without bound too. Neither is a capacity risk today; both
are unbounded in principle.

Files changed: `config/host/journald-alwayson.conf` (new),
`config/host/logrotate-alwayson.conf` (four subdirectory blocks),
`agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md` (§17.5).<br><br><strong>Evidence:</strong><br><code># journald today: 4G in use, shipped caps all commented out<br>$ journalctl --disk-usage<br>Archived and active journals take up 4G in the file system.<br>$ grep -n '^#*SystemMaxUse\|^#*MaxRetentionSec' /etc/systemd/journald.conf<br>27:#SystemMaxUse=<br>35:#MaxRetentionSec=0<br>$ df -h /<br>/dev/nvme0n1p2  458G  308G  127G  71% /</code></td>
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
<td valign="top"><strong>Repository exists and verifies; deliberately not scheduled. 2026-10-03.</strong> Merged with the earlier duplicate of this item. The operator chose <code>/media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS</code>, which sits inside the running pCloud sync root, so the repository replicates to pCloud without a separate rclone remote. Initialised and proven: snapshot <code>56bf1af5</code>, 63 files, <code>restic check</code> no errors. It reuses the local repository password, so the existing <code>ao-admin/restic-repository-password</code> wallet entry governs both. <strong>Deliberately not live:</strong> no timer, no cron, no reference from <code>restic-run.sh</code> — the nightly job still writes only to the local repository. Enabling it is an operator decision.<br><br><strong>PROGRESS by 17-backup-restore-monitoring-and-completion-criteria.</strong> **New proposal for OPS-30 — the one item of my thirteen that had no proposal of
its own.** (Everything below is re-measured today, 2026-10-04; nothing is carried
over from the earlier run unverified.)

**The row's title is now false in a good way.** "Off-site restic repository does
not exist" — it does exist, it decrypts with the production credential, it
verifies clean, and **this run establishes something the earlier proposals did
not: it has replicated to pCloud.**

```
$ stat -c '%d %i %n' /media/…/PCLOUD_STORAGE/ALWAYSON-BACKUPS \
                      /home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS
2049 5505025 /media/…/PCLOUD_STORAGE/ALWAYSON-BACKUPS
 218 211841 /home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS
```

Different device id (2049 local ext4 vs 218 pCloud FUSE) **and** different inode,
so these are two real trees. The FUSE mount is live (`pCloud.fs`), and the
replicated repository opens and checks clean from the pCloud side:

```
$ RESTIC_REPOSITORY=/home/scottw/pCloudDrive/PCLOUD_STORAGE/ALWAYSON-BACKUPS \
    restic check --read-data-subset=1/10
no errors were found
```

That is the meaningful upgrade: a copy that has actually left the machine, which
is what "off-site" is supposed to mean. My earlier proposals described the USB-disk
copy only and were careful to call it local-but-disjoint; that understated it.

**Honest limit on that claim.** This proves the files are present and restorable
through the pCloud mount. It does **not** independently prove the remote account
holds them — that needs a pCloud-side status query I did not run, and I am not
going to assert account state I did not measure. Read it as "off-site and
verifiable from the mount: proven", "uploaded to the account: supported, unconfirmed".

**Why it stays Open anyway.** The repository is real but it is not yet a backup:

- it holds **one** snapshot, `56bf1af5`, tagged `alwayson-offsite-proof`;
- that snapshot is **304 KiB / 103 files, `config` and `artifacts` only** — no
  `data/`, no `logs/`, no `backups/`;
- `grep -c 'ALWAYSON-BACKUPS\|offsite' restic-run.sh` → **0**, and the only
  restic timer is `ao-restic-prefetch.timer`. Nothing refreshes it.

So it is a verified proof of mechanism, not a maintained copy of anything that
would be lost with the host. **The acceptance criterion that actually matters is
not "create a repository" — it is "the off-host repository carries the same path
set as the nightly job".** That is a larger copy than the operator has approved
for automatic off-site transfer.

**One property worth stating because it is easy to over-credit:** the 1TB disk is
*removable, locally attached* media that happens to sit inside a synced folder.
When it is not attached, nothing is written and nothing detects that. The real
guarantee is "a copy exists and replicates when the disk is attached", not "a copy
is maintained". Only scheduling plus a liveness check upgrades it.

**Blocked on an operator decision, deliberately not taken.** Scheduling a recurring
privileged job that writes backup media into the live pCloud sync root touches
backup data and creates a recurring privileged action. I stopped rather than doing
it unasked. Enabling it, and approving the off-site path set, are both operator
calls.

Files changed: `agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md` (new §17.1.1.2; §17.1
device table now carries the pCloud row).

*Related, and a retraction to carry forward: see my revised `ops-a-OPS-29.md`.
I had wrongly reported `ALWAYSON-RESTIC2PCLOUD` as absent. It exists and is
empty, exactly as OPS-29 states. Do not merge that row away on my earlier say-so.*<br><br><strong>Evidence:</strong><br><code># The repository exists, opens with the production credential, and verifies:<br>$ set -a; . /run/user/1000/ao-restic.env; set +a<br>$ export RESTIC_REPOSITORY=/media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS<br>$ restic cat config<br>{ "version": 2,<br>  "id": "d22cddc074532b53bcea8ee739c3b7b7107d9fd3baa3224125d0e569fbfb94be",<br>  "chunker_polynomial": "33c903993a9dcf" }<br>$ restic snapshots<br>56bf1af5  2026-10-03 08:59:59  scottw-ms7b44  alwayson-offsite-proof<br>          /ALWAYSON/artifacts  304.564 KiB<br>          /ALWAYSON/config<br>1 snapshots<br>$ restic check --read-data-subset=1/10<br>no errors were found</code></td>
</tr>
<tr>
<td valign="top">OPS-31</td>
<td valign="top"><strong>The backup shares a filesystem with the data it protects</strong></td>
<td valign="top">ST-18</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§17.1</td>
<td valign="top">**Mitigated by the off-site repository, not closed. Measured by device id: <code>/ALWAYSON</code> and <code>/var/backups/alwayson-restic</code> are both device <code>66306</code>, so the local repository cannot survive loss of the root disk; the pCloud-rooted repository is device <code>2049</code>, different physical media. Because it is not yet scheduled, that copy is not yet maintained, so this stays open until off-site is enabled and holds consecutive snapshots. <code>ao-egress-archive</code> is not a substitute: §11.6 makes it a sale-transfer store with no restore duty.<br><br><strong>PROGRESS by 17-backup-restore-monitoring-and-completion-criteria.</strong> **Mitigated but still OPEN — this item is unclosable on evidence alone, and
that is the finding.** Measured by device id:

| Path | Device | Media |
|---|---|---|
| `/ALWAYSON` (the data) | 66306 | root disk |
| `/var/backups/alwayson-restic` (local repo) | **66306** | **same disk as the data** |
| `…/PCLOUD_STORAGE/ALWAYSON-BACKUPS` (off-site) | 2049 | separate media |

The local repository cannot survive loss of the root disk. The off-site
repository is on genuinely different physical media and verifies clean, so
**3-2-1 is now partially met** — copy two is still on the root disk, but a
host-disjoint copy exists. §17 previously claimed flatly "Nothing outside this
host currently holds a copy"; that is no longer true and has been corrected in
the section rather than left to drift.

**Why it stays open anyway.** A single unmaintained snapshot is not a copy. The
off-site repository holds exactly one snapshot, tagged
`alwayson-offsite-proof`, covering only `config` and `artifacts`; it is not
referenced by `restic-run.sh` and has no timer. Until it is scheduled and
holds a series, it mitigates total disk loss but does not satisfy "one
off-site copy" in the sense the policy intends.

`ao-egress-archive` is not a substitute and §17 says so explicitly: §11.6 makes
it a sale-transfer store with no restore duty.

**Blocked on an operator decision, deliberately not taken:** scheduling a
recurring privileged job that writes backup media into the live pCloud sync
root. That touches backup data and creates a recurring privileged action, so
I stopped rather than doing it unasked.

Files changed: `agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md` (§17 intro device-id
table and 3-2-1 status).<br><br><strong>Evidence:</strong><br><code># device ids re-measured — local repo and the data share one device:<br>$ for p in /ALWAYSON /var/backups/alwayson-restic \<br>    /media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS; do<br>    printf '%s -&gt; %s\n' "$p" "$(stat -c %d "$p")"; done<br>/ALWAYSON -&gt; 66306<br>/var/backups/alwayson-restic -&gt; 66306<br>/media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS -&gt; 2049</code></td>
</tr>
<tr>
<td valign="top">OPS-29</td>
<td valign="top"><strong>Off-site restic repository does not exist</strong></td>
<td valign="top">ST-18</td>
<td valign="top"><strong>Open</strong></td>
<td valign="top">§17.1, §11.6</td>
<td valign="top">The pCloud folder <code>ALWAYSON-RESTIC2PCLOUD</code> exists at the account root but is empty and nothing has been uploaded. Point the restic repository at it (rclone WebDAV or SFTP) so a second, host-disjoint copy exists. The repository is encrypted client-side, so pCloud holds ciphertext only, which stays inside the §11.6 boundary<br><br><strong>PROGRESS by 17-backup-restore-monitoring-and-completion-criteria.</strong> **This item contradicts OPS-30 in §19, and OPS-30 is the accurate one.** Both
are titled "Off-site restic repository does not exist". Measured this session:

- **OPS-30** says the operator chose
  `/media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE/ALWAYSON-BACKUPS`, that it is
  initialised and verifies, and that it is deliberately not scheduled.
- **OPS-29** says the pCloud folder `ALWAYSON-RESTIC2PCLOUD` exists at the
  account root but is empty, and prescribes rclone WebDAV or SFTP.

OPS-29's folder is **absent entirely** — `find . -maxdepth 1 -iname '*RESTIC*'`
returns only `./ALWAYSON-BACKUPS`. OPS-29 describes a location that no longer
exists as described, and its prescribed remedy (a second rclone remote and a
WebDAV credential) was explicitly superseded by the operator's choice of a path
inside the running pCloud sync root, which replicates with no rclone remote at
all.

**Recommended to the compiler:** OPS-29 should be merged into OPS-30 as a
duplicate rather than tracked separately, since tracking both implies two
independent off-site workstreams and one of them describes a path that does not
exist. I am not editing §19 to do this.

**What genuinely remains open, and it is what OPS-31 also waits on:** the
off-site repository holds exactly **one** snapshot, tagged
`alwayson-offsite-proof`, covering only `config` and `artifacts`. It is not
referenced by `restic-run.sh` (grep count 0) and has no timer. Until it is
scheduled it mitigates total disk loss but is not a maintained off-site copy,
and — per the device-id measurement in the OPS-31 proposal — the local
repository is still on the same disk as the data it protects.

**Enabling it is an operator decision** and was not done: it means a recurring
privileged job writing to backup media inside the pCloud sync root.

Files changed: `agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md` (§17 intro, device-id
table and 3-2-1 status).<br><br><strong>Evidence:</strong><br><code># OPS-29's stated remedy folder does not exist on the pCloud root:<br>$ cd /media/scottw/1TBSAMSUNGDATA/PCLOUD_STORAGE &amp;&amp; find . -maxdepth 1 -iname '*RESTIC*'<br>./ALWAYSON-BACKUPS<br># the folder OPS-29 names, ALWAYSON-RESTIC2PCLOUD, is ABSENT — not "present but empty"</code></td>
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

</table>

## 19.2 Completed items and verification evidence

Finished work, kept once with the evidence that closed it, followed by the standing
verification checks against the running system. Nothing listed here is outstanding.

<table>
<thead>
<tr>
<th align="left" width="7%">ID</th>
<th align="left" width="12%">Item</th>
<th align="left" width="9%">Component</th>
<th align="left" width="11%">Status</th>
<th align="left" width="8%">Standard served</th>
<th align="left" width="53%">Current state or acceptance criteria</th>
</tr>
</thead>
<tbody>
<tr>
<td valign="top">OPS-23</td>
<td valign="top"><strong>Roll-ups cannot be drilled into</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§12.5</td>
<td valign="top"><strong>CLOSED 12-host-installation-and-configuration.</strong> Every collapsed row now carries its `members` and renders them as a `&lt;details&gt;`
drill-down in Markdown, HTML and the PDF, with each member's own installed
version (`libc6 (2.42-1)`) rather than a bare name. §12.5.6 documents it.

The original failure was **silent**, which is why it survived: members were
computed and carried on the row as `members`, but the HTML renderer never
emitted them, so the drill-down existed in Markdown only and HTML/PDF quietly
lost it. Nothing errored; the document just stopped answering a question.
`TestRollupsCanBeDrilledInto` (7 tests) asserts the HTML path and that the
drill-down survives the print stylesheet, since a PDF that hides it reintroduces
the same dead end. Member names are HTML-escaped — they come from `.desktop`
files on disk.

**Two fixes that the first fix created.** Attaching members made the Markdown
~3× larger, but the roll-up renderer joined them into one table cell, so the
Ubuntu archive came out as a single **40,000-character line** — technically
"reachable", practically as useless as the original count. Package roll-ups now
render one member per row in their own collapsible block. And the two apt
roll-ups were still bare counts after the first pass; both now attach theirs.
The ROS train matters most: it is FROZEN, making "which 351 packages are
affected" the question an operator will actually ask. `rollup_details_md()` was
extracted from `render()` so this is unit-testable — `render()` spends hundreds
of apt round trips, which no test should pay to assert a formatting rule.

**What I got wrong, and the reason this took a second pass.** I verified this
item against the **tracked artifacts** rather than against a fresh render, and
they showed only 2 summaries and **0** drill-downs — which reads exactly like
"the fix does not work". The tracked `docs/software-status.md` and
`tmp/software-status.html` are dated 2026-10-03 20:53 while the generator landed
2026-10-04 10:30. The code was correct and the artifacts simply predated it. I
re-ran the generator into a scratch directory and every number in the section
reproduced exactly (4 summaries, 38 drill-downs).

**Left open, and it is a real gap:** the committed documents have **not** been
regenerated, so the shipped PDF still collapses the apt and ROS roll-ups to bare
counts. One `./scripts/build-update/refresh-install-log.sh` fixes it, but that
rewrites tracked documents and belongs to whoever owns the render cadence, not
to a validator change.<br><br><strong>Evidence:</strong><br><code>$ AO_ROOT=$PWD python3 scripts/build-update/provenance-log.py --offline \<br>      --out /tmp/ops23v/s.md --html /tmp/ops23v/s.html --plan /tmp/ops23v/p.json<br>$ grep -o '&lt;summary&gt;[^&lt;]*&lt;/summary&gt;' /tmp/ops23v/s.md<br>&lt;summary&gt;Rolled-up launchers — expand to list every application entry (153 entries across 34 groups)&lt;/summary&gt;<br>&lt;summary&gt;Ubuntu archive packages — expand to list all 3857 packages with their installed versions&lt;/summary&gt;<br>&lt;summary&gt;ROS 2 lyrical (whole train) — expand to list all 351 packages with their installed versions&lt;/summary&gt;<br>&lt;summary&gt;KDE Plasma Desktop — expand to list all 191 components&lt;/summary&gt;</code></td>
</tr>
<tr>
<td valign="top">OPS-20</td>
<td valign="top"><strong><code>apply-plan.py</code> dry-run validator</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§12.5</td>
<td valign="top"><strong>CLOSED 12-host-installation-and-configuration.</strong> `scripts/build-update/apply-plan.py` validates a plan without executing
anything, and prints what an updater *would* touch: eligible items, argv step
count, items that need a human, and the target set. Exit codes are `0`
well-formed, `2` usage, `3` validation failure, `4` hash mismatch. §12.5.4
documents it.

The `--expect-hash` flag is the part that makes it usable for approval. The
plan regenerates on every refresh and the `generated` timestamp alone changes
its bytes when no item changed, so **the file an operator approved is not the
file a tool would run**. `--expect-hash` refuses anything but the approved
bytes, and `TestVerbAllowlistAgreesAcrossFiles` asserts the verb allowlist is
identical in the validator and the generator.

**The trap, recorded because it cost real time and would mislead the next
agent.** The validator defaults `AO_ROOT` to `/ALWAYSON`, so running it from a
worktree silently validates **the live main-repo plan, not your worktree's**,
and prints a plausible result. A first run of mine reported 199 items and
schema 1 while the worktree plan held 224 items and schema 2. Always pass
`AO_ROOT=$PWD` and check the `plan :` line against the file you meant.

The same class of bug existed literally in `refresh-install-log.sh`, whose
summary-report heredoc opened a hardcoded
`/ALWAYSON/data/build-update/update-plan.json` while the surrounding script
honoured `AO_ROOT`; it now takes the path as `sys.argv[1]`.

**Still-open, and deliberately not done here:** the *live* `/ALWAYSON` plan is
still schema 1 (193 of 199 items carry no `manual` key), so the validator exits
**3** against it with 33 problems. Regenerating it is one
`./scripts/build-update/refresh-install-log.sh`, but that rewrites tracked
documents and is an operator action, not a silent side effect of a validation
change.<br><br><strong>Evidence:</strong><br><code>$ AO_ROOT=$PWD python3 scripts/build-update/apply-plan.py --no-snapshot<br>plan        : /tmp/ao-sessions/wt-ops-b/data/build-update/update-plan.json<br>sha256      : b753e5dab017df1be539b4b86e26713cc1293d9cde1c034ebb376f78aac9453f<br>generated   : 2026-10-04T16:55:20+00:00   schema: 2<br>items       : 224  -&gt; 0 eligible, 224 excluded<br>would run   : 0 argv steps across 0 item(s)<br>would touch: NOTHING - no item is eligible<br>EXECUTED    : nothing. This tool is a validator only.<br>validation  : OK</code></td>
</tr>
<tr>
<td valign="top">OPS-19</td>
<td valign="top"><strong>Update-plan steps are prose, not executable</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§12.5</td>
<td valign="top"><strong>CLOSED 12-host-installation-and-configuration.</strong> `update-plan.json` is now **schema 2**: every step is an argv **array**, never a
string, and prose is carried separately under `manual`. The `eligible` decision
is taken on the strength of `steps` alone, so "eligible" now means *a machine can
carry this out* rather than *no recorded rule forbids it*. `provenance-log.py`
§12.5.3 documents it.

Measured on this host: **0 eligible of 224**, with **0** steps that are not
argv arrays. `_argv_is_safe()` downgrades any argument carrying a shell
metacharacter to prose rather than emitting it, so a plan can never be run
through a shell and an item named `pkg; rm -rf /` produces no executable step.

**What I got wrong, which is the part worth reading.** The section as first
written claimed "`brave` remains genuinely automatable and is emitted as argv".
I checked it instead of repeating it, and it is **false as stated**. The
generator does emit `["snap","refresh","brave"]`, but the plan shows
`"steps": []` for `brave`, because the writer gates on the decision —
`"steps": steps if decision == "eligible" else []` — and `brave`'s verdict is
`?`, not `**NO**`: the snap channel was unreachable, so there is no evidence it
is behind. The two statements answer different questions. `brave` is the only
item whose *source* admits a mechanical step; it is not eligible **today**
because the evidence for updating it does not exist, not because it is
unautomatable. Had the section been left as written, the next reader would
have looked for that argv in the plan, not found it, and concluded the generator
had regressed. The section now states the correction explicitly.

**Consequence for the executor.** Because every item is currently excluded, the
plan publishes **no steps at all**, so nothing is safe to hand to an executor
yet. That is the truth of this host rather than a defect, and the validator
(OPS-20) reports it as such.<br><br><strong>Evidence:</strong><br><code>$ python3 -c "import json; p=json.load(open('data/build-update/update-plan.json')); ..."<br>schema 2 items 224<br>summary {'behind': 1, 'eligible': 0, 'excluded': 224}<br>steps non-list: 0</code></td>
</tr>
<tr>
<td valign="top">OPS-02</td>
<td valign="top">Version-matrix capture automation</td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§4.1 rule 9, §16</td>
<td valign="top"><strong>CLOSED 12-host-installation-and-configuration.</strong> New `scripts/validation/check-image-digests.sh` compares every digest in
`config/platform/version-matrix.yaml` against the digests the **deployed** units
actually carry, and reports drift. §12.5.5 documents it. It found real drift on
first run: **7 stale rows, 1 unpinned deployed image, 4 deployed digests absent
from the matrix.**

`capture-version-matrix.sh` did not and could not cover this: it `sed`-rewrites
five host facts (systemd, podman, netplan, nvidia) and never looks at an image
at all. I left it untouched and added a separate script.

**The check reads deployed units, not `quadlet/`** — deliberately. Quadlet
deploys flat, so `~/.config/containers/systemd/` holds copies; comparing against
the repository would report "no drift" at exactly the moment the live system had
drifted. The deployed unit is the only thing describing what is running.

**The check reports, it never rewrites.** Where a row disagrees with the live
system, deciding which side is right is an operator judgement — stale document,
unapproved deploy, or an unrecorded deliberate change. A script that adopted the
live digest would make the matrix self-fulfilling and launder a hand edit into
an apparently-captured fact. **The seven rows above are reported, not fixed.**
That is the deliberate part and the part most likely to look like incompleteness.
Resolving them is listed below.

**A bug the tests caught on the first run.** When every deployed image is
unpinned, the digest-extracting `grep` matches nothing and exits 1; under
`set -e` + `pipefail` that aborted the script with **status 1 and no output at
all**. A gate that fails without saying why is worse than no gate. Fixed by
tolerating the empty result in collection rather than by loosening `set -e`,
because the unpinned images are what the script most needs to report. The five
new tests drive the real script against a synthetic tree and assert exit codes,
so the OK path is exercised as carefully as the failing ones — a check only ever
seen failing proves nothing, since "7 rows drifted" is also what a broken
comparison prints.

### Open findings for the operator (need explicit approval — not actioned)

1. **7 stale matrix rows.** Decide per row whether the document or the live unit
   is right. The clearest: the matrix records
   `postgres@sha256:a65e6a84…` in two rows while all three deployed postgres
   units (`ao-fabrication-db`, `ao-mastodon-db`, `ao-sales-db`) run
   `sha256:d74eeac9…`. Also 4 deployed digests the matrix never mentions. **This
   needs operator approval** — correcting the matrix asserts the live state is
   intended, and correcting the units is a redeploy.
2. **`Image=localhost/gz-sim10-resolute:gui-svgfix` is not digest-pinned**, a
   live README §4.1 rule 9 violation. It is a local build, so pinning it means
   recording a build recipe and its reproducibility, not just editing a file.
   **Needs operator approval.**<br><br><strong>Evidence:</strong><br><code>$ AO_ROOT=$PWD bash scripts/validation/check-image-digests.sh --check<br>deployed units  : 21 in /home/scottw/.config/containers/systemd<br>distinct digests: 14<br>UNPINNED  Image=localhost/gz-sim10-resolute:gui-svgfix<br>DRIFT     mapping.broker_image_digest              sha256:91d0f7e8c748e...<br>DRIFT     simulation.gazebo_images                 sha256:0c19f326a339e...<br>DRIFT     simulation.image_foxglove_bridge         sha256:6d3461ddf0277...<br>DRIFT     sales.mastodon.image_postgres            sha256:a65e6a841f6c4...<br>DRIFT     sales.mastodon.image_redis               sha256:91d0f7e8c748e...<br>DRIFT     operations.image_postgres_shared         sha256:a65e6a841f6c4...<br>matrix digests matched a deployed unit  : 11<br>matrix digests matching nothing deployed: 7<br>deployed Image= lines without a digest  : 1<br>UNLISTED  deployed but absent from the matrix: sha256:d74eeac9a635...  (postgres, 3 units)<br>UNLISTED  deployed but absent from the matrix: sha256:c6eabf748fc7...  (redis, 2 units)<br>UNLISTED  deployed but absent from the matrix: sha256:9acc6d4df749...  (foxglove)<br>UNLISTED  deployed but absent from the matrix: sha256:55f8dbcf8dec...  (gz-sim10-server)<br>RESULT: DRIFT -- 7 stale matrix row(s), 1 unpinned deployed image(s).<br>$ echo $?<br>1</code></td>
</tr>
<tr>
<td valign="top">OPS-04</td>
<td valign="top">Restore-test script contract</td>
<td valign="top">ST-18</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§17.1</td>
<td valign="top"><strong>CLOSED 17-backup-restore-monitoring-and-completion-criteria.</strong> **Closed, and this proposal is late.** §17.1.1 has said "OPS-04 closed
2026-10-04" since commit `667e3f5`, but no proposal file was ever written — the
session was interrupted after editing the section and before writing the
proposal. The claim was in the section with nothing behind it, which is exactly
the state this single-writer arrangement exists to prevent. I re-derived the
evidence from the live host rather than trusting the section's own text.

The item asked the section either to state that the `check-*.sh` scripts implement
the seven-step restore test, or to acknowledge the requirement has no executor.
The answer is neither: it has an executor, and it is
`scripts/restore/restore-restic-drill.sh`. `grep -l 'restic' scripts/validation/*.sh`
returns nothing, so the validators are confirmed not to be the owners.

**What I checked in the section and got right**, because the section cites line
numbers and those rot: all seven `STEP` banners are still at the cited lines
(88, 95, 115, 121, 173, 181, 190), and the three refusals reproduce with exit 2
rather than the exit 1 recorded in the older OPS-10 proposal. That older figure
was wrong — exit 2 is the documented usage/refused code.

**The one deviation is recorded, not smoothed over.** §17.1 step 4 says "compare
hashes with stored manifests". There is no stored per-file manifest of the
backed-up set; the only `.sha256` files under `artifacts` are three upstream
Corda vendor checksums for jars and packages. The drill therefore compares the
restored tree against the **live** tree, which answers "did anything change since
the snapshot" rather than "does the snapshot match a recorded baseline". §17.1.1
says so explicitly. Creating a baseline manifest would be new backup behaviour
and is OPS-09's decision, not this item's.

This closes the *ownership* question only. The drill still has no cadence —
nothing schedules it, so §17.1's "Monthly" requirement is unmet, and that half
stays with OPS-24.

Files changed: `agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md` (§17.1.1 verified, no
substantive edit needed beyond the line-number recheck).<br><br><strong>Evidence:</strong><br><code># the requirement has an executor, and it is not a check-*.sh validator:<br>$ grep -l 'restic' scripts/validation/*.sh<br>NONE<br>$ ls scripts/restore/<br>restore-corda-test.sh  restore-mapping-artifact-test.sh  restore-restic-drill.sh<br>restore-sales-db-test.sh  restore-simulation-artifact-test.sh  verify-hashes-and-receipts.sh</code></td>
</tr>
<tr>
<td valign="top">FIELD-08</td>
<td valign="top"><strong><code>ao-fabrication</code> deployed with <code>a_fab</code></strong></td>
<td valign="top">ST-30</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§3.3.0, ES.1</td>
<td valign="top"><strong>CLOSED 03-high-level-architecture.</strong> **FIELD-08 closes on all four criteria, each measured.** The owning section is
`03-high-level-architecture` (§3.3.0), which I do not own — so I changed **nothing in my
own two section files** for this item. This proposal carries the evidence instead.

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | Domain on `10.89.12.0/24`, `Internal=true` | **met** | subnet + gateway + `internal: true`, `ao-fabrication-db` at `10.89.12.3/24` |
| 2 | Per-machine production data from ≥1 real machine into `a_fab` | **met** | 17 rows, all `printer-01`, a real Klipper machine at `10.42.0.96` |
| 3 | Separation from `ao-sim-fabrication` demonstrated | **met** | disjoint container sets, disjoint mounts, no `machine_production` in any sim container |
| 4 | `a_fab` registered in `network-cidrs.yaml` | **met** | `network-cidrs.yaml:12` |

Criterion 2 is the load-bearing one and it is satisfied with **actual rows**, not merely a
wired-up path. Criterion 3 is *demonstrated* three ways rather than asserted.

**Caveat the compiler must carry, not bury.** The data is **stale** — newest row is
2026-10-01 00:35 UTC and it is 2026-10-04 — and the collector is failing every pass because
`printer-01` is powered off. The item closes because the criterion is *"data pulled from at
least one individual machine"*, and 17 rows prove the pipeline works end to end; it does
**not** close because ingestion is healthy. The collector infrastructure itself is provably
alive: the timer is `enabled`/`active`, fires every ~5 minutes, and correctly isolates a
per-machine outage (`0 ok, 0 failed, 1 offline`) rather than failing the unit. **Please do
not render FIELD-08 as "ingestion currently working".**

**What I got wrong, and the reason.** My first pass ran `psql -U postgres` and got
`FATAL: role "postgres" does not exist`, and I was one step from treating that as "the
database is unreachable, FIELD-08 cannot be evidenced". Wrong twice over. The role name was
*my assumption* — the project's own convention is `POSTGRES_USER` from the container env
(§3.3.0: "a separate logical database with its own application role"; and
`fetch-kwallet-secret.sh:136` states explicitly that the role is `fabrication_role` while
`a_fab` is the database name). **Reason: I guessed a default credential instead of reading
the credential the deployment actually declares, and then let one command's error generalise
into a verdict on the entire item.** Reading `podman inspect --format '{{range
.Config.Env}}...'` first costs one command. Generalisable lesson for every session here: on
this project, take the credential from the container environment before concluding anything
about a database.<br><br><strong>Evidence:</strong><br><code># (3) separation from ao-sim-fabrication: disjoint networks, disjoint mounts, no sim data<br>$ podman network inspect ao-sim-fabrication --format '{{range .Containers}}{{.Name}} {{end}}'<br>ao-sim-fabrication-foxglove ao-sim-fabrication-gz<br>$ podman exec ao-fabrication-db psql -U fabrication_role -d a_fab -c '\dt'<br> public | machine_production | table | fabrication_role<br>$ podman exec ao-sim-fabrication-gz sh -c 'find / -maxdepth 3 -name "*machine_production*"'<br>(no output — simulation holds no production data)<br>$ podman inspect ao-sim-fabrication-gz --format '{{range .Mounts}}{{.Source}} -&gt; {{.Destination}}{{"\n"}}{{end}}'<br>/ALWAYSON/data/sim-fabrication/fuel -&gt; /gzfuel<br>/ALWAYSON/data/sim-fabrication/plugins -&gt; /gzplugins<br>/ALWAYSON/data/sim-fabrication/results -&gt; /results<br>/ALWAYSON/GAZEBO -&gt; /ALWAYSON/GAZEBO<br>/ALWAYSON/data/sim-fabrication/gzhome -&gt; /gzhome<br>$ podman inspect ao-fabrication-db --format '{{range .Mounts}}{{.Source}} -&gt; {{.Destination}}{{"\n"}}{{end}}'<br>/home/scottw/webodm/fabrication-dbdata -&gt; /var/lib/postgresql/data</code></td>
</tr>
<tr>
<td valign="top">OPS-25</td>
<td valign="top"><strong>Install the logrotate policy</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§16.3</td>
<td valign="top"><strong>CLOSED 17-backup-restore-monitoring-and-completion-criteria.</strong> Installed and confirmed by an observed rotation, not by an exit code.

Two things had to be fixed before the install would have worked. Two logs in
`operations/` — `pkexec-post-deploy.log` and `apply-20260831-fixes.log` — were
owned by root, so the `su scottw scottw` block could not rotate them. The first
attempt at fixing this gave them their own policy block, which was wrong: the
existing `operations/*.log` wildcard already matched them, so logrotate rejected
the whole file with `duplicate log entry for
/ALWAYSON/logs/operations/apply-20260831-fixes.log` and exit 1. That would have
made the daily timer fail. They are chowned to `scottw:scottw` instead; they are
the only two non-scottw logs under `/ALWAYSON/logs` and nothing needs them
root-owned. `find /ALWAYSON/logs -name '*.log' ! -user scottw` now returns 0.

The confirmation worth recording: an ordinary `logrotate -v` run returned
**exit 0 while rotating nothing** — it reported "log does not need rotating
(log has already been rotated)". Treating that exit code as proof would have
closed this item on a no-op. The forced run is the evidence: 13 rotated files
created, `agent-install.log` renumbered .2 through .16 against its 400-rotation
budget, and `audit.log` moved from inode 18219280 to 18223513 with the new file
created `scottw:scottw 0664`.

The policy uses `nocopytruncate`, which is only safe if writers reopen the file
per write. `ao_backup_run` and `ao_restore_test` in `scripts/lib/common.sh`
append with `&gt;&gt;` on every call and hold no descriptor, so a rename cannot
orphan a writer. Proved rather than assumed: after rotation, calling
`ao_backup_run` wrote into the new `backup.log` while `backup.log.1` stayed at
1247 bytes, so nothing was written into the rotated inode and lost.<br><br><strong>Evidence:</strong><br><code>$ ls -la /etc/logrotate.d/alwayson<br>-rw-r--r-- 1 root root 4588 Oct  4 00:16 /etc/logrotate.d/alwayson</code></td>
</tr>
<tr>
<td valign="top">OPS-34</td>
<td valign="top"><strong>Grafana reads SQLite through snapshots, never the live personal databases</strong></td>
<td valign="top">ST-19</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§6.A.2, §6.A.3, §4.3</td>
<td valign="top"><strong>CLOSED 17-backup-restore-monitoring-and-completion-criteria.</strong> Closed. The operator directive of 2026-10-03 — "Grafana must have a real SQLite
datasource", superseding the snapshot design — is implemented and verified in
the running container, not merely in the provisioning file.

Verified three ways, deliberately: the plugin directory lists
`frser-sqlite-datasource`; the unsign-plugin allow-list names that one id (not
`*`); Grafana's own HTTP API returns the datasource with
`"type":"frser-sqlite-datasource"` and `"status":"OK"` from `/health`; and the
container log shows nine `checkHealth ... status=ok` entries across the seven
provisioned stores (AO-SQLite, Elisa, MeshChatX observer, nPerf history, nPerf
settings, openclaw main, openclaw sitebot).

Note what did **not** change: the snapshot indirection described in
`config/platform/monitoring/grafana/provisioning/datasources/sqlite-snapshots.yml`
still stands, and it still holds. Every path points into `/var/lib/ao-sqlite`,
which is a read-only bind mount of `VACUUM INTO` output written by
`collect-system-health.py`, so Grafana still never opens a live store. A real
SQLite datasource means a real SQLite *driver*, not a live read of a WAL store.
Both measured reasons for the indirection survive: a WAL store cannot be read
through a read-only mount because SQLite must write the `-shm` index, and
`VACUUM INTO` output is delete-mode and opens cleanly read-only.

The unsigned-plugin caveat recorded earlier still applies and is unchanged:
`plugin.json` carries `signature: null` and Grafana refuses to load the plugin
without the allow-list entry. That is a standing supply-chain decision for the
operator, not an outstanding work item.<br><br><strong>Evidence:</strong><br><code>$ podman ps -a --format '{{.Names}} {{.Status}}' | grep -i grafana<br>ao-grafana Up 12 hours</code></td>
</tr>
<tr>
<td valign="top">PLAT-04</td>
<td valign="top">Asserting install verification</td>
<td valign="top">ST-01, ST-25</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§12.3</td>
<td valign="top"><strong>CLOSED 12-host-installation-and-configuration.</strong> §12.3's verify block now asserts. The old block is replaced by
`scripts/validation/verify-host-baseline.sh`, which exits non-zero on any
failure and names the check that failed.

The defect was that the block could not fail at all. Its cgroup line was
`test "$(stat -fc %T /sys/fs/cgroup)" = "cgroup2fs" &amp;&amp; echo ...`, which is
silent when the test fails; nothing read its return code; and the block's
overall exit status was 0 either way. Reproduced before the change: breaking
the cgroup check left the output unchanged and the script still exited 0.

Two details worth recording. It asserts the **value** of `Linger`, not merely
that the key exists, because without linger every container stops at logout.
And it reports `aa-enforce` as a WARN naming the cause rather than passing on
`aa-status` — `aa-status` ships in the base `apparmor` package and succeeds
even though no profile can be enforced on this host, since `apparmor-utils`
is not installed. That absence is recorded in §2.3 and installing it needs
operator approval, so it is surfaced, not silently passed.

Tested in both directions on purpose: a verifier that only ever passes would
be the same defect in new clothing. The failing case above is a genuine
negative control run with `stat` and `loginctl` stubbed, not a claim about a
host in that state.<br><br><strong>Evidence:</strong><br><code>$ bash scripts/validation/verify-host-baseline.sh ; echo "exit=$?"<br>=== ALWAYS ON host baseline verification (asserting) ===<br>  PASS  podman responds (5.7.0)<br>  PASS  systemd --user manager reachable<br>  PASS  linger enabled (survives logout)<br>  PASS  cgroup v2 unified hierarchy<br>  PASS  aa-status present<br>  WARN  aa-enforce MISSING - apparmor-utils not installed, so no profile can be<br>  WARN    enforced or inspected. §2.3 records this; install needs operator approval.<br>--- 5 passed, 0 failed ---<br>RESULT: PASS<br>exit=0</code></td>
</tr>
<tr>
<td valign="top">SIM-14</td>
<td valign="top"><strong>RL objects are a catalogue, not world entities</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§10.2.1, §19.1 SIM-05</td>
<td valign="top"><strong>CLOSED 10-simulation-architecture.</strong> §19.1 records SIM-14 as absent ("That model does not exist"). It exists. The nine
catalogue entries in `GAZEBO/sim/objects.yaml` are generated into the committed
`factory.world` as a non-static `rl_objects` model with nine links, and the running
server reports those links through the portal. The separation the item is really
concerned with -- RL entities held apart from the static `factory_assets` so a
training run can vary count and placement without rebuilding the world -- is
implemented by making the model non-static.

§10.3 in my section file now records the measurement instead of the §19 assertion.

**Closing this does not mean the generator is sound, and I found a real defect
while verifying it.** `build-rl-objects.py --check` exits 1 against the committed
world. Two separate causes, both reproduced on a copy under `/tmp/gen-test`:

1. The committed block carries `&lt;specular&gt;` and `&lt;shininess&gt;` on all nine
   materials, added by commit `fa3f8f6` ("material shininess"), which the
   generator was never taught to emit. Nine material lines differ.
2. `--write` strips the existing block and re-appends before `&lt;/world&gt;`, so the
   model moves from line 623 to the end of the file -- after `safety_zones` and
   `conveyor_loops`. Regeneration is not idempotent in position even once cause 1
   is settled.

Neither is a §19 item, so I have left both open rather than renumbering into a
group I do not own. Cause 2 is the more dangerous of the two: a routine refresh
silently reorders three generated models in the world that the live server has
open. That belongs in a new SIM item.

**What I got wrong.** I ran `--write` against `/ALWAYSON` before I had copied the
tree to a scratch directory. That modified the shared live tree, which is exactly
the interference I am supposed to avoid; I caught it in the diff (149 insertions,
147 deletions, the rl_objects block relocated) and restored with
`git checkout -- GAZEBO/worlds/factory.world`, after which
`git status --short -- GAZEBO/ scripts/ quadlet/` printed nothing and the file
sha256 returned to `bce32f2a7ff035b4022db82d9a90267ca829261d08038d3e26e5ff3fe5f51053`.
I caused the fault, so I reverted only my own edit -- but the sequence was wrong,
and the diff is what caught it rather than my checking first.<br><br><strong>Evidence:</strong><br><code>§19.1 recorded this item as absent ("That model does not exist"). The model<br>exists in the world as live links. Measured 2026-10-03.</code></td>
</tr>
<tr>
<td valign="top">SIM-13</td>
<td valign="top"><strong>Safety-zone and interlock model absent</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§10.2</td>
<td valign="top"><strong>CLOSED 10-simulation-architecture.</strong> §19.1 was wrong on this item and the correction matters more than the closure. It
records SIM-13 as absent with the sentence "nothing in the repo implements one";
`GAZEBO/sim/safety_zones.yaml`, `scripts/simulation/verify_safety_zones.py` and
the portal's `/api/safety-zones` endpoint have all existed and been serving since
before this session began.

I have added §10.3 to my section file. It states what was measured rather than
what is claimed: four zones resolved with computed boxes, three interlocks
declared and all of them reporting-only, and the two unresolved machine datums
named in the open rather than buried. The "rehearsal only, actuates nothing"
boundary is recorded in the README in the same words the tool prints, because a
reader scanning §10 could otherwise mistake a zone model for an enforced one.

Two points I deliberately did **not** close. The `printer-01` and `cnc-01` gaps
are real and remain open — they need operator-supplied datums, which is not mine
to invent. And no interlock is enforced anywhere, so closing this item must not be
read as "the simulation has working safety interlocks"; it means the model exists,
resolves, and is honest about not enforcing.

**What I got wrong.** I spent this session assuming §19 was a reliable index and
only checked it against the running system at the end. Checking first would have
found that two of my fourteen items were already delivered, and that the manifest
drift had grown well past the size §19 recorded.<br><br><strong>Evidence:</strong><br><code>§19.1 recorded this item as absent ("nothing in the repo implements one"). It is<br>present, running, and served by the portal. Measured 2026-10-03.</code></td>
</tr>
<tr>
<td valign="top">SIM-09</td>
<td valign="top"><strong><code>elev_arms</code> framing uses the boned datum, not the as-built arms</strong></td>
<td valign="top">ST-08</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§10.2.1</td>
<td valign="top"><strong>CLOSED 10-simulation-architecture.</strong> §19.1 lists SIM-09 as outstanding ("elev_arms framing uses the boned datum, not
the as-built arms"). That was fixed on 2026-10-02 in commit `365bd42`, before this
session began, and I am closing it on that basis rather than on new work.

The fix had two halves. The boned datum itself was corrected: `cell-arms` origin
moved from `6.401314` to `5.981314` because the stored value was the mesh centre
in x/y while the field is documented as the min corner, so it was displaced by
exactly half the extent. And all four arm cameras were re-aimed at the true
as-built centroid. A line-of-sight checker was added against the world collision
boxes and azimuth x distance swept for vantages with clear line of sight and the
whole measured AABB in frame; the arms cell admits only a 65-115 degree azimuth
band.

I verified the arithmetic rather than trusting the commit message: origin plus
half of extent reproduces the centroid `6.401314, 2.6978645, 1.150797` to the
precision the datum carries, which is the invariant that makes the datum and the
cameras unable to disagree.

§10.3 in my section file records the corrected datum and the `elev_arms` pose.

**What I got wrong.** I opened this item expecting the datum/camera disagreement to
still be live and had drafted a note describing it as an unfixed inconsistency
before reading the commit history. The fix predates my session. I should have run
`git log -S` on the datum values before writing anything about them -- that one
command would have told me the item was already closed.<br><br><strong>Evidence:</strong><br><code>§19.1 records this as outstanding. It was fixed in commit 365bd4277d310c4bda616015766b45e5f49a04b8.<br>Verified against the committed tree 2026-10-03.</code></td>
</tr>
<tr>
<td valign="top">SEC-03</td>
<td valign="top"><strong>Documented credential rotation, revocation and recovery</strong></td>
<td valign="top">ST-24</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§14.1.1</td>
<td valign="top"><strong>CLOSED 14-secrets-and-service-identity.</strong> Added §14.2 covering all four things §14.1.1 required and none of which were
documented anywhere:

- **§14.2.1 Rotation** — 4-step table. The load-bearing rule: rotate in the
  wallet and restart the unit, never edit the env file (it is overwritten at the
  next start) and never re-run `genenv` (would mint new SECRET_KEY_BASE /
  OTP_SECRET and invalidate every session). Includes the `pg_hba` 127.0.0.1-trust
  trap: verify a changed role password over TCP, not the socket.
- **§14.2.2 Revocation** — per-credential. Wallet entry overwrite; Doorkeeper
  `revoked_at` sweep for the bridge token; SECRET_KEY_BASE as a deliberate
  session-invalidating action; and the note that revocation is incomplete until
  the old value is out of backups too.
- **§14.2.3 Expiration** — none enforced; the `expires_in: nil` bridge token is
  a standing rotation obligation, not a solved problem.
- **§14.2.4 Wallet backup and restore** — the gap above, plus an interactive
  restore procedure whose fallback is rotation (ALTER ROLE / re-mint / put),
  never recovering an old value.
- **§14.2.5 Break-glass order** — 4 steps, first three non-destructive, fourth
  (rotate a live credential) reserved to the operator. Names the failure mode to
  avoid: adding a compensating `Environment=` line to a unit to work around a
  missing fetch, which turns a transient locked wallet into a permanent
  plaintext secret in a tracked file.

I also noted that `docs/runbooks/secrets.md` is stale — it describes
per-service-account homes and a manual copy-out step, both superseded by §13.2
and the wallet flow — and marked §14.2 as authoritative over it. **I did not
edit that runbook**: it is not my file, and correcting it is a separate call.

What I got wrong: my first attempt to confirm `POSTGRES_PASSWORD_FILE` support
used `find / -maxdepth 3`, which missed `/usr/local/bin/docker-entrypoint.sh`
(depth 4) and made me briefly believe the image did not honour it. A later
`-maxdepth 1`-style search on `/` found it. The conclusion was unchanged, but
the first measurement was wrong — when a `find` returns nothing, verify the depth
before concluding the file is absent.<br><br><strong>Evidence:</strong><br><code>$ grep -rln -i 'break-glass\|rotation\|revocation' --include='*.md' agents/COORDINATION (README UPDATES) (README UPDATES)/16*/section.md agents/COORDINATION (README UPDATES) (README UPDATES)/17*/section.md<br>(no match in §16/§17; only "Rotation: /etc/logrotate.d/" — logs, not credentials)</code></td>
</tr>
<tr>
<td valign="top">PLAT-03</td>
<td valign="top"><code>apparmor-utils</code> and GPU toolkit packages</td>
<td valign="top">ST-01, ST-25</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§12.3</td>
<td valign="top"><strong>CLOSED 02-platform-baseline.</strong> **`apparmor-utils` is genuinely missing, and it is a real gap rather than a cosmetic one.**
§12.3's verify block runs `aa-status`, and §4.1's AppArmor policy work depends on `aa-enforce`,
`aa-complain`, `aa-decode`, `aa-logprof` and `aa-genprof`. Measured: only `aa-status` exists, and
`dpkg -S` shows it ships in the **base `apparmor` package**, not in `apparmor-utils` — which is
`Installed: (none)`. All five profile tools are `MISSING`.

So §12.3's verification passes today by coincidence: the one binary it calls happens to be
provided by a package that is not the one named for the feature. On a freshly provisioned host
nothing breaks *today*, but the first assertion that touches a profile will fail, and the
profiling workflow has no tooling at all.

**Confirmed the gap is real, in both install lists.** Neither
`scripts/bootstrap/02-install-host-dependencies.sh` (line 6) nor
`scripts/bootstrap/ao-bootstrap-privileged.sh` (lines 44–64) names `apparmor-utils`, and
`scripts/provision/provision.sh` never mentions apparmor. That is why the package is absent on a
host whose own bootstrap chain would not install it.

**Why this item closes anyway.** The requirement is now written down where it belongs — new
**§2.3** of my section, "Packages the Verification Steps Depend On", naming `apparmor-utils`
against the tools §4.1 needs and recording the installed state of `nvidia-container-toolkit`.
PLAT-03 asks for the gap to be identified; identification is the deliverable.

**Not done — needs another group.** Adding the package to the install lists means editing
§12.3 and `scripts/bootstrap/02`, both owned by OPS-B. Also recorded: the version matrix's
`nvidia-container-toolkit 1.20.0` row is wrong (actually `1.20.1-1`) — noted in §2.3, matrix
file not mine to edit.

**One thing I got wrong.** I first assumed the install lists were stale copies of a longer
original and that §12.3 held the full list. Both lists are genuinely complete-as-written for
their scope; the defect is that `apparmor-utils` was never in either. I got it wrong by
assuming drift rather than checking the actual package arrays with `sed -n`.<br><br><strong>Evidence:</strong><br><code>$ dpkg -S /usr/sbin/aa-status<br>apparmor: /usr/sbin/aa-status<br>$ apt-cache policy apparmor-utils | head -2<br>  Installed: (none)<br>$ for b in aa-status aa-enforce aa-complain aa-decode aa-logprof aa-genprof; do printf '%-11s %s\n' "$b" "$(command -v $b || echo MISSING)"; done<br>aa-status    /usr/sbin/aa-status<br>aa-enforce   MISSING<br>aa-complain  MISSING<br>aa-decode    MISSING<br>aa-logprof   MISSING<br>aa-genprof   MISSING</code></td>
</tr>
<tr>
<td valign="top">PLAT-01</td>
<td valign="top"><strong>Mapping runtime designation</strong></td>
<td valign="top">ST-03</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§13.2</td>
<td valign="top"><strong>CLOSED 13-podman-runtime-and-quadlet-policy.</strong> §13.2 now opens with an explicit designation — **rootless, single-store, under `scottw`
(uid 1000)** — followed by a seven-row table of the measurements above, so the designation is
re-derivable rather than asserted. The old text said only that every container "runs rootless
under the operator account" without naming the account or the store, and its rules forbade the
per-service model without saying whether it was actually present.

New **§13.2.1** records the deviation that kept this item open: the three per-service accounts
(`ao-sales` 993, `ao-ledger` 994, `ao-mapping` 997) and
`/etc/systemd/system/ao-podman-bridge.service` still exist on the host. They hold no store, no
socket and no process, so they do not make the runtime mixed. **This corrects §19.2**, whose
"Verified; mixed-store deviation documented" row described a deviation that does not exist.

**Two things I got wrong, and why.**

1. **I could not enumerate the rootful store, so I did not claim it is empty.**
   `/var/lib/containers/storage` exists and its `db.sql` was written 2026-09-30, so something
   has used it. `sudo` on this host requires interactive authentication, so
   `sudo ls /var/lib/containers/storage/overlay-images/` returned `Permission denied`. §13.2
   therefore says the system store is *"unused by any workload"*, **not** *"empty"* — different
   claims, and only the first is proven. **OPEN for the operator:** one `sudo` command settles
   it. I did not request escalation; a non-interactive agent cannot answer it, and guessing
   would have been worse than saying so.
2. **§13.2 and §19.2 contradicted each other, and I initially treated §13.2 as the correct
   side.** `OPS-14` asserts a mixed-store deviation is recorded in §19.2; I searched §19.2 for
   that record and found only a one-line summary with no measurement behind it. I got this
   wrong by assuming the more detailed document was authoritative. The measurement settled it:
   `loginctl` and `ps` show nothing runs under those accounts, so there is no mixed store to
   record.

**Not done, deliberately.** The three accounts and the disabled unit are left in place —
deleting a user or a unit file needs explicit operator approval (README §4.1 rule 3). Reported,
not executed.

**Cross-group.** `OPS-14` asks for this same reconciliation and can close on §13.2.1, but
§19.1 is not mine to edit — the compiler merges that row.<br><br><strong>Evidence:</strong><br><code>$ podman info --format '{{.Host.Security.Rootless}}'<br>true<br>$ podman info --format '{{.Store.GraphRoot}} | {{.Store.RunRoot}}'<br>/home/scottw/.local/share/containers/storage | /run/user/1000/containers</code></td>
</tr>
<tr>
<td valign="top">PAY-07</td>
<td valign="top"><strong>Reconcile the payment-provider decision</strong></td>
<td valign="top">ST-12, ST-27</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§7.2, §7.3</td>
<td valign="top"><strong>CLOSED 07-public-storefront-and-payment-policy.</strong> §7.2 now states in one normative place that the provider set — PayPal, Zelle and
Coinbase/USDC — **is decided and closed as a policy question**. It explicitly
reconciles the two stale references rather than leaving them to contradict it:
ES.2's "deployable once the provider decision is recorded (§7.2)" and ST-27's
"open on payment-provider selection" both refer to the *implementation* being
gated, not to the choice being unmade. §7.2 also states plainly that choosing the
providers never authorised accepting a payment — §4.1 rule 14 still applies and
ST-12 remains the gate.

I did **not** edit ES.2 or ST-27 (§00 and §19 are not mine). The reconciliation
is achieved by making §7.2 the single authority and naming the stale wording, so
the compiler session can update the other two in one pass if it wants the mirror.

Two things I got wrong:

1. **I initially treated a `Section 18.4` reference in my own file as a live
   cross-reference and went looking for a section 18.** There is no section 18.
   `MANIFEST.md` has no `18-*` entry and `git log --diff-filter=D` finds no deleted
   18 directory, so this was never a renumbering casualty — it is a dangling
   reference to a section that does not exist in the compiled document. I
   repointed it at §7.2, which is where the Zelle/Coinbase content actually lives.

2. **I nearly accepted ST-12's wording that the adapter "runs with no DSN" because
   §19 said so, and only checked because the Quadlet's own comment predicted the
   opposite.** The container env disagreed with §19 immediately. A row in §19
   describing live runtime state is a hypothesis; the running container is the
   measurement. I should have run `podman inspect` before reading anything else.

3. **My first pass at this finding reported "70 dangling `Section 18.x` references
   across 21 files" and named `quadlet/networks/*.network`,
   `config/platform/topology-model.yaml`, `config/platform/version-matrix.yaml`,
   the Grafana dashboard JSON and `docs/compliance/*.md`. That was wrong — I
   estimated the sweep from memory instead of running the count, then listed
   plausible-sounding paths I had never grepped.** Re-measured on 2026-10-03:

       $ grep -rn 'Section 18' . --exclude-dir=.git \
             --exclude-dir='README - ARCHIVE' --exclude-dir=proposals
       ./scripts/payment/ao-payment-adapter.py:11:Controls enforced here (Section 18.4):
       ./scripts/payment/ao-payment-adapter.py:42:# deliberately absent: Section 18.4 forbids automated Zelle verification.
       ./scripts/payment/ao-payment-adapter.py:215:            # Refuse to treat any inbound POST as Zelle evidence. Section 18.4:
       ./scripts/payment/ao-payment-adapter.py:217:            self._reply(501, {"error": "Zelle is manual-reconciliation only (Section 18.4)"})
       ./quadlet/payment/ao-ingress-payment.container:15:# Written but NEVER enabled ... Section 18.4
       ./docs/runbooks/mastodon.md:115:  the loopback-only `RAILS_FORCE_SSL=false` exception is retired (Section 18.5).
       ./docs/runbooks/mastodon-validation.md:73:   loopback SSL deviation is now retired (Section 18.5) — use the
       ./config/sales/migrate/02-payment-reconciliation.sql:11:-- no other table changes. Section 18.4 requires Zelle reconciliation to be

   The true figure is **9 occurrences across 5 live files** (31 across 10 files if
   the `README - ARCHIVE` tree is counted). No network unit file, topology model,
   version matrix, Grafana dashboard or compliance doc contains one — that detail
   was fabricated on my part and I withdraw it.

   The live finding stands, and it is the part worth acting on:
   `ao-payment-adapter.py` quotes "Section 18.4" **to a client in an HTTP 501
   body** (line 217), so a real caller is directed to a section that does not
   exist, and line 11 presents a non-existent section as the authority for the
   controls in force. **Recommend OPS or the compiler own the sweep**, repointing
   the payment references at §7.2, where that content now lives. I fixed only the
   reference in my own file: the adapter's string is emitted in operator-facing
   output, so repointing it is a live-behaviour edit rather than a documentation
   edit, and it is not mine to make unilaterally.<br><br><strong>Evidence:</strong><br><code>$ grep -c '| \`18' agents/COORDINATION (README UPDATES) (README UPDATES)/MANIFEST.md<br>0</code></td>
</tr>
<tr>
<td valign="top">PAY-04</td>
<td valign="top"><code>salesdb</code> schema initialization</td>
<td valign="top">ST-11, ST-12</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§3.3.1, §15.1</td>
<td valign="top"><strong>CLOSED 07-public-storefront-and-payment-policy.</strong> **PAY-04's acceptance criterion is met and I recommend closing it.** "Live
application schema initialized; read-only reporting views defined" — both halves
are measured true against the running database, not asserted.

§7.3.1 now records the state: 18 base tables (the 14 core tables of §15.1 plus
`correlation_records`, `sale_contracts`, `sale_contract_lines`, `sale_evidence`),
5 reporting views, and the least-privilege reporting boundary — `sales_reporting_role`
has `SELECT` on exactly the five views and on **zero** base tables, which is the
§6 separation the architecture requires.

What I got wrong:

1. **My first two psql attempts failed and I misread why.** I sourced
   `sales-db.env` and exported `PGUSER`, but the shell already had `PGUSER=scottw`
   from the environment and the error was `password authentication failed for user
   "scottw"` — not a missing-variable error, so the obvious cause was wrong. Two
   things bit me: `sales-db.env` has no `POSTGRES_USER` key (I assumed it did),
   and an inherited `PGUSER` beats nothing. The fix was to set `PGUSER` explicitly
   in the same command rather than trusting the sourced file to be complete.
2. **No writes were issued against `salesdb` at any point in this session.** Every
   statement was a `SELECT` against `information_schema`. I deliberately did not
   run the migration files to "make sure" they applied — the database was already
   live and re-running `config/sales/init/*.sql` would be an unapproved write to
   production data for no informational gain.

Scope note for the compiler: PAY-03's *stated criterion* is met and proven, but
its *title* names a Sales API that does not exist. I propose closing PAY-03 on its
criterion and raising a separate new PAY item for the missing API, rather than
holding PAY-03 open against a criterion it already passes. See `pay-PAY-03.md`.

Not done, and deliberately: PAY-04 is closed, but **PAY-03 is not**, and they are
adjacent. The schema is initialized and the reporting views are correct, but the
service that would *use* them does not exist — see `pay-PAY-03.md`.<br><br><strong>Evidence:</strong><br><code>$ psql -h 127.0.0.1 -p 15432 -d salesdb -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY 1;"<br>       table_name<br>-----------------------<br> audit_events<br> correlation_records<br> customer_contacts<br> customers<br> entitlements<br> fulfillment_events<br> order_lines<br> orders<br> payment_provider_events<br> payment_references<br> product_versions<br> products<br> receipts<br> returns<br> sale_contract_lines<br> sale_contracts<br> sale_evidence<br> support_cases<br>(18 rows)</code></td>
</tr>
<tr>
<td valign="top">PAY-03</td>
<td valign="top">Sales API and receipt/fulfillment workflow</td>
<td valign="top">ST-11, ST-12</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§7.3, §15.1</td>
<td valign="top"><strong>CLOSED 07-public-storefront-and-payment-policy.</strong> **PAY-03's stated acceptance criterion is met and proven: "A sales receipt manifest
can be generated without exposing sensitive data."** Closing on that criterion.

Evidence chain, all read-only against a scratch receipt in `/tmp`: the receipt
passes structural validation (exit 0); the *same* receipt with a `card_number`
field is rejected with exit 13, so the sensitive-field gate is enforced rather
than documented; `build-manifest.sh` emits a 14-field manifest containing no
customer, SKU, serial or card token and whose `content_hash_sha256` matches
`sha256(receipt)`; `sign-manifest.sh` attaches an Ed25519 signature that verifies
(`Signature Verified Successfully`). Nothing was submitted anywhere —
`submit-ledger-event.sh` exits 3 at staging because the gateway is undeployed.

§7.3.1 now records this, plus a **trap I found while proving it**: the signature
is over the *pre-signing* digest, so verifying against the final manifest fails
with `Signature Verification Failure`. No in-tree verifier accounts for this and no
`verify-manifest` script exists. The ingest-side verifier must hash the manifest
with `signature` and `producer_key_id` removed, or it will reject every validly
signed manifest. Recorded in §7.3.1 so the next builder cannot miss it.

**Scope I did not close, and want the compiler to see.** PAY-03's *title* is
"Sales API and receipt/fulfillment workflow". The receipt/manifest half is real and
proven. The **Sales API does not exist** — no Quadlet unit, script or config
anywhere in the tree implements one; the only `ao-sales` containers are
`ao-sales-db` and §15.3's five Mastodon containers, and `ao-sales` is a network,
not an application. So nothing in the current build can turn a verified payment
event into an order/receipt/entitlement record. I am **not** closing that gap by
silence: §7.3.1 states it as OPEN, and I propose a new item.

What I got wrong:

1. **I wrote "Ed25519 signing works" into §7.3.1 on the strength of the earlier
   session summary, before I had run it.** This session ran it, and the naive
   verification *failed*. My first conclusion — that the signing chain was broken —
   was also wrong: I had hashed the post-signing file. The real answer required
   reading `sign-manifest.sh` line by line to see the digest is taken before the
   `jq` mutation. Both halves of that were mistakes; recording them because
   "signing works" and "verification works" looked identical until the last command.
2. **I used a throwaway `/tmp` Ed25519 key rather than a wallet key, deliberately.**
   `sign-manifest.sh` only accepts `wallet:ao-sim-vehicle` or
   `wallet:ao-sim-fabrication`. I did **not** use those, because a *simulation*
   producer key must never sign a real sale receipt — that would put a sim identity
   into receipt provenance. I also did not create any new wallet entry. The
   throwaway key was shredded. The consequence to note: **the sales producer key
   does not exist in the wallet at all** (`ao-ledger hasFolder= False`), so
   production receipt signing is blocked on an operator-created key. I did not
   create the key; creating signing credentials is the operator's call.<br><br><strong>Evidence:</strong><br><code>$ ./scripts/validation/validate-sale-receipt.sh /tmp/paydemo/receipt.json<br>OK: structural receipt validation passed: /tmp/paydemo/receipt.json<br>exit=0</code></td>
</tr>
<tr>
<td valign="top">OPS-22</td>
<td valign="top"><strong>No regression tests for the inventory generator</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§12.5</td>
<td valign="top"><strong>CLOSED 12-host-installation-and-configuration.</strong> `scripts/build-update/test_generators.py` holds **29 passing tests** covering the
three defects the item names, plus defects found while writing them. §12.5.2
documents the suite.

The item's proposed two assertions ("every pull step carries a 64-character
digest", "no step embeds a not-a-value marker") are both present, and the suite
caught a **fourth defect the item did not mention**:

`update_steps()` validated a digest by checking only the `sha256:` prefix.
`sha256:` plus 12 hex characters passes that test, so
`podman pull repo@sha256:&lt;12&gt;` was emitted — a command that reads as correct and
is rejected by any registry with HTTP 400. Length is part of what makes a digest
reference valid, so `is_complete_digest()` now checks algorithm *and* body length.

The three defects named in the item are covered by
`test_truncated_digest_produces_no_step`, `test_prose_error_string_produces_no_step`,
`test_every_pull_step_across_shapes_has_full_hex`,
`test_no_pull_step_embeds_a_not_a_value_marker`,
`test_desktop_app_uses_owning_package`,
`test_display_name_never_reaches_the_command`.

**Repairing the harness was a prerequisite, not a detail.** The file did not run
at all: a stray fragment of a previous test hung off the end of the file *after*
`unittest.main()`, so the block was dead code that never executed, and its four
tests errored. The `TestAptHistoryParsing` fixture called `importlib.reload()` on
a module that was never in `sys.modules`, raising `ImportError` for every test in
that class. The parser now takes an injectable `log_dir`, so the fixture uses a
`tempfile.mkdtemp()` directory instead — the test never touches `/var/log/apt`,
which matters because the real log is system state.

Run the suite after any change to the generators. It is fast enough not to be an
excuse (0.27 s) and it is the only thing standing between the next defect and a
plausible-looking document.<br><br><strong>Evidence:</strong><br><code>$ python3 scripts/build-update/test_generators.py<br>...<br>Ran 29 tests in 0.266s</code></td>
</tr>
<tr>
<td valign="top">OPS-21</td>
<td valign="top"><strong>Install dates are inferred, not recorded</strong></td>
<td valign="top">ST-01</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§12.5</td>
<td valign="top"><strong>CLOSED 12-host-installation-and-configuration.</strong> The `Installed` column is now ground truth from `/var/log/apt/history.log`, parsed
by the new `scripts/build-update/apt_history.py`. §12.5.1 documents it.

**The item text was wrong about one number.** It said the log "holds 13 dated
transactions". Measured across `history.log` plus both rotated siblings it holds
**186** transactions, indexing **4,445** distinct packages — 4,281 installed,
86 known only as upgrades from before the retained window, 2,098 installed
unattended. The 13 figure is the count in the *live* `history.log` alone, which
is only the newest slice. Anyone reading that item and checking one file would
have concluded the parser was broken.

dpkg's `.list` mtime cannot distinguish install from upgrade because dpkg
rewrites that file on every unpack. apt's log separates them by keyword, so the
column now also distinguishes an unattended upgrade from an operator-initiated
one (`Commandline` inspection) and a purge from an install.

Two honest limits are recorded rather than hidden: coverage is bounded by apt's
own log retention, so absence means *unknown* and never *not installed*; and a
purged package returns `(None, record)` so the cell can read
`not installed (removed/purged &lt;date&gt;)` instead of printing an install date for
software `dpkg -l` no longer lists. `nginx` is the live example — the :8765
portal is a host python3 process now.

**A silent failure was found while verifying this and is the most important
finding in the batch.** The first implementation used a bare `import apt_history`,
which resolves against `sys.path` — and `sys.path[0]` is the *current working
directory*, not the script's directory. `refresh-install-log.sh` runs
`cd "$AO_ROOT"` before invoking the generator, so the import raised `ImportError`
on every production run and fell back to the dpkg mtime. The output looked
completely normal and carried the older, less accurate dates. The module is now
loaded by `__file__`; the CWD-independence is asserted by
`test_apt_history_loads_regardless_of_working_directory`, which runs the
generator as a subprocess with `cwd=/tmp`. Verified above: the label now reads
`(apt history, Install)` from outside the script directory.

Note for the next agent: **do not trust a fallback path that degrades silently.**
Had the fallback logged a warning, this would have been caught on day one.<br><br><strong>Evidence:</strong><br><code>$ python3 scripts/build-update/apt_history.py<br>packages indexed      : 4445<br>  installed           : 4281<br>  upgrade-only (pre-window): 86<br>  installed unattended: 2098<br>log files read        : ['history.log.1.gz', 'history.log.2.gz', 'history.log']</code></td>
</tr>
<tr>
<td valign="top">OPS-03</td>
<td valign="top">Scripts layout completeness</td>
<td valign="top">ST-01, ST-25</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§16.1</td>
<td valign="top"><strong>CLOSED 16-scripts-and-operational-standards.</strong> §16.1 now carries **§16.1.2** naming `scripts/sales/` and
`scripts/validation/validate-sale-receipt.sh` as they actually are.

**The item's premise was a stale measurement, and it is retracted.** Both paths
exist and hold the expected content: `sales/` has seven scripts and
`validate-sale-receipt.sh` is present and executable. The "missing" report
predates the scripts landing — `validate-sale-receipt.sh` was written on
2026-10-03 at 18:48, which is after the report was filed. The correct action was
neither "add" nor "repoint" but to re-measure and retract.

The full measured layout of all eighteen `scripts/` subdirectories is now in
§16.1.2 so the next reader does not re-derive it: `bootstrap` 7, `deploy` 6,
`validation` 11, `mapping` 5, `radio` 4, `simulation` 15, `storefront` 4,
`ledger` 4, `backup` 9, `restore` 5, `maintenance` 5, `mastodon` 10,
`operations` 21, `ops` 8, `openclaw` 1, `payment` 3, `sales` 7, `lib` 1, plus
one top-level file `sync-lmstudio-readme-preset.sh`.

Worth flagging to the compiler: the section previously listed directories as
empty while other sections referenced files inside them. That is the failure
mode OPS-03 was created to catch, and it recurs whenever a document is written
from intent rather than from `ls`.<br><br><strong>Evidence:</strong><br><code>$ ls -1 scripts/sales/ | wc -l<br>7<br>$ ls -1 scripts/sales/<br>add-pdf-form-fields.py<br>autofill-handoff-form.py<br>intake-kit-request-pdf.sh<br>intake-request-record.py<br>intake-to-pdf.sh<br>issue-transaction-bundle.sh<br>validate-transaction-bundle.sh<br>$ ls -l scripts/validation/validate-sale-receipt.sh<br>-rwxrwxr-x 1 scottw scottw 1893 Oct  3 18:48 scripts/validation/validate-sale-receipt.sh</code></td>
</tr>
<tr>
<td valign="top">OPS-10</td>
<td valign="top"><strong>Named backup and restore executors</strong></td>
<td valign="top">ST-18</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§16.1, §17.1</td>
<td valign="top"><strong>CLOSED 17-backup-restore-monitoring-and-completion-criteria.</strong> New §17.1.1 "Named executors" gives every row of the §17.1 frequency table a
named script path, a systemd unit, a timer and a cadence. The defect was that
§16.1 listed `scripts/backup/` and `scripts/restore/` as empty directories
while ST-18 claimed active timers; both directories are now populated and the
six unit files exist under `systemd/backup/`.

The seven-step restore test now has a named executor —
`scripts/restore/restore-restic-drill.sh` — which is new in this session.
§17.1.1 states honestly that it has **no cadence**: nothing schedules it, so
§17.1's "Monthly" requirement is still unmet and that half of the item is
carried by OPS-24 rather than claimed here.

**Correction worth recording:** I first searched `quadlet/operations/` for the
restic units and got nothing, and my instinct was to record that they did not
exist. They do — under `systemd/backup/`. I had assumed a directory layout
instead of enumerating one, which is the single most expensive mistake available
in a repo this size. The units are also **not deployed**
(`ls ~/.config/containers/systemd/ | grep -i restic` → none deployed), because
they are root-level units installed by `install-backup-schedule.sh`, not
Quadlets.

Files changed: `agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md` (§17.1.1),
`scripts/restore/restore-restic-drill.sh` (new).<br><br><strong>Evidence:</strong><br><code>$ find . -name '*restic*' -not -path './.git/*'   # (also ao-db-dump units checked the same way)<br>./systemd/backup/ao-restic-verify.timer<br>./systemd/backup/ao-restic-verify.service<br>./systemd/backup/ao-restic-prefetch.timer<br>./systemd/backup/ao-restic-prefetch.service<br>./systemd/backup/ao-restic-backup.timer<br>./systemd/backup/ao-restic-backup.service<br>./scripts/backup/restic-run.sh<br>./scripts/backup/verify-backup.sh<br>./scripts/restore/restore-restic-drill.sh</code></td>
</tr>
<tr>
<td valign="top">OPS-08</td>
<td valign="top"><strong>Executable restore runbook with RPO and RTO</strong></td>
<td valign="top">ST-18</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§17.1</td>
<td valign="top"><strong>CLOSED 17-backup-restore-monitoring-and-completion-criteria.</strong> New §17.1.2 states an RPO and an RTO **per data class** rather than one number
for the system, and §17.1.3 gives the restore ordering the two are bounded by.

A single RPO would have been a fiction. The measured position is: **no class
achieves better than 24 h**, because no WAL or continuous archiving is
configured and the nightly timer is the only mechanism. §17.1's own row
proposing "continuous or 15-minute" WAL for critical recovery objectives is now
labelled **aspirational and not implemented** in the section text, because
leaving it there would let a reader believe the requirement was met.

The secret class is called out separately and honestly: KDE Wallet is not
backed up, deliberately, so its RPO is **total loss** and recovery depends on
out-of-band re-provisioning. Stating that plainly is more useful than rounding
it into a number.

Files changed: `agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md` (§17.1.2, §17.1.3).<br><br><strong>Evidence:</strong><br><code># the seven-step restore test the RPO/RTO table is bounded by, with its<br># executor named in OPS-10 — run against the off-host repository:<br>$ export RESTIC_REPOSITORY=/media/scottw/…/ALWAYSON-BACKUPS<br>$ restic snapshots --json | python3 -c '…'<br>count: 1<br>  56bf1af5 2026-10-03T08:59:59-07:00 ['alwayson-offsite-proof'] ['/ALWAYSON/artifacts','/ALWAYSON/config']<br>$ restic check --read-data-subset=1/10<br>no errors were found</code></td>
</tr>
<tr>
<td valign="top">NET-04</td>
<td valign="top"><strong>Confirm the 4.3 prohibited-paths list</strong></td>
<td valign="top">ST-01, ST-02</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§4.3</td>
<td valign="top"><strong>CLOSED 04-security-isolation-and-data-policy.</strong> **The list is confirmed complete and correct, with one thing restored that was
genuinely lost, and one thing that needs a human.**

Restored. The rebuilt §4.3 was a table of ten rule-cited prohibitions. It is not
wrong, but it is not the original: it says *why* a class of path is forbidden and
never names the specific source → target pairs. The original, recovered verbatim
from the v6 archive and now §4.3.1, is eight lines of exactly those pairs. Both
are kept — §4.3.1 for what an operator checks against a running host, §4.3.2 for
the rule that enforces each. I did not overwrite §4.3.2 with the recovered list,
because the recovered list carries no rule references and the rebuilt one is
correct as far as it goes; deleting either would lose information.

Two recovered lines are superseded and are **marked, not deleted**, because
silently dropping a line from a prohibition list hides the decision that dropped
it: *Field/Mapping → payment provider* is now reached only through the controlled
adapters (§5.2), and *Fabrication simulation → live machinery* no longer carries
its "during phase one" qualifier — the prohibition is absolute now (§10.2).

**Needs a human decision, and it is the reason I am not claiming this is fully
settled.** I recovered the list from an archive and cross-checked it against the
rest of this document; I did not obtain operator re-approval of the recovered
text. §4.3.3 says so explicitly in the section itself, so the next reader cannot
mistake recovery for approval. If the operator confirms the recovered list as the
approved original, NET-04 closes with nothing further; if the operator has a
different original in mind, §4.3.1 is the place the correction goes.

**Supplied that was lost with the misplaced content:** nothing else. The
overwritten body was a duplicate of the sale-chain diagram, and that diagram is
present and correct in §3.3.2. I checked rather than assuming: the sale-chain
figure and its five-step narrative are at §3.3.2 lines 202-210, with the image
`assets/topology-detail-salechain.png`.

**What I got wrong.** My first search for the original was `git log` on the
section file, which returned exactly one commit — `09be9ce`, the consolidation
that created `agents/COORDINATION (README UPDATES) (README UPDATES)/`. That is correct and useless: the section
file has only ever had one version, so its history cannot contain the loss. The
loss happened upstream, before the split into section files. Reason: I searched
the history of the artefact I was editing rather than the history of the
*content*. The original was recoverable within one command of looking in the
archive tree, which I only reached by grepping the whole repo for the section
heading.

**Cross-check performed.** I also checked `config/platform/topology-model.yaml`
for a machine-readable prohibition edge list to reconcile against, and there is
none — the model's `edge:` block carries adapter paths and statuses but no
deny-edges. So the recovered text has no second independent source, which is
precisely why the operator confirmation is still wanted.<br><br><strong>Evidence:</strong><br><code>The operator-approved original was recoverable; it was in the repo the whole<br>time. Provenance chain, not memory:<br>$ git --no-pager log --oneline -1 -- 'README - ARCHIVE/ALWAYS ON — Architecture, Operations, and Status - v6.md'<br>b3d35e7 docs(archive): add the superseded README history</code></td>
</tr>
<tr>
<td valign="top">NET-03</td>
<td valign="top"><strong>Single authoritative network inventory</strong></td>
<td valign="top">ST-01, ST-02</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§2.2, §5.1.2</td>
<td valign="top"><strong>CLOSED 05-network-domains-and-controlled-external-access.</strong> **The real defect was the direction of authority, and it is fixed.**
`config/platform/network-cidrs.yaml` was documented as the single source of
truth, but `check-network-isolation.sh` overwrote it on every run from a
hardcoded `expected=(...)` array of eleven names plus an `egress=(...)` array of
three. The file named as the authority was derived from the script, so the
script was the real source of truth and the file was a generated artefact wearing
an authority label. Adding a network to podman without also editing that array
would have silently deleted the network from the authority on the next run — the
exact failure mode §19 described as "the named source of truth is not
authoritative."

The script now reads the registry and asserts the host against it, in both
directions. It never writes the file. It asserts the CIDR as well as the
`Internal` flag, it detects any live `ao-*` network missing from the registry,
and it fails if the total (14), internal count (11) or egress count (3) changes
without a deliberate count decision. Negative tests 1-3 above prove each new
assertion actually bites rather than printing and exiting zero.

**The three disagreeing counts are already one count, and it was already
fourteen.** §19 said "§2.2 says twelve, §13.3 says twelve, this document says
thirteen." Measured 2026-10-03, that is stale in §19, not in §2.2 or §13.3:
`02-platform-baseline/section.md` says "Fourteen" and enumerates eleven
internal plus three egress; `13-podman-runtime-and-quadlet-policy/section.md`
says "the 14 ao-*.network definitions"; the live host has exactly 14 `ao-*`
networks with 11 `Internal=true` and 3 `Internal=false`. So no count edit was
needed in §2.2 or §13.3, and I did not edit those files — they are not mine.
§5.1.1 is now a generated inventory with the count asserted by the script rather
than stated in prose, which is what makes it stay true.

`ao-html-window` (10.89.14) and `ao-build-update` (10.89.13) were already rows in
§5.1.1 as it stood — §19's claim that they appear "in no table" was also stale.
They are still rows, and the table's first column was empty on thirteen of
fourteen rows (a rendering bug from the generator); that is fixed.

**What I got wrong.** I first wrote the new script through the editor with
`[[ ... ]] &amp;&amp; x=y` compound conditions and a comment-strip line that would have
tripped `set -e` on the first false test, terminating the script silently mid-run
with exit 0. I caught it by reading it back rather than running it, and rewrote it
with explicit `if` blocks. Reason: I optimised for a short diff against the old
script instead of for a script that survives `set -Eeuo pipefail`. Lesson: any
`&amp;&amp;`-chained statement as the *last* command of a loop body under `set -e` is a
silent-truncation bug.

**Assumption stated.** The script keeps its absolute `/ALWAYSON/scripts/lib/common.sh`
source line, so `ao_audit` still writes to the live audit log when run from a
checkout. I added an `AO_REGISTRY` override purely so it can be exercised against
a non-live tree; production calls take the default. I did not change
`check-deployment-conformance.sh`, which independently reads the registry — it is
not my file, and it remains correct because the file format is unchanged.<br><br><strong>Evidence:</strong><br><code>$ AO_REGISTRY=$PWD/config/platform/network-cidrs.yaml bash scripts/validation/check-network-isolation.sh<br>OK: ao-payment (10.89.1.0/24) Internal=true<br>OK: ao-field (10.89.2.0/24) Internal=true<br>OK: ao-mapping (10.89.3.0/24) Internal=true<br>OK: ao-sim-vehicle (10.89.4.0/24) Internal=true<br>OK: ao-sim-fabrication (10.89.5.0/24) Internal=true<br>OK: ao-ledger-ingest (10.89.6.0/24) Internal=true<br>OK: ao-ledger-core (10.89.7.0/24) Internal=true<br>OK: ao-data (10.89.8.0/24) Internal=true<br>OK: ao-admin (10.89.9.0/24) Internal=true<br>OK: ao-fabrication (10.89.12.0/24) Internal=true<br>OK: ao-html-window (10.89.14.0/24) Internal=true<br>OK: ao-reporting-egress (10.89.10.0/24) Internal=false by decision<br>OK: ao-sales (10.89.0.0/24) Internal=false by decision<br>OK: ao-build-update (10.89.13.0/24) Internal=false by decision<br>OK: all domain networks present; isolation domains internal-only; 3 egress networks non-internal by decision; registry matches host (14 = 11 + 3)<br>EXIT=0</code></td>
</tr>
<tr>
<td valign="top">NET-02</td>
<td valign="top"><strong>CIDR reconciliation in <code>network-cidrs.yaml</code></strong></td>
<td valign="top">ST-02</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§2.2</td>
<td valign="top"><strong>CLOSED 05-network-domains-and-controlled-external-access.</strong> The CIDR reconciliation §19 left open is closed as a *measurement*, not an edit.
Every registered CIDR matches the running host, and `check-network-isolation.sh`
now asserts it on every run instead of overwriting the registry with whatever
podman happened to report (see net-NET-03.md).

The `ao-egress-community` name/CIDR reconciliation that §19 called "a rename
decision, not a registry edit" turns out not to need a decision at all, because
the premise is wrong: **the network is not live.** §19 says it "is live on
10.89.11.0/24". `podman network inspect` says it does not exist. `10.89.11.0/24`
is a reserved hole, deliberately unallocated. The retirement is already recorded
in `config/mastodon/instance-policy.yaml` and in
`scripts/mastodon/federate-local.sh`. So there is no rename to approve: the
retirement already happened, was already documented, and only §19's description of
it was out of date.

I corrected §5.1 (which said the range was "folded into ao-sales") and §5.1.1 to
state the accurate position: reserved, unallocated, name retired, community
egress carried inside `ao-sales`. Both now carry the `podman network inspect`
evidence.

**Two staleness findings belong to other groups — reported, not edited.**

1. `config/platform/topology-model.yaml:582` still declares `ao-egress-community`
   with `status: implemented` and `includes: [mastodon-web, mastodon-sidekiq]`.
   That is a **live topology model asserting a network that does not exist**, and
   `generate-topology.py` feeds the Grafana dashboard from it, so the dashboard
   will draw a phantom adapter network. This is the "Grafana topology dashboard"
   part of NET-02's remaining list. It is a config file outside my ownership and
   the fix belongs to whoever owns the topology model — flagging, not touching.
2. `config/platform/gui-boundary-matrix.yaml:102` says external publication
   happens "only through ao-egress-community **when enabled**", implying a
   disabled adapter pending enablement. In fact it is retired, not pending.
   Same owner question.

Also stale, and not mine: `docs/runbooks/mastodon.md:97` describes the delivery
path as requiring "the scoped ao-egress-community Sidekiq route, WORK 000060
outstanding", while `instance-policy.yaml` records WORK 000060 as done
(2026-09-30) and `ao-sales` as the live path. An operator following that runbook
would look for a route that does not exist.

**What I got wrong.** My first instinct on reading NET-02 was to treat
"10.89.11 is live" as a fact in the brief and go looking for a registry entry to
fix. The brief was describing a past state. Had I trusted it, I would have
either added a bogus `ao-egress-community` line to the registry or escalated a
phantom "rename decision" to the operator. Lesson: a stale line in §19 is a
hypothesis, not a specification — measure before reconciling.

**Not done, deliberately.** I did not edit the topology model, the GUI boundary
matrix, or the Mastodon runbook. All three are outside my two section files.<br><br><strong>Evidence:</strong><br><code>The registry is correct and agrees with the live host, network for network.<br>$ AO_REGISTRY=$PWD/config/platform/network-cidrs.yaml bash scripts/validation/check-network-isolation.sh<br>OK: all domain networks present; isolation domains internal-only; 3 egress networks non-internal by decision; registry matches host (14 = 11 + 3)<br>EXIT=0</code></td>
</tr>
<tr>
<td valign="top">LEDGER-06</td>
<td valign="top"><strong>Accounting model for the authoritative ledger</strong></td>
<td valign="top">ST-09, ST-10</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§11.1, §11.3, §4.4, §7.2</td>
<td valign="top"><strong>CLOSED 11-ledger-provenance-archive-and-ipfs.</strong> The §19 criteria offered a choice: "Define the model **or** state that the
ledger records references only and accounting is computed in reporting." I took
the first option, because §3.2 and §11.1 both already declare Corda the
"complete ledger of debits and credits", so defining the model makes existing
architecture text true instead of contradicting it.

§11.3.1 now defines, concretely:

- **Accounts** — a closed set of 8 (`CASH_EU`/`CASH_US`, `CASH_PENDING`,
  `RECEIVABLE_CUSTOMER`, `REVENUE_SALE`, `REVENUE_DIGITAL_TRANSFER`,
  `REFUNDS_PAYABLE`, `TAX_PAYABLE_&lt;jurisdiction&gt;`, `EXPENSE_ARCHIVE`), with the
  rejection rule for anything outside it.
- **Debit/credit semantics** — balanced double-entry, `SUM(debits)=SUM(credits)`
  per transaction per currency, integer minor units, no floats, no suspense
  account, no stored running balance.
- **Immutability** — corrections are reversing transactions, never edits or
  deletes.
- **Currency** — single-currency postings, explicit `FX_REVALUATION` with a
  recorded rate source, no implicit read-time conversion.
- **Posting rule** — "NO EVENT, NO POSTING", with a table binding each event to
  its gate. A provider webhook and a payment validation are explicitly *not*
  postings; only all three §11.2.2 gates together allow one.
- **Reconciliation** against `salesdb` per correlation tuple, with four named
  outcomes and an explicit rule that `salesdb_only` blocks a receipt being called
  final (§11.2.3).
- **The §4.4 accounting report** defined as a computed projection, not a stored
  balance.

The §7.2 tension resolves cleanly: Corda is authoritative for *approved
postings*, PostgreSQL for *source operational data*, and the report is computed
in reporting. §7.2's "Corda does not replace accounting processing" is honoured
by the explicit statement that a posting is evidence, never a payment
instruction.

## What I got wrong

My first edit placed §11.3.1 *after* the `## 11.4` heading, producing a
duplicated `## 11.4` and a mis-nested subsection. I caught it by re-grepping
headings after the edit rather than trusting the diff, and fixed it. Worth
remembering: the editor replaced the first `old_text` match, so anchoring on a
heading that was about to be duplicated is fragile.

## Note for the compiler

This item closes on documentation, not on running code. The model is now
defined; **no Corda node exists to enforce it**. If the operator intends the
weaker reading ("references only"), this is the section to revisit.<br><br><strong>Evidence:</strong><br><code>Added §11.3.1 "Accounting Model for the Authoritative Ledger" to<br>agents/COORDINATION (README UPDATES) (README UPDATES)/11-ledger-provenance-archive-and-ipfs/section.md</code></td>
</tr>
<tr>
<td valign="top">LEDGER-05</td>
<td valign="top">Ledger socket-bridge diagnosis</td>
<td valign="top">ST-09, ST-10</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§17.1</td>
<td valign="top"><strong>CLOSED 11-ledger-provenance-archive-and-ipfs.</strong> `check-ledger-ingest.sh` is resolved and deterministic, and it runs
unprivileged — the acceptance criteria allowed either the script being resolved
**or** a pending privileged command, and the script route is the one that
actually holds. Exit `3` is a defined PENDING state, distinct from healthy (`0`)
and from failure (`44`).

Added §11.2.4 "Ledger-Ingest Probe Status" recording this with the output above.
The diagnosis result is negative and worth stating plainly: **there is no
socket-bridge fault to diagnose.** The probe is blocked solely because the
`ledger-ingest` gateway does not exist yet, which is downstream of the Corda 5
node build and the operator key ceremony.

I also recorded that `submit-ledger-event.sh` stages rather than loses data, so
nothing is at risk while the gateway is absent.

## What I got wrong

I initially tried to write this section assuming there would be a real bridge
fault to diagnose — the item name implies one. There isn't. The honest output is
"the probe works, the service does not exist yet." I also nearly claimed the
client-side behaviour was verified after only *reading* the scripts; I then ran
them, which is what surfaced the signature weakness recorded in §11.2.5.

## Note for the compiler

No §19 wording change needed beyond status; the acceptance criteria stand as
written and are met.<br><br><strong>Evidence:</strong><br><code>$ bash /ALWAYSON/scripts/validation/check-ledger-ingest.sh<br>PENDING: ledger-ingest gateway not deployed yet (Section 2.8 step 3 awaits Corda version approval)<br>EXIT=3</code></td>
</tr>
<tr>
<td valign="top">FIELD-13</td>
<td valign="top"><strong>Rule on LoRaWAN naming</strong></td>
<td valign="top">ST-04</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">ES.1, §9.4</td>
<td valign="top"><strong>CLOSED 09-field-and-lora-architecture.</strong> §9 gains a new **§9.4.3** stating the rule the item asks for: whether RNode-over-Reticulum is
*ever* called LoRaWAN in any artefact.

**Decision: it is not. The approved wording is "raw LoRa over Reticulum (RNode), NOT LoRaWAN".**
The stack implements no LoRaWAN device, gateway or network-server architecture, so the term
does not apply to it at any layer. This is not a stylistic preference — §9.4 already forbade
describing the system as LoRaWAN unless a true device/gateway/network-server architecture
exists, and no such deployment is selected.

**Applied within the sections I own.** The rule is now written into §9.4.3, and §9.2.2's
`PEOPLE-RADIO` row was corrected to the approved wording, cross-referencing §9.4.3. That row
previously read `**LoRaWAN-related communication** … This radio is the LoRaWAN path for human
conversation.` and now reads `**Raw-LoRa human communication** … it is **not** LoRaWAN
(§9.4.3)`. Both radio profiles already carried
`frequency_plan: "US915 hybrid-channel raw LoRa (NOT LoRaWAN)"`, so no config file needed
changing.

**Two contradictions remain outside my sections. I did not edit them — they belong to their
owning sessions.** They are reported here so the compiler can route them:

| File | Line | Problem |
|---|---|---|
| `es-executive-summary/section.md` | 11 | calls `PEOPLE-RADIO` "**LoRaWAN for communication only**" — the clearest violation, and the exact one FIELD-13 was raised about |
| `19-.../section.md` | 615, 619 | FIELD-07's own title and criteria say "MeshChatX **LoRaWAN** path" and "recorded as LoRaWAN-related communication" |

`02-platform-baseline/section.md:18` mentions LoRaWAN but is **already compliant** — it says
"over raw LoRa *unless a true LoRaWAN deployment is selected*", which is the rule this item
asked to be decided. No change needed there, and I am not proposing one.

**Why FIELD-13 can close while FIELD-07 stays open.** FIELD-13 asks for a decision and
application. The decision is made, recorded in §9.4.3, and applied everywhere I own. The two
remaining occurrences sit in other sessions' files plus §19 itself, which is single-writer and
which I must not edit — so I report them instead. **The compiler should not read FIELD-13's
closure as "the word has been purged repo-wide"; it has not.**<br><br><strong>Evidence:</strong><br><code># every LoRaWAN mention in the source of truth, by section<br>$ grep -rc -i 'lorawan' agents/COORDINATION (README UPDATES) (README UPDATES)/*/section.md | grep -v ':0'<br>agents/COORDINATION (README UPDATES) (README UPDATES)/02-platform-baseline/section.md:1<br>agents/COORDINATION (README UPDATES) (README UPDATES)/09-field-and-lora-architecture/section.md:11<br>agents/COORDINATION (README UPDATES) (README UPDATES)/19-current-status-and-outstanding-work/section.md:4<br>agents/COORDINATION (README UPDATES) (README UPDATES)/es-executive-summary/section.md:1</code></td>
</tr>
<tr>
<td valign="top">FIELD-12</td>
<td valign="top"><strong>One canonical radio device-name table</strong></td>
<td valign="top">ST-04</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§2.1, §9.2.1, §9.4</td>
<td valign="top"><strong>CLOSED 09-field-and-lora-architecture.</strong> §9 gains a new **§9.4.2** publishing the one canonical device-name table the item asks for, and
resolving the three-way contradiction between §2.1, §19 and §9.2.1.

| Radio | Live port | `by-path` discriminator | `ID_PATH` |
|---|---|---|---|
| `DRONE-RADIO` (917 MHz) | `/dev/ttyUSB0` | `pci-0000:05:00.0-usb-0:1:1.0-port0` | `pci-0000:05:00.0-usb-0:1:1.0` |
| `PEOPLE-RADIO` (915 MHz) | `/dev/ttyUSB1` | `pci-0000:00:14.0-usb-0:13:1.0-port0` | `pci-0000:00:14.0-usb-0:13:1.0` |

Two findings the compiler should not lose:

1. **§19's `/dev/heltec-v3` is wrong and must not be reinstated.** Both boards are Heltec V3,
   so one name could only ever point at one of them. `99-ao-heltec.rules` *deliberately*
   declines to create it.
2. **`by-id` cannot identify `PEOPLE-RADIO` at all** — only one link exists, pointing at
   `ttyUSB0`. Both ports also share a byte-identical `ID_SERIAL`, confirming §9.2.1's claim
   that identity cannot come from the USB serial descriptor. **`by-path` is the only working
   discriminator**, which is what the live Reticulum config already uses.

**§2.1's `/dev/ao-drone-radio` and `/dev/ao-people-radio` are specified but absent.** The udev
rule is installed and provably correct — `udevadm test` shows it *would* create both symlinks,
one per line, matched to the right port. The cause is ordering: the rule was installed
`2026-09-30 23:05:58`, after both adapters were already enumerated, and udev applies `add` rules
only at enumeration. An `udevadm trigger` would create them.

**Not performed — operator action required.** `udevadm trigger` on live serial devices is a stop
condition under "live radio, serial or network configuration". So the table above is published
against `by-path`, which works today; the `ao-*` names become valid once the operator triggers.
Nothing in §9.2.1 depends on the `ao-*` names, so no section is blocked by this.

**The MAC column is deliberately empty.** §9.4.2 asks for it, and obtaining the SX1262 MAC
requires opening the RNode serial port, which `ReticulumMeshChatX` (PID 840861) currently holds
open. That is live radio configuration. The column is marked **not measured** rather than
guessed — if the compiler renders FIELD-12 as "fully closed with MACs", that would be a stronger
claim than the evidence supports. The item is closed on the *decision and the table*, which is
what it asked for; the MAC is the one cell still owed.<br><br><strong>Evidence:</strong><br><code># live ports<br>$ ls -la /dev/serial/by-path/<br>pci-0000:00:14.0-usb-0:13:1.0-port0     -&gt; ../../ttyUSB1<br>pci-0000:00:14.0-usbv2-0:13:1.0-port0   -&gt; ../../ttyUSB1<br>pci-0000:05:00.0-usb-0:1:1.0-port0      -&gt; ../../ttyUSB0<br>pci-0000:05:00.0-usbv2-0:1:1.0-port0    -&gt; ../../ttyUSB0</code></td>
</tr>
<tr>
<td valign="top">FIELD-11</td>
<td valign="top"><strong>Authoritative mapping database name and location</strong></td>
<td valign="top">ST-03</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§8.1, §8.4, §8.5, §3.3.1</td>
<td valign="top"><strong>CLOSED 08-mapping-and-photogrammetry.</strong> §8 gains a new **§8.4.1** stating the single answer the item asks for.

- Logical database: **`webodm_dev`** (not `webodm`, which survives only as a 2026-09-30
  rollback artefact per ST-03).
- Physical storage: **`/home/scottw/webodm/dbdata`**, bind-mounted to `/var/lib/postgresql/data`
  on `ao-webodm-db`. This confirms §8.4 was already right and needs no change.
- Backup scope: **included**, proven at `scripts/backup/dump-all-postgres.sh:18`.

**The third requirement — "confirm it is inside the backup scope" — is met. But the acceptance
criteria also observed that §8.1/§8.5 require all mapping storage on the photogrammetry drive,
"which as written contains neither." That part is NOT met and is not fixed.** The PostgreSQL
data directory is on the root filesystem. I recorded this as an explicit approved deviation in
§8.4.1 rather than dropping the requirement, and flagged that the drive-residency half should
be carried forward as a **new FIELD item** rather than reopening FIELD-11. Moving a live
PostgreSQL data directory is an operator decision and a service-configuration change.

If the compiler prefers to keep FIELD-11 open instead, the honest status is "name and
location decided and evidenced; drive residency still deviated."<br><br><strong>Evidence:</strong><br><code>$ podman inspect ao-webodm-db --format '{{range .Mounts}}{{.Source}} -&gt; {{.Destination}}{{end}}'<br>/home/scottw/webodm/dbdata -&gt; /var/lib/postgresql/data</code></td>
</tr>
<tr>
<td valign="top">FIELD-05</td>
<td valign="top"><code>umsgpack</code> persistence error</td>
<td valign="top">ST-04, ST-05, ST-06</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§9.2</td>
<td valign="top"><strong>CLOSED 09-field-and-lora-architecture.</strong> §9 gains a new **§9.2.3** classifying the item exactly as the acceptance criteria allow —
"formally accepted as a historical bounded-ratchet defect with restart-persistence evidence".

The 12,364 `umsgpack` errors are entirely confined to `meshchatx.log.2`; the two newer rotated
logs contain zero. The error block ends immediately before a restart that reinstalls the persist
worker, so it is a packaging defect in the pre-2026-09-24 AppImage build (bundled Reticulum
lacked `umsgpack`), not a live fault.

Restart-persistence evidence is supplied as required: the ratchet file mtime
(`2026-10-03 09:51:34`) precedes the running process start (`16:57:27`) by seven hours and a
20-second re-sample shows an unchanged sha256, so the persist worker has written nothing in the
current instance.

**Two things the compiler must not lose.** First, §9.2.3 records a *separate, still-live*
defect found while gathering this evidence: 3 `[Errno 9] Bad file descriptor` persist failures,
each landing in the same second as a `DRONE-RADIO` interface teardown. This is a different bug
and is **not** covered by closing FIELD-05. Second, I did not fix anything — repair means
touching the serial device and the running Reticulum stack, which is a stop condition.<br><br><strong>Evidence:</strong><br><code>$ cd ~/.reticulum-meshchatx/logs<br>$ for f in meshchatx.log.2 meshchatx.log.1 meshchatx.log; do echo -n "$f: "; grep -c umsgpack "$f"; done<br>meshchatx.log.2: 12364<br>meshchatx.log.1: 0<br>meshchatx.log: 0</code></td>
</tr>
<tr>
<td valign="top">FIELD-04</td>
<td valign="top">Reticulum gateway listener review</td>
<td valign="top">ST-04, ST-05, ST-06</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§9.3, §9.4</td>
<td valign="top"><strong>CLOSED 09-field-and-lora-architecture.</strong> §9 gains a new **§9.3.1** that *decides* reachability rather than leaving it open, which is
what the acceptance criteria ask for.

Decision: **`0.0.0.0:4242` stays LAN-reachable and is approved as designed.** Reachability is
proven by actual TCP connects from both loopback and `192.168.87.135` (the `wlp3s0` LAN
address), not inferred from the bind address. Reasoning recorded: it is a Reticulum protocol
listener in a `user` unit, not a public ingress, so §4.1 rule 4 does not bite; and the field
radios address the mesh by RF, not TCP, so loopback-only binding would break the design
without reducing exposure.

**Caveat recorded honestly in §9.3.1 and repeated here.** The item also says "reviewed
against field-domain firewall policy", and I could only half-do that. There is no field-domain
firewall policy file at all (`config/field/` contains only `heltec-v3`), and the §9.3 table's
claim that `4242/tcp ALLOW Anywhere` is an explicit UFW allow could not be re-verified —
`/etc/ufw/user.rules` is `0640 root:root` and `ufw status` requires sudo. So: **reachability is
decided and evidenced; the mechanism is unverified.** If the compiler or operator reads
FIELD-04 as "firewall policy confirmed", that would be a stronger claim than I can support.<br><br><strong>Evidence:</strong><br><code>$ ss -ltnp | grep -E '18000|4242'<br>LISTEN 0 128  127.0.0.1:18000  0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=17))<br>LISTEN 0 1    0.0.0.0:4242     0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=46))</code></td>
</tr>
<tr>
<td valign="top">COMM-04</td>
<td valign="top">OpenClaw OAuth and conversation validation</td>
<td valign="top">ST-15</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§15.2</td>
<td valign="top"><strong>CLOSED 15-sales-mastodon-openclaw-and-local-ai.</strong> Recommend **close**. Both halves of the item were already done on 2026-10-01; this pass
**re-verified** rather than repeated them, and that distinction matters — no new public
post was made, so no external publication occurred without approval.

My section file gains a five-point re-verification record under §15.2, covering:

1. **Auth half confirmed** — `verify_credentials` returns HTTP 200 for `acct=bot`. Token
   length is 43 characters; the value was never printed, only measured.
2. **Operator decision confirmed live** — line 281 is `'visibility': 'public'` with the
   `@author` mention prefix retained, in **both** the `/ALWAYSON` copy and the deployed
   `~/.local/bin` copy. No stale `unlisted` variant is hiding anywhere.
3. **Deployed file identity** — `sha256` `486e7472…99c19` for both, i.e. a
   byte-identical **copy, not a symlink**. Flagged in §15.2 because editing the
   `/ALWAYSON` copy alone will *not* change live behaviour without a unit restart. This is
   the same load-bearing trap documented for Quadlets, and it now applies to this script.
4. **Cursor is idle by type, not the old fault** — `max(notifications.id)` is 8 while the
   cursor is 7. Both rows are `type=follow`, which the bridge skips by design. The
   previously reported stale-cursor fault (cursor *ahead* of the newest id) is fixed, and
   the bridge's own recovery log line is present in the journal:
   `cursor 68 is ahead of newest notification 7; notification ids were reset`.
5. **No 401 crash-loop regression** — the unit has run 2 days without restarting.

The journal also preserves the original fault history for the next session, including the
run of `failed status … HTTP Error 404: Not Found` and the `cursor 68 is ahead of newest
notification 7` recovery. I left those in place rather than cleaning them.

**What I got wrong:** my first two attempts to measure the cursor used a one-line
`echo '...' | podman exec` combination whose embedded SQL quotes collided with the shell
quoting, producing `unexpected EOF while looking for matching '''` and a syntax error. I
had read those two failed turns as *evidence about the database* before noticing they were
shell parse errors — the worst possible failure mode, because an error message can be
mistaken for a null result. I switched to writing probe scripts to `/tmp` with quoted
heredocs and a `Q()` helper, after which no query failed for quoting reasons.

I also initially reported the notification count as `count=2` alongside
`max_notification_id=8`, and briefly worried the bridge was stalled. It is not: `follow` is
not a type the bridge acts on. Checking the `type` column before calling idleness a fault
is the lesson.<br><br><strong>Evidence:</strong><br><code># Auth half - wallet-held token, VALUE NEVER PRINTED, only length measured:<br>$ /ALWAYSON/scripts/ops/wallet-read-secret.py kdewallet ao-mastodon openclaw-bot-access-token | tr -d '\n' | wc -c<br>token length (chars) = 43<br>$ curl -s -o /tmp/vc.json -w '%{http_code}' -H "Authorization: Bearer $TOK" \<br>  'https://mastodon.300x3.com/api/v1/accounts/verify_credentials'<br>verify_credentials HTTP = 200<br>acct = bot | username = bot | id = 117363090433277638</code></td>
</tr>
<tr>
<td valign="top">COMM-03</td>
<td valign="top">Remote account approval/rejection record</td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§15.4.5</td>
<td valign="top"><strong>CLOSED 15-sales-mastodon-openclaw-and-local-ai.</strong> Recommend **close**, with an important contradiction recorded rather than papered over.

The acceptance criterion was "recorded separately from local account follow state", so my
section file gains a new **§15.4.6 "Remote Account Approval and Rejection Record"** — a
standing table, explicitly separate from §15.4.9's follow relationships, holding one row
per remote account with the action taken and its basis. It carries the nine-table row-count
query above as its evidence, and states that nothing in the moderation tables is
self-populating, so a future block or approval must be added as a row by the operator
(per §15.4.1 "Operator duties"). No remote account has been rejected to date.

The judgement call worth the operator's attention: **ten of the twelve remote actors are
`actor_type=Application`, not people.** They are protocol discovery artefacts — a
Mastodon instance or a Friendica node fetching `/actor` during ordinary federation. They
are not sign-ups, not approval candidates, and must not be logged as if they were. §15.4.6
says so explicitly, because "remote account contacted us" and "a user registered" are easy
to conflate when reading an `accounts` table.

Only two remote actors are actual accounts, and both are recorded: `300x3@mastodon.social`
(**accepted**, `actor_type=Service`, `bot=true` — the project's *own* remote identity, so
blocking it would sever the operator's own presence) and `Gargron@mastodon.social`
(**accepted as a remote actor, not followed** — an ordinary local→remote follow, not a
moderation event).

**The contradiction I could not resolve alone.** COMM-03 presupposes an approval workflow,
but registration is closed, so there is no queue to approve from:

```
$ curl -s https://mastodon.300x3.com/api/v1/instance | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('registrations'),d.get('approval_required'))"
False False
```

No `registrations` row exists in `settings` (Mastodon 4.3 treats absent as disabled),
`follow_requests = 0` and `user_invite_requests = 0`. Meanwhile
`config/mastodon/instance-policy.yaml` line 24 still asserts
`registrations: "open with approval gate (approval_required: true)"`. **The policy file and
the running service now disagree.** I corrected my own §15.3 and §15.4.2 to match the
measured service, and raised `instance-policy.yaml` line 24 as drift row **D6** in the
COMM-01 proposal for the session that owns `config/`. I did not edit that file myself.

This does not block the close — the record exists and is now written down — but the
operator should decide whether the intended state is "closed" (in which case D6 is a doc
fix) or "open with approval gate" (in which case **the service configuration is wrong**,
and opening registration is a moderation decision I am not authorised to make).

**What I got wrong:** my first query used `settings.name`, which does not exist in
Mastodon 4.3 — the column is `settings.var`. It returned only `reserved_usernames` via a
fallback and would have supported a false "no registration settings at all". I also queried
`notifications.status_id`, which this schema version does not have. Both errors were loud
(SQL errors, no rows), which is the good case, but for several turns I was reasoning from
empty results as though they were measurements. The `accounts` table also has **no**
`username=''` rows, so an early "orphan account" hypothesis I formed from a count was
simply wrong.<br><br><strong>Evidence:</strong><br><code>$ podman exec mastodon-db psql -U mastodon -d mastodon -At -c \<br>  "select 'blocks='||(select count(*) from blocks)<br>        ||' domain_blocks='||(select count(*) from domain_blocks)<br>        ||' account_domain_blocks='||(select count(*) from account_domain_blocks)<br>        ||' email_domain_blocks='||(select count(*) from email_domain_blocks)<br>        ||' canonical_email_blocks='||(select count(*) from canonical_email_blocks)<br>        ||' follow_requests='||(select count(*) from follow_requests)<br>        ||' invites='||(select count(*) from invites)<br>        ||' ip_blocks='||(select count(*) from ip_blocks)<br>        ||' user_invite_requests='||(select count(*) from user_invite_requests);"<br>blocks=0 domain_blocks=0 account_domain_blocks=0 email_domain_blocks=0<br>canonical_email_blocks=0 follow_requests=0 invites=0 ip_blocks=0 user_invite_requests=0</code></td>
</tr>
<tr>
<td valign="top">COMM-02</td>
<td valign="top">Reverse-follow validation</td>
<td valign="top">—</td>
<td valign="top"><strong>Implemented</strong></td>
<td valign="top">§15.4.4</td>
<td valign="top"><strong>CLOSED 15-sales-mastodon-openclaw-and-local-ai.</strong> Recommend **close**. The acceptance criterion was "confirmed from the remote `following`
collection and local incoming relationship tables, never inferred from local outgoing
state" — and that is exactly the method used. The decisive evidence is the remote side:
`300x3@mastodon.social`'s `following` collection returns both `admin@mastodon.300x3.com`
and `bot@mastodon.300x3.com`, which no amount of local-table reading could have
manufactured.

My section file gains a new **§15.4.9 "Federation Contact Asymmetry (measured, not a
fault)"**, which records a finding I judged too easy to misread in a later session.

What I found is that the relationship is **not** reciprocal, and someone auditing this
later would reasonably mistake that for drift:

- The remote `following` collection lists both local accounts, but the mirror's
  `followers` collection lists **only** `bot`. Local `follows` rows 3 and 4
  (`300x3@mastodon.social` → `bot`, → `admin`) were created by the *remote* account's own
  requests, not by us.
- `admin` has no outgoing remote follow at all. The only local→remote row in the table is
  `bot → admin` (row 1).
- `Gargron@mastodon.social` was paginated to exhaustion — 25 pages, 2000 follower
  entries — and does not follow any `300x3.com` account. This is *correct*: row 2
  (`Gargron → bot`) records that Gargron follows our bot, which is the remote account's
  business, not a reciprocity requirement.

§15.4.9 states plainly that this asymmetry is how ActivityPub follow requests work, not a
defect, so a future session does not "fix" it by adding follows.

Two supporting negatives are also recorded, because a broken pipeline can look identical
to a quiet one: the sidekiq queues are empty (`LLEN queue:push_public = 0`,
`LLEN queue:pull = 0`, `redis-cli KEYS 'queue:*'` → empty array), and the actor endpoint
answers 200 on five consecutive tries.

**What I got wrong:** my first pagination script reported `300x3@mastodon.social` with
`our_accounts_found` listing `bot@mastodon.300x3.com` **25 times**, and
`total_followers_seen=25`. That is not 25 followers. The mirror has exactly one follower.
The bug was mine: I passed `max_id` from the last item of each page but never stopped, so
with a single-item result set the loop re-requested the same page 25 times. I nearly
recorded "the remote mirror has 25 followers of our bot" as evidence. The single
authoritative call (`limit=80`, no pagination) returns `followers_count= 1`, which is what
§15.4.9 records. Lesson: an unpaginated endpoint call should be the *first* measurement,
not the fallback after a paginating one looks odd.

A separate transient also nearly became a false finding: the actor endpoint
`https://mastodon.300x3.com/users/bot` returned **502** on the first probe. Re-probing
five times returned 200 every time, and `/api/v1/instance`, `/api/v2/instance` and `/` all
returned 200. I recorded it as transient rather than as a fault — one observation is not a
finding, and `mastodon.social` WebFinger answering 404 for our accts is likewise normal
(Mastodon does not federate WebFinger for accounts it has no local record of).<br><br><strong>Evidence:</strong><br><code># Primary evidence: the REMOTE following collection on mastodon.social, not local state.<br>$ curl -s -H 'Accept: application/json' \<br>  'https://mastodon.social/api/v1/accounts/115945980770248178/following?limit=80' \<br>  | python3 -c "import sys,json; d=json.load(sys.stdin); print('count=',len(d)); [print(a['acct'],'|',a['url']) for a in d]"<br>count= 2<br>admin@mastodon.300x3.com | https://mastodon.300x3.com/@admin<br>bot@mastodon.300x3.com   | https://mastodon.300x3.com/@bot</code></td>
</tr>
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
<td valign="top">§14.1.1</td>
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
<td valign="top">Complete 2026-10-02. The bridge is built locally as <code>localhost/foxglove-bridge</code> (own Containerfile, digest-pinned) rather than installed from <code>packages.ros.org</code>, which stays unreachable per SIM-07 — so that blocker no longer gates Foxglove views. Two silent faults had to be cleared first. The gz→ROS hop needs the five <code>gz_*_vendor/lib</code> directories and <code>/opt/ros/lyrical/lib</code> on <code>LD_LIBRARY_PATH</code>; without them the process stayed up, accepted connections, bridged nothing, and logged no error. And the server must set <code>GZ_IP=0.0.0.0</code> — the GUI appeared to work without it only because it shares the server's network namespace, which masked a container with no route. The bridge must also be on both <code>ao-html-window</code> and <code>ao-sim-fabrication</code>: a matching <code>GZ_PARTITION</code> does not route between two internal bridges. Verified 2026-10-02: <code>Advertising new channel 4 for topic "/factory/camera/image"</code>, <code>sensor_msgs/msg/Image</code> publisher count 1, frames at the world's 10 Hz.</td>
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
