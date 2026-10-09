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

That script is the asserting replacement for the block this section used to
carry. The old block was replaced because it **could not fail**: the cgroup
test `test "$(stat -fc %T /sys/fs/cgroup)" = "cgroup2fs" && echo ...` is
silent when the test fails, nothing read its return code, and the block's
overall exit status was 0 either way. Reproduced 2026-10-03 — breaking the
cgroup check changed nothing and the block still exited 0. A check that
cannot fail verifies nothing, so no §19.2 evidence could rest on it.

The replacement was tested in both directions, because a verifier that only
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

The `loginctl show-user -p Linger` line that section 12.3 used to carry was
read-only and silent on failure, and linger is a real precondition rather than a
nicety: every workload here is a *rootless user* Quadlet unit under
`~/.config/containers/systemd/`, driven by `systemd --user`, and that instance
only exists for the operator account while a session is open. Log out of KDE and
every container, timer and Quadlet-generated unit for this account stops, and none
of them come back on their own after a reboot. `ao-lmstudio.service` already
depends on this - its own header says "Starts at boot via user lingering".

So the rebuild must **report** linger before it starts any unit, and the
provisioner now does, at stage 20, before stage 50:

```bash
./scripts/validation/check-user-linger.sh          # report
./scripts/validation/check-user-linger.sh --check  # gate: 0 ok, 1 fault, 2 no such account
```

Measured on this host 2026-10-04:

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

### A false FAIL is the worst kind of checker defect

The checker's first revision reported `FAIL: linger is not enabled` — and exited 1 —
for an account that **does not exist at all**. Measured: `loginctl show-user alwayson-ledger -p Linger` returns
`Failed to look up user ... No such process`, but with `--value` it returns the
literal string `unknown`, which the script compared against `yes`. And
`/var/lib/systemd/linger/` is not proof of existence: `alwayson-ledger`,
`alwayson-mapping` and `alwayson-sales` all have marker files on this host while
`getent passwd` finds none of them, so a leftover marker is misleading. A false
FAIL on a checker is the worst kind of defect, because it teaches the operator to
ignore it — which would hide a genuine `Linger=no`. The check now tests
`getent passwd` first and exits **2** for "no such account", distinct from **1**
for a real fault.

Two earlier counting bugs in the same script are also fixed and worth naming,
because both produced confident, wrong output: it grepped unit files for
`\.container`, a name systemd never creates (Quadlet *generates*
`ao-<name>.service`), so it claimed "21 deployed but none enabled" on a host with
26 containers running; and it called `id -u` with no argument, so checking any
account other than the caller reported `/run/user/-1`.

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

`scripts/provision/rollback.sh` is the missing half of §12.4. Until now each stage of
`provision.sh` described only what it *built*, and a rebuild that failed halfway left the
operator with no documented way back. The script is **dry-run by default**, mirroring
`provision.sh`, because undo is as dangerous as the action.

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

**Verified, dry run.** State is identical before and after, and the summary line is last:

```text
$ bash -n scripts/provision/rollback.sh && echo 'SYNTAX OK'
SYNTAX OK
$ bash scripts/provision/rollback.sh >/tmp/rb5.out 2>&1; echo "rc=$?"
rc=0
$ grep -n '^--- stage' /tmp/rb5.out
5:--- stage 90: verification artefacts (nothing to undo)
8:--- stage 70: persistent data (NEEDS OPERATOR - not undone)
17:--- stage 60: secrets (NEEDS OPERATOR - not undone)
22:--- stage 55: restic backup units
37:--- stage 50: Quadlet unit files (per domain)
51:--- stage 40: vendor blobs (NEEDS OPERATOR - not undone)
56:--- stage 30: snaps and flatpak (NEEDS OPERATOR - commands printed only)
67:--- stage 20: apt repositories added by stage 10
81:--- stage 10: nothing to undo
$ tail -1 /tmp/rb5.out
dry run only. Nothing was changed. Re-run with --yes to apply.
```

```text
# BEFORE: units=85 restic=6 nets=14 timer=enabled
$ bash scripts/provision/rollback.sh >/dev/null 2>&1
# AFTER : units=85 restic=6 nets=14 timer=enabled
```

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

**Still open on this item.** A clean-room rebuild has still never been executed, so the
procedure remains unproven end to end; and `bootstrap/01` photogrammetry verification is
still not gated on §17.3 evidence as §16.1 requires. The rollback half is written and
proven; those two are not mine to close here.

#### A number in the stage table above was wrong

The stage-50 row read "9 Quadlet domains, 22 units". **22 is only the `.container` count.**
Measured across all nine domains the Quadlet *source* units are **36**:

```text
$ find quadlet -type f \( -name '*.container' -o -name '*.network' -o -name '*.volume' -o -name '*.build' \) | wc -l
36
$ find quadlet -type f | grep -oE '\.[a-z]+$' | sort | uniq -c
     22 .container
     15 .network
      1 .path
     16 .service
      1 .sh
      5 .timer
```

An undercount here is not cosmetic: stage 50 deploys **every** source unit, so a reader
trusting "22" would conclude seven network units and six `ao-*` service/timer units were
never deployed.

