# COORDINATION — J: RNS public/private split — how to draw it, and what NOT to draw

**From:** Cline session, 2026-10-01 late evening
**Scope:** the MeshChatX / Reticulum (RNS) topology representation, and the
`ao-build-update` network. **The topology GRAPHIC is NOT mine to do — it is
handed to whichever session takes it.** This document supplies the facts it needs
and must not conflict with.
**State:** design facts COMMITTED to `config/build-update/stable-refs.yaml`.
No Quadlet, no network, no service was changed. MeshChatX still runs as a host
user service on `127.0.0.1:18000`, untouched.

## Read this first

1. **The RNS public/private split is ALREADY IMPLEMENTED and it is correct.**
   Do not draw it as two stacks, two installs, or two networks. It is ONE RNS
   stack with TWO RNode interfaces in different interface modes. If the graphic
   shows two separate MeshChatX/RNS installations, it is wrong.
2. **There is no `interface_routing_id` in this RNS build.** I checked the
   bytecode. Do not draw or describe routing-ID ranges; that mechanism does not
   exist here. Separation is by INTERFACE MODE.
3. `config/build-update/stable-refs.yaml` is a file I have been editing. It
   carries the `meshchatx_placement` decision and its evidence. Read it before
   editing that file; do not remove that block.
4. The operator's own ES.1 brief in `X - README - GITHUB REVIEW - 20261001.txt`
   already asks for the radio rows to be combined as RNODE CLIENT A = PEOPLE-RADIO
   and RNODE CLIENT B = DRONE-RADIO. **Naming discrepancy, see Traps.**

## The verified facts (measured 2026-10-01 ~22:00)

Single stack, `~/.reticulum/config`, read by MeshChatX via
`--reticulum-config-dir`. 43 interfaces up.

    [[PEOPLE-RADIO]]  915 MHz / 125 kHz   selected_interface_mode = 1
    [[DRONE-RADIO]]   917 MHz / 250 kHz   selected_interface_mode = 7
                                         + mode = internal, discoverable = no

Bytecode exposes `MODE_FULL` and `MODE_INTERNAL`. So mode 1 = FULL (peers on the
public network), mode 7 = INTERNAL (private leaf: no transit, not announced).

`rnstatus` at runtime confirms it:

    RNodeInterface[PEOPLE-RADIO]  Up  Mode Full     5.47 kbps  noise -93 dBm
    RNodeInterface[DRONE-RADIO]   Up  Mode Internal 10.94 kbps noise -87 dBm

Both are backed by named udev symlinks from
`/ALWAYSON/config/field/heltec-v3/udev/99-ao-heltec.rules`:
`/dev/ao-drone-radio` -> ttyUSB0, `/dev/ao-people-radio` -> ttyUSB1, mode 0660,
group dialout, `ID_MM_DEVICE_IGNORE=1` so ModemManager cannot steal them.

Alongside the two radios are roughly thirty `TCPClientInterface` peers on port
4242 to public Reticulum backbones. That set is the PUBLIC half.

MeshChatX (pid 5239) holds BOTH serial devices open, because it embeds RNS.

## QGroundControl changes the picture — do not draw it as a separate air path

The operator stated QGC will **eventually be set up to use RNS to communicate to
the drone, encrypted.** I had wrongly assumed QGC would sit outside RNS on the
raw LoRa link. That assumption was wrong and it matters: because drone traffic
is intended to travel THROUGH this one stack, one stack is the CORRECT design
rather than a compromise. Two RNS installations would break it, because Routing
IDs are meaningful only within a single stack.

So the picture is: one RNS, two radios, one of them in Internal mode. QGC's future
encrypted path rides the internal half.

## How to represent it (answering the operator)

**On the graphic — draw:**
- MeshChatX as the single operator of Reticulum, one node, not two.
- Two RNode interfaces hanging off it, labelled with mode: PEOPLE-RADIO (Full,
  public) and DRONE-RADIO (Internal, not discoverable).
- The public TCP backbone cloud as the third egress off PEOPLE-RADIO/public side.
- Mark DRONE-RADIO as reaching the drone Pi5 only, and note QGC's encrypted path
  rides it.
- The private/public boundary as a property of DRONE-RADIO's mode, not as a
  separate network.

**In Podman, if it is ever containerised — the shape I verified is viable:**
- Device pass-through WORKS. Tested: `podman run -v /dev/ao-drone-radio:/dev/ao-drone-radio`
  and the same for people-radio both present the device and read it.
- It would need TWO networks: `ao-field` (Internal=true, the field/drone side)
  plus a new non-internal egress network, exactly the `ao-reporting-egress`
  precedent that `ao-grafana` and `ao-metabase` already use.
- Web UI stays on loopback, `PublishPort=127.0.0.1:18000:18000`.
- **NOT DONE.** It changes network topology, isolation policy and adds serial
  passthrough to a container. That needs operator approval and is out of scope for
  me. It is also NOT needed to fix the security question, because the split is
  already enforced by RNS interface mode.

## Open findings

1. **Docker device ownership inside a container.** The pass-through test showed
   the device as `nobody:nobody` inside the container even though the host side
   is 0660 root:dialout. A MeshChatX container would need `GroupAdd=dialout` and a
   matching user, otherwise it can open the ports but may not as its own service
   user. Needs testing if containerisation is ever approved. Needs operator
   approval to proceed at all.
2. **`autoconnect_announces_to_internal = yes`** is set globally in the RNS
   config (line 9). I did not determine what it affects in this version. Worth
   checking before anyone claims the internal side is airtight. Recommend operator
   review.
3. **Naming collision with the operator brief.** `X - README - GITHUB REVIEW`
   calls the drone radio **"DONE-RADIO"** in one line. The RNS config, the udev
   symlink and everything I verified say **DRONE-RADIO**. I believe "DONE" is a
   typo for "DRONE", but whoever does the graphic should confirm rather than draw
   "DONE-RADIO".

## Traps

- `rnstatus` output is long and the RNode entries are far down. Grep for RNode,
  do not read the top.
- The RNS shipped with MeshChatX is **compiled `.pyc` only**. `grep` over it finds
  nothing; use `strings <file>.pyc`.
- `/home/scottw/.reticulum/config` contains key material further down. Filter
  `key_material` / `password` before pasting anything.
- MeshChatX holds BOTH radios in one process. Killing it drops both radios at
  once, including the drone link.
- `ao-field` is `Internal=true`. Anything on it has no public egress by
  definition. This is why containerising MeshChatX needs a second network.

## Housekeeping

- I did not modify `TOPOLOGY/`, `TOPOLOGY - SINGLE GRAPHIC/`, or
  `scripts/operations/generate-topology.py`. Those are untouched and available.
- The graphic is generated from `/ALWAYSON/config/platform/topology-model.yaml`
  by `scripts/operations/generate-topology.py`. I DID edit that YAML earlier today
  (ao-build-update rows only). Any session regenerating the graphic should
  re-read it; my rows are current.
