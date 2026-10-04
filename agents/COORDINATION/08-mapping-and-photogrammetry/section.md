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

**Validated 2026-10-03 — the tree does not match this specification.** The mount itself is
healthy; the folder layout is not. See §8.5.1 for the per-directory result. The tree below
remains the specification; it is recorded as **not yet satisfied**, not as corrected.

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
| Signed manifests | `/ALWAYSON/artifacts/mapping-manifests/` |

`/ALWAYSON/data/mapping/postgres/` and `/ALWAYSON/data/mapping/redis/` are not part of the
design and must stay empty; neither is a bind mount for the running services.

### 8.4.1 Authoritative mapping database — decided 2026-10-03

The §8.4 table said `~/webodm/dbdata`, ST-03 said the app reads `webodm_dev`, and §3.3.1 named
`webodm`. **One name, one location — decided here:**

| Question | Answer |
|---|---|
| Logical database | **`webodm_dev`** |
| Physical storage | **`/home/scottw/webodm/dbdata`**, bind-mounted at `/var/lib/postgresql/data` on `ao-webodm-db` |
| Backup scope | **Included** — `scripts/backup/dump-all-postgres.sh:18` |

Measured:

```bash
$ podman inspect ao-webodm-db --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{end}}'
/home/scottw/webodm/dbdata -> /var/lib/postgresql/data

$ podman exec ao-webodm-db psql -U postgres -tAc \
    "SELECT datname FROM pg_database WHERE NOT datistemplate ORDER BY 1;"
postgres
webodm
webodm_dev

$ grep -n webodm scripts/backup/dump-all-postgres.sh
15:  # mastodon and webodm live in their own containers; the host dump cannot see them.
18:  bash "$C" mapping ao-webodm-db webodm_dev postgres || { echo "FAIL: webodm"; fail=1; }

$ podman inspect ao-webodm-webapp --format '{{range .Config.Env}}{{println .}}{{end}}' \
    | grep -vi 'password\|secret\|key' | grep -i database
WO_DATABASE_HOST=ao-webodm-db
```

The `webodm` database still exists but is **not** the authoritative one; per ST-03 it was the
duplicate host-cluster database, migrated into `webodm_dev` and the duplicates dropped
2026-09-30 (backups in `backups/duplicate-db-20260930/`). It is retained only as a rollback
artefact. **Any reader of this README must use `webodm_dev`.** `~/webodm/dbdata` is confirmed
correct and needs no change.

**The §8.1/§8.5 requirement that mapping storage sit on the photogrammetry drive is NOT met,
and is recorded as an approved deviation rather than silently dropped.** The PostgreSQL
data directory is on the root filesystem; the drive holds `webodm/{media,projects,nodeodm,temp,logs}`,
which is where the imagery and processing state actually live. Moving a live PostgreSQL data
directory onto an external drive would change service configuration and is an operator decision.
FIELD-11 is closed on the *name and location* question, which is what the item asked; the
drive-residency half remains an open deviation, recorded in §8.4.1 and to be carried forward
as a new **FIELD** item rather than reopened.

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

### 8.5.1 Validation executed 2026-10-03 — mount passes, tree fails

The shipped validator passes:

```bash
$ bash scripts/validation/check-photogrammetry-mount.sh
OK: photogrammetry mount valid: systemd-1
/dev/sdb1; 434G free
rc=0
```

against `config/mapping/photogrammetry-volume.env`
(`PHOTOGRAM_UUID=498597d4-9fc8-42cf-8db7-4e71ede53267`, `PHOTOGRAM_MIN_FREE_GB=100`). UUID
match, mount-marker and free-space checks all pass. The autofs stacking noted in the script
comment is handled correctly.

**But the validator does not check the directory tree at all**, even though §8.5 lists
"Required directories are missing" as a refusal condition. Enumerating §8.2's required paths
directly:

```bash
$ M=/media/scottw/500GBPHOTOGRAM
$ for d in incoming incoming/drone incoming/operator incoming/quarantine validated rejected \
           webodm webodm/media webodm/projects webodm/nodeodm webodm/temp webodm/logs \
           deliverables manifests manifests/intake manifests/processing \
           manifests/ledger-submissions exports exports/pcloud-staging \
           exports/ipfs-staging backups backups/mapping-db retention \
           retention/pending-review retention/eligible-for-archive tmp tmp/processing \
           README.md .mounted-ok; do
    [ -e "$M/$d" ] && printf 'OK      %s\n' "$d" || printf 'MISSING %s\n' "$d"
  done
```

| Result | Paths |
|---|---|
| **Present** | `incoming`, `validated`, `rejected`, `webodm`, `webodm/{media,projects,nodeodm,temp,logs}`, `deliverables`, `manifests`, `exports`, `backups`, `retention`, `retention/{pending-review,eligible-for-archive}`, `tmp`, `.mounted-ok` |
| **Missing — 11** | `incoming/drone`, `incoming/operator`, `incoming/quarantine`, `manifests/intake`, `manifests/processing`, `manifests/ledger-submissions`, `exports/pcloud-staging`, `exports/ipfs-staging`, `backups/mapping-db`, `tmp/processing`, `README.md` |

