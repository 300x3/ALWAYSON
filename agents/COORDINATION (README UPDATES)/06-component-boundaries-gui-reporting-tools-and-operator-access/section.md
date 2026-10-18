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
over TCP to the host's `10.42.0.1` on `ao-reporting-egress`; both containers are also on
`ao-admin`. Both are loopback-and-socket scoped, which is why neither needs a public port:
Grafana on `127.0.0.1:3001` and Metabase on `127.0.0.1:3002`, loopback-bound only (`ss -ltn`).

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
  `sales_reporting_role` holds `SELECT` on **five views** and nothing else on `salesdb` —
  `v_reporting_orders`, `v_reporting_receipts`, `v_reporting_entitlements`,
  `v_reporting_sale_provenance`, `v_corda_entry_readiness`. It is not a superuser and has no
  `CREATE`/`CREATEDB`/`CREATEROLE`. It holds no privilege on any base table: reading `orders`
  directly fails with `permission denied for table orders`, while reading `v_reporting_orders`
  succeeds. That is the read-only boundary holding, not merely declared. Note the word
  **views**: the grant is on views owned by `sales_migration_role`, and the underlying tables
  are granted to `sales_api_role` and `sales_backup_role`, never to the reporting role.
  The separate `metabase_app` role exists **only** on the Metabase application database, not on
  `salesdb`, so the reporting path to the business data is `sales_reporting_role`.
  One thing to watch, not a breach: `sales_migration_role` on the same cluster **is** a
  superuser with `CREATEDB` and `CREATEROLE`. That is the migration identity and it is not
  handed to a reporting tool, but any future convenience that grants it to Metabase or
  Grafana would void the read-only boundary above.
  Execution as the reporting role — not a catalog read — is how this is verified:
  a catalog view reports what is *granted*; connecting proves what actually *happens*,
  which is the claim that matters:

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
  authorization bypass. It SHALL carry only narrowly approved local data paths.
- No GUI may add a public listener, broad host networking, unrestricted Podman
  socket access, `--privileged`, shared writable storage, or unrelated-domain
  secret merely to simplify deployment or troubleshooting.
- Any material gap against these boundaries SHALL be recorded in §19.1 with its
  owner and acceptance criteria before a production declaration — no production
  declaration ships with an untracked gap.

The machine-readable inventory that implements this requirement is
`/ALWAYSON/config/platform/gui-boundary-matrix.yaml`.
