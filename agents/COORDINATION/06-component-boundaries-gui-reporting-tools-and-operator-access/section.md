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
of it. Reconciling the YAML is **not** mine to do — it is a config file outside the three
section files I own, and the `ao-egress-community` name/CIDR question is an existing §19.1
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
ao-prometheus              -> ao-prometheus.service
ao-grafana                 -> ao-grafana.service
ao-metabase                -> ao-metabase.service
ao-sim-fabrication-gz      -> ao-sim-fabrication-gz.service
ao-sim-fabrication-foxglove -> ao-sim-fabrication-foxglove.service
vigorous_shannon           -> <none>
dreamy_rosalind            -> <none>
relaxed_tharp              -> <none>
confident_khayyam          -> <none>
keen_bhabha                -> <none>
ao-sqli3                   -> <none>
```

The **conclusion is unchanged** — exactly six running containers have no service owner,
and they are the four Grafana duplicates and the two Foxglove duplicates. But it now
rests on a key that returns a value, and on the whole-container enumeration rather than
on a hand-picked subset. A reader should treat any ownership claim anywhere in this
section that does not show `PODMAN_SYSTEMD_UNIT` as unproven.

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
rows. Two of them also mount host paths that are *not* the sanctioned read-only snapshot
copies: `confident_khayyam` mounts `/tmp/tmp.2HBNsh7zgo:/probe` and `ao-sqli3` mounts
`/tmp/sqli-plugins2:/var/lib/grafana/plugins`, both **writable, both from `/tmp`**, one of them
supplying the unsigned `frser-sqlite-datasource` plugin to a Grafana instance that is not the
one with the allow-list policy.

Mitigating, measured, and worth stating so this is not over-read:

- **No listener is exposed.** `podman port` reports nothing for all four (`map[]`, pasta
  mode), and `ss -ltn` shows no new Grafana port. The only `3000/3001/3002` listeners belong to
  `mastodon-web` (3000), `ao-grafana` (3001) and `ao-metabase` (3002), all loopback-bound.
- **None is privileged**, none is on an `ao-*` network, and none is quadlet-started.

So this is a **conformance and hygiene defect, not an exposure**: unmanaged duplicate GUIs
outside the inventory, two of them writable-mount-bearing. **Not mine to remediate.** Stopping
containers is destructive, touches another group's running work, and the `/tmp` plugin mounts
are the subject of the unsigned-plugin question that §6.A.3 and the OPS group already track.
Recorded here and reported to the operator; no action taken.

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
("nothing has an owner!") and is indistinguishable from "I asked the wrong question." The
correct key is `PODMAN_SYSTEMD_UNIT`, and the self-check is to run it over the whole
container list and confirm that the containers you believe are managed actually come back
with a service name. If every row is empty, the key is wrong, not the fleet.

---
