# P. 2026-10-05 — LM Studio: one loaded model validated as shared OpenClaw+Cline endpoint (no split performed)

From: Cline act-mode session (LM Studio / OpenClaw / Cline handoff execution)
Scope: host LM Studio daemon (llmster), OpenClaw provider, Cline CLI lmstudio provider
State: NOT committed. Zero configuration files changed. New uncommitted files:
`/ALWAYSON/logs/operations/lmstudio-shared-endpoint-2026-10-05.log` (journal) and
this document. Everything else OPEN as listed below.

**Supersedes:** revision 2, 2026-10-05 ~14:10 PDT — all four open findings below
were resolved same-day under direct operator directives; see "Open findings →
Resolutions". Findings 1-4 are CLOSED; only cosmetic observations remain.

## Read this first

1. **The source document contradicts itself.** `/home/scottw/Desktop/DASHBOARD
   UPDATES/I NEED TO SPLIT MY LOADED LM STUDIO MODEL INTO TWO.md` contains TWO
   answers: part 1 says run TWO LM Studio servers (1234 public via Caddy + 1235
   private); part 2 says explicitly "Do NOT create a second server instance."
   The operator chose part 2 ("maximize gpu use by running the lmstudio model
   and using it for openclaw requests as well as cline requests while still
   separating the content"). Part 1 was NOT implemented and cannot fit anyway:
   measured GTX 1080 has 8192 MiB and one nemotron instance already costs
   ~4.5 GiB; README §4.3 also lists `Public internet → … LM Studio …` as
   prohibited without explicit operator approval.
2. **Nothing needed fixing — do not "repair" configs that already work.**
   Measured: server loopback-only on 127.0.0.1:1234 with 401 auth, engine runs
   `--parallel 2` (that IS "Max Concurrent Predictions = 2"), OpenClaw points at
   `http://127.0.0.1:1234/v1` (api=`openai-completions`), and Cline already has
   a working `lmstudio` provider whose stored apiKey is sha256-equal to the KDE
   Wallet entry. The handoff doc suggests `api: openai-responses` — the live,
   working value is `openai-completions`; leave it.
3. **My only self-correction:** an early length/hash probe of the wallet token
   reported 37 chars (measurement artifact: literal quotes leaked into the
   printf pipeline). Verified truth: entry `lmstudio-api-key` is 35 chars and
   equals Cline's stored apiKey. No token rotation occurred.
4. `lastUsedProvider` in `~/.cline/data/settings/providers.json` is still
   `cline` (cloud). That is deliberate — I did not change the operator's default
   provider. Local runs select it per-invocation with `-P lmstudio`.

## Evidence (2026-10-05, full log in journal)

```
$ ss -ltn | grep :1234        -> 127.0.0.1:1234 (llmster pid 2658)
$ curl /v1/models (no token)  -> 401
$ lms ps                      -> nemotron-3-nano-4b IDLE ctx 100096 parallel 2
$ engine args                 -> --n-gpu-layers 999999 --parallel 2 --ctx-size 100000
4-request barrier test        -> all 200, peak in-flight=4, zero sentinel cross-leak
real overlap test             -> openclaw_window (7.2s) entirely inside
                                 cline_window (124s); OpenClaw reply 200,
                                 own sentinel only; GPU 83-91%, VRAM peak 5972 MiB
cline -P lmstudio             -> exit 0, exact sentinel (2172ms; recheck 7829ms)
post-test                     -> model loaded, 5736/8192 MiB, bind unchanged, 401
api-prediction-history        -> newest pack ~Sep 24: today's tests wrote no
                                 prompt/response content to disk
```

Content separation is client-side (OpenClaw agent SQLite vs Cline task sessions;
server stateless per request) — no shared conversational state exists to leak.

## What was changed

- Created journal `/ALWAYSON/logs/operations/lmstudio-shared-endpoint-2026-10-05.log`
- Created this document
- Nothing else. Pre-existing dirty files under `/ALWAYSON/TOPOLOGY/` belong to
  another session; not staged, not touched. No commits made.

## Open findings → Resolutions (all closed same-day, 2026-10-05)

1. **Max Concurrent Predictions 2 → 3/4 — CLOSED, operator decision: STAY AT 2**
   ("we only want two — one openclaw, one cline"). No change made; `--parallel 2`
   remains in the supervisor and the live engine.
2. **`ao-lmstudio-preset-sync.service` failed — CLOSED, REPAIRED.** Root cause:
   ≥5 rapid README writes on Oct 2 tripped systemd start-limit; both units stuck
   failed so the path unit stopped watching (README changed Oct 4, preset stale).
   Fixed: `reset-failed` both units, added `StartLimitIntervalSec=300` /
   `StartLimitBurst=60`, daemon-reload, regenerated preset (state hash now ==
   README hash `d43b05aa…`, 891324 bytes, JSON valid), manual trigger →
   "Finished", path unit active. Work-product consumers: repo-wide grep finds
   only the generator script — no automation reads the preset; its consumer is
   the operator manually via the LM Studio GUI preset list.
3. **`lms-key-2` — CLOSED, KEPT + chmod 600 (documented policy exception).**
   Reversible probe proved dependence: with the file moved aside, `lms ps` dies
   `ENOENT: ... open '.../lms-key-2'` (restored, sha unchanged, `lms ps` OK).
   The `lms` CLI builds `clientPasskey: lmsKey + lmsKey2` from this file with an
   UNGUARDED read in its connect path — deleting it breaks `lms` and therefore
   `ao-lmstudio.service`. It is the CLI↔daemon IPC passkey half, NOT the HTTP
   API token (that is KDE Wallet entry `lmstudio-api-key`); vendor-hardcoded
   path means it cannot move to the wallet. Mode tightened 0664 → 600.
4. **OpenClaw ao- prefix — CLOSED, FIXED AND VERIFIED.** Three parts: (a) dist
   patch `constants-obO8goqF.js` `GATEWAY_SYSTEMD_SERVICE_NAME` →
   `ao-openclaw-gateway` (backup `.bak-ao-20261005`); (b) residual wrong state
   root-caused to legacy `Environment=OPENCLAW_SYSTEMD_UNIT=openclaw-gateway.service`
   in the unit files — fixed in BOTH `~/.config/systemd/user/` and
   `~/.config/containers/systemd/` copies; (c) daemon-reload + gateway restart
   (pid 1276383, env verified). Verification: `openclaw status` →
   "systemd user installed · enabled · running (pid 1276383, state active)";
   `openclaw gateway status` → "Service: systemd user (enabled)"; strace shows
   `is-enabled`/`show` targeting `ao-openclaw-gateway.service`; relay + bridge
   units active after restart. Durability: run
   `/ALWAYSON/scripts/operations/patch-openclaw-ao-unit-name.sh` after every
   `openclaw update` (idempotent, tested rc=0).

Remaining cosmetic observations (not touched): `openclaw gateway status` warns
the unit PATH lacks `/home/scottw/.bun/bin` (pre-existing); `Node service` row
"not installed" is correct — no node service is deployed.

## Traps (updated)

- Wallet helper REQUIRES its argument: `openclaw-kwallet-secret lmstudio-api-key`
  (bare call → "Unsupported wallet entry", exit 64).
- Supervisor unit is `ao-lmstudio.service`, not the `alwayson-lmstudio.service`
  named in the supervisor script's own comment (stale comment).
- Cline's model spelling `nemotron-3-nano-4b` (no org prefix) is valid; server
  normalizes to `nvidia/nemotron-3-nano-4b:2`.
- Long reasoning prompts can outlive client timeouts (my 200-word-essay test hit
  my own `-t 120`); short sentinel prompts complete in 2-8s.
- `run_commands` here caps at 30s — background long tests and poll flag files.
- `openclaw update` overwrites `dist/` and reverts the ao- name constant — run
  `/ALWAYSON/scripts/operations/patch-openclaw-ao-unit-name.sh` afterwards.
- Never run `openclaw gateway install` — it would overwrite the customized
  unit file (wallet/DBUS Environment lines live only there).
- The unit's `OPENCLAW_SYSTEMD_UNIT` Environment line drives which unit
  `openclaw status` probes — keep it equal to `ao-openclaw-gateway.service` in
  BOTH unit-file copies (user + containers/systemd).

## Housekeeping

Scratch dir `/tmp/cline-lmstudio-smoke/` (test scripts, sentinel responses,
logs) is deletable; 3 short-lived Cline test sessions exist in `~/.cline/data`.
Journal is the authoritative detail record.
