#!/usr/bin/env node
/**
 * ALWAYS ON - validation: loopback service reachability through a real browser.
 *
 * Drives Google Chrome via Playwright and loads every service listed in
 * config/platform/loopback-services.yaml, asserting a real HTTP status and a
 * real content marker.
 *
 * WHY A BROWSER AND NOT curl
 *   curl proves a socket accepts bytes. It cannot prove a page renders, or that
 *   the right application is answering. That distinction matters here: Mastodon's
 *   :3000 origin correctly issues "301 -> https://127.0.0.1:3000/" where no TLS
 *   listener exists, so an HTTPS probe there fails while the service is healthy.
 *   Loading the page is what separates "listening" from "serving".
 *
 * CHROME IS LAUNCHED THROUGH A WRAPPER - DO NOT "SIMPLIFY" THIS
 *   The `google-chrome` on PATH is NOT the browser. It is a wrapper that sets
 *   XDG_CACHE_HOME=/home/scottw/.cache/chrome and execs the real binary. The
 *   isolation is load-bearing: Chrome writes fontconfig cache format v12 while
 *   this host's fontconfig 2.17.1 reads v9. Without the override, fontconfig
 *   follows back-link symlinks into v12 data and plasmashell SIGSEGVs in
 *   FcCharSetHasChar / QFontEngineMultiFontConfig, taking the desktop to a black
 *   screen with no panel and a broken lock screen.
 *
 *   channel:"chrome" is used because ~/.cache/ms-playwright holds only Firefox
 *   and ffmpeg. There is no bundled Chromium, and the system install is used
 *   rather than pulling ~150 MB of duplicate browser.
 *
 * EXIT CODES
 *   0  all verifiable services passed
 *   40 one or more services failed
 *   10 configuration or precondition error
 */
"use strict";

const fs = require("fs");
const net = require("net");
const os = require("os");
const path = require("path");
const { spawn, spawnSync } = require("child_process");

const AO_ROOT = process.env.AO_ROOT || "/ALWAYSON";
const INVENTORY = path.join(AO_ROOT, "config/platform/loopback-services.yaml");
const QUADLET_DIR = path.join(AO_ROOT, "quadlet");
const CHROME_WRAPPER = path.join(os.homedir(), ".local/bin/google-chrome");
const SCREENSHOT_DIR = "/tmp/ao-local-services";
const NAV_TIMEOUT_MS = 20000;

const PASS = "PASS", FAIL = "FAIL", UNVERIFIABLE = "UNVERIFIABLE";

function log(m) { process.stderr.write(`check-local-services: ${m}\n`); }


function loadInventory() {
  // Parsing is delegated to Python's PyYAML (already a dependency of this
  // project) rather than hand-rolled. Two hand-written YAML loaders were tried
  // here and both were wrong: the first discarded the nested meta block, and
  // the second collapsed the services list into a single object. A real parser
  // is the correct tool; Node is kept for what it is uniquely good at here,
  // driving the browser.
  const res = spawnSync("python3", ["-c", PY_YAML_READER, INVENTORY], {
    encoding: "utf8", maxBuffer: 8 * 1024 * 1024,
  });
  if (res.status !== 0) {
    log(`ERROR: could not parse ${INVENTORY}`);
    if (res.stderr) log(res.stderr.trim().split("\n").slice(0, 3).join(" "));
    return null;
  }
  let data;
  try { data = JSON.parse(res.stdout); }
  catch (e) { log(`ERROR: inventory did not yield valid JSON: ${e.message}`); return null; }
  if (!data || !data.services || !data.services.length) {
    log("ERROR: inventory lists no services");
    return null;
  }
  return data;
}

const PY_YAML_READER = [
  "import json, sys, yaml",
  "with open(sys.argv[1], encoding='utf-8') as fh:",
  "    sys.stdout.write(json.dumps(yaml.safe_load(fh)))",
].join("\n");


