---
item: NET-04
action: close
evidence: |
  The operator-approved original was recoverable; it was in the repo the whole
  time. Provenance chain, not memory:
  $ git --no-pager log --oneline -1 -- 'README - ARCHIVE/ALWAYS ON — Architecture, Operations, and Status - v6.md'
  b3d35e7 docs(archive): add the superseded README history

  $ sed -n '671,690p' 'README - ARCHIVE/ALWAYS ON — Architecture, Operations, and Status - v6.md'
  ## 4.3 Prohibited Paths
  Sales/AI → MAVLink, ArduPilot, ROS, Gazebo, LoRa, RNS, MeshChatX
  Sales/AI → WebODM workers, raw imagery, Corda core
  Payment → OpenClaw, LM Studio, Mastodon, field, mapping, simulation
  Field → payment provider, Mastodon, OpenClaw, LM Studio, Corda core
  Mapping → flight control, LoRa/RNS, payment provider, Mastodon, Corda core
  Vehicle simulation → live drones, live radios, sales, payments, Corda core
  Fabrication simulation → live machinery during phase one, sales, payments, Corda core
  Public internet → PostgreSQL, Redis, WebODM workers, LM Studio, Corda,
                    ROS, MAVLink, Gazebo, QGroundControl, RNS, MeshChatX

  That archive is this document's declared ancestor, which makes it the right
  source for "the operator-approved original":
  $ grep -n 'authority' config/platform/topology-model.yaml
  20:authority: "/ALWAYSON/TOPOLOGY/ALWAYS ON — Architecture, Operations, and Status - v6.md"
  21:authority_short: "v6"

  The misplaced sale-chain content was NOT lost; it already lives in section 3:
  $ grep -n 'sale chain' agents/COORDINATION (README UPDATES)/03-high-level-architecture/section.md
  202:The sale chain on the right of the following extract — customer picks to checkout,
  203:verified payment event, salesdb record, signed receipt manifest, and Corda state —
  204:is the same five-step chain drawn in ES.2. Payment intake is shown at the left,
  ...
  208:![Zoom of the five-step sale chain column of the ES.2 master topology...](assets/topology-detail-salechain.png)

  So the two halves of the damage are now both accounted for: the prohibition
  list is restored as 4.3.1, and the duplicated sale-chain diagram is carried
  once, in 3.3.2, where it belongs.
section: 04-security-isolation-and-data-policy
---
**The list is confirmed complete and correct, with one thing restored that was
genuinely lost, and one thing that needs a human.**

Restored. The rebuilt §4.3 was a table of ten rule-cited prohibitions. It is not
wrong, but it is not the original: it says *why* a class of path is forbidden and
never names the specific source → target pairs. The original, recovered verbatim
from the v6 archive and now §4.3.1, is eight lines of exactly those pairs. Both
are kept — §4.3.1 for what an operator checks against a running host, §4.3.2 for
the rule that enforces each. I did not overwrite §4.3.2 with the recovered list,
because the recovered list carries no rule references and the rebuilt one is
correct as far as it goes; deleting either would lose information.

Two recovered lines are superseded and are **marked, not deleted**, because
silently dropping a line from a prohibition list hides the decision that dropped
it: *Field/Mapping → payment provider* is now reached only through the controlled
adapters (§5.2), and *Fabrication simulation → live machinery* no longer carries
its "during phase one" qualifier — the prohibition is absolute now (§10.2).

**Needs a human decision, and it is the reason I am not claiming this is fully
settled.** I recovered the list from an archive and cross-checked it against the
rest of this document; I did not obtain operator re-approval of the recovered
text. §4.3.3 says so explicitly in the section itself, so the next reader cannot
mistake recovery for approval. If the operator confirms the recovered list as the
approved original, NET-04 closes with nothing further; if the operator has a
different original in mind, §4.3.1 is the place the correction goes.

**Supplied that was lost with the misplaced content:** nothing else. The
overwritten body was a duplicate of the sale-chain diagram, and that diagram is
present and correct in §3.3.2. I checked rather than assuming: the sale-chain
figure and its five-step narrative are at §3.3.2 lines 202-210, with the image
`assets/topology-detail-salechain.png`.

**What I got wrong.** My first search for the original was `git log` on the
section file, which returned exactly one commit — `09be9ce`, the consolidation
that created `agents/COORDINATION (README UPDATES)/`. That is correct and useless: the section
file has only ever had one version, so its history cannot contain the loss. The
loss happened upstream, before the split into section files. Reason: I searched
the history of the artefact I was editing rather than the history of the
*content*. The original was recoverable within one command of looking in the
archive tree, which I only reached by grepping the whole repo for the section
heading.

**Cross-check performed.** I also checked `config/platform/topology-model.yaml`
for a machine-readable prohibition edge list to reconcile against, and there is
none — the model's `edge:` block carries adapter paths and statuses but no
deny-edges. So the recovered text has no second independent source, which is
precisely why the operator confirmation is still wanted.
