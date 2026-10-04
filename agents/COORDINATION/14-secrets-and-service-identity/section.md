# 14. Secrets and Service Identity

## 14.1 Secret Delivery

Use Podman secrets or systemd credentials. Prefer file-based secret delivery
rather than environment variables.


### 14.1.1 KDE Wallet Secret Management

KDE Wallet is the operator-side secret and credential store for this host. Section 14.1 is
the policy; this subsection is the integration. The unattended-delivery deviation is recorded
in **§14.1.6**, the rotation and recovery procedure in **§14.2**.

**Runtime.** Daemon `kwalletd6` on the `org.kde.kwalletd6` D-Bus name, wallet `kdewallet`,
auto-unlocked with the operator's Plasma login. `org.kde.kwalletd` and `org.kde.kwalletd5`
are also live; prefer `kwalletd6` in new code.

| Item | Value |
|---|---|
| Object path | `/modules/kwalletd6` |
| `open()` | returns a live handle against wallet `kdewallet` |
| Methods used by `scripts/ops/wallet-read-secret.py` | `hasEntry`, `readPassword` |
| Method used by `scripts/ops/wallet-write-secret.py` | `writePassword` |

**Tooling.**

- Management CLI `scripts/ops/kwallet-provision.sh` (`create-folders`, `put`, `get`), run only
  from the interactive Plasma session while the wallet is unlocked.
- `scripts/operations/fetch-kwallet-secret.sh` runs as a Quadlet `ExecStartPre`: it waits for
  the desktop session and kwalletd (max ~60s), reads the required entries, and writes a
  service-specific `0600` env file the unit consumes via `--env-file`. It serves
  `ao-mastodon-db`, `ao-sales-db`, `ao-webodm-db` and `ao-fabrication-db`. **A new key must be
  added as a `case` branch in that script or the unit fails.**
- Env files materialise under `%h/.local/share/ao-secrets/`, via `ao-wallet-bridge.sh` or the
  unit's own `ExecStartPre`. `~/secrets/` holds unrelated material and is not part of the
  delivery path.

**Login-gated start is intended.** Services that consume wallet secrets start after Plasma
login and are not expected to start unattended before a password is entered. The ~60s wait is
the bounded startup allowance for that login, not a fallback for a passwordless boot. Auto-login
is an operator convenience, not a requirement of this design.

**All services run under the operator's own account.** No service requires a separate
service-account user, and no per-service container store is created (§13.2).

**One folder per domain.** Every credential lives in exactly one `ao-*` folder and its service
reads it from there, so a role and the application connecting to it always share one value.
There is no generic or cross-domain folder.

| Folder | Purpose |
|---|---|
| `ao-mastodon` | Mastodon application secrets (§15.3) and OpenClaw OAuth material; read by `fetch-mastodon-env.sh` and the wallet bridge |
| `ao-sales` | `sales-db-password` |
| `ao-fabrication` | `fabrication-db-password` |
| `ao-mapping` | WebODM postgres password |
| `ao-admin` | `grafana-db-password`, `grafana-admin-password`, `metabase-db-password`, `metaread-password`, `sales-reporting-password`, `restic-repository-password` |
| `ao-sim-vehicle`, `ao-sim-fabrication` | Per-domain credential folders matching the §14.1 authorized-domain table |
| `ao-payment`, `ao-field`, `ao-ledger`, `ao-archive` | Created only when the consumer exists and the credential is provisioned (§14.1.2), never speculatively. `ao-payment` is provisioned as part of ST-12 |

Entries are listed by name only — values are never in Git, logs, or docs. Every key lives in
the `ao-` folder for the domain that owns it.

| Folder | Entries |
|---|---|
| `ao-mastodon` | `mastodon-secret-key-base`, `mastodon-otp-secret`, `mastodon-db-password`, `mastodon-ar-deterministic-key`, `mastodon-ar-primary-key`, `mastodon-ar-derivation-salt`, `mastodon-admin-password`, `openclaw-bot-client-id`, `openclaw-bot-client-secret`, `openclaw-bot-access-token`, `openclaw-bot-password`, `roundtrip`/`roundtrip2` (test artifacts) |
| `ao-sales` | `sales-db-password` |
| `ao-fabrication` | `fabrication-db-password` |
| `ao-mapping` | WebODM postgres password |
| `ao-admin` | `grafana-db-password`, `grafana-admin-password`, `metabase-db-password`, `metaread-password`, `sales-reporting-password`, `restic-repository-password` |

**Rules.**

- Never print, copy, export, or log entry values; confirm presence only, using the D-Bus
  `hasEntry` method on `org.kde.kwalletd6`. (`entryList` takes a further argument and is not
  used by the tooling.)
- Entries are named per service and per purpose; domain folders enforce the §14.1
  authorized-domain boundaries.
- Rotation, revocation, expiration, and recovery procedures must be documented before
  production use.
- **No plaintext duplicate of a wallet entry exists.** Credential material lives in the wallet
  and nowhere else. No file under `secrets/` or `config/` may hold a credential the wallet also
  holds.

