---
item: FIELD-11
action: close
evidence: |
  $ podman inspect ao-webodm-db --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{end}}'
  /home/scottw/webodm/dbdata -> /var/lib/postgresql/data

  $ podman exec ao-webodm-db psql -U postgres -tAc \
      "SELECT datname FROM pg_database WHERE NOT datistemplate ORDER BY 1;"
  postgres
  webodm
  webodm_dev

  $ grep -n webodm scripts/backup/dump-all-postgres.sh
  18:  bash "$C" mapping ao-webodm-db webodm_dev postgres || { echo "FAIL: webodm"; fail=1; }

  $ podman inspect ao-webodm-webapp --format '{{range .Config.Env}}{{println .}}{{end}}' \
      | grep -vi 'password\|secret\|key' | grep -i database
  WO_DATABASE_HOST=ao-webodm-db
section: 08-mapping-and-photogrammetry
---

§8 gains a new **§8.4.1** stating the single answer the item asks for.

- Logical database: **`webodm_dev`** (not `webodm`, which survives only as a 2026-09-30
  rollback artefact per ST-03).
- Physical storage: **`/home/scottw/webodm/dbdata`**, bind-mounted to
  `/var/lib/postgresql/data` on `ao-webodm-db`. This confirms §8.4 was already right and needs no
  change.
- Backup scope: **included**, proven at `scripts/backup/dump-all-postgres.sh:18`.

**Not fixed:** the mapping PostgreSQL data directory is still on the root filesystem rather than
the photogrammetry drive. That is an approved deviation (recorded in §8.4.1) and is carried forward
as a separate FIELD item for the drive-residency half rather than reopening FIELD-11.
