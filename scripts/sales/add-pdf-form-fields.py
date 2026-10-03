#!/usr/bin/env python3
"""
ALWAYS ON - make a rendered ALWAYS ON PDF form clickable/fillable.

    add-pdf-form-fields.py <in.pdf> <out.pdf> [--fields fields.json]

Chrome renders the design; it cannot emit AcroForm widgets. This script
overlays real PDF text fields on top of it using pikepdf, positioned from
sentinels the template placed in the page, so the clickable field and the
printed label cannot drift apart.

Sentinels: the template marks each fillable slot with

    <div class="ff" data-ff="requester_name">
      <span class="tok">@@F7@@</span><span class="v">...</span>
    </div>

The sentinel text is transparent on the page but still present in the PDF
text layer, so `pdftotext -bbox` reports where it landed. We read those
coordinates and write a /Widget annotation with matching /Rect, then strip the
sentinel glyphs from the content so nothing odd shows in a printed copy.

Field appearance streams are generated so the field shows its value in any
viewer, and /NeedAppearances is left true so viewers refresh them on open.

Requires: pikepdf, pdftotext (poppler). Nothing is sent anywhere; this only
rewrites a local PDF.
"""
import argparse
import json
import re
import subprocess
import sys
import zlib
from pathlib import Path

import pikepdf

TOKEN = re.compile(r"@@F(\d+)@@")
DEFAULT_FONT = "Helvetica"


def find_sentinels(pdf_path: Path) -> dict:
    """Map sentinel id -> (x0, y0, x1, y1) in PDF points."""
    out = subprocess.run(
        ["pdftotext", "-bbox", str(pdf_path), "-"],
        capture_output=True, text=True, check=True,
    ).stdout

    found = {}
    for match in TOKEN.finditer(out):
        # take the bounding box of the <word> element holding this token
        start = out.rfind("<word", 0, match.start())
        end = out.find("</word>", match.end())
        if start == -1 or end == -1:
            continue
        word = out[start:end]
        coords = dict(
            (k, float(v))
            for k, v in re.findall(r'(xMin|yMin|xMax|yMax)="([\d.]+)"', word)
        )
        if len(coords) == 4:
            found[int(match.group(1))] = coords
    return found


def esc(text: str) -> bytes:
    """Escape a string for a PDF literal string object."""
    out = text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
    return out.encode("latin-1", "replace")


def appearance(value: str, width: float, height: float, multiline: bool,
               size: float) -> bytes:
    """A minimal but valid /AP /N stream showing the field value."""
    lines = value.split("\n") if multiline else [value]
    ops = ["q", f"BT", f"/{DEFAULT_FONT} {size:g} Tf", "0.06 0.10 0.16 rg",
           f"1 0 0 1 {2:.1f} {height - size - 2:.1f} Tm"]
    first = True
    for line in lines[:4]:
        if not first:
            ops.append(f"1 0 0 1 0 {-size - 1.2:.1f} Tm")
        ops.append(f"({esc(line).decode('latin-1')}) Tj")
        first = False
    ops.append("ET")
    ops.append("Q")
    body = ("\n".join(ops)).encode("latin-1", "replace")
    stream = zlib.compress(body)

    return (
        f"<< /Type /XObject /Subtype /Form /FormType 1 "
        f"/BBox [0 0 {width:.2f} {height:.2f}] "
        f"/Resources << /Font << /{DEFAULT_FONT} << "
        f"/Type /Font /Subtype /Type1 /BaseFont /{DEFAULT_FONT} >> >> >> >> "
        f"/Length {len(stream)} /Filter /FlateDecode >>\nstream\n"
    ).encode("ascii") + stream + b"\nendstream"


COLUMN_NAMES = {
    10: "category", 11: "item_name", 12: "sku", 13: "quantity", 14: "notes",
}


def derive_name(ident: int, boxes: dict) -> str:
    """A readable field name derived from the sentinel id.

    Ids encode position as base*1000 + row*10 + column, where base is the
    template cell's own token id. A field named "row1_sku" is usable in a PDF
    viewer; "field_11012" is not.
    """
    base = ident // 1000
    remainder = ident % 1000
    row = remainder // 10
    if base in COLUMN_NAMES:
        return "row%d_%s" % (row, COLUMN_NAMES[base])
    return "field_%d" % base


