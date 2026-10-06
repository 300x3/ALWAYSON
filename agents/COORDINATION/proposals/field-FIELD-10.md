---
item: FIELD-10
action: update
evidence: |
  # THE TREE HAS CHANGED SINCE THE LAST PASS -- sections 8.5.1/8.5.3 are partly stale.
  # 10 of the 18 specified directories are missing, and ALL TEN are second level.
  $ M=/media/scottw/500GBPHOTOGRAM
  $ for d in incoming/drone incoming/operator incoming/quarantine \
             manifests/intake manifests/processing manifests/ledger-submissions \
             exports/pcloud-staging exports/ipfs-staging backups/mapping-db tmp/processing; do
      printf '%-30s ' $d
      if mkdir $M/$d 2>/dev/null; then echo MKDIR-OK; rmdir $M/$d; else echo MKDIR-DENIED; fi
  done
  incoming/drone                   MKDIR-DENIED
  incoming/operator                MKDIR-DENIED
  incoming/quarantine               MKDIR-DENIED
  manifests/intake                 MKDIR-DENIED
  manifests/processing             MKDIR-DENIED
  manifests/ledger-submissions     MKDIR-DENIED
  exports/pcloud-staging           MKDIR-DENIED
  exports/ipfs-staging             MKDIR-DENIED
  backups/mapping-db               MKDIR-DENIED
  tmp/processing                   MKDIR-DENIED

  # CONTROL: the same command SUCCEEDS under the parents the operator owns.
  $ mkdir $M/webodm/projects/__fieldtest && rmdir $M/webodm/projects/__fieldtest
  (exit 0 -- created and removed)

  # The cause, enumerated rather than inferred:
  $ getent group alwayson-mapping ao-mapping
  alwayson-mapping:x:975:                       <-- NO MEMBERS
  ao-mapping:x:1001:scottw,ao-mapping           <-- operator IS here
  $ stat -c '%n owner=%U group=%G mode=%a' $M/incoming $M/webodm $M/retention
  /media/.../incoming   owner=ao-mapping group=alwayson-mapping mode=770
  /media/.../webodm     owner=scottw     group=ao-mapping        mode=770
  /media/.../retention  owner=scottw     group=scottw            mode=770

  # The mount validator PASSES and must not be quoted as evidence for this item --
  # it validates the mount, never the tree.
  $ bash scripts/validation/check-photogrammetry-mount.sh
  OK: photogrammetry mount valid: systemd-1
  /dev/sdb1; 434G free
  rc=0

  # One spec clause DOES hold: nothing is world-writable.
  $ find $M -maxdepth 2 -type d -perm -0002 | head
  (no output)
section: 08-mapping-and-photogrammetry
---

**Supersedes:** this file revises the FIELD session's own earlier proposal of this path,
rewritten 2026-10-05 08:12 PDT. The earlier revision was never merged into §19.2, so the
compiler should take this version as the only FIELD proposal for this item.

**FIELD-10 stays OPEN, action `update`.** New subsection **§8.5.5** records the measurement.

The headline the compiler should not miss: **the gap is now quantified, and it is exactly the
second level of the tree.** `webodm/{media,projects,nodeodm,temp,logs}` and
`retention/{pending-review,eligible-for-archive}` now exist; the ten directories still missing are
all second-level under parents owned `ao-mapping:alwayson-mapping` mode `770`. Group
`alwayson-mapping` (gid 975) has **no members at all**, so the operator is neither owner nor
group for those parents. Measured by attempting creation, ten times, ten `MKDIR-DENIED` — with a
control under `webodm/` that succeeds, proving the cause is ownership and not a broken mount.

**Two corrections for the compiler, both about over-reading:**

1. **Do not render §8.2's "the tree does not match this specification" as meaning nothing was
   created.** Directories were modified `Oct 4 17:30`, after the last pass. §8.5.1 and §8.5.3
   are partly stale on the *size* of the gap; they are not stale on its existence.
2. **A green `check-photogrammetry-mount.sh` is not evidence for FIELD-10.** It returns `rc=0`
   while the tree it is nominally guarding fails, because it validates the mount and never
   inspects the directory list. Quoting it as validation of this item would be wrong.

**The repair is two ordered steps and the first is privileged:** `usermod -aG alwayson-mapping
scottw`, then the ten `mkdir`s. `sudo -n true` returns "interactive authentication is required",
so this session could not perform either and did not try to force it.

**What I got wrong.** I reached for a `touch` probe inside `incoming/` to prove write denial
more directly. It returned `setting times: Permission denied` — and then I could not `stat`, `ls`
or `rm` the path, because the directory is unreadable to me. **A possible zero-byte
`/media/scottw/500GBPHOTOGRAM/incoming/.fieldprobe` may still exist.** I am flagging it rather
than claiming it is gone, because I cannot prove either way. The `mkdir` probes above were
create-then-delete attempts that were all refused, so they left nothing.
