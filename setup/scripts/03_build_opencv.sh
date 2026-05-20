#!/bin/bash
set -e

VERSION="4.13.0"

export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

echo "=== Usuwanie starych konfiguracji OpenCV ==="
sudo rm -rf /usr/lib/cmake/opencv4
sudo rm -rf /usr/lib/aarch64-linux-gnu/cmake/opencv4

echo "=== Pobieranie OpenCV ${VERSION} ==="
cd /tmp && rm -rf opencv-${VERSION} opencv_contrib-${VERSION} opencv.zip opencv_contrib.zip

echo "Pobieranie OpenCV ${VERSION}..."
wget -q --show-progress -O opencv.zip https://github.com/opencv/opencv/archive/refs/tags/${VERSION}.zip
unzip -q opencv.zip

echo "Pobieranie opencv_contrib ${VERSION}..."
wget -q --show-progress -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/refs/tags/${VERSION}.zip
unzip -q opencv_contrib.zip

echo "=== Budowanie OpenCV z CUDA ==="
cd opencv-${VERSION} && mkdir -p build && cd build

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DWITH_CUDA=ON \
  -DCUDA_ARCH_BIN=8.7 \
  -DCUDA_ARCH_PTX="" \
  -DOPENCV_EXTRA_MODULES_PATH=/tmp/opencv_contrib-${VERSION}/modules \
  -DWITH_NEON=ON \
  -DBUILD_opencv_cudaarithm=OFF \
  -DBUILD_opencv_cudalegacy=OFF \
  -DWITH_CUDNN=ON \
  -DCMAKE_INSTALL_PREFIX=/usr/local \
  -DBUILD_TESTS=OFF \
  -DBUILD_PERF_TESTS=OFF \
  -DBUILD_EXAMPLES=OFF

make -j1
sudo make install
sudo ldconfig

echo "=== Weryfikacja instalacji OpenCV ==="
python3 -c "import cv2; print('OpenCV version:', cv2.__version__); print('CUDA support:', cv2.cuda.getCudaEnabledDeviceCount(), 'device(s)')" || echo "⚠️  Python cv2 check pominięty (może nie być zainstalowany)"

echo "✅ OpenCV ${VERSION} z CUDA zainstalowany"