function checkDrift(data) {
  const declared = new Set(
    (((data.meta || {}).published_by_quadlet) || []).map((e) => e.port)
  );
  const actual = new Set();
  // Match the CONTAINER port (group 2), not the host port. ao-sales-db
  // publishes 127.0.0.1:15432:5432, and 15432 is a loopback alias of
  // PostgreSQL, which is a database, not an HTTP service. Using host ports
  // reported those as missing web services.
  const re = /^PublishPort=127\.0\.0\.1:(\d+):(\d+)/;
  const WEB = new Set(["3000", "4000", "3001", "3002", "9090"]);
  const walk = (dir) => {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) walk(p);
      else if (e.name.endsWith(".container")) {
        for (const line of fs.readFileSync(p, "utf8").split("\n")) {
          const m = line.trim().match(re);
          if (m && WEB.has(m[2])) actual.add(parseInt(m[1], 10));
        }
      }
    }
  };
  if (fs.existsSync(QUADLET_DIR)) walk(QUADLET_DIR);
  let clean = true;
  for (const port of [...actual].sort((a, b) => a - b)) {
    if (!declared.has(port)) { log(`DRIFT: port ${port} is published by a Quadlet unit but is not in the inventory`); clean = false; }
  }
  for (const port of [...declared].sort((a, b) => a - b)) {
    if (!actual.has(port)) { log(`DRIFT: inventory lists port ${port} as Quadlet-published but no unit publishes it`); clean = false; }
  }
  return clean;
}

function tcpOk(host, port) {
  return new Promise((resolve) => {
    const sock = new net.Socket();
    const done = (v) => { sock.destroy(); resolve(v); };
    sock.setTimeout(2000);
    sock.once("connect", () => done(true));
    sock.once("timeout", () => done(false));
    sock.once("error", () => done(false));
    sock.connect(port, host);
  });
}

async function preflight(services) {
  try { require(resolvePlaywright()); }
  catch (e) {
    log("ERROR: playwright not resolvable. Looked in the npx cache.");
    log("       Install with: npm i -g playwright  (browsers not needed; system Chrome is used)");
    return false;
  }
  if (!fs.existsSync(CHROME_WRAPPER)) {
    log(`ERROR: Chrome wrapper missing at ${CHROME_WRAPPER}`);
    log("       The wrapper provides the fontconfig isolation this host requires.");
    return false;
  }
  for (const svc of services) {
    if (svc.verifiable === false) continue;
    if (svc.start_with_check) continue; // started by checkOne just before use
    const u = new URL(svc.url);
    const port = parseInt(u.port || (u.protocol === "https:" ? "443" : "80"), 10);
    if (!(await tcpOk(u.hostname, port))) {
      log(`ERROR: nothing listening on ${u.hostname}:${port} for ${svc.name}`);
      return false;
    }
  }
  return true;
}

function resolvePlaywright() {
  const npx = path.join(os.homedir(), ".npm/_npx");
  if (fs.existsSync(npx)) {
    for (const d of fs.readdirSync(npx)) {
      const cand = path.join(npx, d, "node_modules/playwright");
      if (fs.existsSync(cand)) return cand;
    }
  }
  for (const cand of ["playwright", "playwright-core"]) {
    try { return require.resolve(cand); } catch (e) { /* keep looking */ }
  }
  return "playwright";
}

/**
 * Start a service that is run on demand rather than deployed as a unit.
 *
 * scripts/operations/web-console-server.py has no systemd or Quadlet unit, so
 * nothing has it listening. The preflight TCP check would otherwise abort the
 * whole run with "nothing listening". This starts it, waits for the port, and
 * records the child so it can be stopped again, leaving no stray process.
 */
function startOnDemand(svc) {
  const cfg = svc.start_with_check;
  if (!cfg) return null;
  // spawn() takes the program and its arguments separately and does NOT parse
  // a command string. Passing the whole string as the program gave
  // ENOENT: spawn python3 scripts/... 8099 ENOENT. Split it properly, and
  // resolve a relative script path against cwd so the child can find it.
  const parts = String(cfg.command).trim().split(/\s+/);
  const prog = parts[0];
  const args = parts.slice(1);
  const child = spawn(prog, args, { cwd: cfg.cwd || AO_ROOT, detached: false, stdio: "ignore" });
  // Without a listener, a failed spawn is an unhandled 'error' event that
  // kills the whole run rather than failing just this one service.
  child.on("error", (e) => log(`WARN ${svc.name}: could not start (${e.code || e.message})`));
  const u = new URL(svc.url);
  const port = parseInt(u.port || "80", 10);
  return new Promise((resolve) => {
    const deadline = Date.now() + 10000;
    const poll = async () => {
      if (Date.now() > deadline) { log(`WARN ${svc.name}: did not start listening on ${port}`); return resolve(child); }
      if (await tcpOk(u.hostname, port)) return resolve(child);
      await new Promise((r) => setTimeout(r, 400));
      poll();
    };
    poll();
  });
}

