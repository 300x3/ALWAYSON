---
item: NET-05
action: create
evidence: |
  NEW ITEM RAISED BY THIS SESSION, not closed. It is a divergence between two
  files, one of which is not mine.

  ao-html-window's purpose is recorded two different ways.

  ES.2 says it is a public-facing egress window publishing to 300x3.com:
  $ grep -n 'ao-html-window' agents/COORDINATION/es-executive-summary/section.md
  73:| **`ao-html-window`** | adapter | **A public-facing (egress) window
     for viewing HTML content on the 300x3.com website.** ... It only ever
     needs to publish to 300x3.com ... | Outbound publication to 300x3.com
     only. Deployable |

  The deployed unit says the opposite - it has no route off the host at all:
  $ cat quadlet/networks/ao-html-window.network
  # Operator-facing READ-ONLY display network: serves 2D/3D HTML renders to the
  # operator's browser. It accepts NO input and exposes NO control channel.
  # Requested by operator 2026-10-01.
  # Internal=true is deliberate and NOT a limitation.
  [Network]
  NetworkName=ao-html-window
  Driver=bridge
  Internal=true

  And it is currently carrying a simulation container, not a storefront:
  $ podman inspect ao-sim-fabrication-foxglove \
      --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}'
  ao-html-window ao-sim-fabrication

  "Publishes only to 300x3.com" and "Internal=true, no route off the host" cannot
  both be true. An Internal=true bridge cannot publish to anything off-host.

  WHY THIS IS NOT MINE TO FIX. ES.2 belongs to the executive-summary session.
  Changing the deployed network to match ES.2 would mean flipping Internal=false,
  which is a public-routing change and Rule 6 territory. Changing ES.2 to match
  the deployed unit is the likely correct direction, but it is not my file.
  I corrected only my own row in section 05 and flagged this.

  It is also a public-exposure question, so it is explicitly NOT something I
  should resolve unilaterally: if ES.2 is the accurate intent, then publishing
  this network is an unapproved public path that needs the operator.
section: 05-network-domains-and-controlled-external-access
---
**New work item: reconcile `ao-html-window`'s recorded purpose with its
deployed state.**

My §5.1 row previously repeated ES.2's claim and was therefore wrong about the
running host. It now states what the deployed unit actually does: an
`Internal=true`, loopback-only, read-only display network. The re-measured
*Attached now* column and a new §5.1.2 are described in
`proposals/net-NET-02.md`, which covers the same evidence.

Nothing is published, nothing is exposed, and no configuration was touched. This
item asks a question, and its answer may be "ES.2 is stale and should be edited",
which is the executive-summary session's call, or "this network should be
public", which is the operator's call under §4.1 rule 6.

Acceptance criteria: ES.2 and §5.1 agree on what `ao-html-window` is; and the
`Attached now` column is known to be re-measurable rather than assumed.