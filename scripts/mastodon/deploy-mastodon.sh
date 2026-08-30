#!/usr/bin/env bash
# ALWAYS ON - mastodon/deploy-mastodon.sh
# Deploy a LOCAL, self-contained Mastodon instance containerized on the
# internal ao-sales network (no public listener; loopback-only), operated
# from the desktop with Tokodon (KDE).
#
# NOTE: starting the containers requires running under the alwayson-sales
# service account (rootless isolate). This host cannot escalate without a
# TTY, so the operator must run the start steps from a real terminal.
#
# Usage:
#   deploy-mastodon.sh genenv   # write secrets/mastodon/mastodon.env + KWallet
#   deploy-mastodon.sh deploy    # ensure network; print enable instructions
#   deploy-mastodon.sh create <handle> <email> [password]   # owner + wallet
#   deploy-mastodon.sh status
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh

SEC=/ALWAYSON/secrets/mastodon/mastodon.env
KW=/ALWAYSON/scripts/ops/kwallet-provision.sh
W=kdewallet
FOLDER=ao-mastodon

genenv() {
  ao_require_cmds openssl
  install -d -m 0700 -o scottw -g scottw /ALWAYSON/secrets/mastodon
  local K O P
  K=$(test -f "$SEC" && sed -n 's/^SECRET_KEY_BASE=//p' "$SEC" | tail -1 || true)
  K=${K:-$(openssl rand -hex 64)}
  O=$(test -f "$SEC" && sed -n 's/^OTP_SECRET=//p' "$SEC" | tail -1 || true)
  O=${O:-$(openssl rand -hex 32)}
  P=$(test -f "$SEC" && sed -n 's/^POSTGRES_PASSWORD=//p' "$SEC" | tail -1 || true)
  P=${P:-$(openssl rand -hex 24)}
  umask 077
  cat > "$SEC" <<EOF
# ALWAYS ON Mastodon - local instance env (generated, gitignored).
LOCAL_DOMAIN=localhost
SINGLE_USER_MODE=false
DEFAULT_LOCALE=en
SECRET_KEY_BASE=$K
OTP_SECRET=$O
# rails database wiring (mastodon app)
DB_HOST=mastodon-db
DB_USER=mastodon
DB_NAME=mastodon
DB_PASS=$P
# postgres container wiring (used by the DB unit)
POSTGRES_DB=mastodon
POSTGRES_USER=mastodon
POSTGRES_PASSWORD=$P
# redis (mastodon app)
REDIS_HOST=mastodon-redis
REDIS_PORT=6379
# concurrency
WEB_CONCURRENCY=2
MAX_THREADS=5
STREAMING_CLUSTER_NUM=1
# no full-text search on a tiny local instance
ES_ENABLED=false
EOF
  chmod 0600 "$SEC"; chown scottw:scottw "$SEC" 2>/dev/null || true
  "$KW" put "$W" "$FOLDER" mastodon-secret-key-base "$K" >/dev/null
  "$KW" put "$W" "$FOLDER" mastodon-otp-secret      "$O" >/dev/null
  "$KW" put "$W" "$FOLDER" mastodon-db-password     "$P" >/dev/null
  echo "OK: $SEC (gitignored) written + mirrored to KDE Wallet ao-mastodon"
}

deploy() {
  ao_require_cmds podman
  test -f "$SEC" || genenv
  podman network exists ao-sales || podman network create ao-sales
  cat <<EOF2
OK: network 'ao-sales' present, env in place.
Containers: quadlet/sales/ao-mastodon-{db,redis,web,sidekiq,streaming}.container
Web/streaming publish ONLY to 127.0.0.1 (loopback; no public listener).

OPERATOR (root TTY) - pull + enable:
  # under the alwayson-sales rootless store/account
  sudo -u alwayson-sales env HOME=/home/alwayson-sales \\
    XDG_RUNTIME_DIR=/run/user/\$(id -u alwayson-sales) bash -c \\
    'podman pull docker.io/mastodon/mastodon:v4.3.7'
  sudo -u alwayson-sales env HOME=/home/alwayson-sales \\
    XDG_RUNTIME_DIR=/run/user/\$(id -u alwayson-sales) \\
    systemctl --user daemon-reload
  sudo -u alwayson-sales env HOME=/home/alwayson-sales \\
    XDG_RUNTIME_DIR=/run/user/\$(id -u alwayson-sales) \\
    systemctl --user enable --now \\
      ao-mastodon-db ao-mastodon-redis ao-mastodon-web \\
      ao-mastodon-sidekiq ao-mastodon-streaming

(Image: mastodon/mastodon:v4.3.7. If anonymous docker.io pull is denied, use
 a mirror - see docs/runbooks/mastodon.md.)
EOF2
}

create_user() {
  test -f "$SEC" || genenv
  [ $# -ge 2 ] || { echo "usage: create <handle> <email> [password]"; exit 2; }
  local handle="$1" email="$2" pass="${3:-}"
  [ -n "$pass" ] || pass=$(openssl rand -hex 12)
  "$KW" put "$W" "$FOLDER" mastodon-owner-password "$pass" >/dev/null
  echo "Owner password -> KDE Wallet: ao-mastodon/mastodon-owner-password"
  echo "When the stack is up, in sales store:"
  echo "  podman exec mastodon-web bin/tootctl accounts create '$handle' \\"
  echo "      --email '$email' --confirmed --role Owner --password '$pass'"
}

status() {
  echo "ao-sales network:"; podman network exists ao-sales && echo "  present" || echo "  MISSING"
  echo "mastodon containers (try sales bridge):"
  podman --url unix:///run/ao-podman/sales.sock ps -a 2>/dev/null | grep -Ei 'mastodon|sales-db' || echo "  none visible via bridge"
}

case "${1:-}" in
  genenv) genenv ;;
  deploy) deploy ;;
  create) shift; create "$@" ;;
  status) status ;;
  *) echo "usage: deploy-mastodon.sh {genenv|deploy|create|status}"; exit 2 ;;
esac