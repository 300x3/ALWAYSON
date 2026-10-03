#!/usr/bin/env bash
# Move the Gazebo GUI viewport camera to an absolute world pose.
# The GUI's saved gui.config <camera_pose> is NOT reliably honoured at load
# (observed 2026-10-01), so the pose is applied live through the GUI's own
# /gui/move_to/pose service, which IS honoured.
# Usage: move_gui_camera.sh <x> <y> <z> <roll> <pitch> <yaw>
set -euo pipefail
[ "$#" -eq 6 ] || { echo "usage: $0 x y z roll pitch yaw" >&2; exit 1; }
CONTAINER=ao-sim-fabrication-gui-gz
BIN=/tmp/ao_move_camera
if podman exec "$CONTAINER" test -x "$BIN" 2>/dev/null; then
  :
else
  podman cp /ALWAYSON/scripts/simulation/gztools/move_camera.cpp "$CONTAINER:$BIN.cpp" >/dev/null
  podman exec -w /tmp "$CONTAINER" bash -lc \
    "g++ -std=c++17 $BIN.cpp -o $BIN \$(pkg-config --cflags --libs gz-transport gz-msgs)"
fi
podman exec -e GZ_PARTITION=alwayson_fabrication_sim -e GZ_IP=127.0.0.1 "$CONTAINER" \
  "$BIN" "$1" "$2" "$3" "$4" "$5" "$6"