**Grafana is wallet-backed like everything else.** Its web admin password is
`ao-admin/grafana-admin-password`; `fetch-kwallet-secret.sh` maps it through `wallet_folder_for`
and emits a `grafana-admin-password` case branch, and `ao-grafana.container` reads two files:
`config/platform/monitoring/grafana-admin.env` for non-secret settings
(`GF_SECURITY_ADMIN_USER`, `GF_USERS_ALLOW_SIGN_UP`, `GF_AUTH_ANONYMOUS_ENABLED`) and
`%h/.local/share/ao-secrets/reporting-grafana-admin.env` for `GF_SECURITY_ADMIN_PASSWORD`,
materialised `0600` by the unit's `ExecStartPre` and never tracked. `/api/health` returns 200
with database ok, and an admin login using the wallet value returns HTTP 200.

**Scripts that need these credentials read them from the wallet at start-up, never from a
plaintext file.**

- `scripts/operations/fetch-kwallet-secret.sh` — carries the `ao-admin` keys in
  `wallet_folder_for`.
- `scripts/ops/provision-metaread.sh`, `provision-sales-reporting.sh` — read the password from
  the wallet and mirror it back instead of seeding it from a file.
- `scripts/ops/provision-reporting-postgres.sh` — reads `metabase-db-password` and
  `grafana-db-password` from `ao-admin`.
- `scripts/mastodon/post.sh` — materialises the bot credential from the wallet into a `0600`
  temp file and shreds it on exit.
- `scripts/mastodon/provision-openclaw-bot.sh` — stores the generated password in the wallet
  only and writes no env file.

`check-secrets-exposure.sh` carries three rule-7 checks: a tracked `.env` must not carry a
credential, a Quadlet `EnvironmentFile` pointing into `config/` or `secrets/` must not be
secret-bearing, and any secret-bearing env file on disk must not be readable by other users.

### 14.1.2 Secret-delivery rules

**One folder per domain.** Each credential lives in exactly one `ao-*` folder, and each
service reads it from there. There is no generic or cross-domain wallet folder, and
`fetch-kwallet-secret.sh` maps each key to its owning folder rather than a hardcoded one.

| Credential | Folder |
|---|---|
| `sales-db-password` | `ao-sales` |
| `fabrication-db-password` | `ao-fabrication` |
| `webodm-postgres-password` | `ao-mapping` |
| `mastodon-db-password` | `ao-mastodon` |
| `payment-db-password`, `payment-paypal-webhook-id`, `payment-paypal-webhook-secret`, `payment-coinbase-webhook-secret` | `ao-payment` |
| `pcloud-webdav-password`, `pcloud-webdav-user` | `ao-archive` |

The last two rows are mapped in `wallet_folder_for` but **neither folder exists on this
host**. Measured 2026-10-04, `folderList` de-duplicated returns exactly seven `ao-*`
folders — `ao-admin`, `ao-fabrication`, `ao-mapping`, `ao-mastodon`, `ao-sales`,
`ao-sim-fabrication`, `ao-sim-vehicle` — and `ao-payment` and `ao-archive` are both absent.
§14.1.1 already says these folders are "created only when the consumer exists and the
credential is provisioned, never speculatively"; the `ao-payment` consumer does exist and is
running, which makes its absent folder a fault rather than correct restraint. See §14.1.7.

**Mapping is not the same as deliverability.** `wallet_folder_for` routes 30-odd entry names,
but a mapping only means the fetcher will *try*. Several entries the fetcher names are read
by other consumers instead — `openclaw-bot-client-secret` and
`cloudflare-tunnel-credentials-json` by `fetch-openclaw-mastodon-env.sh` and
`fetch-cloudflared-env.sh`, `producer-private-key` by `scripts/ledger/sign-manifest.sh` —
and those are not affected by a missing entry in `wallet_folder_for`. Conversely an entry
that *is* mapped but whose folder is absent is a hard fetch failure, which is the
`ao-payment` case.

A role and the application that connects to it must use the same password, so a fresh
`mastodon-dbdata` cannot be created with a different password than the application connects
with.

**One env root.** Every unit that consumes a secret-bearing env file reads
`%h/.local/share/ao-secrets/`: `ao-mastodon-db`, `ao-sales-db`, `ao-webodm-db`,
`ao-webodm-web`, `ao-webodm-worker`, `ao-fabrication-db`, the `ao-mastodon-web` /
`ao-mastodon-streaming` / `ao-mastodon-sidekiq` set, `ao-mastodon-web`'s repair `ExecStartPost`,
`ao-grafana`, `ao-metabase`, `ao-ingress-payment`, `ao-status-collect`,
`ao-db-security-collect` and `ao-fabrication-collect`. No secret-bearing env file is written to
`%h/secrets/`.

The one deliberate exception is `ao-grafana`'s
`EnvironmentFile=/ALWAYSON/config/platform/monitoring/grafana-admin.env`. It sits in the tracked
`config/` tree and is readable by other users (`0644`), which is safe only because it is
non-secret by construction: `GF_SECURITY_ADMIN_USER`, `GF_USERS_ALLOW_SIGN_UP`,
`GF_AUTH_ANONYMOUS_ENABLED` and `GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS` and nothing else. The
admin password is read separately from the `0600` wallet-materialised file. Verify the
non-secreteness by key name, not by assuming it:

    $ sed 's/=.*/=/' config/platform/monitoring/grafana-admin.env | grep -v '^#' | grep -v '^$'
    GF_SECURITY_ADMIN_USER=
    GF_USERS_ALLOW_SIGN_UP=
    GF_AUTH_ANONYMOUS_ENABLED=
    GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS=
    → exactly four keys, no password, token or key name present.

