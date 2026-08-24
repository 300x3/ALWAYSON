# ALWAYS ON — Secrets Management Runbook

Policy: Section 3.4 — file-based secrets, per-domain authorization, never in
Git/logs/HTML/pCloud/IPFS. This host's operator chose **KDE Wallet** as the
human-facing store; service accounts read dedicated secret files instead.

## Human/operator side: KDE Wallet (KWallet)

1. Open **KDE Wallet Manager** (`kwalletmanager5`, Plasma menu → Utilities → Security).
2. Use the default wallet `kdewallet` (unlocks with your Plasma login).
3. Create one folder per domain: `ao-sales`, `ao-payment`, `ao-field`,
   `ao-mapping`, `ao-ledger`, `ao-archive`, `ao-admin`.
4. Store entries as **name → password** pairs, e.g.:
   - `ao-archive/pcloud-archive-credential`
   - `ao-payment/webhook-signing-secret`
   - `ao-field/heltec-radio-key`
   - `ao-ledger/rpc-user`, `ao-ledger/rpc-password`

KWallet encrypts at rest with your login session and never touches disk unencrypted.

## Service side: per-user secret files (what containers actually read)

Services run as their own accounts (e.g. `alwayson-mapping`) and read secret
**files** with `0600 <account>:<account>` permissions from the account's home:

| Service account | File | Used by |
|---|---|---|
| `alwayson-mapping` | `/home/alwayson-mapping/secrets/webodm.env` | WebODM db/webapp/worker |

Quadlet units reference them with `EnvironmentFile=` or Podman `Secret=`.
These files are outside `/ALWAYSON` and excluded from Git by `.gitignore`.

## Flow when provisioning a new credential

1. Operator stores the value in KWallet under the domain folder.
2. Operator manually copies the value into the target service-account file:
   `install -m 0600 -o <svc> -g <svc> /dev/null <file>` then edit.
   (Copy via clipboard/KWrite — never via shell history or logs.)
3. Restart the affected user service:
   `sudo -u <svc> XDG_RUNTIME_DIR=/run/user/<uid> systemctl --user restart <unit>`
4. Verify with `check-secrets-exposure.sh` (scans tracked files).

## Rotation

Rotate = update KWallet entry + service file + restart unit + note in audit log.
Database passwords additionally require `ALTER ROLE` before/after file swap.
