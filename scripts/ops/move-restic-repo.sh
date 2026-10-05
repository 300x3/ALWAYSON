#!/usr/bin/env bash
# ALWAYS ON - move the local restic repository to the 1TB Samsung drive
# (operator instruction 2026-10-04, OPS-31: "MOVE IT TO THIS DRIVE
# /media/scottw/1TBSAMSUNGDATA/ AS AO-RESTIC-BACKUP").
#
# WHY THIS NEEDS ROOT: the live repository is /var/backups/alwayson-restic,
# owned root:root mode 0700, and the agent account has NO passwordless sudo
# (verified 2026-10-04: `sudo -n true` fails). It cannot even be measured
# without privilege -- `du -sb` returns nothing. So this script is pkexec-only
# and must be run by the operator.
#
# WHAT IT DOES, IN ORDER, AND WHY:
#   1. Verifies the target drive is actually mounted and is a real filesystem.
#      Copying into a path that merely EXISTS would scatter a root-owned repo
#      onto the root filesystem via the mountpoint's parent -- the exact class
#      of silent data-location bug this move is meant to fix.
#   2. Refuses to run if a repository already exists at the destination. It
#      never merges or overwrites an existing repo.
#   3. Uses restic's OWN copy, not cp/rsync. restic copy is snapshot-aware: it
#      copies pack files and rebuilds indexes, and it verifies the result. A raw
#      cp of a repository that is mid-write can produce one that opens but
#      fails to check.
#   4. Verifies the copy with `restic check --read-data-subset` before
#      declaring success, then re-checks the SOURCE.
#   5. Only after verification does it repoint restic.env at the new path. The
#      source is left in place, NOT deleted. An operator-approved move is not
#      approval to delete.
#
# Usage:
#   pkexec bash /ALWAYSON/scripts/ops/move-restic-repo.sh
set -Eeuo pipefail
IFS=$'\n\t'

DEST_BASE=/media/scottw/1TBSAMSUNGDATA
DEST="$DEST_BASE/AO-RESTIC-BACKUP"
ENVFILE=/ALWAYSON/secrets/operations/restic.env

[ "$(id -u)" -eq 0 ] || { echo "ERROR: must run as root (pkexec)" >&2; exit 1; }
command -v restic >/dev/null || { echo "ERROR: restic not installed" >&2; exit 1; }

echo "== step 1: verify the destination is a real mounted filesystem =="
# The drive is removable (1TB Samsung). If it is not mounted, its mountpoint
# directory still exists on the root filesystem, so a copy would succeed while
# landing on the wrong disk. Compare the device of the mountpoint against the
# device of its parent directory.
if ! mountpoint -q "$DEST_BASE"; then
  echo "ERROR: $DEST_BASE is NOT a mountpoint." >&2
  echo "Mount the drive first, then re-run. Refusing to copy into the" >&2
  echo "root filesystem by way of an unmounted mountpoint." >&2
  exit 2
fi
dev_dest="$(findmnt -no SOURCE --target "$DEST_BASE" 2>/dev/null || echo unknown)"
dev_parent="$(findmnt -no SOURCE --target "$DEST_BASE/.." 2>/dev/null || echo unknown)"
echo "   $DEST_BASE -> $dev_dest"
echo "   parent     -> $dev_parent"
if [ "$dev_dest" = "$dev_parent" ]; then
  echo "ERROR: $DEST_BASE shares a device with its parent ($dev_dest)." >&2
  echo "That means it is not a separate mounted drive. Refusing." >&2
  exit 2
fi
avail_gb="$(df -BG --output=avail "$DEST_BASE" | tail -1 | tr -dc '0-9')"
src_gb="$(du -sg /var/backups/alwayson-restic 2>/dev/null | awk '{print $1}')"
echo "   source ${src_gb:-?} GB, destination has ${avail_gb:-?} GB available"
if [ "${avail_gb:-0}" -lt "${src_gb:-0}" ]; then
  echo "ERROR: destination has less free space than the source needs." >&2; exit 2
fi

echo "== step 2: refuse to overwrite an existing destination repository =="
if [ -e "$DEST" ]; then
  echo "ERROR: $DEST already exists. Refusing to merge or overwrite." >&2
  echo "Move it aside by hand if you intend to replace it." >&2
  exit 2
fi

echo "== step 3: restic-aware copy =="
# Credentials come from the env file, never the command line.
password="$(sed -n 's/^RESTIC_PASSWORD=//p' "$ENVFILE" | tail -n1)"
[ -n "$password" ] || { echo "ERROR: no RESTIC_PASSWORD in $ENVFILE" >&2; exit 3; }
repo_src="$(sed -n 's/^RESTIC_REPOSITORY=//p' "$ENVFILE" | tail -n1)"
[ -n "$repo_src" ] || repo_src=/var/backups/alwayson-restic
echo "   source repo: $repo_src"
echo "   dest repo:   $DEST"
install -d -m 0700 "$DEST"
RESTIC_PASSWORD="$password" restic -r "$repo_src" copy "$DEST"

echo "== step 4: verify the COPY before repointing anything =="
RESTIC_PASSWORD="$password" restic -r "$DEST" check --read-data-subset
echo "   destination verified"
RESTIC_PASSWORD="$password" restic -r "$repo_src" check
echo "   source verified"

echo "== step 5: repoint the configuration at the new location =="
cp -a "$ENVFILE" "${ENVFILE}.pre-move-$(date +%Y%m%d-%H%M%S)"
sed -i "s|^RESTIC_REPOSITORY=.*|RESTIC_REPOSITORY=$DEST|" "$ENVFILE"
echo "   RESTIC_REPOSITORY now: $(sed -n 's/^RESTIC_REPOSITORY=//p' "$ENVFILE")"

echo
echo "MOVE COMPLETE. The destination repository is verified and configured."
echo "The source at $repo_src has been LEFT IN PLACE."
echo "Deleting it is a separate decision and was deliberately not taken here."
echo
echo "Next steps for the operator:"
echo "  1. Run one backup and confirm it lands on the drive:"
echo "       systemctl start ao-restic-backup.service"
echo "       journalctl -u ao-restic-backup.service -n 40 --no-pager"
echo "  2. Once satisfied, remove the old repository by hand:"
echo "       rm -rf $repo_src"
echo "  3. Re-run the restore drill against the NEW path:"
echo "       RESTIC_PASSWORD=\$(/ALWAYSON/scripts/ops/wallet-read-secret.py kdewallet ao-admin restic-repository-password) \\"
echo "         /ALWAYSON/scripts/restore/restore-restic-drill.sh --repo $DEST \\"
echo "           --scratch /var/tmp/ao-restore-drill"