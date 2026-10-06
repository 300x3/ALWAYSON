---
item: SEC-03
action: close
evidence: |
  The documentation item is satisfied; §14.2 exists and covers all four required
  subjects. Re-verified 2026-10-05 that its load-bearing external claims still hold.

  Rotation / revocation / recovery are documented nowhere else — the §19 sibling
  sections contain no credential material (only logrotate):

    $ grep -rln -i 'break-glass\|rotation\|revocation' \
        agents/COORDINATION (README UPDATES) (README UPDATES)/16*/section.md agents/COORDINATION (README UPDATES) (README UPDATES)/17*/section.md
    → only "Rotation: /etc/logrotate.d/" — logs, not credentials

  The backup gap claim in §14.2.4 still holds, re-read from the live script:

    $ grep -n 'restic backup ' scripts/backup/restic-run.sh | head -1
    ao_run bash -c "set -a && source '$envfile' && restic backup '$AO_ROOT/config'
    '$AO_ROOT/artifacts' '$AO_ROOT/backups/postgres' '$AO_ROOT/data/ardupilot' …"

  → ~/.local/share/kwalletd/ is NOT in the list, and cannot be (a .kwl is encrypted
  against kdewallet.salt). Stated as a gap, not papered over. The procedure is backed
  up (it lives in this section, under $AO_ROOT/config); the secrets are rotated,
  never restored.

  The non-shredding claim in §14.1.6/§14.2.1 still holds — only three scripts shred:

    $ grep -rln 'shred' scripts/
    scripts/mastodon/post.sh
    scripts/mastodon/mastodon-openclaw-bridge.py
    scripts/ledger/sign-manifest.sh

  §14.2.5 break-glass order verified still applicable, and extended: step 2's
  mtime-versus-start-timestamp check now carries the converse case.
section: 14-secrets-and-service-identity
---
Confirming **closed** as proposed on 2026-10-04, with the procedure re-verified rather
than assumed. §14.2 documents all four things §14.1.1 required and none of which existed
before: rotation (§14.2.1), revocation (§14.2.2), expiration (§14.2.3), and wallet backup
plus recovery (§14.2.4), with a break-glass order for the operator (§14.2.5). Every
external claim the procedure depends on was re-measured today and still holds: the wallet
is outside the restic set, and delivery copies are not shredded.

This pass **strengthened §14.2.1 and §14.2.5** rather than changing their shape, because
the `mastodon.env` divergence (see sec-SEC-02-recheck) is precisely a failure of the
verification steps as originally written:

- §14.2.1 step 3 accepted "file mtime advanced" as proof a rotation completed. That check
  passes while the file disagrees with the wallet, because a legitimate fetch can be
  followed by a divergence. The pass condition is now **wallet and delivered copy hash
  equal, and the unit has restarted** — neither "the file changed" nor "the unit is active"
  is sufficient.
- §14.2.5 step 2 treated only "file older than process" as the fault signature. The live
  `ao-ingress-payment` state is its mirror image — a correct newer file behind a process
  that predates it — so the check now compares the file against the process's actual
  environment via `podman inspect … Config.Env`.

That is the substantive reason to close this item now rather than at the end of the pass:
the procedures were documented on 10-04, and today's measurement found the one verification
gap they had. Both gaps are now closed in the section file itself.

No credential, unit, wallet entry or file mode was changed by this session.