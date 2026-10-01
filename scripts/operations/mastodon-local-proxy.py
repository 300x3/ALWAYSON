#!/usr/bin/env python3
# ALWAYS ON - scripts/operations/mastodon-local-proxy.py
# Loopback-only reverse proxy so the Mastodon local UI opens over plain HTTP.
# Problem: mastodon-web enforces RAILS_FORCE_SSL=true and answers
#   http://127.0.0.1:3000/ with "301 -> https://127.0.0.1:3000/" but no TLS
#   listener exists on 3000, so a browser gets SSL_ERROR_UNKNOWN.
# Fix: forward loopback:3300 -> loopback:3000 and inject
#   "X-Forwarded-Proto: https" so Rack/Rails treats the request as already
#   HTTPS and serves content instead of redirecting (verified 200 via curl).
# Controls: binds 127.0.0.1 only (no public port, README 4.1 rule 6/4);
#   forces Connection: close so every request carries the injected header;
#   touches no Mastodon config, credentials, or data.
# Usage: python3 mastodon-local-proxy.py [listen_port] [target_port]
import socket
import sys
import threading

LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3300
TARGET = ("127.0.0.1", int(sys.argv[2]) if len(sys.argv) > 2 else 3000)
INJECT = b"X-Forwarded-Proto: https"
FORCE_CLOSE = b"Connection: close"


def pipe(src, dst):
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except OSError:
        pass
    finally:
        try:
            dst.shutdown(socket.SHUT_WR)
        except OSError:
            pass


def handle(client):
    upstream = None
    try:
        head = b""
        while b"\r\n\r\n" not in head:
            chunk = client.recv(4096)
            if not chunk:
                client.close()
                return
            head += chunk
            if len(head) > 65536:
                client.close()
                return
        head, remainder = head.split(b"\r\n\r\n", 1)
        lines = head.split(b"\r\n")
        kept = [lines[0]]
        for line in lines[1:]:
            if line.lower().startswith(b"connection:"):
                continue  # replaced below so the header is carried every request
            kept.append(line)
        kept.insert(1, INJECT)
        kept.insert(2, FORCE_CLOSE)
        upstream = socket.create_connection(TARGET, timeout=30)
        upstream.sendall(b"\r\n".join(kept) + b"\r\n\r\n" + remainder)
        t = threading.Thread(target=pipe, args=(upstream, client), daemon=True)
        t.start()
        pipe(client, upstream)
        t.join(timeout=5)
    except OSError as exc:
        sys.stderr.write("proxy: %s\n" % exc)
    finally:
        for sock in (client, upstream):
            if sock is not None:
                try:
                    sock.close()
                except OSError:
                    pass


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_HOST, LISTEN_PORT))
    server.listen(64)
    sys.stderr.write(
        "mastodon-local-proxy: %s:%d -> %s:%d (loopback only)\n"
        % (LISTEN_HOST, LISTEN_PORT, TARGET[0], TARGET[1])
    )
    while True:
        conn, _ = server.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()
