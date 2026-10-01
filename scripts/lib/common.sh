#!/usr/bin/env bash
# ALWAYS ON shared script library - Section 4.2 compliance helpers.
# Scripts still begin with their own strict header; source this after it.

AO_ROOT="/ALWAYSON"
AO_LOG_DIR="$AO_ROOT/logs"
AO_AUDIT_LOG="$AO_LOG_DIR/audit.log"

ao_now_utc() { date -u --iso-8601=seconds; }

ao_log() {
  # ao_log LEVEL MESSAGE...
  local level="$1"; shift
  printf '%s %s %s\n' "$(ao_now_utc)" "$level" "$*" | tee -a "$AO_LOG_DIR/script-runs.log" >&2
}

ao_audit() {
  # Record an audit entry for operational changes (Section 4.2 requirement).
  mkdir -p "$AO_LOG_DIR"
  printf '%s actor=%s script=%s %s\n' \
    "$(ao_now_utc)" "${SUDO_USER:-$USER}" "${0##*/}" "$*" >> "$AO_AUDIT_LOG"
}

# ao_audit_secret() - like ao_audit, but refuses to record a message that
# contains a credential. Rule 7 forbids secrets in the journal; a caller that
# builds its message from a wallet read could otherwise leak one by accident.
# The message is checked against a credential-shaped pattern and redacted rather
# than dropped, so the action is still recorded.
ao_audit_secret() {
  local msg="$*"
  if printf '%s' "$msg" | grep -qE '(PASSWORD|TOKEN|SECRET|API_?KEY|BEARER)[=: ]+[A-Za-z0-9+/_.-]{6,}'; then
    msg="$(printf '%s' "$msg" | sed -E 's/((PASSWORD|TOKEN|SECRET|API_?KEY|BEARER)[=: ]+)[A-Za-z0-9+/_.-]{6,}/\1<redacted>/gI')"
    printf '%s actor=%s script=%s REDACTED-BY-AUDIT-GUARD %s\n' \
      "$(ao_now_utc)" "${SUDO_USER:-$USER}" "${0##*/}" "$msg" >> "$AO_AUDIT_LOG"
    return 0
  fi
  ao_audit "$@"
}

ao_require_cmds() {
  local missing=0 c
  for c in "$@"; do
    if ! command -v "$c" >/dev/null 2>&1; then
      echo "ERROR: required command not found: $c" >&2
      missing=1
    fi
  done
  return "$missing"
}

ao_lock() {
  # ao_lock <name> - exclusive lock for scripts whose concurrent invocation could corrupt data
  local lockdir="$AO_ROOT/tmp/locks"
  mkdir -p "$lockdir"
  local lf="$lockdir/${1}.lock"
  exec 9>"$lf" || return 1
  if ! flock -n 9; then
    echo "ERROR: another instance of ${0##*/} is running (lock: $lf)" >&2
    exit 31
  fi
}

ao_dry_run_init() {
  AO_DRY_RUN=0
  # NOTE: do not use a bare `[[ ]] && ...` here — under `set -e` a false
  # result would silently terminate calling scripts (bug fixed 2026-08-31).
  if [[ "${1:-}" == "--dry-run" ]]; then
    AO_DRY_RUN=1
  fi
  return 0
}

ao_run() {
  # Execute external/mutating operation honoring --dry-run.
  if (( AO_DRY_RUN )); then
    ao_log INFO "DRY-RUN: $*"
  else
    "$@"
  fi
}
