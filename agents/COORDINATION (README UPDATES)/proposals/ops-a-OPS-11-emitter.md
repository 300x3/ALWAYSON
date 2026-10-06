---
item: OPS-11
action: update
evidence: |
  # THIRD proposal on OPS-11. Corrects a table in the section file and adds the
  # open ground that survives the redeploy OPS-11 already requires.

  # FINDING: the three backup alerts depend on metrics NOTHING emits.
  # A repository-wide grep returns only the rule file that CONSUMES them:
  $ cd /ALWAYSON && grep -rln 'ao_backup_last_success\|ao_restore_test_last_pass\|ao_backup_last_verify' .
  ./config/platform/monitoring/alwayson-alerts.yml

  # the only textfile emitter that exists:
  $ ls /ALWAYSON/data/prometheus-textfile/
  ao-db-security.prom

  # and Prometheus holds zero ao_* series:
  $ curl -s localhost:9090/api/v1/label/__name__/values | \
      python3 -c 'import json,sys; v=json.load(sys.stdin)["data"]; print("ao_* series:", [x for x in v if x.startswith("ao_")])'
  ao_* series: []

  # still no rule groups loaded at all (unchanged from the correction proposal):
  $ curl -s localhost:9090/api/v1/rules | python3 -c 'import json,sys; print("groups:",len(json.load(sys.stdin)["data"]["groups"]))'
  groups: 0

  # CORRECTION to the section's 17.2.2 threshold table. The previous names and
  # values were reconstructed from meaning, not read from the file. Real expr lines:
  $ grep -n 'alert:\|expr:' /ALWAYSON/config/platform/monitoring/alwayson-alerts.yml | grep -A1 'AoBackup\|AoRestore\|AoRepository'
  108:    - alert: AoBackupStale
  109:      expr: (time() - ao_backup_last_success_timestamp_seconds) > 93600
  123:    - alert: AoRestoreTestStale
  124:      expr: (time() - ao_restore_test_last_pass_timestamp_seconds) > 3024000
  137:    - alert: AoRepositoryVerifyStale
  138:      expr: (time() - ao_backup_last_verify_timestamp_seconds) > 777600
section: 17-backup-restore-monitoring-and-completion-criteria
---
Adds **§17.2.1.1**, which takes the "three rules reference metrics nothing
exports" note that both prior OPS-11 proposals mention in passing and makes it
the measured, primary statement.

`AoBackupStale`, `AoRestoreTestStale` and `AoRepositoryVerifyStale` are the only
three of the ten rules built from custom series rather than `node_*`/`up`, and
**no exporter, textfile collector, recording rule or scrape job produces any
`ao_*` series anywhere in the repository.** The single repo-wide grep returns
exactly one file: the rule file that consumes them. Prometheus currently holds
zero `ao_*` series.

Consequence, which is the point: adding the missing `Volume=` line and
restarting `ao-prometheus` would load all ten rules, but these three would
evaluate to an **empty vector**. An expression over a non-existent series does
not fire and does not report "no data" — it is silent. So the redeploy does not
fix OPS-11; the remaining work is a missing collector, not a threshold and not a
deployment. The `data/prometheus-textfile/` channel already used by
`ao-db-security.prom` is the obvious implementation. I have not written it,
because it changes what `ops` emits into a shared monitoring path and it is the
mechanism by which an operator would be paged about backup failure — new
alerting behaviour, which is operator territory.

**Also corrected the §17.2.2 threshold table, now transcribed from the `expr:`
lines.** The previous entry claimed `AoBackupStale` fires at 900 s (15 m); the
file says 93600 s (26 h). The old names (`ao_restic_backup_last_success`,
`ao_restore_test_last_run`, `ao_repository_verify_last_success`) were likewise
reconstructed rather than read, and were wrong the same way.

What I got wrong, and it is the same failure mode twice in one session: I wrote
a threshold table from what the rules are *for* instead of reading the values.
The invented 900 s against a nightly job was **twenty-six times tighter** than
the real threshold — a reader tuning against it would have concluded the nightly
backup breaches its own SLO on every run. The real 93600 s is a 26 h threshold
against a 24 h job: a 2 h grace window, which is a deliberate decision someone
made. My "sensible" number was the wrong one. A retuned table must be diffed
against its source, however confident it feels; and a threshold that looks loose
deserves a question rather than a correction.

Files changed: `agents/COORDINATION (README UPDATES) (README UPDATES)/…/17-…/section.md` (new §17.2.1.1;
§17.2.2 table corrected).