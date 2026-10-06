# COORDINATION — E: ao-grafana + ao-metabase were DOWN; KWallet readiness gate asked the wrong question

**From:** Cline session, 2026-10-01 ~22:20 PDT
**Scope:** `scripts/operations/fetch-kwallet-secret.sh`,
`scripts/operations/fetch-reporting-env.sh`, and the live recovery of two
`ao-admin` services. Built on document B's wallet work.
**State:** Two scripts fixed and verified live. Both services recovered.
**NOT committed.** Journal: `logs/operations/2026-10-01-kwallet-readiness-gate-fix.log`

---

## Read this first

1. **Two services were DOWN and nobody reported it.** `ao-grafana.service` and
   `ao-metabase.service` were `inactive` from the 15:08 login until I found them
   at ~22:15. Document B verified Grafana healthy at 14:05 and wrote "verified"
   — true *then*, and no longer true ~1 hour later at the reboot.
   **A "verified" claim in B is not a live status.** Re-check before relying on it.
2. **The root cause is in B's own file, and it is a readiness-gate bug, not a
   missing-credential bug.** The gate tested *is kwalletd on the bus*, which is
   true ~20s before the wallet is *unlocked*. It never actually waited. Any other
   script that reads KWallet at login has the same bug.
3. **My first fix attempt was wrong and I caught it mid-flight.** I was about to
   add `After=ao-wallet-bridge.service` to seven Quadlets. Reading
   `ao-wallet-bridge.sh` showed it materializes **only** mastodon + sales-db —
   it never materializes grafana or metabase secrets. Those units fetch their
   *own* secrets. Ordering them after the bridge would have fixed nothing while
   requiring a flat redeploy of two domains. **Do not apply that ordering fix.**
4. **`isOpen` has two D-Bus overloads and this will bite you.** Use
   `isOpen(handle)`. Passing an app name raises `TypeError` because dbus-python
   binds the proxy to the *last* declared signature. Document B's `hasEntry:
   false` trap has a sibling here.

---

## Symptom / evidence

```
$ systemctl --user is-active ao-grafana.service    -> inactive
$ systemctl --user is-active ao-metabase.service   -> inactive

$ journalctl --user -u ao-grafana.service -o short-precise
Oct 01 15:08:20.446773 systemd[2225]: Starting ao-grafana.service ...
Oct 01 15:08:21.022470 systemd[2225]: ao-grafana.service: Failed with result 'exit-code'.
   ... 5 attempts in ~5 seconds ...
Oct 01 15:08:25.060311 systemd[2225]: Start request repeated too quickly.

$ journalctl --user -u ao-metabase.service
Oct 01 15:08:25.167328 systemd[2225]: Control process exited, code=exited, status=3/NOTIMPLEMENTED
```

Decisive evidence — a **0-byte, mode-0664 leftover temp file**:

```
$ stat -c '%y %s bytes mode=%a' ~/.local/share/ao-secrets/reporting-grafana-admin.env.tmp
2026-10-01 15:08:23.903978231 0 bytes mode=664
```

0 bytes proves the write block never executed, so `hasEntry` returned false —
the wallet was **locked**. Not a missing file, not a wrong password. Timing
lines up exactly:

```
$ pgrep -a kwalletd6
3227 /usr/bin/kwalletd6                    # daemon ALREADY up at 15:08
$ systemctl --user status ao-wallet-bridge.service
  OK: wallet-backed Mastodon env materialized  15:08:40