function stopOnDemand(child) {
  if (child && !child.killed) { try { child.kill("SIGTERM"); } catch (e) { /* already gone */ } }
}

async function checkOne(context, svc) {
  const name = svc.name;
  if (svc.browser_skip) {
    // No browser row at all: this entry is judged by runTransportProbes, and
    // returning a placeholder here made :3000 appear twice in the report.
    log(`SKIP ${name} (${svc.url}) - judged by the transport probe, not the browser`);
    return null;
  }
  if (svc.verifiable === false) {
    const reason = (svc.reason || "").replace(/\s+/g, " ").trim();
    log(`UNVERIFIABLE ${name} (${svc.url}) - ${reason}`);
    return { name, url: svc.url, status: UNVERIFIABLE, detail: reason };
  }
  const started = await startOnDemand(svc);
  const page = await context.newPage();
  let response = null;
  try {
    response = await page.goto(svc.url, {
      timeout: svc.nav_timeout_ms || NAV_TIMEOUT_MS,
      waitUntil: svc.wait_until || "domcontentloaded",
    });
    const status = response ? response.status() : 0;
    const expected = svc.expect_status || [];
    if (!expected.includes(status)) {
      return await fail(page, svc, `status ${status} not in expected [${expected}]`);
    }
    const headers = response.headers();
    if (svc.expect_location) {
      const actual = (headers["location"] || "").trim();
      if (!actual.includes(svc.expect_location)) {
        return await fail(page, svc, `Location ${JSON.stringify(actual)} does not contain ${JSON.stringify(svc.expect_location)}`);
      }
    }
    if (svc.expect_title) {
      const title = await page.title();
      if (!title.toLowerCase().includes(String(svc.expect_title).toLowerCase())) {
        return await fail(page, svc, `title ${JSON.stringify(title)} does not contain ${JSON.stringify(svc.expect_title)}`);
      }
    }
    if (svc.expect_landing_path) {
      const finalPath = new URL(page.url()).pathname;
      if (finalPath !== svc.expect_landing_path) {
        return await fail(page, svc, `landed on ${finalPath}, expected ${svc.expect_landing_path}`);
      }
    }
    if (svc.expect_body) {
      const html = await page.content();
      if (!html.toLowerCase().includes(String(svc.expect_body).toLowerCase())) {
        return await fail(page, svc, `body does not contain ${JSON.stringify(svc.expect_body)}`);
      }
    }
    log(`PASS ${name} (${svc.url}) - HTTP ${status}`);
    return { name, url: svc.url, status: PASS, detail: `HTTP ${status}` };
  } catch (e) {
    const detail = String(e.message || e).replace(/\s+/g, " ").slice(0, 200);
    return { name, url: svc.url, status: FAIL, detail };
  } finally {
    await page.close().catch(() => {});
    if (svc.start_with_check && svc.start_with_check.stop_after) stopOnDemand(started);
  }
}

async function fail(page, svc, detail) {
  const shot = path.join(SCREENSHOT_DIR, svc.name.toLowerCase().replace(/[^a-z0-9]+/g, "-") + ".png");
  let full = detail;
  try { await page.screenshot({ path: shot }); full = `${detail} (screenshot: ${shot})`; } catch (e) { /* page may be unusable */ }
  log(`FAIL ${svc.name} (${svc.url}) - ${full}`);
  return { name: svc.name, url: svc.url, status: FAIL, detail: full };
}

/**
 * Transport-level probe for entries marked browser_skip.
 *
 * A browser cannot assert a redirect it follows itself: navigating to
 * http://127.0.0.1:3000/ makes Chrome follow the 301 to an https endpoint with
 * no TLS listener and die with net::ERR_SSL_PROTOCOL_ERROR. The 301 is a real,
 * correct fact about the origin, so it is checked here instead, by a request
 * that does not follow redirects.
 */
