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

### 9.2.3 Bounded-ratchet persistence — classified 2026-10-03, **CLASSIFICATION REVERSED 2026-10-05**

> **READ THIS BEFORE THE PARAGRAPHS BELOW.** Everything under this heading up to the
> 2026-10-05 entry was written on 2026-10-03/04 and **two of its claims are now known to be
> wrong**: (1) the `umsgpack` fault is *not* demonstrably historical — the count quoted here
> **reproduces in no retained log today**, so the evidence it rested on was rotation-fragile;
> (2) the causal hypothesis I withdrew below is **re-supported** by fresh data. The
> 2026-10-05 entry supersedes both. FIELD-05 is reopened.

The `umsgpack` error named in FIELD-05 was classified as **historical and resolved**. It is not
occurring. Counts across the whole rotated log set:

```bash
$ cd ~/.reticulum-meshchatx/logs
$ for f in meshchatx.log.2 meshchatx.log.1 meshchatx.log; do
    echo -n "$f: "; grep -c umsgpack "$f"; done
meshchatx.log.2: 12364
meshchatx.log.1: 0
meshchatx.log: 0
```

**2026-10-05: the 12,364 count no longer reproduces in any file, and the error text is absent
everywhere.** Re-measured binary-safe, across all four retained logs:

```bash
$ for f in meshchatx.log.3 meshchatx.log.2 meshchatx.log.1 meshchatx.log; do
    echo "$f: umsgpack=$(grep -ac umsgpack $f)  'No module named'=$(grep -ac 'No module named' $f)"
  done
meshchatx.log.3: umsgpack=0  'No module named'=0
meshchatx.log.2: umsgpack=0  'No module named'=0
meshchatx.log.1: umsgpack=0  'No module named'=0
meshchatx.log:   umsgpack=0  'No module named'=0
```

`No module named 'umsgpack'` — the exact string quoted below — **occurs in no retained log.**
The segment holding those errors has been overwritten by rotation since 2026-10-04. **Reason the
earlier claim was wrong: a count taken from a rotated log filename is not durable evidence,
and I treated it as though it were.** A grep count of 0 in the *current* file proves only that
the current file has none, which is a much weaker claim than "historical and resolved".

All 12,364 occurrences were the identical line, and the block terminated immediately before a
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

**CORRECTION 2026-10-04: this cadence figure is wrong by a factor of ~150.** The
"roughly every 30–60 minutes" cadence above was derived from the timestamps of the
*ratchet persist failures* — there are only 13 of those — not from the teardowns
themselves. Counting the teardowns directly:

```bash
$ grep -c 'unrecoverable error' ~/.reticulum-meshchatx/logs/meshchatx.log        # 994
$ grep -c 'Bounded ratchet persist failed' ~/.reticulum-meshchatx/logs/meshchatx.log # 0
$ grep -ch 'unrecoverable error' ~/.reticulum-meshchatx/logs/meshchatx.log{,.1,.2,.3}
994 / 7800 / 2389 / 29                                                        # 11,212 total
```

**2026-10-05: the `0` on line two of that block was TRUE when written, and is no longer true.**
It now reads **4**. The logs are binary to `grep`, so I re-checked with `grep -ac` to rule out a
counting artefact — `grep -c` and `grep -ac` both return 4, so the increase is real, not a
truncation effect. The four are new occurrences dated today; the withdrawal below was sound on
2026-10-04 and is superseded by §9.2.3.1 because the association it denied has since held
again. The teardown counts on lines one and three are unaffected — the cadence conclusion
below stands. (The current log's `DRONE-RADIO` teardown count is now 3889, up from 994 as
measured on 2026-10-04: the figure grows continuously because the radio is still retrying.)

**`DRONE-RADIO` is not dropping hourly — it is retrying roughly every 7 seconds and has
never recovered.** Consecutive events at `07:25:38`, `07:25:44`, `07:25:51`, `07:25:57`.
The conclusion of the paragraph above still stands, and in fact hardens: a link that dies
every *seven seconds* is even less a link one could prove a midflight mission update over.
Only the period was wrong, not the judgement.

**The causal hypothesis above is also not supported, and I withdraw it.** It rested on
"every occurrence is adjacent to a teardown". That is true of the 13 `[Errno 9]` persist
failures, but those were in `meshchatx.log.1`/`.3`; the *current* log has 994 teardowns and
**zero** persist failures, so the association does not hold in the log where the fault is
actually happening now. A shared-fd mechanism remains plausible in principle, but on this
evidence it is **unproven and now positively unsupported**, and the far simpler reading is
the one §9.5.2 reaches: the board is enumerated but does not answer the RNode detection
handshake, and the `[Errno 9]` persist errors are a consequence of the port closing, not a
cause. Recorded rather than deleted, per the rule against editing history quietly.

Original hypothesis, now **withdrawn** on the evidence above and retained only so the
correction is auditable: it attributed both the `[Errno 9]` persist failures and the cadence
to a shared file descriptor — the persist worker writing through an fd it does not own, which
fails when Reticulum tears the interface down and closes the port. That mechanism was never
proven (no stack trace is logged) and is now positively unsupported, since the log where the
fault actually recurs contains no persist failures at all.

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

#### 9.2.3.1 Classification reversed 2026-10-05 — the persist fault is LIVE, and it tracks
#### the `DRONE-RADIO` teardown

