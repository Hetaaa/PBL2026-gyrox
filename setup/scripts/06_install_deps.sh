#!/usr/bin/env bash
set -euo pipefail

ROS_DISTRO="${ROS_DISTRO:-humble}"

# NOTE:
# - librealsense / rtabmap core / custom OpenCV are expected to be built from source
#   in your Jetson setup flow.
# - This script installs native APT/ROS dependencies required by slam
#   and only stack-specific runtime packages (no duplicated ROS desktop/tooling).

if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo is required to install system packages"
  exit 1
fi

sudo apt update

sudo apt install -y \
  python3-yaml \
  python3-numpy

# Runtime/system libs used by ROS visualization and point cloud stack.
sudo apt install -y \
  libsqlite3-dev \
  libpcl-dev \
  liboctomap-dev \
  libzip-dev \
  libgl1-mesa-dev \
  libglu1-mesa-dev \
  freeglut3-dev

# Core ROS stack and tools not already covered by ros-humble-desktop.
sudo apt install -y \
  "ros-${ROS_DISTRO}-realsense2-camera" \
  "ros-${ROS_DISTRO}-rtabmap-ros" \
  "ros-${ROS_DISTRO}-imu-filter-madgwick" \
  "ros-${ROS_DISTRO}-robot-state-publisher" \
  "ros-${ROS_DISTRO}-tf2-tools" \
  "ros-${ROS_DISTRO}-depthimage-to-laserscan" \
  "ros-${ROS_DISTRO}-grid-map-ros" \
  "ros-${ROS_DISTRO}-grid-map-msgs" \
  "ros-${ROS_DISTRO}-image-transport" \
  "ros-${ROS_DISTRO}-vision-msgs" \
  "ros-${ROS_DISTRO}-octomap-server" \
  "ros-${ROS_DISTRO}-pcl-ros" \
  "ros-${ROS_DISTRO}-sensor-msgs-py" \
  "ros-${ROS_DISTRO}-rmw-zenoh-cpp"

if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
  sudo rosdep init
fi
rosdep update

echo "Native ROS dependencies installed for ${ROS_DISTRO}."
