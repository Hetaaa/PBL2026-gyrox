#!/bin/bash
set -e

echo "-------------------------------------------------------"
echo "KROK 0: Naprawa repozytoriów i instalacja ROS 2 Humble"
echo "-------------------------------------------------------"

# 1. Agresywne czyszczenie duplikatów, które powodowały błędy
echo "--- Czyszczenie starych wpisów repozytorium ---"
sudo rm -f /etc/apt/sources.list.d/ros2.list
sudo rm -f /etc/apt/sources.list.d/ros2.sources
sudo sed -i '/packages.ros.org/d' /etc/apt/sources.list

# 2. Ustawienie locale (wymagane przez ROS 2)
sudo apt update && sudo apt install locales -y
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# 3. Dodanie klucza i repozytorium w JEDNYM poprawnym formacie
echo "--- Dodawanie klucza GPG i repozytorium ROS 2 ---"
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# 4. Instalacja ROS 2 i narzędzi
echo "--- Instalacja pakietów ROS 2 Humble (Desktop) ---"
sudo apt update
sudo apt install -y \
  ros-humble-desktop \
  ros-dev-tools \
  python3-colcon-common-extensions \
  python3-rosdep \
  python3-argcomplete

# 5. Inicjalizacja rosdep
echo "--- Inicjalizacja rosdep ---"
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
    sudo rosdep init
fi
rosdep update

# 6. Automatyczne dodanie source do .bashrc
if ! grep -q "source /opt/ros/humble/setup.bash" ~/.bashrc; then
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
    echo "Dodano source /opt/ros/humble/setup.bash do ~/.bashrc"
fi

echo "-------------------------------------------------------"
echo "SUKCES: ROS 2 Humble zainstalowany pomyślnie!"
echo "Zrestartuj terminal lub wpisz: source ~/.bashrc"
echo "-------------------------------------------------------"