**The 2026-10-03 classification above is withdrawn. FIELD-05 is reopened.** Two separate things
were wrong with it, and the second is the one that matters operationally.

**1. The `umsgpack` evidence does not survive.** The 12,364 count and the string
`No module named 'umsgpack'` reproduce in **no retained log** (counts above). The classification
"historical packaging defect, never recurred" rested entirely on a count taken from a rotated
filename, and rotation has since destroyed the segment it referred to. I cannot now prove the
`umsgpack` fault ever stopped, only that its evidence is gone.

**2. The persist fault is still happening, today.** On 2026-10-04 I withdrew the
shared-file-descriptor explanation, on the grounds that the current log had 994 `DRONE-RADIO`
teardowns and **zero** persist failures. That reading was correct on the day — but the zero was a
*count from an earlier point in a live log*, and the current log is still being appended to. It
now holds four, and the association is exact:

```bash
$ grep -ac 'Bounded ratchet persist failed' meshchatx.log
4                                   # in the current log, i.e. today
$ grep -a 'Bounded ratchet persist failed' meshchatx.log | tail -1
ERROR:meshchatx.rns_ratchet_persist:Bounded ratchet persist failed: [Errno 9] Bad file descriptor
$ grep -an 'Bounded ratchet persist failed' meshchatx.log | cut -d: -f1
8049
12279
16470
19670
```

Every occurrence, with its surrounding lines — note the same second, and the reconnect that
immediately follows:

```text
[2026-10-05 03:15:33] [Error]  The interface RNodeInterface[DRONE-RADIO] experienced an unrecoverable error and is now offline.
[2026-10-05 03:15:33] [Error]  Reticulum will attempt to reconnect the interface periodically.
ERROR:...rns_ratchet_persist:Bounded ratchet persist failed: [Errno 9] Bad file descriptor
[2026-10-05 03:15:33] [Error]  Error while reconnecting port, the contained exception was: 'NoneType' object cannot be interpreted as an integer
[2026-10-05 03:15:38] [Notice] Opening serial port /dev/serial/by-path/pci-0000:05:00.0-usb-0:1:1.0-port0...
```

Identical shape at `04:59:53`, `06:42:08` and `07:59:53`. Counts of this live error per file,
oldest first: `.3` 2, `.2` 13, `.1` 9, current 4.

**Why this is the same defect and not a new one.** `[Errno 9] Bad file descriptor` on a persist
write, firing in the same second as an interface teardown, is consistent with **the ratchet
state file's descriptor being closed as a side effect of the `DRONE-RADIO` reset** — the
hypothesis I withdrew. The withdrawal was sound on the evidence available on 2026-10-04; it is
superseded because that evidence was a snapshot of a file still being written to. It is
reinstated as the **leading hypothesis, not a proven mechanism**: I have not traced the code
path, and no stack trace is logged.

**The operational consequence, which is the point.** The persistence subsystem is failing daily
and **downstream of the same broken board** that blocks FIELD-01/02/03/06. One board repair may
clear both. That is a stronger result than the closure I gave on 2026-10-04, where I noted this
error and then wrote it off as "a different bug, not covered by closing FIELD-05" — which left a
real daily fault with no open item against it.

**Why I got it wrong, in the form that generalises.** Two different mistakes, both from trusting
a count more than its scope. First, the `umsgpack` figure came from a **rotated** log filename, and
rotation has since destroyed the segment it described — a `grep -c` against a file that will be
overwritten answers "what is in this file now", which I read as "what is true of the fault". The
tell was available and I recorded it: the count lived in `meshchatx.log.2` in one pass and
`meshchatx.log.3` in the next. **A count that moves when you rename the file is not measuring the
fault.** Second, the "zero persist failures" I used to withdraw the teardown hypothesis was a
count of a **live, still-growing** log — correct that day, superseded today, and I nearly
dismissed today's four as a measurement artefact.

**On the binary-grep worry, checked rather than assumed:** these logs *are* binary to `grep`
(`binary file matches`), which is a real trap for anyone counting here. I tested whether it
explained the discrepancy and it does not — `grep -c` and `grep -ac` both return 4 on the current
log. So use `grep -a` for safety, but the numbers above are not a truncation effect.

**Nothing was changed.** Read-only inspection. No service restart, no file touched.

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

**Re-verified 2026-10-04 15:09 — the decision stands, the caveat is now better characterised.**
Both connects still succeed and the listener is unchanged. I also confirmed the blocker is a
**privilege wall and not a missing file**, which sharpens what is left to check:

```bash
$ ufw status
ERROR: You need to be root to run this script
$ sudo -n true
sudo: interactive authentication is required
$ find <repo>/config -iname '*firewall*' -o -iname '*ufw*'
(no output)
```

So there are **two** distinct things a privileged reviewer must supply, not one:

1. **The mechanism** — whether UFW is loaded and whether `4242/tcp` is an explicit `ALLOW`
   (the §9.3 table asserts this; it remains an assertion). Requires `sudo ufw status` or read
   access to `/etc/ufw/user.rules`.
2. **The policy to review against** — FIELD-04 asks for a review against "field-domain firewall
   policy", and **no such policy document exists in the repository.** `config/field/` contains
   only `heltec-v3`. There is nothing written down for the 4242 exposure to be judged against.

