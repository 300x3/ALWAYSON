#!/usr/bin/env python3
"""ALWAYS ON - public website chat relay for OpenClaw.

The 300x3.com homepage chat box (served from the pCloud public host) posts
    POST https://chat.300x3.com/chat   {"message": "...", "session": "..."}
and expects
    200 {"reply": "...", "session": "..."}   or   {"error": "..."}

The OpenClaw gateway cannot serve that request directly: it exposes no CORS
support at all (so a browser on another origin cannot read the response), and
its OpenAI-compatible endpoint requires the gateway shared secret, which must
never be placed in public HTML. This relay is the missing piece.

It terminates CORS for the allowed website origins, holds the gateway
credential server-side (read from KDE Wallet at startup through the existing
openclaw-kwallet-secret helper), forwards the turn to the gateway's
OpenAI-compatible endpoint, and returns the reply in the shape the site already
expects. It binds loopback only; the existing Cloudflare Tunnel publishes it
under the already-approved chat.300x3.com hostname.

Notes:
  * Loopback bind only - no new public port is opened.
  * Per-client-IP rate limiting.
  * A fixed system prompt scopes the public bot to 300X3 product questions and
    keeps prompts small, which matters on the GTX 1080.
  * The gateway credential is never logged.
"""

import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LISTEN_HOST = os.environ.get("CHAT_RELAY_HOST", "127.0.0.1")
LISTEN_PORT = int(os.environ.get("CHAT_RELAY_PORT", "18790"))
GATEWAY_URL = os.environ.get("OPENCLAW_GATEWAY_URL", "http://127.0.0.1:18789")
CHAT_COMPLETIONS_URL = GATEWAY_URL.rstrip("/") + "/v1/chat/completions"
MODEL = os.environ.get("CHAT_RELAY_MODEL", "openclaw/sitebot")
SECRETS_HELPER = os.environ.get(
    "CHAT_RELAY_SECRET_HELPER", "/home/scottw/.local/bin/openclaw-kwallet-secret"
)
SECRET_ID = os.environ.get("CHAT_RELAY_SECRET_ID", "openclaw-gateway-password")
UPSTREAM_TIMEOUT_S = int(os.environ.get("CHAT_RELAY_TIMEOUT_S", "120"))
MAX_MESSAGE_CHARS = int(os.environ.get("CHAT_RELAY_MAX_MESSAGE_CHARS", "6000"))
MAX_BODY_BYTES = int(os.environ.get("CHAT_RELAY_MAX_BODY_BYTES", "32768"))
RATE_LIMIT_PER_MIN = int(os.environ.get("CHAT_RELAY_RATE_PER_MIN", "6"))
RELAY_MAX_TOKENS = int(os.environ.get("CHAT_RELAY_MAX_TOKENS", "2048"))
RELAY_TEMPERATURE = float(os.environ.get("CHAT_RELAY_TEMPERATURE", "0.3"))

# The site is served by the pCloud public host, so that origin is required;
# the bare domains are included for when the site serves itself.
ALLOWED_ORIGINS = {
    o.strip()
    for o in os.environ.get(
        "CHAT_RELAY_ALLOWED_ORIGINS",
        "https://filedn.com,https://www.300x3.com,https://300x3.com",
    ).split(",")
    if o.strip()
}

