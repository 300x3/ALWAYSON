# ALWAYS ON — topology artifacts and live links

Generated `2026-09-29T04:37:11Z` from `/ALWAYSON/README.md` declarations plus live inspection.
Regenerate with `python3 /ALWAYSON/scripts/operations/generate-topology.py`.

## Diagram and documents (this folder)

| File | What it is |
|---|---|
| `alwayson-system-topology.svg` | Vector diagram — open in a browser or Inkscape |
| `alwayson-system-topology.png` | Raster diagram, 144 dpi |
| `alwayson-system-topology.html` | Self-contained diagram + full inventory tables |
| `alwayson-system-topology.dot` | Graphviz source |
| `topology-inventory.json` | Machine-readable inventory (declared + live + drift) |
| `TOPOLOGY.md` | Markdown inventory tables |
| `grafana-dashboard.json` | Grafana dashboard definition (provisioned copy) |
| `grafana-provider.yml` | Grafana file-provider definition (provisioned copy) |
| `alwayson-workload-networks.html` | Companion sheet — see its `.svg` / `.png` / `.dot` |
| `alwayson-host-software.html` | Companion sheet — see its `.svg` / `.png` / `.dot` |
| `alwayson-field-and-edge.html` | Companion sheet — see its `.svg` / `.png` / `.dot` |

## Live loopback links

| Service | URL |
|---|---|
| Grafana — ALWAYS ON system topology dashboard | http://127.0.0.1:3001/d/alwayson-topology/alwayson-system-topology |
| Grafana root | http://127.0.0.1:3001 |
| Prometheus | http://127.0.0.1:9090 |
| Metabase | http://127.0.0.1:3002 |

All operator listeners are loopback-only by policy (v6 §4.1 rule 6 and `config/platform/listener-allowlist.yaml`); Grafana requires an operator login. No public port is opened by these links.

## This run

- Networks: 15 (12 live)
- Containers: 16 declared, 13 running
- Listeners observed: 77 (31 loopback, 27 non-loopback)
- Drift items: 2
