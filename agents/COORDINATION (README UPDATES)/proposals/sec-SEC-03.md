---
item: SEC-03
action: close
evidence: |
  $ grep -rln -i 'break-glass\|rotation\|revocation' --include='*.md' agents/COORDINATION (README UPDATES) (README UPDATES)/16*/section.md agents/COORDINATION (README UPDATES) (README UPDATES)/17*/section.md
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
- **§14.2.5 Break-glass order** — **5 steps** (was 4). Steps 1–4 non-destructive, step 5
  (rotate a live credential) reserved to the operator. Names the failure mode to avoid:
  adding a compensating `Environment=` line to a unit to work around a missing fetch,
  which turns a transient locked wallet into a permanent plaintext secret in a tracked file.

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

## Second pass, 2026-10-04 (this session)

**§14.2.5 gained a step, renumbered 1–5, nothing removed.** New **step 2: "Is a delivery copy
older than the process reading it?"** — compare env-file mtime against the unit's
`ActiveEnterTimestamp`. It earns a place in this document specifically because §14.1.7 found a
live service running on a delivery copy sixteen hours older than itself (SEC-04), and because
that fetch failed **without writing a single journal line**, owing to an `ExecStartPre=-`
ignore-failure prefix. Every other step in this list produces evidence; that one produces
nothing, so a new detection path was needed rather than a re-ordering of existing ones.

This also changes what "recovery" means at step 4. The list already says to *rotate, never
restore*, and §14.1.7 shows why that principle earns its place: `payment.env` could not be
regenerated because the wallet folder does not exist, and the only reason the service was
still functioning at all is that a **stale copy from before the fault** survived on disk. That
accident is the sole reason there is no outage. The generalisation — *"when a wallet entry
cannot be read, whatever delivery copy is still on disk is unverified material of unknown age,
and mtime versus unit start time is how you find out"* — is now stated in §14.1.7 rather than
left implicit, because it is the situation the operator will meet next.

**SEC-03 itself remains open.** Nothing in this pass supplies the missing wallet backup and
restore mechanism — that gap is unchanged, and §14.2.4 still records it. No credential was
rotated, revoked or inspected by value; this pass read entry *names*, file *modes*, and
sha256 *prefixes* only.

Re-verified unchanged this pass: `check-secrets-exposure.sh` exits 0; `podman secret ls` is
empty; `grep -rn 'Secret=' quadlet/` is 0.