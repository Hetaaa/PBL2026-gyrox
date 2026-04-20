#!/usr/bin/env bash
set -euo pipefail

ROS_DISTRO="${ROS_DISTRO:-humble}"

if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo is required to install packages"
  exit 1
fi

sudo apt update
sudo apt install -y \
  "ros-${ROS_DISTRO}-rmw-zenoh-cpp" \
  "ros-${ROS_DISTRO}-cyclonedds" \
  "ros-${ROS_DISTRO}-zenoh-bridge-dds"

# Make sure ROS binaries are visible in this shell while validating install.
if [[ -f "/opt/ros/${ROS_DISTRO}/setup.bash" ]]; then
  # shellcheck disable=SC1090
  source "/opt/ros/${ROS_DISTRO}/setup.bash"
fi

if command -v zenoh-bridge-ros2dds >/dev/null 2>&1; then
  echo "OK: zenoh-bridge-ros2dds found in PATH"
elif command -v zenoh-bridge-dds >/dev/null 2>&1; then
  mkdir -p "${HOME}/.local/bin"
  ln -sf "$(command -v zenoh-bridge-dds)" "${HOME}/.local/bin/zenoh-bridge-ros2dds"
  echo "Created compatibility link: ~/.local/bin/zenoh-bridge-ros2dds -> zenoh-bridge-dds"
  if ! grep -Fq 'export PATH="$HOME/.local/bin:$PATH"' "${HOME}/.bashrc"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "${HOME}/.bashrc"
    echo "Added ~/.local/bin to PATH in ~/.bashrc"
  fi
else
  echo "WARNING: zenoh-bridge-ros2dds binary is not in PATH"
  echo "Try: source /opt/ros/${ROS_DISTRO}/setup.bash"
  echo "If still missing, install from Eclipse Zenoh releases for your architecture."
fi
