---
item: PAY-07
action: close
evidence: |
  $ grep -c '| \`18' agents/COORDINATION/MANIFEST.md
  0

  # section 18 does not exist in the compiled document at all

  $ sed -n '74,78p' agents/COORDINATION/07-public-storefront-and-payment-policy/section.md   (before edit)
  2. A purchase button routes to provider-hosted checkout (PayPal hosted button
     today; Zelle instructions and Coinbase/USDC flow per Section 18.4 as

  $ python3 agents/COORDINATION/tools/compile.py
  wrote README.md from 21 sections
  exit=0

  $ git --no-pager diff --stat -- agents/COORDINATION/07-public-storefront-and-payment-policy/section.md README.md
   README.md                                          | 166 +++++++++++++++++++--
   .../section.md                                     | 166 +++++++++++++++++++--
  # README delta == section delta, so no other section drifted during recompile
section: 07-public-storefront-and-payment-policy
---
§7.2 now states in one normative place that the provider set — PayPal, Zelle and
Coinbase/USDC — **is decided and closed as a policy question**. It explicitly
reconciles the two stale references rather than leaving them to contradict it:
ES.2's "deployable once the provider decision is recorded (§7.2)" and ST-27's
"open on payment-provider selection" both refer to the *implementation* being
gated, not to the choice being unmade. §7.2 also states plainly that choosing the
providers never authorised accepting a payment — §4.1 rule 14 still applies and
ST-12 remains the gate.

I did **not** edit ES.2 or ST-27 (§00 and §19 are not mine). The reconciliation
is achieved by making §7.2 the single authority and naming the stale wording, so
the compiler session can update the other two in one pass if it wants the mirror.

Two things I got wrong:

1. **I initially treated a `Section 18.4` reference in my own file as a live
   cross-reference and went looking for a section 18.** There is no section 18.
   `MANIFEST.md` has no `18-*` entry and `git log --diff-filter=D` finds no deleted
   18 directory, so this was never a renumbering casualty — it is a dangling
2. **I nearly accepted ST-12's wording that the adapter "runs with no DSN" because
   §19 said so, and only checked because the Quadlet's own comment predicted the
   opposite.** The container env disagreed with §19 immediately. A row in §19
   describing live runtime state is a hypothesis; the running container is the
   measurement. I should have run `podman inspect` before reading anything else.
   reference to a section that does not exist in the compiled document. I
   repointed it at §7.2, which is where the Zelle/Coinbase content actually lives.
   **This is a repo-wide problem, not mine**: 70 dangling `Section 18.x`
   references across 21 files, including `scripts/payment/ao-payment-adapter.py`,
   `quadlet/networks/*.network`, `config/platform/topology-model.yaml`,
   `config/platform/version-matrix.yaml`, the Grafana dashboard JSON,
   `docs/compliance/*.md` and `docs/runbooks/mastodon*.md`. I fixed only the one in
   my file. **Recommend the compiler or OPS own a sweep**, because the adapter's
   501 handler text quotes "Section 18.4" to a client and to the operator, and the
   network unit files cite a section that is not there.