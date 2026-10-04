#!/usr/bin/env bash
# ALWAYS ON - install-log-retention.sh: install the logrotate policy and the
# journald retention drop-in (README 16.3, work items OPS-25 and OPS-26).
#
# The policies are STAGED in the repository and validated; this script is the
# privileged step that puts them in place. It is deliberately NOT run by any
# automated job and performs no rotation itself -- logrotate.timer does that on
# its own schedule after the policy is installed.
#
# Run via: pkexec bash /ALWAYSON/scripts/ops/install-log-retention.sh [--dry-run]
#
# What it installs, and why each target:
#   config/host/logrotate-alwayson.conf -> /etc/logrotate.d/alwayson
#       The drop-in name is "alwayson", not "logrotate-alwayson.conf", because
#       logrotate ignores files whose names contain a '.' in some builds and
#       README 16.3 names the installed path /etc/logrotate.d/alwayson.
#   config/host/journald-alwayson.conf -> /etc/systemd/journald.conf.d/60-alwayson-retention.conf
#       A numbered drop-in, not an edit of /etc/systemd/journald.conf, because
#       a package upgrade overwrites the shipped file.
#
# It does NOT restart systemd-journald unless --restart-journald is passed.
# Restarting the journal daemon is a visible host action and is left to the
# operator as a separate, explicit decision.
set -Eeuo pipefail
IFS=$'\n\t'

SRC_CONF=/ALWAYSON/config/host/logrotate-alwayson.conf
SRC_JOURNALD=/ALWAYSON/config/host/journald-alwayson.conf
DEST_LOGROTATE=/etc/logrotate.d/alwayson
DEST_JOURNALD_DIR=/etc/systemd/journald.conf.d
DEST_JOURNALD="$DEST_JOURNALD_DIR/60-alwayson-retention.conf"

dry_run=0
restart_journald=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) dry_run=1 ;;
    --restart-journald) restart_journald=1 ;;
    -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

for f in "$SRC_CONF" "$SRC_JOURNALD"; do
  [ -r "$f" ] || { echo "ERROR: staged source missing: $f" >&2; exit 1; }
done

# Preflight: logrotate must exist before anything is written. Without this the
# validation step below exits 127 with a bare "command not found" AFTER the
# policy has already been installed, leaving a broken file in /etc/logrotate.d.
command -v logrotate >/dev/null || {
  echo "ERROR: logrotate is not installed; refusing to install an unvalidatable policy" >&2
  exit 1; }

# A dry run only prints what it WOULD do and writes nothing, so it must work
# unprivileged -- otherwise the operator cannot check the staged policy without
# escalating first, which is exactly backwards. The root requirement applies to
# the real install only (measured: `install-log-retention.sh --dry-run` as the
# unprivileged session user failed with "must run as root" before this guard
# was narrowed to the install path).
if [ "$dry_run" -eq 0 ] && [ "$(id -u)" -ne 0 ]; then
  echo "ERROR: installing requires root; re-run via: pkexec bash $0" >&2
  echo "       (--dry-run needs no root and can be run as-is)" >&2
  exit 1
fi

if [ "$dry_run" -eq 1 ]; then
  echo "DRY RUN -- no files will be written."
  echo "would install: $SRC_CONF -> $DEST_LOGROTATE"
  echo "would install: $SRC_JOURNALD -> $DEST_JOURNALD"
  echo "would run:    logrotate --debug $SRC_CONF"
  logrotate --debug "$SRC_CONF" 2>&1 | grep -E '^rotating pattern' || true
  exit 0
fi

