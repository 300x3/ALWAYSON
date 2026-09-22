# ALWAYS ON — Mastodon Runbook (federated apex deployment, WORK 000060 2026-09-22)

Scope: operator chose to **self-host Mastodon locally** (rather than only
posting to an external host) and to operate it from the desktop with
**Tokodon** (KDE Mastodon client, already installed at `/usr/bin/tokodon`).
Public origin is **`https://300x3.com`** via Cloudflare Tunnel edge
(`alwayson-mastodon`); the stack stays containerized on
the internal `ao-sales` network; Web/Streaming publish **only to 127.0.0.1**
(`PublishPort=127.0.0.1:3000` / `:4000`). **No public port is opened on the
workstation** — the tunnel connector is the only public path
(`listener-allowlist` stays empty of inbound host ports).

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
the Mastodon Web UI at `https://300x3.com` (or Tokodon).

## 5. Tokodon (operator client)
1. Launch Tokodon (KDE menu → Tokodon); "Add account".
2. Enter server URL: `https://300x3.com` (the federated apex origin;
   identity `LOCAL_DOMAIN=300x3.com`, so handles read `@admin@300x3.com` /
   `@bot@300x3.com`).
3. Complete the OAuth authorization (registering an application in Mastodon).
   Tokodon stores its own credential via the KDE secret store; keep a copy of
   the client id/secret in KWallet ao-mastodon/tokodon-client-* if you
   prefer to reuse that application registration (see below).
4. Posts/boosts/replies from Tokodon are the "operator client" feed.
   OpenClaw talks to the same origin over HTTPS with a dedicated bot account.

### Optional: pre-registered Tokodon application
Mastodon OAuth client credentials for Tokodon can be created ahead of time
(against the public origin):
```bash
curl -s -X POST https://300x3.com/api/v1/apps \
  -d 'client_name=Tokodon' -d 'redirect_uris=urn:ietf:wg:oauth:2.0:oob' \
  -d 'scopes=read write follow'
```
Store `client_id`/`client_secret` in KWallet `ao-mastodon`:
```bash
/ALWAYSON/scripts/ops/kwallet-provision.sh put kdewallet ao-mastodon tokodon-client-id <id>
/ALWAYSON/scripts/ops/kwallet-provision.sh put kdewallet ao-mastodon tokodon-client-secret <secret>
```

## 6. Ledger/adapter notes (Section 3.8 carried over)
- Outbound egress only to approved host (`approved_pub_host: 300x3.com`;
  delivery path requires the scoped `ao-egress-community` Sidekiq route,
  WORK 000060 outstanding).
- Any OpenClaw post must be draft-by-default; human approval mandatory for
  pricing/orders/shipping/warranty/financial/technical safety/legal.
- Publication audit log stays immutable; mirror publishes in the
  `logs/audit.log` convention.

## 7. Current federated deployment (live as of 2026-09-22, WORK 000060)

The running stack is the `alwayson-sales` Quadlet set (`ao-mastodon-{db,
redis,web,sidekiq,streaming}`) on `ao-sales`, served publicly at
`https://300x3.com` via Cloudflare Tunnel `alwayson-mastodon`.

- Web origin `127.0.0.1:3000` (loopback-only). The `Host` header **must** be
  `300x3.com` — the tunnel supplies it (other hosts → empty 403 by design).
- Streaming origin `127.0.0.1:4000` (separate `mastodon-streaming` image, v4.3.7,
  routed by the tunnel ingress via `^/api/v1/streaming`).
- TLS: enforced at the edge (`RAILS_FORCE_SSL=true`, `LOCAL_HTTPS=true`);
  the loopback-only `RAILS_FORCE_SSL=false` exception is retired (Section 18.5).
- Operator OAuth client: **Tokodon** at `https://300x3.com`.
- Accounts of record: `admin` (admin@300x3.com), `bot` (bot@300x3.com);
  registrations open with approval gate.

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
