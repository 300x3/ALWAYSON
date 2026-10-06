# 2026-10-04 — SEC-01 wallet completion, OPS-13/24/31 backup work, PLAT-02 matrix

Operator instruction: the seven dashboard questions were redundant; proceed on
the answers already given. No item was treated as a blocker.

## SEC-01 — all credentials now live only in KDE Wallet

Audit method: enumerated wallet FOLDERS (ao-admin, ao-mapping, ao-sales,
ao-mastodon, ao-fabrication, ao-payment, ao-archive) rather than guessing entry
names. The first pass guessed names and produced six false "ABSENT" results;
the real folder routing is in scripts/operations/fetch-kwallet-secret.sh
(wallet_folder_for). Re-audited against the true names.

Found genuinely absent: 4 x ao-payment, 2 x ao-archive (pCloud), 1 x
ao-admin/metabase-admin-password.

Error made and corrected: the first write used a RANDOM 32-char value for
payment-db-password. That would have broken the live DSN on the next
regeneration of ~/.local/share/ao-secrets/payment.env, because the file is
rebuilt by fetch-kwallet-secret.sh from the wallet. Corrected by writing the
LIVE value already in payment.env, then verifying a full regeneration is
identical apart from three previously-absent webhook variables.

Verified: 19/19 keys read back non-empty via wallet-read-secret.py. Lengths
and entry names only; no value was printed or journalled.

NOTE: three newly generated webhook placeholder values appeared in the agent
transcript during a diff. They are random defaults for entries that did not
previously exist, and the operator is expected to replace the pCloud pair.

## OPS-13 — TimeoutStopSec=20s added to ao-restic-backup.service

## OPS-31 — relocation prepared, NOT executed

/var/backups/alwayson-restic is root:root 0700 and this account has no
passwordless sudo, so the move cannot be performed here.
scripts/ops/move-restic-repo.sh written for the operator to run under pkexec.
It refuses to copy into an unmounted mountpoint (the removable drive's
directory exists even when the drive is absent, so a naive copy would land on
the root filesystem), refuses to overwrite an existing repo, uses restic copy
rather than cp, verifies with restic check before repointing config, and
LEAVES THE SOURCE IN PLACE.

## OPS-24 / OPS-31 — retention, the actual inflation fix

Measurement: `forget`/`prune` appeared nowhere in scripts/ except the pCloud
setup. The local repository had NO retention and grew without bound.
restic 0.18.1 has no --max-repo-size, so the 40 GB budget cannot be a flag.
scripts/backup/restic-retention.sh added: keep 24 hourly / 7 daily / 4 weekly
/ 6 monthly grouped by host,paths, plus a measured budget check that exits
non-zero on breach rather than silently succeeding. Wired as a separate
05:10 timer so a prune failure cannot fail the 03:30 backup.
Tested end to end on a throwaway repo, including idempotency.

## PLAT-02 — version matrix

config/platform/version-matrix.yaml already existed from the prior Backup &
Install session and is digest-pinned as the operator described. The log he
called rigorous is logs/installation/agent-install.log.1 (3,710 lines); the
current agent-install.log is 0 bytes after rotation.

Bug found in scripts/validation/capture-version-matrix.sh: `podman info
--format '{{.Host.Version}}'` no longer resolves on podman 5.7 (field moved to
.Version.Version), and the `|| echo unknown` fallback wrote the literal string
"podman unknown" into the matrix, degrading a good value. Fixed, and the
fallback now fails loudly instead of inventing a value.

## OPS-24 — restore drill

Bug found: scripts/restore/restore-restic-drill.sh validated --repo and echoed
it but never passed it to restic; every call was bare `restic`, so the drill
only worked if the caller had exported RESTIC_REPOSITORY. With --repo alone it
failed with a misleading "could not resolve a snapshot". Fixed by exporting
the validated path. Drill then passed: 88 files restored, 56 hashed, 56
identical, result=PASS, exit 0.

## Verified commands
- wallet read-back: 19/19 present, 0 missing
- check-secrets-exposure.sh: OK, no secret-shaped content in tracked files
- systemd-analyze verify on both new units: parse clean
- restic retention on throwaway repo: passes, idempotent
