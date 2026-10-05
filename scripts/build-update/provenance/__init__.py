"""ao-build-update provenance log, split by concern (OPS-18).

The generator used to be one ~2,300-line module holding collection, policy,
plan generation and rendering together. Repeated edits to that file produced
malformed edits that only surfaced at compile time, so the seams are now real
module boundaries:

    common      constants, subprocess, timestamps, normalisation
    collector   evidence gathering - the only module with mutable caches
    policy      what an updater may do, and the recorded reason for each
    plan        machine-readable update plans (eligible / excluded)
    render      rows to Markdown and HTML; no policy, no network

Dependency direction is strictly one way:

    plan    -> policy, render, common
    render  -> collector, policy, common
    collector -> common
    policy  -> stdlib only

`provenance-log.py` remains the executable entrypoint and re-exports every
public name, so `test_generators.py` and any existing caller keep working.

A NOTE ON UNDERSCORE NAMES. `from .collector import *` does NOT import
`_load_apt_history`, `_argv_is_safe` or any other underscore-prefixed name, and
two regression tests reach exactly those. The re-export below therefore walks
each submodule's namespace and binds EVERY top-level name, leading underscore
included. `__all__` is built from the same walk for the same reason: a plain
`import *` at the entrypoint would otherwise silently drop them again.
"""
from __future__ import annotations

from . import common, policy, collector, render, plan
from .common import (AO_ROOT, ARCHIVE_PAGES, INVENTORY, TIMEOUT, UNMANAGED,
                     is_complete_digest, load_yaml, norm, now_utc, run)
from .policy import (EXCLUSIONS, NEEDS_APPROVAL, PIN_POLICY, PLAN_VERBS,
                     _argv_is_safe, pin_policy, update_risk)
from .render import (CSS, HEADERS, NOT_A_VALUE, UNKNOWN, match_of,
                     rollup_details_md, rows_to_html, to_html)
from .plan import update_steps, write_update_plan
from .collector import cache_ttl, set_cache_ttl

_SUBMODULES = (common, policy, collector, render, plan)

# Bind every top-level name of every submodule, in dependency order, so the
# owning module wins. `render` imports names FROM `collector`, so walking
# collector first keeps the definitions rather than the aliases.
#
# MUTABLE STATE IS THE CAVEAT, and it is why `cache_ttl()` / `set_cache_ttl()`
# and `set_offline()` exist instead of a bare `OFFLINE` / `CACHE_TTL` global.
# These bindings are SNAPSHOTS taken at import time. If the owning module later
# REBINDS its own name with a `global` statement, this copy silently keeps the
# old value -- a copy that is not a module and must not be treated as one.
# Measured: after `_load_apt_history()` cached the module in `collector`,
# `provenance._APT_HISTORY_MODULE` still read 'unset'. Any state that crosses a
# module boundary therefore goes through an accessor owned by the writer.
for _mod in _SUBMODULES:
    for _name in dir(_mod):
        if not _name.startswith("__"):
            globals().setdefault(_name, getattr(_mod, _name))

# Deleted BEFORE __all__ is built, not merely underscore-prefixed: pytest
# imports this package while collecting scripts/ and treats a leftover
# attribute as something to resolve. Building __all__ first would publish these
# three names into the entrypoint's `from provenance import *`, and the star
# import would then fail looking for them.
del _mod, _name, _SUBMODULES

# Everything except dunders, underscore names INCLUDED - see the note above.
__all__ = [_n for _n in dir() if not _n.startswith("__")]