Ownership is correct at the top level — every directory is `ao-mapping:alwayson-mapping`
(mode `drwxrws---`, group `rwx`, **world has no permission at all**), and `.mounted-ok` is
`scottw:scottw`. The setgid bit `s` is set, so new files inherit the mapping group, which is
the correct arrangement for a shared mapping volume.

**Correction to an earlier claim in this subsection.** A first pass ran
`find "$M" -maxdepth 4 -type d -perm -0002` and reported "empty", concluding no directory is
world-writable. That conclusion was **not sound**: `find` also emitted
`Permission denied` for 8 of the 10 top-level subtrees, and the exit status was 1. The empty
result meant "none of the two subtrees this session can read", not "none on the drive".
Re-measured honestly:

```bash
$ id -u
1000
$ M=/media/scottw/500GBPHOTOGRAM
$ ok=0; no=0; for d in incoming validated rejected webodm deliverables manifests \
      exports backups retention tmp; do
    [ -r "$M/$d" ] && ok=$((ok+1)) || no=$((no+1)); done; echo "readable=$ok unreadable=$no"
readable=2 unreadable=8

$ ls -la $M
drwxrws--- 13 scottw     ao-mapping        4096 Aug 26 16:57 .
drwxrws---  3 ao-mapping alwayson-mapping  4096 Aug 23 18:31 backups
drwxrws---  2 ao-mapping alwayson-mapping  4096 Aug 23 18:31 deliverables
drwxrws---  4 ao-mapping alwayson-mapping  4096 Aug 23 18:31 exports
drwxrws---  5 ao-mapping alwayson-mapping  4096 Aug 23 18:31 incoming
drwxrws---  5 ao-mapping alwayson-mapping  4096 Aug 23 18:31 manifests
drwxrws---  2 ao-mapping alwayson-mapping  4096 Aug 23 18:31 rejected
drwxrws---  4 scottw     scottw            4096 Aug 23 18:31 retention
drwxrws---  3 ao-mapping alwayson-mapping  4096 Aug 23 18:31 tmp
drwxrws---  2 ao-mapping alwayson-mapping  4096 Aug 23 18:31 validated
drwxrws---  7 scottw     ao-mapping        4096 Aug 23 18:31 webodm
```

So: **no world-writable directory at depth 1** is confirmed, and the `ao-mapping` ownership
scheme is confirmed. **Depths 2-4 are unverified** for an unprivileged session — eight
subtrees could not be traversed. Full ownership and permission validation therefore
**cannot be signed off from here**; it needs `sudo` or an `ao-mapping` group membership. This
is a *second* reason, alongside the 11 missing directories, that FIELD-10 stays open.

The reserved `data/mapping` paths are correctly **absent**, as §8.4 requires:

```bash
$ ls -la /ALWAYSON/data/mapping/postgres/ /ALWAYSON/data/mapping/redis/
ls: cannot access '/ALWAYSON/data/mapping/postgres/': No such file or directory
ls: cannot access '/ALWAYSON/data/mapping/redis/': No such file or directory
```

The `.mounted-ok` sentinel exists and is empty (`size=0`), owned `scottw:scottw` mode
`rw-rw----` — which is correct: it is a presence marker, not a content marker.

`backups/mapping-db` being missing is the consequential one: it is where the §8.4.1 database
backups would land on the drive. This does **not** put the database outside backup scope —
`scripts/backup/dump-all-postgres.sh:18` already dumps `webodm_dev` — but it does mean there is
currently no on-drive copy.

**Two consequences for the reader:**

1. §8.5's claim that WebODM "must refuse to start" on missing directories is **not enforced by
   any shipped script.** `check-photogrammetry-mount.sh` exits 0 on a drive that is 11 directories
   short of its own specification. A green validator run is therefore **not** evidence that §8.2
   holds, and must not be cited as such.
2. Creating the missing directories would change live storage on the photogrammetry drive,
   which is outside what this session may do unprompted. **Not created.** FIELD-10 stays
   **open** with this evidence attached — the validation has now been *run and failed*, which is
   strictly more progress than the prior "unvalidated" state.

## 8.6 3D Model Identity and Database Cross-Referencing

Every 3D model, model revision, component, assembly, and derived artifact must be
addressable from the same database and ledger correlation system used for sales
and receipts. The model file is not itself the authority; the authoritative
relationship is the PostgreSQL registry entry plus the signed content manifest.

### 8.6.1 Identifier hierarchy

Use a stable, globally unique `model_object_id` for the logical object and a
separate `model_revision_id` for each version:

```text
model_object_id       # Stable identity of the logical 3D object or assembly
model_revision_id     # One specific model revision/artifact
serial_number         # Physical asset, when the model represents a sold product
correlation_id        # Business/event correlation across PostgreSQL and Corda
receipt_number        # Commercial receipt, when the model is sold
event_timestamp_utc   # When the relationship/event was recorded
content_hash_sha256   # Hash of the exact model file or packaged artifact
```

