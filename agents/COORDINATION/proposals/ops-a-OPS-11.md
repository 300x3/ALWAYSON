---
item: OPS-11
action: update
evidence: |
  $ podman images --format '{{.Repository}}:{{.Tag}}' | grep -i alert || echo 'no alertmanager image'
  no alertmanager image

  # rules exist and validate in-tree:
  $ podman run --rm -v .../monitoring:/etc/prometheus:ro --entrypoint promtool \
      docker.io/prom/prometheus@sha256:d47ad27c... check config /etc/prometheus/prometheus.yml
    SUCCESS: 1 rule files found
    SUCCESS: 10 rules found

  # BUT nothing on the host emits the three backup metrics -- re-measured 2026-10-04:
  $ grep -rln 'ao_backup_last_success\|ao_restore_test_last_pass\|ao_backup_last_verify' .
  ./config/platform/monitoring/alwayson-alerts.yml      <- the rules; no emitter
  $ ls /ALWAYSON/data/prometheus-textfile/
  ao-db-security.prom                                  <- the only textfile emitter
  $ curl -s localhost:9090/api/v1/label/__name__/values | python3 -c \
      '...print([x for x in v if x.startswith("ao_")])'
  ao_* series: []

  # and the rules are still not loaded -- repo quadlet has the mount, deployed does not:
  $ grep -n 'alwayson-alerts' quadlet/operations/ao-prometheus.container
  18:Volume=/ALWAYSON/config/platform/monitoring/alwayson-alerts.yml:/etc/prometheus/alwayson-alerts.yml:ro,Z
  $ grep -n 'Volume=' ~/.config/containers/systemd/ao-prometheus.container
  12:Volume=/ALWAYSON/config/platform/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro,Z
  $ curl -s localhost:9090/api/v1/rules
  {"status":"success","data":{"groups":[]}}            <- 0 groups loaded

  # real expressions, read from the file (the 17.2.2 table had these wrong):
  $ grep -n 'alert:\|expr:' config/platform/monitoring/alwayson-alerts.yml
  - alert: AoBackupStale
    expr: (time() - ao_backup_last_success_timestamp_seconds) > 93600
  - alert: AoRestoreTestStale
    expr: (time() - ao_restore_test_last_pass_timestamp_seconds) > 3024000
  - alert: AoRepositoryVerifyStale
    expr: (time() - ao_backup_last_verify_timestamp_seconds) > 777600
section: 17-backup-restore-monitoring-and-completion-criteria
---
**Stays OPEN**, now on **three** grounds rather than one.

Ground 1 -- no routing target. Unchanged from the previous revision: no
Alertmanager container, image or receiver exists. Adding one is a new component,
a new network path and probably a new credential (4.1 rules 6/7), so it needs
operator approval and was not built.

Ground 2 -- the rules are not loaded. New this session, and it is the 16.1.1
trap: the repository Quadlet declares the `alwayson-alerts.yml` read-only mount,
but `~/.config/containers/systemd/ao-prometheus.container` is a flat copy dated
Oct 1 with **one** `Volume=` line. `GET /api/v1/rules` returns `groups: []`.
Nothing was redeployed -- restarting `ao-prometheus` would drop observed scrape
targets, so it is left as an operator action.

Ground 3 -- **the three backup alerts have no metric source.** This is new and it
changes what fixing ground 2 would accomplish. `AoBackupStale`,
`AoRestoreTestStale` and `AoRepositoryVerifyStale` are the only rules not built
from `node_*` or `up`; a repository-wide grep for their metric names returns
exactly one file -- the rule file that consumes them. Prometheus holds zero
`ao_*` series. So the redeploy would load all ten rules, seven would evaluate,
and these three would evaluate to **empty**: an absent series yields no vector,
which neither fires nor reports "no data". The alerting would look correct while
the exact failure mode of 17.2.1 -- a backup that silently stops -- stayed
uncovered. The gap is a missing collector, not a threshold to tune; the
`data/prometheus-textfile/` channel already used by `ao-db-security.prom` is the
obvious shape for it. Not written here: it changes alerting behaviour an operator
relies on.

**Corrected a factual error in 17.2.2.** The threshold table had been
reconstructed from what each rule is *for* rather than read from the `expr:`
lines. The real metric names carry a `_timestamp_seconds` suffix, and the real
thresholds are far looser than the table claimed: 93600 s (26 h) not 900 s,
3024000 s (35 d) not 86400 s, 777600 s (9 d) not 604800 s. The 900 s backup
threshold was **26x tighter than what is written, against a job that runs once a
night** -- a reader tuning against the table would have concluded the nightly job
breaches its own SLO on every run.

**What I got wrong this round.** I nearly filed the emitter gap as "known
unwired" -- carried forward from an earlier revision that had spotted the
missing metric names but filed it as partial coverage rather than checking
whether *anything* produced them. A name nothing emits is not partial coverage;
it is a rule that cannot fire, and the difference matters because partial
coverage is at least visible on a dashboard while this is invisible in both. The
lesson: "referenced" must be checked through to the producer, not stopped at the
consumer.