```

Units first attempted **15:08:20**, ~20s before the wallet was usable.

## Root cause

```bash
# fetch-kwallet-secret.sh — the old gate
kwallet_ready() {
    busctl --user list 2>/dev/null | grep -qE '...org\.kde\.kwalletd6?5?...'
}
```

This asks *"is the daemon PRESENT"*. kwalletd6 is D-Bus-activated the moment
anything touches it and appears long before unlock. The predicate returned true
immediately, so the intended 60-second wait **never actually waited**. Then:
`hasEntry` false → `ExecStartPre` fails → systemd burns its 5 fast restarts in
about 5 seconds → unit stays down.

`fetch-reporting-env.sh` (metabase) was worse still: **no wait at all**.

## What was changed

Two files only. Both under `/ALWAYSON/scripts/operations/`. No Quadlet touched,
no unit file redeployed, no data modified.

1. **`fetch-kwallet-secret.sh`** — gate now asks *"is the wallet OPEN"* via the
   D-Bus method `isOpen(handle)`, keeping the 30×2s budget.
2. **`fetch-reporting-env.sh`** — given the same wait it never had.
3. **`fetch-kwallet-secret.sh`** — added `umask 077`. It had **none**, so
   `"$OUTPUT_FILE.tmp"` was created **0664** and the secret sat world-readable
   for the whole write block; only the final file was `chmod 600`. The sibling
   already had `umask 077` — an oversight, and B's new
   `check-secrets-exposure.sh` guard **cannot see it** because it inspects final
   files only. Measured, not assumed: fresh output now `mode=600`.
4. **`fetch-kwallet-secret.sh`** — added an `EXIT` trap deleting a stale `.tmp`
   on failure. Installed **after** the arg check and `OUTPUT_FILE` assignment,
   because `set -u` would abort the trap on the usage-error path. (I got this
   wrong on the first edit and the file lost its `exit 1`/`fi` block; caught by
   re-reading and repaired.)

```
$ git --no-pager diff --stat scripts/operations/fetch-kwallet-secret.sh \
                        scripts/operations/fetch-reporting-env.sh
 2 files changed, 98 insertions(+), 1 deletion(-)
