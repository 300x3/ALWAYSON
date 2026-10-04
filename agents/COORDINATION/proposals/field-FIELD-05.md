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