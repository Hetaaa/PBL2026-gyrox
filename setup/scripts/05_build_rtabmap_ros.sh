#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROS_WS="$(realpath "$SCRIPT_DIR/../../ros2_ws")"

export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
export CMAKE_PREFIX_PATH=/usr/local:$CMAKE_PREFIX_PATH
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH

echo "Praca w workspace: $ROS_WS"

if [ ! -d "$ROS_WS" ]; then
    echo "BŁĄD: Nie znaleziono folderu $ROS_WS"
    exit 1
fi

# Weryfikacja rtabmap core
if [ ! -f /usr/local/lib/cmake/rtabmap/RTABMapConfig.cmake ]; then
    echo "❌ RTAB-Map core nie znaleziony — odpal najpierw 04_build_rtabmap.sh!"
    exit 1
fi

echo "=== Czyszczenie ROS2 workspace ==="
cd "$ROS_WS"
rm -rf build install log

echo "=== Przygotowanie środowiska ==="
source /opt/ros/humble/setup.bash

RTABMAP_DIR=$(find /usr/local/lib -maxdepth 1 -name 'rtabmap-*' -type d | head -1)
echo "RTABMAP_DIR: $RTABMAP_DIR"

echo "=== Budowanie rtabmap ROS packages z allow-overriding ==="
colcon build \
    --packages-select rtabmap_conversions rtabmap_msgs rtabmap_odom rtabmap_slam rtabmap_viz rtabmap_util \
    --allow-overriding rtabmap_conversions rtabmap_msgs rtabmap_odom rtabmap_slam rtabmap_util rtabmap_viz \
    --parallel-workers 1 \
    --cmake-args \
        -DCMAKE_BUILD_TYPE=Release \
        -DOpenCV_DIR=/usr/local/lib/cmake/opencv4 \
        -DRTABMAP_DIR=$RTABMAP_DIR \
        -DCMAKE_PREFIX_PATH=/usr/local \
        -DCMAKE_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu

echo "-------------------------------------------------------"
echo "✅ Gotowe! Pamiętaj o: source install/setup.bash"
echo "=== Weryfikacja linkowania ==="
ldd "$ROS_WS/install/rtabmap_odom/lib/rtabmap_odom/stereo_odometry" | grep -E "librtabmap_core|libopencv"