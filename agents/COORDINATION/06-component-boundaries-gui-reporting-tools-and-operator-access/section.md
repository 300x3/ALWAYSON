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

So §5.1 group D (18 rows, counted) is the current statement, and the YAML is a lagging subset
of it. Reconciling the YAML is **not** mine to do — it is a config file outside the three
section files I own, and the `ao-egress-community` name/CIDR question is an existing §19.1
item belonging to another group. This subsection records the gap so the next reader is not
misled.

---
