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

# ZANIM ROZPOCZNIEMY KOMPILACJĘ: czyścimy stare buildy OpenCV 4.5
echo "Czyszczenie starych katalogów kompilacji..."
cd "$ROS_WS"
rm -rf build/ install/ log/

# 2. Środowisko (ROS2 Humble + CUDA)
source /opt/ros/humble/setup.bash
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# 4. Kompilacja całego workspace (tryb Release, 1 rdzeń dla bezpieczeństwa RAM na Jetsonie)
# Usunęliśmy selektywne ograniczanie paczek, aby zbudowały się też wiadomości ArUco
echo "Rozpoczynanie kompilacji workspace..."
colcon build --symlink-install \
    --allow-overriding cv_bridge image_geometry \
    --parallel-workers 1 \
    --cmake-args \
    -DCMAKE_BUILD_TYPE=Release 

echo "-------------------------------------------------------"
echo "Gotowe! Pamiętaj o: source install/setup.bash"