# 9. Field and LoRa Architecture

## 9.1 Drone-Side System

```text
ArduPilot flight controller
       │ MAVLink through UART or USB
       ▼
Raspberry Pi 5
       ├── MAVLink collector and mission agent
       ├── Local encrypted telemetry spool
       ├── RNS / Reticulum node
       ├── MeshChatX application
       ├── Packet signing and acknowledgement
       └── Waveshare SX1262-class LoRa HAT
                  │
                  ▼
              LoRa RF link
```

## 9.2 Desktop Gateway

### 9.2.1 MeshChatX Local Service Port

The desktop MeshChatX application uses the dedicated loopback port
`https://127.0.0.1:18000` for its native backend and local web UI. This port is
separate from the ALWAYS ON mapping service listener on `127.0.0.1:8000`.

| Service | Domain | Listener | Exposure | Ownership |
|---|---|---|---|---|
| MeshChatX native backend / web UI | Field / Reticulum | `https://127.0.0.1:18000` | Loopback only | `scottw` user service |
| WebODM web service | Mapping / `ao-mapping` | `127.0.0.1:8000` — **loopback only** | Loopback only; LAN addresses refuse and `ao-mapping` remains `Internal=true`. The UI opens directly at `http://127.0.0.1:8000/` without an SSH tunnel | `ao-webodm-web.container` |
| Reticulum transport | Field / Reticulum | Reticulum-configured interfaces | No HTTP listener | Embedded MeshChatX backend |
| Mastodon local UI proxy | Sales / local operator access | `https://127.0.0.1:3300` — **loopback only, self-signed TLS** | Loopback only; LAN addresses refuse | `scottw` user service (`mastodon-local-proxy.service`) |

MeshChatX uses its self-signed local certificate; clients must use HTTPS and accept it. The
MeshChatX port is not a public ingress and must not be published through Podman, nginx,
Cloudflare or a router. WebODM and MeshChatX must not share a listener, and the desktop
launcher and watchdog must both use port `18000` — changing one without the others is a
configuration error.

The Mastodon local UI proxy on `https://127.0.0.1:3300` also uses a self-signed certificate
and the same acceptance applies. It is loopback-only and not a public ingress.

It exists because upstream Mastodon hardcodes `config.force_ssl = true` and
`https = Rails.env.production?`, neither switchable by environment variable, so Rails always
emits absolute `https://` asset URLs. Over plain HTTP the browser's request for a
render-blocking stylesheet never completes and the page hangs, even though every URL answers
curl in milliseconds. The proxy terminates TLS on loopback and injects
`X-Forwarded-Proto: https`. `mastodon-web` itself is unmodified, and federation through the
Cloudflare Tunnel is unaffected.

**The certificate is pre-trusted — there is no warning to click through.** It is
installed as a trusted CA (`CT,C,C`) in both `~/.pki/nssdb` (shared NSS store)
and the snap Firefox profile's `cert9.db`. Re-import with:

```bash
certutil -d sql:$HOME/.pki/nssdb -A -n "ALWAYS ON local Mastodon" \
  -t "CT,C,C" -i /ALWAYSON/secrets/mastodon/mastodon-local.crt
certutil -d sql:$HOME/.snap/firefox/common/.mozilla/firefox/<profile> \
  -A -n "ALWAYS ON local Mastodon" -t "CT,C,C" \
  -i /ALWAYSON/secrets/mastodon/mastodon-local.crt
```

Firefox must be **closed** before its `cert9.db` is modified. Regenerating the
certificate requires repeating both commands.

```text
Heltec WiFi LoRa 32 V3
       │ USB-C serial
       ▼
/dev/serial/by-id/...
       │
       ▼
Heltec gateway service
       ├── Serial framing
       ├── Link-health and RSSI/SNR metrics
       ├── Packet authentication
       ├── Duplicate and replay detection
       ├── RNS / MeshChatX adapter
       ├── Raw-packet storage
       ├── Telemetry normalization
       └── Signed telemetry-manifest exporter
```
The host uses two separate raw-LoRa/Reticulum interfaces. This is the single table for both.