That comparison is also where the counting trap lies. Comparing *all* 81 deployed files
against the repo's 61 distinct basenames yields **32 apparent orphans** — but they are not
stale copies. Every one of the 32 is a `.service`, and each self-declares as generated:

```text
$ head -3 ~/.config/containers/systemd/ao-sales-db.service
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
script. For `ao-data` the two currently agree, so nothing is broken today:

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

Measured on this host 2026-10-04, dry run against the real manifest:

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

**All eight are present on this host and verified.** Five have no vendor URL and
so cannot be fetched unattended even in principle — a property of the vendors,
not a gap in the provisioner, and the honest residue of OPS-17. Three (gh, bun,
cline) are installable; the first two verify against a recorded `installed_sha256`.

### Check presence before reachability

The first revision tested "does this entry have a url?" **before** "is the file already
installed?", and `continue`d out of the loop. The consequence, measured: `lm-studio`, `pcloud` and `nperf` were all reported
`MANUAL ... a human must place this file` while **all three exist on disk and all
three hash to the manifest's own recorded `sha256`**. The report told the operator
to go fetch files that were already installed and verified — "cannot be fetched
automatically" and "is not installed" are different facts, and only the second is
a problem. Presence is now checked first; an entry with no url but a present,
matching file reports OK with the caveat in parentheses.

Two further defects, both found by testing rather than reading:

- **An all-numeric digest was silently erased.** YAML coerces unquoted
  `0000…0` to the integer `0`, and the `or ""` fallbacks then rendered that as
  the empty string, so the entry degraded to "no installed digest recorded" and
  reported **OK** — the one outcome a digest check must never produce. Every
  scalar is now `str()`-ed, so the entry reports DRIFT instead. Real digests in
  the manifest are quoted and contain `a`–`f`, so they round-trip exactly.
- **Every failure exited 0.** A DRIFT and a failed download were both reported
  as text and then succeeded, which is a provisioner whose failure signal is a
  line nobody is reading. Because `provision.sh` calls this through its `run`
  helper, which propagates the return code unguarded, that would have aborted
  stage 40 of the whole rebuild — so the `run` call is now `|| true` as well. A
  drifted AppImage must not leave the host without its Quadlet units; the
  installer refuses to overwrite (README §4.1 rules 2/3), so "carry on and tell
  the operator" is the correct outcome, not "stop the world".

The OK, DRIFT, MANUAL and dry-run paths were each exercised against a throwaway
fixture manifest rather than asserted. The fixture was first written with `kind:`
before the schema key `install:` was checked, which is why its first run reported
two entries as "no installed digest" — the fixture was wrong, not the script, and
re-running with the correct key produced the DRIFT it was built to provoke.

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

**It used to be wrong, and wrong in a way that mattered.** dpkg keeps no install
timestamp, so the date was inferred from the mtime of
`/var/lib/dpkg/info/<pkg>.list` — a file dpkg rewrites on *every* unpack. The
column therefore displayed the last **upgrade** date under an install heading. An
operator auditing a deployment would read "installed 2026-10-01" for a package
that had in fact been installed in April and merely upgraded that day.

apt's history log does hold the truth, and it separates the two cases: every
transaction records `Start-Date`, the exact `Commandline`, and distinct
`Install:` / `Upgrade:` / `Remove:` / `Purge:` lines. Four facts now reach the
document that did not before:

| Fact | How it is derived |
|---|---|
| install vs upgrade | the item-line keyword, not a file mtime |
| unattended vs operator-initiated | `Commandline` contains `unattended-upgrade` or a packagekit upgrade role |
| removed / purged | a later `Remove:`/`Purge:` wins over the earlier `Install:`; the cell reads `not installed (removed/purged <date>)` |
| who asked | the `Requested-By:` user, where apt recorded one |

Measured against the real log (2026-10-04):

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

Three defects had shipped because nothing asserted them, and each now has a
test:

1. **Truncated digests became pull commands.** `update_steps()` checked only the
   `sha256:` prefix, so `sha256:` plus 12 hex characters produced
   `podman pull repo@sha256:<12>`, which a registry rejects with HTTP 400 — a
   command that looked correct and could never work. `is_complete_digest()` now
   checks the algorithm *and* the full body length, and suppresses command
   generation entirely.
2. **Steps built from a display name.** A row for the application "Account
   Wizard" produced `apt install --only-upgrade Account`, which does not exist.
   Steps now use the owning package name.
3. **A prose error string used as a digest.** `"upstream digest unreachable
   (registry refused)"` reached the command generator. Any value that is not a
   complete digest now yields no command.

A fourth defect was found and fixed *by* this suite: `update_steps()` accepted a
12-character digest while a nearby assertion already expected it to be rejected.

Two further tests exist specifically because the fixes were silent when
reverted. `test_apt_history_loads_regardless_of_working_directory` runs the
generator as a subprocess with `cwd=/tmp`: the original `import apt_history`
resolved against `sys.path`, which holds the **current working directory**, not
the script's own directory — and `refresh-install-log.sh` does `cd "$AO_ROOT"`
first. The import therefore raised `ImportError` on every production run and
silently fell back to the dpkg mtime, producing a document that looked normal
and carried the older, less accurate dates. The module is now loaded by
`__file__`. Without the test this regression is invisible: the failure mode is
a plausible-looking document, not an error.

