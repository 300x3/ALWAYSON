#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# patch-openclaw-ao-unit-name.sh
#
# Re-applies the ALWAYS ON "ao-" systemd unit-name convention patch to the
# OpenClaw npm package. `openclaw update` / reinstalls overwrite dist/ and
# silently revert GATEWAY_SYSTEMD_SERVICE_NAME to "openclaw-gateway", which
# makes `openclaw status` report the gateway as disabled/stopped (the real
# unit is ~/.config/systemd/user/ao-openclaw-gateway.service).
#
# Idempotent: exits 0 when already patched. Run after every OpenClaw update.
# Context: COORDINATION BETWEEN AI/P. 2026-10-05-lmstudio-shared-endpoint.md
# ---------------------------------------------------------------------------
set -euo pipefail

DIST="/home/scottw/.npm-global/lib/node_modules/openclaw/dist"
CONST="$DIST/constants-obO8goqF.js"
UNIT="/home/scottw/.config/systemd/user/ao-openclaw-gateway.service"

[ -f "$CONST" ] || { echo "SKIP: $CONST not found (OpenClaw layout changed?)" >&2; exit 1; }

changed=0

replace_once() {
    local file="$1" old="$2" new="$3"
    if grep -qF "$old" "$file"; then
        [ -f "$file.bak-ao-patch" ] || cp -p "$file" "$file.bak-ao-patch"
        python3 - "$file" "$old" "$new" <<'PYEOF'
import sys
path, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(path, encoding="utf-8").read()
assert s.count(old) == 1, f"pattern not unique in {path}: {old!r}"
open(path, "w", encoding="utf-8").write(s.replace(old, new))
PYEOF
        echo "PATCHED: $(basename "$file"): $old -> $new"
        changed=1
    fi
}

replace_once "$CONST" \
    'const GATEWAY_SYSTEMD_SERVICE_NAME = "openclaw-gateway";' \
    'const GATEWAY_SYSTEMD_SERVICE_NAME = "ao-openclaw-gateway";'
replace_once "$CONST" \
    'return `openclaw-gateway${suffix}`;' \
    'return `ao-openclaw-gateway${suffix}`;'

if [ "$changed" = 1 ]; then
    echo "OK: dist patch applied (backup at $CONST.bak-ao-patch)"
elif grep -qF 'GATEWAY_SYSTEMD_SERVICE_NAME = "ao-openclaw-gateway"' "$CONST"; then
    echo "OK: dist already patched"
else
    echo "ERROR: constants file exists but expected patterns were not found." >&2
    echo "Inspect $CONST manually before trusting status output." >&2
    exit 1
fi

# The unit-side override is ours (not npm's) and must also use the ao- name;
# status parses Environment= lines from this file to decide which unit to probe.
if [ -f "$UNIT" ]; then
    if grep -q 'OPENCLAW_SYSTEMD_UNIT=openclaw-gateway.service' "$UNIT"; then
        echo "ERROR: $UNIT still sets the legacy OPENCLAW_SYSTEMD_UNIT override" >&2
        exit 1
    fi
    echo "OK: unit override $(grep -o 'OPENCLAW_SYSTEMD_UNIT=[^ ]*' "$UNIT" | head -1)"
else
    echo "WARN: $UNIT missing" >&2
fi

echo "Verify with: openclaw status  (Gateway service row must show enabled/running)"