echo "--- validating the logrotate policy before installing it ---"
# Parse-only: --debug prints what it WOULD do and changes nothing. A parse error
# here means the policy is malformed, and installing it would leave logrotate
# unable to process the file.
#
# Two known-benign messages are filtered out:
#   "logrotate in debug mode does nothing except printing debug messages"
#   "error opening state file /var/lib/logrotate/status: ... Permission denied"
# The second appears when --debug runs as a non-root user and is not a policy
# error. Anything else matching unknown option / bad line / error: is fatal.
dbg="$(mktemp)"
tmp_policy="$(mktemp)"
# Validate a 0644 COPY, never the repo file directly. logrotate silently ignores
# any policy file that is group- or world-writable:
#   "error: Ignoring /ALWAYSON/config/host/logrotate-alwayson.conf because it is
#    writable by group or others."
# The repo convention is 0664 scottw:scottw, so validating the source in place
# always yields ZERO parsed blocks and looks like an empty policy. Installing a
# 0644 copy is what makes it readable to logrotate at run time too.
install -m 0644 "$SRC_CONF" "$tmp_policy"
# logrotate --debug exits non-zero when it cannot open the state file as a
# non-root user, which is expected here and is NOT a policy error. Under
# `set -e` that non-zero exit would abort the script before the diagnostics
# below can run, so the status is captured explicitly instead of left bare.
rc=0
logrotate --debug "$tmp_policy" >/dev/null 2>"$dbg" || rc=$?
# Filter the known-benign messages before deciding whether anything is wrong:
#
#   "logrotate in debug mode does nothing except printing debug messages"
#       Emitted by every --debug run.
#   "error opening state file /var/lib/logrotate/status: ... Permission denied"
#       --debug run as a user that cannot write /var/lib/logrotate. Expected in
#       the dry-run and validation path; not a policy error.
#   "Ignoring ... because it is writable by group or others"
#       The STAGED source in the repo is mode 0664 (scottw:scottw, the repo
#       convention), so logrotate refuses to read it directly. This is exactly
#       why the script INSTALLS a 0644 copy rather than pointing logrotate at the
#       repo file -- the refusal is the desired behaviour, not a fault. It must
#       be filtered here, or the script can never validate its own source.
#
# Everything else matching unknown option / bad line / error: is fatal.
problems="$(grep -vE 'debug mode does nothing|error opening state file|writable by group or others' "$dbg" \
  | grep -iE 'unknown option|bad line|^error:' || true)"
blocks="$(grep -cE '^rotating pattern' "$dbg" || true)"
rm -f "$dbg" "$tmp_policy"
if [ -n "$problems" ]; then
  echo "ERROR: logrotate reported a problem with the staged policy; not installing" >&2
  echo "$problems" >&2
  exit 1
fi
# A non-zero exit with no parse complaint is not a policy error: --debug exits
# non-zero when it cannot open the state file as a non-root user.
echo "  policy parses cleanly; $blocks blocks found (logrotate exit=$rc)"
[ "${blocks:-0}" -ge 5 ] || {
  echo "ERROR: expected 5 policy blocks (top-level + 4 subdirectories), found ${blocks:-0}" >&2
  exit 1; }

echo "--- installing $DEST_LOGROTATE ---"
install -m 0644 "$SRC_CONF" "$DEST_LOGROTATE"
echo "--- installing $DEST_JOURNALD ---"
install -d -m 0755 "$DEST_JOURNALD_DIR"
install -m 0644 "$SRC_JOURNALD" "$DEST_JOURNALD"

echo "--- verifying installed files ---"
cmp -s "$SRC_CONF" "$DEST_LOGROTATE" \
  && echo "OK: logrotate policy matches the staged source" \
  || { echo "ERROR: logrotate policy differs after install" >&2; exit 1; }
cmp -s "$SRC_JOURNALD" "$DEST_JOURNALD" \
  && echo "OK: journald drop-in matches the staged source" \
  || { echo "ERROR: journald drop-in differs after install" >&2; exit 1; }

echo
echo "Installed. Current state:"
echo "  journald BEFORE restart: $(journalctl --disk-usage 2>&1)"
if [ "$restart_journald" -eq 1 ]; then
  echo "--- restarting systemd-journald (--restart-journald was passed) ---"
  systemctl restart systemd-journald
  sleep 2
  echo "  journald AFTER restart: $(journalctl --disk-usage 2>&1)"
else
  echo
  echo "systemd-journald was NOT restarted. The new caps take effect on the next"
  echo "restart. To apply now, re-run with --restart-journald, or:"
  echo "  sudo systemctl restart systemd-journald"
  echo "Existing journal files are trimmed lazily; journald does not rewrite"
  echo "history on restart, it just enforces the cap as files rotate."
fi
echo "OK: log and journal retention installed"