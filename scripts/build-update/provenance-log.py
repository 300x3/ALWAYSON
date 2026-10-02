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
def released_digest(host, repo, tag):
    """What the publisher currently offers for this tag.

    This is the "released" half of pinned-versus-released. Without it a log can
    only say what is installed, which is half the answer.
    """
    # A first segment that is not a registry is a Docker Hub namespace, not a
    # hostname: "opendronemap/nodeodm" and "webodm/webodm_db" are Hub repos. The
    # same short-name normalisation drift-report.py uses.
    if host not in ("docker.io", "ghcr.io", "quay.io"):
        host, repo = "docker.io", f"{host}/{repo}"
    api = {"docker.io": "registry-1.docker.io", "ghcr.io": "ghcr.io",
           "quay.io": "quay.io"}.get(host)
    if api is None:
        return "-"
    token = None
    tok = {"docker.io": f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:{repo}:pull",
           "ghcr.io": f"https://ghcr.io/token?scope=repository:{repo}:pull"}.get(host)
    if tok:
        d = get_json(tok)
        token = d.get("token") if d else None
    url = f"https://{api}/v2/{repo}/manifests/{tag}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Accept", ", ".join([
        "application/vnd.oci.image.index.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.docker.distribution.manifest.v2+json"]))
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return (r.headers.get("Docker-Content-Digest") or "-")[:19]
    except Exception:
        return "unreachable"


