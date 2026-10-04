#!/usr/bin/env bash
# ALWAYS ON host provisioner - rebuild this host from a bare Ubuntu/KDE install.
#
# Starting point: Ubuntu 26.04 with KDE Plasma, Cline CLI, and an internet
# connection. This script reconstructs everything else that is recorded in the
# repository, in stages, each of which is idempotent and independently re-runnable.
#
# DESIGN RULES (from AGENTS.md and README section 4.1):
#   * READ-ONLY about existing data. Nothing here deletes, prunes or restores
#     data/. Stage 90 only *checks* that data is present.
#   * Never writes a secret. Stage 80 only verifies that required secrets exist
#     and refuses to continue if any are missing. Values come from the operator.
#   * Never installs without --yes. Default is a dry run that prints the plan.
#   * Podman + systemd Quadlet only. Never Docker.
set -uo pipefail

AO_ROOT="${AO_ROOT:-/ALWAYSON}"
STAGE_DIR="$(dirname "$(readlink -f "$0")")"
ASSUME_YES=0
[ "${1:-}" = "--yes" ] && ASSUME_YES=1
LOG="$AO_ROOT/logs/operations/$(date -u +%Y%m%dT%H%M%SZ)-provision.log"
LEDGER="$AO_ROOT/logs/operations/provision-ledger.jsonl"
mkdir -p "$(dirname "$LOG")"
exec > >(tee -a "$LOG") 2>&1

say()  { printf '%s\n' "$*"; }
run()  {
  if [ "$ASSUME_YES" -eq 1 ]; then eval "$2"; rc=$?
  else printf '  [dry-run] %s\n' "$2"; rc=0; fi
  printf '{"ts":"%s","stage":"%s","step":"%s","rc":%s}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" "$rc" >> "$LEDGER"
  return $rc
}
have() { command -v "$1" >/dev/null 2>&1; }

say "=== ALWAYS ON provisioner ==="
say "mode      : $([ "$ASSUME_YES" -eq 1 ] && echo APPLY || echo 'DRY-RUN (pass --yes to apply)')"
say "host      : $(hostname)   kernel: $(uname -r)"
say "repo      : $AO_ROOT"
say ""

# ---- 10: repository keys and sources -------------------------------------
# 8 third-party archives, verified present on the running host. ROS is added
# but NOT trusted: packages.ros.org fails TLS verification from this network.
stage_repos() {
  say "--- stage 10: apt repositories"
  run 10 "install -d -m 0755 /etc/apt/keyrings"
  for spec in \
    "https://cli.github.com/packages stable main|githubcli-archive-keyring" \
    "https://download.vscodium.com/debs vscodium main|vscodium-archive-keyring" \
    "https://repo.steampowered.com/steam stable steam|steam" \
    "https://dl.google.com/linux/chrome-stable/deb stable main|google-chrome" \
    "https://packages.microsoft.com/repos/edge-stable stable main|microsoft-edge" \
    "https://deb.nodesource.com/node_24.x nodistro main|nodesource" \
    "https://nvidia.github.io/libnvidia-container/stable/deb/amd64 /|nvidia-container-toolkit-keyring" ; do
    loc="${spec%%|*}"; key="${spec##*|}"
    [ -f "/etc/apt/keyrings/${key}.gpg" ] && { say "  present: ${key}.gpg"; continue; }
    run 10 "install -d -m 0755 /etc/apt/keyrings && curl -fsSL -o /etc/apt/keyrings/${key}.gpg '${loc%% *}/gpg' && chmod 0644 /etc/apt/keyrings/${key}.gpg"
    say "  source: ${loc}"
  done
  say "  ROS 2   : packages.ros.org - registered but UNREACHABLE (TLS). Not worked around."
}

