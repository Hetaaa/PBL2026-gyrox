#!/bin/bash
# Start Zenoh Router on Robot (Jetson) for remote RViz visualization

set -euo pipefail

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ZENOH_CONFIG="${WORKSPACE_DIR}/scripts/zenoh/robot.json5"
LOG_DIR="${WORKSPACE_DIR}/.logs/zenoh"
PID_FILE="${LOG_DIR}/zenoh_router.pid"
LOG_FILE="${LOG_DIR}/zenoh_router.log"

mkdir -p "${LOG_DIR}"

echo "=========================================="
echo "Starting Zenoh Router on Robot"
echo "=========================================="

# Check if binary exists
if ! command -v zenoh-bridge-ros2dds >/dev/null 2>&1; then
    if command -v zenoh-bridge-dds >/dev/null 2>&1; then
        ZENOH_BIN="zenoh-bridge-dds"
    else
        echo "❌ Zenoh not installed!"
        echo "Run: bash setup/scripts/07_install_zenoh.sh"
        exit 1
    fi
else
    ZENOH_BIN="zenoh-bridge-ros2dds"
fi

# Check if already running
if [[ -f "${PID_FILE}" ]]; then
    old_pid="$(cat "${PID_FILE}")"
    if ps -p "${old_pid}" >/dev/null 2>&1; then
        echo "⚠️  Zenoh router already running (PID: ${old_pid})"
        echo "To restart, run: bash scripts/zenoh/stop_zenoh_router.sh"
        exit 0
    fi
fi

# Get robot's IP address
ROBOT_IP=$(hostname -I | awk '{print $1}')

echo "Robot IP: $ROBOT_IP"
echo "Port: 7447"
echo "Config: $ZENOH_CONFIG"
echo ""

# Start Zenoh router
nohup "${ZENOH_BIN}" -c "${ZENOH_CONFIG}" > "${LOG_FILE}" 2>&1 &
ZENOH_PID=$!
echo "${ZENOH_PID}" > "${PID_FILE}"

sleep 1

# Verify startup
if ps -p "${ZENOH_PID}" >/dev/null 2>&1; then
    echo "✅ Zenoh router started (PID: ${ZENOH_PID})"
    echo ""
    echo "=========================================="
    echo "Waiting for ROS2 nodes to connect..."
    echo "=========================================="
    sleep 3
    echo ""
    echo "Connected topics (being bridged):"
    tail -20 "${LOG_FILE}" | grep -E "Listener|Connect" || true
else
    echo "❌ Failed to start Zenoh!"
    cat "${LOG_FILE}"
    exit 1
fi

echo ""
echo "Tell laptop to connect to: tcp/$ROBOT_IP:7447"
echo ""
echo "Logs: tail -f ${LOG_FILE}"
echo "Stop: bash scripts/zenoh/stop_zenoh_router.sh"
