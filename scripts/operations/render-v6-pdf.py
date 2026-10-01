#!/usr/bin/env python3
"""Render the ALWAYS ON v6 Markdown to a self-contained HTML file for WeasyPrint.

Supports only the constructs the v6 document actually uses: headings,
paragraphs, blockquotes, fenced code blocks, ordered/unordered lists, pipe
tables, and horizontal rules. Inline `code`, **bold**, *italic* are handled.

Nothing is executed or fetched; the output is fully self-contained so the PDF
never depends on network access.
"""

import base64
import html
import re
import struct
import sys
from pathlib import Path

CODE_LANGS = {"text", "bash", "yaml", "json", "sql", ""}

# Topology sheets are laid out rankdir=LR, so most are very tall and narrow while
# the database sheet is very wide. Neither fits a portrait text page at a
# readable size, so wide sheets are given their own landscape page.
WIDE_SHEET_RATIO = 1.4


def png_size(path):
    """Return (width, height) from a PNG IHDR chunk, or None if not a PNG.

    Reads the header directly so the renderer needs no image library.
    """
    try:
        with path.open("rb") as fh:
            head = fh.read(24)
    except OSError:
        return None
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", head[16:24])


def inline(text):
    """Escape first, then apply inline markdown, so markup introduced by a
    later substitution is not double-escaped."""
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", out)
    out = re.sub(r"(?<![\w_])_([^_\n]+)_(?![\w_])", r"<em>\1</em>", out)
    return out


def resolve_asset(base, rel):
    """Resolve an asset path relative to the Markdown file, then relative to
    its parent directories. The v6 document sits in TOPOLOGY/ but references
    assets/ at the repository root, so a plain relative join is not enough."""
    for candidate in (base, *base.parents):
        path = (candidate / rel).resolve()
        if path.is_file():
            return path
    return None


def figure(src_line, base):
    """Handle a standalone ![alt](path) line, resolving the path relative to
    the Markdown file. The image is inlined as base64 so the HTML stays
    self-contained and WeasyPrint never reads from disk or network."""
    m = re.match(r"^!\[([^\]]*)\]\(([^)\s]+)\)\s*$", src_line.strip())
    if not m:
        return None
    alt, rel = m.group(1), m.group(2)
    if re.match(r"^[a-z]+://", rel):
        return '<p class="image-missing">[external image not embedded: %s]</p>' % html.escape(rel)
    path = resolve_asset(base, rel)
    if path is None:
        return (
            '<p class="image-missing">[figure not found: %s]</p>' % html.escape(rel)
        )
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    # Only the generated topology sheets need special layout. Scoping this by
    # filename matters: the simulation figures are also wide, but they read
    # fine at text-column width and must stay inline with their captions.
    is_sheet = path.stem.startswith("alwayson-")
    if "WEBSITEMAIN" in rel:
        cls = "cover"
    elif is_sheet:
        # A topology sheet is unreadable scaled to the 105mm text-column cap, so
        # it gets a full page instead. Wide sheets additionally need landscape.
        size = png_size(path)
        if size and size[0] / size[1] >= WIDE_SHEET_RATIO:
            cls = "sheet sheet-landscape"
        elif size:
            cls = "sheet"
        else:
            cls = ""
    else:
        cls = ""
    return (
        '<figure class="%s"><img src="data:%s;base64,%s" alt="%s"/>'
        "<figcaption>%s</figcaption></figure>"
        % (cls, mime, data, html.escape(alt, quote=True), html.escape(alt))
    )


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def is_sep(line):
    s = line.strip()
    return bool(s) and s.startswith("|") and set(s.replace("|", "").replace(" ", "")) <= set("-:")


def render(md, base):
    lines = md.split("\n")
    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        fig = figure(stripped, base)
        if fig:
            out.append(fig)
            i += 1
            continue

        m = re.match(r"^```(\w*)\s*$", stripped)
        if m:
            lang = m.group(1).lower()
            body = []
            i += 1
            while i < n and not re.match(r"^```\s*$", lines[i].strip()):
                body.append(lines[i])
                i += 1
            i += 1
            cls = ' class="lang-%s"' % lang if lang in CODE_LANGS and lang else ""
            out.append("<pre><code%s>%s</code></pre>" % (cls, html.escape("\n".join(body))))
            continue

        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            out.append("<hr/>")
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (level, inline(m.group(2).strip()), level))
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < n and is_sep(lines[i + 1]):
            header = split_row(stripped)
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            out.append("<table><thead><tr>")
            for c in header:
                out.append("<th>%s</th>" % inline(c))
            out.append("</tr></thead><tbody>")
            for r in rows:
                r = r + [""] * (len(header) - len(r))
                out.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in r[: len(header)]) + "</tr>")
            out.append("</tbody></table>")
            continue

        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>" + render("\n".join(buf), base) + "</blockquote>")
            continue

        if re.match(r"^[-*+]\s+", stripped):
            out.append("<ul>")
            while i < n and re.match(r"^[-*+]\s+", lines[i].strip()):
                item = re.sub(r"^[-*+]\s+", "", lines[i].strip())
                item = re.sub(r"^\d+\.\s+", "", item)
                out.append("<li>%s</li>" % inline(item))
                i += 1
            out.append("</ul>")
            continue

        if re.match(r"^\d+[.)]\s+", stripped):
            out.append("<ol>")
            while i < n and re.match(r"^\d+[.)]\s+", lines[i].strip()):
                item = re.sub(r"^\d+[.)]\s+", "", lines[i].strip())
                out.append("<li>%s</li>" % inline(item))
                i += 1
            out.append("</ol>")
            continue

        buf = [stripped]
        i += 1
        while i < n:
            s2 = lines[i].strip()
            if (
                not s2
                or s2.startswith("|")
                or s2.startswith("```")
                or s2.startswith(">")
                or re.match(r"^#{1,6}\s", s2)
                or re.match(r"^[-*+]\s+", s2)
                or re.match(r"^\d+[.)]\s+", s2)
                or re.match(r"^(-{3,}|\*{3,}|_{3,})$", s2)
            ):
                break
            buf.append(s2)
            i += 1
        out.append("<p>%s</p>" % inline(" ".join(buf)))

    return "\n".join(out)