```
## Verification (positive controls included, per B's rules)

```
$ bash -n <both scripts>                                   -> syntax OK
$ fetch-kwallet-secret.sh            -> usage exit 1, no "unbound variable"
$ fresh fetch output mode            -> 600
$ negative control: missing daemon    -> gate=FALSE (correct)
$ positive control: failing fetch    -> no .tmp leftover (CLEANED)
$ systemctl --user restart ao-grafana.service   -> active, container Up
$ systemctl --user restart ao-metabase.service  -> active, container Up
$ curl -w '%{http_code}' 127.0.0.1:3001/api/health        -> 200 {"database":"ok"}
$ curl -u "admin:<wallet value>"   127.0.0.1:3001/api/health -> 200
$ curl --max-time 20 127.0.0.1:3002/api/health             -> 200 {"status":"ok"}
$ systemctl --user list-units --all | grep -E '\bfailed\b' -> empty
$ bash scripts/validation/check-secrets-exposure.sh -> OK, exit 0
$ find ~/.local/share/ao-secrets/ -name '*.tmp'    -> empty
```

**Trap: metabase answers `503` for its first ~18s.** That is JVM init, not a
fault — the log says `Metabase Initialization COMPLETE in 18.3 s`. I nearly
logged it as a failure. Re-check after init before judging.

**Not a defect:** `mastodon.env` and `sales-db.env` are mode **0640**, not 0600.
`ao-wallet-bridge.sh` sets those deliberately via `setfacl` for the `ao-sales`
consumer UID. Correct as-is; don't "fix" it.

## Open findings

1. **Seven Quadlets read KWallet in `ExecStartPre` and none order on the wallet
   being unlocked.** `ao-fabrication-db`, `ao-grafana`, `ao-metabase`,
   `ao-mastodon-db`, `ao-sales-db`, `ao-ingress-payment`, `ao-webodm-db`.
   The gate fix removes the *symptom* for all of them, but the underlying
   start-ordering gap is still there. **Needs operator approval** before any
   Quadlet edit + flat redeploy of 5 domains. Recommend leaving it: the gate is
   the more robust fix (it survives a locked wallet for any reason, not just at
   login). My recommendation is **do not** do the ordering change.
2. **`check-secrets-exposure.sh` cannot detect the `.tmp` exposure class.** It
   globs `*.env`/`*.credential`, so `*.env.tmp` is invisible to it. Consider
   extending the glob and adding a `.tmp` mode check. No operator approval
   needed (validation script only) — not done, out of scope here.
3. **Carried forward from B, still OPEN, still untouched by me:** `~/.bashrc`
   `LM_API_TOKEN` duplicate (needs approval, **do not rotate**);
   `pkexec-post-deploy.sh:46-52` generating a password (needs approval, root
   path); `~/pCloudDrive/PUBLIC FOLDER` never scanned (safe, unactioned);
   `roundtrip`/`roundtrip2` wallet test artifacts (safe to delete, unactioned);
   README §14.1.1 claiming `ao-payment`/`ao-field`/`ao-ledger`/`ao-archive` exist
   when `folderList` does not return them.

## Two things I got wrong

1. **I proposed the wrong fix before diagnosing fully.** I reached for
   `After=ao-wallet-bridge.service` on the strength of "grafana failed at login
   and the bridge ran at login". I had *assumed* the bridge supplied grafana's
   secrets because B's topology calls KWallet the "secret authority". Reading
   `ao-wallet-bridge.sh` disproved it in one command. **Reason:** I inferred the
   data flow from architecture prose instead of reading the script that produces
   the file. Same class of error B documents in its retraction box — assuming a
   layout instead of enumerating it.
2. **My first `trap` edit corrupted the script.** Installing `trap ... EXIT`
   before `OUTPUT_FILE` was assigned meant `set -u` would abort inside the
   handler; my follow-up edit then deleted the `exit 1` / `fi` / `shift` block
---

# ADDENDUM — follow-up work, same session

**Supersedes:** nothing above is retracted. This addendum records four further
items and **corrects one claim I made earlier in this document**.

## A. My "lock test" did not work — read this before trusting it

I proposed a cheap test: lock the wallet, prove the gate reports FALSE, unlock.
**It cannot be done that way.** `KWallet` exposes no `lock()`/`unlock()`; the only
lever is `closeAllWallets()`, and calling it does *not* leave the wallet locked —
the next `open()` transparently re-unlocks via PAM:

```
STEP 1: gate with wallet OPEN   -> TRUE
STEP 2: closeAllWallets()
STEP 3: gate with wallet CLOSED -> TRUE      <-- should have been FALSE
```

**So the locked-wallet path is still proven only by the 0-byte `.tmp`
forensics, not by a live lock/unlock cycle.** I am not claiming otherwise. The
wallet was verified fully intact afterwards: **18 unique folders, 39 entries**,
identical to the pre-test inventory. Both services were unaffected throughout
(passwords are baked into container env, so the runtime never re-reads the
wallet).

## B. `folderList` returns DUPLICATE rows — this will fool your next audit

My first enumeration reported **990 rows / "972 folders"**. That looks like
catastrophic data duplication. It is not:

```
folderList raw rows = 990
folderList UNIQUE  = 18      <-- the truth
```

`entriesList` behaves the same way. **Always `set()` the result before counting.**
Had I not cross-checked against B's known 18, I would have reported a fabricated
54× duplication incident. Recorded in README §14.1.4.

## C. pCloud Public Folder scanned — B's open finding 4, now closed

50,422 files. Repo has **0 commits and no remote**, so nothing was ever committed
or pushed. Scanned 12,998 candidate files (excluding `node_modules`, `.git`,
and >2MB binaries) in 6 chunks — the 30s command ceiling killed every full-tree
background scan, which is why it was chunked.

**Exactly one hit**, and it is a placeholder:

```
ARCHIVED/300X3-FRONTEND/X-ARCHIVE/-GENERAL-FILE_ME/BACKEND DEVELOPMENT REPORT - UNFORMATTED
  line 2082, 2389:  export MISTRAL_API_KEY=<redacted>
  len=24  prefix "you..."  sha256 8bedb84b4ace  -> matches placeholder markers
