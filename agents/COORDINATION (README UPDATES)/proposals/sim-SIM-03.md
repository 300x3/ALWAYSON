---
item: SIM-03
action: keep-open
evidence: |
  Measured 2026-10-04. QGroundControl is not on this host in any form, and the SITL
  stack it would attach to is not started.

  $ which QGroundControl
  (no output; exit 1)
  $ ls /opt/QGroundControl*
  ls: cannot access '/opt/QGroundControl*': No such file or directory

  $ podman ps -a --format '{{.Names}}' | grep -i -e qgc -e ground
  (no output)
  ^ no QGC container either, stopped or otherwise

  The SITL side it would talk to is present but not running:
  $ ls quadlet/sim-vehicle/
  ao-ardupilot-sitl.container
  $ systemctl --user is-active ao-ardupilot-sitl.service
  inactive
  $ systemctl --user is-enabled ao-ardupilot-sitl.service
  masked

  So there is no interactive workflow to validate end to end: neither the GCS nor
  the vehicle-side SITL it connects to is active on this host.
section: 10-simulation-architecture
---

SIM-03 stays open. There is no QGroundControl workflow to validate, because neither end of it
exists in a running state.

QGroundControl is not installed — not on the host, not as a container. The SITL unit it
would attach to, `ao-ardupilot-sitl.service`, is present but both **masked and inactive**.
That is a deliberate state, not a fault: an outward-facing radio-ish control link that
nobody has asked to expose stays masked, and I am not unmasking it to see what happens.

I did not install QGroundControl. It is a large GUI application with its own network
behaviour and a MAVLink link to a SITL instance; installing it unattended is a
configuration change to a masked unit's counterpart that §4.1 rule 12 covers, and SIM-03's
own acceptance criteria are about *validating* a workflow rather than provisioning one. The
validation has to be human-in-the-loop anyway — it ends with someone flying the vehicle.

**What I got wrong.** I checked `which` and `/opt` and concluded "not installed", then began
drafting as if a Quadlet might already be staged for it under a name I had not guessed. I
should have listed the Quadlet directory and grepped the container set in one pass, as I did
for SIM-01, instead of assuming a hidden unit existed. The two items share the same lesson:
a name I did not try is not an absence, and `podman ps -a` plus `ls quadlet/` settles it.
