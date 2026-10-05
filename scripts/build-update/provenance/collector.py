"""Evidence gathering: what is installed and where it came from.

Every function that reads local state, spawns a subprocess or queries an
upstream endpoint. This is the only module with mutable module-level caches
(`_CACHE_HITS`, `_CAND_VER`, `COLLECTED`, `OFFLINE`); they exist because the
un-cached form spawned ~230 apt subprocesses per run and stopped completing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
import urllib.error
import urllib.request

from .common import (AO_ROOT, ARCHIVE_PAGES, INVENTORY, TIMEOUT,
                     UNMANAGED, is_complete_digest, load_yaml, norm, now_utc, run)




CACHE_DIR = AO_ROOT / "data/build-update/cache"


CACHE_DIR = AO_ROOT / "data/build-update/cache"
# How long a fetched "latest version" stays usable without re-checking. A stale
# verdict is still reported, but age is written into the document so a reader can
# see it. Re-checking is cheap; lying about freshness is not.
CACHE_TTL = int(os.environ.get("AO_CACHE_TTL", "21600"))   # 6h


_CACHE_TTL = [int(os.environ.get("AO_CACHE_TTL", "21600"))]   # 6h
OFFLINE = False          # set by --offline; never touches the network


def cache_ttl() -> int:
    """Seconds a fetched upstream value stays usable without re-checking.

    A list cell, not a plain global, because `--refresh` rebinds the TTL at
    runtime and `render` reads it to print the banner. A bare global read in
    another module would bind a stale copy at import time and print the
    default TTL even on a forced refresh. One accessor, one owner.
    """
    return _CACHE_TTL[0]


def set_cache_ttl(seconds: int) -> None:
    _CACHE_TTL[0] = seconds


OFFLINE = False          # set by --offline; never touches the network
_CACHE_HITS = {}


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
    if rec and (time.time() - rec.get("ts", 0)) < cache_ttl():
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
    if rec and (time.time() - rec.get("ts", 0)) < cache_ttl():
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
        # apt_history.py is a SIBLING OF THE PACKAGE, not a sibling of this
        # file: the split (OPS-18) moved this function into provenance/ while
        # apt_history.py stayed in scripts/build-update/. The original
        # `parent / "apt_history.py"` pointed INSIDE the package and raised
        # FileNotFoundError, which the except clause below swallowed into
        # None - the same silent fallback to the dpkg mtime this function was
        # written to eliminate, reintroduced by the refactor.
        #
        # Both locations are tried so the lookup is independent of where this
        # module is vendored from.
        here = Path(__file__).resolve().parent
        for cand in (here.parent / "apt_history.py", here / "apt_history.py"):
            if cand.is_file():
                path = cand
                break
        else:
            raise OSError("apt_history.py not found next to the provenance package")
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
    global OFFLINE
    OFFLINE = args.offline
    if args.refresh and not OFFLINE:
        # TTL 0 makes every cached entry read as expired, so each lookup is
        # re-fetched. Failed fetches are still never written as values.
        set_cache_ttl(0)

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
