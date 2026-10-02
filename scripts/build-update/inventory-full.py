#!/usr/bin/env python3
"""ALWAYS ON ao-build-update: exhaustive installed-software inventory.

Every piece of software on the host, with each item tagged FIRST to the Ubuntu
26.04 LTS release it belongs to and only then to the repository that delivers it.

Release-first tagging
---------------------
The release is the primary key because that is the question an operator actually
asks: "is this part of my supported platform, or is it something someone else
ships?" Every apt package resolves to exactly one of:

    Ubuntu LTS (base)       *.ubuntu.com, suite == the release codename
    Ubuntu LTS updates      *.ubuntu.com, suite == <codename>-updates
    Ubuntu LTS security     *.ubuntu.com, suite == <codename>-security
    Third-party: <host>     every other repository (nvidia, microsoft, google,
                            steam, vscodium, gh, nodesource, OSRF, ros) -
                            NOT part of Ubuntu 26.04 LTS
    Not in any apt index    installed but absent from every downloaded index

Software that no apt package owns is grouped by delivery mechanism instead,
because "how does this get updated" is the other half of the answer. An earlier
version of this inventory only looked at package managers and therefore missed
the 300+ desktop applications, the AppImages, the /opt trees, and the ~90
executables in ~/.local/bin.

Usage:
  inventory-full.py [--markdown] [--out FILE] [--json-only]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

AO_ROOT = Path(os.environ.get("AO_ROOT", "/ALWAYSON"))
LISTS = Path("/var/lib/apt/lists")
DPKG_STATUS = Path("/var/lib/dpkg/status")
DESKTOP_DIRS = [Path("/usr/share/applications"),
                Path.home() / ".local/share/applications"]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run(cmd, timeout=120):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, check=False)
        return p.returncode, p.stdout, p.stderr
    except (subprocess.TimeoutExpired, OSError) as e:
        return 127, "", str(e)


def os_release():
    info = {}
    f = Path("/etc/os-release")
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                info[k] = v.strip().strip('"')
    return {"pretty": info.get("PRETTY_NAME", "unknown"),
            "id": info.get("ID", "unknown"),
            "version_id": info.get("VERSION_ID", "unknown"),
            "codename": info.get("VERSION_CODENAME", "unknown")}


def release_tag(host, suite, codename):
    if "ubuntu.com" in host:
        if suite == codename:
            return f"Ubuntu {codename} LTS (base)"
        if suite.endswith("-security"):
            return "Ubuntu LTS security"
        if suite.endswith("-updates"):
            return "Ubuntu LTS updates"
        return f"Ubuntu ({suite or codename})"
    return f"Third-party: {host}"


def installed_packages():
    """package -> installed version, from one parse of the dpkg status file."""
    out = {}
    if not DPKG_STATUS.exists():
        return out
    for block in DPKG_STATUS.read_text(errors="replace").split("\n\n"):
        if "Status: install ok installed" not in block:
            continue
        name = ver = None
        for line in block.splitlines():
            if line.startswith("Package: "):
                name = line[9:].strip()
            elif line.startswith("Version: "):
                ver = line[9:].strip()
        if name and ver:
            out[name] = ver
    return out


def index_files():
    """package -> (version, host, suite, component) from apt's downloaded indexes.

    The filename encodes the repository, which is how every package gets its
    release attribution without a per-package `apt-cache policy` call (that would
    be 4000+ subprocesses).
    """
    found = {}
    for path in sorted(glob.glob(str(LISTS / "*_Packages"))):
        base = os.path.basename(path)
        m = re.match(r"(.+?)_dists_(.+?)_(.+?)_binary-[^_]+_Packages$", base)
        if m:
            host_raw, suite, component = m.group(1), m.group(2), m.group(3)
        else:
            m2 = re.match(r"(.+?)_Packages$", base)
            if not m2:
                continue
            host_raw, suite, component = m2.group(1), "", ""
        host = (host_raw.replace("%5f", "_").replace("%3a", ":")
                       .replace("__", "/").replace("_", "/"))
        try:
            text = Path(path).read_text(errors="replace")
        except OSError:
            continue
        for block in text.split("\n\n"):
            name = ver = None
            for line in block.splitlines():
                if line.startswith("Package: "):
                    name = line[9:].strip()
                elif line.startswith("Version: "):
                    ver = line[9:].strip()
            if name and ver:
                # First index wins: apt prefers earlier sources, so a package
                # present in several repos is attributed to the one that would
                # actually be installed.
                found.setdefault(name, (ver, host, suite, component))
    return found


def desktop_apps(installed):
    """Every installed GUI application, from the .desktop entries themselves."""
    apps = []
    for d in DESKTOP_DIRS:
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
            if name:
                apps.append({"id": f.stem, "name": name, "scope": d.parent.name,
                             "apt_package": pkg or "",
                             "apt_version": installed.get(pkg, "") if pkg else ""})
    return apps


def non_package_apps():
    """Applications no package manager owns. None of these update themselves."""
    apps = []
    for root in (Path.home() / "Applications", Path.home() / "Documents",
                 Path("/opt"), Path("/usr/local"), Path.home() / ".local/bin"):
        if not root.exists():
            continue
        try:
            found = list(root.rglob("*.AppImage"))
        except (OSError, PermissionError):
            found = []
        for f in sorted(found)[:80]:
            apps.append({"kind": "AppImage", "name": f.name, "path": str(f),
                         "update_source": "MANUAL re-download; no package manager"})
    opt = Path("/opt")
    if opt.exists():
        for d in sorted(opt.iterdir()):
            if d.is_dir():
                apps.append({"kind": "/opt tree", "name": d.name, "path": str(d),
                             "update_source": "MANUAL; installed under /opt, not apt"})
    ulb = Path("/usr/local/bin")
    if ulb.exists():
        for f in sorted(ulb.iterdir()):
            if f.is_file() or f.is_symlink():
                apps.append({"kind": "/usr/local/bin", "name": f.name, "path": str(f),
                             "update_source": "MANUAL; built or dropped locally"})
    return apps


def user_binaries():
    """Executables in ~/.local/bin, classified by what plausibly provides them."""
    third = {"bun", "bunx", "gh", "obsidian", "pcloud", "google-chrome",
             "google-chrome-stable", "mcp", "cline", "nPerf.AppImage"}
    out = []
    d = Path.home() / ".local/bin"
    if not d.exists():
        return out
    for f in sorted(d.iterdir()):
        n = f.name
        if n.startswith("__") or n.endswith(".bak") or ".BAK" in n:
            continue
        if not (f.is_file() or f.is_symlink()):
            continue
        if n.endswith((".py", ".js", ".sh")) or n.startswith(("esptool", "espefuse",
                                                               "espsecure", "mav", "rns", "rn")):
            src = "local script or project tool"
        elif n in third:
            src = "third-party tool installed to ~/.local/bin"
        else:
            src = "python entry point or local tool"
        out.append({"name": n, "path": str(f), "source": src})
    return out


def python_ecosystem():
    """pip --user, pipx, npm globals: software apt never sees."""
    rows = []
    rc, out, _ = run([sys.executable, "-m", "pip", "list", "--user",
                      "--format=freeze"], timeout=150)
    if rc == 0:
        for line in out.splitlines():
            if "==" in line:
                n, v = line.split("==", 1)
                rows.append({"ecosystem": "pip --user", "name": n, "version": v,
                             "update_source": "PyPI; manual, no upgrade timer"})
    rc, out, _ = run(["pipx", "list", "--short"], timeout=60)
    if rc == 0:
        for line in out.splitlines():
            f = line.split()
            if f:
                rows.append({"ecosystem": "pipx", "name": f[0],
                             "version": f[1] if len(f) > 1 else "",
                             "update_source": "PyPI; pipx upgrade, manual"})
    rc, out, _ = run(["npm", "ls", "-g", "--depth=0"], timeout=90)
    if rc == 0:
        for line in out.splitlines():
            line = line.strip().lstrip("├─└│ ").strip()
            if "@" in line and not line.startswith("npm error"):
                n, _, v = line.rpartition("@")
                if n:
                    rows.append({"ecosystem": "npm -g", "name": n, "version": v,
                                 "update_source": "npm registry; manual"})
    return rows


def snaps():
    rc, out, _ = run(["snap", "list"], timeout=60)
    if rc != 0:
        return []
    rows = []
    for line in out.splitlines()[1:]:
        f = line.split()
        if len(f) >= 4:
            rows.append({"name": f[0], "version": f[1], "rev": f[2],
                         "channel": f[3],
                         "update_source": "snap store; UNATTENDED"})
    return rows


def flatpaks():
    rc, out, _ = run(["flatpak", "list", "--app",
                      "--columns=application,version,branch,origin"], timeout=60)
    if rc != 0:
        return []
    rows = []
    for line in out.splitlines():
        f = line.split("\t")
        if len(f) >= 4:
            rows.append({"app": f[0], "version": f[1], "branch": f[2],
                         "origin": f[3],
                         "update_source": "flathub; manual, no timer installed"})
    return rows


def containers():
    rows = []
    for f in sorted((AO_ROOT / "quadlet").glob("*/*.container")):
        ref = next((l.split("=", 1)[1].strip()
                    for l in f.read_text().splitlines()
                    if l.startswith("Image=")), "")
        rows.append({"unit": f.stem, "domain": f.parent.name, "image": ref,
                     "update_source": "container registry; manual promote"})
    return rows


def collect():
    osr = os_release()
    installed = installed_packages()
    idx = index_files()
    tagged = []
    for name, ver in installed.items():
        meta = idx.get(name)
        if meta:
            _, host, suite, component = meta
            tag = release_tag(host, suite, osr["codename"])
        else:
            host = suite = component = ""
            tag = "Not in any apt index (locally built, or source removed)"
        tagged.append({"package": name, "version": ver, "release": tag,
                       "origin": host, "suite": suite, "component": component,
                       "ubuntu_lts": tag.startswith("Ubuntu")})

    rc, upg, _ = run(["apt", "list", "--upgradable"], timeout=120)
    upgradable = {}
    for line in upg.splitlines():
        m = re.match(r"^([^/]+)/\S+\s+\S+\s+\S+\s+\[upgradable from:\s*([^\]]+)\]",
                     line.strip())
        if m:
            upgradable[m.group(1)] = m.group(2)

    dapps, npkg, ubin, pynpm = (desktop_apps(installed), non_package_apps(),
                                user_binaries(), python_ecosystem())
    sn, fl, ct = snaps(), flatpaks(), containers()
    return {
        "generated": now_utc(), "os": osr,
        "kernel": run(["uname", "-r"])[1].strip(),
        "counts": {
            "apt_packages": len(tagged),
            "ubuntu_lts": sum(1 for t in tagged if t["ubuntu_lts"]),
            "third_party": sum(1 for t in tagged if t["release"].startswith("Third-party")),
            "not_indexed": sum(1 for t in tagged if t["release"].startswith("Not in any")),
            "upgradable": len(upgradable),
            "desktop_apps": len(dapps), "non_package_apps": len(npkg),
            "user_binaries": len(ubin), "python_npm": len(pynpm),
            "snaps": len(sn), "flatpaks": len(fl), "containers": len(ct),
        },
        "apt_packages": tagged, "apt_upgradable": upgradable,
        "desktop_apps": dapps, "non_package_apps": npkg,
        "user_binaries": ubin, "python_npm": pynpm,
        "snaps": sn, "flatpaks": fl, "containers": ct,
    }


def by_release(tagged):
    g = {}
    for t in tagged:
        g.setdefault(t["release"], []).append(t)
    for k in g:
        g[k].sort(key=lambda x: x["package"])
    return dict(sorted(g.items(), key=lambda kv: (not kv[0].startswith("Ubuntu"), kv[0])))


def render(d):
    L = []
    w = L.append
    c, osr = d["counts"], d["os"]

    w("# ALWAYS ON — Exhaustive Software Inventory")
    w("")
    w(f"> Generated `{d['generated']}` by `scripts/build-update/inventory-full.py`.")
    w("> Do not hand-edit; regenerate with:")
    w(">")
    w("> ```bash")
    w("> /ALWAYSON/scripts/build-update/inventory-full.py --markdown \\")
    w(">   --out /ALWAYSON/docs/applications.md")
    w("> ```")
    w("")
    w(f"Host: **{osr['pretty']}** — codename `{osr['codename']}`, version "
      f"`{osr['version_id']}`, kernel `{d['kernel']}`.")
    w("")
    w("Every item is tagged **first** to the Ubuntu LTS release it belongs to, and")
    w("only then to the repository that delivers it. That ordering answers the")
    w("question that matters when deciding what to update: is this part of the")
    w("supported platform, or is it something a third party ships?")
    w("")

    w("## Totals")
    w("")
    w("| Category | Count |")
    w("|---|---|")
    for label, key in [
        ("apt packages installed", "apt_packages"),
        ("— of which Ubuntu 26.04 LTS", "ubuntu_lts"),
        ("— of which third-party repositories", "third_party"),
        ("— of which in no apt index", "not_indexed"),
        ("apt packages behind `Candidate`", "upgradable"),
        ("Desktop applications (`.desktop`)", "desktop_apps"),
        ("Applications with no package manager", "non_package_apps"),
        ("Executables in `~/.local/bin`", "user_binaries"),
        ("pip / pipx / npm-global", "python_npm"),
        ("Snap packages", "snaps"),
        ("Flatpak applications", "flatpaks"),
        ("Quadlet containers", "containers"),
    ]:
        w(f"| {label} | **{c[key]}** |")
    w("")

    w("## APT packages, grouped by release")
    w("")
    w("⚠️ marks a package that has a newer `Candidate` than what is installed.")
    w("")
    for release, items in by_release(d["apt_packages"]).items():
        w(f"### {release} — {len(items)} packages")
        w("")
        if not release.startswith("Ubuntu"):
            w("*(not part of Ubuntu 26.04 LTS — updates are the vendor's decision)*")
            w("")
        w(f"<details><summary>Show all {len(items)}</summary>")
        w("")
        w("| Package | Version | Suite | Component |")
        w("|---|---|---|---|")
        for t in items:
            mark = " ⚠️" if t["package"] in d["apt_upgradable"] else ""
            w(f"| `{t['package']}`{mark} | `{t['version']}` | "
              f"{t['suite'] or '—'} | {t['component'] or '—'} |")
        w("")
        w("</details>")
        w("")

    if d["apt_upgradable"]:
        w("### Behind `Candidate`")
        w("")
        w("| Package | Installed |")
        w("|---|---|")
        for name, old in sorted(d["apt_upgradable"].items()):
            w(f"| `{name}` | `{old}` |")
        w("")

    w("## Desktop applications")
    w("")
    w(f"`{c['desktop_apps']}` entries, enumerated from `/usr/share/applications` and")
    w("`~/.local/share/applications`. A hand-picked list of \"the main ones\" omits")
    w("most of what is installed; this is the exhaustive set.")
    w("")
    w("<details><summary>Show all</summary>")
    w("")
    w("| Application | Desktop id | Provided by |")
    w("|---|---|---|")
    for a in d["desktop_apps"]:
        prov = f"`{a['apt_package']}` `{a['apt_version']}`" if a["apt_package"] else "—"
        w(f"| {a['name']} | `{a['id']}` | {prov} |")
    w("")
    w("</details>")
    w("")

    w("## Applications with no package manager")
    w("")
    w("Invisible to any apt, snap, or flatpak inventory. Several are load-bearing")
    w("for this project. **Nothing here updates itself** — each is a manual")
    w("re-download, and a stale one is invisible until it fails.")
    w("")
    w("| Kind | Name | Path | Update source |")
    w("|---|---|---|---|")
    for a in d["non_package_apps"]:
        w(f"| {a['kind']} | `{a['name']}` | `{a['path']}` | {a['update_source']} |")
    w("")

    w("## Executables in `~/.local/bin`")
    w("")
    w("| Name | Likely source |")
    w("|---|---|")
    for b in d["user_binaries"]:
        w(f"| `{b['name']}` | {b['source']} |")
    w("")

    w("## pip / pipx / npm global")
    w("")
    w("| Ecosystem | Package | Version | Update source |")
    w("|---|---|---|---|")
    for p in d["python_npm"]:
        w(f"| {p['ecosystem']} | `{p['name']}` | `{p['version']}` | {p['update_source']} |")
    w("")

    w("## Snap, Flatpak, and containers")
    w("")
    w("| Package | Version | Channel / branch | Update source |")
    w("|---|---|---|---|")
    for s in d["snaps"]:
        w(f"| snap:`{s['name']}` | `{s['version']}` (rev {s['rev']}) | "
          f"{s['channel']} | {s['update_source']} |")
    for f_ in d["flatpaks"]:
        w(f"| flatpak:`{f_['app']}` | `{f_['version']}` | "
          f"{f_['branch']} ({f_['origin']}) | {f_['update_source']} |")
    for ct in d["containers"]:
        w(f"| container:`{ct['unit']}` | — | {ct['domain']} | {ct['update_source']} |")
    w("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Exhaustive installed-software inventory.")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--json-only", action="store_true")
    args = ap.parse_args()

    d = collect()

    # The complete JSON always goes to the gitignored data path, never next to
    # the markdown: it carries host paths (/home/..., /opt/...) and is a
    # megabyte of machine-readable detail that does not belong in a public repo.
    js = AO_ROOT / "data/build-update/inventory-full.json"
    js.parent.mkdir(parents=True, exist_ok=True)
    t = js.with_suffix(js.suffix + ".tmp")
    t.write_text(json.dumps(d, indent=1, sort_keys=True), encoding="utf-8")
    t.replace(js)
    print(f"wrote {js}")

    if args.json_only:
        c = d["counts"]
        print(f"  apt {c['apt_packages']} (Ubuntu LTS {c['ubuntu_lts']}, "
              f"third-party {c['third_party']}, unindexed {c['not_indexed']})")
        return 0

    if args.markdown and args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        t = p.with_suffix(p.suffix + ".tmp")
        t.write_text(render(d), encoding="utf-8")
        t.replace(p)
        print(f"wrote {p}")
    else:
        print(render(d))

    c = d["counts"]
    print(f"  apt {c['apt_packages']} (Ubuntu LTS {c['ubuntu_lts']}, "
          f"third-party {c['third_party']}, unindexed {c['not_indexed']})")
    print(f"  desktop apps {c['desktop_apps']}, non-package "
          f"{c['non_package_apps']}, ~/.local/bin {c['user_binaries']}, "
          f"py/npm {c['python_npm']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
