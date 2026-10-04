---
item: OPS-11
action: update
evidence: |
  $ curl -s http://127.0.0.1:9090/api/v1/rules | python3 -c '...print("groups:",len(...))'
  groups: 0

  $ podman ps -a --format '{{.Names}}' | grep -i alert || echo 'no alertmanager container'
  no alertmanager container
  $ podman images --format '{{.Repository}}:{{.Tag}}' | grep -i alert || echo 'no alertmanager image'
  no alertmanager image

  # after the change — rules exist and validate:
  $ podman run --rm -v .../monitoring:/etc/prometheus:ro --entrypoint promtool \
      docker.io/prom/prometheus@sha256:d47ad27c... check config /etc/prometheus/prometheus.yml
  Checking /etc/prometheus/prometheus.yml
    SUCCESS: 1 rule files found
   SUCCESS: /etc/prometheus/prometheus.yml is valid prometheus config file syntax

  Checking /etc/prometheus/alwayson-alerts.yml
    SUCCESS: 10 rules found

  $ python3 -c "import yaml; ..."   # rule/group inventory
    ao-storage -> 3 rules
      - AoFilesystemLowSpace | for 30m | sev warning
      - AoFilesystemCriticallyFull | for 10m | sev critical
      - AoFilesystemReadOnly | for 5m | sev critical
    ao-backup -> 3 rules
      - AoBackupStale | for 15m | sev critical
      - AoRestoreTestStale | for 1h | sev warning
      - AoRepositoryVerifyStale | for 1h | sev warning
    ao-host -> 2 rules
      - AoMemoryLow | for 15m | sev warning
      - AoLoadHigh | for 30m | sev warning
    ao-collector -> 2 rules
      - AoExporterDown | for 5m | sev critical
      - AoDbSecurityCollectorStale | for 30m | sev warning
    total rules: 10

  $ for m in node_systemd_unit_state ...; do curl -s ".../api/v1/query?query=$m"; done
  node_systemd_unit_state          series: 0
  node_filesystem_avail_bytes      series: 12
section: 17-backup-restore-monitoring-and-completion-criteria
---
**Stays OPEN.** Two of the three parts of this item are now done; the third is
blocked on an operator decision.

Done in §17.2.1 and §17.2.2: the alerting component is named (Prometheus rule
evaluation, explicitly not Alertmanager, which is measured absent), the
thresholds are stated per rule in a ten-rule table, and the rules exist as a
validated file — `config/platform/monitoring/alwayson-alerts.yml`, mounted
read-only by `ao-prometheus.container` and loaded via `rule_files`.

Why it is not closed: **there is no routing target.** The item asks for "the
routing target per severity" and none exists — no Alertmanager container, no
image, no receiver anywhere. Rules evaluate and show up in Grafana, but nothing
reaches an operator who is not already looking at the dashboard. Adding
Alertmanager plus a delivery target means a new component, a new network path
and very likely a new credential, which is §4.1 rule 6/7 territory and needs
explicit operator approval. I stopped there rather than build it.

Also honest about partial coverage, recorded in §17.2.2 and §17.2.3: three of
the ten rules (`AoBackupStale`, `AoRestoreTestStale`,
`AoRepositoryVerifyStale`) reference metric names nothing currently exports, so
they cannot fire yet; and seven of the eleven required conditions have no
exporter at all, measured by `node_systemd_unit_state` returning 0 series and
only two scrape jobs existing. A rule that can never fire is not alerting, so
these are documented as unwired rather than counted as coverage.

**What I got wrong, twice, both worth reading.** First, I inlined a top-level
`groups:` block into `prometheus.yml` because that is how rule files normally
look; `promtool` rejected it with `field groups not found in type
config.plain`, and the rules had to be split into a second file that
`prometheus.yml` references through `rule_files`. Second, while fixing the YAML
indentation I ran a `sed` that stripped the two leading spaces from every line
in a range, which broke the block structure, and then a second `sed` that added
them back to a range whose start line I had miscomputed. Both produced
plausible-looking files that failed validation. Lesson: validate YAML with a
real parser after every reindent, and never fix indentation with a blind
line-range `sed`.

Files changed: `config/platform/monitoring/alwayson-alerts.yml` (new),
`config/platform/monitoring/prometheus.yml` (rule_files + moved comment),
`quadlet/operations/ao-prometheus.container` (second read-only mount).