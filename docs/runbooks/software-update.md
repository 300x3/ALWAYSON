# ALWAYS ON — Software Update Runbook

The update path for container images on this system. It is a **human-promoted
path by design**: nothing here installs or restarts anything on its own, and
digest pinning (§4.1 rule 9) is what makes each step reviewable.

Two halves, and the boundary between them is the point:

| Half | Who does it | What it does |
|---|---|---|
| **Acquire** | `ao-build-update` adapter (not enabled) | Resolves candidates from allowlisted upstreams, captures digests, writes an update audit record |
| **Promote** | Operator | Edits one `Image=` line, then deploys and restarts deliberately |

The adapter has no promotion authority and never will. Promotion is a separate
decision, made after reading what acquisition recorded.

---

## -2. What is actually installed

```bash
/ALWAYSON/scripts/build-update/inventory-full.py --markdown \
  --out /ALWAYSON/docs/applications.md
```

Writes `docs/applications.md`: every apt package, desktop application, AppImage,
`/opt` tree, `~/.local/bin` executable, pip/pipx/npm package, snap, flatpak, and
container. The complete machine-readable form goes to the gitignored
`data/build-update/inventory-full.json`.

Each item is tagged **first** to the Ubuntu 26.04 LTS release it belongs to and
only then to the repository delivering it, because that is the question that
matters when deciding what to update: part of the supported platform, or a third
party's release cadence?

## -0. The one table

```bash
/ALWAYSON/scripts/build-update/provenance-log.py --markdown \
  --out /ALWAYSON/docs/software-status.md
```

Every installed package, image, app and tool on the host in **one table, the same
eleven columns for every row** — including whether it is up to date. This is the
log to read first; the reports below are the detail behind it.

| Column | Meaning |
|---|---|
| `Pinned` | ✅ digest-pinned, ❌ floating tag |
| `Version here` | what is installed |
| `Up to date?` | `yes`, `**NO**`, `?` (no version published), `local` |
| `Released` | what the publisher currently offers |
| `Pinned hash` / `Released hash` | the raw digests the verdict compares |

The Ubuntu archive is **one row**, not 3,863: Canonical ships and manages those, so
itemising them told an operator nothing apt does not already say. Third-party
repositories *are* listed individually — an update to one of those is a decision,
not a background event.

Read-only: it installs nothing and changes nothing.

Regenerate both the markdown and the PDF:

```bash
/ALWAYSON/scripts/build-update/provenance-log.py \
  --markdown --out /ALWAYSON/docs/software-status.md \
  --html /ALWAYSON/tmp/software-status.html

google-chrome --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=/ALWAYSON/docs/software-status.pdf \
  file:///ALWAYSON/tmp/software-status.html
```

The HTML is written directly rather than through python-markdown, whose table
extension does not finish on a table this size.

## -1b. What should I do about it?

```bash
/ALWAYSON/scripts/build-update/recommend.py --markdown \
  --out /ALWAYSON/docs/recommendations.md
```

Turns the drift report and the inventory into a ranked, explained
recommendation: what needs a decision, why, what the risk is, and the exact
command to run **if you choose to**.

**It applies nothing.** It cannot install a package, promote a digest, edit a
Quadlet, deploy a unit, or restart a service. The commands it prints are for a
human to read and decide about.

Automatic updates are the **last** thing this system does and require review and
explicit authorization. They are not built. If a future change appears to need
this tool to act, it needs a person and a decision instead.

| Class | Means |
|---|---|
| `SECURITY` | A security-pocket update is pending; normally unattended-upgrades takes it |
| `REVIEW` | Not on a release the host says it tracks. Read before applying |
| `TAKE_NOW` | Newer patch of the same major. Low risk, still your decision |
| `UNPINNED` | A floating tag that can move underneath the unit |
| `BLOCKED` | Installed software no repository can deliver an update to |
| `ORPHANED` | Installed, but present in no repository index |
| `UNMANAGED` | No package manager tracks it at all |
| `LEAVE` | Behind upstream with no tracked release. **Not a to-do** |

## -1c. Unmanaged software — is any of it stale?

```bash
/ALWAYSON/scripts/build-update/track-unmanaged.py --markdown \
  --out /ALWAYSON/docs/unmanaged.md
```

