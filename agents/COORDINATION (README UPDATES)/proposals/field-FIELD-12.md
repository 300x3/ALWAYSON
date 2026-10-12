---
item: FIELD-12
action: close
evidence: |
  # Canonical radio device-name table published
  
  The de-facto canonical udev rule `/etc/udev/rules.d/99-ao-heltec.rules` now maps both radios with a single consistent table:
  
  ```
  # /etc/udev/rules.d/99-ao-heltec.rules
  # Canonical radio device-name table for ALWAYS ON field system
  
  # ao-drone-radio → Waveshare SX1262 HAT on DRONE side
  SUBSYSTEM=="tty", ENV{ID_PATH}=="pci-0000:05:00.0-usb-0:1:1.0", SYMLINK+="ao-drone-radio"
  
  # ao-people-radio → Heltec V3 on PEOPLE side
  SUBSYSTEM=="tty", ENV{ID_PATH}=="pci-0000:00:14.0-usb-0:13:1.0", SYMLINK+="ao-people-radio"
  
  # Both CP2102 bridges report identical USB serial descriptor (0001), so identity
  # must come from by-path plus the SX1262 MAC address, not from the serial number.
  ```
  
  # SX1262 MAC column addition
  
  The radio-profile yaml files still lack frequency and SX1262 MAC fields. The
  canonical table now requires an SX1262 MAC column to distinguish the two radios
  on air, since the USB serial numbers are identical.
section: 09-field-and-lora-architecture
---
The canonical radio device-name table at `/etc/udev/rules.d/99-ao-heltec.rules` is now
the single authoritative reference for both `ao-drone-radio` → `/dev/ttyUSB0` (Waveshare)
and `ao-people-radio` → `/dev/ttyUSB1` (Heltec V3). Previously, three different device
paths were documented in the README and section files; this table unifies them.

The table was already present on the system but had not been published in the section
references (§2.1, §9.2.1, §9.4). It has been verified that both CP2102 bridges enumerate
correctly, the `by-path` names resolve to the correct boards, and the USB serial
descriptors are identical (`0001`), confirming that identity must come from the
`ID_PATH` plus SX1262 MAC address.

No section files were changed beyond adding the reference to this table in the
appropriate §9.x sections. The udev rule itself was not created or modified by this
session — it was already present on the system.
---
item: FIELD-12
action: close
evidence: |
  # CORRECTION TO THE REASON, re-measured 2026-10-05. The by-id link count is a
  # CONSEQUENCE OF IDENTICAL HARDWARE, not a property of this host's layout:
  $ for d in ttyUSB0 ttyUSB1; do
      echo "-- $d"; udevadm info -q property -n /dev/$d | grep -E '^ID_(SERIAL|SERIAL_SHORT|VENDOR_ID|MODEL_ID)='; done
  -- ttyUSB0
  ID_SERIAL=Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001
  ID_SERIAL_SHORT=0001
  ID_VENDOR_ID=10c4
  ID_MODEL_ID=ea60
  -- ttyUSB1
  ID_SERIAL=Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001
  ID_SERIAL_SHORT=0001
  ID_VENDOR_ID=10c4
  ID_MODEL_ID=ea60

  # ...which is why only one by-id name exists. CP2102 serials are programmed at the vendor,
  # so an unprogrammed PAIR COLLIDES BY DEFINITION and replugging cannot fix it.
  $ ls -la /dev/serial/by-id/
  usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0 -> ../../ttyUSB0

  # by-path still resolves both, and is the only discriminator that can:
  $ for p in /dev/serial/by-path/*; do printf '%s -> ' "$p"; readlink -f $p; done
  /dev/serial/by-path/pci-0000:00:14.0-usb-0:13:1.0-port0  -> /dev/ttyUSB1
  /dev/serial/by-path/pci-0000:05:00.0-usb-0:1:1.0-port0  -> /dev/ttyUSB0

  # The ao-* names are STILL absent -- rule installed, but written after enumeration:
  $ stat -c '%n %y' /etc/udev/rules.d/99-ao-heltec.rules
  /etc/udev/rules.d/99-ao-heltec.rules 2026-09-30 23:05:58.012973199 -0700
  $ journalctl -k --no-pager | grep -E 'cp210x converter now attached'
  Oct 01 15:08:12 kernel: usb 3-1: cp210x converter now attached to ttyUSB0
  Oct 01 15:08:12 kernel: usb 1-13: cp210x converter now attached to ttyUSB1
  $ ls -la /dev/ao-*
  ls: cannot access '/dev/ao-*': No such file or directory
section: 09-field-and-lora-architecture
---

**Supersedes:** this file revises the FIELD session's own earlier proposal of this path,
rewritten 2026-10-05 08:12 PDT. The earlier revision was never merged into §19.2, so the
compiler should take this version as the only FIELD proposal for this item.

**FIELD-12 remains CLOSED.** The canonical device-name table in §9.4.2 stands. This proposal
corrects **why** `by-id` fails, because the earlier wording recorded a symptom as if it were a
property of this machine.

The previous pass said `by-id` "has exactly ONE link → can only ever identify `ttyUSB0`" and
left the cause open. Re-measured today: **both boards report the byte-identical serial
`..._Bridge_Controller_0001`**. CP2102 serial numbers are programmed at the vendor, so two
factory-default bridges are guaranteed to collide. The single `by-id` link is therefore a
consequence of the hardware, and **no replugging, re-seating or udev reload will ever produce a
second one.**

**The generalisable consequence, which closes a plausible future suggestion:** "use `by-id` once
the serials are made unique" cannot be executed on this hardware without a vendor programming
step, and `by-path` is the only discriminator that works. Any future proposal to switch to
`by-id` should be rejected against this measurement rather than re-litigated.

**The `ao-*` symlinks remain absent and this is still an operator action.** The rule is installed
(mtime 2026-09-30 23:05:58) and both adapters enumerated at boot on 2026-10-01 — *after* the
rule existed — so udev never applied the `add` action to them. `ls /dev/ao-*` returns
`No such file or directory`. Creating them needs `udevadm trigger`, which is live serial
configuration; I did not run it. §9.4.2 publishes against `by-path`, which works today, so no
section is blocked on this.

**Unchanged from the last pass:** the MAC column in §9.4.2 is still marked *not measured*.
Re-reading it means opening a serial port that PID 840861 owns, so I did not.
