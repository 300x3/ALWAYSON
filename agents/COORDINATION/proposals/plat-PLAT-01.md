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
  # NOTE 2026-10-04: the 'wc -l' form below was WRONG and is corrected.
  # It printed 3, not 0. Use the grep form -- it discriminates.
  $ systemctl list-unit-files 'ao-webodm*'
  UNIT FILE                STATE     PRESET

  0 unit files listed.
  rc=1
  $ systemctl list-unit-files 'ao-webodm*' | grep -c '^ao-'
  0                                  # <- the valid measurement
  # control: an impossible pattern prints the SAME 3 lines, which is how the
  # error was found. 'grep -c .' also returns 2 (blank line dropped), not 0.
  $ systemctl list-unit-files 'ao-nonexistentxyz*' | wc -l
  3
  # the same grep form in the scope where units DO exist:
  $ systemctl --user list-unit-files 'ao-webodm*' | grep -c '^ao-'
  4

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

## Re-verification 2026-10-04, and a correction to this file's own evidence

Every measurement in this proposal was re-run against the live host on 2026-10-04 and
reproduced unchanged: `Rootless` `true`, `GraphRoot` `/home/scottw/.local/share/containers/
storage`, the four `ao-webodm-*` units still `generated` in the user scope, no `User=`/`Group=`
in `quadlet/`, empty `podman-connections.json`, no `/run/ao-podman`, the bridge unit still
`disabled`/`not-found`, the three per-service accounts still present with no process and no
linger, `/var/lib/containers/storage/db.sql` still `Sep 30 20:26`, and the four WebODM
containers still running from the operator store.

**One citation in this file was wrong and is corrected above.** The system-level unit count
was cited as `systemctl list-unit-files 'ao-webodm*' | wc -l` → `0`. That command returns
**`3`**, not `0`, because systemctl prints a header, a blank line and a `0 unit files
listed.` summary regardless of matches — a control with an impossible pattern returns the
same `3`. **The conclusion (no system-level units) is correct and was re-measured with a
form that works** (`| grep -c '^ao-'` → `0`, versus `4` in the user scope). What was wrong
was the evidence, not the finding. Recorded because a citation an agent cannot reproduce is
worse than no citation: it invites the next reader to trust a number that was never measured.

**Fifth error overall, and the reason it survived two commits.** I wrote the `wc -l` form on
2026-10-03 and did not re-run it when I later re-verified the *host* state on 2026-10-04 — I
re-ran the substantive checks and assumed the recorded command still produced the recorded
output. Re-verifying a claim is not the same as re-running the exact command that backs it,
and for a method that is wrong *in a way that always looks plausible* only the exact command
catches it. The `grep -c '^ao-'` form with a control pattern is now in §2.5 as a trap.

## Cross-group

`OPS-14` asks for this same reconciliation and can close on §13.2.1, but §19.1 is not
mine to edit — the compiler merges that row.
## Third pass 2026-10-04 — the rootful store was enumerable all along

Re-verification reproduced every finding above, and then **overturned one of my own claims**.
§13.2.1 said the rootful store's "contents are `drwx------ root root`" and that enumerating it
"needs one `sudo` command and operator approval". **Both wrong, and I had not tested either.**

```
$ stat -c '%A %U:%G %n' /var/lib/containers/storage
drwxr-xr-x root:root /var/lib/containers/storage
$ stat -c '%A %n' /var/lib/containers/storage/overlay-images/
drwx------ /var/lib/containers/storage/overlay-images/     # the 0700 is the CHILD, not the root
$ ls -la /var/lib/containers/storage/ | sed -n '4p'
-rw-r--r-- 1 root root 114688 Sep 30 20:26 db.sql            # world-readable

$ python3 -c "import sqlite3; c=sqlite3.connect('file:/var/lib/containers/storage/db.sql?mode=ro',uri=True); print({t: c.execute('select count(*) from '+t).fetchone()[0] for t in ('ContainerConfig','ContainerState','ContainerExitCode','VolumeConfig','PodConfig','ContainerDependency')})"
{'ContainerConfig': 0, 'ContainerState': 0, 'ContainerExitCode': 0, 'VolumeConfig': 0, 'PodConfig': 0, 'ContainerDependency': 0}
```

**The rootful store holds no containers, no pods, no volumes and no dependency records.** The
store root is `drwxr-xr-x` and `db.sql` is `0644`, so this needed **no `sudo` and no operator
approval** — the thing I said needed approval. This upgrades the single-store designation from
"unused by any workload" to "contains no workload records at all", and it makes `PLAT-01`'s
"mixed-store deviation closed or confirmed" answer unambiguous: **there is no mixed store and
nothing left in the rootful store that a workload could have used.**

`ContainerConfig` has columns `ID, Name, PodID, JSON`, and that JSON would carry `Env` — so I
selected counts only and **never printed a row value**. `sqlite3(3)` is not installed; Python's
`sqlite3` module needs no package.

**Still open, narrower:** `overlay-images/` is `0700` and `ls` on it returns `Permission denied`
as uid 1000, so **residual image blobs are still unverified**. Last write `2026-09-30` is
consistent with images predating the rootless migration but does not prove it; the rootless store
has 102 image records and is fully enumerable. One `sudo` command would settle it — recommended
action, **no automatic action taken, no deletion proposed.**

### What I got wrong, sixth time: I asserted a mode I never measured

I wrote `drwx------ root root` for the store root and built an OPEN item on it. I had observed
`Permission denied` from `ls overlay-images/` and inferred the *store's* mode from the
*child's*. `ls` failing tells you about the path you asked for, not its parent. I generalised a
child's mode to its parent and then reported the parent as unreadable.

Worse, I converted that error into a **needless approval gate** — "enumerating it needs one
`sudo` command and operator approval". The correct claim was free and instant. An unverifiable
OPEN item is worse than an absent one, because the next agent inherits the constraint and either
believes the store is opaque or asks the operator for permission to do nothing.

The class of bug is **inferring a fact about a parent from a child's attributes**, and it is the
same class as the `wc -l` mistake above it: the conclusion was plausible, the supporting command
had never been run. Three of my six errors here are of this shape — a plausible story attached
to a measurement I did not make. Rule 5 exists precisely because I keep violating it.

I also reproduced it *inside this correction*: my first draft cited the enumeration as a
two-line `python3 -c` with an indented continuation, which raises `IndentationError` and
produces no output. I caught it by replaying every citation before committing and rewrote it as
a single verified line.
