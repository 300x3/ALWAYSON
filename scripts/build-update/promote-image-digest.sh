#!/usr/bin/env bash
# ALWAYS ON - build-update: promote a verified image digest into a Quadlet.
#
# The acquisition side of the update path is ao-build-update (README 5.2.1). This
# script is the other half: taking a digest that acquisition recorded and putting
# it into the Image= line of the quadlet that runs it.
#
# It is deliberately narrow. It edits exactly one Image= line in exactly one
# file, it refuses anything it does not fully understand, and it never starts,
# stops, or restarts anything. Deployment stays a separate, explicit step
# (deploy-quadlet-domain.sh) so that reviewing a diff and running it are two
# different decisions.
#
# Usage:
#   promote-image-digest.sh <domain> <unit>.container <image-reference>
#   promote-image-digest.sh --check <domain> <unit>.container
#
# Examples:
#   # see what is pinned now, and whether it is a digest
#   ./promote-image-digest.sh --check operations ao-grafana.container
#
#   # point the unit at a new digest (reference must be digest-pinned)
#   ./promote-image-digest.sh operations ao-grafana.container \
#     docker.io/grafana/grafana-oss@sha256:<64 hex>
#
# Refuses (exit 3) unless all of these hold:
#   - the file is a .container under /ALWAYSON/quadlet/<domain>/
#   - it contains exactly one Image= line
#   - the new reference is fully qualified and carries a sha256 digest
#   - --check is not combined with a new reference
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_lock promote-image-digest

usage() {
  cat >&2 <<'EOF'
Usage:
  promote-image-digest.sh <domain> <unit>.container <image-reference>
  promote-image-digest.sh --check <domain> <unit>.container
EOF
  exit 2
}

check_only=0
if [[ "${1:-}" == "--check" ]]; then
  check_only=1
  shift
fi

domain="${1:-}"; unit="${2:-}"; ref="${3:-}"
[[ -n "$domain" && -n "$unit" ]] || usage
[[ "$unit" == *.container ]] || { echo "ERROR: not a .container: $unit" >&2; exit 2; }

SRC="$AO_ROOT/quadlet/$domain"
[[ -d "$SRC" ]] || { echo "ERROR: no quadlet domain at $SRC" >&2; exit 10; }
FILE="$SRC/$unit"
[[ -f "$FILE" ]] || { echo "ERROR: no such unit: $FILE" >&2; exit 10; }

# Count Image= lines. Zero means the unit is malformed; more than one means we
# cannot tell which is authoritative, and guessing is how the wrong image ships.
mapfile -t img_lines < <(grep -n '^Image=' "$FILE" || true)
count="${#img_lines[@]}"
if (( count == 0 )); then
  echo "ERROR: no Image= line in $FILE" >&2
  exit 3
fi
if (( count > 1 )); then
  echo "ERROR: $count Image= lines in $FILE; refusing to guess which is current" >&2
  exit 3
fi

current="$(sed -n 's/^Image=//p' "$FILE")"
lineno="${img_lines[0]%%:*}"

# Report what is pinned, and whether it is pinned the way this project requires.
if [[ "$current" == *@sha256:* ]]; then
  state="DIGEST-PINNED"
else
  state="NOT PINNED (floating tag)"
fi
echo "unit:    $domain/$unit (line $lineno)"
echo "current: $current"
echo "state:   $state"

if (( check_only == 1 )); then
  if [[ -n "$ref" ]]; then
    echo "ERROR: --check takes no image reference" >&2
    exit 2
  fi
  exit 0
fi

[[ -n "$ref" ]] || usage

# The new reference must be fully qualified (a registry host) and digest-pinned.
# Both are hard requirements, not warnings: an unpinned Image= line is exactly
# the failure mode this project is built to prevent.
[[ "$ref" == */* ]] || { echo "ERROR: reference is not fully qualified: $ref" >&2; exit 3; }
[[ "$ref" == *@sha256:* ]] || {
  echo "ERROR: reference carries no sha256 digest: $ref" >&2
  echo "       A floating tag would silently drift. Pin a digest." >&2
  exit 3
}
digest="${ref##*@sha256:}"
[[ "$digest" =~ ^[0-9a-f]{64}$ ]] || {
  echo "ERROR: digest is not 64 lowercase hex characters: $digest" >&2
  exit 3
}

if [[ "$ref" == "$current" ]]; then
  echo "OK: already pinned to that reference; nothing to do"
  exit 0
fi

# Refuse a cross-registry swap silently. Changing the registry host is a bigger
# decision than changing a version, and should be a deliberate one.
#
# Docker SHORT NAMES must be normalised first, or this comparison is wrong:
# "postgres@sha256:..." has no "/" at all, so ${ref%%/*} yields the whole string
# and every short-name promotion looks like a registry change. Short names expand
# to docker.io/<repo>, and "postgres"/"redis" expand into the "library" namespace.
host_of() {
  local r="$1" h
  h="${r%%/*}"
  if [[ "$r" != */* ]]; then
    case "$h" in
      postgres|redis|python|alpine|ubuntu|nginx|node|openjdk)
        printf 'docker.io/library' ;;
      *) printf 'docker.io' ;;
    esac
  elif [[ "$h" == "docker.io" || "$h" == "ghcr.io" || "$h" == "quay.io" ]]; then
    printf '%s' "$h"
  else
    # a Docker Hub namespace such as opendronemap/nodeodm
    printf 'docker.io'
  fi
}
cur_host="$(host_of "$current")"; new_host="$(host_of "$ref")"
if [[ "$cur_host" != "$new_host" ]] && [[ "$current" == *@sha256:* ]]; then
  echo "ERROR: registry change $cur_host -> $new_host" >&2
  echo "       Changing registry is not a version bump. Confirm and edit by hand." >&2
  exit 3
fi

# Single-line, in-place substitution. No rewrite of the rest of the file.
tmp="$(mktemp)"
sed "s|^Image=.*|Image=$ref|" "$FILE" > "$tmp"
mv "$tmp" "$FILE"

# Prove the edit landed on the line we intended and that nothing else moved.
new_count="$(grep -c '^Image=' "$FILE")"
new_val="$(sed -n 's/^Image=//p' "$FILE")"
if [[ "$new_count" != "1" || "$new_val" != "$ref" ]]; then
  echo "ERROR: post-edit verification failed (Image= lines: $new_count)" >&2
  exit 4
fi

ao_audit "promoted $domain/$unit image: $current -> $ref"
echo "pinned:  $ref"
echo
echo "NOT deployed. The unit is staged in the repo only. To apply it:"
echo "  $AO_ROOT/scripts/deploy/validate-quadlet-domain.sh $domain"
echo "  $AO_ROOT/scripts/deploy/deploy-quadlet-domain.sh  $domain"
echo "  systemctl --user restart <unit>.service"
echo "Review the diff before deploying:"
echo "  git --no-pager diff $domain/$unit"