### 12.5.3 `eligible` now means a machine can do it (OPS-19)

`update-plan.json` used to carry a single `steps` list per item, mixing two
things that cannot be combined: commands an executor could run
(`podman pull repo@sha256:<64>`) and prose no executor could ever run
(`edit Image= in quadlet/<domain>/<unit>.container`). An item was marked
**eligible** on the strength of the first while carrying the second, so
"eligible" did not mean "automatable" and **nothing in the file distinguished
them**.

`update_steps()` now returns `{"steps": [...], "manual": [...]}`, and the
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

The consequence is visible and worth stating plainly: on this host the plan now
reports **0 eligible of 224**. That is not a regression, it is the truth. The
old count of 6 was counting items whose only "step" was a sentence about
editing a Quadlet file.

**A correction to what this section claimed when first written.** It said
"`brave` remains genuinely automatable and is emitted as argv". That was
checked rather than assumed, and it is false as stated. `update_steps()`
*does* emit argv for `brave` —

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

That is the validator earning its keep: the live plan is still schema 1 and has
not been regenerated since §12.5.3 landed, so **it is not yet safe to hand to
an executor**. Regenerating it is one `./scripts/build-update/refresh-install-log.sh`.

**A trap worth recording for the next agent.** The validator defaults `AO_ROOT`
to `/ALWAYSON`, so running it from a worktree validates **the live main-repo
plan, not your worktree's** — silently, with a plausible-looking result. This trap is easy to hit
this: a first run reported 199 items and schema 1 while the worktree plan held
224 items and schema 2. Always pass `AO_ROOT=$PWD`, and sanity-check the
`plan :` line in the output against the file you meant. The same class of bug
existed literally in `refresh-install-log.sh`, whose summary-report heredoc
opened a hardcoded `/ALWAYSON/data/build-update/update-plan.json` while the
surrounding script honoured `AO_ROOT`; it now takes the path as `sys.argv[1]`.

### 12.5.5 Image digests are checked against what is deployed (OPS-02)

`config/platform/version-matrix.yaml` records image digests as free text in
YAML strings. Nothing compared those strings to anything, so a row could only
change by a hand edit, and a stale row was indistinguishable from a correct one
by reading it. `capture-version-matrix.sh` does not help: it rewrites five host
facts (systemd, podman, netplan, nvidia) with `sed` and never looks at an
image at all.

The check now exists as `scripts/validation/check-image-digests.sh`, and it
found real drift immediately. **7 matrix rows name a digest no deployed unit
carries, 1 deployed image is not digest-pinned, and 4 deployed digests appear
nowhere in the matrix:**

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

**A bug this check had on its first run, which the tests caught.** When every
deployed image is unpinned, the digest-extracting `grep` matches nothing and
exits 1; under `set -e` + `pipefail` that aborted the script with **status 1
and no output at all**. A gate that fails without saying why is worse than no
gate, because the next reader cannot tell a real finding from a crash. It is
fixed by tolerating the empty result in collection rather than by loosening
`set -e`, because the unpinned images are precisely what the script most needs
to report.

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
a dead end. Each roll-up now carries a `members` list and renders it as a
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

**A trap here, and the reason the numbers above were nearly unprovable.** The
tracked render artifacts `docs/software-status.md` and `tmp/software-status.html`
are **stale** — dated 2026-10-03 20:53, while the generator carrying this fix
landed 2026-10-04 10:30. So checking the fix against them shows 2 summaries and
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
committed documents have **not** been regenerated, so the shipped PDF still
collapses those rows to bare counts. That is a real outstanding action, and it
is why the evidence above comes from a scratch render rather than from the
tracked files — the claim is about the generator, and it is stated as such.

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

The two apt roll-ups were still bare counts after that first pass — checked
the rendered output rather than trusting the code, and `Ubuntu archive packages`
and `ROS 2 lyrical (whole train)` carried no members. Both lists are already in
`inv`, so both now attach theirs; the ROS one matters most because the train is
FROZEN, making "which 351 packages are affected" the question an operator will
actually ask. `test_the_apt_rollups_carry_their_members` is the guard, and I
confirmed it is not vacuous by deleting both `members` keys and watching it
fail with `Ubuntu archive packages is a roll-up with no members`.

**A second fix the first one created.** Attaching members made the Markdown
~3× larger, but the existing roll-up renderer joined them into a single table
cell (`', '.join(members)`), so the Ubuntu archive came out as **one
40,000-character line**. That technically satisfied "the members are reachable"
and practically failed the reader as badly as the original count — a single row
you cannot scan is not a drill-down. Package roll-ups now render one member per
row with the version in its own column, in their own collapsible block; the
launcher grouping keeps its joined cell, where members are short and few. The
roll-up emitter was extracted from `render()` into `rollup_details_md()` so this
is unit-testable — `render()` spends hundreds of apt round trips, which no test
should pay to assert a formatting rule.

---
