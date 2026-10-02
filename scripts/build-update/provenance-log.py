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
TIMEOUT = 12

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
_RAW_CACHE = {}


def registry_digest_raw(host, repo, tag):
    """Full manifest digest for a tag, or None.

    CACHED. Without it the same image was re-fetched once per row that uses it -
    postgres appears in three units, redis in two - turning a 13-repository job
    into ~88 sequential HTTP round trips, and the run did not finish in five
    minutes.
    """
    key = (host, repo, tag)
    if key in _RAW_CACHE:
        return _RAW_CACHE[key]
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
            _RAW_CACHE[key] = r.headers.get("Docker-Content-Digest")
            return _RAW_CACHE[key]
    except Exception:
        _RAW_CACHE[key] = None
        return None


_TAG_CACHE = {}


HUB_PAGES = int(os.environ.get("AO_HUB_PAGES", "4"))


def _hub_tags(repo, want=None):
    """digest -> [tags] for a Docker Hub repo.

    This is what turns a pinned digest into a version a human can read: the Hub
    API returns a digest for every tag, so the pinned digest reverse-looks-up to a
    version. Grafana resolves on page one - `latest` and `13.0.2` share a digest -
    which is precisely the comparison two raw hashes hide.

    It PAGES. A one-shot call only covers the publisher's 100 most recent tags,
    and an older pin falls outside that window and stayed a bare hash. Given the
    digest we are trying to place, paging stops as soon as it is found.
    """
    if repo not in _TAG_CACHE:
        m = {}
        for page in range(1, HUB_PAGES + 1):
            d = get_json(f"https://hub.docker.com/v2/repositories/{repo}/tags"
                         f"?page_size=100&page={page}&ordering=last_updated")
            res = (d or {}).get("results") or []
            for r in res:
                if r.get("name") and r.get("digest"):
                    m.setdefault(r["digest"], []).append(r["name"])
            if want:
                short = str(want).split("sha256:")[-1]
                if any(dg.split("sha256:")[-1].startswith(short[:16]) for dg in m):
                    break
            if not res or not (d or {}).get("next"):
                break
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
            for page in (1, 2):
                for r in (get_json(f"https://api.github.com/repos/{gh[repo]}"
                                   f"/releases?per_page=50&page={page}") or []):
                    if r.get("tag_name"):
                        cands.append(r["tag_name"])
        for tag in [c for c in cands if c][:8]:
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
    m = (_ghcr_tags(repo) if host == "ghcr.io"
         else _hub_tags(repo, want=digest))
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
        rel_full = registry_digest_raw(host, repo, tag) if not offline else None
        rel_ver = version_for(host, repo, rel_full) if rel_full else None
        rows.append({
            "item": f.stem, "via": f"container/{f.parent.name}",
            "publisher": host,
            "repo": f"{host}/{repo}" if "/" in base else f"docker.io/library/{host}",
            "pinned": pin_ver or "no version tag",
            "released": rel_ver or "no version tag",
            "tag": tag,
            "pin_hash": digest[:19] if digest else "-",
            "rel_hash": (rel_full[:19] if rel_full else "-"),
            "is_pinned": bool(digest),
            "download": f"podman pull {base}@{digest}" if digest else ref,
            "local": False, "exact": False,
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
    """One table. Every row, the same eleven columns, top to bottom."""
    cont, sn, fl = containers(offline), snaps(offline), flatpaks(offline)
    apts = apt_rows(inv, codename)
    direct = direct_and_unmanaged(offline)
    rows = cont + sn + fl + apts + direct

    behind = len([r for r in rows if match_of(r) == "**NO**"])
    current = len([r for r in rows if match_of(r) == "yes"])
    unknown = len([r for r in rows if match_of(r) == "?"])
    local = len([r for r in rows if match_of(r) == "local"])

    L = []
    w = L.append
    w(f"# Software status - {inv['os']['pretty']} - {now_utc()[:10]}")
    w("")
    w(f"**{len(rows)} items.** {behind} behind - {current} up to date - "
      f"{unknown} no version published - {local} local build. "
      f"Generated by `scripts/build-update/provenance-log.py`; read-only.")
    w("")
    w("| Item | Via | Publisher | Repository / archive | Pinned | Version here | "
      "Up to date? | Released | Pinned hash | Released hash | Download |")
    w("|---|---|---|---|:---:|---|:---:|---|---|---|---|")
    rank = {"**NO**": 0, "?": 1, "local": 2, "yes": 3}
    for r in sorted(rows, key=lambda x: (rank.get(match_of(x), 5), str(x["item"]).lower())):
        dl = r.get("download", "-")
        cell = (f"[get]({dl})" if str(dl).startswith("http")
                else (f"`{dl}`" if str(dl).startswith("podman") else str(dl)))
        mark = "\u2705" if r.get("is_pinned") else "\u274c"
        up = {"yes": "yes", "**NO**": "**NO**", "?": "?", "local": "local"}[match_of(r)]
        tag = r.get("tag")
        rel = f"`{r['released']}`" + (f" ({tag})" if tag else "")
        w(f"| `{r['item']}` | {r['via']} | {r['publisher']} | {r['repo']} | {mark} | "
          f"`{r['pinned']}` | {up} | {rel} | `{r.get('pin_hash', '-')}` | "
          f"`{r.get('rel_hash', '-')}` | {cell} |")
    w("")
    return "\n".join(L) + "\n"


UNKNOWN = ("-", "no upstream", "no feed", "unreachable", "not recorded", "")


def _is_digest(v):
    return "sha256:" in str(v)


def _digest_of(v):
    """Hex after sha256:, ignoring any trailing " (tag)" annotation."""
    m = re.search(r"sha256:([0-9a-f]{8,})", str(v))
    return m.group(1) if m else ""


def same_version(a, b, exact=False):
    """Compare two version-ish values.

    Three traps, each of which once produced a confident "yes" on data that
    differed: digests must not go through norm() (which takes the "256" out of
    "sha256"); Debian revisions must not be stripped (1.2.15.3-1ubuntu1.5 and
    ...-1ubuntu1.7 both reduce to 1.2.15.3); everything else compares on the
    numeric core.
    """
    a, b = str(a), str(b)
    if _is_digest(a) or _is_digest(b):
        da, db = _digest_of(a), _digest_of(b)
        return bool(da) and da == db
    if exact:
        return a.strip() == b.strip()
    return norm(a) == norm(b)


def match_of(r):
    # Compare hashes when both are present. Display strings are for reading; a
    # comparison against "no version tag" or a rolling alias proves nothing.
    ph, rh = str(r.get("pin_hash", "")), str(r.get("rel_hash", ""))
    if _is_digest(ph) or _is_digest(rh):
        da, db = _digest_of(ph), _digest_of(rh)
        if da and db:
            return "yes" if da == db else "**NO**"
        return "?"
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
