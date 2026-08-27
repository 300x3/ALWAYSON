# Container Visibility & GUI Access Runbook

## Purpose
Provide operator (scottw) GUI access to all ALWAYS ON rootless container
stacks while preserving the Section 1.3 strict per-service isolation model.

## Architecture
Rootless Podman is per-user. Production containers run under dedicated
service accounts (alwayson-mapping uid 997, alwayson-sales uid 993,
alwayson-ledger uid 994). Their Podman API sockets are bound to those
accounts and are not visible to scottw's GUI directly.

To expose them to the operator without weakening isolation, a root-owned
socat bridge forwards each service socket to a scottw-accessible loopback
socket in /run/ao-podman/ (0660, local-only, no network exposure):

  /run/user/<uid>/podman/podman.sock  --socat-->  /run/ao-podman/<domain>.sock

Service: ao-podman-bridge.service (boot-persistent)
Script:  /usr/local/sbin/ao-podman-bridge.sh

## Registered Podman connections (scottw)
~/.config/containers/podman-connections.json

| Name    | URI                          | Reports |
|---|---|---|
| mapping | unix:///run/ao-podman/mapping.sock | broker, db, webapp, worker, nodeodm (5 running, 8 images) |
| sales   | unix:///run/ao-podman/sales.sock   | sales-db (1 running) |
| ledger  | unix:///run/ao-podman/ledger.sock  | (no containers staged) |

The Default connection is `mapping`; switch with GUI dropdown or
`podman --connection <name> ps`.

## GUI: native Podman Desktop (non-sandboxed)
- Location: ~/Applications/podman-desktop/
- Menu entry: "Podman Desktop" (installed to ~/.local/share/applications)
- Important: the native build is NOT a Flatpak sandbox, so it reads scottw's
  host podman connections file directly and can reach the bridges.
- Containers/Images/Volumes/Secrets/Networks are shown per connection.

## CLI access per connection
  podman --connection mapping ps
  podman --connection sales ps
  podman --connection ledger ps

## Isolation preserved
- Bridge sockets are loopback-only (0660), owned by scottw.
- Service accounts still own their container runtime and secrets.
- No cross-domain broad networking is introduced; this is read/manage
  access by the operator into each domain.

## Rebuild after reboot
v2.1 bridge script (scripts/deploy/ao-podman-bridge.sh) runs a reconcile loop
with PID-file health checks: it waits for the service users' sockets, brings
bridges up as they appear, and repairs dead instances — no manual restart
needed after reboot.

If bridges are still missing after ~30s:
  systemctl restart ao-podman-bridge.service
  journalctl -u ao-podman-bridge.service -n 20   # expect per-domain bridge_up lines

### 2026-08-26 incident record
After this morning's reboot the original v1 script hit its boot race:
journal showed `mapping/sales/ledger: bridge_missing_src` x3, no socat
processes, /run/ao-podman/ empty. Same day:
- v2 retry loop authored, installed via pkexec; validation then exposed a
  bug in its own pgrep-quoted health check (never matched -> churn/spawn leak).
- v2.1 (PID-file health checks) authored, installed via pkexec, verified
  LIVE: PIDs stable across >=3 reconcile cycles, pidfiles in /run/ao-podman/,
  mapping+sales bridges verified end-to-end (`podman --url unix:///run/ao-podman/<name>.sock info`).
- OPEN at close of session: ledger.sock bridged but EOFs on every request —
  the alwayson-ledger user's podman backend is unhealthy. Diagnose with:
    pkexec /tmp/ledger-diag.sh        # or re-create from this repo's history
  (runs `podman info` as alwayson-ledger + pulls uid-994 journal).

