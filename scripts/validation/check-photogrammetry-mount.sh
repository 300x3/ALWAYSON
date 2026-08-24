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

actual_uuid="$(findmnt -n -o UUID --target "$PHOTOGRAM_MOUNT" 2>/dev/null || true)"

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

echo "OK: photogrammetry mount valid: ${source_device}; ${available_gb}G free"