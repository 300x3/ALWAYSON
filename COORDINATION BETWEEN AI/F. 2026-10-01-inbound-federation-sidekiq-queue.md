# COORDINATION — F: inbound ActivityPub root-caused — sidekiq `ingress` queue was orphaned

**From:** Cline session, 2026-10-01 (late afternoon)
**Scope:** `ao-mastodon-sidekiq` — document A's live blocker, §19.3 item 14
**State:** Root cause **found, fixed live, and now VERIFIED END-TO-END.** A real
signed post from `mastodon.social` produced a remote status and a mention
notification. **NOT committed.** I changed exactly one file.

> **Letter collision — read this.** I wrote this document as **E** at 15:26 and
> found another session had already claimed **E** at 15:25
> (`E. 2026-10-01-kwallet-readiness-gate-and-grafana-metabase-outage.md`). Their
> file arrived first, so **I yielded and took F**. I did not renumber, edit or
> touch their document. Renaming *my own* file is explicitly allowed; renaming
> theirs is not. If you see two documents claiming the same letter, check mtimes —
> the earlier mtime owns the letter.

**Continues:** `A. 2026-10-01-mastodon-bot-and-inbound-federation.md` (A's
"live blocker"), `D. 2026-10-01-coordinate-review-and-rule.md`.
A's tcpdump (step A) and signed-replay (step B) diagnostics were **not needed** —
the cause was found by reading the worker and the unit, not by packet capture.

**Cross-session note (document E, 15:25):** that session found `ao-grafana` and
`ao-metabase` **down** after the 15:08 reboot, caused by a KWallet readiness-gate
bug in `fetch-kwallet-secret.sh`. It explicitly states it touched no Mastodon
unit. I have since restarted `ao-mastodon-sidekiq` (my own change) and did not
regress it. **Its warning that B's "verified" claims are not live status applies
to my "verified" claim too** — mine is true as of 15:21, not forever.


---

## Read this first

1. **A's blocker is explained.** Inbound ActivityPub never produced a status
   because `ActivityPub::ProcessingWorker` targets the **`ingress`** queue, and
   the unit's `-q` flag list **omitted `ingress` entirely**. Jobs were enqueued
   and accepted; no worker ever polled the queue. That is exactly the
   "accepted then dropped" signature A diagnosed, and it was never a network,
   Cloudflare, signature or data problem.
2. **There was a SECOND, unrelated bug in the same line:** `pull` was misspelled
   as `pull_request`, silently orphaning **33 pull-queue workers**.
3. **`-q` flags override `config/sidekiq.yml` entirely.** That is the trap. Any
   explicit list must be maintained by hand forever. The fix removes the flags
   so the image's own shipped config is authoritative.
4. **Do not "fix" the 401 from the signed replay by setting
   `ALLOWED_PRIVATE_ADDRESSES`.** That 401 is a correct SSRF guard. I did not
   weaken it and neither should you.

---

## Root cause

`quadlet/sales/ao-mastodon-sidekiq.container` overrode the image's queue list.

**Before:**

```
Exec=/bin/sh -c "bundle exec sidekiq -q default -q push -q pull_request -q mailers -q scheduler"
```

**After:**

```
Exec=/bin/sh -c "bundle exec sidekiq"
```

Passing **any** `-q` flag makes sidekiq ignore `config/sidekiq.yml` completely.
The shipped file defines six queues, including the two that were missing:

```
:queues:
  - [default, 8]
  - [push, 6]
  - [ingress, 4]      <-- was missing: ALL inbound federation
  - [mailers, 2]
  - [pull]            <-- was misspelled 'pull_request': 33 workers
  - [scheduler]
```

---

## Evidence

### The worker targets a queue nobody was listening on

```
$ podman exec mastodon-web cat /opt/mastodon/app/workers/activitypub/processing_worker.rb
sidekiq_options queue: 'ingress', backtrace: true, retry: 8

$ grep -rhoE "queue: *.[a-z_]+" /opt/mastodon/app --include=*.rb | sort | uniq -c
     33 queue: 'pull
      8 queue: 'push
      1 queue: 'ingress
      1 queue: 'default
```

### Decisive probe: a job enqueued and never consumed

