#!/usr/bin/env bash
# Print the live Gazebo GUI viewport camera pose (x y z roll pitch yaw).
set -euo pipefail
CONTAINER=ao-sim-fabrication-gui-gz
BIN=/tmp/ao_read_camera
if ! podman exec "$CONTAINER" test -x "$BIN" 2>/dev/null; then
  podman cp /ALWAYSON/scripts/simulation/gztools/read_gui_camera.cpp "$CONTAINER:$BIN.cpp" >/dev/null
  podman exec -w /tmp "$CONTAINER" bash -lc \
    "g++ -std=c++17 $BIN.cpp -o $BIN \$(pkg-config --cflags --libs gz-transport gz-msgs)"
fi
podman exec -e GZ_PARTITION=alwayson_fabrication_sim -e GZ_IP=127.0.0.1 "$CONTAINER" "$BIN" | head -1
