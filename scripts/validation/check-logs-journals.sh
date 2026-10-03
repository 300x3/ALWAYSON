#!/usr/bin/env bash
# ALWAYS ON - check-logs-journals.sh: verify the Section 16.3 log set exists and
# is being updated. A Section 16.3 log that silently stops updating is the same
# defect as one that is missing, so both are checked here.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh

# Section 16.3 log|staleness-days. A log is stale when it is older than its
# staleness budget. "0" means event-driven: it only updates when its subject
# runs, so age alone is not a fault and the row is reported as EVENT-DRIVEN.
# A negative budget means "no entry is required yet" (the subject does not
# exist on this host) and the row is reported as NOT-APPLICABLE.
declare -a rows=(
  "installation-journal.log|30"
  "operations-journal.log|7"
  "audit.log|7"
  "backup.log|30"
  "restore-test.log|3650"
  "gpu-runtime-check.log|90"
  "script-runs.log|7"
  "mastodon-local-proxy.log|7"
  "sim-gz-server.log|7"
  "sim-foxglove-bridge.log|7"
  "sim-clock-bridge.log|7"
  "web-console.log|30"
  "lmstudio-readme-preset.sha256|90"
)
declare -a dirs=(
  "gpu-runtime|3650"
  "backup|3650"
  "operations|30"
  "installation|3650"
)

now="$(date -u +%s)"
missing=0
stale=0

printf '%-34s %-16s %s\n' "LOG (Section 16.3)" "STATE" "LAST WRITE (UTC)"
printf '%s\n' "----------------------------------------------------------------------"

for row in "${rows[@]}"; do
  name="${row%%|*}"
  budget="${row##*|}"
  path="$AO_LOG_DIR/$name"
  if [[ ! -e "$path" ]]; then
    printf '%-34s %-16s %s\n' "$name" "MISSING" "-"
    missing=$((missing + 1))
    continue
  fi
  mtime="$(stat -c %Y "$path")"
  age_days=$(( (now - mtime) / 86400 ))
  when="$(date -u -d "@$mtime" +%Y-%m-%dT%H:%M:%SZ)"
  if (( budget < 0 )); then
    state="NOT-APPLICABLE"
  elif (( age_days > budget )); then
    state="STALE (${age_days}d > ${budget}d)"
    stale=$((stale + 1))
  else
    state="OK (${age_days}d)"
  fi
  printf '%-34s %-16s %s\n' "$name" "$state" "$when"
done

# MeshChatX is checked at its REAL location, not at a placeholder.
# It is installed and runs as reticulum-meshchatx.service; the application
# writes its own log into its storage dir, which is 907 MB of live state
# (identities, session secret, mbtiles) and is NOT relocated into logs/.
# An earlier version of this script marked it "not applicable" on the false
# ground that MeshChatX was not installed. Absence of an ao-field unit is
# not evidence of absence of software -- verify the running service instead.
mcx_log="$HOME/.reticulum-meshchatx/logs/meshchatx.log"
if ! systemctl --user is-active --quiet reticulum-meshchatx.service; then
  printf '%-34s %-16s %s\n' "meshchatx.service" "NOT-RUNNING" "-"
  missing=$((missing + 1))
elif [[ ! -f "$mcx_log" ]]; then
  printf '%-34s %-16s %s\n' "meshchatx.log (app)" "MISSING" "-"
  missing=$((missing + 1))
else
  mtime="$(stat -c %Y "$mcx_log")"
  age_days=$(( (now - mtime) / 86400 ))
  when="$(date -u -d "@$mtime" +%Y-%m-%dT%H:%M:%SZ)"
  if (( age_days > 1 )); then
    printf '%-34s %-16s %s\n' "meshchatx.log (app)" "STALE (${age_days}d)" "$when"
    stale=$((stale + 1))
  else
    printf '%-34s %-16s %s\n' "meshchatx.service" "OK (${age_days}d)" "$when"
  fi
fi

for row in "${dirs[@]}"; do
  name="${row%%|*}"
  budget="${row##*|}"
  path="$AO_LOG_DIR/$name"
  if [[ ! -d "$path" ]]; then
    printf '%-34s %-16s %s\n' "$name/" "MISSING" "-"
    missing=$((missing + 1))
    continue
  fi
  newest="$(find "$path" -type f -printf '%T@\n' 2>/dev/null | sort -n | tail -1)"
  if [[ -z "$newest" ]]; then
    printf '%-34s %-16s %s\n' "$name/" "EMPTY" "-"
    continue
  fi
  mtime="${newest%.*}"
  age_days=$(( (now - mtime) / 86400 ))
  when="$(date -u -d "@$mtime" +%Y-%m-%dT%H:%M:%SZ)"
  if (( budget < 0 )); then
    state="NOT-APPLICABLE"
  elif (( age_days > budget )); then
    state="STALE (${age_days}d > ${budget}d)"
    stale=$((stale + 1))
  else
    state="OK (${age_days}d)"
  fi
  printf '%-34s %-16s %s\n' "$name/" "$state" "$when"
done

printf '%s\n' "----------------------------------------------------------------------"
printf 'missing=%d stale=%d\n' "$missing" "$stale"

ao_operation "check-logs-journals.sh missing=$missing stale=$stale"

if (( missing > 0 )); then
  echo "FAIL: $missing Section 16.3 log(s) missing" >&2
  exit 1
fi
if (( stale > 0 )); then
  echo "WARN: $stale Section 16.3 log(s) past their staleness budget" >&2
  exit 2
fi
echo "PASS: every Section 16.3 log exists and is within its staleness budget"
exit 0