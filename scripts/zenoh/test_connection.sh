#!/bin/bash
# Zenoh Connection Troubleshooting Guide
# Diagnozowanie problemów z połączeniem między robotem a laptopem

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=========================================="
echo "Zenoh Connection Diagnostic Test"
echo "=========================================="
echo ""

# 1. Check if zenoh is installed
echo "[1] Sprawdzam instalację Zenoh..."
if command -v zenoh-bridge-ros2dds >/dev/null 2>&1; then
    echo "✅ zenoh-bridge-ros2dds: $(which zenoh-bridge-ros2dds)"
elif command -v zenoh-bridge-dds >/dev/null 2>&1; then
    echo "⚠️  zenoh-bridge-dds (alternative): $(which zenoh-bridge-dds)"
else
    echo "❌ Zenoh NOT INSTALLED!"
    echo "   Install: pip install zenoh-bridge-ros2dds"
    exit 1
fi
echo ""

# 2. Check ROS2
echo "[2] Sprawdzam ROS2..."
if [ -z "$ROS_DISTRO" ]; then
    echo "⚠️  ROS2 not sourced, sourcing..."
    source /opt/ros/humble/setup.bash 2>/dev/null || {
        echo "❌ Cannot source ROS2!"
        exit 1
    }
fi
echo "✅ ROS Distro: $ROS_DISTRO"
echo ""

# 3. Check config files
echo "[3] Sprawdzam pliki konfiguracyjne..."
ROBOT_CONFIG="$SCRIPT_DIR/robot.json5"
HOST_CONFIG="$SCRIPT_DIR/host.json5"

if [ -f "$ROBOT_CONFIG" ]; then
    echo "✅ robot.json5: EXISTS"
else
    echo "❌ robot.json5: MISSING!"
fi

if [ -f "$HOST_CONFIG" ]; then
    echo "✅ host.json5: EXISTS"
else
    echo "❌ host.json5: MISSING!"
fi
echo ""

# 4. Check Zenoh router process
echo "[4] Sprawdzam procesy Zenoh..."
if pgrep -f "zenoh-bridge.*robot.json5" >/dev/null; then
    PID=$(pgrep -f "zenoh-bridge.*robot.json5")
    echo "✅ Zenoh Router RUNNING (PID: $PID)"
else
    echo "⚠️  Zenoh Router NOT running on this machine"
    echo "   (OK if running on robot)"
fi
echo ""

# 5. Check ROS2 domain ID
echo "[5] Sprawdzam ROS_DOMAIN_ID..."
echo "   ROS_DOMAIN_ID: ${ROS_DOMAIN_ID:=0}"
echo ""

# 6. List available topics (if this is robot)
echo "[6] Dostępne topiki ROS2:"
timeout 2 ros2 topic list 2>/dev/null || echo "   ⚠️  No topics yet (bridge may not be running)"
echo ""

# 7. Advice
echo "=========================================="
echo "RECOMMENDATIONS:"
echo "=========================================="
echo ""
echo "Na ROBOCIE:"
echo "  1. Uruchom: bash scripts/zenoh/start_zenoh_router.sh"
echo "  2. Sprawdź logi: tail -f .logs/zenoh/zenoh_router.log"
echo "  3. Sprawdź: ps aux | grep zenoh"
echo ""
echo "Na LAPTOPIE:"
echo "  1. Sprawdź IP robota: ROBOT_IP=<IP>"
echo "  2. Uruchom: bash scripts/zenoh/run_remote_rviz.sh ROBOT_IP"
echo "  3. Sprawdź logi: tail -f .logs/zenoh/zenoh_client.log"
echo ""
echo "DEBUGOWANIE:"
echo "  - Sprawdź firewall: sudo ufw allow 7447/tcp"
echo "  - Ping robota: ping ROBOT_IP"
echo "  - Topiki z robota: ros2 topic list"
echo ""
