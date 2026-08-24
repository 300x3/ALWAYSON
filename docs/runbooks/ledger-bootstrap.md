# ALWAYS ON — Corda 5.2.2 Ledger Bootstrap Runbook

State after scaffold (automated, see installation journal):
- Service account `alwayson-ledger` (linger enabled)
- Database `cordadb` / role `corda` on host PostgreSQL 18 (loopback only),
  credentials in `/home/alwayson-ledger/secrets/corda-db.env` (0600)
- Verified artifacts in `/home/alwayson-ledger/dist/`:
  `corda-combined-worker-5.2.2.0.jar`, `corda-cli-installer-5.2.2.0.zip`
- systemd user unit installed: `ao-ledger-core.service` (**not started**)

## Remaining manual steps (require operator key ceremonies)

1. **Install the CLI** (as any admin user):
   ```bash
   unzip ~/dist/corda-cli-installer-5.2.2.0.zip -d ~/corda-cli
   ~/corda-cli/bin/corda-cli.sh --version
   ```
2. **Generate TLS certificates & key stores** for the cluster (operator holds
   passphrases — store them in KWallet under `ao-ledger`):
   - `corda-cli.sh keys generate-csr` / cert chain per Corda 5 docs
3. **Create the worker configuration** at
   `/home/alwayson-ledger/config/combined-worker.conf`
   - DB section points at 127.0.0.1:5432/cordadb with values from the env file
   - crypto/TLS sections reference the generated stores
4. **Encrypt & install config**:
   ```bash
   corda-cli.sh config encrypt ...   # produces encrypted override
   sudo install -o alwayson-ledger -g alwayson-ledger -m 0600 <encrypted> \
     /home/alwayson-ledger/config/
   ```
5. **Start**:
   ```bash
   sudo -u alwayson-ledger env HOME=/home/alwayson-ledger \
     XDG_RUNTIME_DIR=/run/user/$(id -u alwayson-ledger) \
     systemctl --user enable --now ao-ledger-core.service
   ```
6. **Verify**: worker logs show successful DB migration + workers lifecycle
   (`journalctl --user -u ao-ledger-core.service`), then run
   `/ALWAYSON/scripts/validation/check-ledger-ingest.sh`.

## Isolation notes

- Ledger-core runs as a native systemd service (documented deviation: OSS
  Corda 5 ships no official container image; native process can reach the
  loopback PostgreSQL without widening any listener).
- The future ledger-ingest gateway (the ONLY component other domains talk to)
  will be a separate Podman service on `ao-ingest` path with mTLS.