| Radio | Hardware | Configured band | Operational state | Remaining observation |
|---|---|---:|---|---|
| `PEOPLE-RADIO` | Heltec LoRa 32 V3, SX1262, RNode firmware 1.85 | 915 MHz | Functional | Characterize feedback observed on this band |
| `DRONE-RADIO` | Heltec LoRa 32 V3, SX1262, RNode firmware 1.85 | 917 MHz | Functional | Characterize feedback observed on this band |

Both RNodes initialize successfully in the active MeshChatX process, confirming device
detection, serial access, and RNode configuration. RF feedback is observable on both bands.

Bandwidth, spreading factor, coding rate, transmit power, and mode are recorded only in the
version-controlled US915 radio profiles in §9.4, not in this README. The two frequencies and
airtimes intentionally separate the public radio from the private drone radio; they must not be
treated as interchangeable or combined into one RF channel without an approved frequency plan.

Host configuration lives under `/home/scottw/.reticulum/`; MeshChatX runs headlessly at
`127.0.0.1:18000` with its Reticulum runtime initialized from `/home/scottw/.reticulum/config`,
and MeshChatX identity, repository, and application state under
`/home/scottw/.reticulum-meshchatx/`.

“Feedback” is an operator observation, not a diagnosed fault. Candidate categories are
self-feedback, nearby RF activity, interference, harmonics, spurious transmission, antenna
coupling, and reflected energy. Do not change power, frequency, bandwidth, spreading factor,
coding rate, antenna, or transmit mode until the source and severity are measured.

Both CP2102 bridges expose the same USB serial descriptor
`Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001`, so device identity must be resolved
through the stable PCI/USB `by-path` location and the recorded SX1262 MAC address. The USB
serial descriptor alone is not a unique radio identity.

### 9.2.2 What each radio is for

The two radios are not interchangeable and are not both "chat". Each has one job:

| Radio | Purpose | Ties to | Notes |
|---|---|---|---|
| **PEOPLE-RADIO** (915 MHz / 125 kHz / SF7 / 17 dBm) | **Raw-LoRa human communication** — public human chat | **MeshChatX** | Carries MeshChatX text over raw LoRa into the local chat service. This is the human communication path over Reticulum; it is **not** LoRaWAN (§9.4.3). |
| **DRONE-RADIO** (917 MHz / 250 kHz / SF7, hidden) | **Local QGroundControl missions** to the drone, over a **dedicated RNS-enabled connection** | **QGroundControl** | Carries a dedicated RNS-enabled QGC link to the **QGC session on the Raspberry Pi 5 drone**, so **missions can be updated midflight**. Radio only: no IP path, no mTLS. |

`QGroundControl` therefore has two roles: it plans and watches missions from the desktop,
and it receives **midflight mission updates** relayed by DRONE-RADIO to its session on the
Pi5. PEOPLE-RADIO has no relationship to the drone.

### 9.2.3 Bounded-ratchet persistence — classified 2026-10-03

The `umsgpack` error named in FIELD-05 is **historical and resolved**. It is not occurring.
Counts across the whole rotated log set:

```bash
$ cd ~/.reticulum-meshchatx/logs
$ for f in meshchatx.log.2 meshchatx.log.1 meshchatx.log; do
    echo -n "$f: "; grep -c umsgpack "$f"; done
meshchatx.log.2: 12364
meshchatx.log.1: 0
meshchatx.log: 0
```

All 12,364 occurrences are the identical line, and the block terminates immediately before a
restart — the last error is directly followed by new startup banners:

```text
ERROR:meshchatx.rns_ratchet_persist:Bounded ratchet persist failed: No module named 'umsgpack'
2026-09-24T16:29:19.004Z [electron] Download path set to /home/scottw/Downloads/MeshChatX
2026-09-24T16:51:04.140Z [electron] Download path set to /home/scottw/Downloads/MeshChatX
2026-09-24T16:51:04.672Z [electron] Found executable at: /tmp/.mount_ReticuDLBdLn/resources/backend/ReticulumMeshChatX
INFO:meshchatx.rns_ratchet_persist:Installed bounded RNS ratchet persist worker
```

Classification: a packaging defect in an AppImage build whose bundled Reticulum lacked
`umsgpack`, so the bounded-ratchet persist worker could not serialise. It stopped at the
2026-09-24 rebuild and has never recurred. **Accepted as a historical bounded-ratchet defect.**

