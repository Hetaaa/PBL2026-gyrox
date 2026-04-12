#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROS_DISTRO="${ROS_DISTRO:-humble}"
DEFAULT_RVIZ_CONFIG="${WORKSPACE_DIR}/scripts/rvizConfig.rviz"
RVIZ_CONFIG="${1:-${DEFAULT_RVIZ_CONFIG}}"

set +u
source "/opt/ros/${ROS_DISTRO}/setup.bash"
set -u

if [[ -f "${WORKSPACE_DIR}/ros2_ws/install/setup.bash" ]]; then
  set +u
  source "${WORKSPACE_DIR}/ros2_ws/install/setup.bash"
  set -u
fi

if ! command -v rviz2 >/dev/null 2>&1; then
  echo "rviz2 is not installed or not on PATH"
  echo "Install ROS desktop tools with: bash setup/scripts/00_install_ros2.sh"
  exit 1
fi

exec rviz2 -d "${RVIZ_CONFIG}"
