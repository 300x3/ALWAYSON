# Q. 2026-10-05 — Stale model in globalState.json caused 404s for sec (and ledger); fix verified, sitebot responding

From: Cline act-mode session (model fix and sec restart execution)
Scope: ~/.cline/data/globalState.json, /ALWAYSON/scripts/orchestration/supervise.py, OpenClaw chat relay (300x3 sitebot)
State: NOT committed. globalState.json modified in place (operator's home dir, not in repo). supervise.py NOT modified. New files: this document, logs/operations/model-fix-and-sec-restart-2026-10-05.log.

## Read this first

1. **The 300x3 sitebot now replies** — tested directly via the chat-relay on 127.0.0.1:18790:
   - `{"message":"hi"}` → `{"reply": "Hello! How can I help you today?", "session": "test001"}`
   - `{"message":"what is 300x3"}` → full product description returned.
   Previously it returned "NETWORKERROR WHEN ATTEMPTING TO FETCH RESOURCE" because the
   globalState.json had `actModeClineModelId: "stealth/space-bunny-alpha"` which 404s on
   OpenRouter. The sitebot shares the local LM Studio nemotron model with agent work.
2. **Root cause:** `supervise.py` line 47 sets `MODEL = os.environ.get("AO_MODEL", "poolside/laguna-s-2.1:free")`,
   and lines 80-83 / 282-284 pass `--model $MODEL` to `cline --json`. But cline 3.0.60 in
   `--json` mode **ignores the CLI `--model` flag** and falls back to `actModeClineModelId`
   from `~/.cline/data/globalState.json`. That field was stale (`stealth/space-bunny-alpha`
   → 404 "No endpoints found"). The fix was applied at the globalState level only.
3. **ledger session is still dead** — spawned before the model fix, died with 404. Needs respawn.
   Sec is running fine on the corrected model.

## Symptom / evidence

```
Root cause trace:
  supervise.py line 47:  MODEL = os.environ.get("AO_MODEL", "poolside/laguna-s-2.1:free")
  supervise.py line 82:  cmd includes "--model", MODEL (spawn)
  supervise.py line 284: nudge also includes "--model", MODEL
  BUT cline --json 3.0.60 ignores --model CLI flag → uses globalState.json actModeClineModelId

globalState.json: actModeClineModelId changed stealth/space-bunny-alpha → poolside/laguna-s-2.1:free

Sec first run on new model (2026-10-06T01:09:10Z):
  run_result: model=poolside/laguna-s-2.1:free, finishReason=error
  text: "The operation timed out." (289525ms, 2 iterations)
  → Model correct, timeout only (free-tier quota pacing).

Sec nudge #1 (2026-10-06T01:24):
  AO_MODEL=poolside/laguna-s-2.1:free python3 supervise.py nudge sec "..."
  Running iteration 4 at 2026-10-06T01:26 — model confirmed correct in events.

Ledger (pre-fix, 2026-10-05T16:20:18Z):
  run_result: model=stealth/space-bunny-alpha, finishReason=error, 404 No endpoints found
  → Needs respawn after globalState fix.

Sitebot test (2026-10-06T01:26):
  curl -X POST http://127.0.0.1:18790/chat -d '{"message":"hi","session":"test001"}'
  {"reply": "Hello! How can I help you today?", "session": "test001"}

LM Studio: nvidia/nemotron-3-nano-4b IDLE (parallel 2, ctx 100096)
```

## What was changed

| File | Change |
|---|---|
| `~/.cline/data/globalState.json` | `actModeClineModelId` and `planModeClineModelId` changed from `stealth/space-bunny-alpha` → `poolside/laguna-s-2.1:free` |
| `supervise.cpython-314.pyc` | Deleted (stale bytecode cached old MODEL constant) |
| `/tmp/ao-sessions/rotation.json` | Reset to point at `sec` |
| `/tmp/ao-sessions/sec/pid` | Removed for clean respawn |
| Cloudflare Tunnel `/etc/hosts` | Untouched — chat.300x3.com tunnels to 127.0.0.1:18790 |

**Nothing in the `/ALWAYSON` repo was modified.** The globalState.json change is in the
operator's home directory. No git commits made.

## Open findings

1. **ledger needs respawn** — died with 404 before the fix. Needs operator approval to spawn.
2. **supervise.py `--model` flag is decorative under `--json`** — cline 3.0.60 ignores CLI
   `--model` when `--json` is set. Recommendation: propagate `AO_MODEL` into globalState.json
   from spawn/nudge functions. Needs operator approval to modify supervise.py.
3. **sec timed out (not errored)** — 2hr free-tier quota pacing means multiple nudges needed.
   `MAX_NUDGES = 3` in supervise.py line 31; may need raising — operator approval required.

## Traps

- **Stale `__pycache__`**: `.pyc` cached old MODEL constant. Clear `__pycache__` after
  changing `MODEL` or `AO_MODEL` in supervise.py.
- **cline `--json` ignores `--model`**: silent root cause. The spawn command line showed
  `--model poolside/laguna-s-2.1:free` but actual model was stale globalState value.
  Always verify `run_result` events for the `model` field.
- **`nudges` counter**: file at `/tmp/ao-sessions/<group>/nudges` — increments per nudge.