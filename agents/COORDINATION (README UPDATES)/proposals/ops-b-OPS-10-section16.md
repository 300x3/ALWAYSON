---
item: OPS-10
action: close
evidence: |
  $ find systemd -type f | sort
  systemd/backup/ao-restic-backup.service
  systemd/backup/ao-restic-backup.timer
  systemd/backup/ao-restic-prefetch.service
  systemd/backup/ao-restic-prefetch.timer
  systemd/backup/ao-restic-verify.service
  systemd/backup/ao-restic-verify.timer

  $ grep -l 'exit 3' scripts/restore/*.sh
  scripts/restore/restore-corda-test.sh
  scripts/restore/restore-mapping-artifact-test.sh
  scripts/restore/restore-sales-db-test.sh
  scripts/restore/restore-simulation-artifact-test.sh

  $ for f in scripts/restore/*.sh; do bash -n $f && echo "OK $f"; done
  OK scripts/restore/restore-corda-test.sh
  OK scripts/restore/restore-mapping-artifact-test.sh
  OK scripts/restore/restore-sales-db-test.sh
  OK scripts/restore/restore-simulation-artifact-test.sh
  OK scripts/restore/verify-hashes-and-receipts.sh
section: 16-scripts-and-operational-standards
---
§16.1.2 now names every backup and restore script, the unit that invokes it, and
the real state of the seven-step restore test. The item asked for two things; both
are answered, and one of them answers "no".

**Executors and units.** `scripts/backup/` holds nine scripts.
`restic-run.sh` ← `ao-restic-backup.service`, `verify-backup.sh` ←
`ao-restic-verify.service`, `fetch-restic-env.sh` ← `ao-restic-prefetch.service`.
`systemd/backup/` is the repository's only systemd tree and holds exactly six unit
files — three service/timer pairs. Backup and restore are also the last subsystem
still on plain units rather than Quadlet, which is worth a decision but is not
this item's scope.

The non-obvious part, and the reason `ls scripts/backup/` alone is misleading:
`fetch-restic-env.sh` lives in `operations/`, not `backup/`, yet both restic
timers depend on it to resolve wallet-backed credentials. A reader auditing only
the directory the section named would conclude the backup path has no credential
step at all.

**The restore test has an executor and one implementation, not five.** Of five
scripts in `scripts/restore/`, `verify-hashes-and-receipts.sh` (steps 3–5) is
implemented — it recomputes `sha256sum` over each manifest's
`local_storage_reference`, compares against `content_hash_sha256`, checks receipt
linkage, and exits 51 on mismatch. The other four exit 3 with `PENDING: <path>
requires completed backups plus isolated test-path approval`. They are honest
stubs, and `bash -n` passes on all five, so they will not fail confusingly.

**The cadence does not exist, and the item's request cannot be met without
approval.** There is no restore timer. `check-logs-journals.sh` asserts
`restore-test.log` freshness at 3650 days — a placeholder that can never fail,
not a cadence. Closing the four stubs and setting a real interval both need
**explicit operator approval** of an isolated restore test path; I have not
assumed either. §16.1.2 states this rather than implying the test runs.