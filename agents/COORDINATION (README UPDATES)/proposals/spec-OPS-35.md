---
item: OPS-35
action: new
evidence: |
  Four Grafana containers are running with no Quadlet owner, absent from §5.1 group D.
  Measured 2026-10-04:

    $ podman ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}' | grep -i grafana
    ao-metabase                              docker.io/metabase/metabase@sha256:fc96...  Up 2 days
    relaxed_tharp    docker.io/grafana/grafana:11.6.0            Up 28 hours
    confident_khayyam docker.io/grafana/grafana:11.6.0           Up 28 hours
    keen_bhabha       docker.io/grafana/grafana-oss:11.6.0       Up 25 hours
    ao-sqli3          docker.io/grafana/grafana-oss:11.6.0       Up 25 hours
    ao-grafana        docker.io/grafana/grafana-oss@sha256:b739...  Up 24 hours

  Ownership and network, via the Quadlet label and network list:

    relaxed_tharp     created=2026-10-03 08:54:41 nets=(none) netmode=pasta priv=false unit=
    confident_khayyam created=2026-10-03 09:00:35 nets=(none) netmode=pasta priv=false unit=
    keen_bhabha       created=2026-10-03 11:50:02 nets=(none) netmode=pasta priv=false unit=
    ao-sqli3          created=2026-10-03 11:50:58 nets=(none) netmode=pasta priv=false unit=
    ao-grafana        nets=ao-admin ao-reporting-egress     netmode=bridge unit=ao-grafana.service

  Only ao-grafana carries a Quadlet label. The other four have no service owner and are not
  on any of the fourteen registered ao-* networks; they use rootless pasta.

  Two carry writable mounts from /tmp, not the sanctioned read-only snapshot copies:

    confident_khayyam mounts=/tmp/tmp.2HBNsh7zgo:/probe
    ao-sqli3          mounts=/tmp/sqli-plugins2:/var/lib/grafana/plugins

  Mitigating, measured: no listener is exposed. `podman port` returns map[] for all four and
  `ss -ltn` shows no additional Grafana port. The only 3000/3001/3002 listeners are
  mastodon-web 127.0.0.1:3000, ao-grafana 127.0.0.1:3001, ao-metabase 127.0.0.1:3002,
  all loopback-bound. None is privileged.

  This is DISTINCT from the existing OPS-16, which covers only vigorous_shannon and
  dreamy_rosalind (two Foxglove containers). OPS-16 does not mention Grafana. Suggesting
  OPS-35 rather than widening OPS-16 so neither item loses its identity.
section: 06-component-boundaries-gui-reporting-tools-and-operator-access
---
# What I got wrong, and why

**I repeated a mistake my own prior session had already declared.** In enumerating the
Metabase environment I ran `podman inspect ao-metabase --format '{{range .Config.Env}}...'`
unfiltered and printed `MB_DB_PASS` into session output. My previous proposal recorded this
exact incident and named the safe method (`| grep -v -i pass`). I read that file and still did
it. The value is not reproduced in any section file, the README, or this proposal, and it is
not a credential I created — but it was printed when it should not have been, and knowing the
fix is not the same as applying it. The filter is now the first thing I type, not a
correction I read afterwards.

**I nearly repeated a different overclaim.** I first wrote "the four
`localhost/foxglove-bridge` containers". `podman ps -a | grep -c foxglove` returns **3**, of
which one is the sanctioned digest-pinned `ao-sim-fabrication-foxglove`. I had counted by
remembering the earlier `podman ps` listing rather than by re-running the count. Same failure
class as the four errors recorded in the previous proposal: a number in prose that no command
produced. Corrected before commit, and the count is stated here so a later reader can check it.

**One stale cross-reference survived two prior revisions.** §3.3.0 ended by pointing at §2.2 to
reconcile "the adjacent unregistered `10.89.10.0/24` and `10.89.11.0/24`". `10.89.10.0/24` has
been registered as `ao-reporting-egress` since §2.2 was rewritten, and §2.2 contains no
reconciliation text at all. The previous session corrected PostGIS, the reporting grants, and
four impossible dates in these same sections and passed over this sentence. Lesson for me: a
# Other corrections made this session

**§1 — the host is not Kubuntu.** `lsb_release -a` reports Ubuntu 26.04.1 LTS "resolute";
`/etc/kubuntu-release` does not exist; `kubuntu-desktop` is `Installed: (none)` and lives in
`universe`. Three `kubuntu-*` packages are installed. The host is Ubuntu LTS with KDE Plasma
6.6.6 on SDDM. Every functional claim §1 rests on is independently true and was verified
(`konqueror`, `kwalletmanager5`, `kwallet-query` present; `ros2` at `/opt/ros/lyrical/bin/ros2`;
i7-8700K; GeForce GTX 1080). Only the distribution label was loose. §1 now records this rather
than leaving a reader to discover it.

