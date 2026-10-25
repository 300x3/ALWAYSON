#!/usr/bin/env python3
"""ALWAYS ON - collect backup health metrics for Prometheus (OPS-39).

Writes three gauges to the Prometheus textfile collector directory so that
AoBackupStale, AoRestoreTestStale and AoRepositoryVerifyStale (alwayson-alerts.yml)
have real metrics to evaluate instead of `no data`:

  ao_backup_last_success_timestamp_seconds   last restic backup with result=OK
  ao_restore_test_last_pass_timestamp_seconds last restore test with result=OK
  ao_backup_last_verify_timestamp_seconds    last verify-backup.sh audit entry

Reads the README 16.3 journals under AO_LOG_DIR (never writes to them), converts
ISO-8601 timestamps to Unix epoch seconds, and writes atomic Prometheus textfile
output. Missing journals yield metric 0 (never ran) rather than absent series.
"""

from __future__ import annotations

import os
import pathlib
import re
import sys
import time

AO_ROOT = pathlib.Path(os.environ.get("AO_ROOT", "/ALWAYSON"))
AO_LOG_DIR = pathlib.Path(os.environ.get("AO_LOG_DIR", AO_ROOT / "logs"))
OUT_DIR = pathlib.Path(
    os.environ.get("AO_PROM_TEXTFILE_DIR", AO_ROOT / "data" / "prometheus-textfile")
)

BACKUP_LOG = AO_LOG_DIR / "backup.log"
RESTORE_TEST_LOG = AO_LOG_DIR / "restore-test.log"
AUDIT_LOG = AO_LOG_DIR / "audit.log"

ISO_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})")


def iso_to_epoch(iso: str) -> int:
    """Convert an ISO-8601 timestamp to Unix epoch seconds."""
    # Python 3.7+: fromisoformat handles the +00:00 offset.
    return int(time.mktime(time.strptime(iso, "%Y-%m-%dT%H:%M:%S%z")))


def last_matching_timestamp(log_path: pathlib.Path, predicate) -> int | None:
    """Return the epoch of the most recent line in log_path matching predicate.

    Journals are append-only; the newest matching entry is the last line that
    satisfies predicate. Returns None if the file is absent or no line matches.
    """
    if not log_path.is_file():
        return None
    best: int | None = None
    try:
        for line in log_path.read_text(errors="replace").splitlines():
            m = ISO_RE.match(line)
            if not m:
                continue
            if predicate(line):
                ts = iso_to_epoch(m.group(1))
                if best is None or ts > best:
                    best = ts
    except OSError:
        return None
    return best


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    backup_ok = last_matching_timestamp(
        BACKUP_LOG, lambda line: " result=OK " in line
    )
    restore_ok = last_matching_timestamp(
        RESTORE_TEST_LOG, lambda line: " result=OK " in line
    )
    verify_ok = last_matching_timestamp(
        AUDIT_LOG, lambda line: "script=verify-backup.sh" in line
    )

    now = int(time.time())

    # Gauge semantics: 0 means "never recorded", which for a stale alert means
    # the condition is permanently true (correctly stale).
    lines: list[str] = []
    lines.append(
        "# HELP ao_backup_last_success_timestamp_seconds "
        "Unix timestamp of the last successful restic backup (0 = never)."
    )
    lines.append("# TYPE ao_backup_last_success_timestamp_seconds gauge")
    lines.append(
        f"ao_backup_last_success_timestamp_seconds {backup_ok if backup_ok is not None else 0}"
    )
    lines.append("")
    lines.append(
        "# HELP ao_restore_test_last_pass_timestamp_seconds "
        "Unix timestamp of the last passing restore test (0 = never)."
    )
    lines.append("# TYPE ao_restore_test_last_pass_timestamp_seconds gauge")
    lines.append(
        f"ao_restore_test_last_pass_timestamp_seconds {restore_ok if restore_ok is not None else 0}"
    )
    lines.append("")
    lines.append(
        "# HELP ao_backup_last_verify_timestamp_seconds "
        "Unix timestamp of the last successful repository integrity check (0 = never)."
    )
    lines.append("# TYPE ao_backup_last_verify_timestamp_seconds gauge")
    lines.append(
        f"ao_backup_last_verify_timestamp_seconds {verify_ok if verify_ok is not None else 0}"
    )
    lines.append("")

    out_path = OUT_DIR / "ao-backup-health.prom"
    tmp_path = out_path.with_suffix(".prom.tmp")
    tmp_path.write_text("\n".join(lines))
    tmp_path.replace(out_path)

    print(f"[ao-backup-health] backup={backup_ok} restore={restore_ok} verify={verify_ok}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
