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
2. Enter server URL: `http://localhost:3000`  (the loopback publisher).
3. Complete the OAuth authorization (registering an application in Mastodon).
   Tokodon stores its own credential via the KDE secret store; keep a copy of
   the client id/secret in KWallet `ao-sales/mastodon-tokodon-client-*` if you
   prefer to reuse that application registration (see below).
4. Posts/boosts/replies from Tokodon are the "operator client" feed.
   OpenClaw will talk to the same local HTTP API with a dedicated bot account.

### Optional: pre-registered Tokodon application
Mastodon OAuth client credentials for Tokodon can be created ahead of time:
```bash
curl -s -X POST http://127.0.0.1:3000/api/v1/apps \
  -d 'client_name=Tokodon' -d 'redirect_uris=urn:ietf:wg:oauth:2.0:oob' \
  -d 'scopes=read write follow'
```
Store `client_id`/`client_secret` in KWallet `ao-sales`:
```bash
/ALWAYSON/scripts/ops/kwallet-provision.sh put kdewallet ao-sales tokodon-client-id <id>
/ALWAYSON/scripts/ops/kwallet-provision.sh put kdewallet ao-sales tokodon-client-secret <secret>
```

## 6. Ledger/adapter notes (Section 3.8 carried over)
- Outbound egress only to approved host. For this instance it is local; keep
  `approved_pub_host: null`.
- Any OpenClaw post must be draft-by-default; human approval mandatory for
  pricing/orders/shipping/warranty/financial/technical safety/legal.
- Publication audit log stays immutable; mirror publishes in the
  `logs/audit.log` convention.

## Troubleshooting
- Image pull denied → use a reviewed mirror; record digest in
  `config/platform/version-matrix.yaml` under new `mastodon:` block.
- web can't reach db → confirm both on `ao-sales`, `DB_HOST=mastodon-db`.
- OTP/Secret mismatch → they're in KWallet `ao-mastodon`; re-run `genenv`
  (it preserves existing values).