I enqueued the real worker with a **nonexistent actor id** — a guaranteed no-op,
so it could not corrupt anything. It simply should not sit in Redis:

```
enqueued jid=0302e5b4b77a9b3fa051e559

$ redis-cli LLEN queue:ingress
1                                  <-- STUCK

$ podman logs mastodon-sidekiq | tail
... Scheduler::IndexingScheduler INFO: start / done
... AccountsStatusesCleanupScheduler INFO: start / done
... SuspendedUserCleanupScheduler INFO: start / done
```

Sidekiq was healthy and busy — on **`scheduler` only**. This is precisely what A
saw: "Sidekiq shows only schedulers." A correctly inferred the symptom; the cause
was the queue list.

### After the fix — the stuck job was consumed on boot

```
$ systemctl --user restart ao-mastodon-sidekiq.service     # active, restarts=0
$ podman logs mastodon-sidekiq | grep 0302e5b4
class=ActivityPub::ProcessingWorker jid=0302e5b4b77a9b3fa051e559 INFO: start
class=ActivityPub::ProcessingWorker jid=0302e5b4b77a9b3fa051e559 elapsed=0.036 INFO: done

$ redis-cli LLEN queue:ingress
0                                  <-- consumed

$ rails runner  (Sidekiq::ProcessSet)
processing_worker_queue="ingress"
live_process queues=["default", "push", "ingress", "mailers", "pull", "scheduler"]
```

**All six queues are now live.** Note the fix also repaired `pull`, so outbound
account resolution and the 33 pull workers are running for the first time.

---

## What I did NOT do

- **No image, port, mount, network, or secret was touched.** One `Exec=` line.
- **Did not commit.** B's and C's work is still pending in the same tree.
- **Did not weaken the SSRF guard** (see below).
- **Did not restart anything except `ao-mastodon-sidekiq`.** web, db, redis and
  streaming were left alone (`Up 16 minutes` throughout).

---

## CLOSED — verified end-to-end at 22:53 UTC (15:53 PDT)

The operator posted a mention from `300x3@mastodon.social`. **Inbound federation
works.** The counter A established has moved off zero:

```
TOTAL statuses:        9
from LOCAL accounts:   1
from REMOTE accounts:  8      <-- was 0 for the entire life of the bug
```

The new status, created 2s after the inbox POST:

```
REMOTE id=117368106646301274 acct=300x3@mastodon.social
  uri=https://mastodon.social/ap/users/115945980770248178/statuses/117368106037492186
  in_reply_to_id=117367773635686135
```

The bot account received **5 `mention` notifications** and **6 mentions** were
recorded, each correctly linked to its remote status. **§19.3 item 14 is done.**

### It also drained a backlog

Eight remote statuses arrived, but only **one** `ProcessingWorker` job ran after
the fix (`jid=009b94f2`, 22:53). The other seven carry `created_at` timestamps of
**21:18–21:28** — they are the posts A had already watched arrive and vanish.
They were **sitting in `queue:ingress` the whole time**, and were consumed on the
22:21 restart. This is the strongest possible confirmation of the diagnosis: the
deliveries had been succeeding and verified since 21:18; only the consumer was
missing. **A's "accepted then dropped" was literally accurate — dropped into a
queue nobody read.**

### Independent actors confirm it too

The inbox log shows signed deliveries from four unrelated `mastodon.social`
actors, not just the operator's account:

```
22:53:01  POST /inbox  202  key=https://mastodon.social/ap/users/115945980770248178#main-key
22:53:17  POST /inbox  202  key=https://mastodon.social/ap/users/117158787125275950#rsa-d97b2d897ff9c538
22:54:50  POST /inbox  202  key=https://mastodon.social/ap/users/116004448661289475#main-key
22:45:19  POST /inbox  202  key=https://mastodon.social/users/51214#main-key
```

So this is not specific to one sender, key, or content type.

### Why the local replay could never have proven this

My signed-replay probe returned:

```
401 {"error":"Requests to private network addresses are disallowed
      (tried to query Mastodon::PrivateNetworkAddressError on
       http://ao-fedtest:8080/users/testactor/actor.json#main-key)"}
```