Two stray files under `ao-secrets/` are documented elsewhere: the orphaned
`legacy-alwayson-folder.env` (**§14.1.6**) and the dangling `~/secrets/mastodon.env` symlink,
which is outside this root and inert.

### 14.1.3 One env file, one wallet entry

**There is exactly one env file, and it is the live `EnvironmentFile`.**

| Location | Role |
|---|---|
| `~/.local/share/ao-secrets/mastodon.env` | **The only env file.** Loaded by `EnvironmentFile=` in `quadlet/sales/ao-mastodon-web.container` |
| KDE Wallet `kdewallet` / `ao-mastodon` / `mastodon-env` | Wallet copy of the same content, verified byte-identical by SHA-256 (1043 bytes) |
| KDE Wallet `ao-mastodon` / `mastodon-secret-key-base`, `mastodon-otp-secret`, `mastodon-db-password` | Per-key wallet entries |

No second copy of this file is kept anywhere, and nothing may be restored into the
repository. A stale copy is worse than no copy: its `DB_PASS` / `POSTGRES_PASSWORD` would not
match the running instance and its `LOCAL_DOMAIN` would be wrong, so restoring it would
break PostgreSQL auth for `mastodon-db`.

**`genenv` is non-destructive by rule.** It refuses to run when the env file already exists.
Regenerating it would mint new `SECRET_KEY_BASE` / `OTP_SECRET` / `POSTGRES_PASSWORD`,
invalidate every session, break DB auth, and write `LOCAL_DOMAIN=localhost` — breaking the
instance and its federation.

**`genenv` derives its path from `$HOME`, never `$AO_ROOT`.** The repository root is
`/ALWAYSON`; writing there would place a second, untracked, non-ignored copy of the secrets
inside the working tree. This is the same class of bug as the drift the single-file rule
prevents.

Consumers of the env file are `scripts/mastodon/deploy-mastodon.sh` and
`scripts/mastodon/provision-mastodon-encryption.sh`.

### 14.1.4 KDE Wallet D-Bus access

For services that must read secrets unattended, the wallet is reached over D-Bus as follows.

| Element | Value |
|---|---|
| Bus name | `org.kde.kwalletd6` (also answers `org.kde.kwalletd`, `org.kde.kwalletd5`) |
| Object path | `/modules/kwalletd6` |
| Interface | `org.kde.KWallet` |
| Wallet in use | `kdewallet` (`wallets()` returns `as 1 "kdewallet"`) |

Signatures for the methods the tooling actually uses:

```
wallets()                      -> as
open(s wallet, x appId, s app)  -> i handle      (-1 = unavailable/locked)
close(i handle, s app, b forget) -> i
readPassword(i, s folder, s key, s app)  -> s
writePassword(i, s folder, s key, s value, s app) -> i
folderList(i handle, s app)     -> as
hasFolder(i, s folder, s app)   -> b
createFolder(i, s folder, s app) -> b
entriesList(i, s folder, s app) -> a{sv}
```

**Three `busctl` pitfalls, all of which produce misleading errors:**

1. `int64` arguments need an explicit type prefix — `open kdewallet x 0 app`.
   Without it: `Unknown signature type k`. Omit `x` and the call fails.
2. Several methods are **overloaded**, and `busctl` picks one signature:
   `isOpen` exists as both `isOpen(i)` and `isOpen(s)`, so
   `isOpen kdewallet` fails with `Too few parameters for signature`.
3. **The same overload trap applies to `dbus-python`, not just `busctl`.**
   dbus-python binds the proxy to the *last declared* signature, so
   `iface.isOpen(handle, 'app')` raises
   `TypeError: Fewer items found in D-Bus signature` — the opposite error text
   from `busctl`, for the same underlying cause. **Use the one-argument
   `isOpen(handle)`.** `folderList` and `entriesList` are also multi-argument:
   `folderList(handle, app)` and `entriesList(handle, folder, app)`.

There is **no `listFolders` method** — the folder enumeration method is
`folderList`. There is also no `introspect` on `org.kde.KWallet`; that lives on
`org.freedesktop.DBus.Introspectable`. Both mistakes were made and corrected
while auditing the Mastodon bridge.

**`folderList` returns DUPLICATE rows — de-duplicate before counting.** Measured
2026-10-01: a raw count reported 990 rows / "972 folders", which looks like
catastrophic duplication. `set()` gives the true **18 folders**; the same applies
to `entriesList`, whose de-duplicated `ao-*` + `Passwords` total is **39 entries**.

**Readiness: use `isOpen`, not daemon presence.** Gating on
`busctl --user list | grep kwalletd6` is wrong — kwalletd6 is D-Bus-activated the
moment anything touches it and appears long before the wallet is unlocked, so the
gate returns true instantly and any timeout behind it never waits. This caused a
login outage on 2026-10-01: `ao-grafana` and `ao-metabase` read a locked wallet,
failed their `ExecStartPre`, exhausted systemd's 5 fast restarts in ~5s and stayed
down. Both fetchers now use `isOpen(handle)` with a 30×2s budget.

