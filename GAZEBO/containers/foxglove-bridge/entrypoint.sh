#!/bin/bash
# Foxglove bridge entrypoint: TWO hops, both required.
#   1. ros_gz_bridge    gz-transport -> ROS 2   (brings the camera image in)
#   2. foxglove_bridge ROS 2 -> Foxglove WS     (serves it to the viewer)
#
# Written as a script rather than a bash -c one-liner on purpose: in
# "a && b & c" the shell backgrounds the WHOLE "a && b" list and runs c
# unsourced, which made foxglove_bridge fail to load
# libfoxglove_bridge_component.so. Separate statements avoid that entirely.

# NOTE: do NOT add "set -u" here. /opt/ros/lyrical/setup.bash references
# AMENT_TRACE_SETUP_FILES without a default, so `set -u` aborts the source with
#   line 8: AMENT_TRACE_SETUP_FILES: unbound variable
# and the container exits before either hop starts. Measured. "set -o pipefail"
# alone is safe and is kept.

set -o pipefail

# shellcheck disable=SC1091
source /opt/ros/lyrical/setup.bash

# Be explicit anyway: the ament executables live under lib/<pkg>/ and are not
# on PATH even after sourcing.
#
# EVERY entry below is load-bearing. Measured 2026-10-02: the previous revision
# listed only three directories and the gz hop silently bridged NOTHING. Two
# independent causes, both proven:
#
# 1. /opt/ros/lyrical/lib/x86_64-linux-gnu was MISSING. The ROS middleware
#    itself lives there - librmw_fastrtps_cpp.so, libfastcdr.so.2. Without it
#    every ROS process aborts at startup:
#      "dlopen error: libfastcdr.so.2: cannot open shared object file"
#      "failed to load any RMW implementations"
#
# 2. The five gz *_vendor/lib directories were MISSING. ros_gz_bridge links
#    libgz-transport.so.15 and libgz-msgs.so.12; both ship under
#    /opt/ros/lyrical/opt/<name>_vendor/lib and are on NO default loader path.
#    Without them the gz hop fails to load and does nothing SILENTLY: the
#    process stays alive, Foxglove still accepts connections, and the viewer
#    shows only /rosout and /parameter_events with no error anywhere. That
#    silence is what made this fault expensive to find.
#
# Do NOT trim the five vendor dirs. ros_gz_bridge cannot find gz-transport or
# gz-msgs without them.
export LD_LIBRARY_PATH="/opt/ros/lyrical/lib:/opt/ros/lyrical/lib/x86_64-linux-gnu:/opt/ros/lyrical/lib/foxglove_bridge:/opt/ros/lyrical/lib/ros_gz_bridge"
for _gz_vendor in gz_math_vendor gz_msgs_vendor gz_tools_vendor gz_transport_vendor gz_utils_vendor; do
    export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/ros/lyrical/opt/${_gz_vendor}/lib"
done

# parameter_bridge, not bridge_node — see HOP 1 below for why.
GZ_BRIDGE=/opt/ros/lyrical/lib/ros_gz_bridge/parameter_bridge
FG_BRIDGE=/opt/ros/lyrical/lib/foxglove_bridge/foxglove_bridge

# -----------------------------------------------------------------------------
# HOP 1 — gz-transport -> ROS 2
# -----------------------------------------------------------------------------
# USE parameter_bridge, NOT bridge_node. Measured 2026-10-02: bridge_node is the
# bare component and, given only these parameters, it creates NO publisher at
# all - it stays alive, logs nothing, and bridges nothing. parameter_bridge is
# the executable that actually builds the topic list.
#
# The topic spec is 'TOPIC@ROS2_type[gz_type'. The '[' is the direction bracket
# meaning Gazebo -> ROS ONLY, which is what this view-only surface needs. The
# previous revision used bridge_node with '-p topic:=...@ros2' and a bare
# 'bridge_type:=gz.msgs.Image'; that combination bridges nothing.
#
# 'sensor_msgs/msg/Image' is REQUIRED and was the missing piece. ros_gz_bridge
# maps gz.msgs.Image <-> sensor_msgs/msg/Image; you cannot name the gz type
# alone. Naming it wrong gives, measured:
#   "No template specialization for the pair"
# while naming it correctly logs:
#   Creating GZ->ROS Bridge: [/factory/camera/image (gz.msgs.Image)
#                            -> /factory/camera/image (sensor_msgs/msg/Image)]
#   and the topic then appears in `ros2 topic list` at ~9.7 Hz.
# Keep the gz topic name and the ROS topic name identical - the '/factory/'
# prefix on both is what preserves the leading slash as a valid global ROS 2
# topic. Verified against the running server.
# ---------------------------------------------------------------------------
# GZ_IP — load-bearing, and it must be this container's OWN address.
# ---------------------------------------------------------------------------
# gz-transport discovery advertises GZ_IP. With it unset, gz-transport falls back
# to the container hostname, which does not resolve to a reachable address, and
# the hop binds somewhere the server cannot be reached from. Measured with it
# unset: the gz topic was visible from this container but reported
#   "No publishers on topic [/factory/camera/image]"
# so the subscriber connected and no image data ever arrived.
#
# It must be the address on ao-sim-fabrication (the domain the Gazebo server is
# on), NOT the ao-html-window address, and NOT 127.0.0.1. 127.0.0.1 resolves to
# this container itself, so a remote publisher would send its images to the
# bridge's own loopback. The GUI avoids all of this because it shares the
# server's network namespace.
#
# Derived at runtime from the container's own interfaces so it cannot drift out
# of step with the address podman actually assigned.
GZ_IP="$(hostname -i 2>/dev/null | tr ' ' '\n' | grep -E '^10\.89\.5\.' | head -1)"
if [ -z "$GZ_IP" ]; then
    echo "[entrypoint] FATAL: no ao-sim-fabrication address found; cannot bridge" >&2
    exit 1
