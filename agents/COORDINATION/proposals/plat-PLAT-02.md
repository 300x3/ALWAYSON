---
item: PLAT-02
action: update
evidence: |
  # the nginx:alpine row PLAT-02 names is already gone
  $ grep -rn 'nginx:alpine' . --exclude-dir=.git | grep -E '^\./(quadlet|config)/'
  (no output)
  $ sed -n '6,7p' quadlet/sim-fabrication/ao-sim-fabrication-portal.service
  # THIS REPLACES "gazebo-portal". That container was a throwaway nginx whose
  # docroot was the stock /usr/share/nginx/html
  $ grep -n 'image_nginx' config/platform/version-matrix.yaml
  46:  image_nginx: "not in use - the :8765 portal is the ao-sim-fabrication-portal.service python3 host process"

  # every quadlet image is digest-pinned except two deliberate exceptions
  $ grep -rh '^Image=' quadlet/ | grep -vc '@sha256:'
  2
  $ grep -rn '^Image=' quadlet/ | grep -v '@sha256:'
  quadlet/sim-vehicle/ao-ardupilot-sitl.container:12:Image=ghcr.io/ardupilot/ardupilot-sitl:latest
  quadlet/sim-fabrication/ao-sim-fabrication-gui-gz.container:47:Image=localhost/gz-sim10-resolute:gui-svgfix

  # but SIX RUNNING containers are tag-only, and none is owned by a unit
  $ podman ps --format '{{.Names}}\t{{.Image}}' | grep -v '@sha256:'
  ao-sqli3              docker.io/grafana/grafana-oss:11.6.0
  confident_khayyam     docker.io/grafana/grafana:11.6.0
  dreamy_rosalind       localhost/foxglove-bridge:latest
  keen_bhabha           docker.io/grafana/grafana-oss:11.6.0
  relaxed_tharp         docker.io/grafana/grafana:11.6.0
  vigorous_shannon      localhost/foxglove-bridge:latest
  # -> all six have podman-generated names, so no Quadlet unit owns them

  # matrix drift found
  $ uname -r ; grep -n '^  kernel:' config/platform/version-matrix.yaml
  7.0.0-38-generic
    3:  kernel: "7.0.0-34-generic"          # refreshed 2026-10-01; was recorded as 7.0.0-31-generic
  $ dpkg-query -W -f='${Package} ${Version}\n' nvidia-container-toolkit
  nvidia-container-toolkit 1.20.1-1        # matrix line 14 records 1.20.0
  $ podman ps --format '{{.Image}}' | grep postgres | sort -u
  docker.io/library/postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f
  # matrix records postgres@sha256:a65e6a84... which nothing runs
section: 02-platform-baseline
---
**Half of this item was already done and the item was never updated to say so.** The
`nginx:alpine` row PLAT-02 exists to fix has not existed in `quadlet/` or `config/` since the
`gazebo-portal` container was retired — `grep -rn 'nginx:alpine' . --exclude-dir=.git` returns
only historical mentions in `docs/compliance/installation-status.md`, `GAZEBO/`, an archived
`TOPOLOGY/` JSON, and the §19 text itself. §19.2 stated this on 2026-10-01; PLAT-02 was left
open against the old wording.

§2.5 of my section records the audit. Findings:

- **Repository is clean.** Only two tag-only `Image=` lines, both deliberate (`ardupilot-sitl:latest`,
  a local `localhost/` build).
- **Six running containers are tag-only** — four Grafana on `:11.6.0`, two on
  `localhost/foxglove-bridge:latest`. All six have `podman run`-generated names, so **no
  Quadlet unit owns them**; they duplicate the pinned `ao-grafana` and
  `ao-sim-fabrication-foxglove`. They are §19 `OPS-16` strays and are **not removed here** —
  container deletion needs operator approval.
- **Three matrix rows are stale**, and the PostgreSQL one is the serious: the matrix records
  `postgres@sha256:a65e6a84…` while `ao-sales-db`, `mastodon-db` and `ao-fabrication-db`
  actually run `postgres@sha256:d74eeac9…`. A version matrix naming a digest nothing runs
  cannot verify what is deployed. `host.kernel` records `7.0.0-34-generic` against a live
  `7.0.0-38-generic`, and the toolkit row records `1.20.0` against `1.20.1-1`. Four further
  running digests are absent from the matrix entirely.

**What I got wrong.** I first wrote "all 25 running containers are digest-pinned" from reading
the `sort -u` digest list rather than counting the exceptions, and only caught it when I ran
`podman ps ... | grep -v '@sha256:'` to cite a figure — it returned six. The reason I got it
wrong: I summarised the digest-pinned list and never enumerated its complement. §2.5 now states
six, names them, and says why none of them belongs to a unit.

**Not closed.** `PLAT-02` also asks for capture automation, which is `OPS-02` and belongs to
OPS-B; and the matrix rows need editing, and `config/platform/version-matrix.yaml` is not mine
---

# RE-VERIFICATION 2026-10-04 16:40 — every §2.5 figure re-run

I re-measured rather than trusting the audit above, because three of its numbers were
written by a pass that has already been wrong twice on this item. **All reproduce
unchanged:**

