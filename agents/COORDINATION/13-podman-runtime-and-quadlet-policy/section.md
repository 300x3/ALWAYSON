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
their output are in `agents/COORDINATION/proposals/plat-PLAT-01.md`.

| Question | Measured answer |
|---|---|
| Is the operator Podman rootless? | `podman info --format '{{.Host.Security.Rootless}}'` → `true` |
| Which store backs it? | `podman info --format '{{.Store.GraphRoot}}'` → `/home/scottw/.local/share/containers/storage` |
| Do any Quadlet units name a `User=` or `Group=`? | none — `grep -rn '^User=\|^Group=' quadlet/` returns nothing |
| Are there system-level `.container` units? | `systemctl list-unit-files 'ao-webodm*' \| grep -c '^ao-'` → `0`; every mapping unit is `systemctl --user`, state `generated` (Quadlet generator output) |
| Are the WebODM containers in the operator store? | `podman ps` lists `ao-webodm-{webapp,worker,db,broker}` and `ao-nodeodm` from the rootless store above |
| Are the declared extra connections real? | `podman system connection list` → header only; `~/.config/containers/podman-connections.json` is `{"Connection":{},"Farm":{}}` |
| Does `/run/ao-podman/` exist? | `ls /run/ao-podman` → `No such file or directory` |
| Is `ao-podman-bridge.service` active? | `systemctl is-enabled ao-podman-bridge.service` → `disabled`; `systemctl --user is-enabled` → `not-found` |

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
| `/var/lib/containers/storage` | exists, `db.sql` last written 2026-09-30 | **OPEN** — see below |

**Deviation.** The host carries three unused service accounts and one disabled system unit
that this design does not authorise. They hold no container store, no socket and no process,
so the single-store designation above is unaffected. They are **left in place**: removing an
account or a unit file is a deletion, and README §4.1 rule 3 requires explicit operator
approval. **This is an OPEN item for the operator**, not a defect in the running system.

**OPEN — the rootful store could not be enumerated.** `/var/lib/containers/storage` exists
and its `db.sql` was modified 2026-09-30, so something has written to it. Its contents are
`drwx------ root root` and `sudo` on this host requires interactive authentication, so
`sudo ls /var/lib/containers/storage/overlay-images/` returned `Permission denied`. **This
document therefore claims the system store is *unused by any workload*, not that it is
*empty*.** The distinction matters: a stale image or container left in the rootful store is
not a workload, but it is data an operator may want reclaimed. Enumerating it needs one
`sudo` command and operator approval — recommended action, no automatic action taken.

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
