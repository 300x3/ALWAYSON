#!/usr/bin/env bash
# ALWAYS ON - check-network-isolation.sh
#
# config/platform/network-cidrs.yaml is the SOURCE OF TRUTH (README 2.2, 5.1.1).
# This script READS it and asserts that the running host agrees. It is
# deliberately read-only: it never creates, edits, or regenerates the registry.
#
# The previous version rebuilt that file from a hardcoded `expected=(...)` array,
# so the file the document named as the authority was in fact derived from the
# script, and any network added to podman but absent from that array was
# silently deleted from the authority on the next run. Adding a network is now
# a deliberate two-step act: create it, then add its line to the registry.
#
# Usage:
#   check-network-isolation.sh               assert the registry against the host
#   check-network-isolation.sh --emit-table  print the 5.1.1 inventory rows,
#                                           derived from the registry
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_require_cmds podman

# Overridable only so the script can be exercised against a checkout that is
# not the live /ALWAYSON tree. Production calls take the default.
registry="${AO_REGISTRY:-$AO_ROOT/config/platform/network-cidrs.yaml}"

# Expected totals, asserted rather than printed (README 2.2, 5.1.1, 13.3 all
# state these numbers). Adding or removing a network without also changing the
# count is a failure, not a silently-renumbered document.
expected_total=14
expected_internal=11
expected_egress=3

emit_table=false
if [[ "${1:-}" == "--emit-table" ]]; then emit_table=true; fi

[[ -r "$registry" ]] || { echo "ERROR: registry not readable: $registry" >&2; exit 2; }

# --- read the registry -----------------------------------------------------
# Line format: <name> internal=<bool> subnets=<cidr>[,<cidr>...]
declare -A reg_internal=()
declare -A reg_subnets=()
registry_order=()
while IFS= read -r raw || [[ -n "$raw" ]]; do
  line="${raw%%$'\r'}"
  # strip leading whitespace
  line="${line#"${line%%[![:space:]]*}"}"
  [[ -z "$line" ]] && continue
  [[ "${line:0:1}" == "#" ]] && continue
  name="${line%% *}"
  int=""
  sub=""
  if [[ "$line" =~ internal=(true|false) ]]; then int="${BASH_REMATCH[1]}"; fi
  if [[ "$line" =~ subnets=([^[:space:]]+) ]]; then sub="${BASH_REMATCH[1]%%,*}"; fi
  if [[ -z "$int" || -z "$sub" ]]; then
    echo "ERROR: unparseable registry line: $raw" >&2
    exit 2
  fi
  if [[ -n "${reg_internal[$name]+x}" ]]; then
    echo "ERROR: duplicate network in registry: $name" >&2
    exit 2
  fi
  reg_internal["$name"]="$int"
  reg_subnets["$name"]="$sub"
  registry_order+=("$name")
done < "$registry"

# --- assert the registry against the running host --------------------------
fails=0
n_internal=0
n_egress=0

for name in "${registry_order[@]}"; do
  want_int="${reg_internal[$name]}"
  want_sub="${reg_subnets[$name]}"
  if [[ "$want_int" == "true" ]]; then
    n_internal=$((n_internal + 1))
  else
    n_egress=$((n_egress + 1))
  fi

  if ! info="$(podman network inspect "$name" \
        --format '{{.Name}} internal={{.Internal}} {{range .Subnets}}{{.Subnet}} {{end}}' 2>/dev/null)"; then
    echo "ERROR: registry network missing from podman: $name" >&2
    fails=$((fails + 1))
    continue
  fi

  got_int="false"
  if [[ "$info" == *"internal=true"* ]]; then got_int="true"; fi
  if [[ "$got_int" != "$want_int" ]]; then
    echo "ERROR: $name registry says internal=$want_int but podman reports internal=$got_int" >&2
    fails=$((fails + 1))
  fi
  if [[ "$info" != *"$want_sub"* ]]; then
    echo "ERROR: $name registry says $want_sub but podman reports: $info" >&2
    fails=$((fails + 1))
  fi

  if [[ "$emit_table" == true ]]; then
    printf '| `%s` | %s | %s |\n' "$name" "$want_sub" "$want_int"
  elif [[ "$want_int" == "false" ]]; then
    # Egress networks are Internal=false on purpose: they exist to reach a
    # provider. Reported, never treated as a violation.
    echo "OK: $name ($want_sub) Internal=false by decision"
  else
    echo "OK: $name ($want_sub) Internal=true"
  fi
done

# --- a live ao-* network absent from the registry is a real defect ---------
# The previous version structurally could not see this: it only walked its own
# hardcoded array.
while read -r live; do
  if [[ -z "${reg_internal[$live]+x}" ]]; then
    live_sub="$(podman network inspect "$live" --format '{{range .Subnets}}{{.Subnet}}{{end}}' 2>/dev/null || true)"
    echo "ERROR: live podman network not in the registry: $live ($live_sub)" >&2
    fails=$((fails + 1))
  fi
done < <(podman network ls --format '{{.Name}}' | grep '^ao-' || true)

# --- asserted totals -------------------------------------------------------
n_total=$((n_internal + n_egress))
if (( n_total != expected_total )); then
  echo "ERROR: registry lists $n_total ao-* networks, expected $expected_total" >&2
  fails=$((fails + 1))
fi
if (( n_internal != expected_internal )); then
  echo "ERROR: registry lists $n_internal Internal=true, expected $expected_internal" >&2
  fails=$((fails + 1))
fi
if (( n_egress != expected_egress )); then
  echo "ERROR: registry lists $n_egress Internal=false, expected $expected_egress" >&2
  fails=$((fails + 1))
fi

if [[ "$emit_table" == true ]]; then
  printf '<!-- registry: %d ao-* networks, %d Internal=true, %d Internal=false -->\n' \
    "$n_total" "$n_internal" "$n_egress"
  if (( fails > 0 )); then exit 1; fi
  exit 0
fi

if (( fails == 0 )); then
  ao_audit "network isolation verified: $n_total ao-* networks match registry ($n_internal internal, $n_egress egress by decision)"
  echo "OK: all domain networks present; isolation domains internal-only; $n_egress egress networks non-internal by decision; registry matches host ($n_total = $n_internal + $n_egress)"
  exit 0
fi

echo "FAILED: $fails isolation assertion(s)" >&2
exit 42
