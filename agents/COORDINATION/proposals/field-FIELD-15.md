---
item: FIELD-15
action: update
evidence: |
  # The deviation is unchanged: the mapping database is NOT on the photogrammetry drive.
  $ podman inspect ao-webodm-db --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{end}}'
  /home/scottw/webodm/dbdata -> /var/lib/postgresql/data
                                 # root filesystem, not /media/scottw/500GBPHOTOGRAM

  # What is NEW this pass: the precondition is now a MEASURED, QUANTIFIED gate rather
  # than a caution. The drive is not a place the operator can manage.
  $ getent group alwayson-mapping ao-mapping
  alwayson-mapping:x:975:                       <-- NO MEMBERS
  ao-mapping:x:1001:scottw,ao-mapping

  # 8 of the 10 top-level directories are inaccessible to the operator:
  $ M=/media/scottw/500GBPHOTOGRAM
  $ for d in incoming validated rejected deliverables manifests exports backups tmp webodm retention; do
      printf '%-14s ' $d; [ -r $M/$d ] && [ -x $M/$d ] && echo accessible || echo DENIED; done
  incoming       DENIED
  validated      DENIED
  rejected       DENIED
  deliverables   DENIED
  manifests      DENIED
  exports        DENIED
  backups        DENIED
  tmp            DENIED
  webodm         accessible
  retention      accessible

  # Why: every DENIED parent is owned by a group the operator is not in, mode 770, other=---:
  $ stat -c '%n owner=%U group=%G mode=%a' $M/incoming $M/tmp $M/webodm $M/retention
  /media/.../incoming  owner=ao-mapping group=alwayson-mapping mode=770
  /media/.../tmp       owner=ao-mapping group=alwayson-mapping mode=770
  /media/.../webodm    owner=scottw     group=ao-mapping        mode=770
  /media/.../retention owner=scottw     group=scottw            mode=770

  # And the fix is privileged, which is why this session could not perform it:
  $ sudo -n true
  sudo: interactive authentication is required
section: 08-mapping-and-photogrammetry
---

**Supersedes:** this file revises the FIELD session's own earlier proposal of this path,
rewritten 2026-10-05 08:12 PDT. The earlier revision was never merged into §19.2, so the
compiler should take this version as the only FIELD proposal for this item.

**FIELD-15 stays OPEN, action `update`.** New subsection **§8.5.5** supplies the measured gate
this item was waiting on.

The item's own proposal said the relocation "is therefore not a single decision but two, in this
order: group membership, then data-directory move". That ordering claim is now **backed by
enumeration rather than inference**: 8 of the 10 top-level directories on the drive are
inaccessible to the operator, and all 8 sit under parents owned `ao-mapping:alwayson-mapping`
mode `770` with `other=---`, while group `alwayson-mapping` has no members. Only `webodm/` and
`retention/` — the two the operator owns directly — are reachable.

**So the answer to FIELD-15's precondition question is measured, not argued: the drive cannot yet
accept storage whose operator cannot inspect it.** Moving the PostgreSQL data directory onto this
volume today would turn a documented, recoverable deviation into one where the database exists
somewhere the operator can neither read, back up nor verify — and §8.4.1 already lists backup
scope as part of what this database's location governs.

**I did not move anything and did not attempt the group fix.** `sudo -n true` returns
"interactive authentication is required", so `usermod -aG alwayson-mapping scottw` is not
available to this session. I did not create, chgrp, move or delete any directory or file on the
drive, and I did not stop, restart or reconfigure `ao-webodm-db`.

**Housekeeping the operator must check, because I cannot prove it clean.** My write-denial probe
used `touch` inside `incoming/`, which returned `setting times: Permission denied`. I can neither
`stat` nor `rm` the resulting path, because the directory is unreadable to me. **Please check for
and remove `/media/scottw/500GBPHOTOGRAM/incoming/.fieldprobe`** — it may be a zero-byte file
left by my probe. I am flagging it rather than asserting it is gone. My `mkdir` probes elsewhere
on the drive were all refused by the kernel and left nothing.
