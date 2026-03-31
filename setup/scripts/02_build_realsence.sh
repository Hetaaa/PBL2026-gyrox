#!/bin/bash
set -e

# Lokalizacja źródeł względem skryptu
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LIBRS_DIR="$SCRIPT_DIR/../libs/librealsense"

echo "-------------------------------------------------------"
echo "Budowanie librealsense z CUDA dla Jetson Orin Nano"
echo "Lokalizacja: $LIBRS_DIR"
echo "-------------------------------------------------------"

if [ ! -d "$LIBRS_DIR" ]; then
    echo "BŁĄD: Nie znaleziono folderu $LIBRS_DIR. Sprawdź submoduły."
    exit 1
fi

cd "$LIBRS_DIR"
mkdir -p build && cd build

# Czyścimy stare konfiguracje
rm -rf *

# Konfiguracja CMake pod Orina
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_EXAMPLES=true \
    -DBUILD_GRAPHICAL_EXAMPLES=true \
    -DBUILD_PYTHON_BINDINGS=bool:true \
    -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc \
    -DBUILD_WITH_CUDA=true \
    -DCMAKE_CUDA_ARCHITECTURES=87 \
    -DFORCE_RSUSB_BACKEND=OFF \
    -DCHECK_FOR_UPDATES=false

echo "--- Rozpoczynam kompilację na $(nproc) rdzeniach ---"
make -j$(nproc)

echo "--- Instalacja systemowa ---"
sudo make install
sudo ldconfig

echo "--- Sukces! Przetestuj wpisując: realsense-viewer ---"