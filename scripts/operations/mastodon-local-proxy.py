#!/usr/bin/env python3
# ALWAYS ON - scripts/operations/mastodon-local-proxy.py
# Loopback-only TLS-terminating reverse proxy so the Mastodon local UI opens
# over HTTPS without a browser certificate error beyond the first acceptance.
#
# Why this exists. mastodon-web runs RAILS_ENV=production and upstream hardcodes
#   config/environments/production.rb:  config.force_ssl = true
#   config/initializers/1_hosts.rb:     https = Rails.env.production? || ...
# Neither is switchable by environment variable, so Rails *always* generates
# absolute "https://..." asset URLs (config.x.use_https is true in production).
# A plain-HTTP listener therefore produces a page that loads its own HTML but
# then asks the browser for "https://127.0.0.1:3300/custom.css" on a port with
# no TLS listener: the handshake never completes, the stylesheet stays pending
# forever, and because it is render-blocking DOMContentLoaded never fires. The
# symptom is a page that looks slow/unstable while curl reports every URL as
# fast. Puma logged the cause directly: "Are you trying to open an SSL
# connection to a non-SSL Puma?" - the handshake bytes were being piped
# straight through to Puma.
#
# Fix: terminate TLS here, on loopback only. Then
#   1. the "https://127.0.0.1:3300/..." URLs Rails generates actually resolve,
#      so the render-blocking stylesheet completes and the page paints at once;
#   2. X-Forwarded-Proto: https is still injected so Rails keeps generating
#      https URLs that match this listener (removing it would cause a redirect
#      loop back to :3000);
#   3. upstream stays plain HTTP on 127.0.0.1:3000, so mastodon-web is not
#      modified and federation through the Cloudflare Tunnel is untouched.
#
# Controls (README 4.1 rule 4/6):
#   - binds 127.0.0.1 only, so no public port is exposed;
#   - the certificate is self-signed for 127.0.0.1/localhost and lives under
#     /ALWAYSON/secrets/, which is git-ignored;
#   - touches no Mastodon config, credentials, or data.
#
# Usage: python3 mastodon-local-proxy.py [listen_port] [target_port] [cert] [key]
import os
import socket
import ssl
import sys
import threading

LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3300
TARGET = ("127.0.0.1", int(sys.argv[2]) if len(sys.argv) > 2 else 3000)
CERT = sys.argv[3] if len(sys.argv) > 3 else "/ALWAYSON/secrets/mastodon/mastodon-local.crt"
KEY = sys.argv[4] if len(sys.argv) > 4 else "/ALWAYSON/secrets/mastodon/mastodon-local.key"
INJECT = b"X-Forwarded-Proto: https"
FORCE_CLOSE = b"Connection: close"
HEAD_TIMEOUT = 30  # only for reading the request head; cleared before piping


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
        # Bound the head read. Without this a peer that opens a connection and
        # sends nothing (or sends bytes that never contain CRLFCRLF) parks this
        # thread and its socket forever.
        client.settimeout(HEAD_TIMEOUT)
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
        # Clear the head timeout before streaming: WebSocket connections to the
        # Mastodon streaming API are legitimately idle for long stretches, and
        # a timeout here would sever live timelines.
        client.settimeout(None)
        upstream.settimeout(None)
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


def tls_context():
    for path in (CERT, KEY):
        if not os.path.exists(path):
            sys.exit("TLS material missing: %s" % path)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile=CERT, keyfile=KEY)
    return ctx


def main():
    ctx = tls_context()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_HOST, LISTEN_PORT))
    server.listen(64)
    sys.stderr.write(
        "mastodon-local-proxy: https://%s:%d -> http://%s:%d (loopback only, self-signed)\n"
        % (LISTEN_HOST, LISTEN_PORT, TARGET[0], TARGET[1])
    )
    while True:
        conn, _ = server.accept()
        # Handshake per connection so a bad or aborted handshake closes only
        # that socket instead of killing the listener.
        try:
            tls_conn = ctx.wrap_socket(conn, server_side=True)
        except (ssl.SSLError, OSError) as exc:
            sys.stderr.write("proxy: TLS handshake failed: %s\n" % exc)
            try:
                conn.close()
            except OSError:
                pass
            continue
        threading.Thread(target=handle, args=(tls_conn,), daemon=True).start()


if __name__ == "__main__":
    main()
