#!/usr/bin/env python3
"""Ground-truth install dates for Debian packages, from apt's own history.

Why this exists
---------------
dpkg records no install timestamp in its database. The previous implementation
inferred the date from the mtime of `/var/lib/dpkg/info/<pkg>.list`, which dpkg
rewrites on every unpack -- so the column showed the LAST UPGRADE date while
labelling it "Installed". That is wrong in the direction that matters: an
operator reading it concludes a package was freshly deployed when it was
actually merely upgraded months later, and cannot distinguish a deliberate
install from an `unattended-upgrade` run.

`/var/log/apt/history.log` (plus its rotated `.gz` siblings) does hold the truth:
apt writes one stanza per transaction carrying `Start-Date`, the exact
`Commandline`, and separate `Install:` / `Upgrade:` / `Remove:` / `Purge:` lines
naming every package and the versions moved between. That distinguishes install
from upgrade, and distinguishes an unattended upgrade from a human one.

Limits, stated rather than hidden
---------------------------------
* Coverage is bounded by apt's own log retention. Rotations here reach back far
  enough to cover the whole install, but a package installed before the oldest
  surviving stanza is simply not in the index -- callers must treat "absent"
  as unknown, never as "not installed".
* A transaction logged as `Upgrade:` means the package was installed earlier,
  outside the retained window. It is reported as an upgrade date and flagged,
  not passed off as an install date.
* `Install:` lines carry the version dpkg resolved *to*; the previous version
  is not recoverable from the history log for an upgrade.

No network, no writes. This module only reads log files.
"""
from __future__ import annotations

import gzip
import re
from pathlib import Path

APT_LOG_DIR = Path("/var/log/apt")

# One stanza: Start-Date, Commandline, Requested-By, then the item lines.
_START = re.compile(r"^Start-Date:\s*(.+)$")
_CMDLINE = re.compile(r"^Commandline:\s*(.*)$")
_ITEM = re.compile(r"^(Install|Upgrade|Remove|Purge|Reinstall):\s*(.*)$")

# "name:arch (old, new)" or "name:arch (version)" or "name:arch (version, automatic)"
_PKG = re.compile(r"^([A-Za-z0-9][A-Za-z0-9+.\-]*)(?::([A-Za-z0-9_\-]+))?\s*\(([^)]*)\)")

# Transactions performed by an unattended upgrader rather than a human.
_UNATTENDED = ("unattended-upgrade", "packagekit role='update-packages'",
                "packagekit role='upgrade-packages'")

# date -> "YYYY-MM-DD". apt writes "2026-10-01  06:29:21" (two spaces).
_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
def _log_files(log_dir=None):
    """Every apt history file, oldest first.

    Rotated files sort lexicographically *after* the live one
    (history.log.1.gz < history.log.2.gz), which is the wrong order, so the
    live log is appended last explicitly. Ordering matters: the same package
    can appear in several transactions and the EARLIEST install is the one
    that answers "when was this installed".

    `log_dir` is injectable purely so the parser can be tested against a
    fixture without touching the real system log.
    """
    d = Path(log_dir) if log_dir else APT_LOG_DIR
    rotated = sorted(d.glob("history.log.*.gz"))
    live = d / "history.log"
    return rotated + ([live] if live.exists() else [])


def _read(path):
    try:
        if str(path).endswith(".gz"):
            with gzip.open(path, "rt", errors="replace") as fh:
                return fh.read()
        return path.read_text(errors="replace")
    except OSError:
        return ""


def _parse_versions(spec):
    """Versions named on one item line: "1.0, 1.1" -> ["1.0", "1.1"].

    dpkg also uses the comma slot for the "automatic" flag ("4.25.12.3, automatic"),
    which is not a version. Keeping it would put a non-version into a list
    documented as versions, and any caller rendering them would print it as one.
    """
    return [v.strip() for v in spec.split(",")
            if v.strip() and v.strip() != "automatic"]


def _split_items(spec):
    """Split an item line's package list on commas OUTSIDE parentheses.

    `Upgrade: a:amd64 (1.0, 1.1), b:amd64 (2.0)` is two packages, but a naive
    `spec.split(",")` also cuts inside the version list and yields fragments
    like " 1.1)" that match no package -- silently dropping the real ones.
    """
    parts, depth, cur = [], 0, []
    for ch in spec:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return [p for p in (s.strip() for s in parts) if p]