**The locked path cannot be tested directly.** KWallet exposes no `lock()`;
`closeAllWallets()` does not leave the wallet locked, because the next `open()`
transparently re-unlocks via PAM. Use the forensic signal instead: a **0-byte
`.tmp`** from a failed fetch proves the wallet was locked, since the write block
never ran.

**Environment is not a barrier.** The systemd user manager carries
`DBUS_SESSION_BUS_ADDRESS`, `DISPLAY`, `WAYLAND_DISPLAY` and
`XDG_RUNTIME_DIR`, so a user unit needs no `Environment=` additions to reach
the wallet.

**Token requirements.** An HTTP 401 from the OpenClaw bridge is a token problem, never a
D-Bus, transport, or token-format problem. The requirements:

1. The systemd user manager carries `DBUS_SESSION_BUS_ADDRESS`, `DISPLAY` and
   `WAYLAND_DISPLAY`. A minimal `Environment=` block does not block wallet access.
2. A Mastodon access token is **43 base64 characters**, not 64 hex characters.
3. A token must be created with `expires_in: nil`. Doorkeeper reads `expires_in: 0` as
   *expires in zero seconds* — already expired — and the API answers
   `{"error":"The access token expired"}`.
4. The bridge owns a Doorkeeper application (`openclaw-mastodon-bridge`) with scopes
   `read:accounts read:notifications write:statuses read:statuses`. The token is stored in
   KDE Wallet at `ao-mastodon` / `openclaw-bot-access-token`, never in a file.

**Re-minting, when needed:** create or reuse the app, revoke prior tokens for
it, then create the token with `expires_in: nil`. Always store the result in
KDE Wallet rather than a file, and shred the temporary copy. Do not copy
existing token-handling scripts without checking for `expires_in: 0`.

### 14.1.5 Minting Mastodon API tokens

```
podman exec -i mastodon-web sh -c 'cat > /tmp/mint.rb' < mint.rb
podman exec mastodon-web sh -c \
  'cd /opt/mastodon && RAILS_ENV=production bundle exec rails runner /tmp/mint.rb'
```

```ruby
bot   = Account.find_by(username: 'bot', domain: nil)   # Mastodon 4.3 has no `local` column
owner = bot.user                                        # Doorkeeper owner_id/resource_owner_id are users.id
SCOPES = 'read:accounts read:notifications write:statuses read:statuses'
app = Doorkeeper::Application.find_by(name: 'openclaw-mastodon-bridge') ||
      Doorkeeper::Application.create!(name: 'openclaw-mastodon-bridge', scopes: SCOPES,
        redirect_uri: 'urn:ietf:wg:oauth:2.0:oob', confidential: false, owner: owner)
Doorkeeper::AccessToken.where(application_id: app.id).update_all(revoked_at: Time.now.utc)
tok = Doorkeeper::AccessToken.create!(application: app, resource_owner_id: owner.id,
  scopes: SCOPES, expires_in: nil, use_refresh_token: false)   # nil, NOT 0
File.write('/tmp/bot_token', tok.token)
```

Three traps: there is no `accounts.local` column;
`owner_id` and `resource_owner_id` reference the **`users`** table, not
`accounts`; and `expires_in: 0` produces an already-expired token.
### 14.1.6 Recorded deviation — env-file delivery instead of Podman secrets

**Orphaned plaintext copy: `%h/.local/share/ao-secrets/legacy-alwayson-folder.env`.** Found
2026-10-04, mode `0600`, holding four credential values by key name —
`mastodon-db-password`, `sales-db-password`, `webodm-postgres-password`,
`fabrication-db-password` — and referenced by **no** quadlet unit, script or section file. It is
a plaintext duplicate of wallet-held credentials, which §14.1.1's rules forbid outright.

Four measured facts, by sha256 prefix and no values printed, comparing each legacy key against
the live env file the owning unit reads:

| Legacy key | vs live env file | Result |
|---|---|---|
| `sales-db-password` | `sales-db.env` `POSTGRES_PASSWORD` | **SAME** (48 chars) — currently valid |
| `webodm-postgres-password` | `webodm.env` `POSTGRES_PASSWORD` | **SAME** (32 chars) — currently valid |
| `fabrication-db-password` | `fabrication-db.env` `POSTGRES_PASSWORD` | **SAME** (32 chars) — currently valid |
| `mastodon-db-password` | `mastodon-db.env` `POSTGRES_PASSWORD` | DIFFERENT (48 vs 40 chars) — stale |

**Three of the four are live database passwords, not historical artefacts.** An earlier draft of
this subsection reported only the `sales-db-password` match and characterised the file as "neither
wholly useless nor wholly current"; that was measured against two keys with the wrong live key
names and understated the exposure by a factor of three. The corrected count is the one above. The
practical consequence is unchanged but sharper: this file is a plaintext store of **three
currently-valid production database credentials** plus one stale one, and it is exactly the
duplication §14.2 exists to prevent.

`check-secrets-exposure.sh` does **not** catch it — that
script checks *tracked* files and file modes, and this file is untracked and correctly `0600`.
It was found by enumerating `ao-secrets/` and comparing against the units that read it, not by
running the guard. The guard's blind spot is itself the finding: **rule 7 compliance is only as
good as the tracked-file assumption**, and a `0600` copy of three live database passwords plus
one stale one sits outside both Git and the units.

