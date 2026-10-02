#!/usr/bin/env python3
"""ALWAYS ON ao-build-update: pinned-vs-stable drift report.

Answers the question the inventory exists to answer: for every managed item,
what is pinned on this host, and what does upstream currently release as
stable? A difference is a DRIFT finding that needs a human decision; equality
is the desired state.

This script is strictly read-only. It resolves, compares, and reports. It never
pulls an image, never installs a package, and never restarts anything. Promotion
is `promote-image-digest.sh`, a separate and explicit step.

COMPARISON IS LIKE-FOR-LIKE
---------------------------
A pinned digest is a *manifest list* digest (what `podman pull` records in
`.Digest` and `RepoDigests`). `podman manifest inspect --verbose` exposes only
per-platform digests, so it is NOT a valid comparison and would report drift for
every image. This resolves the list digest from the registry's
`Docker-Content-Digest` response header, which is the same kind of value.

Usage:
  drift-report.py [--markdown] [--out FILE] [--offline]

  --offline  skip all network resolution; report pinned state and mark every
             upstream column UNKNOWN. Useful for a host with no egress.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

AO_ROOT = Path(os.environ.get("AO_ROOT", "/ALWAYSON"))
QUADLET = AO_ROOT / "quadlet"

DEFAULT_STABLE_TAG = "latest"
MANIFEST_ACCEPT = ", ".join([
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
])
TIMEOUT = 20

# ---------------------------------------------------------------------------
# STABLE REFERENCE POLICY - the data behind "released as stable by the repo"
# ---------------------------------------------------------------------------
# This lives in data, not in code, because it is a POLICY decision and it is
# meant to be argued about and edited without touching Python.
#
#   tracked_tag: a release the host INTENDS to be on. pinned != tracked_tag is a
#     real DRIFT and needs a human decision.
#   major_series: the major version the host is deliberately held at. When
#     upstream's `latest` has moved to a NEW major, the row is reported as
#     BEHIND LATEST, which is information rather than a defect: promoting would
#     be a major version change, not an update.
#   None means no declared stable channel exists for that image, so the
#   comparison falls back to `latest` and is reported as BEHIND LATEST.
#
# Populated from what the project actually runs, not from every image on the
# internet. Verify the tags exist before trusting a row.

# Hosts whose name in a reference differs from the registry API hostname.
REGISTRY_API = {
    "docker.io": "registry-1.docker.io",
    "index.docker.io": "registry-1.docker.io",
    "ghcr.io": "ghcr.io",
    "quay.io": "quay.io",
}
TOKEN_URL = {
    "docker.io": ("https://auth.docker.io/token?service=registry.docker.io&scope=repository:{repo}:pull", None),
    "ghcr.io": ("https://ghcr.io/token?scope=repository:{repo}:pull", None),
    "quay.io": ("https://quay.io/v2/auth?service=quay.io&scope=repository:{repo}:pull", None),
}


def load_untracked():
    """The untracked: list of the policy file, for deliberate-pattern matching."""
    path = AO_ROOT / "config/build-update/stable-refs.yaml"
    if not path.exists():
        return []
    out, in_list = [], False
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        st = line.strip()
        if indent == 0:
            in_list = (st == "untracked:")
            continue
        if in_list and st.startswith("- pattern:"):
            out.append({"pattern": st.split(":", 1)[1].strip().strip("\"'")})
    return out


def load_stable_refs():
    """Read config/build-update/stable-refs.yaml into {repo: {attr: value}}.

    A hand parser rather than PyYAML: this runs against a minimal image and the
    file shape is fixed by schema_version. Parsed by indentation - a two-space
    indent is an image key, a deeper indent is one of its attributes.

    It fails loudly rather than returning {} on an unrecognised shape, because
    an empty policy silently turns every DRIFT into a BEHIND LATEST and hides
    the one real finding.
    """
    path = AO_ROOT / "config/build-update/stable-refs.yaml"
    if not path.exists():
        raise SystemExit(f"ERROR: stable-reference policy not found: {path}")
    images, cur, in_images = {}, None, False
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        s = line.strip()
        if indent == 0:
            in_images = (s == "images:")
            cur = None
            continue
        if not in_images:
            continue
        if indent == 2 and s.endswith(":"):
            cur = s[:-1]
            images[cur] = {}
        elif cur and indent >= 4 and ":" in s:
            k, _, v = s.partition(":")
            v = v.strip().strip("\"'")
            images[cur][k.strip()] = None if v in ("null", "~", "") else v
    if not images:
        raise SystemExit(f"ERROR: no image entries parsed from {path}")
    return images


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run(cmd, timeout=30):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return p.returncode, p.stdout, p.stderr
    except (subprocess.TimeoutExpired, OSError) as e:
        return 127, "", str(e)


# Docker short names used by units in this repo. A reference like "postgres@sha256:.."
# has no registry prefix at all, so it must be expanded before any registry call.
# "library/" is Docker Hub's implicit namespace for single-segment official images.
SHORT_NAME_REPO = {
    "postgres": "library/postgres",
    "redis": "library/redis",
    "python": "library/python",
    "alpine": "library/alpine",
    "ubuntu": "library/ubuntu",
    "nginx": "library/nginx",
    "node": "library/node",
    "openjdk": "library/openjdk",
}


def parse_ref(ref: str):
    """(registry, repo, tag_or_digest) from a possibly short image reference.

    Docker short names are expanded to docker.io/<repo> so that every reference
    reaching the registry layer is fully qualified. A short name that cannot be
    resolved is returned as-is and will surface as an explicit unresolved row
    rather than being silently skipped.
    """
    if "@" in ref:
        base, digest = ref.split("@", 1)
        host, sep, repo = base.partition("/")
        if not sep:
            # single segment: an official Docker Hub image ("postgres@sha256:..")
            host, repo = "docker.io", SHORT_NAME_REPO.get(host, f"library/{host}")
        elif host not in REGISTRY_API:
            # first segment is a Docker Hub namespace, not a hostname
            # ("opendronemap/nodeodm@sha256:..")
            host, repo = "docker.io", base
        return host, repo, digest

    host, sep, rest = ref.partition("/")
    if not sep:
        return "docker.io", SHORT_NAME_REPO.get(host, f"library/{host}"), "latest"
    # A first segment that is not a known registry is a Docker Hub namespace
    # ("opendronemap/nodeodm"), not a hostname. Treating it as a registry was
    # the reason those rows could never resolve.
    if host not in REGISTRY_API:
        return "docker.io", ref if "@" not in ref else ref.split("@")[0], "latest"
    repo, has_tag = rest.rpartition(":")
    if not repo or "/" in has_tag:
        repo, tag = rest, "latest"
    else:
        tag = has_tag
    return host, repo, tag


def registry_digest(host: str, repo: str, tag: str):
    """Resolve a tag to its manifest-list digest via the registry API.

    Returns (digest, note). digest is None when it could not be resolved; note
    then says why. Never raises, so one unreachable registry cannot abort the
    report.
    """
    api = REGISTRY_API.get(host)
    if api is None:
        return None, f"no API mapping for {host}"

    tmpl = TOKEN_URL.get(host, (None, None))[0]
    token = None
    if tmpl:
        url = tmpl.format(repo=repo)
        try:
            with urllib.request.urlopen(url, timeout=TIMEOUT) as r:
                token = json.loads(r.read().decode()).get("token")
        except (urllib.error.URLError, OSError, ValueError, TimeoutError) as e:
            return None, f"token request failed: {getattr(e, 'reason', e)}"
        if not token:
            return None, "registry returned no token"

    url = f"https://{api}/v2/{repo}/manifests/{tag}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Accept", MANIFEST_ACCEPT)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            digest = r.headers.get("Docker-Content-Digest")
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code} for {host}/{repo}:{tag}"
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        return None, f"unreachable: {getattr(e, 'reason', e)}"
    except Exception as e:  # never let one registry abort the whole report
        return None, f"{type(e).__name__}: {e}"
    if not digest:
        return None, "registry returned no Docker-Content-Digest header"
    return digest, None


# ---------------------------------------------------------------------------
# sources
# ---------------------------------------------------------------------------
def collect_containers():
    """Every Image= line in the quadlet tree, with its domain."""
    out = []
    for f in sorted(QUADLET.glob("*/*.container")):
        domain = f.parent.name
        unit = f.stem
        ref = ""
        for line in f.read_text().splitlines():
            if line.startswith("Image="):
                ref = line.split("=", 1)[1].strip()
                break
        out.append({"domain": domain, "unit": unit, "ref": ref, "path": str(f)})
    return out


def collect_apt():
    """installed version for every package, plus the drift set.

    Performance matters here: the host has ~4500 packages and `apt-cache policy`
    per package would be 4500 subprocesses. Instead the installed version comes
    from a single parse of the dpkg status file, and the drift set comes from a
    single `apt list --upgradable`. Only the (small) drift set is then resolved
    to a repository.
    """
    # 1. installed versions, one file read
    installed = {}
    status = Path("/var/lib/dpkg/status")
    if status.exists():
        for block in status.read_text(errors="replace").split("\n\n"):
            if "Status: install ok installed" not in block:
                continue
            name = ver = None
            for line in block.splitlines():
                if line.startswith("Package: "):
                    name = line[9:].strip()
                elif line.startswith("Version: "):
                    ver = line[9:].strip()
            if name and ver:
                installed[name] = ver

    # 2. drift set, one call
    _, out, _ = run(["apt", "list", "--upgradable"], timeout=120)
    drifted = []
    seen = {}
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("Listing"):
            continue
        if "[upgradable from:" not in line:
            continue
        # A line is: pkg/suite,suite VERSION ARCH [upgradable from: OLD]
        # Three fields follow the package, not two, so the arch must be
        # consumed or the bracket never matches.
        m = re.match(r"^([^/]+)/\S+\s+\S+\s+\S+\s+\[upgradable from:\s*([^\]]+)\]", line)
        if m:
            name = m.group(1)
            # `apt list --upgradable` emits one line per ARCHITECTURE, so a
            # multi-arch package (gstreamer1.0-plugins-good on amd64 AND i386)
            # appears twice with identical versions. Keyed on package name, that
            # double-counted the package and reported 5 pending where there were
            # 4 distinct packages. Keep one row per package.
            if name in seen:
                seen[name]["architectures"].add(line.split()[2] if len(line.split()) > 2 else "?")
                continue
            seen[name] = {"package": name, "installed": m.group(2),
                          "architectures": {line.split()[2] if len(line.split()) > 2 else "?"}}
            drifted.append(seen[name])

    # 3. resolve repository for the drift set only
    for r in drifted:
        _, pol, _ = run(["apt-cache", "policy", r["package"]], timeout=20)
        cand = origin = suite = None
        for line in pol.splitlines():
            s = line.strip()
            if s.startswith("Candidate:"):
                cand = s.split(":", 1)[1].strip()
            elif re.match(r"^\d+\s+https?://", s):
                f_ = s.split()
                if origin is None:
                    origin, suite = f_[1], (f_[2] if len(f_) > 2 else "")
        r["candidate"] = cand
        r["origin"] = origin
        r["suite"] = suite
        r["drift"] = True

    return installed, drifted


def collect_snap():
    rc, out, _ = run(["snap", "list"], timeout=45)
    if rc != 0:
        return []
    rows = []
    for line in out.splitlines()[1:]:
        f = line.split()
        if len(f) < 4:
            continue
        rows.append({"name": f[0], "version": f[1], "rev": f[2], "channel": f[3]})
    return rows



def collect_flatpak():
    rc, out, _ = run(["flatpak", "list", "--app",
                      "--columns=application,version,branch,origin"], timeout=60)
    if rc != 0:
        return []
    rows = []
    for line in out.splitlines():
        f = line.split("\t")
        if len(f) < 4:
            continue
        rows.append({"app": f[0], "version": f[1], "branch": f[2], "origin": f[3]})
    return rows


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------
def build(as_md: bool, offline: bool):
    lines = []
    w = lines.append

    if as_md:
        w("# ALWAYS ON — Pinned vs Stable")
        w("")
        w(f"> Generated `{now_utc()}` by `scripts/build-update/drift-report.py`.")
        w("")
        w("> Read-only. This resolves and compares; it never pulls, installs, or restarts.")
        w("> Promotion is a separate, explicit step (`promote-image-digest.sh`).")
        w("")
        w("Two verdicts mean different things, and the difference matters:")
        w("")
        w("- **DRIFT** — behind a *tracked release tag* (Mastodon `v4.3.7`). The host")
        w("  intends to be on that release, so this is a real finding.")
        w("- **BEHIND LATEST** — the upstream `latest` tag has moved. This is **usually")
        w("  not a defect**: an image deliberately held at an older major (Postgres 17")
        w("  while `latest` is 18) reports exactly this. Treat it as information, not")
        w("  as a to-do. Promoting to `latest` would be a MAJOR version change.")
        w("")
        w("Neither verdict is an instruction to update. A bump may be a major version,")
        w("a schema change, or a rebuild with no upstream equivalent.")
        w("")
    else:
        w(f"ALWAYS ON - pinned vs stable   {now_utc()}")
        w("")

    STABLE = load_stable_refs()
    UNTRACKED = load_untracked()
    summary = {"in_sync": 0, "drift": 0, "unresolved": 0, "local": 0,
               "unpinned": 0, "behind_latest": 0, "behind_tracked": 0,
               "held": 0}
    containers = collect_containers()
    verdicts = []

    # ---- containers ------------------------------------------------------
    w("## 1. Container images" if as_md else "\n=== 1. CONTAINER IMAGES ===")
    w("")
    if as_md:
        w("| Unit | Domain | Pinned digest | Upstream stable | Verdict |")
        w("|---|---|---|---|---|")
    else:
        w(f"{'UNIT':<32} {'PINNED':<20} {'UPSTREAM':<20} VERDICT")

    for c in containers:
        ref, name, up = c["ref"], c["unit"], "-"
        if not ref:
            verdict, pinned = "NO Image= LINE", "-"
            summary["unpinned"] += 1
        elif ref.startswith("localhost/"):
            verdict, pinned = "LOCAL BUILD (no upstream)", ref
            summary["local"] += 1
        elif "@" not in ref:
            # A floating tag. Whether that is a defect depends on intent: an
            # operator may want the most recent build, in which case pinning it
            # would be WRONG. Intent lives in the untracked: list of the policy
            # file, so the report reflects the decision rather than a rule.
            pinned = ref
            if any(ref.startswith(u.get("pattern", "\0")) for u in UNTRACKED):
                verdict = "UNPINNED BY CHOICE (operator wants latest)"
                summary["unpinned_choice"] = summary.get("unpinned_choice", 0) + 1
            else:
                verdict = "NOT PINNED (floating tag)"
                summary["unpinned"] += 1
        else:
            host, repo, pinned = parse_ref(ref)
            key = f"{host}/{repo}"
            policy = STABLE.get(key, {})
            tracked = policy.get("tracked_tag")
            compare_tag = tracked or DEFAULT_STABLE_TAG
            if offline:
                up, verdict = "-", "NOT CHECKED (offline)"
                summary["unresolved"] += 1
            else:
                up, err = registry_digest(host, repo, compare_tag)
                if up is None:
                    up, verdict = "-", f"UNRESOLVED: {err}"
                    summary["unresolved"] += 1
                elif up == pinned:
                    verdict = "IN SYNC"
                    summary["in_sync"] += 1

                elif policy.get("held_digest") == pinned:
                    # The operator has explicitly accepted THIS pinned digest.
                    # Compare against the PINNED value, not the upstream one:
                    # the whole point of a hold is that upstream differs. Being
                    # behind is expected and accepted, so it is not a finding.
                    verdict = f"HELD (operator-accepted, tracking {tracked})"
                    summary["held"] = summary.get("held", 0) + 1
                elif tracked and policy.get("tag_kind") == "release":
                    # A precise release the host intends to be on, and it is not
                    # on it. Unambiguously a finding.
                    verdict = f"DRIFT (release {tracked})"
                    summary["drift"] += 1
                elif tracked:
                    # A ROLLING major tag (postgres:17, redis:7). These are
                    # rebuilt for security patches, so a mismatch means a newer
                    # patch of the same major is available. Actionable, but it is
                    # not a version decision and must not be read as one.
                    verdict = f"BEHIND TRACKED TAG ({tracked}, rolling: newer patch of same major)"
                    summary["behind_tracked"] = summary.get("behind_tracked", 0) + 1
                else:
                    # No declared stable channel. Upstream `latest` moved. For an
                    # image held at an older major this is expected; for a
                    # rebuilt base tag it is routine. Information, not action.
                    verdict = "BEHIND LATEST (no tracked release tag)"
                    summary["behind_latest"] = summary.get("behind_latest", 0) + 1

        verdicts.append({"unit": name, "domain": c["domain"], "ref": ref,
                         "pinned": pinned, "upstream": up, "verdict": verdict})
        sp = str(pinned).split(":")[-1][:16]
        su = str(up).split(":")[-1][:16]
        if as_md:
            w(f"| `{name}` | {c['domain']} | `{sp}` | `{su}` | {verdict} |")
        else:
            w(f"{name:<32} {sp:<20} {su:<20} {verdict}")

    # ---- apt -------------------------------------------------------------
    apt_installed, drift_apt = collect_apt()
    if as_md:
        w("")
        w("## 2. APT packages")
        w("")
        w(f"`{len(apt_installed)}` packages installed, `{len(drift_apt)}` differ from the current")
        w("`Candidate`. Policy: `-security` installs unattended; `-updates` and")
        w("third-party repositories wait for an operator decision.")
        w("")
        if drift_apt:
            w("| Package | Installed | Candidate | Repository |")
            w("|---|---|---|---|")
            for r in sorted(drift_apt, key=lambda x: x["package"])[:100]:
                w(f"| `{r['package']}` | `{r['installed']}` | `{r['candidate']}` | "
                  f"{r['origin'] or '-'} {r['suite'] or ''} |")
        else:
            w("No drift: every installed package matches its `Candidate`.")
    else:
        w("")
        w(f"=== 2. APT: {len(apt_installed)} packages, {len(drift_apt)} differ from Candidate ===")
        for r in sorted(drift_apt, key=lambda x: x["package"])[:40]:
            w(f"  {r['package']}: {r['installed']} -> {r['candidate']}  [{r['origin']}]")

    # ---- snap ------------------------------------------------------------
    snaps = collect_snap()
    _, refresh, _ = run(["snap", "refresh", "--list"], timeout=60)
    pending = [l.strip() for l in refresh.splitlines()
               if l.strip() and "up to date" not in l.lower()]
    if as_md:
        w("")
        w("## 3. Snap")
        w("")
        w(f"`{len(snaps)}` snaps installed. snapd refreshes these **unattended** — the one")
        w("category on this host that updates itself.")
        w("")
        w("Pending refresh:" if pending else "No pending refreshes: every snap is at its channel revision.")
        for p in pending[:25]:
            w(f"- `{p}`")
    else:
        w("")
        w(f"=== 3. SNAP: {len(snaps)} installed, {len(pending)} pending ===")
        for p in pending[:20]:
            w(f"  {p}")

    # ---- flatpak ---------------------------------------------------------
    apps = collect_flatpak()
    if as_md:
        w("")
        w("## 4. Flatpak")
        w("")
        w(f"`{len(apps)}` applications. `flatpak-system.timer` is **not installed**, so these")
        w("do not update themselves.")
        w("")
        w("| Application | Version | Branch | Origin |")
        w("|---|---|---|---|")
        for a in apps:
            w(f"| `{a['app']}` | `{a['version']}` | {a['branch']} | {a['origin']} |")
    else:
        w("")
        w(f"=== 4. FLATPAK: {len(apps)} apps (no auto-update timer) ===")
        for a in apps:
            w(f"  {a['app']} {a['version']} [{a['branch']}] {a['origin']}")

    # ---- summary ---------------------------------------------------------
    w("")
    if as_md:
        w("---")
        w("")
        w("## Summary")
        w("")
        w("| Outcome | Count | Meaning |")
        w("|---|---|---|")
        w(f"| IN SYNC | {summary['in_sync']} | Pinned digest equals upstream stable. Leave alone. |")
        w(f"| **DRIFT** | **{summary['drift']}** | Behind a tracked release tag. Needs a decision. |")
        w(f"| HELD | {summary.get('held', 0)} | Deliberately held at this digest by operator decision. Not a finding. |")
        w(f"| BEHIND TRACKED TAG | {summary['behind_tracked']} | Newer **patch of the same major** is out (rolling tag). Safe to take; not a version decision. |")
        w(f"| BEHIND LATEST | {summary['behind_latest']} | No tracked release tag exists for this image, so `latest` is all there is. **Not a defect.** |")
        w(f"| UNRESOLVED | {summary['unresolved']} | Registry did not answer. Retry or investigate. |")
        w(f"| LOCAL BUILD | {summary['local']} | Built on this host; no upstream to compare. |")
        w(f"| UNPINNED BY CHOICE | {summary.get('unpinned_choice', 0)} | Floating tag the operator WANTS (most recent). Not a defect. |")
        w(f"| **NOT PINNED** | **{summary['unpinned']}** | Floating tag or missing `Image=`, not chosen. A finding. |")
        w("")
        w("## Keeping this current")
        w("")
        w("```bash")
        w("# regenerate")
        w("/ALWAYSON/scripts/build-update/drift-report.py --markdown \\")
        w("  --out /ALWAYSON/docs/drift.md")
        w("")
        w("# apply one decision")
        w("/ALWAYSON/scripts/build-update/promote-image-digest.sh <domain> <unit>.container <ref>")
        w("```")
        w("")
        w("Run it after a promotion, before deciding an `apt upgrade`, and any time you")
        w("want to know whether the host is behind. It is read-only, so running it costs")
        w("nothing and changes nothing.")
    else:
        w("")
        w("=== SUMMARY ===")
        w(f"  in sync    {summary['in_sync']}")
        w(f"  DRIFT      {summary['drift']}")
        w(f"  behind-latest {summary['behind_latest']}")
        w(f"  unresolved {summary['unresolved']}")
        w(f"  local      {summary['local']}")
        w(f"  unpinned   {summary['unpinned']}")

    return "\n".join(lines) + "\n", summary, apt_installed, drift_apt, snaps, apps, verdicts


def main() -> int:
    ap = argparse.ArgumentParser(description="Pinned vs stable drift report (read-only).")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--offline", action="store_true",
                    help="skip network resolution; mark upstream UNKNOWN")
    args = ap.parse_args()

    text, summary, apt_installed, drift_apt, snaps, apps, verdicts = build(
        args.markdown, args.offline)

    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(p)
        print(f"wrote {p}")
        side = AO_ROOT / "data/build-update/drift.json"
        try:
            side.parent.mkdir(parents=True, exist_ok=True)
            side.write_text(json.dumps({
                "generated": now_utc(), "summary": summary,
                "apt_package_count": len(apt_installed),
                "apt_drift": [{**r, "architectures": sorted(r.get("architectures", []))} for r in drift_apt],
                "snaps": snaps, "flatpaks": apps, "containers": verdicts,
            }, indent=2, sort_keys=True), encoding="utf-8")
            print(f"wrote {side}")
        except OSError as e:
            print(f"note: sidecar not written: {e}", file=sys.stderr)
    else:
        print(text)

    # Non-zero when a human is needed, so this can later gate a pipeline.
    if summary["drift"] or summary["unpinned"] or summary["unresolved"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
