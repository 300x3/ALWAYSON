# 12. Host Installation and Configuration

## 12.1 Installation Journal

Create the journal before installation activity:

```bash
sudo install -d -m 0750 -o "$USER" -g "$USER" /ALWAYSON/logs/installation
touch /ALWAYSON/logs/installation/agent-install.log
chmod 0640 /ALWAYSON/logs/installation/agent-install.log
```

## 12.2 Initial Non-Destructive Inventory

Run before installing or changing anything:

```bash
{
  echo "===== Timestamp ====="
  date --iso-8601=seconds

  echo "===== Host ====="
  hostnamectl

  echo "===== OS ====="
  cat /etc/os-release

  echo "===== Kernel ====="
  uname -a

  echo "===== CPU / RAM ====="
  lscpu
  free -h

  echo "===== Storage ====="
  lsblk -o NAME,SIZE,FSTYPE,FSVER,LABEL,UUID,MOUNTPOINTS
  df -hT

  echo "===== Photogrammetry Mount ====="
  findmnt /media/scottw/500GBPHOTOGRAM || true

  echo "===== Podman ====="
  command -v podman || true
  podman version 2>&1 || true
  podman info 2>&1 || true

  echo "===== systemd ====="
  systemd --version

  echo "===== cgroups ====="
  stat -fc %T /sys/fs/cgroup

  echo "===== GPU ====="
  lspci -nnk | grep -A3 -Ei 'VGA|3D|NVIDIA' || true
  command -v nvidia-smi && nvidia-smi || true

  echo "===== Network ====="
  ip -brief address
  ss -tulpn
  ss -tulpn6

  echo "===== Firewall ====="
  sudo ufw status verbose 2>&1 || true
  sudo nft list ruleset 2>&1 || true

  echo "===== Existing systemd services ====="
  systemctl --user list-unit-files --type=service 2>&1 || true

  echo "===== Existing containers: current user ====="
  podman ps -a 2>&1 || true

  echo "===== Existing containers: system store ====="
  sudo podman ps -a 2>&1 || true

  echo "===== Existing Podman networks: current user ====="
  podman network ls 2>&1 || true

  echo "===== Existing Podman networks: system store ====="
  sudo podman network ls 2>&1 || true

  echo "===== Reticulum and MeshChatX ====="
  command -v rnsd || true
  rnsd --version 2>&1 || true
  pgrep -a -f 'rnsd|ReticulumMeshChatX' || true
  ss -ltnp 2>/dev/null | grep -E '(:18000|:4242)' || true

  if [ -f "$HOME/.reticulum/config" ]; then
    echo "--- Reticulum configuration ---"
    grep -nE '^\[\[|^type =|^(interface_enabled|enabled) =|^target_host =|^target_port =|^port =|^mode =' \
      "$HOME/.reticulum/config"
  fi

  if [ -d "$HOME/.reticulum-meshchatx/logs" ]; then
    echo "--- Recent MeshChatX errors and warnings ---"
    tail -n 500 "$HOME/.reticulum-meshchatx/logs/meshchatx.log" \
      | grep -Ei 'error|warning|disabled|interface|umsgpack' || true
  fi

  echo "===== Serial devices ====="
  ls -l /dev/serial/by-id/ 2>&1 || true
} | tee -a /ALWAYSON/logs/installation/agent-install.log
```

Pause and report if:

- The photogrammetry drive is not mounted.
- The mountpoint is an ordinary root-filesystem directory.
- Mapping storage is below 100 GB free.
- Existing WebODM, Podman, Docker, Corda, PostgreSQL, ROS, Gazebo, or related
  services conflict.
- NVIDIA driver state is broken.
- cgroups v2 or the selected Podman runtime mode does not work.
- Firewall policy conflicts with intended isolation.
- A proposed service port is already bound.
- Heltec cannot be found through a stable `/dev/serial/by-id/` path.
- MeshChatX or Reticulum is unexpectedly absent after installation approval.
- The Reticulum configuration contains an interface not present in the approved
  inventory.
- A supposedly enabled interface repeatedly fails without a documented
  compensating control.
- The Reticulum gateway listener is reachable from an unapproved network.
- MeshChatX reports persistence, cryptographic-state, or repository-integrity
  errors.

## 12.3 Host Dependencies

After inventory review and explicit operator approval:

```bash
sudo apt update

sudo apt install -y \
  podman \
  uidmap \
  slirp4netns \
  fuse-overlayfs \
  containernetworking-plugins \
  nftables \
  ufw \
  git \
  curl \
  jq \
  ca-certificates \
  gnupg \
  openssl \
  restic \
  smartmontools \
  lm-sensors \
  acl \
  python3 \
  python3-venv \
  python3-pip
```

