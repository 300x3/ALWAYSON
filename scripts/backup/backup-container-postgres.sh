#!/usr/bin/env bash
# ALWAYS ON - dump a PostgreSQL database from a Quadlet container (podman exec).
#
# Used for the databases that are container-scoped by design and therefore do NOT
# live on the host cluster: mastodon (mastodon-db) and webodm (ao-webodm-db).
# backup-host-postgres.sh cannot reach them, because it always dumps
# 127.0.0.1:5432 on the host.
#
# Usage: backup-container-postgres.sh <label> <container> <db> <user>
set -Eeuo pipefail
label="${1:?}"; container="${2:?}"; db="${3:?}"; user="${4:?}"
outdir="/ALWAYSON/backups/postgres/${label}"
mkdir -p "$outdir"
out="${outdir}/$(date -u +%Y%m%dT%H%M%SZ)-${db}.sql.gz"
tmp="${out}.tmp"
cleanup() { rm -f "$tmp"; }
trap cleanup EXIT

# pg_dump runs INSIDE the container, so no password leaves it: the container
# already holds its own credentials from the wallet-materialised env file.
# Run as the container's postgres OS user, and name the database role
# explicitly. The role and the OS user do not always share a name - the
# mastodon-db image has no 'mastodon' user, and the container's default user is
# root, which is not a database role either.
if podman exec -u postgres -e PGUSER="$user" -e PGDATABASE="$db" "$container" \
     pg_dump --no-owner --no-privileges 2>"$tmp.err" | gzip -9 >"$tmp"; then
  size=$(stat -c %s "$tmp")
  if [ "$size" -lt 200 ]; then
    echo "FAILED: ${label}/${db} dump suspiciously small (${size} bytes)" >&2
    cat "$tmp.err" >&2
    exit 1
  fi
  mv "$tmp" "$out"
  rm -f "$tmp.err"
  echo "OK: ${label}/${db} -> $out (${size} bytes)"
else
  echo "FAILED: ${label}/${db} container dump" >&2
  cat "$tmp.err" >&2
  exit 1
fi
