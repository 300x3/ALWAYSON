#!/usr/bin/env python3
"""Probe free Cline models BEYOND the promotional list.

Operator instruction 2026-10-09: stop trusting only the 4 promo ids in
https://api.cline.bot/api/v1/ai/cline/recommended-models ("free" key) and
probe the wider free surface. Three sources, cheapest first:

  1. cline-free/* ids from the recommended-models "free" key (promo list).
  2. OpenRouter :free models (list needs no key). Probed only if this host
     holds an OpenRouter key -- else listed but skipped, never attempted.
  3. Local LM Studio models (`lms ls`): $0, private, no quota. Currently
     coordinator-reserved (nemotron-3-nano-4b); workgroups may use them ONLY
     with explicit operator approval. Probe records availability only.

Probe protocol per model (mirrors the 2026-10-08 verification): a real
edit-and-run task in an isolated cwd. PASS = edited correctly AND
finishReason=completed AND totalCost=0. BILLABLE (cost>0) is never assigned.

Usage: probe-freemium.py list | probe | status
Ledger: /tmp/ao-sessions/model-ledger.json + artifacts/dashboard copy.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEDGER_TMP = "/tmp/ao-sessions/model-ledger.json"
LEDGER_REPO = os.path.join(ROOT, "artifacts/dashboard/model-ledger.json")
RECOMMENDED_URL = "https://api.cline.bot/api/v1/ai/cline/recommended-models"
OPENROUTER_URL = "https://openrouter.ai/api/v1/models"
PROBE_DIR = "/tmp/ao-probe/freemium"


def _get(url, timeout=20):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.load(r)


def cline_free_ids():
    try:
        d = _get(RECOMMENDED_URL)
        return [(m["id"], m.get("name", "")) for m in d.get("free", [])]
    except Exception as e:
        print("recommended-models unreachable: %s" % e)
        return []


def openrouter_free_ids():
    try:
        d = _get(OPENROUTER_URL)
        return [(m.get("id", ""), (m.get("name") or "")[:60])
                for m in d.get("data", []) if ":free" in m.get("id", "")]
    except Exception as e:
        print("openrouter unreachable: %s" % e)
        return []


def openrouter_key_present():
    for f in ("~/.cline/data/secrets.json", "~/.cline/data/globalState.json"):
        try:
            if "sk-or" in json.dumps(json.load(open(os.path.expanduser(f)))):
                return True
        except Exception:
            pass
    return bool(os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OR_API_KEY"))


def local_models():
    try:
        out = subprocess.run(["lms", "ls"], capture_output=True,
                             text=True, timeout=30).stdout
        models, loaded = [], None
        for line in out.splitlines():
            p = line.strip().split()
            if len(p) >= 1 and "/" in p[0] and not line.startswith(("LLM", "You have")):
                models.append(p[0])
                if "LOADED" in line:
                    loaded = p[0]
        return models, loaded
    except Exception as e:
        print("lms ls failed: %s" % e)
        return [], None


def load_ledger():
    for p in (LEDGER_TMP, LEDGER_REPO):
        try:
            return json.load(open(p))
        except Exception:
            continue
    return {"probed": {}, "updated": ""}


def save_ledger(led):
    led["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    for p in (LEDGER_TMP, LEDGER_REPO):
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            json.dump(led, open(p, "w"), indent=1)
        except Exception as e:
            print("ledger write %s failed: %s" % (p, e))


def probe_cline_model(mid, timeout=150):
    """One edit-and-run probe. Returns (verdict, detail)."""
    d = os.path.join(PROBE_DIR, mid.replace("/", "_"))
    os.makedirs(d, exist_ok=True)
    target = os.path.join(d, "probe.txt")
    open(target, "w").write("WRONG\n")
    prompt = ("In %s: overwrite probe.txt with exactly FIXED, then run "
              "`cat probe.txt` and reply exactly: PROBE-DONE" % d)
    try:
        p = subprocess.run(["cline", "--json", "--cwd", d, "--model", mid, prompt],
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "TIMEOUT", "no finish within %ds" % timeout
    verdict, detail = "ERROR", (p.stderr.strip() or p.stdout.strip())[-300:]
    for line in p.stdout.splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") != "run_result":
            if e.get("type") == "error" and verdict == "ERROR":
                detail = str(e.get("message", ""))[:200]
            continue
        u = e.get("usage", {}) or {}
        cost = u.get("totalCost")
        txt = str(e.get("text", ""))
        if e.get("finishReason") == "completed" and "PROBE-DONE" in txt:
            got = open(target).read().strip() if os.path.exists(target) else "<missing>"
            if got == "FIXED" and cost == 0:
                verdict, detail = "PASS", "edited+ran, totalCost=0"
            elif got != "FIXED":
                verdict, detail = "FAIL", "completed but file=%r" % got
            else:
                verdict, detail = "BILLABLE", "completed but totalCost=%s" % cost
        elif "429" in txt or "INFERENCE_CAP_ERROR" in txt or "limit" in txt.lower():
            verdict, detail = "DRY", txt[:200]
        else:
            verdict, detail = "ERROR", txt[:200]
    return verdict, detail


def cmd_list():
    print("== 1: cline-free promo ==")
    for mid, name in cline_free_ids():
        print("  %-45s %s" % (mid, name))
    print("== 2: openrouter :free (key: %s) ==" % openrouter_key_present())
    for mid, name in openrouter_free_ids():
        print("  %-50s %s" % (mid, name))
    print("== 3: local LM Studio (coordinator-reserved) ==")
    for m in local_models()[0]:
        print("  %s" % m)


def cmd_status():
    led = load_ledger()
    print("ledger: %s" % led.get("updated", "never"))
    for mid in sorted(led.get("probed", {})):
        r = led["probed"][mid]
        print("  %-45s %-8s %s [%s]" % (mid, r["verdict"], r["detail"][:80], r.get("ts", "?")))


def cmd_probe():
    led = load_ledger()
    probed = led.setdefault("probed", {})
    cands = [mid for mid, _ in cline_free_ids()]
    if openrouter_key_present():
        cands += [mid for mid, _ in openrouter_free_ids()]
    else:
        print("no OpenRouter key: :free ids listed, not probed")
    for mid in cands:
        if mid in probed and probed[mid]["verdict"] in ("PASS", "BILLABLE"):
            continue
        print("probing %-45s ..." % mid, flush=True)
        v, d = probe_cline_model(mid)
        probed[mid] = {"verdict": v, "detail": d, "ts": time.strftime("%Y-%m-%d %H:%M")}
        print("  -> %s %s" % (v, d))
        save_ledger(led)
    print("done. Only PASS + totalCost=0 models are candidates.")
    cmd_status()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"list": cmd_list, "probe": cmd_probe}.get(cmd, cmd_status)()