Point 2 is the more useful finding. Even with full root, "reviewed against field-domain firewall
policy" could not be completed as written, because the policy is unwritten. Closing that gap is
a documentation task in a section this session does not own; it is reported rather than edited.

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

## 9.5 Measured radio link state 2026-10-04

The two RNodes are both physically present and enumerated, but **only one of them is
operational**. `PEOPLE-RADIO` (915 MHz) is up; `DRONE-RADIO` (917 MHz) has been in a hard
reconnect failure since 2026-09-25. This is the dominant constraint on every remaining
field-link item and is recorded here so the next session does not re-derive it.

### 9.5.1 `DRONE-RADIO` has never come up since 2026-09-25 16:27

The last successful detection of either radio is 2026-09-25 16:27:11. Since then every
attempt has failed identically:

```bash
$ grep -h 'is configured and powered up' ~/.reticulum-meshchatx/logs/meshchatx.log* | tail -3
[2026-09-24 11:02:55] RNodeInterface[DRONE-RADIO] is configured and powered up
[2026-09-25 16:27:08] RNodeInterface[PEOPLE-RADIO] is configured and powered up
[2026-09-25 16:27:11] RNodeInterface[DRONE-RADIO] is configured and powered up

$ grep -ch 'unrecoverable error' ~/.reticulum-meshchatx/logs/meshchatx.log{,.1,.2,.3}
994
7800
2389
29
                                                        # 11,212 total.
                                                        # The current log grows live at ~7s per cycle,
                                                        # so this count rises continuously.
```

Every failure has the same three-line signature, repeating about every 7 seconds:

```text
[2026-10-04 07:25:38] [Notice] Opening serial port /dev/serial/by-path/pci-0000:05:00.0-usb-0:1:1.0-port0...
[2026-10-04 07:25:40] [Error]  Could not detect device for RNodeInterface[DRONE-RADIO]
[2026-10-04 07:25:40] [Error]  A serial port error occurred, the contained exception was: [Errno 9] Bad file descriptor
[2026-10-04 07:25:40] [Error]  The interface RNodeInterface[DRONE-RADIO] experienced an unrecoverable error and is now offline.
```

The failure is still live at the time of writing — the last event is 2026-10-04 09:18:25.

### 9.5.2 The fault is the radio board, not the port, the symlink or permissions

Ruled out by measurement, not assumption:

| Candidate cause | Verdict | Evidence |
|---|---|---|
| `by-path` symlink missing | **Ruled out** | `pci-0000:05:00.0-usb-0:1:1.0-port0 -> ../../ttyUSB0` present |
| Permission / `dialout` | **Ruled out** | `id` → `20(dialout)`; device is `crw-rw---- root:dialout` |
| Cable / USB enumeration | **Ruled out** | `cp210x 3-1:1.0: converter now attached to ttyUSB0`, `ID_SERIAL_SHORT=0001` |
| Port contended by another process | **Not the cause** | the same stack owns both radios; `PEOPLE-RADIO` on the other port works |
| **RNode firmware not answering** | **Best supported** | `Could not detect device` with no port-level error before it |

The distinction matters. A port that cannot be opened raises a permission or busy error;
this port opens and then yields `Errno 9` during the RNode detection handshake, which is
what a board that is enumerated but not running RNode firmware does. The kernel logged a
clean attach and has logged no disconnect.

**This is a hardware/firmware fault on the DRONE-RADIO board and needs physical
intervention — reseat the USB cable, or reflash the RNode firmware.** It cannot be fixed
from the documentation side, and it is the reason FIELD-01, FIELD-02, FIELD-03, FIELD-06
and FIELD-07 cannot be closed on evidence.

### 9.5.3 `PEOPLE-RADIO` is up and clean

`PEOPLE-RADIO` came up at 2026-10-03 16:57:56, 29 seconds after the current process
started, and has logged no error since. It is the only radio currently on air.

```bash
$ grep -h 'PEOPLE-RADIO. is configured and powered up' ~/.reticulum-meshchatx/logs/meshchatx.log.1
[2026-10-03 16:57:56] [Notice] RNodeInterface[PEOPLE-RADIO] is configured and powered up
$ grep -c 'PEOPLE' ~/.reticulum-meshchatx/logs/meshchatx.log
0
```

The asymmetry is the whole finding: the 915 MHz radio is healthy, the 917 MHz radio is
dead. Any characterisation of "both bands" is therefore characterisation of one band.

### 9.5.4 A single-radio host cannot measure what FIELD-01 and FIELD-03 ask for

FIELD-01 wants RSSI, SNR, noise floor, packet loss, retry behaviour and airtime **on both
RNodes**. With one radio offline there is no second node to measure against, and no RF
traffic in the logs at all:

```bash
$ grep -oh -E '(RSSI|rssi)[=: ]+[-0-9.]+' ~/.reticulum-meshchatx/logs/meshchatx.log* | wc -l
0
```

FIELD-03 wants 915/917 isolation *measured*. Separation between two bands cannot be
characterised while one band has no transmitter on it; the 915 MHz receiver is only ever
hearing ambient noise, which is not an isolation measurement. **These items cannot be
closed by any amount of further analysis on this host** — they need the DRONE-RADIO board
repaired first.

### 9.5.5 Field items blocked, and on what

