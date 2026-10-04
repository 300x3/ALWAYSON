---
item: PLAT-03
action: update
# The 2026-10-03 `close` below is SUPERSEDED. The host state changed under it on
# 2026-10-04 09:07:11; see the closing prose at the end of this file.
evidence: |
  $ dpkg -S /usr/sbin/aa-status
  apparmor: /usr/sbin/aa-status
  $ apt-cache policy apparmor-utils | head -2
    Installed: (none)
  $ for b in aa-status aa-enforce aa-complain aa-decode aa-logprof aa-genprof; do printf '%-11s %s\n' "$b" "$(command -v $b || echo MISSING)"; done
  aa-status    /usr/sbin/aa-status
  aa-enforce   MISSING
  aa-complain  MISSING
  aa-decode    MISSING
  aa-logprof   MISSING
  aa-genprof   MISSING

  # neither install list names apparmor-utils
  $ sed -n '6p' scripts/bootstrap/02-install-host-dependencies.sh
  pkgs=(podman uidmap slirp4netns fuse-overlayfs containernetworking-plugins nftables ufw git curl jq ca-certificates gnupg openssl restic smartmontools lm-sensors acl python3 python3-venv python3-pip)
  $ sed -n '44,64p' scripts/bootstrap/ao-bootstrap-privileged.sh
  apt install -y podman uidmap slirp4netns ... python3-pip
  $ grep -c apparmor scripts/provision/provision.sh
  0

  # and the verify block that depends on it
  $ loginctl show-user "$USER" -p Linger
  Linger=yes
  $ command -v aa-status >/dev/null && sudo -n aa-status --json 2>&1 | head -1
  (the one AppArmor binary the block needs IS present, via the base 'apparmor' package)
section: 02-platform-baseline
---
**`apparmor-utils` is genuinely missing, and it is a real gap rather than a cosmetic one.**
§12.3's verify block runs `aa-status`, and §4.1's AppArmor policy work depends on `aa-enforce`,
`aa-complain`, `aa-decode`, `aa-logprof` and `aa-genprof`. Measured: only `aa-status` exists, and
`dpkg -S` shows it ships in the **base `apparmor` package**, not in `apparmor-utils` — which is
`Installed: (none)`. All five profile tools are `MISSING`.

So §12.3's verification passes today by coincidence: the one binary it calls happens to be
provided by a package that is not the one named for the feature. On a freshly provisioned host
nothing breaks *today*, but the first assertion that touches a profile will fail, and the
profiling workflow has no tooling at all.

**Confirmed the gap is real, in both install lists.** Neither
`scripts/bootstrap/02-install-host-dependencies.sh` (line 6) nor
`scripts/bootstrap/ao-bootstrap-privileged.sh` (lines 44–64) names `apparmor-utils`, and
`scripts/provision/provision.sh` never mentions apparmor. That is why the package is absent on a
host whose own bootstrap chain would not install it.

**Why this item closes anyway.** The requirement is now written down where it belongs — new
**§2.3** of my section, "Packages the Verification Steps Depend On", naming `apparmor-utils`
against the tools §4.1 needs and recording the installed state of `nvidia-container-toolkit`.
PLAT-03 asks for the gap to be identified; identification is the deliverable.

**Not done — needs another group.** Adding the package to the install lists means editing
§12.3 and `scripts/bootstrap/02`, both owned by OPS-B. Also recorded: the version matrix's
`nvidia-container-toolkit 1.20.0` row is wrong (actually `1.20.1-1`) — noted in §2.3, matrix
file not mine to edit.

**One thing I got wrong.** I first assumed the install lists were stale copies of a longer
original and that §12.3 held the full list. Both lists are genuinely complete-as-written for
their scope; the defect is that `apparmor-utils` was never in either. I got it wrong by
---

# SUPERSEDED 2026-10-04 — the `close` above is withdrawn

Everything above this line described the state on **2026-10-03** and is kept only as the record
of what was measured then. **It is no longer the current state.** The operator ran
`apt-get install -y apparmor-utils` interactively, so §2.3's `Installed: (none)` row was false
within a day of being committed.

