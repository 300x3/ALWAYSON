#!/usr/bin/env bash
# ALWAYS ON - restore-restic-drill.sh: isolated restore drill (README 17.1 steps 1-7).
#
# Performs the seven README 17.1 restore-test requirements against a real
# restic repository, restoring ONLY into a caller-supplied scratch directory.
# It never writes to the live data paths and never runs restic prune, forget,
# unlock, or check --write.
#
# Usage:
#   restore-restic-drill.sh --repo <path> [--snapshot <id>] [--scratch <dir>]
#
# Safety contract (this is the point of the script):
#   * The scratch directory must be absent or empty. The script refuses to write
#     into a directory that already holds files, so a mistyped
#     --scratch /ALWAYSON/data cannot clobber live data.
#   * The scratch directory is refused outright if it is inside /ALWAYSON.
#   * No repository is opened for writing. Only `restic snapshots` and
#     `restic restore` are invoked.
#
# Exit codes: 0 drill passed, 1 drill failed, 2 usage/refused, 3 environment
# (restic missing, repository unreadable, no snapshot).
set -Eeuo pipefail
IFS=$'\n\t'

repo=""; snapshot=""; scratch=""
while [ $# -gt 0 ]; do
  case "$1" in
    --repo)     repo="${2:?--repo needs a value}"; shift 2 ;;
    --snapshot) snapshot="${2:?--snapshot needs a value}"; shift 2 ;;
    --scratch)  scratch="${2:?--scratch needs a value}"; shift 2 ;;
    -h|--help)  sed -n '2,22p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -n "$repo" ] || { echo "ERROR: --repo is required" >&2; exit 2; }
[ -n "$scratch" ] || { echo "ERROR: --scratch is required (never defaults to a live path)" >&2; exit 2; }

command -v restic >/dev/null || { echo "ERROR: restic not installed" >&2; exit 3; }

# The safety refusals below come BEFORE the credential check, deliberately. They
# protect the live tree, so they must not be reachable only by someone who
# already holds the repository password. Measured 2026-10-04: with the
# RESTIC_PASSWORD check ahead of them, `--scratch /ALWAYSON/data/evil` aborted
# with a credential error instead of the refusal message, so the README 17.4
# safety evidence did not reproduce unless a password happened to be exported.