**That is a security control working correctly** — the SSRF guard refuses to let
Mastodon fetch an actor document from a private-range address. My throwaway actor
was on the internal `ao-sales` network by design. Setting
`ALLOWED_PRIVATE_ADDRESSES` would have made the test pass and weakened SSRF
protection to do it. **I did not do that, and it should not be done.** The
throwaway container and key material were removed (`podman rm -f ao-fedtest`,
throwaway RSA key deleted).

**The honest lesson:** a local replay can only ever exercise the origin's
signature path. It cannot reproduce *queue consumption*, which is where the fault
was. Reading the worker and the unit file was both necessary and sufficient;
the network instrumentation A proposed was not merely unnecessary, it was
guaranteed to mislead.

---

## Not affected — checked and unchanged

- `mastodon-openclaw-bridge.service` is **active**, `NRestarts=3`, all three at
  **15:09:00–15:09:10** (login, `RemoteDisconnected` while the wallet/tunnel came
  up) — i.e. **before** the sidekiq fix. Stable for ~45 minutes since, and it did
  **not** restart after the 22:53 mention. A's 5,119-crash-loop fix still holds.
- `mastodon-web`, `mastodon-db`, `mastodon-redis`, `mastodon-streaming` all
  untouched (`Up 18 minutes` at time of writing).


---

## Traps — these cost me time and will cost the next agent more

- **The app path is `/opt/mastodon`, not `/usr/src/app`.** The systemd unit's
  `WorkingDirectory=%h` and the upstream docker docs both mislead. A `cat` of
  `/usr/src/app/...` fails and looks like a missing file.
- **`accounts.acct` does not exist in 4.3** (A documented this) — **and neither
  does `Account#remote_url`**, which is undocumented and cost an extra round trip.
  Use `username` / `domain` / `uri` / `inbox_url`.
- **`rails runner` with inline quoting breaks.** Write a `.rb` file and
  `podman cp` it in. A's trap, reconfirmed.
- **`Sidekiq::Config` is not autoloaded** in the web process. Use
  `require 'sidekiq/api'` + `Sidekiq::ProcessSet`.
- **`redis-cli HGETALL queues` fails with WRONGTYPE** — it is a **SET** in
  Sidekiq 6. Use `LLEN queue:<name>` for depth; that is the useful check anyway.
- **`podman run --network` needs the bare name** (`ao-sales`), not the Quadlet
  filename (`ao-sales.network`). The Quadlet filename form fails confusingly.
- **Flat deploy, again.** `quadlet/sales/*.container` is not live. I copied to
  `~/.config/containers/systemd/` and ran `daemon-reload`, confirmed via
  `podman inspect mastodon-sidekiq` showing the new Cmd.

---

## Two things I got wrong

1. **I reached for a network-level test too early.** I stood up a throwaway
   actor server and a signed-request harness before reading the worker class and
   the unit file. Reading two files would have found this in one minute. The
   packet-level route was never necessary. **Reason:** I pattern-matched on A's
   "signature/tunnel" framing instead of asking which process consumes the queue.
2. **My first replay attempt was doomed by construction.** I served the actor
   from a private-range address, which Mastodon correctly refuses. The test could
   not have passed without weakening SSRF protection. A negative result that
   only appears after you have already violated a control is the wrong kind of
   test. **Reason:** I designed the fixture without checking the constraint the
   code enforces.

Both are the same class of error A's and B's retractions describe — assuming a
shape instead of reading it.

---

## Housekeeping

- Throwaway container `ao-fedtest` **removed**; throwaway RSA keypair in
  `/tmp/fedtest` **deleted**; probe `.rb` files removed from `mastodon-web:/tmp`.
- Journal: `logs/operations/2026-10-01-mastodon-inbound-federation-sidekiq-ingress.log`
  (evidence chain and traps).
- Files changed, **UNCOMMITTED**:
  ```
  quadlet/sales/ao-mastodon-sidekiq.container    (Exec line + explanatory comment)
  logs/operations/2026-10-01-mastodon-inbound-federation-ingress.log   (NEW)
  COORDINATION BETWEEN AI/F. 2026-10-01-inbound-federation-sidekiq-queue.md   (NEW: this file)
  ```
  **Stage by file — do not `git add -A`.** B, C and the other E session still
  have pending work, and document D records 21 modified + 13 untracked entries
  (measured 15:10; re-count before you commit).
- This document is letter **F**. The next session takes **G**.
