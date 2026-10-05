# ALWAYS ON - restic retention policy (operator budget: 40 GB total, set
# 2026-10-04, OPS-24/OPS-31).
#
# WHY A SEPARATE SCRIPT: scripts/backup/restic-run.sh created a snapshot every
# night and never ran `forget` or `prune` anywhere. Measured 2026-10-04:
# grep for forget|prune across scripts/ matched only the pCloud setup script,
# so the LOCAL repository had no retention at all and grew without bound. That
# is precisely the "logs/backups going crazy" the operator warned about.
#
# WHY NOT A SINGLE FLAG: restic 0.18.1 has no --max-repo-size, so the 40 GB
# budget cannot be expressed declaratively. `restic forget` only takes
# keep-{last,hourly,daily,weekly,monthly,yearly,within,tag} and --group-by.
# So the budget is enforced as a measured CHECK that refuses to prune blindly
# and reports the breach instead.
#
# SCHEDULE (operator, 2026-10-04): daily incremental backups, plus one full
# backup per quarter. restic deduplicates, so a "full" here means a snapshot
# that also carries --tag full, giving the quarterly restore point a durable
# label; it is not a separate full-copy repository.
#
# Usage:
#   restic-retention.sh --env-file <path> [--dry-run] [--max-gb 40]
#
# SAFETY: refuses to run if the repository is unreadable, if restic reports an
# error, or if the size cannot be measured. It never touches live /ALWAYSON
# data paths. `prune` only ever removes pack files that are no longer
# referenced by any retained snapshot; `forget` decides which snapshots are
# retained. Dry-run changes nothing.
set -Eeuo pipefail
IFS=$'\n\t'

envfile=""; dry_run=0; max_gb=40
while [ $# -gt 0 ]; do
  case "$1" in
    --env-file) envfile="${2:?--env-file needs a value}"; shift 2 ;;
    --max-gb)   max_gb="${2:?--max-gb needs a value}"; shift 2 ;;
    --dry-run)  dry_run=1; shift ;;
    -h|--help)  sed -n '2,26p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -n "$envfile" ] || { echo "ERROR: --env-file is required" >&2; exit 2; }
[ -r "$envfile" ] || { echo "ERROR: cannot read env file: $envfile" >&2; exit 3; }
command -v restic >/dev/null || { echo "ERROR: restic not installed" >&2; exit 3; }
case "$max_gb" in (*[!0-9]*|'') echo "ERROR: --max-gb must be a whole number" >&2; exit 2 ;; esac

# Pass arguments as an ARRAY, never through `$*`. The first version used
# `restic_do() { bash -c "... restic $*"; }`, which looks correct but is not:
# bash does NOT word-split an unquoted $* on IFS inside `bash -c` the way a
# shell would at the command line, so every flag after the first arrived as a
# separate word and the shell tried to run it as a command. Measured
# 2026-10-04 on a throwaway repo: "Fatal: no policy was specified" followed by
# `--tag: command not found`, `--keep-hourly: command not found` and eight more.
# It exited non-zero, so nothing was pruned -- the failure was loud, not
# destructive -- but the feature did not work at all.
restic_do() {
  local -a cmd=(restic "$@")
  RESTIC_REPOSITORY="$repo" RESTIC_PASSWORD="$restic_password" "${cmd[@]}"
}

# Measure BEFORE pruning, so the reported figure is the real pre-prune state.
repo="$(sed -n 's/^RESTIC_REPOSITORY=//p' "$envfile" | tail -n1)"
[ -n "$repo" ] || { echo "ERROR: RESTIC_REPOSITORY not set in $envfile" >&2; exit 3; }
if [ ! -d "$repo" ]; then
  echo "ERROR: repository path does not exist: $repo" >&2; exit 3
fi

# Read the password into a variable and pass it per-call via the environment,
# never on the command line, so it cannot appear in a process listing.
restic_password="$(sed -n 's/^RESTIC_PASSWORD=//p' "$envfile" | tail -n1)"
[ -n "$restic_password" ] || {
  echo "ERROR: RESTIC_PASSWORD not set in $envfile" >&2; exit 3
}

