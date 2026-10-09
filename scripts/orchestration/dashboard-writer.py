#!/usr/bin/env python3
"""Tiny local writer + control panel for the ALWAYS ON dashboard.

Serves artifacts/dashboard/ over http://127.0.0.1:8766 and accepts:
  POST /answers   merge submitted decisions into answers.json
  POST /spawn     (re)start the 11 agent sessions via supervise.py
  POST /stop      stop the sessions, the watcher, the collector and the guards

Loopback only, no auth, no external binding. It writes ONLY answers.json plus
process control - no path comes from the request body except item ids, which are
validated against the item pattern. Anything else is rejected.

/spawn and /stop deliberately do NOT take a body: every group name is a
compile-time constant here, so a request cannot influence which processes are
signalled. /stop is the only destructive route and it refuses to run anything
outside /ALWAYSON's own orchestration tree.

Reading answers back: render-dashboard.py loads answers.json and pre-fills the
fields, so a decision survives a re-render and is visible to the agent sessions.
"""
import json, os, re, sys, subprocess, signal, time, datetime as dt
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR = os.path.join(ROOT, "artifacts/dashboard")
ANS = os.path.join(DIR, "answers.json")
SESS = "/tmp/ao-sessions"
ORCH = os.path.join(ROOT, "scripts/orchestration")
SUPERVISE = os.path.join(ORCH, "supervise.py")
ROTATE = os.path.join(ORCH, "rotate-agents.py")
PORT = int(os.environ.get("AO_DASH_PORT", "8766"))
ITEM_RE = re.compile(r"^[A-Z]{2,6}-\d{1,3}$")
GROUPS = ["plat", "net", "sec", "ledger", "pay", "comm",
          "field", "sim", "ops-a", "ops-b", "spec"]

def _count_sessions():
    ps = subprocess.run(["ps", "-eo", "cmd"], capture_output=True, text=True).stdout
    return sum(1 for l in ps.splitlines()
               if "cline --json" in l and "bash -c" not in l and "grep" not in l)


def do_spawn():
    """Advance the single-agent rotation, or report the current shift.

    2026-10-05: the operator runs ONE agent at a time in 2-hour shifts, not
    11 parallel sessions. The old behaviour here -- clearing every pid marker
    and spawning all 11 -- would fight the rotation timer by launching 11
    agents the timer would then stop. So this button now runs
    `rotate-agents.py rotate`: hands off to the next group if the shift is
    over, revives the current agent if it died mid-shift, does nothing if
    the shift is healthy. rotate-agents.py owns the actual launch so the
    dashboard and the CLI cannot drift apart on how a session is started.
    """
    r = subprocess.run([sys.executable, ROTATE, "rotate"],
                       cwd=ROOT, capture_output=True, text=True, timeout=300)
    time.sleep(6)
    s = subprocess.run([sys.executable, ROTATE, "status"],
                       cwd=ROOT, capture_output=True, text=True, timeout=30)
    return {"spawned": (r.stdout or "").strip().splitlines()[-8:],
            "rotation": (s.stdout or "").strip(),
            "returncode": r.returncode,
            "live": _count_sessions(),
            "stderr": (r.stderr or "")[-300:]}


def do_stop():
    """Stop the sessions and the ALWAYS ON automation. Nothing else.

    Only signals processes whose command line matches one of these exact
    patterns, all of which belong to this project. cline is matched on the
    '--json' flag the supervisor always passes, so an unrelated interactive
    cline session is left alone.
    """
    stopped = []
    ps = subprocess.run(["ps", "-eo", "pid,args"], capture_output=True, text=True).stdout
    patterns = [
        "cline --json",
        "supervise.py watch",
        "collect-metrics.py",
        "dashboard.sh",
        "work30.sh",
    ]
    mine = os.getpid()
    for line in ps.splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        pid_s, _, cmd = line.partition(" ")
        if not pid_s.isdigit() or "bash -c" in cmd or "grep" in cmd:
            continue
        if int(pid_s) == mine or "dashboard-writer.py" in cmd:
            continue
        if any(p in cmd for p in patterns):
            try:
                os.kill(int(pid_s), signal.SIGTERM)
                stopped.append(int(pid_s))
            except (ProcessLookupError, PermissionError):
                pass
    # clear the stale pid files so a later spawn does not read a dead pid
    for g in GROUPS:
        for f in ("pid", "nudges"):
            try:
                os.remove(os.path.join(SESS, g, f))
            except FileNotFoundError:
                pass
    # SIGTERM is asynchronous and cline takes a moment to unwind its children.
    # The first version read the count after a flat 3s and reported 21 live when
    # the true figure was 0 - the button would have told the operator it had
    # failed when it had succeeded. Poll until it settles instead.
    for _ in range(20):
        time.sleep(1)
        if _count_sessions() == 0:
            break
    return {"signalled": len(stopped), "live": _count_sessions()}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        b = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        # No cache headers at all before this. With none set the browser is
        # free to heuristically cache the page, so a tab left open kept
        # showing an old render indefinitely -- measured 2026-10-09: the page
        # still read 36% complete while the server was answering 3%, because
        # the tab was serving its own copy and never re-requesting. The
        # operator cannot tell a stale tab from a broken dashboard.
        self.send_header("Cache-Control",
                         "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, open(os.path.join(DIR, "index.html"), encoding="utf-8").read(),
                       "text/html; charset=utf-8")
        elif self.path == "/answers":
            self._send(200, open(ANS, encoding="utf-8").read() if os.path.exists(ANS) else "{}")
        elif self.path == "/health":
            self._send(200, json.dumps({"ok": True, "answers": ANS,
                                        "live": _count_sessions()}))
        else:
            self._send(404, '{"error":"not found"}')

    def do_POST(self):
        if self.path == "/spawn":
            try:
                return self._send(200, json.dumps(do_spawn()))
            except Exception as e:
                return self._send(500, json.dumps({"error": str(e)[:300]}))
        if self.path == "/stop":
            try:
                return self._send(200, json.dumps(do_stop()))
            except Exception as e:
                return self._send(500, json.dumps({"error": str(e)[:300]}))
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