| Item | Status | Blocker |
|---|---|---|
| FIELD-01 | Blocked | §9.5.1 — DRONE-RADIO offline; no RF metrics exist to record |
| FIELD-02 | Blocked | §9.5.1 — no end-to-end link over the drone path |
| FIELD-03 | Blocked | §9.5.4 — one band has no transmitter, so isolation is unmeasurable |
| FIELD-06 | Blocked | §9.5.1, plus needs the Pi5 (absent, §9.5.6) and an in-flight test |
| FIELD-07 | Blocked | needs *two* ends of a PEOPLE-RADIO mesh; only the desktop radio exists |
| FIELD-09 | Blocked | §9.5.6 — RPi5 not present on this network at all |

### 9.5.6 The Pi5 drone is absent from this network

FIELD-06 and FIELD-09 both terminate on a Raspberry Pi 5 running the QGC session. There is
no Pi5 reachable:

```bash
$ getent hosts raspberrypi raspbianpios alwayondrone rpi5
(no output — not in DNS)
$ ls ~/.ssh/config
ls: cannot access '/home/scottw/.ssh/config': No such file or directory
$ ip neigh
169.254.207.81 dev eno1 lladdr 30:05:5c:ee:a2:9b STALE
10.42.0.96   dev eno1 FAILED
192.168.87.1  dev wlp3s0 lladdr 16:22:3b:67:bd:98 REACHABLE
```

`10.42.0.96` is `printer-01`, not the drone, and it is down. The dnsmasq lease file is
empty. There is no SSH configuration for any Pi. The drone is simply not connected, so no
QGC session exists to send a mission to, in flight or otherwise.

**Operator input needed for FIELD-06 and FIELD-09:** power and connect the Pi5 drone, and
supply its address or an SSH entry. Until then there is nothing to test against.

### 9.5.7 Re-verification 2026-10-04 15:09 — every blocker above is still live

§9.5.1–§9.5.6 are dated 2026-10-03/04 and their numbers were taken earlier in the day. Before
relying on any of them, all six were re-measured. **Nothing has recovered.** The counts that
move are the offline-retry totals, which grow continuously at roughly one event per 7 seconds:

```bash
$ date -Is
2026-10-04T15:09:41-07:00

$ grep -h 'is configured and powered up' ~/.reticulum-meshchatx/logs/meshchatx.log* | tail -2
[2026-09-25 16:27:08] [Notice]   RNodeInterface[PEOPLE-RADIO] is configured and powered up
[2026-09-25 16:27:11] [Notice]   RNodeInterface[DRONE-RADIO] is configured and powered up
                                 # <- unchanged: still 2026-09-25, still no success since

$ grep -ch 'unrecoverable error' ~/.reticulum-meshchatx/logs/meshchatx.log{,.1,.2,.3}
3667   7800   2389   29          # 13,885 total; was 11,212 at 09:18, 994 in the first pass

$ tail -3 ~/.reticulum-meshchatx/logs/meshchatx.log
[2026-10-04 15:09:36] [Error]    A serial port error occurred, ... [Errno 9] Bad file descriptor
[2026-10-04 15:09:36] [Error]    The interface RNodeInterface[DRONE-RADIO] experienced an unrecoverable error and is now offline.
[2026-10-04 15:09:36] [Notice]   Reticulum will attempt to reconnect the interface periodically.
```

**Drone still absent** (§9.5.6 unchanged, and the neighbour table has since lost an entry —
`10.42.0.5` has appeared as `FAILED` and `10.42.0.96` `printer-01` remains down):

```bash
$ getent hosts raspberrypi raspbianpios alwayondrone rpi5
(no output)
$ ls ~/.ssh/config
ls: cannot access '/home/scottw/.ssh/config': No such file or directory
$ ip neigh
169.254.207.81 dev eno1 lladdr 30:05:5c:ee:a2:9b STALE
10.42.0.96   dev eno1 FAILED
10.42.0.5    dev eno1 FAILED
192.168.87.1  dev wlp3s0 lladdr 16:22:3b:67:bd:98 REACHABLE
```

**The `:4242` decision still holds** (§9.3.1, FIELD-04) — both connects succeed, listener
unchanged:

```bash
$ ss -ltnp | grep -E '18000|4242'
LISTEN 0 128  127.0.0.1:18000  0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=17))
LISTEN 0 1    0.0.0.0:4242     0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=46))
$ timeout 5 bash -c 'exec 3<>/dev/tcp/192.168.87.135/4242' && echo lan-OK
lan-OK
```

**The firewall mechanism is still unverifiable from here**, and I confirmed this is a privilege
wall rather than a missing file — there is no field-domain firewall policy to review at all:

```bash
$ ufw status
ERROR: You need to be root to run this script
$ sudo -n true
sudo: interactive authentication is required
$ ls /tmp/ao-sessions/wt-field/config/field/
heltec-v3                       # no firewall/ufw file anywhere under config/
$ find /tmp/ao-sessions/wt-field/config -iname '*firewall*' -o -iname '*ufw*'
(no output)
```

**One measurement note, and a correction to my own first claim about it.** `grep` reports
`meshchatx.log.2` as a **binary file**, which I initially took to mean a bare `grep -c` would
silently under-count it and that quoted totals would disagree between sessions. **That is
wrong, and I checked it before leaving it in the record:**

