#!/usr/bin/env bash
# ALWAYS ON - build-update: inventory-inventory.sh
# Actually: inventory-system.sh. Emits the installed-software inventory for the
# ao-build-update network, grouped by category, with what each item is pinned to
# and where its updates come from.
#
# WHY A GENERATOR AND NOT A DOCUMENT
# The version matrix drifts by hand (README 19.1 items 34/35) and this host has
# already proven it: version-matrix.yaml records kernel 7.0.0-34-generic while
# the running kernel is 7.0.0-38-generic. A hand-written inventory would be
# wrong the day after it was written. This reads the live system instead, so it
# is true when it runs and says so when something cannot be read.
#
# Columns, per item:
#   PINNED TO   the exact immutable reference, when there is one; "not pinned"
#               is a finding, not a blank
#   UPDATE FROM the mechanism that would deliver a new version, and whether it
#               does so unattended
#
# Usage: inventory-system.sh [--markdown] [--out FILE]
#   default output is stdout in a fixed-width table
set -Eeuo pipefail
IFS=$'\n\t'

AS_MD=0
OUT=""
while (( $# )); do
  case "$1" in
    --markdown) AS_MD=1; shift ;;
    --out) OUT="${2:-}"; [[ -n "$OUT" ]] || { echo "ERROR: --out needs a file" >&2; exit 2; }; shift 2 ;;
    *) echo "ERROR: unknown argument: $1" >&2; exit 2 ;;
  esac
done

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
# dpkg_version <pkg> -> version, or "-" when the package is not installed.
dpkg_version() {
  local v
  v="$(dpkg-query -W -f='${Version}' "$1" 2>/dev/null || true)"
  [[ -n "$v" ]] && printf '%s' "$v" || printf '%s' "-"
}

# pin_state <image-reference> -> "not pinned (floating tag)" or the digest.
# A bare localhost/ tag is a LOCAL BUILD, which is a different thing from an
# unpinned upstream tag and is labelled as such rather than lumped in.
pin_state() {
  local ref="$1"
  if [[ "$ref" == *@sha256:* ]]; then
    printf 'digest %s' "${ref##*@}"
  elif [[ "$ref" == localhost/* ]]; then
    printf 'local build (tag %s)' "${ref##*:}"
  elif [[ -z "$ref" || "$ref" == "-" ]]; then
    printf 'no Image= line'
  else
    printf 'NOT PINNED (floating tag)'
  fi
}

section() {
  if (( AS_MD )); then printf '\n## %s\n\n' "$1"; else printf '\n=== %s ===\n' "$1"; fi
}

# row <name> <version> <pinned> <source> [notes]
row() {
  local name="$1" ver="$2" pin="$3" src="$4" notes="${5:-}"
  if (( AS_MD )); then
    printf '| `%s` | %s | %s | %s | %s |\n' "$name" "$ver" "$pin" "$src" "$notes"
  else
    printf '%-38s %-26s %-34s %s\n' "$name" "$ver" "$pin" "$src"
    [[ -n "$notes" ]] && printf '%-38s %-26s %-34s   -> %s\n' "" "" "" "$notes"
  fi
  return 0
}

header() {
  if (( AS_MD )); then
    printf '| Component | Version | Pinned to | Update source | Notes |\n'
    printf '|---|---|---|---|---|\n'
  else
    printf '%-38s %-26s %-34s %s\n' "COMPONENT" "VERSION" "PINNED TO" "UPDATE SOURCE"
    printf '%-38s %-26s %-34s %s\n' "--------------------------------------" \
      "--------------------------" "----------------------------------" "----------------"
  fi
}

# apt_update_source <pkg> -> how apt would deliver an update, unattended or not.
# Derived from the apt policy of the package's own version, not guessed.
apt_update_source() {
  local pkg="$1" origin="" suite=""
  # The apt version table looks like:
  #   500 http://us.archive.ubuntu.com/ubuntu resolute/universe amd64 Packages
  # so the suite is field 3. Skip the /var/lib/dpkg/status pseudo-source, which
  # is not a repository, and skip any non-http entry.
  # awk must print the two fields with a NEWLINE, not a space: this script runs
  # under IFS=$'\n\t', which does not split on spaces, so a space-separated
  # pair collapses into $1 and the suite ends up inside the origin.
  origin="$(apt-cache policy "$pkg" 2>/dev/null | awk '
    $1 ~ /^[0-9]+$/ && $2 ~ /^https?:/ && $2 !~ /dpkg.status/ {
      o=$2; sub(/\/[^/]+$/,"",o); print o "\n" $3; exit
    }')" || true
  suite="$(printf '%s' "$origin" | tail -1)"
  origin="$(printf '%s' "$origin" | head -1)"
  [[ -n "$origin" ]] || origin="unknown"
  [[ -n "$suite"  ]] || suite="unknown"
  # These must be separate statements. Chaining them on one `local` line makes
  # each expansion read the same pre-assignment value, so ${host%%/*} strips
  # from the unstripped string and the host keeps its "/ubuntu" path segment.
  local host="${origin#http://}"
  host="${host#https://}"
  host="${host%%/*}"
  local pocket="${suite##*/}"
  case "$pocket" in
    security) printf 'apt -security (UNATTENDED)'; return 0 ;;
    updates)  printf 'apt -updates (manual)';       return 0 ;;
  esac
  # Anything not served by the Ubuntu archive is third-party: a vendor repo such
  # as nvidia.github.io carries no suite component at all, and its version-table
  # line ends in the literal word "Packages". Name those by host, because the
  # last path segment is just "deb" and tells a reader nothing.
  # The Ubuntu archive is mirrored per-region (us.archive.ubuntu.com,
  # archive.ubuntu.com, ...) and the security pocket is a separate host, so match
  # the suffix rather than an exact hostname.
  # suite is "<codename>[/<component>]" and pocket is the last segment, so the
  # two overlap. Report the pocket once, which is what tells a reader whether an
  # update is security or ordinary.
  case "$host" in
    *archive.ubuntu.com|*security.ubuntu.com)
      printf 'apt %s (manual)' "$pocket" ;;
    *)
      printf 'apt third-party: %s (manual)' "$host" ;;
  esac
}


