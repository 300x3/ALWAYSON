#!/usr/bin/env python3
"""ALWAYS ON ao-build-update: controlled software-update acquisition.

Implements the README 5.2.1 role of the ao-build-update adapter: acquire
candidate images and packages from allowlisted upstream sources, capture their
digests, and write an update audit record.

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
It does not install, promote, restart, or deploy anything. It does not run apt,
dpkg, or unattended-upgrades. It does not edit a Quadlet file. It does not touch
a workload network or container. Promotion is a human action; this produces the
verified set a human decides from (README 5.2.1, 4.1 rule 9).

Modes
-----
  --plan    Resolve and report only. Makes no network call and writes only the
            audit record. This is the default, and the safe one.
  --fetch   Additionally resolve the current digest of each candidate from the
            local Podman store. Read-only: no layer pull, no install.

Exit codes: 0 ok, 2 usage, 3 config error, 4 allowlist violation.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

AO_ROOT = Path(os.environ.get("AO_ROOT", "/ALWAYSON"))
# AO_BUILD_UPDATE_ALLOWLIST exists because the two roots do not agree on the
# config path. On the host the allowlist is
#   /ALWAYSON/config/build-update/registry-allowlist.yaml
# but the Quadlet mounts that config directory directly at
#   /opt/ao-build-update/config
# so inside the container the same file is at
#   /opt/ao-build-update/config/registry-allowlist.yaml
# Re-rooting AO_ROOT is therefore not enough on its own, and guessing a
# "config/build-update/" subdirectory that does not exist in the container is
# what produced exit code 3 in the first run. The unit sets this explicitly.
ALLOWLIST = Path(os.environ.get(
    "AO_BUILD_UPDATE_ALLOWLIST",
    AO_ROOT / "config/build-update/registry-allowlist.yaml"))
SUPPORTED_SCHEMA = 1

# Inside the Quadlet the project is not mounted at its host path. The container
# gets the allowlist at /opt/ao-build-update/config and the two writable
# directories at /var/lib/ao-build-update and /var/log/ao-build-update, so the
# same script has to work from either root. AO_ROOT is the single switch: the
# unit sets it, and the allowlist's staging_dir/audit_log are resolved through
# the same override so a host run and a container run agree on where evidence
# lands. The mount points themselves are in ao-build-update.container; if they
# are ever changed, change them there too.


def _resolve(path_str: str, root: Path) -> Path:
    """Resolve a configured absolute path against the active root.

    A path under /ALWAYSON is re-rooted; anything else is used verbatim, so an
    allowlist may still point at a genuinely external location.
    """
    p = Path(path_str)
    if p.is_absolute() and str(p).startswith("/ALWAYSON"):
        return root / p.relative_to("/ALWAYSON")
    return p


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def die(code: int, msg: str):
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def parse_allowlist(path: Path) -> dict:
    """Parse the allowlist.

    Deliberately a small hand parser rather than a PyYAML dependency: this runs
    in a minimal image and the file shape is fixed by schema_version. It errors
    loudly rather than guessing when the shape is unfamiliar.
    """
    if not path.exists():
        die(3, f"allowlist not found: {path}")

    registry_hosts: set = set()
    package_hosts: set = set()
    denied: set = set()
    section = None
    staging = None
    audit = None
    schema = None

    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        s = line.strip()

        if s.startswith("schema_version:"):
            schema = s.split(":", 1)[1].strip()
        elif s.startswith("registries:"):
            section = "registries"
        elif s.startswith("package_sources:"):
            section = "packages"
        elif s.startswith("denied:"):
            section = "denied"
        elif s.startswith("staging_dir:"):
            staging = s.split(":", 1)[1].strip()
        elif s.startswith("audit_log:"):
            audit = s.split(":", 1)[1].strip()
        elif s.startswith("- host:"):
            host = s.split(":", 1)[1].strip().strip("\"'")
            if section == "registries":
                registry_hosts.add(host)
            elif section == "packages":
                package_hosts.add(host)
            elif section == "denied":
                denied.add(host)
            else:
                die(3, f"host entry outside a known section: {s!r}")

    if schema is None:
        die(3, "allowlist has no schema_version")
    if schema != str(SUPPORTED_SCHEMA):
        die(3, f"unsupported allowlist schema_version {schema!r} "
               f"(this adapter understands {SUPPORTED_SCHEMA})")
    if not registry_hosts:
        die(3, "allowlist permits no container registry; acquisition would be a no-op")
    if not staging or not audit:
        die(3, "allowlist must set staging_dir and audit_log")

    # Evidence paths get their own overrides for the same reason as the
    # allowlist: AO_ROOT re-rooting alone would aim at
    # /opt/ao-build-update/data/... and /opt/ao-build-update/logs/..., but the
    # writable mounts are /var/lib/ao-build-update and /var/log/ao-build-update.
    staging = os.environ.get("AO_BUILD_UPDATE_STAGING") or str(_resolve(staging, AO_ROOT))
    audit = os.environ.get("AO_BUILD_UPDATE_AUDIT_LOG") or str(_resolve(audit, AO_ROOT))

    return {
        "registries": registry_hosts,
        "package_sources": package_hosts,
        "denied": denied,
        "staging_dir": staging,
        "audit_log": audit,
    }


def classify(ref: str):
    """Return (host, remainder) for a fully qualified image reference."""
    if "@" in ref or "/" in ref.split(":")[0]:
        host, _, rest = ref.partition("/")
        return host, rest
    die(2, f"image reference is not fully qualified: {ref!r} "
           f"(README 4.1 rule 9 requires a registry host and a digest)")


def check_allowed(ref: str, allow: dict) -> str:
    """Enforce the allowlist and the digest requirement. Returns a verdict."""
    host, _ = classify(ref)
    if host in allow["denied"]:
        return f"DENIED: {host} is on the adapter deny list"
    if host not in allow["registries"]:
        return f"NOT-ALLOWLISTED: {host} is not a permitted container registry"
    if "@sha256:" not in ref:
        return f"UNPINNED: {host} is allowed but the reference carries no sha256 digest"
    return "ALLOWED-PINNED"


def resolve_digest(ref: str) -> dict:
    """Resolve a reference to a manifest digest from the local Podman store.

    Read-only. No layer pull, no container created. A failure here is recorded
    as unresolved, never as a pass.
    """
    proc = subprocess.run(
        ["podman", "image", "inspect", ref, "--format", "{{.Digest}}"],
        capture_output=True, text=True, timeout=120, check=False,
    )
    digest = proc.stdout.strip()
    return {
        "reference": ref,
        "resolved_digest": digest or None,
        "resolved": bool(digest),
        "detail": None if digest else (proc.stderr.strip() or "not present locally"),
    }


def write_audit(allow: dict, run: dict) -> Path:
    """Append the run record to the update audit log."""
    log = Path(allow["audit_log"])
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(run, sort_keys=True) + "\n")
    try:
        os.chmod(log, 0o644)
    except OSError:
        pass
    return log


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Controlled software-update acquisition for ALWAYS ON. "
                    "Never installs, promotes, or deploys.")
    ap.add_argument("reference", nargs="*",
                    help="fully qualified image reference, digest-pinned")
    ap.add_argument("--plan", action="store_true",
                    help="resolve nothing; report the allowlist boundary only (default)")
    ap.add_argument("--fetch", action="store_true",
                    help="resolve each allowlisted reference to its current digest")
    args = ap.parse_args()

    allow = parse_allowlist(ALLOWLIST)
    mode = "fetch" if args.fetch else "plan"
    started = now_utc()

    run = {
        "timestamp": started,
        "component": "ao-build-update",
        "mode": mode,
        "operator": os.environ.get("SUDO_USER") or os.environ.get("USER") or "unknown",
        "promoted": False,
        "installed": False,
        "note": "acquisition and digest capture only; promotion is a separate "
                "operator action (README 5.2.1)",
        "results": [],
    }

    if not args.reference:
        run["results"].append({
            "reference": None,
            "verdict": "NO-REFERENCES",
            "detail": f"no reference supplied; allowlist permits "
                      f"{sorted(allow['registries'])}",
        })
    else:
        for ref in args.reference:
            verdict = check_allowed(ref, allow)
            entry = {"reference": ref, "verdict": verdict}
            if verdict != "ALLOWED-PINNED":
                entry["resolved_digest"] = None
                entry["detail"] = "no resolution attempted"
            elif args.fetch:
                entry.update(resolve_digest(ref))
            else:
                entry["resolved_digest"] = None
                entry["detail"] = "not resolved (--plan); use --fetch to resolve"
            run["results"].append(entry)

    log = write_audit(allow, run)

    staging = Path(allow["staging_dir"])
    staging.mkdir(parents=True, exist_ok=True)
    stamp = started.replace(":", "").replace("-", "")
    # Runs can land inside the same second, and a report is evidence: a later run
    # must not silently overwrite an earlier one. If the name is taken, suffix it.
    report = staging / f"acquisition-{stamp}.json"
    n = 1
    while report.exists():
        n += 1
        report = staging / f"acquisition-{stamp}-{n}.json"
    report.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"mode:        {mode}")
    print("promoted:    no (by design)")
    print("installed:   no (by design)")
    print(f"audit:       {log}")
    print(f"report:      {report}")
    for entry in run["results"]:
        line = f"  {entry.get('reference') or '(none)'}: {entry['verdict']}"
        if entry.get("resolved_digest"):
            line += f" -> {entry['resolved_digest']}"
        print(line)

    breached = [r for r in run["results"]
                if r["verdict"].startswith(("DENIED", "NOT-ALLOWLISTED", "UNPINNED"))]
    if breached:
        print("allowlist boundary enforced; see the audit record", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
