---
item: FIELD-05
action: reopen
evidence: |
  # *** I CLOSED THIS ITEM ON A FALSE PREMISE. IT MUST REOPEN. ***
  #
  # The closure rested on a count taken from a ROTATED log filename. It no longer reproduces
  # in any retained log, and the error text I quoted is absent everywhere:
  $ cd ~/.reticulum-meshchatx/logs
  $ for f in meshchatx.log.3 meshchatx.log.2 meshchatx.log.1 meshchatx.log; do
      echo "$f: umsgpack=$(grep -ac umsgpack $f)  'No module named'=$(grep -ac 'No module named' $f)"
    done
  meshchatx.log.3: umsgpack=0  'No module named'=0
  meshchatx.log.2: umsgpack=0  'No module named'=0
  meshchatx.log.1: umsgpack=0  'No module named'=0
  meshchatx.log:   umsgpack=0  'No module named'=0

  # THE PERSIST FAULT IS REAL AND STILL LIVE -- 4 occurrences in the CURRENT log, today:
  $ grep -ac 'Bounded ratchet persist failed' meshchatx.log
  4
  $ grep -a 'Bounded ratchet persist failed' meshchatx.log | tail -1
  ERROR:meshchatx.rns_ratchet_persist:Bounded ratchet persist failed: [Errno 9] Bad file descriptor
  # NOTE: [Errno 9] Bad file descriptor, NOT "No module named 'umsgpack'".
  # Per file, oldest first: .3=2  .2=13  .1=9  current=4

  # Every occurrence lands in the SAME SECOND as a DRONE-RADIO teardown:
  $ grep -an 'Bounded ratchet persist failed' meshchatx.log | cut -d: -f1
  8049
  12279
  16470
  19670
  $ sed -n '8047,8051p' meshchatx.log | cut -c1-150
  INFO:meshchatx.rns:[2026-10-05 03:15:33] [Error]    The interface RNodeInterface[DRONE-RADIO] experienced an unrecoverable error and is now offline.
  INFO:meshchatx.rns:[2026-10-05 03:15:33] [Error]    Reticulum will attempt to reconnect the interface periodically.
  ERROR:meshchatx.rns_ratchet_persist:Bounded ratchet persist failed: [Errno 9] Bad file descriptor
  INFO:meshchatx.rns:[2026-10-05 03:15:33] [Error]    Error while reconnecting port, the contained exception was: 'NoneType' object cannot be interpreted as an integer
  INFO:meshchatx.rns:[2026-10-05 03:15:38] [Notice]   Opening serial port /dev/serial/by-path/pci-0000:05:00.0-usb-0:1:1.0-port0...
  # identical shape at 04:59:53, 06:42:08, 07:59:53

  # The zero I cited on 2026-10-04 to withdraw the teardown hypothesis was a snapshot of a
  # LIVE log that has since grown -- not a miscount. Verified binary-safe both ways:
  $ echo "no-a: $(grep -c 'Bounded ratchet persist failed' meshchatx.log)  -a: $(grep -ac 'Bounded ratchet persist failed' meshchatx.log)"
  no-a: 4  -a: 4
section: 09-field-and-lora-architecture
---

**Supersedes:** this file revises the FIELD session's own earlier proposal of this path,
rewritten 2026-10-05 08:12 PDT. The earlier revision was never merged into §19.2, so the
compiler should take this version as the only FIELD proposal for this item.

**FIELD-05 must REOPEN, action `reopen`.** This is a correction of my own closure and is the most
important item in this handoff.

**What I got wrong.** I closed FIELD-05 on 2026-10-04 claiming 12,364 `umsgpack` errors were
confined to one rotated log and were therefore a historical packaging defect. **That count
reproduces in no file today**, and the string `No module named 'umsgpack'` I quoted as evidence
appears in **no retained log at all**. Reason: the count came from a *rotated filename*, and
rotation has since overwritten the segment. The tell was in front of me — the count lived in
`meshchatx.log.2` in one pass and `meshchatx.log.3` in the next, which I recorded as a
correction and then kept trusting anyway. **A count that moves when you rename the file is not
measuring the fault.**

**The fault is real and still happening.** `Bounded ratchet persist failed` occurs **4 times in
the current log today**, error `[Errno 9] Bad file descriptor`. On 2026-10-04 I saw this second
error and wrote it off as "a different bug, not covered by closing FIELD-05" — which left a
daily-failing persistence subsystem with no open item against it. That was the wrong call.

**Strong new correlation, and it may be the most useful thing here.** All 4 of today's
occurrences land in the **same second** as a `DRONE-RADIO` teardown, immediately before the
reconnect that reopens the port — 03:15:33, 04:59:53, 06:42:08, 07:59:53. `[Errno 9] Bad file
descriptor` on a persist write during an interface teardown is consistent with the ratchet state
file's descriptor being closed as a side effect of the `DRONE-RADIO` reset.

**Honesty about the earlier withdrawal.** On 2026-10-04 I withdrew this exact hypothesis because
the current log then showed 994 teardowns and 0 persist failures. That was a correct reading *of
that moment* — the current log is still being appended to, and it now holds 4. So the withdrawal
was sound and is now superseded, rather than having been a mistake. I checked whether the
discrepancy was a `grep` binary-file artefact (these logs do report `binary file matches`) and it
is not: `grep -c` and `grep -ac` both return 4.

**Not proven.** I have not traced the code path and no stack trace is logged, so treat
"the board teardown closes the ratchet fd" as the leading hypothesis with the evidence above,
not a diagnosis.

**Why it matters beyond this item:** if the cause is shared, this is **not an independent
problem** — one `DRONE-RADIO` board repair may clear both this and FIELD-01/02/03/06, which are
all blocked on that same board.

**Nothing was changed.** Read-only. No service, file or radio touched.
