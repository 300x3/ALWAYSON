---
item: PLAT-03
action: close
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
assuming drift rather than checking the actual package arrays with `sed -n`.