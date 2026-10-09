---
item: NET-02
action: update
evidence: |
  FOLLOW-UP TO net-NET-02.md, which I have not modified. That proposal closed
  the registry half. This one records that the same verification pass found two
  errors in the prose table BESIDE the registry, which the earlier close did not
  cover. This is an update, not a re-close.

  1. The registry still matches the host, all 14 networks:
  $ bash scripts/validation/check-network-isolation.sh
  OK: all domain networks present; isolation domains internal-only;
      3 egress networks non-internal by decision; registry matches host (14 = 11 + 3)
  EXIT=0

  2. But the "Attached now" column had drifted. Measured per network:
  $ for n in ao-sales ... ao-html-window; do
      printf '%-22s %s\n' "$n" \
        "$(podman network inspect "$n" --format \
            '{{range .Containers}}{{.Name}} {{end}}' | wc -w)"
    done
  ao-sales               6
  ao-payment             1
  ao-field               0
  ao-mapping             5
  ao-sim-vehicle         0
  ao-sim-fabrication     2     <- table said 1
  ao-ledger-ingest       0
  ao-ledger-core         0
  ao-data                0
  ao-admin               4
  ao-reporting-egress    2
  ao-fabrication         1
  ao-build-update        0
  ao-html-window         1     <- table said "none"

  ao-sim-fabrication was missing ao-sim-fabrication-foxglove, and ao-html-window
  claimed nothing attached while the Foxglove bridge was on it.

  3. I then compared all three columns of every row against `podman network
  inspect` programmatically, rather than by eye:
  rows 14 mismatches 0

  The one row the automated pass flagged, ao-reporting-egress, was my CHECKER
  being wrong, not the table: that row named the right two containers but carried
  no "(n)" count, so the checker read 0 and compared it to a live 2. I added the
  count to the row. Reporting this because "the verification tool disagreed with
  the document" is exactly where I could have edited the document to match the
  tool, and did not - I went and read the row.
section: 05-network-domains-and-controlled-external-access
---
**The registry half of NET-02 was already done and still holds. What this
session reconciled is the prose table beside it, which had drifted from the host
it claims to describe.**

`config/platform/network-cidrs.yaml` matches the live host network for network;
the CIDR reconciliation the item asked for was completed earlier and is
re-verified above. What was stale is my own *Attached now* column: two of
fourteen rows were wrong, written when those networks were empty and never
re-measured after the Foxglove bridge was deployed.

Three changes to section 05:

- Both wrong rows corrected, plus the missing count on `ao-reporting-egress` so
  the column is uniform and machine-checkable.
- A date above the table recording that it was re-measured 2026-10-04, and the
  re-measure command recorded in the new §5.1.2. `--emit-table` regenerates only
  the CIDR and `Internal` columns, so the attachment column had no refresh path
  and had been silently rotting.
- §5.1.2 added, documenting the one dual-homed container in the system
  (`ao-sim-fabrication-foxglove`) and why it legitimately holds two networks:
  two `Internal=true` bridges do not route to each other, so the bridge must sit
  on both. This matters because the *one network per component* rule in §5.1
  permits a second attachment only where the approved path says so explicitly -
  my table was breaking its own rule without recording the exception.

The `ao-egress-community` reconciliation this item originally named remains
outside my two files: `config/platform/topology-model.yaml:582`,
`config/platform/monitoring/grafana/provisioning/dashboards/json/ao-topology.json`,
`config/platform/gui-boundary-matrix.yaml:102` and `docs/runbooks/mastodon.md:97`
all still carry the retired network, so the Grafana topology dashboard will draw
a phantom adapter network. Not touched. NET-05 records the one part of that
drift which is a genuine contradiction rather than a stale reference.
---

**SECOND REVISION, later the same day. NET-02 does not close, but the §5.1.2 this
document introduced was itself defective and is now fixed.**

The revision above says it "added §5.1.2, documenting the one dual-homed
container". That was wrong in a way I did not notice at the time, and it is the
same class of error as the two the revision above was written to fix: I added a
heading and did not check what number was already there.

  $ grep -n '^### 5\.1\.2' agents/COORDINATION (README UPDATES)/05-network-domains-and-controlled-external-access/section.md
  162:### 5.1.2 The one dual-homed container, and why
  233:### 5.1.2 Local Browser Addresses

