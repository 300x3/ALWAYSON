#!/usr/bin/env python3
"""Read one KDE Wallet password without exposing metadata or values in logs."""
import dbus
import sys


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: wallet-read-secret.py <wallet> <folder> <key>", file=sys.stderr)
        return 2
    wallet, folder, key = sys.argv[1:4]
    app = "alwayson-secret-consumer"
    try:
        bus = dbus.SessionBus()
        wallet_api = dbus.Interface(
            bus.get_object("org.kde.kwalletd6", "/modules/kwalletd6"),
            "org.kde.KWallet",
        )
        handle = int(wallet_api.open(wallet, dbus.Int64(0), app))
        try:
            if handle < 0 or not bool(wallet_api.hasEntry(handle, folder, key, app)):
                print("wallet entry unavailable", file=sys.stderr)
                return 3
            value = str(wallet_api.readPassword(handle, folder, key, app))
        finally:
            try:
                wallet_api.close(handle, False, app)
            except Exception:
                pass
        if not value:
            print("wallet entry unavailable", file=sys.stderr)
            return 3
        sys.stdout.write(value)
        return 0
    except Exception as exc:
        print(f"wallet read failed: {type(exc).__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