Its origin is not recorded anywhere in the repository — no quadlet unit, script or section file
references `legacy-alwayson-folder`. Given the name and the fact that it holds exactly one
password for each of the four DB domains, it appears to be a pre-wallet-folder consolidation
artefact: a moment when the credential layout was one file instead of one folder per domain.

**Not deleted by this session.** Removing it is a deletion of secret-classified material, which
is outside this session's authority (brief stop conditions). **Operator decision requested** —
recommend deletion. The reasoning matters and cuts the other way from a first reading: because
three of the four values are **currently valid**, deleting the file removes a real plaintext
store of live credentials, and it loses nothing operationally, because the wallet remains the
system of record and the live env files are re-fetched at every start (the scope paragraph below).
Deleting is therefore strictly safer than keeping. Rotation is **not** required by the presence of the
file, because nothing outside it uses those values and they were never committed to Git, a
backup set, or an external network; rotation becomes required only if the operator judges the
host's local user account to be untrusted.

**Status: recorded, awaiting operator ratification.** This subsection exists because
§14.1 mandates Podman secrets or systemd credentials while every implemented path is a
wallet-materialised `0600` env file. The deviation is real, and it is documented here rather
than silently left in place. **It is not self-approving** — README §4.1 rule 14 reserves the
decision to the operator.

**Scope of the deviation.** Secret *storage* is the KDE Wallet, encrypted at rest. Secret
*delivery* is a `0600` env file under `%h/.local/share/ao-secrets/`, refreshed at start-up by
`fetch-kwallet-secret.sh`. Env files are **delivery copies, not stores**: the wallet is the
only system of record, and every file is rewritten from the wallet on each refresh, so losing
one costs a re-fetch, not a credential.

The **first draft of this paragraph named only four consumers** —
`ao-mastodon-db`, `ao-sales-db`, `ao-webodm-db` and `ao-fabrication-db`. That understated the
deviation by roughly a factor of three. Measured 2026-10-04, the delivery set is **eight
secret-bearing env files**, not four:

| Env file | Produced by | Consumer |
|---|---|---|
| `mastodon-db.env` | `fetch-kwallet-secret.sh … mastodon-db-password` | `ao-mastodon-db` |
| `sales-db.env` | `… sales-db-password` | `ao-sales-db` |
| `webodm.env` | `… webodm-postgres-password` | `ao-webodm-db` |
| `fabrication-db.env` | `… fabrication-db-password` | `ao-fabrication-db` |
| `payment.env` | `… payment-credentials` | `ao-ingress-payment` |
| `reporting-grafana-admin.env` | `… grafana-admin-password` | `ao-grafana` |
| `reporting-grafana-postgres.env` | `fetch-reporting-env.sh grafana` | `ao-grafana`, `ao-status-collect`, `ao-db-security-collect` |
| `reporting-metabase.env` | `fetch-reporting-env.sh metabase` | `ao-metabase` |

Plus `mastodon.env` (1041 bytes, mode `0640`, wallet entry `ao-mastodon/mastodon-env`,
byte-identical to the file per §14.1.3), consumed by `ao-mastodon-web`, `-streaming` and
`-sidekiq` and by the repair `ExecStartPost`. **The operator is therefore being asked to
ratify a deviation covering nine files across fifteen units, not four files across four
units.** The four-database framing was inherited from the SEC-01 acceptance criterion, which
names only mastodon-db, sales-db and webodm-db; the criterion is narrower than the
implementation, and the implementation is what needs approving.

**A mode exception inside that set, stated precisely.** `mastodon.env` is `0640`, not `0600`,
because `ao-wallet-bridge.sh` adds the ACL that lets `ao-sales` read it. Measured:

    $ getfacl -p ~/.local/share/ao-secrets/mastodon.env
    user::rw-  user:ao-sales:r--  group::---  mask::r--  other::---

The other eight env files are `0600 scottw:scottw` with no ACL. So "all delivery copies are
`0600`" is true of eight files and false of the ninth; §14.1.6 previously said so uniformly.

**Why the mandated mechanism is not used.** Podman secrets (`podman secret ls` returns an
empty list; Podman 5.7.0) would have to be populated *from* the wallet by a root or
podman-owned helper at start-up, which relocates the plaintext to a second long-lived store
rather than removing it, and `Secret=` cannot be populated from a login-gated wallet at all.
Systemd `LoadCredential=` is available to the systemd user manager but is not usable by
Podman-managed containers, which take `EnvironmentFile=`/`Secret=`, not systemd credentials.

**Compensating controls actually in place** (each verified, not asserted):

| Control | Evidence |
|---|---|
| Value lives only in the wallet | `fetch_secret` reads via D-Bus `readPassword` and prints nothing; the value is only ever written to the output file |
| Files are `0600`, created under `umask 077` | `umask 077` at `fetch-kwallet-secret.sh` line 14; `chmod 600 "$OUTPUT_FILE"` at end of script |
| Write is atomic, so a partial file is never read | `{ … } > "$OUTPUT_FILE.tmp"` then `mv` then `chmod 600`; `trap cleanup_tmp EXIT` removes a stranded `.tmp` |
| Consumer ACL is narrow, not world-readable | `mastodon.env` ACL is `user:ao-sales:r--`, `group::---`, `other::---`, set by `ao-wallet-bridge.sh` |
| No plaintext copy in the repository | `.gitignore:1` is `secrets/`; env files live under `%h/.local/share/ao-secrets/`, outside the worktree |
| Exposure is checked in CI | `check-secrets-exposure.sh` carries the three rule-7 checks described in §14.1.1 |