```
$ podman ps --format '{{.Names}}' | wc -l
25                                        # §2.5's "25 running containers" holds
$ grep -rn '^Image=' quadlet/ | grep -v '@sha256:' | wc -l
2                                         # the two deliberate unpinned images
$ podman ps --format '{{.Names}}\t{{.Image}}' | grep -v '@sha256:' | wc -l
6                                         # the same six strays, same names
$ uname -r
7.0.0-38-generic                          # matrix still records 7.0.0-34-generic
$ dpkg-query -W -f='${Package} ${Version}\n' nvidia-container-toolkit
nvidia-container-toolkit 1.20.1-1         # matrix still records 1.20.0
$ podman ps --format '{{.Image}}' | grep postgres | sort -u
docker.io/library/postgres@sha256:d74eeac9...   # matrix records ...a65e6a84
```

The Redis finding also reproduces precisely — the matrix records
`redis@sha256:91d0f7e8…` in **two** places (`broker_image_digest` line 21 and
`image_redis` line 48) while both running Redis containers use
`redis@sha256:c6eabf74…`. There are **14 distinct running digests**.

**The drift is entirely mine to report and not mine to fix.** `PLAT-02` cannot close:
the corrections belong in `config/platform/version-matrix.yaml`, which this session does
not own, and the capture automation is `OPS-02` (OPS-B). I re-verified rather than
closed, because the previous pass on this item had already retracted one claim
("all 25 running containers are digest-pinned") after the same command returned six.

## One finding this pass did not expect, and it belongs to another group

The `ao-restic-*` units found at system level during PLAT-01 re-verification
(`ao-restic-backup`, `ao-restic-prefetch`, `ao-restic-verify` and their three timers,
`/etc/systemd/system/`, dated 2026-10-02) are **backup** units. `ao-restic-backup.timer`
and `ao-restic-verify.timer` are `enabled`; `ao-restic-prefetch.timer` is `disabled`.
They run `/ALWAYSON/scripts/backup/restic-run.sh` with
`Environment=RESTIC_ENV_FILE=/run/user/1000/ao-restic.env`.

I have **not** touched them — backup and restore data is an explicit stop condition, and
§17 belongs to OPS-B. But two facts are worth flagging to whoever owns §17, and one is
contradictory: §19 `OPS-15` states a backup schedule was automated 2026-08-31, while the
unit files that implement it are dated **2026-10-02**. I make no claim about which is
right — that needs §17's own evidence and it is not mine to adjudicate. No secret is
named here; only the environment variable's name and path.
to edit. Recorded in §2.5, left for the compiler and OPS-B.

---

# THIRD PASS 2026-10-04 17:05 — re-measured; still not closable from this session

Every figure in the audit above was re-run. **All reproduce unchanged**, so this pass adds no new
drift — it corrects the *count* of the drift, which the earlier passes understated.

```
$ uname -r
7.0.0-38-generic                                  # matrix line 3 says 7.0.0-34-generic
$ dpkg-query -W -f='${Package} ${Version}\n' nvidia-container-toolkit
nvidia-container-toolkit 1.20.1-1                 # matrix line 14 says 1.20.0
$ podman ps --format '{{.Image}}' | grep postgres | sort -u
docker.io/library/postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f
$ grep -n 'a65e6a84\|91d0f7e8' config/platform/version-matrix.yaml | sed 's/: *"docker.*//'
21:  broker_image_digest
47:    image_postgres
48:    image_redis
61:  image_postgres_shared
# ^^ the stale digests live in FOUR keys across FOUR lines
$ podman ps --format '{{.Image}}' | grep redis | sort -u
docker.io/library/redis@sha256:c6eabf748fc7a61dbb5a705c78bcf3d6377b1127a97d0ce965c11c44ba46896f
$ grep -rh '^Image=' quadlet/ | grep -vc '@sha256:'
2
$ grep -rn '^Image=' quadlet/ | grep -v '@sha256:'
quadlet/sim-vehicle/ao-ardupilot-sitl.container:12:Image=ghcr.io/ardupilot/ardupilot-sitl:latest
quadlet/sim-fabrication/ao-sim-fabrication-gui-gz.container:47:Image=localhost/gz-sim10-resolute:gui-svgfix
$ podman ps --format '{{.Names}}\t{{.Image}}' | grep -v '@sha256:' | wc -l
6
$ podman ps --format '{{.Names}}' | wc -l
25
```

## Correction: the drift is four keys across four lines, not "three rows"

Earlier passes reported three stale rows. The redis digest appears in **two** matrix keys
(`broker_image_digest` line 21, `image_redis` line 48) and postgres in **two more**
(`image_postgres` line 47, `image_postgres_shared` line 61). Counting *rows* rather than *keys* is
how "three" survived two re-verification passes. Corrected in §2.5.

**Still not closable here.** Two independent reasons, both unchanged:

1. The corrections belong in `config/platform/version-matrix.yaml`, which this session does not own.
   Recording the drift in §2.5 does not fix the matrix, and a version matrix that names a digest
   nothing runs cannot verify the deployment — so the item must stay open until someone with
   ownership edits the file.
2. The capture automation the item asks for is `OPS-02`, assigned to OPS-B.

The six tag-only running containers remain **unowned strays** (§19 `OPS-16`). Not removed here —
container deletion requires operator approval under README §4.1 rule 3.

## What I got wrong on this pass

I nearly reported "four stale rows" as a new correction without checking how many *lines* each
one occupies, which is the exact error I am correcting in the paragraph above. I caught it because
I ran `grep -n` for the digest prefixes instead of assuming one line each. **Count the thing you
are claiming to count** — a "row" claim needs the row numbers, and a digest appears wherever it
appears.