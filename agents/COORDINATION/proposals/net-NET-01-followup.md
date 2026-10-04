---
item: NET-01
action: update
evidence: |
  FOLLOW-UP to net-NET-01.md and net-NET-01-correction.md, neither of which I
  have modified. NET-01 REMAINS OPEN. This records a contradiction between two
  paragraphs of my own section file, which the earlier corrections left behind.

  The correction established by execution that the allowlist IS enforced in
  code. I re-ran all three cases myself this session rather than citing the
  earlier run:
  $ python3 scripts/build-update/ao-build-update.py localhost/foo:latest
    localhost/foo:latest: DENIED: localhost is on the adapter deny list
  EXIT=4
  $ python3 scripts/build-update/ao-build-update.py docker.io/library/nginx:latest
    docker.io/library/nginx:latest: UNPINNED: docker.io is allowed but the
    reference carries no sha256 digest
  EXIT=4
  $ python3 scripts/build-update/ao-build-update.py \
      'docker.io/library/nginx@sha256:0000...0000'
    docker.io/library/nginx@sha256:0000...0000: ALLOWED-PINNED
  EXIT=0

  Still, sixty lines below that verified evidence, the "Containment" paragraph
  still read:

    "**Containment - required, not yet enforced.** ... that restriction is not
     currently enforced by any mechanism, and this paragraph states the
     requirement the adapter must meet, not a control that is operating."

  That is flatly false and it contradicted the blockquote directly above it. The
  earlier correction fixed the blockquote and left the paragraph below it, so the
  section simultaneously told the reader the control was real and that nothing
  enforced it. Corrected.

  WHY IT SURVIVED TWO PASSES. Both prior sessions verified the script and both
  then edited only the nearest paragraph to the evidence. Nobody read forward to
  the next place the same claim was repeated. A correction verified against a
  command is still a correction against ONE occurrence, not against the claim.
section: 05-network-domains-and-controlled-external-access
---
**NET-01 stays open. What changed is that my section no longer contradicts
itself about whether the allowlist works.**

The corrected **Containment** paragraph now reads "enforced in code, unenforced
at the segment", matching the verified evidence above it, and states plainly
that its previous wording was wrong. The substance of the item is unchanged and
still blocked:

- **Segment-level enforcement is absent.** `ao-build-update` is an ordinary
  `Internal=false` bridge; anything else attached to it reaches the internet
  without consulting the allowlist. Closing this needs firewall or proxy policy,
  which is Rule 6 and §4.1 rule 13 territory. Not authored, not touched.
- **Separate adapter credentials** are a secret acquisition, an explicit stop
  condition. Not created.
- **`ao-ingress-payment` and `ao-egress-archive`** remain unimplemented, needing
  destination allowlists, validated TLS, separate credentials and connection
  logging.

All three remain operator decisions. I did not touch firewall policy, did not
create a credential, and did not enable the unit.