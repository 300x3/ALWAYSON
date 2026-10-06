---
item: OPS-34
action: close
evidence: |
  $ podman ps -a --format '{{.Names}} {{.Status}}' | grep -i grafana
  ao-grafana Up 12 hours

  $ podman exec ao-grafana sh -c 'ls /var/lib/grafana/plugins/; env | grep ALLOW_LOADING'
  frser-sqlite-datasource
  GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS=frser-sqlite-datasource

  # Grafana's own API, not the config file:
  $ podman exec ao-grafana sh -c 'curl -s -u "$GF_SECURITY_ADMIN_USER:$GF_SECURITY_ADMIN_PASSWORD" \
      "http://localhost:3000/api/datasources/uid/ao-sqlite"'
  {"name":"ALWAYS ON SQLite","type":"frser-sqlite-datasource","uid":"ao-sqlite",
   "jsonData":{"databases":[{"path":"/var/lib/ao-sqlite/db-openclaw-agent-main.db"},...]},"access":"proxy"}

  $ podman exec ao-grafana sh -c 'curl -s -u "$GF_SECURITY_ADMIN_USER:$GF_SECURITY_ADMIN_PASSWORD" \
      "http://localhost:3000/api/datasources/uid/ao-sqlite/health"'
  {"message":"Data source is working","status":"OK"}

  $ podman logs ao-grafana 2>&1 | grep checkHealth | grep -c 'status=ok'
  9
section: 17-backup-restore-monitoring-and-completion-criteria
---
Closed. The operator directive of 2026-10-03 — "Grafana must have a real SQLite
datasource", superseding the snapshot design — is implemented and verified in
the running container, not merely in the provisioning file.

Verified three ways, deliberately: the plugin directory lists
`frser-sqlite-datasource`; the unsign-plugin allow-list names that one id (not
`*`); Grafana's own HTTP API returns the datasource with
`"type":"frser-sqlite-datasource"` and `"status":"OK"` from `/health`; and the
container log shows nine `checkHealth ... status=ok` entries across the seven
provisioned stores (AO-SQLite, Elisa, MeshChatX observer, nPerf history, nPerf
settings, openclaw main, openclaw sitebot).

Note what did **not** change: the snapshot indirection described in
`config/platform/monitoring/grafana/provisioning/datasources/sqlite-snapshots.yml`
still stands, and it still holds. Every path points into `/var/lib/ao-sqlite`,
which is a read-only bind mount of `VACUUM INTO` output written by
`collect-system-health.py`, so Grafana still never opens a live store. A real
SQLite datasource means a real SQLite *driver*, not a live read of a WAL store.
Both measured reasons for the indirection survive: a WAL store cannot be read
through a read-only mount because SQLite must write the `-shm` index, and
`VACUUM INTO` output is delete-mode and opens cleanly read-only.

The unsigned-plugin caveat recorded earlier still applies and is unchanged:
`plugin.json` carries `signature: null` and Grafana refuses to load the plugin
without the allow-list entry. That is a standing supply-chain decision for the
operator, not an outstanding work item.
