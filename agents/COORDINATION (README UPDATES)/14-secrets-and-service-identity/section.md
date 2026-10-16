# 14. Secrets and Service Identity

## 14.1 Secret Delivery

**Policy.** Secret storage SHALL be the KDE Wallet, encrypted at rest. Secret delivery
SHALL be a wallet-materialised `0600` env file under `%h/.local/share/ao-secrets/`,
consumed by the unit via Podman `EnvironmentFile=` and refreshed at start-up by
`fetch-kwallet-secret.sh` (Open work items `SEC-01`/`SEC-02` in §19.1 track operator
ratification of the nine-file/fifteen-unit delivery set). Prefer file-based secret delivery
rather than environment variables.

**Specified design (SEC-01/SEC-02).** The login-gated KDE Wallet
design is the specified secret-delivery mechanism for this host, implementing the §4.1 rule 7
requirement (`Only use KDE Wallet for passwords, tokens, keys, and other secret material`).
Services that consume wallet secrets start
after Plasma login (`WantedBy=graphical-session.target`) and are not expected to start
unattended before a password is entered. The ~60 s wait in `fetch-kwallet-secret.sh` is the
bounded startup allowance for that login, not a fallback for a passwordless boot. Auto-login is
an operator convenience, not a requirement of this design.

**Required controls for the specified design.**

| Control | Implementation | Verification |
|---|---|---|
| Login-gated startup | All wallet-backed units: `PartOf=graphical-session.target`, `WantedBy=graphical-session.target` | `systemctl --user show <unit> -p WantedBy,PartOf` |
| Secret delivery via 0600 env file | `fetch-kwallet-secret.sh` writes `%h/.local/share/ao-secrets/*.env` with `umask 077`, `chmod 600` | `stat -c '%a %n' ~/.local/share/ao-secrets/*.env` |
| Env-file lifetime bound to unit | File rewritten on every `ExecStartPre`; unit restart required to pick up rotation | `podman inspect <container> --format '{{.State.StartedAt}}'` vs file mtime |
| Shred-on-exit | Temp file `*.tmp` created under `umask 077`, cleaned by `trap cleanup_tmp EXIT` | `grep -n 'cleanup_tmp' scripts/operations/fetch-kwallet-secret.sh` |
| No secret in journal | `ExecStartPre` without `-` prefix logs fetch failure; `-` prefix only on `ao-ingress-payment` (documented exception) | `journalctl --user -u <unit> -g 'wallet entry unavailable\|no wallet folder mapped'` |
| No cross-domain folder | One `ao-*` folder per credential domain; service reads only its owning folder | `kwallet-provision.sh list kdewallet` |
| Wallet backup gap acknowledged | KDE Wallet (`~/.local/share/kwalletd/`) is **not** in the restic path set; §14.2.4 records this as a known single point of failure requiring operator decision | `grep -n 'kwalletd' scripts/backup/restic-run.sh` (returns nothing) |

**Operator approval required before production declaration.** This specified design and its required
controls must be explicitly approved by the operator before any production declaration. The
design touches secrets, credentials, and a live running service (README §4.1 rules 12 and 14).

### 14.1.1 KDE Wallet Secret Management

KDE Wallet is the operator-side secret and credential store for this host. This subsection
documents the integration. The specified login-gated delivery design is stated in **§14.1** (policy
box above), the rotation and recovery procedure in **§14.2**.

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
  `ao-mastodon-db`, `ao-sales-db`, `ao-webodm-db`, `ao-fabrication-db`, and `ao-ingress-payment`.
  **A new key must be added as a `case` branch in that script or the unit fails.**
- Env files materialise under `%h/.local/share/ao-secrets/`, via `ao-wallet-bridge.sh` or the
  unit's own `ExecStartPre`. `~/secrets/` holds unrelated material and is not part of the
  delivery path. **No fabrication credential file may exist under `~/secrets/` (ST-30); all
  fabrication credentials live exclusively in the `ao-fabrication` KDE Wallet folder.**

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

The last two rows are mapped in `wallet_folder_for`. Confirm folder presence through the
D-Bus `hasFolder(handle, folder, app)` probe with a nonsense-name negative control —
a probe that returns `True` for invented folders is broken, and the control is what makes
positive results believable:

    ao-admin True  ao-fabrication True  ao-mapping True  ao-mastodon True
    ao-sales True  ao-sim-fabrication True  ao-sim-vehicle True
    ao-payment True  ao-archive True
    zzz-does-not-exist-9999  False            <- control: the probe is not lying
    ao-totally-made-up       False
    ''                       True             <- empty folder name returns True

