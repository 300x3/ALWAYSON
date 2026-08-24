#!/usr/bin/env bash
# ALWAYS ON privileged bootstrap - Sections 2.4, 2.6
# Run via: pkexec bash /home/scottw/ALWAYSON-staging/scripts/bootstrap/ao-bootstrap-privileged.sh
set -Eeuo pipefail
IFS=$'\n\t'

LOG=/home/scottw/ALWAYSON-staging/logs/installation/agent-install.log
exec >>"$LOG" 2>&1
echo "===== PRIVILEGED BOOTSTRAP START $(date --iso-8601=seconds) ====="

# --- Section 2.6: Build /ALWAYSON ---
install -d -m 0750 \
  /ALWAYSON/{docs,quadlet,config,secrets,data,artifacts,ipfs,pcloud,backups,logs,scripts,tests,tmp}

install -d -m 0750 \
  /ALWAYSON/docs/{adr,architecture,runbooks,compliance} \
  /ALWAYSON/storefront/{source,build,releases,manifests,pcloud-public-folder} \
  /ALWAYSON/quadlet/{networks,volumes,sales,payment,field,mapping,sim-vehicle,sim-fabrication,ledger,operations} \
  /ALWAYSON/config/{platform,storefront,sales,payment,drone,field,mapping,sim-vehicle,sim-fabrication,ledger,pcloud,ipfs} \
  /ALWAYSON/data/{sales,payment,field,mapping,sim-vehicle,sim-fabrication,ledger,cache} \
  /ALWAYSON/artifacts/{storefront-releases,drone-releases,telemetry-manifests,mapping-manifests,vehicle-simulation-manifests,fabrication-simulation-manifests,sales-receipts} \
  /ALWAYSON/logs/installation \
  /ALWAYSON/scripts/{bootstrap,deploy,validation,mapping,radio,simulation,storefront,ledger,backup,restore,maintenance}

install -d -m 0750 \
  /ALWAYSON/config/field/heltec-v3 \
  /ALWAYSON/config/drone/waveshare-lora \
  /ALWAYSON/config/mapping/processing-profiles \
  /ALWAYSON/config/sim-vehicle/worlds \
  /ALWAYSON/config/sim-vehicle/missions \
  /ALWAYSON/config/sim-fabrication/{worlds,robot-arms,safety-zones,task-plans} \
  /ALWAYSON/config/storefront/{payment-links,mastodon-links,support-links}

chown -R scottw:scottw /ALWAYSON
chmod 0750 /ALWAYSON
echo "/ALWAYSON layout created (Section 2.6)"

# Merge staged inventory journal into final location
cat /home/scottw/ALWAYSON-staging/logs/installation/agent-install.log >> /ALWAYSON/logs/installation/agent-install.log 2>/dev/null || true

# --- Section 2.4: Host dependencies ---
export DEBIAN_FRONTEND=noninteractive
apt update
apt install -y \
  podman \
  uidmap \
  slirp4netns \
  fuse-overlayfs \
  containernetworking-plugins \
  nftables \
  ufw \
  git \
  curl \
  jq \
  ca-certificates \
  gnupg \
  openssl \
  restic \
  smartmontools \
  lm-sensors \
  acl \
  python3 \
  python3-venv \
  python3-pip
echo "Host dependencies installed (Section 2.4)"

echo "===== PRIVILEGED BOOTSTRAP COMPLETE $(date --iso-8601=seconds) ====="
echo "BOOTSTRAP_OK"