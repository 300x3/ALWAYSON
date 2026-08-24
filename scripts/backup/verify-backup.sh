# ALWAYS ON - verify-backup.sh: weekly repository integrity check (Section 4.4).
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
envfile="$AO_ROOT/secrets/operations/restic.env"
[[ -f "$envfile" ]] || { echo "PENDING: restic env not provisioned" >&2; exit 3; }
bash -c "set -a && source '$envfile' && restic check --read-data-subset=5%"
ao_audit "restic integrity check completed"
echo "OK: repository integrity verified"
