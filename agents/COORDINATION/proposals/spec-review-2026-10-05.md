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
$ podman ps -q | wc -l
  25
  $ podman inspect ao-grafana ao-sim-fabrication-foxglove \
      vigorous_shannon dreamy_rosalind relaxed_tharp confident_khayyam \
      keen_bhabha ao-sqli3 --format '{{.Name}} {{.ImageName}}'
  ao-grafana docker.io/grafana/grafana-oss@sha256:b739cda4b61ba3b90707578b643a22cd851fecf4498e6c6ec2d8f9d622a5d0b2
  ao-sim-fabrication-foxglove localhost/foxglove-bridge@sha256:9acc6d4df749ea10f3e97b4b6676a14d864dcb06781ffe7ad551736af0052c87
  vigorous_shannon localhost/foxglove-bridge:latest
  dreamy_rosalind localhost/foxglove-bridge:latest
  relaxed_tharp docker.io/grafana/grafana:11.6.0
  confident_khayyam docker.io/grafana/grafana:11.6.0
  keen_bhabha docker.io/grafana/grafana-oss:11.6.0
  ao-sqli3 docker.io/grafana/grafana-oss:11.6.0

  $ podman inspect ao-grafana ao-metabase --format '{{.Name}} {{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}'
  ao-grafana  ao-admin ao-reporting-egress
  ao-metabase ao-admin ao-reporting-egress
section: 06-component-boundaries-gui-reporting-tools-and-operator-access
---

# Review pass, 2026-10-05 — corrected a completeness claim I made in the same section

**Supersedes:** the earlier revision of this proposal. Same path, same findings 1 and 2 below,
plus a self-correction in finding 3 that changes an evidence block in §6.

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

## 3. My own §6 enumeration was 11 of 25 containers, described as complete

Found on re-measurement, same day, and it is the most important item in this document because
it is a defect in my own committed evidence rather than in someone else's.

Commit `9b76a22` added a correction block to §6.A.3.2 stating that the ownership conclusion
"rests on a key that returns a value, and on the whole-container enumeration rather than on a
hand-picked subset." The block showed **eleven** containers. The host runs **twenty-five**.
The other fourteen were simply absent from the transcription.

The conclusion survived — 6 unmanaged, 19 managed — and the six are the same six. But the
completeness claim was false when written, and it was the specific claim a reviewer would most
reasonably have relied on, since the whole point of that paragraph was to fix an earlier
truncated enumeration.

**Why the omission was dangerous rather than merely sloppy.** The fourteen missing containers
included `ao-ingress-payment`, `ao-sales-db`, `ao-webodm-db`, `mastodon-db` and
`ao-fabrication-db` — the containers holding authoritative payment, sales, mapping, social and
fabrication data. If any one of those had been unowned, the finding would have been far more
serious than "six duplicate GUIs". A truncated enumeration structurally cannot tell "six
leftovers" apart from "six leftovers plus an unowned database", because it never looks.

**Root cause, named as a rule.** The loop *was* fleet-wide — it iterated `podman ps` output. I
then pasted a filtered subset of its output and attached the word "complete" to the paste. So
the failure was not in the command; it was in the transcription between running a complete
command and recording it. Pasted evidence must be raw, and the denominator must appear next to
it (`podman ps -q | wc -l`) so the ratio is visible rather than asserted.

This is the **third** instance of the same class in this one subsection, after the wrong label
key and the mount-`RW` misread. Naming the pattern: a comment, a name, or a plausible
narrative asserting a property nobody measured — and the variant where I am the one writing the
assertion.

**Also fixed while there:** the file carried **two subsections numbered `6.A.3.2`**. The later
one is now `6.A.3.3`; no cross-reference pointed at it, so nothing else moves. Duplicate
numbering in a compiled document silently breaks anchors and makes "see 6.A.3.2" ambiguous,
which is how two corrections end up contradicting each other in a reader's head.

## New measurement, not previously recorded: the unowned set is also the unpinned set

Worth reporting because it changes the severity of the cleanup. Every **managed** container
inspected is digest-pinned (`ao-grafana` → `grafana-oss@sha256:b739cda4…`,
`ao-sim-fabrication-foxglove` → `foxglove-bridge@sha256:9acc6d4d…`). **All six unowned
containers are unpinned** — four on `grafana:11.6.0` / `grafana-oss:11.6.0` and two on
`foxglove-bridge:latest`. So these are the only containers on the host whose image content can
change underneath them without a service restart. Still OPS/SIM hygiene, not exposure, and
still not mine to remediate.

## What I got wrong, and why

**Three things.**

1. I asserted mechanism from names and comments instead of measuring them. The bridge was
   described as the container-to-PostgreSQL path on the strength of being called a "reporting
   bridge" on "ao-admin"; I never ran `ss -ltnp` to see what it actually bound. The `8731`
   listener was invisible because I enumerated *containers* and assumed that inventory was
   complete — the listener namespace is not the container namespace.
2. I transcribed a subset of a fleet-wide command and called it the whole fleet (finding 3).
   The command was right; the record was not.
3. The pre-existing `PODMAN_SYSTEMD_UNIT` trap was written as though the label-key question
   were now settled. It was settled for *ownership* and I never re-checked it against *image
   pinning*, which is a different question with a different key — and the answer inverted
   (all managed pinned, all unowned unpinned).

## Verified-unchanged (re-measured, all still accurate)

§1 host OS/Plasma/Kubuntu-package claims; §3 fourteen-network inventory and all `internal`
flags and subnets; the eleven-`Internal=true`/three-egress split; the five granted reporting
views on `salesdb` with base-table denial; `sales_migration_role` as sole superuser;
`metabase_app` absent from `salesdb`; per-domain PostgreSQL versions (18 host, 17 sales/
mastodon/fabrication, 9.5 WebODM); PostGIS 2.3.2 in `webodm_dev` only; Redis 8.0.5 host /
7.4.11 container; the four unowned Grafana containers and two unowned Foxglove duplicates;
`podman port` empty for all four; the read-only SQLite snapshot mount.