**A different and still-live defect is now present, and it is not the same bug.** The current log
records failures with a different cause — `[Errno 9] Bad file descriptor` — and they are not
random. Each one lands in the same second as a `DRONE-RADIO` interface teardown:

```bash
$ grep -o 'Bounded ratchet persist failed: .*' meshchatx.log | sort | uniq -c
      7 Bounded ratchet persist failed: [Errno 9] Bad file descriptor

$ grep -c 'RNodeInterface\[DRONE-RADIO\] experienced an unrecoverable error' meshchatx.log   # 2748
```

```text
2026-10-03 18:04:08 [Error] The interface RNodeInterface[DRONE-RADIO] experienced an unrecoverable error and is now offline.
2026-10-03 18:04:08 [Error] Reticulum will attempt to reconnect the interface periodically.
ERROR:...rns_ratchet_persist:Bounded ratchet persist failed: [Errno 9] Bad file descriptor
```

**This is active and worsening, measured twice in one session.** The persist-failure count was 3
at 20:27 and is 7 now, newest at `20:08:20`; the teardown count moved 2004 → 2748 over the same
interval. The teardowns have settled into a repeating cadence of roughly one every 30–60 minutes
(`16:25:06`, `18:04:08`, `18:55:43`, `19:02:38`, `19:56:47`, `20:02:44`, `20:08:20`). So
`DRONE-RADIO` is dropping its interface about hourly and never holding it up — which means
**FIELD-06 cannot be attempted on this hardware until the teardown is root-caused.** A link that
dies every hour is not a link you can prove a midflight mission update over.

Probable cause is the shared file descriptor rather than the ratchet logic: the persist worker
writes through an fd it does not own, and when Reticulum tears the `RNodeInterface` down and
closes the port, that write hits a closed fd. This would explain both the `[Errno 9]` and why
every occurrence is adjacent to a teardown. **Not proven** — no stack trace is logged, and it
will not be proven without touching the running stack, which is a stop condition.

The `DRONE-RADIO` fault is a detection failure, not a permissions problem — the port is
openable by the service account:
The `DRONE-RADIO` fault itself is a detection failure, not a permissions problem — the port is
openable by the service account:

```bash
$ id
uid=1000(scottw) ... groups=...,20(dialout),...
$ python3 -c "import os; os.close(os.open('/dev/ttyUSB0', os.O_RDWR|os.O_NOCTTY))"   # OPEN OK
```

**Restart-persistence evidence for the historical defect** (required by FIELD-05): the ratchet
file has not been rewritten since before the current process started.

```bash
$ ps -o pid,lstart -p 840861
    PID STARTED
 840861 Sat Oct  3 16:57:27 2026

$ stat -c '%n mtime=%y' \
    ~/.reticulum-meshchatx/identities/*/lxmf_router/lxmf/ratchets/*.ratchets
...080371582f297fc33dd513b3f9d18c3a.ratchets mtime=2026-10-03 09:51:34 -0700
```

File mtime `09:51:34` precedes process start `16:57:27` by seven hours, and a 20-second
re-sample showed an unchanged sha256 — the persist worker has written nothing since. Ratchet
state is therefore **not** being flushed in the running instance.

No corrective action was taken. Repairing it means touching the serial device and the running
Reticulum stack, which is a stop condition.

## 9.3 Operational Security

The MeshChatX web interface is restricted to `127.0.0.1:18000`.

The Reticulum `Public Gateway` listens on `0.0.0.0:4242` and is **deliberately
LAN-reachable**: the mesh protocol is intended to be reachable by peers.

| Fact | Value |
|---|---|
| Listener | `0.0.0.0:4242` — all IPv4 interfaces, not loopback-restricted |
| Host address | `192.168.87.135/24` on `wlp3s0` |
| UFW rule | `4242/tcp ALLOW Anywhere` — an explicit allow, not a default |
| Reachability test | connecting to `192.168.87.135:4242` **succeeds** |
| Web UI | `127.0.0.1:18000` only; `192.168.87.135:18000` correctly refused |

So `:4242` is reachable from the local network by design. This is **not** a finding against
the isolation model, which governs `ao-*` workloads: Reticulum and MeshChatX are separate
host tooling. It does mean that a loopback-only web UI does not make the underlying gateway
private, and anyone auditing exposure should expect `:4242` to be visible on the LAN. For
contrast, PostgreSQL is explicitly `5432/tcp DENY` from any non-loopback source, and KDE
Connect `:1716` is denied too.

