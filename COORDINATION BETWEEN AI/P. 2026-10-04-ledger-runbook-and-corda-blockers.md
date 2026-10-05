# P. Corda bootstrap runbook asserts two pieces of state that do not exist, so its own start command cannot run

**From:** LEDGER session (ledger, accounting, provenance)
**Scope:** LEDGER-01 … LEDGER-07; §11.1–§11.10; seven §19 proposals
**State:** COMMITTED `e809d98`, pushed `ai-ledger`, GitHub API **HTTP 200**. Nothing applied to live data, credentials, or money. **OPEN** — LEDGER-01, -02, -03, -04, -07 all remain open and operator-blocked.

## Read this first

1. **`docs/runbooks/ledger-bootstrap.md` is worse than two sessions have reported.** The 2026-10-03 and 2026-10-04 passes found the wrong *account name* and stopped. That same "State after scaffold" block also asserts **"linger enabled"** (false) and **"systemd user unit installed"** (false, and self-refuting). Measured below.
2. **LEDGER-07 has a fourth blocker that is NOT a key ceremony.** Even with a working `cordadb` password, the node cannot be started by the runbook's procedure. Anyone planning the ceremony needs to know there are two things to fix, not one.
3. **§19's "cordadb holds 0 tables" is still unverified after three sessions.** Do not restate it as fact. An authentication failure is not evidence of an empty database.
4. `systemctl --user is-active` prints `inactive` for a unit that **does not exist**. Three LEDGER sessions have now hit this. Use `-p LoadState`.

## Evidence

```text
$ cd /ALWAYSON/data/corda-install && sha256sum -c *.sha256sum
corda-cli-installer-5.2.2.0.zip: OK
corda-combined-worker-5.2.2.0.jar: OK
notary-plugin-non-validating-server-5.2.2.0-package.cpb: OK

$ getent passwd ao-ledger
ao-ledger:x:994:974:ALWAYS ON ledger core service:/home/alwayson-ledger:/usr/sbin/nologin
$ id -u alwayson-ledger
id: 'alwayson-ledger': no such user

# runbook line 4: "(linger enabled)"  -- FALSE
$ loginctl show-user ao-ledger -p Linger
Failed to get user: User ID 994 is not logged in or lingering
$ loginctl list-users
 UID USER   LINGER STATE
1000 scottw yes    active
1 users listed.
$ ls -d /run/user/994
ls: cannot access '/run/user/994': No such file or directory

# runbook line 9: "unit installed (not started)"  -- FALSE
$ systemctl --user show ao-ledger-core.service -p LoadState -p FragmentPath
LoadState=not-found
FragmentPath=
$ systemctl --user list-unit-files | grep -iE 'ledger|corda'   # rc=1
$ systemctl list-unit-files          | grep -iE 'ledger|corda' # rc=1
$ find /etc/systemd /usr/lib/systemd ~/.config/systemd \
       -iname '*ledger*' -o -iname '*corda*'                   # no output
$ find quadlet -iname '*ledger*'
quadlet/networks/ao-ledger-core.network

$ bash /ALWAYSON/scripts/validation/check-ledger-ingest.sh
PENDING: ledger-ingest gateway not deployed yet (Section 2.8 step 3 awaits Corda version approval)
EXIT=3

$ bash /ALWAYSON/scripts/ledger/build-manifest.sh map_product TOTALLY_MADE_UP_DOMAIN /tmp/p.txt ref://x | jq -r .origin_domain
TOTALLY_MADE_UP_DOMAIN                       # origin_domain unvalidated
$ bash /ALWAYSON/scripts/ledger/build-manifest.sh not_a_type ao-mapping /tmp/p.txt ref://x
ERROR: bad object_type                       # object_type IS validated -- asymmetry is real
EXIT=11

$ bash /ALWAYSON/scripts/ledger/sign-manifest.sh /tmp/p.json wallet:ao-sales
ERROR: manifest or key missing (keys live in KDE Wallet ao-sim-*; ...)
EXIT=10                                     # wallet:ao-sales is unimplemented, not "missing"

$ jq -r '{producer_key_id, authorization_policy_id, sig_len:(.signature|length)}' \
    /ALWAYSON/artifacts/pending-ledger-submissions/20260824/manifest.json
{ "producer_key_id": "test", "authorization_policy_id": "", "sig_len": 96 }
```

## What was changed

Only files I own. Nothing else was touched.

| File | Change |
|---|---|
| `agents/COORDINATION/11-.../section.md` | **New §11.10** (third-pass verification); §11.7 gains blocker 4 and a pointer |
| `README.md` | Recompiled. `compile.py --check` -> `identical`; diff confined to section 11, purely additive |
| `agents/COORDINATION/proposals/ledger-LEDGER-0{1..7}.md` | Third-pass evidence added; LEDGER-07 gained the fourth blocker |

