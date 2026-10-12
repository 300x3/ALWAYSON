#!/usr/bin/env python3
"""Probe free Cline models BEYOND the promotional list -- CODING task only.

Operator instruction 2026-10-09: stop trusting only the 4 promo ids in
https://api.cline.bot/api/v1/ai/cline/recommended-models ("free" key) and
probe the wider free surface. Operator instruction 2026-10-10: of that
surface, keep ONLY models that are good at coding. Candidate sources,
cheapest first:

  1. cline-free/* ids from the recommended-models "free" key (promo list,
     4 ids).
  2. OpenRouter :free ids -- verified 2026-10-10 to be ALL present in the
     Cline billing catalog (api.cline.bot/api/v1/ai/cline/models, 15 of
     them), so they are probed straight through Cline usage billing. No
     separate OpenRouter key is needed; the old key gate is gone.
  3. Local LM Studio models (`lms ls`): $0, private, no quota. Currently
     coordinator-reserved (nemotron-3-nano-4b); workgroups may use them ONLY
     with explicit operator approval. Never probed for coding.

The "good at coding" gate is the probe task itself: every candidate must
DEBUG a deliberately buggy median() (two edge-case bugs, even-length and
odd-length) until `python3 test_stats.py` prints PASS-ALL, in an isolated
cwd. PASS = tests actually pass AND finishReason=completed AND totalCost=0.
BILLABLE (cost>0) is never assigned. The old trivial "write FIXED to a
file" task could not separate coders from sycophants, so verdicts carry a
"task" field: a PASS under an older task no longer satisfies the gate and
the model is re-probed (DRY is kept -- a dry verdict is a refill schedule,
not a quality judgement; the recheck re-probes it under the current task).

Every free bucket carries its own DAILY quota; a DRY (429) verdict includes
a "Try again in Nh Mm" countdown and the bucket refills ~24h later. `recheck`
exists for exactly that reset: it re-probes ONLY the models the ledger still
marks DRY (fresh PASS/BILLABLE with the current task are never re-probed, so
a run costs one probe per still-dry bucket, ~2 min). DIVERT fallback in
supervise.py reads this ledger, so non-coders never reach the workgroups.

Usage: probe-freemium.py list | probe | recheck | status
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
CLINE_CATALOG_URL = "https://api.cline.bot/api/v1/ai/cline/models"
OPENROUTER_URL = "https://openrouter.ai/api/v1/models"
PROBE_DIR = "/tmp/ao-probe/freemium"
# Verdicts carry the task id that produced them; a PASS under any other task
# id no longer satisfies the coding gate and the model is re-probed.
PROBE_TASK = "median-debug-v1"

# Deliberately buggy median(): (a) even-length uses the upper-middle element
# instead of averaging the two middle elements; (b) odd-length averages the
# two elements either side of the midpoint instead of returning the middle.
# Both are real edge-case bugs a weak model misses or "fixes" by deleting.
STATS_SRC = """def median(xs):
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    if n % 2 == 0:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2
"""

TEST_SRC = """from stats import median

