# 2026-10-02 — One-page topology: band-row clearance fix, commit, pCloud publish

Operator request: band tops were clipping text at the top of band 4; lower the
row while keeping all nine bands in line. Then: push to git, and upload the
live HTML to pCloud at the local filepath.

## Root cause

`LN_BOT` is only the last LANE line. The label de-collision pass can push a
pill BELOW its lane, and a pill is PILL_H (24) tall centred on that line, so a
displaced pill overhangs it. At `MARGIN_T = LN_BOT + 18` the band tops landed
at y=706, and band 4's top border cut through the "factory and kitchen world"
pill at y=710..734.

Also removed: `ROW_TOP = MARGIN_T + max(HEAD.values())`, which added band 2's
347px caption allowance above all nine boxes and drew nothing in it — a void
above the whole row. Each band already reserves only what its own caption
needs via `b["_sy"] = b["_by"] + HEAD[bk]`, so the slack was purely dead
space at the top of the page.

## Change

`TOPOLOGY/TOPOLOGY - SINGLE GRAPHIC/build_svg.py`
- `MARGIN_T = LN_BOT + 18 + 2*LN_STEP`   (line ~567)
- `ROW_TOP = MARGIN_T`                   (line ~639)

Both are single constants, so the nine band rects keep ONE top edge.

## Verification (measured on the rebuilt SVG, not assumed)

    band top edges            {768}      <- exactly one value, all nine in line
    lowest pill bottom        734
    clearance                 34 px
    clipped elements          NONE
    nodes / edges             66 / 81
    font sizes 29/26/25       67 / 365 / 103
    ao-html-window            x2
    CONFIRMED SALE PDF OUTPUT x1
    PostgreSQL 18 (host cluster)  x1
    band pages                9
    canvas                    7746 x 5233, aspect 1.480

Self-correction: an earlier check in the same session reported "11 px
clearance, nothing clipped" and a later naive pass reported ~28 spurious
"CLIPPED" entries. Both were measurement bugs, not new layout faults. The
first filtered pills to `y < 706`, so the offending pill at y=710 fell
outside the filter and was scored ok. The second compared every element,
including footer legend swatches at y~1856-3992, against a y=768 threshold.

## Git

Staged by file (never `git add -A`; the tree is shared with other sessions).
Only `build_svg.py` is tracked — all generated outputs under this directory
are gitignored, so the commit carries the generator only.

    5c4bc11  fix(topology): remove void above bands, then lower row clear of displaced pills
    136b5e4..5c4bc11  main -> main   (origin = https://github.com/300x3/ALWAYSON.git)

## pCloud publish

Route: pCloud is mounted at `/home/scottw/pCloudDrive` (FUSE, rw). The public
link is an in-place path, `PUBLIC FOLDER/***CURRENT***/site/`, published as
the filedn.com link recorded in README.md:125 and :131. `rclone` is NOT
installed and `scripts/storefront/publish-pcloud-storefront.sh` exits 3
(pending operator approval), so neither was used or needed.

Pre-publication checks:
- Secret scan of the HTML: only topology prose matched ("SECRETS ON THIS
  HOST", "fetch-kwallet-secret.sh"). No key, token, password, or PEM material.
- External references: ZERO. The page is fully self-contained.

Backup taken and hash-confirmed before overwrite:
`alwayson-single-topology.html.bak-20261002-1350-pre-5c4bc11`
(5c85a9291b1eeddee20103a6777dba3163f4e67fc74f9ad5e6208aa425a3f2dc, 400882 B)

Copy made to a `.tmp-upload` name and moved into place, so the live file was
never truncated mid-write.

    before  5c85a9291b1eeddee20103a6777dba3163f4e67fc74f9ad5e6208aa425a3f2dc  400882 B
    after   95f6161922c06d5f7739908b693b8ba8d42ad0cd1bb7d134d7ee3602a2b6cf25  419038 B

Remote propagation: the filedn.com URL returned the new hash on the FIRST
poll, no retry needed.

Live-page checks via headless browser against the public URL (not the local
file): band tops {768}, clearance 34 px, 66 cards, 9 band pages each carrying
a full inline SVG, all nine band titles present in tab order, page renders.

## Open items carried forward

- `WARNING labels with no free spot: ['publishes HTML content to 300x3.com']`
  — pre-existing build warning, unchanged by this edit, not caused by it.
- README.md:125 and :131 already describe this page as "rebuilt 2026-10-02"
  and as the stable hosted link, so no README edit was required.
