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
supersedes: |
  Revision 2026-10-05T~08:00 — corrects the scale of this item. The original
  framing ("the forced rotation at 00:18:38") is superseded on two points:
  (1) there has now been a second, UNATTENDED rotation at 2026-10-05 00:22:50,
  so this is no longer latent; (2) the original overstated imminent loss by
  implying the .1 files are "the real, current logs". They are not currently
  growing. See §17.5.3.
---
**New work item raised by this session, not a closure.**

**Correction, 2026-10-05 — two things in my original framing of this item were
wrong, and the second one matters.**

1. It attributed the phenomenon to "the forced rotation at 00:18:38". That was
   the only rotation I had evidence for. A second rotation has since run
   **unattended** at 2026-10-05 00:22:50, which promotes this from a latent
   hazard to an active one. Evidence in §17.5.2 and in `ops-a-OPS-25.md`.
2. It said the `.1` files "are the real, current logs" and implied output is
   actively diverging. **They are not currently growing.** Measured twice, 20 s
   apart:

```
$ stat -c '%s %y' /ALWAYSON/logs/sim-gz-server.log.1; sleep 20; stat -c '%s %y' /ALWAYSON/logs/sim-gz-server.log.1
1437117 2026-10-04 09:25:00.508796406 -0700
1437117 2026-10-04 09:25:00.508796406 -0700
```

Gazebo has written **nothing** since 2026-10-04 09:25, and `sim-gz-server.log`
being 0 bytes is as much a consequence of that silence as of the detached
descriptor. I overclaimed. The honest statement is that the fault is dormant
*right now* and becomes live *on the next write*, which lands in an inode the
policy has already stopped tracking. `ao-sim-fabrication-gz` has been up 38 h and
`ao-sim-fabrication-foxglove` 2 d 12 h — both quiet, consistent with an idle
simulation rather than a crashed one.

The mechanism, unchanged and still correct: `conmon` opened
`-l k8s-file:/ALWAYSON/logs/sim-gz-server.log` once at container start and never
re-resolves the name. `nocopytruncate` renames the path without touching the
inode, so the writer follows the inode while the policy tracks the name. After
`rotate 14` shifts the name onward the inode is unlinked **while still open**,
and output continues into space no `ls` or `du` can see, reclaimed only at
process exit.

```
$ lsof /ALWAYSON/logs/sim-gz-server.log.1
COMMAND     PID   USER FD   TYPE DEVICE SIZE/OFF     NODE NAME
conmon   1195162 scottw 6w   REG  259,2  1437117 18222278 /ALWAYSON/logs/sim-gz-server.log.1

$ stat -c '%n ino=%i links=%h size=%s' /ALWAYSON/logs/sim-gz-server.log*
/ALWAYSON/logs/sim-gz-server.log    ino=18223611 links=1 size=0   <- policy manages this
/ALWAYSON/logs/sim-gz-server.log.1  ino=18222278 links=1 size=1437117  <- conmon writes this
```

`links=1` on the detached inode is the number to watch: it drops to 0 the moment
the last `.N` rotation removes the name, and that is the point of no return.

**The validator blindness still stands and is the more useful half of this
item** — `check-logs-journals.sh` reads the *live* file's mtime, which rotation
recreated fresh, so an empty file satisfies it and a detached writer is
undetectable:

```
$ bash scripts/validation/check-logs-journals.sh | grep -E 'sim-gz|foxglove|PASS'
sim-gz-server.log                  OK (1d)          2026-10-04T07:18:38Z
sim-foxglove-bridge.log            OK (1d)          2026-10-04T07:18:38Z
PASS: every Section 16.3 log exists and is within its staleness budget
```

Re-measured 2026-10-05; an earlier run of the same command on 2026-10-04 showed
`OK (0d)`. The drift from 0d to 1d is the staleness counter working correctly
against a live file that nobody is writing to — which is precisely the point:
the validator is watching a file that no writer holds open, and will keep
reporting PASS as long as its staleness budget is not exceeded, entirely
regardless of whether Gazebo is actually logging.

**Why this is not fixed here.** Fixing the mechanism means `copytruncate` or a
`postrotate` that signals a running simulation
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