**Env-file lifetime and shred-on-exit — stated precisely, because §14.1.1 calls a file here a
plaintext duplicate.** The `0600` env files are **not** shredded on exit; they persist for the
lifetime of the unit and are overwritten in place at the next start. Only the transient `.tmp`
is removed, and only with `rm -f`, not `shred`. The scripts that *do* shred are
`scripts/mastodon/post.sh` (`trap 'shred -u "$ENV"' EXIT`) and `scripts/ledger/sign-manifest.sh`.
So the accurate statement is: **delivery copies persist on disk at `0600` between start-ups and
are replaced, not shredded.** This is the accepted residual exposure of the deviation and is
why the wallet — not these files — is designated the system of record.

**Two stale facts corrected while writing this subsection.**

1. §19 ST-30 records `~/secrets/fabrication-db.env` as a `0600` file. **No such file exists.**
   `find ~/secrets -name '*fabrication-db*'` returns nothing; the live file is
   `~/.local/share/ao-secrets/fabrication-db.env` (`-rw-------`, 100 bytes), matching the
   single-env-root rule in §14.1.2. ST-30's text is stale and should not be read as evidence
   of a second delivery path. Correction proposed to the §19 compiler; ST-30 is not this
   session's file to edit.
2. `~/secrets/mastodon.env` is a **dangling symlink** to
   `/ALWAYSON/secrets/mastodon/mastodon.env`, which does not exist
   (`ls: cannot access …: No such file or directory`). It is inert, because
   `quadlet/sales/ao-sales-db.container` and the Mastodon units read
   `EnvironmentFile=%h/.local/share/ao-secrets/…`, not `~/secrets/`. Reported, **not removed** —
   deleting files is outside this session's authority and it may be another session's artifact.

**Migration remains available if the operator prefers it.** The pinned Postgres image
(`postgres@sha256:d74eeac9a…`) calls `file_env 'POSTGRES_PASSWORD'` at line 235 of
`/usr/local/bin/docker-entrypoint.sh`, so `POSTGRES_PASSWORD_FILE` **is** honoured; a Podman
`Secret=` mounted at `/run/secrets/…` plus `Environment=POSTGRES_PASSWORD_FILE=/run/secrets/…`
would satisfy §14.1 for the database services. It has not been applied: it changes live unit
definitions and live credential delivery, and therefore stops for operator approval.

### 14.1.7 `payment.env` is a stale delivery copy, and §19 ST-12's "runs with no DSN" is wrong

Found 2026-10-04. **The payment adapter has been running since 2026-10-01 15:08 with an env
file whose wallet source does not exist.** This is a liveness and correctness fault, not a
documentation drift, and it is in this section because the fault is in secret *delivery*.

The measured chain, each step a command and its output:

**1. The wallet folder the fetcher needs does not exist.**

    $ python3 … folderList(h,'ao-secret-reader')
    ao-payment exists: False
    ao-archive exists: False

`wallet_folder_for` maps `payment-db-password`, `payment-paypal-webhook-id`,
`payment-paypal-webhook-secret` and `payment-coinbase-webhook-secret` to `ao-payment`
(`fetch-kwallet-secret.sh` line 90). §19 ST-12 already recorded that "the four `ao-payment`
wallet entries do not exist yet". Confirmed: the folder is absent, not merely empty.

**2. The env file therefore cannot be refreshed, and has not been.**

    $ stat -c '%n mtime=%y' ~/.local/share/ao-secrets/payment.env
    payment.env mtime=2026-09-30 23:18:29
    $ systemctl --user show ao-ingress-payment.service -p ActiveEnterTimestamp
    ActiveEnterTimestamp=Thu 2026-10-01 15:08:41 PDT 2026

**The file is older than the process reading it by roughly sixteen hours.** Every start since
2026-10-01 has consumed a file frozen at 2026-09-30.

**3. The fetch failure is silenced, so nothing reports it.**

    $ grep -rn 'ExecStartPre=-' quadlet/
    quadlet/payment/ao-ingress-payment.container:63:ExecStartPre=-…fetch-kwallet-secret.sh … payment-credentials

The leading `-` makes systemd ignore the exit status. `fetch_secret` exits 2
("no wallet folder mapped") and 3 ("wallet entry unavailable"), but `ExecStartPre=-` discards
both. Consequently:

    $ journalctl --user -u ao-ingress-payment.service --since 2026-10-01 \
        | grep -cE 'wallet entry unavailable|no wallet folder mapped'
    0

**Zero** occurrences. The failure is real, recurring on every start, and produces no journal
entry at all. This is the same class of fault as the 2026-10-01 grafana/metabase outage
recorded in §14.1.4 — a failed fetch — except that there the fetch was loud and the units
crashed visibly, and here it is silent and the unit runs on stale material. The `-` prefix
converts a loud failure into a silent one.

**4. The stale file is not inert, and §19 ST-12's claim is false.**

