# WORK 000010 — Mastodon/Tokodon/OpenClaw/LLM Validation Runbook

Date: 2026-08-28 · Objective: complete WORK 000010 acceptance criteria from
README §19 with an operator present for interactive steps.

## Pre-flight status (verified by agent, 2026-08-28)

| Check | Result |
|---|---|
| Tokodon installed | ✅ `/usr/bin/tokodon` |
| Mastodon Quadlet units in repo | ✅ `quadlet/sales/ao-mastodon-{db,redis,web,sidekiq,streaming}.container` |
| Mastodon stack running | ❌ NOT running — port 127.0.0.1:3000/4000 closed; units not found in any user session |
| Secrets present | ✅ `secrets/mastodon/mastodon.env`, `openclaw-mastodon.env` (gitignored) |
| Instance policy | ✅ `config/mastodon/instance-policy.yaml` — local_domain `300x3`, loopback-only, no federation |
| LM Studio models | ✅ present under `~/.lmstudio/models` |
| LM Studio server | ❌ port 1234 not listening — app must be started and a model loaded |
| OpenClaw | ✅ installed `~/.npm-global/bin/openclaw`, config at `~/.openclaw/openclaw.json` |
| Runbook | ✅ `docs/runbooks/mastodon.md` |

Root cause of "blocked": the `ao-mastodon-*` user units belong to the
`alwayson-sales` service account and are not installed/enabled in its systemd
session. All management commands for that account require operator sudo.

## Progress 2026-08-28 (agent session, pkexec)

- Quadlet units installed into
  `/home/alwayson-sales/.config/containers/systemd/sales/` and aligned with the
  deployed environment:
  - `EnvironmentFile=%h/secrets/mastodon.env` (env mirrored from
    `/ALWAYSON/secrets/mastodon/mastodon.env`, owned `alwayson-sales`, 0600;
    repo units updated — the sales account cannot read `/ALWAYSON/secrets`).
  - Network references corrected to `ao-sales-network.network` /
    `ao-sales-network.service` (the actually deployed network unit).
  - db image reference aligned to `docker.io/library/postgres@sha256:a65e…`.
- `systemctl --user daemon-reload` completed in the sales session.
- `ao-sales-db` and `ao-sales-network` confirmed running.
- **Image pull FAILED** (runbook §2): `docker.io/mastodon/mastodon:v4.3.7`
  anonymous pull denied; `mirror.gcr.io` has no such manifest.

## Remaining operator step (authenticated TTY)

```bash
pkexec bash   # or any authenticated root shell
su -s /bin/bash alwayson-sales
podman login docker.io        # once, if rate-limited
podman pull docker.io/mastodon/mastodon:v4.3.7
exit
systemctl --user enable --now ao-mastodon-db ao-mastodon-redis \
  ao-mastodon-web ao-mastodon-sidekiq ao-mastodon-streaming
```
Then resume the checklist at step 2 (health verification).


1. **Bring up the stack** (per `docs/runbooks/mastodon.md` §2–3):
   ```bash
   sudo -u alwayson-sales env HOME=/home/alwayson-sales \
     XDG_RUNTIME_DIR=/run/user/$(id -u alwayson-sales) \
     systemctl --user daemon-reload
   sudo -u alwayson-sales env HOME=/home/alwayson-sales \
     XDG_RUNTIME_DIR=/run/user/$(id -u alwayson-sales) \
     systemctl --user enable --now ao-mastodon-db ao-mastodon-redis \
       ao-mastodon-web ao-mastodon-sidekiq ao-mastodon-streaming
   ```
2. **Verify health:** `podman exec mastodon-db pg_isready`;
   `curl -s http://127.0.0.1:3000/api/v1/instance | head`; streaming on :4000.
   Run migrations if needed: `podman exec mastodon-web bin/rails db:prepare`.
3. **Start LM Studio desktop**, load the approved model, enable the local
   server (verify `curl http://127.0.0.1:1234/v1/models`).
4. **Tokodon login:** add account with server URL `http://localhost:3000`
   (or the approved `300x3` origin per instance-policy). If OAuth fails on
   insecure-cookie/HTTPS redirect, confirm `LOCAL_HTTPS=false`,
   `RAILS_FORCE_SSL=false` on loopback (ISSUE 000600) and use the
   authorization-code flow — password grant is unavailable in v4.3.
5. **Approve accounts/API access** for the admin and bot accounts if flagged
   (`tootctl accounts approve <name>`).
6. **OpenClaw local conversation:** with the bot token from
   `secrets/mastodon/openclaw-mastodon.env`, exchange a local-only direct
   message and confirm a locally generated draft response from the LM Studio
   model. **No external publication** — `approved_pub_host: null`.
7. **Post-validation evidence:** record results in README §20; confirm logs
   contain no credentials, tokens, or prompts.

## Acceptance criteria (from README §19 / WORK 000010)

- [ ] Tokodon connects via localhost/approved origin
- [ ] OAuth completes without insecure-cookie or forced-HTTPS failure
- [ ] OpenClaw drafts a response through the configured local model
- [ ] No external publication occurs
- [ ] Logs clean of sensitive content