Verify — **this block asserts and exits non-zero on failure**:

```bash
./scripts/validation/verify-host-baseline.sh
```

The script asserts and exits non-zero on failure. Any inline verification block
in this section must be able to fail: an inline cgroup test of the form
`test "$(stat -fc %T /sys/fs/cgroup)" = "cgroup2fs" && echo ...` is silent when
the test fails, nothing reads its return code, and the block's exit status is 0
either way. A check that cannot fail verifies nothing, so no §19.2 evidence may
rest on one.

The script must be tested in both directions, because a verifier that only
ever passes is the same defect wearing a new hat:

```
$ ./scripts/validation/verify-host-baseline.sh
  PASS  podman responds (5.7.0)
  PASS  systemd --user manager reachable
  PASS  linger enabled (survives logout)
  PASS  cgroup v2 unified hierarchy
  PASS  aa-status present
  WARN  aa-enforce MISSING - apparmor-utils not installed ...
  --- 5 passed, 0 failed ---
RESULT: PASS                                    # exit 0

# with stat and loginctl stubbed to report a broken host:
  FAIL  linger is 'Linger=no', expected 'yes' - containers stop at logout (OPS-13)
  FAIL  cgroup fs type is 'tmpfs', expected 'cgroup2fs'
  --- 3 passed, 2 failed ---
RESULT: FAIL (2 check(s) failed)                # exit 1
```

It asserts the **value** of `Linger` rather than the presence of the key, and
reports `aa-enforce` as a WARN with the reason, instead of passing on
`aa-status` — which ships in the base `apparmor` package and succeeds even
though no profile can actually be enforced on this host (see §2.3).
### 12.3.1 Linger is a precondition, not a nicety (OPS-13)

**Overlap with the baseline verifier above, stated so the next reader does not
double-count it.** `verify-host-baseline.sh` already asserts `Linger == yes` as
one of its five checks, and that is the check to trust for the yes/no question.
`check-user-linger.sh` is **not** a second opinion on that question - it is a
*diagnostic* for it, reporting the linger state alongside the user-manager
runtime, the deployed unit count and the running `ao-*` service count, so that
when the baseline check fails you can see why. Both agree on the value.

It earns a separate existence because the baseline check is a single boolean over
one account, and this is the one that exits **2** for an account that does not
exist - the failure mode a `[ "$linger" = "yes" ]` test handles worst. See the
bug below.

The `loginctl show-user -p Linger` check must not be read-only and silent on failure —
linger is a real precondition rather than a nicety: every workload here is a *rootless user* Quadlet unit under
`~/.config/containers/systemd/`, driven by `systemd --user`, and that instance
only exists for the operator account while a session is open. Log out of KDE and
every container, timer and Quadlet-generated unit for this account stops, and none
of them come back on their own after a reboot. `ao-lmstudio.service` already
depends on this - its own header says "Starts at boot via user lingering".

So the rebuild must **report** linger before it starts any unit, and the
provisioner does so at stage 20, before stage 50:

```bash
./scripts/validation/check-user-linger.sh          # report
./scripts/validation/check-user-linger.sh --check  # gate: 0 ok, 1 fault, 2 no such account
```

Expected output:

```console
$ bash scripts/validation/check-user-linger.sh
user            : scottw
Linger          : yes
State           : active
OK:   linger enabled
marker file     : present (/var/lib/systemd/linger/scottw)
OK:   user manager runtime /run/user/1000 present
      running user services: 90
deployed units  : 21 .container files in /home/scottw/.config/containers/systemd
generated ao-*  : 48 service units under systemd --user
running ao-*    : 26
```

**The provisioner deliberately does not enable linger.** `loginctl enable-linger`
needs root and writes `/var/lib/systemd/linger/` — a host-level change, which
README §4.1 rules 1 and 3 place with the operator. The stage reports the state
and prints the exact command; it does not run it.

## 12.4 Rebuilding This Host From Nothing

**Kubuntu 26.04 LTS is the starting point** — <https://kubuntu.org/download/>. Install it
first, then KDE Plasma, Cline CLI and an internet connection are what the provisioner expects.
`scripts/provision/provision.sh` reconstructs everything else the repository already
describes, in stages. It is **dry-run by default**; pass `--yes` to apply.

```bash
./scripts/provision/provision.sh          # dry run: prints every action
./scripts/provision/provision.sh --yes    # apply
```

