#!/usr/bin/env bash
# ALWAYS ON - deploy: deploy-quadlet-domain.sh (Section 4.1)
# Usage: deploy-quadlet-domain.sh <domain> [--dry-run]
# Copies approved Quadlet definitions from $AO_ROOT/quadlet/<domain>/ into the
# rootless systemd user directory and daemon-reloads.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_dry_run_init "${2:-}"

domain="${1:-}"
[[ -n "$domain" ]] || { echo "Usage: ${0##*/} <sales|payment|field|mapping|sim-vehicle|sim-fabrication|ledger|operations> [--dry-run]" >&2; exit 2; }

SRC="$AO_ROOT/quadlet/$domain"
DEST="$HOME/.config/containers/systemd/$domain"

[[ -d "$SRC" ]] || { echo "ERROR: no quadlet definitions at $SRC" >&2; exit 10; }
ls "$SRC"/* >/dev/null 2>&1 || { echo "ERROR: $SRC contains no unit files yet" >&2; exit 11; }

ao_run mkdir -p "$DEST"
for f in "$SRC"/*; do
  ao_log INFO "deploying $(basename "$f") -> $DEST/"
  ao_run install -m 0644 "$f" "$DEST/"
done
ao_run systemctl --user daemon-reload
(( AO_DRY_RUN )) || ao_audit "deployed quadlet domain $domain"
echo "OK: domain '$domain' deployed ($(ls "$SRC" | wc -l) units)"