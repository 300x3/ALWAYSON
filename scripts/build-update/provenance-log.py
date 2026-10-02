#!/usr/bin/env python3
"""ALWAYS ON ao-build-update: complete software provenance log.

One document recording, for every piece of software on this host, WHERE IT COMES
FROM: publisher, repository, installed version, upstream version, and the exact
download link. The other reports answer "is it stale?"; this one answers "what
is it and where do I get it?" - which is the question you have to ask before you
can update anything.

READ-ONLY. Queries version endpoints and reads local state. Installs nothing,
downloads nothing, changes nothing.

Covers all five delivery mechanisms, because they each need a different kind of
"where does this come from":

    container   registry, repository, digest, and the pull reference
    snap        publisher and the snapcraft store page
    flatpak     origin remote and the flathub page
    apt         archive host, suite, component, and the package page
    direct      vendor site, version, and the download link (no feed)

Usage:
  provenance-log.py [--markdown] [--out FILE] [--html FILE] [--offline]
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
INVENTORY = AO_ROOT / "data/build-update/inventory-full.json"
UNMANAGED = AO_ROOT / "config/build-update/unmanaged-software.yaml"
TIMEOUT = 20

# Apt suites to name in the package URL.
# Apt archives, mapped to the human-facing package page for each host.
ARCHIVE_PAGES = {
    "us.archive.ubuntu.com": "https://packages.ubuntu.com/{codename}/{pkg}",
    "archive.ubuntu.com": "https://packages.ubuntu.com/{codename}/{pkg}",
    "security.ubuntu.com": "https://packages.ubuntu.com/{codename}/{pkg}",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run(cmd, timeout=30):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return p.returncode, p.stdout, p.stderr
    except (subprocess.TimeoutExpired, OSError) as e:
        return 127, "", str(e)


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "alwayson-ao-build-update"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read().decode())
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        return None


def norm(v):
    if not v:
        return ""
    m = re.search(r"(\d+(?:\.\d+)*)", str(v))
    return m.group(1) if m else ""


def load_yaml(path):
    try:
        import yaml
    except ImportError:
        sys.exit("ERROR: PyYAML required")
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


# ---------------------------------------------------------------------------
# sources
# ---------------------------------------------------------------------------
def registry_digest_raw(host, repo, tag):
    """Full manifest digest for a tag, or None. Used for tag<->digest mapping."""
    api = {"docker.io": "registry-1.docker.io", "ghcr.io": "ghcr.io",
           "quay.io": "quay.io"}.get(host)
    if api is None:
        return None
    token = None
    tok = {"docker.io": f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:{repo}:pull",
           "ghcr.io": f"https://ghcr.io/token?scope=repository:{repo}:pull"}.get(host)
    if tok:
        d = get_json(tok)
        token = d.get("token") if d else None
    req = urllib.request.Request(f"https://{api}/v2/{repo}/manifests/{tag}", method="GET")
    req.add_header("Accept", ", ".join([
        "application/vnd.oci.image.index.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.docker.distribution.manifest.v2+json"]))
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.headers.get("Docker-Content-Digest")
    except Exception:
        return None


_TAG_CACHE = {}


def _hub_tags(repo):
    """digest -> tag for a Docker Hub repo, in ONE call.

    This is what turns a pinned digest into a version a human can read: the Hub
    API returns a digest for every tag, so the pinned digest reverse-looks-up to a
    version. Grafana resolves immediately - `latest` and `13.0.2` share a digest -
    which is precisely the comparison two raw hashes hide.
    """
    if repo not in _TAG_CACHE:
        d = get_json(f"https://hub.docker.com/v2/repositories/{repo}/tags"
                     f"?page_size=100&ordering=last_updated")
        m = {}
        for r in (d or {}).get("results", []):
            if r.get("name") and r.get("digest"):
                m.setdefault(r["digest"], []).append(r["name"])
        _TAG_CACHE[repo] = m
    return _TAG_CACHE[repo]


def _ghcr_tags(repo):
    """digest -> tag for a ghcr.io repo, by resolving recent release tags."""
    if repo not in _TAG_CACHE:
        m = {}
        stable = load_yaml(AO_ROOT / "config/build-update/stable-refs.yaml").get("images") or {}
        cands = [(stable.get(repo) or {}).get("tracked_tag")]
        gh = {"ghcr.io/mastodon/mastodon": "mastodon/mastodon",
              "ghcr.io/mastodon/mastodon-streaming": "mastodon/mastodon",
              "ghcr.io/ardupilot/ardupilot-sitl": "ArduPilot/ardupilot"}
        if repo in gh:
            for r in (get_json(f"https://api.github.com/repos/{gh[repo]}/releases?per_page=6") or [])[:6]:
                if r.get("tag_name"):
                    cands.append(r["tag_name"])
        for tag in [c for c in cands if c][:6]:
            dg = registry_digest_raw("ghcr.io", repo, tag)
            if dg:
                m.setdefault(dg, []).append(tag)
        _TAG_CACHE[repo] = m
    return _TAG_CACHE[repo]


_ROLLING = {"latest", "stable", "main", "master", "edge", "nightly", "default"}


def _best_tag(tags):
    """Pick the most version-like tag from those sharing one digest.

    Several tags usually point at the same digest - `latest` and `13.0.2` are the
    same image - and picking the first one alphabetically produced nonsense such
    as "v1" for node-exporter, which is a different major entirely. Prefer a real
    dotted version, then a v-prefixed one, and fall back to a rolling alias only
    when nothing better exists.
    """
    vs = [t for t in tags if t not in _ROLLING]
    exact = [t for t in vs if re.fullmatch(r"v?\d+(\.\d+)*", t)]
    if exact:
        return max(exact, key=lambda t: [int(x) for x in t.lstrip("v").split(".")])
    prefixed = [t for t in vs if re.match(r"^v?\d+\.\d+", t)]
    if prefixed:
        return max(prefixed, key=lambda t: [int(x) for x in
                                           re.findall(r"\d+", t)[:3]] or [0])
    if vs:
        return vs[0]
    return next(iter(tags), None)


def version_for(host, repo, digest):
    """Human-readable version for a digest.

    Returns None when the publisher offers no version tag covering it. That is
    deliberate: showing a wrong version is worse than showing none, so the caller
    keeps the digest instead.
    """
    if not digest or "sha256:" not in str(digest):
        return None
    short = str(digest).split("sha256:")[-1]
    m = _ghcr_tags(repo) if host == "ghcr.io" else _hub_tags(repo)
    tags = [t for d, lst in m.items()
            if d.split("sha256:")[-1].startswith(short[:16]) for t in lst]
    return _best_tag(tags) if tags else None


def released_digest(host, repo, tag):
    """Short digest the publisher currently offers for a tag."""
    d = registry_digest_raw(host, repo, tag)
    return d[:19] if d else "-"


def containers(offline=False):
    stable = {}
    p = AO_ROOT / "config/build-update/stable-refs.yaml"
    if p.exists():
        stable = (load_yaml(p).get("images") or {})
    rows = []
    stable = {}
    p = AO_ROOT / "config/build-update/stable-refs.yaml"
    if p.exists():
        stable = (load_yaml(p).get("images") or {})
    rows = []
    for f in sorted((AO_ROOT / "quadlet").glob("*/*.container")):
        ref = next((l.split("=", 1)[1].strip() for l in f.read_text().splitlines()
                    if l.startswith("Image=")), "")
        if not ref or ref.startswith("localhost/"):
            publisher = "built on this host (ao-sim-fabrication)" if ref else "-"
            rows.append({"item": f.stem, "via": f"container/{f.parent.name}",
                         "publisher": publisher, "repo": ref or "-",
                         "pinned": "-", "released": "no upstream",
                         "download": "(local build; no upstream)", "local": True})
            continue
        if "@" in ref:
            base, digest = ref.split("@", 1)
        else:
            base, digest = ref, ""
        host, _, repo = base.partition("/")
        tag = (stable.get(f"{host}/{repo}") or {}).get("tracked_tag") or "latest"
        released = "-" if offline else released_digest(host, repo, tag)
        # Reverse-map the pinned digest to a version TAG. Without this the table
        # only ever showed two hashes, which tells a human nothing about versions.
        pin_ver = version_for(host, repo, digest) if (digest and not offline) else None
        rel_ver = version_for(host, repo, released) if (released and not offline) else None
        rows.append({
            "item": f.stem, "via": f"container/{f.parent.name}",
            "publisher": host,
            "repo": f"{host}/{repo}" if "/" in base else f"docker.io/library/{host}",
            "pinned": pin_ver or (digest[:19] if digest else "NOT PINNED"),
            "released": f"{rel_ver or released} ({tag})",
            "is_pinned": bool(digest),
            "download": f"podman pull {base}@{digest}" if digest else ref,
            "local": False, "exact": True,
        })
    return rows


def snaps(offline=False):
    rc, out, _ = run(["snap", "list"])
    if rc != 0:
        return []
    rows = []
    for line in out.splitlines()[1:]:
        f = line.split()
        if len(f) < 4:
            continue
        released = "-"
        if not offline:
            _, info, _ = run(["snap", "info", f[0]], timeout=30)
            for line in info.splitlines():
                st = line.strip()
                if st.startswith("latest/") and ":" in st:
                    # "latest/stable:  1.96.60 2026-09-30 (688) 227MB -"
                    released = st.split(":", 1)[1].split()[0]
                    break
        rows.append({"item": f[0], "via": f"snap/{f[3]}",
                     "publisher": f[5] if len(f) > 5 else "canonical",
                     "repo": "snap store",
                     "pinned": f[1], "released": released or "-", "is_pinned": True,
                     "download": f"https://snapcraft.io/{f[0]}", "local": False})
    return rows


def flatpaks(offline=False):
    rc, out, _ = run(["flatpak", "list", "--app",
                      "--columns=application,version,branch,origin"])
    if rc != 0:
        return []
    rows = []
    for line in out.splitlines():
        f = line.split("\t")
        if len(f) < 4:
            continue
        released = "-"
        if not offline:
            _, rl, _ = run(["flatpak", "remote-ls", "--columns=version", f[3], f[0]],
                           timeout=45)
            for line in rl.splitlines():
                if line.strip():
                    released = line.strip()
                    break
        rows.append({"item": f[0], "via": f"flatpak/{f[2]}",
                     "publisher": f[3], "repo": f[3],
                     "pinned": f[1], "released": released or "-", "is_pinned": True,
                     "download": f"https://flathub.org/apps/{f[0]}", "local": False})
    return rows


def apt_candidates(inv):
    """installed -> candidate, for the packages that differ.

    Candidate == installed for every package not in `apt list --upgradable`, so
    one call answers this for all 4,200-odd rows instead of 4,200 apt-cache
    invocations.
    """
    _, out, _ = run(["apt", "list", "--upgradable"], timeout=120)
    cand = {}
    for line in out.splitlines():
        # A line reads: pkg/suite VERSION ARCH [upgradable from: OLD].
        # The NEW version is field 2; the bracketed one is what is INSTALLED.
        # Capturing the bracketed value here inverted the comparison and made
        # every drifting package look current.
        m = re.match(r"^([^/]+)/\S+\s+(\S+)\s+\S+\s+\[upgradable from:\s*([^\]]+)\]",
                     line.strip())
        if m:
            cand[m.group(1)] = m.group(2)
    for t in inv.get("apt_packages", []):
        cand.setdefault(t["package"], t["version"])
    return cand


def apt_rows(inv, codename):
    """Every apt package with its archive, suite, component and package page.

    4,000+ rows, so the report links the archive rather than repeating it on every
    line, and only names the page URL for packages that are notable enough to
    have one.
    """
    rows = []
    cand = apt_candidates(inv)
    for t in inv.get("apt_packages", []):
        origin = t.get("origin") or "unknown"
        host = origin.split("/")[0] if origin else "unknown"
        tmpl = ARCHIVE_PAGES.get(host)
        page = tmpl.format(codename=codename, pkg=t["package"]) if tmpl else f"{origin}/{t['package']}"
        rows.append({
            "item": t["package"], "via": f"apt/{t.get('suite') or '-'}",
            "publisher": host,
            "repo": f"{t.get('component') or '-'}",
            "pinned": t["version"],
            "released": cand.get(t["package"], t["version"]),
            "group": t["release"],
            "download": page, "local": False, "exact": True, "is_pinned": True,
        })
    return rows


def direct_and_unmanaged(offline):
    """Vendor-published software: publisher site, version, download link."""
    reg = load_yaml(UNMANAGED)
    rows = []
    for a in reg.get("appimages", []) or []:
        upstream = "-"
        if not offline and a.get("checkable") and a.get("github_repo"):
            d = get_json(f"https://api.github.com/repos/{a['github_repo']}/releases/latest")
            if d:
                upstream = d.get("tag_name", "-")
        rows.append({
            "item": a["name"], "via": "vendor/AppImage",
            "publisher": a.get("publisher") or a.get("source") or "not recorded",
            "repo": f"github.com/{a['github_repo']}" if a.get("github_repo") else "no repository",
            "pinned": a.get("version_in_name") or "no version in filename",
            "released": upstream,
            "download": a.get("linux_amd64_direct") or a.get("download_url") or "none known",
            "note": (a.get("note") or "").strip(), "local": False,
        })
    for e in reg.get("executables", []) or []:
        upstream = "-"
        if not offline and e.get("checkable"):
            if e.get("check_kind") == "github" and e.get("github_repo"):
                d = get_json(f"https://api.github.com/repos/{e['github_repo']}/releases/latest")
                if d:
                    upstream = d.get("tag_name", "-")
            elif e.get("check_kind") == "pypi" and e.get("pypi_package"):
                d = get_json(f"https://pypi.org/pypi/{e['pypi_package']}/json")
                if d:
                    upstream = d["info"]["version"]
            elif e.get("check_kind") == "apt" and e.get("apt_package"):
                _, pol, _ = run(["apt-cache", "policy", e["apt_package"]])
                for line in pol.splitlines():
                    if line.strip().startswith("Candidate:"):
                        upstream = line.split(":", 1)[1].strip()
                        break
        repo = f"https://github.com/{e['github_repo']}" if e.get("github_repo") else "-"
        dl = repo if repo != "-" else (e.get("download_url") or "-")
        rows.append({"item": e["name"], "via": "vendor/executable",
                     "publisher": e.get("publisher") or "see repository",
                     "repo": repo, "pinned": e.get("version", "unknown"),
                     "released": upstream, "download": dl,
                     "note": (e.get("note") or "").strip(), "local": False})
    for dd in (reg.get("direct_downloads") or []):
        pkg = dd.get("package", "")
        rows.append({"item": f"{pkg} (direct .deb)", "via": "vendor/.deb",
                     "publisher": dd.get("publisher") or "vendor", "repo": "no feed",
                     "pinned": dd.get("installed", "-"), "released": "no feed",
                     "download": dd.get("source_url") or dd.get("download_url") or "-",
                     "note": (dd.get("note") or "").strip(), "local": False})
    return rows


def render(inv, codename, offline):
    L = []
    w = L.append

    cont, sn, fl = containers(offline), snaps(offline), flatpaks(offline)
    apts = apt_rows(inv, codename)
    direct = direct_and_unmanaged(offline)

    # ONE schema for every row, whatever delivered it. The operator asked for the
    # table to line up top to bottom with the same columns, so every mechanism is
    # normalised to the same keys and rendered in a single master table rather
    # than five tables with five different shapes.
    rows = cont + sn + fl + apts + direct
    # match_of returns the MARKDOWN string "**NO**"; comparing against a bare
    # "NO" silently produced an empty backlog while the table showed the markers.
    behind = [r for r in rows if match_of(r) == "**NO**"]
    uncheck = [r for r in rows if match_of(r) == "?"]

    w("# ALWAYS ON — Complete Software Provenance Log")
    w("")
    w(f"**Generated `{now_utc()}`** by `scripts/build-update/provenance-log.py`.")
    w("")
    w("> **Read-only.** Queries version endpoints and reads local state. Installs")
    w("> nothing, downloads nothing, changes nothing. Regenerate rather than edit.")
    w("")
    w("Every row uses the **same columns**, whatever delivered it, so the table lines")
    w("up top to bottom: what it is, how it arrived, who publishes it, where it")
    w("lives, what is **pinned** here, what is **released** upstream, whether they")
    w("match, and where to get it.")
    w("")
    w(f"Host: **{inv['os']['pretty']}** (codename `{codename}`), kernel `{inv['kernel']}`.")
    w("")

    w("## Summary")
    w("")
    w("| Delivery | Rows | Behind | Uncheckable |")
    w("|---|---|---|---|")
    for label, group in [("Container images", cont), ("apt packages", apts),
                         ("Snap", sn), ("Flatpak", fl),
                         ("Vendor-published", direct)]:
        b = len([r for r in group if match_of(r) == "**NO**"])
        u = len([r for r in group if match_of(r) == "?"])
        w(f"| {label} | {len(group)} | {b if b else '-'} | {u if u else '-'} |")
    w(f"| **Total** | **{len(rows)}** | **{len(behind)}** | **{len(uncheck)}** |")
    w("")
    if behind:
        w(f"**{len(behind)} item(s) pinned behind what is released.** Listed first so")
        w("the backlog is at the top rather than buried:")
        w("")
        for r in sorted(behind, key=lambda x: x["item"]):
            w(f"- `{r['item']}` — `{r['pinned']}` → `{r['released']}` ({r['via']})")
        w("")

    w("## The complete table")
    w("")
    w("| Item | Via | Publisher | Repository / archive | Pinned | **Version here** | **Released** | Match | Download |")
    w("|---|---|---|---|:---:|---|---|---|---|")
    w("")
    w("✅ = pinned to an immutable digest. ❌ = floating tag, no immutability")
    w("guarantee. The **Version here** column reverse-maps the pinned digest to a")
    w("publisher tag, so two hashes can be read as two versions. Where it still shows")
    w("a hash, the pinned build is older than the publisher's recent tag list and no")
    w("tag covers it — that is reported rather than guessed.")
    order = {"**NO**": 0, "?": 1, "local": 2, "yes": 3}
    for r in sorted(rows, key=lambda x: (order.get(match_of(x), 5), x["item"].lower())):
        dl = r.get("download", "-")
        cell = f"[get]({dl})" if str(dl).startswith("http") else (
            f"`{dl}`" if str(dl).startswith("podman") else str(dl))
        mark = "✅" if r.get("is_pinned") else "❌"
        w(f"| `{r['item']}` | {r['via']} | {r['publisher']} | {r['repo']} | {mark} | "
          f"`{r['pinned']}` | `{r['released']}` | {match_of(r)} | {cell} |")
    w("")

    w("---")
    w("")
    w("## Archives and stores referenced")
    w("")
    w("| Source | Address | Serves |")
    w("|---|---|---|")
    for h, p, sv in [
        ("Docker Hub", "https://hub.docker.com", "official and community images"),
        ("GitHub Container Registry", "https://ghcr.io", "Mastodon, ArduPilot SITL"),
        ("Snap Store", "https://snapcraft.io", "all snap packages"),
        ("Flathub", "https://flathub.org", "Bottles"),
        ("Ubuntu archive", "https://archive.ubuntu.com/ubuntu", "26.04 LTS base and updates"),
        ("Ubuntu security", "https://security.ubuntu.com/ubuntu", "security, unattended"),
        ("packages.ros.org", "http://packages.ros.org/ros2/ubuntu", "ROS 2 - TLS FAULT"),
        ("nvidia.github.io", "https://nvidia.github.io/libnvidia-container", "NVIDIA toolkit"),
        ("Microsoft", "https://packages.microsoft.com/repos/edge-stable", "Edge"),
        ("Google", "https://dl.google.com/linux/chrome-stable/deb", "Chrome"),
        ("OSRF", "https://packages.osrfoundation.org/gazebo/ubuntu-stable", "Gazebo"),
        ("Valve", "https://repo.steampowered.com/steam", "Steam"),
        ("NodeSource", "https://deb.nodesource.com/node_24.x", "Node.js"),
        ("GitHub CLI", "https://cli.github.com/packages", "gh"),
        ("VSCodium", "https://download.vscodium.com/debs", "VSCodium"),
    ]:
        w(f"| {h} | [{p}]({p}) | {sv} |")
    w("")
    return "\n".join(L) + "\n"


UNKNOWN = ("-", "no upstream", "no feed", "unreachable", "not recorded", "")


def _is_digest(v):
    return "sha256:" in str(v)


def _digest_of(v):
    """The hex after sha256:, ignoring any trailing " (tag)" annotation."""
    m = re.search(r"sha256:([0-9a-f]{8,})", str(v))
    return m.group(1) if m else ""


def same_version(a, b, exact=False):
    """Compare two version-ish values.

    Three traps, all of which produced a confident "yes" on data that differed:

    1. Digests must NOT go through norm(): norm() takes the first digit run, which
       for "sha256:d74e..." is the "256" inside "sha256" - so every digest compared
       equal to every other digest.
    2. Debian revisions must not be stripped. norm() cuts at the first "-", so
       1.2.15.3-1ubuntu1.5 and 1.2.15.3-1ubuntu1.7 both reduced to "1.2.15.3" and
       an outdated security-adjacent package reported as current. apt rows pass
       exact=True and are compared whole.
    3. Everything else (tags, tool versions) is fine on the numeric core.
    """
    a, b = str(a), str(b)
    if _is_digest(a) or _is_digest(b):
        da, db = _digest_of(a), _digest_of(b)
        return bool(da) and da == db
    if exact:
        return a.strip() == b.strip()
    return norm(a) == norm(b)


def match_of(r):
    pin = str(r.get("pinned", "-"))
    rel = str(r.get("released", "-")).split(" (")[0].strip()
    if r.get("local"):
        return "local"
    if rel in UNKNOWN:
        return "?"
    if "no version" in pin:
        return "?"
    return "yes" if same_version(pin, rel, r.get("exact", False)) else "**NO**"


CSS = ("body{font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;max-width:1600px;"
       "margin:2rem auto;padding:0 1rem;color:#1c1c1e;background:#fff}"
       "table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:12.5px}"
       "th,td{border:1px solid #d0d3d6;padding:.3rem .45rem;text-align:left;vertical-align:top}"
       "th{background:#e9ecef;position:sticky;top:0}"
       "tr:nth-child(even) td{background:#f8f9fa}"
       "code{background:#eef1f5;padding:.1rem .3rem;border-radius:3px;font-size:11.5px}"
       "details{margin:1rem 0}summary{cursor:pointer;font-weight:600}"
       "h1,h2{border-bottom:1px solid #d0d3d6;padding-bottom:.3rem}"
       "blockquote{border-left:4px solid #adb5bd;margin:1rem 0;padding:.4rem 1rem;color:#495057}")


def to_html(text: str) -> str:
    import markdown as md
    body = md.markdown(text, extensions=["tables", "fenced_code", "toc"])
    return (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>ALWAYS ON — Software Provenance</title><style>{CSS}</style>"
            f"</head><body>{body}</body></html>")


def main():
    ap = argparse.ArgumentParser(
        description="Complete software provenance log (read-only).")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--html", help="also render to HTML at this path")
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()

    if not INVENTORY.exists():
        sys.exit("ERROR: run inventory-full.py first.")
    inv = json.loads(INVENTORY.read_text())
    text = render(inv, inv["os"]["codename"], args.offline)

    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        t = p.with_suffix(p.suffix + ".tmp")
        t.write_text(text, encoding="utf-8")
        t.replace(p)
        print(f"wrote {p}")
    else:
        print(text)

    if args.html:
        h = Path(args.html)
        h.parent.mkdir(parents=True, exist_ok=True)
        h.write_text(to_html(text), encoding="utf-8")
        print(f"wrote {h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