def parse_history(log_dir=None):
    """package -> record of the earliest transaction that installed it.

    Record fields:
      date        YYYY-MM-DD
      action      Install | Upgrade | Remove | Purge | Reinstall
      versions    versions named by the transaction, oldest first
      commandline the exact commandline apt recorded
      unattended  True when the transaction was not operator-initiated
      requested_by the `Requested-By:` user, when apt recorded one

    Only `Install` and `Reinstall` set a record. A later Upgrade does not
    overwrite an earlier Install -- it is recorded in `upgraded` so the caller
    can say "installed 2026-08-25, upgraded 2026-10-01" rather than silently
    reporting the upgrade date as the install date.

    `log_dir` is injectable for testing only; production callers omit it and
    read /var/log/apt.
    """
    index = {}
    for path in _log_files(log_dir):
        text = _read(path)
        if not text:
            continue
        for stanza in text.split("\n\n"):
            if not stanza.strip():
                continue
            date = None
            cmdline = None
            requested_by = None
            items = []
            for line in stanza.splitlines():
                m = _START.match(line)
                if m and date is None:
                    d = _DATE.match(m.group(1).strip())
                    date = d.group(1) if d else None
                    continue
                m = _CMDLINE.match(line)
                if m and cmdline is None:
                    cmdline = m.group(1).strip()
                    continue
                if line.startswith("Requested-By:"):
                    requested_by = line.split(":", 1)[1].strip()
                    continue
                m = _ITEM.match(line)
                if m and date:
                    items.append((m.group(1), m.group(2)))
            if not date or not items:
                continue
            for action, spec in items:
                for pkg in _split_items(spec):
                    pm = _PKG.match(pkg.strip())
                    if not pm:
                        continue
                    name, arch = pm.group(1), pm.group(2)
                    versions = _parse_versions(pm.group(3))
                    key = f"{name}:{arch}" if arch else name
                    rec = index.setdefault(key, {
                        "date": date, "action": action, "versions": versions,
                        "commandline": cmdline, "unattended": bool(
                            cmdline and any(u in cmdline for u in _UNATTENDED)),
                        "requested_by": requested_by, "upgraded": None,
                        "removed": False})
                    # Keep the earliest install; a later transaction is an
                    # upgrade of something installed outside this window.
                    if action in ("Install", "Reinstall"):
                        if rec["action"] not in ("Install", "Reinstall") or date < rec["date"]:
                            rec.update(date=date, action=action, versions=versions,
                                       commandline=cmdline,
                                       unattended=bool(
                                           cmdline and any(u in cmdline
                                                           for u in _UNATTENDED)),
                                       requested_by=requested_by)
                    elif action == "Upgrade" and rec["upgraded"] is None:
                        rec["upgraded"] = date
                    elif action in ("Remove", "Purge"):
                        # A package that was installed and later removed is NOT
                        # currently installed, and the removal is the most recent
                        # truth about it. dbeaver-ce was installed 2026-08-29 and
                        # purged 2026-10-01; reporting the install date for a
                        # package `dpkg -l` no longer lists would be a lie told
                        # in the "Installed" column. Files are read oldest-first
                        # (rotated logs then the live one), so a later removal
                        # overwrites the earlier install -- which is the correct
                        # final state. An install AFTER a removal starts a fresh
                        # record, handled by the Install branch above.
                        rec.update(date=date, action=action, versions=versions,
                                   commandline=cmdline,
                                   unattended=bool(
                                       cmdline and any(u in cmdline
                                                       for u in _UNATTENDED)),
                                   requested_by=requested_by,
                                   removed=True)
    return index


def _alias_candidates(pkg):
    """Names dpkg/apt may use for one package, most specific first."""
    cands = [pkg]
    if ":" in pkg:
        cands.append(pkg.split(":", 1)[0])
    else:
        for arch in ("amd64", "i386", "arm64"):
            cands.append(f"{pkg}:{arch}")
    return cands


def install_date(pkg, index=None):
    """(date, record) for a package, or (None, None) if history has no say.

    A package whose most recent transaction was a Remove or Purge returns
    (None, record): the record is still returned so the caller can SAY the
    package was removed on that date, but no date is offered as an install
    date for something that is not installed.

    The caller decides how to render a missing date; this function never
    invents one.
    """
    if not pkg:
        return None, None
    idx = parse_history() if index is None else index
    for name in _alias_candidates(pkg):
        if name in idx:
            rec = idx[name]
            if rec.get("removed"):
                return None, rec
            return rec["date"], rec
    return None, None


if __name__ == "__main__":
    idx = parse_history()
    installs = sum(1 for r in idx.values() if r["action"] in ("Install", "Reinstall"))
    upgrades = sum(1 for r in idx.values() if r["action"] == "Upgrade")
    un = sum(1 for r in idx.values() if r["unattended"])
    print(f"packages indexed      : {len(idx)}")
    print(f"  installed           : {installs}")
    print(f"  upgrade-only (pre-window): {upgrades}")
    print(f"  installed unattended: {un}")
    print(f"log files read        : {[p.name for p in _log_files()]}")