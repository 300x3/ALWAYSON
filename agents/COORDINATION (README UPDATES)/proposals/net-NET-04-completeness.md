---
item: NET-04
action: update
evidence: |
  NET-04 does NOT close. The recovered list is verbatim-correct but incomplete for
  the system as it now stands, and I found that by checking the running host rather
  than the archive. Two gaps, both new, neither a transcription error.

  GAP 1 - §4.3.2 row 2 forbids what the architecture deliberately does.

    $ grep -n 'Any workload network to the public internet' \
        agents/COORDINATION (README UPDATES) (README UPDATES)/04-security-isolation-and-data-policy/section.md
    87:| Any workload network to the public internet | ... | Rules 6, §5.2 |

    $ podman network ls --format '{{.Name}} {{.Internal}}' | grep ao- | grep false
    ao-build-update false
    ao-reporting-egress false
    ao-sales false

    $ for n in ao-sales ao-reporting-egress; do
        printf '%s: ' "$n"
        podman network inspect "$n" --format '{{range .Containers}}{{.Name}} {{end}}'
      done
    ao-sales: mastodon-redis ao-sales-db mastodon-web mastodon-streaming mastodon-db mastodon-sidekiq
    ao-reporting-egress: ao-grafana ao-metabase

    ao-sales is a WORKLOAD network - §5.1 group A lists it, and group A's own header
    reads "every row is an Internal=true Podman network EXCEPT ao-sales". So row 2
    prohibits by name the arrangement §5.1 declares and the host runs. Unsatisfiable
    without breaking the platform.

    The recovered §4.3.1 has NO such row. It says the narrower true thing:
    "Public internet -> PostgreSQL, Redis, WebODM workers, ..." which is INBOUND.
    Row 2 is an artefact of the rebuild, not of the v6 original.

    I marked the stale wording superseded IN PLACE and restated the outbound
    restriction that is intended and held. I did not delete the row - §4.3.1 itself
    warns that deleting a prohibition hides the decision.

  GAP 2 - the live public ingress path is named by no prohibition at all.

    $ grep -n -i 'cloudflare' \
        agents/COORDINATION (README UPDATES) (README UPDATES)/04-security-isolation-and-data-policy/section.md
    (no output before §4.3.4)

    $ systemctl --user is-active cloudflared-alwayson.service
    active

    $ grep -n 'hostname\|service:' ~/.cloudflared/config.yml
      - hostname: chat.300x3.com
        service: http://127.0.0.1:18790
      - hostname: chat.300x3.com
        service: http://127.0.0.1:18789
      - hostname: mastodon.300x3.com
        service: http://127.0.0.1:3000
      - service: http_status:404

    A RUNNING internet ingress path with three hostname rules into loopback origins
    in ao-sales. It is the mechanism by which the public internet reaches a workload
    domain - the exact subject of §4.3.2 row 2 - and the prohibition list names
    neither the tunnel, nor its credential, nor its rule.

    PROPOSED, NOT APPLIED. Adding a row means deciding which rule governs an external
    ingress mechanism. That is the operator's, not mine.

  Cross-check, because a claim of incompleteness must not rest on my own reading:

    $ V6='README - ARCHIVE/ALWAYS ON — Architecture, Operations, and Status - v6.md'
    $ for n in ao-sales ao-reporting-egress ao-build-update ao-html-window \
               ao-fabrication ao-payment; do
        printf '%-22s v6:%s now:%s\n' "$n" \
          "$(grep -c "$n" "$V6")" \
          "$(grep -c "$n" config/platform/network-cidrs.yaml)"
      done
    ao-sales               v6:12  now:1
    ao-reporting-egress    v6:0   now:1
    ao-build-update        v6:3   now:1
    ao-html-window         v6:0   now:1
    ao-fabrication         v6:0   now:1
    ao-payment             v6:8   now:1

    Three networks in the live registry appear NOWHERE in v6, so no v6-derived list
    could name them. This is coverage drift measured, not assumed.

  Neither gap shows the recovered text was mis-transcribed. Both are a 2026-06 list
  meeting a 2026-10 architecture, the expected direction of drift.

    $ python3 agents/COORDINATION (README UPDATES) (README UPDATES)/tools/compile.py --check
    identical
section: 04-security-isolation-and-data-policy
---
**NET-04's acceptance criterion was "confirm it is complete and correct". I cannot
confirm complete, and I can now say precisely why — which is more than the previous
pass could.**

The previous pass recovered the v6 text verbatim and correctly reasoned that
recovery is not approval. What it did not do was ask whether a list written before
`ao-fabrication`, `ao-reporting-egress` and the Cloudflare Tunnel existed still
covers them. It does not, in two places, and both gaps were found by measuring the
host rather than by re-reading the archive.

The more serious is gap 1, and it is a defect **in the rebuilt §4.3.2 table, not in
the recovered §4.3.1**. Row 2 read "Any workload network to the public internet"
with no exception. `ao-sales` and `ao-reporting-egress` are workload networks, are
deliberately `Internal=false`, carry eight live containers between them, and are
declared non-internal by §5.1 group A's own header. The row prohibited the
architecture. I have marked it superseded in place and restated it as the outbound
restriction that is intended and actually held — a workload service reaches the
internet only through a controlled adapter, never directly. I did not delete the
row, because §4.3.1's own reasoning applies to it: deleting a prohibition hides
the decision that deleted it.

Gap 2 is a coverage gap in **both** lists. The Cloudflare Tunnel is the live
public ingress path into `ao-sales`, it is `active`, and no prohibition names it.
Which rule governs an external ingress mechanism is an operator decision, so I
proposed the row rather than writing it.

I also added **§5.2.3** to the network section, because the question "which
prohibition covers a non-internal workload network" is unanswerable from §4.3
alone. It now records that the three `Internal=false` networks are **not three
instances of one thing** — `ao-sales` is group A (workload), `ao-reporting-egress`
is group C (component boundary), `ao-build-update` is group B (adapter) — and that
for the first two, containment rests on the one-network-per-component convention
rather than on a control. **No network was created, removed, re-CIDRed or
re-flagged; the registry is byte-identical**, verified by
`git --no-pager diff --stat config/ scripts/ quadlet/` returning empty.

**What I got wrong.** My first action was to re-run
`check-network-isolation.sh` — which I already knew would pass — and to re-read
§4.3.1 against the archive to confirm the transcription. That is verification of
the thing verified three times already. The productive question was coverage, not
fidelity, and two greps against the running host answered it. The reason: I
inherited the framing "the recovered list is the deliverable" and treated NET-04 as
a transcription audit. NET-04 says *complete and correct*, and completeness is a
claim about the present, which an archive cannot settle.

**Process note, recorded because it nearly caused a real violation.** My first
attempt at these two proposals used the filenames `net-NET-01.md` and
`net-NET-04.md`, which were already committed and already listed in `.applied` —
they were merged into §19.2 by the compiler. I overwrote both. I caught it with
`git status`, restored them with `git checkout --`, and rewrote under the
`-recheck` / `-completeness` suffixes already used by earlier NET passes. No
previously-applied proposal was lost, and the lesson is recorded because the
temptation is structural: the brief's template literally says
`proposals/net-<ITEM-ID>.md`, and for items that have already been proposed once
that filename is a loaded gun.
