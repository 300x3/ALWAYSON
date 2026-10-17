# 8. Mapping and Photogrammetry

## 8.1 Dedicated Storage

The dedicated local workspace for WebODM and photogrammetry is:

```text
/media/scottw/500GBPHOTOGRAM/
```

This drive is authoritative for:

- Incoming drone imagery.
- Validated imagery sets.
- Rejected and quarantined uploads.
- WebODM media and project data.
- NodeODM intermediates.
- Mapping deliverables.
- Mapping processing and provenance manifests.
- pCloud/IPFS archive staging.
- Mapping-database backup exports.

WebODM must not use the root filesystem, `$HOME`, or Podman writable container
layers for high-volume processing.

## 8.2 Required Directory Tree

The tree below is the specification. Compliance on the live drive is tracked in
§19.1 FIELD-10.

```text
/media/scottw/500GBPHOTOGRAM/
├── README.md
├── .mounted-ok
├── incoming/
│   ├── drone/
│   ├── operator/
│   └── quarantine/
├── validated/
│   └── <mission-id>/
├── rejected/
│   └── <mission-id-or-date>/
├── webodm/
│   ├── media/
│   ├── projects/
│   ├── nodeodm/
│   ├── temp/
│   └── logs/
├── deliverables/
│   └── <mission-id>/
│       ├── orthophoto/
│       ├── point-cloud/
│       ├── dem-dsm/
│       ├── textured-model/
│       ├── reports/
│       └── manifest/
├── manifests/
│   ├── intake/
│   ├── processing/
│   └── ledger-submissions/
├── exports/
│   ├── pcloud-staging/
│   └── ipfs-staging/
├── backups/
│   └── mapping-db/
├── retention/
│   ├── pending-review/
│   └── eligible-for-archive/
└── tmp/
    └── processing/
```

No directory in this tree may be world-writable. Use dedicated mapping
ownership, explicit groups, and ACLs only when necessary.

## 8.3 Mapping Processing Flow

```text
Authenticated drone or operator upload
      │
      ▼
Telemetry data ingest to imagery-ingest service, from 3DR N1 (autopilot module)
Imagery-ingest service from Raspberry Pi camera and sensor (companion computer)
      ├── File type validation
      ├── SHA-256 checksum
      ├── EXIF and metadata validation
      ├─── Mission association (autopilot telemetry incorporated
      │   and the WebODM project name)
      ├── Storage quota check
      ├── File-count validation
      └── Quarantine on failure
              │
              ▼
WebODM API and project task creation
              │
              ▼
Queue / Redis
              │
              ▼
NodeODM processing worker
      ├── Orthomosaic
      ├── Point cloud
      ├── DSM / DEM
      ├── Textured model
      └── Processing report
              │
              ▼
Mapping-result exporter
      ├── Hashes outputs
      ├── Generates signed manifest
      ├── Stages approved archive bundle
      └── Submits signed manifest to ledger ingestion
```

## 8.4 Persistent Locations

The directory tree in §8.2 fixes the layout of imagery, projects, deliverables and manifests.
These are the locations the tree does not show.

| Data | Location |
|---|---|
| Mapping PostgreSQL | `~/webodm/dbdata`, bind-mounted on `ao-webodm-db` |
| Redis persistence | A named Podman volume on `ao-webodm-broker` |
| Signed manifests | `/ALWAYSON/artifacts/mapping-manifests/` |` |

## 8.4.1 Authoritative mapping database name and location

The single authoritative mapping database is **`webodm_dev`** in container `ao-webodm-db`,
with physical data at `~/webodm/dbdata` (`/home/scottw/webodm/dbdata`, bind-mounted at
`/var/lib/postgresql/data`), and it is within the backup scope
(`scripts/backup/dump-all-postgres.sh:18` dumps `webodm_dev`). The app reads `webodm_dev`
by default (`WO_DATABASE_NAME` unset; upstream `settings.py` default `webodm_dev`). The empty
`webodm` database in the same container is a 2026-09-30 rollback artefact, not the live
database. Measured 2026-10-16: `webodm_dev` holds 32 public tables (10 projects, 10 tasks);
`webodm` holds 0. This resolves the conflict between §8.4 (`~/webodm/dbdata`), §3.3.1
(`webodm`), and ST-03 (`webodm_dev`). The duplicate `POSTGRES_DB=webodm` default in
`quadlet/mapping/ao-webodm-db.container` is vestigial (the live `webodm_dev` predates it)
and changing it is an operator action.

The data directory resides on the root filesystem rather than the photogrammetry
drive; this gap is tracked as Open work item FIELD-11 in §19.1. Moving
a live PostgreSQL data directory is an operator decision and service-configuration
change. Measured 2026-10-16: the drive top level is now operator-writable
(`scottw:ao-mapping`, and `scottw` is in `ao-mapping`), but eight subdirectories
(`backups`, `deliverables`, `exports`, `incoming`, `manifests`, `rejected`, `tmp`,
`validated`) remain `ao-mapping:alwayson-mapping` mode `770` with `alwayson-mapping`
empty, so they are still operator-denied; see FIELD-10. Any move must fix that
ownership first, or the database lands on a volume its own operator cannot manage.

`/ALWAYSON/data/mapping/postgres/` and `/ALWAYSON/data/mapping/redis/` are not part of
the design and must stay empty; neither is a bind mount for the running services.

## 8.5 Mapping Mount Validation

The drive must be identified by filesystem UUID, not by `/dev/sdX`.

WebODM must refuse to start when:

- The mount is absent.
- The mountpoint resolves to the root filesystem.
- The mounted UUID differs from the approved UUID.
- `.mounted-ok` is absent.
- Available space is below the configured minimum.
- Required directories are missing.
- Mapping service ownership or permissions are incorrect.

Required validation:

```bash
lsblk -f
findmnt /media/scottw/500GBPHOTOGRAM
blkid
df -hT /media/scottw/500GBPHOTOGRAM
```

Begin with CPU-only validation. Enable GTX 1080 access only after validated
container GPU runtime, driver compatibility, measurable workload benefit, and a
documented CPU-only recovery path.
## 8.5.5 FIELD-10 measurement (2026-10-16)

- Support top level: `scottw:ao-mapping` mode `2770` — operator-writable; `scottw` is a member of
  `ao-mapping` (gid 1001), but **not** of `alwayson-mapping` (gid 975), which has no members at
  all.
- 8 of the 18 fixed sub-trees still sit under parents owned `ao-mapping:alwayson-mapping` mode
  `770`: `backups`, `deliverables`, `exports`, `incoming`, `manifests`, `rejected`, `tmp`,
  `validated`.
- 10 depth-2 directories are missing because they sit under those denied parents:
  `incoming/{drone,operator,quarantine}`, `manifests/{intake,processing,ledger-submissions}`,
  `exports/{pcloud-staging,ipfs-staging}`, `backups/mapping-db`, `tmp/processing`.
- Measured 2026-10-16 by attempting creation 10×: all `MKDIR-DENIED`, with a control under
  `webodm/` that succeeds.
- The §8.5 refusal conditions are now enforced by `scripts/validation/check-photogrammetry-mount.sh`
  (exit 25 when the required directories are missing; exit 26 when ownership/permissions are
  incorrect; exit 0 once remediated).
- Remediation remains an operator action: `sudo usermod -aG alwayson-mapping scottw` (then re-login)
  so that scottw is a member of `alwayson-mapping`, after which the 8 parents are writable and the
  10 directories can be created.

