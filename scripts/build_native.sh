#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROS_DISTRO="${ROS_DISTRO:-humble}"

set +u
source "/opt/ros/${ROS_DISTRO}/setup.bash"
set -u

cd "${WORKSPACE_DIR}/ros2_ws"

colcon build --symlink-install --packages-ignore realsense2_camera realsense2_camera_msgs realsense2_description realsense2_ros_mqtt_bridge realsense2_rviz_plugin rtabmap_conversions rtabmap_costmap_plugins rtabmap_demos rtabmap_examples rtabmap_launch rtabmap_msgs rtabmap_odom rtabmap_python rtabmap_ros rtabmap_rviz_plugins rtabmap_slam rtabmap_sync rtabmap_util rtabmap_viz "$@"