The `ao-payment` and `ao-archive` entries must return `hasEntry = True` for their rows
above (`payment-db-password`, `payment-paypal-webhook-id`, `payment-paypal-webhook-secret`,
`payment-coinbase-webhook-secret`, `pcloud-webdav-password`, `pcloud-webdav-user`).

**A negative control is mandatory on every probe run.** A probe that returns `True` for
invented folders while genuine folders flip between passes is indistinguishable from a
broken probe; the nonsense-name control is what earns a positive result. **A finding that
contradicts a prior measurement must be earned with a negative control, not asserted.**

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
| KDE Wallet `kdewallet` / `ao-mastodon` / `mastodon-env` | Wallet entry whose value materialises `mastodon.env` (§14.1.3). Byte-identity is not assumed — compare before relying on it. |
| KDE Wallet `ao-mastodon` / `mastodon-secret-key-base`, `mastodon-otp-secret`, `mastodon-db-password` | Per-key wallet entries |

No second copy of this file is kept anywhere, and nothing may be restored into the
repository. A stale copy is worse than no copy: its `DB_PASS` / `POSTGRES_PASSWORD` would not
match the running instance and its `LOCAL_DOMAIN` would be wrong, so restoring it would
break PostgreSQL auth for `mastodon-db`.

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
`org.freedesktop.DBus.Introspectable` — both are easy to reach for by habit, so check
the interface name before writing a call.

**`folderList` returns DUPLICATE rows — de-duplicate before counting.** A raw count
returns each folder several times and reads as catastrophic duplication (hundreds of
rows for a dozen real folders). `set()` gives the true folder count; the same applies
to `entriesList`, whose `ao-*` + `Passwords` total must be taken from the set.

**Readiness: use `isOpen`, not daemon presence.** Gating on
`busctl --user list | grep kwalletd6` is wrong — kwalletd6 is D-Bus-activated the
moment anything touches it and appears long before the wallet is unlocked, so the
gate returns true instantly and any timeout behind it never waits. Without this
gate `ao-grafana` and `ao-metabase` read a locked wallet, fail their `ExecStartPre`,
exhaust systemd's 5 fast restarts in ~5s and stay down. Both fetchers must use
`isOpen(handle)` with a 30×2s budget.

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
### 14.1.6 Specified delivery — env-file delivery via Podman `EnvironmentFile`

**Forbidden plaintext copy: `%h/.local/share/ao-secrets/legacy-alwayson-folder.env`.** This
path must not exist: it is mode `0600`, holds one credential for each of the four DB domains
(`mastodon-db-password`, `sales-db-password`, `webodm-postgres-password`,
`fabrication-db-password`), and is referenced by **no** quadlet unit, script or section file.
It is a plaintext duplicate of wallet-held credentials, which §14.1.1's rules forbid outright.

Comparing each legacy key against the live env file the owning unit reads (sha256 prefix,
never a value) is how any residual copy is assessed:

| Legacy key | vs live env file | Result |
|---|---|---|
| `sales-db-password` | `sales-db.env` `POSTGRES_PASSWORD` | **SAME** (48 chars) — a live credential |
| `webodm-postgres-password` | `webodm.env` `POSTGRES_PASSWORD` | **SAME** (32 chars) — a live credential |
| `fabrication-db-password` | `fabrication-db.env` `POSTGRES_PASSWORD` | **SAME** (32 chars) — a live credential |
| `mastodon-db-password` | `mastodon-db.env` `POSTGRES_PASSWORD` | DIFFERENT (48 vs 40 chars) — superseded |

**Treat the file's entire contents as live production database credentials.** It is exactly the
duplication §14.2 exists to prevent.

`check-secrets-exposure.sh` does **not** catch it — that script checks *tracked* files and file
modes, and this file is untracked and correctly `0600`. **Rule 7 compliance therefore rests on
more than the tracked-file assumption**: enumerate `ao-secrets/` and compare each file against
the units that read it, because a `0600` copy of live database passwords sits outside both Git
and the units.

No quadlet unit, script or section file references `legacy-alwayson-folder`, so its origin is
unrecoverable from the repository; treat it as a pre-wallet-folder consolidation artefact — one
credential file per DB domain rather than one wallet folder per domain.