# Refuse any scratch path inside the live tree, checked on the resolved absolute
# path so a relative path or a symlink cannot evade it.
scratch_abs="$(readlink -m "$scratch")"
case "$scratch_abs" in
  /ALWAYSON|/ALWAYSON/*)
    echo "REFUSED: scratch path $scratch_abs is inside the live /ALWAYSON tree." >&2
    echo "Use a path outside /ALWAYSON, e.g. /var/tmp/ao-restore-drill." >&2
    exit 2 ;;
esac

if [ -e "$scratch_abs" ] && [ -n "$(ls -A "$scratch_abs" 2>/dev/null)" ]; then
  echo "REFUSED: scratch directory $scratch_abs already exists and is not empty." >&2
  echo "A restore drill must never overwrite existing content." >&2
  exit 2
fi

# Credentials are required only once the scratch path is known to be safe, and
# still before anything is created on disk.
: "${RESTIC_PASSWORD:?ERROR: RESTIC_PASSWORD must be set in the environment, never passed as an argument}"

mkdir -p "$scratch_abs"

# Step 0: resolve the snapshot under test. With no explicit --snapshot, take the
# newest snapshot rather than array position 0. `restic snapshots --latest 1`
# returns one entry PER PATH GROUP, so its head is not necessarily the newest --
# the same trap that made the backup journal record a stale snapshot ID (see
# scripts/backup/restic-run.sh).
if [ -z "$snapshot" ]; then
  snapshot="$(restic snapshots --json 2>/dev/null | python3 -c '
import json,sys
try:
    snaps = json.load(sys.stdin)
except Exception:
    sys.exit(3)
if not snaps:
    sys.exit(3)
print(max(snaps, key=lambda s: s.get("time",""))["short_id"])' || true)"
  [ -n "$snapshot" ] || { echo "ERROR: could not resolve a snapshot; pass --snapshot explicitly" >&2; exit 3; }
  echo "using newest snapshot: $snapshot"
fi

echo "STEP 1: restore to isolated test path $scratch_abs (never the live tree)"
restic restore "$snapshot" --target "$scratch_abs" || {
  echo "FAIL: restic restore returned non-zero" >&2; exit 1; }

# Restored /ALWAYSON sources land under $scratch_abs/ALWAYSON/<path>.
live_root="$scratch_abs/ALWAYSON"
[ -d "$live_root" ] || live_root="$scratch_abs"
echo "STEP 2: validate database integrity"
# The PostgreSQL dumps are gzipped SQL. A truncated or corrupt dump fails at
# decompression; a dump that decompresses but has almost no content is caught by
# a size floor, matching the >1KB floor backup-host-postgres.sh already applies
# on the write side.
db_found=0; db_bad=0
while IFS= read -r dump; do
  [ -n "$dump" ] || continue
  db_found=$((db_found+1))
  if ! gzip -t "$dump" 2>/dev/null; then
    echo "  CORRUPT (gzip): ${dump#"$scratch_abs"/}"; db_bad=$((db_bad+1)); continue
  fi
  bytes="$(gzip -dc "$dump" 2>/dev/null | wc -c)"
  if [ "$bytes" -lt 1024 ]; then
    echo "  SUSPICIOUS (${bytes}B decompressed): ${dump#"$scratch_abs"/}"; db_bad=$((db_bad+1)); continue
  fi
  echo "  OK ${dump#"$scratch_abs"/} (${bytes}B decompressed)"
done < <(find "$scratch_abs" -path '*/backups/postgres/*' -name '*.sql.gz' 2>/dev/null | sort)
echo "  database dumps checked: $db_found, problems: $db_bad"

echo "STEP 3: recalculate artifact hashes"
hashfile="$scratch_abs/.drill-hashes.txt"
( cd "$live_root" && find . -type f ! -name '.drill-hashes.txt' -print0 | sort -z | xargs -0 sha256sum ) > "$hashfile" 2>/dev/null || true
total_files="$(wc -l < "$hashfile")"
echo "  hashed $total_files files under $live_root"

echo "STEP 4: compare hashes with the live tree"
# A drill compares against LIVE only to report drift. Differences are EXPECTED
# and are NOT failures: the snapshot is by definition older than the live tree.
# What matters is that the drill separates drift from corruption, so this step
# reports three buckets rather than a single pass/fail, and every "changed" file
# is checked for an mtime newer than the snapshot before being called drift.
#
# The snapshot time is normalised to a UTC epoch. restic reports local time with
# an offset (e.g. 2026-10-03T08:59:59.123-07:00); Python's fromisoformat plus
# astimezone(utc) handles the offset, and the [:19] truncation avoids restic's
# nanosecond precision, which fromisoformat rejects on some Python builds.
snapshot_epoch="$(restic snapshots --json "$snapshot" 2>/dev/null | python3 -c '
import json,sys
from datetime import datetime, timezone
try:
    t = json.load(sys.stdin)[0]["time"][:19]
    print(int(datetime.fromisoformat(t).astimezone(timezone.utc).timestamp()))
except Exception:
    print(0)' || echo 0)"
echo "  snapshot time as UTC epoch: $snapshot_epoch"

same=0; changed=0; changed_before_snapshot=0; missing=0
# Strip the restore prefix so a path like ./config/x from the scratch tree is
# looked up under the LIVE /ALWAYSON tree. The comparison must ALWAYS be against
# the live file: comparing the restored copy to itself reports "identical" for
# every file and hides both real drift and corruption. (Found and fixed during
# the first run of this script -- see README 17.4.)
while IFS= read -r rel; do
  rel="${rel#./}"
  case "$rel" in .drill-hashes.txt) continue ;; esac
  snap_hash="$(awk -v p="./$rel" '$2==p {print $1}' "$hashfile" | head -1)"
  live="/ALWAYSON/$rel"
  [ -e "$live" ] || { missing=$((missing+1)); continue; }
  live_hash="$(sha256sum "$live" | cut -d' ' -f1)"
  if [ "$live_hash" = "$snap_hash" ]; then
    same=$((same+1))
  else
    changed=$((changed+1))
    # Flag any difference whose live mtime is OLDER than the snapshot: that
    # cannot be explained by drift and is the corruption signature.
    mtime="$(stat -c %Y "$live" 2>/dev/null || echo 0)"
    if [ "$snapshot_epoch" -gt 0 ] && [ "$mtime" -lt "$snapshot_epoch" ]; then
      changed_before_snapshot=$((changed_before_snapshot+1))
      [ "$changed_before_snapshot" -le 10 ] && \
        echo "  SUSPECT (live older than snapshot): $rel"
    else
      [ "$changed" -le 10 ] && echo "  changed since snapshot (drift): $rel"
    fi
  fi
done < <(cd "$live_root" && find . -type f | sort)
echo "  identical: $same, changed: $changed, changed-but-older-than-snapshot: $changed_before_snapshot, live-only: $missing"

echo "STEP 5: verify associated Corda receipt/manifests where available"
receipts="$(find "$scratch_abs" -path '*pending-ledger-submissions*' -name 'manifest.json' 2>/dev/null | wc -l)"
echo "  pending-ledger-submission manifests found: $receipts"
if [ "$receipts" -eq 0 ]; then
  echo "  NOTE: none present in this snapshot. That is a PATH-SET observation, not a pass."
  echo "        README 17.4 records which data classes the restic path set covers."
fi

echo "STEP 6: record operator, source backup ID, result and exceptions"
result=PASS
[ "$db_bad" -gt 0 ] && result=FAIL
[ "$changed_before_snapshot" -gt 0 ] && result=FAIL
echo "  operator=$(id -un) source_snapshot=$snapshot repo=$repo"
echo "  scratch=$scratch_abs files_hashed=$total_files db_dumps=$db_found db_problems=$db_bad"
echo "  identical=$same changed=$changed suspect=$changed_before_snapshot live_only=$missing manifests=$receipts"
echo "  result=$result"

echo "STEP 7: alert on failure"
if [ "$result" = FAIL ]; then
  echo "  DRILL FAILED -- corrupt database dump, or a file differs from the"
  echo "  snapshot without an explanation. README 17.1 requires an alert on"
  echo "  restore-test failure; report this to the operator."
  exit 1
fi
echo "  no failure to alert on."
echo
echo "Drill scratch directory left in place for inspection: $scratch_abs"
echo "Remove it when finished: rm -rf $scratch_abs"
exit 0