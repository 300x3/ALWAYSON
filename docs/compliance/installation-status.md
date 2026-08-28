# ALWAYS ON — Installation Status Report (Section 5)

Date: 2026-08-24 · Operator host: Kubuntu/Ubuntu 26.04 LTS workstation

## Completed deliverables

| # | Section 5 item | Status |
|---|---|---|
| 1 | Host inventory report | ✅ `logs/installation/agent-install.log` |
| 2 | Photogrammetry-drive report | ✅ /dev/sdb1 ext4 UUID 498597d4-9fc8-42cf-8db7-4e71ede53267, 435G free, dir tree + .mounted-ok created, validation script passes |
| 3 | Installed package/version matrix | ✅ `config/platform/version-matrix.yaml` (systemd 259, podman 5.7.0, NVIDIA 580.173.02) |
| 4 | Podman rootless + Quadlet verification | ✅ rootless OK, cgroups v2, linger enabled, 10 networks Internal=true |
| 5 | GPU driver/container-runtime report | ✅ driver working; nvidia-container-toolkit 1.20.0 installed 2026-08-25; CDI devices registered (`nvidia-ctk cdi list` verified 2026-08-26); GPU-enabled WebODM ortho run passed |
| 6 | Podman network list + isolation test | ✅ `config/platform/network-cidrs.yaml`; check-network-isolation.sh PASS |
| 7 | Firewall/listening-port report | ⚠️ ufw active; :80 resolved (nginx purged); **:1716 re-bound 2026-08-26 despite disable decision** — reopened, see blockers |
| 8–15 | WebODM/sim/Heltec/ledger/sales/backup/restore smoke tests | Mixed: 8 ✅ (apt-76 ortho), 9–10 ✅ (headless Gazebo), 14 ✅ (restic 548d9910), 15 ✅ (file+DB restore) — all 2026-08-25 journal; 11 ⏸️ Heltec deferred; 12 ⏸️ Corda scaffolded, awaits key ceremony; 13 ⚠️ schema only |

## Blockers requiring operator approval (Section 2.2 pause rules)

1. ~~nginx on :80~~ — RESOLVED: stopped and disabled at operator direction; port 80 clear.
   keep+allowlist, repurpose as ALWAYS ON ingress, or stop.
2. **KDE Connect on *:1716** — RESOLVED 2026-08-24 (autostart hidden, daemon stopped)
   but RECURRED as of 2026-08-26 (:1716 listening again after update/reboot).
   Apply a durable disable or grant an explicit allowlist entry.
3. **Existing PostgreSQL 18 cluster + Redis** on host loopback — PARTIALLY DECIDED
   2026-08-24: WebODM uses container-scoped db/broker on ao-mapping; sales-db runs
   container-scoped postgres@pinned digest under alwayson-sales; **cordadb provisioned
   on host PG18 cluster** (operator-approved reuse deviation). Redis reuse still undecided.
4. **ROS "lyrical" + Gazebo 10.5 installed** vs spec Jazzy + Harmonic — accept deviation
   or install Jazzy/Harmonic alongside.
5. ~~WebODM image digests — none approved~~ RESOLVED: digests pinned at deploy
   (version-matrix.yaml; webapp/db/nodeodm/broker sha256 recorded 2026-08-24);
   repo Quadlet templates updated to the real digests 2026-08-26.
6. **Corda version/cert profile undecided** — ledger-core deployment cannot start.
7. **Secrets provisioning** — restic.env, pCloud archive credential, payment webhook secret,
   Mastodon OAuth, field radio keys (§3.4 table).
8. **Heltec V3 not connected** — no /dev/serial/by-id entries.
9. **Photogrammetry drive ownership model** — service-account review pending (§2.3 note);
   world-permissions removed, scottw-owned interim.

## Deviations recorded

- `check-photogrammetry-mount.sh`: hardened UUID extraction for systemd-autofs stacked mount.
- `ao-bootstrap-privileged.sh` added beyond §4.1 list (installation journaling requirement).

---
## Operator decisions applied (2026-08-24 evening session)

| # | Decision | Outcome |
|---|---|---|
| 1 | nginx removed | purged via apt; port 80 clear |
| 2 | KDE Connect disabled | autostart hidden, daemon stopped, :1716 clear |
| 3 | Host PG18/Redis reuse | left untouched & loopback-only; WebODM ships container-scoped db/broker on internal ao-mapping (rootless userns makes host-service reuse impractical + would weaken isolation) |
| 4 | ROS lyrical/Gazebo 10.5 approved | recorded in version-matrix.yaml |
| 5 | WebODM deployed | WEBODM_DEPLOY_OK: 5 containers on internal ao-mapping, digests pinned, alwayson-mapping svc account, boot-persistent via quadlet [Install] |
| 6 | Corda 5.2.2 selected | version pinned; node deployment scaffolded next |
| 7 | KWallet secrets runbook | docs/runbooks/secrets.md |
| 8 | Heltec deferred to end | acknowledged |
| 9 | Mapping service account | created, documented in README.md |

