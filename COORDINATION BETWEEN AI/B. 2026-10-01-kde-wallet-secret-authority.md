# COORDINATION — KDE Wallet secret-authority migration

**From:** Cline session, 2026-10-01
**Scope:** Making KDE Wallet the sole password authority (README §4.1 rule 7, §4.2, §14.1.1)
**State:** Migration applied and verified. **NOT committed.** Full wallet inventory included.
**Supersedes:** the earlier revision of this file (same path) dated 14:18.

> ### ⚠️ TWO FINDINGS FROM THE EARLIER AUDIT ARE RETRACTED
>
> An independent panel review found both were produced by the *same*
> closed-world mistake: I assumed the wallet's layout instead of enumerating it.
>
> 1. **"LM Studio token has NO wallet copy" — RETRACTED, WRONG.**
>    `Passwords/lmstudio-api-key` exists and is **byte-identical** (35 chars) to
>    the `~/.bashrc` copy. KDE's stock `Passwords` folder can never appear in a
>    hand-typed list of `ao-*` folders, which is all I searched. OpenClaw's
>    wallet-backed provider resolves it correctly.
> 2. **"Cloudflare credentials are outside the wallet (MEDIUM)" — RETRACTED.**
>    `scripts/operations/fetch-cloudflared-env.sh:13-15` reads
>    `ao-mastodon/cloudflare-tunnel-id` and `ao-mastodon/cloudflare-tunnel-credentials-json`
>    from KDE Wallet and materializes them `0400` at startup. `~/.cloudflared/`
>    is a runtime artifact, correctly permissioned.
>
> **Do not re-report either as an open finding.** The genuinely open item is much
> narrower — see "Open findings".

---

## Complete wallet inventory

Produced by enumerating the wallet, **not** by searching a hand-typed folder list.
18 unique folders / 2704 entries total; the 8 below are ALWAYS ON-relevant,
holding **39 entries**. Regenerate with `folderList` -> `entriesList` (D-Bus
methods documented and host-verified at README:3222, 3225, item 32 at 4664).

| Folder | Entries |
|---|---|
| `Passwords` (2) | `lmstudio-api-key`, `openclaw-gateway-password` |
| `ao-admin` (6) | `grafana-admin-password`, `grafana-db-password`, `metabase-db-password`, `metaread-password`, `restic-repository-password`, `sales-reporting-password` |
| `ao-fabrication` (1) | `fabrication-db-password` |
| `ao-mapping` (5) | `producer-private-key`, `webodm-api-password`, `webodm-api-user`, `webodm-postgres-password`, `webodm-secret-key` |
| `ao-mastodon` (21) | `cloudflare-origin-cert-pem`, `cloudflare-tunnel-credentials-json`, `cloudflare-tunnel-id`, `mastodon-admin-password`, `mastodon-ar-derivation-salt`, `mastodon-ar-deterministic-key`, `mastodon-ar-primary-key`, `mastodon-bot-password`, `mastodon-db-password`, `mastodon-env`, `mastodon-otp-secret`, `mastodon-owner-password`, `mastodon-secret-key-base`, `openclaw-bot-access-token`, `openclaw-bot-client-id`, `openclaw-bot-client-secret`, `openclaw-bot-password`, `roundtrip`, `roundtrip2`, `tokodon-client-id`, `tokodon-client-secret` |
| `ao-sales` (2) | `sales-api-db-password`, `sales-db-password` |
| `ao-sim-fabrication` (1) | `producer-private-key` |
| `ao-sim-vehicle` (1) | `producer-private-key` |

**Entries the earlier audit never knew existed** (my curated list touched only 13
of these 39): `producer-private-key` in three folders, `webodm-api-password`,
`webodm-secret-key`, `sales-api-db-password`, `cloudflare-origin-cert-pem`,
`tokodon-client-id`/`tokodon-client-secret`, `mastodon-owner-password`,
`mastodon-ar-*` key material, and `roundtrip` / `roundtrip2` — the last two are
**test artifacts that should be deleted.**

Note: `ao-payment`, `ao-field`, `ao-ledger` and `ao-archive` do **not** appear
above. README §14.1.1 calls them "provisioned empty 2026-08-31", but `folderList`
does not return them. Reconcile the README with reality.

---

## What was changed today (all UNCOMMITTED)

### 1. Grafana admin password moved into the wallet
`config/platform/monitoring/grafana.env` held a cleartext
`GF_SECURITY_ADMIN_PASSWORD` at mode **0664** with **no** wallet entry. The
Grafana *database* password had been migrated; the web *admin* password never was.
The file is now split:

| File | Holds | Tracked |
|---|---|---|
| `config/platform/monitoring/grafana-admin.env` | `GF_SECURITY_ADMIN_USER`, `GF_USERS_ALLOW_SIGN_UP`, `GF_AUTH_ANONYMOUS_ENABLED` | yes, intentionally |
| `~/.local/share/ao-secrets/reporting-grafana-admin.env` | `GF_SECURITY_ADMIN_PASSWORD` (0600, materialized by `ExecStartPre`) | no, never |

New entry: `ao-admin/grafana-admin-password`. `fetch-kwallet-secret.sh` gained the
`ao-admin` folder mapping and a `grafana-admin-password` output branch.
**Verified:** `/api/health` 200, database ok, admin login via wallet value 200.

### 2. Seven plaintext duplicates shredded
Each was compared against its wallet entry first.

| Removed | Authoritative wallet entry |
|---|---|
| `config/platform/monitoring/grafana.env` | `ao-admin/grafana-admin-password` |
| `secrets/reporting/grafana-postgres.env` | `ao-admin/grafana-db-password` |
| `secrets/reporting/metabase.env` | `ao-admin/metabase-db-password` |
| `secrets/reporting/metaread.env` | `ao-admin/metaread-password` |
| `secrets/reporting/sales-reporting.env` | `ao-admin/sales-reporting-password` |
| `secrets/mastodon/openclaw-mastodon.env` | `ao-mastodon/openclaw-bot-*` |
| `secrets/mastodon-db.env` | `ao-mastodon/mastodon-db-password` |

Two results worth keeping: `secrets/mastodon-db.env` **did not match** the wallet
(a genuinely stale leftover, not a mirror). The `openclaw-mastodon.env` access
token **differed from the wallet but tested HTTP 200 valid** against `300x3.com` —
a *second live credential*, not a stale copy. Its consumers were repointed at the
wallet before removal.

### 3. Six consumers repointed at the wallet
`provision-metaread.sh`, `provision-sales-reporting.sh` and
`provision-reporting-postgres.sh` previously *seeded* from a plaintext file and
mirrored outward; they are now wallet-first. `mastodon/post.sh` materializes
credentials into a `0600` mktemp file and shreds it on an EXIT trap.
`mastodon/provision-openclaw-bot.sh` writes no env file at all.

### 4. Two new guards
`check-secrets-exposure.sh` gained three rule-7 checks (tracked `.env` must not
carry a credential; a Quadlet `EnvironmentFile` under `config/`/`secrets/` must
not be secret-bearing; secret env files must not be other-readable). **Both file
checks were negative-tested** by planting deliberate violations and confirming
they fail — a validator that has only ever passed proves nothing.

`scripts/lib/common.sh` gained `ao_audit_secret()`, which masks a credential that
would otherwise be journalled.

---

## Open findings

### 1. `~/.bashrc` holds a duplicate of a wallet-held token — do NOT rotate
`~/.bashrc` line 129: `export LM_API_TOKEN="sk-lm-..."` (35 chars; segments
`[2,2,8,20]` split on `-`/`:` — **it contains a colon**).

- The wallet copy is **correct and valid** (`Passwords/lmstudio-api-key`,
  byte-identical), so this is a *redundant-copy* problem, not a lost secret.
- `~/.bashrc` is **0644** (world-readable); the token also appears **5 times** in
  `~/.bash_history`.
- Two **live Cline processes** (PID 7836 `node /usr/bin/cline -c /ALWAYSON`,
  PID 7844) already hold it in their environment.
- No consumer found in `/etc/systemd/system`, `~/.config/systemd/user`,
  `/ALWAYSON/quadlet` or `/ALWAYSON/scripts`.
- LM Studio's own config has `logSensitiveData: false`, `logIncomingTokens: false`.

**Proposed, awaiting operator approval:** remove line 129, `chmod 600 ~/.bashrc`,
filter the 5 history occurrences. **Rotation is explicitly NOT recommended** —
the wallet copy is already good and rotating a working key adds risk for no gain.
Nothing has been changed; `.bashrc` and history are untouched.

### 2. `~/pCloudDrive/PUBLIC FOLDER` is a git repo and was never scanned
It is the first named prohibited path in rule 7. The earlier audit only checked
`/ALWAYSON/pcloud` (empty) and wrongly reported pCloud as clean. **Verified:** the
repo exists, has **0 commits and no remote**, so no secret is committed — but the
history scan was never actually run there.

### 3. `roundtrip` / `roundtrip2` test artifacts in `ao-mastodon`
Leftovers from the D-Bus verification work. Safe to delete from the wallet.

---

## Verified clean (read the methodology caveat below)