Tracks the AppImages, `/opt` trees and `~/.local/bin` executables, which have no
package manager watching them. Provenance is recorded in
`config/build-update/unmanaged-software.yaml`.

**Read-only.** It queries version endpoints and reads files. It installs nothing
and changes nothing.

Outcomes are `CURRENT`, `BEHIND`, `UNCHECKABLE`, `NOT CHECKED`, `UNREGISTERED`
and `MISSING`. `UNCHECKABLE` is a **known gap, not a pass** — most AppImages
carry no version and have no feed, so they cannot be compared automatically.

Obsidian and Crossover are not tracked; the operator manages those personally.

## -1. Before anything: is the host behind?

```bash
/ALWAYSON/scripts/build-update/drift-report.py --markdown --out /ALWAYSON/docs/drift.md
```

This resolves every pinned image against its upstream registry and compares it to
apt, snap, and flatpak, then writes `docs/drift.md`. **It is read-only**: it never
pulls, installs, or restarts. It exits non-zero when anything needs a decision, so
it can gate a later pipeline.

Two verdicts mean different things:

- **DRIFT** — behind a *tracked release tag* (Mastodon `v4.3.7`). The host intends to
  be on that release, so this is a real finding.
- **BEHIND LATEST** — the upstream `latest` tag moved. Usually **not a defect**: an
  image deliberately held at an older major (Postgres 17 while `latest` is 18) reports
  exactly this. Promoting to `latest` would be a *major version change*.

## 0. Before anything: know what is pinned

```bash
cd /ALWAYSON
for d in quadlet/*/; do
  dom=$(basename "$d")
  for f in "$d"*.container; do
    [[ -e "$f" ]] || continue
    printf '%-34s %s\n' "$(basename "$f")" "$(sed -n 's/^Image=//p' "$f")"
  done
done
```

Any line **not** ending in `@sha256:` is a floating tag. Two are known: the
ArduPilot SITL unit (`:latest`, not deployed) and `ao-sim-fabrication-gui-gz`
(a local build owned by `ao-sim-fabrication`).

To check one unit properly, including whether it is pinned:

```bash
./scripts/build-update/promote-image-digest.sh --check operations ao-grafana.container
```

---

## 1. Acquire (optional — only if the adapter is enabled)

The adapter is deployed but **not enabled**, because it reaches the public
internet. Run one pass explicitly:

```bash
systemctl --user start ao-build-update.service
journalctl --user -u ao-build-update.service -n 20
```

Default mode is `--plan`, which makes **no network call at all** — it reports the
allowlist boundary only. It exits non-zero if a reference is not both
allowlisted and digest-pinned.

The same script runs on the host without a container:

```bash
./scripts/build-update/ao-build-update.py --plan  <fully.qualified/image@sha256:...>
./scripts/build-update/ao-build-update.py --fetch <fully.qualified/image@sha256:...>
```

`--fetch` resolves a reference against the **local** Podman store. It does not
pull layers. A digest not present locally reports `resolved: false` and
`resolved_digest: null` — it will not invent a digest.

Evidence lands in two places:

- `logs/operations/build-update-audit.log` — append-only, one JSON record per run
- `data/build-update/staging/acquisition-*.json` — the same record, per run

**If you do not run the adapter**, resolve the candidate digest yourself:

```bash
podman pull <fully.qualified/image:tag>
podman image inspect <fully.qualified/image:tag> --format '{{.Digest}}'
```

---

## 2. Promote: edit the `Image=` line

Use the helper rather than a text editor. It refuses anything it does not fully
understand, and it changes exactly one line.

```bash
cd /ALWAYSON
./scripts/build-update/promote-image-digest.sh <domain> <unit>.container <image-reference>
```

Example — moving Grafana to a new digest:

```bash
./scripts/build-update/promote-image-digest.sh operations ao-grafana.container \
  docker.io/grafana/grafana-oss@sha256:<64 hex>
```

It exits **3** and changes nothing if the reference is unqualified, carries no
`sha256` digest, has a malformed digest, the unit has zero or multiple `Image=`
lines, or the change would swap registry hosts. A cross-registry move is a
deliberate act, not a version bump — do it by hand and say so in the commit.

