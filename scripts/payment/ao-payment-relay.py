#!/usr/bin/env python3
"""ALWAYS ON - host-side relay for ao-ingress-payment (README Section 7.2).

ao-payment is Internal=true, so the adapter has no route to the public
internet. Public provider webhooks therefore terminate at the host (Cloudflare
Tunnel) and this relay forwards them into the domain.

This mirrors the ao-fabrication-collect pattern in reverse (Section 3.3.0):
the host performs the hop that the internal domain cannot, then hands the data
in. It exists so the adapter keeps its own domain and joins no second network.

Binds loopback only. It never listens on a LAN or public address, and it never
relays anywhere except the adapter's fixed in-domain address.
"""
from __future__ import annotations

import argparse
import http.client
import logging
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

# The adapter's address. Rootless Podman gives the host no route into an
# Internal=true network, so ao-ingress-payment publishes 127.0.0.1:8899 (the
# same loopback pattern as ao-sales-db and ao-fabrication-db). This constant is
# never derived from an inbound request, so a caller cannot redirect the relay.
ADAPTER_HOST = "127.0.0.1"
ADAPTER_PORT = 8899  # loopback-published from ao-ingress-payment


def resolve_adapter() -> str:
    """Adapter address. Fixed to loopback; see the container unit's comment.

    Rootless Podman provides no host route into an Internal=true network, so
    the adapter publishes 127.0.0.1:8899 instead. This is a constant, never
    derived from an inbound request, so a caller cannot redirect the relay.
    """
    return ADAPTER_HOST
# Cap relayed bodies; the adapter enforces its own limit too.
MAX_BODY = 256 * 1024
log = logging.getLogger("ao-payment-relay")


class Relay(BaseHTTPRequestHandler):
    server_version = "ao-payment-relay"

    def log_message(self, fmt, *a):
        log.info(fmt % a)

    def _forward(self, body: bytes, headers: dict) -> tuple[int, bytes]:
        adapter_host = resolve_adapter()
        # Only signature-relevant headers are forwarded; hop-by-hop headers
        # and anything client-supplied that could confuse the adapter are not.
        keep = {
            k: v for k, v in headers.items()
            if k.lower().startswith("paypal-transmission")
            or k.lower() in ("content-type", "coinbase-signature")
        }
        conn = http.client.HTTPConnection(adapter_host, ADAPTER_PORT, timeout=15)
        try:
            conn.request("POST", self.path, body=body, headers=keep)
            r = conn.getresponse()
            return r.status, r.read()
        finally:
            conn.close()

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            self.send_error(400, "bad length")
            return
        body = self.rfile.read(length)
        try:
            status, payload = self._forward(body, dict(self.headers))
        except Exception as exc:  # noqa: BLE001
            # Never surface internal detail to the caller.
            log.error("relay failed: %s", type(exc).__name__)
            self.send_error(503, "adapter unavailable")
            return
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        adapter_host = resolve_adapter()
        conn = http.client.HTTPConnection(adapter_host, ADAPTER_PORT, timeout=10)
        try:
            conn.request("GET", "/health")
            r = conn.getresponse()
            payload = r.read()
        except Exception:  # noqa: BLE001
            self.send_error(503, "adapter unavailable")
            return
        finally:
            conn.close()
        self.send_response(r.status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> int:
    ap = argparse.ArgumentParser(description="ao-ingress-payment host relay")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8900)
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        log.info("relay %s:%s -> %s:%s (%s)", args.host, args.port,
                 ADAPTER_HOST, ADAPTER_PORT)
    except Exception as exc:  # noqa: BLE001
        log.warning("adapter not resolvable yet (%s); will retry per request",
                    type(exc).__name__)
    HTTPServer((args.host, args.port), Relay).serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
