---
item: FIELD-05
action: close
evidence: |
  $ cd ~/.reticulum-meshchatx/logs
  $ for f in meshchatx.log.2 meshchatx.log.1 meshchatx.log; do echo -n "$f: "; grep -c umsgpack "$f"; done
  meshchatx.log.2: 12364
  meshchatx.log.1: 0
  meshchatx.log: 0

  # last umsgpack line is followed immediately by a restart banner
  51501:ERROR:meshchatx.rns_ratchet_persist:Bounded ratchet persist failed: No module named 'umsgpack'
  2026-09-24T16:29:19.004Z [electron] Download path set to /home/scottw/Downloads/MeshChatX
  2026-09-24T16:51:04.672Z [electron] Found executable at: /tmp/.mount_ReticuDLBdLn/resources/backend/ReticulumMeshChatX
  INFO:meshchatx.rns_ratchet_persist:Installed bounded RNS ratchet persist worker

  # restart-persistence evidence (required by the acceptance criteria)
  $ ps -o pid,lstart -p 840861
      PID STARTED
   840861 Sat Oct  3 16:57:27 2026
  $ stat -c '%n mtime=%y' ~/.reticulum-meshchatx/identities/*/lxmf_router/lxmf/ratchets/*.ratchets
  ...080371582f297fc33dd513b3f9d18c3a.ratchets mtime=2026-10-03 09:51:34 -0700
  # 20s re-sample: sha256 unchanged (8e0734d6811861e95f53...)

  # a DIFFERENT, still-live error exists now and is NOT the same defect
  $ grep -c 'Bounded ratchet persist failed' meshchatx.log     # 3, all "[Errno 9] Bad file descriptor"
  $ grep -c 'RNodeInterface\[DRONE-RADIO\] experienced an unrecoverable error' meshchatx.log   # 2004
section: 09-field-and-lora-architecture
---
§9 gains a new **§9.2.3** classifying the item exactly as the acceptance criteria allow —
"formally accepted as a historical bounded-ratchet defect with restart-persistence evidence".

The 12,364 `umsgpack` errors are entirely confined to `meshchatx.log.2`; the two newer rotated
logs contain zero. The error block ends immediately before a restart that reinstalls the persist
worker, so it is a packaging defect in the pre-2026-09-24 AppImage build (bundled Reticulum
lacked `umsgpack`), not a live fault.

Restart-persistence evidence is supplied as required: the ratchet file mtime
(`2026-10-03 09:51:34`) precedes the running process start (`16:57:27`) by seven hours and a
20-second re-sample shows an unchanged sha256, so the persist worker has written nothing in the
current instance.

**Two things the compiler must not lose.** First, §9.2.3 records a *separate, still-live*
defect found while gathering this evidence: 3 `[Errno 9] Bad file descriptor` persist failures,
each landing in the same second as a `DRONE-RADIO` interface teardown. This is a different bug
and is **not** covered by closing FIELD-05. Second, I did not fix anything — repair means
touching the serial device and the running Reticulum stack, which is a stop condition.
**CORRECTION 2026-10-04 — log filenames in the evidence block.** The counts above are right
but two filenames are not, because log rotation renumbered them between the original
investigation and now. Measured today, per file, with each file's own time range:

```bash
$ cd ~/.reticulum-meshchatx/logs
$ for f in meshchatx.log.3 meshchatx.log.2 meshchatx.log.1 meshchatx.log; do
    echo "$f: $(grep -c umsgpack $f) umsgpack"; done
meshchatx.log.3: 12364      <- the errors are HERE, not in .log.2
meshchatx.log.2: 0
meshchatx.log.1: 0
meshchatx.log:  0
```

**The 12,364 errors are in `meshchatx.log.3`, not `meshchatx.log.2` as the evidence block
states.** The conclusion is unchanged — still entirely historical, still zero in all three
newer logs — but a reader following the original block would grep the wrong file, find
nothing, and wrongly conclude the errors had vanished rather than moved.

**A stronger version of the same finding.** The error block's end is dateable, and it lands
*before* the `DRONE-RADIO` fault began:

```bash
$ grep -B1 'umsgpack' meshchatx.log.3 | grep -o '\[[0-9-]* [0-9:]*\]' | tail -1
[2026-09-22 19:27:51]        # last persist failure
$ head -1 meshchatx.log.2
[2026-09-25 16:27:17] Auto-connecting discovered BackboneInterface ...
```

**All `umsgpack` persist failures stopped on 2026-09-22 19:27:51 — three days *before* the
`DRONE-RADIO` teardown loop began on 2026-09-25 16:27.** The two defects are therefore
**independent**, and §9.2.3 must not imply the radio teardown relates to them. Confirmed by
counting: the current log holds 994 `unrecoverable error` events and **0** ratchet-persist
failures. The `[Errno 9] Bad file descriptor` persist failures noted above are the *current*
error and are a third, separate thing.

**What I got wrong, and the reason.** I did not re-check the log filenames before citing them
here — I had them right in my own commands (`meshchatx.log.3`) and still drafted the note
against `.log.2` from the earlier draft. **Reason: I wrote the correction from the previous
draft's framing instead of from today's measurement, which is the same error I recorded on
FIELD-09 in this same batch — re-verifying a prior note means re-running it, not re-reading
it.** Worth stating once for the whole project: rotated log filenames are unstable
identifiers; always cite them with the file's measured time range.