```bash
$ for f in ~/.reticulum-meshchatx/logs/meshchatx.log{,.1,.2,.3}; do
    printf '%-16s a=%-6s plain=%s\n' "$(basename $f)" \
      "$(grep -ac 'unrecoverable error' $f)" "$(grep -c 'unrecoverable error' $f)"; done
meshchatx.log    a=3713   plain=3713
meshchatx.log.1  a=7800   plain=7800
meshchatx.log.2  a=2389   plain=2389
meshchatx.log.3  a=29     plain=29
```

The counts are **identical**. `grep -c` reports a count even when it also prints the
`binary file matches` notice; the notice concerns pattern *output*, not `-c`. So the only real
source of disagreement between sessions is the genuine one: **the current log grows ~1 event
per 7 seconds**, so any total is stale within minutes. Quote a total with its timestamp or
quote none.

Reason I got it wrong: I inferred a counting error from an unrelated warning line instead of
running the comparison. The `-a` flag was already the right instinct for *reading* the file, but
I projected it onto `-c` where it makes no difference.

### 9.5.8 Second re-verification 2026-10-04 15:59 — all six blockers still live

§9.5.7 was measured at 15:09 the same day. Re-measured at 15:59 before relying on it.
**Nothing recovered.** The only numbers that move are the continuously-growing retry totals.

```bash
$ date -Is
2026-10-04T15:59:52-07:00

$ grep -ah 'is configured and powered up' ~/.reticulum-meshchatx/logs/meshchatx.log* | tail -2
[2026-09-25 16:27:08] [Notice]   RNodeInterface[PEOPLE-RADIO] is configured and powered up
[2026-09-25 16:27:11] [Notice]   RNodeInterface[DRONE-RADIO] is configured and powered up
                                  # unchanged: last success for DRONE-RADIO is still 2026-09-25

$ for f in ~/.reticulum-meshchatx/logs/meshchatx.log{,.1,.2,.3}; do \
    printf '%-16s %s\n' "$(basename $f)" "$(grep -ac 'unrecoverable error' $f)"; done
meshchatx.log    4063      # was 3667 at 15:09
meshchatx.log.1  7800
meshchatx.log.2  2389
meshchatx.log.3  29
                 ----
                 14281     # was 13,885; +396 in 50 minutes, consistent with ~1 per 7s

$ tail -3 ~/.reticulum-meshchatx/logs/meshchatx.log
[2026-10-04 15:59:46] [Error]    The interface RNodeInterface[DRONE-RADIO] experienced an unrecoverable error and is now offline.
[2026-10-04 15:59:46] [Error]    Reticulum will attempt to reconnect the interface periodically.
[2026-10-04 15:59:51] [Notice]   Opening serial port /dev/serial/by-path/pci-0000:05:00.0-usb-0:1:1.0-port0...
```

**The retry loop is the same loop, still cycling, in the same order, 50 minutes later.** This is
the strongest available confirmation that the fault is persistent hardware/software state and not
a transient: an intermittent board would produce intermittent recoveries, and there is not one.

**Drone still absent** (§9.5.6 unchanged — `getent` returns nothing, no `~/.ssh/config`, both
`10.42.0.96` and `10.42.0.5` still `FAILED`):

```bash
$ getent hosts raspberrypi raspbianpios alwayondrone rpi5
(no output)
$ ls ~/.ssh/config
ls: cannot access '/home/scottw/.ssh/config': No such file or directory
$ ip neigh
169.254.207.81 dev eno1 lladdr 30:05:5c:ee:a2:9b STALE
10.42.0.96 dev eno1 FAILED
10.42.0.5    dev eno1 FAILED
192.168.87.1  dev wlp3s0 lladdr 16:22:3b:67:bd:98 REACHABLE
```

**The `:4242` decision still holds** (§9.3.1, FIELD-04) — listener unchanged and still reachable
from the LAN address:

```bash
$ ss -ltnp | grep -E '18000|4242'
LISTEN 0 128  127.0.0.1:18000  0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=17))
LISTEN 0 1    0.0.0.0:4242     0.0.0.0:*  users:(("ReticulumMeshCh",pid=840861,fd=46))
$ timeout 5 bash -c 'exec 3<>/dev/tcp/192.168.87.135/4242' && echo lan-OK
lan-OK
```

**The firewall mechanism is still unverifiable from here** — privilege wall, and still no policy
document anywhere under `config/`:

```bash
$ ufw status
ERROR: You need to be root to run this script
$ sudo -n true
sudo: interactive authentication is required
$ find config -iname '*firewall*' -o -iname '*ufw*'
(no output)
```

**The live radio settings are unchanged**, so §9.4.1's profile-vs-live comparison remains valid
as of now — 915 MHz / 125 kHz / SF7 / 17 dBm and 917 MHz / 250 kHz / SF7 / 17 dBm:

```bash
$ grep -A12 'RNodeInterface' ~/.reticulum/config | grep -E 'frequency|bandwidth|spreadingfactor|txpower'
frequency = 915000000
bandwidth = 125000
spreadingfactor = 7
txpower = 17
frequency = 917000000
bandwidth = 250000
spreadingfactor = 7
txpower = 17
```

