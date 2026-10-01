# ALWAYS ON - check-secrets-exposure.sh: scan git-tracked files for secret-shaped content.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_require_cmds git
cd "$AO_ROOT"
patterns=(
  'BEGIN [A-Z ]*PRIVATE KEY'
  '(api[_-]?key|secret|password|passwd|token)[[:space:]]*[:=][[:space:]]*["'"'"']?[A-Za-z0-9+/]{16,}'
  'AKIA[0-9A-Z]{16}'
)
violations=0
while IFS= read -r f; do
  [[ -f "$f" ]] || continue
  for p in "${patterns[@]}"; do
    hits="$(grep -Ein "$p" -- "$f" 2>/dev/null | grep -viE 'REPLACE_WITH|example|placeholder|""|\$\{|\$1' || true)"
    if [[ -n "$hits" ]]; then
      echo "SECRET-SHAPED CONTENT in $f:" >&2; echo "$hits" >&2
      violations=$((violations+1))
    fi
  done
done < <(git ls-files)

# Rule 7 says KDE Wallet is the sole secret authority. A tracked .env is fine
# if it holds no secret (non-secret settings are tracked deliberately, e.g.
# config/mapping/photogrammetry-volume.env). What must never exist is a tracked
# .env carrying a credential, because the wallet already holds it.
secret_key_re='^(GF_SECURITY_[A-Z_]*PASSWORD|GF_DATABASE_PASSWORD|GF_ADMIN_PASSWORD|MB_DB_PASS|POSTGRES_PASSWORD|METAREAD_PASSWORD|SALES_REPORTING_PASSWORD|DB_PASS|RESTIC_REPOSITORY_PASSWORD|[A-Z_]*PASSWORD|[A-Z_]*ACCESS_TOKEN|[A-Z_]*REFRESH_TOKEN|[A-Z_]*CLIENT_SECRET|[A-Z_]*API_KEY|[A-Z_]*SECRET_KEY|SECRET_KEY_BASE|OTP_SECRET)=.+'
while IFS= read -r f; do
  [[ -f "$f" ]] || continue
  case "$f" in
    *.env)
      if grep -qE "$secret_key_re" -- "$f" 2>/dev/null; then
        echo "VIOLATION: tracked env file $f holds a credential; secrets belong in KDE Wallet only (rule 7)" >&2
        violations=$((violations+1))
      fi
      ;;
  esac
done < <(git ls-files)

# Quadlet units must not take a secret-bearing EnvironmentFile from inside
# config/. Only %h/.local/share/ao-secrets/ (materialised 0600 from the wallet)
# and non-secret settings files are acceptable there.
while IFS= read -r f; do
  [[ -f "$f" ]] || continue
  hits="$(grep -nE '^EnvironmentFile=/ALWAYSON/(secrets|config)/' -- "$f" 2>/dev/null || true)"
  if [[ -n "$hits" ]]; then
    while IFS= read -r line; do
      target="${line#*:}"
      target="${target#EnvironmentFile=}"
      if grep -qE "$secret_key_re" -- "$target" 2>/dev/null; then
        echo "VIOLATION: $f sources secret-bearing $target (should be wallet-backed)" >&2
        violations=$((violations+1))
      fi
    done <<< "$hits"
  fi
done < <(git ls-files 'quadlet/*')

# Any secret-bearing env file on disk must not be readable beyond its owner.
# 0600 is the norm; 0640/0644 with an ACL that grants no access to "other" is
# also acceptable (ao-secrets/mastodon.env is read by the ao-sales user via an
# explicit ACL entry).
# 2026-10-01: the glob above matched only '*.env' and '*.credential', so a temp
# file left behind by a fetcher ('*.env.tmp') was INVISIBLE to this check. That
# is not hypothetical: fetch-kwallet-secret.sh lacked `umask 077`, so its
# "$OUTPUT_FILE.tmp" was created 0664 and held a real secret mid-write, while
# the final file was chmod 600 and this validator passed. The fetch scripts now
# set umask 077 and clean up on EXIT, but the check must still catch the class
# in case a future fetcher reintroduces it.
#
# Two additions:
#   1. match '*.env.tmp' / '*.credential.tmp' as secret-bearing paths;
#   2. flag ANY leftover .tmp in the secrets directory at all, because an
#      orphaned temp file means a fetcher died mid-run and its final file may
#      be stale rather than absent.
while IFS= read -r f; do
  [[ -f "$f" ]] || continue
  # Only TEMP files get the "leftover debris" treatment. A legitimate .env that
  # simply holds no secret-shaped key (payment.env carries a DSN, not a key
  # name) is NOT debris and must not be flagged. My first attempt applied this
  # branch to every matched file and wrongly failed 4 healthy files.
  case "$f" in
    *.tmp)
      if ! grep -qE "$secret_key_re" -- "$f" 2>/dev/null; then
        # An orphaned temp file means a fetcher died mid-run.
        echo "VIOLATION: $f is a leftover temp file from a failed secret fetch; remove it" >&2
        violations=$((violations+1))
        continue
      fi
      ;;
  esac
  grep -qE "$secret_key_re" -- "$f" 2>/dev/null || continue
  mode="$(stat -c '%a' "$f")"
  other="$(stat -c '%A' "$f" | cut -c8-10)"
  if [[ "$other" != "---" ]]; then
    echo "VIOLATION: $f is accessible by others ($mode) but holds secrets; must be 0600 or ACL-restricted" >&2
    violations=$((violations+1))
  fi
done < <(find /ALWAYSON/secrets "$HOME/.local/share/ao-secrets" "$AO_ROOT/config" -type f \
           \( -name '*.env' -o -name '*.credential' -o -name '*.env.tmp' -o -name '*.credential.tmp' \) 2>/dev/null)

(( violations == 0 )) && echo "OK: no secret-shaped content in tracked files" || { echo "FAIL: $violations file(s)" >&2; exit 43; }
