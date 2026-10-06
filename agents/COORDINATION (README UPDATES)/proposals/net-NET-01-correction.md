---
item: NET-01
action: update
evidence: |
  CORRECTION TO MY OWN EARLIER CLAIM. net-NET-01.md says, and §5.2.1 said
  until this commit, "Nothing at runtime reads registry-allowlist.yaml".
  That is FALSE. The allowlist IS read at runtime and it DOES refuse
  disallowed references. Measured 2026-10-04:

  $ grep -n 'ALLOWLIST' scripts/build-update/ao-build-update.py
  41:ALLOWLIST = Path(os.environ.get(
  42:    "AO_BUILD_UPDATE_ALLOWLIST",
  43:    AO_ROOT / "config/build-update/registry-allowlist.yaml"))
  85:        die(3, f"allowlist not found: {path}")
  165:    return f"DENIED: {host} is on the adapter deny list"
  281:        return 4

  Proven by execution, not by reading. Three cases, one control:

  $ python3 scripts/build-update/ao-build-update.py localhost/foo:latest
  allowlist boundary enforced; see the audit record
    localhost/foo:latest: DENIED: localhost is on the adapter deny list
  EXIT=4

  $ python3 scripts/build-update/ao-build-update.py docker.io/library/nginx:latest
  allowlist boundary enforced; see the audit record
    docker.io/library/nginx:latest: UNPINNED: docker.io is allowed but the
    reference carries no sha256 digest
  EXIT=4

  $ python3 scripts/build-update/ao-build-update.py \
      'docker.io/library/nginx@sha256:0000000000000000000000000000000000000000000000000000000000000000'
    docker.io/library/nginx@sha256:0000...0000: ALLOWED-PINNED
  EXIT=0

  Allowlist contents are real policy, not a stub:
  $ python3 -c "import yaml;d=yaml.safe_load(open('config/build-update/registry-allowlist.yaml'));print(d['registries'],d['denied'])"
  registries: docker.io, ghcr.io, quay.io
  denied: packages.ros.org (TLS verification failure from this host; not
    disabled by decision), localhost, 127.0.0.1

  Each run appends to the append-only audit log and writes a staging report;
  mode is plan and promoted/installed are false, so nothing was fetched,
  installed or promoted. Confirmed in the audit tail:
  "mode": "plan", "installed": false, "promoted": false

  WHAT I GOT WRONG, AND WHY. I wrote "nothing reads them at runtime" after
  grepping only for the *filename* string across scripts/ and quadlet/, not for
  the *concept*. The consumer loads the path through an env-var default
  (AO_BUILD_UPDATE_ALLOWLIST), so the literal string
  "registry-allowlist.yaml" still appears at line 43 but my earlier grep
  pattern was too narrow to surface the enforcement logic, and I read the
  absence of a grep hit as absence of a control. I had also already read
  lines 5 and 22 of this same file, which describe exit code 4 as
  "allowlist violation" - and did not reconcile that with my own conclusion.
  Lesson: grep the mechanism, not just the name, and never let a conclusion
  contradict a docstring I have already read.

  THE CORRECT PICTURE, which is narrower and not reassuring enough to close
  NET-01. There are two distinct controls and I had collapsed them:
    - CODE ENFORCEMENT - real and verified. The script refuses to plan
      anything not on the list, and refuses unpinned references.
    - SEGMENT ENFORCEMENT - absent. ao-build-update is an ordinary
      Internal=false bridge. Any OTHER container attached to that network
      bypasses the allowlist entirely and can reach the whole internet.
  So the allowlist is a refusal to PLAN, not a refusal to ROUTE. §5.2.1 now
  says exactly that, with the three commands and their real exit codes.

  NET-01 REMAINS OPEN. The blockers in net-NET-01.md are unchanged and were
  not overstated by this correction: segment-level enforcement still needs
  firewall/proxy policy (Rule 6, §4.1 rule 13) and the adapter still needs
  its own separate credentials (a secret - explicit stop condition). Neither
  is mine to author.

  Side effect to be aware of: running these three tests appended three
  records to /ALWAYSON/logs/operations/build-update-audit.log and wrote three
  staging reports under data/build-update/staging/. They are audit records of a
  real verification, so I am leaving them rather than deleting anything. No
  secret value is in them - only public hostnames and references.
section: 05-network-domains-and-controlled-external-access
---
**NET-01 stays open; this corrects the evidence, not the status.** I had
recorded the destination allowlist as unenforced. It is enforced in code -
verified above by execution, three cases, exit 4/4/0. The gap is narrower
than I wrote: the script is a genuine control, not documentation of intent.

§5.2.1's blockquote now distinguishes the two controls instead of conflating
them. The allowlist governs *this script*; it does not govern the segment.
`Internal=false` means anything else attached to `ao-build-update` reaches the
internet without consulting the list at all. So "the only sanctioned outbound"
in **Containment** is still a requirement the adapter must satisfy rather than
a property the network has, and the standing instruction not to attach a
container to this network still stands.

The two stop conditions are unchanged and still operator decisions: a
firewall/proxy design for segment-level enforcement, and separate adapter
credentials. I did not author either, did not touch firewall policy, and did
not create a credential.