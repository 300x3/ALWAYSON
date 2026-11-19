#!/usr/bin/env bash
# ALWAYS ON - load and validate the separate SIM-18 vehicle race course.
set -Eeuo pipefail
IFS=$'\n\t'
. /ALWAYSON/scripts/lib/common.sh

AO_LOCK_NAME="sim-vehicle-course"
STATIC_ONLY=0
KEEP_RUNNING=0
for arg in "$@"; do
  case "$arg" in
    --static-only) STATIC_ONLY=1 ;;
    --keep-running) KEEP_RUNNING=1 ;;
    *) echo "ERROR: unknown argument: $arg" >&2; exit 64 ;;
  esac
done

if (( STATIC_ONLY )); then
  exec python3 /ALWAYSON/scripts/simulation/verify-vehicle-course.py
fi

ao_require_cmds podman python3 sha256sum
ao_lock "$AO_LOCK_NAME"
ao_audit "SIM-18 headless vehicle-course validation requested"
RUN_ID="$(date -u +%Y%m%dT%H%M%S)-$$"
RUN_DIR="/ALWAYSON/data/sim-vehicle/results/vehicle-course-$RUN_ID"
mkdir -p "$RUN_DIR"
python3 /ALWAYSON/scripts/simulation/verify-vehicle-course.py > "$RUN_DIR/static-validation.json"

IMAGE="localhost/gz-sim10-server@sha256:55f8dbcf8decb0b97c6be7cf2fde8859b0fd05735c7a759df09a12e091933581"
TOOLS_IMAGE="localhost/gz-sim10-resolute@sha256:14bb123b4b7f946de91f9124275d77abdd17562db19a7061934bf2addc69761a"
CONTAINER="ao-sim-vehicle-course-validation"
TOOLS_CONTAINER="ao-sim-vehicle-course-tools"
WORLD="/ALWAYSON/GAZEBO/worlds/vehicle_race_course.world"

gz_exec() {
  podman exec "$TOOLS_CONTAINER" bash -c \
    '. /opt/ros/lyrical/setup.bash && exec gz "$@"' bash "$@" 9>&-
}

cleanup() {
  local rc=$?
  trap - EXIT
  if podman container exists "$CONTAINER"; then
    podman logs "$CONTAINER" > "$RUN_DIR/gazebo-server.log" 2>&1 || true
  fi
  if (( ! KEEP_RUNNING )); then
    podman stop --time 5 "$TOOLS_CONTAINER" > /dev/null 2>&1 || true
    podman stop --time 10 "$CONTAINER" > /dev/null 2>&1 || true
  fi
  ao_operation "SIM-18 result=$([ "$rc" -eq 0 ] && echo PASS || echo FAIL) evidence=$RUN_DIR keep_running=$KEEP_RUNNING"
  exit "$rc"
}
trap cleanup EXIT

if podman container exists "$CONTAINER"; then
  podman start "$CONTAINER" > /dev/null 9>&-
else
  podman run --detach --name "$CONTAINER" --network=none --read-only \
    --tmpfs /tmp:rw,nosuid,size=128m --cap-drop=ALL \
    --security-opt=no-new-privileges \
    --env HOME=/tmp --env GZ_IP=127.0.0.1 \
    --env GZ_PARTITION=alwayson_vehicle_sim --env GZ_VERSION=10 \
    --env GZ_SIM_RESOURCE_PATH=/ALWAYSON/GAZEBO/models \
    --env ROS_DOMAIN_ID=21 \
    --volume /ALWAYSON/GAZEBO:/ALWAYSON/GAZEBO:ro,Z \
    --entrypoint /usr/libexec/gz/sim10/gz-sim-server \
    "$IMAGE" "$WORLD" -r -s -v 4 > /dev/null 9>&-
fi

if podman container exists "$TOOLS_CONTAINER"; then
  podman start "$TOOLS_CONTAINER" > /dev/null 9>&-
