# COORDINATION — Mastodon local UI, OpenClaw bot, inbound federation

**From:** Cline session, 2026-10-01 (afternoon)
**Complements:** `2026-10-01-kde-wallet-secret-authority.md` — read it first. I
followed the wallet-authority conventions and did not touch your files.
**State:** "Committed" below is committed. The federation investigation is
**open and undiagnosed** — read "The live blocker" before starting.

---

## Read this first

1. **Do not "fix" the Mastodon proxy by deleting it.** It exists because
   upstream hardcodes `config.force_ssl = true` (README §14.1.4).
2. **The `@bot` API token is in KDE Wallet at `ao-mastodon` /
   `openclaw-bot-access-token` and works.** All four `openclaw-bot-*` entries
   are present, so your `fetch-openclaw-mastodon-env.sh` will succeed.
3. **Inbound ActivityPub does not work here.** That is the live blocker, and it
   is *not* the same problem as anything I fixed today.

---

## Committed today

```
a83bc62 fix(mastodon): give the OpenClaw bridge a working API token
f47590f docs(secrets): record verified kwalletd6 D-Bus access (19.5 item 32)
3d940ff docs(readme): add 5.1.2 listing every ao- network in one place
b0864ca docs(matrix): refresh stale host facts and the evidence date
4f1a37d fix(podman): align the operator surface with README 13.1 rootless model
88370f2 fix(images): digest-pin the last tag-only operational images
7928f03 docs(mastodon): record that the local UI certificate is pre-trusted
dd8fbfc chore(bookmarks): correct the server bookmark list and harden the updater
3b7b5f6 fix(deploy): target the flat Quadlet unit directory systemd actually reads
b243816 refactor(secrets): keep one mastodon env file, mirrored to KDE Wallet
```

**I did not sweep your uncommitted work into any of these.** Verified:
`grafana-admin-password` appears 5x in the working-tree `README.md` and 0x in
`HEAD`. Your 13 files are still pending — stage by file.

---

## Two things I got wrong (recorded so they are not repeated)

---

## Defects I fixed in the Mastodon data

Both are the same class: the instance was populated directly in PostgreSQL
without Mastodon's normal setup.

**1. Bot token.** `bot` had **zero** active tokens and no Doorkeeper app for the
bridge (only `ao-outbound-proof`). Created app `openclaw-mastodon-bridge`
(id 3, owner `bot`/user 2), scopes `read:accounts read:notifications
write:statuses read:statuses`, `expires_in: nil`. Stored in the wallet. Bridge
went from **5,119 crash-loops on 401 to 0 restarts**.

**2. Empty account URIs.** `aoadmin` and `bot` had `uri=""`, `inbox_url=""`,
`shared_inbox_url=""`. Repaired to `https://mastodon.300x3.com/users/<name>`
etc. Mastodon matches inbound mentions **by URI**, so this alone would have
broken every mention.

There is also **no local `Instance` row** — all 4 rows are remote probes
(`fedibook.de` and friends). May be benign in 4.3, but same pattern.

---

## The live blocker: inbound ActivityPub

**This is §19.3 item 14, not item 16**, and it blocks item 16 entirely.

### Established

```
TOTAL statuses:        1
from LOCAL accounts:   1
from REMOTE accounts:  0      <-- inbound has NEVER produced a status
```

Three mentions were posted from `300x3@mastodon.social`. The last is
well-formed and *is* delivered:

```
post   https://mastodon.social/@300x3/117367758586832791
       21:24:31Z  mentions: ['bot@mastodon.300x3.com']     OK
inbox  21:24:33Z  POST /inbox -> 202                        OK
bot    notifications: 0        statuses: 1 (its own 01:45)
```

### The decisive result


### Ruled out

| Hypothesis | Verdict |
|---|---|
| Missing AP signing keys | Ruled out — actor serves a valid `publicKey` (4.3 keeps keys in the DB, not `config/keys/`) |
| Malformed mention | Ruled out — `mentions` array correct |
| Delivery not happening | Ruled out — inbox POST lands 2s after each post |
| Cloudflare mangling the body | **Largely ruled out** — verification succeeds, so signed bytes arrive intact |
| Bot token / account URI | Fixed, and unrelated — inbound fails for *any* sender |

### Next steps, in order

**A — capture what the tunnel actually delivers.** Highest value.
`cloudflared -> 127.0.0.1:3000` is plain HTTP on loopback, so a capture sees it
in the clear with no service change:

```bash
pkexec tcpdump -i lo -A -s0 -w /tmp/inbox.pcap 'tcp port 3000'
# have someone post a mention, then:
pkexec tcpdump -r /tmp/inbox.pcap -A | less
```

