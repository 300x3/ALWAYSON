"""What an automated updater is allowed to do, and why.

Every constant here is a decision RECORDED for this host, not a value inferred
from the data. `EXCLUSIONS` and `NEEDS_APPROVAL` are the operator constraints
from the project rules; `PIN_POLICY` distinguishes a deliberate hold from an
accident. This module is deliberately dependency-free so the allowlist can be
read and audited on its own, with no import graph to follow.
"""
from __future__ import annotations

import os



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
