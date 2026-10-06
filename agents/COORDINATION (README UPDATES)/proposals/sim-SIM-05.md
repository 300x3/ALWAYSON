---
item: SIM-05
action: keep-open
evidence: |
  Measured 2026-10-04. Three of four limbs are delivered; the fourth is not merely
  missing but contradicted by the portal's own design, which makes this a decision
  for the operator rather than work for me.

  LIMB 1 -- world setup scripted and repeatable: PARTIAL.
  The world exists and a runner exists, but the runner is a deliberate stub:
  $ cat scripts/simulation/run-fabrication-scenario.sh
  # ALWAYS ON - simulation/run-fabrication-scenario.sh
  set -Eeuo pipefail
  IFS=$'\n\t'
  . /ALWAYSON/scripts/lib/common.sh
  echo "PENDING: run-fabrication-scenario.sh requires its domain deployment
        first (Section 2.8 safe sequence)"
  exit 3
  ^ it exits 3 and does nothing. Not repeatable yet.

  LIMB 2 -- boning frame and tolerances measurable and exported: PARTIAL.
  Boning is measurable in place and served by the portal:
  $ curl -s http://127.0.0.1:8765/api/boning
  (200, cells with datum origin/extent, joint limits and tolerances)
  but it is NOT exported to a durable artifact:
  $ find artifacts -iname '*boning*'
  (no output)
  ^ nothing under artifacts/. It is servable, not exportable.

  LIMB 3 -- RL objects addressable and resettable: addressable YES, resettable NO.
  $ curl -s http://127.0.0.1:8765/api/objects | head -c 120
  {"model": "rl_objects", "resettable": true, "total_objects": 9, ...
  ^ resettable:true is now paired with reset_available:false and a reset_note
    naming the discrepancy (corrected this session, see below)
  $ curl -s -o /dev/null -w '%{http_code}\n' -X POST http://127.0.0.1:8765/api/reset
  405
  ^ the portal refuses every write verb by design. Reset is not merely absent,
    it is actively refused.

  LIMB 4 -- "the world fully settable and operable from the browser-served HTML
  portal": NOT MET, and deliberately so.
  $ sed -n '294,299p' scripts/simulation/ao-sim-portal.py
    def do_POST(self):
        # VIEW-ONLY. Every write verb is refused; the portal exposes no route
        # that can change the simulation. 405 with an Allow header is the
        # correct response for a method the resource does not support.
  $ curl -s http://127.0.0.1:8765/api/health
  {"ok": true, "view_only": true, "reports_on": "ao-sim-fabrication",
   "controls": null}

  Datum frames ARE checked against the real machine envelopes, and that part holds:
  $ python3 scripts/simulation/verify_safety_zones.py
  REHEARSAL ONLY - actuates nothing. 4 zones, 2 unresolved dependencies.
    [ok]  zone-arms-cell / zone-arms-reach / zone-conveyor-cell / zone-fabrication-floor
    [GAP] printer-01  datum.origin is null (source: declared-by-operator)
    [GAP] cnc-01     datum.origin is null (source: declared-by-operator)
  No interlock is enforced in the simulation; they report only.
section: 10-simulation-architecture
---

SIM-05 stays open. It is the most nearly-complete item in my group, and the reason it
cannot close is not effort — it is that **the fourth acceptance limb asks for something the
portal is architected to refuse.**

The criteria require the world to be "fully settable and operable from the browser-served
HTML portal". The portal is deliberately view-only: `do_POST` returns 405 for every write
verb and `/api/health` advertises `view_only: true, controls: null`. Those are good
properties for a service that reports on a facility, and I am not proposing to weaken them
to satisfy a line of an acceptance table. Making the portal able to set and operate the
world is a change to the safety posture of a browser-reachable service, and it needs the
operator to say yes explicitly. That is a decision, not a ticket.

The other three limbs are genuinely advanced. The world exists and renders (SIM-06, verified
today). Boning is measurable and served at `/api/boning` with real datum frames, and the
safety-zone check passes on all four zones with honest GAPs for the two machines whose datum
origin is operator-declared rather than measured. RL objects are addressable as nine live
links. What is missing is export — `find artifacts -iname '*boning*'` returns nothing, so
boning is servable but not exported — and the runner script, which is a stub exiting 3.

One correction from this session: `/api/objects` was serving `"resettable": true` copied
from the YAML, which read as a verified capability when the portal exposes no reset endpoint
at all. It now sits beside `reset_available: false` and a note naming the discrepancy. That
makes the portal honest; it does not deliver reset, so this limb stays open on both counts.

**What I got wrong.** I opened by reading limb 4 as "the portal needs a few control routes
added" and started costing that out. Reading the handler changed my mind entirely: the
refusal is a documented design decision with a comment explaining why, not an oversight. I
was about to recommend removing a safety property of a browser-reachable service because an
acceptance table mentioned the word "operable". Matching the requirement's wording against
its actual intent is a step I skipped.
