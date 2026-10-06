---
item: FIELD-08
action: close
evidence: |
  # (3) separation from ao-sim-fabrication: disjoint networks, disjoint mounts, no sim data
  $ podman network inspect ao-sim-fabrication --format '{{range .Containers}}{{.Name}} {{end}}'
  ao-sim-fabrication-foxglove ao-sim-fabrication-gz
  $ podman exec ao-fabrication-db psql -U fabrication_role -d a_fab -c '\dt'
   public | machine_production | table | fabrication_role
  $ podman exec ao-sim-fabrication-gz sh -c 'find / -maxdepth 3 -name "*machine_production*"'
  (no output — simulation holds no production data)
  $ podman inspect ao-sim-fabrication-gz --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'
  /ALWAYSON/data/sim-fabrication/fuel -> /gzfuel
  /ALWAYSON/data/sim-fabrication/plugins -> /gzplugins
  /ALWAYSON/data/sim-fabrication/results -> /results
  /ALWAYSON/GAZEBO -> /ALWAYSON/GAZEBO
  /ALWAYSON/data/sim-fabrication/gzhome -> /gzhome
  $ podman inspect ao-fabrication-db --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'
  /home/scottw/webodm/fabrication-dbdata -> /var/lib/postgresql/data

  # caveat: ingestion is CURRENTLY failing because the machine is powered off
  $ journalctl --user -u ao-fabrication-collect.service -n 4 --no-pager
  Oct 04 09:17:31 ... Starting ao-fabrication-collect.service...
  Oct 04 09:17:34 ... skipped printer-01: offline (<urlopen error [Errno 113] No route to host>)
  Oct 04 09:17:34 ... pass complete: 0 ok, 0 failed, 1 offline
  $ ping -c1 -W2 10.42.0.96
  1 packets transmitted, 0 received, 100% packet loss
  $ systemctl --user is-enabled ao-fabrication-collect.timer; is-active -> enabled / active
section: 03-high-level-architecture
---
**FIELD-08 closes on all four criteria, each measured.** The owning section is
`03-high-level-architecture` (§3.3.0), which I do not own — so I changed **nothing in my
own two section files** for this item. This proposal carries the evidence instead.

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | Domain on `10.89.12.0/24`, `Internal=true` | **met** | subnet + gateway + `internal: true`, `ao-fabrication-db` at `10.89.12.3/24` |
| 2 | Per-machine production data from ≥1 real machine into `a_fab` | **met** | 17 rows, all `printer-01`, a real Klipper machine at `10.42.0.96` |
| 3 | Separation from `ao-sim-fabrication` demonstrated | **met** | disjoint container sets, disjoint mounts, no `machine_production` in any sim container |
| 4 | `a_fab` registered in `network-cidrs.yaml` | **met** | `network-cidrs.yaml:12` |

Criterion 2 is the load-bearing one and it is satisfied with **actual rows**, not merely a
wired-up path. Criterion 3 is *demonstrated* three ways rather than asserted.

**Caveat the compiler must carry, not bury.** The data is **stale** — newest row is
2026-10-01 00:35 UTC and it is 2026-10-04 — and the collector is failing every pass because
`printer-01` is powered off. The item closes because the criterion is *"data pulled from at
least one individual machine"*, and 17 rows prove the pipeline works end to end; it does
**not** close because ingestion is healthy. The collector infrastructure itself is provably
alive: the timer is `enabled`/`active`, fires every ~5 minutes, and correctly isolates a
per-machine outage (`0 ok, 0 failed, 1 offline`) rather than failing the unit. **Please do
not render FIELD-08 as "ingestion currently working".**

**What I got wrong, and the reason.** My first pass ran `psql -U postgres` and got
`FATAL: role "postgres" does not exist`, and I was one step from treating that as "the
database is unreachable, FIELD-08 cannot be evidenced". Wrong twice over. The role name was
*my assumption* — the project's own convention is `POSTGRES_USER` from the container env
(§3.3.0: "a separate logical database with its own application role"; and
`fetch-kwallet-secret.sh:136` states explicitly that the role is `fabrication_role` while
`a_fab` is the database name). **Reason: I guessed a default credential instead of reading
the credential the deployment actually declares, and then let one command's error generalise
into a verdict on the entire item.** Reading `podman inspect --format '{{range
.Config.Env}}...'` first costs one command. Generalisable lesson for every session here: on
this project, take the credential from the container environment before concluding anything
about a database.