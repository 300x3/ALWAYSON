---
item: OPS-17
action: close
evidence: |
  $ AO_ROOT=/tmp/ao-sessions/wt-ops-b bash scripts/provision/install-vendor-binaries.sh
  vendor binaries declared: 8
  OK      qgroundcontrol v5.1.0 - present, digest matches
  OK      reticulum-meshchatx v4.9.1 - present, digest matches
  OK      lm-studio v0.4.20-1 - present, digest matches (no url: not auto-installable)
  OK      pcloud v- - present, digest matches (no url: not auto-installable)
  OK      nperf v- - present, digest matches (no url: not auto-installable)
  OK      gh v2.97.0 - present, digest matches
  OK      bun v1.4.2 - present, digest matches
  OK      cline v3.0.60 - present, no installed digest recorded to check against
    path: /home/scottw/.local/bin/cline

  installed=0  already-present=8  manual=0  refused=0  failed=0
  rc=0

  # exit contract, proven with a throwaway fixture manifest
  $ VENDOR_MANIFEST=/tmp/ao-vt/manifest.yaml bash scripts/provision/install-vendor-binaries.sh
  DRIFT   fake-drift v1.0 at /tmp/ao-vt/fake.AppImage
    on disk: 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
    manifest installed_sha256: dead0000beef0000dead0000beef0000dead0000beef0000dead0000beef0000
    NOT overwritten (README 4.1 rules 2/3). Resolve by hand, or update the
    manifest digest in one commit once the newer artifact is measured.
  MANUAL  fake-nourl-absent (v1.0)
  rc=2

  $ bash -n scripts/provision/install-vendor-binaries.sh && bash -n scripts/provision/provision.sh
  (clean)

  # provision.sh dry run must not hand --yes to the installer
  $ AO_ROOT=/tmp/ao-sessions/wt-ops-b bash scripts/provision/provision.sh
    vendor blobs (AppImages, vendor executables):
    [dry-run] bash /tmp/ao-sessions/wt-ops-b/scripts/provision/install-vendor-binaries.sh
  --- stage 50: podman networks and Quadlet units
  # stage 40 no longer aborts the rebuild on a refused entry
section: 12-host-installation-and-configuration
---
New `config/build-update/vendor-binaries.yaml` (8 entries) and
`scripts/provision/install-vendor-binaries.sh`, delegated to from `provision.sh`
stage 40. §12.4.1 replaces the old §12.4 line that called AppImages and vendor
tarballs a third category that "must be fetched by hand".

All eight are present on this host and verify. Five have **no vendor URL**, so
they cannot be fetched unattended even in principle — a property of the vendors,
not a gap in the provisioner. That residue is stated in the section rather than
papered over.

**What I got wrong**, four defects, three of which made the tool report OK or
success when it should not have.

1. **Ordering.** The first revision tested "does this entry have a url?" *before*
   "is the file already installed?", and `continue`d. Measured consequence:
   `lm-studio`, `pcloud` and `nperf` all reported `MANUAL ... a human must place
   this file` while **all three exist on disk and all three hash to the manifest's
   own recorded `sha256`**. "Cannot be fetched automatically" and "is not
   installed" are different facts and only the second is a problem; I had
   conflated them and would have sent the operator to re-fetch three working
   files.
2. **Archive/AppImage digest conflation.** One field was used for both the
   download and the installed file. For an AppImage they are the same; for
   `archive-extract` they are not, so every archive reported a false DRIFT on a
   host where the binary was correct. Split into `sha256` and `installed_sha256`.
3. **An all-numeric digest was silently erased, and reported OK.** YAML coerces
   unquoted `0000…0` to integer `0`, and the `or ""` fallbacks rendered that as
   the empty string — so the entry degraded to "no installed digest recorded" and
   printed **OK**. That is the single worst outcome a digest check can produce.
   Found only because my own fixture used `0000…0`; every real digest contains
   `a`–`f` and would never have triggered it. Every scalar is now `str()`-ed, so
   it reports DRIFT instead.
4. **Every failure exited 0.** A DRIFT and a failed download were both printed
   and then succeeded. Worse, `provision.sh` calls this through its `run` helper,
   which propagates the return code **unguarded** — so simply adding a correct
   non-zero exit would have aborted stage 40 and left the host with no Quadlet
   units at all. The installer now exits 1/2 and the `run` call is `|| true`.
   A drifted AppImage must not stop the world: the installer refuses to overwrite
   (README §4.1 rules 2/3), so "carry on, tell the operator" is correct.

On (3) I should be precise: `str()` does not restore the leading zeros — YAML has
already dropped them by then, so the compared value is `0`, not `0000…0`. It
converts a silent OK into a visible DRIFT. That is why real digests in the
manifest are quoted.

A trap worth naming for the next session: my fixture was written with `kind:`
before I checked the schema key, which is `install:`. The fixture's first run
reported two entries as "no installed digest" and I initially read that as a
script bug. The fixture was wrong. I only caught it by dumping the parsed JSON
with `bash -x` and seeing the key come back null.