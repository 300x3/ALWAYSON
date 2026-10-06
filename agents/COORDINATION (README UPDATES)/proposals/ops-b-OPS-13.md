---
item: OPS-13
action: close
evidence: |
  $ bash scripts/validation/check-user-linger.sh --check ; echo "rc=$?"
  user            : scottw
  Linger          : yes
  State           : active
  OK:   linger enabled
  marker file     : present (/var/lib/systemd/linger/scottw)
  OK:   user manager runtime /run/user/1000 present
        running user services: 90
  deployed units  : 21 .container files in /home/scottw/.config/containers/systemd
  generated ao-*  : 48 service units under systemd --user
  running ao-*    : 26
  rc=0

  $ loginctl show-user "$(whoami)" -p Linger
  Linger=yes

  # ground truth for the exit-2 path
  $ AO_LINGER_USER=alwayson-ledger bash scripts/validation/check-user-linger.sh --check
  rc=2            # no such account, distinct from a fault
  $ getent passwd alwayson-ledger ; echo $?
  2               # account does not exist, yet a linger marker file does

  # provision.sh dry run reaches stage 20 before stage 50
  $ AO_ROOT=/tmp/ao-sessions/wt-ops-b bash scripts/provision/provision.sh
  --- stage 20: user linger (required by every rootless Quadlet unit)
    linger: enabled for scottw
    [dry-run] bash /tmp/ao-sessions/wt-ops-b/scripts/validation/check-user-linger.sh
  --- stage 30: snaps (16) and flatpak (1)
section: 12-host-installation-and-configuration
---
New `scripts/validation/check-user-linger.sh`, wired into `provision.sh` stage 20
so linger is reported before stage 50 deploys any unit. §12.3.1 documents why
this is a precondition rather than a nicety: every workload here is a rootless
*user* Quadlet unit, and that `systemd --user` instance only exists while a
session is open, so logging out of KDE stops every container and none return on
reboot.

The provisioner **reports** linger and deliberately does not enable it:
`loginctl enable-linger` needs root and writes `/var/lib/systemd/linger/`, which
README §4.1 rules 1/3 place with the operator. This needs operator approval if
anyone wants the rebuild to do it unattended — I did not.

**What I got wrong.** Three bugs, all of which produced confident, wrong output.

1. A false `FAIL` for an account that does not exist.
   `loginctl show-user <ghost> -p Linger` prints `Failed to look up user`, but
   with `--value` it prints the literal string `unknown`, which the script
   compared against `yes`. Worse, `/var/lib/systemd/linger/` is not proof of
   existence — `alwayson-ledger`, `alwayson-mapping` and `alwayson-sales` all
   have marker files on this host while `getent passwd` finds none of them. The
   check now tests `getent passwd` first and exits 2, distinct from exit 1. A
   false FAIL on a checker is the worst kind of defect: it trains the operator to
   ignore the tool, which would then hide a genuine `Linger=no`.
2. It grepped unit files for `\.container`, a name systemd never creates —
   Quadlet *generates* `ao-<name>.service`. It therefore claimed "21 deployed but
   none enabled" on a host with 26 ao-* services running.
3. It called `id -u` with no argument, so checking any account other than the
   caller reported `/run/user/-1`.

I did not catch 2 and 3 by reading the script; both surfaced only when I ran the
check on this host and compared its numbers against `systemctl --user`.