**Removing it is an operator action, not a specification step.** Deleting the file removes a
plaintext store of live credentials and loses nothing operationally: the wallet remains the
system of record and the live env files are re-fetched at every start (scope paragraph below),
so deletion is strictly safer than keeping it. Rotation is not required by the file's presence
alone, because nothing outside it uses those values and they were never committed to Git, a
backup set, or an external network; rotation becomes required only if the operator judges the
host's local user account to be untrusted. The deletion decision is recorded in
`README-ACTION_ITEMS/status-and-references.md`.

**This specified design requires operator ratification.** This subsection states the
specified delivery mechanism: every implemented path is a
wallet-materialised `0600` env file consumed via Podman `EnvironmentFile=`.
**It is not self-approving** — README §4.1 rule 14 reserves the decision to the operator.

**Scope of the specified design.** Secret *storage* is the KDE Wallet, encrypted at rest. Secret
*delivery* is a `0600` env file under `%h/.local/share/ao-secrets/`, refreshed at start-up by
`fetch-kwallet-secret.sh`. Env files are **delivery copies, not stores**: the wallet is the
only system of record, and every file is rewritten from the wallet on each refresh, so losing
one costs a re-fetch, not a credential.

The delivery set is **eight secret-bearing env files**, not four:

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
`-sidekiq` and by the repair `ExecStartPost`. **The operator SHALL therefore ratify
nine files across fifteen units, not four files across four
units (Open work items `SEC-01`/`SEC-02` in §19.1).** The four-database framing was inherited from the SEC-01 acceptance criterion, which
names only mastodon-db, sales-db and webodm-db; the criterion is narrower than the
implementation, and the implementation is what needs approving.

**A mode exception inside that set, stated precisely.** `mastodon.env` is `0640`, not `0600`,
because `ao-wallet-bridge.sh` adds the ACL that lets `ao-sales` read it. Measured:

    $ getfacl -p ~/.local/share/ao-secrets/mastodon.env
    user::rw-  user:ao-sales:r--  group::---  mask::r--  other::---

The other eight env files are `0600 scottw:scottw` with no ACL. So "all delivery copies are
`0600`" is true of eight files and false of the ninth: `mastodon.env` is `0640` with an
ACL granting `ao-sales` read (§14.1.4).

**Why Podman secrets / systemd credentials are not the delivery path.** Podman secrets (`podman secret ls` returns an
empty list; Podman 5.7.0) would have to be populated *from* the wallet by a root or
podman-owned helper at start-up, which relocates the plaintext to a second long-lived store
rather than removing it, and `Secret=` cannot be populated from a login-gated wallet at all.
Systemd `LoadCredential=` is available to the systemd user manager but is not usable by
Podman-managed containers, which take `EnvironmentFile=`/`Secret=`, not systemd credentials.

**Required controls** (each verified, not asserted):

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
are replaced, not shredded.** This is the specified residual handling of this design and is
why the wallet — not these files — is designated the system of record.

**Two file-layout facts this subsection depends on:**

1. **Exactly one env root (§14.1.2).** The live file is
   `~/.local/share/ao-secrets/fabrication-db.env` (`0600`); no fabrication credential file
   may exist under `~/secrets/`. Where §19 ST-30 states otherwise, that text is owned by
   the §19 compiler, not by this specification.
2. `~/secrets/mastodon.env` must be treated as **inert** if present: it is a dangling symlink
   to `/ALWAYSON/secrets/mastodon/mastodon.env`, and `quadlet/sales/ao-sales-db.container`
   and the Mastodon units read `EnvironmentFile=%h/.local/share/ao-secrets/…`, not
   `~/secrets/`. Deleting files is outside this specification's authority.

**Migration to Podman `Secret=` is available and requires operator approval.** The pinned
Postgres image (`postgres@sha256:d74eeac9a…`) calls `file_env 'POSTGRES_PASSWORD'` at line 235
of `/usr/local/bin/docker-entrypoint.sh`, so `POSTGRES_PASSWORD_FILE` **is** honoured; a Podman
`Secret=` mounted at `/run/secrets/…` plus `Environment=POSTGRES_PASSWORD_FILE=/run/secrets/…`
would satisfy §14.1 for the database services. Applying it changes live unit definitions and
live credential delivery, and therefore stops for operator approval.

## 14.2 Credential rotation, revocation and recovery

