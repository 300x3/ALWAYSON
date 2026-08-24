#!/usr/bin/env bash
# ALWAYS ON - validation: unapproved exposed ports (Section 4.1, Section 2.2 pause rules)
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_lock check-open-ports

ALLOWLIST="$AO_ROOT/config/platform/listener-allowlist.yaml"
[[ -f "$ALLOWLIST" ]] || { echo "ERROR: missing $ALLOWLIST" >&2; exit 10; }

violations=0
report=""
# TCP listeners only; UDP handled by mDNS/kdeconnect policy review.
while read -r local_addr; do
  ip="${local_addr%:*}"
  port="${local_addr##*:}"
  case "$ip" in
    127.*|'::1'|'[::1]') continue ;;                 # loopback: acceptable
    '0.0.0.0'|'*'|'[::]'|'::')                       # wildcard bind
      if grep -qE "^[[:space:]]*- ${port}$" "$ALLOWLIST"; then
        report+="APPROVED  wildcard :${port}\n"
      else
        report+="VIOLATION public wildcard :${port} not in allowlist\n"
        violations=$((violations+1))
      fi ;;
    *)                                               # LAN-scoped bind
      report+="REVIEW    lan-bound ${ip}:${port}\n" ;;
  esac
done < <(ss -tlnH | awk '{print $4}')

printf '%s' "$report"
if (( violations > 0 )); then
  echo "FAIL: $violations unapproved public listener(s) - resolve or allowlist after operator review" >&2
  exit 40
fi
echo "OK: no unapproved public listeners (IPv4/IPv6)"