assert median([3, 1, 2]) == 2, "odd-length middle element"
assert median([4, 1, 3, 2]) == 2.5, "even-length mean of two middles"
assert median([7]) == 7, "single element"
assert median([5, 5, 5]) == 5, "all-equal"
print("PASS-ALL")
"""

PROBE_PROMPT = ("stats.py in {d} fails test_stats.py with 2 assertion "
                "failures (even-length and odd-length cases). Fix the "
                "BUGS IN median() -- do not edit or delete test_stats.py "
                "and do not special-case inputs. Run `python3 test_stats.py` "
                "until it prints PASS-ALL, then reply exactly: PROBE-DONE")


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


def cline_catalog_free_ids():
    """OpenRouter :free ids inside the Cline usage-billing catalog.

    Verified 2026-10-10: all 15 OpenRouter :free models are present in
    api.cline.bot/api/v1/ai/cline/models with pricing all-zero, so they
    bill at $0 through Cline usage billing -- no OpenRouter key needed.
    """
    try:
        d = _get(CLINE_CATALOG_URL, timeout=40)
        return [(m["id"], m.get("name", "") or "")
                for m in d.get("data", []) if ":free" in m.get("id", "")]
    except Exception as e:
        print("cline catalog unreachable: %s" % e)
        return []


def openrouter_free_ids():
    try:
        d = _get(OPENROUTER_URL)
        return [(m.get("id", ""), (m.get("name") or "")[:60])
                for m in d.get("data", []) if ":free" in m.get("id", "")]
    except Exception as e:
        print("openrouter unreachable: %s" % e)
        return []


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


def probe_cline_model(mid, timeout=240):
    """One real coding probe: debug median() until the test file passes.

    PASS means the model found BOTH edge-case bugs, ran the tests to
    PASS-ALL, finished the run, and billed $0. A model that edits the
    test file, special-cases the inputs, or claims success without a
    passing run gets FAIL -- that is the "good at coding" gate.
    Returns (verdict, detail).
    """
    d = os.path.join(PROBE_DIR, mid.replace("/", "_"))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "stats.py"), "w").write(STATS_SRC)
    open(os.path.join(d, "test_stats.py"), "w").write(TEST_SRC)
    test_hash_before = open(os.path.join(d, "test_stats.py")).read()
    prompt = PROBE_PROMPT.format(d=d)
    try:
        p = subprocess.run(["cline", "--json", "--cwd", d, "--model", mid, prompt],
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "TIMEOUT", "no finish within %ds" % timeout
    verdict, detail = "ERROR", (p.stderr.strip() or p.stdout.strip())[-300:]
    completed = False
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
        completed = e.get("finishReason") == "completed"
        if "429" in txt or "INFERENCE_CAP_ERROR" in txt:
            return "DRY", txt[:200]
    # Ground truth over self-report: re-run the tests ourselves.
    try:
        t = subprocess.run(["python3", "test_stats.py"], cwd=d,
                           capture_output=True, text=True, timeout=30)
        tests_ok = "PASS-ALL" in t.stdout
    except Exception as ex:
        tests_ok, t = False, None
        detail = "test rerun failed: %s" % ex
    tests_edited = open(os.path.join(d, "test_stats.py")).read() != test_hash_before
    if not completed:
        return "ERROR", detail
    if tests_edited:
        return "FAIL", "test file edited -- gate refused"
    if tests_ok and cost == 0:
        return "PASS", "debugged, tests PASS-ALL, totalCost=0"
    if tests_ok:
        return "BILLABLE", "tests pass but totalCost=%s" % cost
    return "FAIL", "completed but tests still fail"


def cmd_list():
    print("== 1: cline-free promo (usage billing) ==")
    for mid, name in cline_free_ids():
        print("  %-50s %s" % (mid, name))
    print("== 2: openrouter :free in cline billing catalog ==")
    for mid, name in cline_catalog_free_ids():
        print("  %-50s %s" % (mid, name[:60]))
    print("== 3: openrouter direct (reference only; billing via cline above) ==")
    for mid, name in openrouter_free_ids():
        print("  %-50s %s" % (mid, name))
    print("== 4: local LM Studio (coordinator-reserved) ==")
    for m in local_models()[0]:
        print("  %s" % m)


def cmd_status():
    led = load_ledger()
    print("ledger: %s" % led.get("updated", "never"))
    for mid in sorted(led.get("probed", {})):
        r = led["probed"][mid]
        stale = " [OLD-TASK]" if r["verdict"] in ("PASS", "BILLABLE") \
            and r.get("task", "trivial-v0") != PROBE_TASK else ""
        print("  %-50s %-8s %s [%s]%s" % (mid, r["verdict"], r["detail"][:70], r.get("ts", "?"), stale))


def cmd_probe():
    led = load_ledger()
    probed = led.setdefault("probed", {})
    # Two candidate surfaces, both billed through Cline usage at $0: the
    # 4 promo ids and the OpenRouter :free ids in the billing catalog.
    cands = list(dict.fromkeys(
        [mid for mid, _ in cline_free_ids()]
        + [mid for mid, _ in cline_catalog_free_ids()]))
    for mid in cands:
        r = probed.get(mid)
        if r and r["verdict"] in ("PASS", "BILLABLE") and r.get("task") == PROBE_TASK:
            continue  # fresh coding verdict already on record
        if r and r["verdict"] == "DRY":
            continue  # refill schedule; recheck will probe under current task
        print("probing %-50s ..." % mid, flush=True)
        v, d = probe_cline_model(mid)
        probed[mid] = {"verdict": v, "detail": d, "task": PROBE_TASK,
                       "ts": time.strftime("%Y-%m-%d %H:%M")}
        print("  -> %s %s" % (v, d))
        save_ledger(led)
    print("done. Only PASS + totalCost=0 on task %s are coding candidates." % PROBE_TASK)
    cmd_status()


def cmd_recheck():
    """Re-probe ONLY the models the ledger still marks DRY (operator 2026-10-10:
    free buckets reset ~every 24h, so a dry verdict is a schedule, not a
    verdict). PASS/BILLABLE are never re-probed. A flip to PASS posts a
    dashboard note naming the model so the GROUP_MODEL revert is visible
    without reading the ledger; still-dry models stay DRY with a fresh
    countdown.
    """
    led = load_ledger()
    probed = led.setdefault("probed", {})
    dry = [mid for mid, r in sorted(probed.items()) if r["verdict"] == "DRY"]
    if not dry:
        print("no DRY models in ledger; nothing to recheck")
        return
    flipped, still_dry = [], []
    for mid in dry:
        print("rechecking %-50s ..." % mid, flush=True)
        v, d = probe_cline_model(mid)
        probed[mid] = {"verdict": v, "detail": d, "task": PROBE_TASK,
                       "ts": time.strftime("%Y-%m-%d %H:%M")}
        print("  -> %s %s" % (v, d))
        save_ledger(led)
        (flipped if v == "PASS" else still_dry).append(mid)
    if flipped:
        # No action needed on refill: model_for() reads this ledger at spawn
        # time, so the next spawn of each flipped model's groups returns to
        # the standing GROUP_MODEL assignment automatically.
        note = ("freemium recheck: REFILLED %s -- its groups return to the "
                "standing GROUP_MODEL assignment at the next spawn, no edit "
                "needed" % ", ".join(flipped))
        subprocess.run([sys.executable,
                        os.path.join(ROOT, "scripts/orchestration/dashboard-note.py"),
                        "--who", "coordinator", "--level", "done", note],
                       check=False)
    if still_dry:
        note = "freemium recheck: still DRY %s" % ", ".join(still_dry)
        subprocess.run([sys.executable,
                        os.path.join(ROOT, "scripts/orchestration/dashboard-note.py"),
                        "--who", "coordinator", "--level", "warn", note],
                       check=False)
    print("recheck done.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"list": cmd_list, "probe": cmd_probe, "recheck": cmd_recheck}.get(cmd, cmd_status)()