`model_object_id` remains stable across revisions. A revised model must not reuse
an old revision ID. `serial_number` links the model to a physical product; it
is not a replacement for the model object ID.

**3D objects come and go; the data about them must not.** The identity, the
registry record, and the ledger references must remain consistent for the life
of the object, and must be able to exist in either of two states:

- **With no 3D object at all.** A `model_object_id` may exist with no current
  revision — for example before any geometry is authored, or after every
  revision has been retired. The registry row, its links, and its Corda
  references stay valid and remain the authoritative history.
- **With a connection to a new object.** A replacement object receives its own
  `model_object_id`, and `model_object_links` records the relation between the
  two. The original identity is never overwritten or reused.

Consequently, no business record may depend on the presence of a 3D file.
Serial numbers, receipts, entitlements, manifests, and Corda state reference the
`model_object_id` and its revisions, never a file path. `content_hash_sha256`
is an attribute of a revision, not of the object, and a revision whose artifact
is no longer on disk stays in the registry as a `retired` record with its hash
intact.

### 8.6.2 Metadata carried with the 3D model

Each model package must carry a sidecar metadata document or embedded metadata
block containing at least:

```json
{
  "model_object_id": "OBJ-300X3-BATTERY-0001",
  "model_revision_id": "REV-2026-09-25-01",
  "object_type": "cad_assembly",
  "source_system": "cad_release",
  "serial_number": "SN-300X3-000042",
  "correlation_id": "ORDER-2026-000123-A",
  "receipt_number": "RCPT-2026-000123",
  "event_timestamp_utc": "2026-09-25T12:34:56Z",
  "schema_version": "1.0",
  "content_hash_sha256": "SHA256_DIGEST",
  "source_artifact_reference": "opaque internal reference",
  "license_reference": "approved license/terms reference",
  "is_public_proof_eligible": false
}
```

The metadata is cross-referenced, not duplicated wholesale: the model contains
identity and reference fields, PostgreSQL contains the operational record, and
Corda contains the signed state/reference.

### 8.6.3 Database registry

The model registry is a PostgreSQL schema equivalent to:

```text
model_objects
  model_object_id, object_type, canonical_name, created_at_utc, created_by,
  current_revision_id

model_revisions
  model_revision_id, model_object_id, revision_number, content_hash_sha256,
  source_artifact_reference, archive_reference, license_reference,
  created_at_utc, created_by

model_object_links
  model_object_id, link_type, serial_number, correlation_id, receipt_number,
  event_timestamp_utc, valid_from_utc, valid_to_utc

model_ledger_references
  model_revision_id, corda_event_type, corda_transaction_id, corda_state,
  corda_confirmed_at_utc, manifest_reference
```

`model_object_links` is the cross-reference table. It relates a model object to
a product, serial number, receipt, order, mapping project, simulation result,
release, or other approved object without embedding the operational record in
the 3D file.

### 8.6.4 Cross-reference flow

```text
CAD/3D authoring tool
        │ model_object_id + model_revision_id
        ▼
Model registry (PostgreSQL)
        ├── serial_number → product/asset record
        ├── correlation_id + receipt_number → sale contract record
        ├── content_hash → exact model artifact
        └── manifest reference → signed ledger event
                                  │
                                  ▼
                             Corda state
```

A viewer, CAD tool, WebODM/NodeODM exporter, or marketing application resolves
a model by reading its object/revision IDs, validating the content hash, looking
up the PostgreSQL registry, following approved links to the serial/receipt
record, following the Corda projection, and returning only fields permitted for
that audience.

### 8.6.5 Integrity and relationship rules

- A model revision has exactly one `model_revision_id`.
- A model revision has one immutable `content_hash_sha256`.
- A revision ID cannot point to different content hashes.
- A model object may have many revisions, but exactly one is the current revision.
- A physical serial number may have many model revisions over its lifetime.
- A receipt may reference many model objects or serials through the link table.
- A model relationship records `event_timestamp_utc` and its source.
- A retired revision is preserved and marked `retired`, never reused.
- A Corda reference is required before a model is called provenance-verified.
- A content hash proves file integrity, not authenticity or publication safety.

### 8.6.6 Public and private model metadata

Internal metadata may contain serial numbers, correlation IDs, and opaque
references. Public marketing metadata should contain only approved fields:

```text
model_object_id or public proof ID
product/SKU
approved serial or proof token
revision label
provenance status
public verification reference
content hash or public proof hash
license/terms reference
```

Do not publish customer identity, receipt totals, addresses, payment references,
private simulation data, internal paths, or Corda transaction details unless that
disclosure is explicitly approved.

### 8.6.7 Relationship to the sale/receipt process

For a sold product, the 3D model metadata (`model_object_id`,
`model_revision_id`, `serial_number`) resolves to the PostgreSQL model registry,
`sale_contract_lines`, receipt/correlation projection, and signed Corda
provenance reference. The receipt and model may each show a reference to the
same correlation record. Neither file is the authoritative sale ledger.

---
