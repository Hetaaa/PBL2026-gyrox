#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROS_DISTRO="${ROS_DISTRO:-humble}"

set +u
source "/opt/ros/${ROS_DISTRO}/setup.bash"
set -u

required_pkgs=(
  slam_bringup
  project_bringup
  robot_model
  scan_filter
  ultrasonic_driver
  zones_manager
  closest_element_info
)

missing_pkgs=()
for pkg in "${required_pkgs[@]}"; do
  if ! ros2 pkg prefix "$pkg" >/dev/null 2>&1; then
    missing_pkgs+=("$pkg")
  fi
done

if (( ${#missing_pkgs[@]} > 0 )); then
  echo "Missing ROS packages: ${missing_pkgs[*]}"
  echo "Install native deps: bash scripts/install_native_deps.sh"
  exit 1
fi

if [[ -f "${WORKSPACE_DIR}/ros2_ws/install/setup.bash" ]]; then
  set +u
  source "${WORKSPACE_DIR}/ros2_ws/install/setup.bash"
  set -u
else
  echo "Build workspace first: cd ros2_ws && colcon build --symlink-install"
  exit 1
fi

exec ros2 launch project_bringup project_launch.py "$@"
