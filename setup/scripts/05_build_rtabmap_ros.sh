#!/bin/bash
set -e

# 1. Automatyczne ustalenie ścieżki do workspace (dwa foldery w górę od skryptu)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROS_WS="$(realpath "$SCRIPT_DIR/../../ros2_ws")"

echo "Praca w workspace: $ROS_WS"

if [ ! -d "$ROS_WS" ]; then
    echo "BŁĄD: Nie znaleziono folderu $ROS_WS"
    exit 1
fi

cd "$ROS_WS"

# 2. Środowisko (ROS2 Humble + CUDA)
source /opt/ros/humble/setup.bash
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# 4. Kompilacja (tryb Release, 1 rdzeń dla bezpieczeństwa RAM)
colcon build --symlink-install \
    --parallel-workers 1 \
    --cmake-args \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_LIBRARY_PATH="/usr/lib/aarch64-linux-gnu" 

echo "-------------------------------------------------------"
echo "Gotowe! Pamiętaj o: source install/setup.bash"