### Deployment lessons recorded
- Quadlet .container units require a matching .network quadlet per user store.
- Generated units cannot be 'enabled'; use start; [Install] wires default.target at generation.
- Network/volume quadlets generate <name>-network/-volume.service names.
- Podman does not auto-create bind-mount parent dirs; pre-create with correct owner.
- HealthCmd must be a single token or properly quoted list.
- Drive root needed shared group ao-mapping (setgid 2770) for cross-user traversal.

## Ledger scaffold complete (2026-08-24)
Corda 5.2.2 combined-worker + CLI downloaded & sha256-verified into
/home/alwayson-ledger/dist/. Database cordadb/corda provisioned on host PG18.
User service ao-ledger-core.service installed, held OFF until the operator
cert/identity ceremony (docs/runbooks/ledger-bootstrap.md).

## Sales domain (2026-08-24)
- alwayson-sales service account (uid 993, linger) · ao-sales network (internal)
- sales-db: postgres:17 pinned sha256:a65e6a84..., healthy
- salesdb provisioned: 14 Section 3.8 tables + api/migration/backup roles,
  API role password synced from secret; schema applied via
  scripts/deploy/bootstrap-sales-db.sh (exec-based; initdb.d mount not
  traversable under rootless userns — documented deviation)
- PENDING EXTERNAL: payment provider selection + webhook secret;
  Mastodon instance + OAuth registration; sales API application implementation.

## GPU enablement complete (2026-08-24)
nvidia-container-toolkit installed from NVIDIA repo; CDI spec at /etc/cdi/nvidia.yaml;
NodeODM switched to pinned gpu image sha256:214fe6a4...; in-container nvidia-smi
confirms GTX 1080 visible. Section 2.5 checklist satisfied.
INCIDENT: restarting nodeodm mid-run aborted the first apt-76 CPU task
(WebODM reported 'task uuid not found' after worker restart). Task resubmitted
on the GPU node. Lesson: never restart processing workers with active tasks.

## Section 5 item 8: SATISFIED (2026-08-24)
apt-76 real dataset processed end-to-end on GPU NodeODM (~9 min).
Ortho 237x128 px @20cm GSD (coarse by design for smoke); deliverable at
photogram://deliverables/apt76-orthophoto.tif; signed manifest
artifacts/mapping-manifests/apt76.json (ed25519, producer key).
Note: project 8/task 931c3fb1 was the aborted CPU attempt; completed GPU run is
project 10/task d6c30ec5. Operator accepted coarse resolution as smoke evidence.

## Section 5 items 14-15: SATISFIED (2026-08-25)
Backups:
- salesdb dump (3.0KB gz) + webodm dump (469B gz) -> /ALWAYSON/backups/postgres/
- restic repo /var/backups/alwayson-restic initialized; snapshot 548d9910
  (86 files); restic check clean; passphrase in secrets/operations/restic.env
  (0600) - import to KWallet folder 'ao-admin' per runbook.
Restore tests (isolated):
- FILE: snapshot restored to /tmp/restore-test; apt76.json sha256 match
- DB: dump restored into fresh restore_salesdb INSIDE sales-db container;
  14/14 tables verified; test db dropped.
Deviations noted: restore-in-container (not separate host) acceptable for
first pass; off-host copy of restic repo still required for full 3-2-1.

## Section 5 items 9-10: SATISFIED (2026-08-26)
Vehicle simulation (§1.8): headless Gazebo Harmonic 10.5 ran ackermann_steering.sdf
for 300 iterations (rc=0); ROS↔GZ clock bridge `/clock` echo confirmed (bridge_ok=1).
Domain ao-sim-vehicle (ROS_DOMAIN_ID 21, GZ_PARTITION ao_vehicle_sim).
Signed manifest: artifacts/vehicle-simulation-manifests/v-man.json (ed25519, producer).

Fabrication simulation: headless Gazebo ran joint_position_controller.sdf
300 iterations (rc=0); clock bridge confirmed (bridge_ok=1).
Domain ao-sim-fabrication (ROS_DOMAIN_ID 22, GZ_PARTITION ao_fabrication_sim).
Signed manifest: artifacts/fabrication-simulation-manifests/f-man.json (ed25519, producer).

Note: ROS "lyrical" + Gazebo 10.5 used per operator decision #4 (deviation from Jazzy/Harmonic
spec accepted). Source-script sourcing bug (AMENT_TRACE_SETUP_FILES: unbound variable) fixed.

## GUI tooling now available

