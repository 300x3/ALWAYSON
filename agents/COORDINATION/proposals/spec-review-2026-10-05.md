---
# NOT a real work item. This is a review report, not a proposed §19.1 row.
# Both findings belong to SEC/NET. The compiler or the owning group should assign
# the real ID(s); I deliberately did NOT take a number in the SEC namespace,
# because SEC-04 may already be in use by that session and I cannot see their
# uncommitted work. Do not merge this as a numbered row without the SEC session
# picking the ID.
item: none
action: report
evidence: |
  $ ss -ltnp | grep -vE '127\.0\.0\.1|\[::1\]|Local'
  LISTEN 0 5    10.42.0.1:5432     0.0.0.0:*  users:(("socat",pid=5124,fd=5))
  LISTEN 0 5    0.0.0.0:8731       0.0.0.0:*  users:(("python3",pid=1010842,fd=3))
  LISTEN 0 1    0.0.0.0:4242       0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=46))

  $ ps -o pid,lstart,etime,args -p 1010842
      PID   STARTED    ELAPSED COMMAND
  1010842  Thu Oct  1 20:09:45 2026  3-11:48:07 python3 -m http.server 8731
  $ ls -l /proc/1010842/cwd
  … -> /media/scottw/1TBSAMSUNGDATA/PCLOUD-PUBLIC/***CURRENT***

  $ curl -sI http://192.168.87.135:8731/ | head -2
  HTTP/1.0 200 OK
  Server: SimpleHTTP/0.6 Python/3.14.4
section: 06-component-boundaries-gui-reporting-tools-and-operator-access
---

# Two measured findings from the SPEC review pass, 2026-10-05

No items were assigned to this session, so this is a review-only pass. Both findings are
recorded in §3 and §6 as measurements. Both are **reported, not remediated** — each touches a
stop condition (public port / firewall policy / network configuration). Neither is mine to
close.

## 1. `python3 -m http.server 8731` on `0.0.0.0`, serving the pCloud Public Folder

`python3 -m http.server` binds all interfaces by default and has no authentication. The
working directory is the pCloud Public Folder — the path §4.2 classifies as *Public* and that
§4.1 rule 5 governs. It answers HTTP 200 on the Wi-Fi address `192.168.87.135`.

Running since 2026-10-01, so it is very likely a deliberate operator action and not a stray
process. It is a host process, so it appears in **no** container inventory and in no row of
§5.1 group D.

**Not stopped.** Stopping it is destructive to whatever the operator is serving, and
re-binding is a public-port decision needing explicit approval (§4.1 rules 6, 13). If the
intent was a local preview the fix is `--bind 127.0.0.1`; if genuine LAN sharing, it should
become a Quadlet with a declared listener policy. **SEC/NET own the decision.**

## 2. `ao-postgres-reporting-bridge` binds the equipment LAN, not a Podman gateway

The bridge is a host `socat` binding `10.42.0.1`, which is the host's own **equipment LAN**
address. The ao-admin gateway is `10.89.9.1`. Both the script's comment and the systemd unit
description assert the ao-admin gateway:

```
# ALWAYS ON - expose the host PostgreSQL loopback listener only on the internal
# ao-admin Podman gateway. PostgreSQL itself remains bound to localhost.
GATEWAY=10.42.0.1
```

**The comment is wrong, not the address.** Consequences, all measured and recorded in §3.3.0.1:

- PostgreSQL is genuinely loopback-only (`listen_addresses = 'localhost'`), but the bridge
  republishes it on the wired equipment LAN, so the cluster is reachable by anything that can
  route to `10.42.0.1`. The Wi-Fi address refuses, because `socat` binds `10.42.0.1`
  explicitly rather than `0.0.0.0`.
- `ao-admin` membership is **not** what makes it reachable. A container on `ao-admin` alone
  gets `Network is unreachable`. The reporting containers reach it via `ao-reporting-egress`
  (`Internal=false`). So Metabase's database access depends on the egress network, and
  removing `ao-reporting-egress` would break it.
- The unit description's stated reason for the service ("ao-admin gateway address only exists
  once those containers' networks are created") describes a dependency that does not exist.

**SEC/NET own this too** — it is a network-boundary question and re-binding is a stop
condition.

## What I got wrong, and why

Both findings share one root cause worth naming for the next reviewer: **I asserted mechanism
from names and comments instead of measuring them.** The bridge was described as the
container-to-PostgreSQL path on the strength of being called a "reporting bridge" on "ao-admin";
I never ran `ss -ltnp` to see what it actually bound. The `8731` listener was invisible because
I enumerated *containers* (`podman ps`) and assumed that inventory was complete. The §6 trap I
had already written about label keys not applying to a hand-picked subset applies here too —
completeness of an inventory is only established by enumerating the whole namespace, and the
listener namespace is not the container namespace.

A third, smaller lesson: the existing §6 correction about mount `RW` flags and the existing
`PODMAN_SYSTEMD_UNIT` trap were both instances of *a comment or a plausible story asserting a
property nobody measured*. This pass found the same class twice more, in files I did not write.

## Verified-unchanged (re-measured, all still accurate)

§1 host OS/Plasma/Kubuntu-package claims; §3 fourteen-network inventory and all `internal`
flags and subnets; the eleven-`Internal=true`/three-egress split; the five granted reporting
views on `salesdb` with base-table denial; `sales_migration_role` as sole superuser;
`metabase_app` absent from `salesdb`; per-domain PostgreSQL versions (18 host, 17 sales/
mastodon/fabrication, 9.5 WebODM); PostGIS 2.3.2 in `webodm_dev` only; Redis 8.0.5 host /
7.4.11 container; the four unowned Grafana containers and two unowned Foxglove duplicates;
`podman port` empty for all four; the read-only SQLite snapshot mount.