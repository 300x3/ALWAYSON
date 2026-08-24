# ALWAYS ON — WebODM Access Runbook

The WebODM UI/API has **no published port** (Section 1.3: no public exposure).
The stack runs rootless inside the `alwayson-mapping` user session on the
internal-only `ao-mapping` network.

## Operator access from this desktop

The webapp listens on 8000 inside its container. Reach it via the mapping
user's Podman socket using a temporary socat forward, or run an interactive
browser container on `ao-mapping`:

```bash
# As alwayson-mapping (from a root shell):
runuser -u alwayson-mapping -- env HOME=/home/alwayson-mapping \
  XDG_RUNTIME_DIR=/run/user/997 \
  podman run --rm --network ao-mapping -p 127.0.0.1:8000:8000 \
  curlimages/curl sleep infinity   # or use a tiny TCP proxy image

# Then browse: http://localhost:8000   (loopback-only bind = not public)
```

Recommended one-liner check:

```bash
sudo -u alwayson-mapping env HOME=/home/alwayson-mapping \
  XDG_RUNTIME_DIR=/run/user/997 \
  podman exec webapp curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8000/
# expect 200/302 when healthy
```

## API-driven autonomous processing

Scripts authenticate to `http://webapp:8000/api/...` from containers on
`ao-mapping` (see scripts/mapping/). No credentials cross the network in
plaintext beyond the internal bridge; session tokens are obtained per job.

## Service control

```bash
MU=alwayson-mapping
sudo -u $MU env HOME=/home/$MU XDG_RUNTIME_DIR=/run/user/$(id -u $MU) \
  systemctl --user status|restart|stop ao-webodm-{db,broker,web,worker}.service ao-nodeodm.service
```

## First-boot notes

- The db volume persists at `/home/alwayson-mapping/webodm/dbdata`
- Media lives on the photogrammetry drive:
  `/media/scottw/500GBPHOTOGRAM/webodm/media`
- NodeODM auto-registration: add processing node `nodeodm:3000` once in the UI
  (`WO_DEFAULT_NODES=0` disables auto-add so registration is explicit)