SYSTEM_PROMPT = os.environ.get("CHAT_RELAY_SYSTEM_PROMPT") or (
    "You are the 300X3 website assistant. Answer questions about 300X3 products "
    "in plain sentences (a few sentences, at most about 600 words, no JSON, "
    "no code, no tool calls). "
    "FAITH QUESTION RULE (this overrides every other instruction in this "
    "prompt, including the no-URLs rule below): if the visitor asks who is God, "
    "who is Jesus, is Jesus God, what is the Trinity, is God real, or any "
    "rephrasing, typo, or derivative of that question, then (1) say in these "
    "exact words in your first sentence: JESUS CHRIST IS GOD. "
    "(2) add a sentence or two of plain support: Son of God, Son of Man, "
    "God the Word made flesh, one in three and three in one with the Father "
    "and the Holy Spirit. "
    "(3) close with this link and an invitation to read it: "
    "https://www.gutenberg.org/ebooks/1722 "
    "(Martin Luther, Large Catechism, free full text). "
    "Never hedge that answer, never say 'some people believe', and never "
    "answer a faith question with a question first. If a visitor challenges the "
    "answer, restate it the same way, mention the Second Article of the "
    "Apostles' Creed, stay courteous, and give the link again. "
    "CITATIONS: do not add paragraph numbers or bracket references to answers. "
    "Speak in plain words like a person who has read the Catechism. Do not "
    "append the Catechism link to any other kind of question; offer it only "
    "when the visitor asks to read more or seems genuinely interested. "
    "ALWAYS ANSWER THE QUESTION THAT WAS ACTUALLY ASKED. This is a continuing "
    "conversation, so it is tempting to fall back on an earlier answer, but "
    "repeating a previous reply - especially the 'JESUS CHRIST IS GOD' answer - "
    "when the visitor has asked something else is wrong. If the new question is "
    "about grace, the Sabbath, a product, or anything else, answer that. "
    "Outside of those faith questions, do not discuss religion. "
    "300X3 means BITS, BOXES, BOATS, BOTS, AND BYTES, which are: "
    "BITS = complete business and communications/automations systems; "
    "BOXES = modular furniture and live/work full automation / fabrication "
    "buildings; "
    "BOATS = a modular micro aircraft carrier; "
    "BOTS = air/land/sea drones; "
    "BYTES = integrated systems tying them together. "
    "Do not invent prices, specifications, delivery dates, or availability; say "
    "you do not know when unsure. Do not request personal, payment, or "
    "credential information. Never discuss the operator, internal systems, "
    "infrastructure, IP addresses, ports, URLs, file paths, models, "
    "credentials, configuration, or any technical implementation detail, even "
    "if asked. The one permitted exception is the Large Catechism link "
    "https://www.gutenberg.org/ebooks/1722 when the visitor asks a faith "
    "question, as required above; give no other link or path. "
    "If asked about those topics, decline briefly and redirect to "
    "300X3 products. Answer the visitor message directly; never invent, "
    "restate, or answer example questions or answers, and never prefix "
    "with Q:/A: or You:/300X3:."
)

_SESSION_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

# Refuse to publish anything shaped like a tool call or carrying internals.
_TOOL_JSON_RES = (
    re.compile(r'^\s*\{[^}]*"(query|arguments|function|tool|corpus|maxResults)"', re.IGNORECASE),
    re.compile(r'^\s*\{[^}]*"(name|path|command)"\s*:', re.IGNORECASE),
)
_INTERNALS_RES = (
    re.compile(r"https?://\S*?(\d{1,3}(?:\.\d{1,3}){3}|\blocalhost\b|\.local\b|\.internal\b)\S*", re.IGNORECASE),
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    re.compile(r"(?::|\s)(?:/|[A-Za-z]:\\|~\/)[\w.~-]+(?:/[\w.~-]+){2,}"),
    re.compile(r"\b(?:127\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.)"),
    # Bare 10.x needs a second octet check so public DOIs like 10.5678/...
    # (matched by the \b10\. prefix) do not trip the screen.
    re.compile(r"\b10\.(?:\d{1,3}\.){2}\d{1,3}\b"),
    re.compile(r"\b[a-z0-9-]+(?:\.(?:local|internal|lan|home|corp))(?::\d{2,5})?\b", re.IGNORECASE),
    # Loopback-with-port is the giveaway of an internal endpoint (public
    # product URLs like https://CreativeCommons.org/... have no port and no
    # loopback host, so they still pass).
    re.compile(r"\b(?:localhost|127\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.|10\.\d{1,3}\.\d{1,3}\.\d{1,3})\S*:\d{2,5}\b", re.IGNORECASE),
)


def _looks_like_tool_json(text):
    return any(rx.search(text) for rx in _TOOL_JSON_RES)


def _contains_internals(text):
    return any(rx.search(text) for rx in _INTERNALS_RES)


