#!/usr/bin/env python3
"""Export the ALWAYS ON topology model to JSON for Grafana reporting.

Reads the model from ../TOPOLOGY - SINGLE GRAPHIC/build_svg.py (the source of truth) by
executing it and capturing its NODES / BANDS / SECTIONS / EDGES tables. It does
NOT import the rendering code path — build_svg.py writes the SVG as a side effect
of being executed, so the output is discarded and only the data tables are kept.

Usage:
    python3 export_topology_model.py [-o topology-model.json]

Re-run after every edit to build_svg.py and commit both files together.
"""
import argparse
import collections
import contextlib
import importlib.util
import io
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
BUILDER = os.path.join(HERE, os.pardir,
                       "TOPOLOGY - SINGLE GRAPHIC", "build_svg.py")

# Model fields, in the order a consumer should read them.
NODE_FIELDS = ("id", "band", "cls", "title", "purpose", "status", "details",
               "sec", "note")


def load_builder():
    """Execute build_svg.py and return its module, discarding the SVG it emits."""
    if not os.path.isfile(BUILDER):
        sys.exit("builder not found: %s" % BUILDER)
    spec = importlib.util.spec_from_file_location("build_svg", BUILDER)
    mod = importlib.util.module_from_spec(spec)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            spec.loader.exec_module(mod)
    except SystemExit:
        pass  # the builder may call sys.exit on --check; the tables are still set
    return mod


def export(mod):
    """Build the reportable model from the builder's tables."""
    # GRP_MEMBERS maps group -> member bands, so a band's own column has to be
    # found by inverting it (bands 6/7/8 all live in the "prog" group).
    band_col = {bk: g for g, members in mod.GRP_MEMBERS.items() for bk in members}

    bands = []
    for b in mod.BANDS:
        col = band_col.get(b["key"])
        bands.append({
            "n": b["n"],
            "key": b["key"],
            "title": b["title"],
            "purpose": b.get("purpose", ""),
            "column": col,
            "column_members": list(mod.GRP_MEMBERS.get(col, [])),
        })

    sections = []
    for band_key, title, ids, kind in mod.SECTIONS:
        sections.append({
            "band": band_key, "title": title,
            "nodes": list(ids), "kind": kind,
        })

    nodes = []
    for n in mod.NODES:
        row = {k: n.get(k) for k in NODE_FIELDS}
        row["details"] = list(n.get("details", []))
        nodes.append(row)

    edges = [{"source": a, "target": b, "label": lab, "kind": k}
             for a, b, lab, k in mod.EDGES]

    return {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "authority": "/ALWAYSON/README.md  (v6 sections; see sec field)",
        "generated_by": "TOPOLOGY REPORTING - FOR GRAFANA DASHBOARD/"
                        "export_topology_model.py",
        "declared_source": "/ALWAYSON/TOPOLOGY/TOPOLOGY - SINGLE GRAPHIC/"
                            "build_svg.py",
        "observed": False,
        "observed_note": "EXPECTED-TO-BE-INSTALLED plan, not live state. "
                         "Live state lives in topology-inventory.json.",
        "columns": list(mod.GRP_ORDER),
        "bands": bands,
        "sections": sections,
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "nodes": len(nodes),
            "edges": len(edges),
            "bands": len(bands),
            "sections": len(sections),
            "by_status": dict(collections.Counter(n["status"] for n in nodes)),
            "by_class": dict(collections.Counter(n["cls"] for n in nodes)),
            "by_band": dict(collections.Counter(n["band"] for n in nodes)),
            "by_edge_kind": dict(collections.Counter(e["kind"] for e in edges)),
        },
    }


def validate(model):
    """Fail loudly rather than emit a model the dashboard would misread."""
    errs = []
    ids = [n["id"] for n in model["nodes"]]
    if len(ids) != len(set(ids)):
        dup = [i for i, c in collections.Counter(ids).items() if c > 1]
        errs.append("duplicate node ids: %s" % dup)
    band_keys = {b["key"] for b in model["bands"]}
    if any(b["column"] is None for b in model["bands"]):
        errs.append("a band is not assigned to a column group")
    for n in model["nodes"]:
        if n["band"] not in band_keys:
            errs.append("node %s in unknown band %r" % (n["id"], n["band"]))
    placed = [i for s in model["sections"] for i in s["nodes"]]
    if collections.Counter(placed) != collections.Counter(ids):
        errs.append("sections do not cover every node exactly once")
    for e in model["edges"]:
        for end in (e["source"], e["target"]):
            if end not in set(ids):
                errs.append("edge references unknown node %r" % end)
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default=os.path.join(HERE, "topology-model.json"))
    args = ap.parse_args()

    model = export(load_builder())
    errs = validate(model)
    if errs:
        for e in errs:
            print("VALIDATION ERROR: %s" % e, file=sys.stderr)
        sys.exit(1)

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(model, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    s = model["summary"]
    print("wrote %s" % args.out)
    print("  %d nodes, %d edges, %d bands, %d sections"
          % (s["nodes"], s["edges"], s["bands"], s["sections"]))
    print("  by status: %s" % s["by_status"])


if __name__ == "__main__":
    main()
