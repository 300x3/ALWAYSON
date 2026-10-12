# MeshChatX integrity repair — 2026-10-10 18:15

Cleared the orange "Critical integrity failure" banner on
`https://127.0.0.1:18000/#/about#about-database-backups`.

## Symptom

Orange header banner: `Critical security component integrity compromised: Integrity manifest
tampered or replaced`. Classified *critical*, so the app treated it as a hard integrity gate.

## Root cause

The identity manifest at
`~/.reticulum-meshchatx/identities/2ba93a0dcd5881a9ea21f2e2cf93e4b3/integrity-manifest.json`
had a stale/invalid **HMAC**. All 20 tracked file hashes were correct and there was no content
drift — the manifest body was faithful, only its signature failed to authenticate. Cause: an earlier
session (recorded in `status-and-references.md` as ST-11) edited `integrity-manifest.json` directly,
which invalidates the signature by design.

## Method (no hand-editing of a signed file)

The binary is a Nuitka build with no Python source, so the HMAC scheme was recovered from shipped
bytecode and the fix applied with the app's own code:

1. Extracted `ReticulumMeshChatX-v4.9.1-linux-x86_64.AppImage`; read
   `resources/backend/lib/meshchatx/src/backend/integrity_manager.pyc`.
2. Recovered the scheme by disassembly:
   - `_canonical` = `json.dumps(payload, sort_keys=True, separators=(',',':'))`
   - `_sign_payload` = `HMAC-SHA256(key, canonical).hexdigest()`
   - `_manifest_hmac` signs every key except `hmac`

   Verified against both `manifests.json` registries, which validate.
3. Loaded the real `IntegrityManager` from its `.pyc` under system Python 3.14.4 (same minor
   version as the bytecode) and reproduced the exact critical message.
4. Pre-flight: `_scan_storage()` vs on-disk manifest showed **NEW: none, MISSING: none, HASH
   CHANGED: none** — proving only the signature was bad.
5. Stopped the service, backed up the broken manifest to
   `/tmp/mcx_repair/integrity-manifest.json.BROKEN.bak`
   (sha256 `9484acd65eef499d60725c4dfed3879920e11b2cf38bb6e9f4e4d9f7ee2c5381`), then called
   `save_manifest(reason='acknowledge')`.

## Result

- `check_integrity()` → `(True, [])` immediately after re-signing.
- HMAC verifies independently; `database.db` metadata corrected to `size=18083840`.
- Service restarted (MainPID 4091073, `NRestarts=0`); `journalctl` shows **no** integrity, tamper,
  or critical-security lines since 18:16:03.
- Headless Chrome on the About page: banner strings present **0 times**. Page now reaches
  `Authentication Required`, the normal login gate — the app passed the integrity gate.
- Database confirmed healthy before the change: `PRAGMA integrity_check` = `ok`, 43 tables.

## Expected residual (not a fault)

`database.db` legitimately changes while the app runs, so a later scan reports
`Expected change after unclean shutdown or update: modified: database.db`. Measured:
`select_critical_integrity_issues()` returns **NONE** for it — non-critical, does **not** raise the
orange banner. Clears on the next clean-exit baseline.

## Lesson

Never hand-edit `integrity-manifest.json`; the signature covers the body. Use
`/api/app/integrity/acknowledge` (the UI's "Acknowledge & Reset") or the app's own
`save_manifest()` path. Repair scripts: `/tmp/mcx_repair/run_repair.py`, `verify_now.py`.
