---
item: PAY-05
action: update
evidence: |
  # The public storefront site tree, enumerated
  $ find '/home/scottw/pCloudDrive/PUBLIC FOLDER/***CURRENT***/site' -type f
  /home/scottw/pCloudDrive/PUBLIC FOLDER/***CURRENT***/site/index.html
  /home/scottw/pCloudDrive/PUBLIC FOLDER/***CURRENT***/site/alwayson-single-topology.html
  count=2

  # assets exist but are images only — no export, route or embed
  $ find '/home/scottw/pCloudDrive/PUBLIC FOLDER/***CURRENT***/assets' -type f | wc -l
  49
  $ ... | grep -vE '\.(png|jpg|jpeg|gif)$' | wc -l
  0            # every asset is a still image; none is a view

  # repository side
  $ git --no-pager ls-files | grep -iE 'storefront|public.*\.html|index\.html'
  GAZEBO/portal/index.html
  GAZEBO/portal/viewer/index.html
  config/storefront/release-policy.yaml
  scripts/storefront/build-storefront.sh
  scripts/storefront/publish-pcloud-storefront.sh
  scripts/storefront/rollback-storefront-release.sh
  scripts/storefront/verify-storefront-release.sh

  # publishing is itself gated, so nothing reaches the public tree
  $ grep -n 'PENDING' scripts/storefront/publish-pcloud-storefront.sh
  5:echo "PENDING: publish-pcloud-storefront.sh requires pCloud Public Folder
      credential provisioning (Section 3.4) - paused for operator approval"

  # the three loopback-only rows, as stated in my own section file
  $ grep -n 'loopback' agents/COORDINATION/07-.../section.md
  127:| 2 | MeshChatX — network visualizer | ... loopback-only and **not a
      public ingress** (§9.2.1), so it cannot be iframed. ...
  132:| 7 | Mastodon — live forum | ... `127.0.0.1:3300/`, loopback-only, ...
  133:| 8 | Gazebo/Foxglove — simulation | ... sim console `127.0.0.1:8099/sim`,
      Gazebo portal `127.0.0.1:8765/` ... bridge on `127.0.0.1:8081`. ...

  # SIM-04 / SIM-05 referenced 5 times in §19 — the gate is real, not invented
  $ grep -cE 'SIM-0[45]' agents/COORDINATION/19-.../section.md
  5
section: 07-public-storefront-and-payment-policy
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