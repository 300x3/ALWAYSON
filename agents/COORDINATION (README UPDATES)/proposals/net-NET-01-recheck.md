---
item: NET-01
action: update
evidence: |
  NET-01 REMAINS OPEN. Both halves are still operator decisions and I touched neither.
  What I add this pass is a third option the previous pass did not name, plus a
  README regression I found and fixed.

  === STATE RE-MEASURED, NOT CITED ===

    $ systemctl --user is-active ao-ingress-payment.service ao-payment-relay.service \
        ao-build-update.service
    active
    active
    inactive
    $ systemctl --user is-enabled ao-ingress-payment.service ao-payment-relay.service \
        ao-build-update.service ao-egress-archive.service
    generated
    enabled
    generated
    not-found
    $ podman network inspect ao-build-update \
        --format '{{range .Containers}}{{.Name}} {{end}}'
    (empty)
  Unchanged: one adapter running, one scaffolded-not-enabled, one absent.

  === NEW: THE "TWO OPTIONS" WERE NOT THE ONLY TWO ===
  net-NET-01.md offered the operator exactly two choices for the inert allowlist:
  (a) approve a firewall rule set on the ao-build-update bridge, or (b) declare the
  allowlist documentation of intent. That was a false dichotomy.

  There is a third, smaller option I did not name: remove the ao-build-update
  network and unit until an enforcement mechanism is approved. The segment exists
  only to carry a script that is not running, on a non-internal bridge, so its
  current state is a non-internal network with no workload attached and no
  segment-level control. That is not a defect today - nothing is attached - but it
  is a loaded state, and it is a strictly smaller operator decision than either
  option I offered, because it requires no firewall work at all.

  I am NOT applying it. Removing a network or a deployed unit touches live network
  configuration, an explicit stop condition in my brief.

  === FIXED: README WAS NOT COMPILED - A REAL REGRESSION ===
  I found this by running the check the compiler session installed, which no earlier
  NET pass had run in this worktree:

    $ python3 agents/COORDINATION (README UPDATES)/tools/compile.py --check
    DIFFERS
    EXIT=1

  Cause: the previous commit c7644a1 edited the SECTION file (the 5.2.2 date and the
  5.1 group B row) but did not recompile, so README.md still carried 2026-10-10
  where the section file said 2026-10-04:

    $ git --no-pager show HEAD -- agents/COORDINATION (README UPDATES)/05-.../section.md
    -Measured 2026-10-10.  §19 and this section previously recorded this adapter as
    +Measured 2026-10-04.  §19 and this section previously recorded this adapter as

  The SECTION file is correct and README was stale. 2026-10-04 is right:

    $ date
    Mon Oct  5 08:04:22 AM PDT 2026
    $ systemctl --user show ao-ingress-payment.service \
        -p ActiveEnterTimestamp --value
    Thu 2026-10-01 15:08:41 PDT

  so the measured "3 days ago" is consistent with 2026-10-04 and 2026-10-10 is a
  future date. Recompiled; now agrees:

    $ python3 agents/COORDINATION (README UPDATES)/tools/compile.py --check
    identical

  Why it mattered: §19.1's NET-01 row and README both told readers the adapter was
  "Deployable" and unimplemented while the host said active since 2026-10-01. A
  stale README is how that error survived four passes. Hand-editing README.md
  would have been the wrong fix - the section file is the source of truth, so I
  recompiled from it.
section: 05-network-domains-and-controlled-external-access
---
**NET-01 stays open. No adapter state changed, and I made no change to any
adapter, unit, credential, route or network.**

The one thing I got wrong last pass was structural rather than factual, and
correcting it is the substance of this proposal. I put the operator's decision
about the inert `ao-build-update` allowlist as two options — build a firewall, or
admit the allowlist is documentation. That was a false dichotomy. There is a
third option strictly smaller than both: **retire the network and the unit until
an enforcement mechanism is approved.** The segment exists only to carry a script
that is not running, on a non-internal bridge, so it currently has no workload
attached and no segment-level control. That is not a live exposure, but it is a
loaded state, and retiring it needs no firewall work at all. I have not applied
it: removing a deployed unit and a network is live network configuration, an
explicit stop condition in my brief. But the operator should not be told the
choice is binary when it is not.

**A regression I found and fixed, and what it says about the previous pass.**
`compile.py --check` returned `DIFFERS`. The previous commit had edited my section
file and left README unrecompiled, so README still carried a **2026-10-10**
measurement date that the section file had already corrected to **2026-10-04**.
The section file was right — the adapter has been active since 2026-10-01 and
today is 2026-10-05, so 2026-10-10 was a future date. I recompiled; `--check` now
returns `identical`. I fixed it by recompiling rather than by editing README.md,
because the section file is the source of truth and the bug was precisely that
README had drifted out of step with it.

**What I got wrong, and the reason, because it generalises.** Four NET passes had
asserted NET-01 without once running the compiler's own consistency check — a
single command, installed, answering in one second. Every pass measured the
*runtime* carefully and treated the *document* as automatically consistent, so
each produced confident findings while the repository still shipped a README
asserting the adapter was unimplemented. I had the tool available and did not
reach for it. Verification that is cheap and already automated should be run
*first*, ahead of careful measurement of something expensive: it is the check
most likely to find something new.

**Still open, unchanged, escalated rather than acted on.** The missing rate
limiting in `scripts/payment/ao-payment-adapter.py` is PAY's file and is payment
processing — untouched. The phantom `ao-egress-community` in
`topology-model.yaml`, `gui-boundary-matrix.yaml` and the generated Grafana JSON
is unchanged and is not mine.
