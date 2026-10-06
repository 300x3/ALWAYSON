---
item: PAY-05
action: update
evidence: |
  $ find '/home/scottw/pCloudDrive/PUBLIC FOLDER/***CURRENT***/site' -type f
  /home/scottw/pCloudDrive/PUBLIC FOLDER/***CURRENT***/site/index.html
  /home/scottw/pCloudDrive/PUBLIC FOLDER/***CURRENT***/site/alwayson-single-topology.html
  count=2

  $ grep -oE '(127\.0\.0\.1|localhost|10\.[0-9]+\.[0-9]+\.[0-9]+|192\.168\.[0-9]+\.[0-9]+|172\.(1[6-9]|2[0-9]|3[01])\.[0-9]+\.[0-9]+)' index.html | sort | uniq -c
  (no output — no loopback or LAN reference in the published site)

  $ grep -oiE 'instructables[^"'\'']{0,60}' index.html | sort -u
  instructables-badge.png
  instructables.com/member/SCOTT%20WIDMANN/instructables
  Instructables — fabrication directions
  Instructables badge: bottom-right of every product modal.

  $ grep -oiE '(mastodon|meshchat)[^"'\'']{0,50}' index.html | sort -u
  meshchatx.com/        (outbound link)
  mastodon.social/search?q=300x3   (outbound link)

  $ grep -oE '<iframe[^>]*src="[^"]*"' index.html
  '+(d.embed||d.href)+'      (one dynamic template, no hard-coded origin)
  $ grep -oc '<iframe' index.html
  1
section: 07-public-storefront-and-payment-policy
---

**Revision 2, 2026-10-05. Supersedes the revision of 2026-10-04. Re-measurement
only; nothing was built, published or exposed.**

**PAY-05 stays OPEN.** All three preconditions recorded on 2026-10-01 still hold,
and the §7.1 boundary is intact — the published site still contains **no**
loopback, LAN or Podman address, verified by grep over `index.html` itself rather
than inferred from the build.