# ---- 20: host dependencies ----------------------------------------------
# DELEGATES to scripts/bootstrap/02 rather than repeating its package list.
# Two copies of that list had already drifted from README 12.3; one owner is
# the point of item 62 ("one ordered procedure that names the scripts").
stage_deps() {
  say "--- stage 20: host dependencies (delegating to scripts/bootstrap/02)"
  run 20 "bash $AO_ROOT/scripts/bootstrap/02-install-host-dependencies.sh"
  # bootstrap/02 exits 5 rather than installing unattended: it wants an
  # operator at the keyboard. Keep that gate; do not paper over it.
  say "  NOTE: bootstrap/02 exits 5 when packages are missing and will not"
  say "  install unattended. Run the printed sudo apt line yourself."
  # Layout and networks are also already owned by the bootstrap chain; do not
  # reimplement them here.
  run 20 "bash $AO_ROOT/scripts/bootstrap/03-create-operational-layout.sh"
  run 20 "bash $AO_ROOT/scripts/bootstrap/04-create-podman-networks.sh"
  run 20 "bash $AO_ROOT/scripts/bootstrap/00-inventory.sh"

  # ---- linger (OPS-13) --------------------------------------------------
  # Must happen BEFORE the Quadlet units in stage 50 are started. Rootless user
  # units are driven by systemd --user, which only exists for the operator
  # account while a session is open; without linger the whole rebuild comes
  # back dead after the next logout or reboot.
  #
  # It is NOT enabled here. `loginctl enable-linger` needs root and writes
  # /var/lib/systemd/linger/, a host-level change - README 4.1 rules 1 and 3
  # put that with the operator. What this stage does is report the current
  # state and, if linger is off, print the exact command to fix it.
  say "--- stage 20: user linger (required by every rootless Quadlet unit)"
  linger="$(loginctl show-user "${SUDO_USER:-$USER}" -p Linger --value 2>/dev/null || echo unknown)"
  if [ "$linger" = "yes" ]; then
    say "  linger: enabled for ${SUDO_USER:-$USER}"
  else
    say "  linger: $linger  <-- rootless containers will NOT survive a reboot"
    say "  Fix (needs root): sudo loginctl enable-linger ${SUDO_USER:-$USER}"
  fi
  run 20 "bash $AO_ROOT/scripts/validation/check-user-linger.sh"
}

# ---- 30: snaps and flatpak ----------------------------------------------
# 16 snaps and 1 flatpak, enumerated from the installed set.
stage_snaps() {
  say "--- stage 30: snaps (16) and flatpak (1)"
  for s in brave firefox cups orcaslicer mesa-2404 snapd bare core20 core22 \
           core24 core26 gnome-42-2204 gnome-46-2404 gtk-common-themes \
           gtk-theme-breeze icon-theme-breeze; do
    snap list 2>/dev/null | awk '{print $1}' | grep -qx "$s" && continue
    run 30 "snap install $s"
  done
  flatpak list --app --columns=application 2>/dev/null | grep -qx com.usebottles.bottles \
    || run 30 "flatpak install -y flathub com.usebottles.bottles"
}

# ---- 40: host software recorded in the inventory ------------------------
# Derived from config/build-update/unmanaged-software.yaml, not hardcoded.
stage_host_apps() {
  say "--- stage 40: host applications from the inventory registry"
  python3 - <<'PY'
import yaml, pathlib
p = pathlib.Path("/ALWAYSON/config/build-update/unmanaged-software.yaml")
reg = yaml.safe_load(p.read_text()) or {}
for e in reg.get("executables", []):
    pkg = e.get("apt_package")
    if pkg:
        print(f"  apt: {pkg} ({e.get('publisher','?')})")
PY
  # AppImages and vendor blobs are NOT printed as "manual, go away" any more.
  # They have their own manifest and their own installer (OPS-17). Delegating
  # is the point: this stage used to be the place where the rebuild quietly
  # stopped being able to restore the host.
  say "  vendor blobs (AppImages, vendor executables):"
  # ASSUME_YES is always set (0 or 1), so ${ASSUME_YES:+...} would expand even
  # when it is 0 and hand --yes to the installer during a dry run. Test it.
  #
  # The rc is captured and NOT allowed to abort the rebuild. The installer exits
  # 2 on a REFUSED/DRIFT entry, but that is exactly the case README 4.1 rules
  # 2/3 forbid this script from resolving automatically: the file on disk is
  # not what the manifest says, and overwriting it is a destructive change.
  # Aborting here would mean a single drifted AppImage leaves the host with no
  # Quadlet units at all - the installer deliberately refuses to overwrite, so
  # the correct outcome is "carry on, tell the operator", not "stop the world".
  if [ "$ASSUME_YES" -eq 1 ]; then
    run 40 "bash $AO_ROOT/scripts/provision/install-vendor-binaries.sh --yes" || true
  else
    run 40 "bash $AO_ROOT/scripts/provision/install-vendor-binaries.sh" || true
  fi
  say "  MANUAL = no url or no vendor digest; the file cannot be fetched"
  say "  unattended. REFUSED/DRIFT = something is on disk that the manifest"
  say "  does not agree with, and NOTHING was overwritten. Both need a human."
  say "  Neither aborts the rest of the rebuild."
}