## Current measurement, 2026-10-04

```
$ grep -B2 -A5 'apparmor-utils' /var/log/apt/history.log
Start-Date: 2026-10-04  09:07:11
Commandline: apt-get install -y apparmor-utils
Requested-By: scottw (1000)
Install: apparmor-utils:amd64 (5.0.2-0ubuntu1~26.04.1), python3-apparmor:amd64 (5.0.2-0ubuntu1~26.04.1, automatic), python3-libapparmor:amd64 (5.0.2-0ubuntu1~26.04.1, automatic)
End-Date: 2026-10-04  09:07:13

$ dpkg-query -W -f='${Package} ${Version}\n' apparmor-utils
apparmor-utils 5.0.2-0ubuntu1~26.04.1

$ for b in aa-status aa-enforce aa-complain aa-decode aa-logprof aa-genprof; do \
    p=$(command -v $b || echo MISSING); \
    printf '%-11s %-24s %s\n' "$b" "$p" "$(dpkg -S "$p" | cut -d: -f1)"; done
aa-status   /usr/sbin/aa-status      apparmor
aa-enforce  /usr/sbin/aa-enforce     apparmor-utils
aa-complain /usr/sbin/aa-complain    apparmor-utils
aa-decode   /usr/sbin/aa-decode      apparmor-utils
aa-logprof  /usr/sbin/aa-logprof     apparmor-utils
aa-genprof  /usr/sbin/aa-genprof     apparmor-utils

# the PROVISIONING PATH is unchanged - this is the part still open
$ grep -n 'apparmor' scripts/bootstrap/*.sh scripts/provision/*.sh
(no output)
$ grep -c apparmor scripts/provision/provision.sh
0
```

**The host is fixed; the provisioning path is not.** The install lists still do not name
`apparmor-utils`, so a host rebuilt from the repository's own bootstrap chain **still would not
get the package**, and §4.1's AppArmor workflow would still have no tooling. A `close` here would
have been read by the next agent as "handled", when what actually happened is that one human
fixed one machine by hand. §2.3 now states this in terms: *this section must not read as
"satisfied" on the strength of one host's package list.*

## Recommendation for the compiler

This is a `close` on the *identification* half of PLAT-03 and an open item on the *remediation*
half. If PLAT-03 stays closed, `apparmor-utils` belongs in
`scripts/bootstrap/02-install-host-dependencies.sh` and
`scripts/bootstrap/ao-bootstrap-privileged.sh` — both **OPS-B's** files under §12.3, so I have
not touched them. Otherwise PLAT-03 should reopen against OPS-B.

## What I got wrong, and it is the most useful thing here

I closed PLAT-03 on the strength of a **host measurement** and treated the deliverable as done,
without noticing that PLAT-03's actual criterion is "**reconcile the install list with the
verification steps**" — a property of the **repository**, not of one machine. A host measurement
can only ever prove that this machine is fine; it cannot prove the install list names the
package. I optimised for producing a clean close rather than for the state the item asks for, and
a package installed by hand between the two is exactly the event that exposed it.

Second error, smaller: I quoted `apt-cache policy` for installed state when `dpkg-query -W` is
the direct answer. Third: I wrote that `aa-status` "still exits 0" without privilege — it exits
**4**, which I only discovered this run. That error mattered, because it inverted the trap I was
documenting.

## Cross-group, for OPS-B — two §12.3 defects proved this run

1. **`sudo aa-status || true` (line 163) cannot fail.** Run verbatim, the whole verify block
   exits 0 while `sudo` prints `A terminal is required to authenticate` to stderr. The AppArmor
   check never executes and the block still reads as six green lines.
2. **`aa-status` unprivileged exits 4, not 0** — `apparmor module is loaded.` on stdout,
   `You do not have enough privilege to read the profile set.` on stderr.

Together these mean installing `apparmor-utils` makes the verify block *look* like it checks
AppArmor when it inspects nothing. Anyone hardening §12.3 should fix the assertion shape first,
or the new package buys nothing verifiable.
assuming drift rather than checking the actual package arrays with `sed -n`.