ST-12 states the adapter "runs with no DSN and no webhook secret and cannot accept a payment."
Measured, with the password reduced to a length and a sha256 prefix:

    $ sed -n 's|^PAYMENT_DSN=postgresql://[^:]*:\([^@]*\)@.*|\1|p' payment.env | wc -c
    49                                     # 48 chars + newline
    $ sed -n 's|^PAYMENT_DSN=postgresql://[^:]*:\([^@]*\)@.*|\1|p' payment.env \
        | tr -d '\n' | sha256sum | cut -c1-12
    03521083973b

That prefix is **identical to the live `sales-db-password`** recorded in §14.1.6
(`03521083973b`, 48 chars) — the same value the orphaned `legacy-alwayson-folder.env` carries.
So `payment.env` holds a **currently-valid sales database password**, embedded in a DSN as
`postgresql://sales_migration_role:<password>@127.0.0.1:15432/salesdb`.

**The DSN is present and usable. ST-12's "runs with no DSN" is incorrect**, and the
conclusion drawn from it — that the adapter "cannot accept a payment" — rests on a measurement
that does not hold. The three webhook secret lines are genuinely absent (the file has one key,
`PAYMENT_DSN`), so the adapter has a database connection but no webhook verification material.
The correct statement is narrower: **it holds a live sales-DB credential and no webhook
secrets**, which is a different and less safe situation than ST-12 describes, because the
DSN alone grants database access.

**5. `check-secrets-exposure.sh` cannot see it**, for the same reason it missed
`legacy-alwayson-folder.env`: the file is untracked and correctly `0600`, and the guard's
`$secret_key_re` does not match `PAYMENT_DSN` — a deliberate carve-out at
`check-secrets-exposure.sh` line 79, whose comment says `payment.env` "carries a DSN, not a key
name". The carve-out was written so a healthy DSN file would not be flagged as leftover temp
debris; the side effect is that the one file carrying a real password in DSN form is
structurally invisible to the guard.

**Operator decision requested. Not changed by this session**, because it touches payment
credentials and a live running service (brief stop conditions; README §4.1 rules 12 and 14).

1. **Create the four `ao-payment` wallet entries**, then restart `ao-ingress-payment`. This is
   ST-12's own outstanding action and it also fixes the staleness. Recommended first.
2. **Decide whether the `-` prefix on line 63 should stay.** It was presumably added so a
   missing-wallet fetch would not block the unit — but the result is a unit that runs
   indefinitely on an env file it can never refresh, with no log line. If it stays, the
   staleness needs a separate check; if it goes, a locked wallet takes the unit down with it.
   Either is defensible, but the current state documents neither.
3. **Note for §19**: ST-12's "runs with no DSN" needs correcting. ST-12 is not this session's
   file, so this is raised as a proposal, not an edit.

Cross-group: the *credential content* of this is PAY territory and the ST-12 row is the
compiler's. The *delivery-mechanism* fault — silent fetch failure on a `0600` stale copy — is
SEC's and is what §14.1.7 records.

## 14.2 Credential rotation, revocation and recovery

