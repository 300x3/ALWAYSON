# TOPOLOGY

Working topology documents. This folder is the home for the live diagram set
and the reporting inputs. It is referenced by the main `README.md`.

## Layout

| Folder | What it is | Status |
|---|---|---|
| `TOPOLOGY - SINGLE GRAPHIC/` | **The authoritative one-page diagram** and its source | **Current — regenerate this** |
| `TOPOLOGY - REPORTING, FOR GRAFANA DASHBOARD/` | Model exported to JSON for Grafana | **Current — depends on the single graphic** |
| `TOPOLOGY - ARCHIVE/` | Superseded output and review notes | Historical. Do not use as authority |

## Which file is which

**`alwayson-single-topology.svg` is the working file.** It is the canonical
diagram: every other format in this folder is a rendering of it, and the
`README.md` images and the published viewer are all copies of that rendering.
When you need the diagram itself — to read it at full resolution, to check a
card, to open it in Inkscape, or to see what a change did — open the **SVG**.

**`.png` and `.html` are outputs, not sources.** They are produced *from* the
SVG — the PNG and PDF are rendered from it with Inkscape, and the HTML embeds
it inline — and must never be edited to change the diagram:

| File | Role | Notes |
|---|---|---|
| `alwayson-single-topology.svg` | **The working file** | Canonical. The thing everything else is generated from |
| `alwayson-single-topology.png` | Output | Raster of the SVG. Needed because GitHub does not render SVG inline |
| `alwayson-single-topology-left.png` / `-right.png` | Outputs | Crops of the rendered PNG, split at the seam |
| `alwayson-single-topology.html` | Output | The SVG embedded in a self-contained viewer |
| `alwayson-single-topology.pdf` | Output | For print |
| `alwayson-single-topology.json` | Output | Machine contract for the Grafana reporting chain |
| `bands/` | Outputs | One reflowed zoom page per band, from the same SVG |

If the SVG and a PNG ever disagree, **the SVG is correct** — fix the SVG, then
regenerate. Editing a `.png` or the `.html` directly is the mistake that this
note exists to prevent, because the next `build_svg.py` run silently discards it.

To change the diagram, edit `build_svg.py` (below) and re-run it; it rewrites
the SVG first and the outputs after it.

## TOPOLOGY - SINGLE GRAPHIC — the source of truth

`build_svg.py` is the only file to edit by hand. Everything else in that folder
is generated from it, so editing a generated file directly will be overwritten
on the next run.

```bash
cd "/ALWAYSON/TOPOLOGY/TOPOLOGY - SINGLE GRAPHIC" && python3 build_svg.py
```

Writes `alwayson-single-topology.svg` **first**, then the `.png`, the two
portrait `-left` / `-right` panels, `.pdf`, `.html`, `.json`, and `bands/` from
it. Run the exporter below afterwards so the two cannot drift.

Set `ALWAYSON_TOPO_OUT` to write the output somewhere else; by default it is
written next to the script.

### The fold

The two portrait panels are cut at the seam the viewer's **Seam** button points
at, so the viewer and the paper fold in the same place. The seam scan refuses
to cut through a card, a text run, or the interior of a band column, and
prefers the corridor immediately left of a column box. It currently selects
**svg x=3299**, the gutter just left of the section 4 *Stores and reporting*
column, so every band stays whole in one half.

## TOPOLOGY - REPORTING, FOR GRAFANA DASHBOARD

```bash
cd "/ALWAYSON/TOPOLOGY/TOPOLOGY - REPORTING, FOR GRAFANA DASHBOARD"
python3 export_topology_model.py
```

Reads the model out of `build_svg.py` and rewrites `topology-model.json`
(66 nodes, 81 edges, 9 bands). The dashboard JSON must not be hand-edited.

## TOPOLOGY - ARCHIVE

Superseded material, kept for the record only. These are the earlier
per-topic sheets (`alwayson-system-topology`, `alwayson-databases`,
`alwayson-host-software`, `alwayson-workload-networks`,
`alwayson-field-and-edge`), a `TOPOLOGY.md`, `LIVE-LINKS.md`, and some review
notes and `trace-*.png` captures.

Most of it predates the single graphic and does **not** reflect the current
model. Where the archive and `TOPOLOGY - SINGLE GRAPHIC` disagree, the single
graphic governs. Nothing in here is regenerated.
