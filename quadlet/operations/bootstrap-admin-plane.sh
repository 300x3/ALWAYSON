#!/usr/bin/env bash
# Unprivileged bootstrap: waits for image pulls, installs/starts ao-admin
# plane as user Quadlet units, verifies health. No root required.
LOG=/ALWAYSON/logs/operations/bootstrap.log
exec >>"$LOG" 2>&1
printf '===== %s bootstrap start =====\n' "$(date --iso-8601=seconds)"
for i in $(seq 1 120); do
  grep -q PULLS2_DONE /ALWAYSON/logs/operations/image-pull2.log 2>/dev/null && break
  sleep 10
done
if ! grep -q PULLS2_DONE /ALWAYSON/logs/operations/image-pull2.log; then echo 'TIMED OUT waiting for pulls'; exit 1; fi
for img in docker.io/grafana/grafana-oss:11.6.0 docker.io/prom/prometheus:v3.4.1 docker.io/prom/node-exporter:v1.9.1; do
  podman image exists "$img" || { echo "MISSING $img"; exit 1; }
done
cp /ALWAYSON/quadlet/operations/ao-*.container /ALWAYSON/quadlet/operations/ao-*.volume ~/.config/containers/systemd/
systemctl --user daemon-reload
systemctl --user start ao-prometheus.service
sleep 3
systemctl --user start ao-node-exporter.service
sleep 2
systemctl --user start ao-grafana.service
systemctl --user start ao-metabase.service
sleep 20
for u in ao-prometheus ao-node-exporter ao-grafana ao-metabase; do
  echo "$u: $(systemctl --user is-active $u.service)"
done
for hp in 9090 3001 3002; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "http://127.0.0.1:$hp/" || true)
  echo "port $hp HTTP $code"
done
node=$(curl -s --max-time 5 http://127.0.0.1:9090/api/v1/query?query=up 2>/dev/null | grep -o '"value":\["[0-9.]*","1"\]' | wc -l)
echo "prometheus up-vectors: $node"
printf '===== %s bootstrap end =====\n' "$(date --iso-8601=seconds)"