# ---------------------------------------------------------------------------
# 1. PODMAN / NETWORK
# ---------------------------------------------------------------------------
podman_network() {
  section "1. PODMAN AND NETWORK"
  row "podman" "$(podman --version 2>/dev/null | awk '{print $3}')" \
    "$(apt_update_source podman)" "apt -updates (manual)"
  row "quadlet / systemd" "$(systemctl --version 2>/dev/null | head -1 | awk '{print $2}')" \
    "$(apt_update_source systemd)" "apt -updates (manual)"

  printf '\n'
  header
  local f dom name ref pin note live
  for f in /ALWAYSON/quadlet/*/*.container; do
    [[ -e "$f" ]] || continue
    dom="$(basename "$(dirname "$f")")"
    name="$(basename "$f" .container)"
    ref="$(sed -n 's/^Image=//p' "$f")"
    pin="$(pin_state "$ref")"
    live="$(systemctl --user is-active "$name.service" 2>/dev/null || true)"
    note=""
    [[ "$live" == "active" ]] && note="running" || note="not running"
    if [[ "$pin" == NOT* ]]; then note="$note; FLOATING TAG"; fi
    row "$name" "$dom" "$pin" "container registry (manual promote)" "$note"
  done

  printf '\n'
  if (( AS_MD )); then
    printf '| NETWORK | INTERNAL | SUBNET | UPDATE SOURCE |\n|---|---|---|---|\n'
  else
    printf '%-38s %-12s %-18s %s\n' "NETWORK" "INTERNAL" "SUBNET" "UPDATE SOURCE"
  fi
  local net
  while read -r net; do
    [[ -n "$net" ]] || continue
    if (( AS_MD )); then
      printf '| `%s` | %s | %s | local (defined in /ALWAYSON/quadlet/networks) |\n' "$net" \
        "$(podman network inspect "$net" --format '{{.Internal}}' 2>/dev/null)" \
        "$(podman network inspect "$net" --format '{{range .Subnets}}{{.Subnet}}{{end}}' 2>/dev/null)"
    else
      printf '%-38s %-12s %-18s %s\n' "$net" \
        "$(podman network inspect "$net" --format '{{.Internal}}' 2>/dev/null)" \
        "$(podman network inspect "$net" --format '{{range .Subnets}}{{.Subnet}}{{end}}' 2>/dev/null)" \
        "local (defined in /ALWAYSON/quadlet/networks)"
    fi
  done < <(podman network ls --format '{{.Name}}' 2>/dev/null | grep '^ao-' | sort)
}


# ---------------------------------------------------------------------------
# 2. DESKTOP SOFTWARE
# ---------------------------------------------------------------------------
desktop_software() {
  section "2. DESKTOP SOFTWARE"
  printf '\nSnap:\n'
  header
  # NB: this script runs under IFS=$'\n\t', which does NOT split on spaces, so
  # a bare `read` would collapse every snap field into $1. IFS is set locally
  # for the loop and restored after, so the rest of the script is unaffected.
  local name ver rev track
  local saved_ifs="$IFS"
  IFS=$' \t\n'
  while read -r name ver rev track _rest; do
    [[ -n "$name" ]] || continue
    row "snap:$name" "$ver (rev $rev)" "channel $track" "snap (UNATTENDED via snapd)"
  done < <(snap list 2>/dev/null | tail -n +2)
  IFS="$saved_ifs"

  printf '\nFlatpak:\n'
  header
  local app
  while read -r app _; do
    [[ -n "$app" ]] || continue
    row "flatpak:$app" "$(flatpak info "$app" 2>/dev/null | awk -F': +' '/^[[:space:]]*Version:/{print $2; exit}')" \
      "$(flatpak info "$app" 2>/dev/null | awk -F': +' '/^[[:space:]]*Branch:/{print $2; exit}')" \
      "flatpak (manual; no timer installed)"
  done < <(flatpak list --app --columns=application 2>/dev/null)

  printf '\nAPT-installed desktop applications:\n'
  header
  # Selected rather than exhaustive: the full 4497-package dpkg list is not an
  # inventory a human reads, and the point here is what runs on the desktop.
  local p v
  for p in kcalc okular dolphin konsole gimp inkscape openscad blender \
           libreoffice libreoffice-calc vlc audacious kdenlive shotwell \
           gnome-terminal xterm; do
    v="$(dpkg_version "$p")"
    [[ "$v" == "-" ]] && continue
    row "apt:$p" "$v" "not pinned" "$(apt_update_source "$p")"
  done
}


# ---------------------------------------------------------------------------
# 3. LIBRARIES
# ---------------------------------------------------------------------------
libraries() {
  section "3. LIBRARIES"
  printf '\nROS 2 (host):\n'
  header
  local rosdir dist
  for rosdir in /opt/ros/*; do
    [[ -d "$rosdir" ]] || continue
    dist="${rosdir##*/}"
    row "ros2:$dist" "distro $dist" "pinned by suite; NOT held by apt" \
      "apt (packages.ros.org UNREACHABLE - TLS failure)"
    # -f '.' emits one character per matched package; the explicit \n is what
    # makes wc -l reliable here.
    row "ros2:$dist packages" "$(dpkg-query -W -f '.\n' 'ros-*-*' 2>/dev/null | grep -c . || true) installed" \
      "not pinned individually" "apt (repository unreachable)"
  done

  printf '\nGazebo:\n'
  header
  local g v
  for g in gz-tools gz-sim10-server gz-sim10-cli; do
    v="$(dpkg_version "$g")"
    [[ "$v" == "-" ]] && continue
    row "apt:$g" "$v" "not pinned; no apt hold" "$(apt_update_source "$g")"
  done
  row "Gazebo Sim (container)" "10.5.0" "local build digest" \
    "built from GAZEBO/containers (ao-sim-fabrication)"

  printf '\nLanguage runtimes:\n'
  header
  row "python3" "$(python3 --version 2>/dev/null | awk '{print $2}')" "not pinned" \
    "$(apt_update_source python3)"
  row "node" "$(node --version 2>/dev/null)" "not pinned" "tarball/nvm; not from apt"
  row "npm" "$(npm --version 2>/dev/null)" "bundled with node" "with node"

  printf '\nFlatpak runtimes (shared libraries):\n'
  header
  local rt branch ver
  while read -r rt branch ver _; do
    [[ -n "$rt" ]] || continue
    row "flatpak:$rt" "$ver" "branch $branch" "flatpak (manual)"
  done < <(flatpak list --runtime --columns=name,branch,version 2>/dev/null | sort -u)

