#!/usr/bin/env python3
# ALWAYS ON - scripts/operations/web-console-server.py
# Loopback-only operator web console (binds 127.0.0.1 only; no public port).
# Routes:
#   /       index with links to the console pages
#   /sim    ROS 2 / Gazebo / Foxglove browser console (talks to
#           foxglove_bridge ws://127.0.0.1:8765 subprotocol foxglove.sdk.v1)
#   /podman dynamic Podman + systemd status (runs `podman ps -a`,
#           `podman network ls`, `systemctl --user list-units` live)
# Usage: python3 web-console-server.py [port]   (default 8099)
import html
import subprocess
import sys

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8099

INDEX_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>ALWAYS ON console</title>
<style>body{font-family:sans-serif;background:#111;color:#eee;margin:2em}
a{color:#6cf} li{margin:.4em 0}</style></head><body>
<h1>ALWAYS ON — loopback operator console</h1>
<ul>
<li><a href="/sim">/sim — ROS 2 Lyrical + Gazebo Sim 10.5 + Foxglove bridge console</a></li>
<li><a href="/podman">/podman — Podman containers &amp; networks (live)</a></li>
</ul>
<p>All routes bind 127.0.0.1 only.</p>
</body></html>
"""

SIM_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>ALWAYS ON sim console</title>
<style>body{font-family:sans-serif;background:#111;color:#eee;margin:1.5em}
table{border-collapse:collapse;margin-top:.6em}td,th{border:1px solid #444;padding:4px 10px;text-align:left}
.ok{color:#6f6}.bad{color:#f66}code{color:#fc6}</style></head><body>
<h1>ROS 2 Lyrical + Gazebo 10.5 — Foxglove bridge console</h1>
<p>Bridge: <code>ws://127.0.0.1:8765</code> (subprotocol <code>foxglove.sdk.v1</code>) — status: <b id="st" class="bad">connecting…</b></p>
<p>Messages received: <b id="n">0</b> · <span id="clock">/clock: waiting</span></p>
<h2>Channels</h2>
<table id="ch"><tr><th>id</th><th>topic</th><th>schema</th></tr></table>
<script>
let ws=null,n=0,clockId=null,tries=0;
function setStatus(t,cls){const e=document.getElementById("st");e.textContent=t;e.className=cls;}
function tick(){document.getElementById("n").textContent=n;}
function connect(){
 tries++; ws=new WebSocket("ws://127.0.0.1:8765/","foxglove.sdk.v1"); ws.binaryType="arraybuffer";
 ws.onopen=()=>{setStatus("connected (try "+tries+")","ok");
   ws.send(JSON.stringify({op:"subscribe",subscriptions:[]}));};
 ws.onmessage=(e)=>{ if(typeof e.data==="string"){ let j; try{j=JSON.parse(e.data);}catch(_){return;}
   if(j.op==="advertise"){ const tb=document.getElementById("ch");
     (j.channels||[]).forEach(c=>{const r=document.createElement("tr");
       r.innerHTML="<td>"+c.id+"</td><td>"+c.topic+"</td><td>"+(c.schemaName||"")+"</td>";
       tb.appendChild(r); if(c.topic==="/clock") clockId=c.id;});
     if(clockId!==null&&clockId!==undefined)
       ws.send(JSON.stringify({op:"subscribe",subscriptions:[{id:1,clockId:undefined,channelId:clockId}]}));}
 } else { n++; tick(); if(clockId!==null) document.getElementById("clock").textContent="/clock: "+n+" msg(s)"; }
 };
 ws.onclose=()=>{setStatus("disconnected — retrying in 3s","bad");setTimeout(connect,3000);};
 ws.onerror=()=>{try{ws.close();}catch(_){}};
}
connect();
</script></body></html>
"""


def run(cmd):
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return out.stdout or out.stderr
    except Exception as exc:  # noqa: BLE001 - render any failure on the page
        return "ERROR: %s\n" % exc


def podman_html():
    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        "<meta http-equiv='refresh' content='15'>",
        "<title>ALWAYS ON Podman status</title>",
        "<style>body{font-family:sans-serif;background:#111;color:#eee;margin:1.5em}"
        "table{border-collapse:collapse}td,th{border:1px solid #444;padding:4px 8px;text-align:left}"
        "code{color:#fc6} a{color:#6cf}</style></head><body>",
        "<h1>Podman — containers, networks, services</h1>",
        "<p><a href='/'>console index</a> · auto-refresh 15s</p>",
        "<h2>podman ps -a</h2><pre>",
        html.escape(run(["podman", "ps", "-a", "--format",
                         "{{.Names}} | {{.Status}} | {{.Networks}} | {{.Ports}}"])),
        "</pre><h2>podman network ls</h2><pre>",
        html.escape(run(["podman", "network", "ls"])),
        "</pre><h2>systemctl --user ao-* services</h2><pre>",
        html.escape(run(["systemctl", "--user", "list-units", "--type=service",
                         "--state=running", "--no-pager"])),
        "</pre></body></html>",
    ]
    return "".join(parts)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 - http.server API
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            body, ctype = INDEX_HTML, "text/html; charset=utf-8"
        elif path == "/sim":
            body, ctype = SIM_HTML, "text/html; charset=utf-8"
        elif path == "/podman":
            body, ctype = podman_html(), "text/html; charset=utf-8"
        else:
            self.send_response(404)
            self.end_headers()
            return
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        sys.stderr.write("web-console: %s\n" % (fmt % args))


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    sys.stderr.write("web-console: http://127.0.0.1:%d/ (loopback only)\n" % PORT)
    srv.serve_forever()
