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
  15:  # mastodon and webodm live in their own containers; the host dump cannot see them.
  18:  bash "$C" mapping ao-webodm-db webodm_dev postgres || { echo "FAIL: webodm"; fail=1; }

  $ podman inspect ao-webodm-webapp --format '{{range .Config.Env}}{{println .}}{{end}}' \
      | grep -vi 'password\|secret\|key' | grep -i database
  WO_DATABASE_HOST=ao-webodm-db
section: 08-mapping-and-photogrammetry
---
§8 gains a new **§8.4.1** stating the single answer the item asks for.

- Logical database: **`webodm_dev`** (not `webodm`, which survives only as a 2026-09-30
  rollback artefact per ST-03).
- Physical storage: **`/home/scottw/webodm/dbdata`**, bind-mounted to `/var/lib/postgresql/data`
  on `ao-webodm-db`. This confirms §8.4 was already right and needs no change.
- Backup scope: **included**, proven at `scripts/backup/dump-all-postgres.sh:18`.

**The third requirement — "confirm it is inside the backup scope" — is met. But the acceptance
criteria also observed that §8.1/§8.5 require all mapping storage on the photogrammetry drive,
"which as written contains neither." That part is NOT met and is not fixed.** The PostgreSQL
data directory is on the root filesystem. I recorded this as an explicit approved deviation in
§8.4.1 rather than dropping the requirement, and flagged that the drive-residency half should
be carried forward as a **new FIELD item** rather than reopening FIELD-11. Moving a live
PostgreSQL data directory is an operator decision and a service-configuration change.

If the compiler prefers to keep FIELD-11 open instead, the honest status is "name and
location decided and evidenced; drive residency still deviated."