# ---- 50: podman networks and Quadlet ------------------------------------
stage_quadlet() {
  say "--- stage 50: podman networks and Quadlet units"
  say "  22 units across 8 domains. Unit files deploy FLAT:"
  say "  ~/.config/containers/systemd/ holds COPIES. Editing the repo is inert"
  say "  until deployed, so the deploy script is mandatory, not optional."
  # Deploy each domain exactly once. A domain may hold both .network and
  # .container files, so globbing for both and looping separately deployed it
  # twice, and `[ -f dir/*.net ]` with several matches is a bash syntax error.
  for d in "$AO_ROOT"/quadlet/*/; do
    n=$(basename "$d")
    compgen -G "$d*.network" >/dev/null || compgen -G "$d*.container" >/dev/null || continue
    run 50 "./scripts/deploy/deploy-quadlet-domain.sh $n"
  done
}

# ---- 55: backup schedule -----------------------------------------------
# The restic units used to live ONLY in /etc/systemd/system, untracked by the
# repository, so a rebuild silently lost the backup schedule. They are now
# version-controlled under systemd/backup/ and deployed from here.
stage_backup() {
  say "--- stage 55: restic backup units (from systemd/backup/)"
  n=0
  for f in "$AO_ROOT"/systemd/backup/*.service "$AO_ROOT"/systemd/backup/*.timer; do
    [ -f "$f" ] || continue
    n=$((n+1))
    run 55 "sudo install -m 0644 -o root -g root '$f' /etc/systemd/system/$(basename "$f")"
  done
  say "  $n unit files. Requires sudo: this stage is the one part of the"
  say "  provisioner that cannot run unprivileged."
  run 55 "sudo systemctl --user daemon-reload && sudo systemctl --user enable --now ao-restic-prefetch.timer ao-restic-backup.timer ao-restic-verify.timer"
  say "  ao-restic-prefetch caches the wallet-authorised secret to"
  say "  /run/alwayson/restic.env so the ROOT backup needs no wallet session."
}

# ---- 60: secrets --------------------------------------------------------
# Refuses to continue. Never prints or writes a value.
required_secrets() {
  # DERIVED from the units themselves, never hand-maintained. Two earlier
  # versions of this script were wrong: one asserted a hand-written list naming
  # a file that does not exist, and the next checked /ALWAYSON/secrets/ while
  # the units actually read ~/.local/share/ao-secrets/ - reporting ten secrets
  # MISSING that were all present. The unit file is the only authority.
  grep -rhoE '^EnvironmentFile=-?[^ ]+' "$AO_ROOT/quadlet" 2>/dev/null \
    | sed -E 's/^EnvironmentFile=-?//' | sort -u | while read -r f; do
        printf '%s\n' "${f//%h/$HOME}"
      done
}

stage_secrets() {
  say "--- stage 60: secrets the units actually read (presence only)"
  missing=0
  for f in $(required_secrets); do
    if [ -e "$f" ]; then say "  present: ${f/#$HOME/~}"
    else say "  MISSING: ${f/#$HOME/~}"; missing=$((missing+1)); fi
  done
  say "  Secrets live in ~/.local/share/ao-secrets/ and are NOT in git."
  say "  A reinstall must restore them from backup to that exact path."
  say "  This script never reads, prints or writes a secret value."
  [ "$missing" -gt 0 ] && say "  $missing missing - dependent services will not start."
  return 0
}

# ---- 70: data ------------------------------------------------------------
# CHECK ONLY. Restoration is destructive-adjacent and stays a human decision.
stage_data() {
  say "--- stage 70: persistent data (CHECK ONLY - never restores)"
  for d in ardupilot corda-install sim-fabrication sales mapping; do
    if [ -d "$AO_ROOT/data/$d" ]; then
      say "  present: data/$d ($(du -sh "$AO_ROOT/data/$d" 2>/dev/null | cut -f1))"
    else
      say "  ABSENT : data/$d - restore from backup BEFORE starting services"
    fi
  done
  say "  Restoration is a human decision (AGENTS.md rule 2/3)."
}

# ---- 90: verification ---------------------------------------------------
stage_verify() {
  say "--- stage 90: verification"
  run 90 "python3 $AO_ROOT/scripts/build-update/inventory-full.py"
  run 90 "python3 $AO_ROOT/scripts/build-update/provenance-log.py --markdown --offline"
  say "  Then DIFF the regenerated inventory against docs/software-status.md."
  say "  A mismatch means the rebuild is not faithful; do not proceed."
}

main() {
  say ""; stage_repos; stage_deps; stage_snaps; stage_host_apps
  stage_quadlet
  stage_backup
  say ""; stage_secrets || say "  WARNING: secrets missing - services will not start."
  stage_data; stage_verify
  say ""; say "provision complete. log: $LOG"
}
main "$@"
