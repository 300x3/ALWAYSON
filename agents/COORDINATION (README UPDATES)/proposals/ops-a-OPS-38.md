---
item: OPS-38
action: new
section: 17-backup-restore-monitoring-and-completion-criteria
evidence: |
  # NEW ITEM. Next free id after OPS-37. Never renumbered.

  # FINDING: the ten README 17.2 alert rules exist in the repo but the RUNNING
  # Prometheus has loaded none of them. This is the flat-deploy trap (README
  # 16.1.1) caught in the act, and it outranks the missing-emitter gap already
  # recorded in 17.2.1.1.

  $ grep -cE '^\s+- alert:' /ALWAYSON/config/platform/monitoring/alwayson-alerts.yml
  10

  $ curl -s localhost:9090/api/v1/rules | python3 -c 'import json,sys;print("groups:",len(json.load(sys.stdin)["data"]["groups"]))'
  groups: 0

  # prometheus.yml does ask for them, so this is not an omission in config:
  $ grep -n -A2 rule_files /ALWAYSON/config/platform/monitoring/prometheus.yml
  rule_files:
    - /etc/prometheus/alwayson-alerts.yml

  # cause: repo Quadlet has the mount, DEPLOYED copy does not.
  $ diff /ALWAYSON/quadlet/operations/ao-prometheus.container \
         ~/.config/containers/systemd/ao-prometheus.container
  13,18d12
  < # README 17.2 alerting rules (OPS-11). Loaded via rule_files in prometheus.yml.
  < Volume=/ALWAYSON/config/platform/monitoring/alwayson-alerts.yml:/etc/prometheus/alwayson-alerts.yml:ro,Z

  # Prometheus starts CLEANLY with a rule_files glob that matches no file, so
  # there is no error to notice. That is why it survived since 2026-10-03.

  # EXPECTED SECOND-ORDER EFFECT once fixed - three of ten will still be
  # 'no data' because their emitters do not exist (see 17.2.1.1):
  #   AoBackupStale, AoRestoreTestStale, AoRepositoryVerifyStale
  # The other seven read node-exporter / self-metric / textfile series and
  # should go green immediately.

  # NOTE: AoRepositoryVerifyStale measures exactly the control OPS-37 shows has
  # never run. Loading these rules would surface that fault to the operator
  # within its 1h 'for' window. The two items share a narrative.

  PREPARED FIX (NOT applied - live unit is a copy, and restarting ao-prometheus
  is a monitoring-plane service interruption outside this session's remit):
    copy /ALWAYSON/quadlet/operations/ao-prometheus.container over
    ~/.config/containers/systemd/, then systemctl --user daemon-reload and
    restart ao-prometheus. The repository file is already correct; only the
    deployed copy lags.

  NEEDS EXPLICIT OPERATOR APPROVAL: yes - container restart on the monitoring plane.
---
