#!/usr/bin/env bash
# Regenerate the software status log (Markdown + HTML + PDF).
#
# READ-ONLY WITH RESPECT TO THE SYSTEM. This script installs, upgrades, promotes,
# deploys and restarts nothing. It reads apt/dpkg/podman/snap state and writes
# documents. It is safe to run at any time; it never changes software state.
#
# Usage:  sudo ./scripts/build-update/refresh-install-log.sh [--offline|--refresh]
#
#   --offline   regenerate from cached upstream data only (no network, ~1s)
#   --refresh   force every upstream lookup NOW, ignoring the cache TTL. This is
#               the fast path for bringing the "Released hash" column up to date.
# Without either, cached values younger than the TTL (6h) are reused.
#
# Why manual and not a systemd timer: docs/software-status.md is a tracked audit
# document. A timer would rewrite it unattended while an operator is mid-review.
# Automatic UPDATES remain prohibited pending operator authorisation.
set -euo pipefail

AO_ROOT="${AO_ROOT:-/ALWAYSON}"
LOG_DIR="$AO_ROOT/logs/operations"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$LOG_DIR/${STAMP}-software-status-refresh.log"
BACKUP="$AO_ROOT/backups/software-status/$STAMP"
OFFLINE="${1:-}"
REFRESH="${2:-}"
if [ "${1:-}" = "--refresh" ]; then REFRESH="--refresh"; OFFLINE=""; fi

mkdir -p "$LOG_DIR" "$BACKUP"
exec > >(tee -a "$LOG") 2>&1

echo "=== ALWAYS ON software status refresh ==="
echo "start (UTC) : $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "host        : $(hostname)"
echo "kernel      : $(uname -r)"
echo "git HEAD    : $(git -C "$AO_ROOT" rev-parse HEAD 2>/dev/null || echo 'not a git checkout')"
echo "script      : $AO_ROOT/scripts/build-update/provenance-log.py"
echo "offline     : ${OFFLINE:-no}"

# Keep the previous document outside the repo. backups/ is gitignored; a .bak
# beside the file would not be, and would litter the tree.
for f in software-status.md software-status.pdf; do
  [ -f "$AO_ROOT/docs/$f" ] && cp -a "$AO_ROOT/docs/$f" "$BACKUP/" || true
done
echo "backup      : $BACKUP"

cd "$AO_ROOT"
python3 -m py_compile scripts/build-update/provenance-log.py

python3 scripts/build-update/provenance-log.py --markdown \
        --out "$AO_ROOT/docs/software-status.md" \
        --html "$AO_ROOT/tmp/software-status.html" \
        ${REFRESH:+--refresh} ${OFFLINE:+$OFFLINE}

# Report the Released hash column explicitly: how many containers carry an
# upstream digest, and how many do not. A blank hash must never be mistaken for
# "up to date", so it is counted and named every run.
MD="$AO_ROOT/docs/software-status.md"
with_hash=$(awk -F'|' '/Rolled-up launchers/{exit} /container/{h=$10;gsub(/`| +/,"",h); if(h!="-")n++} END{print n+0}' "$MD")
no_hash=$(awk -F'|' '/Rolled-up launchers/{exit} /container/{h=$10;gsub(/`| +/,"",h); if(h=="-")n++} END{print n+0}' "$MD")
echo "released-hash: $with_hash container(s) with an upstream digest, $no_hash without"
echo "cache        : $(find "$AO_ROOT/data/build-update/cache" -name '*.json' 2>/dev/null | wc -l) entries"

# PDF is a rendering of the same table. Prefer pandoc; fall back to headless
# Chrome, which is already installed here, so the PDF never silently goes stale.
HTML="$AO_ROOT/tmp/software-status.html"
PDF="$AO_ROOT/docs/software-status.pdf"
if command -v pandoc >/dev/null 2>&1; then
  pandoc "$HTML" -o "$PDF" --metadata title="ALWAYS ON Software Status" \
    || echo "WARNING: pandoc failed; PDF left unchanged"
elif command -v google-chrome >/dev/null 2>&1; then
  google-chrome --headless --disable-gpu --no-sandbox --no-pdf-header-footer \
    --print-to-pdf="$PDF" "file://$HTML" >/dev/null 2>&1 \
    && echo "pdf: rendered via headless chrome" \
    || echo "WARNING: headless chrome failed; PDF left unchanged"
else
  echo "WARNING: no PDF renderer (pandoc or google-chrome); PDF left unchanged"
fi

echo
echo "rows        : $(grep -c '^| ' "$AO_ROOT/docs/software-status.md")"
echo "end (UTC)   : $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "exit        : 0"
echo "affirmation : no package installed, promoted, deployed or restarted."
echo "log         : $LOG"
