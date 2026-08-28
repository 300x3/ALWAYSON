# ALWAYS ON — Mastodon (local instance) Runbook

Scope: operator chose to **self-host Mastodon locally** (rather than only
posting to an external host) and to operate it from the desktop with
**Tokodon** (KDE Mastodon client, already installed at `/usr/bin/tokodon`).
This stays inside the project's isolation model: the stack is containerized on
the internal `ao-sales` network; Web/Streaming publish **only to 127.0.0.1**
(`PublishPort=127.0.0.1:3000` / `:4000`). **No public listener is opened**
(`listener-allowlist` stays empty).

## Design
- db:      `quadlet/sales/ao-mastodon-db.container`      (postgres, container-scoped, does NOT touch host PG18)
- redis:   `quadlet/sales/ao-mastodon-redis.container`    (container-scoped)
- web:     `quadlet/sales/ao-mastodon-web.container`      (rails, 127.0.0.1:3000)
- sidekiq: `quadlet/sales/ao-mastodon-sidekiq.container`  (workers)
- stream:  `quadlet/sales/ao-mastodon-streaming.container`(127.0.0.1:4000)
- env:     `/ALWAYSON/secrets/mastodon/mastodon.env` (gitignored)
- policy:  `config/mastodon/instance-policy.yaml`
- wallet:  KDE Wallet folder `ao-mastodon`

## 1. Generate secrets (done once)
```bash
/ALWAYSON/scripts/mastodon/deploy-mastodon.sh genenv
# mirrors MASTODON_SECRET_KEY_BASE / OTP_SECRET / DB password into
# KDE Wallet folder ao-mastodon, and writes the (gitignored) env file.
```

## 2. Pull image (operator root TTY)
The official image `docker.io/mastodon/mastodon:v4.3.7` may deny anonymous
pulls. Try in order:
```bash
sudo -u alwayson-sales env HOME=/home/alwayson-sales \
  XDG_RUNTIME_DIR=/run/user/$(id -u alwayson-sales) \
  bash -c 'podman pull docker.io/mastodon/mastodon:v4.3.7'
```
If denied, use a mirror (verify its source/digest before production):
- `docker.io/linuxserver/mastodon:latest` (community opinion, weighs image)
- `quay.io/...` / any you trust

## 3. Enable the stack
```bash
sudo -u alwayson-sales env HOME=/home/alwayson-sales \
  XDG_RUNTIME_DIR=/run/user/$(id -u alwayson-sales) \
  systemctl --user daemon-reload
sudo -u alwayson-sales env HOME=/home/alwayson-sales \
  XDG_RUNTIME_DIR=/run/user/$(id -u alwayson-sales) \
  systemctl --user enable --now \
    ao-mastodon-db ao-mastodon-redis ao-mastodon-web \
    ao-mastodon-sidekiq ao-mastodon-streaming
```
Check: `podman exec mastodon-db pg_isready`, then rails migrations:
```bash
podman exec mastodon-web bin/rails db:prepare
```

## 4. Create owner (first user; password auto-saved to KWallet)
```bash
/ALWAYSON/scripts/mastodon/deploy-mastodon.sh create admin you@300x3.com
# then, once web is up, in the sales store:
podman exec mastodon-web bin/tootctl accounts create admin \
  --email you@300x3.com --confirmed --role Owner
# (deploy script stores the generated owner password in ao-mastodon)
```
Create support/bot accounts similarly (role Admin), and set avatars/bio via
the Mastodon Web UI at `http://127.0.0.1:3000` (or Tokodon).

## 5. Tokodon (operator client)
1. Launch Tokodon (KDE menu → Tokodon); "Add account".
2. Enter server URL: `http://localhost:3000`  (the loopback publisher; the
   instance is branded **300X3** — LOCAL_DOMAIN=300x3, so the operator account
   handle will read like `@admin@300x3`).
3. Complete the OAuth authorization (registering an application in Mastodon).
   Tokodon stores its own credential via the KDE secret store; keep a copy of
   the client id/secret in KWallet ao-mastodon/tokodon-client-* if you
   prefer to reuse that application registration (see below).
