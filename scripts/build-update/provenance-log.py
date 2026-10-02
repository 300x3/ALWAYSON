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
                "pinned": pinned, "released": "no upstream feed",
                "pin_hash": "-", "rel_hash": "-",
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
                "released": "no upstream feed",
                "pin_hash": "-", "rel_hash": "-", "is_pinned": False,
                "download": "vendor site (not recorded)",
                "local": False, "date": file_date(p) if p.exists() else "-",
            }
        # NEVER let released mirror pinned. When both held the same string,
        # same_version() returned True and the row claimed to be "up to date"
        # with no upstream comparison performed at all. There is no feed for a
        # plain apt package here, so these honestly stay "?" until one exists.
        row["force_match"] = "?"
        if multi:
            row["members"] = names
        rows.append(row)
    return rows


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
        "publisher": "Canonical",
        "repo": "archive.ubuntu.com + security.ubuntu.com",
        "pinned": f"{len(ubuntu)} packages, {inv['os']['pretty']}",
        "released": "managed by apt; security pocket unattended",
        "pin_hash": "-", "rel_hash": "-", "is_pinned": True,
        "download": "https://packages.ubuntu.com/resolute/",
        "local": False, "nocompare": True, "platform": True,
    }]


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
        rows.append({
            "item": t["package"], "via": "apt/third-party",
            "publisher": (t["origin"] or "vendor").split("/")[0],
            "repo": f"{t.get('component') or '-'}",
            "pinned": t["version"], "released": t["version"],
            "pin_hash": "-", "rel_hash": "-", "is_pinned": True,
            "download": "-", "local": False,
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
        "pin_hash": "55f8dbcf8decb0b9", "rel_hash": "-", "is_pinned": True,
        "download": "https://packages.osrfoundation.org/gazebo/ubuntu-stable/",
        "local": True, "platform": True,
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
        "pin_hash": "-", "rel_hash": "-", "is_pinned": True,
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
        "publisher": "packages.ros.org",
        "repo": f"{len(ros)} packages, suite {'/'.join(suites)}",
        "pinned": f"{distro}, built for Ubuntu {policy.get('validate_against_release','26.04')}",
        "released": state,
        "pin_hash": "-", "rel_hash": "-", "is_pinned": True,
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
        "pin_hash": "-", "rel_hash": "-", "is_pinned": True,
        "download": "https://packages.kubuntu.org/", "local": False,
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
            publisher = "built on this host (ao-sim-fabrication)" if ref else "-"
            rows.append({"item": f.stem, "via": f"container/{f.parent.name}",
                         "publisher": publisher, "repo": ref or "-",
                         "pinned": "-", "released": "no upstream",
                         "download": "(local build; no upstream)", "local": True,
                         "date": dates.get(ref.split("@")[0].split(":")[0], "-")})
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
        released = rel_full[:19] if rel_full else "-"
        # Reverse-map the pinned digest to a version TAG. Without this the table
        # only ever showed two hashes, which tells a human nothing about versions.
        pin_ver = version_for(host, repo, digest) if (digest and not offline) else None
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
            "date": dates.get(base.split("@")[0], "-"),
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
        released, publisher = "-", (f[4] if len(f) > 4 else "-")
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
                    # "latest/stable:  1.96.60 2026-09-30 (688) 227MB -"
                    released = st.split(":", 1)[1].split()[0]
                    break
        rows.append({"item": f[0], "via": f"snap/{f[3]}",
                     "publisher": publisher,
                     "repo": "snap store",
                     "pinned": f[1], "released": released or "-", "is_pinned": True,
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
                     "pinned": f[1], "released": released or "-", "is_pinned": True,
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
            "released": upstream,
            "download": a.get("linux_amd64_direct") or a.get("download_url") or "none known",
            "note": (a.get("note") or "").strip(), "local": False,
            "date": file_date(a["path"]) if a.get("path") else "-",
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
                     "note": (e.get("note") or "").strip(), "local": False,
                     "date": (apt_date(e["apt_package"]) if e.get("apt_package")
                              else file_date(e["path"]) if e.get("path") else "-")})
    for dd in (reg.get("direct_downloads") or []):
        pkg = dd.get("package", "")
        rows.append({"item": f"{pkg} (direct .deb)", "via": "vendor/.deb",
                     "publisher": dd.get("publisher") or "vendor", "repo": "no feed",
                     "pinned": dd.get("installed", "-"), "released": "no feed",
                     "download": dd.get("source_url") or dd.get("download_url") or "-",
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
                     "pinned": t.get("version", "-"), "released": "no feed",
                     "pin_hash": "-", "rel_hash": "-", "is_pinned": True,
                     "download": t.get("source_url") or "vendor site (not recorded)",
                     "local": False, "date": apt_date(pkg)})
    return rows


def apt_date(pkg):
    """Install date for a Debian package.

    dpkg records no install timestamp in its database, so the only local
    evidence is the mtime of the package's .list file, written when dpkg last
    unpacked it. That is the install OR last upgrade date - there is no way to
    tell which, so the column is labelled honestly rather than pretending.
    """
    if not pkg:
        return "-"
    for suf in (".list",):
        p = Path("/var/lib/dpkg/info") / f"{pkg}{suf}"
        try:
            if p.exists():
                return time.strftime("%Y-%m-%d",
                                     time.gmtime(p.stat().st_mtime))
        except OSError:
            return "-"
    return "-"


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


HEADERS = ["Item", "Via", "Publisher", "Repository / archive", "Pinned",
           "Version here", "Up to date?", "Released", "Pinned hash",
           "Released hash", "Installed", "Download"]


def _fmt_age(seconds):
    s = int(seconds)
    if s < 90:
        return f"{s}s"
    if s < 5400:
        return f"{s // 60}m"
    return f"{s // 3600}h"


COLLECTED = {}


def render(inv, codename, offline):
    """One table. Every row, the same twelve columns, top to bottom."""
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
        banner.append(f"Upstream data re-checked between "
                      f"{_fmt_age(freshest)} and {_fmt_age(oldest)} ago "
                      f"(cache TTL {CACHE_TTL // 3600}h).")
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
    w("| Item | Via | Publisher | Repository / archive | Pinned | Version here | "
      "Up to date? | Released | Pinned hash | Released hash | Installed | Download |")
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
        dl = r.get("download", "-")
        cell = (f"[get]({dl})" if str(dl).startswith("http")
                else (f"`{dl}`" if str(dl).startswith("podman") else str(dl)))
        mark = "\u2705" if r.get("is_pinned") else "\u274c"
        up = {"yes": "yes", "**NO**": "**NO**", "?": "?",
              "local": "local", "summary": "-"}[match_of(r)]
        tag = r.get("tag")
        rel = f"`{r['released']}`" + (f" ({tag})" if tag else "")
        item = f"`{r['item']}`"
        if r.get("italic"):
            item = f"*{item}*"
        w(f"| {item} | {r['via']} | {r['publisher']} | {r['repo']} | {mark} | "
          f"`{r['pinned']}` | {up} | {rel} | `{r.get('pin_hash', '-')}` | "
          f"`{r.get('rel_hash', '-')}` | {r.get('date', '-')} | {cell} |")
    rolled = [(r["item"], r["members"]) for r in rows if r.get("members")]
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
    w("")
    return "\n".join(L) + "\n"


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


def match_of(r):
    # A row with nothing to compare against is not "behind" - it is simply a
    # summary. The collapsed Ubuntu row compares two prose strings and would
    # otherwise always read as a finding.
    if r.get("nocompare"):
        return "summary"
    if r.get("force_match"):
        return r["force_match"]
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
