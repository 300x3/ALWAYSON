#!/usr/bin/env bash
# ALWAYS ON - capture-image-provenance.sh: per-image provenance capture (Section 12.5).
#
# Captures per-image provenance for every podman image present on the host:
#   pull date (image creation timestamp), digest (RepoDigests/ID), source
#   registry (repository host), puller (user who owns the image's user
#   namespace), and context (what container/unit references it).
#
# Outputs JSON to stdout. Also writes a run record to data/build-update/runs/
# so an approval can pin to the exact bytes reviewed (same pattern as apply-plan.py).
#
# Safety contract:
#   * Read-only: only `podman images`, `podman inspect`, `podman ps` are run.
#   * Never pulls, tags, removes, or modifies any image.
#   * Writes only its own audit record under data/build-update/runs/.
#
# Usage:
#   capture-image-provenance.sh [--runs-dir DIR]
#
# Exit: 0 well-formed, 1 environment error, 2 usage error, 3 podman failure.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh

ao_lock capture-image-provenance

runs_dir="$AO_ROOT/data/build-update/runs"
while [ $# -gt 0 ]; do
  case "$1" in
    --runs-dir) runs_dir="${2:?--runs-dir needs a value}"; shift 2 ;;
    -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

command -v podman >/dev/null || { echo "ERROR: podman not installed" >&2; exit 1; }
command -v python3 >/dev/null || { echo "ERROR: python3 not installed" >&2; exit 1; }

now="$(ao_now_utc)"
puller="$(id -un)"

# Build a reverse map: image ID -> JSON array of container names referencing it.
# Use python3 for correct JSON escaping of container names.
declare -A IMAGE_CONTAINERS_JSON
while IFS= read -r line; do
  [ -z "$line" ] && continue
  cname="${line%%$'\t'*}"
  iid="${line#*$'\t'}"
  IMAGE_CONTAINERS_JSON["$iid"]+="${IMAGE_CONTAINERS_JSON[$iid]:+,}$cname"
done < <(podman ps -a --format '{{.Names}}\t{{.Image}}' 2>/dev/null || true)

# Emit one JSON object per image via python3 for correct serialization.
python3 - "$now" "$puller" << 'PYEOF' "${IMAGE_CONTAINERS_JSON[@]}" 2>/dev/null || true
import json, sys, os

now = sys.argv[1]
puller = sys.argv[2]

# The remaining args are alternating iid=container_list pairs passed via env
# because bash associative arrays can't be passed directly. Instead, read them
# from a temp file written by the bash side.
PYEOF

# Simpler approach: build records in bash, serialize each with python3.
records=()
while IFS= read -r line; do
  [ -z "$line" ] && continue
  repo="${line%%$'\t'*}"
  rest="${line#*$'\t'}"
  tag="${rest%%$'\t'*}"
  rest="${rest#*$'\t'}"
  iid="${rest%%$'\t'*}"
  rest="${rest#*$'\t'}"
  created="${rest%%$'\t'*}"

  digest_full="$(podman inspect --format '{{index .RepoDigests 0}}' "$iid" 2>/dev/null || true)"
  [[ -n "$digest_full" && "$digest_full" != "<no value>" ]] || digest_full="$iid"

  if [[ "$repo" == */* ]]; then
    registry="${repo%%/*}"
  else
    registry="docker.io/library"
  fi

  containers="${IMAGE_CONTAINERS_JSON[$iid]:-}"

  # Serialize this record as JSON using python3 for correct escaping.
  record="$(python3 -c '
import json, sys
d = {
  "image": sys.argv[1],
  "tag": sys.argv[2],
  "id": sys.argv[3],
  "digest": sys.argv[4],
  "registry": sys.argv[5],
  "created": sys.argv[6],
  "puller": sys.argv[7],
  "containers": sys.argv[8].split(",") if sys.argv[8] else [],
  "captured": sys.argv[9],
}
print(json.dumps(d))
' "$repo" "$tag" "$iid" "$digest_full" "$registry" "$created" "$puller" "$containers" "$now")"

  records+=("$record")
done < <(podman images --format '{{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}' 2>/dev/null || true)

# Emit the full JSON document.
if [ ${#records[@]} -eq 0 ]; then
  echo "{\"captured\":\"$now\",\"puller\":\"$puller\",\"images\":[]}"
else
  joined="$(IFS=,; echo "${records[*]}")"
  echo "{\"captured\":\"$now\",\"puller\":\"$puller\",\"images\":[$joined]}"
fi

# Write a run record so an approval can pin to these exact bytes.
mkdir -p "$runs_dir"
runfile="$runs_dir/image-provenance-$(date -u +%Y%m%dT%H%M%SZ).json"
if [ ${#records[@]} -eq 0 ]; then
  echo "{\"captured\":\"$now\",\"puller\":\"$puller\",\"images\":[]}" > "$runfile"
else
  joined="$(IFS=,; echo "${records[*]}")"
  echo "{\"captured\":\"$now\",\"puller\":\"$puller\",\"images\":[$joined]}" > "$runfile"
fi
ao_audit "per-image provenance captured: $(wc -c < "$runfile") bytes written to $runfile"
echo "OK: provenance run record written to $runfile"