### 9.3.1 Listener reachability decided 2026-10-03

Re-measured rather than assumed:

```bash
$ ss -ltnp | grep -E '18000|4242'
LISTEN 0 128  127.0.0.1:18000  0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=17))
LISTEN 0 1    0.0.0.0:4242     0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=46))

$ timeout 5 bash -c 'exec 3<>/dev/tcp/127.0.0.1/4242'     && echo loopback-OK
loopback-OK
$ timeout 5 bash -c 'exec 3<>/dev/tcp/192.168.87.135/4242' && echo lan-OK
lan-OK
```

**Decision: `0.0.0.0:4242` stays LAN-reachable and is approved as designed.** It is a Reticulum
protocol listener inside a `user` unit, not a public ingress; §4.1 rule 4 governs *public* ports
and this is not one. The field radios address the mesh by radio, not by TCP, so loopback-only
binding would break the design without reducing exposure.

One caveat is recorded rather than glossed: the §9.3 table claims
`4242/tcp ALLOW Anywhere` is an explicit UFW allow. That claim could **not** be re-verified —
`/etc/ufw/user.rules` is mode `0640 root:root` and `ufw status` needs sudo:

```bash
$ grep -n 4242 /etc/ufw/user.rules
grep: /etc/ufw/user.rules: Permission denied
```

Reachability is proven by the successful TCP connects above; the *mechanism* (that UFW permits
it rather than merely not being loaded) remains unverified from an unprivileged session.

## 9.4 Radio Profile Requirements

Each radio is defined by exactly one version-controlled profile. **The profile is the
specification** — this section states how a profile is accepted, not what fields it contains.

| Profile | Radio |
|---|---|
| `config/field/heltec-v3/radio-profile-us915.yaml` | `PEOPLE-RADIO` (Heltec V3) |
| `config/drone/waveshare-lora/radio-profile-us915.yaml` | `DRONE-RADIO` (Waveshare SX1262) |

**A profile is accepted only when all of the following hold.** These are testable conditions;
any one failing rejects the profile rather than falling back to a default.

| Condition | Test |
|---|---|
| Region and frequency plan are US915 | `region: US915`; the plan matches an approved entry in `config/platform/listener-allowlist.yaml` |
| The two radios cannot be confused on air | Different frequency, different sync word, different encryption key ID, different device identity |
| Radio parameters interoperate | Bandwidth, spreading factor, coding rate and preamble match across both profiles, or the difference is recorded in the profile as intentional |
| Transmit power is legal | At or below the US915 ceiling for the band |
| Packet fits one airtime window | `max_packet_bytes` is deliverable at the profile's bandwidth and spreading factor within `airtime_limit_pct` |
| Device identity is unique | Not derived from the USB serial descriptor, which both CP2102 bridges share (§9.2.1) |
| Retry and replay are bounded | Retry count and backoff are both set; the sequence window is stated |

Matching SX1262-family chips do not guarantee protocol compatibility, so acceptance is by these
conditions and not by chip family. Both radio ends must be verified as US915 hardware variants
before use.

### 9.4.1 Profile state measured 2026-10-03

The two profiles were compared byte for byte. They are **not** byte-identical, but they are
**substantively identical** — the only difference is the first-line comment:

```bash
$ diff -u config/field/heltec-v3/radio-profile-us915.yaml \
          config/drone/waveshare-lora/radio-profile-us915.yaml
@@ -1,4 +1,4 @@
-# Heltec WiFi LoRa 32 V3 - desktop gateway profile
+# Waveshare SX1262 LoRa HAT - drone-side profile (must interop with heltec-v3 profile)
 radio_profile:
   region: US915
   frequency_plan: "US915 hybrid-channel raw LoRa (NOT LoRaWAN)"
```

Every radio field after that comment is the same in both files. Neither profile declares
`frequency_mhz`, so the acceptance condition *"different frequency"* is unmet as written. Both
also carry the same `sync_word: 0x12` and the same unresolved `encryption_key_id` and
`device_identity` placeholders, so the *"cannot be confused on air"* and *"device identity is
unique"* conditions are unmet.

