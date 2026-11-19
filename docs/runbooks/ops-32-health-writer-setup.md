# OPS-32 Health Writer Credential Setup

**Status:** Blocked on PostgreSQL superuser access. `ao_health_writer` role exists with proper permissions but password is not set, and `pg_hba.conf` has no entry for it.

**Date:** 2026-11-11

---

## Current State

| Item | State | Details |
|------|-------|---------|
| `ao_health_writer` PostgreSQL role | ✅ EXISTS | `rolcanlogin=true`, `rolsuper=false`, `rolinherit=false` |
| Schema `ao_status` | ✅ EXISTS | 11 tables + 1 view in `grafana` database |
| `ao_health_writer` permissions | ✅ GRANTED | `USAGE` on schema `ao_status`, `INSERT/UPDATE/DELETE/TRUNCATE` on all tables |
| `grafana_app` privileges | ✅ Verified | `CREATE` on `grafana` database, `rolsuper=false`, `rolcreaterole=false`, `rolcreatedb=false` |
| `collect-system-health.py` | ✅ Ready | Connects as `ao_health_writer` to `/var/run/postgresql` → `grafana` |
| `pg_hba.conf` entry for `ao_health_writer` | ❌ MISSING | Falls through to `local all all peer` — fails because `scottw` ≠ `ao_health_writer` |
| `ao_health_writer` password in PostgreSQL | ❌ NOT SET | Requires superuser `ALTER ROLE` |
| `ao_health_writer` password in KDE Wallet | ❌ MISSING | `ao-admin/ao_health_writer_password` — wallet read times out (entry likely doesn't exist) |

---

## What Needs to Be Done

### Step 1: Set the `ao_health_writer` PostgreSQL role password

**Requires:** PostgreSQL superuser access (operator must run as `postgres` user)

```bash
# Generate a password (operator chooses)
openssl rand -base64 32

# Set the role password (requires superuser)
sudo -u postgres psql -c "ALTER ROLE ao_health_writer PASSWORD '<generated-password>';"
```

### Step 2: Store password in KDE Wallet

```bash
# Store in KDE Wallet (run as scottw after Plasma login)
python3 /ALWAYSON/scripts/ops/wallet-write-secret.py kdewallet ao-admin ao_health_writer_password '<generated-password>'
```

### Step 3: Add `pg_hba.conf` entry for `ao_health_writer`

**File:** `/ALWAYSON/config/platform/postgresql/pg_hba.conf`

Add this line **above** the `local all all peer` catch-all (line ~130, after the `grafana_app` entry):

```
local   grafana          ao_health_writer                        scram-sha-256
```

**Also add for TCP (if needed):**
```
host    grafana          ao_health_writer        127.0.0.1/32    scram-sha-256
host    grafana          ao_health_writer        ::1/128         scram-sha-256
```

**Then reload PostgreSQL:**
```bash
sudo systemctl reload postgresql
# or
sudo -u postgres psql -c "SELECT pg_reload_conf();"
```

### Step 4: Verify end-to-end

```bash
# Test connection as ao_health_writer
export PGPASSWORD='<generated-password>'
psql -h /var/run/postgresql -U ao_health_writer -d grafana -c "SELECT 1;"

# Test collect-system-health.py
python3 /ALWAYSON/scripts/operations/collect-system-health.py --dry-run
```

---

## Why This Is Blocked

`ALTER ROLE ao_health_writer PASSWORD ...` requires PostgreSQL superuser (`postgres` role). The `scottw` user is not a superuser and cannot `su - postgres` (no password), `pkexec -u postgres` fails (pg_wrapper), and `sudo -u postgres` requires interactive terminal authentication.

The `grafana_app` role has `CREATE` on the `grafana` database but cannot `CREATEROLE` or `SUPERUSER` — it can grant privileges on `ao_status` tables but cannot set another role's password.

---

## After Step 3 (pg_hba.conf reload)

Once `pg_hba.conf` has the `ao_health_writer` entry and PostgreSQL is reloaded:
- `collect-system-health.py` will connect as `ao_health_writer` instead of `grafana_app`
- The deviation note in `ao-status.sql` (writer sharing `grafana_app`) is resolved
- OPS-32 can be marked COMPLETE

---

## References

- `README-ACTION_ITEMS/status-and-references.md` — OPS-32 row
- `README.md` §6.A.3 — reporting identities
- `README.md` §4.1 rule 1 — least privilege
- `/ALWAYSON/scripts/operations/collect-system-health.py` — the collector
- `/ALWAYSON/config/platform/postgresql/ao-status.sql` — schema setup
- `/ALWAYSON/config/platform/postgresql/pg_hba.conf` — authentication rules
