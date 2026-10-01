#!/usr/bin/env bash
# ALWAYS ON - manual payment reconciliation (README Section 7.2, 18.4).
#
# Zelle publishes no webhook and offers no public API, so it is reconciled by
# hand under the same control as a wire transfer (Section 7.2): the operator
# records the evidence, an approval reference, and the result. Nothing here
# marks a payment validated on its own; every validated row requires an
# explicit operator approval reference, and the approving operator is stored.
#
# No provider secret is accepted on the command line or written to any log.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh
ao_require_cmds psql

usage() {
  cat >&2 <<'USAGE'
usage: ao-payment-reconcile.sh <record|list>
  record --order-id <uuid> --provider <paypal|Zelle|coinbase> --ref <provider-ref> \
         --amount-cents <int> --currency <ISO4217> --settlement-ref <id> \
         --approved-by <operator> [--authorization-ref <ref>] [--note <text>]
  list
USAGE
}

cmd="${1:-}"; [ -n "$cmd" ] || { usage; exit 2; }
[ "$#" -ge 2 ] && shift

env_file="${AO_HOME}/.local/share/ao-secrets/payment.env"
dsn="$(grep -h '^PAYMENT_DSN=' "$env_file" 2>/dev/null | cut -d= -f2- || true)"
[ -n "$dsn" ] || { ao_log "ERROR: no PAYMENT_DSN in ${env_file}"; exit 1; }

q() { psql "$dsn" -v ON_ERROR_STOP=1 -qX -c "$1"; }

case "$cmd" in
  list)
    q "SELECT provider, state, count(*), max(updated_at)
       FROM payment_references GROUP BY 1,2 ORDER BY 1,2;"
    ;;
  record)
    provider=""; ref=""; amount=""; currency=""; settlement=""; approved=""
    authref=""; note=""; order_id=""
    while [ "$#" -gt 0 ]; do
      case "$1" in
        --order-id) order_id="${2:-}"; shift 2;;
        --provider) provider="${2:-}"; shift 2;;
        --ref) ref="${2:-}"; shift 2;;
        --amount-cents) amount="${2:-}"; shift 2;;
        --currency) currency="${2:-}"; shift 2;;
        --settlement-ref) settlement="${2:-}"; shift 2;;
        --approved-by) approved="${2:-}"; shift 2;;
        --authorization-ref) authref="${2:-}"; shift 2;;
        --note) note="${2:-}"; shift 2;;
        *) ao_log "unknown argument: $1"; usage; exit 2;;
      esac
    done
    [ -n "$provider" ] && [ -n "$ref" ] && [ -n "$amount" ] && [ -n "$currency" ] \
      && [ -n "$settlement" ] && [ -n "$approved" ] && [ -n "$order_id" ] \
      || { usage; exit 2; }
    # Validate as a UUID by shape, letting PostgreSQL be the final authority
    # on the cast. A shell glob over [0-9a-fA-F] would need one character per
    # hex digit, which is unreadable and easy to miscount.
    if ! printf '%s' "$order_id" | grep -Eq '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'; then
      ao_log "order-id must be a uuid"; exit 2
    fi
    case "$provider" in paypal|Zelle|coinbase) ;; *) ao_log "provider must be paypal, Zelle or coinbase"; exit 2;; esac
    case "$currency" in [A-Z][A-Z][A-Z]) ;; *) ao_log "currency must be a 3-letter ISO code"; exit 2;; esac
    case "$amount" in ''|*[!0-9]*) ao_log "amount-cents must be an integer"; exit 2;; esac
    case "$currency" in *[a-z]*) ao_log "currency must be uppercase"; exit 2;; esac
    # Idempotent on provider_ref: re-recording updates state, never duplicates.
    # order_id is NOT NULL and orders has no reference column, so the operator
    # must state which order this payment settles.
    q "INSERT INTO payment_references
         (order_id, provider, provider_ref, state, amount_cents, currency,
          settlement_ref, approved_by, authorization_ref, note, updated_at)
       VALUES ('${order_id}'::uuid, '${provider}', '${ref}', 'verified',
               ${amount}, '${currency}', '${settlement}', '${approved}',
               '${authref}', '${note}', now())
       ON CONFLICT (provider_ref) DO UPDATE
         SET state='verified', amount_cents=EXCLUDED.amount_cents,
             currency=EXCLUDED.currency, approved_by=EXCLUDED.approved_by,
             authorization_ref=EXCLUDED.authorization_ref,
             settlement_ref=EXCLUDED.settlement_ref,
             note=EXCLUDED.note, updated_at=now();"
    ao_audit "payment-reconcile provider=${provider} ref=${ref} approved_by=${approved}"
    ;;
  *)
    usage; exit 2;;
esac
