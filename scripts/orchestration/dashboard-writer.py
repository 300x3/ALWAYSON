#!/usr/bin/env python3
"""Tiny local writer so the dashboard's Save button persists decisions.

Serves artifacts/dashboard/ over http://127.0.0.1:8765 and accepts POST /answers,
which merges the submitted answers into artifacts/dashboard/answers.json.

Loopback only, no auth, no external binding: it is a scratch file the operator
fills in on their own machine. It writes ONLY that one JSON file - no path comes
from the request body except the item ids, which are validated against the item
pattern. Anything else is rejected.

Reading it back: render-dashboard.py loads answers.json and pre-fills the fields,
so a decision survives a re-render and is visible to the agent sessions.
"""
import json, os, re, sys, datetime as dt
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR = os.path.join(ROOT, "artifacts/dashboard")
ANS = os.path.join(DIR, "answers.json")
PORT = int(os.environ.get("AO_DASH_PORT", "8766"))
ITEM_RE = re.compile(r"^[A-Z]{2,6}-\d{1,3}$")

class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        b = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, open(os.path.join(DIR, "index.html"), encoding="utf-8").read(),
                       "text/html; charset=utf-8")
        elif self.path == "/answers":
            self._send(200, open(ANS, encoding="utf-8").read() if os.path.exists(ANS) else "{}")
        elif self.path == "/health":
            self._send(200, json.dumps({"ok": True, "answers": ANS}))
        else:
            self._send(404, '{"error":"not found"}')

    def do_POST(self):
        if self.path != "/answers":
            return self._send(404, '{"error":"not found"}')
        try:
            n = int(self.headers.get("Content-Length", "0"))
            if n <= 0 or n > 200000:
                return self._send(400, '{"error":"bad size"}')
            data = json.loads(self.rfile.read(n).decode())
            rows = data.get("answers") or []
            cur = {}
            if os.path.exists(ANS):
                try:
                    cur = json.load(open(ANS, encoding="utf-8"))
                except ValueError:
                    cur = {}
            now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
            saved = 0
            for r in rows:
                item = str(r.get("item", ""))
                val = str(r.get("answer", ""))[:4000].strip()
                if not ITEM_RE.match(item) or not val:
                    continue
                cur[item] = {"answer": val, "answered_at": now}
                saved += 1
            tmp = ANS + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(cur, fh, indent=1, sort_keys=True)
            os.replace(tmp, ANS)          # atomic: never a half-written file
            self._send(200, json.dumps({"saved": saved}))
        except Exception as e:
            self._send(500, json.dumps({"error": str(e)[:200]}))

if __name__ == "__main__":
    os.makedirs(DIR, exist_ok=True)
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print("dashboard writer on http://127.0.0.1:%d  -> %s" % (PORT, ANS), flush=True)
    srv.serve_forever()
