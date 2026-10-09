---
item: OPS-11
action: update
evidence: |
  # *** THE PRIOR PROPOSAL'S FIRST EVIDENCE LINE WAS A FALSE PASS. ***
  # It cited `groups: 0` as proof the rules were loaded. data.groups having
  # length zero means Prometheus is evaluating NO RULE GROUPS AT ALL.
  # The remaining lines in it (promtool on a --rm throwaway container) are
  # valid evidence that the FILES are correct. They say nothing about the
  # RUNNING service, which is what this correction is about.
  $ curl -s http://127.0.0.1:9090/api/v1/rules \
      | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["data"]["groups"]))'
  0

  # the repository Quadlet has BOTH mounts:
  $ grep -c '^Volume=' quadlet/operations/ao-prometheus.container
  2
  # the DEPLOYED copy has ONE - Quadlets deploy flat, so the edit never took effect:
  $ grep -c '^Volume=' ~/.config/containers/systemd/ao-prometheus.container
  1
  $ grep '^Volume=' ~/.config/containers/systemd/ao-prometheus.container
  Volume=/ALWAYSON/config/platform/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro,Z

  # confirmed from inside the running container:
  $ podman exec ao-prometheus ls /etc/prometheus/alwayson-alerts.yml
  ls: cannot access '/etc/prometheus/alwayson-alerts.yml': No such file or directory

  # a SECOND failure behind the first: a file bind mount follows the INODE, and
  # the in-tree config was replaced rather than edited, so the container holds
  # the OLD inode. The mount LOOKS correct and promtool says SUCCESS on it.
  $ stat -c 'host      inode=%i size=%s' /ALWAYSON/config/platform/monitoring/prometheus.yml
  host      inode=18223436 size=2503
  $ podman exec ao-prometheus stat -c 'container inode=%i size=%s' /etc/prometheus/prometheus.yml
  container inode=18219046 size=1881
  $ podman exec ao-prometheus grep -c rule_files /etc/prometheus/prometheus.yml
  0
  $ podman exec ao-prometheus promtool check config /etc/prometheus/prometheus.yml
  Checking /etc/prometheus/prometheus.yml
   SUCCESS: /etc/prometheus/prometheus.yml is valid prometheus config file syntax

  # routing target still absent, re-measured:
  $ podman ps -a --format '{{.Names}}' | grep -i alertmanager || echo NONE
  NONE
section: 17-backup-restore-monitoring-and-completion-criteria
---
**Supersedes** the evidence line `groups: 0` in `ops-a-OPS-11.md` of this date.
That earlier proposal is left in place rather than edited, per the rule that a
session does not rewrite its own prior record — but its first evidence line is
wrong and this corrects it.

**I filed `groups: 0` as evidence that the rules were loaded. It is the
opposite.** `data.groups` having length zero means Prometheus is evaluating no
rule groups at all. I read a healthy-looking integer as proof of success without
asking what the number meant. The rest of that proposal is fine — `promtool`
against a throwaway container does prove the two *files* are valid and contain
10 rules — but it says nothing about the running service, which is the entire
point of this item.

Re-measuring properly found **two independent deployment faults**, neither
visible from the repository:

1. **The mount was never deployed.** `quadlet/operations/ao-prometheus.container`
   declares two `Volume=` lines; the deployed copy at
   `~/.config/containers/systemd/ao-prometheus.container` declares one. Quadlets
   deploy as flat copies, so editing the in-tree file changed nothing live, and
   the alerts file is absent from the running container.
2. **The mounted config is stale by inode.** Even the mount that does exist is
   bound to the old inode (18219046, 1881 B) rather than the current one
   (18223436, 2503 B). A file bind mount follows the inode, not the path, so
   replacing the file in place — which an editor or `git checkout` does — leaves
   the container reading the previous version indefinitely. The container's copy
   has no `rule_files:` key at all.

Fault 2 is the more dangerous, because it is invisible: the mount looks correct,
and `promtool check config` on the container's own copy returns SUCCESS, since
the stale file is a perfectly valid config — just not the one on disk. A future
fix that adds the alerts mount without restarting the container would appear to
work and still evaluate no rules.

**The generalisable lesson**, since this is the second time this session filed a
number that could not fail. The drill in OPS-24 compared the restored tree with
itself and reported `identical: 63`. Here a zero was read as healthy. In both
cases the measurement was structurally incapable of signalling the fault it was
being used to rule out. A verification has to be asked "what result would prove
this broken?", and the answer has to be checked against something real.

I did not redeploy. Restarting `ao-prometheus` interrupts its scrape targets,
and adding a mount to a deployed Quadlet is an operator action. **OPS-11 now has
three open grounds, not one:** no routing target (unchanged), the alerts mount
not deployed (new), and the stale config inode (new).

Unchanged and still true: the alerting component is Prometheus rule evaluation,
the ten thresholds stand, and `AoBackupStale` / `AoRestoreTestStale` /
`AoRepositoryVerifyStale` still reference metric names nothing exports — so even
once deployed, those three cannot fire.

Files changed: `agents/COORDINATION (README UPDATES)/…/17-…/section.md` (§17.2.1 rewritten;
§17.2.2 and §17.2.3 unchanged and still accurate).