def containers(offline=False):
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
            rows.append({"unit": f.stem, "domain": f.parent.name, "publisher": publisher,
                         "repository": ref or "-", "installed": "-", "upstream": "-",
                         "download": "(local build; no upstream)"})
            continue
        if "@" in ref:
            base, digest = ref.split("@", 1)
        else:
            base, digest = ref, ""
        host, _, repo = base.partition("/")
        tag = (stable.get(f"{host}/{repo}") or {}).get("tracked_tag") or "latest"
        released = "-" if offline else released_digest(host, repo, tag)
        rows.append({
            "unit": f.stem, "domain": f.parent.name,
            "publisher": host,
            "repository": f"{host}/{repo}" if "/" in base else f"docker.io/library/{host}",
            "installed": digest[:19] if digest else "not pinned",
            "released": released, "tag": tag,
            "download": f"podman pull {base}@{digest}" if digest else ref,
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
        rows.append({"name": f[0], "version": f[1], "rev": f[2], "channel": f[3],
                     "publisher": f[5] if len(f) > 5 else "canonical",
                     "released": released,
                     "download": f"https://snapcraft.io/{f[0]}"})
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
        rows.append({"name": f[0], "version": f[1], "branch": f[2], "origin": f[3],
                     "released": released,
                     "download": f"https://flathub.org/apps/{f[0]}"})
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
            "package": t["package"], "version": t["version"],
            "publisher": host, "suite": t.get("suite") or "-",
            "component": t.get("component") or "-",
            "release_group": t["release"],
            "released": cand.get(t["package"], t["version"]),
            "download": page,
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
            "item": a["name"], "publisher": a.get("publisher") or a.get("source") or "-",
            "repository": a.get("github_repo") or "not published as a repository",
            "installed": a.get("version_in_name") or "no version in filename",
            "upstream": upstream,
            "download": a.get("linux_amd64_direct") or a.get("download_url") or "none known",
            "note": (a.get("note") or "").strip(),
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
        rows.append({"item": e["name"], "publisher": e.get("publisher") or "see repository",
                     "repository": repo, "installed": e.get("version", "unknown"),
                     "upstream": upstream, "download": dl,
                     "note": (e.get("note") or "").strip()})
    for dd in (reg.get("direct_downloads") or []):
        pkg = dd.get("package", "")
        rows.append({"item": f"{pkg} (direct .deb)",
                     "publisher": dd.get("publisher") or "vendor",
                     "repository": "-", "installed": dd.get("installed", "-"),
                     "upstream": "no feed",
                     "download": dd.get("source_url") or dd.get("download_url") or "-",
                     "note": (dd.get("note") or "").strip()})
    return rows


def render(inv, codename, offline):
    L = []
    w = L.append
    cont, sn, fl = containers(offline), snaps(offline), flatpaks(offline)
    apts = apt_rows(inv, codename)
    direct = direct_and_unmanaged(offline)

    w("# ALWAYS ON — Complete Software Provenance Log")
    w("")
    w(f"**Generated `{now_utc()}`** by `scripts/build-update/provenance-log.py`.")
    w("")
    w("> **Read-only.** Queries version endpoints and reads local state. Installs")
    w("> nothing, downloads nothing, changes nothing. Regenerate rather than edit:")
    w("> this file has no hand-written content.")
    w("")
    w("For every piece of software on this host: **who publishes it, where it lives,")
    w("what version is installed, what the publisher currently offers, and the exact")
    w("download link.** The other reports ask *is it stale*; this one answers *what is")
    w("it and where do I get it* — the question you must answer before updating.")
    w("")
    w(f"Host: **{inv['os']['pretty']}** (codename `{codename}`), kernel `{inv['kernel']}`.")
    w("")

    w("## Coverage")
    w("")
    w("| Delivery | Items |")
    w("|---|---|")
    w(f"| Container images (Quadlet) | {len(cont)} |")
    w(f"| apt packages | {len(apts)} |")
    w(f"| Snap | {len(sn)} |")
    w(f"| Flatpak | {len(fl)} |")
    w(f"| Vendor-published (AppImage, direct .deb, local executables) | {len(direct)} |")
    w("")

    w("## 1. Container images")
    w("")
    w("Pull the reference shown; it is already digest-pinned.")
    w("")
    w("| Unit | Domain | Publisher / registry | Repository | **Pinned** | **Released** (`{tag}`) | Match | Download |")
    w("|---|---|---|---|---|---|---|---|")
    for r in cont:
        pin, rel = r["installed"], r.get("released", "-")
        if r["publisher"].startswith("built on"):
            match = "local"
        elif rel in ("-", "unreachable"):
            match = "?"
        else:
            match = "yes" if rel == pin else "**NO**"
        tag = r.get("tag", "-")
        w(f"| `{r['unit']}` | {r['domain']} | {r['publisher']} | `{r['repository']}` | "
          f"`{pin}` | `{rel}` ({tag}) | {match} | `{r['download']}` |")
    w("")

    w("## 2. Snap")
    w("")
    w("snapd refreshes these unattended — the only category on this host that")
    w("updates itself.")
    w("")
    w("| Package | **Pinned** | Rev | **Released** (channel) | Match | Channel | Publisher | Store |")
    w("|---|---|---|---|---|---|---|---|")
    for r in sn:
        rel = r.get("released", "-")
        match = "?" if rel == "-" else ("yes" if rel == r["version"] else "**NO**")
        w(f"| `{r['name']}` | `{r['version']}` | {r['rev']} | `{rel}` ({r['channel']}) | "
          f"{match} | {r['channel']} | {r['publisher']} | [link]({r['download']}) |")
    w("")

    if fl:
        w("## 3. Flatpak")
        w("")
        w("`flatpak-system.timer` is **not installed**, so these do not update themselves.")
        w("")
    w(f"## 4. apt packages — {len(apts)}")
    w("")
    groups = {}
    for r in apts:
        groups.setdefault(r["release_group"], []).append(r)
    w("Grouped by release first, because that is the question that matters when")
    w("deciding what to update: part of the supported platform, or a third party's")
    w("release cadence?")
    w("")
    behind = [r for r in apts if r.get("released") and r["released"] != r["version"]]
    w("| Release group | Packages | Behind `Candidate` | Archive |")
    w("|---|---|---|---|")
    for g, items in groups.items():
        hosts = sorted({i["publisher"] for i in items if i["publisher"] != "unknown"})
        n = len([i for i in items if i.get("released") and i["released"] != i["version"]])
        w(f"| {g} | {len(items)} | {n if n else '-'} | {', '.join(f'`{h}`' for h in hosts[:4])} |")
    w("")
    if behind:
        w(f"**{len(behind)} apt package(s) have a newer `Candidate` than what is installed:**")
        w("")
        for r in behind:
            w(f"- `{r['package']}` `{r['version']}` -> `{r['released']}` ({r['suite']})")
    w("")
    w("<details><summary>Every apt package, with its archive page link</summary>")
    w("")
    w("| Package | **Pinned** | **Released** | Match | Suite | Component | Package page |")
    w("|---|---|---|---|---|---|---|")
    for r in apts:
        rel = r.get("released") or r["version"]
        match = "yes" if rel == r["version"] else "**NO**"
        w(f"| `{r['package']}` | `{r['version']}` | `{rel}` | {match} | {r['suite']} | "
          f"{r['component']} | [link]({r['download']}) |")
    w("")
    w("</details>")
    w("")

    w("## 5. Vendor-published software")
    w("")
    w("No package manager owns these. Provenance was recorded by hand in")
    w("`config/build-update/unmanaged-software.yaml`. Where no publisher or")
    w("repository could be identified, that is stated rather than guessed.")
    w("")
    w("| Item | Publisher | Repository | **Pinned** | **Released** | Match | Download | Note |")
    w("|---|---|---|---|---|---|---|---|")
    for r in direct:
        dl = f"[link]({r['download']})" if str(r["download"]).startswith("http") else r["download"]
        note = r["note"].replace("\n", " ")[:120]
        rel = r["upstream"]
        if rel in ("-", "no feed"):
            match = "?"
        else:
            match = "yes" if norm(rel) == norm(r["installed"]) or "no version" in str(r["installed"]) else "**NO**"
        w(f"| `{r['item']}` | {r['publisher']} | {r['repository']} | `{r['installed']}` | "
          f"`{rel}` | {match} | {dl} | {note} |")
    w("")

    w("---")
    w("")
    w("## Archives and stores referenced")
    w("")
    w("| Source | Address | Serves |")
    w("|---|---|---|")
    for h, p, s in [
        ("Docker Hub", "https://hub.docker.com", "official and community images"),
        ("GitHub Container Registry", "https://ghcr.io", "Mastodon, ArduPilot SITL"),
        ("Snap Store", "https://snapcraft.io", "all snap packages"),
        ("Flathub", "https://flathub.org", "Bottles"),
        ("Ubuntu archive", "https://archive.ubuntu.com/ubuntu", "Ubuntu 26.04 LTS base and updates"),
        ("Ubuntu security", "https://security.ubuntu.com/ubuntu", "security pocket, unattended"),
        ("packages.ros.org", "http://packages.ros.org/ros2/ubuntu", "ROS 2 — TLS FAULT, unreachable"),
        ("nvidia.github.io", "https://nvidia.github.io/libnvidia-container", "NVIDIA container toolkit"),
        ("Microsoft", "https://packages.microsoft.com/repos/edge-stable", "Edge"),
        ("OSRF", "https://packages.osrfoundation.org/gazebo/ubuntu-stable", "Gazebo"),
        ("Valve", "https://repo.steampowered.com/steam", "Steam"),
        ("NodeSource", "https://deb.nodesource.com/node_24.x", "Node.js"),
        ("GitHub CLI", "https://cli.github.com/packages", "gh"),
        ("VSCodium", "https://download.vscodium.com/debs", "VSCodium"),
    ]:
        w(f"| {h} | [{p}]({p}) | {s} |")
    w("")
    return "\n".join(L) + "\n"

CSS = ("body{font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;max-width:1500px;"
       "margin:2rem auto;padding:0 1rem;color:#1c1c1e;background:#fff}"
       "table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:13px}"
       "th,td{border:1px solid #d0d3d6;padding:.35rem .5rem;text-align:left;vertical-align:top}"
       "th{background:#e9ecef;position:sticky;top:0}"
       "tr:nth-child(even) td{background:#f8f9fa}"
       "code{background:#eef1f5;padding:.1rem .3rem;border-radius:3px;font-size:12px}"
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
