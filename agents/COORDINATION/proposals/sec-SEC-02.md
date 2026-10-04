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
it. Re-measured 2026-10-04 against each live env file by sha256 prefix, no
values printed:

    sales-db-password        = 03521083973b  len 48
    sales-db.env             = 03521083973b  len 48  → SAME (live-valid)
    webodm-postgres-password = 6d174927d250  len 32
    webodm.env               = 6d174927d250  len 32  → SAME (live-valid)
    fabrication-db-password  = f0d6bb4481fd  len 32
    fabrication-db.env       = f0d6bb4481fd  len 32  → SAME (live-valid)
    mastodon-db-password     = 8c3319896c87  len 48
    mastodon-db.env          = 4f090748460c  len 40  → DIFFERENT (stale)

**Three of the four are live database passwords.** `check-secrets-exposure.sh`
returns `OK: no secret-shaped content in tracked files` and does **not** catch it
— it checks tracked files and modes, and this file is neither. Recorded in
**§14.1.6**. **Not deleted**: deleting secret-classified material is outside this
session's authority. Recommend the operator delete it — because three values are
live, deletion strictly reduces exposure and costs nothing operationally (the
wallet is the system of record; live env files re-fetch at every start).
Rotation is *not* required by the file's existence; it was never committed to
Git, a backup set, or an external network. Note the guard's blind spot — a rule-7
check that only inspects Git will not see untracked `0600` files, and this is the
first instance of that.

What I got wrong (second pass, 2026-10-04): the first version of this proposal
reported **one** of the four values as live-valid. That was wrong, and the cause
was mine — I compared the legacy keys against guessed live key names
(`PGPASSWORD` for WebODM, upper-case `SALES_DB_PASSWORD`) which do not exist. All
three wrong guesses produced an empty `cut` result, so two *real* matches were
recorded as missing, and the one key I did get right was the only match reported.
A `grep` that finds nothing and an absent key look identical in a one-line
`cut`, and `printf '%s' '' | sha256sum` still prints a valid-looking
`e3b0c44298fc` (the SHA-256 of the empty string), so the failure was silent rather
than loud. Fix: enumerate the keys of each env file first, compare only names that
`grep` has confirmed exist, and treat an unexpected empty value as a broken
measurement rather than a negative result. §14.1.6 now carries the corrected
table and the correction is stated in the section itself, not silently fixed.

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