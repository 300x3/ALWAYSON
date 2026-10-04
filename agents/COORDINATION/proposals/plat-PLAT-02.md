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
to edit. Recorded in §2.5, left for the compiler and OPS-B.