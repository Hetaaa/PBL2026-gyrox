#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RTABMAP_DIR="$SCRIPT_DIR/../libs/rtabmap"

echo "-------------------------------------------------------"
echo "Budowanie silnika RTAB-Map z CUDA dla Jetsona (OpenCV 4.8 od NVIDIA)"
echo "-------------------------------------------------------"

cd "$RTABMAP_DIR"
mkdir -p build && cd build
rm -rf *

# Automatycznie wykryje systemowe OpenCV 4.8.0 dostarczone przez JetPack
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DWITH_CUDA=ON \
    -DCMAKE_CUDA_ARCHITECTURES=87 \
    -DWITH_REALSENSE2=ON \
    -DCMAKE_INSTALL_PREFIX=/usr/local

# Kompilacja na wszystkich dostępnych rdzeniach procesora Orin
make -j4
sudo make install
sudo ldconfig

echo "--- Silnik RTAB-Map zainstalowany pomyślnie! ---"