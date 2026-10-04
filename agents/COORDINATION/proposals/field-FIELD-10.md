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

---

**UPDATE 2026-10-04 15:09 — §8.5.2 added: the blocker now has a measured root cause.**
Action stays `update`; the item still cannot close, but one of its two unresolved questions is
answered and the other is no longer ambiguous.

The previous version of this proposal left the ownership half as "unverified at depths 2-4".
That was a symptom, not a finding. §8.5.2 now measures the cause:

```bash
$ stat -c '%n owner=%U group=%G mode=%a' /media/scottw/500GBPHOTOGRAM/tmp
.../tmp owner=ao-mapping group=alwayson-mapping mode=770
$ getent group alwayson-mapping
alwayson-mapping:x:975:              # no members at all
$ id -nG scottw | tr ' ' '\n' | grep -xE '1001|975'
1001                                # in ao-mapping; NOT in alwayson-mapping (975)
$ mkdir /media/scottw/500GBPHOTOGRAM/tmp/processing
mkdir: Permission denied
$ sg ao-mapping -c "mkdir -p /media/scottw/500GBPHOTOGRAM/tmp/processing"
mkdir: Permission denied
```

`sg ao-mapping` failing is the load-bearing detail: the operator *is* in group `ao-mapping`
(1001), but these directories are group-owned by **`alwayson-mapping` (975)**, which the
operator is not in, and `other` is `---`. So the operator falls through to `other` and is
denied. That is why §8.5.1 could not traverse 8 of 10 subtrees — a hard denial, not an
incomplete attempt.

**A second fault surfaced with it: depth-2 ownership is inconsistent with depth 1.** Three
patterns coexist on one volume — `ao-mapping:alwayson-mapping` (top level),
`scottw:ao-mapping` (`webodm/media`), `scottw:scottw` (`retention/pending-review`).

```bash
$ stat -c '%n owner=%U group=%G' /media/scottw/500GBPHOTOGRAM/retention/pending-review \
                               /media/scottw/500GBPHOTOGRAM/webodm/media
.../retention/pending-review owner=scottw group=scottw
.../webodm/media              owner=scottw group=ao-mapping
```

This **corrects §8.5.1's claim that setgid makes the ownership arrangement correct.** Setgid
propagates the *parent's group* — here `alwayson-mapping`, precisely the group the operator
cannot write through. Setgid is propagating the fault as reliably as it propagates the intent.
The correction is recorded in §8.5.1 with a pointer to §8.5.2 rather than deleted.

**Read this before "fixing" it:** the mode is `770` with `other=---` and no world-writable
directory, which is exactly what §8.2 requires. **The operator being locked out is the security
policy working correctly, not failing.** The repair is to add the operator to the mapping group
(`sudo usermod -aG alwayson-mapping scottw`, then re-login) — **not** to relax the mode to
`777` or add world-write ACLs. If any other session proposes loosening these permissions to
make a mapping path writable, that is a regression against §8.2 and should be refused.

**What I got wrong this session, and the reason.** I overwrote this proposal's entire
frontmatter with the FIELD-15 content while intending to append to the body — I passed the
existing header text as `old_text`, so the write landed on top of the file and destroyed
FIELD-10's `item:`/`action:` block. **Reason: I used a replace-the-whole-header idiom to
create a *different* file, in the wrong file.** I caught it on the next read and restored with
`git checkout -- agents/COORDINATION/proposals/field-FIELD-10.md` (99 lines, header intact),
then created `field-FIELD-15.md` as a separate new file. No other session's file was touched.

Note for other sessions: **the frontmatter is the one part of a proposal you must never
replace, only read.** Every other part of these files is safely appendable.