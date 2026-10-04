---
item: OPS-21
action: close
evidence: |
  $ python3 scripts/build-update/apt_history.py
  packages indexed      : 4445
    installed           : 4281
    upgrade-only (pre-window): 86
    installed unattended: 2098
  log files read        : ['history.log.1.gz', 'history.log.2.gz', 'history.log']

  $ python3 -c "...install_date('dbeaver-ce')..."
  dbeaver-ce   None  Purge   unattended=False  removed=True
  nginx        None  Purge   unattended=False  upgraded=2026-08-22  removed=True
  rclone       2026-10-03  Install  unattended=False

  $ cd /tmp && python3 -c "...load provenance-log.py by path..."
  apt_date(rclone) = 2026-10-03 (apt history, Install)

  $ python3 scripts/build-update/test_generators.py
  Ran 29 tests in 0.282s
  OK

  $ diff /tmp/run1.md /tmp/run2.md && echo IDENTICAL
  IDENTICAL: generator is deterministic across two independent runs

  $ grep -oE '\((apt history|dpkg mtime|earliest evidence)[^)]*\)' run.md \
      | sed 's/; upgraded.*//' | sort | uniq -c | sort -rn
    106 (apt history, Install)
     54 (apt history, Install
      2 (earliest evidence: upgrade; install predates log window)
      2 (dpkg mtime)
section: 12-host-installation-and-configuration
---
The `Installed` column is now ground truth from `/var/log/apt/history.log`, parsed
by the new `scripts/build-update/apt_history.py`. §12.5.1 documents it.

**The item text was wrong about one number.** It said the log "holds 13 dated
transactions". Measured across `history.log` plus both rotated siblings it holds
**186** transactions, indexing **4,445** distinct packages — 4,281 installed,
86 known only as upgrades from before the retained window, 2,098 installed
unattended. The 13 figure is the count in the *live* `history.log` alone, which
is only the newest slice. Anyone reading that item and checking one file would
have concluded the parser was broken.

dpkg's `.list` mtime cannot distinguish install from upgrade because dpkg
rewrites that file on every unpack. apt's log separates them by keyword, so the
column now also distinguishes an unattended upgrade from an operator-initiated
one (`Commandline` inspection) and a purge from an install.

Two honest limits are recorded rather than hidden: coverage is bounded by apt's
own log retention, so absence means *unknown* and never *not installed*; and a
purged package returns `(None, record)` so the cell can read
`not installed (removed/purged <date>)` instead of printing an install date for
software `dpkg -l` no longer lists. `nginx` is the live example — the :8765
portal is a host python3 process now.

**A silent failure was found while verifying this and is the most important
finding in the batch.** The first implementation used a bare `import apt_history`,
which resolves against `sys.path` — and `sys.path[0]` is the *current working
directory*, not the script's directory. `refresh-install-log.sh` runs
`cd "$AO_ROOT"` before invoking the generator, so the import raised `ImportError`
on every production run and fell back to the dpkg mtime. The output looked
completely normal and carried the older, less accurate dates. The module is now
loaded by `__file__`; the CWD-independence is asserted by
`test_apt_history_loads_regardless_of_working_directory`, which runs the
generator as a subprocess with `cwd=/tmp`. Verified above: the label now reads
`(apt history, Install)` from outside the script directory.

Note for the next agent: **do not trust a fallback path that degrades silently.**
Had the fallback logged a warning, this would have been caught on day one.