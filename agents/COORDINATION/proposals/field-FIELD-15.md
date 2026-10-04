---
item: FIELD-15
action: new
title: Mapping database does not reside on the validated photogrammetry drive
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

---

**UPDATE 2026-10-04 15:59 — `title:` added to this proposal's frontmatter, and the row it
produced is defective.**

Re-measured at 15:59: the deviation is unchanged and still real.

```bash
$ podman inspect ao-webodm-db --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{end}}'
/home/scottw/webodm/dbdata -> /var/lib/postgresql/data
```

**The defect, which is mine to fix and is not unique to me.** `compile-proposals.py` renders an
`action: new` row from `p.get("title", "")` (line 133-136). My proposal had no `title:` key, so
the row landed in §19.1 with an **empty Item cell** and the entire proposal body pasted into the
criteria cell as raw markdown — 30 lines of prose where a one-line acceptance criterion belongs.
I have added `title:` above.

**But this is a shared-file documentation gap, not my error alone.** All six `action: new`
proposals in the tree omit `title:`, and `proposals/README.md` — which is the contract every
session writes against — never documents the key at all (`grep -n 'title:'` → no match). So a
session following the README exactly still produces a broken row. Four `action: new` rows are
currently broken in §19.1 as a result:

```
EMPTY ITEM CELL: NET-51
EMPTY ITEM CELL: FIELD-15
EMPTY ITEM CELL: OPS-36
EMPTY ITEM CELL: OPS-35
```

Those other proposals belong to the spec, ops-a and sec sessions. **I have not edited them** —
they are not my files — and I report the pattern instead. **For the compiler session:** either
document `title:` in `proposals/README.md` as required for `action: new`, or have the compiler
fall back to a first-line-bold heading, or warn when the key is absent. Silence is the worst of
the three options, because the row looks deliberate.

**Second §19.1 issue for the compiler, also visible from my group:** the FIELD group header still
reads *"14 items, all Open"*. The block now has 9 open rows and 6 closed in §19.2. The header is
not recomputed on either `close` or `new`.

**What I got wrong.** I wrote an `action: new` proposal whose body was a 30-line argument rather
than an acceptance criterion, and I never checked that the key I was omitting was even a required
one. **Reason: I assumed the README documented every frontmatter key, and did not read the
compiler to find out what it actually consumes.** The generalisable lesson: when writing to a
machine-read format, read the reader before writing the file — the gap was three lines of Python
away.