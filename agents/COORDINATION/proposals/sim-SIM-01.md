---
item: SIM-01
action: keep-open
evidence: |
  Measured 2026-10-04. The fabrication GUI client exists and runs; the vehicle one
  does not, and the DDS/interface policy is unwritten in both places it would live.

  GUI clients -- one of two exists:
  $ podman ps --format '{{.Names}} {{.Status}}' | grep -i -e gz -e foxglove
  ao-sim-fabrication-gz         Up 15 hours
  ao-sim-fabrication-foxglove  Up 38 hours
  # no ao-sim-vehicle-gz, no ao-vehicle-gz, no equivalent Quadlet:
  $ ls quadlet/sim-vehicle/
  ao-ardupilot-sitl.container
  ^ SITL only. There is no vehicle GUI client .container at all.

  DDS / interface policy -- absent where it would be enforced:
  $ grep -rn 'CYCLONEDDS\|RMW_IMPLEMENTATION\|FASTRTPS\|dds' \
      quadlet/sim-vehicle/*.container quadlet/sim-fabrication/*.container
  (no output)
  ^ zero hits. No Unit ships an Environment= line selecting a DDS implementation,
    so each container silently uses its own default. On this host the two live
    sim containers are on different networks and cannot see each other anyway.

  What IS decided and working is the partition, not the middleware:
  GZ_PARTITION / GZ_IP are set per container so the fabrication gz-sim server and
  its GUI never share a namespace with anything else.
section: 10-simulation-architecture
---

SIM-01 stays open on both limbs, and neither is close to done.

The **DDS policy** limb has no artifact. I grepped both Quadlet directories for
`CYCLONEDDS`, `RMW_IMPLEMENTATION`, `FASTRTPS` and `dds` and got nothing. There is no
documented middleware choice and no `Environment=` line enforcing one, so each container
falls back to its own compiled-in default. That is not necessarily broken today — the
fabrication pair works because `GZ_PARTITION` and `GZ_IP` isolate them and they share a
network — but "it happens to work" is not a decided policy, and it will not survive
adding the vehicle side.

The **GUI clients** limb is half done. `ao-sim-fabrication-gz` and
`ao-sim-fabrication-foxglove` are both up and have been for 15 and 38 hours. The vehicle
side has **no GUI client container at all** — `quadlet/sim-vehicle/` holds exactly one file,
`ao-ardupilot-sitl.container`, which is the SITL process, not a viewer. So there is nothing
to decide the policy for until that is built.

I did not build the vehicle GUI client: it is new Quadlet work on a network I have not been
asked to extend, and SIM-08/SIM-04 gate what should be exposed. I did not modify any
network, no `Environment=` line, and no running container.

**What I got wrong.** I first ran the GUI-client grep expecting to find a vehicle viewer,
because §19 phrases SIM-01 as "clients deployed" and I had assumed the vehicle side was
merely unverified like the fabrication side had been. Listing the Quadlet directory is what
showed the file does not exist at all. Absent is a different finding from inactive, and I
nearly filed them as the same thing.
