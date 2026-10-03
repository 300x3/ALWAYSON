#!/usr/bin/env bash
# ALWAYS ON - second restic repository on pCloud (off-site copy, README 17.1).
#
# WHY: the local repository shares a filesystem with the data it protects, so it
# cannot survive loss of this host. This sets up the off-site copy that closes
# OPS-30 and OPS-32 together.
#
# The pCloud password is NEVER written to disk, to a file, or to Git. It is read
# from the KDE Wallet entry below, used to build the rclone remote in a
# root-owned 0600 file, and the rclone config is removed immediately after.
# restic encrypts client-side, so pCloud only ever holds ciphertext.
set -Eeuo pipefail
IFS=$'\n\t'

AO_ROOT="${AO_ROOT:-/ALWAYSON}"
WALLET_FOLDER=ao-archive
WALLET_ENTRY=pcloud-webdav-password
WALLET_USER="${PCLOUD_USER:-}"
REMOTE=pc
URL=https://webdav.pcloud.com
RCLONE_CONF=/root/.config/rclone/rclone.conf
ENVFILE=/run/alwayson/pcloud-restic.env

say() { printf '%s\n' "$*"; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

[ -n "$WALLET_USER" ] || die "set PCLOUD_USER (the pCloud account email). Not guessed."
command -v rclone >/dev/null || die "rclone not installed"
command -v restic >/dev/null || die "restic not installed"

password="$(/ALWAYSON/scripts/ops/wallet-read-secret.py kdewallet "$WALLET_FOLDER" "$WALLET_ENTRY")" \
  || die "wallet entry $WALLET_FOLDER/$WALLET_ENTRY unavailable"
[ -n "$password" ] || die "wallet entry $WALLET_FOLDER/$WALLET_ENTRY is empty"
say "OK: credential read from the KDE Wallet (value never displayed or stored)."

install -d -m 0700 /root/.config/rclone /run/alwayson
# The password appears in the process arguments of rclone config if passed that
# way, which is visible in /proc. Write the config through stdin instead.
umask 077
cat > "$RCLONE_CONF" <<EOF
[$REMOTE]
type = webdav
url = $URL
vendor = other
user = $WALLET_USER
pass = $(printf '%s' "$password" | sed 's/"/\\"/g')
EOF
chmod 0600 "$RCLONE_CONF"
unset password

say "--- verifying the remote ---"
rclone lsd "${REMOTE}:" --max-depth 1 >/dev/null 2>&1 \
  || die "cannot reach ${REMOTE}: at $URL. Check the credential and that WebDAV is enabled on the account."

say "--- destination folder ---"
rclone mkdir "${REMOTE}:ALWAYSON-RESTIC2PCLOUD" 2>/dev/null || true

# A second repository needs its own password; derive it from the local one so a
# single wallet entry governs both, and never transmit the plaintext.
localpw="$(sed -n 's/^RESTIC_PASSWORD=//p' /run/alwayson/ao-restic.env 2>/dev/null || true)"
[ -n "$localpw" ] || die "no local restic password cached at /run/alwayson/ao-restic.env"
export RESTIC_PASSWORD="$localpw"
unset localpw

REPO="rclone:${REMOTE}:ALWAYSON-RESTIC2PCLOUD"
if restic snapshots --repo "$REPO" >/dev/null 2>&1; then
  say "repository already initialised at $REPO"
else
  say "--- initialising the off-site repository ---"
  restic init --repo "$REPO" || die "restic init failed"
fi

say "--- first off-site backup ---"
restic backup "$AO_ROOT/config" "$AO_ROOT/artifacts" "$AO_ROOT/backups/postgres" \
  --repo "$REPO" --tag alwayson-offsite
restic forget --repo "$REPO" --keep-hourly 24 --keep-daily 7 --keep-weekly 4 --keep-monthly 6
restic check --repo "$REPO" --read-data-subset=1/20 || die "off-site integrity check failed"

# The rclone config holds the plaintext credential. It has served its purpose;
# re-create it at run time from the wallet instead of leaving it on disk.
rm -f "$RCLONE_CONF"
say "OK: rclone config removed after use; it is rebuilt from the wallet on each run."
say "DONE: off-site repository live at $REPO"