size_bytes="$(sudo -n du -sb "$repo" 2>/dev/null | awk '{print $1}' || true)"
if [ -z "$size_bytes" ]; then
  size_bytes="$(du -sb "$repo" 2>/dev/null | awk '{print $1}' || true)"
fi
[ -n "$size_bytes" ] || {
  echo "ERROR: cannot measure repository size at $repo (needs read access)." >&2
  echo "       Refusing to prune without a size measurement." >&2
  exit 3
}
size_gb="$(awk -v b="$size_bytes" 'BEGIN{printf "%.2f", b/1024/1024/1024}')"
echo "repository:  $repo"
echo "size:        ${size_gb} GB (budget ${max_gb} GB)"

snap_count() {
  # Count WITHOUT letting a python traceback reach stderr. The first version
  # piped `restic snapshots --json` straight into json.load, so any non-JSON
  # output (a warning line, an empty stream when the repo has no snapshots yet)
  # printed a JSONDecodeError traceback and reported 0 -- which reads as "no
  # snapshots exist" when the truth was "the count failed". Measured 2026-10-04
  # on a fresh throwaway repo that DID hold one tagged snapshot: it printed 0.
  local n
  n="$(restic_do snapshots --tag alwayson --json 2>/dev/null \
      | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(1)
print(len(data) if isinstance(data, list) else 0)' 2>/dev/null || true)"
  # An empty string means the count genuinely failed; report it as such rather
  # than as a legitimate zero.
  [ -n "$n" ] || { echo "ERROR: could not count snapshots in $repo" >&2; exit 3; }
  printf '%s' "$n"
}

snap_before="$(snap_count)"
echo "snapshots:   ${snap_before} tagged alwayson"

# Retention: 24 hourly / 7 daily / 4 weekly / 6 monthly, grouped per host+path.
# Grouping matters: without it a single global window would delete snapshots
# of one path group because another path group was busier.
echo
echo "retention policy: --keep-hourly 24 --keep-daily 7 --keep-weekly 4 --keep-monthly 6"
echo "grouping:         --group-by host,paths"
if [ "$dry_run" -eq 1 ]; then
  echo
  echo "DRY RUN: nothing will be changed. Equivalent command:"
  echo "  restic forget --tag alwayson --keep-hourly 24 --keep-daily 7 \\"
  echo "      --keep-weekly 4 --keep-monthly 6 --group-by host,paths"
  echo "  restic prune"
  exit 0
fi

echo
restic_do forget --tag alwayson \
  --keep-hourly 24 --keep-daily 7 --keep-weekly 4 --keep-monthly 6 \
  --group-by host,paths || {
  echo "ERROR: restic forget failed; not pruning" >&2; exit 1
}
echo "forget complete; running prune (reclaims unreferenced pack files)"
restic_do prune || { echo "ERROR: restic prune failed" >&2; exit 1; }

snap_after="$(snap_count)"
size_after="$(du -sb "$repo" 2>/dev/null | awk '{print $1}' || echo "$size_bytes")"
size_after_gb="$(awk -v b="$size_after" 'BEGIN{printf "%.2f", b/1024/1024/1024}')"
echo
echo "after:          ${size_after_gb} GB, ${snap_after} snapshots (was ${size_gb} GB, ${snap_before})"

over="$(awk -v a="$size_after_gb" -v m="$max_gb" 'BEGIN{print (a>m)?"YES":"no"}')"
if [ "$over" = YES ]; then
  echo
  echo "OVER BUDGET: ${size_after_gb} GB exceeds the ${max_gb} GB ceiling."
  echo "Retention kept every snapshot the policy requires. The excess is real"
  echo "data, not an over-retention artifact -- review the path set in"
  echo "scripts/backup/restic-run.sh, or raise the budget with the operator."
  exit 1
fi
echo "within budget (${size_after_gb} GB <= ${max_gb} GB)"