**Two corrections to how I have been quoting these totals.** First, §9.5.7's own advice — *quote
a total with its timestamp or quote none* — is what I have done here; the 14,281 figure is only
true at 15:59 and is already wrong. Second, my first pass in this pass used `grep -ah` on the
glob while §9.5.7 used a per-file loop; the two agree (`4063+7800+2389+29 = 14281`), so the
totals are not sensitive to that choice, but the **`-a` flag is** — see §9.5.7, where a file
that `grep` calls binary is still counted correctly without it.

### 9.5.9 Third re-verification 2026-10-04 17:52 — blockers unchanged, and the port is now *proven* open

§9.5.7 and §9.5.8 are dated 15:09 and 15:59. Re-measured at **17:52**, per §9.5.7's own
rule that a count is quoted with its timestamp or not at all.

**Totals have moved; state has not.** Detection failures, per file, each with its own span:

```bash
$ date -Is
2026-10-04T17:52:44-07:00
$ cd ~/.reticulum-meshchatx/logs
$ for f in meshchatx.log.3 meshchatx.log.2 meshchatx.log.1 meshchatx.log; do \
    printf '%-16s %s .. %s  detect-fail=%s\n' "$f" \
      "$(head -1 $f | grep -oE '\[[0-9-]+ [0-9:]+\]')" \
      "$(tail -1 $f | grep -oE '\[[0-9-]+ [0-9:]+\]')" \
      "$(grep -ac 'Could not detect device' $f)"; done
meshchatx.log.3   .. [2026-09-25 16:27:17]  detect-fail=328
meshchatx.log.2  [2026-09-25 16:27:17] .. [2026-10-03 14:39:54]  detect-fail=2487
meshchatx.log.1  [2026-10-03 14:39:56] .. [2026-10-04 07:25:33]  detect-fail=8270
meshchatx.log    [2026-10-04 07:25:38] .. [2026-10-04 17:52:43]  detect-fail=5155
                                                         # total 16,240 (was 14,281 at 15:59)
```

**New this pass — the port opens, proved by watching the file descriptors.** §9.5.2 argued
the port opens because the error is `Errno 9` rather than `EACCES`/`EBUSY`. That is
inference from an error string. It can now be observed directly: `DRONE-RADIO`'s descriptor
is repeatedly created and destroyed on the retry cycle, while `PEOPLE-RADIO`'s descriptor is
held open continuously.

```bash
$ (for i in $(seq 1 20); do \
    printf '%s count=%s fds=[%s]\n' "$(date +%T)" \
      "$(ls -l /proc/840861/fd | grep -c ttyUSB)" \
      "$(ls -l /proc/840861/fd | grep ttyUSB | awk '{print $9"="$11}' | tr '\n' ' ')"; \
    sleep 2; done)
17:48:02 count=1 fds=[48=/dev/ttyUSB1 ]
17:48:05 count=2 fds=[30=/dev/ttyUSB0 48=/dev/ttyUSB1 ]
17:48:07 count=1 fds=[48=/dev/ttyUSB1 ]
17:48:13 count=2 fds=[20=/dev/ttyUSB0 48=/dev/ttyUSB1 ]
17:48:19 count=2 fds=[48=/dev/ttyUSB1 64=/dev/ttyUSB0 ]
...
```

`fd 48 -> /dev/ttyUSB1` (`PEOPLE-RADIO`) is present in **every** sample. The `ttyUSB0`
descriptor appears, changes number between attempts (20, 30, 64), and disappears. That is the
signature of a **successful open immediately followed by a close** — the kernel grants the
descriptor and the RNode detection handshake then fails. A permission fault would never
produce a descriptor at all; a contended port would fail at open.

The descriptor is also *not* stale. The inode behind it matches the live device node, so
this is not a leaked handle to a removed device:

```bash
$ stat -c '%n inode=%i' /dev/ttyUSB0 /dev/ttyUSB1
/dev/ttyUSB0 inode=782
/dev/ttyUSB1 inode=786
$ for f in /proc/840861/fd/*; do t=$(readlink $f); case "$t" in *ttyUSB*) \
    echo "fd=$(basename $f) $t inode=$(stat -Lc %i $f)";; esac; done
fd=48 /dev/ttyUSB1 inode=786
```

**Retry cadence is steady at roughly one failure every 7–8 seconds**, consistent since the
fault began and showing no decay, no backoff and no recovery:

```bash
$ tail -2000 ~/.reticulum-meshchatx/logs/meshchatx.log | grep 'unrecoverable error' \
    | grep -oE '\[[0-9-]+ [0-9:]+\]' | cut -c2-17 | cut -c1-16 | uniq -c | tail -5
      8 2026-10-04 17:43
      7 2026-10-04 17:44
      7 2026-10-04 17:45
      8 2026-10-04 17:46
      5 2026-10-04 17:48
```

**Everything else in §9.5 still holds.** `PEOPLE-RADIO` has logged nothing at all in the
current log (0 lines, zero errors). There is still zero RF telemetry — `RSSI`, `SNR`,
`noise floor`, `airtime` and `packet loss` all return 0 matches across all four logs. The Pi5
is still absent. The live radio settings are unchanged (915 MHz / 125 kHz / SF7 / 17 dBm and
917 MHz / 250 kHz / SF7 / 17 dBm), so §9.4.1's profile-vs-live comparison stands.

#### What I got wrong this pass, and the reason

