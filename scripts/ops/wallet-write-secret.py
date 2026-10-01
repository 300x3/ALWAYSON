#!/usr/bin/env python3
"""Write one KDE Wallet password. Never logs the value."""
import dbus
import sys


def main() -> int:
    if len(sys.argv) != 5:
        print("usage: wallet-write-secret.py <wallet> <folder> <key> <value>",
              file=sys.stderr)
        return 2
    wallet, folder, key = sys.argv[1:4]
    value = sys.argv[4]
    if not value:
        print("refusing to write an empty value", file=sys.stderr)
        return 3
    app = "alwayson-secret-writer"
    try:
        bus = dbus.SessionBus()
        api = dbus.Interface(
            bus.get_object("org.kde.kwalletd6", "/modules/kwalletd6"),
            "org.kde.KWallet",
        )
        handle = int(api.open(wallet, dbus.Int64(0), app))
        if handle < 0:
            print("wallet unavailable or locked", file=sys.stderr)
            return 4
        try:
            api.writePassword(handle, folder, key, value, app)
        finally:
            try:
                api.close(handle, False, app)
            except Exception:
                pass
        print(f"OK: wrote {folder}/{key} (value not shown)")
        return 0
    except Exception as exc:
        print(f"wallet write failed: {type(exc).__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