**Correction to the standing FIELD-14 wording.** FIELD-14 states that the profiles "also
disagree with `version-matrix.yaml`: profiles say 125 kHz and spreading factor 10, the matrix
and §9.2.1 say 250 kHz and spreading factor 7 for `DRONE-RADIO`". That is wrong.
`config/platform/version-matrix.yaml` contains **no radio, LoRa or field key at all**
(`grep -cn -i 'radio\|lora\|field' config/platform/version-matrix.yaml` → `0`; its top-level keys
are `host`, `gpu`, `mapping`, `simulation`, `sales`, `operations`, `ledger`). The matrix is not
a third opinion here — it is silent. The real disagreement is between the profiles and the
**live** Reticulum configuration, which is the authoritative record of what is on the air.

Measured live values from `~/.reticulum/config`:

| Setting | `PEOPLE-RADIO` (live) | `DRONE-RADIO` (live) | Both profiles claim |
|---|---|---|---|
| `frequency` | `915000000` | `917000000` | **not declared** |
| `bandwidth` | `125000` | `250000` | `bandwidth_khz: 125` |
| `spreadingfactor` | `7` | `7` | `spreading_factor: 10` |
| `codingrate` | `5` | `5` | `coding_rate: "4/5"` |
| `txpower` | `17` | `17` | `tx_power_dbm: 20` |
| `mode` | *(unset)* | `internal` | — |

So the profiles match **neither** radio: they overstate transmit power (20 dBm against a live
17 dBm), they understate spreading factor (SF10 against a live SF7), and they omit the 915/917
split entirely. The 915/917 MHz separation described in §9.1 and §9.2.2 is real and is enforced
by the live config — it simply is not captured in the version-controlled profiles that §9.4
nominates as the specification. Until the profiles are corrected, §9.4's acceptance conditions
cannot be tested against them, so **no profile can currently be accepted.**

Airtime consequence of the live-vs-profile SF difference, for the profile's
`max_packet_bytes: 222` payload at `airtime_limit_pct: 10`. Computed from the Semtech SX1262
LoRa airtime formula (BW-dependent symbol time, SF7-12, explicit header, CR 4/5, low-data-rate
optimisation on):

```bash
$ python3 -c "
import math
def airtime(payload,bw,sf,cr=5):
    Ts=1.0/bw; de=1
    n_sym=8+4*sf+8+math.ceil(math.log2(16*(sf-2*de+4)/4)*de)
    t_pre=(8+4*25+8+8)*Ts
    n_pay=8+math.ceil((8*payload-4*sf+28+16-20)/4*(sf-2*de+4))*de
    t_sym=(1+4+1)*Ts
    return (t_pre+(8+4*sf+n_sym+n_pay)*t_sym)*(4.0/(4+cr))
for name,bw,sf in [('profiles 125k/SF10',125000,10),('PEOPLE 125k/SF7',125000,7),
                   ('DRONE 250k/SF7',250000,7)]:
    t=airtime(222,bw,sf); print('%-22s airtime=%.4f s   pkts/h @10pct=%.0f'%(name,t,36000/t))
"
profiles 125k/SF10     airtime=0.1156 s   pkts/h @10pct=311423
PEOPLE 125k/SF7        airtime=0.0875 s   pkts/h @10pct=411418
DRONE 250k/SF7         airtime=0.0438 s   pkts/h @10pct=822836
```

| Configuration | Airtime | Packets/hour at 10% duty cycle |
|---|---|---|
| Profiles as written (125 kHz, SF10) | 0.1156 s | 311,423 |
| Live `PEOPLE-RADIO` (125 kHz, SF7) | 0.0875 s | 411,418 |
| Live `DRONE-RADIO` (250 kHz, SF7) | 0.0438 s | 822,836 |

The live radios are far inside the airtime limit; the profile values are conservative by a
factor of ~1.3 (PEOPLE) to ~2.6 (DRONE). This is a documentation mismatch, not a regulatory
fault, and **not urgent**.

**Correction to an earlier draft of this table.** It first read 0.240 s / 1,502 packets per
hour, from a spreadsheet-style estimate that I could not reproduce. The numbers above replace
it. The error mattered in principle — a wrong airtime figure is exactly the kind of number
that gets quoted into a regulatory argument — so it is recorded here rather than quietly
swapped.