This subsection exists because §14.1.1 requires rotation, revocation, expiration and recovery
to be documented before production use, and none of it was documented in §14, §16 or §17.
`docs/runbooks/secrets.md` carries a three-line "Rotation" note, but it is stale: it describes
per-service-account homes (`alwayson-mapping`) and a manual copy-out step, both superseded by
§13.2 (all services run under the operator's account) and by the wallet-materialised flow.
**This subsection is the procedure; the runbook's summary is the non-authoritative copy.**

### 14.2.1 Rotation

Rotation is *write the new value to the wallet, then let the fetchers redistribute it*. The
fetchers run as `ExecStartPre`, so the file is rewritten from the wallet on the next start —
rotation is completed by restarting the consuming unit, not by copying a file.

| Step | Action | Verify |
|---|---|---|
| 1 | Operator writes the new value to the owning `ao-*` folder via `scripts/ops/kwallet-provision.sh put` | `hasEntry` true on `org.kde.kwalletd6` |
| 2 | For a **database** password, change the role **first**, so the wallet and the live role never disagree: `ALTER ROLE <role> PASSWORD …` | role login succeeds |
| 3 | Restart the consuming unit; `ExecStartPre` re-fetches and atomically rewrites the `0600` file | `systemctl --user is-active <unit>`; file mtime advanced |
| 4 | Confirm no other copy exists | `find ~/secrets ~/.local/share/ao-secrets -newer <marker>`; `check-secrets-exposure.sh` |

**Never** rotate by editing an env file directly. The file is overwritten at the next start, so
an edit is silently reverted and, worse, leaves the wallet and the running service
disagreeing. **Never** regenerate `mastodon.env` via `genenv` to rotate: it refuses to run when
the file exists and would otherwise mint new `SECRET_KEY_BASE` / `OTP_SECRET`, invalidate every
session, and write `LOCAL_DOMAIN=localhost` (§14.1.3).

Database password rotation ordering matters because `pg_hba` trusts `127.0.0.1` for these
roles: TCP auth can fail while the socket still appears to work. Confirm with a TCP client, not
a socket, after changing a role password.

### 14.2.2 Revocation

Revocation is credential-specific; there is no single "revoke everything" switch.

- **Wallet entry** — overwrite the entry with a fresh unusable value via
  `kwallet-provision.sh put`, then restart every unit that reads it. The wallet is the system
  of record, so this is the revocation.
- **Mastodon access token** (§14.1.5) — `Doorkeeper::AccessToken.where(application_id: …)
  .update_all(revoked_at: Time.now.utc)` revokes every prior token for the bridge application.
  Store any replacement in KDE Wallet, never a file.
- **Mastodon sessions** — changing `SECRET_KEY_BASE` invalidates every session. Treat it as a
  deliberate operator action, not routine rotation, and warn before doing it.
- **Exposed secret** — revocation is incomplete until the old value is also removed from every
  artefact that ever held it: env files, backups, Git history, logs. Backup snapshots taken
  while the old value was live still contain it (§14.2.4).

### 14.2.3 Expiration

No credential on this host has an enforced expiry. Passwords persist until rotated by the
operator. Tokens are the exception and are pinned deliberately: the OpenClaw bridge token is
created with `expires_in: nil`, because Doorkeeper reads `expires_in: 0` as *already expired*
(§14.1.4). **A non-expiring token raises the rotation obligation** — it is a standing item on
the break-glass list in §14.2.5, not a solved one.

### 14.2.4 Wallet backup and restore

**Gap, stated rather than papered over: the wallet is not in the backup set.** The restic
snapshot in `scripts/backup/restic-run.sh` line 30 covers `$AO_ROOT/config`, `artifacts`,
`backups/postgres`, and the `data/*` trees. `~/.local/share/kwalletd/` is **not** on that
list, and it cannot be: a `.kwl` file is encrypted against `kdewallet.salt`, so a snapshot
without the salt is unrestorable, and restoring a `.kwl` alone would not restore the
credential *values* the services consume.

Consequently the current recovery posture is: **the wallet is the single point of failure for
every credential on this host, and it has no automated backup.** Adding one is a backup-data
change and is flagged for the operator rather than applied.

**Restore procedure, for the operator to run interactively** (wallet must be unlocked; never
script it, and never let a value transit a shell argument or a log):

1. Restore the host or the user account. If `~/.local/share/kwalletd/kdewallet.kwl` is
   present and valid, the wallet opens with the Plasma login — verify with `wallets()` returning
   `as 1 "kdewallet"` and `open()` returning a handle ≥ 0.
2. If the wallet file is gone or will not open, the credentials must be re-provisioned from
   their other sources of record, or **rotated**. Rotation is always available and is the
   correct fallback: a database role password is set by `ALTER ROLE`, a token by re-minting
   (§14.1.5), an admin password by `kwallet-provision.sh put`. There is no path that recovers
   an old value, which is a security property, not an outage.
3. After any re-provisioning, run `check-secrets-exposure.sh` and restart the consumers.

**Procedure that is itself inside the backup set.** A credential-recovery runbook that lives
only in an unbacked file does not satisfy §14.2. The procedure above is written into
`agents/COORDINATION/14-secrets-and-service-identity/section.md`, which **is** covered by the
restic snapshot via `$AO_ROOT/config` and the repository, so the procedure survives a restore
even though the secrets do not. The deliberate split is: **the procedure is backed up; the
secrets are rotated, never restored.**

### 14.2.5 Break-glass order for the operator

In order, stopping at the first step that resolves the fault. Steps 1–4 are non-destructive;
step 5 changes a live credential and is the operator's alone. Step 2 was added 2026-10-04
after §14.1.7 found a delivery copy that had gone stale without any fault being reported.

1. **Is it the wallet being locked?** Check `isOpen(handle)` — not `busctl --user list |
   grep kwalletd6`, which returns true the instant kwalletd is D-Bus-activated and therefore
   never waits. A `0-byte` `.tmp` under `ao-secrets/` is the forensic signature of a locked
   wallet (§14.1.4). Fix: unlock the wallet from the Plasma session and restart the unit.
2. **Is a delivery copy older than the process reading it?** Compare the two mtimes before
   anything else, because it is the cheapest check and it catches the silent failure mode:

       $ stat -c '%y %n' %h/.local/share/ao-secrets/*.env
       $ systemctl --user show <unit> -p ActiveEnterTimestamp

   An env file older than the unit's start timestamp means the `ExecStartPre` did not rewrite
   it. §14.1.7 documents this happening silently for sixteen hours on `ao-ingress-payment`
   because its `ExecStartPre` carries the `-` ignore-failure prefix. **A fetch that fails on a
   `-`-prefixed `ExecStartPre` leaves no journal entry**, so mtime-versus-start-timestamp is
   the only reliable signal that a delivery copy has gone stale.
3. **Is the unit simply not started?** These units are `WantedBy=graphical-session.target` and
   are *expected* to be down before Plasma login. That is the login-gated design, not a fault.
4. **Is the entry present?** `hasEntry` on the owning folder via `kwallet-provision.sh get` /
   `fetch_secret`; a missing entry is re-provisioned by the operator with a **new** value.
5. **Rotate, do not restore.** If a value is suspected exposed, or unrecoverable, write a new
   value to the owning `ao-*` folder and restart (§14.2.1). This is the only path for a lost
   wallet, and it does not require the old value.

**Never**, in any break-glass step: print a value to a terminal, log, ticket or chat; restore
an env file from a backup; copy a value between hosts or folders outside its owning `ao-*`
domain; or add a compensating `Environment=` line to a unit to work around a missing fetch.
The last one is the failure mode that turns a five-minute locked wallet into a permanent
plaintext secret in a tracked file.
