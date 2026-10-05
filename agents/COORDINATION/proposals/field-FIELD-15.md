---
item: FIELD-15
action: new
evidence: |
  # The deviation is real: the mapping database is NOT on the photogrammetry drive
  $ podman inspect ao-webodm-db --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{end}}'
  /home/scottw/webodm/dbdata -> /var/lib/postgresql/data
                                 # root filesystem, not /media/scottw/500GBPHOTOGRAM

  # ...and the drive is not writable by the operator in its intended ownership arrangement
  $ stat -c '%n owner=%U group=%G mode=%a' /media/scottw/500GBPHOTOGRAM/tmp
  /media/scottw/500GBPHOTOGRAM/tmp owner=ao-mapping group=alwayson-mapping mode=770
  $ getent group alwayson-mapping
  alwayson-mapping:x:975:          # no members
  $ id -nG scottw | tr ' ' '\n' | grep -xE '1001|975'
  1001                              # ao-mapping only; 975 absent
  $ mkdir /media/scottw/500GBPHOTOGRAM/tmp/processing
  mkdir: Permission denied
  $ sg ao-mapping -c "mkdir -p /media/scottw/500GBPHOTOGRAM/tmp/processing"
  mkdir: Permission denied
section: 08-mapping-and-photogrammetry
---
New item, next free number in the FIELD group (FIELD-01..FIELD-14 are all taken; no renumbering).

**Title: mapping database does not reside on the validated photogrammetry drive.**

§8.4.1 closes FIELD-11 on the *name and location* question and explicitly declines to close the
drive-residency half, promising to "carry it forward as a new FIELD item rather than reopening
FIELD-11". That promise had no corresponding item in §19 — it was recorded only as prose in
§8.4.1, where nothing tracks it. This proposal is that item.

**Why it needs its own ID rather than living inside FIELD-10.** FIELD-10 is about the *directory
tree* and ownership of the drive. This is about *where a database's data directory sits*. They
are adjacent but distinct, and the fix for one does not fix the other: FIELD-10 is repaired by
`usermod -aG alwayson-mapping scottw` plus `mkdir`, and this item would still be open
afterwards, because the PostgreSQL data directory stays on the root filesystem regardless.

**The ordering constraint is new and worth the operator knowing.** §8.5.2 measured today shows
the drive is group-owned by `alwayson-mapping` and the operator is not in that group, so `mkdir`
fails even on paths §8.2 already requires. **Any decision to relocate PostgreSQL storage onto
this drive must fix that ownership first**, or the database lands on a volume that its own
operator cannot create, back up or inspect. The relocation is therefore not a single decision
but two, in this order: group membership, then data-directory move.

**Not attempted.** Moving a live PostgreSQL data directory changes service configuration and is
an operator decision under §4.1 rule 12. Nothing was created, moved or chgrp'd on the drive or
in `~/webodm/dbdata`.