else
  podman run --detach --name "$TOOLS_CONTAINER" \
    --network="container:$CONTAINER" --read-only \
    --tmpfs /tmp:rw,nosuid,size=128m --cap-drop=ALL \
    --security-opt=no-new-privileges \
    --volume /opt/ros/lyrical:/opt/ros/lyrical:ro \
    --env HOME=/tmp --env GZ_IP=127.0.0.1 \
    --env GZ_PARTITION=alwayson_vehicle_sim --env GZ_VERSION=10 \
    --entrypoint /bin/sleep "$TOOLS_IMAGE" infinity > /dev/null 9>&-
fi

ready=0
for _ in $(seq 1 30); do
  if gz_exec topic -l 2>/dev/null | grep -q '^/world/vehicle_race_course/scene/info$'; then
    ready=1
    break
  fi
  sleep 1
done
if (( ! ready )); then
  echo "ERROR: vehicle_race_course did not publish scene/info" >&2
  exit 1
fi

move_probe() {
  local id=$1 x=$2 y=$3 z=$4 tolerance=$5
  local request="name: \"course_probe\" position { x: $x y: $y z: $z }"
  local response
  response=$(gz_exec service \
    -s /world/vehicle_race_course/set_pose \
    --reqtype gz.msgs.Pose --reptype gz.msgs.Boolean --timeout 3000 \
    --req "$request" 2>&1)
  printf '%s\n' "$response" > "$RUN_DIR/$id-set-pose-response.txt"
  grep -q 'data: true' <<< "$response"
  gz_exec topic -e \
    -t /world/vehicle_race_course/dynamic_pose/info -n 1 \
    > "$RUN_DIR/$id-dynamic-pose.txt"
  python3 /ALWAYSON/scripts/simulation/verify-vehicle-course.py \
    --pose-sample "$RUN_DIR/$id-dynamic-pose.txt" \
    --expect "$x" "$y" "$z" --tolerance "$tolerance" \
    > "$RUN_DIR/$id-pose-validation.json"
}

mapfile -t WAYPOINTS < <(python3 - <<'PY'
import json
m=json.load(open('/ALWAYSON/GAZEBO/sim/vehicle-course.json'))
for w in m['waypoints']:
    print(w['id'], *w['pose'], w['tolerance_m'])
PY
)
: > "$RUN_DIR/checkpoints.jsonl"
for row in "${WAYPOINTS[@]}"; do
  IFS=' ' read -r id x y z tolerance <<< "$row"
  move_probe "$id" "$x" "$y" "$z" "$tolerance"
  python3 - "$RUN_DIR" "$id" "$x" "$y" "$z" <<'PY' >> "$RUN_DIR/checkpoints.jsonl"
import json, pathlib, sys
p=pathlib.Path(sys.argv[1]); ident=sys.argv[2]
validation=json.loads((p/f'{ident}-pose-validation.json').read_text())
validation.update(id=ident, service_response=(p/f'{ident}-set-pose-response.txt').read_text().strip())
print(json.dumps(validation, sort_keys=True))
PY
done

move_probe reset 0 0 1 0.25
python3 - "$RUN_DIR" <<'PY'
import json, pathlib, sys
p=pathlib.Path(sys.argv[1])
checkpoints=[json.loads(line) for line in (p/'checkpoints.jsonl').read_text().splitlines()]
reset=json.loads((p/'reset-pose-validation.json').read_text())
static=json.loads((p/'static-validation.json').read_text())
result={
  'schema_version':'1.0', 'item':'SIM-18', 'result':'PASS',
  'course_id':'ao-vehicle-air-land-sea-race-v1',
  'world':static['world'], 'world_sha256':static['world_sha256'],
  'building_world_sha256':static['building_world_sha256'],
  'mode':static['mode'], 'dynamics_claim':'none',
  'checkpoints':checkpoints, 'reset':reset,
  'external_network':False, 'physical_vehicle_used':False,
}
(p/'result.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
print(json.dumps({'result':'PASS','evidence':str(p/'result.json'),'checkpoints':len(checkpoints)}, indent=2))
PY