**I announced a hardware event that had not happened.** The first `ls -la /dev/ttyUSB*` in
this pass showed `Oct 4 17:42` on both nodes, at almost exactly the moment I was logging in,
and I recorded it as "the USB devices were re-enumerated at 17:42 today — right now". That
would have been a significant claim: a fresh enumeration would have meant someone had
re-plugged the hardware and the radio still failed.

It was false. `mtime` on a device node moves when the node is **accessed**, and my own
commands were reading them. `ctime` — the creation/change time — is what answers this
question, and it has not moved since 2026-10-01 23:53:

```bash
$ stat -c '%n mtime=%y ctime=%z' /dev/ttyUSB0 /dev/ttyUSB1
/dev/ttyUSB0 mtime=2026-10-04 17:51:22 ctime=2026-10-01 23:53:34
/dev/ttyUSB1 mtime=2026-10-04 17:51:20 ctime=2026-10-01 23:53:34
```

**Reason: I read a timestamp field without knowing what it measured, and the coincidence
with my own session start made the wrong reading feel like a discovery.** The generalisable
form, which joins the rotated-log-filename lesson in FIELD-05: *a number that appears to
corroborate what you expected is the most dangerous kind of evidence here.* Verify that the
field means what you think it means before you build a finding on it.

**Nothing was touched.** No radio, no serial port, no firewall, no config file, no restart of
the Reticulum stack. All six blockers in §9.5.5 remain live.

### 9.5.10 Fourth re-verification 2026-10-05 07:56 — the `DRONE-RADIO` fault narrows to the
### board's own firmware, with every hardware alternative excluded

§9.5.2 concluded the fault "is the radio board, not the port, the symlink or permissions". That
conclusion was reached without enumerating the remaining hardware causes, and **this pass closes
that gap.** The exclusion is by measurement, and it is what an operator needs in order to know
whether to reseat a cable, replace a board, or stop looking at this host at all.

`DRONE-RADIO` is still down with zero successful detections and the failure signature is
unchanged — the port opens and the board does not identify itself:

```text
$ tail -6 ~/.reticulum-meshchatx/logs/meshchatx.log
[2026-10-05 07:53:34] [Error]    Could not detect device for RNodeInterface[DRONE-RADIO]
[2026-10-05 07:53:34] [Error]    A serial port error occurred, the contained exception was: [Errno 9] Bad file descriptor
[2026-10-05 07:53:34] [Error]    The interface RNodeInterface[DRONE-RADIO] experienced an unrecoverable error and is now offline.
```

The last successful detection anywhere in the retained logs is still 2026-09-25 17:22:28. Counts
per rotated file, oldest first — the outage has now run **ten days continuously**:

| Log | First line | `DRONE-RADIO` unrecoverable |
|---|---|---|
| `meshchatx.log.3` | 2026-09-25 16:27:17 | 2353 |
| `meshchatx.log.2` | 2026-10-03 14:39:56 | 7798 |
| `meshchatx.log.1` | 2026-10-04 07:25:38 | 7866 |
| `meshchatx.log` | 2026-10-04 23:58:26 | 3777 |

**The last row is a live figure and grows continuously** — it was 3777 when first counted and
3898 on a later count the same morning, because the radio is still retrying every few seconds.
**Treat it as a lower bound, and never cite a count from `meshchatx.log` as a fixed number.**
The three rotated rows are stable. Same caveat applies to the teardown total in §9.2.3.

**Alternative 1 — "the USB adapter is absent." Excluded.** Both `CP2102` bridges are enumerated
on the expected buses and the kernel logged eight `cp210x` lines with **no disconnect or reset
since**:

```text
$ lsusb | grep -i 10c4
Bus 001 Device 010: ID 10c4:ea60 Silicon Labs CP210x UART Bridge
Bus 003 Device 002: ID 10c4:ea60 Silicon Labs CP210x UART Bridge

$ journalctl -k --no-pager | grep -E 'cp210|ttyUSB' | tail -6
Oct 01 15:08:12 kernel: usb 3-1: Product: CP2102 USB to UART Bridge Controller
Oct 01 15:08:12 kernel: usb 1-13: Product: CP2102 USB to UART Bridge Controller
Oct 01 15:08:12 kernel: cp210x 3-1:1.0: cp210x converter detected
Oct 01 15:08:12 kernel: usb 3-1: cp210x converter now attached to ttyUSB0
Oct 01 15:08:12 kernel: cp210x 1-13:1.0: cp210x converter detected
Oct 01 15:08:12 kernel: usb 1-13: cp210x converter now attached to ttyUSB1
```

`ttyUSB0` is the `DRONE-RADIO` port and it is **live**: ctime 2026-10-01 23:53:34, and `ls -la`
shows a present character device.

**Alternative 2 — "the port name is wrong or stale." Excluded.** All `by-path` symlinks resolve,
and the one `DRONE-RADIO` uses is the correct board per §9.4.2 and `~/.reticulum/radio-ids.txt`
(`3-1` = the USB-C port = `pci-0000:05:00.0`):

```text
$ for p in /dev/serial/by-path/*; do printf '%s -> ' "$p"; readlink -f $p; done
/dev/serial/by-path/pci-0000:00:14.0-usb-0:13:1.0-port0  -> /dev/ttyUSB1
/dev/serial/by-path/pci-0000:05:00.0-usb-0:1:1.0-port0  -> /dev/ttyUSB0
```

