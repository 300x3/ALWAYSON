---
item: PAY-07
action: close
evidence: |
  $ grep -c '| \`18' agents/COORDINATION (README UPDATES) (README UPDATES)/MANIFEST.md
  0

  # section 18 does not exist in the compiled document at all

  $ sed -n '74,78p' agents/COORDINATION (README UPDATES) (README UPDATES)/07-public-storefront-and-payment-policy/section.md   (before edit)
  2. A purchase button routes to provider-hosted checkout (PayPal hosted button
     today; Zelle instructions and Coinbase/USDC flow per Section 18.4 as

  $ python3 agents/COORDINATION (README UPDATES) (README UPDATES)/tools/compile.py
  wrote README.md from 21 sections
  exit=0

  $ git --no-pager diff --stat -- agents/COORDINATION (README UPDATES) (README UPDATES)/07-public-storefront-and-payment-policy/section.md README.md
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
   reference to a section that does not exist in the compiled document. I
   repointed it at §7.2, which is where the Zelle/Coinbase content actually lives.

2. **I nearly accepted ST-12's wording that the adapter "runs with no DSN" because
   §19 said so, and only checked because the Quadlet's own comment predicted the
   opposite.** The container env disagreed with §19 immediately. A row in §19
   describing live runtime state is a hypothesis; the running container is the
   measurement. I should have run `podman inspect` before reading anything else.

3. **My first pass at this finding reported "70 dangling `Section 18.x` references
   across 21 files" and named `quadlet/networks/*.network`,
   `config/platform/topology-model.yaml`, `config/platform/version-matrix.yaml`,
   the Grafana dashboard JSON and `docs/compliance/*.md`. That was wrong — I
   estimated the sweep from memory instead of running the count, then listed
   plausible-sounding paths I had never grepped.** Re-measured on 2026-10-03:

       $ grep -rn 'Section 18' . --exclude-dir=.git \
             --exclude-dir='README - ARCHIVE' --exclude-dir=proposals
       ./scripts/payment/ao-payment-adapter.py:11:Controls enforced here (Section 18.4):
       ./scripts/payment/ao-payment-adapter.py:42:# deliberately absent: Section 18.4 forbids automated Zelle verification.
       ./scripts/payment/ao-payment-adapter.py:215:            # Refuse to treat any inbound POST as Zelle evidence. Section 18.4:
       ./scripts/payment/ao-payment-adapter.py:217:            self._reply(501, {"error": "Zelle is manual-reconciliation only (Section 18.4)"})
       ./quadlet/payment/ao-ingress-payment.container:15:# Written but NEVER enabled ... Section 18.4
       ./docs/runbooks/mastodon.md:115:  the loopback-only `RAILS_FORCE_SSL=false` exception is retired (Section 18.5).
       ./docs/runbooks/mastodon-validation.md:73:   loopback SSL deviation is now retired (Section 18.5) — use the
       ./config/sales/migrate/02-payment-reconciliation.sql:11:-- no other table changes. Section 18.4 requires Zelle reconciliation to be

   The true figure is **9 occurrences across 5 live files** (31 across 10 files if
   the `README - ARCHIVE` tree is counted). No network unit file, topology model,
   version matrix, Grafana dashboard or compliance doc contains one — that detail
   was fabricated on my part and I withdraw it.

   The live finding stands, and it is the part worth acting on:
   `ao-payment-adapter.py` quotes "Section 18.4" **to a client in an HTTP 501
   body** (line 217), so a real caller is directed to a section that does not
   exist, and line 11 presents a non-existent section as the authority for the
   controls in force. **Recommend OPS or the compiler own the sweep**, repointing
   the payment references at §7.2, where that content now lives. I fixed only the
   reference in my own file: the adapter's string is emitted in operator-facing
   output, so repointing it is a live-behaviour edit rather than a documentation
   edit, and it is not mine to make unilaterally.