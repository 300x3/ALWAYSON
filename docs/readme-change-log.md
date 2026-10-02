# README change log

Revision history for `/ALWAYSON/README.md`. This is where history belongs — the body of
the README states the current architecture and the current work, and does not narrate how
it got there.

## 2026-10-02 — README update per the GitHub review

Source of the review: `COORDINATION BETWEEN AI/X - README - GITHUB REVIEW - 20261001.txt`

| Change | Effect on the document |
|---|---|
| Added a **WHY** row under Project origin | States the goal: a fully autonomous live/work/fabricate area supporting fully autonomous air, land and sea vehicles and their daily-carry equipment, doing everything itself for any business and any owner even when the internet turns off, at the size of a small storage unit, garage, or parking space |
| Renamed the ES.2 reporting question | "Does monitoring need Grafana?" became "What are the database reporting tools and their functions?", and now emphasises that **all three** — Prometheus, Grafana, Metabase — are read-only over the databases that already exist, none is a system of record, and none writes to a source database |
| Removed the **Domoticz shared server** row | The `*:6144` row was history for a listener already removed on 2026-09-30. Dropped from the listener table |
| Gazebo portal `:8765` and operator console `:8099` moved into ALWAYS ON | Both were listed under "listeners not part of ALWAYS ON". They now have their own table as ALWAYS ON loopback listeners, and the "no public listener" claim is restated to cover them. §19 item 43 was added for the console having no unit |
| MeshChatX documented as a coordination system | It is the coordination system for the ALWAYS ON Reticulum network stack and the LoRa radios, and it only needs to speak to the **Reticulum network stack** |
| QGroundControl given a dedicated RNS-enabled link | DRONE-RADIO carries a dedicated RNS-enabled QGC connection to the drones, so missions reach the QGC session on the Pi5 and can be updated midflight. Recorded in ES.1 (RNode client B, QGroundControl) and §9.2.2 |
| ES.3.1 restructured | The five-column status table became four columns — "Next action" folded under "Current state and next action" — so it fits portrait reading and the state column gets the width |
| Repaired the ST-13 row | The row was split by a stray empty cell, so it rendered as seven columns and its "Next action" was lost. Also removed a sentence duplicated within the row |
| ES.1.1, ES.3 and ES.3.2 relabelled as high-level summaries of §19 | Each now says so explicitly. The low-level items, acceptance criteria and standards stay in §19 |
| History removed from the body | "The former §3.2 status table has been deleted", "both of the tables that used to live here have been removed", and similar sentences were removed from ES.1.1, ES.3 and §3.2, and are recorded in this file instead |
| §19.0 priorities converted to a table | The numbered list is now a table, consistent with the rest of §19 |
| Topology enlargements re-synced | `assets/ao-single-topology{,-left,-right}.png`, `ao-single-topology.svg` and `ao-single-topology.html` were dated 02:04 while the build in `TOPOLOGY/TOPOLOGY - SINGLE GRAPHIC/` was 13:49. All five are now byte-identical to the build, and the previous copies are in `backups/topology-assets-pre-sync-20261002/` |

### Verified

```
sha256 TOPOLOGY/TOPOLOGY - SINGLE GRAPHIC/alwayson-single-topology.svg
      == assets/ao-single-topology.svg
      6ea23949a82609af97190f83effe8d0673c6db26ec450713fed444b51110e353

sha256 TOPOLOGY/TOPOLOGY - SINGLE GRAPHIC/alwayson-single-topology-left.png
      == assets/ao-single-topology-left.png
      70da92c9cc4238b4d3763bea1270a4915ba8e08a41e1d37cd58cc3a8f29291e2

sha256 TOPOLOGY/TOPOLOGY - SINGLE GRAPHIC/alwayson-single-topology-right.png
      == assets/ao-single-topology-right.png
      1bc4da3376284ea3eacfb8a294e5c91926ffec612004a0e892488bbfbecd9d0d

sha256 TOPOLOGY/TOPOLOGY - SINGLE GRAPHIC/alwayson-single-topology.html
      == assets/ao-single-topology.html
      95f6161922c06d5f7739908b693b8ba8d42ad0cd1bb7d134d7ee3602a2b6cf25
```

Font sizes in the synced SVG are 26/25/24 for card text, up from 20/19/22 before the sync,
which is the "increase the small font by at least 3 points" review item.

### Published live viewer — verified current, nothing to publish

The live viewer linked in ES.2 was checked end to end and is already serving the new
diagram, so nothing was republished:

```
curl -sS -o served.html -w 'http_code=%{http_code} size=%{size_download}' \
  'https://filedn.com/l5JNexbL2ipFNaQcAkmV7lQ/%2A%2A%2ACURRENT%2A%2A%2A/site/alwayson-single-topology.html'
  http_code=200 size=419038

sha256 served.html
  == TOPOLOGY/TOPOLOGY - SINGLE GRAPHIC/alwayson-single-topology.html
  == assets/ao-single-topology.html
  == PCLOUD-PUBLIC/***CURRENT***/site/alwayson-single-topology.html
  95f6161922c06d5f7739908b693b8ba8d42ad0cd1bb7d134d7ee3602a2b6cf25

cmp served.html <build>   -> identical (byte for byte, not merely equal length)
```

Markers present in the served bytes: `ao-html-window` ×3, `CONFIRMED SALE PDF OUTPUT` ×2,
`PostgreSQL 18 (host cluster)` ×3, `PostgreSQL 18.6` ×0. The file was published 13:58:11,
nine minutes after the 13:49:34 build.

An earlier note in `logs/operations/readme-succinct-pass-20261002.log` recorded that the
hosted viewer still served the old diagram. That was true when written and was overtaken
when the file was republished at 13:58; it should not be relied on now.

The pCloud `site/` folder holds only `alwayson-single-topology.html` and `index.html`.
The earlier `alwayson-single-topology-v2.html` and a `.bak-20261002-1350-pre-5c4bc11` sit
in `PCLOUD-PUBLIC/ARCHIVED/`. Nothing links to the `-v2` name — `index.html` contains no
reference to the topology at all.

### Review items already satisfied before this pass

These were verified in place and left unchanged: the single Radios row covering Wi-Fi and
the two LoRa radios; the RNode client A / client B split; OpenClaw folded into Social media
with the LM Studio row directly below; the email-endpoint template and PDF work-order flow;
Prometheus hardened via ad-hoc security AI review; Corda and Corda persistence combined;
no OrcaSlicer reference under additive fabrication; bCNC moved into real fabrication; the
split into Simulation (fabrication) and Simulation (vehicles); `ao-html-window` in the
topology; the ES.1.1 note that the working file is a `.SVG` outputting hosted `.HTML` plus
static `.PNG` and `.PDF`; the ES.2 column ordering and grouping; the stores-and-reporting
grouping; the single PostgreSQL 18 host cluster; the field/radio ordering; and the
"CONFIRMED SALE PDF OUTPUT" note under KIT REQUEST PDF intake.

## 2026-10-01 — Succinctness pass

See `logs/operations/readme-succinct-pass-20261002.log`. Ten ES.1 rows were tightened with
no fact removed, and the topology assets were synced from the build at 01:17.