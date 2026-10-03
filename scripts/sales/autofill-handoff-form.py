#!/usr/bin/env python3
"""
ALWAYS ON - autofill a PDF form template from a JSON record.

Pure standard library. No network, no database, no Corda, no payment.

    autofill-handoff-form.py <template.html> <record.json> <out.html> [out.pdf]

Placeholders are normal elements carrying a data-* attribute, so the template
stays valid, printable HTML in its own right:

    <span data-f="name">           scalar substitution, HTML-escaped
    <tbody data-rows="items">      replicated once per record["tables"]["items"]
    <span data-yes="field">        gains class .on when the value is truthy
    <span data-on="field">         prints the record value, not its own text

A null or empty value prints an em dash, so an unfilled field is visibly
unfilled rather than silently empty.
"""
import argparse
import html
import json
import re
import subprocess
import sys
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path

EMDASH = "—"
SKIP = {"input", "br", "img", "hr", "meta", "link", "area", "source",
        "param", "track", "wbr", "col", "embed", "base"}

# A placeholder is one element on its own logical unit: <tag ... data-f="x">...</tag>
# where the tag never nests another tag of the same name. Template fields are
# written that way, and requiring it keeps the substitution unambiguous.
FIELD_OPEN = re.compile(
    r'<(?P<tag>[a-zA-Z][\w-]*)(?P<attrs>[^>]*?\bdata-f="(?P<field>[^"]+)"[^>]*?)>'
)


def replace_fields(doc: str, values: dict, used: set, skip: set = ()) -> str:
    """Substitute the inner text of each data-f element with a record value.

    The closing tag is taken from the SAME LINE as the opening tag. A
    placeholder is written as one line, and searching forward for the first
    "</span>" anywhere would run past the element and eat the rest of the
    table whenever a neighbouring cell holds a sentinel span.

    Fields named in `skip` are left untouched, which is how already-filled
    table rows survive the later scalar pass.
    """
    out, pos = [], 0

    for match in FIELD_OPEN.finditer(doc):
        if match.start() < pos:
            continue
        tag = match.group("tag")
        field = match.group("field")
        close = "</%s>" % tag

        line_end = doc.find("\n", match.end())
        if line_end == -1:
            line_end = len(doc)
        end = doc.find(close, match.end(), line_end)
        if end == -1:
            continue

        out.append(doc[pos:match.start()])
        if field in skip:
            # Already carries its own row's value; copy it through untouched.
            out.append(doc[match.start():end + len(close)])
        else:
            used.add(field)
            out.append(
                f'<{tag}{match.group("attrs")}>{esc(values.get(field))}{close}'
            )
        pos = end + len(close)

    out.append(doc[pos:])
    return "".join(out)


def esc(value) -> str:
    """Render a record value as display text, never as markup."""
    if value is None:
        return EMDASH
    if isinstance(value, bool):
        return "yes" if value else "no"
    text = str(value)
    return html.escape(text) if text.strip() else EMDASH


def truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() not in ("", "no", "false", "0", "null")


