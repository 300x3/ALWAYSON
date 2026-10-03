#!/bin/bash
# ALWAYS ON: read the saved GUI camera pose and apply it as the world default.
# The GUI viewport camera is NOT the world's <gui><camera> block; it is
# MinimalScene's <camera_pose> in gui.config. Both are updated so the saved
# default and the opening view agree.
# Usage: save-gui-camera-pose.sh [world]
set -euo pipefail
WORLD="${1:-/ALWAYSON/GAZEBO/worlds/factory.world}"
GUI_CONFIG="${GZ_GUI_CONFIG:-/home/scottw/.local/share/ao-simulation/gui-home/.gz/sim/10/gui.config}"

POSE="$(python3 - "$GUI_CONFIG" <<'PY'
import sys, re
text = open(sys.argv[1], encoding='utf-8', errors='replace').read()
# gui.config is a bare sequence of top-level <plugin> elements with no single
# root, so ElementTree cannot parse it. Scope the search to the 3D View plugin.
m = re.search(r'<plugin\b[^>]*name="3D View".*?</plugin>', text, re.S)
if not m:
    sys.exit('ERROR: no "3D View" plugin block found in gui.config')
c = re.search(r'<camera_pose>(.*?)</camera_pose>', m.group(0), re.S)
if not c or not c.group(1).strip():
    sys.exit('ERROR: no <camera_pose> found under the 3D View plugin')
print(' '.join(c.group(1).split()))
PY
)"
echo "GUI camera_pose: $POSE"

cp "$WORLD" "$WORLD.bak.$(date -u +%Y%m%dT%H%M%SZ)"
python3 - "$WORLD" "$POSE" <<'PY'
import sys, re, pathlib
world, pose = pathlib.Path(sys.argv[1]), sys.argv[2]
t = world.read_text()
# world-level <gui><camera><pose> (first occurrence)
t, n1 = re.subn(r'(<gui>\s*<camera\b[^>]*>\s*<pose>)[^<]*(</pose>)',
                lambda m: m.group(1) + pose + m.group(2), t, count=1)
# camera_rig model pose
t, n2 = re.subn(r'(<model name="camera_rig">\s*<pose>)[^<]*(</pose>)',
                lambda m: m.group(1) + pose + m.group(2), t, count=1)
world.write_text(t)
print(f"world: gui/camera pose updated={n1}  camera_rig pose updated={n2}")
if not (n1 and n2):
    sys.exit("ERROR: expected to update both poses")
PY

python3 -c "import xml.etree.ElementTree as ET; ET.parse('$WORLD'); print('world parses OK')"
echo "Applied. Restart the GUI to see it."