Confirmed today: the site is still exactly the two specified files; the Instructables
badge exists only as a *reference* (an `instructables-badge.png` asset name and the
operator's member URL) and the operator-supplied image is still not supplied; and
the Mastodon and MeshChatX entries are still **outbound links, not iframes**.

**What I got wrong:**

1. **My first iframe check produced a false positive and I nearly filed it as
   "one live iframe".** `grep -oc '<iframe' index.html` returns `1`, which reads
   like a count of one embedded view. It is not — it is a single *dynamic template*
   whose `src` is `+(d.embed||d.href)+`, i.e. a JS expression evaluated at runtime
   from catalog data. The count proves a template exists, not that any view is
   live. Extracting the `src` showed no hard-coded origin at all, which is the
   real finding: nothing is embedded from a publishable origin today, so no
   iframe is actually serving. **A tag count is not a count of live views.**
2. I nearly recorded the Instructables badge as "present, so that precondition is
   resolved". It is not: an asset *name* in the markup is not the asset. The
   operator specified a particular logo and said not to substitute it, so the
   correct state is still "unsupplied" and I have kept it open.

Not done, deliberately: nothing built, nothing published, no public entry opened.
Every live view in §7.1.2 is a new public entry under §4.1 rule 6 and needs
explicit operator approval; the Instructables image, the Mastodon/MeshChatX
publishable origins, and SIM-04/SIM-05 for the three simulation views are all
still outstanding and none of them is mine to decide.

---

## SUPERSEDED — revision 1 (2026-10-04), retained for audit


**INDEPENDENT RE-VERIFICATION 2026-10-04 — item still OPEN, nothing built.**

Re-measured rather than assumed. The storefront tree is still exactly the two files
recorded in §7.1.1, every asset is still a still image, and the publish script is
still gated:

```text
$ find '/home/scottw/pCloudDrive/PUBLIC FOLDER/***CURRENT***/site' -type f
.../site/index.html
.../site/alwayson-single-topology.html
count=2

$ find '/home/scottw/pCloudDrive/PUBLIC FOLDER/***CURRENT***/assets' -type f \
    | grep -vE '\.(png|jpg|jpeg|gif)$' | wc -l
0
```

Note the path, because getting it wrong caused the error recorded in the note above:
it is `~/pCloudDrive/PUBLIC FOLDER` — **no space, `PUBLIC FOLDER` in caps**. A
`find` against `~/pCloud Drive/Public Folder` returns nothing and looks identical to
"the storefront does not exist".

**Nothing was built, published, or exposed this session.** All nine rows remain
blocked per §7.1.3. Rows 2, 7 and 8 each require a new public ingress, which is
§4.1 rule 6 and reserved to the operator.

---
**PAY-05 stays OPEN. Nothing was built, published, or exposed.** I am filing
`update`, not `close`, because the criterion ("the nine views ... are built and
reachable from the modals") is not met and cannot be met by me — six of the nine
rows are blocked on an operator decision or on data that does not exist yet.

I added **§7.1.3** to my section file, which did not previously distinguish the
requirement table from the build state. The table in §7.1.2 lists nine views as a
*requirement*; read alone it looks like a status report. §7.1.3 now states
plainly that **none of the nine is built**, enumerates the storefront tree to
prove it, and gives the per-row blocker for all nine:

| Row | View | Blocker |
|---|---|---|
| 1 | Instructables robot link | **No technical blocker** — outbound link plus one operator-supplied image. Needs the asset and a check that the Instructables wordmark is not substituted. |
| 2 | MeshChatX visualizer | `127.0.0.1:18000/`, loopback-only. Needs a new public ingress (§4.1 rule 6). |
| 3 | IPFS-pCloud orthotiff | Data must be produced and licensed first (§8 WebODM). |
| 4 | Trimble San Vicente | Same — point clouds must be produced. |
| 5 | LocusMap | LocusMap tile terms must be confirmed. |
| 6 | Mapbox | External account/token confirmation. |
| 7 | Mastodon live forum | `mastodon.social` refuses framing; local instance is `127.0.0.1:3300/`, loopback-only. Needs a new public entry. |
| 8 | Gazebo/Foxglove | Three loopback-only origins; also gated on §19.1 SIM-04/SIM-05. |
| 9 | Trimble SketchUp grid | Licence confirmation. |

Row 1 is the only row I could build without a new authority, and I did not build
it, because it requires an **operator-supplied image asset that does not exist**
and publishing it is still a new public entry under §4.1 rule 6.

**This extends the 2026-10-01 PAY-05 note rather than contradicting it.** That
note recorded three preconditions; those three (Instructables image absent, no
publishable Mastodon/MeshChatX origin, sim views gated on SIM-04/05) all still
hold, and I re-measured rather than assuming. What I added is the reason they
hold and the status of the other six rows, which no one had recorded.

Two things I got wrong:

1. **I first looked for the storefront at `~/pCloud Drive/Public Folder` and got
   nothing.** The real path is `~/pCloudDrive/PUBLIC FOLDER` — no space, and
   `PUBLIC FOLDER` in caps. A `find` that returns no results is indistinguishable
   from "the storefront does not exist", and I nearly wrote the weaker and wrong
   claim "no storefront exists at all" into §7.1.3. **I should have resolved the
   path from the repo before searching the filesystem** — `publish-pcloud-storefront.sh`
   was the file to read, and reading it first would have avoided the false
   negative entirely.
2. **My first verification run of the sales PDF used a free-form request body
   and the parser returned `items=0 ... INCOMPLETE`.** The script did not fail
   loudly — it produced a valid JSON record and exited **4**, which is an expected
   "incomplete request" code, not a crash. Had I stopped there I would have
   written "the intake path is broken" into §7.3.1. The real constraint is a fixed
   labelled format (`SUBJECT:`/`NAME:`/`EMAIL:`/`KIT REQUESTED:`/`COMMENTS:`)
   documented in `scripts/sales/intake-request-record.py`. Re-running in that
   shape gave `exit=0` and all three PDFs. **A non-zero exit from these scripts is
   a documented outcome, not necessarily a fault — read the header before
   concluding anything.**

Not mine to fix, reported rather than touched: `publish-pcloud-storefront.sh`
still references "Section 3.4", which is part of the repo-wide dangling
`Section 18.x`-style cross-reference problem raised in `pay-PAY-07.md`. §3.4 is a
real section, so this one resolves; I did not edit the script because
`scripts/` is outside my owned file list.