- **`/ALWAYSON/logs/`** — 27 files, zero secret values.
- **ALWAYS ON git history — 2436 commits** (`git rev-list --all | wc -l`).
  Secret-*shaped* matches exist (`POSTGRES_PASSWORD=`, `MASTODON_BOT_PASSWORD=`)
  but all are shell variables (`$BOTPASS`), `$(openssl rand ...)` generation
  commands, or wallet reads (`PGPASSWORD="$(... kwallet ...)"`). **No literal value
  was ever committed.** HEAD is clean. *A panel member claimed this repo has 206
  commits — that is wrong; 2436 is the measured value.*
- **5 other repos** (HTML-300X3, both OpenClaw workspaces, webodm, ardupilot) — clean at HEAD.
- **systemd units** (system + user) — keyword hits only, zero inline `Environment=` secrets.
- **`~/.openclaw/openclaw.json`** — correctly wallet-backed via exec providers.
- **`~/.cloudflared/`** — `cert.pem` 0600, credentials `.json` 0400, `config.yml`
  0644 contains **no token**. Sourced from the wallet at startup. No action.
- **Podman** — no secrets, no `auth.json`. No `.netrc`, `.pgpass`, ssh keys,
  `~/.aws`, `~/.kube`, `~/.azure`, restic configs.

---

## Methodology rules — read before running any secret audit here

These come from the two errors this session made. Both produced false
"everything is clean" results, which are the dangerous kind.

1. **A negative result cannot self-validate.** "CLEAN" proves nothing unless you
   show the tool *would* have found a planted secret. Run a **positive control** in
   the same pass and report a coverage manifest
   (`folders discovered: N; folders searched: N; fixtures matched: k/N`).
2. **Never curate the search space.** Use `folderList` -> `entriesList`, not a
   typed list of expected folder names. Compare by **sha256**, not plaintext
   equality.
3. **`hasEntry: false` does not mean "does not exist"** — it also means "no such
   folder" or "bad handle". `kwallet-provision.sh:42` guards this itself with
   `|| echo '(false,)'`. That is what bit me twice.
4. **Regex character classes must match the real alphabet.** Mine used
   `sk-[A-Za-z0-9]{20,}`; the real token contains `-` and `:`, so it returned
   **zero matches** on a file that definitely contained it. Include `-` `_` `:`
   and verify against a planted fixture.
5. **Keyword matching is not value matching.** A detector matching
   `export ...TOKEN=` confirms a *name*, not a credential. Confirm the value's
   shape separately, or say only what you actually verified.
6. **Use committed scripts, not ad-hoc heredocs.** A throwaway probe printed
   `length: 0` for a key it had reported as `len 1338` — a key-path nesting bug,
   and a number with no unit looks authoritative anyway. Assert types, label
   output, journal the command per rule 11.

---

## Housekeeping for the next agent

1. **Nothing is committed.** 13 modified files plus new
   `config/platform/monitoring/grafana-admin.env`. The working tree also has
   **unrelated** pre-existing changes (GAZEBO files,
   `config/platform/loopback-services.yaml`, `config/platform/version-matrix.yaml`,
   `.playwright-mcp/`) — **stage by file; do not `git add -A`.**
2. `secrets/mastodon.env` is a **dangling symlink** (pre-existing, untouched).
3. `pkexec-post-deploy.sh:46-52` still *generates* the metaread password to a file.
   It never prints the value and mirrors to the wallet, but it is the last script
   creating a plaintext credential rather than reading one. Root-run bootstrap
   path — change carefully.
4. `ao-payment` is intentionally empty (ST-12). Do not "helpfully" populate it.
5. **This folder is shared with other AI sessions** (A = mastodon bot/federation,
   C = gazebo GUI render fault, this = B). Read the others before acting; do not
   renumber or overwrite another session's file.

### Conventions
- Never print, copy or log a secret value. Compare in-process by hash/equality;
  output only lengths and key names. Presence checks use `hasEntry`.
- Prefer `kwalletd6` over `kwalletd5` in new code (README:2974).
- Commit style: `type(scope): summary`.
- **Quadlets deploy FLAT** via `scripts/deploy/deploy-quadlet-domain.sh <domain>`.
  Editing `quadlet/<domain>/*.container` does **not** change the live unit — files
  under `~/.config/containers/systemd/` are **copies, not symlinks**. Verify with
  `systemctl --user show ao-grafana.service -p SourcePath`.
- New wallet-backed keys need a branch in **two** places in
  `fetch-kwallet-secret.sh`: `wallet_folder_for()` **and** the output `case`.
  A missing branch restart-loops the unit (README:2985).
