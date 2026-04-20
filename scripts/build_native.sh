#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROS_DISTRO="${ROS_DISTRO:-humble}"

set +u
source "/opt/ros/${ROS_DISTRO}/setup.bash"
set -u

cd "${WORKSPACE_DIR}/ros2_ws"

colcon build --symlink-install --packages-select slam robot_model "$@"
