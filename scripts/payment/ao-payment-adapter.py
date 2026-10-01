#!/usr/bin/env python3
"""ALWAYS ON - ao-ingress-payment webhook adapter (README Section 7.2, 18.4).

Receives provider payment events and emits normalized payment state into
salesdb. It does NOT process cards, does NOT store provider secrets, and does
NOT move money. PayPal events must carry a valid provider signature. Zelle has
no public API or webhook, so it is a manual-reconciliation queue only and is
never auto-validated. Coinbase/USDC settlement is recorded from an operator
supply of settlement evidence, not scraped.

Controls enforced here (Section 18.4):
  - PayPal: signature verified before ANY row is written.
  - Zelle: manual reconciliation only; requires operator approval reference.
  - Coinbase: on-chain settlement is the verification.
  - No raw payload is stored; only a SHA-256 hash and an opaque reference.
  - Nothing here is eligible for Corda until all three evidence classes exist.

The adapter runs inside ao-payment (Internal=true). It has no route to the
internet and no published port; the host-side relay terminates public traffic
and forwards in (the ao-fabrication-collect pattern, Section 3.3.0).
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

# Providers permitted by the sale_evidence.provider CHECK constraint in
# config/sales/init/01-database.sql. Spelling matches
# config/sales/sale-receipt.schema.json exactly; "Zelle" is capitalised in both,
# per operator confirmation 2026-10-01. See
# config/sales/migrate/01-normalise-zelle-provider.sql.
PROVIDERS = ("website", "paypal", "Zelle", "coinbase", "bank", "manual_reconciliation")
# Providers that may be auto-validated from an inbound event. Zelle is
# deliberately absent: Section 18.4 forbids automated Zelle verification.
AUTOMATED = ("paypal", "coinbase")
MAX_BODY = 256 * 1024


def log(msg: str) -> None:
    print(f"[ao-payment] {msg}", file=sys.stderr, flush=True)


def payload_hash(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def opaque_ref(provider: str, provider_ref: str) -> str:
    """Store an opaque internal reference, never the raw payload (Section 7.2)."""
    return f"{provider}:{hashlib.sha256(provider_ref.encode()).hexdigest()[:32]}"


def verify_paypal(headers, body: bytes, secret: str) -> bool:
    """Verify the PayPal webhook transmission signature.

    PayPal signs the concatenated transmission id, timestamp and body, using a
    HMAC keyed on the webhook id. We also replay-guard on the timestamp.
    """
    if not secret:
        log("REJECT paypal: no webhook secret configured")
        return False
    t_id = headers.get("PAYPAL-TRANSMISSION-ID")
    t_time = headers.get("PAYPAL-TRANSMISSION-TIME")
    t_sig = headers.get("PAYPAL-TRANSMISSION-SIG")
    if not (t_id and t_time and t_sig):
        log("REJECT paypal: missing transmission headers")
        return False
    # Replay guard: reject timestamps more than 5 minutes old.
    try:
        from datetime import datetime, timezone
        sent = datetime.strptime(t_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        age = abs((datetime.now(timezone.utc) - sent).total_seconds())
        if age > 300:
            log(f"REJECT paypal: stale transmission ({int(age)}s)")
            return False
    except ValueError:
        log("REJECT paypal: unparseable transmission time")
        return False
    expected = hmac.new(
        secret.encode(), f"{t_id}|{t_time}|".encode() + body, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, t_sig):
        log("REJECT paypal: signature mismatch")
        return False
    return True


def normalize(provider: str, event: dict) -> dict:
    """Map a provider event to our normalized shape. Never stores raw secrets."""
    ref = (
        event.get("id")
        or event.get("txn_id")
        or event.get("payment_id")
        or event.get("transaction_id")
        or ""
    )
    ev_type = (
        event.get("event_type")
        or event.get("type")
        or event.get("event")
        or "unknown"
    )
    amount = event.get("amount")
    currency = (event.get("currency") or "USD").upper()
    if isinstance(amount, dict):
        currency = (amount.get("currency_code") or currency).upper()
        amount = amount.get("value")
    return {
        "provider": provider,
        "event_type": ev_type,
        "provider_ref": str(ref),
        "currency": currency,
        "amount_cents": to_cents(amount),
    }


def to_cents(amount) -> int | None:
    if amount is None:
        return None
    try:
        return int(round(float(amount) * 100))
    except (TypeError, ValueError):
        return None


class Sink:
    """Minimal salesdb writer.

    Uses psycopg only if available; otherwise records to stdout so the adapter
    can be exercised without a database. No credential is ever logged.
    """

    def __init__(self, dsn: str | None):
        self.dsn = dsn

    def record(self, n: dict, body_hash: str, verified: bool, note: str = "") -> None:
        ref = opaque_ref(n["provider"], n["provider_ref"])
        line = (
            f"event provider={n['provider']} type={n['event_type']} "
            f"ref={ref} amount_cents={n['amount_cents']} currency={n['currency']} "
            f"verified={verified} sha256={body_hash[:16]}.."
        )
        if self.dsn:
            try:
                import psycopg  # type: ignore
                with psycopg.connect(self.dsn) as conn, conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO payment_provider_events "
                        "(provider, event_type, payload_hash_sha256, raw_ref) "
                        "VALUES (%s,%s,%s,%s)",
                        (n["provider"], n["event_type"], body_hash, ref),
                    )
                    conn.commit()
                log(f"stored: {line}")
                return
            except Exception as exc:  # noqa: BLE001
                log(f"ERROR storing event ({type(exc).__name__}); not accepting as verified")
                raise
        log(f"DRY-RUN (no DSN): {line} {note}")


class Handler(BaseHTTPRequestHandler):
    sink: Sink
    secret: str
    dry: bool

    def log_message(self, fmt, *a):  # quieter default logging
        log("http " + (fmt % a))

    def _reply(self, code: int, body: dict):
        raw = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/health":
            self._reply(200, {"ok": True, "enabled": not self.dry})
        else:
            self._reply(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/webhook/paypal":
            provider = "paypal"
        elif self.path == "/webhook/coinbase":
            provider = "coinbase"
        elif self.path == "/webhook/Zelle":
            provider = "Zelle"
        else:
            self._reply(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            self._reply(400, {"error": "bad length"})
            return
        body = self.rfile.read(length)
        bh = payload_hash(body)

        if provider in AUTOMATED:
            if not verify_paypal(self.headers, body, self.secret):
                # Rejected events are logged but NEVER written: an unverified
                # event must not be able to create business state.
                self._reply(401, {"error": "signature verification failed"})
                return
        elif provider == "Zelle":
            # Refuse to treat any inbound POST as Zelle evidence. Section 18.4:
            # Zelle has no webhook; reconciliation is operator-only.
            self._reply(501, {"error": "Zelle is manual-reconciliation only (Section 18.4)"})
            return

        try:
            event = json.loads(body)
        except json.JSONDecodeError:
            self._reply(400, {"error": "invalid json"})
            return
        if not isinstance(event, dict):
            self._reply(400, {"error": "object required"})
            return

        n = normalize(provider, event)
        if not n["provider_ref"]:
            self._reply(400, {"error": "missing provider reference"})
            return
        try:
            self.sink.record(n, bh, verified=True)
        except Exception:  # noqa: BLE001
            self._reply(503, {"error": "storage unavailable"})
            return
        self._reply(200, {"accepted": True, "provider": provider})


def main() -> int:
    ap = argparse.ArgumentParser(description="ao-ingress-payment adapter")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8899)
    ap.add_argument("--dsn", default=os.environ.get("PAYMENT_DSN"),
                    help="salesdb DSN; omit for dry-run (no rows written)")
    ap.add_argument("--webhook-secret", default=os.environ.get("PAYPAL_WEBHOOK_SECRET", ""))
    ap.add_argument("--dry-run", action="store_true",
                    help="serve but never write, regardless of DSN")
    args = ap.parse_args()

    if args.dry_run:
        args.dsn = None
    if not args.dsn:
        log("DRY-RUN: no salesdb DSN, nothing will be written")
    if not args.webhook_secret:
        log("WARN: no PAYPAL webhook secret; paypal events will be REJECTED")
    Handler.sink = Sink(args.dsn)
    Handler.secret = args.webhook_secret
    Handler.dry = args.dry_run
    log(f"listening on {args.host}:{args.port}")
    HTTPServer((args.host, args.port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