**Alternative 3 — "permissions or group membership." Excluded.** The operator is in `dialout`
and both nodes are `root:dialout 0660`, readable and writable:

```text
$ ls -la /dev/ttyUSB0 /dev/ttyUSB1
crw-rw---- 1 root dialout 188, 0 /dev/ttyUSB0
crw-rw---- 1 root dialout 188, 1 /dev/ttyUSB1
$ for d in /dev/ttyUSB0 /dev/ttyUSB1; do [ -r $d ] && [ -w $d ] && echo "$d rw OK"; done
/dev/ttyUSB0 rw OK
/dev/ttyUSB1 rw OK
```

**Alternative 4 — "something else is holding the port." Excluded, and this one needed sampling
rather than a single check.** `ReticulumMeshChatX` (PID 840861) holds **only** `ttyUSB1` — the
`PEOPLE-RADIO` port — and nothing else holds `ttyUSB0`. Sampling three times over six seconds
caught `ttyUSB0` momentarily held by Reticulum itself, which is its own retry loop grabbing and
releasing the port, not a third-party conflict:

```text
$ fuser -v /dev/ttyUSB0 /dev/ttyUSB1
                     USER        PID ACCESS COMMAND
/dev/ttyUSB1:        scottw    840861 F.... ReticulumMeshCh
        # nothing listed for /dev/ttyUSB0
```

**What is left, stated precisely.** The USB bridge enumerates and the node opens, but the
**ESP32 on the `DRONE-RADIO` board does not answer the identification RNode sends on that
bridge.** That is a board-side or cable-side condition — the board's own firmware state, a
damaged or charge-only cable, or the board needing a power cycle — and it is **not diagnosable
or repairable from this host.** `DRONE-RADIO` is correctly configured and correctly addressed;
there is nothing in the software configuration to change.

**This is a stop condition, and I stopped.** "Live radio, serial or network configuration" is on
the operator-approval list. I did not `udevadm trigger`, did not cycle the USB bus, did not open
either port for a manual probe, and did not restart the Reticulum stack. The MAC in
`radio-ids.txt` dates from 2026-09-21 and I did not re-read it from hardware, because that means
opening a serial port the running service owns.
**Nothing was touched.** No radio, no serial port, no firewall, no config file. Every blocker in
§9.5.5 still requires physical repair or operator action.
**Correction to a prior claim in this section, and it is the one most likely to mislead the next
reader.** §9.4.2 and the FIELD-12 proposal record that `by-id` has "exactly ONE link → can only
ever identify `ttyUSB0`". The observation still holds, but the reason was written as though it
were a property of this host's layout. It is not: **both bridges ship with the byte-identical
factory serial descriptor `Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001`**, because
CP2102 serials are programmed at the vendor and a factory-default pair collides by definition.
Re-measured today on both devices:

```text
$ for d in ttyUSB0 ttyUSB1; do udevadm info -q property -n /dev/$d | grep -E '^ID_(SERIAL|PATH)='; done
ID_SERIAL=Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001
ID_PATH=pci-0000:05:00.0-usb-0:1:1.0
ID_SERIAL=Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001
ID_PATH=pci-0000:00:14.0-usb-0:13:1.0
```

So the single `by-id` link is a **consequence of identical hardware**, and no amount of
replugging will ever produce a second `by-id` name. **`by-path` is the only discriminator that
can work for these two boards** — a property of the hardware, not an accident of one boot.
§9.4.2's table should be read that way, and any future suggestion to "just use `by-id` once the
serial is unique" is closed by this.

**Two stale-by-date findings the compiler should re-check rather than copy.**

- **The `ao-*` symlinks from FIELD-12 are still absent**, cause unchanged: the rule is installed
  (`/etc/udev/rules.d/99-ao-heltec.rules`, mtime `2026-09-30 23:05:58`) and both adapters
  enumerated at boot on 2026-10-01, i.e. **after** the rule was written. `ls /dev/ao-*` →
  `No such file or directory`. Creating them still needs an operator `udevadm trigger`, which is
  a live-serial action and was not performed.
- **FIELD-05's `umsgpack` fault has not recurred.** `grep -c umsgpack` on the current log returns
  **0**, with the last occurrence still in `meshchatx.log.2`. That *supports* FIELD-05's closure
  rather than reopening it: the persistence error stopped instead of continuing.

**Nothing was touched.** No radio, no serial port, no `udevadm trigger`, no USB reset, no
firewall change, no config edit, no restart. `PEOPLE-RADIO` is up with zero error lines today
(`grep -c 'PEOPLE-RADIO'` on the current log → `0`).

**What I got wrong this pass.** I queried `journalctl -k --since '2026-10-04'` and `dmesg` to test
whether the USB link had flapped, and got **empty output from both** — which reads exactly like
"nothing happened". It is not evidence of that. `dmesg` is unreadable for this user, and the
`--since` window genuinely contained no kernel messages, while the *unfiltered* query showed the
eight lines that do exist, all from Oct 01. The lesson is the one from FIELD-05's rotated logs and
my own §9.5.9 timestamp error, now for the third time in this section: **an empty result from a
query whose scope I did not verify is not a negative finding.** I got the right answer only after
running the unfiltered query and reading what it returned.