4. Posts/boosts/replies from Tokodon are the "operator client" feed.
   OpenClaw will talk to the same local HTTP API with a dedicated bot account.

### Optional: pre-registered Tokodon application
Mastodon OAuth client credentials for Tokodon can be created ahead of time:
```bash
curl -s -X POST http://localhost:3000/api/v1/apps \
  -d 'client_name=Tokodon' -d 'redirect_uris=urn:ietf:wg:oauth:2.0:oob' \
  -d 'scopes=read write follow'
```
Store `client_id`/`client_secret` in KWallet `ao-mastodon`:
```bash
/ALWAYSON/scripts/ops/kwallet-provision.sh put kdewallet ao-mastodon tokodon-client-id <id>
/ALWAYSON/scripts/ops/kwallet-provision.sh put kdewallet ao-mastodon tokodon-client-secret <secret>
```

## 6. Ledger/adapter notes (Section 3.8 carried over)
- Outbound egress only to approved host. For this instance it is local; keep
  `approved_pub_host: null`.
- Any OpenClaw post must be draft-by-default; human approval mandatory for
  pricing/orders/shipping/warranty/financial/technical safety/legal.
- Publication audit log stays immutable; mirror publishes in the
  `logs/audit.log` convention.

## 7. Current local dev stack (live as of 2026-08-28)

The running local stack is the `300x3-*` container set (rootless Podman on
`ao-sales`) fronted by an `nginx:alpine` proxy — **distinct** from the production
Quadlet units `ao-mastodon-*` documented in §Design, which remain scaffolded.

- Web at `http://localhost:3000`. The `Host` header **must** be `localhost`, not
  `127.0.0.1` — Mastodon's host authorization rejects other hosts with an empty
  403. The proxy rewrites `Host: localhost` for all upstream requests.
- Streaming at `127.0.0.1:4000` (separate `mastodon-streaming` image, v4.3.7,
  routed by the proxy via `/api/v1/streaming`).
- SSL: `RAILS_FORCE_SSL=false` via patched `production.rb`
  (`config/mastodon/patches/production.rb`).
- Operator OAuth client: **Tokodon** (running on display `:0`).

### Bot token (password grant is disabled in Mastodon v4.3.7)

Mint a token bound to an existing bot user via Doorkeeper (run inside the web
container), then persist it with the wallet provisioner:

```bash
podman exec 300x3-web bin/rails runner \
  "u=User.find_by(email:'300x3@posteo.net'); \
   t=Doorkeeper::AccessToken.create!(application_id:Doorkeeper::Application.find_by(uid:'<client_id>').id, resource_owner_id:u.id, scopes:'read write'); \
   puts t.token"
```

Persist the result as `MASTODON_ACCESS_TOKEN` and wallet `ao-mastodon/mastodon-access-token`
(see `scripts/mastodon/provision-openclaw-bot.sh`).

### OpenClaw smoke test

```bash
scripts/mastodon/post.sh "status text" --visibility private
```

Expect HTTP 200 with JSON containing the new status `id` (verify at
`/api/v1/accounts/verify_credentials` → `statuses_count` increments).

### Gotchas recap

| Symptom | Cause | Fix |
|---|---|---|
| 403 empty body on POST through proxy | `Host: 127.0.0.1` | use `localhost` (or proxy rewrites Host) |
| 403 "pending approval" | account `approved=false` | set `approved=true` at creation |
| OAuth "unsupported grant type: password" | v4.3.7 blocks it | mint via Doorkeeper (above) |

## Troubleshooting

- Image pull denied → use a reviewed mirror; record digest in
  `config/platform/version-matrix.yaml` under new `mastodon:` block.
- web can't reach db → confirm both on `ao-sales`, `DB_HOST=mastodon-db`.
- OTP/Secret mismatch → they're in KWallet `ao-mastodon`; re-run `genenv`
  (it preserves existing values).
