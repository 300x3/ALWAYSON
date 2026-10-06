"""Shared constants and the three primitives everything else needs:
subprocess execution, UTC timestamps and value normalisation. Nothing here has
any knowledge of provenance, policy or rendering.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path




AO_ROOT = Path(os.environ.get("AO_ROOT", "/ALWAYSON"))


AO_ROOT = Path(os.environ.get("AO_ROOT", "/ALWAYSON"))
INVENTORY = AO_ROOT / "data/build-update/inventory-full.json"


INVENTORY = AO_ROOT / "data/build-update/inventory-full.json"
UNMANAGED = AO_ROOT / "config/build-update/unmanaged-software.yaml"


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
