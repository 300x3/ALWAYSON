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
## 2026-10-02 — ES.3, ES.3.2 and section 19 merged into one log at §19

Operator instruction: "combine ES3.1, ES3.2 and 19 into a single log at 19 and ensure it does
not duplicate anything. That log is the current status. No executive summary is needed."

| Change | Detail |
|---|---|
| Removed the Executive Summary status section | `ES.3 Implementation Status and Current Work`, its `ES.3.1` table of 30 component rows, and the `ES.3.2` work summary. There is no longer any status or work content in the Executive Summary. `ES.4` was renumbered `ES.3` (Detailed System Record). ES.1 (architecture corrections) and ES.2 (master topology) are unchanged |
| New §19 structure | **19.1** component status (30 rows, ST-01..ST-30) · **19.2** outstanding work (46 rows, numbered 1–46) · **19.3** completed items · **19.4** operator setup priorities |
| Duplication removed | ST-20 and ST-04 previously restated their work items verbatim; 19.1 now gives a one-line pointer to the 19.2 row instead. Verified by a token-overlap scan across both tables: zero rows now share six or more significant words |
| Numbering defects fixed | The old §19 had two rows numbered `38`, two numbered `43`, and two numbered `32`/`33` in different subsections. All work items are now numbered continuously 1–46 with no repeats |
| Work items with no ST component now say so | Added a `Component` column to 19.2 so each work item names the 19.1 row it belongs to, rather than restating that component's state |
| Completed items preserved | Five finished items (ActivityPub round trip, Mastodon service-account consolidation, per-modal purchase buttons, kwalletd6 D-Bus details, digest-pinning) moved to §19.3 with their closing evidence rather than being deleted. Checked first: three of the five had no matching row in §20, so dropping them would have destroyed the only record |
| Cross-references updated | Every "ES.3", "ES.3.1", "ES.3.2", "ES.4", "§19.3", "§19.5", "§19 row 17" and `WORK 000xxx` reference now points at §19.1, §19.2 or §19.3 as appropriate. All 30 `ST-` IDs referenced anywhere in the document are defined in 19.1 |

### Verified

```
tables in document            51, malformed rows 0
19.1 component rows           30, unique 30
19.2 work rows                46, contiguous 1..46
duplicate ids                 none
ST ids referenced but undefined  none
old §19 work items missing from new §19  0
```

The `WORK 000600`–`WORK 000801` identifiers were a second numbering scheme for the same work
and have been removed in favour of the §19.2 row numbers. Every one was checked against the
merged list first: each had a matching item.

## 2026-10-02 — Sections 1–16 became pure specification; 17–19 carry all current state

Operator rule: everything above section 17 is the planned future state, with no inconclusive
language, no moving target, no change, revision, or decision recorded in the body. Sections
17–19 are for things that are developing. Each section was also tightened while being
converted.

A pattern scan over sections 1–16 found **129** passages carrying status, history, decision,
or tentative language. **10 remain, and all 10 are specification vocabulary**, not status:
the `supersedes` / `replaced_by` link types in the §8 model registry, the `pending-review/`
directory name in the §8.2 tree, the `status = received | validated | rejected |
superseded` enum in §11, and "Corda entry is blocked until…" as the rule itself in §11.

### Whole subsections rewritten as specification

| Section | Was | Now |
|---|---|---|
| §2.2 | "Current Host Facts" — measured values, a verification date, and a note that an older count was wrong | **Platform Baseline** — the requirement, with a pointer that the measured values are in §19.1. The measured baseline was moved into ST-01 so nothing was lost |
| §3.2 | A pointer to the removed ES.3 tables | **Where Status Lives** — four lines saying status is §19.1, work is §19.2, evidence is §20 |
| §7.1.2 | A nine-row table with `State` = "Planned — not built" and a "Decision needed" column | The same nine views with a **Requirement and constraint** column; no state column at all |
| §13.2 | "Podman Store Model — deviation CLOSED 2026-10-01", including a 50-line narrative of a dead `socat` bridge, three dead podman connections, and a resolution log | The store model as a rule set, plus the compensating controls |
| §13.3.1 / §13.3.2 | "Directories that exist but are not in the diagram" and "Diagram entries with no directory yet" — both framed as correction of an earlier tree | One **Additional paths** subsection |
| §14.1.2 | "Secret-delivery open items — both CLOSED", a ledger of past edits | **Secret-delivery rules** — one folder per domain, one env root, and the credential→folder table |
| §14.1.3 | "RESOLVED 2026-10-01 — one env file, one wallet entry", with the deleted path and the defect found | The rule: one env file, `genenv` is non-destructive, `$HOME` not `$AO_ROOT` |
| §14.1.4 | "Verified kwalletd6 D-Bus access (2026-10-01)" and a 401 debugging post-mortem including "the bridge had crash-looped 5,119 times" | The D-Bus values as specification, and the four token requirements as rules |
| §15.4 | "**Category:** Implemented and operational (completed 2026-09-24)" and text about a superseded loopback stage | Scope statement only |
| §15.4.3 | A "Superseded design (retained for history): workstation nginx" block | The one federation edge path |
| §16.1.1 | "Quadlet deploy path, and two open findings", with a "Deploy target corrected 2026-10-01" narrative | **Quadlet deploy path** — flat deployment as a rule, with the `SourcePath` check |

### Other conversions

