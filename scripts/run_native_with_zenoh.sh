#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

cleanup() {
  echo -e "${YELLOW}Stopping Zenoh router...${NC}"
  bash "${WORKSPACE_DIR}/scripts/zenoh/stop_zenoh_router.sh" || true
}

trap cleanup EXIT INT TERM

echo -e "${BLUE}=========================================="
echo "Starting Complete System with Zenoh Router"
echo "==========================================${NC}"
echo ""

# Get robot IP
ROBOT_IP=$(hostname -I | awk '{print $1}')
echo -e "${GREEN}✓ Robot IP: $ROBOT_IP${NC}"
echo ""

# Start Zenoh router
echo -e "${BLUE}Starting Zenoh Router...${NC}"
bash "${WORKSPACE_DIR}/scripts/zenoh/start_zenoh_router.sh"

echo ""
echo -e "${GREEN}=========================================="
echo "Zenoh Router is running!"
echo "==========================================${NC}"
echo ""
echo -e "${YELLOW}For remote RViz on laptop:${NC}"
echo -e "  Run: bash scripts/zenoh/run_remote_rviz.sh $ROBOT_IP"
echo ""
echo -e "${YELLOW}Available topics for visualization:${NC}"
echo "  • /tf (robot transforms) - 10 Hz"
echo "  • /tf_static (static frames) - 1 Hz"
echo "  • /scan (lidar points) - 2 Hz"
echo "  • /rtabmap/cloud_map (SLAM 3D map) - 0.5 Hz"
echo "  • /robot_description (robot model URDF) - 1 Hz"
echo "  • /zones_color_panel (zone indicator) - 2 Hz"
echo ""
echo -e "${BLUE}Starting ROS2 Project Launch...${NC}"
echo ""

exec bash "${WORKSPACE_DIR}/scripts/run_native.sh" "$@"
