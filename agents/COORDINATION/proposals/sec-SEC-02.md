---
item: SEC-02
action: update
evidence: |
  $ find ~/secrets -name 'fabrication*' -o -name '*fabrication-db*'
  (no output — the file ST-30 records does not exist)

  $ ls -la ~/.local/share/ao-secrets/fabrication-db.env
  -rw-------  1 scottw scottw  100 Oct  1 21:31 fabrication-db.env
  → the real path, consistent with the single-env-root rule in §14.1.2.

  $ ls -la ~/secrets/mastodon.env
  lrwxrwxrwx ... 39 Aug 29 19:39 mastodon.env -> /ALWAYSON/secrets/mastodon/mastodon.env
  $ ls -la /ALWAYSON/secrets/mastodon/mastodon.env
  ls: cannot access '/ALWAYSON/secrets/mastodon/mastodon.env': No such file or directory
  → dangling symlink. Inert: units read %h/.local/share/ao-secrets/, not ~/secrets/.

  $ grep -rn 'Secret=' quadlet/ | wc -l
  0
section: 14-secrets-and-service-identity
---
`update`. The policy/implementation reconciliation itself is done and is recorded in
**§14.1.6**; what remains is operator ratification, exactly as in SEC-01. Both items
share one decision, so they should close together.

Handled in this section file:

- **The reconciliation.** §14.1 mandates Podman secrets or systemd credentials;
  every implemented path is a wallet-materialised `0600` env file, which §14.1.1
  itself calls a plaintext duplicate. §14.1.6 records the deviation, states the
  compensating controls, and states env-file lifetime and shred-on-exit behaviour
  in full — including that env files are **not** shredded and persist between
  starts. The alternative (migrate to Podman/systemd credentials) is shown to be
  technically available for the database services and is **not applied**, because
  it changes live credential delivery.
- **The dangling §14.1.1 cross-reference.** The item notes "§14.1.1 points at a
  this document subsection that does not exist." Fixed: §14.1.1 now names **§14.1.6**
  and **§14.2** explicitly, and both now exist. That was the one pre-existing line
  I modified in §14.1.1 — everything else I added is below §14.1.5.

**`~/secrets/fabrication-db.env` (ST-30) — no such file exists.** The `find` above
returns nothing. The live file is `~/.local/share/ao-secrets/fabrication-db.env` at
`0600`, which matches §14.1.2's single-env-root rule. ST-30's text is stale and
should not be read as evidence of a second delivery path. **I did not edit ST-30** —
it is not mine — so this correction needs the §19 compiler to apply. This is
adverse-to-ST-30 rather than adverse-to-me, so I want it explicit: the honest
reading is that §14.1.2 was right and ST-30's note drifted, not that a secret is
sitting in a second location.

**Also found 2026-10-04, new: `~/.local/share/ao-secrets/legacy-alwayson-folder.env`** —
mode `0600`, untracked, referenced by no unit or script, and holding four
credential values by key name (`mastodon-db-password`, `sales-db-password`,
`webodm-postgres-password`, `fabrication-db-password`). This is precisely the
duplication SEC-02 exists to reconcile, and §14.1.1's own rules already forbid
it. By sha256 prefix, no values printed:

    legacy sales-db-password      = c0fa51768a38
    sales-db.env/POSTGRES_PASSWORD = c0fa51768a38  → SAME (live-valid)
    legacy mastodon-db-password    = cbd78a234974
    mastodon-db.env/POSTGRES_PASSWORD = 4cb870628b50 → DIFFERENT (stale)

`scripts/validation/check-secrets-exposure.sh` returns `OK` and does **not**
catch it — it checks tracked files and modes, and this file is neither. Recorded
in **§14.1.6**. **Not deleted**: deleting secret-classified material is outside
this session's authority. Recommend the operator delete it; the
`mastodon-db-password` it holds is already superseded, so nothing recoverable is
lost. Note the guard's blind spot — rule 7 checking that only inspects Git will
not see untracked `0600` files, and this is the first instance of that.

What I got wrong: my first `check-secrets-exposure.sh` invocation used a path
that does not exist (`scripts/operations/…`); the real path is
`scripts/validation/…`. The shell reported the error and **still exited 0**,
because the `EXIT=$?` I appended captured the exit of `tail`, not the script.
A missing file would have been recorded as a passing check. Same trap as the
`find -maxdepth 3` error already in this proposal: verify the command ran.

**Also found, not fixed: `~/secrets/mastodon.env` is a dangling symlink** to
`/ALWAYSON/secrets/mastodon/mastodon.env`, which does not exist. It is inert —
`quadlet/sales/ao-sales-db.container` and the Mastodon units all read
`EnvironmentFile=%h/.local/share/ao-secrets/…`, never `~/secrets/`. **I did not
remove it**: deletion is outside this session's authority (brief stop conditions)
and it may be another session's artifact. Reporting it for the operator.

What I got wrong: I first edited §14.1.6's heading to "Approved deviation" while
its own first line said "awaiting operator ratification" — the heading claimed an
approval that does not exist. I changed it to "Recorded deviation". A heading that
asserts operator consent is exactly the kind of thing this session must not
produce unprompted.