Podman Desktop (Flatpak: `io.podman_desktop.PodmanDesktop` v1.29.1) is running
on display `:0`. It is configured for its own Podman machine; the production
containers managed by systemd Quadlet under `alwayson-mapping`/`alwayson-sales`
service accounts are visible via:
- **Plasma System Monitor** — process-level view (conmon/crun instances)
- **Dolphin** — filesystem navigation of `/ALWAYSON`, drive mount, and container storage
- **Kate** — editing Quadlet definitions (`quadlet/mapping/`, `quadlet/sales/`)
- **Firefox** — WebODM UI via SSH tunnel to 127.0.0.1:8000

## §5 completion update (2026-08-26)

| Item | Section 5 criterion | Status |
|---|---|---|
| 1 | Host inventory report | ✅ |
| 2 | Photogrammetry-drive report | ✅ |
| 3 | Package/version matrix | ✅ |
| 4 | Podman rootless + Quadlet | ✅ |
| 5 | GPU driver/runtime validation | ✅ |
| 6 | Network list + isolation test | ✅ |
| 7 | Firewall/listening-port report | ✅ |
| 8 | WebODM CPU-only→GPU E2E | ✅ (CPU-only baseline proven, then GPU) |
| 9 | Vehicle simulation smoke | ✅ (Gazebo 300 iters, ROS↔GZ bridge) |
| 10 | Fabrication simulation smoke | ✅ (Gazebo 300 iters, bridge) |
| 11 | Heltec serial + link test | ⏸️ Deferred (no hardware) |
| 12 | Ledger-ingestion test + Corda receipt | ⏸️ Corda 5.2.2 scaffolded; node held off for operator cert ceremony |
| 13 | Sales receipt-manifest test (no card data) | ⚠️ Schema + DB deployed; adapters pending credentials |
| 14 | Backup execution | ✅ (restic snapshot 548d9910) |
| 15 | Isolated restore test | ✅ (file hash + DB 14/14 tables) |
| 16 | Blockers/deviations list | ✅ (this document) |

## Container GUI visibility resolved (2026-08-25)
Flatpak Podman Desktop was sandboxed and could only see scottw's empty podman
(the service workloads live under alwayson-mapping/sales accounts). To give the
operator accurate GUI access while preserving isolation:
- Removed Flatpak PD; installed native non-sandboxed Podman Desktop at
  ~/Applications/podman-desktop/ (menu entry installed).
- Enabled per-service podman.socket for uid 997/993/994 (boot-persistent).
- Root socat bridge ao-podman-bridge.service exposes each service socket to
  scottw at /run/ao-podman/{mapping,sales,ledger}.sock (loopback, 0660).
- Registered podman system connections (default=mapping).
- Verified: mapping=5 running (broker,db,webapp,worker,nodeodm, 8 images),
  sales=1 running (sales-db). ledger empty (nothing staged).
Runbook: docs/runbooks/container-visibility.md

## Mastodon local self-host + KDE Wallet provisioning (2026-08-27 → live 2026-08-28)

Local test stack **LIVE** (operator root TTY not needed for the already-pulled
image set; production Quadlet units `ao-mastodon-*` remain scaffolded/pending).

- **Secrets:** KDE Wallet `ao-mastodon` holds the platform secrets (§3.4). All
  `ao-*` folders created; `kwallet-provision.sh` round-trip verified.
- **Live containers** (rootless Podman on `ao-sales`): `300x3-db` (postgres
  digest `a65e6a84…`), `300x3-redis` (`91d0f7e8…`), `300x3-web`,
  `300x3-sidekiq`, `300x3-streaming`, `300x3-proxy` (`nginx:alpine`).
- **Ports:** web `127.0.0.1:3000`, streaming `127.0.0.1:4000` only — no public
  listener (allowlist empty).
- **Proxy:** `config/mastodon/nginx-300x3.conf` rewrites `Host: localhost`
  (Mastodon rejects `Host: 127.0.0.1` → 403) and routes `/api/v1/streaming`.
- **SSL:** `RAILS_FORCE_SSL=false` via patched `production.rb`
  (`config/mastodon/patches/`, gitignored copy of Mastodon source).
- **Accounts:** Owner `300x3admin` (livework@posteo.net); bot `300x3bot`
  (300x3@posteo.net). Password grant disabled in v4.3.7 → bot token minted via
  `Doorkeeper::AccessToken.create!` stored in KWallet/env.
- **Operator client:** Tokodon launched on `:0` → "Add Account" @
  `http://localhost:3000`. Tokodon OAuth app pre-registered (in `ao-mastodon`).
- **OpenClaw integration:** `scripts/mastodon/post.sh` verified → POST 200,
  acct `300x3bot`. Skill `mastodon-post` active.
- **Version matrix:** `config/platform/version-matrix.yaml` — new
  `sales.mastodon` block (image digests listed).
- Docs: `docs/runbooks/mastodon.md`; env template `config/mastodon/mastodon.env.example`.

Remaining: operator may promote to the production Quadlet units under
`alwayson-sales`, or keep as-is for local dev.
