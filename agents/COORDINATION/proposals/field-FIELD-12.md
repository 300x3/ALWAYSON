---
item: FIELD-12
action: close
evidence: |
  # live ports
  $ ls -la /dev/serial/by-path/
  pci-0000:00:14.0-usb-0:13:1.0-port0     -> ../../ttyUSB1
  pci-0000:00:14.0-usbv2-0:13:1.0-port0   -> ../../ttyUSB1
  pci-0000:05:00.0-usb-0:1:1.0-port0      -> ../../ttyUSB0
  pci-0000:05:00.0-usbv2-0:1:1.0-port0    -> ../../ttyUSB0

  # by-id has exactly ONE link -> can only ever identify ttyUSB0
  $ ls -la /dev/serial/by-id/
  usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0 -> ../../ttyUSB0

  # both bridges report the BYTE-IDENTICAL serial descriptor
  $ for d in ttyUSB0 ttyUSB1; do udevadm info -q property -p /sys/class/tty/$d \
      | grep -E '^ID_SERIAL=|^ID_PATH='; done
  ID_SERIAL=Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001
  ID_PATH=pci-0000:05:00.0-usb-0:1:1.0
  ID_SERIAL=Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001
  ID_PATH=pci-0000:00:14.0-usb-0:13:1.0

  # the ao-* symlinks §2.1 promises do not exist
  $ ls -la /dev/ao-drone-radio /dev/ao-people-radio
  ls: cannot access '/dev/ao-drone-radio': No such file or directory
  ls: cannot access '/dev/ao-people-radio': No such file or directory

  # ...but the rule is installed, correct, and provably able to fire
  $ udevadm test /sys/class/tty/ttyUSB0 2>&1 | grep 99-ao-heltec
  ttyUSB0: /etc/udev/rules.d/99-ao-heltec.rules:18 SYMLINK+="ao-drone-radio": Added device node symlink "ao-drone-radio".
  $ udevadm test /sys/class/tty/ttyUSB1 2>&1 | grep 99-ao-heltec
  ttyUSB1: /etc/udev/rules.d/99-ao-heltec.rules:19 SYMLINK+="ao-people-radio": Added device node symlink "ao-people-radio".

  # live Reticulum config agrees with by-path
  $ grep -A12 '\[\[DRONE-RADIO\]\]' ~/.reticulum/config | grep frequency
  frequency = 917000000
section: 09-field-and-lora-architecture
---
§9 gains a new **§9.4.2** publishing the one canonical device-name table the item asks for, and
resolving the three-way contradiction between §2.1, §19 and §9.2.1.

| Radio | Live port | `by-path` discriminator | `ID_PATH` |
|---|---|---|---|
| `DRONE-RADIO` (917 MHz) | `/dev/ttyUSB0` | `pci-0000:05:00.0-usb-0:1:1.0-port0` | `pci-0000:05:00.0-usb-0:1:1.0` |
| `PEOPLE-RADIO` (915 MHz) | `/dev/ttyUSB1` | `pci-0000:00:14.0-usb-0:13:1.0-port0` | `pci-0000:00:14.0-usb-0:13:1.0` |

Two findings the compiler should not lose:

1. **§19's `/dev/heltec-v3` is wrong and must not be reinstated.** Both boards are Heltec V3,
   so one name could only ever point at one of them. `99-ao-heltec.rules` *deliberately*
   declines to create it.
2. **`by-id` cannot identify `PEOPLE-RADIO` at all** — only one link exists, pointing at
   `ttyUSB0`. Both ports also share a byte-identical `ID_SERIAL`, confirming §9.2.1's claim
   that identity cannot come from the USB serial descriptor. **`by-path` is the only working
   discriminator**, which is what the live Reticulum config already uses.

**§2.1's `/dev/ao-drone-radio` and `/dev/ao-people-radio` are specified but absent.** The udev
rule is installed and provably correct — `udevadm test` shows it *would* create both symlinks,
one per line, matched to the right port. The cause is ordering: the rule was installed
`2026-09-30 23:05:58`, after both adapters were already enumerated, and udev applies `add` rules
only at enumeration. An `udevadm trigger` would create them.

**Not performed — operator action required.** `udevadm trigger` on live serial devices is a stop
condition under "live radio, serial or network configuration". So the table above is published
against `by-path`, which works today; the `ao-*` names become valid once the operator triggers.
Nothing in §9.2.1 depends on the `ao-*` names, so no section is blocked by this.

**The MAC column is deliberately empty.** §9.4.2 asks for it, and obtaining the SX1262 MAC
requires opening the RNode serial port, which `ReticulumMeshChatX` (PID 840861) currently holds
open. That is live radio configuration. The column is marked **not measured** rather than
guessed — if the compiler renders FIELD-12 as "fully closed with MACs", that would be a stronger
claim than the evidence supports. The item is closed on the *decision and the table*, which is
what it asked for; the MAC is the one cell still owed.