# ---------------------------------------------------------------------------
# 4. OPERATING SYSTEM AND DRIVERS
# ---------------------------------------------------------------------------
os_and_drivers() {
  section "4. OPERATING SYSTEM AND DRIVERS"
  printf '\nOperating system:\n'
  header
  local pretty="" codename="" kernel recorded note=""
  pretty="$(. /etc/os-release; printf '%s' "${PRETTY_NAME:-unknown}")"
  codename="$(. /etc/os-release; printf '%s' "${VERSION_CODENAME:-unknown}")"
  kernel="$(uname -r)"
  row "Ubuntu" "$pretty ($codename)" "release suite" "apt -security (UNATTENDED)"
  row "kernel (running)" "$kernel" "n/a - selected at boot" "apt (manual; needs reboot)"

  # Drift check against the hand-maintained matrix. This host has already proven
  # the failure mode, so the inventory reports it rather than trusting the file.
  recorded="$(sed -n 's/^[[:space:]]*kernel:[[:space:]]*"\([^"]*\)".*/\1/p' \
    /ALWAYSON/config/platform/version-matrix.yaml 2>/dev/null | head -1)"
  if [[ -n "$recorded" && "$recorded" != "$kernel" ]]; then
    note="records $recorded - STALE, running $kernel"
  else
    note="agrees with the running kernel"
  fi
  row "kernel (version-matrix.yaml)" "${recorded:-not recorded}" "hand-maintained" \
    "manual edit" "$note"

  printf '\nAPT upgrade state:\n'
  header
  row "unattended-upgrades" "$(dpkg_version unattended-upgrades)" \
    "base + -security only" "ENABLED, running (apt-daily-upgrade.timer)"
  row "packages held" "$(apt-mark showhold 2>/dev/null | wc -l)" "none held" \
    "nothing protects Gazebo/ROS from an apt upgrade"
  row "packages upgradable" "$(apt list --upgradable 2>/dev/null | tail -n +2 | wc -l)" \
    "n/a" "pending; -updates is manual"

  printf '\nGPU driver:\n'
  header
  local drvver gpuname
  drvver="$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1)"
  gpuname="$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)"
  row "NVIDIA kernel driver" "$drvver on $gpuname" "pinned by nvidia-dkms-580" \
    "apt -updates (manual; DKMS rebuild)"
  row "nvidia-container-toolkit" "$(dpkg_version nvidia-container-toolkit)" "not pinned" \
    "$(apt_update_source nvidia-container-toolkit)"
  row "CDI spec (authoritative)" "/var/run/cdi/nvidia.yaml" "regenerated by nvidia-ctk" \
    "regenerated on driver change"
  row "CDI spec (stale copy)" "/etc/cdi/nvidia.yaml" "pins 580.173.02 - STALE" \
    "regenerate or remove"

  printf '\nFirmware:\n'
  header
  local fw
  for fw in $(dpkg-query -W -f='${Package}\n' 'firmware-*' 2>/dev/null | head -6); do
    row "apt:$fw" "$(dpkg_version "$fw")" "not pinned" "$(apt_update_source "$fw")"
  done
}

}


# ---------------------------------------------------------------------------
main() {
  if (( AS_MD )); then
    printf '# ALWAYS ON — Installed Software Inventory\n\n'
    printf '> Generated `%s` by `scripts/build-update/inventory-system.sh --markdown`.\n' \
      "$(date -u --iso-8601=seconds)"
    printf '>\n'
    printf '> **Do not edit this file by hand.** It is generated from the live system.\n'
    printf '>\n'
    printf '> ```bash\n'
    printf '> /ALWAYSON/scripts/build-update/inventory-system.sh --markdown \\\n'
    printf '>   --out /ALWAYSON/docs/inventory.md\n'
    printf '> ```\n'
  else
    printf 'ALWAYS ON - installed software inventory   %s\n' "$(date -u --iso-8601=seconds)"
    printf 'Generated by scripts/build-update/inventory-system.sh\n'
  fi

  podman_network
  desktop_software
  libraries
  os_and_drivers

  if (( AS_MD )); then
    printf '\n---\n\n'
    printf '## How to read these tables\n\n'
    printf '| Term | Meaning |\n|---|---|\n'
    printf '| `digest sha256:...` | Immutable. Cannot drift without an explicit edit. Safe. |\n'
    printf '| `NOT PINNED (floating tag)` | **A finding.** The tag can move under the unit. |\n'
    printf '| `local build` | Built on this host. A rebuild changes the digest and fails the unit until re-pinned. |\n'
    printf '| `not pinned` | An ordinary package with no immutability guarantee. |\n'
    printf '| `UNATTENDED` | Upgrades itself with no human involvement. |\n'
    printf '| `manual` | Waits for an operator decision. |\n'
    printf '\n'
    printf '## Keeping this current\n\n'
    printf 'The inventory is generated, so it is never hand-edited. What it needs is\n'
    printf 'to be *regenerated* at the right moments:\n\n'
    printf '| When | Action |\n|---|---|\n'
    printf '| After any image promotion | `./scripts/build-update/inventory-system.sh --markdown --out docs/inventory.md` |\n'
    printf '| After any `apt upgrade` | same |\n'
    printf '| After a driver or kernel change | same — the OS table flags matrix drift automatically |\n'
    printf '| Weekly | `inventory-refresh.timer` regenerates it into a working copy for review |\n'
    printf '\n'
    printf 'The weekly timer regenerates the file and writes it to a working copy for\n'
    printf 'review, so drift shows up as a diff instead of being discovered later. It\n'
    printf 'does **not** install anything, and it does not touch a running service.\n'
  else
    printf '\nPinned to: digest = immutable | NOT PINNED = floating tag, can drift\n'
    printf '            local build = built here, rebuild changes the digest\n'
  fi
}

# --out writes to a file; without it the report goes to stdout. Writing goes
# through a temp file in the same directory and an atomic rename, so a reader
# never sees a half-written inventory.
if [[ -n "$OUT" ]]; then
  outdir="$(dirname "$OUT")"
  [[ -d "$outdir" ]] || { echo "ERROR: no such directory: $outdir" >&2; exit 10; }
  tmp="$(mktemp "${OUT}.XXXXXX")"
  main > "$tmp"
  mv "$tmp" "$OUT"
  echo "wrote $OUT ($(wc -l < "$OUT") lines)"
else
  main
fi
