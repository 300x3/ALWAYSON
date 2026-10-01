# AGENTS.md — ALWAYS ON project rules

Rules for Cline (and any other agent) working on the ALWAYS ON project.
`/ALWAYSON` is the project home. A copy of the mandatory working-directory rule
is also installed globally (`~/.cline/rules/00-alwayson-home.md`,
`~/.agents/AGENTS.md`, `~/Documents/Cline/Rules/`), so it is known before any
chat starts — this file is the project-level authority.

## Working directory

- Work from **`/ALWAYSON`**. Use absolute paths (`/ALWAYSON/...`) for all reads,
  writes, searches, and commands.
- `/ALWAYSON` is the live, authoritative copy. Legacy material lives under
  `/ALWAYSON/backups/` — `gitcli/ALWAYSON-push` (old git clone) and
  `gitcli/ALWAYSON-staging` (old install staging) are archived reference
  only; never edit them or run anything from them.

## Document authority

- `/ALWAYSON/README.md` is the single authoritative document: architecture,
  implemented configuration, operational requirements, validation evidence,
  approved deviations, known issues, and work queue.
- When implementation differs from an architecture requirement, the difference
  must be recorded in the README's *Approved Deviations and Open Decisions*
  section — never silently diverge.
- Never guess paths or status. Read, then cite what you read. If retrieval or
  evidence is weak, say so instead of inventing details.

## Non-negotiable rules (README §4.1 — mirrored; the README is authoritative)

1. Inspect before changing.
2. Preserve existing data.
3. Never format, repartition, delete, prune, or overwrite without explicit
   operator approval.
4. Never install Docker daemon, Docker Compose, or Watchtower.
5. Use Podman and Quadlet only.
6. Never expose a public port without explicit operator approval.
7. Never place secrets in scripts, logs, HTML, Git, pCloud Public Folder, IPFS,
   Corda payloads, shell history, or documentation examples.
8. Never use `--privileged` as a default.
9. Use pinned image digests for operational services.
10. Verify the photogrammetry drive before deploying or operating WebODM.
11. Record commands, versions, significant output, and failures in the
    installation or operational journal.
12. Stop and report conflicts involving services, packages, networks, mounts,
    ports, serial devices, firewall policy, or existing data.
13. Do not broaden network access, database privileges, filesystem access,
    container privileges, or secret access merely to bypass an error.
14. Require explicit human approval before publishing external communications,
    initiating payments, changing production credentials, deleting data, or
    modifying external records.

## Layout

| Path | Purpose |
|---|---|
| `/ALWAYSON/README.md` | Authoritative project document |
| `/ALWAYSON/config/` | Configuration and service definitions (Podman Quadlet inputs, network CIDRs, radio profiles) |
| `/ALWAYSON/quadlet/` | systemd Quadlet unit definitions — the only supported container lifecycle |
| `/ALWAYSON/scripts/` | Install, validation, operations, and journal scripts |
| `/ALWAYSON/docs/` | Supporting documentation |
| `/ALWAYSON/data/` | Persistent service data (PostgreSQL, Redis, etc.) |
| `/ALWAYSON/logs/` | Operational logs |
| `/ALWAYSON/artifacts/` | Generated artifacts and signed manifests |
| `/ALWAYSON/backups/` | Backup and restore material |
| `/ALWAYSON/secrets/` | Secret-classified material — never echo, log, or commit |
| `/ALWAYSON/forms/` | Project forms |

## Conventions

- Container runtime is Podman only; containers are managed through systemd
  Quadlet definitions — never Docker Compose or shell-wrapper orchestration.
- All workload networks are `Internal=true`; CIDRs live in
  `/ALWAYSON/config/platform/network-cidrs.yaml`.
- Follow the existing Git commit style: `type(scope): summary`
  (e.g. `security(postgresql): ...`, `docs: ...`). Commit only when the user
  asks; leave unrelated pre-existing working-tree changes alone.
- Record significant commands, versions, output, and failures in the
  operational journal as you go (README §4.1 rule 11).
- Data classification and handling rules are in README §4.2; prohibited
  cross-domain paths are in README §4.3. Check them before moving any data.