function runTransportProbes(services) {
  const results = [];
  for (const svc of services) {
    if (!svc.browser_skip) continue;
    const u = new URL(svc.url);
    const expected = svc.expect_status || [];
    const req = require("http").request(
      { host: u.hostname, port: u.port || 80, path: u.pathname, method: "GET",
        headers: { "Accept": "*/*" } },
      (res) => {
        res.resume();
        const status = res.statusCode;
        const location = (res.headers.location || "").trim();
        let detail, ok = true;
        if (!expected.includes(status)) { ok = false; detail = `status ${status} not in expected [${expected}]`; }
        else if (svc.expect_location && !location.includes(svc.expect_location)) {
          ok = false; detail = `Location ${JSON.stringify(location)} does not contain ${JSON.stringify(svc.expect_location)}`;
        } else { detail = `HTTP ${status}` + (location ? ` -> ${location}` : ""); }
        const out = { name: svc.name, url: svc.url, status: ok ? PASS : FAIL, detail };
        if (ok) log(`PASS ${svc.name} (${svc.url}) - ${detail}`);
        else log(`FAIL ${svc.name} (${svc.url}) - ${detail}`);
        results.push(out);
      }
    );
    req.on("error", (e) => {
      const detail = String(e.message).replace(/\s+/g, " ").slice(0, 160);
      log(`FAIL ${svc.name} (${svc.url}) - ${detail}`);
      results.push({ name: svc.name, url: svc.url, status: FAIL, detail });
    });
    req.setTimeout(10000, () => req.destroy(new Error("timeout")));
    req.end();
  }
  return results;
}

function audit(results) {
  const journal = path.join(AO_ROOT, "LOGS-JOURNALS/operations-journal.log");
  if (!fs.existsSync(path.dirname(journal))) return;
  const counts = { [PASS]: 0, [FAIL]: 0, [UNVERIFIABLE]: 0 };
  for (const r of results) counts[r.status]++;
  const stamp = new Date().toISOString().replace(/\.\d+Z$/, "+00:00");
  const lines = [`${stamp} check-local-services: ${counts[PASS]} pass, ${counts[FAIL]} fail, ${counts[UNVERIFIABLE]} unverifiable (browser: Chrome via Playwright)`];
  for (const r of results) lines.push(`    ${r.status.padEnd(12)} ${r.name.padEnd(24)} ${r.detail}`);
  fs.appendFileSync(journal, lines.join("\n") + "\n");
  log(`journaled to ${journal}`);
}

async function main() {
  const data = loadInventory();
  if (!data) return 10;
  checkDrift(data);
  if (!(await preflight(data.services))) return 10;

  const { chromium } = require(resolvePlaywright());
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  const browser = await chromium.launch({
    channel: "chrome",
    executablePath: CHROME_WRAPPER,
    headless: true,
    args: ["--disable-gpu", "--ignore-certificate-errors"],
  });
  const results = [];
  try {
    const context = await browser.newContext({ ignoreHTTPSErrors: true });
    for (const svc of data.services) {
      const r = await checkOne(context, svc);
      if (r) results.push(r);
    }
  } finally {
    await browser.close().catch(() => {});
  }

  results.push(...await new Promise((resolve) => {
    const out = runTransportProbes(data.services);
    setTimeout(() => resolve(out), 1500);
  }));

  const pad = (s, n) => String(s).padEnd(n);
  console.log("=".repeat(78));
  const nameWidth = Math.max(26, ...results.map((r) => r.name.length + 2));
  console.log(`${pad("STATUS", 13)}${pad("SERVICE", nameWidth)}URL`);
  console.log("=".repeat(78));
  for (const r of results) console.log(`${pad(r.status, 13)}${pad(r.name, nameWidth)}${r.url}`);
  const failures = results.filter((r) => r.status === FAIL);
  const unver = results.filter((r) => r.status === UNVERIFIABLE);
  console.log("-".repeat(78));
  console.log(`${results.length - failures.length - unver.length} pass, ${failures.length} fail, ${unver.length} unverifiable`);
  for (const r of unver) console.log(`  UNVERIFIABLE ${r.name}: ${r.detail}`);
  audit(results);
  if (failures.length) { console.log(`FAIL: ${failures.length} service(s) failed reachability`); return 40; }
  console.log("OK: every verifiable loopback service is reachable and serving");
  return 0;
}

main().then((c) => process.exit(c)).catch((e) => {
  log(`ERROR: ${e.message || e}`);
  process.exit(10);
});
