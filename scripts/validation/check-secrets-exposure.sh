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
(( violations == 0 )) && echo "OK: no secret-shaped content in tracked files" || { echo "FAIL: $violations file(s)" >&2; exit 43; }
