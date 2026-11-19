#!/usr/bin/env python3
"""ALWAYS ON Field Gateway (ao-field-gateway) — ST-22.

Handles USB serial LoRa frames from Heltec V3 RNodes,
normalizes telemetry into manifests, and spools raw packets.

DRONE-RADIO on /dev/ao-drone-radio (ttyUSB0)
PEOPLE-RADIO on /dev/ao-people-radio (ttyUSB1)

Usage:
    field-gateway.py --plan        # Validate config, no serial access
    field-gateway.py               # Run gateway (reads serial frames)
"""

from __future__ import annotations

import json
import os
import pathlib
import select
import signal
import time
import uuid

import termios

from common import ao_log, ao_now_utc, ao_lock, AO_ROOT

DRONE_RADIO = os.environ.get("GATEWAY_DRONE_RADIO", "/dev/ao-drone-radio")
PEOPLE_RADIO = os.environ.get("GATEWAY_PEOPLE_RADIO", "/dev/ao-people-radio")
CONFIG_DIR = os.environ.get("GATEWAY_CONFIG_DIR", "/ALWAYSON/config/field")
SPOOL_DIR = os.environ.get("GATEWAY_SPOOL_DIR", "/ALWAYSON/data/field")
BAUDRATE = 115200
def load_radio_profile(path: str) -> dict:
    import yaml
    with open(path, "r") as f:
        return yaml.safe_load(f)


def open_serial(port: str) -> int:
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    attrs = termios.tcgetattr(fd)
    attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK
                  | termios.ISTRIP | termios.INLCR | termios.IGNCR
                  | termios.ICRNL | termios.IXON)
    attrs[1] &= ~termios.OPOST
    attrs[2] &= ~(termios.CSIZE | termios.PARENB)
    attrs[2] |= termios.CS8
    attrs[3] &= ~(termios.ECHO | termios.ECHONL | termios.ICANON
                  | termios.ISIG | termios.IEXTEN)
    attrs[6][termios.VMIN] = 1
    attrs[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    termios.tcflush(fd, termios.TCIOFLUSH)
    termios.cfsetspeed(fd, BAUDRATE)
    return fd


def read_frame(fd: int, timeout_s: float = 1.0) -> bytes | None:
    deadline = time.monotonic() + timeout_s
    buf = bytearray()
    while time.monotonic() < deadline:
        try:
            data = os.read(fd, 64)
        except BlockingIOError:
            data = b""
        except OSError:
            return None
        if not data:
            time.sleep(0.01)
            continue
        buf.extend(data)
        if len(buf) >= 4:
            frame_len = (buf[0] << 8) | buf[1]
            if 4 <= frame_len <= 226:
                if len(buf) >= frame_len:
                    frame = bytes(buf[:frame_len])
                    del buf[:frame_len]
                    return frame
    return None

def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
            crc &= 0xFFFF
    return crc


def parse_frame(frame: bytes, radio_id: str) -> dict | None:
    if len(frame) < 4:
        return None
    frame_len = (frame[0] << 8) | frame[1]
    if len(frame) != frame_len or frame_len < 4:
        return None
    payload = frame[2:-2]
    crc_stored = frame[-2] | (frame[-1] << 8)
    crc_calc = crc16_ccitt(payload)
    if crc_stored != crc_calc:
        return None
    return {
        "radio_id": radio_id,
        "frame_len": frame_len,
        "payload_hex": payload.hex(),
        "payload_len": len(payload),
        "crc16": f"0x{crc_stored:04x}",
        "received_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def write_raw_packet(frame: bytes, radio_id: str) -> None:
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    fname = f"{ts}_{radio_id}_{uuid.uuid4().hex[:8]}.bin"
    fpath = pathlib.Path(SPOOL_DIR) / fname
    fpath.write_bytes(frame)


def write_manifest(parsed: dict) -> None:
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    fname = f"{ts}_{parsed['radio_id']}_manifest.json"
    fpath = pathlib.Path(SPOOL_DIR) / fname
    manifest = {
        "manifest_id": str(uuid.uuid4()),
        "object_type": "telemetry_batch",
        "origin_domain": "field",
        "created_at_utc": parsed["received_at_utc"],
        "schema_version": "1.0",
        "radio_id": parsed["radio_id"],
        "frame_len": parsed["frame_len"],
        "payload_len": parsed["payload_len"],
        "payload_hex": parsed["payload_hex"],
        "crc16": parsed["crc16"],
    }
    fpath.write_text(json.dumps(manifest, indent=2) + "\n")

def validate_config() -> bool:
    ok = True

    profile_paths = [
        pathlib.Path(CONFIG_DIR) / "heltec-v3" / "radio-profile-us915.yaml",
        pathlib.Path("/ALWAYSON/config/drone/waveshare-lora/radio-profile-us915.yaml"),
    ]
    for profile_path in profile_paths:
        if not profile_path.exists():
            ao_log("ERROR", f"radio profile missing: {profile_path}")
            ok = False
        else:
            ao_log("INFO", f"radio profile OK: {profile_path}")

    for port, label in ((DRONE_RADIO, "DRONE-RADIO"),
                        (PEOPLE_RADIO, "PEOPLE-RADIO")):
        if os.path.exists(port):
            ao_log("INFO", f"serial path OK: {label} -> {port}")
        else:
            ao_log("ERROR", f"serial path missing: {label} -> {port}")
            ok = False

    pathlib.Path(SPOOL_DIR).mkdir(parents=True, exist_ok=True)
    ao_log("INFO", f"spool dir: {SPOOL_DIR}")

    return ok


def run_gateway() -> int:
    try:
        import yaml
    except ImportError:
        ao_log("ERROR", "PyYAML not installed — cannot load radio profiles")
        return 1

    profiles = {}
    for name, path in (
        ("drone", pathlib.Path(CONFIG_DIR) / "heltec-v3" / "radio-profile-us915.yaml"),
        ("people", pathlib.Path("/ALWAYSON/config/drone/waveshare-lora/radio-profile-us915.yaml")),
    ):
        if path.exists():
            profiles[name] = load_radio_profile(str(path))
        else:
            ao_log("WARN", f"radio profile missing: {path}")

    fds = {}
    for port, label in ((DRONE_RADIO, "drone"),
                        (PEOPLE_RADIO, "people")):
        try:
            fd = open_serial(port)
            fds[fd] = label
            ao_log("INFO", f"opened serial {label}: {port}")
        except OSError as e:
            ao_log("ERROR", f"cannot open serial {label} {port}: {e}")
            return 1

    if not fds:
        ao_log("ERROR", "no serial ports opened")
        return 1

    running = True

    def handle_signal(signum, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    ao_log("INFO", "field gateway running — reading serial frames")

    while running:
        readable, _, _ = select.select(list(fds.keys()), [], [], 1.0)
        for fd in readable:
            label = fds[fd]
            frame = read_frame(fd)
            if frame is None:
                continue
            parsed = parse_frame(frame, label)
            if parsed is None:
                continue
            write_raw_packet(frame, label)
            write_manifest(parsed)

    for fd in fds:
        try:
            os.close(fd)
        except OSError:
            pass

    ao_log("INFO", "field gateway stopped")
    return 0


def main() -> int:
    if "--plan" in sys.argv or "--help" in sys.argv or "-h" in sys.argv:
        if validate_config():
            print("OK: field-gateway config valid — ready for serial access")
            return 0
        else:
            print("ERROR: field-gateway config validation failed")
            return 1
    return run_gateway()


if __name__ == "__main__":
    sys.exit(main())

