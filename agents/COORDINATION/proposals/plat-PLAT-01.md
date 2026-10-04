---
item: PLAT-01
action: close
evidence: |
  $ podman info --format '{{.Host.Security.Rootless}}'
  true
  $ podman info --format '{{.Store.GraphRoot}} | {{.Store.RunRoot}}'
  /home/scottw/.local/share/containers/storage | /run/user/1000/containers

  $ systemctl --user list-unit-files 'ao-webodm*'
  UNIT FILE                    STATE      PRESET
  ao-webodm-broker.service     generated  -
  ao-webodm-db.service         generated  -
  ao-webodm-web.service        generated  -
  ao-webodm-worker.service     generated  -
  $ systemctl list-unit-files 'ao-webodm*' | wc -l
  0

  $ grep -rn '^User=\|^Group=' quadlet/
  (no output)

  $ podman system connection list
  Name        URI         Identity    Default     ReadWrite
  (header only)
  $ cat ~/.config/containers/podman-connections.json
  {"Connection":{},"Farm":{}}

  $ ls /run/ao-podman
  ls: cannot access '/run/ao-podman/': No such file or directory

  $ systemctl is-enabled ao-podman-bridge.service ; systemctl --user is-enabled ao-podman-bridge.service
  disabled          # rc=1
  not-found         # rc=4
  $ systemctl cat ao-podman-bridge.service | sed -n '1,3p'
  # /etc/systemd/system/ao-podman-bridge.service
  [Service]
  ExecStart=/usr/local/sbin/ao-podman-bridge.sh

  -- the rejected per-service scaffolding, measured --
  $ getent passwd | grep -E 'ao-|alwayson'
  ao-sales:x:993:973:ALWAYS ON sales domain service:/home/alwayson-sales:/usr/sbin/nologin
  ao-ledger:x:994:974:ALWAYS ON ledger core service:/home/alwayson-ledger:/usr/sbin/nologin
  ao-mapping:x:997:975:ALWAYS ON mapping domain service:/home/alwayson-mapping:/usr/sbin/nologin
  $ loginctl show-user ao-mapping -p Linger
  Failed to get user: User ID 997 is not logged in or lingering
  $ ps -eo user,pid,comm --no-headers | awk '$1 ~ /ao-|alwayson/'
  (no rows)
  $ ls -l /var/lib/containers/storage/db.sql
  -rw-r--r-- 1 root root 114688 Sep 30 20:26   # exists; contents NOT readable (see OPEN)

  -- the workload containers are in the operator store --
  $ podman ps --format '{{.Names}}' | grep webodm
  ao-webodm-webapp
  ao-webodm-worker
  ao-webodm-db
  ao-webodm-broker
section: 13-podman-runtime-and-quadlet-policy
---
§13.2 now opens with an explicit designation — **rootless, single-store, under `scottw`
(uid 1000)** — followed by a seven-row table of the measurements above, so the designation is
re-derivable rather than asserted. The old text said only that every container "runs rootless
under the operator account" without naming the account or the store, and its rules forbade the
per-service model without saying whether it was actually present.

New **§13.2.1** records the deviation that kept this item open: the three per-service accounts
(`ao-sales` 993, `ao-ledger` 994, `ao-mapping` 997) and
`/etc/systemd/system/ao-podman-bridge.service` still exist on the host. They hold no store, no
socket and no process, so they do not make the runtime mixed. **This corrects §19.2**, whose
"Verified; mixed-store deviation documented" row described a deviation that does not exist.

**Two things I got wrong, and why.**

1. **I could not enumerate the rootful store, so I did not claim it is empty.**
   `/var/lib/containers/storage` exists and its `db.sql` was written 2026-09-30, so something
   has used it. `sudo` on this host requires interactive authentication, so
   `sudo ls /var/lib/containers/storage/overlay-images/` returned `Permission denied`. §13.2
   therefore says the system store is *"unused by any workload"*, **not** *"empty"* — different
   claims, and only the first is proven. **OPEN for the operator:** one `sudo` command settles
   it. I did not request escalation; a non-interactive agent cannot answer it, and guessing
   would have been worse than saying so.
2. **§13.2 and §19.2 contradicted each other, and I initially treated §13.2 as the correct
   side.** `OPS-14` asserts a mixed-store deviation is recorded in §19.2; I searched §19.2 for
   that record and found only a one-line summary with no measurement behind it. I got this
   wrong by assuming the more detailed document was authoritative. The measurement settled it:
   `loginctl` and `ps` show nothing runs under those accounts, so there is no mixed store to
   record.

**Not done, deliberately.** The three accounts and the disabled unit are left in place —
deleting a user or a unit file needs explicit operator approval (README §4.1 rule 3). Reported,
not executed.

**Cross-group.** `OPS-14` asks for this same reconciliation and can close on §13.2.1, but
§19.1 is not mine to edit — the compiler merges that row.