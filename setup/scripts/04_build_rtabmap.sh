#!/bin/bash
set -e

RTABMAP_SRC="/home/pbl/pbl/PBL2026-gyrox/setup/libs/rtabmap"

export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
export CMAKE_PREFIX_PATH=/usr/local:$CMAKE_PREFIX_PATH
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH

echo "=== Czyszczenie starego rtabmap ==="
sudo find /opt/ros/humble -name "*rtabmap*" -delete 2>/dev/null || true
sudo rm -rf /opt/ros/humble/lib/aarch64-linux-gnu/rtabmap* 2>/dev/null || true
sudo find /usr/local -name "*rtabmap*" -delete 2>/dev/null || true
sudo rm -rf /usr/local/lib/rtabmap* 2>/dev/null || true
sudo ldconfig
echo "✅ Stary rtabmap usunięty"

echo "=== Weryfikacja OpenCV ==="
if [ ! -f /usr/local/lib/cmake/opencv4/OpenCVConfig.cmake ]; then
    echo "❌ OpenCV nie znaleziony w /usr/local — odpal najpierw 03_build_opencv.sh!"
    exit 1
fi
echo "✅ OpenCV OK"

echo "=== Budowanie rtabmap core ==="
echo "Branch: $(cd $RTABMAP_SRC && git branch --show-current) @ $(cd $RTABMAP_SRC && git log --oneline -1)"
cd "$RTABMAP_SRC"
rm -rf build && mkdir -p build && cd build

cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DCMAKE_PREFIX_PATH=/usr/local \
    -DWITH_CUDA=ON \
    -DCMAKE_CUDA_ARCHITECTURES=87 \
    -DWITH_REALSENSE2=ON \
    -DWITH_G2O=ON \
    -DWITH_OPENGV=ON \
    -DWITH_GTSAM=OFF \
    -DOpenCV_DIR=/usr/local/lib/cmake/opencv4

make -j4
sudo make install
sudo ldconfig

echo "✅ RTAB-Map core zainstalowany"
echo "=== Weryfikacja linkowania core ==="
ldd /usr/local/lib/librtabmap_core.so | grep -E "opencv|cuda" | head -5
