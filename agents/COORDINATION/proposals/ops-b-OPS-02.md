---
item: OPS-02
action: close
evidence: |
  $ AO_ROOT=$PWD bash scripts/validation/check-image-digests.sh --check
  deployed units  : 21 in /home/scottw/.config/containers/systemd
  distinct digests: 14
  UNPINNED  Image=localhost/gz-sim10-resolute:gui-svgfix
  DRIFT     mapping.broker_image_digest              sha256:91d0f7e8c748e...
  DRIFT     simulation.gazebo_images                 sha256:0c19f326a339e...
  DRIFT     simulation.image_foxglove_bridge         sha256:6d3461ddf0277...
  DRIFT     sales.mastodon.image_postgres            sha256:a65e6a841f6c4...
  DRIFT     sales.mastodon.image_redis               sha256:91d0f7e8c748e...
  DRIFT     operations.image_postgres_shared         sha256:a65e6a841f6c4...
  matrix digests matched a deployed unit  : 11
  matrix digests matching nothing deployed: 7
  deployed Image= lines without a digest  : 1
  UNLISTED  deployed but absent from the matrix: sha256:d74eeac9a635...  (postgres, 3 units)
  UNLISTED  deployed but absent from the matrix: sha256:c6eabf748fc7...  (redis, 2 units)
  UNLISTED  deployed but absent from the matrix: sha256:9acc6d4df749...  (foxglove)
  UNLISTED  deployed but absent from the matrix: sha256:55f8dbcf8dec...  (gz-sim10-server)
  RESULT: DRIFT -- 7 stale matrix row(s), 1 unpinned deployed image(s).
  $ echo $?
  1

  $ python3 -m pytest scripts/build-update/test_generators.py -q
  62 passed in 0.73s
section: 12-host-installation-and-configuration
---
New `scripts/validation/check-image-digests.sh` compares every digest in
`config/platform/version-matrix.yaml` against the digests the **deployed** units
actually carry, and reports drift. §12.5.5 documents it. It found real drift on
first run: **7 stale rows, 1 unpinned deployed image, 4 deployed digests absent
from the matrix.**

`capture-version-matrix.sh` did not and could not cover this: it `sed`-rewrites
five host facts (systemd, podman, netplan, nvidia) and never looks at an image
at all. I left it untouched and added a separate script.

**The check reads deployed units, not `quadlet/`** — deliberately. Quadlet
deploys flat, so `~/.config/containers/systemd/` holds copies; comparing against
the repository would report "no drift" at exactly the moment the live system had
drifted. The deployed unit is the only thing describing what is running.

**The check reports, it never rewrites.** Where a row disagrees with the live
system, deciding which side is right is an operator judgement — stale document,
unapproved deploy, or an unrecorded deliberate change. A script that adopted the
live digest would make the matrix self-fulfilling and launder a hand edit into
an apparently-captured fact. **The seven rows above are reported, not fixed.**
That is the deliberate part and the part most likely to look like incompleteness.
Resolving them is listed below.

**A bug the tests caught on the first run.** When every deployed image is
unpinned, the digest-extracting `grep` matches nothing and exits 1; under
`set -e` + `pipefail` that aborted the script with **status 1 and no output at
all**. A gate that fails without saying why is worse than no gate. Fixed by
tolerating the empty result in collection rather than by loosening `set -e`,
because the unpinned images are what the script most needs to report. The five
new tests drive the real script against a synthetic tree and assert exit codes,
so the OK path is exercised as carefully as the failing ones — a check only ever
seen failing proves nothing, since "7 rows drifted" is also what a broken
comparison prints.

### Open findings for the operator (need explicit approval — not actioned)

1. **7 stale matrix rows.** Decide per row whether the document or the live unit
   is right. The clearest: the matrix records
   `postgres@sha256:a65e6a84…` in two rows while all three deployed postgres
   units (`ao-fabrication-db`, `ao-mastodon-db`, `ao-sales-db`) run
   `sha256:d74eeac9…`. Also 4 deployed digests the matrix never mentions. **This
   needs operator approval** — correcting the matrix asserts the live state is
   intended, and correcting the units is a redeploy.
2. **`Image=localhost/gz-sim10-resolute:gui-svgfix` is not digest-pinned**, a
   live README §4.1 rule 9 violation. It is a local build, so pinning it means
   recording a build recipe and its reproducibility, not just editing a file.
   **Needs operator approval.**