- The status column in the §5.1 combined matrix no longer names a status; it carries the ST
  ID only. Adapter rows read "Deployable" rather than "Planned — not yet deployed".
- §5.1.2 no longer says "ST-10 Planned, not deployed" or "ST-09 Blocked" in the network table.
- §5.1 "Sections 5.2, 6.1 and 6.A.1 formerly held four separate tables" → "are".
- §5.1 no longer records that `ao-egress-community` "is removed"; it states there is no
  separate community egress network.
- ES.1 "Change Summary" (ES.1.1) was deleted: it was history in the body, and the operator
  asked for no executive summary. Revision history lives only in this file.
- The `Reading order` row now states the split explicitly: §1–16 is specification, §17–19 is
  current, and where they differ §17–19 is the fact and §1–16 the requirement.
- ES.1's Corda row no longer narrates the removal of the V4 install; the blocked state is in
  ST-09 where it belongs.

### Verified

```
sections 1-16, status/history/decision/tentative passages   129 -> 10
  (the 10 are spec vocabulary: model-registry link types, a directory name,
   a status enum, and "blocked until" as the rule itself)
tables in document                        49, malformed rows 0
ST ids referenced but not defined in 19.1 none
README asset + docs links                 14 referenced, 14 present
```

Spec word count for sections 1–16 fell from 27,103 to 25,384. The reduction is history and
status narration, not specification: every rule that was expressed as a resolved narrative
was restated as a rule.

## 2026-10-02 — Data-model decisions replaced with end results; section-by-section de-duplication

Operator instruction: `supersedes` / `replaced_by` are decisions, so document the end result,
not what was superseded. `received` / `validated` / `rejected` are not useful — only the end
result. `blocked` is a §19 work item, not specification. Nothing in section 17 may carry that
language either. Then go section by section for succinctness and for repetition within a
section and between sections.

### End results, not decisions

| Was | Now |
|---|---|
| §8.6.1 — a `model_object_links` row of type `supersedes` / `replaced_by` | "`model_object_links` records the relation between the two. The original identity is never overwritten or reused." |
| §8.6.1 — a revision "remains as a `superseded` or `retired` record" | A revision whose artifact is no longer on disk stays in the registry as a **`retired`** record with its hash intact |
| §8.6.5 — "Superseded revisions are preserved and marked `superseded`" | "A retired revision is preserved and marked `retired`, never reused." Also: "only one current revision" → "**exactly one** is the current revision" |
| §11.2.2 — `status = received \| validated \| rejected \| superseded` | The record carries no status column at all. Eligibility is expressed as three presence facts, and anything short of all three does not count |
| §11.2.2 — "Corda entry is **blocked** until all three evidence classes are present" | "A sale is **eligible** for Corda submission only when all three evidence classes are present" |
| §17.1 — the off-site pCloud folder "created 2026-09-30; empty, and restic does not yet point at it" | The folder name, with restic configured to write to it (§19.2) |

### Section-by-section de-duplication

A 7-gram overlap detector was run over the whole document, separately for repeats inside one
section and repeats across sections.

| Finding | Fix |
|---|---|
| §9.2.1 — the paragraph "Both RNodes are functional and initialize successfully…" appeared **verbatim twice** | Second copy deleted |
| The Mastodon identity paragraph (login emails, canonical handles, the `aoadmin` → `admin` rename, the `reserved_usernames` note) appeared in **four** places: §15.3, §15.4.1, §18.5, and §20 | §15.4.2 is now the single specification. §15.3 and §18.5 point to it; the duplicate bullet in §15.4.1 was deleted. `reserved_usernames` now appears only in §19.1 and §20, which are status and evidence |
| §19.1 ST-07 and ST-08 repeated the same four baseline capabilities in full | ST-08 now says "the same four baseline capabilities as ST-07". The capability list is stated once, in ST-07 |
| ES.1 repeated the four simulation capabilities in both simulation rows | The vehicles row now reads "the same four baseline capabilities as `ao-sim-fabrication` (§10.1)" |
| §3.3.1 carried Grafana's `/api/health` verification result | Removed from the spec table; it is evidence and lives in §20 |
| §19.1 ST-05, ST-06, ST-19, ST-20, ST-25 repeated evidence detail from §20 | Trimmed to the status, with "Evidence in §20" |
| §18.4.1 repeated why `127.0.0.1:8899` exists, and noted another session's uncommitted edits to a config file | Explanation dropped from the table; the cross-session note removed |
| §3.3.1 recorded the duplicate host-cluster `webodm` database being dropped | Removed; the end result is one `webodm_dev` database in the container |

### Verified

```
sections 1-17, status/history/decision vocabulary   3, all confirmed legitimate:
  two are file-handling rules ("regenerated or removed", "duplicate file is
  removed"), one is the 3.2 pointer that names section 19.2
tables                                        49, malformed rows 0
ST ids referenced but not defined in 19.1     none
asset + docs links                           14 referenced, 14 present
lines                                       4,713
```

Repeats that were deliberately **kept**, because they are not duplication: the HTML/CSS
boilerplate in the §5.1 combined matrix, the identical `Heltec LoRa 32 V3, SX1262, RNode
firmware 1.85` hardware cell on both radio rows, the `ROS 2 Lyrical, Gazebo Sim 10.5.0` stack
shared by the two simulation rows in §2.1, and the §3.3.1 rows that all end with the same
"not automatically part of SQL reporting" boundary.