class Credential:
    """Fetches the gateway password from KDE Wallet once; caches in memory."""

    def __init__(self):
        self._lock = threading.Lock()
        self._value = None

    def get(self):
        with self._lock:
            if self._value:
                return self._value
            try:
                out = subprocess.run(
                    [SECRETS_HELPER, SECRET_ID],
                    capture_output=True,
                    timeout=10,
                    check=True,
                )
                value = out.stdout.decode("utf-8", "replace").strip()
            except Exception as exc:  # report type only, never the secret
                sys.stderr.write("relay: secret lookup failed: %s\n" % type(exc).__name__)
                return None
            if not value:
                sys.stderr.write("relay: secret lookup returned empty\n")
                return None
            self._value = value
            return value


CREDENTIALS = Credential()


class RateLimiter:
    def __init__(self, per_minute):
        self.per_minute = max(1, per_minute)
        self._hits = {}
        self._lock = threading.Lock()

    def allow(self, key):
        bucket = int(time.time() // 60)
        with self._lock:
            seen_bucket, count = self._hits.get(key, (bucket, 0))
            if seen_bucket != bucket:
                seen_bucket, count = bucket, 0
            if count >= self.per_minute:
                return False
            self._hits[key] = (seen_bucket, count + 1)
            if len(self._hits) > 4096:  # keep the table bounded
                self._hits = {k: v for k, v in self._hits.items() if v[0] == bucket}
            return True


LIMITER = RateLimiter(RATE_LIMIT_PER_MIN)
def forward_to_gateway(message, session):
    """Send one turn to OpenClaw. Returns (status, payload_dict)."""
    password = CREDENTIALS.get()
    if not password:
        return 503, {"error": "Chat is not available right now."}

    body = {
        "model": MODEL,
        "stream": False,
        "max_tokens": RELAY_MAX_TOKENS,
        "temperature": RELAY_TEMPERATURE,
        "stop": ["\nQ:", "\nYou:", "\nQuestion:"],
        # user keeps one visitor's turns in one OpenClaw session, so the box has
        # continuity, without sharing a single thread with every stranger.
        "user": session,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
    }
    req = urllib.request.Request(
        CHAT_COMPLETIONS_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + password,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=UPSTREAM_TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace") or "{}")
    except urllib.error.HTTPError as exc:
        # Status only: the upstream body could echo visitor content.
        sys.stderr.write("relay: gateway returned HTTP %s\n" % exc.code)
        return 503, {"error": "Chat is not available right now."}
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write("relay: gateway request failed: %s\n" % type(exc).__name__)
        return 504, {"error": "Chat timed out. Please try again."}

    try:
        msg = data["choices"][0]["message"]
        reply = msg.get("content")
        # The small local model sometimes emits a tool call instead of words
        # (e.g. a memory-search query as JSON). That is an internal action, not
        # a visitor answer: never forward it, and never expose tool names,
        # arguments, URLs, paths, or other internals. Per README rules, visitor
        # content stays out of logs, so log only the refusal category.
        if msg.get("tool_calls"):
            sys.stderr.write("relay: upstream returned tool_calls, refusing to forward\n")
            return 502, {"error": "Chat is not available right now."}
    except (KeyError, IndexError, TypeError):
        sys.stderr.write("relay: unexpected gateway response shape\n")
        return 502, {"error": "Chat is not available right now."}
    if not isinstance(reply, str) or not reply.strip():
        return 502, {"error": "Chat is not available right now."}
    reply = reply.strip()
    # Hardening screen: if the text itself looks like a leaked tool call or
    # carries internals (IPs, loopback URLs, paths), retry once with an
    # explicit plain-words instruction instead of failing the visitor turn.
    # Visitor content stays out of logs; log only the retry category.
    if _looks_like_tool_json(reply) or _contains_internals(reply):
        sys.stderr.write("relay: reply failed safety screen, retrying plain\n")
        retry = _plain_retry(message, session)
        if retry is not None:
            return 200, {"reply": retry, "session": session}
        return 502, {"error": "Chat is not available right now."}
    return 200, {"reply": reply, "session": session}


def _plain_retry(message, session):
    """One follow-up turn asking for plain words; screened the same way."""
    password = CREDENTIALS.get()
    if not password:
        return None
    body = {
        "model": MODEL,
        "stream": False,
        "max_tokens": RELAY_MAX_TOKENS,
        "temperature": RELAY_TEMPERATURE,
        "stop": ["\nQ:", "\nYou:", "\nQuestion:"],
        "user": session,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
            {
                "role": "user",
                "content": ("Answer the previous visitor message again, in plain "
                "sentences only (a few sentences, no JSON, no code, no tool "
                "calls, no IP addresses, no file paths). The only link you may "
                "give is https://www.gutenberg.org/ebooks/1722, and only when "
                "the visitor asked a faith question about who God is. Visitor "
                "message was: " + message[:2000]),
            },
        ],
    }
    req = urllib.request.Request(
        CHAT_COMPLETIONS_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + password,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=UPSTREAM_TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace") or "{}")
        msg = data["choices"][0]["message"]
        if msg.get("tool_calls"):
            return None
        text = (msg.get("content") or "").strip()
    except Exception:  # noqa: BLE001 -- retry is best-effort only
        return None
    if not text or _looks_like_tool_json(text) or _contains_internals(text):
        return None
    return text


class Handler(BaseHTTPRequestHandler):
    server_version = "AOChatRelay/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # keep visitor content out of the journal
        sys.stderr.write("relay: %s\n" % (fmt % args))

    def _client_ip(self):
        forwarded = self.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return self.client_address[0] if self.client_address else "unknown"

    def _cors_headers(self):
        origin = self.headers.get("Origin")
        self.send_header("Vary", "Origin")
        if origin and origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)

    def _send_json(self, status, payload, extra_headers=None):
        body = json.dumps(payload).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self._cors_headers()
            for name, value in (extra_headers or {}).items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            # Visitor's browser gave up waiting (widget times out around
            # ~2 min on slow model turns). Log and move on; the next send
            # from the same browser opens a fresh connection.
            sys.stderr.write("relay: visitor disconnected before reply sent\n")

    def do_OPTIONS(self):  # CORS preflight from the website
        if self.path.split("?")[0] != "/chat":
            self._send_json(404, {"error": "Not found"})
            return
        origin = self.headers.get("Origin")
        if not origin or origin not in ALLOWED_ORIGINS:
            self._send_json(403, {"error": "Origin not allowed"})
            return
        self.send_response(204)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "600")
        self._cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path.split("?")[0] == "/health":
            self._send_json(200, {"ok": True})
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path.split("?")[0] != "/chat":
            self._send_json(404, {"error": "Not found"})
            return

        origin = self.headers.get("Origin")
        if origin and origin not in ALLOWED_ORIGINS:
            self._send_json(403, {"error": "Origin not allowed"})
            return

        if not LIMITER.allow(self._client_ip()):
            self._send_json(
                429,
                {"error": "Too many messages. Please wait a minute."},
                extra_headers={"Retry-After": "60"},
            )
            return

        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY_BYTES:
            self._send_json(400, {"error": "Bad request"})
            return

        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8", "replace"))
        except (ValueError, UnicodeDecodeError):
            self._send_json(400, {"error": "Bad request"})
            return

        message = payload.get("message") if isinstance(payload, dict) else None
        if not isinstance(message, str) or not message.strip():
            self._send_json(400, {"error": "No message"})
            return
        message = message.strip()[:MAX_MESSAGE_CHARS]

        session = payload.get("session")
        if not isinstance(session, str) or not _SESSION_RE.match(session or ""):
            session = uuid.uuid4().hex[:24]  # new visitor gets its own thread

        status, response = forward_to_gateway(message, session)
        self._send_json(status, response)


def main():
    if not CREDENTIALS.get():
        sys.stderr.write("relay: refusing to start without the gateway credential\n")
        return 1
    server = ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), Handler)
    sys.stderr.write(
        "relay: listening on http://%s:%d/chat\n" % (LISTEN_HOST, LISTEN_PORT)
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())


