---
item: FIELD-10
action: update
evidence: |
  # THE TREE HAS CHANGED SINCE THE LAST PASS -- sections 8.5.1/8.5.3 are partly stale.
  # 10 of the 18 fixed sub-tree directories are still missing: the top level is now
  # operator-writable (scottw:ao-mapping 2770), but 8 parents remain
  # ao-mapping:alwayson-mapping mode 770 and their 10 depth-2 children are absent.
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

  # The mount validator is now tree-aware and reports RED on the current state:
  # exit 25 when the required tree directories are missing, exit 26 for the mapping-
  # service ownership/permissions gap. It is NOT green evidence for FIELD-10.
  $ bash scripts/validation/check-photogrammetry-mount.sh 2>&1 | head -1
  ERROR: required photogrammetry tree directories are missing: incoming/drone
  $ bash scripts/validation/check-photogrammetry-mount.sh >/dev/null 2>&1; echo $?
  25

  # One spec clause still holds: nothing is world-writable.
  $ find $M -maxdepth 2 -type d -perm -0002 | head
  (no output)
section: 08-mapping-and-photogrammetry
---

**Supersedes:** this file revises the FIELD session's own earlier proposal of this path,
rewritten 2026-10-16. The earlier revision was never merged into §19.2, so this version is the
only FIELD proposal for this item.

**FIELD-10 is resolved at the validation layer; tree remediation is an operator action.** The
§8.5 refusal conditions are now enforced by `check-photogrammetry-mount.sh` (exit 25 on the current
state, exit 26 for the ownership/permissions gap), and the depth-2 measurement is recorded above.
Closing the item still requires the operator's `usermod -aG alwayson-mapping scottw` plus the ten
`mkdir`s.

The headline the compiler should not miss: **the tree gap has narrowed but is not closed.** Top
level is now operator-writable (`scottw:ao-mapping` mode `2770`) and `webodm/{media,projects,
nodeodm,temp,logs}` plus `retention/{pending-review,eligible-for-archive}` exist. But the 10
depth-2 directories are still missing, and the 8 parents they sit under are
`ao-mapping:alwayson-mapping` mode `770` whose group (alwayson-mapping, gid 975) has **no members
at all**, so scottw is neither owner nor group for those parents. Measured by attempting creation,
ten times, ten `MKDIR-DENIED` — with a control under `webodm/` that succeeds, proving the cause is
ownership and not a broken mount.

**Two corrections for the compiler, both about over-reading:**

1. **Do not render §8.2's "the tree does not match this specification" as meaning nothing was
   created.** Directories were modified `Oct 4 17:30`, after the last pass. §8.5.1 and §8.5.3
   are partly stale on the *size* of the gap; they are not stale on its existence.
2. **A green `check-photogrammetry-mount.sh` is not evidence for FIELD-10.** It now reports a real
   failure (exit 25) while the tree it is nominally guarding fails, because the tree is absent/
   not writable for the mapping service. Quoting it as validation of this item would be wrong.

**The repair is an operator action, not a script change.** The operator must run
`sudo usermod -aG alwayson-mapping scottw` (then re-login) so that scottw becomes a member of
`alwayson-mapping`; with that membership the 8 parents are writable and the ten depth-2 directories
can be created. The validator above reports exit 25 for the missing paths and exit 26 for the
ownership/permissions gap, so the exact remediation set is confirmed before it is applied.

**Operator note.** The ten depth-2 probes failed for a second, distinct reason from the old pass:
the directories do not exist at all. They sit under parents (`incoming`, `manifests`, `exports`,
`backups`, `tmp`) whose group `alwayson-mapping` has no members, so scottw is denied at the parent
before it can create a child. Creating the child therefore requires the parent group to grant
write, or root to create the child with the correct group.
