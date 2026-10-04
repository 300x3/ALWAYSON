---
item: FIELD-10
action: update
evidence: |
  # the shipped validator passes
  $ bash scripts/validation/check-photogrammetry-mount.sh
  OK: photogrammetry mount valid: systemd-1
  /dev/sdb1; 434G free
  rc=0

  # ...but the §8.2 tree it is supposed to guard does not exist
  $ M=/media/scottw/500GBPHOTOGRAM
  $ for d in incoming incoming/drone incoming/operator incoming/quarantine validated \
      rejected webodm webodm/media webodm/projects webodm/nodeodm webodm/temp \
      webodm/logs deliverables manifests manifests/intake manifests/processing \
      manifests/ledger-submissions exports exports/pcloud-staging exports/ipfs-staging \
      backups backups/mapping-db retention retention/pending-review \
      retention/eligible-for-archive tmp tmp/processing README.md .mounted-ok; do
      [ -e "$M/$d" ] && printf 'OK      %s\n' "$d" || printf 'MISSING %s\n' "$d"; done \
    | grep -c MISSING
  11
  MISSING incoming/drone
  MISSING incoming/operator
  MISSING incoming/quarantine
  MISSING manifests/intake
  MISSING manifests/processing
  MISSING manifests/ledger-submissions
  MISSING exports/pcloud-staging
  MISSING exports/ipfs-staging
  MISSING backups/mapping-db
  MISSING tmp/processing
  MISSING README.md

  # reserved paths correctly absent, sentinel present
  $ ls -la /ALWAYSON/data/mapping/postgres/ /ALWAYSON/data/mapping/redis/
  ls: cannot access '/ALWAYSON/data/mapping/postgres/': No such file or directory
  ls: cannot access '/ALWAYSON/data/mapping/redis/': No such file or directory
  $ ls -la /media/scottw/500GBPHOTOGRAM/.mounted-ok
  -rw-rw---- 1 scottw scottw 0 Aug 23 18:31 /media/scottw/500GBPHOTOGRAM/.mounted-ok

  # ownership/permission depth audit is PARTIAL, not clean
  $ M=/media/scottw/500GBPHOTOGRAM
  $ ok=0; no=0; for d in incoming validated rejected webodm deliverables manifests \
        exports backups retention tmp; do
      [ -r "$M/$d" ] && ok=$((ok+1)) || no=$((no+1)); done
  $ echo "readable=$ok unreadable=$no"
  readable=2 unreadable=8
section: 08-mapping-and-photogrammetry
---
**FIELD-10 stays OPEN, action `update`.** The validation has now been *run and it fails*, which
is further progress than the previous "unvalidated" state — but the item cannot close.

§8.5.1 now records the executed validation with the per-directory result. The decisive finding
for the compiler:

**The shipped validator passes on a drive that does not satisfy its own specification.**
`scripts/validation/check-photogrammetry-mount.sh` exits 0 (UUID match, mount marker, 434G
free) while **11 of the 32 required paths in §8.2 are missing**. The script never inspects the
directory tree at all, even though §8.5 lists "Required directories are missing" as a refusal
condition. Consequence for the README: **a green validator run is not evidence that §8.2
holds and must not be cited as such.** If any other session has quoted that green run as
storage validation, that citation is now known to be unsupported.

Of the four acceptance criteria: *tree* fails (11 missing); *sentinel* passes; *checks* pass
mechanically but do not cover the tree; *ownership* is confirmed at depth 1 (`ao-mapping` /
`alwayson-mapping`, mode `drwxrws---`, setgid set) but **unverified at depths 2-4**; and
"WebODM starts only with validated storage" is **unprovable here**, because the validator
cannot fail on a missing directory, so there is no enforced gate.

**I did not create the missing directories.** That would be a live storage change on the
photogrammetry drive — a stop condition, and the operator's call, not a documentation fix.
`backups/mapping-db` is the consequential one: it is where the §8.4.1 database dumps would land
on-drive. This does not put the database outside backup scope (`dump-all-postgres.sh:18` already
dumps `webodm_dev`), but there is currently no on-drive copy.

**What I got wrong, and the reason — read this one.** My first pass ran
`find "$M" -maxdepth 4 -type d -perm -0002`, saw empty output, and wrote "no directory is
world-writable". That was unsound: `find` *also* printed `Permission denied` for 8 of the 10
subtrees and exited 1. The empty result meant "none of the two readable subtrees", not "none on
the drive". **Reason: I read an empty result as a negative finding without reading the exit
status or the stderr.** I had to correct §8.5.1. The correction is in place in the section and
the ownership claim is now scoped honestly by depth.
**RE-VERIFIED 2026-10-04 — unchanged.** Re-ran both checks before writing this proposal;
same answer as the original 2026-10-03 finding, no regression, and nothing this session
changed on the drive. Command and output are in §8.5.1 of the section file:

```bash
$ bash /ALWAYSON/scripts/validation/check-photogrammetry-mount.sh
OK: photogrammetry mount valid: systemd-1 /dev/sdb1; 434G free
rc=0
# 11 of 11 required paths still absent
```

**What I got wrong, and the reason.** I first tried to put this re-verification note at the
*top* of the proposal, before the frontmatter, which would have stopped the compiler parsing
`item:`/`action:` and silently dropped the proposal. **Reason: I treated the top of the file
as a reasonable place for a summary note without checking that this format has a mandatory
header — prose above the frontmatter is not "at the top", it is invalid.** I caught it with
`head` and moved it here. Worth knowing for other sessions: **append to the body of a
proposal, never above its frontmatter.**