fi
export GZ_IP
echo "[entrypoint] gz-transport discovery will advertise GZ_IP=${GZ_IP}"

echo "[entrypoint] starting gz-transport -> ROS 2 hop for /factory/camera/image"
# Eight camera views, all gz -> ROS only ('[' direction bracket). Each is a
# read-only feed; none of them can drive the simulation.
"$GZ_BRIDGE" \
    '/factory/camera/image@sensor_msgs/msg/Image[gz.msgs.Image' \
    '/factory/camera/arms_ne@sensor_msgs/msg/Image[gz.msgs.Image' \
    '/factory/camera/arms_n@sensor_msgs/msg/Image[gz.msgs.Image' \
    '/factory/camera/arms_se@sensor_msgs/msg/Image[gz.msgs.Image' \
    '/factory/camera/arms_e@sensor_msgs/msg/Image[gz.msgs.Image' \
    '/factory/camera/elev_arms@sensor_msgs/msg/Image[gz.msgs.Image' \
    '/factory/camera/elev_conveyor@sensor_msgs/msg/Image[gz.msgs.Image' \
    '/factory/camera/elev_massing@sensor_msgs/msg/Image[gz.msgs.Image' &
GZ_PID=$!

# If the sensor hop dies, tear the container down rather than serving an
# empty Foxglove that looks healthy.
cleanup() {
    echo "[entrypoint] stopping gz hop ($GZ_PID)"
    kill "$GZ_PID" 2>/dev/null
    wait "$GZ_PID" 2>/dev/null
}
trap cleanup EXIT

echo "[entrypoint] starting Foxglove WebSocket on 8081"
# NOTE: the port is a ROS parameter, NOT --port. --port/-p/--ws-port are all
# silently ignored by 3.5.0 and it binds its built-in 8765 instead.
#
# ---------------------------------------------------------------------------
# VIEW-ONLY ENFORCEMENT (operator decision 2026-10-02)
# ---------------------------------------------------------------------------
# Foxglove Studio is a VIEWER of the simulation. It must not be able to affect
# it. These three parameters are what actually enforce that - the network is not
# the control, these are. Measured before this change: capabilities advertised
# clientPublish, both whitelists were ['.*'], and a client COULD advertise a
# writable topic (proved against this live bridge: 'advertise' of
# /factory/cmd_vel was ACCEPTED).
#
#   capabilities           - drop clientPublish (lets a client create writable
#                            topics), parameters and services (expose the bridge's
#                            own DDS set_parameters, a live write path on
#                            ROS_DOMAIN_ID 22). connectionGraph and assets stay:
#                            both are needed to draw the panel UI.
#   client_topic_whitelist - only the eight camera feeds may ever be written.
#                            Everything else a client names is refused.
#   param_whitelist        - empty: no parameter read/write.
#
# asset_uri_allowlist is empty for the same reason: an allow-all default would
# let a viewer pull external assets.
#
# DO NOT express "allow nothing" as []. Measured 2026-10-02: an empty list is
# rejected at startup and the process aborts before it can serve anything:
#   parameter_value_from failed for parameter 'param_whitelist':
#   Invalid parameter value: ... structure contains no value
# '^$' is a regex that matches no name, which is the working idiom. Verified:
# the bridge starts and reports capabilities ['connectionGraph','assets'].
#
# This is a fence, not the whole story: anything else on ao-sim-fabrication with
# ROS_DOMAIN_ID=22 can still reach the domain directly. The guarantee this change
# buys is "a Foxglove client cannot write", not "the domain is write-isolated".
"$FG_BRIDGE" --ros-args \
    -p port:=8081 \
    -p capabilities:="['connectionGraph','assets']" \
    -p client_topic_whitelist:="['/factory/camera/image','/factory/camera/arms_ne','/factory/camera/arms_n','/factory/camera/arms_se','/factory/camera/arms_e','/factory/camera/elev_arms','/factory/camera/elev_conveyor','/factory/camera/elev_massing']" \
    -p param_whitelist:="['^$']" \
    -p asset_uri_allowlist:="['^$']"