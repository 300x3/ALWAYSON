#!/bin/sh
# Prepared 2026-10-03 for 07:00. Nothing here is destructive or irreversible.
# Every step was pre-validated unprivileged; this only re-does the parts that
# need uid 0.
set -e
echo "[$(date -Is)] starting"

# 1. resync the installed logrotate policy with the repo copy (comment header
#    only - non-comment lines already verified identical)
install -m 0644 -o root -g root \
  /ALWAYSON/config/host/logrotate-alwayson.conf /etc/logrotate.d/alwayson
cmp /etc/logrotate.d/alwayson /ALWAYSON/config/host/logrotate-alwayson.conf \
  && echo "logrotate policy synced"

# 2. apparmor-utils: §2.3 records it MISSING, so no profile can be enforced or
#    inspected. This is the only remaining item in that note.
DEBIAN_FRONTEND=noninteractive apt-get install -y apparmor-utils
command -v aa-enforce && echo "aa-enforce now present"

# 3. validate, do not assume
logrotate --debug /etc/logrotate.d/alwayson >/dev/null 2>/tmp/lr-0700.err
echo "logrotate parse errors: $(grep -cE '^error' /tmp/lr-0700.err || true)"

echo "[$(date -Is)] done"
