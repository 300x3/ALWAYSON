---
item: OPS-36
action: open
evidence: |
  # NEW ITEM, first free id in the OPS group (19.1 tops out at OPS-34; my own
  # unmerged OPS-35 proposal also predates this one). Never renumbered.

  # FINDING: the installed logrotate policy justifies nocopytruncate with a
  # safety claim that is FALSE, and two live containers are logging into a
  # rotated file as a result.

  $ grep -n -A3 'nocopytruncate is safe' /etc/logrotate.d/alwayson
  # nocopytruncate is safe here because every writer in scripts/lib/common.sh
  # appends with >> per call and holds no descriptor - verified after rotation:
  # writes landed in the new file and backup.log.1 stayed at 1247 bytes.

  # that writer family does rotate correctly — the sample was not wrong:
  $ stat -c '%n size=%s' /ALWAYSON/logs/backup.log*
  /ALWAYSON/logs/backup.log   size=110
  /ALWAYSON/logs/backup.log.1 size=1247

  # but "every writer" was generalised from that one library. Podman holds a
  # descriptor it never reopens:
  $ podman ps --format '{{.Names}} {{.Status}}' | grep -iE 'gz|foxglove'
  ao-sim-fabrication-foxglove  Up 44 hours
  ao-sim-fabrication-gz       Up 22 hours

  $ lsof /ALWAYSON/logs/sim-gz-server.log.1 /ALWAYSON/logs/sim-foxglove-bridge.log.1
  COMMAND     PID   USER FD   TYPE DEVICE SIZE/OFF     NODE NAME
  conmon   868080 scottw 7w   REG  259,2   100660 18222280 /ALWAYSON/logs/sim-foxglove-bridge.log.1
  conmon  1195162 scottw 6w   REG  259,2  1437117 18222278 /ALWAYSON/logs/sim-gz-server.log.1

  # the live files are empty and nothing holds them; the .1 files are the
  # real, current logs:
  $ stat -c '%n size=%s mtime=%y' /ALWAYSON/logs/sim-gz-server.log*
  /ALWAYSON/logs/sim-gz-server.log   size=0      mtime=2026-10-04 00:18:38
  /ALWAYSON/logs/sim-gz-server.log.1 size=1437117 mtime=2026-10-04 09:25:00
  $ lsof /ALWAYSON/logs/sim-gz-server.log
  (no output)

  # the freshness validator is satisfied by the empty file, so it PASSES:
  $ bash scripts/validation/check-logs-journals.sh | grep -E 'sim-gz|foxglove'
  sim-gz-server.log            OK (0d)          2026-10-04T07:18:38Z
  sim-foxglove-bridge.log       OK (0d)          2026-10-04T07:18:38Z
  PASS: every Section 16.3 log exists and is within its staleness budget

  # conmon's cmdline proves the writer is the k8s-file log driver opened at
  # container start, not a shell appender:
  $ tr '\0' ' ' < /proc/1195162/cmdline | grep -o '\-l k8s-file:[^ ]*'
  -l k8s-file:/ALWAYSON/logs/sim-gz-server.log
section: 17-backup-restore-monitoring-and-completion-criteria
---
**New work item raised by this session, not a closure.**

`/etc/logrotate.d/alwayson` contains a justification for `nocopytruncate` that
is factually wrong, and the policy is currently misdirecting the output of two
running simulation containers. Gazebo (`ao-sim-fabrication-gz`, up 22 hours) and
Foxglove (`ao-sim-fabrication-foxglove`, up 44 hours) have been writing into
`sim-gz-server.log.1` and `sim-foxglove-bridge.log.1` since the forced rotation
at 00:18:38, while the live logs those files are supposed to feed are 0 bytes.
The logrotate policy carries `rotate 14` + `daily`, so those files become
deletion candidates and, when removed, the logs end silently.

The worse half is that `check-logs-journals.sh` reports `OK (0d)` and overall
`PASS`. It checks the live file's mtime, and the rotation recreated that file
fresh and empty — so a validator that can be satisfied by an empty file cannot
detect a detached writer.

**Why this is not fixed here.** Two reasons, both hard. Fixing the mechanism
means `copytruncate` or a `postrotate` that signals a running simulation
container — an operator decision touching a live service. Correcting the false
comment means editing `config/host/logrotate-alwayson.conf`, which this session
does not own, and it would break the `cmp` byte-identity that OPS-25's evidence
depends on until the file is re-installed with root. I made that edit by
accident, reverted it, and confirmed the revert (`git diff --stat` empty,
`cmp` still identical); it is recorded here as a self-reported lapse rather than
left silent.

**What I got wrong.** The original comment's error was generalised from a
sample: `scripts/lib/common.sh` was tested, it passed, and the result was
written down as "every writer". Checking one logging helper does not establish
what every writer does — the container log drivers were never in that library
and never were in that check.