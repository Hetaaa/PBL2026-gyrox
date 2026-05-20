#!/bin/bash
# RViz Remote Visualization over Zenoh
# Run this on your laptop to connect to robot

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_DIR="$(realpath "$SCRIPT_DIR/../..")"

# ============== CONFIGURATION ==============
# ZMIEŃ NA IP ROBOTA!
ROBOT_IP="${1:-192.168.1.100}"  # Change to your robot's IP
ROBOT_PORT="7447"
ZENOH_CONFIG="${SCRIPT_DIR}/host.json5"

echo "=========================================="
echo "RViz Remote Visualization Setup"
echo "=========================================="
echo "Robot IP: $ROBOT_IP"
echo "Port: $ROBOT_PORT"
echo ""

# Check if zenoh-bridge-ros2dds is installed
if ! command -v zenoh-bridge-ros2dds >/dev/null 2>&1; then
    if ! command -v zenoh-bridge-dds >/dev/null 2>&1; then
        echo "❌ Zenoh not installed!"
        echo "Install: pip install zenoh-bridge-ros2dds"
        exit 1
    fi
fi

# Check ROS2 installation
if [ -z "$ROS_DISTRO" ]; then
    echo "Sourcing ROS2..."
    source /opt/ros/humble/setup.bash 2>/dev/null || {
        echo "❌ ROS2 not found. Install or source it first."
        exit 1
    }
fi

# Update config with robot IP
echo "Updating Zenoh config with robot IP: $ROBOT_IP"
sed -i "s|tcp/ROBOT_IP:7447|tcp/$ROBOT_IP:$ROBOT_PORT|g" "$ZENOH_CONFIG"

# Create log directory
LOG_DIR="$WORKSPACE_DIR/.logs/zenoh"
mkdir -p "$LOG_DIR"

echo ""
echo "Starting Zenoh bridge on laptop..."
echo "Config: $ZENOH_CONFIG"
echo ""

# Start Zenoh bridge in background
nohup zenoh-bridge-ros2dds -c "$ZENOH_CONFIG" > "$LOG_DIR/zenoh_host.log" 2>&1 &
ZENOH_PID=$!
echo "✅ Zenoh bridge started (PID: $ZENOH_PID)"

sleep 2

# Check if connection successful
if grep -q "Listener.*0.0.0.0:7447" "$LOG_DIR/zenoh_host.log" 2>/dev/null; then
    echo "✅ Zenoh listening on DDS"
else
    echo "⚠️  Check logs for details: tail -f $LOG_DIR/zenoh_host.log"
fi

echo ""
echo "=========================================="
echo "Starting RViz..."
echo "=========================================="
echo ""

# Set up environment for RViz
export ROS_DOMAIN_ID=0
export ROS_DISCOVERY_SERVER=""

# Start RViz
rviz2 -d "$WORKSPACE_DIR/scripts/rviz/remote_config.rviz" 2>&1 &
RVIZ_PID=$!

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo "Zenoh bridge PID: $ZENOH_PID"
echo "RViz PID: $RVIZ_PID"
echo ""
echo "Available topics:"
echo "  - /tf, /tf_static"
echo "  - /scan, /scan_filtered"
echo "  - /rtabmap/cloud_map"
echo "  - /odom"
echo "  - /zones_color_panel"
echo ""
echo "To stop:"
echo "  kill $ZENOH_PID $RVIZ_PID"
echo ""
echo "Logs: $LOG_DIR/zenoh_host.log"
echo ""

# Wait for processes
wait