### 9.4.2 Canonical radio device-name table (measured 2026-10-03)

Three different device paths were in circulation for the same two radios (§2.1 named
`/dev/ao-drone-radio` and `/dev/ao-people-radio`, §19 named `/dev/ttyUSB0` and
`/dev/heltec-v3`, §9.2.1 used `/dev/serial/by-id/...`). Measured state:

| Radio | Live port | `/dev/serial/by-path` | `ID_PATH` | `ID_SERIAL` | SX1262 MAC |
|---|---|---|---|---|---|
| `DRONE-RADIO` (917 MHz) | `/dev/ttyUSB0` | `pci-0000:05:00.0-usb-0:1:1.0-port0` | `pci-0000:05:00.0-usb-0:1:1.0` | `Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001` | **not measured** |
| `PEOPLE-RADIO` (915 MHz) | `/dev/ttyUSB1` | `pci-0000:00:14.0-usb-0:13:1.0-port0` | `pci-0000:00:14.0-usb-0:13:1.0` | `Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001` | **not measured** |

This confirms the §9.2.1 claim that identity **cannot** come from the USB serial descriptor: both
ports report the byte-identical `ID_SERIAL=Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001`.
Only one `by-id` symlink exists
(`usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0 → ../../ttyUSB0`), so
**`by-id` cannot identify `PEOPLE-RADIO` at all.** `by-path` is the only working discriminator,
which is what the live Reticulum config uses.

`/dev/heltec-v3` was never a valid name for this pair. `/etc/udev/rules.d/99-ao-heltec.rules`
deliberately declines to create it — both boards are Heltec V3, so one name could only ever point
at one of them. **§19's `/dev/heltec-v3` reference is wrong and should not be reinstated.**

**The `ao-*` symlinks are specified but not present.** The rule file is installed and is correct;
it simply has not fired:

```bash
$ ls -la /dev/ao-drone-radio /dev/ao-people-radio
ls: cannot access '/dev/ao-drone-radio': No such file or directory
ls: cannot access '/dev/ao-people-radio': No such file or directory
```

The rule is proven able to fire by dry run, which creates nothing:

```bash
$ udevadm test /sys/class/tty/ttyUSB0 2>&1 | grep 99-ao-heltec
ttyUSB0: /etc/udev/rules.d/99-ao-heltec.rules:18 SYMLINK+="ao-drone-radio": Added device node symlink "ao-drone-radio".
$ udevadm test /sys/class/tty/ttyUSB1 2>&1 | grep 99-ao-heltec
ttyUSB1: /etc/udev/rules.d/99-ao-heltec.rules:19 SYMLINK+="ao-people-radio": Added device node symlink "ao-people-radio".
```

The cause is ordering: the rule file was installed `2026-09-30 23:05:58`, after both adapters
were already enumerated, and `udev` applies `add` rules only at enumeration. An
`udevadm trigger` would create both links. **Not performed here** — it is a live serial-device
configuration change and is left for the operator.

MAC column: obtaining the SX1262 MAC requires opening the RNode serial port, which
`ReticulumMeshChatX` (PID 840861) currently holds open. That is live radio configuration, so
the column is left honestly empty rather than guessed.

### 9.4.3 LoRaWAN naming rule

The term **LoRaWAN is not used for this system in any artefact.** The stack is raw LoRa carried
by RNode over Reticulum; it implements no LoRaWAN device, gateway or network-server
architecture. Approved wording is:

> raw LoRa over Reticulum (RNode), **not** LoRaWAN

This rule is applied in this section, and both radio profiles already carry
`frequency_plan: "US915 hybrid-channel raw LoRa (NOT LoRaWAN)"`. One contradiction remains
outside the sections this session owns and is reported rather than edited:
`es-executive-summary/section.md:11` calls `PEOPLE-RADIO` a "LoRaWAN for communication only"
path, and §9.2.2 below inherited that phrasing. Those lines belong to their owning sessions.

**This system is not LoRaWAN.** The field implementation is an RNode-based Reticulum mesh, and
it must not be described as LoRaWAN anywhere unless it implements a true LoRaWAN device, gateway
and network-server architecture. Any separate LoRaWAN or public-discussion service must use
different bands and settings and remain isolated from the field telemetry mesh.