```

No `MISTRAL*` entry exists anywhere in the wallet, so there is no live credential
for it to be. The 4 credential-shaped *filenames* repo-wide are all third-party
vendor files (public CA certs, translation binaries) in an archived WordPress
backup.

**Verdict: no live secret in the Public Folder.** The placeholder should still be
scrubbed before that folder is ever shared — flagged, not changed.

## D. Validator extended, README reconciled

`check-secrets-exposure.sh` now catches the `.tmp` class it structurally could
not see. Four negative tests, all planted-then-detected-then-removed; baseline
exit 0.

README §14.1.1 now **retracts the "provisioned empty 2026-08-31" claim in place**
for `ao-payment`/`ao-field`/`ao-ledger`/`ao-archive` — `folderList` does not
return them, so they are *absent*, not empty. Plus the dbus-python overload trap,
the duplicate-rows trap, the `isOpen` rule with this outage as the worked example,
and the `closeAllWallets` limitation.

## Three things I got wrong in this follow-up

1. **The validator's first version failed 4 healthy files.** I applied the
   "leftover debris" branch to every matched file instead of only `*.tmp`, so
   `payment.env`, `legacy-alwayson-folder.env`, `grafana-admin.env` and
   `photogrammetry-volume.env` were wrongly reported. Caught only because I ran
   the validator before trusting it. Scoped to `*.tmp`; re-verified.
2. **I nearly reported a fake security incident.** The "972 folders" number was a
   counting artifact, not data duplication. I caught it by checking against B's
   known-good inventory — the same discipline B's retractions describe.
3. **My README correction was itself wrong on first draft.** I wrote that
   `kwallet-provision.sh` "creates templates but not folders". Reading the script
   disproved it: it has `createFolder()` and `put()` auto-creates a missing
   folder. Corrected before commit. **Reason:** I generalised from a filename
   without reading the function — assuming a layout instead of enumerating it,
   the exact error B documents.

## Still needs the operator

- `~/.bashrc` `LM_API_TOKEN` duplicate — untouched (**do not rotate**).
- `pkexec-post-deploy.sh:46-52` — untouched, root path.
- `roundtrip` / `roundtrip2` in `ao-mastodon` — **confirmed still present**, and
  deliberately **not** deleted. B called them "safe to delete", but deleting wallet
  entries is a write to the secret store and I did not treat that as sufficient
  authorisation. One word from you and I remove them.
- The `MISTRAL_API_KEY` placeholder in the Public Folder — scrub before sharing.

## Not recommended

The seven-Quadlet start-ordering change. The `isOpen` gate is the more robust fix
because it survives a locked wallet for *any* reason, not just at login.
   outright. I only noticed because I re-read the file. **Reason:** I chained
   two structural edits on a script with `set -euo pipefail` and trusted the
   editor's success message. `bash -n` plus a usage-path test is now part of my
   routine for shell edits here.

## Housekeeping

- **My changes are uncommitted**, mixed into a tree that already holds B's and
  C's uncommitted work. My two files:
  `scripts/operations/fetch-kwallet-secret.sh`,
  `scripts/operations/fetch-reporting-env.sh`.
  **Stage by file. Do not `git add -A`.**
- New journal file: `logs/operations/2026-10-01-kwallet-readiness-gate-fix.log`.
- I removed one stale file: `~/.local/share/ao-secrets/reporting-grafana-admin.env.tmp`
  (0 bytes, mode 0664, no secret content — debris from the failed run).
- No secret value was printed or logged anywhere, including this document.
- Temporary probes in `/tmp` were used and removed; `/tmp/ao-*.env` scratch
  files cleaned up.
- I did **not** edit any Quadlet, did **not** redeploy, did **not** commit, did
  **not** touch `~/.bashrc`, the wallet, or `pkexec-post-deploy.sh`.

## Coordination notes for the other sessions

- **A (mastodon/federation):** your inbound ActivityPub finding is unaffected.
  I touched no mastodon unit; `ao-mastodon-db` is still `active running`. Your
  `openclaw-bot-access-token` was not read or moved.
- **C (gazebo GUI):** untouched and still masked. Your gdb step is still blocked
  only on operator approval for a throwaway image tag. D's finding that the
  reboot already happened still stands — `7.0.0-38-generic`, no
  `/var/run/reboot-required`.
- **D (review/rule):** your numbers were right and are now slightly stale.
  Re-measured at 22:20: modified files **20**, untracked **13**. I did not
  renumber or edit A, B, C or D.