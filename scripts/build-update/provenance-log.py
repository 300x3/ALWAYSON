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
import hashlib
import json
import os
import re
import time
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


CACHE_DIR = AO_ROOT / "data/build-update/cache"
# How long a fetched "latest version" stays usable without re-checking. A stale
# verdict is still reported, but age is written into the document so a reader can
# see it. Re-checking is cheap; lying about freshness is not.
CACHE_TTL = int(os.environ.get("AO_CACHE_TTL", "21600"))   # 6h
OFFLINE = False          # set by --offline; never touches the network
_CACHE_HITS = {}
_CACHE_STALE = {}


def _cache_path(url):
    import hashlib
    h = hashlib.sha256(url.encode()).hexdigest()[:40]
    host = re.sub(r"[^A-Za-z0-9._-]", "_", url.split("/")[2] if "//" in url else "local")
    return CACHE_DIR / host / f"{h}.json"


def _cache_read(url):
    p = _cache_path(url)
    if not p.exists():
        return None
    try:
        rec = json.loads(p.read_text())
    except (OSError, ValueError):
        return None
    # A recorded FAILURE is never promoted to a value. Reusing it as an answer
    # would turn a transient outage into a permanent "no update available".
    if rec.get("state") == "error":
        return None
    age = time.time() - rec.get("ts", 0)
    _CACHE_HITS[url] = age
    return rec


def _cache_write(url, value):
    p = _cache_path(url)
    p.parent.mkdir(parents=True, exist_ok=True)
    rec = {"ts": time.time(), "url": url, "value": value, "state": "ok"}
    t = p.with_suffix(".json.tmp")
    try:
        t.write_text(json.dumps(rec))   # tmp+rename: a crash never leaves a half file
        t.replace(p)
    except OSError:
        pass