§14.1.1 requires rotation, revocation, expiration and recovery to be documented before
production use; this subsection is that documentation.
`docs/runbooks/secrets.md` carries a three-line "Rotation" note that describes
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

**Verify the wallet and the file agree *after* the restart, not just that the file changed.**
Step 3's "file mtime advanced" is a weak check. §14.1.3.2 supplies a real, live example of a
check that passes while the service is wrong — and, importantly, this is *not* the wallet-vs-file
divergence the first pass of §14.1.3 alleged (that claim is retracted above): `mastodon.env` was
materialised correctly, and the fault is that `mastodon-streaming` captured the **previous**
file content because it was created 1.2s before the bridge's write completed. The mtime was
legitimate and recent; the consumer still held stale values. The pass condition is therefore
two-part, and the second half is the one that catches this:

    # (a) key names — the file is the shape the consumer expects
    $ sed 's/=.*/=/' ~/.local/share/ao-secrets/<file>.env | sort > /tmp/fk
    # … read the wallet entry the same way, strip values, sort …
    $ diff /tmp/fk /tmp/wk && echo 'key names identical'
    # then compare full-content sha256 — equality is the pass condition

    # (b) THE CHECK THAT MATTERS MOST: what the RUNNING process actually holds.
    $ podman inspect <container> --format '{{range .Config.Env}}{{println .}}{{end}}' \
        | sed 's/=.*/=/' | sort
    # Compare against the file's key list. Config.Env is a creation-time snapshot,
    # so a correct file beside a never-restarted container is still a stale service.

A rotation is complete when the wallet and every delivered copy hash equal **and** the consuming
unit has restarted **and** that container's `Config.Env` reflects the new file. "The file
changed" is not sufficient, neither is "the unit is active", and neither is "the file on disk
is correct" (see §19.1 ST-12).

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
`agents/COORDINATION (README UPDATES)/14-secrets-and-service-identity/section.md`, which **is** covered by the
restic snapshot via `$AO_ROOT/config` and the repository, so the procedure survives a restore
even though the secrets do not. The deliberate split is: **the procedure is backed up; the
secrets are rotated, never restored.**

### 14.2.5 Break-glass order for the operator

In order, stopping at the first step that resolves the fault. Steps 1–4 are non-destructive;
step 5 changes a live credential and is the operator's alone. Step 2 catches a delivery copy
that has gone stale without any fault being reported (see §19.1 ST-12).

1. **Is it the wallet being locked?** Check `isOpen(handle)` — not `busctl --user list |
   grep kwalletd6`, which returns true the instant kwalletd is D-Bus-activated and therefore
   never waits. A `0-byte` `.tmp` under `ao-secrets/` is the forensic signature of a locked
   wallet (§14.1.4). Fix: unlock the wallet from the Plasma session and restart the unit.
2. **Is a delivery copy older than the process reading it?** Compare the two mtimes before
   anything else, because it is the cheapest check and it catches the silent failure mode:

       $ stat -c '%y %n' %h/.local/share/ao-secrets/*.env
       $ systemctl --user show <unit> -p ActiveEnterTimestamp

   An env file older than the unit's start timestamp means the `ExecStartPre` did not rewrite
   it. This has happened silently for sixteen hours on `ao-ingress-payment`
   because its `ExecStartPre` carries the `-` ignore-failure prefix. **A fetch that fails on a
   `-`-prefixed `ExecStartPre` leaves no journal entry**, so mtime-versus-start-timestamp is
   the only reliable signal that a delivery copy has gone stale.

   **The converse needs its own check.** A file *newer* than the
   process is not proof of health — it is the signature of a completed refresh that no running
   service has picked up. The mtime ordering in the table above treats "file older than
   process" as the fault; it misses the newer case entirely, and that is exactly the state
   `ao-ingress-payment` is in: a correct four-key file behind a container
   that still holds one key. **For any
   `--env-file` consumer, compare the file against the process's actual environment**, not the
   file against its own mtime:

       $ podman inspect <container> --format '{{range .Config.Env}}{{println .}}{{end}}' \
           | sed 's/=.*/=/' | sort          # key names only
       $ podman inspect <container> --format '{{.State.StartedAt}}'

   `Config.Env` is a creation-time snapshot. A key present in the file but absent from
   `Config.Env` means the consumer predates the refresh and needs a restart — and a restart is
   the operator's call, not a step to take while diagnosing.
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
