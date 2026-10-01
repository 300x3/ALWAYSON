#!/usr/bin/env bash
# ALWAYS ON - provision the metaread reporting identity (Section 6.A.2).
# The wallet (ao-admin/metaread-password) is the source of truth: the password
# is read from it and mirrored back, so no plaintext file is created and the
# role can never drift from the wallet (README 4.1 rule 7 / 14.1.1).
set -Eeuo pipefail
umask 077
PW_FILE=/ALWAYSON/secrets/reporting/metaread.env
WALLET_HELPER=/ALWAYSON/scripts/ops/wallet-read-secret.py

# 2026-10-01 hardening. Previously a missing wallet entry silently caused a NEW
# password to be minted and then written to the wallet. That is a legitimate
# first-run bootstrap, but it is also a foot-gun: a typo'd folder name, a locked
# wallet or a wrong --wallet argument all read as "no entry", and the script
# would then silently rotate the password of a LIVE database role. Generating is
# now an explicit, opt-in action.
GENERATE_NEW=0
for arg in "$@"; do
  case "$arg" in
    --generate-new) GENERATE_NEW=1 ;;
    *) echo "Usage: ${0##*/} [--generate-new]" >&2; exit 2 ;;
  esac
done

PW="$("$WALLET_HELPER" kdewallet ao-admin metaread-password 2>/dev/null || true)"
if [ -n "$PW" ]; then
  echo 'reusing the existing metaread password from KDE Wallet'
elif [ "$GENERATE_NEW" -eq 1 ]; then
  PW="$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)"
  echo 'generated a new metaread password (--generate-new)'
else
  echo "ERROR: no ao-admin/metaread-password in KDE Wallet." >&2
  echo "  Refusing to generate implicitly -- that would silently rotate the" >&2
  echo "  password on a live role. Re-run with --generate-new if this really" >&2
  echo "  is a first-time bootstrap. If the wallet is simply locked, unlock it" >&2
  echo "  and retry; a locked wallet is indistinguishable from a missing entry" >&2
  echo "  here, which is exactly why generation must be explicit." >&2
  exit 3
fi
chmod 0644 /tmp/metaread-grants.sql
pkexec /usr/bin/sudo -u postgres /usr/bin/psql -q -v ON_ERROR_STOP=1 --set=pw="$PW" -f /tmp/metaread-grants.sql 2>&1 | tail -15
rm -f "$PW_FILE" "$PW_FILE.tmp"
echo 'OK: metaread password set on the role; no plaintext copy retained'
if /ALWAYSON/scripts/ops/kwallet-provision.sh put kdewallet ao-admin metaread-password "$PW" >/dev/null 2>&1; then
  echo 'OK: mirrored to KDE Wallet (ao-admin/metaread-password)'
else
  echo 'WARN: KDE Wallet mirror failed'
fi
echo DONE