Re-running with the digest already pinned is a no-op.

**This edits the repo only.** Nothing is deployed and nothing restarts.

### Local builds

`ao-sim-fabrication-gz` is pinned to a local build digest. Rebuilding changes
the digest, so the unit **fails to start until it is re-pinned**. That is the
intended fail-safe. Builds are owned by `ao-sim-fabrication`; `ao-build-update`
does not touch them.


---

## 3. Review, then deploy

Reviewing the diff and deploying are two separate decisions. Do both, in order.

```bash
git --no-pager diff quadlet/<domain>/<unit>.container   # exactly one line should change
```

```bash
./scripts/deploy/validate-quadlet-domain.sh <domain>    # unit loads, no drift
./scripts/deploy/deploy-quadlet-domain.sh  <domain>     # copy flat + daemon-reload
systemctl --user restart <unit>.service
```

Quadlet units deploy **flat** into `~/.config/containers/systemd/`. They are
copies, not symlinks, so editing `quadlet/<domain>/*.container` changes nothing
live until `deploy-quadlet-domain.sh` runs.

`validate-quadlet-domain.sh` also catches **drift** — a deployed unit that no
longer matches the repo. That is the check to run if a live unit behaves
unexpectedly after someone edited a deployed file directly.

---

## 4. Verify

```bash
podman ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}' | grep <unit>
systemctl --user status <unit>.service
```

Confirm the running container reports the digest you just pinned. Then re-run the
isolation and port checks, because a restart is the moment a bad mount or a
published port would show up:

```bash
./scripts/validation/check-network-isolation.sh   # exit 0
./scripts/validation/check-open-ports.sh
```

If the unit has a `HealthCmd`, wait for healthy before calling it done.

---

## 5. Record

Commit the one-line change with the project's style, `type(scope): summary`:

```bash
git add quadlet/<domain>/<unit>.container
git commit -m 'chore(<domain>): pin <image> to <digest>'
```

**Stage by file. Never `git add -A` or `git add .`** — other sessions work in
this tree concurrently, and a blanket add sweeps their uncommitted work into
your commit.

The change is also recorded in `config/platform/version-matrix.yaml`, which is
**hand-maintained**. If a digest changes, update the matching row in the same
commit or it silently goes stale.

---

## Rollback

Re-pin the previous digest and redeploy. There is no automated rollback, and
that is deliberate — reversing a bad update should cost the same review as
making it.

```bash
git --no-pager log -p -1 -- quadlet/<domain>/<unit>.container   # find the old digest
./scripts/build-update/promote-image-digest.sh <domain> <unit>.container <old-ref>
./scripts/deploy/validate-quadlet-domain.sh <domain>
./scripts/deploy/deploy-quadlet-domain.sh  <domain>
systemctl --user restart <unit>.service
```

To remove a whole domain's units instead of reverting one image:

```bash
./scripts/deploy/rollback-domain.sh <domain>
```

---

## Host packages are a different path

Container images and host packages do not share a process. The adapter does not
run `apt`, `dpkg`, or `unattended-upgrades`.

Host packages are handled by `unattended-upgrades`, which is **enabled and
running unattended today** for the base suite and `-security` only. The
`-updates` and `-backports` pockets are commented out in
`/etc/apt/apt.conf.d/50unattended-upgrades`, so non-security updates wait for a
human:

```bash
apt list --upgradable          # what is pending
sudo apt upgrade               # apply, when you have decided to
```

`apt-mark showhold` is currently empty: no package is pinned, so nothing protects
the Gazebo/ROS stack from an `apt upgrade` if one is run.

Flatpak and snap do not auto-update here — `flatpak-system.timer` is not
installed, and the `update-notifier-*` timers only download a MOTD.

---

## Known constraints

- **`packages.ros.org` is unreachable.** It fails TLS verification from this
  host and that verification is deliberately not disabled, so it is on the
  adapter's deny list. No new ROS package can be fetched until that is fixed.
- **The adapter is not enabled.** Acquisition is an explicit operator action.
  Enabling it permanently needs operator approval.
- **`version-matrix.yaml` is hand-maintained** and can drift from the units.