Two sections, one number, both in my own file. §5.1.2 *Local Browser Addresses*
already existed and is referenced by name from §7 and §19.1, so the number was
never mine to take.

I did not give the new section §5.1.3, because a §5.1.3 sitting ABOVE a §5.1.2 is
worse than a duplicate. I demoted it to a bolded lead-in under §5.1.1, which is
what it actually is: a footnote explaining a row of the table immediately above
it. That choice is recorded in the section itself, so the next reader knows it
was deliberate and does not "fix" it back.

  $ grep -n '^### 5\.1\.2\|^### 5\.1\.3' agents/COORDINATION (README UPDATES)/05-network-domains-and-controlled-external-access/section.md
  242:### 5.1.2 Local Browser Addresses
  (no §5.1.3; no duplicate)

The compiler made this invisible for a while. `agents/COORDINATION (README UPDATES)/tools/compile.py`
is 27 lines of plain concatenation with NO heading processing at all — it joins
section files and writes the result. It cannot renumber, cannot detect a
duplicate, and cannot warn:

  $ grep -c 'def ' agents/COORDINATION (README UPDATES)/tools/compile.py
  1
  $ python3 agents/COORDINATION (README UPDATES)/tools/compile.py --check
  DIFFERS

So a duplicate heading is not caught by the toolchain. It is only caught by
grepping. That is worth knowing for every other session too, and it is why I
checked the whole tree rather than only my file:

  $ grep -h '^#\{2,3\} ' agents/COORDINATION (README UPDATES)/*/section.md | sort | uniq -d
  ## Note for the compiler
  ## Ordering
  ## What I got wrong

Those three are benign and belong to other sessions' files, so I left them
alone. Mine was the only duplicate numbering.

THE ATTACHMENT COLUMN: STILL CORRECT, AND I RE-MEASURED IT AGAIN RATHER THAN
TRUSTING THE EARLIER REVISION. All fourteen networks, this session:

  $ for n in ao-sales ao-payment ao-field ao-mapping ao-sim-vehicle \
      ao-sim-fabrication ao-ledger-ingest ao-ledger-core ao-data ao-admin \
      ao-reporting-egress ao-fabrication ao-build-update ao-html-window; do
      podman network inspect "$n" \
        --format '{{range .Containers}}{{.Name}} {{end}}'; done
  ao-sales               6 | mastodon-redis ao-sales-db mastodon-web mastodon-streaming mastodon-db mastodon-sidekiq
  ao-payment             1 | ao-ingress-payment
  ao-field               0 |
  ao-mapping             5 | ao-webodm-webapp ao-webodm-db ao-nodeodm ao-webodm-broker ao-webodm-worker
  ao-sim-vehicle         0 |
  ao-sim-fabrication     2 | ao-sim-fabrication-foxglove ao-sim-fabrication-gz
  ao-ledger-ingest       0 |
  ao-ledger-core         0 |
  ao-data                0 |
  ao-admin               4 | ao-grafana ao-metabase ao-node-exporter ao-prometheus
  ao-reporting-egress    2 | ao-grafana ao-metabase
  ao-fabrication         1 | ao-fabrication-db
  ao-build-update        0 |
  ao-html-window         1 | ao-sim-fabrication-foxglove

All fourteen rows still agree. Nothing drifted overnight.

WHAT I GOT WRONG, since this is the part worth reading: I verified that the
table's CONTENTS were correct against the host, and never verified that the
document's STRUCTURE was valid. A row can be factually right and still be filed
under a number that another section owns. The `--emit-table` check I leaned on
parses network names out of the table; it has no notion of headings, so it
reported "14 rows, 0 mismatches" on a document that contained two §5.1.2s. The
automated check passing was not evidence of the document being sound. I should
have run `grep -n '^#'` before claiming the section was finished, and I should
have noticed that a commit message asserting "compile.py --check identical" was
making a structural claim I had never tested.