§19 was **not** edited — proposals are for the compiler to merge.

## Open findings

1. **Runbook asserts non-existent state — operator decision, not mine.** `docs/runbooks/` is outside my ownership. Two false assertions plus a step-5 command that cannot execute. Needs a docs fix by whoever owns runbooks.
2. **Enable linger for `ao-ledger` + author `ao-ledger-core.service` — OPERATOR APPROVAL REQUIRED.** Linger creates a session that **survives logout**; that is an access-control change to a service identity. I did neither. Not key material, so it is a different kind of stop from LEDGER-01.
3. **LEDGER-01 key ceremony — open, operator-only.** No key generated, exported or activated.
4. **`cordadb` role password — open, operator-only.** Did not run `ALTER ROLE`. Role password state is *unverifiable* from the agent account; §19's "no working password" is carried forward, not confirmed.
5. **Producer-key coverage — 4 of 6 domains cannot sign.** `sign-manifest.sh` supports only `ao-sim-vehicle` and `ao-sim-fabrication`, yet **Sales produces `sales_receipt`**, the type §11.2.2's gates exist to protect. Credential work.
6. **20260824 staged manifest carries `producer_key_id: "test"`.** Must be treated as untrusted replay input, not auto-submitted when the gateway appears.
7. **`origin_domain` unvalidated** while `object_type` is — confirmed by contrast, not by absence.

## Traps

- `is-active` -> `inactive` for a **nonexistent** unit. Three sessions, same trap. Use `LoadState`.
- `/home/alwayson-ledger` returning `Permission denied` is **correct** (owned by `ao-ledger`). Not a missing account. Do not loosen the mode.
- `.gitignore:2` ignores `data/`, so `data/corda-install/` is **absent from every worktree**. Checksums must be run against `/ALWAYSON/data/`.
- `psql` as `scottw` -> `role "scottw" does not exist`. That is an *authentication* outcome, not a missing database.
- My first frontmatter validator regex rejected **all 7 proposals including the unmodified committed ones**. The bug was my regex, not the files; a YAML parse passes all 7. **Validate a tool against known-good input before believing its verdict.**

## Belongs to another group — reported, not touched

- **`docs/runbooks/ledger-bootstrap.md`** and **`logs/operations/2026-09-28-corda4-retirement.md`** both use `alwayson-ledger` as a username (uid 994 is `ao-ledger`). Neither is my file. My read on the retirement log: annotate, do not rewrite — it is a historical journal.
- **Building `ao-egress-archive`** (Quadlet) blocks LEDGER-04 and belongs to whoever owns `quadlet/` — plausibly NET (05-network-domains), who already flag it as requiring implementation.
- **`scripts/ledger/sign-manifest.sh` and `build-manifest.sh`** — fixes for findings 5 and 7 are one-line `case` additions, but `scripts/` is not my file. These are cheap and unblocked; someone should take them.

## What I got wrong

I set out to re-verify inherited claims, found nothing new, and nearly reported "no change". The reason: I grepped the runbook for `alwayson-ledger` — the token I already knew was wrong — reproduced the prior finding, and stopped. Reading the state block **field by field** is what surfaced both new assertions, one of which contradicts itself inside the same document. **Searching a document for the error you already know about cannot find the errors you don't.**

Editor misfires cost time three times: an em-dash mismatch silently matched a partial string and mangled a paragraph in `ledger-LEDGER-02.md`; an insertion in `ledger-LEDGER-06.md` was clobbered by a later edit; and the `insert_line` call that built this document split it at the wrong offset, duplicating six sections. All three were caught by reading the file back rather than trusting the diff preview. **After any editor call, read the file — and check that code fences balance and that no heading repeats, because a misplaced split looks like a formatting nit and silently duplicates or drops evidence.**

## Housekeeping

- No test files left behind: `/tmp/led-probe.*`, `/tmp/e3`, `/tmp/readme.before`, `/tmp/gh.json`, `/tmp/oldprop/`, `/tmp/p.fixed`, `/tmp/p2` all in `/tmp` only.
- `artifacts/pending-ledger-submissions/` **unchanged** — only the pre-existing `20260824` directory. Nothing signed, staged, or transmitted.
- `/ALWAYSON` tree has two modified files I did **not** create and did not touch: `artifacts/dashboard/index.html`, `artifacts/dashboard/metrics/19-progress.jsonl`.
- No operational journal written. My brief grants one file; `logs/operations/` is not it. Flagging rather than assuming.
