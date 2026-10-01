# Grafana mapping — model field → dashboard concept

How `topology-model.json` maps onto the existing dashboard at
`../grafana-dashboard.json` (uid `alwayson-topology`, schema 39, provisioned by
`../grafana-provider.yml` from `/etc/grafana/provisioning/dashboards`).

## The one rule that matters most

**This model is a plan, not telemetry.** Every node is
EXPECTED-TO-BE-INSTALLED. The graphic's own authority line says so, and the
export sets `"observed": false`.

So `status` describes *design intent*, and a panel must not render it as a live
health signal with thresholds and alert colouring. Doing so would report
"4 BLOCKED" as though four services were failing right now — which is a
different and wrong claim. The four blocked nodes are blocked by a planned
dependency (notably the Corda key/certificate ceremony, README v6 §18.3).

Live state, when the dashboard needs it, comes from
`../topology-inventory.json`, which is generated from README-authoritative
declarations plus live inspection. That file carries `observed: true` and
timestamps. Keep the two apart.

## Status → colour, for *plan* panels only

| status | count | Suggested node colour | Reading |
|---|---|---|---|
| `IMPLEMENTED` | 33 | green / `ok` | built and in place |
| `IN PROGRESS` | 8 | amber / `warning` | partly built |
| `PARTIAL` | 1 | amber / `warning` | built, incomplete scope |
| `PLANNED` | 12 | blue / `info` | design, not live |
| `BLOCKED` | 4 | red / `error` | **waiting on a named dependency** |

If any of these panels ever gains alert rules, scope them to the inventory
datasource, not this one.

## Class → node group

`cls` is the better grouping key for panels than `band`, because a class can
span bands (`work` appears in band 3 and again inside band 9).

| `cls` | count | meaning |
|---|---|---|
| `ext` | 6 | outside world — not ours |
| `adp` | 6 | controller adapters — the only doors |
| `work` | 16 | workload domains |
| `ledger` | 4 | ledger / manifest chain |
| `data` | 9 | stores and reporting |
| `hw` | 2 | hardware |
| `rf` | 2 | radio |
| `host` | 12 | host-local software |
| `sec` | 1 | secrets on this host |

## Edge kind → edge styling

The graphic already encodes meaning in edge weight; carry it into the graph
panel rather than re-deriving it.

| kind | count | style | meaning |
|---|---|---|---|
| `ok` | 34 | green solid | approved, mTLS, signed, audited |
| `normal` | 23 | grey dashed | ordinary internal |
| `rf` | 3 | amber heavy | radio, no IP |
| `no` | 8 | red dotted | **prohibited by v6 §4.3** |

The 8 `no` edges are the highest-value thing on the dashboard: they are declared
prohibitions, so a panel that lists them is a standing reminder of what must not
be built.

## Node → nodeGraph fields

Mapping for a `nodeGraph` panel built from this model:

| Grafana field | Source |
|---|---|
| `id` | `node.id` (stable — never renumber) |
| `title` | `node.title` |
| `subTitle` | `node.purpose` |
| `mainStat` | `node.status` |
| `secondaryStat` | `node.sec` (authority reference) |
| `detail__` | `node.details` joined with ` · ` |
| `status` | mapped from `status` per the table above |

For edges: `mainStat` = `edge.label`, `secondaryStat` = `edge.kind`.

Band membership is useful for **layout, not for content** — bands are visual
columns in the graphic, and Grafana's nodeGraph does its own layout. Use `cls`
for grouping and keep `band` available for a table panel or an annotation.

## Panels this model supports well

- **Status roll-up** — stat panel, counts per `status`. Label it "plan state".
- **Declared-by-band** — bar gauge, `by_band` in the summary block.
- **Blocked and why** — table of the 4 `BLOCKED` nodes with their `note`. These
  notes ("Blocked on the Corda key/certificate ceremony (18.3)") are the single
  most actionable field in the model.
- **Prohibited paths** — table of the 8 `no` edges, source → target.
- **Authority coverage** — table of `sec` values, for checking that components
  cite v6 sections.
- **Full graph** — `nodeGraph` per the field mapping above.

## Panels it does *not* support

Anything time-series. This model has no timestamps per node and no measurements.
A trend line over `status` would be meaningless — status changes only when
someone edits `build_svg.py`. For rates and history, use the Prometheus
datasource (`${DS_PROMETHEUS}`) that the existing stat panels already use, or the
inventory file's `generated_at_utc`.

## Refresh

`grafana-provider.yml` sets `updateIntervalSeconds: 30` and
`allowUiUpdates: true`, with `disableDeletion: true`. That re-reads the
provisioned JSON from disk; it does **not** re-run `export_topology_model.py`.
The model only changes when the exporter is run and the file committed, so the
dashboard is stable between exports by design.