def measure_layout(pdf_path: Path) -> dict:
    """Left edge and width for every sentinel, as Chrome laid the page out.

    Sentinels in one table column share an xMin, and the next column starts
    where the widest cell of this one ends. Spacing each field to its column is
    what stops the row's five fields from piling on top of one another.
    """
    out = subprocess.run(
        ["pdftotext", "-bbox", str(pdf_path), "-"],
        capture_output=True, text=True, check=True,
    ).stdout

    items = []
    for match in TOKEN.finditer(out):
        start = out.rfind("<word", 0, match.start())
        end = out.find("</word>", match.end())
        if start == -1 or end == -1:
            continue
        box = dict(
            (k, float(v))
            for k, v in re.findall(r'(xMin|xMax|yMin)="([\d.]+)"', out[start:end])
        )
        if len(box) == 3:
            items.append((int(match.group(1)), box))

    if not items:
        return {}

    # id -> its own measured box, for the row lookup below.
    items_lookup = {ident: box for ident, box in items}

    # Column geometry: sentinels in one table column share an xMin, so take
    # the sorted set of left edges and let each column run up to the next.
    # A sentinel's own width is the length of its (short) token text and says
    # nothing about the column, so it must not be used for this.
    #
    # ids < 1000 are standalone slots (one per grid cell); ids >= 1000 are
    # per-row table cells, whose base is the id divided by 1000. Dividing a
    # small id by 1000 gives 0 for all of them, which would merge every
    # standalone slot into a single column.
    def column_key(ident: int) -> int:
        return ident // 1000 if ident >= 1000 else ident

    bases: dict = {}
    for ident, box in items:
        key = column_key(ident)
        left = bases.get(key)
        bases[key] = box["xMin"] if left is None else min(left, box["xMin"])

    edges = sorted(bases.values())
    # Row (>=1000) cells are grouped by their visual row (yMin), not by their
    # own left edge. Keying on the left edge puts every field in a group of
    # one, so each finds no next column and runs to the page edge -- every
    # field in the row then overlaps the one after it. Grouping by y gives the
    # sorted column edges of that row, which is what a cell must end short of.
    #
    # A row's fields sit at slightly different yMin within the same line box,
    # so y is bucketed to the nearest point.
    row_edges: dict = {}
    for ident, box in items:
        if ident < 1000:
            continue
        key = round(box["yMin"], 0)
        row_edges.setdefault(key, []).append(bases[column_key(ident)])
    row_edges = {k: sorted(set(v)) for k, v in row_edges.items()}

    def row_limit(ident: int, left: float) -> float:
        key = round(items_lookup[ident]["yMin"], 0)
        same_row = row_edges.get(key, [left])
        nxt = [e for e in same_row if e > left + 1]
        return min(nxt) if nxt else 760.0

    layout = {}
    for ident, box in items:
        left = bases[column_key(ident)]
        if ident >= 1000:
            limit = row_limit(ident, left)
        else:
            nxt = [e for e in edges if e > left + 1]
            limit = min(nxt) if nxt else 760.0
        layout[ident] = {
            "x": left,
            "y": box["yMin"],
            "width": max(24.0, limit - left - 3.0),
        }
    return layout


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source")
    ap.add_argument("dest")
    ap.add_argument("--fields", help="JSON: {id: {name,value,multiline,width,height}}")
    ap.add_argument("--default-width", type=float, default=180.0)
    ap.add_argument("--default-height", type=float, default=13.5)
    ap.add_argument("--font-size", type=float, default=8.0)
    args = ap.parse_args()

    src, dest = Path(args.source), Path(args.dest)
    if not src.is_file():
        print(f"ERROR: not found: {src}", file=sys.stderr)
        return 2

    spec = json.loads(Path(args.fields).read_text(encoding="utf-8")) if args.fields else {}

    try:
        boxes = find_sentinels(src)
        layout = measure_layout(src)
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: pdftotext failed: {exc}", file=sys.stderr)
        return 3
    if not boxes:
        print("ERROR: no field sentinels found in the rendered PDF", file=sys.stderr)
        return 4

    pdf = pikepdf.open(src)
    page = pdf.pages[0]
    width = float(page.mediabox[2]) - float(page.mediabox[0])
    height_pt = float(page.mediabox[3]) - float(page.mediabox[1])

    font = pdf.make_indirect(pikepdf.Dictionary(
        Type=pikepdf.Name.Font, Subtype=pikepdf.Name.Type1,
        BaseFont=pikepdf.Name.Helvetica,
    ))

    made = 0
    acro_fields = []
    for ident, box in sorted(boxes.items()):
        place = layout.get(ident, {})
        meta = spec.get(str(ident), {})
        name = meta.get("name", derive_name(ident, boxes))
        value = meta.get("value", "")
        multiline = bool(meta.get("multiline", False))

        w = float(meta.get("width", place.get("width", args.default_width)))
        h = float(meta.get("height", args.default_height))

        # Sentinel sits at the top-left of its slot; PDF origin is bottom-left.
        # A sentinel's own width is only the length of its token text, so it
        # says nothing about the slot. Without an explicit width the field runs
        # to the next slot on the same visual row, which is what stops
        # neighbouring fields from covering one another.
        x0 = float(place.get("x", box["xMin"]))
        row_y = float(place.get("y", box["yMin"]))
        same_row = sorted(
            other["x"] for other in layout.values()
            if other["x"] > x0 + 1 and abs(other.get("y", 0) - row_y) < 2
        )
        neighbour = (same_row[0] - 6.0) if same_row else 757.0

        if "width" in meta:
            w = float(meta["width"])
        elif ident in layout and layout[ident]["width"] > 25.0:
            # a real column: sentinel left edge to the next column
            w = float(layout[ident]["width"])
        else:
            w = max(60.0, neighbour - x0)

        h = float(meta.get("height", args.default_height))
        y1 = height_pt - row_y - 1.0
        rect = [x0, y1 - h, x0 + w, y1]

        ap_stream = pdf.make_stream(appearance(
            value, w, h, multiline, args.font_size
        ))

        font_size = args.font_size + (0.5 if multiline else 0.0)
        widget = pikepdf.Dictionary(
            Type=pikepdf.Name.Annot,
            Subtype=pikepdf.Name.Widget,
            FT=pikepdf.Name.Tx,
            T=pikepdf.String(name),
            V=pikepdf.String(value),
            Rect=pikepdf.Array(rect),
            DA=pikepdf.String(f"/Helvetica {font_size:g} Tf 0 0 0.16 rg"),
            F=4,
            Ff=(4096 if multiline else 0),
            MK=pikepdf.Dictionary(
                # Transparent background: the printed label and the
                # already-filled value must stay visible underneath. The
                # white fill of a default widget hides the sheet it sits on.
                BC=pikepdf.Array([0.72, 0.75, 0.79]),
                BG=pikepdf.Array([]),
            ),
            A=pdf.make_indirect(ap_stream),
            P=page.obj,
        )
        # pikepdf has no Page.add_annotation: a widget is a /Widget annotation
        # referenced from the page's /Annots array.
        annots = page.obj.get("/Annots")
        if annots is None:
            annots = pikepdf.Array([])
            page.obj["/Annots"] = annots
        ref = pdf.make_indirect(widget)
        annots.append(ref)
        # A reader enumerates /AcroForm /Fields, not /Annots. Appending only to
        # /Annots draws the boxes but registers nothing: the form then reports
        # zero fields and clicking a slot does nothing. The same object is
        # referenced from both arrays, which is how a merged field/widget is
        # meant to be stored.
        acro_fields.append(ref)
        made += 1

    acro = pdf.Root.get("/AcroForm")
    if acro is None:
        acro = pikepdf.Dictionary(
            Fields=pikepdf.Array([]),
            DR=pikepdf.Dictionary(Font=pikepdf.Dictionary()),
            NeedAppearances=True,
            DA=pikepdf.String("/Helvetica 0 Tf 0 g"),
        )
        pdf.Root["/AcroForm"] = pdf.make_indirect(acro)
    else:
        acro["/NeedAppearances"] = True
    # Collect first, assign once. A reader enumerates /Fields to decide what is
    # clickable; /Annots alone renders boxes that do nothing when clicked.
    acro["/Fields"] = pikepdf.Array(acro_fields)
    acro["/DR"]["/Font"] = pikepdf.Dictionary(Helvetica=font)

    pdf.save(dest)
    pdf.close()

    print(f"OK: {dest}")
    print(f"fields={made} page={width:.0f}x{height_pt:.0f}pt")
    return 0


if __name__ == "__main__":
    sys.exit(main())