Check `Content-Type`, `Host`, `Date`, `Digest`, and above all `Signature`
(`keyId`, `algorithm`, `headers`, `signature`). If `keyId` is not
`.../users/300x3#main-key`, verification passed against the wrong actor. Also
confirm `Digest` matches the body — a body altered in transit fails *body*
verification even with a correct `keyId`.

**B — signed replay straight to the origin.** Generate a throwaway RSA key,
host a minimal actor document, sign a `Create(Note)` per draft-cavage
(`(request-target) host date digest`), POST to `127.0.0.1:3000/inbox` with
`X-Forwarded-Proto: https`. If a job is enqueued and a status created, the
origin path is fine and the fault is upstream. If it 401s, the signature
construction is wrong — diff it against the real request from step A.

I stopped rather than guess: wrong `keyId`, `Digest` mismatch, and an ignored
activity type need different fixes.

---

## Incidental: automated agents

```
friendica@sekretaerbaer.de
friendica@fedibook.de
friendica@friendicadev.sekretaerbaer.de
```

Autonomous Friendica agents crawling public instances — unrelated to the
mentions. The instance is publicly federated so this recurs. Untouched;
deleting just makes them re-register.

---

## Housekeeping

- **I created a dangling symlink.** `secrets/mastodon.env` ->
  `/ALWAYSON/secrets/mastodon/mastodon.env`, whose target I deleted today when
  consolidating to one env file. Untracked, referenced only by a stale doc line
  and three already-disabled units. Your handoff called it "pre-existing" — it
  was mine. Offer to remove it.
- Your open item on `pkexec-post-deploy.sh:46-52` generating the metaread
  password inline is still true; I did not touch it.
- `ao-payment` wallet entries still absent. Left alone, as instructed.

---

## Traps I hit that will bite again

- **Quadlets deploy flat.** Editing `quadlet/<domain>/*.container` changes
  nothing live; `~/.config/containers/systemd/` holds copies, not symlinks.
  `deploy-quadlet-domain.sh` had been writing to a `<domain>/` subdirectory
  **Quadlet does not read** — reporting success while changing nothing. (You
  flagged this too; we converged.)
- **Mastodon 4.3 has no `accounts.local` column.**
- **Doorkeeper `owner_id`/`resource_owner_id` reference `users`, not
  `accounts`.**
- **`rails runner` with inline quoting breaks** — pipe a `.rb` file in via
  `podman exec -i ... sh -c 'cat > /tmp/x.rb'`.
- **`check-network-isolation.sh` had no shebang** and died on bash arrays when
  run directly. Fixed per README §16.2.

```
POST http://127.0.0.1:3000/inbox  (no X-Forwarded-Proto)        -> 308  force_ssl redirect
POST http://127.0.0.1:3000/inbox  (X-Forwarded-Proto: https)    -> 401  {"error":"Request not signed"}
```

1. **The origin is healthy** — it verifies HTTP signatures and correctly
   rejects unsigned requests with 401.
2. **The tunnel's `202`s are therefore *not* unsigned.** Mastodon returns 202
   only when `signed_request_account` resolved, i.e. verification
   **succeeded**. Unsigned gives 401, bad content-type 415, bad JSON 400.

So mastodon.social's deliveries *are* signed and verified, yet **no
`ActivityPub::ProcessingWorker` has ever been enqueued** (Sidekiq shows only
schedulers). Accepted, then dropped before processing.


Both corrected in README §14.1.4:

1. **"The bridge's minimal `Environment=` blocked KDE Wallet."** False — the
   systemd user manager *does* carry `DBUS_SESSION_BUS_ADDRESS`, `DISPLAY`,
   `WAYLAND_DISPLAY`.
2. **"A Mastodon token is 64 hex chars."** False — it is **43 base64 chars**.
   The wallet value had the right shape; it was simply dead.

Also: `expires_in: 0` in Doorkeeper means *expires in zero seconds*, i.e. an
already-expired token (`{"error":"The access token expired"}`). Use
`expires_in: nil`. Recipe in README §14.1.5.

---

## kwalletd6 details (19.5 item 32 — closed)

Bus `org.kde.kwalletd6`, object `/modules/kwalletd6`, interface
`org.kde.KWallet`, wallet `kdewallet`. Full signatures in README §14.1.4.

`busctl` traps: `int64` needs an explicit `x` prefix (else
`Unknown signature type k`); overloaded methods bite — `isOpen` is both
`isOpen(i)` and `isOpen(s)` and busctl picks wrongly. There is **no
`listFolders`**, it is `folderList`. No `introspect` on that interface.
Prefer python-dbus, which worked without incident.
