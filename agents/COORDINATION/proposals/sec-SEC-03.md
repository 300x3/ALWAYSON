---
item: SEC-03
action: close
evidence: |
  $ grep -rln -i 'break-glass\|rotation\|revocation' --include='*.md' agents/COORDINATION/16*/section.md agents/COORDINATION/17*/section.md
  (no match in §16/§17; only "Rotation: /etc/logrotate.d/" — logs, not credentials)

  $ grep -n 'restic backup' scripts/backup/restic-run.sh | head -1
  ao_run bash -c "... restic backup '$AO_ROOT/config' '$AO_ROOT/artifacts'
  '$AO_ROOT/backups/postgres' '$AO_ROOT/data/ardupilot' ... --tag alwayson"

  → §14.2.4: ~/.local/share/kwalletd/ is NOT in the backup set, and cannot be
  (a .kwl is encrypted against kdewallet.salt). Recorded as a gap, not papered over.
  The procedure is backed up (lives in this section, under $AO_ROOT/config);
  the secrets are rotated, never restored.

  $ grep -n 'shred' scripts/operations/*.sh scripts/mastodon/post.sh scripts/ledger/sign-manifest.sh
  → only post.sh and sign-manifest.sh shred. Confirms §14.1.6's claim that env
  files are NOT shredded on exit.
section: 14-secrets-and-service-identity
---
Added §14.2 covering all four things §14.1.1 required and none of which were
documented anywhere:

- **§14.2.1 Rotation** — 4-step table. The load-bearing rule: rotate in the
  wallet and restart the unit, never edit the env file (it is overwritten at the
  next start) and never re-run `genenv` (would mint new SECRET_KEY_BASE /
  OTP_SECRET and invalidate every session). Includes the `pg_hba` 127.0.0.1-trust
  trap: verify a changed role password over TCP, not the socket.
- **§14.2.2 Revocation** — per-credential. Wallet entry overwrite; Doorkeeper
  `revoked_at` sweep for the bridge token; SECRET_KEY_BASE as a deliberate
  session-invalidating action; and the note that revocation is incomplete until
  the old value is out of backups too.
- **§14.2.3 Expiration** — none enforced; the `expires_in: nil` bridge token is
  a standing rotation obligation, not a solved problem.
- **§14.2.4 Wallet backup and restore** — the gap above, plus an interactive
  restore procedure whose fallback is rotation (ALTER ROLE / re-mint / put),
  never recovering an old value.
- **§14.2.5 Break-glass order** — 4 steps, first three non-destructive, fourth
  (rotate a live credential) reserved to the operator. Names the failure mode to
  avoid: adding a compensating `Environment=` line to a unit to work around a
  missing fetch, which turns a transient locked wallet into a permanent
  plaintext secret in a tracked file.

I also noted that `docs/runbooks/secrets.md` is stale — it describes
per-service-account homes and a manual copy-out step, both superseded by §13.2
and the wallet flow — and marked §14.2 as authoritative over it. **I did not
edit that runbook**: it is not my file, and correcting it is a separate call.

What I got wrong: my first attempt to confirm `POSTGRES_PASSWORD_FILE` support
used `find / -maxdepth 3`, which missed `/usr/local/bin/docker-entrypoint.sh`
(depth 4) and made me briefly believe the image did not honour it. A later
`-maxdepth 1`-style search on `/` found it. The conclusion was unchanged, but
the first measurement was wrong — when a `find` returns nothing, verify the depth
before concluding the file is absent.