#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

source /ALWAYSON/config/mapping/photogrammetry-volume.env

source_device="$(findmnt -n -o SOURCE --target "$PHOTOGRAM_MOUNT" 2>/dev/null || true)"
root_device="$(findmnt -n -o SOURCE --target /)"

if [[ -z "$source_device" ]]; then
  echo "ERROR: $PHOTOGRAM_MOUNT is not mounted" >&2
  exit 20
fi

if [[ "$source_device" == "$root_device" ]]; then
  echo "ERROR: $PHOTOGRAM_MOUNT resolves to the root filesystem" >&2
  exit 21
fi

# NOTE: this host stacks a systemd autofs unit over the real mount; findmnt emits
# one row per stacked mount. Take the last non-empty UUID (the real filesystem).
actual_uuid="$(findmnt -n -o UUID --target "$PHOTOGRAM_MOUNT" 2>/dev/null | sed '/^[[:space:]]*$/d' | tail -n 1)"

if [[ -n "${PHOTOGRAM_UUID:-}" && "$PHOTOGRAM_UUID" != "REPLACE_WITH_VERIFIED_UUID" && "$actual_uuid" != "$PHOTOGRAM_UUID" ]]; then
  echo "ERROR: mounted UUID does not match expected UUID" >&2
  exit 22
fi

if [[ ! -f "$PHOTOGRAM_MOUNT/.mounted-ok" ]]; then
  echo "ERROR: mount marker missing" >&2
  exit 23
fi

available_gb="$(df -BG --output=avail "$PHOTOGRAM_MOUNT" | tail -n 1 | tr -dc '0-9')"

if (( available_gb < PHOTOGRAM_MIN_FREE_GB )); then
  echo "ERROR: only ${available_gb}G free; minimum is ${PHOTOGRAM_MIN_FREE_GB}G" >&2
  exit 24
fi

# ----- §8.5 refusal conditions (FIELD-10) -----
# Required directories: the fixed set of the §8.2 tree. The <mission-id>-
# suffixed directories under validated/, rejected/ and deliverables/ are
# intentionally variable and are NOT required to exist at validation time.
required_dirs=(
  incoming/drone
  incoming/operator
  incoming/quarantine
  manifests/intake
  manifests/processing
  manifests/ledger-submissions
  exports/pcloud-staging
  exports/ipfs-staging
  backups/mapping-db
  tmp/processing
)

missing_dirs=()
for d in "${required_dirs[@]}"; do
  if [[ ! -d "${PHOTOGRAM_MOUNT}/${d}" ]]; then
    missing_dirs+=("$d")
  fi
done

if (( ${#missing_dirs[@]} > 0 )); then
  echo "ERROR: required photogrammetry tree directories are missing: ${missing_dirs[*]}" >&2
  exit 25
fi

# Mapping service ownership / permissions: the WebODM service runs as scottw
# (uid 1000, group ao-mapping gid 1001). Every required directory must be
# writable by scottw, or by the mapping group. Nothing may be world-writable
# (§8.2). The validator MUST run as the mapping operator (scottw), not root,
# so the -w test reflects the service's real access.
bad_perm=()
for d in "${required_dirs[@]}" \
         retention/pending-review retention/eligible-for-archive \
         webodm/media webodm/projects webodm/nodeodm webodm/temp webodm/logs; do
  if [[ ! -w "${PHOTOGRAM_MOUNT}/${d}" ]]; then
    bad_perm+=("$d")
  fi
done

if (( ${#bad_perm[@]} > 0 )); then
  echo "ERROR: mapping service ownership/permissions incorrect: ${bad_perm[*]}" >&2
  exit 26
fi

echo "OK: photogrammetry mount valid: ${source_device}; ${available_gb}G free"