| Stage | Restores | Notes |
|---|---|---|
| 10 | 7 third-party apt repositories | ROS 2 is registered but **unreachable** (TLS); not worked around |
| 20 | Host dependencies, layout, podman networks, inventory | **Delegates to `scripts/bootstrap/00`, `02`, `03`, `04`** rather than repeating them. Also **reports linger** before any unit starts (§12.3.1) |
| 30 | 16 snaps, 1 flatpak | Enumerated from the installed set |
| 40 | Host applications | Read from `unmanaged-software.yaml`, not hardcoded. Vendor blobs delegated to `install-vendor-binaries.sh` (§12.4.1) |
| 50 | 9 Quadlet domains, **36 Quadlet source units** | **Quadlet deploys flat** — `~/.config/containers/systemd/` holds copies, so the deploy script is mandatory, not optional |
| 60 | Secret presence check | Derived from the units' own `EnvironmentFile=` lines |
| 70 | Data check only | **Never restores.** Restoration is a human decision (rule 2/3) |
| 90 | Verification | Regenerates the inventory for diffing against `docs/software-status.md` |

Two things a rebuild cannot restore from the repository, and must come from
backup: the **10 secret files** in `~/.local/share/ao-secrets/` (outside git by
design) and the **persistent data** in `data/` (ardupilot 2.1G, corda-install
282M). The **AppImages and vendor binaries** were long described here as a third
category "that must be fetched by hand"; §12.4.1 replaces that with a manifest
and an installer that verifies what is already on disk.

### 12.4.2 Every stage has an undo, and the undo is non-destructive (OPS-12)

`scripts/provision/rollback.sh` is the required counterpart of §12.4: every stage of
`provision.sh` must have a documented, non-destructive way back, so a rebuild that fails
halfway never leaves the operator without one. The script is **dry-run by default**,
mirroring `provision.sh`, because undo is as dangerous as the action.

```bash
./scripts/provision/rollback.sh --list   # what each stage undoes, and whether it needs an operator
./scripts/provision/rollback.sh         # dry run: prints every action
./scripts/provision/rollback.sh --yes   # apply
```

It runs stages in **descending order (90 → 10)** so dependents go before their
dependencies: units are withdrawn before the repositories that supplied them.

**The rule that shapes it: stages differ in whether their undo is safe to automate.**

| Stage | Undo | Safe to run unattended? |
|---|---|---|
| 90 | nothing — regenerated artefacts | yes, informational |
| 70 | **nothing** — stage 70 never restores | yes, reports `data/` sizes only |
| 60 | **nothing** — stage 60 only checked presence | yes, never touches secrets |
| 55 | restic units: stop, disable, remove the 6 unit files | yes, with a warning that this stops backups |
| 50 | Quadlet files per domain, via `deploy/rollback-domain.sh` | yes |
| 40 | vendor blobs | **no** — prints manifest ids, removes nothing |
| 30 | snaps and flatpak | **no** — prints `snap remove` commands, runs none |
| 20 | apt repo files and keyrings | printed, not executed |
| 10 | nothing — stage 10 only *adds* | n/a |

Three things are deliberately **never** undone, because no script here can undo them
safely: `data/` (rule 2/3), **secrets** (the values live in the wallet and in
`~/.local/share/ao-secrets/`, and are not reproducible from this repository), and
Podman networks (removing one strands whatever containers are attached). A rollback that
"restores the host to bare Ubuntu" would be a data-loss event wearing a rollback's
clothes.

The dry run is idempotent by construction: state is identical before and after, and the summary line is last.

The only `rm` the script can reach is `sudo rm -f /etc/systemd/system/<unit>`, named from
`systemd/backup/`. Stage 50 delegates to `rollback-domain.sh`, which removes **only** the
unit files named in `quadlet/<domain>/` and never `rm -r`s the flat unit directory — that
directory holds every other domain, plus the networks and volumes they share.

It closes with the provision ledger's own record of which stages actually ran, read from
`logs/operations/provision-ledger.jsonl` rather than assumed:

```text
$ python3 -c "..." # counting stage keys in the ledger
  stage 10: 62 step(s) recorded
  stage 20: 15 step(s) recorded
  stage 50: 78 step(s) recorded
  stage 55: 7 step(s) recorded
  stage 90: 16 step(s) recorded
```

The rollback half is written; whether a clean-room rebuild has ever executed it end to
end, and whether `bootstrap/01` is gated on §17.3 evidence, are tracked in §19.1 OPS-12.

# Automatically generated by /usr/libexec/podman/quadlet
#
# /ALWAYSON/quadlet/sales/ao-sales-db.container
```

Note the generator is Podman's quadlet helper at `/usr/libexec/podman/quadlet`, **not**
`systemd-container-generator` (that path does not exist on this host). Restricted to
source-typed files the two sets agree almost exactly:

```text
$ find ~/.config/containers/systemd -maxdepth 1 -type f \
    \( -name '*.container' -o -name '*.network' -o -name '*.volume' -o -name '*.build' \) \
    -printf '%f\n' | wc -l