**§1 — QGroundControl is an AppImage, not a package.** No `qgroundcontrol` binary on PATH, no
entry in `/usr/share/applications`; it runs from
`~/Documents/APP IMAGES/QGroundControl-x86_64.AppImage`. `gzserver` is absent from the host PATH
because Gazebo runs containerised. Noted so §1 does not read as a package manifest.

**§6.A.3.1 — the Grafana datasource blocker re-attempted, still blocked, but the host-version
claim is now proven.** `sudo -n -u postgres psql` → `interactive authentication is required`;
`podman exec ao-grafana psql` → `sh: psql: not found` (the image ships no client). What I could
prove: Grafana's own log shows `Connecting to DB dbtype=postgres` with successful migrator lock
and unlock, and Metabase logs `Successfully verified PostgreSQL 18.6 (Ubuntu
# Claims re-verified as correct, with no change made

Proving these took as long as the corrections did, so they are recorded:

- **14 `ao-*` networks**, matching §2.2 and the §6.A.3.1 staleness table.
- **`ao-egress-community` and `ao-ardupilot-sitl` both do not exist** —
  `unable to find network with name or ID ...: network not found`. The §6.A.3.1 claim stands.
- **`10.89.11` absent from the registry** (`grep -c` → 0), folded into `ao-sales` as §5 records.
- **`sales_reporting_role` holds SELECT on exactly five views and no base table** —
  `v_reporting_orders`, `v_reporting_receipts`, `v_reporting_entitlements`,
  `v_reporting_sale_provenance`, `v_corda_entry_readiness`;
  `has_table_privilege(...,'SELECT')` returns `f` for all 17 base tables including `orders`.
  The §6.A.3 read-only claim is correct.
- **`sales_migration_role` is a superuser** with Create role, Create DB, Replication, Bypass RLS
  — matching the §6.A.3 watch-note.
- **Grafana/Metabase reach paths:** `ao-grafana` and `ao-metabase` both on `ao-admin` and
  `ao-reporting-egress`; `GF_DATABASE_HOST=/var/run/postgresql`; `MB_DB_HOST=10.42.0.1`;
  listeners `127.0.0.1:3001` and `127.0.0.1:3002`, loopback-bound only. §6.A.2 is correct.
- **Per-domain PostgreSQL versions in §3.3.1 all confirmed:** `ao-sales-db` 17.11,
  `mastodon-db` 17.11, `ao-fabrication-db` 17.11, `ao-webodm-db` 9.5.25, host cluster 18-main
  online.
- **PostGIS placement in §3.3.1 confirmed:** `webodm` has only `plpgsql`; `webodm_dev` has
  `plpgsql` plus `postgis 2.3.2`.
- **§3.3.0.1 isolation:** inside `ao-fabrication-db`, `/proc/net/route` holds exactly one route
  (its own subnet, no default) and `/proc/net/arp` resolves `10.89.12.1` with flags `0x2`. The
  "judge reachability from ARP, not a refused connect" note is correct.
- **§3.3.0.2 Domoticz posture holds:** `127.0.0.1:8080` open, `10.42.0.1:8080` refused, and no
  `:6144` listener at all.
- **§3.3.0 machine reachability:** `10.42.0.1` answers (0% loss), `10.42.0.96` shows
  `dev eno1 FAILED` in `ip neigh` and 100% loss on ping. The "not currently reachable" caveat
  remains accurate.

# Not touched

No payments, ledger keys, provenance records, secrets, backup/restore data, radio, serial or
firewall configuration, public ports, or any section file outside the three I own. §19 was not
edited. No container was started, stopped or removed. The `ao-egress-community` name/CIDR
decision and the `gui-boundary-matrix.yaml` reconciliation both belong to other groups and were
left untouched.
18.6-0ubuntu0.26.04.1) application database connection`. So the "host PostgreSQL 18" claim in
§3.3.1 is now measured from two independent sources rather than inferred from
`/etc/postgresql/`. Still unconfirmed, and the OPS group's to answer: which datasources Grafana
has actually *loaded*, as distinct from which files are provisioned.
cross-reference into another session's file is a claim about that file, and it goes stale
silently. Cross-references need the same re-verification as the prose around them.
Four unmanaged Grafana containers (`relaxed_tharp`, `confident_khayyam`, `keen_bhabha`,
`ao-sqli3`), created 2026-10-03 during datasource/plugin investigation, are running with no
Quadlet owner and are absent from the §5.1 group D inventory that §6.A.3 declares complete at
eighteen rows. Two of them mount writable `/tmp` paths, and `ao-sqli3` supplies the unsigned
`frser-sqlite-datasource` plugin to a Grafana instance that does not carry the signed instance's
allow-list policy.

**Not remediated by me, deliberately.** Stopping containers is a destructive action on running
state (README §4.1 rule 3), touches other sessions' work, and the unsigned-plugin question is
already tracked by the OPS group. Recorded in §6 as §6.A.3.2 with the full measurement, and
reported to the operator. Needs operator approval before removal.