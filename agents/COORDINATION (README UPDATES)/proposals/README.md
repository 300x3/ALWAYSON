# Proposals — how sessions record §19 changes without colliding

Every group session writes one file here per item it closes. **Sessions never edit
`README-ACTION_ITEMS/status-and-references.md` directly** — all eleven need to record
progress in §19, which makes it the single file where concurrent sessions collide. The
twelfth (compiler) session merges these into §19.2.

Filename: `<group>-<ITEM-ID>.md`, e.g. `ops-a-OPS-11.md`.

```markdown
---
item: OPS-11
action: close
evidence: |
  $ systemctl --user is-enabled ao-backup.timer
  enabled
section: 17-backup-restore-monitoring-and-completion-criteria
---
What changed in your own section file, in prose.
```

`action` is `close`, `update` (progress on a still-open item) or `new` (a genuinely new
item — take the next free number **in your own group** only).