30
# deployed source-typed NOT in repo:  (none)
# repo source-typed NOT deployed:
ao-ardupilot-sitl.container
ao-data.network
ao-field.network
ao-ledger-core.network
ao-ledger-ingest.network
ao-sim-vehicle.network
```

Those six are a real, separate finding and are **reported, not fixed**. Five are
`quadlet/networks/*.network` and one is `quadlet/sim-vehicle/`, none is deployed, yet all
five networks exist live under those exact names:

```text
$ podman network ls --format '{{.Name}}' | grep -E '^ao-(data|field|ledger-core|ledger-ingest|sim-vehicle)$'
ao-data
ao-field
ao-ledger-core
ao-ledger-ingest
ao-sim-vehicle
```

They were therefore created by `bootstrap/04-create-operational-layout`'s sibling
`04-create-podman-networks.sh`, which calls `podman network create` directly. **The same
network is described by two owners** — a repo Quadlet file and an imperative bootstrap
script. For `ao-data` the two agree:

```text
$ grep -E 'NetworkName|Internal' quadlet/networks/ao-data.network
NetworkName=ao-data
Internal=true
$ podman network inspect ao-data --format '{{.Name}} internal={{.Internal}} subnet={{(index .Subnets 0).Subnet}}'
ao-data internal=true subnet=10.89.8.0/24
```

But a future edit to one file would not change the running network. Deciding the single
owner of network creation is a design decision, it touches live network configuration, and
it is **not mine to settle** — it needs an operator decision and, if adopted, a redeploy of
the flat unit copies (§16.1.1). `ao-ardupilot-sitl.container` being undeployed is
unremarkable: SITL is a simulation container, not an always-on service.

### 12.4.1 Vendor blobs are declared, pinned and verified (OPS-17)

`config/build-update/vendor-binaries.yaml` is the manifest; each entry carries an
`id`, `version`, `install` kind, target `path`, a download `sha256`, an optional
`sha256_published_by_vendor`, and — for archives — the `member` to extract and a
separate `installed_sha256` for the extracted binary.

**Two digests, deliberately not conflated.** `sha256` is what the *download*
must hash to. `installed_sha256` is what the *installed file* must hash to. For
an AppImage these are the same value (the file *is* the download); for an
archive they are not, because the download is a `.tar.gz`/`.zip` and the
installed file is the binary inside it. The first revision used one field for
both and reported a false DRIFT for every archive on a host where the binary was
perfectly correct.

```bash
./scripts/provision/install-vendor-binaries.sh          # dry run (default)
./scripts/provision/install-vendor-binaries.sh --yes    # fetch and install
```

Exit codes: **0** clean, **1** a download or install failed, **2** at least one
entry was refused (DRIFT or an unpinned download). `manual` is deliberately *not*
a failure — it means no vendor publishes an artifact, which is an operator phase,
and counting it would make every run red.

Dry run against the real manifest:

```console
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
```

**All eight must be present and verified.** Five have no vendor URL and
so cannot be fetched unattended by design — a property of the vendors,
not a gap in the provisioner, and the honest residue of OPS-17. Three (gh, bun,
cline) are installable; the first two verify against a recorded `installed_sha256`.

## 12.5 Inventory and Update Management

The provisioned host is then verified against the committed inventory, and kept
current from it.

```bash
sudo ./scripts/build-update/refresh-install-log.sh --refresh
```

Regenerates `docs/software-status.md` (229 rows, every cell populated),
`update-plan.json`, the HTML and the PDF. The plan marks every item either
**eligible** with exact ordered steps, or **excluded** with the rule that
excludes it — the payment path (rule 7/14), WebODM and nodeodm (rule 10), the
production databases (rule 14), and the deliberate Mastodon and ArduPilot
decisions. Nothing is executed by the tooling; applying anything is an operator
decision. Ubuntu archive security updates are already handled automatically by
`unattended-upgrades` and need no action here.

### 12.5.1 The Installed column is ground truth from apt history

The `Installed` column of `docs/software-status.md` is produced by
`apt_date()` in `scripts/build-update/provenance-log.py`, which reads
`/var/log/apt/history.log` and its rotated siblings via
`scripts/build-update/apt_history.py`.

**The install date must come from apt's history log, never from a file mtime.**
dpkg keeps no install timestamp, and `/var/lib/dpkg/info/<pkg>.list` is rewritten
on *every* unpack, so its mtime is the last **upgrade** date — reading it as an
install date would date a long-installed package as newly installed.

apt's history log holds the truth and separates the two cases: every transaction
records `Start-Date`, the exact `Commandline`, and distinct
`Install:` / `Upgrade:` / `Remove:` / `Purge:` lines. Four facts must reach the
document:

| Fact | How it is derived |
|---|---|
| install vs upgrade | the item-line keyword, not a file mtime |
| unattended vs operator-initiated | `Commandline` contains `unattended-upgrade` or a packagekit upgrade role |
| removed / purged | a later `Remove:`/`Purge:` wins over the earlier `Install:`; the cell reads `not installed (removed/purged <date>)` |
| who asked | the `Requested-By:` user, where apt recorded one |

Against the real log:

```
$ python3 scripts/build-update/apt_history.py
packages indexed      : 4445
  installed           : 4281
  upgrade-only (pre-window): 86
  installed unattended: 2098
log files read        : ['history.log.1.gz', 'history.log.2.gz', 'history.log']

$ python3 -c "...install_date('dbeaver-ce')..."
dbeaver-ce   None  Purge   unattended=False  removed=True
nginx        None  Purge   unattended=False  upgraded=2026-08-22  removed=True
rclone       2026-10-03  Install  unattended=False
```

Two honest limits, stated rather than papered over:

* **Coverage is bounded by apt's own log retention.** A package installed before
  the oldest surviving stanza is simply absent from the index. Absent means
  *unknown*, never *not installed* — the 86 upgrade-only records above are
  packages whose install predates the retained window.
* **A removal is not an install date.** For a purged package the function
  returns `(None, record)` so the caller can say *why* the cell is empty rather
  than printing a date for software `dpkg -l` no longer lists.

The dpkg-mtime path remains as a fallback and is labelled as such in the cell
(`(dpkg manifest mtime)`) so the two sources are never confused. A genuine
failure to load `apt_history.py` degrades to that fallback and is remembered so
the cost is paid once.

### 12.5.2 Regression tests for the generators

`scripts/build-update/test_generators.py` — run it with
`python3 scripts/build-update/test_generators.py`; no framework is required,
though `pytest` collects it too. **62 tests, all passing**, in about 0.7 s:

```
$ python3 scripts/build-update/test_generators.py
...
Ran 62 tests in 0.73s

OK
```

Three defect classes must be locked down by tests:

1. **Truncated digests must not become pull commands.** `sha256:` plus 12 hex characters
   would produce `podman pull repo@sha256:<12>`, which a registry rejects with HTTP 400 —
   a command that looks correct and can never work. `is_complete_digest()` checks the
   algorithm *and* the full body length and suppresses command generation entirely.
2. **Steps must be built from the owning package name, never a display name.** A row for
   the application "Account Wizard" must not produce `apt install --only-upgrade Account`,
   which does not exist.
3. **A prose error string must never be used as a digest.** A value such as
   `"upstream digest unreachable (registry refused)"` must yield no command.

The suite also asserts that `update_steps()` rejects a 12-character digest, a value
a nearby assertion already expects to be rejected.

Two further tests exist specifically because the fixes were silent when
reverted. `test_apt_history_loads_regardless_of_working_directory` runs the
generator as a subprocess with `cwd=/tmp`: the original `import apt_history`
resolved against `sys.path`, which holds the **current working directory**, not
the script's own directory — and `refresh-install-log.sh` does `cd "$AO_ROOT"`
first. The module must therefore be loaded by `__file__`, never resolved through
`sys.path`: otherwise the import raises `ImportError`, silently falls back to the dpkg
mtime, and produces a document that looks normal while carrying the wrong dates.
Without the test this failure mode is invisible — a plausible-looking document, not
an error.

### 12.5.3 `eligible` means a machine can do it (OPS-19)

`update-plan.json` must not carry a single `steps` list per item, because two
things cannot be combined: commands an executor could run
(`podman pull repo@sha256:<64>`) and prose no executor could ever run
(`edit Image= in quadlet/<domain>/<unit>.container`). An item must not be marked
**eligible** on the strength of the first while carrying the second — **the file
must distinguish them**, so "eligible" means "automatable".

`update_steps()` returns `{"steps": [...], "manual": [...]}`, and the
`eligible` decision is taken on the strength of `steps` alone:

| Field | Meaning | Contract |
|---|---|---|
| `steps` | argv **arrays**, verb-allowlisted | a machine can run these; nothing needs a shell |
| `manual` | prose for a human | never executed, never silently dropped |

Every step is an argv array (`["podman", "pull", "repo@sha256:<64>"]`), never a
string. This is deliberate: a plan-supplied string can only be run through a
shell, and a plan is generated data, not trusted input. `_argv_is_safe()`
downgrades any argument carrying a shell metacharacter to prose rather than
emitting it — an item literally named `pkg; rm -rf /` produces **no**
executable step and keeps its intent under `manual`.

The consequence is visible and worth stating plainly: the plan reports
**0 eligible of 224**, because an item counts as eligible only when it carries
executable argv steps — never when its only "step" is a sentence about editing a
Quadlet file (§12.5.4, OPS-19).

**Eligibility must be read from the plan, never inferred from the source.** The claim
that "`brave` remains genuinely automatable and is emitted as argv" is false as
stated: `update_steps()` *does* emit argv for `brave` —

```
$ python3 -c "...update_steps({'item':'brave','via':'snap/latest/stable'}, None)"
{'steps': [['snap', 'refresh', 'brave']], 'manual': []}
```

— but the emitted plan shows `"steps": []` for `brave`, because the writer
gates on the decision:

```
"steps": steps if decision == "eligible" else [],
```

`brave`'s verdict is `?`, not `**NO**`: the snap channel was unreachable, so
there is **no evidence of being behind**. It is excluded as *"no evidence of
being behind"*, and the exclusion blanks its steps. The distinction matters,
because the two statements answer different questions. `brave` is the only item
whose *source* admits a mechanical step; it is not eligible *today* because the
evidence for updating it does not exist, not because it is unautomatable.
Written the other way round — "only brave is automatable" — the next reader
would look for the argv in the plan, not find it, and conclude the generator
had regressed.

So the honest summary of this host is **0 eligible of 224, and 0 of those 224
carry a `steps` array**, because every one of them is excluded, and the writer
deliberately refuses to publish steps for an excluded item. Measured:

```
$ python3 -c "... json.load(update-plan.json) ..."
schema 2 items 224
summary {'behind': 1, 'eligible': 0, 'excluded': 224}
with steps 0
with manual 0
```

### 12.5.4 `apply-plan.py` — the dry-run validator (OPS-20)

`scripts/build-update/apply-plan.py` answers one question: *if an operator
approved this plan, what would it touch?* It loads the plan, hashes it,
snapshots it into the run directory, validates every step against a verb
allowlist, derives blast-radius groups (units sharing a digest or a deploy
domain) and reports the result. **It executes nothing**, and the module docstring
states it must never be extended to.

```
$ AO_ROOT=$PWD python3 scripts/build-update/apply-plan.py --no-snapshot
plan        : /tmp/ao-sessions/wt-ops-b/data/build-update/update-plan.json
sha256      : b753e5dab017df1be539b4b86e26713cc1293d9cde1c034ebb376f78aac9453f
generated   : 2026-10-04T16:55:20+00:00   schema: 2
items       : 224  -> 0 eligible, 224 excluded
would run   : 0 argv steps across 0 item(s)
manual only : 0 item(s) need a human
would touch: NOTHING - no item is eligible
EXECUTED    : nothing. This tool is a validator only.
validation  : OK
```

**Why approval must pin to the plan hash, not the filename.** The plan
regenerates on every refresh, so the file an operator approved is not the file a
tool would run — the `generated` timestamp alone changes the bytes when no item
changed. `--expect-hash` refuses anything else, so an approval can name exactly
the bytes that were reviewed:

```
$ AO_ROOT=$PWD python3 scripts/build-update/apply-plan.py --no-snapshot \
      --expect-hash 0000...0000
MISMATCH_EXIT=4
HASH MISMATCH
  approved : 0000...0000
  on disk  : b753e5dab017df1be539b4b86e26713cc1293d9cde1c034ebb376f78aac9453f
```

Exit codes: `0` well-formed, `2` usage, `3` validation failure, `4` hash
mismatch.

The verb allowlist is **duplicated rather than imported**, so the validator
still runs when `provenance-log.py` is broken — the file most likely to be
broken is the one that produced the plan. That duplication is a drift risk, so
`TestVerbAllowlistAgreesAcrossFiles` asserts the two lists are identical.

Run against the **live** `/ALWAYSON` plan the same tool exits **3** with 33
problems, and the diagnosis is in the output:

```
$ python3 scripts/build-update/apply-plan.py --no-snapshot     # AO_ROOT=/ALWAYSON
  - items[128] ao-build-update: no `manual` key; an eligible item must separate prose from executable steps
  - plan: 193 of 199 items carry no `manual` key. This is a schema-1 plan
    (prose and executable steps are not separated). Every eligible step in it is
    a bare string, so nothing in it is safe to hand to an executor -- this is
    OPS-19, not a per-item defect.
```

That is the validator earning its keep: **a schema-1 plan is not safe to hand to an
executor**. Regenerate the live plan with one
`./scripts/build-update/refresh-install-log.sh` before citing it.

**A trap worth recording for the next agent.** The validator defaults `AO_ROOT`
to `/ALWAYSON`, so running it from a worktree validates **the live main-repo
plan, not your worktree's** — silently, with a plausible-looking result. This trap is easy to hit
this: a first run reported 199 items and schema 1 while the worktree plan held
224 items and schema 2. Always pass `AO_ROOT=$PWD`, and sanity-check the
`plan :` line in the output against the file you meant. The same class of bug
existed literally in `refresh-install-log.sh`, whose summary-report heredoc
opened a hardcoded `/ALWAYSON/data/build-update/update-plan.json` while the
surrounding script honoured `AO_ROOT`; it takes the path as `sys.argv[1]`.

### 12.5.5 Image digests are checked against what is deployed (OPS-02)

`config/platform/version-matrix.yaml` records image digests as free text in
YAML strings. Nothing compared those strings to anything, so a row could only
change by a hand edit, and a stale row was indistinguishable from a correct one
by reading it. `capture-version-matrix.sh` does not help: it rewrites five host
facts (systemd, podman, netplan, nvidia) with `sed` and never looks at an
image at all.

The check is `scripts/validation/check-image-digests.sh`. It must be run before the
matrix is cited, and it reports drift in three directions — matrix rows whose digest no
deployed unit carries, deployed images that are not digest-pinned, and deployed digests
absent from the matrix:

```
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
UNLISTED  deployed but absent from the matrix: sha256:d74eeac9a635...   (postgres, 3 units)
UNLISTED  deployed but absent from the matrix: sha256:c6eabf748fc7...   (redis, 2 units)
UNLISTED  deployed but absent from the matrix: sha256:9acc6d4df749...   (foxglove)
UNLISTED  deployed but absent from the matrix: sha256:55f8dbcf8dec...   (gz-sim10-server)
RESULT: DRIFT -- 7 stale matrix row(s), 1 unpinned deployed image(s).
$ echo $?
1
```

The postgres row is the clearest case, and the reason a naive check is not
enough. The matrix records `docker.io/library/postgres@sha256:a65e6a84…` in
two rows — `sales.mastodon.image_postgres` and
`operations.image_postgres_shared` — while **all three** deployed postgres
units (`ao-fabrication-db`, `ao-mastodon-db`, `ao-sales-db`) run
`sha256:d74eeac9…`. Nothing is wrong with either digest; the document and the
live system simply stopped agreeing, and neither could tell the other had
moved.

**Why the check reads the deployed units and not the repository tree.**
Quadlet deploys **flat**: `~/.config/containers/systemd/` holds copies, not
symlinks. Comparing the matrix against `quadlet/` would have reported "no
drift" at precisely the moment the live system had drifted — the repository
copy can be correct while the unit that is actually running is not. The
deployed unit is the only thing that describes what is running, so it is the
authority here.

**The check reports; it never rewrites.** Where a row disagrees with the live
system, deciding which side is right is an operator judgement — it may be a
stale document, an unapproved deploy, or a deliberate change never recorded. A
script that adopted the live digest would make the matrix self-fulfilling and
launder a hand edit into an apparently-captured fact. So the seven rows above
are **reported as findings, not fixed**. That is deliberate, and it is the
part most likely to look like incompleteness.

**The check must not abort silently.** When every deployed image is unpinned, the
digest-extracting `grep` matches nothing and exits 1; under `set -e` + `pipefail` that
would abort the script with **status 1 and no output at all**. A gate that fails without
saying why is worse than no gate, because the next reader cannot tell a real finding from
a crash. The collection step therefore tolerates the empty result rather than loosening
`set -e`, because the unpinned images are precisely what the script most needs to report.

That is why the five tests drive the **real script** against a synthetic tree
and assert exit codes, rather than testing a Python reimplementation: a check
only ever observed in its failing state proves nothing, because "7 rows
drifted" is exactly what a broken comparison prints too.

```
$ python3 -m pytest scripts/build-update/test_generators.py -q
62 passed in 0.73s
```

Five cases, and the OK path is exercised as carefully as the failing ones:

| Case | Asserts |
|---|---|
| matrix matches deployed | `RESULT: OK`, exit **0** |
| one stale matrix row | `DRIFT` naming `host.images.a`, exit **1** |
| `Image=…:latest` | `UNPINNED`, exit **1** |
| `sha256:` + 12 hex chars | `UNPINNED`, exit **1** |
| stale row, no `--check` | `RESULT: DRIFT` but exit **0** |

The fourth case is the §12.5.2 lesson reused: a `sha256:` prefix is not a
pinned reference, and the same class of bug that produced
`podman pull repo@sha256:<12>` would otherwise let a 12-character digest pass
here. The fifth case exists because a validation script that *always* exits
non-zero stops being run — so reporting is the default and `--check` is the
gate, and that distinction has to live in the exit code rather than only in
the prose.

### 12.5.6 Roll-ups can be drilled into (OPS-23)

`KDE Plasma Desktop` was one row for 191 components, the Ubuntu archive one row
for 3,857 packages, the ROS train one row for 351. "Is the desktop behind" is
answerable; "update ROS 2 rviz" is not. Collapsing those rows is right — they
were 90 percent of the document — but a collapsed row that hides its members is
a dead end. Each roll-up carries a `members` list and renders it as a
`<details>` drill-down, in Markdown, HTML **and** the PDF:

```
$ grep -o '<summary>[^<]*</summary>' /tmp/ops23v/s.md
<summary>Rolled-up launchers — expand to list every application entry (153 entries across 34 groups)</summary>
<summary>Ubuntu archive packages — expand to list all 3857 packages with their installed versions</summary>
<summary>ROS 2 lyrical (whole train) — expand to list all 351 packages with their installed versions</summary>
<summary>KDE Plasma Desktop — expand to list all 191 components</summary>

$ grep -c "details class='drill'" /tmp/ops23v/s.html
38
```

Reproduce with a scratch render, which touches nothing tracked:

```
$ AO_ROOT=$PWD python3 scripts/build-update/provenance-log.py --offline \
      --out /tmp/ops23v/s.md --html /tmp/ops23v/s.html --plan /tmp/ops23v/p.json
```

**A trap here.** The tracked render artifacts `docs/software-status.md` and
`tmp/software-status.html` must be regenerated by the current generator before
they are used as evidence: a render predating a generator fix rolls up but shows
**0** drill-downs, which reads exactly like "the fix does not work":

```
$ grep -o '<summary>[^<]*</summary>' docs/software-status.md
<summary>Rolled-up launchers — expand to list every application entry (153 entries across 34 groups)</summary>
<summary>KDE Plasma Desktop — expand to list all 191 components</summary>
$ grep -c "details class='drill'" tmp/software-status.html
0
```

Both apt roll-ups are missing there too, which is the §12.5.5 pattern in a
different guise: the code is correct and the artifact predates it. The
committed documents must be regenerated before they are cited, or the shipped PDF
collapses those rows to bare counts — which is why the evidence above comes from a
scratch render rather than from the tracked files: the claim is about the generator.

The HTML drill-down is inline on the row itself, where the count promised it,
and carries every member as its own `<li>`.

Members are rendered with their **own versions** (`libc6 (2.42-1)`), which is
what OPS-23 asks for; a bare list of names would answer "which" but not "which
version".

**The failure this item describes was silent, which is why it was easy to miss.**
The members were computed and carried on the row as `members`, but the HTML
table renderer never emitted them — so the drill-down existed in Markdown only
and the HTML and PDF quietly lost it. Nothing errored; the document just stopped
being able to answer a question. `TestRollupsCanBeDrilledInto` asserts the HTML
path specifically, and that the drill-down survives the print stylesheet,
because a PDF that hides it reintroduces the same dead end. Member names are
HTML-escaped: they come from `.desktop` files on disk and are not trusted.

The two apt roll-ups must carry their members — verify the rendered output rather than
trusting the code: `Ubuntu archive packages` and `ROS 2 lyrical (whole train)` SHALL NOT
render as bare counts. Both lists are already in `inv`, so both attach theirs; the ROS one
matters most because the train is FROZEN, making "which 351 packages are affected" the
question an operator will actually ask. `test_the_apt_rollups_carry_their_members` is the
guard, and it is not vacuous: deleting both `members` keys fails it with
`Ubuntu archive packages is a roll-up with no members`.

**A roll-up must be scannable, not merely reachable.** Members must not be joined into a
single table cell (`', '.join(members)`) — that renders the Ubuntu archive as **one
40,000-character line**, which satisfies "the members are reachable" and fails the reader
as badly as the original count: a single row you cannot scan is not a drill-down. Package
roll-ups render one member per row with the version in its own column, in their own
collapsible block; the launcher grouping keeps its joined cell, where members are short and
few. The roll-up emitter is extracted from `render()` into `rollup_details_md()` so this
is unit-testable — `render()` spends hundreds of apt round trips, which no test
needs to pay to assert a formatting rule.

---
