#!/bin/bash
set -e

# Lokalizacja skryptu i folderów sprzętowych
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
HARDWARE_DIR="$SCRIPT_DIR/../hardware_config"

echo "-------------------------------------------------------"
echo "KROK 1: Przygotowanie systemu Jetson Orin Nano"
echo "-------------------------------------------------------"

# 1. Instalacja bazowych zależności do kompilacji i wideo
echo "--- Instalowanie pakietów APT ---"
sudo apt-get update
sudo apt-get install -y \
    libssl-dev libusb-1.0-0-dev libudev-dev pkg-config \
    libgtk-3-dev cmake build-essential v4l-utils \
    python3-dev python3-pip curl wget

# 2. Konfiguracja uprawnień USB (UDEV)
echo "--- Konfiguracja reguł UDEV dla RealSense ---"
# Pobieramy najnowsze reguły bezpośrednio od Intela
sudo wget -O /etc/udev/rules.d/99-realsense-libusb.rules \
     https://raw.githubusercontent.com/IntelRealSense/librealsense/master/config/99-realsense-libusb.rules

# Przeładowanie reguł, aby system je zauważył
sudo udevadm control --reload-rules && sudo udevadm trigger

# 3. Sprawdzenie modułów jądra (Sterowniki IMU)
echo "--- Sprawdzanie sterowników IIO (IMU) ---"
if ls /dev/iio:device* > /dev/null 2>&1; then
    echo "SUKCES: Urządzenia IIO (IMU) są widoczne w /dev/."
else
    echo "UWAGA: Nie widzę /dev/iio:device. Upewnij się, że Twoje moduły .ko"
    echo "są wgrane do /lib/modules/$(uname -r)/ i wykonałeś sudo depmod -a."
    
    # Opcjonalnie: możemy tu dodać komendę kopiującą, jeśli masz pliki .ko w konkretnym miejscu
    # sudo cp $HARDWARE_DIR/twoje_moduly/*.ko /lib/modules/$(uname -r)/kernel/drivers/iio/...
    # sudo depmod -a
fi

echo "-------------------------------------------------------"
echo "System przygotowany. Teraz uruchom skrypt 02_build_librealsense.sh"
echo "Pamiętaj o fizycznym odłączeniu i podłączeniu kamery!"
echo "-------------------------------------------------------"