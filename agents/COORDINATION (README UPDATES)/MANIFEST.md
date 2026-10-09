# Section manifest

Order is fixed. The compiler concatenates these in this order to produce `README.md`.

| Folder | Section heading |
|---|---|
| `00-frontmatter` | Document front matter |
| `es-executive-summary` | Executive Summary |
| `01-system-purpose` | 1. System Purpose |
| `02-platform-baseline` | 2. Platform Baseline |
| `03-high-level-architecture` | 3. High-Level Architecture |
| `04-security-isolation-and-data-policy` | 4. Security, Isolation, and Data Policy |
| `05-network-domains-and-controlled-external-access` | 5. Network Domains and Controlled External Access |
| `06-component-boundaries-gui-reporting-tools-and-operator-access` | 6. Component Boundaries, GUI Reporting Tools, and Operator Access |
| `07-public-storefront-and-payment-policy` | 7. Public Storefront and Payment Policy |
| `08-mapping-and-photogrammetry` | 8. Mapping and Photogrammetry |
| `09-field-and-lora-architecture` | 9. Field and LoRa Architecture |
| `10-simulation-architecture` | 10. Simulation Architecture |
| `11-ledger-provenance-archive-and-ipfs` | 11. Ledger, Provenance, Archive, and IPFS |
| `12-host-installation-and-configuration` | 12. Host Installation and Configuration |
| `13-podman-runtime-and-quadlet-policy` | 13. Podman Runtime and Quadlet Policy |
| `14-secrets-and-service-identity` | 14. Secrets and Service Identity |
| `15-sales-mastodon-openclaw-and-local-ai` | 15. Sales, Mastodon, OpenClaw, and Local AI |
| `16-scripts-and-operational-standards` | 16. Scripts and Operational Standards |
| `17-backup-restore-monitoring-and-completion-criteria` | 17. Backup, Restore, Monitoring, and Completion Criteria |

<!-- RETIRED 2026-10-09: `19-current-status-and-outstanding-work` and
     `20-status-references` were split out of the README into
     `README-ACTION_ITEMS/status-and-references.md` (doc_id PROJECT-STATUS,
     authoritative). Do NOT re-add rows for them here and do NOT rebuild them
     into README.md. compile.py concatenates only the rows above. -->
