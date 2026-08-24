# ALWAYS ON - verify-storefront-release.sh: hash a release and record it for provenance.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_require_cmds sha256sum tar
rel="${1:-}"
[[ -d "${rel:-}" ]] || { echo "Usage: ${0##*/} <release_dir>" >&2; exit 2; }
tar -C "$(dirname "$rel")" -cf - "$(basename "$rel")" | sha256sum | tee "$rel.sha256"
echo "OK: release digest recorded"