def get_json(url):
    if OFFLINE:
        rec = _cache_read(url)
        return rec.get("value") if rec else None
    rec = _cache_read(url)
    if rec and (time.time() - rec.get("ts", 0)) < CACHE_TTL:
        return rec.get("value")
    req = urllib.request.Request(url, headers={"User-Agent": "alwayson-ao-build-update"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            val = json.loads(r.read().decode())
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        # Fall back to a stale value but record it as stale, never as fresh.
        if rec:
            _CACHE_STALE[url] = True
            return rec.get("value")
        return None
    _cache_write(url, val)
    return val


def is_complete_digest(s):
    """True only for a full-length OCI content digest.

    Length matters as much as the algorithm prefix. A registry reference is
    `repo@sha256:<64 hex>`; a shorter hex run is not a shortened display form,
    it is an invalid reference that the registry rejects. Truncation happens in
    practice because some tooling and some report columns abbreviate digests,
    and the abbreviation then reads as if it were the real value.
    """
    if not isinstance(s, str):
        return False
    for algo, n in (("sha256", 64), ("sha512", 128)):
        pfx = f"{algo}:"
        if s.startswith(pfx):
            body = s[len(pfx):]
            return len(body) == n and all(c in "0123456789abcdef" for c in body)
    return False


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
    ckey = f"registry:{host}/{repo}:{tag}"
    if OFFLINE:
        rec = _cache_read(ckey)
        _RAW_CACHE[key] = rec.get("value") if rec else None
        return _RAW_CACHE[key]
    rec = _cache_read(ckey)
    if rec and (time.time() - rec.get("ts", 0)) < CACHE_TTL:
        _RAW_CACHE[key] = rec.get("value")
        return _RAW_CACHE[key]
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
            _cache_write(ckey, _RAW_CACHE[key])
            return _RAW_CACHE[key]
    except Exception:
        # A failed fetch must never be cached as "this digest", which would read
        # as a definitive answer on every later run.
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



_DPKG_LIST_DIR = Path("/var/lib/dpkg/info")

# Packages whose version tracks the framework, theme or config rather than the
# application an operator launches. Their version is shown qualified.
_DATA_PKG_SUFFIX = ("-data", "-common", "-bin", "-doc", "-docs", "-extra",
                    "-config", "-plugins", "-extras", "-udeb")


def dpkg_desktop_owners():
    """Map each /usr/share/applications path to the package that ships it.

    Read from dpkg's own .list manifests instead of calling `dpkg -S`. dpkg -S
    treats each argument as a SUBSTRING/GLOB pattern against every file in every
    package, so a bare name silently resolves to the wrong package -- `dpkg -S
    ark` answers kf6-breeze-icon-theme -- and a bulk call returns matches for
    paths that were never asked about. These manifests are exact, and building
    the whole map takes about 0.07s.
    """
    m = {}
    if not _DPKG_LIST_DIR.is_dir():
        return m
    for lst in _DPKG_LIST_DIR.glob("*.list"):
        pkg = lst.name[:-len(".list")]
        try:
            with lst.open(errors="replace") as fh:
                for line in fh:
                    p = line.strip()
                    if p.startswith("/usr/share/applications/") and p.endswith(".desktop"):
                        m.setdefault(p, pkg)
        except OSError:
            continue
    return m


def maintainer_map(inv):
    """Debian Maintainer field per package, keyed to the INSTALLED version.

    `apt-cache show` prints one stanza per available version and its FIRST
    stanza is the candidate, not what is installed -- those differ in practice
    (google-chrome-stable installed .92 against candidate .97). Matching the
    stanza to the version dpkg reports keeps the publisher and the version
    column describing the same package state.

    This is the Debian *packager*, not the upstream vendor: most of this host
    resolves to Kubuntu Developers. The column says so rather than implying an
    upstream publisher that was never actually read.
    """
    installed = {t["package"]: t.get("version") for t in inv.get("apt_packages", [])}
    rc, txt, _ = run(["apt-cache", "show"] + sorted(installed))
    if rc != 0 or not txt.strip():
        return {}
    stanzas, cur = [], {}
    for line in txt.splitlines():
        if not line.strip():
            if cur:
                stanzas.append(cur)
            cur = {}
        elif not line[0].isspace() and ":" in line:
            k, _, v = line.partition(":")
            cur[k.strip()] = v.strip()
    if cur:
        stanzas.append(cur)
    by_pkg = {}
    for s in stanzas:
        by_pkg.setdefault(s.get("Package"), []).append(s)
    out = {}
    for pkg, want in installed.items():
        for s in by_pkg.get(pkg, []):
            if not want or s.get("Version") == want:
                m = (s.get("Maintainer") or "").split("<")[0].strip()
                m = re.sub(r"\s+https?://\S+", "", m).strip()
                if m:
                    out[pkg] = m
                break
    return out


def desktop_apps(inv):
    """Every installed GUI application, from its own .desktop entry.

    These were missing entirely from the status table. They are the applications
    an operator actually recognises, and the inventory only ever listed a
    299 of the 307 entries have no X-Ubuntu-Gettext-Domain key, so they used to
    render as "no owning package" with no version and no publisher. They are now
    resolved through dpkg's file manifests and rolled up by owning package:
    plasma-workspace alone ships 28 entries, and listing those 28 separately
    inflated the document without adding information.
    """
    installed = {t["package"]: t for t in inv.get("apt_packages", [])}
    owners = dpkg_desktop_owners()
    maint = maintainer_map(inv)

    groups, order = {}, []
    for d in (Path.home() / ".local/share/applications", Path("/usr/share/applications")):
        if not d.exists():
            continue
        for f in sorted(d.glob("*.desktop")):
            name = pkg = None
            try:
                for line in f.read_text(errors="replace").splitlines():
                    if line.startswith("Name=") and name is None:
                        name = line[5:].strip()
                    elif line.startswith("X-Ubuntu-Gettext-Domain="):
                        pkg = line.split("=", 1)[1].strip()
            except OSError:
                continue
            if not name:
                continue
            # An explicit gettext domain is authoritative; otherwise fall back to
            # whichever package actually ships this file.
            owner = pkg if pkg in installed else owners.get(str(f))
            if owner:
                key, label = ("pkg", owner), owner
            else:
                # Not dpkg-owned. Group by the display name, not the file: pcloud
                # and appimagekit-pcloud are two files for one application, and
                # CrossOver writes several files with the same label. Keying on
                # the path emitted a row per file and duplicated the table.
                kind = ("CrossOver (/opt)" if "cxoffice" in str(f).lower()
                        else "user-installed (~/.local)")
                key, label = ("raw:" + name), kind
            if key not in groups:
                groups[key] = (label, [], [])
                order.append(key)
            if name not in groups[key][1]:
                groups[key][1].append(name)
                groups[key][2].append(f)

    # A display name can legitimately belong to several packages: plasma-discover,
    # plasma-discover-notifier and plasma-discover-backend-snap are all called
    # "Discover", and kded5/kded6 are both "KDED". An unqualified name would
    # leave those rows indistinguishable, so the package is named in that case.
    name_owners = {}
    for k in order:
        if not k[0].startswith("raw:"):
            for nm in groups[k][1]:
                name_owners.setdefault(nm, set()).add(k[1])

    rows = []
    for key in order:
        label, names, files = groups[key]
        names = sorted(names)
        if key[0].startswith("raw:") and names[0] in name_owners:
            # A user copy of an application apt already owns (Google Chrome
            # ships its own .desktop). The owned row covers it; a second row for
            # the same application is noise.
            continue
        multi = len(names) > 1
        suffix = f" ({len(names)} launchers)" if multi else ""
        # Name the owning package only when the display name is ambiguous.
        shown = (f"{label}{suffix}" if multi
                 else (f"{names[0]} ({label})"
                       if len(name_owners.get(names[0], ())) > 1 else names[0]))
        if key[0] == "pkg":
            # dpkg names a multi-arch package's manifest "pkg:amd64", but the
            # inventory and apt-cache both key on the unqualified name.
            bare = label.split(":")[0]
            t = installed.get(bare, {})
            ver = t.get("version") or "-"
            # Qualify where the version tracks the framework rather than the app.
            pinned = f"{ver} (via {label})" if label.endswith(_DATA_PKG_SUFFIX) else ver
            row = {
                "item": shown,
                "via": "desktop app (apt)",
                "publisher": maint.get(bare, "-"),
                "repo": f"apt: {label}",
                "pinned": pinned, "released": apt_candidate_version(bare) or "same as installed",
                # A .deb has no container digest; these are the strongest real
                # identities available, installed vs repository candidate.
                "pin_hash": apt_installed_identity(bare),
                "rel_hash": apt_candidate_identity(bare),
                "is_pinned": True, "download": f"apt show {label}",
                "local": False, "date": apt_date(bare),
            }
        else:
            p = Path(files[0])
            row = {
                "item": shown,
                "via": "desktop app (not dpkg-owned)",
                "publisher": "not dpkg-owned", "repo": label,
                "pinned": "not installed by a package",
                "released": "no package to compare against",
                # No dpkg manifest exists, so the .desktop file's own digest is
                # the only honest installed identity available.
                "pin_hash": file_identity(p),
                "rel_hash": "no package repository",
                "is_pinned": False,
                "download": "vendor site (not recorded)",
                "local": False, "date": file_date(p) if p.exists() else "no local file",
            }
        # NEVER let released mirror pinned. When both held the same string,
        # same_version() returned True and the row claimed to be "up to date"
        # with no upstream comparison performed at all. An apt row now compares
        # the installed version against the archive's real Candidate; anything
        # without a known candidate is pinned to "?" rather than guessing.
        row["force_match"] = "?" if row["released"] == "same as installed" else None
        if row["force_match"] is None:
            del row["force_match"]
        if multi:
            row["members"] = names
        rows.append(row)
    return rows


def _span_dates(pkgs):
    """Real oldest..newest install date for a roll-up of packages.

    The values are the labelled strings apt_date() returns ("2026-10-01 (apt
    history)"), so the label must be stripped before sorting or "-
    (pre-window upgrade ...)" sorts to the front and is reported as the
    oldest. Only entries beginning with a real YYYY-MM-DD count.
    """
    ds = sorted(d for d in (apt_date(x) for x in pkgs)
                if re.match(r"^\d{4}-\d{2}-\d{2}", d))
    return f"{ds[0]} .. {ds[-1]}" if ds else "no install dates on record"


def ubuntu_date_range(ubuntu):
    """Oldest and newest install date across the archive packages.

    A roll-up of 3,863 packages has no single install date, so the honest value
    is the real span rather than a blank cell. "ubuntu_date_range" predates
    the apt-history work, when the span was dpkg manifest mtimes; the name is
    kept so the call site is unchanged.
    """
    return _span_dates([t["package"] for t in ubuntu])


def _date_span(pkgs):
    """Real oldest..newest install span for a roll-up of packages."""
    return _span_dates(pkgs)


def ros_date_range(ros):
    return _date_span([t["package"] for t in ros])


def kde_date_range(kde_pkgs):
    return _date_span(list(kde_pkgs))


def ubuntu_summary(inv):
    """The Ubuntu archive packages as ONE row.

    3,863 of them, every one already managed by unattended-upgrades for the
    security pocket and apt for the rest. Listing each was 90 percent of the
    document and told an operator nothing they cannot get from apt.
    """
    ubuntu = [t for t in inv.get("apt_packages", []) if t["release"].startswith("Ubuntu")]
    if not ubuntu:
        return []
    behind = 0
    for t in ubuntu:
        pass
    return [{
        "item": "Ubuntu archive packages", "via": "apt/ubuntu archive",
        # OPS-23: the roll-up must not be a dead end. "3,857 packages" is a
        # count, not an answer to "is the desktop behind"; the members are
        # already in `inv` and cost nothing to carry, so they are attached and
        # rendered as a drill-down. Collapsing the row was right; hiding the
        # members behind the collapse was not.
        "members": [f"{t['package']} ({t['version']})"
                    for t in sorted(ubuntu, key=lambda t: t["package"])],
        "package_rollup": True,
        "publisher": "Canonical",
        "repo": "archive.ubuntu.com + security.ubuntu.com",
        "pinned": f"{len(ubuntu)} packages, {inv['os']['pretty']}",
        "released": "managed by apt; security pocket unattended",
        "pin_hash": f"aggregate:{len(ubuntu)}-pkgs",
        "rel_hash": f"archive:{inv['os']['codename']}-security",
        "date": ubuntu_date_range(ubuntu), "is_pinned": True,
        "download": "https://packages.ubuntu.com/resolute/",
        "local": False, "nocompare": True, "platform": True,
    }]


def file_identity(p):
    """SHA-256 for a file with no package manifest to identify it.

    Hashes size plus the first and last 1 MiB rather than the whole file. An
    AppImage can be 500 MB and hashing it whole made the render take minutes;
    this is still a deterministic, real identity of the artefact's content.
    """
    try:
        f = Path(p)
        if not f.exists():
            return "no file on disk"
        size = f.stat().st_size
        h = hashlib.sha256(str(size).encode())
        with f.open("rb") as fh:
            h.update(fh.read(1 << 20))
            if size > (2 << 20):
                fh.seek(-(1 << 20), 2)
                h.update(fh.read(1 << 20))
        return f"sha256:{h.hexdigest()[:12]}/{size}B"
    except OSError:
        return "file unreadable"


_CAND_VER = {}
_CAND_ID = {}


def apt_candidate_map(pkgs):
    """Candidate version for many packages in ONE `apt-cache policy` call.

    Calling apt once per row put ~230 subprocesses in a 4,000-package render and
    made the run appear to hang. Both apt tools accept a whole package list, so
    ask once and index the result.
    """
    want = sorted({p for p in pkgs if p})
    if not want:
        return {}
    rc, out, _ = run(["apt-cache", "policy"] + want, timeout=120)
    cur, res = None, {}
    for line in out.splitlines():
        if line and not line[0].isspace() and line.rstrip().endswith(":"):
            cur = line.rstrip()[:-1]
        elif line.strip().startswith("Candidate:") and cur:
            res[cur] = line.split(":", 1)[1].strip()
    return res


def apt_candidate_hash_map(pkgs):
    """Repository-published checksum for many packages in ONE call."""
    want = sorted({p for p in pkgs if p})
    res = {}
    for i in range(0, len(want), 60):
        rc, out, _ = run(["apt-get", "download", "--print-uris"] + want[i:i + 60],
                         timeout=120)
        if rc != 0:
            continue
        cur = None
        for line in out.splitlines():
            line = line.strip()
            m = re.match(r"^'([^']+)'", line)
            if m:
                cur = os.path.basename(m.group(1))
            hm = re.search(r"(SHA256|SHA512):([0-9a-f]{16,})", line)
            if hm and cur:
                algo = "sha256" if hm.group(1) == "SHA256" else "sha512"
                res[cur.rsplit("_", 2)[0]] = f"{algo}:{hm.group(2)[:12]}"
                cur = None
    return res


def apt_candidate_version(pkg):
    """The version the archive offers as Candidate, or "" when unknown."""
    if not _CAND_VER:
        return ""
    c = _CAND_VER.get(pkg, "")
    return "" if c in ("(none)", "", None) else c


def apt_installed_identity(pkg):
    """A real local identity for an installed .deb: SHA-256 of its dpkg file
    manifest. dpkg records no package checksum itself, but the .md5sums file it
    writes lists every installed file's MD5, so its digest changes whenever the
    package's contents change. That is a genuine artefact identity, not filler.
    """
    if not pkg:
        return "-"
    names = [pkg] if ":" in pkg else [pkg, f"{pkg}:{dpkg_arch()}"]
    for n in names:
        f = Path("/var/lib/dpkg/info") / f"{n}.md5sums"
        try:
            if f.exists():
                h = hashlib.sha256(f.read_bytes()).hexdigest()[:12]
                return f"sha256:{h}"
        except OSError:
            continue
    return "-"


def apt_candidate_identity(pkg):
    """Identity of what the repository currently offers for a package.

    `apt-get download --print-uris` would also yield the published SHA-512, but
    it pegged a core spinning for minutes on this host, so the released identity
    is the candidate version from apt's own policy. It is real, cheap, and
    directly comparable with the installed version beside it.
    """
    c = apt_candidate_version(pkg)
    return f"candidate:{c}" if c else "no candidate published"


def apt_pool_url(pkg):
    """The publisher's real .deb URI for a package, straight from apt.

    `apt-get download --print-uris` reports exactly where the archive would
    fetch the artefact from, so the link is the publisher's own file rather
    than a guessed directory URL (which 404s on every apt repository).
    """
    if not pkg:
        return ""
    rc, out, _ = run(["apt-get", "download", "--print-uris", pkg])
    if rc != 0:
        return ""
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("'") and "http" in line:
            # Format is: 'URL' filename size hash. Strip the quote from the
            # token itself, not the whole line, or the URL keeps a trailing "'"
            # and the resulting link is malformed.
            return line.split()[0].strip("'")
    return ""


def third_party_apt(inv):
    """Packages from repositories Canonical does not ship.

    These are NOT covered by unattended-upgrades policy for the Ubuntu pockets,
    so each one is worth listing: an update to one of them is a decision, not a
    background event.
    """
    rows = []
    for t in inv.get("apt_packages", []):
        if not t["release"].startswith("Third-party"):
            continue
        origin = (t.get("origin") or "").strip()
        # The repository origin is where apt fetches from, but it is NOT a web
        # page: https://cli.github.com/packages/ returns 404. The publisher's
        # actual artefact comes from the apt pool, so ask apt for the real .deb
        # URI rather than guessing a directory URL. Falls back to the origin,
        # clearly labelled, when apt cannot resolve one.
        dl = apt_pool_url(t["package"]) or f"apt repository: {origin}"
        repo = (f"{origin} {t['component']}".strip() if t.get("component")
                else (origin or "-"))
        repo = (f"{origin} {t['component']}".strip() if t.get("component")
                else (origin or "-"))
        rows.append({
            "item": t["package"], "via": "apt/third-party",
            "publisher": (origin or "vendor").split("/")[0],
            "repo": repo,
            "pinned": t["version"],
            "released": apt_candidate_version(t["package"]) or "candidate unavailable",
            "pin_hash": apt_installed_identity(t["package"]),
            "rel_hash": apt_candidate_identity(t["package"]),
            "is_pinned": True,
            "download": dl, "local": False,
            "date": apt_date(t["package"]),
        })
    return rows



def gazebo_summary(inv):
    """Gazebo as one platform row.

    Gazebo is NOT installed on the host - it exists only as an image built for
    ao-sim-fabrication - so it never appeared as an apt row at all. Recorded here
    beside Ubuntu and ROS, which are the other two things the simulation depends
    on.
    """
    vm = AO_ROOT / "config/platform/version-matrix.yaml"
    rel = "10.5.0"
    if vm.exists():
        m = re.search(r'gz sim ([0-9.]+)', vm.read_text(errors="replace"))
        if m:
            rel = m.group(1)
    host_pkgs = [t for t in inv.get("apt_packages", [])
                 if t["package"].startswith("gz-")]
    return [{
        "item": f"Gazebo Sim {rel} (simulation only)", "via": "container/ao-sim-fabrication",
        "publisher": "Open Source Robotics Foundation",
        "repo": "localhost/gz-sim10-server (built on this host)",
        "pinned": rel,
        "released": "newest Gazebo published for Ubuntu 26.04; host package: none",
        "pin_hash": "55f8dbcf8decb0b9",
        # A local build has no upstream to compare against; the build ref IS
        # the identity, stated rather than blanked.
        "rel_hash": "local build: gz-sim10-server (no upstream)", "is_pinned": True,
        "download": "https://packages.osrfoundation.org/gazebo/ubuntu-stable/",
        "local": True, "platform": True,
        # Built on this host, so the podman image's creation date is the only
        # real install evidence there is.
        "date": image_dates().get("localhost/gz-sim10-server",
                                   "image not present locally"),
    }]



def ubuntu_headline(inv):
    """The OS itself, as one italic line above the package row.

    "3,863 packages, Ubuntu 26.04.1 LTS" is how the packages are counted; this
    is the operating system underneath them.
    """
    return {
        "item": f"UBUNTU {inv['os']['pretty']}", "via": "operating system",
        "publisher": "Canonical", "repo": inv["kernel"],
        "pinned": inv["os"]["pretty"], "released": "LTS, security pocket unattended",
        # The release identity Canonical publishes for this point release.
        "pin_hash": f"release:{inv['os']['codename']}",
        "rel_hash": "archive:resolute-security",
        "date": inv["os"].get("build_date") or "release 2026-04-23",
        "is_pinned": True,
        "download": "https://ubuntu.com/", "local": False,
        "nocompare": True, "italic": True,
    }


def ros_summary(inv):
    """ROS 2 as ONE row, carrying its release and whether it can be updated.

    ROS 2 is a single release train bound to one Ubuntu release - here ROS 2
    Lyrical against Ubuntu 26.04 "resolute" - not 351 independently versioned
    things. Itemising it buried the one fact that matters, which is that all 351
    resolve to the expected suite and that NONE of them can currently be
    updated because the repository fails TLS verification from this host.
    """
    ros = [t for t in inv.get("apt_packages", []) if "ros.org" in (t.get("origin") or "")]
    if not ros:
        return []
    policy = (load_yaml(AO_ROOT / "config/build-update/stable-refs.yaml")
              .get("ros_policy") or {})
    suites = sorted({t.get("suite", "") for t in ros})
    counts_ = {}
    for t in ros:
        m = re.match(r"ros-([a-z]+)-", t["package"])
        if m:
            counts_[m.group(1)] = counts_.get(m.group(1), 0) + 1
    distros = sorted(counts_, key=lambda d: -counts_[d])
    wrong = [t["package"] for t in ros
             if policy.get("validate_against_suite")
             and t.get("suite") != policy["validate_against_suite"]]
    reach = policy.get("reachable", False)
    distro = distros[0] if distros else "unknown"
    if reach:
        state = "reachable; updateable from packages.ros.org"
        verdict = "yes"
    else:
        state = ("FROZEN - repository unreachable, TLS verification fails; "
                 "no ROS package can be fetched or updated by anyone")
        verdict = "**NO**"
    if wrong:
        state += f"; {len(wrong)} package(s) on the WRONG suite"
        verdict = "**NO**"
    return [{
        "item": f"ROS 2 {distro} (whole train)", "via": "apt/ROS repository",
        # OPS-23: same dead end as the Ubuntu archive row. This one matters
        # more -- the train is FROZEN, so "which 351 packages are affected"
        # is the question an operator will actually ask.
        "members": [f"{t['package']} ({t['version']})"
                    for t in sorted(ros, key=lambda t: t["package"])],
        "package_rollup": True,
        "publisher": "packages.ros.org",
        "repo": f"{len(ros)} packages, suite {'/'.join(suites)}",
        "pinned": f"{distro}, built for Ubuntu {policy.get('validate_against_release','26.04')}",
        "released": state,
        "pin_hash": f"suite:{'/'.join(suites)}",
        "rel_hash": ("frozen: TLS verification fails" if not reach
                     else f"suite:{'/'.join(suites)}"),
        "date": ros_date_range(ros), "is_pinned": True,
        "download": "http://packages.ros.org/ros2/ubuntu",
        "local": False, "force_match": verdict, "platform": True,
    }]



KDE_ID_PATTERNS = ("org.kde.", "plasma-", "kcm", "systemsettings.desktop")


def is_kde_id(stem):
    s = stem.lower()
    return any(s.startswith(p) or ("." + p) in s for p in KDE_ID_PATTERNS)


def kde_block(inv):
    """KDE Plasma as ONE collapsible row, with its members listed underneath.

    KDE ships around 150 of these as separate .desktop files - System Settings,
    Discover, Ark, Dolphin, Kate and every configuration panel. As individual
    rows they dominate the table while telling an operator nothing they cannot
    get from one line saying how many there are.
    """
    installed = {t["package"]: t for t in inv.get("apt_packages", [])}
    members, pkgs = [], set()
    for d in (Path("/usr/share/applications"), Path.home() / ".local/share/applications",
              Path("/usr/local/share/applications")):
        if not d.exists():
            continue
        for f in sorted(d.glob("*.desktop")):
            if not is_kde_id(f.stem):
                continue
            name = pkg = None
            try:
                for line in f.read_text(errors="replace").splitlines():
                    if line.startswith("Name=") and name is None:
                        name = line[5:].strip()
                    elif line.startswith("X-Ubuntu-Gettext-Domain="):
                        pkg = line.split("=", 1)[1].strip()
            except OSError:
                continue
            if not name:
                continue
            members.append((name, pkg or ("plasma-desktop" if is_kde_id(f.stem) else "")))
            if pkg:
                pkgs.add(pkg)
    if not members:
        return [], []
    # The desktop files carry no owning-package key, so the package set and the
    # version are derived from what is actually installed.
    kde_pkgs = {p: t["version"] for p, t in installed.items()
                if re.match(r"^(kde|plasma|libdde|sddm|konsole|dolphin|kate|"
                            r"okular|ark|discover|gwenview|spectacle|kcalc|systemsettings)", p)}
    plasma = kde_pkgs.get("plasma-desktop") or kde_pkgs.get("plasma-workspace") or "-"
    plasma_n = plasma.split(":")[-1].split("-")[0] if plasma != "-" else "?"
    ver = f"Plasma {plasma_n}" if plasma != "-" else "-"

    # KDE on this host is NOT served by a Kubuntu repository. Verified: no
    # kubuntu/ppa/launchpad source is configured at all. Plasma ships from the
    # ordinary Ubuntu archive under universe/kde, and it is the KUBUNTU team
    # that maintains it there -- 95 of the 147 desktop owners on this machine
    # list "Kubuntu Developers" as Maintainer. Naming the team is accurate;
    # inventing a Kubuntu repository would not be, so the row reports the
    # archive it actually came from, read from apt rather than assumed.
    origin, section = "-", "-"
    rc, pol, _ = run(["apt-cache", "policy", "plasma-desktop"])
    if rc == 0:
        seen = []
        # A version-table line is "<pin> <uri> <suite>/<component> <arch> Packages",
        # so the URI is not at the start of the line.
        for line in pol.splitlines():
            m = re.search(r"(https?://\S+/ubuntu)\s+(\S+)/(\S+)", line)
            if m and m.group(1) not in seen:
                seen.append((m.group(1), m.group(2), m.group(3)))
        if seen:
            uri, suite, comp = seen[0]
            origin = f"{uri} {suite}/{comp}"
    rc2, show, _ = run(["apt-cache", "show", "plasma-desktop"])
    if rc2 == 0:
        m2 = re.search(r"^Section:\s*(.+)$", show, re.M)
        if m2:
            section = m2.group(1).strip()
    repo = origin if origin != "-" else (f"Ubuntu archive — {section}"
                                         if section != "-" else "-")

    row = {
        "item": f"KDE Plasma Desktop ({len(members)} components)",
        "via": "apt/KDE packages",
        "publisher": "KDE, packaged by Kubuntu for Ubuntu",
        "repo": repo,
        "pinned": ver,
        "released": (f"KDE Plasma {plasma_n} via the Ubuntu archive; "
                     f"no separate Kubuntu repository exists on this host"),
        "pin_hash": f"{len(kde_pkgs)}-pkgs:{plasma_n}",
        "rel_hash": (f"universe:{plasma_n}" if plasma != "-" else "unknown"),
        "date": kde_date_range(kde_pkgs), "is_pinned": True,
        # packages.kubuntu.org no longer resolves (verified against a public
        # resolver as well as locally); KDE retired that package browser. Plasma
        # is installed from the Ubuntu archive, so Canonical's package page is
        # the correct publisher link and is what actually resolves.
        "download": "https://packages.ubuntu.com/resolute/plasma-desktop",
        "local": False,
        "nocompare": True,
    }
    return row, sorted(members)


def image_dates():
    """Map repository -> local image creation date.

    podman reports Created as a relative string ("16 hours ago"), which is
    useless in a table, so CreatedAt is requested instead and truncated to a
    date. Read once per run rather than per container.
    """
    rc, out, _ = run(["podman", "images", "--format",
                      "{{.Repository}}|{{.CreatedAt}}"], timeout=90)
    m = {}
    if rc != 0:
        return m
    for line in out.splitlines():
        if "|" not in line:
            continue
        repo, _, created = line.partition("|")
        d = created.strip().split(" ")[0]
        repo = repo.strip()
        m.setdefault(repo, d)
        # podman always prints the registry, but a quadlet may write the short
        # form ("webodm/webodm_db"). Index both spellings so a short reference
        # finds its date instead of silently rendering as "-".
        if "/" in repo:
            host, _, short = repo.partition("/")
            if "/" not in short:
                m.setdefault(short, d)
    return m


def image_publisher(host, repo):
    """Who published a container image, from what is actually knowable here.

    The registry host is NOT the publisher: docker.io is a distribution channel,
    and anyone can push to ghcr.io under any namespace. Only a named namespace
    says anything, and an official Docker image says nothing at all. Nothing
    else was ever read -- image labels were not inspected -- so this does not
    invent a vendor.
    """
    if repo.startswith("library/"):
        return "Docker Official Image (publisher not declared)"
    org = repo.split("/")[0]
    if "/" in repo:
        return f"{org} ({host} namespace; not verified as the vendor)"
    return f"{host}/{repo} (publisher not declared)"


def containers(offline=False):
    stable = {}
    p = AO_ROOT / "config/build-update/stable-refs.yaml"
    if p.exists():
        stable = (load_yaml(p).get("images") or {})
    rows = []
    dates = image_dates()
    for f in sorted((AO_ROOT / "quadlet").glob("*/*.container")):
        ref = next((l.split("=", 1)[1].strip() for l in f.read_text().splitlines()
                    if l.startswith("Image=")), "")
        if not ref or ref.startswith("localhost/"):
            publisher = ("built on this host (ao-sim-fabrication)" if ref
                        else "no Image= line in unit")
            rows.append({"item": f.stem, "via": f"container/{f.parent.name}",
                         "publisher": publisher, "repo": ref or "no Image= line",
                         "pinned": "built on this host",
                         "released": "local build: no upstream",
                         "download": "(local build; no upstream)", "local": True,
                         "pin_hash": (dates.get(ref.split("@")[0].split(":")[0])
                                      or "not built locally"),
                         "rel_hash": "local build: no upstream",
                         "date": (dates.get(ref.split("@")[0].split(":")[0])
                                  or "no local image")})
            continue
        if "@" in ref:
            base, digest = ref.split("@", 1)
        else:
            base, digest = ref, ""
        host, _, repo = base.partition("/")
        # A quadlet may write a short reference such as "webodm/webodm_db". The
        # first component is then part of the repository path, not a registry:
        # Docker's own rule is that a first component containing no "." or ":",
        # and not named "localhost", is not a registry host. Without this, host
        # came out as "webodm", matched no registry API, and the Released hash
        # silently rendered as "-" instead of the digest.
        if not repo or ("." not in host and ":" not in host and host != "localhost"):
            repo, host = base, "docker.io"
        tag = (stable.get(f"{host}/{repo}") or {}).get("tracked_tag") or "latest"
        # One fetch serves both the short digest and the reverse version lookup.
        rel_full = None if offline else registry_digest_raw(host, repo, tag)
        released = (rel_full[:19] if rel_full
                    else "upstream digest not published for this tag")
        # Reverse-map the pinned digest to a version TAG. Without this the table
        # only ever showed two hashes, which tells a human nothing about versions.
        pin_ver = version_for(host, repo, digest) if (digest and not offline) else None
        rel_ver = version_for(host, repo, rel_full) if rel_full else None
        rows.append({
            "item": f.stem, "via": f"container/{f.parent.name}",
            "publisher": image_publisher(host, repo),
            "repo": f"{host}/{repo}" if "/" in base else f"docker.io/library/{host}",
            "pinned": pin_ver or "no version tag",
            "released": rel_ver or "no version tag",
            "tag": tag,
            "pin_hash": digest[:19] if digest else "floating tag, no digest pinned",
            "rel_hash": (rel_full[:19] if rel_full
                           else "upstream digest unreachable (registry refused)"),
            # The displayed digest is truncated for width, but a truncated digest
            # is NOT a valid manifest reference: `podman pull repo@sha256:<12>`
            # fails. Keep the full digest for anything that executes a command.
            "rel_digest": rel_full or "",
            "is_pinned": bool(digest),
            # The pull must name the TARGET digest, not the one already
            # installed. Pointing it at the pinned digest made "update this"
            # a silent no-op that re-pulled today's image and reported success.
            "download": (f"podman pull {base}@{rel_full}" if (rel_full and rel_full != digest)
                         else f"podman pull {base}@{digest}" if digest else ref),
            "local": False, "exact": False,
            "date": dates.get(base.split("@")[0], "image not present locally"),
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
        released, rel_rev, publisher = "-", "", (f[4] if len(f) > 4 else "-")
        if not offline:
            _, info, _ = run(["snap", "info", f[0]], timeout=30)
            for line in info.splitlines():
                st = line.strip()
                # The store names the publisher ("Brave Software"); `snap list`
                # only carries a verified account id ("brave**"). Prefer the name.
                if st.startswith("publisher:"):
                    named = st.split(":", 1)[1].split("(")[0].strip()
                    if named:
                        publisher = named
                elif st.startswith("latest/") and ":" in st:
                    # "latest/stable:  1.96.60 2026-09-30 rev 688 227MB -"
                    parts = st.split(":", 1)[1].split()
                    released = parts[0] if parts else "-"
                    if "rev" in parts:
                        rel_rev = parts[parts.index("rev") + 1]
                    break
        rows.append({"item": f[0], "via": f"snap/{f[3]}",
                     "publisher": publisher,
                     "repo": f"snap store (snapcraft.io/{f[0]}) — snap package, no .deb form",
                     "pinned": f[1],
                     "released": released if released != "-" else "channel unreachable",
                     # A snap exposes no sha256 digest, but the revision number is
                     # the store's real monotonic identity for that build.
                     "pin_hash": f"rev{f[2]}/{f[1]}",
                     "rel_hash": (f"rev{rel_rev}/{released}" if rel_rev
                                  else "revision not published"),
                     "is_pinned": True,
                     "download": f"https://snapcraft.io/{f[0]}", "local": False,
                     "date": snap_date(f[0], f[2])})
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
                     "pinned": f[1],
                     "released": released if released != "-" else "remote unreachable",
                     # Flatpak exposes no digest here; branch + origin is the real
                     # identity of what is installed and what the remote offers.
                     "pin_hash": f"branch:{f[2]}|origin:{f[3]}",
                     "rel_hash": (f"branch:{f[2]}|origin:{f[3]}@{released}"
                                  if released != "-" else "remote unreachable"),
                     "is_pinned": True,
                     "download": f"https://flathub.org/apps/{f[0]}", "local": False,
                     "date": flatpak_date(f[0])})
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


def direct_and_unmanaged(offline, inv=None):
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
            "released": (upstream if upstream != "-"
                         else "no release feed configured"),
            # An AppImage is a single file on disk; its own SHA-256 is the
            # installed identity, and there is no upstream digest to compare to.
            "pin_hash": file_identity(Path(a["path"])) if a.get("path")
                       else "file not on disk",
            "rel_hash": "upstream publishes no digest for this file",
            "download": a.get("linux_amd64_direct") or a.get("download_url") or "none known",
            "note": (a.get("note") or "").strip(), "local": False,
            "date": file_date(a["path"]) if a.get("path") else "no dated local file",
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
        if repo == "-" and dl != "-":
            # Name where it actually came from rather than leaving the cell blank.
            repo = dl.rstrip("/")
        if upstream == "-":
            upstream = "no upstream feed publishes updates"
        if repo == "-":
            repo = "no repository recorded"
        if dl == "-":
            dl = e.get("download_url") or "vendor site (not recorded)"
        ident = ""
        if e.get("apt_package"):
            ident = apt_installed_identity(e["apt_package"])
        elif e.get("path"):
            ident = file_identity(Path(e["path"]))
        rows.append({"item": e["name"], "via": "vendor/executable",
                     "publisher": e.get("publisher") or "see repository",
                     "repo": repo, "pinned": e.get("version", "version not recorded"),
                     "released": upstream, "download": dl,
                     "pin_hash": ident or "no local manifest",
                     "rel_hash": ("upstream version compared, no digest published"
                                  if upstream.startswith(("v", "1", "2", "3", "0", "4",
                                                          "5", "6", "7", "8", "9"))
                                  else "no upstream digest published"),
                     "note": (e.get("note") or "").strip(), "local": False,
                     "date": (apt_date(e["apt_package"]) if e.get("apt_package")
                              else file_date(e["path"]) if e.get("path")
                              else "no dated local file")})
    for dd in (reg.get("direct_downloads") or []):
        pkg = dd.get("package", "")
        rows.append({"item": f"{pkg} (direct .deb)", "via": "vendor/.deb",
                     "publisher": dd.get("publisher") or "vendor (not recorded)",
                     "repo": "no configured repository",
                     "pinned": dd.get("installed", "-"), "released": "no feed",
                     "download": (dd.get("source_url") or dd.get("download_url")
                                 or "vendor site (not recorded)"),
                     "pin_hash": apt_installed_identity(pkg),
                     "rel_hash": "no repository publishes updates",
                     "note": (dd.get("note") or "").strip(), "local": False,
                     "date": apt_date(pkg)})
    rows.extend(unindexed_debs(inv or {}))
    return rows


def unindexed_debs(inv):
    """Installed .deb packages that belong to no configured apt repository.

    crossover, obsidian and foxglove were installed from a file downloaded from
    the vendor. dpkg tracks them, but no repository declares them, so apt will
    never list an update for them and they never appeared in this table at all.
    An operator has to track these by hand, which is only useful if they are
    visible here.
    """
    rows = []
    dd = inv.get("direct_downloads") or {}
    items = ([{"package": k, **(v if isinstance(v, dict) else {})}
              for k, v in dd.items()] if isinstance(dd, dict)
             else [{"package": p} for p in dd])
    for t in items:
        pkg = t.get("package", "")
        if not pkg:
            continue
        rows.append({"item": f"{pkg} (direct .deb)", "via": "vendor/.deb",
                     "publisher": t.get("publisher") or "vendor (not recorded)",
                     "repo": "no configured repository",
                     "pinned": t.get("version", "unknown"),
                     "released": "no vendor feed publishes updates",
                     # A directly installed .deb is tracked by dpkg, so its
                     # manifest digest is a real identity even with no feed.
                     "pin_hash": apt_installed_identity(pkg),
                     "rel_hash": "no repository publishes updates",
                     "is_pinned": True,
                     "download": t.get("source_url") or "vendor site (not recorded)",
                     "local": False, "date": apt_date(pkg)})
    return rows


_APT_HISTORY_INDEX = None
_APT_HISTORY_MODULE = "unset"   # unset | None (failed) | module


def _load_apt_history():
    """Import apt_history.py by PATH, not by bare name.

    `import apt_history` resolves against sys.path, which contains the CWD --
    not the script's own directory. refresh-install-log.sh runs
    `cd "$AO_ROOT"` before invoking this file, so the bare import raised
    ImportError on every production run and the code silently fell back to the
    dpkg mtime, i.e. the exact wrong source this module exists to replace. The
    failure was invisible: the output looked normal and carried the older,
    less accurate dates. Measured before this fix:

        $ cd /tmp && python3 -c "...load provenance-log.py by path..."
        apt_date(rclone) = 2026-10-03 (dpkg mtime)     <- apt history unused

    Loading by __file__ makes it independent of CWD. A genuine failure is
    remembered so the cost is paid once, and still degrades to the mtime.
    """
    global _APT_HISTORY_MODULE
    if _APT_HISTORY_MODULE != "unset":
        return _APT_HISTORY_MODULE
    try:
        import importlib.util
        path = Path(__file__).resolve().parent / "apt_history.py"
        spec = importlib.util.spec_from_file_location("ao_apt_history", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _APT_HISTORY_MODULE = mod
    except (ImportError, OSError, AttributeError, SyntaxError):
        _APT_HISTORY_MODULE = None
    return _APT_HISTORY_MODULE


def apt_date(pkg):
    """Install date for a Debian package, from apt's own history log.

    dpkg records no install timestamp in its database. The previous source was
    the mtime of `/var/lib/dpkg/info/<pkg>.list`, which dpkg rewrites on every
    unpack -- so the column silently reported the LAST UPGRADE date under the
    heading "Installed". apt's history log does record the install, and it
    separates install from upgrade, so it is preferred.

    Three sources, in order of how well they actually answer the question:

      1. apt history  -- a real `Install:` stanza. This is the true install
         date. If a later `Upgrade:` also touched the package it is reported
         alongside, because "installed X, upgraded Y" is the honest answer.
      2. dpkg manifest mtime -- used ONLY when history has no stanza, e.g. a
         package installed before log retention reached back. This is install
         OR last upgrade and is labelled as such rather than as an install.
      3. "-" -- no evidence at all. Never guessed.

    Note the cost of source 2: for ~3,800 Ubuntu archive packages installed by
    the distribution image there is no history stanza at all, so they keep the
    mtime. That is honest (the mtime is when dpkg last unpacked) but it is not
    an install date, and the column header says so.
    """
    global _APT_HISTORY_INDEX
    if not pkg:
        return "-"
    _ah = _load_apt_history()
    if _ah is not None:
        if _APT_HISTORY_INDEX is None:
            try:
                _APT_HISTORY_INDEX = _ah.parse_history()
            except (OSError, ValueError):
                _APT_HISTORY_INDEX = {}
        date, rec = _ah.install_date(pkg, _APT_HISTORY_INDEX)
        if rec is not None and rec.get("removed"):
            # dpkg no longer lists this package. Printing its install date under
            # an "Installed" heading would be a lie told by the column, and a
            # bare "-" hides the reason. nginx was purged 2026-10-01: the
            # :8765 portal is a host python3 process now, not this container.
            return f"not installed (removed/purged {rec['date']})"
        if date and rec and rec["action"] in ("Install", "Reinstall"):
            up = (f"; upgraded {rec['upgraded']}" if rec.get("upgraded") else "")
            return f"{date} (apt history, {rec['action']}{up})"
        if date and rec and rec["action"] == "Upgrade":
            # Installed before the retained log window. The dpkg manifest mtime
            # would be the same upgrade date wearing no label, so the date is
            # shown with the distinction made explicit instead of being passed
            # off as an install.
            return f"{date} (earliest evidence: upgrade; install predates log window)"
    # dpkg names a multi-arch package's manifest "pkg:amd64.list", so a bare
    # name misses it. Try the declared name first, then the host architecture.
    names = [pkg] if ":" in pkg else [pkg, f"{pkg}:{dpkg_arch()}"]
    for n in names:
        p = Path("/var/lib/dpkg/info") / f"{n}.list"
        try:
            if p.exists():
                return (time.strftime("%Y-%m-%d", time.gmtime(p.stat().st_mtime))
                        + " (dpkg mtime)")
        except OSError:
            return "-"
    return "-"


def dpkg_arch():
    rc, out, _ = run(["dpkg", "--print-architecture"])
    return out.strip() if rc == 0 else "amd64"


def snap_date(name, rev):
    """Install date for a snap, from the blob file in /var/lib/snapd/snaps."""
    if not name:
        return "-"
    d = Path("/var/lib/snapd/snaps")
    for cand in (d / f"{name}_{rev}.snap", d / f"{name}_{rev}.squashfs"):
        try:
            if cand.exists():
                return time.strftime("%Y-%m-%d", time.gmtime(cand.stat().st_mtime))
        except OSError:
            continue
    return "-"


def file_date(path):
    """mtime of a vendor file, for software with no package database."""
    try:
        p = Path(path).expanduser()
        if p.exists():
            return time.strftime("%Y-%m-%d", time.gmtime(p.stat().st_mtime))
    except OSError:
        pass
    return "-"


def flatpak_date(app_id):
    """Install date for a flatpak, from its app directory mtime."""
    if not app_id:
        return "-"
    try:
        p = Path("/var/lib/flatpak/app") / app_id
        if p.exists():
            return time.strftime("%Y-%m-%d", time.gmtime(p.stat().st_mtime))
    except OSError:
        pass
    return "-"


def download_cell(r):
    """The Download cell states WHAT you actually get.

    A page that returns HTTP 200 is not necessarily a download, and for this
    host most are not: 16 of the landing pages are snapcraft.io (which serves
    snaps, never a .deb), 2 are GitHub repo pages (the .deb lives under
    /releases/), and 2 are PyPI (source distributions). Only 3 actually offer an
    amd64 .deb. Labelling each cell removes the chance of an operator following
    a link expecting a .deb and getting a snap instead.
    """
    via = str(r.get("via", ""))
    item = str(r.get("item", ""))
    dl = str(r.get("download", "") or "")
    if via.startswith("snap"):
        return f"`snap install {item}` — snap store, **not** a .deb"
    if via.startswith("flatpak"):
        return f"`flatpak install {dl.rsplit('/', 1)[-1]}` — flatpak, **not** a .deb"
    if via.startswith("container"):
        return f"`{dl}` — OCI image (amd64), no .deb form" if dl.startswith("podman") \
            else f"local build — no upstream artefact"
    if dl.endswith(".deb"):
        return f"[get]({dl}) — **.deb amd64**"
    if dl.lower().endswith(".appimage"):
        return f"[get]({dl}) — AppImage amd64, no .deb form"
    if dl.startswith("http"):
        return f"[page]({dl}) — publisher page, not a direct download"
    return f"`{dl}`" if dl else "no download recorded"


HEADERS = ["Item", "Via", "Publisher", "Repository / archive", "Pinned",
           "Version here", "Up to date?", "Released", "Installed identity",
           "Released identity", "Installed", "Download / source page"]


def _fmt_age(seconds):
    s = int(seconds)
    if s < 90:
        return f"{s}s"
    if s < 5400:
        return f"{s // 60}m"
    return f"{s // 3600}h"


COLLECTED = {}


def desktop_owner_packages():
    """Unqualified owning packages for every installed .desktop entry.

    Pure filesystem work: no subprocesses. Used to size the apt lookups to the
    rows that actually exist.
    """
    owners = dpkg_desktop_owners()
    pkgs = set()
    for d in (Path.home() / ".local/share/applications", Path("/usr/share/applications")):
        if not d.exists():
            continue
        for f in d.glob("*.desktop"):
            pkgs.add(owners.get(str(f), "").split(":")[0])
    pkgs.discard("")
    return pkgs


# Items an automated updater must never touch without an explicit human
# decision. Sourced from the project rules and the recorded constraints, not
# guessed: the panel review was right that this information is NOT in the
# document today, so it is stated here explicitly rather than left implicit.
EXCLUSIONS = {
    "ao-ingress-payment": "rule 7/14: payment path, operator approval required",
    "ao-ardupilot-sitl": "deliberate :latest float (recorded constraint)",
    "ao-mastodon": "deliberately held at a fixed digest (recorded constraint)",
}


# WHY a pin exists. The panel's verdict was that the Pinned column carried no
# signal because it records mechanism, not decision: apt pins everything, so ✅
# appeared everywhere and a deliberate hold looked identical to an accident.
# These are the decisions actually recorded for this host, from the project's
# own constraints - not inferred from the data.
PIN_POLICY = {
    "ao-ardupilot-sitl": ("deliberate-float",
                          "ArduPilot deliberately floats on :latest"),
    "ao-mastodon": ("deliberate-hold",
                    "Mastodon deliberately held at a fixed digest"),
    "ao-mastodon-db": ("deliberate-hold",
                       "Mastodon database deliberately held"),
    "ao-mastodon-web": ("deliberate-hold",
                        "Mastodon web deliberately held"),
    "ao-mastodon-sidekiq": ("deliberate-hold",
                            "Mastodon Sidekiq deliberately held"),
    "ao-mastodon-redis": ("deliberate-hold",
                          "Mastodon Redis deliberately held"),
    "ao-mastodon-streaming": ("deliberate-hold",
                              "Mastodon streaming deliberately held"),
}

# Items an automated updater must never touch without explicit human approval,
# with the rule that forbids it. The panel found five of ten such exclusions
# were NOT inferable from the document; recording them here is what makes the
# document safe to drive automation from.
NEEDS_APPROVAL = {
    "ao-ingress-payment": "rule 7/14: production payment path",
    "ao-webodm-db": "rule 10: photogrammetry drive verification",
    "ao-webodm-web": "rule 10: photogrammetry drive verification",
    "ao-webodm-worker": "rule 10: photogrammetry drive verification",
    "ao-webodm-broker": "rule 10: photogrammetry drive verification",
    "ao-nodeodm": "rule 10: photogrammetry drive verification",
    "ao-fabrication-db": "rule 14: production database, data volume at risk",
    "ao-sales-db": "rule 14: production database, data volume at risk",
    "ao-mastodon-db": "rule 14: production database, data volume at risk",
    "ao-mastodon-redis": "rule 14: production datastore",
}


# Verbs a plan step is permitted to start a process with. A step is an argv
# ARRAY, never a shell string, so nothing in this plan can ever reach `sh -c`.
# The allowlist exists because "executable" must mean executable-and-safe: a
# plan is generated from upstream data (image repositories, package names), and
# upstream data is not trusted input. Anything not named here is emitted as
# prose under `manual` instead, which no executor can run by accident.
PLAN_VERBS = ("podman", "snap", "flatpak", "apt", "apt-get", "systemctl")


def _argv_is_safe(argv):
    """True when an argv array may be executed as-is.

    Three properties, all of which a plain string check would miss:
      * argv[0] must be an allowlisted verb;
      * no argument may be a shell metacharacter run, so the executor cannot be
        talked into `sh -c` by a value that merely *looks* like a flag;
      * no argument may be empty or whitespace, because an empty argument
        silently becomes a different command to some tools.
    """
    if not isinstance(argv, (list, tuple)) or not argv:
        return False
    # A relative path to a repository script is itself an allowlisted action,
    # named explicitly rather than matched by verb because its basename is a
    # filename, not a verb. Checked FIRST: gating on the verb list before this
    # would reject every script path and silently downgrade the Quadlet deploy
    # step to prose, which is exactly the "eligible but not automatable" defect
    # this function exists to remove.
    if str(argv[0]).startswith("./scripts/"):
        return str(argv[0]) == "./scripts/deploy/deploy-quadlet-domain.sh"
    if os.path.basename(str(argv[0])) not in PLAN_VERBS:
        return False
    for a in argv[1:]:
        s = str(a)
        if not s.strip():
            return False
        if any(c in s for c in ";|&$`<>()\n\\\"'*?[]{}"):
            return False
    return True


def update_steps(r, unit_path=None):
    """Exact steps to apply this update, as `{"steps": [...], "manual": [...]}`.

    The split is the whole point of the function, and it was what was missing.
    Steps used to be a flat list of STRINGS mixing two different things:

      "podman pull repo@sha256:<64>"      <- a machine could run this
      "edit Image= in quadlet/mapping/x"  <- no machine could ever run this

    An item was marked `eligible` on the strength of the first while carrying
    the second, so "eligible" did not mean "automatable" and no executor could
    tell which was which. `steps` is now a list of argv arrays drawn from the
    verb allowlist; `manual` is prose a human reads. An executor consumes
    `steps` and must refuse to act when it is empty, whatever `decision` says.

    Deliberately emits NO command rather than a broken one. The Quadlet deploy
    step is the part that is easy to forget and silently leaves the old image
    running: editing the repo unit does nothing, because
    ~/.config/containers/systemd/ holds copies, not symlinks.
    """
    via = str(r.get("via", ""))
    item = str(r.get("item", ""))
    tgt = str(r.get("rel_digest") or r.get("rel_hash", ""))
    steps, manual = [], []
    if via.startswith("container"):
        # Never build a pull command from something that is not a real, COMPLETE
        # digest. Two separate defects lived here:
        #   - a prose error string ("upstream digest unreachable (registry
        #     refused)") used as a digest, producing a plausible-looking but
        #     meaningless command;
        #   - a TRUNCATED digest. Checking only the "sha256:" prefix was not
        #     enough: `sha256:` + 12 hex characters passes that test and
        #     `podman pull repo@sha256:<12>` fails HTTP 400. The length is
        #     part of what makes the reference valid, so it is checked.
        # Emitting no command at all is strictly better than emitting a broken
        # one: a human reads the row, a script gates on `steps` being non-empty.
        if not is_complete_digest(tgt):
            return {"steps": [], "manual": []}
        repo = str(r.get("repo", "")).split(" ")[0]
        steps.append(["podman", "pull", f"{repo}@{tgt}"])
        if unit_path:
            # Rewriting Image= in a Quadlet unit is a text edit with no safe
            # mechanical form: the digest may appear in several keys and the
            # line must stay parseable. It stays prose on purpose.
            manual.append(f"set Image= in {unit_path} to {tgt}")
            steps.append(["./scripts/deploy/deploy-quadlet-domain.sh",
                          unit_path.split("/")[1]])
        else:
            manual.append(f"locate the Quadlet unit for {item} and set "
                          f"Image= to {tgt}, then deploy the domain")
        steps.append(["systemctl", "--user", "daemon-reload"])
        steps.append(["systemctl", "--user", "restart", item])
    elif via.startswith("snap"):
        steps.append(["snap", "refresh", item])
    elif via.startswith("flatpak"):
        steps.append(["flatpak", "update", item])
    elif via.startswith("apt/third-party"):
        steps.append(["apt", "install", "--only-upgrade", item])
    elif via.startswith("desktop app (apt)"):
        # The Item column is the application NAME an operator recognises
        # ("Account Wizard"), not a package name. Feeding that to apt produced
        # `apt install --only-upgrade Account` - a real command that would fail,
        # or worse, match some unrelated package. Use the owning package.
        pkg = str(r.get("repo", "")).replace("apt:", "").strip()
        if pkg:
            steps.append(["apt", "install", "--only-upgrade", pkg])
    else:
        # not dpkg-owned, vendor, local build, ROS: no mechanical step exists.
        pass
    # A step that fails the safety check is downgraded to prose rather than
    # dropped, so the operator still sees the intent but no executor can run it.
    safe = [a for a in steps if _argv_is_safe(a)]
    for a in steps:
        if a not in safe:
            manual.append("manual: " + " ".join(str(x) for x in a)
                          + "   [rejected by the argv safety check]")
    return {"steps": safe, "manual": manual}


def write_update_plan(rows, out_path):
    """Emit a machine-readable plan an automated updater can gate on.

    Every item is either `eligible` with exact ordered steps, or `excluded`
    with the rule that excludes it. There is no third state and no implicit
    default, so an updater cannot act on an item whose status was never decided.

    Schema note (OPS-19): `eligible` means **a machine can carry this out**,
    not merely "no recorded rule forbids it". Each item carries two separate
    lists:

      "steps":  [ ["podman","pull","repo@sha256:<64>"], ... ]   argv arrays
      "manual": [ "set Image= in quadlet/x.container to sha256:...", ... ] prose

    `steps` is what an executor may run, and only without a shell. `manual` is
    never executable. An executor must refuse to act when `steps` is empty,
    whatever `decision` says.
    """
    plan = {
        "generated": now_utc(),
        "host": os.uname().nodename,
        "schema": 2,
        "policy": ("This plan is ADVISORY. `eligible` means the item can be "
                   "applied mechanically from `steps` alone; `excluded` means "
                   "either a recorded project rule forbids it without explicit "
                   "operator approval, or no machine-executable step exists and "
                   "a human is required (see `manual`). `steps` entries are "
                   "argv arrays: run them WITHOUT a shell. Nothing here is "
                   "executed by this tool."),
        "items": [],
    }
    for r in sorted(rows, key=lambda x: str(x.get("item", ""))):
        verdict = match_of(r)
        # Only items needing a decision. An up-to-date item is not "excluded",
        # it simply has nothing to do, and listing 200 of them buries the list.
        if verdict in ("yes", "summary", "local"):
            continue
        item = str(r.get("item", ""))
        pol, why = pin_policy(item)
        unit = None
        if str(r.get("via", "")).startswith("container"):
            for f in sorted((AO_ROOT / "quadlet").glob("*/*.container")):
                if f.stem == item:
                    unit = str(f.relative_to(AO_ROOT))
                    break
        approval = NEEDS_APPROVAL.get(item)
        pol_key = pol
        deliberate = pol != "mechanism-default"
        sm = update_steps(r, unit)
        steps, manual = sm["steps"], sm["manual"]
        if approval:
            decision, reason = "excluded", approval
        elif pol_key == "deliberate-float":
            # Floating is itself the recorded decision. Never auto-update it,
            # whatever the upstream digest happens to say today.
            decision, reason = ("excluded",
                                f"deliberate decision on record: {why}")
        elif pol_key == "deliberate-hold" and verdict == "**NO**":
            decision, reason = ("excluded",
                                f"deliberate decision on record: {why}")
        elif not steps:
            # "eligible" is reserved for items a machine can ACTUALLY carry out.
            # An item whose only instructions are prose is not automatable, and
            # marking it eligible is what made this plan untrustworthy: a
            # consumer gating on `decision == "eligible"` had no way to tell
            # `podman pull <digest>` from `edit Image= in <file>`. Those items
            # are now excluded with a reason that says a human is required, and
            # the prose is preserved under `manual`.
            decision, reason = ("excluded",
                                "no machine-executable step exists for this "
                                "source; the remainder is prose under `manual` "
                                "and needs a human")
        elif verdict != "**NO**":
            # "?" means no upstream comparison was performed. That is not
            # evidence of being behind, so it must never authorise an update.
            decision, reason = ("excluded",
                                "no evidence of being behind; verdict is "
                                "'unknown', not 'behind'")
        else:
            decision, reason = "eligible", (why if deliberate
                                            else "no exclusion recorded")
        plan["items"].append({
            "item": item,
            "via": r.get("via", "-"),
            "verdict": verdict,
            "current": r.get("pinned", "-"),
            "target": r.get("released", "-"),
            "installed_identity": r.get("pin_hash", "-"),
            "target_identity": r.get("rel_hash", "-"),
            "target_digest_full": r.get("rel_digest") or r.get("rel_hash", "-"),
            "pin_policy": pol,
            "pin_reason": why,
            "decision": decision,
            "reason": reason,
            "unit": unit,
            # `steps` are argv arrays drawn from the verb allowlist in
            # provenance-log.py; an executor MUST refuse to run them through a
            # shell. `manual` is prose and is never executable.
            "steps": steps if decision == "eligible" else [],
            "manual": manual,
        })
    n_el = sum(1 for i in plan["items"] if i["decision"] == "eligible")
    n_ex = len(plan["items"]) - n_el
    plan["summary"] = {
        "behind": sum(1 for i in plan["items"] if i["verdict"] == "**NO**"),
        "eligible": n_el, "excluded": n_ex,
    }
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    t = p.with_suffix(p.suffix + ".tmp")
    t.write_text(json.dumps(plan, indent=2, sort_keys=False), encoding="utf-8")
    t.replace(p)
    return plan


def pin_policy(item):
    """deliberate-float / deliberate-hold / mechanism-default, with the reason."""
    return PIN_POLICY.get(item, ("mechanism-default",
                                  "not a recorded decision; this is how the "
                                  "package manager already holds it"))


def update_risk(r):
    """Why this behind item is not a one-command fix, from what we know."""
    item = str(r.get("item", ""))
    via = str(r.get("via", ""))
    for k, why in EXCLUSIONS.items():
        if item.startswith(k):
            return why
    if "webodm" in item or "nodeodm" in item:
        return "rule 10: verify the photogrammetry drive before touching"
    if via.startswith("container") and "db" in item or "postgres" in str(
            r.get("repo", "")).lower() or "redis" in str(r.get("repo", "")).lower():
        return "database: migration and data-volume risk, operator decision"
    if via.startswith("apt/ROS"):
        return "repository unreachable (TLS); cannot be fetched at all"
    if via.startswith("container"):
        return ("edit quadlet/<domain>/<unit>.container, redeploy (Quadlet "
                "copies, not symlinks), then systemctl --user restart")
    if via.startswith("vendor") or via.startswith("apt/third-party"):
        return "third-party; not covered by unattended-upgrades"
    return "operator decision"


def render(inv, codename, offline):
    """One table. Every row, the same twelve columns, top to bottom."""
    # Prime the apt lookup maps with ONE call each. Doing this per row spawned
    # ~230 apt subprocesses and the run stopped completing in reasonable time.
    _CAND_VER.clear()
    # Only packages that actually appear as a row need a lookup. Querying all
    # 4,493 installed packages meant hundreds of apt round trips for ~230 answers.
    all_pkgs = {t["package"] for t in inv.get("apt_packages", [])
                if t["release"].startswith("Third-party")}
    all_pkgs |= desktop_owner_packages()
    _CAND_VER.update(apt_candidate_map(all_pkgs))
    cont, sn, fl = containers(offline), snaps(offline), flatpaks(offline)
    direct = direct_and_unmanaged(offline, inv)
    # The Ubuntu archive collapses to ONE row: 3,863 packages already covered by
    # apt and unattended-upgrades, which was 90 percent of the document and told
    # an operator nothing. Third-party repositories are listed individually,
    # because an update to those is a decision rather than a background event.
    ubuntu = ubuntu_summary(inv)
    ros = ros_summary(inv)
    gz = gazebo_summary(inv)
    third = [t for t in third_party_apt(inv) if "ros.org" not in (t["publisher"] or "")]
    apps = desktop_apps(inv)
    kde_row, kde_members = kde_block(inv)
    platform = ([kde_row] if kde_row else []) + [ubuntu_headline(inv)] + ubuntu + ros + gz
    rows = platform + cont + sn + fl + apps + third + direct

    n_ubuntu = sum(1 for t in inv.get("apt_packages", [])
                   if t["release"].startswith("Ubuntu"))
    behind = len([r for r in rows if match_of(r) == "**NO**"])
    current = len([r for r in rows if match_of(r) == "yes"])
    unknown = len([r for r in rows if match_of(r) == "?"])
    local = len([r for r in rows if match_of(r) == "local"])
    summary = len([r for r in rows if match_of(r) == "summary"])
    # Hand the collected rows back to main(). Rebuilding them there re-ran every
    # network lookup and every apt query a second time, doubling an online run.
    COLLECTED["rows"] = rows
    COLLECTED["counts"] = (behind, current, unknown, local, summary)
    COLLECTED["kde_members"] = kde_members
    COLLECTED["kde_row"] = kde_row

    L = []
    w = L.append
    w(f"# Software status - {inv['os']['pretty']} - {now_utc()[:10]}")
    w("")
    freshest = max(_CACHE_HITS.values(), default=None)
    oldest = None
    if _CACHE_HITS:
        ages = [a for a in _CACHE_HITS.values()]
        oldest, freshest = max(ages), min(ages)
    banner = []
    if offline:
        banner.append("**Offline run: cached upstream data only, no network was "
                      "contacted.**")
    if oldest is not None:
        ttl = f"{CACHE_TTL // 3600}h" if CACHE_TTL else "bypassed, every lookup forced"
        banner.append(f"Upstream data re-checked between "
                      f"{_fmt_age(freshest)} and {_fmt_age(oldest)} ago "
                      f"(cache TTL {ttl}).")
    if _CACHE_STALE:
        banner.append(f"**{len(_CACHE_STALE)} upstream lookups could not be "
                      f"re-checked and fell back to a STALE cached value.**")
    if banner:
        w(" ".join(banner))
        w("")

    # A container whose digest could not be fetched shows "-" in Released hash,
    # which is indistinguishable at a glance from "nothing to compare". Say
    # which ones failed so a blank is never read as a clean result.
    unresolved = [r["item"] for r in rows
                  if str(r.get("via", "")).startswith("container")
                  and str(r.get("rel_hash", "-")) == "-"
                  and not r.get("local")]
    if unresolved:
        w(f"**{len(unresolved)} container(s) have no Released hash:** "
          f"{', '.join(sorted(unresolved))}. Each is a distinct condition — a "
          f"local build, a floating tag, or an upstream fetch that failed; "
          f"expand the row to see which.")
        w("")
    w(f"**{len(rows)} items.** {behind} behind - {current} up to date - "
      f"{unknown} no version published - {local} local build - {summary} summary. "
      f"Plus {n_ubuntu} Ubuntu archive packages collapsed into one row: Canonical "
      f"ships and manages those, so itemising them told an operator nothing. "
      f"Generated by `scripts/build-update/provenance-log.py`; read-only.")
    w("")
    w("Publisher for snaps is the store account; a trailing `**` marks a "
      "**verified** publisher, not a claim of review. Container publishers are "
      "the registry namespace, which is where the image is hosted, NOT proof of "
      "who built it. `Installed identity` is a digest only for containers; for "
      "packages it is a dpkg-manifest hash, for snaps a revision, and for "
      "roll-ups an aggregate label.")
    w("")
    # TRIAGE FIRST. The full inventory is 229 rows and the items needing a
    # decision are scattered through it. Both reviewers of this document said
    # the same thing: it proves provenance rigorously and fails at triage, so
    # the actionable set is lifted to the top where the eye lands.
    action = [r for r in rows if match_of(r) in ("**NO**",)]
    if action:
        w("## Needs action")
        w("")
        w(f"**{len(action)} item(s) are behind.** Everything else in this "
          f"document is inventory and needs no decision.")
        w("")
        w("| Item | Via | Here | Target | Pin policy | Why it cannot simply be updated | Command to apply |")
        w("|---|---|---|---|---|---|---|")
        for r in sorted(action, key=lambda x: (x.get("via", ""), x["item"])):
            risk = update_risk(r)
            pol = pin_policy(str(r["item"]))[0]
            cmd = (r.get("download") or "no automated command")
            w(f"| `{r['item']}` | {r.get('via','-')} | `{r.get('pinned','-')}` | "
              f"`{str(r.get('released','-')).split(' ')[0]}` | {pol} | {risk} | "
              f"{('[cmd](' + cmd + ')' if cmd.startswith('http') else '`' + cmd + '`')} |")
        w("")
        w("**Nothing here has been updated.** Applying any of these is an "
          "operator decision; several carry exclusions recorded in "
          "`docs/runbooks/software-update.md` (WebODM and the payment path "
          "require prior verification).")
        w("")
    w("## Full inventory")
    w("")
    # The last column mixes three different kinds of evidence, so the header
    # names all three rather than calling them all "Installed":
    #   (apt history) - a real Install: stanza in /var/log/apt/history.log.
    #   (dpkg mtime)  - no apt record; the mtime of the dpkg manifest, which
    #                   dpkg rewrites on every unpack. That is install OR last
    #                   upgrade and cannot be told apart from the filesystem.
    #   - (pre-window upgrade D) - apt shows an upgrade but no install, so the
    #                   package predates the retained log window.
    w("Last column: `(apt history)` is the real install date from "
      "`/var/log/apt/history.log`. `(dpkg mtime)` means no apt record exists "
      "and the value is the dpkg manifest mtime, which is install OR last "
      "upgrade and cannot be distinguished. `- (pre-window upgrade D)` means "
      "apt shows the package upgraded on D but installed it before the "
      "retained log window.")
    w("")
    w("| Item | Via | Publisher | Repository / archive | Pinned | Version here | "
      "Up to date? | Released | Installed identity | Released identity | Installed | Download / source page |")
    w("|---|---|---|---|:---:|---|:---:|---|---|---|---|---|")
    rank = {"**NO**": 0, "?": 1, "summary": 2, "local": 3, "yes": 4}
    # ALL platform rows, in reading order: the desktop, the OS, the packages the
    # OS carries, the robot stack bound to it, and the simulator. A partial list
    # here silently pushed KDE and UBUNTU down into the ordinary ranking.
    platform_order = {"KDE Plasma Desktop": 0, "UBUNTU": 1,
                      "Ubuntu archive packages": 2, "ROS 2": 3, "Gazebo Sim": 4}
    def sortkey(x):
        # The three platform rows lead the table, in order, so the base system,
        # the robot stack bound to it, and the simulator read together.
        for k, n in platform_order.items():
            if str(x.get("item", "")).startswith(k):
                return (-1, n, "")
        return (rank.get(match_of(x), 5), 9, str(x.get("item", "")).lower())
    for r in sorted(rows, key=sortkey):
        cell = download_cell(r)
        mark = "\u2705" if r.get("is_pinned") else "\u274c"
        up = {"yes": "yes", "**NO**": "**NO**", "?": "?",
              "local": "local", "summary": "not applicable (roll-up)"}[match_of(r)]
        tag = r.get("tag")
        rel = f"`{r['released']}`" + (f" ({tag})" if tag else "")
        item = f"`{r['item']}`"
        if r.get("italic"):
            item = f"*{item}*"
        w(f"| {item} | {r['via']} | {r['publisher']} | {r['repo']} | {mark} | "
          f"`{r['pinned']}` | {up} | {rel} | `{r.get('pin_hash', '-')}` | "
          f"`{r.get('rel_hash', '-')}` | {r.get('date', '-')} | {cell} |")
    w("")
    return "\n".join(L) + "\n" + rollup_details_md(rows, kde_members) + "\n"


def rollup_details_md(rows, kde_members=None):
    """The collapsible drill-down blocks that follow the main table.

    Split out of `render()` so it can be tested: `render()` spends hundreds of
    apt round trips, which is not something a unit test should pay for to
    assert a formatting rule.
    """
    out = []
    w = out.append
    rolled = [(r["item"], r["members"]) for r in rows
              if r.get("members") and not r.get("package_rollup")]
    if rolled:
        w("")
        w("<details><summary>Rolled-up launchers — expand to list every "
          f"application entry ({sum(len(m) for _, m in rolled)} entries "
          f"across {len(rolled)} groups)</summary>")
        w("")
        w("| Package / group | Launchers |")
        w("|---|---|")
        for item, members in sorted(rolled):
            w(f"| `{item}` | {', '.join(members)} |")
        w("")
        w("</details>")
    # A package roll-up has thousands of members. Joining them into one table
    # cell produced a single 40,000-character line -- technically a drill-down,
    # practically unreadable, and worse than the count it replaced. One member
    # per row, in its own collapsible block per roll-up.
    for r in rows:
        if not (r.get("package_rollup") and r.get("members")):
            continue
        w("")
        w(f"<details><summary>{r['item']} — expand to list all "
          f"{len(r['members'])} packages with their installed versions"
          "</summary>")
        w("")
        w("| Package | Installed version |")
        w("|---|---|")
        for m in r["members"]:
            name, _, ver = m.rpartition(" (")
            w(f"| `{name}` | `{ver.rstrip(')')}` |")
        w("")
        w("</details>")
    if kde_members:
        w("")
        w(f"<details><summary>KDE Plasma Desktop — expand to list all "
          f"{len(kde_members)} components</summary>")
        w("")
        w("| Component | Owning package |")
        w("|---|---|")
        for nm, pk in kde_members:
            w(f"| {nm} | {('`' + pk + '`') if pk else '-'} |")
        w("")
        w("</details>")
    return "\n".join(out)


UNKNOWN = ("-", "no upstream", "no upstream feed", "no feed", "unreachable",
           "not recorded", "not installed by a package", "")


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


NOT_A_VALUE = (
    "no upstream feed publishes updates", "no upstream digest published",
    "no repository checksum", "no candidate published", "candidate unavailable",
    "no vendor feed publishes updates", "no repository publishes updates",
    "no release feed configured", "no upstream digest for this tag",
    "revision not published", "no package repository", "version not recorded",
    "no version published", "remote unreachable", "channel unreachable",
)


def match_of(r):
    # A row with nothing to compare against is not "behind" - it is simply a
    # summary. The collapsed Ubuntu row compares two prose strings and would
    # otherwise always read as a finding.
    if r.get("nocompare"):
        return "summary"
    if r.get("force_match"):
        return r["force_match"]
    # If either side is an explicit "this is not a value" marker, there is
    # nothing to compare. Two identical error strings once compared equal and
    # produced a confident "yes" on a row whose version was never even read.
    for k in ("pinned", "released"):
        if str(r.get(k, "")).strip().lower() in NOT_A_VALUE:
            return "?"
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
       # The inline roll-up drill-down lives inside a table cell, where a 1rem
       # block margin would break the row height and a 6.6pt print rule would
       # hide it entirely. It has to stay compact and always open when printed.
       "details.drill{margin:.15rem 0}details.drill>summary{font-weight:500;"
       "font-size:10.5px;color:#495057}details.drill ul{margin:.2rem 0 0 1rem;"
       "padding-left:.6rem}@media print{details.drill{display:block}"
       "details.drill ul{display:block}}"
       "h1,h2{border-bottom:1px solid #d0d3d6;padding-bottom:.3rem}"
       "blockquote{border-left:4px solid #adb5bd;margin:1rem 0;padding:.4rem 1rem;color:#495057}""h1{font-size:15pt} .counts{font-size:9pt;color:#444;margin:.2rem 0 .6rem}""tr.behind td{background:#fdecea}""@page{size:A4 landscape;margin:9mm}""thead{display:table-header-group} tr{page-break-inside:avoid}""body{font-size:6.6pt} table{font-size:6.2pt} th,td{padding:1px 2px}""code{font-size:5.8pt;background:none;padding:0}")


def rows_to_html(rows, counts, title, kde_members=None):
    """Emit the table straight to HTML, bypassing python-markdown.

    python-markdown's table extension does not finish on a table this size, so
    the markdown round-trip is skipped and the rows are written directly. Same
    data, same columns.
    """
    import html as H
    out = [f"<!doctype html><html><head><meta charset='utf-8'>"
           f"<title>{H.escape(title)}</title><style>{CSS}</style></head><body>",
           f"<h1>{H.escape(title)}</h1>", f"<p class='counts'>{H.escape(counts)}</p>",
           "<table><thead><tr>" + "".join(f"<th>{H.escape(h)}</th>" for h in HEADERS)
           + "</tr></thead><tbody>"]
    rank = {"**NO**": 0, "?": 1, "summary": 2, "local": 3, "yes": 4}
    # ALL platform rows, in reading order: the desktop, the OS, the packages the
    # OS carries, the robot stack bound to it, and the simulator. A partial list
    # here silently pushed KDE and UBUNTU down into the ordinary ranking.
    platform_order = {"KDE Plasma Desktop": 0, "UBUNTU": 1,
                      "Ubuntu archive packages": 2, "ROS 2": 3, "Gazebo Sim": 4}
    def sortkey(x):
        # The three platform rows lead the table, in order, so the base system,
        # the robot stack bound to it, and the simulator read together.
        for k, n in platform_order.items():
            if str(x.get("item", "")).startswith(k):
                return (-1, n, "")
        return (rank.get(match_of(x), 5), 9, str(x.get("item", "")).lower())
    for r in sorted(rows, key=sortkey):
        dl = r.get("download", "-")
        dl_cell = (f'<a href="{H.escape(str(dl))}">get</a>' if str(dl).startswith("http")
                   else H.escape(str(dl)))
        tag = r.get("tag")
        rel = H.escape(str(r["released"])) + (f" ({H.escape(str(tag))})" if tag else "")
        _it = H.escape(str(r["item"]))
        _item = f"<em><code>{_it}</code></em>" if r.get("italic") else f"<code>{_it}</code>"
        # A roll-up row is a dead end without its members: "plasma-workspace
        # (28 launchers)" tells an operator nothing they cannot act on unless
        # they can see which 28. The markdown path has a <details> block per
        # roll-up, but the HTML table did not - those members were computed,
        # carried on the row, and then silently dropped. So they are drilled
        # into inline here, on the row itself, where the count promised them.
        members = r.get("members") or []
        if members:
            lis = "".join(f"<li>{H.escape(str(m))}</li>" for m in members)
            _item += (f"<details class='drill'><summary>"
                      f"{len(members)} entries</summary>"
                      f"<ul>{lis}</ul></details>")
        cells = [_item,
                 H.escape(str(r["via"])), H.escape(str(r["publisher"])),
                 H.escape(str(r["repo"])),
                 "&#10003;" if r.get("is_pinned") else "&#10007;",
                 f"<code>{H.escape(str(r['pinned']))}</code>",
                 H.escape(str(match_of(r)).replace("**", "")),
                 f"<code>{rel}</code>",
                 f"<code>{H.escape(str(r.get('pin_hash', '-')))}</code>",
                 f"<code>{H.escape(str(r.get('rel_hash', '-')))}</code>",
                 H.escape(str(r.get('date', '-'))), dl_cell]
        cls = "behind" if match_of(r) == "**NO**" else ""
        out.append(f"<tr class='{cls}'>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    out.append("</tbody></table>")
    if kde_members:
        items = "".join(f"<li>{H.escape(str(n))}"
                         + (f" &mdash; <code>{H.escape(str(p))}</code>" if p else "")
                         + "</li>" for n, p in kde_members)
        out.append(f"<details><summary>KDE Plasma Desktop &mdash; expand to list all "
                   f"{len(kde_members)} components</summary><ul>{items}</ul></details>")
    out.append("</body></html>")
    return "\n".join(out)


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
    ap.add_argument("--offline", action="store_true",
                    help="use cached upstream data only; never touch the network")
    ap.add_argument("--plan", help="write a machine-readable update plan JSON")
    ap.add_argument("--refresh", action="store_true",
                    help="ignore the cache TTL and re-check every upstream "
                         "value now (this is how the Released hash column is "
                         "brought up to date quickly)")
    args = ap.parse_args()
    global OFFLINE, CACHE_TTL
    OFFLINE = args.offline
    if args.refresh and not OFFLINE:
        # TTL 0 makes every cached entry read as expired, so each lookup is
        # re-fetched. Failed fetches are still never written as values.
        CACHE_TTL = 0

    if not INVENTORY.exists():
        sys.exit("ERROR: run inventory-full.py first.")
    inv = json.loads(INVENTORY.read_text())
    text = render(inv, inv["os"]["codename"], args.offline)
    _rows = COLLECTED["rows"]
    _km = COLLECTED["kde_members"]
    behind, current, unknown, local, _summary = COLLECTED["counts"]

    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        t = p.with_suffix(p.suffix + ".tmp")
        t.write_text(text, encoding="utf-8")
        t.replace(p)
        print(f"wrote {p}")
    else:
        print(text)

    if args.plan:
        plan = write_update_plan(_rows, args.plan)
        print(f"wrote {args.plan}: {plan['summary']}")

    if args.html:
        rows = ubuntu_summary(inv) + ros_summary(inv) + gazebo_summary(inv) + _rows
        title = f"ALWAYS ON - Software Status - {inv['os']['pretty']}"
        counts = (f"{len(rows)} items. {behind} behind - {current} up to date - "
                  f"{unknown} no version published - {local} local build.")
        h = Path(args.html)
        h.parent.mkdir(parents=True, exist_ok=True)
        h.write_text(rows_to_html(rows, counts, title, _km), encoding="utf-8")
        print(f"wrote {h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