CSS = """
@page {
  size: A4;
  margin: 18mm 15mm 20mm 15mm;
  @bottom-center {
    content: counter(page);
    font-family: "DejaVu Sans", sans-serif;
    font-size: 8pt;
    color: #666;
  }
}
body {
  font-family: "DejaVu Serif", Georgia, serif;
  font-size: 9.5pt;
  line-height: 1.45;
  color: #16191d;
}
h1, h2, h3, h4, h5, h6 {
  font-family: "DejaVu Sans", sans-serif;
  color: #0f2a44;
  page-break-after: avoid;
  break-after: avoid;
}
h1 { font-size: 17pt; border-bottom: 1.5pt solid #0f2a44; padding-bottom: 3pt; margin: 0 0 10pt 0; }
h2 { font-size: 13pt; border-bottom: 0.8pt solid #9db4c8; padding-bottom: 2pt; margin: 16pt 0 7pt 0; }
h3 { font-size: 11pt; margin: 12pt 0 5pt 0; }
h4 { font-size: 10pt; margin: 10pt 0 4pt 0; }
p { margin: 0 0 6pt 0; orphans: 2; widows: 2; }
code {
  font-family: "DejaVu Sans Mono", monospace;
  font-size: 8.2pt;
  background: #f2f4f7;
  padding: 0.4pt 1.6pt;
  border-radius: 2pt;
}
pre {
  background: #f7f8fa;
  border: 0.5pt solid #ccd4dd;
  border-left: 2.5pt solid #0f2a44;
  padding: 5pt 7pt;
  margin: 6pt 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  page-break-inside: avoid;
  break-inside: avoid;
}
pre code { background: none; padding: 0; font-size: 7.6pt; line-height: 1.32; }
blockquote {
  border-left: 2.5pt solid #9db4c8;
  margin: 6pt 0;
  padding: 2pt 0 2pt 9pt;
  color: #3d4652;
  background: #fafbfc;
}
table {
  border-collapse: collapse;
  width: 100%;
  margin: 7pt 0;
  font-size: 8pt;
  page-break-inside: auto;
}
thead { display: table-header-group; }
tr { page-break-inside: avoid; break-inside: avoid; }
th {
  background: #0f2a44;
  color: #fff;
  text-align: left;
  font-family: "DejaVu Sans", sans-serif;
  font-size: 8pt;
  padding: 3pt 4pt;
  border: 0.4pt solid #0f2a44;
}
td { border: 0.4pt solid #b8c4d0; padding: 2.6pt 4pt; vertical-align: top; }
tbody tr:nth-child(even) { background: #f5f7f9; }
td code { font-size: 7.4pt; }
ul, ol { margin: 0 0 6pt 0; padding-left: 16pt; }
li { margin-bottom: 2pt; }
hr { border: none; border-top: 0.6pt solid #ccd4dd; margin: 11pt 0; }
figure {
  margin: 8pt 0;
  text-align: center;
  page-break-inside: avoid;
  break-inside: avoid;
}
figure img {
  max-width: 100%;
  max-height: 105mm;
  height: auto;
}
figure.cover img { max-height: 62mm; }

/* Full-page topology sheets. Each starts its own page so the diagram is not
   reduced to an unreadable thumbnail, and a landscape named page is used for
   wide sheets so the 4238x1702 database map keeps a readable type size. */
@page sheet-landscape {
  size: A4 landscape;
  margin: 12mm 10mm 14mm 10mm;
  @bottom-center {
    content: counter(page);
    font-family: "DejaVu Sans", sans-serif;
    font-size: 8pt;
    color: #666;
  }
}
figure.sheet {
  margin: 0;
  padding: 0;
  text-align: center;
  page-break-before: always;
  break-before: page;
  page-break-after: always;
  break-after: page;
}
figure.sheet img { max-width: 100%; max-height: 244mm; height: auto; }
figure.sheet figcaption {
  text-align: left;
  margin: 4pt 0 0 0;
  page-break-before: avoid;
}
figure.sheet-landscape { page: sheet-landscape; }
figure.sheet-landscape img { max-height: 168mm; }
figcaption {
  font-family: "DejaVu Sans", sans-serif;
  font-size: 7.6pt;
  color: #55606c;
  margin-top: 3pt;
  text-align: left;
}
.image-missing {
  font-family: "DejaVu Sans", sans-serif;
  font-size: 8pt;
  color: #8a2b2b;
  background: #fdf3f3;
  border: 0.5pt solid #d9a0a0;
  padding: 4pt 6pt;
}
"""


def main():
    if len(sys.argv) != 3:
        print("usage: render-v6-pdf.py <input.md> <output.html>", file=sys.stderr)
        return 2
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    body = render(src.read_text(encoding="utf-8"), src.parent)
    title = src.stem.replace("_", " ")
    doc = (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8"/>\n'
        "<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n%s\n</body>\n</html>\n"
        % (html.escape(title), CSS, body)
    )
    dst.write_text(doc, encoding="utf-8")
    print("wrote %s (%d bytes)" % (dst, len(doc)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