class Filler:
    def __init__(self, source: str):
        self.src = source
        self.used: set = set()
        self.row_fields: set = set()

    def scalars(self, doc: str, data: dict) -> str:
        """Substitute the scalar data-f placeholders.

        Fields belonging to a generated table row are skipped entirely:
        rows() has already given them their per-row values, and the top-level
        record has no key for an item_* field, so substituting here would
        blank every row back to an em dash.
        """
        return replace_fields(doc, data, self.used, skip=self.row_fields)

    @staticmethod
    def row_regions(doc: str) -> list:
        """Spans of the document occupied by generated table rows."""
        return [
            (m.start(), m.end())
            for m in re.finditer(
                r'<tbody[^>]*data-rows="[^"]*"[^>]*>.*?</tbody>', doc, re.S
            )
        ]

    @staticmethod
    def in_row(spans: list, field: str, doc: str) -> bool:
        for match in FIELD_OPEN.finditer(doc):
            if match.group("field") == field and any(
                start <= match.start() < end for start, end in spans
            ):
                return True
        return False

    def flags(self, doc: str, data: dict) -> str:
        """Apply the class toggle and value-printing placeholders."""
        def on_off(m):
            klass = m.group(1)
            field = m.group(3)
            self.used.add(field)
            new = f"{klass} on" if truthy(data.get(field)) else klass
            return f'class="{new}"{m.group(2)}>'

        doc = re.sub(
            r'class="([^"]+)"([^>]*\bdata-yes="([^"]+)"[^>]*)>', on_off, doc
        )

        def print_value(m):
            field = m.group(3)
            self.used.add(field)
            return f'class="{m.group(1)}" data-on="{field}">{esc(data.get(field))}<'

        return re.sub(
            r'class="([^"]+)"([^>]*\bdata-on="([^"]+)"[^>]*)>[^<]*<', print_value, doc
        )

    def rows(self, doc: str, name: str, data: list) -> str:
        """Replicate each <tbody data-rows="name"> once per row."""
        pattern = re.compile(
            r'(<tbody[^>]*data-rows="%s"[^>]*>)(.*?)(</tbody>)' % re.escape(name),
            re.S,
        )
        match = pattern.search(doc)
        if not match:
            return doc

        template = match.group(2)
        # data-f sits on a span inside each cell, not on the td itself.
        fields = re.findall(r'data-f="([^"]+)"', template)
        for field in fields:
            self.used.add(field)
            self.row_fields.add(field)

        # Per-row sentinels: a repeating table needs a distinct id per cell,
        # or every row's click lands on the same field. Ids are built as
        # <base>*1000 + row*10 + column, which stays unambiguous because each
        # token is matched as a whole delimited string, never by prefix.
        cell_tokens = re.findall(r'@@F(\d+)@@', template)

        rendered = []
        for index, row in enumerate(data or [], start=1):
            block = template
            for position, token in enumerate(cell_tokens, start=1):
                block = re.sub(
                    r"@@F%s@@" % token,
                    "@@F%d@@" % (int(token) * 1000 + index * 10 + position),
                    block,
                )
            for field in fields:
                self.used.add(field)
            # Each clone carries its own row's values, substituted with the
            # same routine scalars() uses so the two cannot drift.
            block = replace_fields(block, row, self.used)
            rendered.append(block)

        body = "".join(rendered) or template
        return doc[: match.start()] + match.group(1) + body + match.group(3) + doc[match.end():]

    def build(self, data: dict) -> str:
        # Rows expand first: scalar substitution would otherwise rewrite the
        # template's placeholder cells before they are cloned per row.
        doc = self.flags(self.src, data)
        for name, rows in (data.get("tables") or {}).items():
            doc = self.rows(doc, name, rows)
        return self.scalars(doc, data)


def inline_css(document: str, css_path: Path) -> str:
    """Embed the stylesheet so the rendered PDF needs no sibling files."""
    if not css_path.is_file():
        print(f"ERROR: stylesheet not found: {css_path}", file=sys.stderr)
        raise SystemExit(2)
    css = css_path.read_text(encoding="utf-8")
    # Drop any <link> to an external stylesheet: relative links break once the
    # filled form is written somewhere else, which is how this shipped once.
    document = re.sub(
        r'<link[^>]*rel="stylesheet"[^>]*>', "", document, flags=re.I
    )
    return document.replace(
        "</head>", f"<style>\n{css}\n</style>\n</head>", 1
    )


def render_pdf(html_path: Path, pdf_path: Path, chrome: str) -> bool:
    cmd = [
        chrome, "--headless", "--disable-gpu", "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path.resolve()}",
        html_path.resolve().as_uri(),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR: cannot run {chrome}: {exc}", file=sys.stderr)
        return False
    if result.returncode != 0 or not pdf_path.exists():
        print("ERROR: PDF render failed", file=sys.stderr)
        print((result.stderr or "")[-1500:], file=sys.stderr)
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("template")
    ap.add_argument("record")
    ap.add_argument("out_html")
    ap.add_argument("out_pdf", nargs="?")
    ap.add_argument("--chrome", default="google-chrome")
    ap.add_argument(
        "--css",
        help="inline this stylesheet into the output; overrides any <link> in "
             "the template, so the printed PDF is self-contained",
    )
    args = ap.parse_args()

    template, record_path = Path(args.template), Path(args.record)
    for path in (template, record_path):
        if not path.is_file():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            return 2

    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {record_path}: {exc}", file=sys.stderr)
        return 2
    if not isinstance(record, dict):
        print("ERROR: record must be a JSON object", file=sys.stderr)
        return 2

    filler = Filler(template.read_text(encoding="utf-8"))
    document = filler.build(record)

    if args.css:
        document = inline_css(document, Path(args.css))

    out_html = Path(args.out_html)
    out_html.write_text(document, encoding="utf-8")

    unused = sorted(k for k in record if k != "tables" and k not in filler.used)
    for key in unused:
        print(f"WARNING: record key '{key}' is not used by the template", file=sys.stderr)

    if args.out_pdf:
        out_pdf = Path(args.out_pdf)
        if not render_pdf(out_html, out_pdf, args.chrome):
            return 3
        print(f"OK: {out_pdf}")
    print(f"OK: {out_html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())